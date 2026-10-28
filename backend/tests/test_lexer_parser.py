import pytest
from backend.app.compiler.parser import parse_source
from backend.app.compiler.ast_nodes import (
    Program, FunctionDef, VarDecl, AssignStmt, IfStmt, WhileStmt,
    ReturnStmt, BinaryOp, UnaryOp, IntLiteral, BoolLiteral
)
from backend.app.compiler.diagnostics import CompilerError

def test_lexer_and_parser_basic_function():
    src = "fn main() -> i32 { return 42; }"
    prog = parse_source(src)
    assert isinstance(prog, Program)
    assert len(prog.functions) == 1
    fn = prog.functions[0]
    assert fn.name == "main"
    assert fn.return_type == "i32"
    assert len(fn.body.statements) == 1
    ret = fn.body.statements[0]
    assert isinstance(ret, ReturnStmt)
    assert isinstance(ret.value, IntLiteral)
    assert ret.value.value == 42

def test_operator_precedence():
    # Precedence: * has higher precedence than +
    src = "fn test() -> i32 { return 10 + 20 * 2; }"
    prog = parse_source(src)
    ret = prog.functions[0].body.statements[0]
    assert isinstance(ret.value, BinaryOp)
    assert ret.value.op == "+"
    assert isinstance(ret.value.left, IntLiteral)
    assert ret.value.left.value == 10
    assert isinstance(ret.value.right, BinaryOp)
    assert ret.value.right.op == "*"

def test_parentheses_override():
    src = "fn test() -> i32 { return (10 + 20) * 2; }"
    prog = parse_source(src)
    ret = prog.functions[0].body.statements[0]
    assert isinstance(ret.value, BinaryOp)
    assert ret.value.op == "*"
    assert isinstance(ret.value.left, BinaryOp)
    assert ret.value.left.op == "+"

def test_while_loop_and_conditionals():
    src = """
    fn loop_test(n: i32) -> i32 {
        let i: i32 = 0;
        while i < n {
            if i == 5 {
                return i;
            } else {
                i = i + 1;
            }
        }
        return 0;
    }
    """
    prog = parse_source(src)
    assert len(prog.functions) == 1
    fn = prog.functions[0]
    assert len(fn.params) == 1
    assert fn.params[0].name == "n"
    assert isinstance(fn.body.statements[1], WhileStmt)

def test_source_locations_tracked():
    src = "fn foo() -> i32 {\n    let x: i32 = 10;\n    return x;\n}"
    prog = parse_source(src)
    decl = prog.functions[0].body.statements[0]
    assert decl.location is not None
    assert decl.location.line == 2

def test_syntax_error_reported():
    bad_src = "fn broken( { return 10; }"
    with pytest.raises(CompilerError) as exc_info:
        parse_source(bad_src)
    assert exc_info.value.stage == "frontend"
    assert exc_info.value.location is not None
