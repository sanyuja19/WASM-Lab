# WASM Lab Troubleshooting Guide

## 1. Common Issues and Resolutions

### 1.1 Backend Offline in Frontend IDE
**Symptom**: The top status bar indicates "Backend Offline" and a red banner states that artifacts are in preview mode.  
**Cause**: The FastAPI backend server is not running on `http://127.0.0.1:8000`.  
**Resolution**:
1. Open PowerShell and navigate to the project directory:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. In the frontend IDE, click **Reconnect**.

---

### 1.2 PowerShell Script Execution Policy Restriction
**Symptom**: Running `.ps1` scripts produces: `File cannot be loaded because running scripts is disabled on this system`.  
**Cause**: Windows default execution policy restricts unsigned scripts.  
**Resolution**:
Run scripts with `-ExecutionPolicy Bypass`:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\dev.ps1
powershell -ExecutionPolicy Bypass -File scripts\test.ps1
powershell -ExecutionPolicy Bypass -File scripts\benchmark.ps1
```

---

### 1.3 Port 8000 or 5173 Already in Use
**Symptom**: `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): address already in use`.  
**Resolution**:
Find and terminate the process holding the port:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process -Force
```

---

### 1.4 Verifying the Native Toolchain
**Symptom**: Compiler reports `Clang/LLVM WebAssembly compiler not found`.  
**Resolution**:
Run the toolchain verification script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-toolchain.ps1
```
Verify that `tools/zig-windows-x86_64-0.14.0/zig.exe` and `tools/wabt-1.0.42/bin/wasm-validate.exe` exist.
