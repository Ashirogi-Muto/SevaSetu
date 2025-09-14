@echo off
echo ====================================
echo    SEVASETU Platform Startup
echo ====================================
echo Starting all required services...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo [1/4] Starting Backend API Server (Port 8000)...
start "SEVASETU Backend API" cmd /k "cd /d f:\hackathon\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/4] Starting AI Model Server (Port 8001)...
start "SEVASETU AI Model Server" cmd /k "cd /d f:\hackathon\ai_model_server && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

echo [3/4] Starting Admin Portal (Port 5173)...
start "SEVASETU Admin Portal" cmd /k "cd /d f:\hackathon\admin-portal && npm run dev"

echo [4/4] Starting Citizen Portal (Port 5174)...
start "SEVASETU Citizen Portal" cmd /k "cd /d f:\hackathon\citizen-portal && npm run dev -- --port 5174"

echo.
echo ====================================
echo   All SEVASETU services starting...
echo ====================================
echo.
echo Services will be available at:
echo  • Backend API:     http://localhost:8000
echo  • AI Model Server: http://localhost:8001  
echo  • Admin Portal:    http://localhost:5173
echo  • Citizen Portal:  http://localhost:5174
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo SECURITY NOTICE:
echo  • CORS is restricted to localhost origins only
echo  • Strong API keys are now in use
echo  • Security headers are enabled
echo.
echo Press any key to close this window...
echo NOTE: Keep the individual service windows open to keep services running
pause >nul