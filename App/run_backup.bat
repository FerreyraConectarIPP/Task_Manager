@echo off
REM Cambiar al directorio donde está tu script
cd /d "C:\Users\fferreyra\Documents\Projectos 2026\Task_Manager\App_v2"

REM Ejecutar el script con Python
python backup.py

REM Pausa para ver mensajes en consola
pause


@REM Esta parte de codigo logra que la direccion en la que se encuentra el script sea la misma desde la que se ejecuta el script, evitando problemas de rutas relativas.

@REM @echo off
@REM REM Cambiar al directorio donde está este script
@REM cd /d "%~dp0"

@REM REM Ejecutar el script con Python
@REM python backup.py

@REM REM Pausa para ver mensajes en consola
@REM pause
