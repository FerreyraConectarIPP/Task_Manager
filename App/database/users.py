# from .connection import get_conn
# from datetime import datetime

# def log_user_login(user_id):
#     """
#     Registra un login en la tabla user_sessions y devuelve el id de la sesión creada.
#     """
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO user_sessions (user_id, login_time) VALUES (?, ?)",
#         (user_id, datetime.now().isoformat())
#     )
#     conn.commit()
#     return cur.lastrowid

# def log_user_logout(session_id):
#     """
#     Actualiza el logout_time de la sesión indicada.
#     """
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute(
#         "UPDATE user_sessions SET logout_time=? WHERE id=?",
#         (datetime.now().isoformat(), session_id)
#     )
#     conn.commit()

# def add_user(username, password, role="user"):
#     conn = get_conn()
#     conn.execute(
#         "INSERT INTO users (username, password, role) VALUES (?,?,?)",
#         (username, password, role)
#     )
#     conn.commit()

# def list_users():
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("SELECT id, username, role, created_at FROM users ORDER BY username")
#     return [dict(r) for r in cur.fetchall()]

# def authenticate_user(username, password):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
#     row = cur.fetchone()
#     return dict(row) if row else None

# def update_user(user_id, username=None, password=None, role=None):
#     conn = get_conn()
#     cur = conn.cursor()
#     fields = []
#     values = []
#     if username:
#         fields.append("username=?")
#         values.append(username)
#     if password:
#         fields.append("password=?")
#         values.append(password)
#     if role:
#         fields.append("role=?")
#         values.append(role)
#     if not fields:
#         return 0
#     values.append(user_id)
#     sql = f"UPDATE users SET {', '.join(fields)} WHERE id=?"
#     cur.execute(sql, tuple(values))
#     conn.commit()
#     return cur.rowcount

# def delete_user(user_id):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("DELETE FROM users WHERE id=?", (user_id,))
#     conn.commit()
#     return cur.rowcount

# def list_user_sessions():
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT us.id, u.username, us.login_time, us.logout_time
#         FROM user_sessions us
#         JOIN users u ON us.user_id = u.id
#         ORDER BY us.login_time DESC
#     """)
#     return [dict(r) for r in cur.fetchall()]



from .connection import get_conn
from datetime import datetime

def log_user_login(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_sessions (user_id, login_time) VALUES (?, ?)",
        (user_id, datetime.now().isoformat())
    )
    conn.commit()
    return cur.lastrowid

def log_user_logout(session_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE user_sessions SET logout_time=? WHERE id=?",
        (datetime.now().isoformat(), session_id)
    )
    conn.commit()

def add_user(username, password, role="user", email=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO users (username, password, role, email) VALUES (?,?,?,?)",
        (username, password, role, email)
    )
    conn.commit()

def list_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, email, created_at FROM users ORDER BY username")
    return [dict(r) for r in cur.fetchall()]

def get_user_by_email(email):
    conn = get_conn()
    cur = conn.cursor()
    # Comparación insensible a mayúsculas para emails
    cur.execute("SELECT * FROM users WHERE LOWER(email)=LOWER(?)", (email,))
    row = cur.fetchone()
    if row:
        return dict(row)
    # Fallback: buscar en tabla people y mapear por nombre (también case-insensitive)
    try:
        cur.execute("SELECT id, name, email FROM people WHERE LOWER(email)=LOWER(?)", (email,))
        p = cur.fetchone()
        if p:
            # intentar obtener usuario cuyo username sea el nombre de la persona
            cur.execute("SELECT * FROM users WHERE LOWER(username)=LOWER(?)", (p[1],))
            user_row = cur.fetchone()
            return dict(user_row) if user_row else None
    except Exception:
        pass
    return None

def get_user_by_username(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    return dict(row) if row else None

def authenticate_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    return dict(row) if row else None

def update_user(user_id, username=None, password=None, role=None, email=None):
    conn = get_conn()
    cur = conn.cursor()
    fields = []
    values = []
    if username:
        fields.append("username=?")
        values.append(username)
    if password:
        fields.append("password=?")
        values.append(password)
    if role:
        fields.append("role=?")
        values.append(role)
    if email is not None:
        fields.append("email=?")
        values.append(email)
    if not fields:
        return 0
    values.append(user_id)
    sql = f"UPDATE users SET {', '.join(fields)} WHERE id=?"
    cur.execute(sql, tuple(values))
    conn.commit()
    return cur.rowcount

def delete_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    return cur.rowcount

def list_user_sessions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT us.id, u.username, us.login_time, us.logout_time
        FROM user_sessions us
        JOIN users u ON us.user_id = u.id
        ORDER BY us.login_time DESC
    """)
    return [dict(r) for r in cur.fetchall()]
