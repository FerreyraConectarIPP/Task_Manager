import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.tasks import add_task, get_tasks_df, update_task

def show_tasks(people_names, people_map):
    st.header("Gestión de Tareas")

    tab1, tab2, tab3 = st.tabs(["Registrar tarea", "Listado", "Editar tarea"])

    # Registrar tarea
    with tab1:
        with st.form("task_form"):
            task_id = st.text_input("ID de la tarea *")

            project = st.text_input("Proyecto asociado *")
            origin = st.text_input("Origen *")
            category = st.text_input("Categoría *")
            task_type = st.text_input("Tipo de tarea *")
            description = st.text_area("Descripción *")
            responsible = st.selectbox("Responsable *", people_names)
            status = st.selectbox("Estado *", ["Pendiente", "En progreso", "Completada", "Cancelada"])

            start_date = st.date_input("Fecha inicio *", date.today())
            start_time = st.time_input("Hora inicio (opcional)", value=None)
            end_date = st.date_input("Fecha fin (opcional)", value=None)
            end_time = st.time_input("Hora fin (opcional)", value=None)

            if st.form_submit_button("Registrar tarea"):
                if not task_id or not project or not origin or not category or not task_type or not description:
                    st.error("❌ Faltan campos obligatorios")
                else:
                    new_id = add_task(
                        task_id, project, origin, category, task_type, description,
                        people_map[responsible], status,
                        start_date.isoformat(),
                        start_time.isoformat() if start_time else None,
                        end_date.isoformat() if end_date else None,
                        end_time.isoformat() if end_time else None
                    )
                    st.success(f"✅ Tarea registrada correctamente con ID {new_id}")

    # Listado
    with tab2:
        df = get_tasks_df()
        if df.empty:
            st.info("No hay tareas registradas")
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
                "id", "project", "origin", "category", "task_type",
                "status", "responsible_name",
                "start_date", "start_time", "end_date", "end_time", "hours"
            ]])

            # 👉 Botón para descargar en Excel
            from io import BytesIO

            def to_excel(df, sheet_name="Tareas"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
                return output.getvalue()

            st.download_button(
                label="📥 Descargar tareas filtradas en Excel",
                data=to_excel(filtered_df),
                file_name="tareas_filtradas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 👉 Botón para descargar en CSV
            st.download_button(
                label="📥 Descargar tareas filtradas en CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="tareas_filtradas.csv",
                mime="text/csv"
            )

    # # Listado
    # with tab2:
    #     df = get_tasks_df()
    #     if df.empty:
    #         st.info("No hay tareas registradas")
    #     else:
    #         st.dataframe(df[[
    #             "id", "project", "origin", "category", "task_type",
    #             "status", "responsible_name",
    #             "start_date", "start_time", "end_date", "end_time", "hours"
    #         ]])

    #         # 👉 Botón para descargar en Excel
    #         from io import BytesIO

    #         def to_excel(df, sheet_name="Tareas"):
    #             output = BytesIO()
    #             with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    #                 df.to_excel(writer, index=False, sheet_name=sheet_name)
    #             return output.getvalue()

    #         st.download_button(
    #             label="📥 Descargar tareas en Excel",
    #             data=to_excel(df),
    #             file_name="tareas.xlsx",
    #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         )

    #         # 👉 Botón para descargar en CSV
    #         st.download_button(
    #             label="📥 Descargar tareas en CSV",
    #             data=df.to_csv(index=False).encode("utf-8"),
    #             file_name="tareas.csv",
    #             mime="text/csv"
    #         )

    # # with tab2:
    # #     df = get_tasks_df()
    # #     if df.empty:
    # #         st.info("No hay tareas registradas")
    # #     else:
    # #         st.dataframe(df[[
    # #             "id", "project", "origin", "category", "task_type",
    # #             "status", "responsible_name",
    # #             "start_date", "start_time", "end_date", "end_time", "hours"
    # #         ]])

    # #         # st.dataframe(df[[
    # #         #     "id", "project", "origin", "category", "task_type",
    # #         #     "status", "responsible_name",
    # #         #     "start_date", "start_time", "end_date", "end_time" # "time_spent"
    # #         # ]])

    # Editar tarea
    with tab3:
        df = get_tasks_df()
        if df.empty:
            st.info("No hay tareas para editar")
        else:
            task_id = st.selectbox("Selecciona tarea a editar", df["id"].tolist())
            selected = df[df["id"] == task_id].iloc[0]

            with st.form("edit_task_form"):
                project = st.text_input("Proyecto", selected["project"])
                origin = st.text_input("Origen", selected["origin"])
                category = st.text_input("Categoría", selected["category"])
                task_type = st.text_input("Tipo de tarea", selected["task_type"])
                description = st.text_area("Descripción", selected["description"])
                status = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada", "Cancelada"],
                                      index=["Pendiente","En progreso","Completada","Cancelada"].index(selected["status"]) if selected["status"] in ["Pendiente","En progreso","Completada","Cancelada"] else 0)

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

                # start_date = st.date_input(
                #     "Fecha inicio",
                #     selected["start_date"].date() if pd.notnull(selected["start_date"]) else None
                # )
                # start_time = st.time_input(
                #     "Hora inicio",
                #     selected["start_time"].time() if pd.notnull(selected["start_time"]) else None
                # )
                # end_date = st.date_input(
                #     "Fecha fin",
                #     selected["end_date"].date() if pd.notnull(selected["end_date"]) else None
                # )
                # end_time = st.time_input(
                #     "Hora fin",
                #     selected["end_time"].time() if pd.notnull(selected["end_time"]) else None
                # )

                # Mostrar tiempo invertido (no editable si lo calculás automáticamente)

                # st.number_input("Tiempo invertido (horas)", value=float(selected["time_spent"]), disabled=True)
                st.number_input("Horas calculadas", value=float(selected["hours"]), disabled=True)

                responsible = st.selectbox("Responsable", people_names,
                                           index=people_names.index(selected["responsible_name"]) if selected["responsible_name"] in people_names else 0)

                submitted_edit = st.form_submit_button("Guardar cambios")
                if submitted_edit:
                    rowcount = update_task(
                        task_id,
                        project=project, origin=origin, category=category, task_type=task_type,
                        description=description, status=status,
                        start_date=start_date.isoformat() if start_date else None,
                        start_time=start_time.isoformat() if start_time else None,
                        end_date=end_date.isoformat() if end_date else None,
                        end_time=end_time.isoformat() if end_time else None,
                        responsible_id=people_map[responsible]
                    )
                    if rowcount:
                        st.success("✅ Tarea actualizada correctamente")
