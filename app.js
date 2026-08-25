const toothCodes = ["M3", "M2", "M1", "P2", "P1", "C", "L", "I", "I", "L", "C", "P1", "P2", "M1", "M2", "M3"];
const state = { arch: "upper", view: "profile", size: 72 };
const rows = [
  { arch: "upper", view: "profile", title: "Arco superior — perfil (maiúsculas)" },
  { arch: "upper", view: "occlusal", title: "Arco superior — face / vista oclusal (minúsculas)" },
  { arch: "lower", view: "occlusal", title: "Arco inferior — face / vista oclusal (minúsculas)" },
  { arch: "lower", view: "profile", title: "Arco inferior — perfil (maiúsculas)" }
];
function fileName(arch, view, index, code) {
  return `assets/reference-vectors/${arch}-${view}-${String(index + 1).padStart(2, "0")}-${code.toLowerCase()}.svg`;
}
function displayCode(code, view) { return view === "occlusal" ? code.toLowerCase() : code; }
function cellMarkup(arch, view, index, code) {
  const label = displayCode(code, view);
  return `<span class="glyph-cell"><span class="glyph-box"><img src="${fileName(arch, view, index, code)}" alt="${label}" width="100" height="180"></span><span class="glyph-code">${label}</span></span>`;
}
function standardPosition(code, side) {
  const half = side === "left" ? toothCodes.slice(0, 8) : toothCodes.slice(8);
  const localIndex = half.indexOf(code);
  if (localIndex < 0) return side === "left" ? 0 : 15;
  return side === "left" ? localIndex : localIndex + 8;
}
function parseSequence(value) {
  const allowed = new Set(["I", "L", "C", "P1", "P2", "M1", "M2", "M3", "|"]);
  return value.toUpperCase().replace(/\s*\|\s*/g, " | ").trim().split(/\s+/).filter(token => allowed.has(token));
}
function renderLive() {
  const tokens = parseSequence(document.querySelector("#sequence").value);
  const dividerIndex = tokens.indexOf("|");
  const teethOnly = tokens.filter(token => token !== "|");
  const fallbackCenter = Math.ceil(teethOnly.length / 2);
  let seenTeeth = 0;
  const row = document.querySelector("#live-arch");
  row.className = `glyph-row live-row ${state.view}`;
  row.style.setProperty("--glyph-size", `${state.size}px`);
  row.innerHTML = tokens.map((token, tokenIndex) => {
    if (token === "|") return '<span class="midline" aria-hidden="true"></span>';
    const side = dividerIndex >= 0 ? (tokenIndex < dividerIndex ? "left" : "right") : (seenTeeth < fallbackCenter ? "left" : "right");
    const position = standardPosition(token, side);
    seenTeeth++;
    return cellMarkup(state.arch, state.view, position, token);
  }).join("");
  const archLabel = state.arch === "upper" ? "superior" : "inferior";
  const viewLabel = state.view === "profile" ? "perfil" : "face / vista oclusal";
  document.querySelector("#preview-title").textContent = `Arco ${archLabel} — ${viewLabel}`;
  document.querySelector("#position-count").textContent = `${teethOnly.length} posições`;
}
function renderReferenceRows() {
  document.querySelector("#reference-rows").innerHTML = rows.map(row => `<section class="reference-row"><h3 class="row-title">${row.title}</h3><div class="glyph-row ${row.view}">${toothCodes.map((code, index) => cellMarkup(row.arch, row.view, index, code)).join("")}</div></section>`).join("");
}
document.querySelectorAll(".button-group").forEach(group => {
  group.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!button) return;
    group.querySelectorAll("button").forEach(item => {
      item.classList.toggle("active", item === button);
      item.setAttribute("aria-pressed", item === button ? "true" : "false");
    });
    state[group.dataset.control] = button.dataset.value;
    renderLive();
  });
});
document.querySelector("#glyph-size").addEventListener("input", event => {
  state.size = Number(event.target.value);
  document.querySelector("#size-value").value = `${state.size} px`;
  renderLive();
});
document.querySelector("#apply").addEventListener("click", renderLive);
document.querySelector("#sequence").addEventListener("keydown", event => { if (event.key === "Enter") renderLive(); });
renderReferenceRows();
renderLive();
