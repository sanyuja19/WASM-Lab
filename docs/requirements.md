# WASM Lab Software Requirements Specification (SRS)

## 1. Functional Requirements

### 1.1 Lexical & Syntactic Requirements
- **FR-1.1**: The lexer must tokenize keywords (`fn`, `let`, `if`, `else`, `while`, `return`, `true`, `false`, `i32`, `bool`), numeric literals, identifiers, arithmetic operators (`+`, `-`, `*`, `/`, `%`), comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`), logical operators (`&&`, `||`, `!`), and delimiters.
- **FR-1.2**: Comments starting with `//` and arbitrary whitespace must be recognized and discarded without altering token stream semantics.
- **FR-1.3**: The parser must parse statements and expressions according to formal operator precedence and associativity rules.
- **FR-1.4**: Syntax errors must be captured with precise line and column numbers.

### 1.2 Semantic Requirements
- **FR-2.1**: The compiler must reject duplicate variable declarations within the same lexical scope.
- **FR-2.2**: The compiler must reject references to undeclared variables or undefined functions.
- **FR-2.3**: Operands of arithmetic operations must be strictly `i32`. Operands of logical operations must be strictly `bool`.
- **FR-2.4**: Condition expressions in `if` and `while` statements must evaluate to `bool`.
- **FR-2.5**: Functions returning non-void types must return a value on every execution path.
- **FR-2.6**: Function call argument counts and types must match the declared signature.

### 1.3 LLVM IR Generation Requirements
- **FR-3.1**: Generates valid LLVM IR with target triple `wasm32-unknown-unknown` and data layout `e-m:e-p:32:32...`.
- **FR-3.2**: Uses memory allocations (`alloca`), stores, and loads for local mutable variables.
- **FR-3.3**: Uses standard SSA basic blocks (`entry`, `if.then`, `if.else`, `if.end`, `while.cond`, `while.body`, `while.end`).
- **FR-3.4**: All generated modules must pass the LLVM module verifier (`mod.verify()`).

### 1.4 LLVM Optimization Requirements
- **FR-4.1**: Provides selectable `O0` and `O2` optimization configurations.
- **FR-4.2**: `O0` must preserve memory allocations and unoptimized instruction layouts.
- **FR-4.3**: `O2` must apply SROA (mem2reg), SCCP (constant propagation), instruction combining, and dead-code elimination.
- **FR-4.4**: Generates line-by-line unified diff and instruction count deltas.

### 1.5 WebAssembly Backend & Runtime Requirements
- **FR-5.1**: Generates genuine standalone `.wasm` binaries using the LLVM backend.
- **FR-5.2**: Validates all generated modules using WABT `wasm-validate`.
- **FR-5.3**: Generates readable WAT disassembly using WABT `wasm2wat`.
- **FR-5.4**: Executes modules in `wasmtime` and browser V8 WebAssembly engines, returning the integer exit code of `main()`.

### 1.6 User Interface Requirements
- **FR-6.1**: Dark graphite developer interface (`#111114`, `#17171C`, `#1C1C22`).
- **FR-6.2**: Monaco Editor with MiniLang syntax highlighting, error markers, and keyboard shortcuts (`Ctrl+Enter`).
- **FR-6.3**: 8-stage interactive compilation pipeline visualizer with live timing metrics.
- **FR-6.4**: Real artifact tabs for LLVM IR, Optimized IR, WAT, Optimization Diff, and AST JSON.
- **FR-6.5**: Export actions for `.ll`, `.opt.ll`, `.wat`, `.wasm`, and `compilation_report.json`.

## 2. Non-Functional Requirements

- **NFR-1 (Performance)**: Compilation pipeline must complete in under 500 ms for standard programs.
- **NFR-2 (Accuracy)**: Zero simulated compiler outputs or hardcoded results.
- **NFR-3 (Reliability)**: Robust error recovery—compiler errors in one stage must cleanly skip subsequent stages without crashing the application.
- **NFR-4 (Security)**: Request size limits (64 KB max), execution timeouts (10s compilation, 5s runtime), sandboxed WebAssembly execution with zero arbitrary system imports.
