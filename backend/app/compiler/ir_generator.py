from typing import Dict, List, Optional
import llvmlite.ir as ir

from .ast_nodes import (
    Program, FunctionDef, Param, Block, Stmt, VarDecl, AssignStmt,
    IfStmt, WhileStmt, ReturnStmt, ExprStmt, Expr, BinaryOp, UnaryOp,
    IntLiteral, BoolLiteral, VarRef, CallExpr
)
from .diagnostics import CompilerError
from ..config import settings

class IRGenerator:
    def __init__(self):
        self.i32 = ir.IntType(32)
        self.i1 = ir.IntType(1)
        self.void = ir.VoidType()
        self.module = ir.Module(name="minilang")
        self.module.triple = settings.TARGET_TRIPLE
        self.module.data_layout = settings.DATA_LAYOUT

        self.functions: Dict[str, ir.Function] = {}
        self.current_function: Optional[ir.Function] = None
        self.builder: Optional[ir.IRBuilder] = None
        self.scopes: List[Dict[str, ir.AllocaInstr]] = []

    def _get_type(self, type_name: str) -> ir.Type:
        if type_name == "i32":
            return self.i32
        elif type_name == "bool":
            return self.i1
        elif type_name == "void":
            return self.void
        raise CompilerError(f"Unsupported type '{type_name}' in IR generation", stage="ir_gen")

    def _push_scope(self):
        self.scopes.append({})

    def _pop_scope(self):
        self.scopes.pop()

    def _declare_var(self, name: str, alloca: ir.AllocaInstr):
        self.scopes[-1][name] = alloca

    def _lookup_var(self, name: str) -> ir.AllocaInstr:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise CompilerError(f"Variable '{name}' not found during IR emission", stage="ir_gen")

    def generate(self, program: Program) -> str:
        # First pass: declare all functions
        for fn in program.functions:
            ret_type = self._get_type(fn.return_type)
            param_types = [self._get_type(p.type_name) for p in fn.params]
            fn_type = ir.FunctionType(ret_type, param_types)
            llvm_fn = ir.Function(self.module, fn_type, name=fn.name)
            self.functions[fn.name] = llvm_fn

        # Second pass: emit function bodies
        for fn in program.functions:
            self._emit_function(fn)

        return str(self.module)

    def _emit_function(self, fn: FunctionDef):
        llvm_fn = self.functions[fn.name]
        self.current_function = llvm_fn

        entry_block = llvm_fn.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)

        self._push_scope()

        # Allocate parameters as local variables and store their initial values
        for i, param in enumerate(fn.params):
            param_val = llvm_fn.args[i]
            param_val.name = param.name
            alloca = self.builder.alloca(self._get_type(param.type_name), name=f"{param.name}.addr")
            self.builder.store(param_val, alloca)
            self._declare_var(param.name, alloca)

        # Emit function body
        self._emit_block(fn.body)

        # Ensure termination if not already terminated
        if not self.builder.block.is_terminated:
            if fn.return_type == "i32":
                self.builder.ret(ir.Constant(self.i32, 0))
            elif fn.return_type == "bool":
                self.builder.ret(ir.Constant(self.i1, 0))
            else:
                self.builder.ret_void()

        self._pop_scope()
        self.current_function = None
        self.builder = None

    def _emit_block(self, block: Block):
        self._push_scope()
        for stmt in block.statements:
            if self.builder.block.is_terminated:
                break
            self._emit_stmt(stmt)
        self._pop_scope()

    def _emit_stmt(self, stmt: Stmt):
        if isinstance(stmt, VarDecl):
            var_type = self._get_type(stmt.type_name)
            alloca = self.builder.alloca(var_type, name=f"{stmt.name}.addr")
            init_val = self._emit_expr(stmt.init)
            self.builder.store(init_val, alloca)
            self._declare_var(stmt.name, alloca)

        elif isinstance(stmt, AssignStmt):
            alloca = self._lookup_var(stmt.target)
            val = self._emit_expr(stmt.value)
            self.builder.store(val, alloca)

        elif isinstance(stmt, ReturnStmt):
            if stmt.value is not None:
                val = self._emit_expr(stmt.value)
                self.builder.ret(val)
            else:
                self.builder.ret_void()

        elif isinstance(stmt, IfStmt):
            cond_val = self._emit_expr(stmt.condition)
            then_block = self.current_function.append_basic_block(name="if.then")
            else_block = self.current_function.append_basic_block(name="if.else") if stmt.else_branch else None
            merge_block = self.current_function.append_basic_block(name="if.end")

            target_else = else_block if else_block else merge_block
            self.builder.cbranch(cond_val, then_block, target_else)

            # Then block
            self.builder.position_at_end(then_block)
            self._emit_block(stmt.then_branch)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)

            # Else block (if any)
            if stmt.else_branch:
                self.builder.position_at_end(else_block)
                self._emit_block(stmt.else_branch)
                if not self.builder.block.is_terminated:
                    self.builder.branch(merge_block)

            # Continue at merge block
            self.builder.position_at_end(merge_block)

        elif isinstance(stmt, WhileStmt):
            cond_block = self.current_function.append_basic_block(name="while.cond")
            body_block = self.current_function.append_basic_block(name="while.body")
            end_block = self.current_function.append_basic_block(name="while.end")

            self.builder.branch(cond_block)

            # Condition block
            self.builder.position_at_end(cond_block)
            cond_val = self._emit_expr(stmt.condition)
            self.builder.cbranch(cond_val, body_block, end_block)

            # Body block
            self.builder.position_at_end(body_block)
            self._emit_block(stmt.body)
            if not self.builder.block.is_terminated:
                self.builder.branch(cond_block)

            # End block
            self.builder.position_at_end(end_block)

        elif isinstance(stmt, ExprStmt):
            self._emit_expr(stmt.expr)

        elif isinstance(stmt, Block):
            self._emit_block(stmt)

    def _emit_expr(self, expr: Expr) -> ir.Value:
        if isinstance(expr, IntLiteral):
            return ir.Constant(self.i32, expr.value)

        elif isinstance(expr, BoolLiteral):
            return ir.Constant(self.i1, 1 if expr.value else 0)

        elif isinstance(expr, VarRef):
            alloca = self._lookup_var(expr.name)
            return self.builder.load(alloca, name=f"{expr.name}.val")

        elif isinstance(expr, UnaryOp):
            val = self._emit_expr(expr.operand)
            if expr.op == "-":
                return self.builder.neg(val, name="neg")
            elif expr.op == "!":
                return self.builder.not_(val, name="not")
            raise CompilerError(f"Unsupported unary operator '{expr.op}'", stage="ir_gen")

        elif isinstance(expr, BinaryOp):
            left = self._emit_expr(expr.left)
            right = self._emit_expr(expr.right)

            if expr.op == "+":
                return self.builder.add(left, right, name="add")
            elif expr.op == "-":
                return self.builder.sub(left, right, name="sub")
            elif expr.op == "*":
                return self.builder.mul(left, right, name="mul")
            elif expr.op == "/":
                return self.builder.sdiv(left, right, name="sdiv")
            elif expr.op == "%":
                return self.builder.srem(left, right, name="srem")

            # Comparisons
            elif expr.op == "<":
                return self.builder.icmp_signed("<", left, right, name="cmp.slt")
            elif expr.op == "<=":
                return self.builder.icmp_signed("<=", left, right, name="cmp.sle")
            elif expr.op == ">":
                return self.builder.icmp_signed(">", left, right, name="cmp.sgt")
            elif expr.op == ">=":
                return self.builder.icmp_signed(">=", left, right, name="cmp.sge")
            elif expr.op == "==":
                return self.builder.icmp_signed("==", left, right, name="cmp.eq")
            elif expr.op == "!=":
                return self.builder.icmp_signed("!=", left, right, name="cmp.ne")

            # Logical ops
            elif expr.op == "&&":
                return self.builder.and_(left, right, name="land")
            elif expr.op == "||":
                return self.builder.or_(left, right, name="lor")

            raise CompilerError(f"Unsupported binary operator '{expr.op}'", stage="ir_gen")

        elif isinstance(expr, CallExpr):
            callee_fn = self.functions.get(expr.callee)
            if not callee_fn:
                raise CompilerError(f"Function '{expr.callee}' not found during IR emission", stage="ir_gen")
            args = [self._emit_expr(arg) for arg in expr.args]
            return self.builder.call(callee_fn, args, name=f"call.{expr.callee}")

        raise CompilerError(f"Unsupported expression type '{type(expr)}'", stage="ir_gen")

def generate_ir(program: Program) -> str:
    gen = IRGenerator()
    return gen.generate(program)
