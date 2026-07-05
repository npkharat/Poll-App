/*
 * TIER 1: PRESENTATION LAYER — JAVASCRIPT
 * Only displays data and forwards input to the API.
 * All vote counting and percentage math happens in the Application tier.
 */

/* =========================
   CONFIG
========================= */

// Local dev:
// const API_BASE_URL = "http://localhost:5000";

// Kubernetes / ingress (same-origin):
// const API_BASE_URL = "";

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "";

/* =========================
   HELPERS
========================= */

const el = (id) => document.getElementById(id);

function joinUrl(base, path) {
  if (!base) return path;
  return `${base.replace(/\/$/, "")}${path}`;
}

async function api(path, options = {}) {
  const res = await fetch(joinUrl(API_BASE_URL, path), {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  let body;
  try {
    body = await res.json();
  } catch {
    body = { error: "Invalid JSON response from server" };
  }

  if (!res.ok) {
    throw new Error(body.error || "Request failed");
  }

  return body;
}

/* =========================
   UI HELPERS
========================= */

function showBanner(msg, isError = false) {
  const b = el("banner");
  b.textContent = msg;
  b.className = `banner ${isError ? "error" : ""}`;
  b.style.display = "block";

  setTimeout(() => {
    b.style.display = "none";
  }, 2500);
}

/* =========================
   POLL RENDERING
========================= */

function renderPoll(poll) {
  const card = document.createElement("div");
  card.className = "poll-card";

  const header = document.createElement("div");
  header.className = "poll-header";

  header.innerHTML = `
    <div>
      <p class="poll-question">${poll.question}</p>
      <p class="poll-meta">${poll.total_votes} vote${poll.total_votes === 1 ? "" : "s"}</p>
    </div>
  `;

  const delBtn = document.createElement("button");
  delBtn.className = "del-poll-btn";
  delBtn.textContent = "🗑";
  delBtn.title = "Delete poll";
  delBtn.onclick = () => deletePoll(poll.id);

  header.appendChild(delBtn);
  card.appendChild(header);

  poll.options.forEach((opt) => {
    const row = document.createElement("div");
    row.className = "option-row";

    row.onclick = () => castVote(poll.id, opt.id);

    row.innerHTML = `
      <div class="option-top">
        <span class="option-name ${opt.is_leading ? "leading" : ""}">
          ${opt.option_text}
        </span>
        <span class="option-stats">
          ${opt.percentage}% (${opt.votes})
        </span>
      </div>
      <div class="bar-track">
        <div class="bar-fill ${opt.is_leading ? "leading" : ""}" style="width:0%"></div>
      </div>
    `;

    card.appendChild(row);

    requestAnimationFrame(() => {
      const bar = row.querySelector(".bar-fill");
      if (bar) bar.style.width = `${opt.percentage}%`;
    });
  });

  return card;
}

/* =========================
   DATA
========================= */

async function loadPolls() {
  const polls = await api("/api/polls");

  const grid = el("pollGrid");
  grid.innerHTML = "";

  el("emptyState").style.display = polls.length ? "none" : "block";

  polls.forEach((p) => {
    grid.appendChild(renderPoll(p));
  });
}

async function castVote(pollId, optionId) {
  try {
    await api(`/api/polls/${pollId}/vote`, {
      method: "POST",
      body: JSON.stringify({ option_id: optionId }),
    });

    await loadPolls();
  } catch (err) {
    showBanner(err.message, true);
  }
}

async function deletePoll(pollId) {
  if (!confirm("Delete this poll?")) return;

  try {
    await api(`/api/polls/${pollId}`, { method: "DELETE" });
    await loadPolls();
  } catch (err) {
    showBanner(err.message, true);
  }
}

/* =========================
   MODAL / CREATE POLL
========================= */

function addOptionField(value = "") {
  const row = document.createElement("div");
  row.className = "option-input-row";

  row.innerHTML = `
    <input type="text" class="option-input" placeholder="Option text" value="${value}" maxlength="200">
    <button type="button" class="remove-option-btn">✕</button>
  `;

  row.querySelector(".remove-option-btn").onclick = () => {
    if (el("optionsList").children.length > 2) {
      row.remove();
    }
  };

  el("optionsList").appendChild(row);
}

function openModal() {
  el("questionInput").value = "";
  el("optionsList").innerHTML = "";

  addOptionField();
  addOptionField();

  el("formError").style.display = "none";
  el("modalOverlay").classList.add("open");
}

function closeModal() {
  el("modalOverlay").classList.remove("open");
}

/* =========================
   EVENTS
========================= */

el("newPollBtn").onclick = openModal;
el("cancelBtn").onclick = closeModal;

el("addOptionBtn").onclick = () => {
  if (el("optionsList").children.length < 8) {
    addOptionField();
  }
};

el("modalOverlay").addEventListener("click", (e) => {
  if (e.target.id === "modalOverlay") closeModal();
});

el("pollForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = el("questionInput").value.trim();
  const options = Array.from(document.querySelectorAll(".option-input"))
    .map((i) => i.value.trim())
    .filter(Boolean);

  try {
    await api("/api/polls", {
      method: "POST",
      body: JSON.stringify({ question, options }),
    });

    closeModal();
    await loadPolls();

    showBanner("Poll created!");
  } catch (err) {
    const box = el("formError");
    box.textContent = err.message;
    box.style.display = "block";
  }
});

/* =========================
   INIT
========================= */

loadPolls();
