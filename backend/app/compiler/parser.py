from typing import Any, List, Optional
from lark import Lark, Transformer, v_args, Token
from lark.exceptions import LarkError, UnexpectedToken, UnexpectedCharacters, UnexpectedEOF

from .grammar import MINILANG_GRAMMAR
from .ast_nodes import (
    Program, FunctionDef, Param, Block, Stmt, VarDecl, AssignStmt,
    IfStmt, WhileStmt, ReturnStmt, ExprStmt, Expr, BinaryOp, UnaryOp,
    IntLiteral, BoolLiteral, VarRef, CallExpr
)
from .diagnostics import SourceLocation, CompilerError

def _loc_from_meta(meta: Any) -> Optional[SourceLocation]:
    if meta is None or not hasattr(meta, "line"):
        return None
    return SourceLocation(
        line=meta.line,
        column=meta.column,
        end_line=getattr(meta, "end_line", meta.line),
        end_column=getattr(meta, "end_column", meta.column),
    )

class ASTBuilder(Transformer):
    def program(self, items: List[FunctionDef]) -> Program:
        return Program(functions=items)

    @v_args(meta=True)
    def function_def(self, meta: Any, items: List[Any]) -> FunctionDef:
        name_tok = items[0]
        params = items[1] if len(items) == 4 and items[1] is not None else []
        ret_type = items[2] if len(items) == 4 else items[1]
        body = items[3] if len(items) == 4 else items[2]
        return FunctionDef(
            name=str(name_tok),
            params=params or [],
            return_type=str(ret_type),
            body=body,
            location=_loc_from_meta(meta)
        )

    def param_list(self, items: List[Param]) -> List[Param]:
        return items

    @v_args(meta=True)
    def param(self, meta: Any, items: List[Any]) -> Param:
        return Param(name=str(items[0]), type_name=str(items[1]), location=_loc_from_meta(meta))

    def type_i32(self, _) -> str:
        return "i32"

    def type_bool(self, _) -> str:
        return "bool"

    @v_args(meta=True)
    def block(self, meta: Any, items: List[Stmt]) -> Block:
        return Block(statements=items, location=_loc_from_meta(meta))

    def statement(self, items: List[Any]) -> Stmt:
        return items[0]

    @v_args(meta=True)
    def var_decl(self, meta: Any, items: List[Any]) -> VarDecl:
        return VarDecl(
            name=str(items[0]),
            type_name=str(items[1]),
            init=items[2],
            location=_loc_from_meta(meta)
        )

    @v_args(meta=True)
    def assign_stmt(self, meta: Any, items: List[Any]) -> AssignStmt:
        return AssignStmt(
            target=str(items[0]),
            value=items[1],
            location=_loc_from_meta(meta)
        )

    @v_args(meta=True)
    def if_stmt(self, meta: Any, items: List[Any]) -> IfStmt:
        cond = items[0]
        then_b = items[1]
        else_b = None
        if len(items) > 2 and items[2] is not None:
            if isinstance(items[2], IfStmt):
                else_b = Block(statements=[items[2]], location=items[2].location)
            else:
                else_b = items[2]
        return IfStmt(condition=cond, then_branch=then_b, else_branch=else_b, location=_loc_from_meta(meta))

    @v_args(meta=True)
    def while_stmt(self, meta: Any, items: List[Any]) -> WhileStmt:
        return WhileStmt(condition=items[0], body=items[1], location=_loc_from_meta(meta))

    @v_args(meta=True)
    def return_stmt(self, meta: Any, items: List[Any]) -> ReturnStmt:
        val = items[0] if items and items[0] is not None else None
        return ReturnStmt(value=val, location=_loc_from_meta(meta))

    @v_args(meta=True)
    def expr_stmt(self, meta: Any, items: List[Any]) -> ExprStmt:
        return ExprStmt(expr=items[0], location=_loc_from_meta(meta))

    @v_args(meta=True)
    def binary_op(self, meta: Any, items: List[Any]) -> BinaryOp:
        left = items[0]
        op = str(items[1])
        right = items[2]
        return BinaryOp(left=left, op=op, right=right, location=_loc_from_meta(meta))

    @v_args(meta=True)
    def or_op(self, meta: Any, items: List[Any]) -> BinaryOp:
        return BinaryOp(left=items[0], op="||", right=items[1], location=_loc_from_meta(meta))

    @v_args(meta=True)
    def and_op(self, meta: Any, items: List[Any]) -> BinaryOp:
        return BinaryOp(left=items[0], op="&&", right=items[1], location=_loc_from_meta(meta))

    @v_args(meta=True)
    def neg(self, meta: Any, items: List[Any]) -> UnaryOp:
        return UnaryOp(op="-", operand=items[0], location=_loc_from_meta(meta))

    @v_args(meta=True)
    def not_op(self, meta: Any, items: List[Any]) -> UnaryOp:
        return UnaryOp(op="!", operand=items[0], location=_loc_from_meta(meta))

    @v_args(meta=True)
    def int_lit(self, meta: Any, items: List[Any]) -> IntLiteral:
        return IntLiteral(value=int(items[0]), location=_loc_from_meta(meta))

    @v_args(meta=True)
    def true_lit(self, meta: Any, _) -> BoolLiteral:
        return BoolLiteral(value=True, location=_loc_from_meta(meta))

    @v_args(meta=True)
    def false_lit(self, meta: Any, _) -> BoolLiteral:
        return BoolLiteral(value=False, location=_loc_from_meta(meta))

    @v_args(meta=True)
    def var_ref(self, meta: Any, items: List[Any]) -> VarRef:
        return VarRef(name=str(items[0]), location=_loc_from_meta(meta))

    @v_args(meta=True)
    def call_expr(self, meta: Any, items: List[Any]) -> CallExpr:
        callee = str(items[0])
        args = items[1] if len(items) > 1 and items[1] is not None else []
        return CallExpr(callee=callee, args=args or [], location=_loc_from_meta(meta))

    def arg_list(self, items: List[Expr]) -> List[Expr]:
        return items

_lark_parser = Lark(MINILANG_GRAMMAR, parser="lalr", propagate_positions=True)

def parse_source(source: str) -> Program:
    try:
        tree = _lark_parser.parse(source)
        ast = ASTBuilder().transform(tree)
        return ast
    except UnexpectedToken as ut:
        loc = SourceLocation(line=ut.line, column=ut.column)
        msg = f"Unexpected token '{ut.token}' at line {ut.line}, column {ut.column}. Expected one of: {list(ut.expected)[:5]}"
        raise CompilerError(message=msg, stage="frontend", code="ERR_SYNTAX", location=loc)
    except UnexpectedCharacters as uc:
        loc = SourceLocation(line=uc.line, column=uc.column)
        msg = f"Unexpected character '{uc.char}' at line {uc.line}, column {uc.column}"
        raise CompilerError(message=msg, stage="frontend", code="ERR_LEXICAL", location=loc)
    except UnexpectedEOF as ue:
        loc = SourceLocation(line=ue.line, column=ue.column)
        msg = f"Unexpected end of file at line {ue.line}, column {ue.column}"
        raise CompilerError(message=msg, stage="frontend", code="ERR_SYNTAX_EOF", location=loc)
    except LarkError as le:
        raise CompilerError(message=str(le), stage="frontend", code="ERR_PARSE")
