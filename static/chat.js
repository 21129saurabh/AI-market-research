// let userRegistered = false;
// let shownPopup = false;

// document.getElementById("submitBtn").addEventListener("click", function(event) {
//     event.preventDefault();

//     const query = document.getElementById("query").value.trim();
//     if (!query) {
//         alert("Please enter a question.");
//         return;
//     }

//     sendPrompt(query);
//     document.getElementById("query").value = "";
// });

// function sendPrompt(message) {
//     addMessage("user", message);

//     fetch("/api/chat/", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message }),
//     })
//     .then((res) => res.json())
//     .then((data) => {
//         if (data.reply) {
//             addMessage("bot", data.reply);
//         } else {
//             addMessage("bot", "(No reply received)");
//         }

//         if (!userRegistered && !shownPopup) {
//             shownPopup = true;
//             document.getElementById("userPopup").style.display = "block";
//         }
//     })
//     .catch((error) => {
//         console.error("Error fetching chat response:", error);
//         addMessage("bot", "Error: Unable to get response.");
//     });
// }

// function addMessage(sender, text) {
//     const chatBox = document.getElementById("chatBox");
//     const msgDiv = document.createElement("div");
//     msgDiv.className = sender === "user" ? "message user" : "message bot";
//     msgDiv.innerHTML = `<p>${text}</p>`;
//     chatBox.appendChild(msgDiv);
//     chatBox.scrollTop = chatBox.scrollHeight;
// }

// document.getElementById("submitDetailsBtn").addEventListener("click", function(event) {
//     event.preventDefault();
//     submitDetails();
// });

// function submitDetails() {
//     const name = document.getElementById("name").value.trim();
//     const email = document.getElementById("email").value.trim();
//     const company_name = document.getElementById("company").value.trim();
//     const mobile_number = document.getElementById("mobile").value.trim();

//     if (!name || !email) {
//         alert("Please fill in required fields: Name and Email.");
//         return;
//     }

//     const payload = { name, email, company_name, mobile_number };

//     fetch("/api/user/", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(payload),
//     })
//     .then((res) => res.json())
//     .then((data) => {
//         userRegistered = true;
//         document.getElementById("userPopup").style.display = "none";
//         alert("Thank you! Your details are saved.");
//     })
//     .catch((error) => {
//         console.error("Error submitting user details:", error);
//         alert("Failed to submit details. Please try again.");
//     });
// }
const apiKey = window.CHATBOT_API_KEY || null;
let userRegistered = false;
let shownForm = false;
console.log("📡 Using API Key:", apiKey);

document
  .getElementById("submitBtn")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const query = document.getElementById("query").value.trim();
    if (!query) {
      alert("Please enter a question.");
      return;
    }

    sendPrompt(query);
    document.getElementById("query").value = "";
  });

function sendPrompt(message) {
  addMessage("user", message);

  fetch("/api/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    credentials: "same-origin", // <-- Added here
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.reply) {
        addMessage("bot", data.reply);
      } else {
        addMessage("bot", "(No reply received)");
      }

      // Show form only if backend says user info is needed and form is not already shown
      if (!userRegistered && !shownForm && data.need_user_info) {
        shownForm = true;
        showUserForm();
      } else {
        console.log(
          "No form shown. Reasons:",
          "userRegistered:",
          userRegistered,
          "shownForm:",
          shownForm,
          "need_user_info:",
          data.need_user_info
        );
      }
    })
    .catch((error) => {
      console.error("Error fetching chat response:", error);
      addMessage("bot", "Error: Unable to get response.");
    });
}

function addMessage(sender, text) {
  const chatBox = document.getElementById("chatBox");
  const msgDiv = document.createElement("div");
  msgDiv.className = sender === "user" ? "message user" : "message bot";
  msgDiv.innerHTML = `<p>${text}</p>`;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showUserForm() {
  const chatBox = document.getElementById("chatBox");

  const formDiv = document.createElement("div");
  formDiv.className = "user-form";

  formDiv.innerHTML = `
        <h4>Tell us about yourself</h4>
        <input type="text" id="name" placeholder="Name*" required />
        <input type="email" id="email" placeholder="Email*" required />
        <input type="text" id="company" placeholder="Company" />
        <input type="text" id="mobile" placeholder="Mobile" />
        <button id="submitDetailsBtn">Submit</button>
    `;

  chatBox.appendChild(formDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  document
    .getElementById("submitDetailsBtn")
    .addEventListener("click", function (event) {
      event.preventDefault();
      submitDetails();
    });
}

function submitDetails() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const company_name = document.getElementById("company").value.trim();
  const mobile_number = document.getElementById("mobile").value.trim();

  if (!name || !email) {
    alert("Please fill in required fields: Name and Email.");
    return;
  }

  const payload = { name, email, company_name, mobile_number };

  fetch("/api/user/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "same-origin", // <-- Added here
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("Server response:", data);
      if (data.status === "saved") {
        userRegistered = true;
        alert("Thank you! Your details are saved.");
        const form = document.querySelector(".user-form");
        if (form) form.remove(); // remove form after submission
      } else if (data.error) {
        alert("Error: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Error submitting user details:", error);
      alert("Failed to submit details. Please try again.");
    });
}
