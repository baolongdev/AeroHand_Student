@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CaiDat.ps1"
set "AERO_EXIT=%ERRORLEVEL%"
pause
exit /b %AERO_EXIT%
