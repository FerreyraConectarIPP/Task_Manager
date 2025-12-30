import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.requirements import add_requirement, get_requirements_df, update_requirement

def show_requirements(people_names, people_map):
    st.header("Gestión de Requerimientos")

    tab1, tab2, tab3 = st.tabs(["Registrar requerimiento", "Listado", "Editar requerimiento"])

    # Registrar requerimiento
    with tab1:
        with st.form("req_form"):
            req_id = st.text_input("ID del requerimiento *")
            origin = st.text_input("Origen *")
            requester = st.text_input("Solicitante *")
            project = st.text_input("Proyecto asociado *")
            category = st.text_input("Categoría *")
            req_type = st.text_input("Tipo de requerimiento *")
            description = st.text_area("Descripción *")
            received_at = st.date_input("Fecha de recepción *", date.today())
            responsible = st.selectbox("Responsable *", people_names)
            status = st.selectbox("Estado *", ["Pendiente", "En análisis", "En desarrollo", "Completado"])

            # Campos opcionales de inicio y fin
            start_date = st.date_input("Fecha inicio (opcional)", value=None)
            start_time = st.time_input("Hora inicio (opcional)", value=None)
            end_date = st.date_input("Fecha fin (opcional)", value=None)
            end_time = st.time_input("Hora fin (opcional)", value=None)

            if st.form_submit_button("Registrar requerimiento"):
                if not req_id or not origin or not requester or not project or not category or not req_type or not description:
                    st.error("❌ Faltan campos obligatorios")
                else:
                    new_id = add_requirement(
                        req_id, project, origin, requester, category, req_type, description,
                        people_map[responsible], status,
                        start_date.isoformat() if start_date else None,
                        start_time.isoformat() if start_time else None,
                        end_date.isoformat() if end_date else None,
                        end_time.isoformat() if end_time else None,
                        received_at.isoformat() if received_at else None
                    )

                    st.success(f"✅ Requerimiento registrado correctamente con ID {new_id}")

    # # Listado
    # with tab2:
    #     df = get_requirements_df()
    #     if df.empty:
    #         st.info("No hay requerimientos registrados")
    #     else:
    #         st.dataframe(df[[
    #             "id", "origin", "requester", "project", "category", "req_type",
    #             "status", "responsible_name",
    #             "received_at", "start_date", "start_time", "end_date", "end_time", "hours"
    #         ]])
    # Listado
    # with tab2:
    #     df = get_requirements_df()
    #     if df.empty:
    #         st.info("No hay requerimientos registrados")
    #     else:
    #         st.dataframe(df[[
    #             "id", "origin", "requester", "project", "category", "req_type",
    #             "status", "responsible_name",
    #             "received_at", "start_date", "start_time", "end_date", "end_time", "hours"
    #         ]])

    #         # 👉 Botón para descargar en Excel
    #         from io import BytesIO

    #         def to_excel(df, sheet_name="Requerimientos"):
    #             output = BytesIO()
    #             with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    #                 df.to_excel(writer, index=False, sheet_name=sheet_name)
    #             return output.getvalue()

    #         st.download_button(
    #             label="📥 Descargar requerimientos en Excel",
    #             data=to_excel(df),
    #             file_name="requerimientos.xlsx",
    #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         )

    #         # 👉 Botón para descargar en CSV
    #         st.download_button(
    #             label="📥 Descargar requerimientos en CSV",
    #             data=df.to_csv(index=False).encode("utf-8"),
    #             file_name="requerimientos.csv",
    #             mime="text/csv"
    #         )

    with tab2:
        df = get_requirements_df()
        if df.empty:
            st.info("No hay requerimientos registrados")
        else:
            col1, col2 = st.columns(2)
            min_date = df["received_at"].min().date() if pd.notnull(df["received_at"]).any() else date.today()
            max_date = df["received_at"].max().date() if pd.notnull(df["received_at"]).any() else date.today()

            start_filter = col1.date_input("Fecha desde", min_date)
            end_filter = col2.date_input("Fecha hasta", max_date)

            df["received_at"] = pd.to_datetime(df["received_at"], errors="coerce")

            mask = (df["received_at"].dt.date >= start_filter) & (df["received_at"].dt.date <= end_filter)
            filtered_df = df.loc[mask]

            st.dataframe(filtered_df[[
                "id", "origin", "requester", "project", "category", "req_type",
                "status", "responsible_name",
                "received_at", "start_date", "start_time", "end_date", "end_time", "hours"
            ]])

            from io import BytesIO

            def to_excel(df, sheet_name="Requerimientos"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
                return output.getvalue()

            st.download_button(
                label="📥 Descargar requerimientos filtrados en Excel",
                data=to_excel(filtered_df),
                file_name="requerimientos_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.download_button(
                label="📥 Descargar requerimientos filtrados en CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="requerimientos_filtrados.csv",
                mime="text/csv"
            )


    # Editar requerimiento
    with tab3:
        df = get_requirements_df()
        if df.empty:
            st.info("No hay requerimientos para editar")
        else:
            req_id = st.selectbox("Selecciona requerimiento a editar", df["id"].tolist())
            selected = df[df["id"] == req_id].iloc[0]

            with st.form("edit_req_form"):
                origin = st.text_input("Origen", selected["origin"])
                requester = st.text_input("Solicitante", selected["requester"])
                project = st.text_input("Proyecto", selected["project"])
                category = st.text_input("Categoría", selected["category"])
                req_type = st.text_input("Tipo de requerimiento", selected["req_type"])
                description = st.text_area("Descripción", selected["description"])
                status = st.selectbox("Estado", ["Pendiente", "En análisis", "En desarrollo", "Completado"],
                                      index=["Pendiente","En análisis","En desarrollo","Completado"].index(selected["status"]) if selected["status"] in ["Pendiente","En análisis","En desarrollo","Completado"] else 0)

                received_at = st.date_input(
                    "Fecha de recepción",
                    selected["received_at"].date() if pd.notnull(selected["received_at"]) else None
                )

                start_date = st.date_input(
                    "Fecha inicio",
                    selected["start_date"].date() if pd.notnull(selected["start_date"]) else None
                )
                start_time = st.time_input(
                    "Hora inicio",
                    datetime.strptime(str(selected["start_time"]), "%H:%M:%S").time()
                    if pd.notnull(selected["start_time"]) else None
                )
                end_date = st.date_input(
                    "Fecha fin",
                    selected["end_date"].date() if pd.notnull(selected["end_date"]) else None
                )
                end_time = st.time_input(
                    "Hora fin",
                    datetime.strptime(str(selected["end_time"]), "%H:%M:%S").time()
                    if pd.notnull(selected["end_time"]) else None
                )

                st.number_input("Horas calculadas", value=float(selected["hours"]), disabled=True)

                responsible = st.selectbox("Responsable", people_names,
                                           index=people_names.index(selected["responsible_name"]) if selected["responsible_name"] in people_names else 0)

                submitted_edit = st.form_submit_button("Guardar cambios")
                if submitted_edit:
                    rowcount = update_requirement(
                        req_id,
                        origin=origin, requester=requester, project=project,
                        category=category, req_type=req_type, description=description,
                        status=status,
                        start_date=start_date.isoformat() if start_date else None,
                        start_time=start_time.isoformat() if start_time else None,
                        end_date=end_date.isoformat() if end_date else None,
                        end_time=end_time.isoformat() if end_time else None,
                        responsible_id=people_map[responsible],
                        received_at=received_at.isoformat() if received_at else None
                    )
                    if rowcount:
                        st.success("✅ Requerimiento actualizado correctamente")
