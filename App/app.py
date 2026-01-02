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
from ui.settings_ui import show_settings
from database.users import authenticate_user, log_user_login, log_user_logout, list_users
import xlsxwriter 

st.set_page_config(page_title="Task & Incident Manager", layout="centered")
init_db()

# --- Manejo de tokens de restablecimiento (si el usuario viene con ?reset_token=... en la URL)
from database.password_reset import get_reset_token, consume_reset_token
from database.users import update_user, get_user_by_email, get_user_by_username
from database.settings import get_setting
from utils.mailer import send_reset_email
from utils.helpers import get_version
from datetime import datetime

# Mostrar versión de código (archivo VERSION o commit git). Visible en sidebar y en parte superior.
version = get_version()
# Barra lateral (siempre visible)
# (La versión y el usuario se muestran ahora en la parte inferior de la barra lateral)
# Resaltar botón de logout en rojo dentro de la sidebar
st.sidebar.markdown("""
<style>
section[data-testid="stSidebar"] .stButton>button{ background-color: #dc2626 !important; color:white !important; border-color:#b91c1c !important;}
</style>
""", unsafe_allow_html=True)

# Si la app fue invocada con ?reset_token=..., mostrar formulario para elegir nueva contraseña o crear cuenta
params = st.query_params
if params.get("reset_token"):
    token = params.get("reset_token")[0]
    token_row = get_reset_token(token)
    if not token_row:
        st.error("Token inválido o expirado para restablecer la contraseña.")
        st.stop()
    # validar expiración
    try:
        expires_at = datetime.fromisoformat(token_row["expires_at"])
    except Exception:
        st.error("Token inválido.")
        st.stop()

    if token_row.get("used"):
        st.error("Este token ya fue usado.")
        st.stop()

    if expires_at < datetime.utcnow():
        st.error("El token ha expirado.")
        st.stop()

    # Si el token está asociado a un user_id distinto de 0, es un restablecimiento normal
    if token_row.get("user_id") and token_row.get("user_id") != 0:
        st.header("Restablecer contraseña")
        with st.form("reset_password_form"):
            new_password = st.text_input("Nueva contraseña", type="password")
            if st.form_submit_button("Actualizar contraseña"):
                update_user(token_row.get("user_id"), password=new_password)
                consume_reset_token(token)
                # limpiar parámetros de query para evitar reenvío accidental
                st.experimental_set_query_params()
                st.success("Contraseña actualizada correctamente. Puedes iniciar sesión ahora.")
                st.stop()
    else:
        # Token de invitación / creación de cuenta para email
        invited_email = token_row.get("email")
        st.header("Crear cuenta")
        st.info(f"Crear una cuenta para: {invited_email}")
        with st.form("create_account_form"):
            new_username = st.text_input("Nombre de usuario")
            new_password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Crear cuenta"):
                if not new_username or not new_password:
                    st.error("Usuario y contraseña son obligatorios")
                else:
                    # comprobar si el username ya existe
                    from database.users import get_user_by_username, add_user
                    if get_user_by_username(new_username):
                        st.error("El nombre de usuario ya existe. Elige otro.")
                    else:
                        add_user(new_username, new_password, role="user", email=invited_email)
                        consume_reset_token(token)
                        st.experimental_set_query_params()
                        st.success("Cuenta creada correctamente. Ahora puedes iniciar sesión.")
                        st.stop()


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

    # Enlace / botón para recuperar contraseña (reemplaza el enlace HTML que no redirige)
    if st.button("¿Olvidaste tu contraseña?"):
        st.session_state["show_forgot"] = True

    if st.session_state.get("show_forgot"):
        st.markdown("### Recuperar contraseña")
        with st.form("forgot_form"):
            forgot_email = st.text_input("Introduce tu email registrado")
            forgot_username = st.text_input("(Opcional) Nombre de usuario (si lo conoces)")
            if st.form_submit_button("Enviar enlace de restablecimiento"):
                from database.users import get_user_by_email, get_user_by_username
                from database.password_reset import create_reset_token
                from utils.mailer import send_reset_email

                user_row = None
                if forgot_email:
                    user_row = get_user_by_email(forgot_email)
                if not user_row and forgot_username:
                    user_row = get_user_by_username(forgot_username)

                if not user_row:
                    st.error("No se encontró un usuario con esos datos. Asegúrate de que el correo esté registrado.")
                else:
                    to_email = forgot_email or user_row.get("email")
                    # obtener APP_BASE_URL desde settings o variable de entorno
                    base_url = get_setting("APP_BASE_URL") or __import__("os").environ.get("APP_BASE_URL") or "http://localhost:8501"
                    token = create_reset_token(user_row.get("id"))
                    reset_link = f"{base_url.rstrip('/')}/?reset_token={token}"
                    ok, msg = send_reset_email(to_email, user_row.get("username"), reset_link)
                    if ok:
                        st.success("Se ha enviado un enlace para restablecer la contraseña. Revisa tu bandeja de entrada.")
                        st.session_state.pop("show_forgot", None)
                    else:
                        st.error(f"No se pudo enviar el correo: {msg}")
                        st.info("Ponte en contacto con el administrador para que configure SMTP.")

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

# 👇 solo los Admins ven Personas, Usuarios, Ajustes y Correos
if st.session_state["user"]["role"] == "Admin":
    menu_options.extend(["Personas", "Usuarios", "Ajustes", "Correos"])
menu = st.sidebar.selectbox("Navegación", menu_options)

# Botón de logout separado (fuera del selectbox de navegación)
logout_clicked = st.sidebar.button("Cerrar sesión")
if logout_clicked:
    if "session_id" in st.session_state:
        log_user_logout(st.session_state["session_id"])
    st.session_state.pop("user", None)
    st.session_state.pop("session_id", None)
    st.success("Sesión cerrada correctamente")
    st.rerun()

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
    st.header("📄 Reporte")
    st.markdown("""
    Este reporte contiene:
    - Indicadores generales
    - Horas consumidas
    - Estado general del área
    """)
    if st.button("Generar y descargar PDF"):
        user = st.session_state.get("user")
        pdf_buffer = generate_mini_report_pdf(generated_by=user, version=version)
        st.download_button(
            label="📥 Descargar Reporte",
            data=pdf_buffer,
            file_name=f"Reporte_medicion_inteligente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

elif menu == "Personas":  # 👈 solo aparece si es Admin
    show_people()

elif menu == "Usuarios":  # 👈 solo aparece si es Admin
    show_users()

elif menu == "Ajustes":  # 👈 solo aparece si es Admin
    show_settings()

elif menu == "Correos":  # 👈 solo aparece si es Admin
    from ui.emails_ui import show_emails
    show_emails()



# Mostrar versión y usuario en la parte inferior de la barra lateral
if "user" in st.session_state:
    usr = st.session_state["user"]
else:
    usr = {"username": "-", "role": "-"}
version_text = f"Versión: {version}"
user_text = f"Usuario: {usr.get('username')} ({usr.get('role')})"
# Usamos HTML con posicion fixed dentro de la sidebar
st.sidebar.markdown(f"<div style='position: fixed; left: 16px; bottom: 16px; color: #8b949e; font-size:12px;'>" 
                    f"{version_text}<br>{user_text}</div>", unsafe_allow_html=True)

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
