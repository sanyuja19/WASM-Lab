import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.compiler.pipeline import CompilerPipeline

def run_benchmark():
    pipeline = CompilerPipeline()
    examples = ["arithmetic.mini", "conditionals.mini", "loops.mini", "functions.mini"]

    print("=" * 86)
    print("                    WASM LAB COMPILER BENCHMARK REPORT")
    print("=" * 86)
    print(f"{'Program':<20} {'Opt':<5} {'Total(ms)':<12} {'Codegen(ms)':<13} {'Size(B)':<10} {'Instructions':<14} {'Result':<8}")
    print("-" * 86)

    for ex in examples:
        path = os.path.join(str(root_dir), "examples", ex)
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()

        for opt in ["O0", "O2"]:
            res = pipeline.run(src, filename=ex, optimization_level=opt, execute=True)
            codegen_time = next((m.duration_ms for m in res.stage_metrics if m.name == "wasm_codegen"), 0.0)
            ret_val = res.runtime_result["return_value"] if res.runtime_result else "N/A"
            inst_str = f"{res.optimization_metrics['initial_instructions']}->{res.optimization_metrics['optimized_instructions']}"
            print(f"{ex:<20} {opt:<5} {res.total_duration_ms:<12.2f} {codegen_time:<13.2f} {res.wasm_size_bytes:<10} {inst_str:<14} {ret_val:<8}")

    print("-" * 86)
    print("All timings measured via Python time.perf_counter() monotonic high-resolution clock.")
    print("=" * 86)

if __name__ == "__main__":
    run_benchmark()
