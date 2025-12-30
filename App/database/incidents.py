# # import pandas as pd
# # from datetime import datetime
# # from .connection import get_conn

# # def add_incident(
# #     incident_id,   # 🔥 ahora es texto
# #     project, category, severity, description, detected_at,
# #     responsible_id, status,
# #     start_date, start_time,
# #     end_date=None, end_time=None,
# #     root_cause=None, corrective_action=None, preventive_action=None
# # ):
# #     conn = get_conn()
# #     cur = conn.cursor()
# #     cur.execute("""
# #         INSERT INTO incidents
# #         (id, project, category, severity, description, detected_at,
# #          responsible_id, status, start_date, start_time,
# #          end_date, end_time,
# #          root_cause, corrective_action, preventive_action, updated_at)
# #         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
# #     """, (
# #         incident_id, project, category, severity, description,
# #         detected_at, responsible_id, status,
# #         start_date, start_time,
# #         end_date, end_time,
# #         root_cause, corrective_action, preventive_action,
# #         datetime.utcnow().isoformat()
# #     ))
# #     conn.commit()
# #     return incident_id   # 👉 devuelve el ID que vos pusiste


# # def update_incident(
# #     incident_id,
# #     project=None, category=None, severity=None, description=None,
# #     detected_at=None, responsible_id=None, status=None,
# #     start_date=None, start_time=None,
# #     end_date=None, end_time=None,
# #     root_cause=None, corrective_action=None, preventive_action=None
# # ):
# #     conn = get_conn()
# #     cur = conn.cursor()

# #     fields = []
# #     values = []

# #     if project is not None: fields.append("project=?"); values.append(project)
# #     if category is not None: fields.append("category=?"); values.append(category)
# #     if severity is not None: fields.append("severity=?"); values.append(severity)
# #     if description is not None: fields.append("description=?"); values.append(description)
# #     if detected_at is not None: fields.append("detected_at=?"); values.append(detected_at)
# #     if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
# #     if status is not None: fields.append("status=?"); values.append(status)
# #     if start_date is not None: fields.append("start_date=?"); values.append(start_date)
# #     if start_time is not None: fields.append("start_time=?"); values.append(start_time)
# #     if end_date is not None: fields.append("end_date=?"); values.append(end_date)
# #     if end_time is not None: fields.append("end_time=?"); values.append(end_time)
# #     if root_cause is not None: fields.append("root_cause=?"); values.append(root_cause)
# #     if corrective_action is not None: fields.append("corrective_action=?"); values.append(corrective_action)
# #     if preventive_action is not None: fields.append("preventive_action=?"); values.append(preventive_action)

# #     # Siempre actualizar la marca de tiempo
# #     fields.append("updated_at=?")
# #     values.append(datetime.utcnow().isoformat())

# #     if not fields:
# #         return 0  # nada para actualizar

# #     values.append(incident_id)
# #     sql = f"UPDATE incidents SET {', '.join(fields)} WHERE id=?"
# #     cur.execute(sql, values)
# #     conn.commit()
# #     return cur.rowcount

# # def get_incidents_df():
# #     conn = get_conn()
# #     df = pd.read_sql_query("""
# #         SELECT i.*, p.name AS responsible_name
# #         FROM incidents i
# #         LEFT JOIN people p ON i.responsible_id = p.id
# #         ORDER BY i.created_at DESC, i.id DESC
# #     """, conn)

# #     # Convertir fechas
# #     for col in ["detected_at", "start_date", "end_date"]:
# #         if col in df.columns:
# #             df[col] = pd.to_datetime(df[col], errors="coerce")

# #     # Calcular duración en horas si hay inicio y fin
# #     if "start_date" in df.columns and "start_time" in df.columns:
# #         df["start_dt"] = pd.to_datetime(df["start_date"].astype(str) + " " + df["start_time"].astype(str),
# #                                         errors="coerce")
# #     if "end_date" in df.columns and "end_time" in df.columns:
# #         df["end_dt"] = pd.to_datetime(df["end_date"].astype(str) + " " + df["end_time"].astype(str),
# #                                       errors="coerce")

# #     if "start_dt" in df.columns and "end_dt" in df.columns:
# #         df["hours"] = (df["end_dt"] - df["start_dt"]).dt.total_seconds() / 3600
# #     else:
# #         df["hours"] = 0

# #     return df



# import pandas as pd
# from datetime import datetime
# from .connection import get_conn

# def add_incident(
#     incident_id,
#     project, category, severity, description, detected_at,
#     responsible_id, assigned_by, status,
#     start_date, start_time,
#     end_date=None, end_time=None,
#     root_cause=None, corrective_action=None, preventive_action=None
# ):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO incidents
#         (id, project, category, severity, description, detected_at,
#          responsible_id, assigned_by, status, start_date, start_time,
#          end_date, end_time,
#          root_cause, corrective_action, preventive_action, updated_at)
#         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#     """, (
#         incident_id, project, category, severity, description,
#         detected_at, responsible_id, assigned_by, status,
#         start_date, start_time,
#         end_date, end_time,
#         root_cause, corrective_action, preventive_action,
#         datetime.utcnow().isoformat()
#     ))
#     conn.commit()
#     return incident_id

# def update_incident(
#     incident_id,
#     project=None, category=None, severity=None, description=None,
#     detected_at=None, responsible_id=None, assigned_by=None, status=None,
#     start_date=None, start_time=None,
#     end_date=None, end_time=None,
#     root_cause=None, corrective_action=None, preventive_action=None
# ):
#     conn = get_conn()
#     cur = conn.cursor()

#     fields = []
#     values = []

#     if project is not None: fields.append("project=?"); values.append(project)
#     if category is not None: fields.append("category=?"); values.append(category)
#     if severity is not None: fields.append("severity=?"); values.append(severity)
#     if description is not None: fields.append("description=?"); values.append(description)
#     if detected_at is not None: fields.append("detected_at=?"); values.append(detected_at)
#     if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
#     if assigned_by is not None: fields.append("assigned_by=?"); values.append(assigned_by)
#     if status is not None: fields.append("status=?"); values.append(status)
#     if start_date is not None: fields.append("start_date=?"); values.append(start_date)
#     if start_time is not None: fields.append("start_time=?"); values.append(start_time)
#     if end_date is not None: fields.append("end_date=?"); values.append(end_date)
#     if end_time is not None: fields.append("end_time=?"); values.append(end_time)
#     if root_cause is not None: fields.append("root_cause=?"); values.append(root_cause)
#     if corrective_action is not None: fields.append("corrective_action=?"); values.append(corrective_action)
#     if preventive_action is not None: fields.append("preventive_action=?"); values.append(preventive_action)

#     fields.append("updated_at=?")
#     values.append(datetime.utcnow().isoformat())

#     if not fields:
#         return 0

#     values.append(incident_id)
#     sql = f"UPDATE incidents SET {', '.join(fields)} WHERE id=?"
#     cur.execute(sql, values)
#     conn.commit()
#     return cur.rowcount

# def get_incidents_df():
#     conn = get_conn()
#     df = pd.read_sql_query("""
#         SELECT i.*, 
#                p.name AS responsible_name,
#                a.name AS assigned_by_name
#         FROM incidents i
#         LEFT JOIN people p ON i.responsible_id = p.id
#         LEFT JOIN people a ON i.assigned_by = a.id
#         ORDER BY i.created_at DESC, i.id DESC
#     """, conn)

#     for col in ["detected_at", "start_date", "end_date"]:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors="coerce")

#     if "start_date" in df.columns and "start_time" in df.columns:
#         df["start_dt"] = pd.to_datetime(df["start_date"].astype(str) + " " + df["start_time"].astype(str), errors="coerce")
#     if "end_date" in df.columns and "end_time" in df.columns:
#         df["end_dt"] = pd.to_datetime(df["end_date"].astype(str) + " " + df["end_time"].astype(str), errors="coerce")

#     if "start_dt" in df.columns and "end_dt" in df.columns:
#         df["hours"] = (df["end_dt"] - df["start_dt"]).dt.total_seconds() / 3600
#     else:
#         df["hours"] = 0

#     return df


import pandas as pd
from datetime import datetime
from .connection import get_conn

def add_incident(
    incident_id,
    project, category, severity, description, detected_at,
    responsible_id, status,
    start_date, start_time,
    end_date=None, end_time=None,
    root_cause=None, corrective_action=None, preventive_action=None
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incidents
        (id, project, category, severity, description, detected_at,
         responsible_id, status, start_date, start_time,
         end_date, end_time,
         root_cause, corrective_action, preventive_action, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        incident_id, project, category, severity, description,
        detected_at, responsible_id, status,
        start_date, start_time,
        end_date, end_time,
        root_cause, corrective_action, preventive_action,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    return incident_id

def update_incident(
    incident_id,
    project=None, category=None, severity=None, description=None,
    detected_at=None, responsible_id=None, status=None,
    start_date=None, start_time=None,
    end_date=None, end_time=None,
    root_cause=None, corrective_action=None, preventive_action=None
):
    conn = get_conn()
    cur = conn.cursor()

    fields = []
    values = []

    if project is not None: fields.append("project=?"); values.append(project)
    if category is not None: fields.append("category=?"); values.append(category)
    if severity is not None: fields.append("severity=?"); values.append(severity)
    if description is not None: fields.append("description=?"); values.append(description)
    if detected_at is not None: fields.append("detected_at=?"); values.append(detected_at)
    if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
    if status is not None: fields.append("status=?"); values.append(status)
    if start_date is not None: fields.append("start_date=?"); values.append(start_date)
    if start_time is not None: fields.append("start_time=?"); values.append(start_time)
    if end_date is not None: fields.append("end_date=?"); values.append(end_date)
    if end_time is not None: fields.append("end_time=?"); values.append(end_time)
    if root_cause is not None: fields.append("root_cause=?"); values.append(root_cause)
    if corrective_action is not None: fields.append("corrective_action=?"); values.append(corrective_action)
    if preventive_action is not None: fields.append("preventive_action=?"); values.append(preventive_action)

    fields.append("updated_at=?")
    values.append(datetime.utcnow().isoformat())

    if not fields:
        return 0

    values.append(incident_id)
    sql = f"UPDATE incidents SET {', '.join(fields)} WHERE id=?"
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def get_incidents_df():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT i.*, 
               p.name AS responsible_name
        FROM incidents i
        LEFT JOIN people p ON i.responsible_id = p.id
        ORDER BY i.created_at DESC, i.id DESC
    """, conn)

    # Convertir fechas
    for col in ["detected_at", "start_date", "end_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Calcular duración en horas si hay inicio y fin
    if "start_date" in df.columns and "start_time" in df.columns:
        df["start_dt"] = pd.to_datetime(df["start_date"].astype(str) + " " + df["start_time"].astype(str),
                                        errors="coerce")
    if "end_date" in df.columns and "end_time" in df.columns:
        df["end_dt"] = pd.to_datetime(df["end_date"].astype(str) + " " + df["end_time"].astype(str),
                                      errors="coerce")

    if "start_dt" in df.columns and "end_dt" in df.columns:
        df["hours"] = (df["end_dt"] - df["start_dt"]).dt.total_seconds() / 3600
    else:
        df["hours"] = 0

    return df
