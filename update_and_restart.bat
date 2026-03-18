@echo off
echo ==========================================
echo   CheckMate - Update and Restart
echo ==========================================
echo.

REM Navigate to the CheckMate folder
cd /d "%~dp0"

REM Pull latest changes from GitHub
echo Pulling latest updates from GitHub...
git stash
git pull origin main
git stash pop

if %errorlevel% neq 0 (
    echo.
    echo WARNING: git pull encountered an issue.
    echo Please check the output above.
    echo You may need to resolve conflicts manually.
    pause
    exit /b 1
)

echo.
echo Update successful! Starting services...
echo.

REM Kill any existing processes on ports 8001 and 3000
echo Stopping any existing CheckMate processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

timeout /t 2 /nobreak >nul

REM Install any new backend dependencies
echo Installing backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt >nul 2>&1

REM Start Backend
echo Starting Backend...
start "CheckMate Backend" cmd /k "cd /d "%~dp0backend" && uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 3 /nobreak >nul

REM Install any new frontend dependencies
echo Installing frontend dependencies...
cd /d "%~dp0frontend"
call yarn install >nul 2>&1

REM Start Frontend
echo Starting Frontend...
start "CheckMate Frontend" cmd /k "cd /d "%~dp0frontend" && yarn start"

echo.
echo ==========================================
echo   CheckMate is starting up!
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:3000
echo ==========================================
echo.
echo Both servers are opening in separate windows.
echo The browser will open automatically in ~30 seconds.
echo.
pause
