/**
 * LegacyLens Chat Interface
 * POSTs to /api/knowledge/agent/chat/ and renders responses.
 */

(function () {
  "use strict";

  const messagesEl = document.getElementById("chat-messages");
  const inputEl    = document.getElementById("chat-input");
  const sendBtn    = document.getElementById("send-btn");

  if (!messagesEl || !inputEl || !sendBtn) return;

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addBubble(text, role, sources) {
    const div = document.createElement("div");
    div.className = `chat-bubble ${role}`;

    const label = document.createElement("div");
    label.className = "bubble-label";
    label.textContent = role === "user" ? "You" : "LegacyLens";
    div.appendChild(label);

    const p = document.createElement("p");
    p.style.whiteSpace = "pre-wrap";
    p.textContent = text;
    div.appendChild(p);

    if (sources && sources.length > 0) {
      const sourcesDiv = document.createElement("div");
      sourcesDiv.className = "sources";
      sourcesDiv.innerHTML = `<strong>Sources (${sources.length}):</strong><br>` +
        sources.map((s, i) => `${i + 1}. ${s.content || s}`).join("<br>");
      div.appendChild(sourcesDiv);
    }

    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
  }

  function addTypingIndicator() {
    const div = document.createElement("div");
    div.className = "typing-indicator";
    div.id = "typing-indicator";
    div.innerHTML = "<span></span><span></span><span></span>";
    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
  }

  async function sendMessage() {
    const query = inputEl.value.trim();
    if (!query) return;

    // Clear input, disable send
    inputEl.value = "";
    sendBtn.disabled = true;
    inputEl.style.height = "44px";

    // Show user message
    addBubble(query, "user");

    // Show typing indicator
    const typing = addTypingIndicator();

    try {
      const resp = await fetch("/api/knowledge/agent/chat/", {
        method:  "POST",
        headers: {
          "Content-Type":  "application/json",
          "X-CSRFToken":   getCsrfToken(),
        },
        body: JSON.stringify({ query }),
      });

      typing.remove();

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const data = await resp.json();

      if (data.status === "ok" && data.data) {
        addBubble(data.data.answer || "(no answer)", "agent", data.data.sources || []);
      } else {
        addBubble("Sorry, I couldn't process that. " + (data.message || ""), "agent");
      }
    } catch (err) {
      typing.remove();
      addBubble(`Error: ${err.message}. Please check the server.`, "agent");
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  // Send on button click
  sendBtn.addEventListener("click", sendMessage);

  // Send on Enter (Shift+Enter = newline)
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  inputEl.addEventListener("input", () => {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + "px";
  });

  scrollToBottom();
})();
