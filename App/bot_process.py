import subprocess
import re
from datetime import datetime
from pathlib import Path
import requests
import time

# Lanzar run.bat en paralelo (no bloqueante)
bat_process = subprocess.Popen([r"C:/Users/fferreyra/Documents/Projectos 2026/Task_Manager/App_v2/run.bat"])

# ------------------------------------------------------------------------------------------------------------------- #
# Descomentar estas lineas para que el path se identifique en el lugar,independientemente de donde este se encuentre. #
# ------------------------------------------------------------------------------------------------------------------- #

# SCRIPT_DIR = Path(__file__).parent
# bat_file = SCRIPT_DIR / "run.bat"
# bat_process = subprocess.Popen([str(bat_file)])

# ------------------------- #
# Config cloudflared        #
# ------------------------- #

CLOUDFLARED_CMD = [
    "cloudflared",
    "tunnel",
    "--url",
    "http://localhost:8501"
]

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"cloudflared_{datetime.now():%Y%m%d_%H%M%S}.log"

URL_REGEX = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")

LAST_URL_FILE = Path("last_url.txt")

# Telegram Bot config
TELEGRAM_BOT_TOKEN = "8390365208:AAG97Ctrr34i5zUNs86xmXMkit1JADM_fSU"
TELEGRAM_CHAT_ID = "1299421176"

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        print("✅ Mensaje Telegram enviado.")
    except Exception as e:
        print(f"⚠️ Error enviando Telegram: {e}")

def read_last_url():
    if LAST_URL_FILE.exists():
        return LAST_URL_FILE.read_text().strip()
    return None

def save_last_url(url: str):
    LAST_URL_FILE.write_text(url)

# ------------------------
# Run cloudflared monitor
# ------------------------
print("▶ Iniciando cloudflared...")

last_url = read_last_url()
found_url = None

process = subprocess.Popen(
    CLOUDFLARED_CMD,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

with LOG_FILE.open("w", encoding="utf-8") as log:
    for line in process.stdout:
        print(line, end="")       # mostrar en consola
        log.write(line)           # guardar en archivo

        if not found_url:
            match = URL_REGEX.search(line)
            if match:
                found_url = match.group(0)
                print(f"\n✅ URL detectada: {found_url}\n")

                if found_url != last_url:
                    save_last_url(found_url)
                    send_telegram_message(f"🌐 Nueva URL de cloudflared:\n{found_url}")
                else:
                    print("ℹ️ La URL es igual a la última guardada. No se envía notificación.")

process.wait()

# Opcional: si querés, podés controlar el estado del .bat
# Por ejemplo, chequear cada tanto si sigue corriendo:
while bat_process.poll() is None:
    # El .bat sigue corriendo
    time.sleep(5)

print("El proceso run.bat finalizó.")
