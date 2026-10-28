import difflib
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..compiler.pipeline import CompilerPipeline, CompilationResult
from ..compiler.runtime import execute_wasm
from ..schemas.requests import CompileRequest, CompareRequest, RunRequest
from ..schemas.responses import (
    CompileResponse, CompareResponse, ExampleProgram,
    CompilerInfoResponse, HealthResponse
)
from ..config import settings, WORKSPACE_ROOT
import llvmlite.binding as llvm
import subprocess

class CompilationService:
    def __init__(self):
        self.pipeline = CompilerPipeline()

    def compile(self, req: CompileRequest) -> CompileResponse:
        res: CompilationResult = self.pipeline.run(
            source=req.source,
            filename=req.filename,
            optimization_level=req.optimization,
            execute=req.execute
        )
        return CompileResponse(**res.to_dict())

    def compare(self, req: CompareRequest) -> CompareResponse:
        # Run O0
        res_o0: CompilationResult = self.pipeline.run(
            source=req.source,
            filename=req.filename,
            optimization_level="O0",
            execute=True
        )
        # Run O2
        res_o2: CompilationResult = self.pipeline.run(
            source=req.source,
            filename=req.filename,
            optimization_level="O2",
            execute=True
        )

        # Generate line-based unified diff between O0 and O2 IR
        ir_diff = None
        if res_o0.optimized_ir and res_o2.optimized_ir:
            diff_lines = list(difflib.unified_diff(
                res_o0.optimized_ir.splitlines(keepends=True),
                res_o2.optimized_ir.splitlines(keepends=True),
                fromfile="O0_unoptimized.ll",
                tofile="O2_optimized.ll",
                n=3
            ))
            ir_diff = "".join(diff_lines)

        return CompareResponse(
            o0_result=CompileResponse(**res_o0.to_dict()),
            o2_result=CompileResponse(**res_o2.to_dict()),
            ir_diff=ir_diff
        )

    def run_wasm(self, req: RunRequest) -> Dict[str, Any]:
        wasm_bytes = base64.b64decode(req.wasm_base64)
        return execute_wasm(wasm_bytes, timeout_seconds=req.timeout_seconds or 5.0)

    def get_health(self) -> HealthResponse:
        compiler_ready = settings.ZIG_COMPILER.exists() and settings.WASM_VALIDATE.exists()
        return HealthResponse(
            status="healthy",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            compiler_ready=compiler_ready,
            runtime_ready=True
        )

    def get_compiler_info(self) -> CompilerInfoResponse:
        # Detected Zig / Clang version
        clang_ver = "unknown"
        if settings.ZIG_COMPILER.exists():
            try:
                res = subprocess.run([str(settings.ZIG_COMPILER), "version"], capture_output=True, text=True, timeout=2)
                clang_ver = f"Zig {res.stdout.strip()} (LLVM 19 backend)"
            except Exception:
                pass

        # WABT version
        wabt_ver = "1.0.42"

        return CompilerInfoResponse(
            llvm_version=str(llvm.llvm_version_info),
            clang_version=clang_ver,
            wabt_version=wabt_ver,
            wasmtime_version="50.0.1",
            target_triple=settings.TARGET_TRIPLE,
            data_layout=settings.DATA_LAYOUT,
            supported_optimizations=["O0", "O2"]
        )

    def get_examples(self) -> List[ExampleProgram]:
        examples_dir = WORKSPACE_ROOT / "examples"
        programs: List[ExampleProgram] = []

        meta = [
            {
                "id": "arithmetic",
                "name": "Basic Arithmetic",
                "filename": "arithmetic.mini",
                "description": "Standard arithmetic with operator precedence, returning 10 + 20 * 2 = 50",
                "expected_output": 50
            },
            {
                "id": "conditionals",
                "name": "Conditionals & Logic",
                "filename": "conditionals.mini",
                "description": "If-else branch selection and comparisons, returning max(45, 90) = 90",
                "expected_output": 90
            },
            {
                "id": "loops",
                "name": "While Loops & Scopes",
                "filename": "loops.mini",
                "description": "While loop computing sum of numbers from 1 to 10 = 55",
                "expected_output": 55
            },
            {
                "id": "functions",
                "name": "Recursive Functions",
                "filename": "functions.mini",
                "description": "Recursive Fibonacci sequence implementation computing fib(10) = 55",
                "expected_output": 55
            },
            {
                "id": "semantic_errors",
                "name": "Semantic Errors Demo",
                "filename": "semantic-errors.mini",
                "description": "Demonstration of duplicate declarations, type mismatches, and undeclared variables",
                "expected_output": 0
            }
        ]

        for item in meta:
            file_path = examples_dir / item["filename"]
            content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
            programs.append(ExampleProgram(
                id=item["id"],
                name=item["name"],
                filename=item["filename"],
                description=item["description"],
                expected_output=item["expected_output"],
                source=content
            ))

        return programs

compilation_service = CompilationService()
