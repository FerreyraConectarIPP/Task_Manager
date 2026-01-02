from datetime import date, time
import os
import subprocess

# Puedes fijar la versión directamente desde el código editando esta constante.
# Ejemplo: cambia APP_VERSION = "v0.0.1" y reinicia la app.
APP_VERSION: str | None = None


def iso_or_none_date(d: date | None) -> str | None:
    return d.isoformat() if d else None

def iso_or_none_time(t: time | None) -> str | None:
    return t.isoformat() if t else None


def get_version() -> str:
    """Obtener la versión de la aplicación.

    Prioridad de fuentes (de mayor a menor):
    1. Variable de entorno APP_VERSION
    2. Constante en código `APP_VERSION` en `utils.helpers` (editable)
    3. Archivo `VERSION` en la carpeta raíz del proyecto (dentro de la carpeta App)
    4. Commit corto de git (branch@sha)
    5. 'unknown' si no se puede determinar
    """
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 1) Variable de entorno
    env_ver = os.environ.get("APP_VERSION")
    if env_ver:
        return env_ver

    # 2) Constante en código
    if APP_VERSION:
        return APP_VERSION

    # 3) VERSION file
    ver_file = os.path.join(base, "VERSION")
    if os.path.exists(ver_file):
        try:
            with open(ver_file, "r", encoding="utf-8") as fh:
                return fh.read().strip()
        except Exception:
            pass

    # 4) Git commit
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=base, stderr=subprocess.DEVNULL, text=True).strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=base, stderr=subprocess.DEVNULL, text=True).strip()
        return f"{branch}@{sha}"
    except Exception:
        return "unknown"
