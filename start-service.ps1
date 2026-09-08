# Human-Agent Services Startup Script (start-service.ps1)

$ErrorActionPreference = "Continue"

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       Starting Human-Agent System" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$BackendPort = 8100
$FrontendPort = 8101

$BackendOccupied = $null
try { $BackendOccupied = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction Stop } catch { }

$FrontendOccupied = $null
try { $FrontendOccupied = Get-NetTCPConnection -LocalPort $FrontendPort -State Listen -ErrorAction Stop } catch { }

if ($BackendOccupied) {
    Write-Warning "Port $BackendPort is already in use!"
} else {
    Write-Host "=> Starting Backend Service on port $BackendPort..." -ForegroundColor Green
    $BackendArgs = @(
        "-NoProfile",
        "-NoExit",
        "-Command",
        "cd `"$PSScriptRoot\backend`"; & `"$PSScriptRoot\backend\venv\Scripts\python.exe`" -m app.main"
    )
    Start-Process "powershell" -ArgumentList $BackendArgs -WindowStyle Normal
}

Start-Sleep -Seconds 1

if ($FrontendOccupied) {
    Write-Warning "Port $FrontendPort is already in use!"
} else {
    Write-Host "=> Starting Frontend Service on port $FrontendPort..." -ForegroundColor Green
    $FrontendArgs = @(
        "-NoProfile",
        "-NoExit",
        "-Command",
        "cd `"$PSScriptRoot\frontend`"; npm run dev"
    )
    Start-Process "powershell" -ArgumentList $FrontendArgs -WindowStyle Normal
}

Write-Host ""
Write-Host "=> Startup processes initiated!" -ForegroundColor Cyan
Write-Host "=> [This window will close in 5 seconds]" -ForegroundColor DarkGray
Start-Sleep -Seconds 5
