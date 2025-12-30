import pandas as pd
from datetime import datetime
from .connection import get_conn

def add_task(
    task_id, project, origin, category, task_type, description,
    responsible_id, status,
    start_date, start_time,
    end_date=None, end_time=None
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks
        (id, project, origin, category, task_type, description,
         responsible_id, status, start_date, start_time,
         end_date, end_time, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        task_id, project, origin, category, task_type, description,
        responsible_id, status,
        start_date, start_time,
        end_date, end_time,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    return task_id

def update_task(
    task_id, project=None, origin=None, category=None, task_type=None,
    description=None, responsible_id=None, status=None,
    start_date=None, start_time=None,
    end_date=None, end_time=None
):
    conn = get_conn()
    cur = conn.cursor()
    fields, values = [], []

    if project is not None: fields.append("project=?"); values.append(project)
    if origin is not None: fields.append("origin=?"); values.append(origin)
    if category is not None: fields.append("category=?"); values.append(category)
    if task_type is not None: fields.append("task_type=?"); values.append(task_type)
    if description is not None: fields.append("description=?"); values.append(description)
    if responsible_id is not None: fields.append("responsible_id=?"); values.append(responsible_id)
    if status is not None: fields.append("status=?"); values.append(status)
    if start_date is not None: fields.append("start_date=?"); values.append(start_date)
    if start_time is not None: fields.append("start_time=?"); values.append(start_time)
    if end_date is not None: fields.append("end_date=?"); values.append(end_date)
    if end_time is not None: fields.append("end_time=?"); values.append(end_time)

    fields.append("updated_at=?")
    values.append(datetime.utcnow().isoformat())
    values.append(task_id)

    sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id=?"
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def get_tasks_df():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT t.*, p.name AS responsible_name
        FROM tasks t
        LEFT JOIN people p ON t.responsible_id = p.id
        ORDER BY t.created_at DESC, t.id DESC
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
