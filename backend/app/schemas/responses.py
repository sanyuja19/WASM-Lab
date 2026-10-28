from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SourceLocationModel(BaseModel):
    line: int
    column: int
    end_line: int
    end_column: int

class DiagnosticModel(BaseModel):
    stage: str
    message: str
    severity: str
    code: Optional[str] = None
    location: Optional[SourceLocationModel] = None

class StageMetricModel(BaseModel):
    name: str
    status: str
    duration_ms: float
    details: Optional[str] = None

class RuntimeResultModel(BaseModel):
    success: bool
    return_value: Optional[int] = None
    duration_ms: float
    exports: List[str] = []
    trap: Optional[str] = None
    error: Optional[str] = None

class CompileResponse(BaseModel):
    success: bool
    filename: str
    optimization_level: str
    total_duration_ms: float
    diagnostics: List[DiagnosticModel] = []
    stage_metrics: List[StageMetricModel] = []
    ast_tree: Optional[Dict[str, Any]] = None
    raw_ir: Optional[str] = None
    optimized_ir: Optional[str] = None
    wat: Optional[str] = None
    wasm_base64: Optional[str] = None
    wasm_size_bytes: int = 0
    optimization_metrics: Optional[Dict[str, Any]] = None
    runtime_result: Optional[RuntimeResultModel] = None
    compiler_logs: List[str] = []

class CompareResponse(BaseModel):
    o0_result: CompileResponse
    o2_result: CompileResponse
    ir_diff: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    compiler_ready: bool
    runtime_ready: bool

class CompilerInfoResponse(BaseModel):
    llvm_version: str
    clang_version: str
    wabt_version: str
    wasmtime_version: str
    target_triple: str
    data_layout: str
    supported_optimizations: List[str]

class ExampleProgram(BaseModel):
    id: str
    name: str
    filename: str
    description: str
    expected_output: int
    source: str
