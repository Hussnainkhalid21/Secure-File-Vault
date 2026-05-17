"""
main.py
-------
Secure File Vault — Flask application entry point.

Registers all API routes and serves the single-page frontend.
Each feature lives in its own module under modules/ for clean separation.
"""

import os
import sys
import base64
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Add the project root to sys.path so modules/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from modules.encryption import encrypt_file
from modules.decryption import decrypt_file
from modules.digital_signature import generate_keys, sign_file, verify_signature
from modules.hash_generator import generate_hashes
from modules.integrity_checker import check_integrity
from modules.compressed_checker import check_compressed
from modules.obfuscated_checker import check_obfuscated

# ─── App Setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)

# 50 MB upload limit as required
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
KEYS_DIR = os.path.join(BASE_DIR, "keys")

# Ensure required directories exist at startup
for d in [UPLOAD_DIR, OUTPUT_DIR, KEYS_DIR]:
    os.makedirs(d, exist_ok=True)


# ─── Helper ───────────────────────────────────────────────────────────────────

def save_upload(file_storage) -> str:
    """Save an uploaded file to UPLOAD_DIR with a secure filename. Returns full path."""
    filename = secure_filename(file_storage.filename)
    path = os.path.join(UPLOAD_DIR, filename)
    file_storage.save(path)
    return path, filename


# ─── Serve Frontend ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the single-page dashboard."""
    return render_template("index.html")


# ─── 1. File Encryption ───────────────────────────────────────────────────────

@app.route("/encrypt", methods=["POST"])
def route_encrypt():
    """
    Encrypt an uploaded file with AES-256-GCM.
    Form fields: file (multipart), password (str)
    Returns: JSON with download_url, or error message.
    """
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400
    password = request.form.get("password", "").strip()
    if not password:
        return jsonify({"error": "Password is required."}), 400

    input_path, filename = save_upload(request.files["file"])
    output_filename = filename + ".enc"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        encrypt_file(input_path, output_path, password)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": f"File encrypted successfully.",
        "output_file": output_filename,
        "download_url": f"/download/{output_filename}",
    })


# ─── 2. File Decryption ───────────────────────────────────────────────────────

@app.route("/decrypt", methods=["POST"])
def route_decrypt():
    """
    Decrypt an AES-256-GCM encrypted file.
    Form fields: file (multipart), password (str)
    Returns: JSON with download_url, or clear error on wrong password.
    """
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400
    password = request.form.get("password", "").strip()
    if not password:
        return jsonify({"error": "Password is required."}), 400

    input_path, filename = save_upload(request.files["file"])
    # Strip .enc suffix if present for the output name
    output_filename = filename[:-4] if filename.endswith(".enc") else "decrypted_" + filename
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        decrypt_file(input_path, output_path, password)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 500

    return jsonify({
        "message": "File decrypted successfully.",
        "output_file": output_filename,
        "download_url": f"/download/{output_filename}",
    })


# ─── 3. Digital Signatures ────────────────────────────────────────────────────

@app.route("/generate-keys", methods=["POST"])
def route_generate_keys():
    """Generate a fresh RSA-2048 key pair and save to the keys/ folder."""
    try:
        keys = generate_keys()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "RSA-2048 key pair generated and saved.",
        "public_key": keys["public_key"],
        "private_key": keys["private_key"],
    })


@app.route("/sign", methods=["POST"])
def route_sign():
    """
    Sign an uploaded file using the stored RSA private key.
    Returns the signature as a Base64 string.
    """
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400

    input_path, filename = save_upload(request.files["file"])

    try:
        signature_bytes = sign_file(input_path)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    signature_b64 = base64.b64encode(signature_bytes).decode()

    # Also save the signature file for download
    sig_filename = filename + ".sig"
    sig_path = os.path.join(OUTPUT_DIR, sig_filename)
    with open(sig_path, "wb") as f:
        f.write(signature_bytes)

    return jsonify({
        "message": "File signed successfully.",
        "signature_b64": signature_b64,
        "download_url": f"/download/{sig_filename}",
    })


@app.route("/verify-signature", methods=["POST"])
def route_verify_signature():
    """
    Verify a file's signature.
    Form fields: file (multipart), signature_b64 (Base64 string)
    """
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400
    sig_b64 = request.form.get("signature_b64", "").strip()
    if not sig_b64:
        return jsonify({"error": "Signature is required."}), 400

    input_path, _ = save_upload(request.files["file"])

    try:
        signature_bytes = base64.b64decode(sig_b64)
        is_valid = verify_signature(input_path, signature_bytes)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Verification error: {str(e)}"}), 500

    return jsonify({
        "valid": is_valid,
        "message": (
            "Signature is VALID — file is original and unmodified."
            if is_valid else
            "Signature is INVALID — file has been modified or signature is wrong."
        ),
    })


# ─── 4. Hash Generator ────────────────────────────────────────────────────────

@app.route("/generate-hash", methods=["POST"])
def route_generate_hash():
    """Generate SHA-256 and SHA-512 hashes of an uploaded file."""
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400

    input_path, filename = save_upload(request.files["file"])

    try:
        result = generate_hashes(input_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "filename": filename,
        "file_size": result["file_size"],
        "sha256": result["sha256"],
        "sha512": result["sha512"],
    })


# ─── 5. Integrity Checker ─────────────────────────────────────────────────────

@app.route("/check-integrity", methods=["POST"])
def route_check_integrity():
    """Compare a file's current hash against a user-provided original hash."""
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400
    original_hash = request.form.get("original_hash", "").strip()
    if not original_hash:
        return jsonify({"error": "Original hash is required."}), 400

    input_path, _ = save_upload(request.files["file"])

    try:
        result = check_integrity(input_path, original_hash)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


# ─── 6. Compressed File Checker ───────────────────────────────────────────────

@app.route("/check-compressed", methods=["POST"])
def route_check_compressed():
    """Inspect a ZIP or TAR archive without extracting it."""
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded."}), 400

    input_path, _ = save_upload(request.files["file"])

    try:
        result = check_compressed(input_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


# ─── 7. Obfuscated File Checker ───────────────────────────────────────────────

@app.route("/check-obfuscated", methods=["POST"])
def route_check_obfuscated():
    """
    Analyse a filename for obfuscation techniques.
    Accepts a filename string (no upload needed — we only check the name).
    Form field: filename (str)
    """
    filename = request.form.get("filename", "").strip()
    if not filename:
        # Also accept from uploaded file's name
        if "file" in request.files and request.files["file"].filename:
            filename = request.files["file"].filename
        else:
            return jsonify({"error": "Filename is required."}), 400

    try:
        result = check_obfuscated(filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


# ─── Download Helper ──────────────────────────────────────────────────────────

@app.route("/download/<filename>")
def download_file(filename):
    """Allow downloading generated files from the outputs/ folder."""
    safe = secure_filename(filename)
    return send_from_directory(OUTPUT_DIR, safe, as_attachment=True)


# ─── Error Handlers ───────────────────────────────────────────────────────────

@app.errorhandler(413)
def request_too_large(e):
    return jsonify({"error": "File too large. Maximum upload size is 50 MB."}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Read PORT from environment (set by Replit workflow)
    port = int(os.environ.get("PORT", 24331))
    # Debug mode off in production; set DEBUG=1 env var for development
    debug = os.environ.get("DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
