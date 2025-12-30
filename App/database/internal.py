import pandas as pd
from datetime import datetime
from .connection import get_conn

def add_internal_activity(
    activity_id,   # 🔥 ahora también se pasa el ID
    category, activity_type, description,
    responsible_id,
    start_date, start_time,
    end_date=None, end_time=None,
    status=None
):
    conn = get_conn()
    conn.execute("""
        INSERT INTO internal_activities
        (id, category, activity_type, description,
         responsible_id, start_date, start_time,
         end_date, end_time,
         status, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        activity_id, category, activity_type, description,
        responsible_id,
        start_date, start_time,
        end_date, end_time,
        status,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    return activity_id


def update_internal_activity(
    activity_id,
    category=None, activity_type=None, description=None,
    responsible_id=None,
    start_date=None, start_time=None,
    end_date=None, end_time=None,
    status=None
):
    conn = get_conn()
    cur = conn.cursor()

    fields = []
    values = []

    if category is not None: fields.append("category=?"); values.append(category)
    if activity_type is not None: fields.append("activity_type=?"); values.append(activity_type)
    if description is not None: fields.append("description=?"); values.append(description)
    if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
    if start_date is not None: fields.append("start_date=?"); values.append(start_date)
    if start_time is not None: fields.append("start_time=?"); values.append(start_time)
    if end_date is not None: fields.append("end_date=?"); values.append(end_date)
    if end_time is not None: fields.append("end_time=?"); values.append(end_time)
    if status is not None: fields.append("status=?"); values.append(status)

    # Siempre actualizar la marca de tiempo
    fields.append("updated_at=?")
    values.append(datetime.utcnow().isoformat())

    if not fields:
        return 0  # nada para actualizar

    values.append(activity_id)
    sql = f"UPDATE internal_activities SET {', '.join(fields)} WHERE id=?"
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount


def get_internal_activities_df():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT ia.*, p.name AS responsible_name
        FROM internal_activities ia
        LEFT JOIN people p ON ia.responsible_id = p.id
        ORDER BY ia.created_at DESC, ia.id DESC
    """, conn)

    # Convertir fechas
    for col in ["start_date", "end_date"]:
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
