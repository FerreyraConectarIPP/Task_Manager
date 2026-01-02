import streamlit as st
from datetime import datetime, time, date
from database.incidents import add_incident, get_incidents_df, update_incident
import pandas as pd
from io import BytesIO
import xlsxwriter 

categorias = [
    "Operación AMI",
    "Hardware",
    "Software / HES / MDM",
    "Firmware / Configuración",
    "Datos / Medición",
    "Infraestructura / IT",
    "Integración",
    "Operativos / Proceso",
    "Seguridad",
    "Otro"
]

subtipos = {
    "Operación AMI": ["Comunicación", "Recolección"],
    "Hardware": ["Medidor", "DCU"],
    "Software / HES / MDM": ["HES", "MDM"],
    "Firmware / Configuración": ["Firmware", "Configuración"],
    "Datos / Medición": ["Datos"],
    "Infraestructura / IT": ["Servidor", "Red"],
    "Integración": ["Integración"],
    "Operativos / Proceso": ["Operativo"],
    "Seguridad": ["Seguridad"],
    "Otro": ["Otro"]
} 

def show_incidents(people_names, people_map):
    st.header("Gestión de Incidentes")

    # Callbacks para actualizar subtipos cuando cambia la categoría
    def _on_category_new_change():
        cat = st.session_state.get("category_new")
        st.session_state["subtype_new"] = subtipos.get(cat, [None])[0]
        st.session_state["last_category_new"] = cat

    def _on_category_edit_change():
        cat = st.session_state.get("category_edit")
        st.session_state["subtype_edit"] = subtipos.get(cat, [None])[0]
        st.session_state["last_category_edit"] = cat


    tab1, tab2, tab3 = st.tabs(["Registrar incidente", "Listado", "Editar incidente"])

    # Registrar incidente
    with tab1:
        # Selección de categoría fuera del formulario para que su cambio provoque re-render inmediato
        category = st.selectbox("Categoría *", categorias, key="category_new")
        # Inicializar subtipo si cambia la categoría
        if st.session_state.get("last_category_new") != category:
            st.session_state["subtype_new"] = subtipos.get(category, [None])[0]
            st.session_state["last_category_new"] = category

        with st.form("incident_form"):
            incident_id = st.text_input("ID del incidente (alfanumérico) *")
            project = st.text_input("Proyecto asociado *")

            # Mostrar la categoría seleccionada y permitir elegir subtipo dentro del formulario
            st.write(f"Categoría: **{category}**")
            subtype = st.selectbox(
                "Subtipo *",
                subtipos.get(category, []),
                key="subtype_new"
            )

            severity = st.radio("Severidad *", ["Baja", "Media", "Alta", "Crítica"], horizontal=True)
            description = st.text_area("Descripción *")
            detected_at = st.date_input("Fecha de detección *", value=date.today())
            responsible = st.selectbox("Responsable *", people_names)
            status = st.radio("Estado *", ["Abierto", "En análisis", "En resolución", "Cerrado"], horizontal=True)

            start_date = st.date_input("Fecha inicio *", value=date.today())
            start_time = st.time_input("Hora inicio (opcional)", value=None)
            end_date = st.date_input("Fecha fin (opcional)", value=date.today())
            end_time = st.time_input("Hora fin (opcional)", value=None)

            root_cause = st.text_area("Causa raíz")
            corrective_action = st.text_area("Acción correctiva")
            preventive_action = st.text_area("Acción preventiva")

            if st.form_submit_button("Registrar incidente"):
                if not incident_id or not project or not category or not severity or not description:
                    st.error("❌ Faltan campos obligatorios")
                else:
                    new_id = add_incident(
                        incident_id,
                        project,
                        category,
                        severity,
                        description,
                        date.fromisoformat(detected_at.isoformat()).isoformat(),
                        people_map[responsible],
                        status,
                        subtype,
                        start_date.isoformat(),
                        start_time.isoformat() if start_time else None,
                        end_date.isoformat() if end_date else None,
                        end_time.isoformat() if end_time else None,
                        root_cause,
                        corrective_action,
                        preventive_action
                    )
                    st.success(f"✅ Incidente registrado correctamente con ID {new_id}")

    # ver Listado
    with tab2:
        df = get_incidents_df()
        if df.empty:
            st.info("No hay incidentes registrados")
        else:
            # Asegurar que detected_at sea datetime antes de calcular rangos
            df["detected_at"] = pd.to_datetime(df["detected_at"], errors="coerce")

            col1, col2 = st.columns(2)
            min_date = (
                df["detected_at"].min().date()
                if pd.notnull(df["detected_at"]).any()
                else date.today()
            )
            max_date = (
                df["detected_at"].max().date()
                if pd.notnull(df["detected_at"]).any()
                else date.today()
            )

            start_filter = col1.date_input("Fecha desde", min_date)
            end_filter = col2.date_input("Fecha hasta", max_date)

            # Filtrar por rango
            mask = (df["detected_at"].dt.date >= start_filter) & (df["detected_at"].dt.date <= end_filter)
            filtered_df = df.loc[mask].copy()

            # Selección de columnas (incluir 'subtype' si existe)
            cols = [
                "id", "project", "category", "severity",
                "status", "responsible_name",
                "detected_at", "start_date", "start_time",
                "end_date", "end_time",
                "root_cause", "corrective_action", "preventive_action"
            ]
            if "subtype" in filtered_df.columns:
                cols.insert(3, "subtype")  # después de category

            # Mostrar la tabla renombrando 'subtype' a 'Subtipo' para claridad
            display_df = filtered_df[cols].copy()
            if "subtype" in display_df.columns:
                display_df = display_df.rename(columns={"subtype": "Subtipo"})

            st.dataframe(display_df)

            # Descargar Excel (renombrar columna para export)
            def to_excel(df_to_save, sheet_name="Incidentes"):
                df_save = df_to_save.copy()
                if "subtype" in df_save.columns:
                    df_save = df_save.rename(columns={"subtype": "Subtipo"})
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_save.to_excel(writer, index=False, sheet_name=sheet_name)
                return output.getvalue()

            # Incluir timestamp en nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_file_name = f"incidentes_filtrados_{timestamp}.xlsx"

            st.download_button(
                label="📥 Descargar incidentes filtrados en Excel",
                data=to_excel(filtered_df[cols]),
                file_name=excel_file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Descargar CSV (renombrar columna para export)
            csv_df = filtered_df[cols].copy()
            if "subtype" in csv_df.columns:
                csv_df = csv_df.rename(columns={"subtype": "Subtipo"})

            csv_file_name = f"incidentes_filtrados_{timestamp}.csv"
            st.download_button(
                label="📥 Descargar incidentes filtrados en CSV",
                data=csv_df.to_csv(index=False).encode("utf-8"),
                file_name=csv_file_name,
                mime="text/csv"
            )

    # Editar incidente
    with tab3:
        df = get_incidents_df()
        if df.empty:
            st.info("No hay incidentes para editar")
        else:
            incident_id = st.selectbox("Selecciona incidente a editar", df["id"].tolist())
            selected = df[df["id"] == incident_id].iloc[0]

            # Selección de categoría fuera del formulario para que su cambio actualice subtipos inmediatamente
            category = st.selectbox(
                "Categoría",
                categorias,
                index=categorias.index(selected["category"]) if selected["category"] in categorias else 0,
                key="category_edit"
            )

            # Inicializar el subtipo al cargar el incidente seleccionado
            subtype_key = "subtype_edit"
            if st.session_state.get("last_incident_selected") != incident_id:
                if "subtype" in selected and selected["subtype"] in subtipos.get(category, []):
                    st.session_state[subtype_key] = selected["subtype"]
                else:
                    st.session_state[subtype_key] = subtipos.get(category, [None])[0]
                st.session_state["last_incident_selected"] = incident_id
                st.session_state["last_category_edit"] = category

            # Si el usuario cambia la categoría durante la edición, resetear subtipo
            if st.session_state.get("last_category_edit") != category:
                st.session_state[subtype_key] = subtipos.get(category, [None])[0]
                st.session_state["last_category_edit"] = category

            with st.form("edit_incident_form"):
                project = st.text_input("Proyecto", selected["project"])
                st.write(f"Categoría: **{category}**")
                subtype = st.selectbox(
                    "Subtipo",
                    subtipos.get(category, []),
                    key=subtype_key
                )

                severity = st.radio(
                    "Severidad",
                    ["Baja", "Media", "Alta", "Crítica"],
                    index=["Baja", "Media", "Alta", "Crítica"].index(selected["severity"]) if selected["severity"] in ["Baja", "Media", "Alta", "Crítica"] else 1,
                    horizontal=True
                )
                description = st.text_area("Descripción", selected["description"])
                status = st.radio(
                    "Estado",
                    ["Abierto", "En análisis", "En resolución", "Cerrado"],
                    index=["Abierto", "En análisis", "En resolución", "Cerrado"].index(selected["status"]) if selected["status"] in ["Abierto", "En análisis", "En resolución", "Cerrado"] else 1,
                    horizontal=True
                )

                # Conversión segura de fechas/horas
                def to_date(val):
                    try:
                        return val.date() if hasattr(val, "date") else datetime.fromisoformat(val).date()
                    except Exception:
                        return date.today()

                def to_time(val):
                    try:
                        if hasattr(val, "hour"):
                            return val
                        return datetime.fromisoformat(val).time()
                    except Exception:
                        return None

                start_date_val = to_date(selected["start_date"]) if selected["start_date"] is not None else date.today()
                start_time_val = to_time(selected["start_time"]) if selected.get("start_time") else None
                end_date_val = to_date(selected["end_date"]) if selected["end_date"] is not None else None
                end_time_val = to_time(selected["end_time"]) if selected.get("end_time") else None

                start_date = st.date_input("Fecha inicio", start_date_val)
                start_time = st.time_input("Hora inicio (opcional)", value=start_time_val)
                end_date = st.date_input("Fecha fin (opcional)", value=end_date_val)
                end_time = st.time_input("Hora fin (opcional)", value=end_time_val)

                root_cause = st.text_area("Causa raíz", selected["root_cause"] or "")
                corrective_action = st.text_area("Acción correctiva", selected["corrective_action"] or "")
                preventive_action = st.text_area("Acción preventiva", selected["preventive_action"] or "")

                detected_at = st.date_input("Fecha de detección", to_date(selected["detected_at"]))
                responsible = st.selectbox(
                    "Responsable",
                    people_names,
                    index=people_names.index(selected["responsible_name"]) if selected["responsible_name"] in people_names else 0
                )

                submitted_edit = st.form_submit_button("Guardar cambios")
                if submitted_edit:
                    rowcount = update_incident(
                        incident_id=incident_id,
                        project=project,
                        category=category,
                        severity=severity,
                        description=description,
                        status=status,
                        subtype=subtype,
                        start_date=start_date.isoformat() if start_date else None,
                        start_time=start_time.isoformat() if start_time else None,
                        end_date=end_date.isoformat() if end_date else None,
                        end_time=end_time.isoformat() if end_time else None,
                        root_cause=root_cause or None,
                        corrective_action=corrective_action or None,
                        preventive_action=preventive_action or None,
                        detected_at=detected_at.isoformat() if detected_at else None,
                        responsible_id=people_map[responsible] if responsible else None
                    )

                    if rowcount:
                        st.success("✅ Incidente actualizado correctamente")
                    else:
                        st.warning("No se detectaron cambios para actualizar")



# import streamlit as st
# from datetime import datetime, date
# from database.incidents import add_incident, get_incidents_df, update_incident
# import pandas as pd
# from io import BytesIO
# import xlsxwriter

# categorias = [
#     "Operación AMI",
#     "Hardware",
#     "Software / HES / MDM",
#     "Firmware / Configuración",
#     "Datos / Medición",
#     "Infraestructura / IT",
#     "Integración",
#     "Operativos / Proceso",
#     "Seguridad"
# ]

# subtipos = {
#     "Operación AMI": ["Comunicación", "Recolección"],
#     "Hardware": ["Medidor", "DCU"],
#     "Software / HES / MDM": ["HES", "MDM"],
#     "Firmware / Configuración": ["Firmware", "Configuración"],
#     "Datos / Medición": ["Datos"],
#     "Infraestructura / IT": ["Servidor", "Red"],
#     "Integración": ["Integración"],
#     "Operativos / Proceso": ["Operativo"],
#     "Seguridad": ["Seguridad"]
# }


# def show_incidents(people_names, people_map):
#     st.header("Gestión de Incidentes")

#     tab1, tab2, tab3 = st.tabs(["Registrar incidente", "Listado", "Editar incidente"])

#     # --- Registrar incidente ---
#     with tab1:
#         with st.form("incident_form"):
#             incident_id = st.text_input("ID del incidente (alfanumérico) *")
#             project = st.text_input("Proyecto asociado *")

#             # Categoría y Subtipo dinámicos (key dependiente de la categoría)
#             category = st.selectbox("Categoría *", categorias, key="category_new")
#             subtype_key = f"subtype_new_{category}"
#             subtype = st.selectbox(
#                 "Subtipo *",
#                 subtipos[category],
#                 key=subtype_key,
#                 index=0
#             )

#             # Severidad simple con radio
#             severity = st.radio("Severidad *", ["Baja", "Media", "Alta", "Crítica"], horizontal=True)

#             description = st.text_area("Descripción *")
#             detected_at = st.date_input("Fecha de detección *", value=date.today())
#             responsible = st.selectbox("Responsable *", people_names)
#             status = st.selectbox("Estado *", ["Abierto", "En análisis", "En resolución", "Cerrado"])

#             start_date = st.date_input("Fecha inicio *", value=date.today())
#             start_time = st.time_input("Hora inicio (opcional)", value=None)
#             end_date = st.date_input("Fecha fin (opcional)", value=date.today())
#             end_time = st.time_input("Hora fin (opcional)", value=None)

#             root_cause = st.text_area("Causa raíz")
#             corrective_action = st.text_area("Acción correctiva")
#             preventive_action = st.text_area("Acción preventiva")

#             submitted_new = st.form_submit_button("Registrar incidente")
#             if submitted_new:
#                 if not incident_id or not project or not category or not severity or not description:
#                     st.error("❌ Faltan campos obligatorios")
#                 else:
#                     try:
#                         new_id = add_incident(
#                             incident_id,
#                             project,
#                             category,
#                             severity,
#                             description,
#                             detected_at.isoformat(),
#                             people_map[responsible],
#                             status,
#                             start_date.isoformat(),
#                             start_time.isoformat() if start_time else None,
#                             end_date.isoformat() if end_date else None,
#                             end_time.isoformat() if end_time else None,
#                             root_cause or None,
#                             corrective_action or None,
#                             preventive_action or None,
#                             subtype  # guardar subtipo (asegúrate de que add_incident lo soporte)
#                         )
#                         st.success(f"✅ Incidente registrado correctamente con ID {new_id}")
#                     except Exception as e:
#                         st.error(f"Error al registrar incidente: {e}")

#     # --- Listado ---
#     with tab2:
#         df = get_incidents_df()
#         if df.empty:
#             st.info("No hay incidentes registrados")
#         else:
#             # Asegurar tipo datetime
#             df["detected_at"] = pd.to_datetime(df["detected_at"], errors="coerce")

#             col1, col2 = st.columns(2)
#             min_date = df["detected_at"].min().date() if pd.notnull(df["detected_at"]).any() else date.today()
#             max_date = df["detected_at"].max().date() if pd.notnull(df["detected_at"]).any() else date.today()

#             start_filter = col1.date_input("Fecha desde", min_date)
#             end_filter = col2.date_input("Fecha hasta", max_date)

#             mask = (df["detected_at"].dt.date >= start_filter) & (df["detected_at"].dt.date <= end_filter)
#             filtered_df = df.loc[mask].copy()

#             # Columnas (incluye subtipo si existe)
#             cols = [
#                 "id", "project", "category", "severity",
#                 "status", "responsible_name",
#                 "detected_at", "start_date", "start_time",
#                 "end_date", "end_time",
#                 "root_cause", "corrective_action", "preventive_action"
#             ]
#             if "subtype" in filtered_df.columns:
#                 cols.insert(3, "subtype")

#             st.dataframe(filtered_df[cols])

#             # Exportar
#             def to_excel(df_to_save, sheet_name="Incidentes"):
#                 output = BytesIO()
#                 with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#                     df_to_save.to_excel(writer, index=False, sheet_name=sheet_name)
#                 return output.getvalue()

#             st.download_button(
#                 label="📥 Descargar incidentes filtrados en Excel",
#                 data=to_excel(filtered_df[cols]),
#                 file_name="incidentes_filtrados.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

#             st.download_button(
#                 label="📥 Descargar incidentes filtrados en CSV",
#                 data=filtered_df[cols].to_csv(index=False).encode("utf-8"),
#                 file_name="incidentes_filtrados.csv",
#                 mime="text/csv"
#             )

#     # --- Editar incidente ---
#     with tab3:
#         df = get_incidents_df()
#         if df.empty:
#             st.info("No hay incidentes para editar")
#         else:
#             incident_id = st.selectbox("Selecciona incidente a editar", df["id"].tolist())
#             selected = df[df["id"] == incident_id].iloc[0]

#             with st.form("edit_incident_form"):
#                 project = st.text_input("Proyecto", selected["project"])
#                 category = st.selectbox(
#                     "Categoría",
#                     categorias,
#                     index=categorias.index(selected["category"]) if selected["category"] in categorias else 0,
#                     key="category_edit"
#                 )

#                 # Subtipo dependiente de categoría (key dinámica)
#                 subtype_key = f"subtype_edit_{category}"
#                 subtype_options = subtipos[category]
#                 if "subtype" in selected and selected["subtype"] in subtype_options:
#                     subtype_index = subtype_options.index(selected["subtype"])
#                 else:
#                     subtype_index = 0

#                 subtype = st.selectbox(
#                     "Subtipo",
#                     subtype_options,
#                     index=subtype_index,
#                     key=subtype_key
#                 )

#                 severity = st.radio(
#                     "Severidad",
#                     ["Baja", "Media", "Alta", "Crítica"],
#                     index=["Baja", "Media", "Alta", "Crítica"].index(selected["severity"]) if selected["severity"] in ["Baja", "Media", "Alta", "Crítica"] else 1,
#                     horizontal=True
#                 )
#                 description = st.text_area("Descripción", selected["description"])
#                 status = st.selectbox(
#                     "Estado",
#                     ["Abierto", "En análisis", "En resolución", "Cerrado"],
#                     index=["Abierto", "En análisis", "En resolución", "Cerrado"].index(selected["status"]) if selected["status"] in ["Abierto", "En análisis", "En resolución", "Cerrado"] else 0
#                 )

#                 # Conversión segura de fechas/horas
#                 def to_date(val):
#                     try:
#                         return val.date() if hasattr(val, "date") else datetime.fromisoformat(val).date()
#                     except Exception:
#                         return date.today()

#                 def to_time(val):
#                     try:
#                         if hasattr(val, "hour"):
#                             return val
#                         return datetime.fromisoformat(val).time()
#                     except Exception:
#                         return None

#                 start_date_val = to_date(selected.get("start_date")) if selected.get("start_date") else date.today()
#                 start_time_val = to_time(selected.get("start_time")) if selected.get("start_time") else None
#                 end_date_val = to_date(selected.get("end_date")) if selected.get("end_date") else None
#                 end_time_val = to_time(selected.get("end_time")) if selected.get("end_time") else None

#                 start_date = st.date_input("Fecha inicio", start_date_val)
#                 start_time = st.time_input("Hora inicio (opcional)", value=start_time_val)
#                 end_date = st.date_input("Fecha fin (opcional)", value=end_date_val)
#                 end_time = st.time_input("Hora fin (opcional)", value=end_time_val)

#                 root_cause = st.text_area("Causa raíz", selected.get("root_cause") or "")
#                 corrective_action = st.text_area("Acción correctiva", selected.get("corrective_action") or "")
#                 preventive_action = st.text_area("Acción preventiva", selected.get("preventive_action") or "")

#                 detected_at = st.date_input("Fecha de detección", to_date(selected["detected_at"]))
#                 responsible = st.selectbox(
#                     "Responsable",
#                     people_names,
#                     index=people_names.index(selected["responsible_name"]) if selected["responsible_name"] in people_names else 0
#                 )

#                 submitted_edit = st.form_submit_button("Guardar cambios")
#                 if submitted_edit:
#                     try:
#                         rowcount = update_incident(
#                             incident_id=incident_id,
#                             project=project,
#                             category=category,
#                             severity=severity,
#                             description=description,
#                             status=status,
#                             start_date=start_date.isoformat() if start_date else None,
#                             start_time=start_time.isoformat() if start_time else None,
#                             end_date=end_date.isoformat() if end_date else None,
#                             end_time=end_time.isoformat() if end_time else None,
#                             root_cause=root_cause or None,
#                             corrective_action=corrective_action or None,
#                             preventive_action=preventive_action or None,
#                             detected_at=detected_at.isoformat() if detected_at else None,
#                             responsible_id=people_map[responsible] if responsible else None,
#                             subtype=subtype  # actualizar subtipo
#                         )
#                         if rowcount:
#                             st.success("✅ Incidente actualizado correctamente")
#                         else:
#                             st.warning("No se detectaron cambios para actualizar")
#                     except Exception as e:
#                         st.error(f"Error al actualizar incidente: {e}")
