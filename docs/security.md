# Security Architecture and Threat Safeguards

## 1. Threat Model & Safeguards

Compilers are inherently complex systems that process arbitrary, untrusted user code. WASM Lab implements defensive engineering across multiple layers:

| Vulnerability Vector | Potential Risk | Implemented Safeguard |
|---|---|---|
| **Denial of Service (Oversized Input)** | Server memory exhaustion | Strict 64 KB (`MAX_SOURCE_SIZE_BYTES`) payload limits in Pydantic schemas. |
| **Compiler Hang / Infinite Recursion** | CPU exhaustion during compilation | 10.0s compilation subprocess timeout (`COMPILATION_TIMEOUT_SECONDS`). |
| **Runtime Infinite Loop** | CPU freeze during WebAssembly execution | 5.0s execution timeout (`EXECUTION_TIMEOUT_SECONDS`). |
| **Command Injection** | Execution of arbitrary host shell commands | Zero shell interpolation (`shell=False`). Subprocesses receive structured argument lists. |
| **File System Pollution** | Disk filling via generated artifacts | Automatic directory cleanup using context-managed `tempfile.TemporaryDirectory`. |
| **Arbitrary Host Access** | Access to host files or network from compiled code | Freestanding WebAssembly sandbox without WASI syscalls, POSIX sockets, or host imports. |
| **Cross-Origin Access** | Unauthorized browser script communication | Configurable CORS middleware in FastAPI restricted to application origins in production. |

## 2. WebAssembly Sandboxing

WebAssembly modules execute in an isolated virtual machine:
1. **Isolated Memory**: The module has access only to its internal linear memory array (`WebAssembly.Memory`). It cannot read or write arbitrary host memory addresses.
2. **Zero System Capabilities**: Because MiniLang does not implement file I/O or network syscalls, no capability descriptors are passed to `wasmtime` or the browser engine.
3. **Deterministic Trapping**: Traps (such as integer division by zero) are caught by the runtime environment and converted into structured diagnostic errors rather than crashing the host process.
