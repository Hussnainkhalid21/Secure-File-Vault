<div align="center">

# 🔐 Secure File Vault

### A full-stack cryptography & file-security toolkit built with Flask

*Seven security tools, one clean dashboard — encrypt, sign, hash, and inspect files entirely in your browser.*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Cryptography](https://img.shields.io/badge/cryptography-42.0.8-FF6B6B?style=for-the-badge&logo=letsencrypt&logoColor=white)](https://cryptography.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[![AES-256-GCM](https://img.shields.io/badge/AES--256--GCM-Authenticated_Encryption-blue?style=flat-square)](#)
[![RSA-2048](https://img.shields.io/badge/RSA--2048-Digital_Signatures-purple?style=flat-square)](#)
[![PBKDF2](https://img.shields.io/badge/PBKDF2-390k_iterations-orange?style=flat-square)](#)
[![NIST](https://img.shields.io/badge/NIST-Compliant-success?style=flat-square)](#)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#%EF%B8%8F-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Feature Deep Dive](#-feature-deep-dive)
- [API Reference](#-api-reference)
- [Security Design Decisions](#%EF%B8%8F-security-design-decisions)
- [License](#-license)

---

## 🎯 Overview

**Secure File Vault** is a full-stack web application that brings together **seven cryptographic and security-analysis tools** in a single-page dashboard. Users can encrypt, decrypt, sign, hash, and inspect files entirely through their browser — all heavy cryptographic work runs server-side in Python using the [`cryptography`](https://cryptography.io/) library maintained by the Python Cryptographic Authority.

> **Built as a semester project** demonstrating real-world cryptographic primitives (AES-256-GCM, RSA-2048, PBKDF2-HMAC) and threat-aware file inspection (RTLO detection, archive analysis, filename scoring).

---

## ✨ Features

<table>
<tr>
<th width="80">#</th>
<th>Feature</th>
<th>Core Technology</th>
<th>What It Does</th>
</tr>
<tr>
<td align="center">🔒</td>
<td><b>File Encryption</b></td>
<td><code>AES-256-GCM + PBKDF2</code></td>
<td>Password-based authenticated encryption</td>
</tr>
<tr>
<td align="center">🔓</td>
<td><b>File Decryption</b></td>
<td><code>AES-256-GCM</code></td>
<td>Decrypt with tamper-detection</td>
</tr>
<tr>
<td align="center">✍️</td>
<td><b>Digital Signatures</b></td>
<td><code>RSA-2048 + PKCS#1v15</code></td>
<td>Sign & verify file authenticity</td>
</tr>
<tr>
<td align="center">#️⃣</td>
<td><b>Hash Generator</b></td>
<td><code>SHA-256 / SHA-512</code></td>
<td>Compute digests with chunked reads</td>
</tr>
<tr>
<td align="center">✅</td>
<td><b>Integrity Checker</b></td>
<td><code>Hash comparison</code></td>
<td>Detect file modification</td>
</tr>
<tr>
<td align="center">📦</td>
<td><b>Compressed File Checker</b></td>
<td><code>zipfile / tarfile</code></td>
<td>Inspect archives without extraction</td>
</tr>
<tr>
<td align="center">🕵️</td>
<td><b>Obfuscated File Checker</b></td>
<td><code>Filename pattern analysis</code></td>
<td>Detect RTLO, double extensions, spoofing</td>
</tr>
</table>

---



**Design principle:** Each security feature lives in its own module. You can open any single file and understand one feature without reading anything else.

---

## 🛠️ Tech Stack

### Backend

| Library | Version | Purpose |
|---|---|---|
| **Python** | 3.11 | Runtime |
| **Flask** | 3.0.3 | Web framework, REST API |
| **cryptography** | 42.0.8 | AES-GCM, RSA, PBKDF2 primitives |
| **Werkzeug** | 3.0.3 | Secure filename handling |

### Frontend

| Technology | Purpose |
|---|---|
| **HTML5** | Single-page dashboard structure |
| **CSS3** | Dark-blue cybersecurity theme, responsive layout |
| **Vanilla JS** | Fetch API, dynamic panels, drag-and-drop uploads |

### Python Standard Library (zero install)

`hashlib` · `zipfile` · `tarfile` · `os.urandom` · `base64`

> **Why Flask over Django?** Flask is minimal and explicit — every route is a plain Python function you can read line by line. For a security project where transparency matters, Flask is the right choice.

---

## 📁 Project Structure

```
secure-file-vault/
│
├── main.py                       # Flask app entry point + all API routes
├── requirements.txt              # Python dependencies (3 packages)
├── README.md
│
├── modules/                      # One Python file per security feature
│   ├── encryption.py             # AES-256-GCM encryption
│   ├── decryption.py             # AES-256-GCM decryption
│   ├── digital_signature.py      # RSA-2048: key gen, sign, verify
│   ├── hash_generator.py         # SHA-256 / SHA-512 (chunked reads)
│   ├── integrity_checker.py      # Hash comparison
│   ├── compressed_checker.py     # ZIP / TAR inspection
│   └── obfuscated_checker.py     # Filename risk scoring
│
├── templates/
│   └── index.html                # Single-page dashboard
│
├── static/
│   ├── css/style.css             # Dark-blue cybersecurity theme
│   └── js/script.js              # Frontend logic
│
├── uploads/                      # Temporary uploaded files
├── outputs/                      # Encrypted / decrypted outputs
└── keys/                         # RSA PEM key pair storage
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.9+**
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Hussnainkhalid21/secure-file-vault.git
cd secure-file-vault

# 2. Install the three Python dependencies
pip install -r requirements.txt

# 3. Start the Flask server
python main.py
```

Open **`http://localhost:24331`** in your browser. 🎉

### First-time usage checklist

- [ ] **Generate RSA keys first** → Digital Signature → Step 1 → Generate Keys
- [ ] **Encrypt → Decrypt round-trip** → Encrypt any file, decrypt the `.enc` output with the same password
- [ ] **Integrity test** → Hash a file, then modify it slightly — the checker should flag it as MODIFIED

---

## 🔬 Feature Deep Dive

<details>
<summary><b>🔒 Feature 1 — File Encryption (AES-256-GCM)</b></summary>

<br>

Encrypts any file using **AES-256-GCM** — the same cipher used by TLS 1.3, WhatsApp, and Signal.

**Step 1 — Generate random salt and nonce**

```python
salt  = os.urandom(16)  # 16 bytes = 128 bits
nonce = os.urandom(12)  # 12 bytes = 96 bits (GCM standard)
```

Both come from the OS cryptographic random number generator. They are unique per encryption — encrypting the same file twice produces completely different output.

**Step 2 — Derive AES key via PBKDF2-HMAC-SHA256**

```python
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,              # 256 bits → AES-256
    salt=salt,
    iterations=390_000,     # NIST recommended minimum for 2023
)
key = kdf.derive(password.encode("utf-8"))
```

The raw password is **never** used as the AES key. PBKDF2 stretches it through 390,000 SHA-256 iterations, making brute-force dictionary attacks extremely slow.

**Step 3 — Encrypt with AES-256-GCM**

```python
aesgcm     = AESGCM(key)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)
```

**Step 4 — Output file layout**

```
[16-byte salt][12-byte nonce][ciphertext + 16-byte GCM tag]
```

Everything needed to decrypt is stored in the file itself. The salt and nonce aren't secret — they're random values, not key material.

**Security properties**

| Property | Guarantee |
|---|---|
| 🔐 Confidentiality | Only the correct password decrypts the file |
| 🛡️ Authentication | Any modification is detected during decryption |
| 🎲 Uniqueness | Every encryption produces unique output |

</details>

<details>
<summary><b>🔓 Feature 2 — File Decryption</b></summary>

<br>

Decryption reverses the encryption exactly:

1. Read first 16 bytes → `salt`
2. Read next 12 bytes → `nonce`
3. The rest → `ciphertext + GCM tag`
4. Re-derive the AES key using PBKDF2 (same 390,000 iterations)
5. Decrypt and verify with AES-GCM

```python
try:
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
except InvalidTag:
    raise ValueError("Incorrect password or the file has been tampered with.")
```

**Wrong password handling:** GCM fails to verify the auth tag and raises `InvalidTag`. There is no silent failure — either correct plaintext, or a clear error.

</details>

<details>
<summary><b>✍️ Feature 3 — Digital Signatures (RSA-2048)</b></summary>

<br>

A digital signature proves two things:

- **Authenticity** — the file was signed by the holder of the private key
- **Integrity** — the file has not been modified since it was signed

**Step 1 — Generate RSA-2048 key pair**

```python
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()
```

**Step 2 — Sign a file**

```python
signature = private_key.sign(
    file_data,
    padding.PKCS1v15(),
    hashes.SHA256(),
)
```

**Step 3 — Verify a signature**

```python
try:
    public_key.verify(signature, file_data, padding.PKCS1v15(), hashes.SHA256())
    return True   # File is original
except InvalidSignature:
    return False  # File has been modified
```

**Symmetric vs. Asymmetric Cryptography**

| | Symmetric (AES) | Asymmetric (RSA) |
|---|---|---|
| **Keys** | One key | Two keys (public + private) |
| **Speed** | Very fast | Slower |
| **Use case** | Encrypting data | Signatures, key exchange |
| **Example** | AES-256-GCM | RSA-2048, ECDSA |

</details>

<details>
<summary><b>#️⃣ Feature 4 — Hash Generator</b></summary>

<br>

Maps any input to a fixed-size digest with four properties:

- **Deterministic** — same file → same hash
- **Avalanche effect** — flipping 1 bit changes ~50% of output bits
- **One-way** — impossible to reverse
- **Collision-resistant** — infeasible to find two files with the same hash

**SHA-256 vs SHA-512**

| Algorithm | Output | Use case |
|---|---|---|
| **SHA-256** | 64 hex chars | Standard — Bitcoin, TLS, code signing |
| **SHA-512** | 128 hex chars | Higher security margin |

**Chunked reading for huge files**

```python
CHUNK_SIZE = 65536  # 64 KB per read
with open(file_path, "rb") as f:
    while chunk := f.read(CHUNK_SIZE):
        sha256.update(chunk)
        sha512.update(chunk)
```

Multi-gigabyte files can be hashed without loading them into RAM.

</details>

<details>
<summary><b>✅ Feature 5 — File Integrity Checker</b></summary>

<br>

The user provides a file and its original hash. The server recomputes and compares.

**Auto-detection:** SHA-256 hashes are 64 characters, SHA-512 are 128 — the algorithm is detected automatically from the hash length.

**Real-world use case:** Linux distros and software publishers publish SHA-256 hashes alongside downloads. Users verify the file hasn't been tampered with in transit.

</details>

<details>
<summary><b>📦 Feature 6 — Compressed File Checker</b></summary>

<br>

**Threat model**

| Threat | Example | Risk |
|---|---|---|
| Double extension | `invoice.pdf.exe` | Windows shows `.pdf` but runs `.exe` |
| Executable inside archive | `setup.bat` | Script executes system commands |
| Nested archive | `payload.zip` inside `archive.zip` | Hides content from 1-level scanners |
| Path traversal | `../../etc/passwd` | Extraction overwrites system files |

**Safe inspection without extraction**

```python
with zipfile.ZipFile(file_path, "r") as zf:
    for info in zf.infolist():
        analyse_entry(info.filename)  # only reads the name, not the data
```

The checker **never executes, extracts, or reads** the content of any file inside the archive.

</details>

<details>
<summary><b>🕵️ Feature 7 — Obfuscated File Checker</b></summary>

<br>

Analyses the **filename only** (no file content is read). Each detected issue adds points:

| Issue | Points | Example |
|---|---:|---|
| Executable final extension | +40 | `document.exe` |
| Double-extension spoofing | +30 | `photo.jpg.exe` |
| RTLO Unicode character (U+202E) | +35 | Visually reverses the filename |
| Very long filename (>100 chars) | +20 | Hides real extension at the end |
| Excessive whitespace | +25 | `file.pdf     .exe` |
| Base64-looking stem | +15 | `aGVsbG8gd29ybGQ=` |
| No extension at all | +10 | `mystery_payload` |

**Risk levels**

- 🔴 Score ≥ 50 → **High** — Do not open
- 🟡 Score ≥ 20 → **Medium** — Scan before opening
- 🟢 Score < 20 → **Low** — Appears normal

**The RTLO trick (U+202E):** This Unicode character forces text to display right-to-left. Attackers craft filenames like `document[U+202E]gpj.exe` which Windows Explorer renders as `documentexe.jpg` — while the actual extension is `.exe`.

</details>

---

## 🌐 API Reference

All routes accept `multipart/form-data` and return JSON.

| Method | Route | Form Fields | Response |
|---|---|---|---|
| `POST` | `/encrypt` | `file`, `password` | `download_url`, `output_file` |
| `POST` | `/decrypt` | `file`, `password` | `download_url` or `error` |
| `POST` | `/generate-keys` | — | `public_key`, `private_key` |
| `POST` | `/sign` | `file` | `signature_b64`, `download_url` |
| `POST` | `/verify-signature` | `file`, `signature_b64` | `valid` (bool), `message` |
| `POST` | `/generate-hash` | `file` | `sha256`, `sha512`, `file_size` |
| `POST` | `/check-integrity` | `file`, `original_hash` | `match` (bool), `current_hash`, `status` |
| `POST` | `/check-compressed` | `file` | `entries[]`, `warnings[]`, `safe_to_extract` |
| `POST` | `/check-obfuscated` | `filename` or `file` | `risk_level`, `score`, `flags[]` |
| `GET`  | `/download/<filename>` | — | File stream (attachment) |

---

## 🛡️ Security Design Decisions

> Every choice in this project has a reason. Here are the important ones.

### 🔑 Password is never stored

The user's password is immediately passed through PBKDF2 (390,000 iterations) and discarded. Only the derived 256-bit key is used. The salt required to re-derive the key is stored inside the encrypted file.

### 🎲 Every encryption is unique

Both the `salt` and `nonce` are generated from `os.urandom()` for every encryption. This prevents **nonce-reuse attacks** — if the same nonce were used twice with the same key in GCM mode, an attacker could XOR the two ciphertexts to recover both plaintexts.

### 🛡️ Authenticated encryption prevents tampering

AES-GCM appends a 16-byte authentication tag. Any modification to the ciphertext — even a single bit flip — causes decryption to fail with an `InvalidTag` error. It is **mathematically impossible** to modify an encrypted file and have it decrypt successfully.

### 📁 Secure filename handling

All uploaded filenames are sanitised with `werkzeug.utils.secure_filename` before disk write — preventing path traversal.

```
Input:  ../../etc/passwd
Output: etc_passwd           ← safe
```

### 📏 Upload size limit

```python
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024   # 50 MB
```

Requests exceeding this are rejected with HTTP 413 before the file is read into memory.

---

## 📦 Requirements

```
flask==3.0.3
cryptography==42.0.8
werkzeug==3.0.3
```

Just **three dependencies**. Everything else is from Python's standard library.

---

## 📜 License

Released under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

### Built with 🔐 by [Muhammad Hussnain](https://github.com/Hussnainkhalid21)

*Cybersecurity undergraduate · HITEC University Taxila*

[![GitHub](https://img.shields.io/badge/GitHub-Hussnainkhalid21-181717?style=for-the-badge&logo=github)](https://github.com/Hussnainkhalid21)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/hussnain-khalid-793480354)

⭐ If you found this useful, consider giving it a star!

</div>
