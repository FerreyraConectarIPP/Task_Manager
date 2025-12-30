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
    else:
        st.info(f"Usuario conectado: {st.session_state['user']['username']}")
        if st.button("Cerrar sesión"):
            if "session_id" in st.session_state:
                log_user_logout(st.session_state["session_id"])
            st.session_state.clear()
            st.success("Sesión cerrada")
            st.rerun()
