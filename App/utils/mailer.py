import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587)) if os.environ.get("SMTP_PORT") else None
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_FROM = os.environ.get("SMTP_FROM") or SMTP_USER

from database.settings import get_setting
from database.emails import log_email


def _resolve_smtp_config():
    # Prioridad: variables de entorno, luego configuración guardada en DB (settings table)
    server = SMTP_SERVER or get_setting("SMTP_SERVER")
    port = SMTP_PORT or (int(get_setting("SMTP_PORT")) if get_setting("SMTP_PORT") else None)
    user = SMTP_USER or get_setting("SMTP_USER")
    password = SMTP_PASSWORD or get_setting("SMTP_PASSWORD")
    from_addr = SMTP_FROM or get_setting("SMTP_FROM") or user
    return {
        "server": server,
        "port": port or 587,
        "user": user,
        "password": password,
        "from": from_addr,
    }


def is_smtp_configured() -> tuple[bool, str]:
    cfg = _resolve_smtp_config()
    if not cfg.get("server"):
        return False, "SMTP no configurado (SMTP_SERVER no definido)."
    return True, "OK"


def send_password_email(to_email: str, username: str, password: str) -> tuple[bool, str]:
    """Enviar un email con la contraseña. Devuelve (ok, message).

    Esta función sigue disponible, pero su uso está desaconsejado en favor del flujo de restablecimiento por token.
    """
    ok, msg = is_smtp_configured()
    if not ok:
        return False, msg

    try:
        cfg = _resolve_smtp_config()
        msg = EmailMessage()
        msg["Subject"] = f"Recuperación de contraseña - {username}"
        msg["From"] = cfg.get("from")
        msg["To"] = to_email
        body = f"Hola {username},\n\nTu contraseña actual es: {password}\n\nPor seguridad, considera cambiarla al ingresar al sistema.\n\nSaludos."
        msg.set_content(body)

        port = cfg.get("port")
        with smtplib.SMTP(cfg.get("server"), port, timeout=10) as s:
            s.starttls()
            if cfg.get("user") and cfg.get("password"):
                s.login(cfg.get("user"), cfg.get("password"))
            s.send_message(msg)
        # registrar éxito en la tabla de logs
        try:
            log_email(to_email, msg["Subject"], body, status="sent")
        except Exception:
            pass
        return True, "Email enviado correctamente"
    except Exception as e:
        # registrar error en la tabla de logs
        try:
            log_email(to_email, f"Recuperación de contraseña - {username}", body, status="failed", error=str(e))
        except Exception:
            pass
        return False, str(e)


def send_reset_email(to_email: str, username: str, reset_link: str) -> tuple[bool, str]:
    """Enviar email con enlace para restablecer contraseña"""
    ok, msg = is_smtp_configured()
    if not ok:
        return False, msg

    try:
        cfg = _resolve_smtp_config()
        msg = EmailMessage()
        msg["Subject"] = f"Restablecer contraseña - {username}"
        msg["From"] = cfg.get("from")
        msg["To"] = to_email
        body = f"Hola {username},\n\nHas solicitado restablecer tu contraseña. Accede al siguiente enlace para elegir una nueva contraseña:\n\n{reset_link}\n\nEste enlace expira en 1 hora. Si no solicitaste este cambio, ignora este mensaje.\n\nSaludos."
        msg.set_content(body)

        port = cfg.get("port")
        with smtplib.SMTP(cfg.get("server"), port, timeout=10) as s:
            s.starttls()
            if cfg.get("user") and cfg.get("password"):
                s.login(cfg.get("user"), cfg.get("password"))
            s.send_message(msg)
        # registrar éxito en la tabla de logs
        try:
            log_email(to_email, msg["Subject"], body, status="sent")
        except Exception:
            pass
        return True, "Email enviado correctamente"
    except Exception as e:
        # registrar error en la tabla de logs
        try:
            log_email(to_email, f"Restablecer contraseña - {username}", body, status="failed", error=str(e))
        except Exception:
            pass
        return False, str(e)


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
