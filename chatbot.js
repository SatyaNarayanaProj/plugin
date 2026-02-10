(function () {
  // Prevent double load
  if (window.AIChatbotLoaded) return;
  window.AIChatbotLoaded = true;

  /* ---------------- CSS ---------------- */
  const style = document.createElement("style");
  style.innerHTML = `
/* Floating chat button */
#ai-chat-button {
  position: fixed;
  bottom: 20px;
  right: 20px;

  width: 56px;
  height: 56px;
  border-radius: 50%;

  background: #1a73e8;
  color: white;
  font-size: 26px;

  display: flex;
  align-items: center;
  justify-content: center;

  cursor: pointer;
  z-index: 2147483647;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}

/* Chat widget */
#ai-chat-widget {
  position: fixed;
  bottom: 90px;
  right: 20px;

  width: 360px;
  height: 500px;

  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);

  display: flex;
  flex-direction: column;

  z-index: 2147483647;
  overflow: hidden;
}

/* Hide widget */
.hidden {
  display: none !important;
}

/* Header */
#ai-chat-header {
  height: 48px;
  padding: 0 14px;

  background: #1a73e8;
  color: white;
  font-weight: 600;

  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Close button */
#ai-chat-close {
  cursor: pointer;
  font-size: 18px;
}

/* Messages */
#ai-chat-messages {
  flex: 1;
  padding: 14px;
  overflow-y: auto;
}

/* Input */
#ai-chat-input {
  display: flex;
  border-top: 1px solid #eee;
}

#ai-chat-input input {
  flex: 1;
  border: none;
  padding: 12px;
  outline: none;
}

#ai-chat-input button {
  background: #1a73e8;
  color: white;
  border: none;
  padding: 0 18px;
  cursor: pointer;
}

/* Messages */
.ai-msg {
  margin-bottom: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  max-width: 80%;
}

.ai-user {
  background: #1a73e8;
  color: white;
  margin-left: auto;
}

.ai-bot {
  background: #f1f3f4;
  color: #222;
  margin-right: auto;
}


  `;
  document.head.appendChild(style);

  /* ---------------- HTML ---------------- */
const widget = document.createElement("div");
widget.innerHTML = `
  <div id="ai-chat-button">💬</div>

  <div id="ai-chat-widget" class="hidden">
    <div id="ai-chat-header">
      AI Assistant
      <span id="ai-chat-close">✕</span>
    </div>

    <div id="ai-chat-messages"></div>

    <div id="ai-chat-input">
      <input type="text" placeholder="Ask me anything..." />
      <button>Send</button>
    </div>
  </div>
`;
document.documentElement.appendChild(widget);

const chatButton = widget.querySelector("#ai-chat-button");
const chatWidget = widget.querySelector("#ai-chat-widget");
const closeBtn = widget.querySelector("#ai-chat-close");

if (!chatButton || !chatWidget || !closeBtn) {
  console.error("Chat toggle elements not found");
}

chatButton.addEventListener("click", () => {
  chatWidget.classList.remove("hidden");
  chatButton.style.display = "none";

  // focus input when opened
  const input = chatWidget.querySelector("input");
  if (input) input.focus();
});

closeBtn.addEventListener("click", () => {
  chatWidget.classList.add("hidden");
  chatButton.style.display = "flex";
});



  const messagesEl = widget.querySelector("#ai-chat-messages");
const inputEl = widget.querySelector("input");
const sendBtn = widget.querySelector("button");

let history = [
  { role: "assistant", content: "Hi 👋 How can I help you today?" }
];

let isSending = false; // 🔒 SEND LOCK

/* ---------------- Helpers ---------------- */
function escapeHTML(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function format(text) {
  const safe = escapeHTML(text);
  return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

function render() {
  messagesEl.innerHTML = "";

  history.forEach(m => {
    const div = document.createElement("div");
    div.className = `ai-msg ${m.role === "user" ? "ai-user" : "ai-bot"}`;
    div.innerHTML = format(m.content);
    messagesEl.appendChild(div);
  });

  // Always scroll to bottom safely
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

/* ---------------- Send ---------------- */
async function send() {
  if (isSending) return; // 🔒 prevent double send

  const text = inputEl.value.trim();
  if (!text) return;

  isSending = true;
  sendBtn.disabled = true;
  inputEl.disabled = true;

  history.push({ role: "user", content: text });
  inputEl.value = "";
  render();

  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history })
    });

    const data = await res.json();
    history.push({ role: "assistant", content: data.reply });

  } catch {
    history.push({
      role: "assistant",
      content: "Sorry, something went wrong."
    });
  }

  render();

  // 🔓 unlock
  isSending = false;
  sendBtn.disabled = false;
  inputEl.disabled = false;
  inputEl.focus();
}

/* ---------------- Events ---------------- */
sendBtn.onclick = send;

inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

/* ---------------- Initial render ---------------- */
render();
})();
