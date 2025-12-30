import streamlit as st
import pandas as pd

from database.schema import init_db
from database.people import list_people
from ui.dashboard import show_dashboard
from ui.tasks_ui import show_tasks
from ui.requirements_ui import show_requirements
from ui.incidents_ui import show_incidents
from ui.internal_ui import show_internal
from ui.people_ui import show_people
from reports.pdf_report import generate_mini_report_pdf
from ui.users_ui import show_users
from database.users import authenticate_user, log_user_login, log_user_logout, list_users
import xlsxwriter 

st.set_page_config(page_title="Task & Incident Manager", layout="centered")
init_db()

if "user" not in st.session_state:
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1f2933, #0d1117);
    }

    #MainMenu, footer {visibility: hidden;}

    .login-container {
        max-width: 420px;
        margin: 6rem auto;
        padding: 32px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
    }

    .github-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 16px;
    }

    .login-title {
        text-align: center;
        font-size: 24px;
        font-weight: 400;
        color: #f0f6fc;
        margin-bottom: 24px;
    }

    label {
        color: #c9d1d9 !important;
        font-weight: 500;
    }

    input {
        background-color: #0d1117 !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        padding: 10px !important;
    }

    .stButton button {
        background-color: #238636 !important;
        color: white !important;
        font-weight: 600;
        width: 100%;
        border-radius: 6px;
        margin-top: 16px;
        height: 40px;
    }

    .stButton button:hover {
        background-color: #2ea043 !important;
    }

    .forgot {
        text-align: right;
        margin-top: 8px;
    }

    .forgot a {
        color: #58a6ff;
        font-size: 13px;
        text-decoration: none;
    }

    .forgot a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    # -------- FORM real (Streamlit) --------
    with st.container():
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign in")

    st.markdown("""
        <div class="forgot">
            <a href="#">Forgot password? So` boludo no, no la cambio.</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------- Auth --------
    if submit:
        normalized_username = username.strip().lower()
        user = authenticate_user(username, password)
        if user:
            st.session_state["user"] = user
            st.success(f"Welcome {username}")
            st.rerun()
        else:
            st.error("Incorrect username or password")

    st.stop()


# # --- LOGIN ---
# if "user" not in st.session_state:
#     st.title("🔐 Login")

#     # 👇 Usamos un formulario para que Enter funcione
#     with st.form("login_form"):
#         username = st.text_input("Usuario")
#         password = st.text_input("Contraseña", type="password")
#         submit = st.form_submit_button("Ingresar")

#     if submit:
#         user = authenticate_user(username, password)
#         if user:
#             st.session_state["user"] = user
#             session_id = log_user_login(user["id"])
#             st.session_state["session_id"] = session_id
#             st.success(f"Bienvenido {username}")
#         else:
#             st.error("Usuario o contraseña incorrectos")

#     if "user" not in st.session_state:
#         st.stop()

# --- MENÚ LATERAL ---
menu_options = ["Dashboard", "Registros", "Reporte PDF"]

# 👇 solo los Admins ven Personas y Usuarios
if st.session_state["user"]["role"] == "Admin":
    menu_options.extend(["Personas", "Usuarios"])

menu_options.append("Logout")
menu = st.sidebar.selectbox("Navegación", menu_options)

# --- SUBMENÚ DE REGISTROS ---
sub_menu = None
if menu == "Registros":
    sub_menu = st.radio(
        "Tipo de registro",
        ["Incidente", "Tarea", "Requerimiento", "Actividad Interna"],
        horizontal=True
    )

# Cache liviano de personas para las pantallas de formularios
people = list_people()
people_map = {p["name"]: p["id"] for p in people}
people_names = [p["name"] for p in people]

# --- NAVEGACIÓN ---
if menu == "Dashboard":
    show_dashboard()

    # 👇 si el logueado es "user", mostrar tabla de usuarios y el historial
    if st.session_state["user"]["role"] == "user":
        st.subheader("Listado de usuarios en el sistema")
        df_users = pd.DataFrame(list_users())
        st.dataframe(df_users)

        st.subheader("Historial de accesos")
        from database.users import list_user_sessions
        df_sessions = pd.DataFrame(list_user_sessions())

        if not df_sessions.empty:
            # convertir a datetime
            df_sessions["login_time"] = pd.to_datetime(df_sessions["login_time"])
            df_sessions["logout_time"] = pd.to_datetime(df_sessions["logout_time"])

            # rango mínimo y máximo
            min_date = df_sessions["login_time"].min().date()
            max_date = df_sessions["login_time"].max().date()

            start_date = st.date_input("Fecha inicio", min_date)
            end_date = st.date_input("Fecha fin", max_date)

            # filtrar por rango
            mask = (df_sessions["login_time"].dt.date >= start_date) & (df_sessions["login_time"].dt.date <= end_date)
            filtered_df = df_sessions.loc[mask]

            st.dataframe(filtered_df)
        else:
            st.info("No hay sesiones registradas todavía.")

elif menu == "Registros" and sub_menu == "Tarea":
    show_tasks(people_names, people_map)

elif menu == "Registros" and sub_menu == "Requerimiento":
    show_requirements(people_names, people_map)

elif menu == "Registros" and sub_menu == "Incidente":
    show_incidents(people_names, people_map)

elif menu == "Registros" and sub_menu == "Actividad Interna":
    show_internal(people_names, people_map)

elif menu == "Reporte PDF":
    st.header("📄 Mini-Reporte")
    st.markdown("""
    Este reporte contiene:
    - Indicadores generales
    - Horas consumidas
    - Estado general del área
    """)
    if st.button("Generar y descargar PDF"):
        pdf_buffer = generate_mini_report_pdf()
        st.download_button(
            label="📥 Descargar Mini-Reporte",
            data=pdf_buffer,
            file_name="mini_reporte_medicion_inteligente.pdf",
            mime="application/pdf"
        )

elif menu == "Personas":  # 👈 solo aparece si es Admin
    show_people()

elif menu == "Usuarios":  # 👈 solo aparece si es Admin
    show_users()

elif menu == "Logout":
    if "session_id" in st.session_state:
        log_user_logout(st.session_state["session_id"])
    st.session_state.pop("user", None)
    st.session_state.pop("session_id", None)
    st.success("Sesión cerrada correctamente")
    st.stop()

st.markdown("---")

# st.caption("Gestor de Tareas e Incidentes — SQLite + Streamlit")




# if menu == "Dashboard":
#     show_dashboard()

#     # 👇 si el logueado es "user", mostrar tabla de usuarios
#     if st.session_state["user"]["role"] == "user":
#         st.subheader("Listado de usuarios en el sistema")
#         df_users = pd.DataFrame(list_users())
#         st.dataframe(df_users)


#         st.subheader("Historial de accesos")

#         from database.users import list_user_sessions
#         df_sessions = pd.DataFrame(list_user_sessions())

#         # 👇 Filtro por fecha
#         if not df_sessions.empty:
#             df_sessions["login_time"] = pd.to_datetime(df_sessions["login_time"])
#             df_sessions["logout_time"] = pd.to_datetime(df_sessions["logout_time"])

#             min_date = df_sessions["login_time"].min().date()
#             max_date = df_sessions["login_time"].max().date()

#             start_date = st.date_input("Fecha inicio", min_date)
#             end_date = st.date_input("Fecha fin", max_date)

#             # Filtrar por rango
#             mask = (df_sessions["login_time"].dt.date >= start_date) & (df_sessions["login_time"].dt.date <= end_date)
#             filtered_df = df_sessions.loc[mask]

#             st.dataframe(filtered_df)
#         else:
#             st.info("No hay sesiones registradas todavía.")

# elif menu == "Registros" and sub_menu == "Tarea":
#     show_tasks(people_names, people_map)

# elif menu == "Registros" and sub_menu == "Requerimiento":
#     show_requirements(people_names, people_map)

# elif menu == "Registros" and sub_menu == "Incidente":
#     show_incidents(people_names, people_map)

# elif menu == "Registros" and sub_menu == "Actividad Interna":
#     show_internal(people_names, people_map)

# elif menu == "Reporte PDF":
#     st.header("📄 Mini-Reporte")
#     st.markdown("""
#     Este reporte contiene:
#     - Indicadores generales
#     - Horas consumidas
#     - Estado general del área
#     """)
#     if st.button("Generar y descargar PDF"):
#         pdf_buffer = generate_mini_report_pdf()
#         st.download_button(
#             label="📥 Descargar Mini-Reporte",
#             data=pdf_buffer,
#             file_name="mini_reporte_medicion_inteligente.pdf",
#             mime="application/pdf"
#         )

# elif menu == "Personas":  # 👈 solo aparece si es Admin
#     show_people()

# elif menu == "Usuarios":  # 👈 solo aparece si es Admin
#     show_users()

# elif menu == "Logout":
#     if "session_id" in st.session_state:
#         log_user_logout(st.session_state["session_id"])
#     st.session_state.pop("user", None)
#     st.session_state.pop("session_id", None)
#     st.success("Sesión cerrada correctamente")
#     st.stop()

# st.markdown("---")
# st.caption("Gestor de Tareas e Incidentes — SQLite + Streamlit")
