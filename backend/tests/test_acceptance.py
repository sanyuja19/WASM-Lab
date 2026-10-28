from backend.app.compiler.pipeline import CompilerPipeline

def test_canonical_acceptance_pipeline():
    """
    Primary Acceptance Test:
    fn main() -> i32 {
        let x: i32 = 10;
        let y: i32 = 20;
        return x + y * 2;
    }
    Must pass all 8 pipeline stages, generate valid WebAssembly,
    and return exactly 50 from the real compiled WebAssembly binary.
    """
    source = """
    fn main() -> i32 {
        let x: i32 = 10;
        let y: i32 = 20;
        return x + y * 2;
    }
    """
    pipeline = CompilerPipeline()
    result = pipeline.run(source, filename="arithmetic.mini", optimization_level="O2", execute=True)

    # 1. Pipeline success
    assert result.success is True, f"Compilation failed: {result.diagnostics}"
    assert len(result.diagnostics) == 0

    # 2. Stage metrics verification
    stage_names = [m.name for m in result.stage_metrics]
    assert "frontend" in stage_names
    assert "semantic" in stage_names
    assert "ir_generation" in stage_names
    assert "llvm_verification" in stage_names
    assert "optimization" in stage_names
    assert "wasm_codegen" in stage_names
    assert "wasm_validation" in stage_names
    assert "runtime" in stage_names

    for stage in result.stage_metrics:
        assert stage.status.value == "success", f"Stage {stage.name} was not success: {stage.status}"

    # 3. LLVM IR verification
    assert result.raw_ir is not None
    assert "wasm32-unknown-unknown" in result.raw_ir
    assert result.optimized_ir is not None
    assert "ret i32 50" in result.optimized_ir

    # 4. WebAssembly binary and WAT verification
    assert result.wasm_size_bytes > 0
    assert result.wat is not None
    assert "(module" in result.wat
    assert result.wasm_base64 is not None

    # 5. Exact return value verification
    assert result.runtime_result is not None
    assert result.runtime_result["success"] is True
    assert result.runtime_result["return_value"] == 50
