import streamlit as st
import pandas as pd
from io import BytesIO
from database.emails import get_logs


def to_excel(df, sheet_name="Correos"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def show_emails():
    st.header("Logs de correos enviados")

    # Sección: agregar contacto rápido
    st.subheader("Contactos de correo")
    from database.email_contacts import add_contact, list_contacts, delete_contact

    with st.form("add_contact_form"):
        col1, col2 = st.columns([2,3])
        name = col1.text_input("Nombre (opcional)")
        email = col2.text_input("Email")
        if st.form_submit_button("Agregar a la lista"):
            if not email:
                st.error("El email es obligatorio")
            else:
                add_contact(email.strip(), name.strip() if name else None)
                st.success("Contacto agregado")

    contacts = list_contacts()
    if contacts:
        st.write("**Contactos guardados:**")
        for c in contacts:
            st.write(f"- {c.get('name') or '-'} — {c.get('email')}  `id={c.get('id')}`")
            if st.button(f"Eliminar {c.get('id')}", key=f"del_{c.get('id')}"):
                delete_contact(c.get('id'))
                st.experimental_rerun()

    st.markdown("---")

    rows = get_logs(limit=1000)
    if not rows:
        st.info("No hay registros de correos todavía.")
    else:
        df = pd.DataFrame(rows)
        st.dataframe(df)

        if st.button("Descargar logs en Excel"):
            st.download_button(
                label="📥 Descargar correos en Excel",
                data=to_excel(df),
                file_name="email_logs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
