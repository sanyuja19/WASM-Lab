import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

from .diagnostics import CompilerError
from ..config import settings

def validate_and_disassemble(wasm_bytes: bytes) -> Tuple[bool, str]:
    """
    Validates the WebAssembly module with WABT wasm-validate
    and disassembles it to WebAssembly Text (WAT) using WABT wasm2wat.
    """
    validate_bin = settings.WASM_VALIDATE
    wasm2wat_bin = settings.WASM2WAT

    if not validate_bin.exists() or not wasm2wat_bin.exists():
        raise CompilerError(
            f"WABT tools not found at {validate_bin} or {wasm2wat_bin}",
            stage="wasm_validator",
            code="ERR_WABT_NOT_FOUND"
        )

    with tempfile.TemporaryDirectory(prefix="wasmlab_val_") as tmpdir:
        wasm_path = Path(tmpdir) / "module.wasm"
        wasm_path.write_bytes(wasm_bytes)

        # 1. Validate using wasm-validate
        val_cmd = [str(validate_bin), str(wasm_path)]
        try:
            val_res = subprocess.run(
                val_cmd,
                capture_output=True,
                text=True,
                timeout=settings.COMPILATION_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired:
            raise CompilerError(
                "wasm-validate timed out",
                stage="wasm_validator",
                code="ERR_VALIDATE_TIMEOUT"
            )
        except Exception as e:
            raise CompilerError(
                f"wasm-validate execution error: {str(e)}",
                stage="wasm_validator",
                code="ERR_VALIDATE_EXEC"
            )

        if val_res.returncode != 0:
            raise CompilerError(
                f"WebAssembly module specification validation failed: {val_res.stderr or val_res.stdout}",
                stage="wasm_validator",
                code="ERR_WASM_INVALID"
            )

        # 2. Disassemble using wasm2wat
        wat_cmd = [str(wasm2wat_bin), "--generate-names", str(wasm_path)]
        try:
            wat_res = subprocess.run(
                wat_cmd,
                capture_output=True,
                text=True,
                timeout=settings.COMPILATION_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired:
            raise CompilerError(
                "wasm2wat timed out",
                stage="wasm_validator",
                code="ERR_WASM2WAT_TIMEOUT"
            )
        except Exception as e:
            raise CompilerError(
                f"wasm2wat execution error: {str(e)}",
                stage="wasm_validator",
                code="ERR_WASM2WAT_EXEC"
            )

        if wat_res.returncode != 0:
            raise CompilerError(
                f"wasm2wat disassembly failed: {wat_res.stderr or wat_res.stdout}",
                stage="wasm_validator",
                code="ERR_WASM2WAT_FAIL"
            )

        wat_text = wat_res.stdout
        return True, wat_text
