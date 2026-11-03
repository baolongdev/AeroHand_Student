@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Hay chay CaiDat.bat truoc.
    pause
    exit /b 1
)
rem Tu tim cong Aero Hand. Co the truyen cong: ChayCamera.bat COM7  ^| chi xem camera: ChayCamera.bat none
set "AERO_PORT=%~1"
if "%AERO_PORT%"=="" set "AERO_PORT=auto"
".venv\Scripts\python.exe" "examples\dieu_khien_camera.py" --port %AERO_PORT%
pause
