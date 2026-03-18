@echo off
echo ==========================================
echo   CheckMate - Push Changes to GitHub
echo ==========================================
echo.

cd /d "%~dp0"

REM Search for git in common install locations
set GIT=
if exist "C:\Program Files\Git\cmd\git.exe"         set GIT="C:\Program Files\Git\cmd\git.exe"
if exist "C:\Program Files\Git\bin\git.exe"         set GIT="C:\Program Files\Git\bin\git.exe"
if exist "C:\Program Files (x86)\Git\cmd\git.exe"   set GIT="C:\Program Files (x86)\Git\cmd\git.exe"
if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe"  set GIT="%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
if exist "%USERPROFILE%\AppData\Local\Programs\Git\cmd\git.exe" set GIT="%USERPROFILE%\AppData\Local\Programs\Git\cmd\git.exe"

REM GitHub Desktop ships its own git
for /d %%D in ("%LOCALAPPDATA%\GitHubDesktop\app-*") do (
    if exist "%%D\resources\app\git\cmd\git.exe" set GIT="%%D\resources\app\git\cmd\git.exe"
)

if "%GIT%"=="" (
    echo ERROR: Could not find git.exe on this computer.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo Found git at: %GIT%
echo.

REM ── Show current status ───────────────────────────────────────────────────
echo Current git status:
%GIT% status --short
echo.

REM ── Stage all changed backend and frontend source files ───────────────────
echo Staging all changed source files...

REM Backend routers (all of them - includes new weightage + Excel routes)
%GIT% add backend/routers/auth_router.py
%GIT% add backend/routers/buildings.py
%GIT% add backend/routers/construction.py
%GIT% add backend/routers/construction_excel.py
%GIT% add backend/routers/costs.py
%GIT% add backend/routers/dashboard.py
%GIT% add backend/routers/financial.py
%GIT% add backend/routers/projects.py
%GIT% add backend/routers/reports.py
%GIT% add backend/routers/sales.py
%GIT% add backend/routers/templates_router.py
%GIT% add backend/routers/__init__.py

REM Core backend files (models, auth, server, generators)
%GIT% add backend/server.py
%GIT% add backend/models.py
%GIT% add backend/auth.py
%GIT% add backend/database.py
%GIT% add backend/requirements.txt

REM Frontend source pages and components
%GIT% add frontend/src/pages/ConstructionProgress.jsx
%GIT% add frontend/src/pages/Buildings.jsx
%GIT% add frontend/src/pages/Dashboard.jsx
%GIT% add frontend/src/pages/Import.jsx
%GIT% add frontend/src/pages/LandCost.jsx
%GIT% add frontend/src/pages/LoginPage.jsx
%GIT% add frontend/src/pages/ProjectCosts.jsx
%GIT% add frontend/src/pages/ProjectForm.jsx
%GIT% add frontend/src/pages/Projects.jsx
%GIT% add frontend/src/pages/Reports.jsx
%GIT% add frontend/src/pages/Sales.jsx

REM Frontend config, context, and layout
%GIT% add frontend/src/config.js
%GIT% add frontend/src/App.js
%GIT% add frontend/src/index.js
%GIT% add frontend/src/context/AuthContext.js
%GIT% add frontend/package.json

REM Deployment config
%GIT% add render.yaml

REM NOTE: .env files are intentionally NOT staged (they contain secrets).
REM       Set environment variables directly in the Render dashboard.
echo.

REM ── Show what will be committed ───────────────────────────────────────────
echo Files staged for commit:
%GIT% diff --cached --name-only
echo.

REM ── Prompt for commit message ─────────────────────────────────────────────
set /p COMMIT_MSG="Enter commit message (or press Enter for auto-message): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=chore: sync all backend routers and frontend pages

echo.
echo Committing with message: %COMMIT_MSG%
%GIT% commit -m "%COMMIT_MSG%"

if %errorlevel% NEQ 0 (
    echo.
    echo Nothing new to commit or commit failed. Check above for details.
    echo.
    pause
    exit /b 0
)

echo.
echo Pushing to GitHub...
%GIT% push origin main

echo.
if %errorlevel% == 0 (
    echo ==========================================
    echo   SUCCESS! Changes pushed to GitHub.
    echo   Render will auto-deploy in 2-3 mins.
    echo   Check: checkmate.johorats.com
    echo   API:   https://checkmate-backend-cxd1.onrender.com/docs
    echo ==========================================
) else (
    echo ==========================================
    echo   Push failed. Common fixes:
    echo   1. Run: git pull origin main --rebase
    echo      Then re-run this script.
    echo   2. Check your GitHub credentials/token.
    echo ==========================================
)

echo.
pause
