"""
digital_signature.py
--------------------
RSA-2048 digital signature operations.

• generate_keys()    — create a fresh RSA key pair and save to the keys/ folder.
• sign_file()        — sign a file's SHA-256 digest with the private key.
• verify_signature() — verify a signature against a file using the public key.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


KEYS_DIR = os.path.join(os.path.dirname(__file__), "..", "keys")


def _keys_path():
    """Return the absolute keys directory path."""
    return os.path.abspath(KEYS_DIR)


def generate_keys() -> dict:
    """
    Generate an RSA-2048 key pair and save to keys/private_key.pem and keys/public_key.pem.
    Returns a dict with the PEM strings for display.
    """
    # Generate a 2048-bit RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Serialize keys to PEM format (no password on private key for demo simplicity)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    os.makedirs(_keys_path(), exist_ok=True)
    with open(os.path.join(_keys_path(), "private_key.pem"), "wb") as f:
        f.write(private_pem)
    with open(os.path.join(_keys_path(), "public_key.pem"), "wb") as f:
        f.write(public_pem)

    return {
        "private_key": private_pem.decode(),
        "public_key": public_pem.decode(),
    }


def sign_file(file_path: str) -> bytes:
    """
    Sign the file at file_path using the stored private key.
    Returns the raw signature bytes.
    Raises FileNotFoundError if private_key.pem does not exist.
    """
    private_key_path = os.path.join(_keys_path(), "private_key.pem")
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(
            "Private key not found. Please generate keys first."
        )

    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(file_path, "rb") as f:
        data = f.read()

    # Sign the SHA-256 digest using PKCS1v15 padding
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return signature


def verify_signature(file_path: str, signature: bytes) -> bool:
    """
    Verify a signature against the file using the stored public key.
    Returns True if valid, False if the file has been modified.
    Raises FileNotFoundError if public_key.pem does not exist.
    """
    public_key_path = os.path.join(_keys_path(), "public_key.pem")
    if not os.path.exists(public_key_path):
        raise FileNotFoundError(
            "Public key not found. Please generate keys first."
        )

    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    with open(file_path, "rb") as f:
        data = f.read()

    try:
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True  # Signature is valid — file is original
    except InvalidSignature:
        return False  # Signature mismatch — file has been modified
