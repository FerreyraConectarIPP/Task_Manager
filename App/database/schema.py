# from .connection import get_conn

# def init_db():
#     conn = get_conn()
#     cur = conn.cursor()

#     # People
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS people (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             email TEXT,
#             role TEXT,
#             active INTEGER DEFAULT 1,
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     # Tasks (con ID alfanumérico y fechas inicio/fin)
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS tasks (
#             id TEXT PRIMARY KEY,
#             project TEXT NOT NULL,
#             origin TEXT NOT NULL,
#             category TEXT NOT NULL,
#             task_type TEXT NOT NULL,
#             description TEXT NOT NULL,
#             responsible_id INTEGER NOT NULL,
#             start_date TEXT NOT NULL,
#             start_time TEXT,
#             end_date TEXT,
#             end_time TEXT,
#             status TEXT NOT NULL,
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP,
#             updated_at TEXT,
#             FOREIGN KEY(responsible_id) REFERENCES people(id)
#         )
#     """)

#     # Requirements (con ID alfanumérico y fechas)
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS requirements (
#             id TEXT PRIMARY KEY,
#             project TEXT NOT NULL,
#             origin TEXT NOT NULL,
#             requester TEXT NOT NULL,
#             category TEXT NOT NULL,
#             req_type TEXT NOT NULL,
#             description TEXT NOT NULL,
#             responsible_id INTEGER NOT NULL,
#             status TEXT NOT NULL,
#             start_date TEXT,
#             start_time TEXT,
#             end_date TEXT,
#             end_time TEXT,
#             received_at TEXT,
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP,
#             updated_at TEXT,
#             FOREIGN KEY(responsible_id) REFERENCES people(id)
#         )
#     """)

#     # Incidents
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS incidents (
#             id TEXT PRIMARY KEY,
#             project TEXT NOT NULL,
#             category TEXT NOT NULL,
#             severity TEXT NOT NULL,
#             description TEXT NOT NULL,
#             detected_at TEXT NOT NULL,
#             responsible_id INTEGER NOT NULL,
#             status TEXT NOT NULL,
#             start_date TEXT NOT NULL,
#             start_time TEXT,
#             end_date TEXT,
#             end_time TEXT,
#             root_cause TEXT,
#             corrective_action TEXT,
#             preventive_action TEXT,
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP,
#             updated_at TEXT,
#             FOREIGN KEY(responsible_id) REFERENCES people(id)
#         )
#     """)

#     # Internal Activities
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS internal_activities (
#             id TEXT PRIMARY KEY,
#             category TEXT NOT NULL,
#             activity_type TEXT NOT NULL,
#             description TEXT NOT NULL,
#             responsible_id INTEGER NOT NULL,
#             start_date TEXT NOT NULL,
#             start_time TEXT,
#             end_date TEXT,
#             end_time TEXT,
#             status TEXT NOT NULL,
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP,
#             updated_at TEXT,
#             FOREIGN KEY(responsible_id) REFERENCES people(id)
#         )
#     """)

#     # Users
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             role TEXT DEFAULT 'user',
#             created_at TEXT DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#  # Tabla de sesiones de usuarios (login/logout) 
#     cur.execute(""" 
#         CREATE TABLE IF NOT EXISTS user_sessions( 
#             id INTEGER PRIMARY KEY AUTOINCREMENT, 
#             user_id INTEGER, 
#             login_time TEXT, 
#             logout_time TEXT, 
#             FOREIGN KEY(user_id) REFERENCES users(id) 
#         ) 
#     """)


#     # Crear superadmin por defecto si no existe
#     cur.execute("SELECT COUNT(*) FROM users WHERE username='Admin'")
#     if cur.fetchone()[0] == 0:
#         cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
#                     ("Admin", "123", "Admin"))

#     # Crear 3 usuarios normales si no existen
#     default_users = [("fferreyra", "F3rn4nd0", "user"),
#                      ("lsilva", "L34ndr0", "user"),
#                      ("Poberto", "P4tr1c10", "user")]

#     for username, password, role in default_users:
#         cur.execute("SELECT COUNT(*) FROM users WHERE username=?", (username,))
#         if cur.fetchone()[0] == 0:
#             cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
#                         (username, password, role))

#     conn.commit()

from .connection import get_conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # People
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tasks
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            origin TEXT NOT NULL,
            category TEXT NOT NULL,
            task_type TEXT NOT NULL,
            description TEXT NOT NULL,
            responsible_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            start_time TEXT,
            end_date TEXT,
            end_time TEXT,
            status TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY(responsible_id) REFERENCES people(id)
        )
    """)

    # Requirements
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            origin TEXT NOT NULL,
            requester TEXT NOT NULL,
            category TEXT NOT NULL,
            req_type TEXT NOT NULL,
            description TEXT NOT NULL,
            responsible_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            start_date TEXT,
            start_time TEXT,
            end_date TEXT,
            end_time TEXT,
            received_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY(responsible_id) REFERENCES people(id)
        )
    """)

    # Incidents (👉 ahora con assigned_by)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            detected_at TEXT NOT NULL,
            responsible_id INTEGER NOT NULL,
            assigned_by INTEGER,  -- 👈 nuevo campo
            status TEXT NOT NULL,
            start_date TEXT NOT NULL,
            start_time TEXT,
            end_date TEXT,
            end_time TEXT,
            root_cause TEXT,
            corrective_action TEXT,
            preventive_action TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY(responsible_id) REFERENCES people(id),
            FOREIGN KEY(assigned_by) REFERENCES people(id)
        )
    """)

    # Internal Activities
    cur.execute("""
        CREATE TABLE IF NOT EXISTS internal_activities (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            responsible_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            start_time TEXT,
            end_date TEXT,
            end_time TEXT,
            status TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY(responsible_id) REFERENCES people(id)
        )
    """)

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User sessions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time TEXT,
            logout_time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Crear superadmin por defecto si no existe
    cur.execute("SELECT COUNT(*) FROM users WHERE username='Admin'")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                    ("Admin", "123", "Admin"))

    # Crear 3 usuarios normales si no existen
    default_users = [
        ("fferreyra", "F3rn4nd0", "user"),
        ("lsilva", "L34ndr0", "user"),
        ("poberto", "P4tr1c10", "user")
    ]

    for username, password, role in default_users:
        cur.execute("SELECT COUNT(*) FROM users WHERE username=?", (username,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                        (username, password, role))

    conn.commit()
