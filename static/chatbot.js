window.initChatbot = function (apiKey) {
  const baseURL = "http://127.0.0.1:8000";
  let userRegistered = false;
  let shownForm = false;
  let isTyping = false;

  const container = document.getElementById("chatbot-container");
  
  container.innerHTML = `
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

      #chatbot-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 60px;
        height: 60px;
        background: linear-gradient(to right, #3b82f6, #2563eb);
        color: #ffffff;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 9999;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      #chatbot-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }

      #chatbot-button svg {
        width: 30px;
        height: 30px;
      }

      #chatbot-box {
        position: fixed;
        bottom: 100px;
        right: 24px;
        width: 360px;
        max-height: 80vh;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        z-index: 10000;
        transform: translateY(20px);
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease-out;
      }

      #chatbot-box.visible {
        transform: translateY(0);
        opacity: 1;
        visibility: visible;
      }

      #chatbot-header {
        background: linear-gradient(to right, #3b82f6, #2563eb);
        color: #ffffff;
        padding: 16px 20px;
        font-weight: 600;
        font-size: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
      }

      #chatBox {
        padding: 16px;
        height: 300px;
        overflow-y: auto;
        background: #f9fafb;
        scroll-behavior: smooth;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .message-row {
        display: flex;
        align-items: flex-start;
        margin-bottom: 12px;
        animation: fadeIn 0.2s ease-in;
      }

      .message-row.user {
        justify-content: flex-end;
        flex-direction: row-reverse;
      }

      .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        margin: 0 10px;
        object-fit: cover;
        border: 2px solid #e5e7eb;
        transition: transform 0.2s ease;
      }

      .avatar:hover {
        transform: scale(1.1);
      }

      .message {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 15px;
        line-height: 1.5;
        position: relative;
      }

      .user .message {
        background: #d1fae5;
        color: #111827;
        border-bottom-right-radius: 4px;
      }

      .bot .message {
        background: #e0e7ff;
        color: #111827;
        border-bottom-left-radius: 4px;
      }

      #chatbot-input {
        display: flex;
        border-top: 1px solid #e5e7eb;
        background: #ffffff;
        padding: 12px;
        box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
      }

      #query {
        flex: 1;
        padding: 12px;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        font-size: 15px;
        outline: none;
        transition: border-color 0.2s ease;
      }

      #query:focus {
        border-color: #3b82f6;
      }

      #submitBtn {
        background: #3b82f6;
        color: #ffffff;
        border: none;
        padding: 0 20px;
        border-radius: 10px;
        cursor: pointer;
        transition: background-color 0.2s ease;
        font-size: 16px;
        margin-left: 8px;
        display: flex;
        align-items: center;
      }

      #submitBtn:hover:not(:disabled) {
        background: #2563eb;
      }

      #submitBtn:disabled {
        background: #bfdbfe;
        cursor: not-allowed;
      }

      .typing {
        display: flex;
        align-items: center;
        color: #6b7280;
        margin-left: 46px;
        margin-bottom: 10px;
        font-size: 14px;
        font-style: italic;
      }

      .typing::after {
        content: '•••';
        animation: pulse 1.5s infinite;
        margin-left: 4px;
      }

      .user-form {
        padding: 16px;
        background: #fefce8;
        border-radius: 12px;
        margin: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.3s ease-in;
      }

      .user-form h4 {
        margin: 0 0 12px;
        font-size: 16px;
        font-weight: 600;
        color: #1f2937;
      }

      .user-form input {
        width: 100%;
        padding: 10px;
        margin-bottom: 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s ease;
      }

      .user-form input:focus {
        border-color: #3b82f6;
      }

      .user-form button {
        width: 100%;
        background: #10b981;
        color: #ffffff;
        padding: 12px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 15px;
        transition: background-color 0.2s ease;
      }

      .user-form button:hover {
        background: #059669;
      }

      @keyframes slideIn {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
      }

      @media (max-width: 480px) {
        #chatbot-box {
          width: 90vw;
          bottom: 90px;
          right: 12px;
        }

        #chatbot-button {
          bottom: 20px;
          right: 20px;
        }

        #chatBox {
          height: 250px;
        }

        .message {
          font-size: 14px;
        }
      }
    </style>

    <div id="chatbot-button">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    </div>

    <div id="chatbot-box">
      <div id="chatbot-header">🤖 AI Market Research Assistant</div>
      <div id="chatBox"></div>
      <div id="chatbot-input">
        <input type="text" id="query" placeholder="Ask about market trends..." />
        <button id="submitBtn">➤</button>
      </div>
    </div>
  `;

  const chatBox = document.getElementById("chatBox");
  const queryInput = document.getElementById("query");
  const submitBtn = document.getElementById("submitBtn");
  const chatbotButton = document.getElementById("chatbot-button");
  const chatbotBox = document.getElementById("chatbot-box");
  const chatbotHeader = document.getElementById("chatbot-header");

  // Toggle chatbot visibility when button is clicked
  chatbotButton.addEventListener("click", function(e) {
    e.stopPropagation();
    chatbotBox.classList.toggle("visible");
  });

  // Close chatbot when clicking outside
  document.addEventListener("click", function(e) {
    if (!chatbotBox.contains(e.target)){
      chatbotBox.classList.remove("visible");
    }
  });

  // Prevent closing when clicking inside the chatbot
  chatbotBox.addEventListener("click", function(e) {
    e.stopPropagation();
  });

  submitBtn.addEventListener("click", handleSend);
  queryInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  });

  function handleSend() {
    const query = queryInput.value.trim();
    if (!query || isTyping) return;
    sendPrompt(query);
    queryInput.value = "";
  }

  function sendPrompt(message) {
    addMessage("user", message);
    showTyping();
    isTyping = true;
    submitBtn.disabled = true;

    fetch(`${baseURL}/api/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, api_key: apiKey }),
      credentials: "include",
    })
      .then((res) => {
        console.log("Chat API response status:", res.status);
        return res.json();
      })
      .then((data) => {
        removeTyping();
        addMessage("bot", data.reply || "(No reply)");
        if (!userRegistered && !shownForm && data.need_user_info) {
          shownForm = true;
          showUserForm();
        }
      })
      .catch((err) => {
        removeTyping();
        console.error("Chat API error:", err);
        addMessage("bot", "Error: Unable to get response.");
      })
      .finally(() => {
        isTyping = false;
        submitBtn.disabled = false;
      });
  }

  function addMessage(sender, text) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const avatar = document.createElement("img");
    avatar.className = "avatar";
    avatar.src = sender === "user" ? "/static/user.jpg" : "/static/assistant.jpg";
    avatar.alt = sender;
    avatar.onerror = () => {
      avatar.src = `https://ui-avatars.com/api/?name=${sender}&background=${sender === "user" ? "d1fae5" : "e0e7ff"}&color=111827`;
    };

    const bubble = document.createElement("div");
    bubble.className = `message ${sender}`;
    bubble.innerHTML = `<p>${text}</p>`;

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function showTyping() {
    const typing = document.createElement("div");
    typing.id = "typing";
    typing.className = "typing";
    typing.innerText = "Assistant is typing";
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function removeTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
  }

  function showUserForm() {
    const formDiv = document.createElement("div");
    formDiv.className = "user-form";
    formDiv.innerHTML = `
      <h4>Tell us about yourself</h4>
      <input type="text" id="name" placeholder="Name*" required />
      <input type="email" id="email" placeholder="Email*" required />
      <input type="text" id="company" placeholder="Company Name" />
      <input type="text" id="mobile" placeholder="Mobile Number" />
      <button id="submit-btn">Submit</button>
    `;
    chatBox.appendChild(formDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    document.getElementById("submit-btn").addEventListener("click", submitDetails);
  }

  function submitDetails() {
    const payload = {
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      company_name: document.getElementById("company").value.trim(),
      mobile_number: document.getElementById("mobile").value.trim(),
    };

    if (!payload.name || !payload.email) {
      return alert("Please enter required fields.");
    }

    console.log("Sending user details to /api/user/:", payload);
    fetch(`${baseURL}/api/user/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    })
      .then((res) => {
        console.log("User API response status:", res.status, "Headers:", res.headers);
        return res.json();
      })
      .then((data) => {
        console.log("User API response data:", data);
        if (data.status === "saved") {
          userRegistered = true;
          alert("Success: Details saved!");
          document.querySelector(".user-form").remove();
        } else {
          alert("Error: " + (data.error || "Unknown error"));
        }
      })
      .catch((err) => {
        console.error("Error saving details:", err);
        alert("Failed to save details. Please try again.");
      });
  }
};