# CheckMate - Push to GitHub (PowerShell version)
# Right-click this file and choose "Run with PowerShell"

Set-Location -Path $PSScriptRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CheckMate - Pushing to GitHub" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Show current status
Write-Host "Current git status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Stage all changed files
Write-Host "Staging files..." -ForegroundColor Yellow

git add backend/routers/auth_router.py
git add backend/routers/buildings.py
git add backend/routers/construction.py
git add backend/routers/construction_excel.py
git add backend/routers/costs.py
git add backend/routers/dashboard.py
git add backend/routers/financial.py
git add backend/routers/projects.py
git add backend/routers/reports.py
git add backend/routers/sales.py
git add backend/routers/templates_router.py
git add backend/routers/__init__.py
git add backend/server.py
git add backend/models.py
git add backend/auth.py
git add backend/database.py
git add backend/requirements.txt
git add frontend/src/pages/ConstructionProgress.jsx
git add frontend/src/pages/Buildings.jsx
git add frontend/src/pages/Dashboard.jsx
git add frontend/src/pages/Import.jsx
git add frontend/src/pages/LandCost.jsx
git add frontend/src/pages/LoginPage.jsx
git add frontend/src/pages/ProjectCosts.jsx
git add frontend/src/pages/ProjectForm.jsx
git add frontend/src/pages/Projects.jsx
git add frontend/src/pages/Reports.jsx
git add frontend/src/pages/Sales.jsx
git add frontend/src/config.js
git add frontend/src/App.js
git add frontend/src/index.js
git add frontend/src/context/AuthContext.js
git add frontend/package.json
git add render.yaml

Write-Host ""
Write-Host "Files staged:" -ForegroundColor Yellow
git diff --cached --name-only
Write-Host ""

# Commit
$msg = "feat: add Excel download/upload for construction progress with bulk copy feature"
Write-Host "Committing: $msg" -ForegroundColor Yellow
git commit -m $msg

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  DONE! Render will deploy in 2-3 mins." -ForegroundColor Green
Write-Host "  Check: checkmate.johorats.com" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
