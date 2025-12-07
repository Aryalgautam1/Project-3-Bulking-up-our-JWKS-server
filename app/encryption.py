import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_encryption_key() -> bytes:
    """
    Get the encryption key from environment variable NOT_MY_KEY.
    Raises ValueError if not set or invalid.
    """
    key = os.getenv("NOT_MY_KEY")
    if not key:
        raise ValueError("NOT_MY_KEY environment variable not set")
    
    # Ensure it's 32 bytes (256 bits) for AES-256
    key_bytes = key.encode('utf-8')
    
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b'_')
    elif len(key_bytes) > 32:
        key_bytes = key_bytes[:32]
    
    return key_bytes


def encrypt_private_key(pem_bytes: bytes) -> bytes:
    """
    Encrypt private key using AES-GCM.
    Returns encrypted data with IV prepended (IV is embedded in the output).
    """
    key = get_encryption_key()
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, pem_bytes, None)
    
    # Prepend nonce to ciphertext (this is the standard approach)
    return nonce + ciphertext


def decrypt_private_key(encrypted_data: bytes) -> bytes:
    """
    Decrypt private key using AES-GCM.
    Expects IV to be prepended to the encrypted data.
    """
    key = get_encryption_key()
    
    # Extract nonce (first 12 bytes) and ciphertext
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    
    aesgcm = AESGCM(key)
    pem_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    
    return pem_bytes