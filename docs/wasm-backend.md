# WebAssembly Backend, Validation, and Runtime Architecture

## 1. WebAssembly Target Configuration

WASM Lab configures LLVM to target standard 32-bit WebAssembly:
- **Target Triple**: `wasm32-unknown-unknown`
- **Data Layout**: `e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20`
  - Little-endian (`e`)
  - 32-bit pointers (`p:32:32`)
  - 64-bit natural alignment (`i64:64`)

## 2. Freestanding Emission & Linking

Traditional C compilers require `libc` (e.g., `musl` or `glibc`) which pulls in heavy POSIX system calls and file descriptor tables. Because MiniLang is a clean, self-contained language, WASM Lab generates **freestanding WebAssembly**:
- Compilation flags:
  `-target wasm32-freestanding -nostdlib -Wl,--no-entry -Wl,--export=main -Wl,--export-all`
- **Zero Imported Symbols**: The resulting module requires no host imports, preventing runtime resolution failures.
- **Minimal Binary Footprint**: Unoptimized binaries are ~300 bytes; optimized binaries are ~230 bytes.

## 3. WebAssembly Binary Section Structure

The generated `.wasm` binary adheres to the standard W3C WebAssembly binary format:
```
+------------------------------------+
| 0x00 0x61 0x73 0x6D (Magic "\0asm")|
+------------------------------------+
| 0x01 0x00 0x00 0x00 (Version 1)    |
+------------------------------------+
| Section 1: Type Section            |
| Section 3: Function Section        |
| Section 5: Memory Section          |
| Section 7: Export Section (main)   |
| Section 10: Code Section           |
| Custom Sections (name, features)   |
+------------------------------------+
```

## 4. WABT Specification Validation & Disassembly

Before execution, every compiled binary is validated using official WABT utilities:
1. `wasm-validate module.wasm`: Verifies that instruction opcodes, local indices, block stack heights, and type signatures strictly conform to W3C WebAssembly specifications.
2. `wasm2wat --generate-names module.wasm`: Disassembles the binary into readable S-expression WebAssembly Text Format (WAT) for user inspection in the IDE.

## 5. Dual Runtime Execution Model

WASM Lab verifies execution across two independent runtimes:

### 5.1 Backend Runtime (`wasmtime`)
- Implemented via `wasmtime-py` (v50.0.1) based on Bytecode Alliance's Cranelift engine.
- Instantiates the module in an isolated store.
- Enforces strict timeout limits (5.0 seconds) and traps on invalid operations (e.g., division by zero).
- Extracts and returns the integer result of `main()`.

### 5.2 Browser Runtime (WebAssembly JavaScript API)
- The frontend decodes the base64 WebAssembly binary and invokes:
  ```typescript
  const wasmModule = await WebAssembly.instantiate(bytes, {});
  const result = wasmModule.instance.exports.main();
  ```
- This proves that the binary executes natively in the user's browser V8 / SpiderMonkey engine without any backend emulation.
