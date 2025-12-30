import streamlit as st
import pandas as pd
from database.tasks import get_tasks_df
from database.incidents import get_incidents_df
from database.requirements import get_requirements_df
from database.internal import get_internal_activities_df

def show_dashboard():
    st.header("📊 Dashboard de Gestión – Medición Inteligente")

    tasks_df = get_tasks_df()
    incidents_df = get_incidents_df()
    requirements_df = get_requirements_df()
    internal_df = get_internal_activities_df()

    # st.subheader("Indicadores generales")
    # k1, k2, k3 = st.columns(3)
    # k1.metric("Tareas", len(tasks_df))
    # k2.metric("Incidentes", len(incidents_df))
    # k3.metric("Requerimientos", len(requirements_df))

    st.subheader("Indicadores generales")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Tareas", len(tasks_df))
    k2.metric("Incidentes", len(incidents_df))
    k3.metric("Requerimientos", len(requirements_df))
    k4.metric("Internas", len(internal_df))

    st.subheader("Consumo total de horas")
    time_data = {
        # "Tareas": tasks_df["time_spent"].sum() if not tasks_df.empty else 0,
        "Tareas": tasks_df["hours"].sum() if not tasks_df.empty else 0,
        # "Incidentes": incidents_df["time_spent"].sum() if not incidents_df.empty else 0,
        "Incidentes": incidents_df["hours"].sum() if not incidents_df.empty else 0,
        # "Requerimientos": requirements_df["time_spent"].sum() if not requirements_df.empty else 0,
        "Requerimientos": requirements_df["hours"].sum() if not requirements_df.empty else 0,
        # "Internas": internal_df["hours"].sum() if not internal_df.empty else 0,
        "Internas": internal_df["hours"].sum() if not internal_df.empty else 0,
    }
    st.bar_chart(pd.Series(time_data))

    # st.subheader("Distribución por estado")
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     if not tasks_df.empty:
    #         st.markdown("**Tareas**")
    #         st.bar_chart(tasks_df["status"].value_counts())
    #     else:
    #         st.info("Sin tareas")
    # with col2:
    #     if not incidents_df.empty:
    #         st.markdown("**Incidentes**")
    #         st.bar_chart(incidents_df["status"].value_counts())
    #     else:
    #         st.info("Sin incidentes")
    # with col3:
    #     if not requirements_df.empty:
    #         st.markdown("**Requerimientos**")
    #         st.bar_chart(requirements_df["status"].value_counts())
    #     else:
    #         st.info("Sin requerimientos")

    st.subheader("Distribución por estado")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if not tasks_df.empty:
            st.markdown("**Tareas**")
            st.bar_chart(tasks_df["status"].value_counts())
        else:
            st.info("Sin tareas")

    with col2:
        if not incidents_df.empty:
            st.markdown("**Incidentes**")
            st.bar_chart(incidents_df["status"].value_counts())
        else:
            st.info("Sin incidentes")

    with col3:
        if not requirements_df.empty:
            st.markdown("**Requerimientos**")
            st.bar_chart(requirements_df["status"].value_counts())
        else:
            st.info("Sin requerimientos")

    with col4:
        if not internal_df.empty:
            st.markdown("**Internas**")
            st.bar_chart(internal_df["status"].value_counts())
        else:
            st.info("Sin internas")


    st.subheader("Carga de trabajo por responsable")
    combined_time = pd.concat([
        # tasks_df[["responsible_name", "time_spent"]].assign(tipo="Tarea") if not tasks_df.empty else pd.DataFrame(),
        tasks_df[["responsible_name", "hours"]].assign(tipo="Tarea") if not tasks_df.empty else pd.DataFrame(),
        # incidents_df[["responsible_name", "time_spent"]].assign(tipo="Incidente") if not incidents_df.empty else pd.DataFrame(),
        incidents_df[["responsible_name", "hours"]].assign(tipo="Incidente") if not incidents_df.empty else pd.DataFrame(),
        # requirements_df[["responsible_name", "time_spent"]].assign(tipo="Requerimiento") if not requirements_df.empty else pd.DataFrame(),
        requirements_df[["responsible_name", "hours"]].assign(tipo="Requerimiento") if not requirements_df.empty else pd.DataFrame(),
        internal_df[["responsible_name", "hours"]].assign(tipo="Interna") if not internal_df.empty else pd.DataFrame(),
    ])

    # if not combined_time.empty:
    #     st.bar_chart(combined_time.groupby("responsible_name")["time_spent"].sum())
    # else:
    #     st.info("No hay datos de responsables")

    if not combined_time.empty:
        st.bar_chart(combined_time.groupby("responsible_name")["hours"].sum())
    else:
        st.info("No hay datos de responsables")

    st.subheader("Evolución temporal de registros")
    evo_data = []
    if not tasks_df.empty:
        evo_data.append(
            tasks_df.assign(date_=tasks_df["start_date"].dt.date)
            .groupby("date_")["id"].count()
            .rename("Tareas")
        )
    if not incidents_df.empty:
        evo_data.append(
            incidents_df.assign(date_=incidents_df["detected_at"].dt.date)
            .groupby("date_")["id"].count()
            .rename("Incidentes")
        )
    if not requirements_df.empty:
        evo_data.append(
            requirements_df.assign(date_=requirements_df["received_at"].dt.date)
            .groupby("date_")["id"].count()
            .rename("Requerimientos")
        )
    if evo_data:
        evo_df = pd.concat(evo_data, axis=1).fillna(0)
        st.area_chart(evo_df)
    else:
        st.info("No hay datos temporales suficientes")

    # st.subheader("Consumo de tiempo")
    # col3, col4 = st.columns(2)
    # with col3:
    #     if not tasks_df.empty:
    #         st.markdown("**Horas por estado de tarea**")
    #         # st.bar_chart(tasks_df.groupby("status")["time_spent"].sum())
    #         st.bar_chart(tasks_df.groupby("status")["hours"].sum())

    # with col4:
    #     if not incidents_df.empty:
    #         st.markdown("**Horas por estado de incidente**")
    #         # st.bar_chart(incidents_df.groupby("status")["time_spent"].sum())
    #         st.bar_chart(incidents_df.groupby("status")["hours"].sum())
    
    st.subheader("Consumo de tiempo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not tasks_df.empty:
            st.markdown("**Horas por estado de tarea**")
            st.bar_chart(tasks_df.groupby("status")["hours"].sum())
        else:
            st.info("Sin tareas")
    
    with col2:
        if not incidents_df.empty:
            st.markdown("**Horas por estado de incidente**")
            st.bar_chart(incidents_df.groupby("status")["hours"].sum())
        else:
            st.info("Sin incidentes")
    
    with col3:
        if not requirements_df.empty:
            st.markdown("**Horas por estado de requerimiento**")
            st.bar_chart(requirements_df.groupby("status")["hours"].sum())
        else:
            st.info("Sin requerimientos")
    
    with col4:
        if not internal_df.empty:
            st.markdown("**Horas por estado de interna**")
            st.bar_chart(internal_df.groupby("status")["hours"].sum())
        else:
            st.info("Sin internas")
    