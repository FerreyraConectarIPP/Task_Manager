import streamlit as st
from database.settings import get_setting, set_setting
from utils.mailer import test_smtp


def show_settings():
    st.header("Ajustes de la aplicación")

    st.subheader("SMTP / Correo saliente")
    smtp_server = st.text_input("SMTP_SERVER", value=get_setting("SMTP_SERVER") or "")
    smtp_port = st.text_input("SMTP_PORT", value=get_setting("SMTP_PORT") or "587")
    smtp_user = st.text_input("SMTP_USER", value=get_setting("SMTP_USER") or "")
    smtp_password = st.text_input("SMTP_PASSWORD", value=get_setting("SMTP_PASSWORD") or "", type="password")
    smtp_from = st.text_input("SMTP_FROM", value=get_setting("SMTP_FROM") or "")

    st.subheader("General")
    app_base_url = st.text_input("APP_BASE_URL", value=get_setting("APP_BASE_URL") or "http://localhost:8501")

    if st.button("Guardar ajustes"):
        set_setting("SMTP_SERVER", smtp_server)
        set_setting("SMTP_PORT", smtp_port)
        set_setting("SMTP_USER", smtp_user)
        set_setting("SMTP_PASSWORD", smtp_password)
        set_setting("SMTP_FROM", smtp_from)
        set_setting("APP_BASE_URL", app_base_url)
        st.success("Ajustes guardados correctamente.")

    st.markdown("---")
    st.subheader("Probar SMTP")
    test_email = st.text_input("Email de destino para prueba", value=get_setting("SMTP_FROM") or "")
    if st.button("Enviar correo de prueba"):
        ok, msg = test_smtp(test_email)
        if ok:
            st.success(msg)
        else:
            st.error(f"No se pudo enviar el correo: {msg}")

    st.info("Nota: estas configuraciones se guardan en la base de datos y se usan para enviar correos para restablecer contraseñas.")
