from .connection import get_conn

# Simple key/value settings store

def ensure_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()


def set_setting(key: str, value: str) -> None:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()


def get_setting(key: str, default: str | None = None) -> str | None:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cur.fetchone()
    return r[0] if r else default


def get_all_settings() -> dict:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM settings")
    return {row[0]: row[1] for row in cur.fetchall()}
