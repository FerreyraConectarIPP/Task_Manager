import os
import shutil
import time
from datetime import datetime, timedelta

start_time = "08:00"
finish_time = "18:00"
date_format = "%H:%M"

t_start = datetime.strptime(start_time, date_format).time()
t_finish = datetime.strptime(finish_time, date_format).time()

interval_time = 2  
time2request = 3600*2
next_try = None

def backup_database(db_file="Database.db", backup_root="BackUp_database"):
    if not os.path.exists(db_file):
        print(f"❌ No se encontró el archivo {db_file}")
        return

    if not os.path.exists(backup_root):
        os.makedirs(backup_root)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"Database_backup_{timestamp}.db"
    backup_path = os.path.join(backup_root, backup_filename)

    shutil.copy2(db_file, backup_path)
    print(f"✅ Copia creada: {backup_path}")

while True:
    ahora = datetime.now()
    curr_time = ahora.time()

    if t_start <= curr_time <= t_finish:
        if next_try is None:
            backup_database("Database.db")
            next_try = ahora + timedelta(hours=interval_time)

        elif ahora >= next_try:
            backup_database("Database.db")
            next_try = ahora + timedelta(hours=interval_time)

    if curr_time > t_finish:
        print("⏹ Fin del intervalo de copias de seguridad.")
        break

    time.sleep(time2request)  # espera 30 segundos antes de chequear otra vez
