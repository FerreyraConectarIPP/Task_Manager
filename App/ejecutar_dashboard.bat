@echo off
cd /d %~dp0
echo Ejecutando la app de Streamlit...
python -m streamlit run app.py
pause