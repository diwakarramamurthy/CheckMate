@echo off
echo Starting CheckMate Backend...
cd /d "%~dp0backend"

if not exist ".env" (
    echo ERROR: .env file not found in backend folder.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on http://localhost:8001
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
pause
