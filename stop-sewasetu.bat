@echo off
echo ====================================
echo   SEVASETU Platform Shutdown
echo ====================================
echo Stopping all SEVASETU services...
echo.

REM Kill processes by port
echo Stopping Backend API (Port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1

echo Stopping AI Model Server (Port 8001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a >nul 2>&1

echo Stopping Admin Portal (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a >nul 2>&1

echo Stopping Citizen Portal (Port 5174)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5174') do taskkill /f /pid %%a >nul 2>&1

REM Also kill by window title (backup method)
taskkill /fi "WINDOWTITLE:SEVASETU*" /f >nul 2>&1

echo.
echo ====================================
echo  All SEVASETU services stopped
echo ====================================
echo.
pause