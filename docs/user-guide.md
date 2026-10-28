# WASM Lab User Guide

## 1. Introduction to MiniLang

MiniLang is a clean, statically typed programming language designed for compiling to WebAssembly.

### 1.1 Program Structure
A MiniLang program consists of function definitions. The entry point of every executable program is `main()`:
```rust
fn main() -> i32 {
    let x: i32 = 10;
    let y: i32 = 20;
    return x + y * 2;
}
```

### 1.2 Data Types
- `i32`: 32-bit signed integers (e.g., `42`, `-10`).
- `bool`: Boolean truth values (`true`, `false`).

### 1.3 Control Flow
#### Conditionals:
```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    } else {
        return b;
    }
}
```

#### While Loops:
```rust
fn sum_to_n(n: i32) -> i32 {
    let sum: i32 = 0;
    let i: i32 = 1;
    while i <= n {
        sum = sum + i;
        i = i + 1;
    }
    return sum;
}
```

#### Functions & Recursion:
```rust
fn fib(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}
```

---

## 2. Using the WASM Lab IDE

### 2.1 The Interface Layout
1. **Activity Rail (Left)**: Switch between File Explorer, Pipeline, Comparison, and Console.
2. **File Explorer**: Click on sample programs (`arithmetic.mini`, `conditionals.mini`, `loops.mini`, `functions.mini`, `semantic-errors.mini`) or click `+` to write custom code.
3. **Monaco Code Editor**: Write code with syntax highlighting, automatic line numbers, and inline diagnostic squiggles.
4. **Pipeline Visualizer**: Displays live status and millisecond execution times across all 8 compiler stages.
5. **Artifact Inspector (Right Tabs)**:
   - **Optimized IR**: View the post-optimization LLVM IR.
   - **Initial IR**: View unoptimized LLVM IR with full alloca/load/store structures.
   - **WebAssembly (WAT)**: View disassembled W3C WebAssembly Text.
   - **Optimization Diff**: Line-by-line colored diff between O0 and O2.
   - **AST Tree**: View hierarchical JSON representation of the parsed Abstract Syntax Tree.
   - **Diagnostics**: View compiler warnings and errors with one-click line jumping.
6. **Runtime Console (Bottom)**:
   - View dual execution verification: **wasmtime** exit code and **in-browser WebAssembly API** exit code!
   - Real-time compiler log stream with timestamps.

### 2.2 Compilation & Keyboard Shortcuts
- Press **`Ctrl + Enter`** (or `Cmd + Enter` on macOS) to instantly compile and run.
- Toggle between **`O0 (Debug)`** and **`O2 (Standard)`** in the top navigation bar.

### 2.3 Downloading Artifacts
In the top right corner of the Artifact Inspector, click:
- **`.WASM`**: Downloads the real binary WebAssembly module.
- **Copy Icon**: Copies the current tab's text to your clipboard.
- **FileDown Icon**: Downloads `compilation_report.json` containing timing benchmarks and compiler metadata.
