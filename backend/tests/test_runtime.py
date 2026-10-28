from backend.app.compiler.wasm_codegen import emit_wasm_binary
from backend.app.compiler.runtime import execute_wasm

def test_runtime_executes_valid_module():
    ir_text = """
    target triple = "wasm32-unknown-unknown"
    target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"

    define i32 @main() {
    entry:
        ret i32 77
    }
    """
    wasm_bytes, _ = emit_wasm_binary(ir_text, optimization_level="O2")
    res = execute_wasm(wasm_bytes)
    assert res["success"] is True
    assert res["return_value"] == 77
    assert res["duration_ms"] >= 0
