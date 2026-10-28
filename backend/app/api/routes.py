from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from ..schemas.requests import CompileRequest, CompareRequest, RunRequest
from ..schemas.responses import (
    CompileResponse, CompareResponse, HealthResponse,
    CompilerInfoResponse, ExampleProgram
)
from ..services.compilation_service import compilation_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Returns system health, toolchain readiness, and application status."""
    return compilation_service.get_health()

@router.get("/compiler-info", response_model=CompilerInfoResponse)
def get_compiler_info() -> CompilerInfoResponse:
    """Returns detected compiler versions, target triple, and optimization passes."""
    return compilation_service.get_compiler_info()

@router.get("/examples", response_model=List[ExampleProgram])
def get_examples() -> List[ExampleProgram]:
    """Returns list of curated MiniLang sample programs with source and metadata."""
    return compilation_service.get_examples()

@router.post("/compile", response_model=CompileResponse)
def compile_code(req: CompileRequest) -> CompileResponse:
    """
    Executes the full machine-independent compilation pipeline:
    Source -> Lex/Parse -> Semantic -> LLVM IR -> Verifier -> Optimizer -> WASM -> Validate -> Runtime.
    """
    if not req.source.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code cannot be empty"
        )
    return compilation_service.compile(req)

@router.post("/compare", response_model=CompareResponse)
def compare_optimizations(req: CompareRequest) -> CompareResponse:
    """
    Runs both O0 (unoptimized) and O2 (optimized) passes on the program,
    returning generated artifacts and line-by-line unified IR diff.
    """
    if not req.source.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code cannot be empty"
        )
    return compilation_service.compare(req)

@router.post("/run")
def run_wasm_binary(req: RunRequest) -> Dict[str, Any]:
    """Executes a standalone WebAssembly binary in wasmtime and returns execution metrics."""
    try:
        return compilation_service.run_wasm(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution error: {str(e)}"
        )
