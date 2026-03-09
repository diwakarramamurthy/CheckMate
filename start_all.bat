@echo off
echo ==========================================
echo   CheckMate - Starting all services
echo ==========================================
echo.

REM Start MongoDB (if not already running as a service)
echo Checking MongoDB...
sc query MongoDB >nul 2>&1
if %errorlevel% == 0 (
    echo MongoDB service found - starting...
    net start MongoDB >nul 2>&1
) else (
    echo MongoDB service not found. Make sure MongoDB is running manually.
    echo You can start it with: mongod --dbpath C:\data\db
    echo.
)

REM Start Backend in a new window
echo Starting Backend...
start "CheckMate Backend" cmd /k "cd /d "%~dp0backend" && pip install -r requirements.txt && uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend in a new window
echo Starting Frontend...
start "CheckMate Frontend" cmd /k "cd /d "%~dp0frontend" && (if not exist node_modules yarn install) && yarn start"

echo.
echo Both servers are starting in separate windows:
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:3000
echo.
pause
