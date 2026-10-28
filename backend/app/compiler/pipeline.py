import base64
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .parser import parse_source
from .semantic import analyze_semantics
from .ir_generator import generate_ir
from .verifier import verify_llvm_ir
from .optimizer import optimize_llvm_ir
from .wasm_codegen import emit_wasm_binary
from .wasm_validator import validate_and_disassemble
from .runtime import execute_wasm
from .diagnostics import (
    Diagnostic, DiagnosticSeverity, StageStatus, StageMetric,
    CompilerError, SourceLocation
)

@dataclass
class CompilationResult:
    success: bool
    filename: str
    optimization_level: str
    diagnostics: List[Diagnostic] = field(default_factory=list)
    stage_metrics: List[StageMetric] = field(default_factory=list)
    total_duration_ms: float = 0.0

    # Intermediate and final representations
    ast_tree: Optional[Dict[str, Any]] = None
    raw_ir: Optional[str] = None
    optimized_ir: Optional[str] = None
    wat: Optional[str] = None
    wasm_base64: Optional[str] = None
    wasm_size_bytes: int = 0

    # Optimization metrics
    optimization_metrics: Optional[Dict[str, Any]] = None

    # Runtime result
    runtime_result: Optional[Dict[str, Any]] = None
    compiler_logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "filename": self.filename,
            "optimization_level": self.optimization_level,
            "total_duration_ms": round(self.total_duration_ms, 3),
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "stage_metrics": [m.to_dict() for m in self.stage_metrics],
            "ast_tree": self.ast_tree,
            "raw_ir": self.raw_ir,
            "optimized_ir": self.optimized_ir,
            "wat": self.wat,
            "wasm_base64": self.wasm_base64,
            "wasm_size_bytes": self.wasm_size_bytes,
            "optimization_metrics": self.optimization_metrics,
            "runtime_result": self.runtime_result,
            "compiler_logs": self.compiler_logs,
        }

class CompilerPipeline:
    def __init__(self):
        self.logs: List[str] = []
        self.metrics: List[StageMetric] = []
        self.diagnostics: List[Diagnostic] = []

    def _log(self, msg: str):
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def run(
        self,
        source: str,
        filename: str = "main.mini",
        optimization_level: str = "O2",
        execute: bool = True
    ) -> CompilationResult:
        pipeline_start = time.perf_counter()
        self.logs = []
        self.metrics = []
        self.diagnostics = []

        self._log(f"Starting compilation of '{filename}' with optimization level {optimization_level}")

        stages = [
            "frontend", "semantic", "ir_generation", "llvm_verification",
            "optimization", "wasm_codegen", "wasm_validation", "runtime"
        ]

        stage_status_map: Dict[str, StageStatus] = {s: StageStatus.WAITING for s in stages}
        stage_times: Dict[str, float] = {s: 0.0 for s in stages}

        ast_tree = None
        raw_ir = None
        optimized_ir = None
        opt_metrics = None
        wasm_bytes = None
        wasm_size = 0
        wat = None
        runtime_res = None
        failed_stage = None

        try:
            # Stage 1: Frontend (Lexing and Parsing)
            t0 = time.perf_counter()
            stage_status_map["frontend"] = StageStatus.RUNNING
            self._log("Running Stage 1: Lexical analysis and parsing...")
            prog = parse_source(source)
            ast_tree = prog.to_dict()
            stage_times["frontend"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["frontend"] = StageStatus.SUCCESS
            self._log(f"Parsing complete ({stage_times['frontend']:.2f} ms). AST generated.")

            # Stage 2: Semantic Analysis
            t0 = time.perf_counter()
            stage_status_map["semantic"] = StageStatus.RUNNING
            self._log("Running Stage 2: Semantic analysis and type checking...")
            sem_diags = analyze_semantics(prog)
            self.diagnostics.extend(sem_diags)
            stage_times["semantic"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["semantic"] = StageStatus.SUCCESS
            self._log(f"Semantic analysis complete ({stage_times['semantic']:.2f} ms). No errors.")

            # Stage 3: LLVM IR Generation
            t0 = time.perf_counter()
            stage_status_map["ir_generation"] = StageStatus.RUNNING
            self._log("Running Stage 3: LLVM IR generation...")
            raw_ir = generate_ir(prog)
            stage_times["ir_generation"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["ir_generation"] = StageStatus.SUCCESS
            self._log(f"LLVM IR generated ({stage_times['ir_generation']:.2f} ms).")

            # Stage 4: LLVM Verification
            t0 = time.perf_counter()
            stage_status_map["llvm_verification"] = StageStatus.RUNNING
            self._log("Running Stage 4: Verifying LLVM IR...")
            verify_llvm_ir(raw_ir)
            stage_times["llvm_verification"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["llvm_verification"] = StageStatus.SUCCESS
            self._log(f"LLVM IR verified successfully ({stage_times['llvm_verification']:.2f} ms).")

            # Stage 5: Optimization
            t0 = time.perf_counter()
            stage_status_map["optimization"] = StageStatus.RUNNING
            self._log(f"Running Stage 5: Applying LLVM {optimization_level} optimization passes...")
            optimized_ir, opt_metrics = optimize_llvm_ir(raw_ir, level=optimization_level)
            stage_times["optimization"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["optimization"] = StageStatus.SUCCESS
            self._log(f"LLVM {optimization_level} complete ({stage_times['optimization']:.2f} ms). Instructions: {opt_metrics['initial_instructions']} -> {opt_metrics['optimized_instructions']}.")

            # Stage 6: WebAssembly Code Generation
            t0 = time.perf_counter()
            stage_status_map["wasm_codegen"] = StageStatus.RUNNING
            self._log("Running Stage 6: LLVM WebAssembly target code generation...")
            wasm_bytes, wasm_size = emit_wasm_binary(optimized_ir, optimization_level=optimization_level)
            stage_times["wasm_codegen"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["wasm_codegen"] = StageStatus.SUCCESS
            self._log(f"WASM binary generated ({stage_times['wasm_codegen']:.2f} ms): {wasm_size} bytes.")

            # Stage 7: WebAssembly Validation & WAT Disassembly
            t0 = time.perf_counter()
            stage_status_map["wasm_validation"] = StageStatus.RUNNING
            self._log("Running Stage 7: WABT module specification validation & disassembly...")
            _, wat = validate_and_disassemble(wasm_bytes)
            stage_times["wasm_validation"] = (time.perf_counter() - t0) * 1000.0
            stage_status_map["wasm_validation"] = StageStatus.SUCCESS
            self._log(f"Module validation succeeded ({stage_times['wasm_validation']:.2f} ms). WAT generated.")

            # Stage 8: Runtime Execution
            if execute:
                t0 = time.perf_counter()
                stage_status_map["runtime"] = StageStatus.RUNNING
                self._log("Running Stage 8: WebAssembly execution runtime (wasmtime)...")
                runtime_res = execute_wasm(wasm_bytes)
                stage_times["runtime"] = (time.perf_counter() - t0) * 1000.0
                stage_status_map["runtime"] = StageStatus.SUCCESS
                ret_val = runtime_res.get("return_value")
                self._log(f"Execution completed ({stage_times['runtime']:.2f} ms). Returned: {ret_val}.")
            else:
                stage_status_map["runtime"] = StageStatus.SKIPPED

        except CompilerError as ce:
            failed_stage = ce.stage
            diag = ce.to_diagnostic()
            self.diagnostics.append(diag)
            self._log(f"ERROR in stage '{ce.stage}': {ce.message}")
            stage_status_map[failed_stage] = StageStatus.FAILED
            # Mark all following stages as SKIPPED
            passed = False
            for s in stages:
                if s == failed_stage:
                    passed = True
                elif passed:
                    stage_status_map[s] = StageStatus.SKIPPED
        except Exception as ex:
            failed_stage = "compiler"
            self.diagnostics.append(Diagnostic(
                stage="compiler",
                message=str(ex),
                severity=DiagnosticSeverity.ERROR,
                code="ERR_INTERNAL"
            ))
            self._log(f"FATAL ERROR: {str(ex)}")

        # Build StageMetric list
        for s in stages:
            self.metrics.append(StageMetric(
                name=s,
                status=stage_status_map[s],
                duration_ms=stage_times[s],
            ))

        total_duration = (time.perf_counter() - pipeline_start) * 1000.0
        success = failed_stage is None and all(d.severity != DiagnosticSeverity.ERROR for d in self.diagnostics)

        wasm_b64 = base64.b64encode(wasm_bytes).decode("ascii") if wasm_bytes else None

        return CompilationResult(
            success=success,
            filename=filename,
            optimization_level=optimization_level,
            diagnostics=self.diagnostics,
            stage_metrics=self.metrics,
            total_duration_ms=total_duration,
            ast_tree=ast_tree,
            raw_ir=raw_ir,
            optimized_ir=optimized_ir,
            wat=wat,
            wasm_base64=wasm_b64,
            wasm_size_bytes=wasm_size,
            optimization_metrics=opt_metrics,
            runtime_result=runtime_res,
            compiler_logs=self.logs,
        )
