@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Hay giai nen toan bo ZIP va chay CaiDat.bat truoc.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m aero_open_sdk
pause
