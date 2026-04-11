const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatMessages = document.getElementById("chatMessages");
const clearBtn = document.getElementById("clearBtn");
const showCitations = document.getElementById("showCitations");
const sendBtn = document.getElementById("sendBtn");

const conversation = [];

function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 180) + "px";
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderSimpleMarkdown(text) {
  let safe = escapeHtml(text);

  // bold
  safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // inline code
  safe = safe.replace(/`([^`]+)`/g, "<code>$1</code>");

  // split into blocks
  const blocks = safe.split(/\n\s*\n/);

  return blocks
    .map(block => {
      const trimmed = block.trim();
      if (!trimmed) return "";

      // bullet list support
      const lines = trimmed.split("\n");
      const isList = lines.every(line => line.trim().startsWith("- ") || line.trim().startsWith("* "));
      if (isList) {
        const items = lines
          .map(line => line.replace(/^[-*]\s+/, "").trim())
          .map(item => `<li>${item}</li>`)
          .join("");
        return `<ul>${items}</ul>`;
      }

      // normal paragraph with line breaks
      return `<p>${lines.join("<br>")}</p>`;
    })
    .join("");
}

function createCitationBlock(citations) {
  if (!citations || citations.length === 0) return null;

  const details = document.createElement("details");
  details.className = "citation-box";

  const summary = document.createElement("summary");
  summary.textContent = "Sources";
  details.appendChild(summary);

  const list = document.createElement("div");
  list.className = "citation-list";
  list.innerHTML = citations.map(c => `<div class="citation-item">${escapeHtml(c)}</div>`).join("");

  details.appendChild(list);
  return details;
}

function addMessage(role, text, citations = []) {
  const row = document.createElement("div");
  row.className = `message ${role}`;

  if (role === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "AI";
    row.appendChild(avatar);
  }

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role === "user" ? "user-bubble" : "assistant-bubble"}`;

  if (role === "assistant") {
    bubble.innerHTML = renderSimpleMarkdown(text);

    if (showCitations.checked) {
      const citationBlock = createCitationBlock(citations);
      if (citationBlock) bubble.appendChild(citationBlock);
    }
  } else {
    bubble.textContent = text;
  }

  content.appendChild(bubble);
  row.appendChild(content);
  chatMessages.appendChild(row);
  scrollToBottom();
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "message assistant";
  row.id = "typingRow";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "AI";

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "bubble assistant-bubble typing-bubble";
  bubble.textContent = "Thinking...";

  content.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(content);

  chatMessages.appendChild(row);
  scrollToBottom();
}

function removeTyping() {
  const row = document.getElementById("typingRow");
  if (row) row.remove();
}

function buildContextMessage(currentMessage) {
  const recent = conversation.slice(-2);

  if (recent.length === 0) return currentMessage;

  let context = "Conversation so far:\n";
  for (const msg of recent) {
    const role = msg.role === "user" ? "User" : "Assistant";
    context += `${role}: ${msg.text}\n`;
  }
  context += `\nCurrent user question:\n${currentMessage}`;
  return context;
}

async function sendMessage(text) {
  addMessage("user", text);
  conversation.push({ role: "user", text });

  addTyping();
  sendBtn.disabled = true;

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: buildContextMessage(text)
      })
    });

    const data = await response.json();
    removeTyping();

    const answer = data.answer || "I could not generate an answer.";
    const citations = data.citations || [];

    addMessage("assistant", answer, citations);
    conversation.push({ role: "assistant", text: answer, citations });
  } catch (error) {
    removeTyping();
    addMessage("assistant", "Something went wrong while contacting the server.");
  } finally {
    sendBtn.disabled = false;
    messageInput.focus();
  }
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const text = messageInput.value.trim();
  if (!text) return;

  messageInput.value = "";
  autoResizeTextarea();
  await sendMessage(text);
});

messageInput.addEventListener("input", autoResizeTextarea);

messageInput.addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

    messageInput.value = "";
    autoResizeTextarea();
    await sendMessage(text);
  }
});

clearBtn.addEventListener("click", () => {
  conversation.length = 0;
  chatMessages.innerHTML = `
    <div class="message assistant">
      <div class="avatar">AI</div>
      <div class="message-content">
        <div class="bubble assistant-bubble">
          <p>Hi! I can help you understand company 10-K filings, compare businesses, and summarize risks in plain English.</p>
        </div>
      </div>
    </div>
  `;
});

showCitations.addEventListener("change", () => {
  // affects new answers only
});

autoResizeTextarea();