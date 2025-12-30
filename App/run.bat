@echo off
cd /d %~dp0
echo Ejecutando la app de Streamlit...
python -m streamlit run app.py
pause


@REM @echo off
@REM cd /d %~dp0
@REM echo Ejecutando la app de Streamlit SOLO en localhost...
@REM python -m streamlit run V3.py --server.address localhost --server.port 8501
@REM pause
