import streamlit as st
from datetime import datetime
from database.internal import (add_internal_activity,update_internal_activity,get_internal_activities_df)
import pandas as pd
def show_internal(people_names, people_map):
    st.header("Gestión de Actividades Internas")

    tab1, tab2, tab3 = st.tabs(["Registrar actividad", "Listado", "Editar"])

    # -------------------------------
    # TAB 1: Registrar nueva actividad
    # -------------------------------
    with tab1:
        with st.form("internal_activity_form"):
            # st.info("Actividad interna: trabajo interno no solicitado externamente")

            activity_id = st.text_input("ID de actividad *")
            category = st.selectbox(
                "Categoría *",
                [
                    "Documentación / Procedimientos",
                    "Capacitación",
                    "Mejora de procesos",
                    "Automatización / Herramientas",
                    "Gestión del área",
                    "Investigación / Evaluación técnica"
                ]
            )

            activity_type = st.selectbox(
                "Tipo *",
                [
                    "Documentación",
                    "Capacitación",
                    "Reunión",
                    "Análisis",
                    "Desarrollo interno",
                    "Investigación"
                ]
            )

            description = st.text_area("Descripción clara *")
            responsible = st.selectbox("Responsable *", people_names)
            start_date = st.date_input("Fecha inicio *", datetime.now())
            start_time = st.time_input("Hora inicio *", datetime.now().time())
            end_date = st.date_input("Fecha fin", value=None)
            end_time = st.time_input("Hora fin", value=None)
            status = st.selectbox("Estado *", ["Planificada", "En curso", "Finalizada"])

            if st.form_submit_button("Registrar actividad"):
                mandatory_missing = (
                    not activity_id or
                    not category or
                    not activity_type or
                    not description or
                    not responsible or
                    not start_date
                )

                if mandatory_missing:
                    st.error("❌ Faltan campos obligatorios")
                else:
                    add_internal_activity(
                        activity_id,
                        category,
                        activity_type,
                        description,
                        people_map[responsible],
                        start_date.isoformat(),
                        start_time.isoformat(),
                        end_date.isoformat() if end_date else None,
                        end_time.isoformat() if end_time else None,
                        status
                    )
                    st.success("✅ Actividad interna registrada correctamente")

    # # -------------------------------
    # # TAB 2: Listado de actividades
    # # -------------------------------
    # with tab2:
    #     df = get_internal_activities_df()
    #     if df.empty:
    #         st.info("No hay actividades internas registradas")
    #     else:
    #         st.dataframe(df[[
    #             "id", "category", "activity_type",
    #             "description", "status",
    #             "responsible_name",
    #             "start_date", "start_time",
    #             "end_date", "end_time",
    #             "hours"
    #         ]])


    # # -------------------------------
    # # TAB 2: Listado de actividades
    # # -------------------------------
    # with tab2:
    #     df = get_internal_activities_df()
    #     if df.empty:
    #         st.info("No hay actividades internas registradas")
    #     else:
    #         st.dataframe(df[[
    #             "id", "category", "activity_type",
    #             "description", "status",
    #             "responsible_name",
    #             "start_date", "start_time",
    #             "end_date", "end_time",
    #             "hours"
    #         ]])

    #         # 👉 Botón para descargar en Excel
    #         from io import BytesIO

    #         def to_excel(df, sheet_name="ActividadesInternas"):
    #             output = BytesIO()
    #             with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    #                 df.to_excel(writer, index=False, sheet_name=sheet_name)
    #             return output.getvalue()

    #         st.download_button(
    #             label="📥 Descargar actividades internas en Excel",
    #             data=to_excel(df),
    #             file_name="actividades_internas.xlsx",
    #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         )

    #         # 👉 Botón para descargar en CSV
    #         st.download_button(
    #             label="📥 Descargar actividades internas en CSV",
    #             data=df.to_csv(index=False).encode("utf-8"),
    #             file_name="actividades_internas.csv",
    #             mime="text/csv"
    #         )

    # -------------------------------
    # TAB 2: Listado de actividades
    # -------------------------------
    with tab2:
        df = get_internal_activities_df()
        if df.empty:
            st.info("No hay actividades internas registradas")
        else:
            # 👉 Filtro por rango de fechas usando la columna start_date
            col1, col2 = st.columns(2)
            min_date = df["start_date"].min().date() if pd.notnull(df["start_date"]).any() else date.today()
            max_date = df["start_date"].max().date() if pd.notnull(df["start_date"]).any() else date.today()

            start_filter = col1.date_input("Fecha desde", min_date)
            end_filter = col2.date_input("Fecha hasta", max_date)

            # Asegurar que start_date sea datetime
            df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

            # Filtrar
            mask = (df["start_date"].dt.date >= start_filter) & (df["start_date"].dt.date <= end_filter)
            filtered_df = df.loc[mask]

            st.dataframe(filtered_df[[
                "id", "category", "activity_type",
                "description", "status",
                "responsible_name",
                "start_date", "start_time",
                "end_date", "end_time",
                "hours"
            ]])

            # 👉 Botón para descargar en Excel
            from io import BytesIO

            def to_excel(df, sheet_name="ActividadesInternas"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
                return output.getvalue()

            st.download_button(
                label="📥 Descargar actividades internas filtradas en Excel",
                data=to_excel(filtered_df),
                file_name="actividades_internas_filtradas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 👉 Botón para descargar en CSV
            st.download_button(
                label="📥 Descargar actividades internas filtradas en CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="actividades_internas_filtradas.csv",
                mime="text/csv"
            )


    # -------------------------------
    # TAB 3: Editar actividad existente
    # -------------------------------
    with tab3:
        df = get_internal_activities_df()
        if df.empty:
            st.info("No hay actividades internas para editar")
        else:
            selected_id = st.selectbox("Seleccionar actividad", df["id"])
            new_category = st.text_input("Nueva categoría", "")
            new_type = st.text_input("Nuevo tipo", "")
            new_description = st.text_area("Nueva descripción", "")
            new_status = st.selectbox("Nuevo estado", ["Planificada", "En curso", "Finalizada"])

            if st.button("Actualizar actividad"):
                update_internal_activity(
                    selected_id,
                    category=new_category if new_category else None,
                    activity_type=new_type if new_type else None,
                    description=new_description if new_description else None,
                    status=new_status
                )
                st.success("✅ Actividad actualizada correctamente")
