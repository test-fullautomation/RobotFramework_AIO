@echo off
REM Start both Learning Tools API and Web Application

echo ========================================
echo Starting Learning Tools Platform
echo ========================================
echo.

REM Set environment variables
set NO_PROXY=localhost,127.0.0.1,::1
set LEARNINGTOOLS_DISABLE_JUPYTER_DETECTION=1
set FLASK_DEBUG=false

REM Check Python
%RobotPythonPath%\python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Starting Learning Tools API on port 5001...
start "Learning Tools API" cmd /k "cd learningtools && %RobotPythonPath%\python api.py"
timeout /t 3 /nobreak > nul

echo [2/3] Starting Web Application on port 5000...
start "Learning Tools WebApp" cmd /k "cd learningwebapp && %RobotPythonPath%\python app.py"
timeout /t 3 /nobreak > nul

echo [3/3] Platform started!
echo.
echo ========================================
echo Access the application at:
echo   http://localhost:5000
echo.
echo API is running at:
echo   http://localhost:5001
echo ========================================
echo.
echo Press any key to open browser...
pause > nul

start http://localhost:5000

echo.
echo Close the terminal windows to stop the servers.
