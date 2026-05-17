"""
hash_generator.py
-----------------
Computes SHA-256 and SHA-512 cryptographic hashes of an uploaded file.
Reads the file in chunks to avoid loading huge files entirely into memory.
"""

import hashlib


CHUNK_SIZE = 65536  # 64 KB per read — efficient for large files


def generate_hashes(file_path: str) -> dict:
    """
    Compute SHA-256 and SHA-512 hashes of the file at file_path.

    Returns a dict:
        {
            "sha256": "<hex string>",
            "sha512": "<hex string>",
            "file_size": <int bytes>,
        }
    """
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    total_bytes = 0

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
            sha512.update(chunk)
            total_bytes += len(chunk)

    return {
        "sha256": sha256.hexdigest(),
        "sha512": sha512.hexdigest(),
        "file_size": total_bytes,
    }
