@echo off
REM Deepfake Detection Dashboard - Quick Start
REM This script starts the Flask backend server

echo.
echo ==========================================
echo Deepfake Detection Dashboard
echo Backend Server Startup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python detected!
echo.

REM Check if requirements are installed
echo Checking for required packages...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
    echo Packages installed successfully!
    echo.
)

REM Start the server
echo Starting Flask server...
echo.
echo ==========================================
echo Server is running on: http://localhost:5000
echo ==========================================
echo.
echo Open index.html in your web browser to access the dashboard
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
