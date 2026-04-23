@echo off
REM Unified project startup script (backend + frontend)

setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo Deepfake Detection Dashboard
echo Full Project Startup
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not available in PATH.
        echo Install Python 3.8+ and run this script again.
        pause
        exit /b 1
    )
    py run_project.py
) else (
    python run_project.py
)

if errorlevel 1 (
    echo.
    echo Startup failed. Check logs above.
)

pause
