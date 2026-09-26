@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting pron-coach at http://127.0.0.1:7860  (close this window to stop)
uv run app.py
pause
