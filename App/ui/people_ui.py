# import streamlit as st
# import pandas as pd
# from database.people import add_person, list_people

# def show_people():
#     st.header("Gestión de Personas")

#     with st.form("person_form"):
#         name = st.text_input("Nombre *")
#         email = st.text_input("Email")
#         role = st.text_input("Rol")
#         if st.form_submit_button("Agregar persona"):
#             if not name:
#                 st.error("El nombre es obligatorio")
#             else:
#                 add_person(name, email, role)
#                 st.success("Persona agregada")

#     st.subheader("Listado de personas")
#     df_people = pd.DataFrame(list_people(active_only=False))
#     st.dataframe(df_people)


import streamlit as st
import pandas as pd
from io import BytesIO
from database.people import list_people, add_person, update_person, delete_person

# Función auxiliar para exportar DataFrame a Excel
def to_excel(df, sheet_name="Personas"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def show_people():
    st.header("Gestión de Personas")

    # Crear persona
    with st.form("add_person_form"):
        name = st.text_input("Nombre *")
        email = st.text_input("Email")
        role = st.selectbox("Rol", ["user", "Admin"])
        active = st.checkbox("Activo", value=True)
        if st.form_submit_button("Agregar persona"):
            if not name:
                st.error("El nombre es obligatorio")
            else:
                add_person(name, email, role, 1 if active else 0)
                st.success("Persona agregada correctamente")
                # recargar lista
                people_df = pd.DataFrame(list_people(active_only=False))
                st.dataframe(people_df)
                return

    st.subheader("Listado de personas")
    people_df = pd.DataFrame(list_people(active_only=False))
    st.dataframe(people_df)

    # Botón para descargar en Excel
    if not people_df.empty:
        st.download_button(
            label="📥 Descargar personas en Excel",
            data=to_excel(people_df),
            file_name="personas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # 🔥 Acciones solo si el logueado es Admin
    if "user" in st.session_state and st.session_state["user"]["role"] == "Admin":
        st.subheader("Administrar personas")

        if not people_df.empty:
            selected = st.selectbox("Selecciona persona", people_df["name"].tolist())
            person_row = people_df[people_df["name"] == selected].iloc[0]

            with st.form("edit_person_form"):
                new_name = st.text_input("Nombre", person_row["name"])
                new_email = st.text_input("Email", person_row.get("email", ""))
                new_role = st.selectbox("Rol", ["user", "Admin"], index=0 if person_row["role"]=="user" else 1)
                new_active = st.checkbox("Activo", value=bool(person_row["active"]))
                if st.form_submit_button("Guardar cambios"):
                    update_person(
                        person_row["id"],
                        name=new_name,
                        email=new_email,
                        role=new_role,
                        active=1 if new_active else 0
                    )
                    st.success("Persona actualizada")
                    people_df = pd.DataFrame(list_people(active_only=False))
                    st.dataframe(people_df)
                    return

            if st.button("Eliminar persona"):
                delete_person(person_row["id"])
                st.success("Persona eliminada")
                people_df = pd.DataFrame(list_people(active_only=False))
                st.dataframe(people_df)
                return
