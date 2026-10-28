# Project Proposal: Machine-Independent Compiler Framework Targeting WebAssembly Using LLVM

**Project Title**: Machine-Independent Compiler Framework Targeting WebAssembly Using LLVM  
**Application Name**: WASM Lab  
**Domain**: Compiler Construction, Programming Language Engineering, Systems Architecture  

---

## 1. Abstract

Modern software engineering increasingly demands high-performance, sandboxed execution across diverse client and server platforms. WebAssembly (Wasm) has emerged as the universal low-level bytecode standard for secure, near-native execution in web browsers, edge computing nodes, and cloud containers. Concurrently, the LLVM compiler infrastructure serves as the state of the art in modular, machine-independent code optimization and target emission.

This project presents **WASM Lab**, an end-to-end, machine-independent compiler framework and interactive developer environment. WASM Lab accepts programs written in **MiniLang** (a statically typed, imperative C-family language), translates them through formal lexical analysis, LALR parsing, and semantic validation, synthesizes strongly typed Static Single Assignment (SSA) LLVM Intermediate Representation, applies genuine LLVM optimization passes (such as SROA/mem2reg, SCCP, and dead-code elimination), compiles the result into freestanding WebAssembly bytecode, validates the module against W3C specification tools, and executes the binary across dual runtime engines (`wasmtime` and browser V8).

## 2. Introduction & Problem Statement

### 2.1 The Problem
Traditional educational compilers frequently commit one of two errors:
1. **Oversimplified Toy Emulation**: Compilers that generate simulated bytecode or mock outputs without interfacing with real industrial toolchains, failing to expose students and researchers to SSA form, real optimization pipelines, and binary linking.
2. **Monolithic Complexity**: Production compilers (like GCC or full Clang) are millions of lines of C++ code, creating an impenetrable barrier to understanding how high-level language constructs map through IR transformations to modern virtual instruction sets.

### 2.2 Existing Approaches & Limitations
- Existing pedagogical compilers usually stop at AST interpretation or emit non-standard stack bytecode.
- Web-based compiler explorers (e.g., Compiler Explorer / Godbolt) display assembly output for pre-existing languages (C, C++, Rust), but do not provide a self-contained compiler pipeline where every stage—from EBNF grammar to custom type checking, LLVM IR emission, and WebAssembly execution—is inspectable, customizable, and debuggable in one coherent framework.

## 3. Objectives

1. **Formal Language Frontend**: Design and implement a complete lexer, LALR(1) parser, and AST with precise source location tracking for MiniLang.
2. **Semantic Verification**: Implement multi-pass semantic analysis, lexical scoping, symbol tables, and type checking for integers (`i32`) and booleans (`bool`).
3. **Structured LLVM IR Synthesis**: Programmatically synthesize valid, verifiable LLVM IR in SSA form using `llvmlite.ir`, avoiding fragile string templates.
4. **LLVM Pass Pipeline**: Construct selectable optimization pipelines (`O0` vs `O2`) leveraging LLVM's modern Pass Manager to perform register promotion, constant folding, and dead-code elimination.
5. **Freestanding WebAssembly Emission**: Lower optimized LLVM IR into valid WebAssembly binary modules (`.wasm`) and human-readable WebAssembly Text (`.wat`).
6. **Dual Runtime Execution**: Execute generated modules in both a controlled backend runtime (`wasmtime`) and directly in the browser's native WebAssembly engine.
7. **Professional IDE Interface**: Provide a responsive dark graphite developer interface with Monaco Editor, 8-stage pipeline visualization, real stage timings, optimization diffs, and artifact downloads.

## 4. Methodology & Architecture

The framework is structured into five distinct, decoupled layers:
1. **Frontend**: MiniLang grammar -> Tokens -> AST -> Semantic Analysis.
2. **Intermediate Representation**: AST -> LLVM IR Builder (`llvmlite.ir`) -> Module Verifier.
3. **Optimization Engine**: TargetMachine + PassBuilder -> NewPM passes (`O0`, `O2`).
4. **Backend**: LLVM Clang freestanding wasm32 compilation -> WABT `wasm-validate` -> `wasm2wat`.
5. **Runtime & Presentation**: `wasmtime` / Browser execution -> FastAPI service -> React + TypeScript + Monaco IDE.

## 5. Tools & Technologies

- **Frontend Language & Tools**: Python 3.13, Lark (LALR Parser), `llvmlite` (LLVM 22/19 bindings).
- **LLVM Toolchain**: Native LLVM Clang compiler with `wasm32-unknown-unknown` target.
- **Wasm Verification**: WABT 1.0.42 (`wasm-validate`, `wasm2wat`).
- **Wasm Runtime**: `wasmtime` 50.0.1 and WebAssembly Browser Engine.
- **Backend API**: FastAPI, Uvicorn, Pydantic v2.
- **IDE Interface**: React 18, TypeScript 5, Vite 5, Tailwind CSS 3, Monaco Editor, Lucide React, Framer Motion.
- **Testing**: `pytest`, HTTPX TestClient.

## 6. Expected Outcomes

- A canonical arithmetic test program:
  ```rust
  fn main() -> i32 {
      let x: i32 = 10;
      let y: i32 = 20;
      return x + y * 2;
  }
  ```
  successfully compiles end-to-end, constant-folds to `ret i32 50`, emits a 234-byte WebAssembly binary, validates via WABT, and executes in both `wasmtime` and browser engines, returning `50`.
- A suite of 28 automated tests passing with zero errors.
- Real-time side-by-side optimization diff showing memory alloca removal and instruction count reductions.

## 7. Limitations & Future Work

- **Current Limitations**: Supports `i32` and `bool` primitive scalar types. Floating-point numbers (`f64`), arrays, pointers, and heap allocations are omitted in the initial version to guarantee zero-dependency freestanding execution.
- **Future Enhancements**: Add floating-point arithmetic (`f64`), user-defined structs, standard library memory allocation (`malloc`/`free`), and multi-file module linking.

## 8. References

1. Lattner, C., & Adve, V. (2004). *LLVM: A compilation framework for lifelong program analysis & transformation*. CGO '04.
2. Haas, A., Rossberg, A., Schuff, D. L., et al. (2017). *Bringing the web up to speed with WebAssembly*. PLDI '17.
3. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.
