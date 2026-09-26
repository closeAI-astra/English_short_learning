@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting pron-coach with a public https URL for your phone (valid 72 hours).
set /p COACH_U=Choose a user name: 
set /p COACH_P=Choose a password: 
uv run app.py --share --auth=%COACH_U%:%COACH_P%
pause
