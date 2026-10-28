# Empirical Performance and Optimization Evaluation

## 1. Methodology

All performance measurements were collected on a Windows x64 workstation running Python 3.13.0, LLVM 19 (via Zig toolchain), and WABT 1.0.42 using high-resolution monotonic clocks (`time.perf_counter()`). Each program was compiled and executed under both `O0` (debug) and `O2` (standard optimization).

Reproducible script: `powershell -ExecutionPolicy Bypass -File scripts\benchmark.ps1`

## 2. Benchmark Results Table

| Program | Optimization | Total Time (ms) | LLVM Codegen (ms) | Binary Size (B) | Instruction Count (Initial -> Opt) | Return Value |
|---|---|---|---|---|---|---|
| `arithmetic.mini` | `O0` | 202.44 | 160.51 | 303 | 10 -> 10 | **50** |
| `arithmetic.mini` | `O2` | 151.95 | 122.82 | 234 | 10 -> 2 (-80%) | **50** |
| `conditionals.mini` | `O0` | 198.66 | 132.04 | 436 | 25 -> 25 | **90** |
| `conditionals.mini` | `O2` | 205.77 | 167.59 | 298 | 25 -> 6 (-76%) | **90** |
| `loops.mini` | `O0` | 174.81 | 135.75 | 434 | 27 -> 27 | **55** |
| `loops.mini` | `O2` | 155.68 | 107.53 | 359 | 27 -> 15 (-44%) | **55** |
| `functions.mini` | `O0` | 176.89 | 149.25 | 453 | 20 -> 20 | **55** |
| `functions.mini` | `O2` | 177.79 | 140.84 | 360 | 20 -> 15 (-25%) | **55** |

## 3. Analysis of Findings

1. **Instruction Elimination**:
   - In `arithmetic.mini`, LLVM's `O2` pipeline completely folds `10 + 20 * 2` into `ret i32 50`, eliminating 8 out of 10 instructions (an 80% reduction in SSA instruction density).
   - In `conditionals.mini`, constant propagation and CFG simplification collapse the conditional jump and dead branches, reducing 25 instructions to 6 instructions.
2. **Binary Size Reduction**:
   - Across all programs, `O2` optimization yields a 19% to 32% reduction in final `.wasm` binary size compared to `O0`.
3. **Compilation Latency**:
   - The total compilation pipeline duration remains consistently between 150 ms and 210 ms, with LLVM backend code emission and linking accounting for approximately 70-80% of total pipeline latency. Frontend lexing, parsing, and semantic analysis execute in under 5 ms.
4. **Correctness Invariance**:
   - In all cases, `O0` and `O2` produce identical runtime mathematical results, confirming that optimization passes preserve program semantics without introducing regressions.
