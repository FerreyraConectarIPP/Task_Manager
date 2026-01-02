@REM Comentarios con rutas absolutas removidos; el .bat usa rutas relativas y fallbacks.


@REM Esta parte de codigo logra que la direccion en la que se encuentra el script sea la misma desde la que se ejecuta el script, evitando problemas de rutas relativas.

@echo off
REM Cambiar al directorio donde está este script
cd /d "%~dp0"

REM Ejecutar el script con Python
if exist "%~dp0backup.py" (
    python "%~dp0backup.py"
) else (
    if exist "%~dp0..\Task_Manager\App_v2\backup.py" (
        pushd "%~dp0..\Task_Manager\App_v2"
        python backup.py
        popd
    ) else (
        echo No se encontró backup.py en "%~dp0" ni en "..\Task_Manager\App_v2"
        echo Ajusta la ruta o coloca el script en el mismo directorio que este .bat
    )
)

REM Pausa para ver mensajes en consola
pause
