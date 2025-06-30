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
            prompt_chain = recent_prompts + "\n" + current_query.strip()

    # 🔁 Now generate chunks based on short-term history
    context_chunks = get_relevant_chunks(prompt_chain, site_id)

    final_prompt = f"""
You are a market research assistant be interactive. Answer clearly based on the following context and cumulative question thread only.

Relevant documents:
{context_chunks}

Cumulative question thread:
{prompt_chain}

suggest follow up questions.
only answer for the last cumulative thread based on previous thread if more than one cumulative thread.
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
@csrf_exempt
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

            # Now generate response
            response_text = generate_text_response(query, site.id, session_id=session_id) or "No answer generated."

            # Update the ChatMessage with response
            chat_message.response = response_text.strip()
            chat_message.save()

            return JsonResponse({
                "reply": response_text,
                "need_user_info": user is None
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
@csrf_exempt
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

            # Save prompt first without response
            chat_message = ChatMessage.objects.create(
                user=None,
                website=site,
                session_id=session_id,
                prompt=query.strip(),
                response=""
            )

            # Now generate response
            response_text = generate_text_response(query, site.id, session_id=session_id)

            # Update response
            chat_message.response = response_text.strip()
            chat_message.save()

            return JsonResponse({"reply": response_text})

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