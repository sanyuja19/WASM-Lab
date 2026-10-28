from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from .diagnostics import SourceLocation

@dataclass
class ASTNode:
    location: Optional[SourceLocation] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {"node_type": self.__class__.__name__}
        if self.location:
            res["location"] = self.location.to_dict()
        for k, v in self.__dict__.items():
            if k == "location":
                continue
            if isinstance(v, ASTNode):
                res[k] = v.to_dict()
            elif isinstance(v, list):
                res[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                res[k] = v
        return res

@dataclass
class Expr(ASTNode):
    pass

@dataclass
class IntLiteral(Expr):
    value: int = 0

@dataclass
class BoolLiteral(Expr):
    value: bool = False

@dataclass
class VarRef(Expr):
    name: str = ""

@dataclass
class BinaryOp(Expr):
    left: Expr = field(default_factory=Expr)
    op: str = ""
    right: Expr = field(default_factory=Expr)

@dataclass
class UnaryOp(Expr):
    op: str = ""
    operand: Expr = field(default_factory=Expr)

@dataclass
class CallExpr(Expr):
    callee: str = ""
    args: List[Expr] = field(default_factory=list)

@dataclass
class Stmt(ASTNode):
    pass

@dataclass
class VarDecl(Stmt):
    name: str = ""
    type_name: str = "i32"
    init: Expr = field(default_factory=Expr)

@dataclass
class AssignStmt(Stmt):
    target: str = ""
    value: Expr = field(default_factory=Expr)

@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr] = None

@dataclass
class Block(Stmt):
    statements: List[Stmt] = field(default_factory=list)

@dataclass
class IfStmt(Stmt):
    condition: Expr = field(default_factory=Expr)
    then_branch: Block = field(default_factory=Block)
    else_branch: Optional[Block] = None

@dataclass
class WhileStmt(Stmt):
    condition: Expr = field(default_factory=Expr)
    body: Block = field(default_factory=Block)

@dataclass
class ExprStmt(Stmt):
    expr: Expr = field(default_factory=Expr)

@dataclass
class Param(ASTNode):
    name: str = ""
    type_name: str = "i32"

@dataclass
class FunctionDef(ASTNode):
    name: str = ""
    params: List[Param] = field(default_factory=list)
    return_type: str = "i32"
    body: Block = field(default_factory=Block)

@dataclass
class Program(ASTNode):
    functions: List[FunctionDef] = field(default_factory=list)
