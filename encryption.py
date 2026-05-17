"""
encryption.py
-------------
Handles AES-256-GCM file encryption using a user-supplied password.

Key derivation uses PBKDF2-HMAC-SHA256 so the raw password is never stored.
The output file format is:  [16-byte salt][12-byte nonce][ciphertext + 16-byte GCM tag]
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# Number of PBKDF2 iterations — high enough to resist brute-force
PBKDF2_ITERATIONS = 390_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from a password and salt using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 256 bits → AES-256
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_file(input_path: str, output_path: str, password: str) -> str:
    """
    Encrypt the file at input_path using AES-256-GCM.

    Steps:
      1. Generate a random 16-byte salt and 12-byte nonce.
      2. Derive a 256-bit key from the password + salt.
      3. Encrypt the plaintext with AESGCM (produces ciphertext + 16-byte auth tag).
      4. Write  salt | nonce | ciphertext  to output_path.

    Returns the output path on success, raises on error.
    """
    # Step 1 — random values ensure every encryption is unique
    salt = os.urandom(16)
    nonce = os.urandom(12)

    # Step 2 — derive encryption key (password is never stored)
    key = derive_key(password, salt)

    # Step 3 — encrypt
    aesgcm = AESGCM(key)
    with open(input_path, "rb") as f:
        plaintext = f.read()

    ciphertext = aesgcm.encrypt(nonce, plaintext, None)  # None = no additional data

    # Step 4 — write salt | nonce | ciphertext to the output file
    with open(output_path, "wb") as f:
        f.write(salt + nonce + ciphertext)

    return output_path
