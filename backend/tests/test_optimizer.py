from backend.app.compiler.parser import parse_source
from backend.app.compiler.semantic import analyze_semantics
from backend.app.compiler.ir_generator import generate_ir
from backend.app.compiler.optimizer import optimize_llvm_ir

def test_o0_preserves_allocas():
    src = "fn main() -> i32 { let x: i32 = 10; return x; }"
    prog = parse_source(src)
    analyze_semantics(prog)
    raw_ir = generate_ir(prog)

    opt_ir, metrics = optimize_llvm_ir(raw_ir, level="O0")
    assert metrics["level"] == "O0"
    assert "alloca" in opt_ir

def test_o2_constant_folds_and_eliminates_allocas():
    src = "fn main() -> i32 { let x: i32 = 10; let y: i32 = 20; return x + y * 2; }"
    prog = parse_source(src)
    analyze_semantics(prog)
    raw_ir = generate_ir(prog)

    opt_ir, metrics = optimize_llvm_ir(raw_ir, level="O2")
    assert metrics["level"] == "O2"
    assert metrics["instructions_eliminated"] > 0
    # O2 constant folds 10 + 20 * 2 = 50 directly into ret i32 50
    assert "ret i32 50" in opt_ir
    assert "alloca" not in opt_ir
