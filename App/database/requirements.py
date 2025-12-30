# import pandas as pd
# from datetime import datetime
# from .connection import get_conn

# def add_requirement(
#     req_id, project, origin, category, req_type, description,
#     responsible_id, status,
#     start_date, start_time,
#     end_date=None, end_time=None,
#     received_at=None
# ):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO requirements
#         (id, project, origin, category, req_type, description,
#          responsible_id, status, start_date, start_time,
#          end_date, end_time, received_at, updated_at)
#         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#     """, (
#         req_id, project, origin, category, req_type, description,
#         responsible_id, status,
#         start_date, start_time,
#         end_date, end_time,
#         received_at,
#         datetime.utcnow().isoformat()
#     ))
#     conn.commit()
#     return req_id

# def update_requirement(
#     req_id, project=None, origin=None, category=None, req_type=None,
#     description=None, responsible_id=None, status=None,
#     start_date=None, start_time=None,
#     end_date=None, end_time=None,
#     received_at=None
# ):
#     conn = get_conn()
#     cur = conn.cursor()
#     fields, values = [], []

#     if project is not None: fields.append("project=?"); values.append(project)
#     if origin is not None: fields.append("origin=?"); values.append(origin)
#     if category is not None: fields.append("category=?"); values.append(category)
#     if req_type is not None: fields.append("req_type=?"); values.append(req_type)
#     if description is not None: fields.append("description=?"); values.append(description)
#     if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
#     if status is not None: fields.append("status=?"); values.append(status)
#     if start_date is not None: fields.append("start_date=?"); values.append(start_date)
#     if start_time is not None: fields.append("start_time=?"); values.append(start_time)
#     if end_date is not None: fields.append("end_date=?"); values.append(end_date)
#     if end_time is not None: fields.append("end_time=?"); values.append(end_time)
#     if received_at is not None: fields.append("received_at=?"); values.append(received_at)

#     fields.append("updated_at=?")
#     values.append(datetime.utcnow().isoformat())
#     values.append(req_id)

#     sql = f"UPDATE requirements SET {', '.join(fields)} WHERE id=?"
#     cur.execute(sql, values)
#     conn.commit()
#     return cur.rowcount

# def get_requirements_df():
#     conn = get_conn()
#     df = pd.read_sql_query("""
#         SELECT r.*, p.name AS responsible_name
#         FROM requirements r
#         LEFT JOIN people p ON r.responsible_id = p.id
#         ORDER BY r.created_at DESC, r.id DESC
#     """, conn)

#     # Convertir fechas
#     for col in ["received_at", "start_date", "end_date"]:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors="coerce")

#     # Calcular datetime completo de inicio y fin
#     if "start_date" in df.columns and "start_time" in df.columns:
#         df["start_dt"] = pd.to_datetime(df["start_date"].astype(str) + " " + df["start_time"].astype(str),
#                                         errors="coerce")
#     if "end_date" in df.columns and "end_time" in df.columns:
#         df["end_dt"] = pd.to_datetime(df["end_date"].astype(str) + " " + df["end_time"].astype(str),
#                                       errors="coerce")

#     # Calcular duración en horas
#     if "start_dt" in df.columns and "end_dt" in df.columns:
#         df["hours"] = (df["end_dt"] - df["start_dt"]).dt.total_seconds() / 3600
#     else:
#         df["hours"] = 0

#     return df

import pandas as pd
from datetime import datetime
from .connection import get_conn

def add_requirement(
    req_id, project, origin, requester, category, req_type, description,
    responsible_id, status,
    start_date, start_time,
    end_date=None, end_time=None,
    received_at=None
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requirements
        (id, project, origin, requester, category, req_type, description,
         responsible_id, status, start_date, start_time,
         end_date, end_time, received_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        req_id, project, origin, requester, category, req_type, description,
        responsible_id, status,
        start_date, start_time,
        end_date, end_time,
        received_at,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    return req_id

def update_requirement(
    req_id, project=None, origin=None, requester=None, category=None, req_type=None,
    description=None, responsible_id=None, status=None,
    start_date=None, start_time=None,
    end_date=None, end_time=None,
    received_at=None
):
    conn = get_conn()
    cur = conn.cursor()
    fields, values = [], []

    if project is not None: fields.append("project=?"); values.append(project)
    if origin is not None: fields.append("origin=?"); values.append(origin)
    if requester is not None: fields.append("requester=?"); values.append(requester)
    if category is not None: fields.append("category=?"); values.append(category)
    if req_type is not None: fields.append("req_type=?"); values.append(req_type)
    if description is not None: fields.append("description=?"); values.append(description)
    if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
    if status is not None: fields.append("status=?"); values.append(status)
    if start_date is not None: fields.append("start_date=?"); values.append(start_date)
    if start_time is not None: fields.append("start_time=?"); values.append(start_time)
    if end_date is not None: fields.append("end_date=?"); values.append(end_date)
    if end_time is not None: fields.append("end_time=?"); values.append(end_time)
    if received_at is not None: fields.append("received_at=?"); values.append(received_at)

    fields.append("updated_at=?")
    values.append(datetime.utcnow().isoformat())
    values.append(req_id)

    sql = f"UPDATE requirements SET {', '.join(fields)} WHERE id=?"
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def get_requirements_df():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT r.*, p.name AS responsible_name
        FROM requirements r
        LEFT JOIN people p ON r.responsible_id = p.id
        ORDER BY r.created_at DESC, r.id DESC
    """, conn)

    # Convertir fechas
    for col in ["received_at", "start_date", "end_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Calcular datetime completo de inicio y fin
    if "start_date" in df.columns and "start_time" in df.columns:
        df["start_dt"] = pd.to_datetime(df["start_date"].astype(str) + " " + df["start_time"].astype(str),
                                        errors="coerce")
    if "end_date" in df.columns and "end_time" in df.columns:
        df["end_dt"] = pd.to_datetime(df["end_date"].astype(str) + " " + df["end_time"].astype(str),
                                      errors="coerce")

    # Calcular duración en horas
    if "start_dt" in df.columns and "end_dt" in df.columns:
        df["hours"] = (df["end_dt"] - df["start_dt"]).dt.total_seconds() / 3600
    else:
        df["hours"] = 0

    return df
