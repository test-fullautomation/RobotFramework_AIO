@echo off
echo ========================================
echo Learning Tools Web Application
echo ========================================
echo.

REM Check if Python is installed
%RobotPythonPath%\python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Installing dependencies...
%RobotPythonPath%\python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting the web application...
echo The application will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

%RobotPythonPath%\python app.py
pause
