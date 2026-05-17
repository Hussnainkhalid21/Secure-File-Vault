"""
integrity_checker.py
--------------------
Compares the current hash of an uploaded file against a user-provided hash.
Supports SHA-256 and SHA-512 automatically detected by string length.
"""

import hashlib


CHUNK_SIZE = 65536


def _compute_hash(file_path: str, algorithm: str) -> str:
    """Compute the hex digest of file_path using the given hashlib algorithm name."""
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def check_integrity(file_path: str, original_hash: str) -> dict:
    """
    Compare the file's current hash against original_hash.

    Auto-detects SHA-256 (64 hex chars) or SHA-512 (128 hex chars) by hash length.
    Returns a dict:
        {
            "algorithm":    "sha256" | "sha512" | "unknown",
            "current_hash": "<hex>",
            "original_hash": "<hex>",
            "match":         True | False,
            "status":        "File is safe / unmodified" | "File has been MODIFIED!",
        }
    """
    original_hash = original_hash.strip().lower()
    length = len(original_hash)

    if length == 64:
        algorithm = "sha256"
    elif length == 128:
        algorithm = "sha512"
    else:
        return {
            "algorithm": "unknown",
            "current_hash": "",
            "original_hash": original_hash,
            "match": False,
            "status": "Unrecognized hash length. Please supply a SHA-256 (64 chars) or SHA-512 (128 chars) hash.",
        }

    current_hash = _compute_hash(file_path, algorithm)
    match = current_hash == original_hash

    return {
        "algorithm": algorithm.upper(),
        "current_hash": current_hash,
        "original_hash": original_hash,
        "match": match,
        "status": "File is safe / unmodified." if match else "WARNING: File has been MODIFIED or corrupted!",
    }
