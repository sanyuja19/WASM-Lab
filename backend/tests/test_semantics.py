import pytest
from backend.app.compiler.parser import parse_source
from backend.app.compiler.semantic import analyze_semantics
from backend.app.compiler.diagnostics import CompilerError

def test_valid_program_passes_semantics():
    src = """
    fn add(a: i32, b: i32) -> i32 {
        return a + b;
    }
    fn main() -> i32 {
        let x: i32 = 10;
        return add(x, 20);
    }
    """
    prog = parse_source(src)
    diags = analyze_semantics(prog)
    assert len(diags) == 0

def test_duplicate_variable_in_same_scope():
    src = """
    fn test() -> i32 {
        let x: i32 = 10;
        let x: i32 = 20;
        return x;
    }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_DUPLICATE_VAR"
    assert "Duplicate variable declaration 'x'" in exc_info.value.message

def test_undeclared_variable_error():
    src = "fn test() -> i32 { return unknown_variable; }"
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_UNDECLARED_VAR"

def test_type_mismatch_assignment():
    src = """
    fn test() -> i32 {
        let x: i32 = true;
        return 0;
    }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_TYPE_MISMATCH"

def test_type_mismatch_arithmetic():
    src = """
    fn test() -> i32 {
        let a: i32 = 10;
        let b: bool = true;
        let c: i32 = a + b;
        return c;
    }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_TYPE_MISMATCH"

def test_wrong_function_argument_count():
    src = """
    fn foo(a: i32, b: i32) -> i32 { return a + b; }
    fn main() -> i32 { return foo(1); }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_ARG_COUNT"

def test_wrong_function_argument_type():
    src = """
    fn foo(a: i32) -> i32 { return a; }
    fn main() -> i32 { return foo(true); }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_ARG_TYPE"

def test_missing_return_in_function():
    src = """
    fn no_return() -> i32 {
        let x: i32 = 10;
    }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_MISSING_RETURN"

def test_scope_isolation_inner_block():
    src = """
    fn scope_test() -> i32 {
        if true {
            let inner: i32 = 42;
        }
        return inner;
    }
    """
    with pytest.raises(CompilerError) as exc_info:
        analyze_semantics(parse_source(src))
    assert exc_info.value.code == "ERR_UNDECLARED_VAR"
