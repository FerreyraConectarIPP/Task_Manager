import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.environ.get("SMTP_SERVER")
# Parse SMTP_PORT env var safely (allow non-set or invalid values)
_SMTP_PORT_ENV = os.environ.get("SMTP_PORT")
try:
    SMTP_PORT = int(_SMTP_PORT_ENV) if _SMTP_PORT_ENV else None
except (TypeError, ValueError):
    # If it's not a valid integer, ignore and fallback to DB/default later
    SMTP_PORT = None
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_FROM = os.environ.get("SMTP_FROM") or SMTP_USER

from database.settings import get_setting
from database.emails import log_email

def _send_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    """Función genérica para enviar un correo a un destinatario."""
    ok, msg = is_smtp_configured()
    if not ok:
        return False, msg
    try:
        cfg = _resolve_smtp_config()
        msg_obj = EmailMessage()
        msg_obj["Subject"] = subject
        msg_obj["From"] = cfg.get("from")
        msg_obj["To"] = to_email
        msg_obj.set_content(body)

        with smtplib.SMTP(cfg["server"], cfg["port"], timeout=10) as s:
            s.starttls()
            if cfg["user"] and cfg["password"]:
                s.login(cfg["user"], cfg["password"])
            s.send_message(msg_obj)

        log_email(to_email, subject, body, status="sent")
        return True, f"Email enviado correctamente a {to_email}"
    except Exception as e:
        log_email(to_email, subject, body, status="failed", error=str(e))
        return False, str(e)


def _resolve_smtp_config():
    # Prioridad: variables de entorno, luego configuración guardada en DB (settings table)
    server = SMTP_SERVER or get_setting("SMTP_SERVER") or None

    # Determine port: prefer env var (already parsed), otherwise DB setting (validated)
    port = None
    if SMTP_PORT is not None:
        port = SMTP_PORT
    else:
        port_setting = get_setting("SMTP_PORT")
        if port_setting:
            try:
                port = int(port_setting)
            except (TypeError, ValueError):
                port = None

    # Validate port range and apply default if invalid/missing
    if not isinstance(port, int) or not (1 <= port <= 65535):
        port = 587

    user = SMTP_USER or get_setting("SMTP_USER")
    password = SMTP_PASSWORD or get_setting("SMTP_PASSWORD")
    from_addr = SMTP_FROM or get_setting("SMTP_FROM") or user

    return {
        "server": server,
        "port": port,
        "user": user,
        "password": password,
        "from": from_addr,
    }


def is_smtp_configured() -> tuple[bool, str]:
    cfg = _resolve_smtp_config()
    if not cfg.get("server"):
        return False, "SMTP no configurado (SMTP_SERVER no definido)."
    return True, "OK"


# def send_password_email(to_email: str, username: str, password: str) -> tuple[bool, str]:
#     """Enviar un email con la contraseña. Devuelve (ok, message).

#     Esta función sigue disponible, pero su uso está desaconsejado en favor del flujo de restablecimiento por token.
#     """
#     ok, msg = is_smtp_configured()
#     if not ok:
#         return False, msg

#     try:
#         cfg = _resolve_smtp_config()
#         msg = EmailMessage()
#         msg["Subject"] = f"Recuperación de contraseña - {username}"
#         msg["From"] = cfg.get("from")
#         msg["To"] = to_email
#         body = f"Hola {username},\n\nTu contraseña actual es: {password}\n\nPor seguridad, considera cambiarla al ingresar al sistema.\n\nSaludos."
#         msg.set_content(body)

#         port = cfg.get("port")
#         with smtplib.SMTP(cfg.get("server"), port, timeout=10) as s:
#             s.starttls()
#             if cfg.get("user") and cfg.get("password"):
#                 s.login(cfg.get("user"), cfg.get("password"))
#             s.send_message(msg)
#         # registrar éxito en la tabla de logs
#         try:
#             log_email(to_email, msg["Subject"], body, status="sent")
#         except Exception:
#             pass
#         return True, "Email enviado correctamente"
#     except Exception as e:
#         # registrar error en la tabla de logs
#         try:
#             log_email(to_email, f"Recuperación de contraseña - {username}", body, status="failed", error=str(e))
#         except Exception:
#             pass
#         return False, str(e)


def send_password_email(to_emails: str | list[str], username: str, password: str) -> dict:
    """Enviar un email con la contraseña.
    
    - Si recibe un string, envía a un solo destinatario.
    - Si recibe una lista, envía uno por uno.
    Devuelve un diccionario con resultados por destinatario.
    """
    ok, msg = is_smtp_configured()
    if not ok:
        return {"error": msg}

    # Normalizar: convertir string en lista
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    results = {}
    subject = f"Recuperación de contraseña - {username}"
    body = (
        f"Hola {username},\n\n"
        f"Tu contraseña actual es: {password}\n\n"
        "Por seguridad, considera cambiarla al ingresar al sistema.\n\nSaludos."
    )

    for to_email in to_emails:
        try:
            cfg = _resolve_smtp_config()
            msg_obj = EmailMessage()
            msg_obj["Subject"] = subject
            msg_obj["From"] = cfg.get("from")
            msg_obj["To"] = to_email
            msg_obj.set_content(body)

            port = cfg.get("port")
            with smtplib.SMTP(cfg.get("server"), port, timeout=10) as s:
                s.starttls()
                if cfg.get("user") and cfg.get("password"):
                    s.login(cfg.get("user"), cfg.get("password"))
                s.send_message(msg_obj)

            try:
                log_email(to_email, subject, body, status="sent")
            except Exception:
                pass
            results[to_email] = (True, "Email enviado correctamente")
        except Exception as e:
            try:
                log_email(to_email, subject, body, status="failed", error=str(e))
            except Exception:
                pass
            results[to_email] = (False, str(e))

    return results


# def send_reset_email(to_email: str, username: str, reset_link: str) -> tuple[bool, str]:
#     """Enviar email con enlace para restablecer contraseña"""
#     ok, msg = is_smtp_configured()
#     if not ok:
#         return False, msg

#     try:
#         cfg = _resolve_smtp_config()
#         msg = EmailMessage()
#         msg["Subject"] = f"Restablecer contraseña - {username}"
#         msg["From"] = cfg.get("from")
#         msg["To"] = to_email
#         body = f"Hola {username},\n\nHas solicitado restablecer tu contraseña. Accede al siguiente enlace para elegir una nueva contraseña:\n\n{reset_link}\n\nEste enlace expira en 1 hora. Si no solicitaste este cambio, ignora este mensaje.\n\nSaludos."
#         msg.set_content(body)

#         port = cfg.get("port")
#         with smtplib.SMTP(cfg.get("server"), port, timeout=10) as s:
#             s.starttls()
#             if cfg.get("user") and cfg.get("password"):
#                 s.login(cfg.get("user"), cfg.get("password"))
#             s.send_message(msg)
#         # registrar éxito en la tabla de logs
#         try:
#             log_email(to_email, msg["Subject"], body, status="sent")
#         except Exception:
#             pass
#         return True, "Email enviado correctamente"
#     except Exception as e:
#         # registrar error en la tabla de logs
#         try:
#             log_email(to_email, f"Restablecer contraseña - {username}", body, status="failed", error=str(e))
#         except Exception:
#             pass
#         return False, str(e)

# def send_reset_email(to_emails: list[str], username: str, reset_link: str) -> dict:
#     """Enviar email con enlace para restablecer contraseña a varios destinatarios."""
#     subject = f"Restablecer contraseña - {username}"
#     body = f"""Hola {username},

# Has solicitado restablecer tu contraseña. Accede al siguiente enlace para elegir una nueva contraseña:

# {reset_link}

# Este enlace expira en 1 hora. Si no solicitaste este cambio, ignora este mensaje.

# Saludos.
# """
#     results = {}
#     for email in to_emails:
#         ok, msg = _send_email(email, subject, body)
#         results[email] = (ok, msg)
#     return results

def send_reset_email(to_emails: str | list[str], username: str, reset_link: str):
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    subject = f"Restablecer contraseña - {username}"
    body = f"""Hola {username},
    Has solicitado restablecer tu contraseña. Accede al siguiente enlace para elegir una nueva contraseña: 
    {reset_link}
    Este enlace expira en 1 hora. Si no solicitaste este cambio, ignora este mensaje.
    Saludos.
    """
    results = {}
    for email in to_emails:
        ok, msg = _send_email(email, subject, body)
        results[email] = (ok, msg)

    # Si solo había un destinatario, devolver tuple para compatibilidad
    if len(results) == 1:
        return list(results.values())[0]
    return results


def test_smtp(to_email: str) -> tuple[bool, str]:
    ok, msg = is_smtp_configured()
    if not ok:
        return False, msg
    try:
        cfg = _resolve_smtp_config()
        msg = EmailMessage()
        msg["Subject"] = "Prueba SMTP desde App"
        msg["From"] = cfg.get("from")
        msg["To"] = to_email
        msg.set_content("Este es un mensaje de prueba para verificar la configuración SMTP.")

        port = cfg.get("port")
        with smtplib.SMTP(cfg.get("server"), port, timeout=10) as s:
            s.starttls()
            if cfg.get("user") and cfg.get("password"):
                s.login(cfg.get("user"), cfg.get("password"))
            s.send_message(msg)
        # registrar éxito en la tabla de logs
        try:
            log_email(to_email, msg["Subject"], "Prueba SMTP desde App", status="sent")
        except Exception:
            pass
        return True, "Correo de prueba enviado correctamente"
    except Exception as e:
        # registrar error en la tabla de logs
        try:
            log_email(to_email, "Prueba SMTP desde App", "Prueba SMTP desde App", status="failed", error=str(e))
        except Exception:
            pass
        return False, str(e)
