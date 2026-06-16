@echo off
REM Jalankan dashboard IGRS (Windows)
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m streamlit run app.py
pause
