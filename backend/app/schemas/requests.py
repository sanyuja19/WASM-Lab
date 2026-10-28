from pydantic import BaseModel, Field
from typing import Optional

class CompileRequest(BaseModel):
    source: str = Field(..., max_length=65536, description="MiniLang source code to compile")
    filename: str = Field(default="main.mini", max_length=128, description="Source filename")
    optimization: str = Field(default="O2", pattern="^(O0|O2)$", description="Optimization level: O0 or O2")
    execute: bool = Field(default=True, description="Whether to execute the generated module in wasmtime")

class CompareRequest(BaseModel):
    source: str = Field(..., max_length=65536, description="MiniLang source code to compile and compare at O0 and O2")
    filename: str = Field(default="main.mini", max_length=128, description="Source filename")

class RunRequest(BaseModel):
    wasm_base64: str = Field(..., description="Base64-encoded WebAssembly binary to execute")
    timeout_seconds: Optional[float] = Field(default=5.0, ge=0.1, le=15.0)
