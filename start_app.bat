@echo off
cd /d %~dp0

echo Starte die AVG Papieranalyse...
streamlit run streamlit_app.py
pause
