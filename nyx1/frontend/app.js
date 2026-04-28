// API Base URL
// Local file preview uses localhost:5000.
// On Vercel full-stack deploys, window.location.origin is the correct API host.
const API_BASE =
  window.location.protocol === "file:"
    ? "http://localhost:5000"
    : (window.API_BASE_URL || window.location.origin);

const API_URL = `${API_BASE}/api/chat/send`;

const messagesEl = document.querySelector("#messages");
const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const statusEl = document.querySelector("#status");
const canvas = document.querySelector("#voiceCanvas");
const ctx = canvas.getContext("2d");

const history = [];

function addMessage(role, content, meta = "") {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  article.innerHTML = `
    <span class="sender">${role === "user" ? "You" : "NYXX Mind"}${meta ? ` - ${meta}` : ""}</span>
    <p></p>
  `;
  article.querySelector("p").textContent = content;
  messagesEl.appendChild(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatus(message) {
  statusEl.textContent = message;
}

async function sendMessage(message) {
  addMessage("user", message);
  history.push({ role: "user", content: message });
  setStatus("NYXX is thinking...");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        history: history.slice(-5),
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    addMessage("assistant", data.response, data.crisis ? "crisis support" : data.emotion);
    history.push({ role: "assistant", content: data.response });
    setStatus(data.crisis ? "Crisis support mode active." : "");
  } catch (error) {
    addMessage(
      "assistant",
      "I could not reach the backend. Start the Python server on port 5000, then try again."
    );
    setStatus(error.message);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  sendMessage(message);
});

document.querySelectorAll("[data-open-chat]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector(".chat-stage").scrollIntoView({ behavior: "smooth", block: "start" });
    input.focus();
  });
});

document.querySelectorAll("[data-open-voice]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector(".voice-screen").scrollIntoView({ behavior: "smooth", block: "center" });
  });
});

document.querySelectorAll("[data-back-home]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector(".home-screen").scrollIntoView({ behavior: "smooth", block: "center" });
  });
});

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.sample;
    document.querySelector(".chat-stage").scrollIntoView({ behavior: "smooth", block: "start" });
    input.focus();
  });
});

function drawVoice(tick) {
  const width = canvas.width;
  const height = canvas.height;
  const cx = width / 2;
  const cy = height / 2;

  ctx.clearRect(0, 0, width, height);
  ctx.save();
  ctx.translate(cx, cy);

  for (let layer = 0; layer < 7; layer += 1) {
    ctx.beginPath();
    const points = 150;
    const base = 54 + layer * 8;

    for (let i = 0; i <= points; i += 1) {
      const angle = (Math.PI * 2 * i) / points;
      const pulse =
        Math.sin(angle * 5 + tick / 620 + layer) * 14 +
        Math.cos(angle * 3 - tick / 760) * 10 +
        Math.sin(tick / 420 + layer) * 5;
      const radius = base + pulse;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius * 0.78;

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    const hue = layer % 3 === 0 ? "289" : layer % 3 === 1 ? "183" : "113";
    ctx.strokeStyle = `hsla(${hue}, 100%, 66%, ${0.48 - layer * 0.04})`;
    ctx.lineWidth = 1.2;
    ctx.stroke();
  }

  const glow = ctx.createRadialGradient(0, 0, 10, 0, 0, 76);
  glow.addColorStop(0, "rgba(156, 255, 143, 0.28)");
  glow.addColorStop(0.48, "rgba(154, 105, 255, 0.18)");
  glow.addColorStop(1, "rgba(105, 241, 255, 0)");
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 0, 86, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
  requestAnimationFrame(drawVoice);
}

requestAnimationFrame(drawVoice);
