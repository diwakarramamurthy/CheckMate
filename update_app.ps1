# CheckMate - Update App from GitHub
# Run this in PowerShell: Right-click -> "Run with PowerShell"

$ErrorActionPreference = "Stop"
$baseUrl = "https://raw.githubusercontent.com/diwakarramamurthy/CheckMate/main"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CheckMate - Downloading Latest Updates  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# All files to download from GitHub
$files = @(
    "backend/server.py",
    "backend/auth.py",
    "backend/database.py",
    "backend/models.py",
    "backend/requirements.txt",
    "backend/routers/__init__.py",
    "backend/routers/auth_router.py",
    "backend/routers/buildings.py",
    "backend/routers/construction.py",
    "backend/routers/costs.py",
    "backend/routers/dashboard.py",
    "backend/routers/financial.py",
    "backend/routers/projects.py",
    "backend/routers/reports.py",
    "backend/routers/sales.py",
    "backend/routers/templates_router.py",
    "frontend/src/App.js",
    "frontend/src/config.js",
    "frontend/src/context/AuthContext.js",
    "frontend/src/utils/formatting.js",
    "frontend/src/components/common/ProtectedRoute.jsx",
    "frontend/src/components/layout/Layout.jsx",
    "frontend/src/components/layout/Sidebar.jsx",
    "frontend/src/pages/Buildings.jsx",
    "frontend/src/pages/ConstructionProgress.jsx",
    "frontend/src/pages/Dashboard.jsx",
    "frontend/src/pages/Import.jsx",
    "frontend/src/pages/LandCost.jsx",
    "frontend/src/pages/LoginPage.jsx",
    "frontend/src/pages/ProjectCosts.jsx",
    "frontend/src/pages/ProjectForm.jsx",
    "frontend/src/pages/Projects.jsx",
    "frontend/src/pages/Reports.jsx",
    "frontend/src/pages/Sales.jsx"
)

$success = 0
$failed = 0

foreach ($file in $files) {
    $url = "$baseUrl/$file"
    $dest = Join-Path $root ($file -replace "/", "\")
    $dir = Split-Path -Parent $dest

    # Create directory if it doesn't exist
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    try {
        Write-Host "Downloading $file..." -NoNewline
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        Write-Host " OK" -ForegroundColor Green
        $success++
    } catch {
        Write-Host " FAILED: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Downloaded: $success files" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "  Failed: $failed files" -ForegroundColor Red
}
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes
Write-Host "Stopping existing CheckMate processes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.MainWindowTitle -like "*CheckMate*" } | Stop-Process -Force -ErrorAction SilentlyContinue
$ports = @(8001, 3000)
foreach ($port in $ports) {
    $conn = netstat -aon 2>$null | Select-String ":$port\s.*LISTENING"
    if ($conn) {
        $pid_ = ($conn -split "\s+")[-1]
        if ($pid_ -match "^\d+$") {
            Stop-Process -Id $pid_ -Force -ErrorAction SilentlyContinue
            Write-Host "  Stopped process on port $port" -ForegroundColor Gray
        }
    }
}

Start-Sleep -Seconds 2

# Start Backend
Write-Host ""
Write-Host "Starting Backend..." -ForegroundColor Yellow
$backendPath = Join-Path $root "backend"
Start-Process "cmd" -ArgumentList "/k", "cd /d `"$backendPath`" && pip install -r requirements.txt && uvicorn server:app --host 0.0.0.0 --port 8001 --reload" -WindowStyle Normal

Start-Sleep -Seconds 4

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $root "frontend"
Start-Process "cmd" -ArgumentList "/k", "cd /d `"$frontendPath`" && yarn start" -WindowStyle Normal

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CheckMate is starting up!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8001" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Browser will open in ~30 seconds." -ForegroundColor Gray
Write-Host "Press any key to close this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
