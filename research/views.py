import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='torch.distributed.elastic')


import os
import uuid
import json
import psycopg2
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from .models import ChatUser, ChatMessage, Website
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
from django.shortcuts import redirect, get_object_or_404
from .models import IngestedFile
import subprocess
import sys

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_CONFIG = {
    "dbname": "market_db",
    "user": "postgres",
    "password": "1329",
    "host": "localhost",
    "port": "5432"
}
os.environ["GOOGLE_API_KEY"] = "AIzaSyAVdXCFfvczcoFpByEZjIZs0QB2I5FGeiQ"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === PG Connection ===
conn = psycopg2.connect(**DB_CONFIG)
register_vector(conn)

# === Lazy Embedder ===
_embedder = None
def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# === Retrieve Chunks per Website ===
def get_relevant_chunks(query, website_id, top_k=3):
    embedder = get_embedder()
    query_vec = embedder.encode([query])[0].tolist()
    table_name = "your_table"
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT content FROM {table_name}
            WHERE website_id = %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (website_id, query_vec, top_k))
        results = cur.fetchall()
    return "\n\n".join(row[0] for row in results)

def get_recent_prompt_chain(session_id, max_turns=3):
    messages = ChatMessage.objects.filter(
        session_id=session_id
    ).exclude(prompt__isnull=True).exclude(prompt__exact="").order_by('-timestamp')[:max_turns]

    formatted = [
        f"User: {msg.prompt.strip()}"
        for msg in reversed(messages)
        if msg.prompt
    ]
    return "\n".join(formatted)

# === Gemini RAG Response with history ===
def generate_text_response(current_query, site_id, session_id=None):
    prompt_chain = current_query.strip()
    if session_id:
        recent_prompts = get_recent_prompt_chain(session_id)
        if recent_prompts:
            prompt_chain = recent_prompts + "\nUser: " + current_query.strip()

    context_chunks = get_relevant_chunks(prompt_chain, site_id)

    final_prompt = f"""
You are an expert **market research assistant** designed to provide accurate, concise, and actionable insights for all types of market analysis and calculations, with visually appealing outputs. Your responses are processed by a backend that renders graphs, so include graph code when appropriate without stating that you cannot draw graphs.

be polite.

### Context
{context_chunks}

### Conversation History
{prompt_chain}

### Instructions
- **Response Focus**: Address the user's most recent query directly. Use the conversation history only if no context in the recent query, to maintain context and ensure coherence, especially for follow-up questions.
-**Same context**: if the query has no context respond according to the nearest context in conversation hisory.
- **Context**: if context is new from the previous query then act upon the new query.
- **Content Quality**: Provide detailed, data-driven insights using only the provided context and history. Avoid speculation or irrelevant details.
- **Market Analysis and Calculations**:
  - Handle all types of market research calculations, including but not limited to:
    - **Compound Annual Growth Rate (CAGR)**: Calculate as `CAGR = ((End Value / Start Value)^(1/Number of Periods) - 1) * 100`. Provide step-by-step calculations in markdown.
    - **Market Share**: Calculate as `(Company Revenue / Total Market Revenue) * 100`. Include comparisons across competitors or regions if relevant.
    - **Growth Rates**: Compute year-over-year or period-over-period growth rates as `((Current Value - Previous Value) / Previous Value) * 100`.
    - **Return on Investment (ROI)**: Calculate as `((Gain from Investment - Cost of Investment) / Cost of Investment) * 100`.
    - **Market Size Projections**: Use linear or exponential models based on available data trends (e.g., linear for steady growth, exponential for rapid growth).
    - **Customer Acquisition Cost (CAC)**: Calculate as `Total Acquisition Costs / Number of New Customers`.
    - **Lifetime Value (LTV)**: Calculate as `Average Revenue per Customer * Average Customer Lifespan`.
    - **Break-even Analysis**: Determine the break-even point as `Fixed Costs / (Selling Price per Unit - Variable Cost per Unit)`.
    - **Other Metrics**: Include Net Promoter Score (NPS), churn rate, or penetration rate if relevant to the query.
  - For each calculation:
    - Show the formula in markdown (e.g., `CAGR = ((End Value / Start Value)^(1/n) - 1) * 100`).
    - Provide a step-by-step breakdown of the calculation using sample or provided data.
    - If data is missing, assume reasonable values based on context, clearly stating assumptions.
    - Include a one-sentence summary of the result's significance.
- **Markdown Formatting**:
  - Use markdown consistently for clear structure.
  - Include `#` for main headings, `##` for subheadings, and `*` for bullet points.
  - Keep paragraphs concise (2-3 sentences) and use bullet points for lists of key points, trends, or data.
  - Example structure for a market report:
    ```markdown
    # Market Report: [Topic]
    ## Overview
    - Key point 1
    - Key point 2
    ## Trends
    - Trend 1
    - Trend 2
    ## Calculations
    - CAGR: [Result]
    - Market Share: [Result]
    ```
- **Graph Generation**:
  - **When to Include**: Include one or more Python `matplotlib` code blocks for:
    - Queries explicitly requesting a "graph", "chart", "visualize", or "show" for data like trends, growth rates, or comparisons.
    - Queries requesting "detailed info", "detailed report", or similar, to visualize multiple key metrics (e.g., market size, CAGR, regional shares, LTV, CAC).
    - Calculations like CAGR, market share, or growth rates, where visualizing trends or comparisons enhances understanding.
  - **Placement**: Insert each graph's code block immediately after the relevant text section (e.g., after `## Market Size` for a market size graph, or `## Regional Analysis` for a pie chart).
  - **Multiple Graphs**: If multiple data points benefit from visualization (e.g., market size over time, regional shares, CAGR trends), include separate `matplotlib` code blocks for each, placed after their respective sections.
  - Place each code block inside triple backticks (```python ... ```).
  - Use `plt.figure(figsize=(8, 2.5))` for consistent sizing.
  - Ensure each graph is clear, labeled (title, axes), and appropriate for the data (e.g., line chart for trends over time, bar chart for comparisons, pie chart for market share).
  - Provide a one-sentence summary before each code block describing what the graph shows.
  - Example:
    ```markdown
    ## Market Size
    The market is projected to grow steadily.
    This graph shows the market size from 2025 to 2032.
    ```python
    import matplotlib.pyplot as plt
    years = [2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032]
    values = [81.86, 86.61, 91.63, 96.95, 102.58, 108.53, 114.82, 121.47]
    plt.figure(figsize=(8, 2.5))
    plt.plot(years, values, marker='o')
    plt.title('Market Size (2025-2032)')
    plt.xlabel('Year')
    plt.ylabel('Market Size (USD Million)')
    plt.grid(True)
    ```
    ## Regional Shares
    North America leads the market.
    This graph shows the market share by region in 2025.
    ```python
    import matplotlib.pyplot as plt
    regions = ['North America', 'Europe', 'Asia-Pacific']
    shares = [50, 30, 20]
    plt.figure(figsize=(8, 2.5))
    plt.pie(shares, labels=regions, autopct='%1.1f%%')
    plt.title('Market Share by Region (2025)')
    ```
- **No Graph Explanation**: Do not explain the code; let the summary suffice.
- **Follow-Up Questions**: End with 1-2 specific, relevant follow-up questions to encourage deeper exploration (e.g., "Would you like a breakdown of market size by region?" or "Should I calculate the LTV for a specific customer segment?").
- **Error Handling**: If data is insufficient for a graph or detailed answer, explain briefly in markdown, include a text-based summary, and suggest alternative insights or questions.

remember the question might not always demand a discriptive response,respond accordingly.

### Your Response
""".strip()

    print("\n" + "="*30 + " GEMINI PROMPT START " + "="*30 + "\n")
    print(final_prompt)
    print("\n" + "="*31 + " GEMINI PROMPT END " + "="*31 + "\n")

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(final_prompt)
        return response.text.strip()
    except Exception as e:
        print("[❌] Gemini API Error:", e)
        return "An error occurred while generating a response."

# === Views ===
def index(request):
    return render(request, "index.html")

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("message", "").strip()
            api_key = data.get("api_key")

            if not query:
                return JsonResponse({"error": "Empty message"}, status=400)
            if not api_key:
                return JsonResponse({"error": "Missing API Key"}, status=400)

            site = Website.objects.filter(api_key=api_key).first()
            if not site:
                return JsonResponse({"error": "Invalid API Key"}, status=403)

            request.session["api_key"] = api_key

            if not request.session.get('chat_session_id'):
                request.session['chat_session_id'] = str(uuid.uuid4())
            session_id = request.session['chat_session_id']

            user = None
            user_id = request.session.get("user_id")
            if user_id:
                user = ChatUser.objects.filter(id=user_id).first()

            # Save prompt first, no response yet
            chat_message = ChatMessage.objects.create(
                user=user,
                website=site,
                session_id=session_id,
                prompt=query.strip(),
                response=""
            )

            # Generate response
            ai_output = generate_text_response(query, site.id, session_id=session_id)
            response_text, image_names = generate_graphs_from_response(ai_output or "")

            # Update the ChatMessage with response
            chat_message.response = response_text.strip()
            chat_message.save()

            return JsonResponse({
                "reply": response_text,
                "need_user_info": user is None,
                "image_urls": [request.build_absolute_uri(f"/media/{img}") for img in image_names] if image_names else []
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST method required."}, status=405)

@csrf_exempt
def save_user_details(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            company_name = data.get("company_name")
            mobile_number = data.get("mobile_number")

            api_key = request.session.get("api_key")
            site = Website.objects.filter(api_key=api_key).first()
            if not site:
                return JsonResponse({"error": "Invalid website for user"}, status=403)

            user, created = ChatUser.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "company_name": company_name,
                    "mobile_number": mobile_number,
                    "website": site
                }
            )

            if not created:
                user.name = name
                user.company_name = company_name
                user.mobile_number = mobile_number
                user.website = site
                user.save()

            request.session["user_id"] = user.id

            session_id = request.session.get('chat_session_id')
            if session_id:
                ChatMessage.objects.filter(user__isnull=True, session_id=session_id).update(user=user)

            return JsonResponse({"status": "saved"})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST method required."}, status=405)

@csrf_exempt
def search_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("message", "").strip()
            api_key = data.get("api_key") or request.headers.get("Authorization", "").replace("Bearer ", "")

            if not query:
                return JsonResponse({"error": "Empty message"}, status=400)
            if not api_key:
                return JsonResponse({"error": "Missing API Key"}, status=400)

            site = Website.objects.filter(api_key=api_key).first()
            if not site:
                return JsonResponse({"error": "Invalid API Key"}, status=403)

            if not request.session.get('chat_session_id'):
                request.session['chat_session_id'] = str(uuid.uuid4())
            session_id = request.session['chat_session_id']

            # Save prompt without user
            chat_message = ChatMessage.objects.create(
                user=None,
                website=site,
                session_id=session_id,
                prompt=query.strip(),
                response=""
            )

            # Generate response
            ai_output = generate_text_response(query, site.id, session_id=session_id)
            response_text, image_names = generate_graphs_from_response(ai_output or "")

            # Update response
            chat_message.response = response_text.strip()
            chat_message.save()

            return JsonResponse({
                "reply": response_text,
                "image_urls": [request.build_absolute_uri(f"/media/{img}") for img in image_names] if image_names else []
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST method required."}, status=405)

def test(request):
    return render(request, "test.html")

def test1(request):
    return render(request, "test1.html")

def validate_key(request):
    api_key = request.GET.get('api_key')
    try:
        site = Website.objects.get(api_key=api_key)
        return JsonResponse({'status': 'valid', 'site': site.domain})
    except Website.DoesNotExist:
        return JsonResponse({'status': 'invalid'}, status=403)

def generate_graphs_from_response(response_text):
    code_blocks = re.findall(r"```python(.*?)```", response_text, re.DOTALL)
    cleaned_text = re.sub(r"```python.*?```", "", response_text, flags=re.DOTALL).strip()
    image_urls = []

    for i, code in enumerate(code_blocks):
        try:
            image_name = f"graph_{uuid.uuid4().hex}_{i}.png"
            image_path = os.path.join(BASE_DIR, "media", image_name)
            image_path = image_path.replace("\\", "/")  # Fix for Windows

            # Remove plt.show() if present
            code = code.replace("plt.show()", "")

            # Set figure size for better display
            plt.figure(figsize=(8, 6))

            # Run the code
            exec_globals = {"plt": plt}
            exec_locals = {}
            exec(code, exec_globals, exec_locals)

            # Save the figure
            plt.savefig(image_path, dpi=100, bbox_inches='tight')
            plt.close()

            if os.path.exists(image_path):
                print(f"[✅] Graph saved to: {image_path}")
                image_urls.append(image_name)
            else:
                print(f"[❌] Graph file not found: {image_path}")

        except Exception as e:
            print(f"[❌] Failed to render graph {i}: {e}")

    return cleaned_text, image_urls



@csrf_exempt
def process_ingestion(request, file_id):
    print("✅ process_ingestion view called")  # Diagnostic print

    ingested_file = get_object_or_404(IngestedFile, id=file_id)
    website_id = ingested_file.website.id

    input_path = ""
    if ingested_file.file:
        input_path = ingested_file.file.path
    elif ingested_file.url:
        input_path = ingested_file.url
    else:
        return redirect('/admin/research/website/')

    try:
        script_path = os.path.join('core', 'ingestion', 'ingest_to_db.py')
        subprocess.run([sys.executable, script_path, input_path, str(website_id)], check=True)
        ingested_file.processed = True
        ingested_file.save()
    except Exception as e:
        print(f"Ingestion failed: {e}")

    return redirect(f'/admin/research/website/{website_id}/change/')

from django.shortcuts import render, redirect
from .models import Website, IngestedFile
from django.contrib import messages

def bulk_upload_view(request, website_id):
    website = Website.objects.get(id=website_id)

    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            ingested_file = IngestedFile.objects.create(website=website, file=f, processed=False)

            # ✅ Immediately call the ingestion process
            try:
                script_path = os.path.join('core', 'ingestion', 'ingest_to_db.py')
                input_path = ingested_file.file.path
                subprocess.run([sys.executable, script_path, input_path, str(website_id)], check=True)
                ingested_file.processed = True
                ingested_file.save()
            except Exception as e:
                print(f"[❌] Ingestion failed for {f.name}: {e}")

        return JsonResponse({"status": "done"})

    return render(request, 'admin/bulk_upload.html', {'website': website})
