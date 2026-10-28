from backend.app.compiler.parser import parse_source
from backend.app.compiler.semantic import analyze_semantics
from backend.app.compiler.ir_generator import generate_ir
from backend.app.compiler.verifier import verify_llvm_ir

def test_ir_generation_and_verification_arithmetic():
    src = "fn main() -> i32 { return 10 + 20 * 2; }"
    prog = parse_source(src)
    analyze_semantics(prog)
    ir_text = generate_ir(prog)
    assert 'target triple = "wasm32-unknown-unknown"' in ir_text
    assert 'define i32 @"main"()' in ir_text
    assert 'mul i32' in ir_text
    assert 'add i32' in ir_text

    # Verify IR with LLVM verifier
    mod = verify_llvm_ir(ir_text)
    assert mod is not None

def test_ir_generation_control_flow():
    src = """
    fn max(a: i32, b: i32) -> i32 {
        if a > b {
            return a;
        } else {
            return b;
        }
    }
    """
    prog = parse_source(src)
    analyze_semantics(prog)
    ir_text = generate_ir(prog)
    assert "icmp sgt" in ir_text
    assert "if.then:" in ir_text
    assert "if.else:" in ir_text
    verify_llvm_ir(ir_text)

def test_ir_generation_while_loop():
    src = """
    fn count(n: i32) -> i32 {
        let i: i32 = 0;
        while i < n {
            i = i + 1;
        }
        return i;
    }
    """
    prog = parse_source(src)
    analyze_semantics(prog)
    ir_text = generate_ir(prog)
    assert "while.cond:" in ir_text
    assert "while.body:" in ir_text
    assert "while.end:" in ir_text
    verify_llvm_ir(ir_text)
