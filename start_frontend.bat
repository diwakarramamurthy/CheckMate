@echo off
echo Starting CheckMate Frontend...
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing npm dependencies (this may take a few minutes)...
    yarn install
)

echo.
echo Starting React dev server on http://localhost:3000
yarn start
pause
