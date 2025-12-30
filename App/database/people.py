# from .connection import get_conn

# def list_people(active_only=True):
#     conn = get_conn()
#     cur = conn.cursor()
#     if active_only:
#         cur.execute("SELECT * FROM people WHERE active=1 ORDER BY name")
#     else:
#         cur.execute("SELECT * FROM people ORDER BY name")
#     return [dict(r) for r in cur.fetchall()]

# def add_person(name, email=None, role="user", active=1):
#     conn = get_conn()
#     conn.execute(
#         "INSERT INTO people (name, email, role, active) VALUES (?,?,?,?)",
#         (name, email, role, active)
#     )
#     conn.commit()

# def init_default_people():
#     conn = get_conn()
#     cur = conn.cursor()

#     # Crear superadmin por defecto si no existe
#     cur.execute("SELECT COUNT(*) FROM people WHERE name='Admin'")
#     if cur.fetchone()[0] == 0:
#         cur.execute("INSERT INTO people (name, email, role, active) VALUES (?,?,?,?)",
#                     ("Admin", "admin@example.com", "Admin", 1))

#     # Crear 3 usuarios normales si no existen
#     default_people = [
#         ("fferreyra", "fferreyra@example.com", "user", 1),
#         ("lsilva", "lsilva@example.com", "user", 1),
#         ("Poberto", "poberto@example.com", "user", 1)
#     ]

#     for name, email, role, active in default_people:
#         cur.execute("SELECT COUNT(*) FROM people WHERE name=?", (name,))
#         if cur.fetchone()[0] == 0:
#             cur.execute("INSERT INTO people (name, email, role, active) VALUES (?,?,?,?)",
#                         (name, email, role, active))

#     conn.commit()


from .connection import get_conn

def list_people(active_only=True):
    """
    Devuelve todas las personas registradas.
    Si active_only=True, solo devuelve las activas.
    """
    conn = get_conn()
    cur = conn.cursor()
    if active_only:
        cur.execute("SELECT * FROM people WHERE active=1 ORDER BY name")
    else:
        cur.execute("SELECT * FROM people ORDER BY name")
    return [dict(r) for r in cur.fetchall()]

def add_person(name, email=None, role="user", active=1):
    """
    Agrega una nueva persona a la tabla people.
    """
    conn = get_conn()
    conn.execute(
        "INSERT INTO people (name, email, role, active) VALUES (?,?,?,?)",
        (name, email, role, active)
    )
    conn.commit()

def update_person(person_id, name=None, email=None, role=None, active=None):
    """
    Actualiza los datos de una persona existente.
    """
    conn = get_conn()
    cur = conn.cursor()
    fields = []
    values = []
    if name:
        fields.append("name=?")
        values.append(name)
    if email:
        fields.append("email=?")
        values.append(email)
    if role:
        fields.append("role=?")
        values.append(role)
    if active is not None:
        fields.append("active=?")
        values.append(active)
    if not fields:
        return 0
    values.append(person_id)
    sql = f"UPDATE people SET {', '.join(fields)} WHERE id=?"
    cur.execute(sql, tuple(values))
    conn.commit()
    return cur.rowcount

def delete_person(person_id):
    """
    Elimina una persona por ID.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM people WHERE id=?", (person_id,))
    conn.commit()
    return cur.rowcount

def authenticate_person(name, email=None):
    """
    Autentica una persona por nombre (y opcionalmente email).
    Devuelve el registro como dict si existe y está activa.
    """
    conn = get_conn()
    cur = conn.cursor()
    if email:
        cur.execute("SELECT * FROM people WHERE name=? AND email=? AND active=1", (name, email))
    else:
        cur.execute("SELECT * FROM people WHERE name=? AND active=1", (name,))
    row = cur.fetchone()
    return dict(row) if row else None

def init_default_people():
    """
    Crea personas por defecto (Admin y 3 usuarios) si no existen.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Crear superadmin por defecto si no existe
    cur.execute("SELECT COUNT(*) FROM people WHERE name='Admin'")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO people (name, email, role, active) VALUES (?,?,?,?)",
                    ("Admin", "admin@example.com", "Admin", 1))

    # Crear 3 usuarios normales si no existen
    default_people = [
        ("fferreyra", "fferreyra@example.com", "user", 1),
        ("lsilva", "lsilva@example.com", "user", 1),
        ("Poberto", "poberto@example.com", "user", 1)
    ]

    for name, email, role, active in default_people:
        cur.execute("SELECT COUNT(*) FROM people WHERE name=?", (name,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO people (name, email, role, active) VALUES (?,?,?,?)",
                        (name, email, role, active))

    conn.commit()
