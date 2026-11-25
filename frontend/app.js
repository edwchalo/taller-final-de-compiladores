const API_URL = "http://127.0.0.1:5000/api/compile";

const DEFAULT_CODE = `a = 10
b = 5
resultado = (a + b) * 2`;

const sourceInput = document.getElementById("source");
const compileBtn = document.getElementById("compile-btn");
const clearBtn = document.getElementById("clear-btn");
const globalStatus = document.getElementById("global-status");

sourceInput.value = DEFAULT_CODE;

compileBtn.addEventListener("click", compileCode);
clearBtn.addEventListener("click", clearAll);

function clearAll() {
  sourceInput.value = "";
  hideStatus();
  document.querySelectorAll(".card").forEach((card) => {
    card.classList.remove("ok", "error", "skipped");
    const title = card.querySelector("h2");
    title.textContent = title.textContent.replace(/^[✓✗•]\s/, "");
    card.querySelector(".card-body").textContent = "Esperando compilación.";
  });
}

async function compileCode() {
  hideStatus();
  compileBtn.disabled = true;
  compileBtn.textContent = "Compilando...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: sourceInput.value }),
    });
    const data = await response.json();
    renderResult(data);
  } catch (error) {
    showStatus(
      "No se pudo conectar con el backend. ¿Está en marcha python backend/app.py?",
      true
    );
  } finally {
    compileBtn.disabled = false;
    compileBtn.textContent = "Compilar";
  }
}

function renderResult(data) {
  const phases = data.phases || {};
  renderLexical(phases.lexical);
  renderSyntax(phases.syntax);
  renderSemantic(phases.semantic);
  renderIntermediate(phases.intermediate);
  renderOptimization(phases.optimization);
  renderAssembly(phases.assembly);

  if (data.success) {
    showStatus("Compilación correcta.", false);
    return;
  }

  const error = data.error || {};
  showStatus(error.description || error.type || "Fallo en la compilación.", true);
}

function renderLexical(phase) {
  if (!markCard("lexical", phase)) {
    return;
  }
  if (phase.status === "error") {
    setBody("lexical", "✗ ERROR LÉXICO");
    return;
  }
  const items = (phase.tokens || [])
    .map((token) => `<li>${escapeHtml(token.type)} → ${escapeHtml(String(token.value))}</li>`)
    .join("");
  setBody("lexical", items ? `<ul class="token-list">${items}</ul>` : "No se encontraron tokens.");
}

function renderSyntax(phase) {
  if (!markCard("syntax", phase)) {
    return;
  }
  if (phase.status === "error") {
    setBody("syntax", "✗ ERROR SINTÁCTICO");
    return;
  }
  setBody("syntax", `<pre>${escapeHtml(phase.tree || "")}</pre>`);
}

function renderSemantic(phase) {
  if (!markCard("semantic", phase)) {
    return;
  }
  if (phase.status === "error") {
    setBody("semantic", "✗ ERROR SEMÁNTICO");
    return;
  }
  const rows = (phase.symbol_table || [])
    .map(
      (item) =>
        `<li>${escapeHtml(item.name)} (línea ${escapeHtml(String(item.declared_at_line))})</li>`
    )
    .join("");
  setBody(
    "semantic",
    rows
      ? `<p>Tabla de símbolos</p><ul class="symbol-list">${rows}</ul>`
      : "No hay variables declaradas."
  );
}

function renderIntermediate(phase) {
  if (!markCard("intermediate", phase)) {
    return;
  }
  setBody("intermediate", `<pre>${escapeHtml((phase.code || []).join("\n"))}</pre>`);
}

function renderOptimization(phase) {
  if (!markCard("optimization", phase)) {
    return;
  }
  const applied = (phase.applied || [])
    .map(
      (item) =>
        `<li><strong>${escapeHtml(item.technique)}</strong>: ${escapeHtml(item.before)} → ${escapeHtml(item.after)}</li>`
    )
    .join("");
  setBody(
    "optimization",
    `
      <p>Código antes de optimizar</p>
      <pre>${escapeHtml((phase.before || []).join("\n"))}</pre>
      <p>Código después de optimizar</p>
      <pre>${escapeHtml((phase.after || []).join("\n"))}</pre>
      ${applied ? `<p>Técnicas utilizadas</p><ul class="opt-list">${applied}</ul>` : "<p>No se aplicaron optimizaciones.</p>"}
    `
  );
}

function renderAssembly(phase) {
  if (!markCard("assembly", phase)) {
    return;
  }
  setBody(
    "assembly",
    `
      <p class="architecture">${escapeHtml(phase.architecture || "")}</p>
      <pre>${escapeHtml((phase.code || []).join("\n"))}</pre>
    `
  );
}

function markCard(phaseKey, phase) {
  const card = document.querySelector(`[data-phase="${phaseKey}"]`);
  const title = card.querySelector("h2");
  const cleanTitle = title.textContent.replace(/^[✓✗•]\s/, "");
  card.classList.remove("ok", "error", "skipped");

  if (!phase || phase.status === "skipped") {
    card.classList.add("skipped");
    title.textContent = `• ${cleanTitle}`;
    setBody(phaseKey, "No ejecutada: la compilación se detuvo en una fase anterior.");
    return false;
  }

  if (phase.status === "error") {
    card.classList.add("error");
    title.textContent = `✗ ${cleanTitle}`;
    return true;
  }

  card.classList.add("ok");
  title.textContent = `✓ ${cleanTitle}`;
  return true;
}

function setBody(phaseKey, html) {
  document.querySelector(`[data-phase="${phaseKey}"] .card-body`).innerHTML = html;
}

function showStatus(message, isError) {
  globalStatus.hidden = false;
  globalStatus.textContent = message;
  globalStatus.className = "global-status " + (isError ? "error" : "ok");
}

function hideStatus() {
  globalStatus.hidden = true;
  globalStatus.textContent = "";
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
