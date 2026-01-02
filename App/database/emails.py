from .connection import get_conn
from datetime import datetime


def ensure_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            to_email TEXT,
            subject TEXT,
            body TEXT,
            sent_at TEXT,
            status TEXT,
            error TEXT
        )
    """)
    conn.commit()


def log_email(to_email: str, subject: str, body: str, status: str = "sent", error: str | None = None) -> None:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO email_logs (to_email, subject, body, sent_at, status, error) VALUES (?,?,?,?,?,?)",
                (to_email, subject, body, datetime.utcnow().isoformat(), status, error))
    conn.commit()


def get_logs(limit: int = 500) -> list[dict]:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, to_email, subject, body, sent_at, status, error FROM email_logs ORDER BY id DESC LIMIT ?", (limit,))
    return [dict(r) for r in cur.fetchall()]
