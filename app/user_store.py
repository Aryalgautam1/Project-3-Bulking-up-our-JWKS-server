import uuid
import sqlite3
from typing import Optional, Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.database import get_db_connection

# Configure Argon2 parameters
ph = PasswordHasher(
    time_cost=2,          # Number of iterations
    memory_cost=65536,    # Memory usage in KB (64 MB)
    parallelism=4,       # Number of parallel threads
    hash_len=32,          # Hash length in bytes
    salt_len=16           # Salt length in bytes
)


def register_user(username: str, email: str) -> Tuple[str, int]:
    """
    Register a new user.
    Generates a UUIDv4 password, hashes it with Argon2, and stores user.
    Returns (password: str, user_id: int).
    Raises ValueError if username or email already exists.
    """
    # Generate secure password using UUIDv4
    password = str(uuid.uuid4())
    
    # Hash the password
    password_hash = ph.hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return password, user_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Username or email already exists: {e}")
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[dict]:
    """
    Get user by username.
    Returns dict with user info or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, email FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "email": row["email"]
    }


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify a password against its hash.
    Returns True if password matches, False otherwise.
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False

