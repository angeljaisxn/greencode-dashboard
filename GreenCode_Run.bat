
@REM @echo off
@REM cd /d "%~dp0"

@REM start "" "http://localhost:8501"

@REM python -m streamlit run dashboard\streamlit_app.py --server.headless true

@REM exit

@echo off
cd /d "%~dp0"
streamlit run dashboard/streamlit_app.py
