import time
from typing import Dict, Any, Optional
import wasmtime

from .diagnostics import CompilerError
from ..config import settings

def execute_wasm(wasm_bytes: bytes, timeout_seconds: float = 5.0) -> Dict[str, Any]:
    """
    Executes a WebAssembly binary module in a controlled runtime environment
    using wasmtime, extracting the return value of 'main'.
    """
    start_time = time.perf_counter()

    try:
        engine = wasmtime.Engine()
        store = wasmtime.Store(engine)
        module = wasmtime.Module(engine, wasm_bytes)

        # Inspect module imports: reject unsupported imports
        imports = module.imports
        if len(imports) > 0:
            import_names = [f"{imp.module}::{imp.name}" for imp in imports]
            raise CompilerError(
                f"WebAssembly module requires unsupported imports: {import_names}",
                stage="runtime",
                code="ERR_UNSUPPORTED_IMPORTS"
            )

        # Instantiate module (freestanding: no imports needed)
        instance = wasmtime.Instance(store, module, [])
        exports = instance.exports(store)

        # Look for entry point
        # Clang freestanding wasm often exports 'main' (which wraps '__original_main') or '__original_main' directly
        main_func = exports.get("main") or exports.get("__original_main")

        if not main_func or not isinstance(main_func, wasmtime.Func):
            export_keys = list(exports.keys())
            raise CompilerError(
                f"Entry point 'main' not found in WebAssembly exports. Available exports: {export_keys}",
                stage="runtime",
                code="ERR_ENTRY_NOT_FOUND"
            )

        # Inspect parameter requirements
        func_type = main_func.type(store)
        param_count = len(func_type.params)

        # Call main with appropriate arguments (0 or 2 for argc/argv)
        if param_count == 0:
            result = main_func(store)
        elif param_count == 2:
            result = main_func(store, 0, 0)
        else:
            raise CompilerError(
                f"Exported 'main' function expects {param_count} parameters, which is unsupported for automatic entry point",
                stage="runtime",
                code="ERR_INVALID_MAIN_SIGNATURE"
            )

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "success": True,
            "return_value": result,
            "duration_ms": round(duration_ms, 3),
            "exports": list(exports.keys()),
            "trap": None,
        }

    except wasmtime.Trap as trap:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "success": False,
            "return_value": None,
            "duration_ms": round(duration_ms, 3),
            "exports": [],
            "trap": str(trap),
            "error": f"WebAssembly execution trap: {str(trap)}"
        }
    except CompilerError:
        raise
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        raise CompilerError(
            f"WebAssembly runtime execution failed: {str(e)}",
            stage="runtime",
            code="ERR_RUNTIME_EXEC"
        )
