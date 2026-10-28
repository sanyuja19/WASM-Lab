import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, List

from .diagnostics import CompilerError
from ..config import settings

def emit_wasm_binary(ir_text: str, optimization_level: str = "O2") -> Tuple[bytes, int]:
    """Compiles LLVM IR into a freestanding WebAssembly (.wasm) binary using the LLVM backend."""
    compiler_path = settings.ZIG_COMPILER
    if not compiler_path.exists():
        raise CompilerError(
            f"Clang/LLVM WebAssembly compiler not found at {compiler_path}",
            stage="wasm_codegen",
            code="ERR_COMPILER_NOT_FOUND"
        )

    with tempfile.TemporaryDirectory(prefix="wasmlab_build_") as tmpdir:
        ll_path = Path(tmpdir) / "module.ll"
        wasm_path = Path(tmpdir) / "module.wasm"

        # Write LLVM IR to temp file
        ll_path.write_text(ir_text, encoding="utf-8")

        # Select clang optimization flag
        opt_flag = "-O0" if optimization_level == "O0" else "-O2"

        # Discover all defined function names in the IR to export
        fn_names = re.findall(r'define\s+[^@]+@"?([a-zA-Z0-9_]+)"?\(', ir_text)
        export_args: List[str] = []
        for fn in fn_names:
            export_args.append(f"-Wl,--export={fn}")

        # Ensure 'main' is exported if present
        if "-Wl,--export=main" not in export_args:
            export_args.append("-Wl,--export=main")

        # Build command: compile LLVM IR directly to freestanding WebAssembly
        cmd = [
            str(compiler_path),
            "cc",
            "-target", "wasm32-freestanding",
            opt_flag,
            "-nostdlib",
            "-Wl,--no-entry",
            *export_args,
            "-o", str(wasm_path),
            str(ll_path)
        ]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.COMPILATION_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired:
            raise CompilerError(
                f"WebAssembly code generation timed out after {settings.COMPILATION_TIMEOUT_SECONDS}s",
                stage="wasm_codegen",
                code="ERR_CODEGEN_TIMEOUT"
            )
        except Exception as e:
            raise CompilerError(
                f"WebAssembly code generation execution error: {str(e)}",
                stage="wasm_codegen",
                code="ERR_CODEGEN_EXEC"
            )

        if res.returncode != 0:
            error_output = res.stderr or res.stdout
            raise CompilerError(
                f"LLVM WebAssembly backend emission failed (exit code {res.returncode}): {error_output}",
                stage="wasm_codegen",
                code="ERR_LLVM_BACKEND"
            )

        if not wasm_path.exists():
            raise CompilerError(
                "Output WebAssembly file was not created by the backend compiler",
                stage="wasm_codegen",
                code="ERR_WASM_FILE_MISSING"
            )

        wasm_bytes = wasm_path.read_bytes()
        return wasm_bytes, len(wasm_bytes)
