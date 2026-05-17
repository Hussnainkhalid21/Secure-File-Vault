# Secure File Vault

A full-stack cybersecurity toolkit built with Python Flask. Provides a single-page dashboard for file encryption, decryption, digital signatures, hash generation, integrity checking, and archive/filename inspection.

## Features

| Feature | Description |
|---|---|
| **File Encryption** | AES-256-GCM encryption with PBKDF2-HMAC key derivation |
| **File Decryption** | Decrypts vault-encrypted files; reports wrong password clearly |
| **Digital Signatures** | RSA-2048 key generation, file signing, and signature verification |
| **Hash Generator** | SHA-256 and SHA-512 with one-click copy |
| **Integrity Checker** | Compare a file's current hash against a known-good hash |
| **Compressed File Checker** | Inspect ZIP/TAR archives without extracting; detect threats |
| **Obfuscated File Checker** | Detect double extensions, RTLO tricks, hidden characters |

## Project Structure

```
artifacts/fortress-vault/
├── main.py                     # Flask app — all routes
├── requirements.txt
├── modules/
│   ├── encryption.py           # AES-256-GCM encryption
│   ├── decryption.py           # AES-256-GCM decryption
│   ├── digital_signature.py    # RSA-2048 sign/verify
│   ├── hash_generator.py       # SHA-256 / SHA-512
│   ├── integrity_checker.py    # Hash comparison
│   ├── compressed_checker.py   # ZIP/TAR inspection
│   └── obfuscated_checker.py   # Filename analysis
├── templates/
│   └── index.html              # Single-page dashboard
├── static/
│   ├── css/style.css           # Dark-blue cybersecurity theme
│   └── js/script.js            # Frontend logic
├── uploads/                    # Temporary uploaded files
├── outputs/                    # Generated/encrypted outputs
└── keys/                       # RSA key pair storage
```

## Security Design

- **AES-256-GCM** — authenticated encryption; ciphertext is tamper-evident via GCM tag
- **PBKDF2-HMAC-SHA256** (390,000 iterations) — derives AES key from password; password never stored
- **Random salt (16 B) + nonce (12 B)** — prepended to every encrypted file for uniqueness
- **RSA-2048 + PKCS1v15** — standard digital signatures
- **werkzeug `secure_filename`** — prevents path-traversal in uploads
- **50 MB upload limit** — configured in Flask
- Archive checker **never extracts** suspicious files
- Obfuscated checker checks filename only — file content is never read for that feature

## Running Locally

```bash
pip install -r requirements.txt
python main.py
```

The server starts on the port set by `$PORT` (default 24331).
