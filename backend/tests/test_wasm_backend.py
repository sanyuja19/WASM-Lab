from backend.app.compiler.wasm_codegen import emit_wasm_binary
from backend.app.compiler.wasm_validator import validate_and_disassemble

def test_wasm_codegen_and_wabt_validation():
    ir_text = """
    target triple = "wasm32-unknown-unknown"
    target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"

    define i32 @main() {
    entry:
        ret i32 50
    }
    """
    wasm_bytes, size = emit_wasm_binary(ir_text, optimization_level="O2")
    assert size > 0
    # WABT validate and disassemble to WAT
    valid, wat = validate_and_disassemble(wasm_bytes)
    assert valid is True
    assert "(module" in wat
    assert "main" in wat
