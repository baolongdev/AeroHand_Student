@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Hay chay CaiDat.bat truoc.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "tools\kiem_tra_cai_dat.py"
pause
