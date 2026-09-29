const $ = (id) => document.getElementById(id);
const drop = $("drop"), file = $("file"), preview = $("preview"), hint = $("hint");
const form = $("form"), qWrap = $("q-wrap"), question = $("question"), go = $("go");
const result = $("result"), meta = $("meta"), status = $("status");

let current = null;

function show(text, kind = "") {
  result.textContent = text;
  result.className = kind;
  meta.textContent = "";
}

function setImage(f) {
  if (!f || !f.type.startsWith("image/")) {
    return show("Elegí un archivo de imagen (JPG, PNG o WEBP).", "error");
  }
  if (preview.src) URL.revokeObjectURL(preview.src);
  current = f;
  preview.src = URL.createObjectURL(f);
  preview.hidden = false;
  hint.hidden = true;
  go.disabled = false;
  show("Listo. Elegí un modo y tocá Analizar imagen.", "empty");
}

file.addEventListener("change", () => setImage(file.files[0]));

["dragenter", "dragover"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); })
);
["dragleave", "drop"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); })
);
drop.addEventListener("drop", (e) => setImage(e.dataTransfer.files[0]));

form.addEventListener("change", (e) => {
  if (e.target.name !== "mode") return;
  const asking = form.mode.value === "ask";
  qWrap.hidden = !asking;
  if (asking) question.focus();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!current) return;

  const asking = form.mode.value === "ask";
  const q = question.value.trim();
  if (asking && !q) return show("Escribí una pregunta sobre la imagen.", "error");

  const body = new FormData();
  body.append("image", current);
  if (asking) body.append("question", q);

  go.disabled = true;
  show("Analizando…", "loading");
  try {
    const res = await fetch("/api/analyze", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Ocurrió un error inesperado.");
    show(data.text);
    meta.textContent = `Respondió en ${data.seconds} s usando ${data.device}`;
  } catch (err) {
    show(err.message, "error");
  } finally {
    go.disabled = false;
  }
});

fetch("/api/health")
  .then((r) => r.json())
  .then((d) => { status.textContent = `Modelo ${d.model} corriendo en ${d.device}`; })
  .catch(() => { status.textContent = "No se pudo conectar con el modelo."; });
