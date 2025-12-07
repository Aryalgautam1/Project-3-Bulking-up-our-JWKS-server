from typing import Optional
from app.database import get_db_connection


def log_auth_request(request_ip: str, user_id: Optional[int] = None):
    """
    Log an authentication request to the auth_logs table.
    Uses parameterized query for SQL injection safety.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO auth_logs (request_ip, user_id) VALUES (?, ?)",
        (request_ip, user_id)
    )
    conn.commit()
    conn.close()

