from .connection import get_conn


def ensure_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def add_contact(email: str, name: str | None = None) -> None:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO email_contacts (name, email) VALUES (?,?)", (name, email))
        conn.commit()
    except Exception:
        # ignore duplicates or errors for now
        pass


def list_contacts() -> list[dict]:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM email_contacts ORDER BY name ASC")
    return [dict(r) for r in cur.fetchall()]


def get_contact_by_email(email: str):
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM email_contacts WHERE LOWER(email)=LOWER(?)", (email,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_contact_by_name(name: str):
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM email_contacts WHERE name=?", (name,))
    row = cur.fetchone()
    return dict(row) if row else None


def delete_contact(contact_id: int) -> int:
    ensure_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM email_contacts WHERE id=?", (contact_id,))
    conn.commit()
    return cur.rowcount
