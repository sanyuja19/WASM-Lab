from typing import Tuple, Dict, Any, List
import llvmlite.binding as llvm
from .diagnostics import CompilerError

def _count_instructions(ir_text: str) -> int:
    count = 0
    for line in ir_text.splitlines():
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("define") or line.startswith("}") or line.endswith(":") or line.startswith("target"):
            continue
        count += 1
    return count

def optimize_llvm_ir(ir_text: str, level: str = "O2") -> Tuple[str, Dict[str, Any]]:
    if level not in ("O0", "O2"):
        raise CompilerError(f"Unsupported optimization level '{level}'. Supported: 'O0', 'O2'", stage="optimizer")

    try:
        llvm.initialize_all_targets()
        llvm.initialize_all_asmprinters()

        mod = llvm.parse_assembly(ir_text)
        mod.verify()

        initial_count = _count_instructions(str(mod))

        target = llvm.Target.from_triple("wasm32-unknown-unknown")
        tm = target.create_target_machine(cpu="generic", opt=2 if level == "O2" else 0)
        pto = llvm.create_pipeline_tuning_options()
        pb = llvm.create_pass_builder(tm, pto)

        mpm = llvm.create_new_module_pass_manager()
        passes: List[str] = []

        if level == "O0":
            # O0: Keep unoptimized memory allocas & linear flow for debugging
            mpm.add_verifier()
            passes = ["ModuleVerifier"]
            mpm.run(mod, pb)
        else:
            # O2: SROA/mem2reg, instcombine, sccp constant propagation, DCE, simplifycfg
            mpm.add_sroa_pass()
            mpm.add_sccp_pass()
            mpm.add_instruction_combine_pass()
            mpm.add_dead_code_elimination_pass()
            mpm.add_simplify_cfg_pass()
            mpm.add_verifier()

            passes = [
                "ScalarReplacementOfAggregates (SROA/mem2reg)",
                "SparseConditionalConstantPropagation (SCCP)",
                "InstructionCombining (InstCombine)",
                "DeadCodeElimination (DCE)",
                "SimplifyControlFlowGraph (SimplifyCFG)",
                "ModuleVerifier"
            ]
            mpm.run(mod, pb)

        optimized_ir = str(mod)
        optimized_count = _count_instructions(optimized_ir)
        diff = initial_count - optimized_count

        metrics: Dict[str, Any] = {
            "level": level,
            "initial_instructions": initial_count,
            "optimized_instructions": optimized_count,
            "instructions_eliminated": max(0, diff),
            "passes_applied": passes,
        }

        return optimized_ir, metrics

    except Exception as e:
        raise CompilerError(
            message=f"LLVM optimization ({level}) failed: {str(e)}",
            stage="optimizer",
            code="ERR_LLVM_OPT"
        )
