from .connection import get_conn
from datetime import datetime, timedelta
import secrets


def ensure_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            email TEXT,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Si la tabla existía sin la columna 'email', añadirla
    cur.execute("PRAGMA table_info('password_reset_tokens')")
    cols = [r[1] for r in cur.fetchall()]
    if 'email' not in cols:
        try:
            cur.execute("ALTER TABLE password_reset_tokens ADD COLUMN email TEXT")
            conn.commit()
        except Exception as e:
            print(f"Warning: no se pudo añadir columna 'email' a password_reset_tokens: {e}")


def create_reset_token(user_id: int | None = None, email: str | None = None, expiry_minutes: int = 60) -> str:
    """Crea un token de restablecimiento.

    - Si `user_id` se suministra, el token servirá para restablecer esa cuenta.
    - Si `user_id` es None y `email` se proporciona, el token servirá para invitar/crear usuario para ese email.
    """
    ensure_table()
    if user_id is None and not email:
        raise ValueError("Se requiere user_id o email para crear un token")
    conn = get_conn()
    cur = conn.cursor()
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()
    # Si user_id es None, almacenamos 0 por compatibilidad con esquemas antiguos
    user_value = user_id if user_id is not None else 0
    cur.execute("INSERT INTO password_reset_tokens (token, user_id, email, expires_at) VALUES (?,?,?,?)",
                (token, user_value, email, expires_at))
    conn.commit()
    return token


def get_reset_token(token: str):
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT token, user_id, email, expires_at, used FROM password_reset_tokens WHERE token=?", (token,))
    row = cur.fetchone()
    if not row:
        return None
    token, user_id, email, expires_at, used = row
    return {"token": token, "user_id": user_id, "email": email, "expires_at": expires_at, "used": bool(used)}


def consume_reset_token(token: str) -> None:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE password_reset_tokens SET used=1 WHERE token=?", (token,))
    conn.commit()


def cleanup_expired_tokens():
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM password_reset_tokens WHERE datetime(expires_at) < datetime('now') OR used=1")
    conn.commit()
