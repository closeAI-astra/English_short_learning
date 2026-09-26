@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist phone_login.txt goto run
echo First time only: choose a user name and password for the phone page (letters and numbers only).
set /p COACH_U=User name: 
set /p COACH_P=Password: 
>phone_login.txt echo %COACH_U%:%COACH_P%
:run
set /p COACH_AUTH=<phone_login.txt
echo Starting pron-coach for your phone. A QR code will appear - scan it with the phone camera.
echo (Login is saved in phone_login.txt. Delete that file to change it.)
uv run app.py --share --auth=%COACH_AUTH%
pause
