"""
decryption.py
-------------
Handles AES-256-GCM file decryption.

Reads the salt and nonce from the encrypted file header, re-derives the key
using the supplied password, and decrypts.  If the password is wrong, AESGCM
raises InvalidTag (GCM authentication failure) which we surface as a clear error.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from modules.encryption import derive_key


def decrypt_file(input_path: str, output_path: str, password: str) -> str:
    """
    Decrypt the file at input_path.

    File layout expected:  [16-byte salt][12-byte nonce][ciphertext + GCM tag]

    Returns the output path on success.
    Raises ValueError with a human-readable message on wrong password or corrupt data.
    """
    with open(input_path, "rb") as f:
        data = f.read()

    # Minimum size check: 16 (salt) + 12 (nonce) + 16 (GCM tag) = 44 bytes
    if len(data) < 44:
        raise ValueError("File is too small to be a valid encrypted file.")

    # Parse the header
    salt = data[:16]
    nonce = data[16:28]
    ciphertext = data[28:]   # includes the 16-byte GCM authentication tag

    # Re-derive the same key using the stored salt
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except InvalidTag:
        # GCM tag mismatch → wrong password or tampered file
        raise ValueError("Incorrect password or the file has been tampered with.")

    with open(output_path, "wb") as f:
        f.write(plaintext)

    return output_path
