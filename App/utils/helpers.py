from datetime import date, time

def iso_or_none_date(d: date | None) -> str | None:
    return d.isoformat() if d else None

def iso_or_none_time(t: time | None) -> str | None:
    return t.isoformat() if t else None
