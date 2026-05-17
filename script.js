/**
 * script.js — Secure File Vault
 * Handles panel switching, form submissions, and result rendering.
 */

// ── Panel Navigation ──────────────────────────────────────────────────────────

const navButtons = document.querySelectorAll(".nav-btn");
const panels = document.querySelectorAll(".panel");
const topbarTitle = document.getElementById("topbar-title");

function switchPanel(panelId) {
  panels.forEach(p => p.classList.remove("active"));
  navButtons.forEach(b => b.classList.remove("active"));

  const target = document.getElementById(panelId);
  if (target) target.classList.add("active");

  const btn = document.querySelector(`[data-panel="${panelId}"]`);
  if (btn) {
    btn.classList.add("active");
    topbarTitle.textContent = btn.querySelector(".label")?.textContent || "Secure File Vault";
  }
}

navButtons.forEach(btn => {
  btn.addEventListener("click", () => switchPanel(btn.dataset.panel));
});

// ── File Drop Zones ───────────────────────────────────────────────────────────

document.querySelectorAll(".file-drop").forEach(zone => {
  const input = zone.querySelector("input[type='file']");
  const nameEl = zone.querySelector(".file-name");

  if (input) {
    input.addEventListener("change", () => {
      if (input.files[0]) nameEl.textContent = input.files[0].name;
    });
  }

  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("drag-over"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    if (input && e.dataTransfer.files[0]) {
      input.files = e.dataTransfer.files;
      nameEl.textContent = e.dataTransfer.files[0].name;
    }
  });
});

// ── Result Box Helpers ────────────────────────────────────────────────────────

function showResult(boxId, html, type = "info") {
  const box = document.getElementById(boxId);
  box.innerHTML = html;
  box.className = `result-box visible ${type}`;
}

function loadingHtml(msg = "Processing…") {
  return `<div class="result-header info"><span class="spinner"></span> ${msg}</div>`;
}

function errorHtml(msg) {
  return `<div class="result-header error">⚠ Error</div><p class="text-muted">${escapeHtml(msg)}</p>`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function downloadBtn(url, label) {
  return `<a href="${url}" download class="btn btn-success btn-sm mt-12">⬇ ${label}</a>`;
}

// ── Generic POST (FormData) ───────────────────────────────────────────────────

async function postForm(url, formData) {
  const res = await fetch(url, { method: "POST", body: formData });
  return res.json();
}

// ── Copy to Clipboard ─────────────────────────────────────────────────────────

function copyText(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = "✓ Copied!";
    setTimeout(() => (btn.textContent = orig), 2000);
  });
}

// ── 1. Encryption ─────────────────────────────────────────────────────────────

document.getElementById("encrypt-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "encrypt-result";
  showResult(box, loadingHtml("Encrypting file…"));

  const fd = new FormData(e.target);
  const data = await postForm("/encrypt", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  showResult(box, `
    <div class="result-header success">✔ Encryption Successful</div>
    <p class="text-muted">${escapeHtml(data.message)}</p>
    <p class="text-muted mt-8">Output file: <span class="mono">${escapeHtml(data.output_file)}</span></p>
    ${downloadBtn(data.download_url, "Download Encrypted File")}
  `, "success");
});

// ── 2. Decryption ─────────────────────────────────────────────────────────────

document.getElementById("decrypt-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "decrypt-result";
  showResult(box, loadingHtml("Decrypting file…"));

  const fd = new FormData(e.target);
  const data = await postForm("/decrypt", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  showResult(box, `
    <div class="result-header success">✔ Decryption Successful</div>
    <p class="text-muted">${escapeHtml(data.message)}</p>
    ${downloadBtn(data.download_url, "Download Decrypted File")}
  `, "success");
});

// ── 3. Digital Signature — Generate Keys ──────────────────────────────────────

document.getElementById("keygen-btn").addEventListener("click", async () => {
  const box = "sig-result";
  showResult(box, loadingHtml("Generating RSA-2048 key pair…"));

  const data = await postForm("/generate-keys", new FormData());

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  // Store public key globally for copy button
  window._pubKey = data.public_key;
  window._privKey = data.private_key;

  showResult(box, `
    <div class="result-header success">✔ Keys Generated</div>
    <div class="mt-8">
      <p class="text-small" style="margin-bottom:4px">PUBLIC KEY</p>
      <div class="key-box" id="pub-key-box">${escapeHtml(data.public_key)}</div>
      <button class="btn btn-outline btn-sm" onclick="copyText(window._pubKey, this)">⧉ Copy Public Key</button>
    </div>
    <div class="mt-12">
      <p class="text-small" style="margin-bottom:4px">PRIVATE KEY (keep secret!)</p>
      <div class="key-box" id="priv-key-box">${escapeHtml(data.private_key)}</div>
      <button class="btn btn-outline btn-sm" onclick="copyText(window._privKey, this)">⧉ Copy Private Key</button>
    </div>
  `, "success");
});

// ── 3. Digital Signature — Sign File ─────────────────────────────────────────

document.getElementById("sign-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "sig-result";
  showResult(box, loadingHtml("Signing file…"));

  const fd = new FormData(e.target);
  const data = await postForm("/sign", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  window._sigB64 = data.signature_b64;

  showResult(box, `
    <div class="result-header success">✔ File Signed</div>
    <div class="hash-row mt-8">
      <span class="hash-label">SIG</span>
      <span class="hash-value">${escapeHtml(data.signature_b64)}</span>
    </div>
    <div class="flex gap-8 flex-wrap mt-8">
      <button class="btn btn-outline btn-sm" onclick="copyText(window._sigB64, this)">⧉ Copy Signature</button>
      ${downloadBtn(data.download_url, "Download .sig File")}
    </div>
  `, "success");
});

// ── 3. Digital Signature — Verify ────────────────────────────────────────────

document.getElementById("verify-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "sig-result";
  showResult(box, loadingHtml("Verifying signature…"));

  const fd = new FormData(e.target);
  const data = await postForm("/verify-signature", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  const type = data.valid ? "success" : "error";
  const icon = data.valid ? "✔" : "✘";
  const cls  = data.valid ? "success" : "error";

  showResult(box, `
    <div class="result-header ${cls}">${icon} Verification Result</div>
    <p class="text-muted">${escapeHtml(data.message)}</p>
  `, type);
});

// ── 4. Hash Generator ─────────────────────────────────────────────────────────

document.getElementById("hash-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "hash-result";
  showResult(box, loadingHtml("Computing hashes…"));

  const fd = new FormData(e.target);
  const data = await postForm("/generate-hash", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  window._sha256 = data.sha256;
  window._sha512 = data.sha512;

  const size = data.file_size < 1024
    ? `${data.file_size} B`
    : data.file_size < 1048576
    ? `${(data.file_size / 1024).toFixed(1)} KB`
    : `${(data.file_size / 1048576).toFixed(2)} MB`;

  showResult(box, `
    <div class="result-header info">⬡ Hash Results — ${escapeHtml(data.filename)} (${size})</div>
    <div class="hash-row">
      <span class="hash-label">SHA-256</span>
      <span class="hash-value" id="sha256-val">${escapeHtml(data.sha256)}</span>
    </div>
    <button class="btn btn-outline btn-sm" onclick="copyText(window._sha256, this)">⧉ Copy SHA-256</button>
    <div class="hash-row mt-12">
      <span class="hash-label">SHA-512</span>
      <span class="hash-value" id="sha512-val">${escapeHtml(data.sha512)}</span>
    </div>
    <button class="btn btn-outline btn-sm" onclick="copyText(window._sha512, this)">⧉ Copy SHA-512</button>
  `, "success");
});

// ── 5. Integrity Checker ──────────────────────────────────────────────────────

document.getElementById("integrity-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "integrity-result";
  showResult(box, loadingHtml("Checking integrity…"));

  const fd = new FormData(e.target);
  const data = await postForm("/check-integrity", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  const type = data.match ? "success" : "error";
  const icon = data.match ? "✔" : "✘";
  const cls  = data.match ? "success" : "error";

  showResult(box, `
    <div class="result-header ${cls}">${icon} ${escapeHtml(data.status)}</div>
    <p class="text-small mt-8">Algorithm: ${escapeHtml(data.algorithm)}</p>
    <div class="hash-row mt-8">
      <span class="hash-label">Current</span>
      <span class="hash-value">${escapeHtml(data.current_hash)}</span>
    </div>
    <div class="hash-row">
      <span class="hash-label">Provided</span>
      <span class="hash-value">${escapeHtml(data.original_hash)}</span>
    </div>
  `, type);
});

// ── 6. Compressed File Checker ────────────────────────────────────────────────

document.getElementById("compressed-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "compressed-result";
  showResult(box, loadingHtml("Inspecting archive…"));

  const fd = new FormData(e.target);
  const data = await postForm("/check-compressed", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  const overallType = data.safe_to_extract ? "success" : "warning";
  const overallIcon = data.safe_to_extract ? "✔" : "⚠";
  const overallMsg  = data.safe_to_extract
    ? "Archive appears safe to extract."
    : "Archive contains suspicious files — review before extracting!";

  let warningsHtml = "";
  if (data.warnings.length > 0) {
    warningsHtml = `<ul class="flag-list mt-12">${data.warnings.map(w => `<li>${escapeHtml(w)}</li>`).join("")}</ul>`;
  }

  let tableRows = data.entries.slice(0, 200).map(entry => {
    const rowCls = entry.risks.includes("executable extension") ? "dangerous"
                 : entry.suspicious ? "suspicious" : "";
    const risks = entry.risks.length ? `<span style="color:var(--warning)">${escapeHtml(entry.risks.join(", "))}</span>` : `<span style="color:var(--success)">Clean</span>`;
    const size = entry.original_size < 1048576
      ? `${(entry.original_size / 1024).toFixed(1)} KB`
      : `${(entry.original_size / 1048576).toFixed(2)} MB`;
    return `<tr class="${rowCls}"><td>${escapeHtml(entry.name)}</td><td>${escapeHtml(entry.extension || "—")}</td><td>${size}</td><td>${risks}</td></tr>`;
  }).join("");

  showResult(box, `
    <div class="result-header ${overallType === "success" ? "success" : "warning"}">${overallIcon} ${overallMsg}</div>
    <p class="text-muted mt-8">Format: <b>${escapeHtml(data.format.toUpperCase())}</b> &nbsp;|&nbsp; Total files: <b>${data.total_files}</b> &nbsp;|&nbsp; Suspicious: <b style="color:${data.suspicious_count > 0 ? 'var(--warning)' : 'var(--success)'}">${data.suspicious_count}</b></p>
    ${warningsHtml}
    <table class="file-table mt-12">
      <thead><tr><th>File Name</th><th>Ext</th><th>Size</th><th>Status</th></tr></thead>
      <tbody>${tableRows}</tbody>
    </table>
    ${data.total_files > 200 ? `<p class="text-small mt-8">Showing first 200 of ${data.total_files} entries.</p>` : ""}
  `, overallType);
});

// ── 7. Obfuscated File Checker ────────────────────────────────────────────────

document.getElementById("obfuscated-form").addEventListener("submit", async e => {
  e.preventDefault();
  const box = "obfuscated-result";
  showResult(box, loadingHtml("Analysing filename…"));

  const fd = new FormData(e.target);
  const data = await postForm("/check-obfuscated", fd);

  if (data.error) return showResult(box, errorHtml(data.error), "error");

  const riskClass = `risk-${data.risk_level.toLowerCase()}`;
  const flagItems = data.flags.map(f =>
    f.includes("No suspicious") ? `<li class="ok">${escapeHtml(f)}</li>` : `<li>${escapeHtml(f)}</li>`
  ).join("");

  showResult(box, `
    <div class="result-header info">⬡ Obfuscation Analysis</div>
    <p class="text-muted mt-8">Filename: <span class="mono">${escapeHtml(data.filename)}</span></p>
    <div class="mt-12 flex gap-8" style="align-items:center">
      <span>Risk Level:</span>
      <span class="risk-badge ${riskClass}">${escapeHtml(data.risk_level)}</span>
      <span class="text-small">(Score: ${data.score})</span>
    </div>
    <ul class="flag-list mt-12">${flagItems}</ul>
    <p class="text-muted mt-12"><b>Recommendation:</b> ${escapeHtml(data.recommendation)}</p>
  `, data.risk_level === "High" ? "error" : data.risk_level === "Medium" ? "warning" : "success");
});

// ── Initialise ────────────────────────────────────────────────────────────────
switchPanel("panel-encrypt");
