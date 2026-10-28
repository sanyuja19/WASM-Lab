# Check toolchain availability and versions
Write-Host "=== WASM Lab Toolchain Inspection ===" -ForegroundColor Cyan

# 1. Python
$pyVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Python: $pyVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Python not found" -ForegroundColor Red
}

# 2. Node & npm
$nodeVersion = node --version 2>&1
$npmVersion = npm --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Node.js: $nodeVersion, npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Node.js/npm not found" -ForegroundColor Red
}

# 3. Python packages
python -c "
import llvmlite, llvmlite.binding as llvm, lark, fastapi, uvicorn, wasmtime, pytest
print(f'[OK] llvmlite: {llvmlite.__version__} (LLVM {llvm.llvm_version_info})')
print(f'[OK] lark: {lark.__version__}')
print(f'[OK] wasmtime: available')
print(f'[OK] fastapi: {fastapi.__version__}')
print(f'[OK] pytest: {pytest.__version__}')
"

# 4. LLVM/Clang for WebAssembly
$zigExe = "tools\zig-windows-x86_64-0.14.0\zig.exe"
if (Test-Path $zigExe) {
    $zigVer = & $zigExe version
    Write-Host "[OK] Clang/LLVM WebAssembly compiler (Zig $zigVer) at $zigExe" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Clang/LLVM compiler not found at $zigExe" -ForegroundColor Red
}

# 5. WABT utilities
$validateExe = "tools\wabt-1.0.42\bin\wasm-validate.exe"
$wasm2watExe = "tools\wabt-1.0.42\bin\wasm2wat.exe"
if ((Test-Path $validateExe) -and (Test-Path $wasm2watExe)) {
    Write-Host "[OK] WABT utilities verified at tools\wabt-1.0.42\bin\" -ForegroundColor Green
} else {
    Write-Host "[FAIL] WABT utilities not found" -ForegroundColor Red
}

Write-Host "======================================" -ForegroundColor Cyan
