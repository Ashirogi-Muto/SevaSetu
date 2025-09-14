@echo off
echo ====================================
echo    SEVASETU Platform Setup
echo ====================================
echo Installing all dependencies...
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

echo [1/4] Installing Backend API dependencies...
cd /d f:\hackathon\backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo [2/4] Installing AI Model Server dependencies...
cd /d f:\hackathon\ai_model_server
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install AI model server dependencies
    pause
    exit /b 1
)

echo [3/4] Installing Admin Portal dependencies...
cd /d f:\hackathon\admin-portal
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install admin portal dependencies
    pause
    exit /b 1
)

echo [4/4] Installing Citizen Portal dependencies...
cd /d f:\hackathon\citizen-portal
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install citizen portal dependencies
    pause
    exit /b 1
)

echo.
echo ====================================
echo   Setup completed successfully!
echo ====================================
echo.
echo You can now run: start-sewasetu.bat
echo.
pause