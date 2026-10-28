# WASM Lab Test Runner Script
Write-Host "=== Running WASM Lab Test Suite ===" -ForegroundColor Cyan

# 1. Backend tests with pytest
Write-Host "`n1. Running Backend & Compiler Test Suite (pytest)..." -ForegroundColor Yellow
python -m pytest backend/tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Backend tests failed!" -ForegroundColor Red
    exit 1
}

# 2. Frontend production build validation
Write-Host "`n2. Validating Frontend Production Build (tsc & vite build)..." -ForegroundColor Yellow
Push-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Frontend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "`n=================================================" -ForegroundColor Green
Write-Host "   ALL BACKEND AND FRONTEND CHECKS PASSED!      " -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
