import llvmlite.binding as llvm
from .diagnostics import CompilerError

def verify_llvm_ir(ir_text: str) -> llvm.ModuleRef:
    try:
        mod = llvm.parse_assembly(ir_text)
        mod.verify()
        return mod
    except Exception as e:
        raise CompilerError(
            message=f"LLVM IR verification failed: {str(e)}",
            stage="verifier",
            code="ERR_LLVM_VERIFY"
        )
