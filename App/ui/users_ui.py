import streamlit as st
import pandas as pd
from io import BytesIO
from database.users import add_user, list_users, update_user, delete_user, list_user_sessions

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()

def show_users():
    st.header("Gestión de Usuarios")

    # Crear usuario
    with st.form("user_form"):
        username = st.text_input("Nombre de usuario *")
        password = st.text_input("Contraseña *", type="password")
        email = st.text_input("Email (opcional)")
        role = st.selectbox("Rol", ["user", "Admin"])
        if st.form_submit_button("Agregar usuario"):
            if not username or not password:
                st.error("El usuario y la contraseña son obligatorios")
            else:
                add_user(username, password, role, email=email if email else None)
                st.success("Usuario agregado correctamente")
                st.rerun()

    st.subheader("Listado de usuarios")
    users_df = pd.DataFrame(list_users())
    st.dataframe(users_df)

    # 👇 botón para descargar en Excel
    if not users_df.empty:
        st.download_button(
            label="📥 Descargar usuarios en Excel",
            data=to_excel(users_df),
            file_name="usuarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # 🔥 Acciones solo si el logueado es Admin
    if "user" in st.session_state and st.session_state["user"]["role"] == "Admin":
        st.subheader("Administrar usuarios")

        if not users_df.empty:
            selected = st.selectbox("Selecciona usuario", users_df["username"].tolist())
            user_row = users_df[users_df["username"] == selected].iloc[0]

            with st.form("edit_user_form"):
                new_username = st.text_input("Usuario", user_row["username"])
                new_password = st.text_input("Contraseña (dejar vacío si no cambia)", type="password")
                new_email = st.text_input("Email (dejar vacío si no cambia)", user_row.get("email", ""))
                new_role = st.selectbox("Rol", ["user", "Admin"], index=0 if user_row["role"]=="user" else 1)
                if st.form_submit_button("Guardar cambios"):
                    update_user(user_row["id"],
                                username=new_username,
                                password=new_password if new_password else None,
                                role=new_role,
                                email=new_email if new_email else None)
                    st.success("Usuario actualizado")
                    st.rerun()

            if st.button("Eliminar usuario"):
                delete_user(user_row["id"])
                st.success("Usuario eliminado")
                st.rerun()

        # 👇 Historial de accesos con filtro por fecha
        st.subheader("Historial de accesos")
        df_sessions = pd.DataFrame(list_user_sessions())

        if not df_sessions.empty:
            df_sessions["login_time"] = pd.to_datetime(df_sessions["login_time"])
            df_sessions["logout_time"] = pd.to_datetime(df_sessions["logout_time"])

            min_date = df_sessions["login_time"].min().date()
            max_date = df_sessions["login_time"].max().date()

            start_date = st.date_input("Fecha inicio", min_date, key="start_admin")
            end_date = st.date_input("Fecha fin", max_date, key="end_admin")

            mask = (df_sessions["login_time"].dt.date >= start_date) & (df_sessions["login_time"].dt.date <= end_date)
            filtered_df = df_sessions.loc[mask]

            st.dataframe(filtered_df)

            # 👇 botón para descargar historial en Excel
            st.download_button(
                label="📥 Descargar historial en Excel",
                data=to_excel(filtered_df),
                file_name="historial_accesos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay sesiones registradas todavía.")
