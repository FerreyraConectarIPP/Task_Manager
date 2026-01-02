# # from reportlab.lib.pagesizes import A4
# # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
# # from reportlab.lib.styles import getSampleStyleSheet
# # from io import BytesIO

# # from database.tasks import get_tasks_df
# # from database.incidents import get_incidents_df
# # from database.requirements import get_requirements_df
# # from database.internal import get_internal_activities_df

# # def generate_mini_report_pdf():
# #     buffer = BytesIO()
# #     doc = SimpleDocTemplate(buffer, pagesize=A4)
# #     styles = getSampleStyleSheet()
# #     elements = []

# #     elements.append(Paragraph("Mini Reporte – Gestión Medición Inteligente", styles["Title"]))
# #     elements.append(Spacer(1, 12))

# #     tasks_df = get_tasks_df()
# #     incidents_df = get_incidents_df()
# #     requirements_df = get_requirements_df()
# #     internal_df = get_internal_activities_df()

# #     elements.append(Paragraph("Indicadores generales", styles["Heading2"]))
# #     kpi_data = [
# #         ["Tareas", len(tasks_df)],
# #         ["Incidentes", len(incidents_df)],
# #         ["Requerimientos", len(requirements_df)],
# #         ["Actividades internas", len(internal_df)],
# #     ]
# #     elements.append(Table(kpi_data))
# #     elements.append(Spacer(1, 12))

# #     elements.append(Paragraph("Horas totales consumidas", styles["Heading2"]))
# #     hours_data = [
# #         ["Tareas", tasks_df["time_spent"].sum() if not tasks_df.empty else 0],
# #         ["Incidentes", incidents_df["time_spent"].sum() if not incidents_df.empty else 0],
# #         ["Requerimientos", requirements_df["time_spent"].sum() if not requirements_df.empty else 0],
# #         ["Actividades internas", internal_df["time_spent"].sum() if not internal_df.empty else 0],
# #     ]
# #     elements.append(Table(hours_data))
# #     elements.append(Spacer(1, 12))

# #     open_incidents = incidents_df[incidents_df["status"] != "Cerrado"] if not incidents_df.empty else incidents_df
# #     elements.append(Paragraph("Incidentes abiertos", styles["Heading2"]))
# #     elements.append(Paragraph(f"Cantidad: {len(open_incidents)}", styles["Normal"]))

# #     doc.build(elements)
# #     buffer.seek(0)
# #     return buffer

# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
# from reportlab.lib.styles import getSampleStyleSheet
# from io import BytesIO

# from database.tasks import get_tasks_df
# from database.incidents import get_incidents_df
# from database.requirements import get_requirements_df
# from database.internal import get_internal_activities_df

# def generate_mini_report_pdf():
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=A4)
#     styles = getSampleStyleSheet()
#     elements = []

#     elements.append(Paragraph("Mini Reporte – Gestión Medición Inteligente", styles["Title"]))
#     elements.append(Spacer(1, 12))

#     tasks_df = get_tasks_df()
#     incidents_df = get_incidents_df()
#     requirements_df = get_requirements_df()
#     internal_df = get_internal_activities_df()

#     # Indicadores generales
#     elements.append(Paragraph("Indicadores generales", styles["Heading2"]))
#     kpi_data = [
#         ["Tareas", len(tasks_df)],
#         ["Incidentes", len(incidents_df)],
#         ["Requerimientos", len(requirements_df)],
#         ["Actividades internas", len(internal_df)],
#     ]
#     elements.append(Table(kpi_data))
#     elements.append(Spacer(1, 12))

#     # Incidentes abiertos
#     open_incidents = incidents_df[incidents_df["status"] != "Cerrado"] if not incidents_df.empty else incidents_df
#     elements.append(Paragraph("Incidentes abiertos", styles["Heading2"]))
#     elements.append(Paragraph(f"Cantidad: {len(open_incidents)}", styles["Normal"]))

#     doc.build(elements)
#     buffer.seek(0)
#     return buffer



from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import pandas as pd

from database.tasks import get_tasks_df
from database.incidents import get_incidents_df
from database.requirements import get_requirements_df
from database.internal import get_internal_activities_df

def generate_mini_report_pdf(generated_by: dict | None = None, version: str | None = None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Cabecera
    elements.append(Paragraph("Mini Reporte – Gestión Medición Inteligente", styles["Title"]))
    elements.append(Spacer(1, 6))
    meta_lines = []
    from datetime import datetime
    meta_lines.append(f"Fecha: {datetime.utcnow().isoformat()}")
    if generated_by:
        meta_lines.append(f"Generado por: {generated_by.get('username', '-') } ({generated_by.get('role', '-')})")
    if version:
        meta_lines.append(f"Versión: {version}")
    elements.append(Paragraph(" — ".join(meta_lines), styles["Normal"]))
    elements.append(Spacer(1, 12))

    tasks_df = get_tasks_df()
    incidents_df = get_incidents_df()
    requirements_df = get_requirements_df()
    internal_df = get_internal_activities_df()

    # --- Indicadores generales ---
    elements.append(Paragraph("Indicadores generales", styles["Heading2"]))
    kpi_data = [
        ["Tareas", len(tasks_df)],
        ["Incidentes", len(incidents_df)],
        ["Requerimientos", len(requirements_df)],
        ["Actividades internas", len(internal_df)],
    ]
    elements.append(Table(kpi_data))
    elements.append(Spacer(1, 12))

    # --- Incidentes abiertos ---
    open_incidents = incidents_df[incidents_df["status"] != "Cerrado"] if not incidents_df.empty else incidents_df
    elements.append(Paragraph("Incidentes abiertos", styles["Heading2"]))
    elements.append(Paragraph(f"Cantidad: {len(open_incidents)}", styles["Normal"]))

    if not open_incidents.empty:
        # Mostrar una tabla con más columnas: incluir Subtipo y estado
        table_data = [["ID", "Proyecto", "Categoría", "Subtipo", "Severidad", "Responsable", "Fecha detección", "Estado"]]
        for _, row in open_incidents.sort_values(by="detected_at", ascending=False).head(10).iterrows():  # mostrar hasta 10
            table_data.append([
                row.get("id", ""),
                row.get("project", ""),
                row.get("category", ""),
                row.get("subtype", "") if "subtype" in row else "",
                row.get("severity", ""),
                row.get("responsible_name", ""),
                str(row.get("detected_at", ""))[:10],
                row.get("status", "")
            ])
        elements.append(Table(table_data))
        elements.append(Spacer(1, 12))

    # --- Distribuciones ---
    if not incidents_df.empty:
        if "severity" in incidents_df.columns:
            severity_counts = incidents_df["severity"].value_counts().reset_index()
            severity_counts.columns = ["Severidad", "Cantidad"]
            elements.append(Paragraph("Distribución de incidentes por severidad", styles["Heading2"]))
            elements.append(Table(severity_counts.values.tolist()))
            elements.append(Spacer(1, 12))

        if "category" in incidents_df.columns and "subtype" in incidents_df.columns:
            cat_sub = incidents_df.groupby(["category", "subtype"]).size().reset_index(name="Cantidad")
            cat_sub_table = [["Categoría", "Subtipo", "Cantidad"]]
            for _, r in cat_sub.iterrows():
                cat_sub_table.append([r["category"], r["subtype"], r["Cantidad"]])
            elements.append(Paragraph("Incidentes por Categoría y Subtipo", styles["Heading2"]))
            elements.append(Table(cat_sub_table))
            elements.append(Spacer(1, 12))

    # --- Tareas por estado ---
    if not tasks_df.empty and "status" in tasks_df.columns:
        task_counts = tasks_df["status"].value_counts().reset_index()
        task_counts.columns = ["Estado", "Cantidad"]
        elements.append(Paragraph("Distribución de tareas por estado", styles["Heading2"]))
        elements.append(Table(task_counts.values.tolist()))
        elements.append(Spacer(1, 12))

    # --- Top responsables con más incidentes ---
    if not incidents_df.empty and "responsible_name" in incidents_df.columns:
        top_resp = incidents_df["responsible_name"].value_counts().reset_index().head(10)
        top_resp.columns = ["Responsable", "Incidentes"]
        elements.append(Paragraph("Top responsables con más incidentes", styles["Heading2"]))
        elements.append(Table(top_resp.values.tolist()))
        elements.append(Spacer(1, 12))

    # --- Últimos requerimientos ---
    if not requirements_df.empty:
        elements.append(Paragraph("Últimos requerimientos registrados", styles["Heading2"]))
        req_table = [["ID", "Proyecto", "Descripción", "Fecha"]]
        for _, row in requirements_df.tail(5).iterrows():
            req_table.append([
                row.get("id", ""),
                row.get("project", ""),
                row.get("description", "")[:50],  # recortar descripción
                str(row.get("created_at", ""))[:10]
            ])
        elements.append(Table(req_table))
        elements.append(Spacer(1, 12))

    # Pie con versión y generador
    footer = []
    if generated_by:
        footer.append(f"Generado por: {generated_by.get('username')} ({generated_by.get('role')})")
    if version:
        footer.append(f"Versión: {version}")
    if footer:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(" | ".join(footer), styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
