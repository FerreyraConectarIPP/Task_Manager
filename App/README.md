# Task & Incident Manager

Esta aplicación es un gestor simple de tareas e incidentes usando Streamlit y SQLite.

## Configuración de SMTP

Puedes configurar el envío de correos de dos maneras:

1. Variables de entorno (prioridad alta):
   - SMTP_SERVER (ej. smtp.example.com)
   - SMTP_PORT (ej. 587)
   - SMTP_USER
   - SMTP_PASSWORD
   - SMTP_FROM (opcional)

   En PowerShell (solo sesión actual):
   ```powershell
   $env:SMTP_SERVER = "smtp.example.com"
   $env:SMTP_PORT = "587"
   $env:SMTP_USER = "user@domain"
   $env:SMTP_PASSWORD = "secret"
   $env:SMTP_FROM = "no-reply@domain"
   ```

2. Desde la app (Admin):
   - Ve a **Ajustes** → configura `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` y `APP_BASE_URL`. Usa **Enviar correo de prueba** para validar.

> Nota: Si no hay configuración SMTP activa, el flujo de "Olvidaste tu contraseña" te mostrará un mensaje indicando que contactes al administrador.

---

## Restablecimiento de contraseña

- Cuando solicitas restablecer la contraseña, la app genera un token con caducidad (1 hora) y envía un enlace por correo con `?reset_token=...`.
- El enlace te lleva a la app para elegir una nueva contraseña.

---

## Pruebas

Se usan `pytest`. Para correr las pruebas:

```bash
cd App
python -m pytest -q
```

Las pruebas incluyen:
- Tokens de restablecimiento (creación, consumo, expiración)
- Envío de emails (SMTP mockeado)
- Registro de emails en la base de datos

---

Si quieres que añada scripts de CI o más tests (p. ej. integración), puedo hacerlo.