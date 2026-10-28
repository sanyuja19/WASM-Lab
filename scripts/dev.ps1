# WASM Lab Development Startup Script
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Starting WASM Lab Development       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend on port 8000
Write-Host "Starting FastAPI Backend at http://127.0.0.1:8000 ..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList $PSScriptRoot\..

Start-Sleep -Seconds 2

# 2. Start Vite Frontend on port 5173
Write-Host "Starting Vite Frontend at http://localhost:5173 ..." -ForegroundColor Green
Set-Location "$PSScriptRoot\..\frontend"
npm run dev
