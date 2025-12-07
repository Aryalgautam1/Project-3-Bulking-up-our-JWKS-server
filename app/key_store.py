import time
from typing import Tuple, List, Optional

from app.database import get_db_connection
from app.encryption import encrypt_private_key, decrypt_private_key


def save_key(pem_bytes: bytes, exp_ts: int) -> int:
    """
    Save a private key PEM to the database with expiry timestamp.
    Encrypts the key using AES-GCM (IV is embedded in the encrypted blob).
    """
    # Encrypt the private key (IV is embedded in the output)
    encrypted_key = encrypt_private_key(pem_bytes)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO keys (key, exp) VALUES (?, ?)",
        (encrypted_key, exp_ts)
    )
    kid = cursor.lastrowid
    conn.commit()
    conn.close()
    return kid


def get_key(expired: bool) -> Optional[Tuple[int, bytes, int]]:
    """
    Get one key from the database.
    - If expired=True: choose one key with exp <= now
    - If expired=False: choose one key with exp > now
    
    Returns (kid:int, pem_bytes:bytes, exp_ts:int) or None if no matching key.
    Decrypts the key before returning.
    """
    now = int(time.time())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if expired:
        cursor.execute(
            "SELECT kid, key, exp FROM keys WHERE exp <= ? ORDER BY kid LIMIT 1",
            (now,)
        )
    else:
        cursor.execute(
            "SELECT kid, key, exp FROM keys WHERE exp > ? ORDER BY kid LIMIT 1",
            (now,)
        )
    
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    # Decrypt the key (IV is embedded in the encrypted data)
    encrypted_key = row["key"]
    pem_bytes = decrypt_private_key(encrypted_key)
    
    return (row["kid"], pem_bytes, row["exp"])


def get_valid_keys() -> List[Tuple[int, bytes, int]]:
    """
    Get all valid (non-expired) keys from the database.
    Returns list of (kid:int, pem_bytes:bytes, exp_ts:int).
    Decrypts keys before returning.
    """
    now = int(time.time())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT kid, key, exp FROM keys WHERE exp > ?",
        (now,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        encrypted_key = row["key"]
        pem_bytes = decrypt_private_key(encrypted_key)
        result.append((row["kid"], pem_bytes, row["exp"]))
    
    return result