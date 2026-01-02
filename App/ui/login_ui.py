# import streamlit as st
# from database.users import authenticate

# def show_login():
#     st.title("🔐 Login")

#     username = st.text_input("Usuario")
#     password = st.text_input("Contraseña", type="password")

#     if st.button("Ingresar"):
#         user = authenticate(username, password)
#         if user:
#             st.success(f"Bienvenido {username}")
#             st.session_state["user"] = user  # 🔥 guardar sesión
#         else:
#             st.error("Usuario o contraseña incorrectos")


import streamlit as st
from database.users import authenticate_user, log_user_login, log_user_logout

def show_login():
    st.header("Inicio de sesión")

    if "user" not in st.session_state:
        # Formulario de login
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar"):
                user = authenticate_user(username, password)
                if user:
                    # 👇 registrar login
                    session_id = log_user_login(user["id"])
                    st.session_state["user"] = user
                    st.session_state["session_id"] = session_id
                    st.success(f"Bienvenido {user['username']}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        # Enlace / botón para recuperar contraseña
        if st.button("¿Olvidaste tu contraseña?"):
            st.session_state["show_forgot"] = True

        if st.session_state.get("show_forgot"):
            st.markdown("### Recuperar contraseña")
            with st.form("forgot_form"):
                forgot_email = st.text_input("Introduce tu email registrado")
                forgot_username = st.text_input("(Opcional) Nombre de usuario (si lo conoces)")
                # Normalizar y validar formato del email antes de procesar
                if forgot_email:
                    forgot_email = forgot_email.strip()
                if forgot_username:
                    forgot_username = forgot_username.strip()
                if st.form_submit_button("Enviar enlace de restablecimiento"):
                    import re
                    from database.users import get_user_by_email, get_user_by_username, update_user
                    from database.password_reset import create_reset_token
                    from utils.mailer import send_reset_email
                    from database.settings import get_setting

                    # Validar formato de email si se introdujo
                    if forgot_email and not re.match(r"[^@]+@[^@]+\.[^@]+", forgot_email):
                        st.error("Formato de correo inválido. Revisa y vuelve a intentar.")
                    else:
                        user_row = None
                        if forgot_email:
                            user_row = get_user_by_email(forgot_email)
                        if not user_row and forgot_username:
                            user_row = get_user_by_username(forgot_username)

                        # Si no se encuentra en users, buscar en contactos guardados y intentar mapear
                        if not user_row and forgot_email:
                            from database.email_contacts import get_contact_by_email

                            contact = get_contact_by_email(forgot_email)
                            if contact:
                                # intentar mapear a un usuario existente por la parte local del email
                                local = contact.get("email").split("@")[0]
                                matched = get_user_by_username(local)
                                if matched:
                                    if not matched.get("email"):
                                        update_user(matched["id"], email=contact.get("email"))
                                        st.info(f"Se ha vinculado el email {contact.get('email')} al usuario {matched.get('username')}")
                                    user_row = get_user_by_username(local)
                                else:
                                    # intentar mapear por nombre
                                    name = contact.get("name")
                                    if name:
                                        maybe = get_user_by_username(name)
                                        if maybe:
                                            if not maybe.get("email"):
                                                update_user(maybe["id"], email=contact.get("email"))
                                                st.info(f"Se ha vinculado el email {contact.get('email')} al usuario {maybe.get('username')}")
                                            user_row = get_user_by_username(name)

                        # Si no se encontró por email, intentar buscar por nombre en contactos
                        if not user_row and forgot_username:
                            from database.email_contacts import get_contact_by_name
                            contact_by_name = get_contact_by_name(forgot_username)
                            if contact_by_name:
                                local = contact_by_name.get("email").split("@")[0]
                                matched = get_user_by_username(local)
                                if matched:
                                    if not matched.get("email"):
                                        update_user(matched["id"], email=contact_by_name.get("email"))
                                        st.info(f"Se ha vinculado el email {contact_by_name.get('email')} al usuario {matched.get('username')}")
                                    user_row = get_user_by_username(local)
                                else:
                                    maybe = get_user_by_username(contact_by_name.get("name"))
                                    if maybe:
                                        if not maybe.get("email"):
                                            update_user(maybe["id"], email=contact_by_name.get("email"))
                                            st.info(f"Se ha vinculado el email {contact_by_name.get('email')} al usuario {maybe.get('username')}")
                                        user_row = get_user_by_username(contact_by_name.get("name"))

                        if not user_row:
                            st.error("No se encontró un usuario con esos datos. Asegúrate de que el correo esté registrado o esté en la lista de contactos (Menú Admin → Correos).")
                        else:
                            to_email = forgot_email or user_row.get("email")
                            st.info(f"Se enviará el enlace de restablecimiento a: {to_email}")

                            base_url = get_setting("APP_BASE_URL") or __import__("os").environ.get("APP_BASE_URL") or "http://localhost:8501"
                            # Si user_row tiene id (usuario), crear token normal; si no, crear token con email para invitación
                            if user_row.get("id"):
                                token = create_reset_token(user_row.get("id"))
                            else:
                                token = create_reset_token(user_id=None, email=to_email)
                            reset_link = f"{base_url.rstrip('/')}/?reset_token={token}"
                            ok, msg = send_reset_email(to_email, user_row.get("username") or to_email, reset_link)
                            if ok:
                                st.success("Se ha enviado un enlace para restablecer la contraseña. Revisa tu bandeja de entrada.")
                                # limpiar estado
                                st.session_state.pop("show_forgot", None)
                            else:
                                st.error(f"No se pudo enviar el correo: {msg}")
                                st.info("Ponte en contacto con el administrador para que configure SMTP.")
    else:
        st.info(f"Usuario conectado: {st.session_state['user']['username']}")
        if st.button("Cerrar sesión"):
            if "session_id" in st.session_state:
                log_user_logout(st.session_state["session_id"])
            st.session_state.clear()
            st.success("Sesión cerrada")
            st.rerun()
