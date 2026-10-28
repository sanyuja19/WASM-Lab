# WASM Lab REST API Specification

The WASM Lab backend is built with FastAPI and exposes standardized, strictly typed JSON endpoints documented via OpenAPI at `/docs`.

## 1. Endpoints Overview

| Method | Endpoint | Description | Request Body | Response Model |
|---|---|---|---|---|
| `GET` | `/api/health` | Health check & toolchain availability | None | `HealthResponse` |
| `GET` | `/api/compiler-info` | Detected LLVM/Clang/WABT toolchain info | None | `CompilerInfoResponse` |
| `GET` | `/api/examples` | Curated sample programs | None | `List[ExampleProgram]` |
| `POST` | `/api/compile` | End-to-end compilation & execution | `CompileRequest` | `CompileResponse` |
| `POST` | `/api/compare` | Compares O0 vs O2 optimization artifacts | `CompareRequest` | `CompareResponse` |
| `POST` | `/api/run` | Executes standalone base64 WASM binary | `RunRequest` | `RuntimeResult` |

---

## 2. Request & Response Schemas

### 2.1 `POST /api/compile`

#### Request:
```json
{
  "source": "fn main() -> i32 { return 50; }",
  "filename": "program.mini",
  "optimization": "O2",
  "execute": true
}
```

#### Response (Success):
```json
{
  "success": true,
  "filename": "program.mini",
  "optimization_level": "O2",
  "total_duration_ms": 154.2,
  "diagnostics": [],
  "stage_metrics": [
    { "name": "frontend", "status": "success", "duration_ms": 3.4 },
    { "name": "semantic", "status": "success", "duration_ms": 0.1 },
    { "name": "ir_generation", "status": "success", "duration_ms": 0.4 },
    { "name": "llvm_verification", "status": "success", "duration_ms": 0.9 },
    { "name": "optimization", "status": "success", "duration_ms": 3.1 },
    { "name": "wasm_codegen", "status": "success", "duration_ms": 115.8 },
    { "name": "wasm_validation", "status": "success", "duration_ms": 28.2 },
    { "name": "runtime", "status": "success", "duration_ms": 2.4 }
  ],
  "ast_tree": { ... },
  "raw_ir": "; ModuleID = ...",
  "optimized_ir": "define i32 @main() { ret i32 50 }",
  "wat": "(module ...)",
  "wasm_base64": "AGFzbQEAAA...",
  "wasm_size_bytes": 234,
  "optimization_metrics": {
    "level": "O2",
    "initial_instructions": 10,
    "optimized_instructions": 2,
    "instructions_eliminated": 8,
    "passes_applied": [ "SROA", "SCCP", "InstCombine", "DCE", "SimplifyCFG", "Verifier" ]
  },
  "runtime_result": {
    "success": true,
    "return_value": 50,
    "duration_ms": 2.4,
    "exports": [ "memory", "__original_main", "main" ]
  },
  "compiler_logs": [ ... ]
}
```

### 2.2 Error Diagnostic Payload (HTTP 200 with `success: false`)
When source code contains a syntax or semantic error:
```json
{
  "success": false,
  "diagnostics": [
    {
      "stage": "semantic",
      "message": "Duplicate variable declaration 'x' in the same scope",
      "severity": "error",
      "code": "ERR_DUPLICATE_VAR",
      "location": {
        "line": 3,
        "column": 5,
        "end_line": 3,
        "end_column": 21
      }
    }
  ],
  "stage_metrics": [
    { "name": "frontend", "status": "success", "duration_ms": 3.1 },
    { "name": "semantic", "status": "failed", "duration_ms": 0.1 },
    { "name": "ir_generation", "status": "skipped", "duration_ms": 0.0 },
    ...
  ]
}
```
