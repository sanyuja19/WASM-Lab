from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .ast_nodes import (
    Program, FunctionDef, Param, Block, Stmt, VarDecl, AssignStmt,
    IfStmt, WhileStmt, ReturnStmt, ExprStmt, Expr, BinaryOp, UnaryOp,
    IntLiteral, BoolLiteral, VarRef, CallExpr
)
from .diagnostics import SourceLocation, CompilerError, Diagnostic, DiagnosticSeverity

@dataclass
class Symbol:
    name: str
    type_name: str
    is_function: bool = False
    param_types: List[str] = field(default_factory=list)
    location: Optional[SourceLocation] = None

class Scope:
    def __init__(self, parent: Optional["Scope"] = None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def resolve(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []
        self.current_function: Optional[FunctionDef] = None
        self.global_functions: Dict[str, Symbol] = {}

    def _error(self, message: str, code: str, location: Optional[SourceLocation]):
        diag = Diagnostic(
            stage="semantic",
            message=message,
            severity=DiagnosticSeverity.ERROR,
            code=code,
            location=location,
        )
        self.diagnostics.append(diag)

    def analyze(self, program: Program) -> List[Diagnostic]:
        self.diagnostics = []
        self.global_functions = {}

        # First pass: collect function signatures
        for fn in program.functions:
            if fn.name in self.global_functions:
                self._error(
                    f"Duplicate function definition '{fn.name}'",
                    "ERR_DUPLICATE_FN",
                    fn.location
                )
            else:
                param_types = [p.type_name for p in fn.params]
                fn_sym = Symbol(
                    name=fn.name,
                    type_name=fn.return_type,
                    is_function=True,
                    param_types=param_types,
                    location=fn.location
                )
                self.global_functions[fn.name] = fn_sym

        # Second pass: check function bodies
        for fn in program.functions:
            self._analyze_function(fn)

        if self.diagnostics:
            # Raise the first fatal error as CompilerError
            first = self.diagnostics[0]
            raise CompilerError(
                message=first.message,
                stage="semantic",
                code=first.code,
                location=first.location
            )

        return self.diagnostics

    def _analyze_function(self, fn: FunctionDef):
        self.current_function = fn
        func_scope = Scope()

        # Check parameter uniqueness
        seen_params: Set[str] = set()
        for param in fn.params:
            if param.name in seen_params:
                self._error(
                    f"Duplicate parameter name '{param.name}' in function '{fn.name}'",
                    "ERR_DUPLICATE_PARAM",
                    param.location
                )
            seen_params.add(param.name)
            func_scope.define(Symbol(
                name=param.name,
                type_name=param.type_name,
                location=param.location
            ))

        # Analyze body
        returns = self._analyze_block(fn.body, func_scope)

        # Check missing return
        if not returns and fn.return_type != "void":
            self._error(
                f"Missing return statement in function '{fn.name}' of return type '{fn.return_type}'",
                "ERR_MISSING_RETURN",
                fn.location
            )

        self.current_function = None

    def _analyze_block(self, block: Block, parent_scope: Scope) -> bool:
        scope = Scope(parent_scope)
        definitely_returns = False

        for stmt in block.statements:
            if definitely_returns:
                # Any statement after unconditional return is unreachable
                pass
            res = self._analyze_statement(stmt, scope)
            if res:
                definitely_returns = True

        return definitely_returns

    def _analyze_statement(self, stmt: Stmt, scope: Scope) -> bool:
        if isinstance(stmt, VarDecl):
            if stmt.name in scope.symbols:
                self._error(
                    f"Duplicate variable declaration '{stmt.name}' in the same scope",
                    "ERR_DUPLICATE_VAR",
                    stmt.location
                )
            init_type = self._analyze_expr(stmt.init, scope)
            if init_type is not None and init_type != stmt.type_name:
                self._error(
                    f"Type mismatch: cannot assign value of type '{init_type}' to variable '{stmt.name}' of type '{stmt.type_name}'",
                    "ERR_TYPE_MISMATCH",
                    stmt.location
                )
            scope.define(Symbol(name=stmt.name, type_name=stmt.type_name, location=stmt.location))
            return False

        elif isinstance(stmt, AssignStmt):
            sym = scope.resolve(stmt.target)
            if not sym or sym.is_function:
                self._error(
                    f"Assignment to undeclared variable '{stmt.target}'",
                    "ERR_UNDECLARED_VAR",
                    stmt.location
                )
            else:
                val_type = self._analyze_expr(stmt.value, scope)
                if val_type is not None and val_type != sym.type_name:
                    self._error(
                        f"Type mismatch: cannot assign value of type '{val_type}' to variable '{stmt.target}' of type '{sym.type_name}'",
                        "ERR_TYPE_MISMATCH",
                        stmt.location
                    )
            return False

        elif isinstance(stmt, ReturnStmt):
            if self.current_function is None:
                self._error("Return statement outside function", "ERR_INVALID_RETURN", stmt.location)
                return True

            expected_type = self.current_function.return_type
            if stmt.value is None:
                if expected_type != "void":
                    self._error(
                        f"Function '{self.current_function.name}' expects return type '{expected_type}', but return is empty",
                        "ERR_RETURN_TYPE",
                        stmt.location
                    )
            else:
                act_type = self._analyze_expr(stmt.value, scope)
                if act_type is not None and act_type != expected_type:
                    self._error(
                        f"Function '{self.current_function.name}' expects return type '{expected_type}', got '{act_type}'",
                        "ERR_RETURN_TYPE",
                        stmt.location
                    )
            return True

        elif isinstance(stmt, IfStmt):
            cond_type = self._analyze_expr(stmt.condition, scope)
            if cond_type is not None and cond_type != "bool":
                self._error(
                    f"If condition must be 'bool', got '{cond_type}'",
                    "ERR_TYPE_MISMATCH",
                    stmt.condition.location or stmt.location
                )
            then_returns = self._analyze_block(stmt.then_branch, scope)
            else_returns = False
            if stmt.else_branch is not None:
                else_returns = self._analyze_block(stmt.else_branch, scope)
            return then_returns and else_returns

        elif isinstance(stmt, WhileStmt):
            cond_type = self._analyze_expr(stmt.condition, scope)
            if cond_type is not None and cond_type != "bool":
                self._error(
                    f"While condition must be 'bool', got '{cond_type}'",
                    "ERR_TYPE_MISMATCH",
                    stmt.condition.location or stmt.location
                )
            self._analyze_block(stmt.body, scope)
            return False

        elif isinstance(stmt, ExprStmt):
            self._analyze_expr(stmt.expr, scope)
            return False

        elif isinstance(stmt, Block):
            return self._analyze_block(stmt, scope)

        return False

    def _analyze_expr(self, expr: Expr, scope: Scope) -> Optional[str]:
        if isinstance(expr, IntLiteral):
            return "i32"

        elif isinstance(expr, BoolLiteral):
            return "bool"

        elif isinstance(expr, VarRef):
            sym = scope.resolve(expr.name)
            if not sym or sym.is_function:
                self._error(
                    f"Use of undeclared variable '{expr.name}'",
                    "ERR_UNDECLARED_VAR",
                    expr.location
                )
                return None
            return sym.type_name

        elif isinstance(expr, UnaryOp):
            op_type = self._analyze_expr(expr.operand, scope)
            if op_type is None:
                return None
            if expr.op == "-":
                if op_type != "i32":
                    self._error(
                        f"Unary operator '-' requires 'i32', got '{op_type}'",
                        "ERR_TYPE_MISMATCH",
                        expr.location
                    )
                    return None
                return "i32"
            elif expr.op == "!":
                if op_type != "bool":
                    self._error(
                        f"Unary operator '!' requires 'bool', got '{op_type}'",
                        "ERR_TYPE_MISMATCH",
                        expr.location
                    )
                    return None
                return "bool"

        elif isinstance(expr, BinaryOp):
            l_type = self._analyze_expr(expr.left, scope)
            r_type = self._analyze_expr(expr.right, scope)
            if l_type is None or r_type is None:
                return None

            arith_ops = {"+", "-", "*", "/", "%"}
            comp_ops = {"<", "<=", ">", ">="}
            eq_ops = {"==", "!="}
            logic_ops = {"&&", "||"}

            if expr.op in arith_ops:
                if l_type != "i32" or r_type != "i32":
                    self._error(
                        f"Operator '{expr.op}' requires 'i32' operands, got '{l_type}' and '{r_type}'",
                        "ERR_TYPE_MISMATCH",
                        expr.location
                    )
                    return None
                return "i32"

            elif expr.op in comp_ops:
                if l_type != "i32" or r_type != "i32":
                    self._error(
                        f"Comparison operator '{expr.op}' requires 'i32' operands, got '{l_type}' and '{r_type}'",
                        "ERR_TYPE_MISMATCH",
                        expr.location
                    )
                    return None
                return "bool"

            elif expr.op in eq_ops:
                if l_type != r_type:
                    self._error(
                        f"Equality operator '{expr.op}' requires matching operand types, got '{l_type}' and '{r_type}'",
                        "ERR_TYPE_MISMATCH",
                        expr.location
                    )
                    return None
                return "bool"

            elif expr.op in logic_ops:
                if l_type != "bool" or r_type != "bool":
                    self._error(
                        f"Logical operator '{expr.op}' requires 'bool' operands, got '{l_type}' and '{r_type}'",
                        "ERR_TYPE_MISMATCH",
                        expr.location
                    )
                    return None
                return "bool"

        elif isinstance(expr, CallExpr):
            if expr.callee not in self.global_functions:
                self._error(
                    f"Call to undefined function '{expr.callee}'",
                    "ERR_UNDEFINED_FN",
                    expr.location
                )
                return None

            fn_sym = self.global_functions[expr.callee]
            expected_count = len(fn_sym.param_types)
            actual_count = len(expr.args)
            if expected_count != actual_count:
                self._error(
                    f"Function '{expr.callee}' expects {expected_count} arguments, got {actual_count}",
                    "ERR_ARG_COUNT",
                    expr.location
                )
                return fn_sym.type_name

            for i, (arg, exp_type) in enumerate(zip(expr.args, fn_sym.param_types)):
                arg_type = self._analyze_expr(arg, scope)
                if arg_type is not None and arg_type != exp_type:
                    self._error(
                        f"Argument {i+1} of '{expr.callee}' expects '{exp_type}', got '{arg_type}'",
                        "ERR_ARG_TYPE",
                        arg.location or expr.location
                    )

            return fn_sym.type_name

        return None

def analyze_semantics(program: Program) -> List[Diagnostic]:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)
