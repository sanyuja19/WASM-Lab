import os
from pathlib import Path
from pydantic import BaseModel, Field

# Project root directory (workspace root)
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    APP_NAME: str = "WASM Lab"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    # Paths to compilers and tools
    ZIG_COMPILER: Path = Field(default_factory=lambda: WORKSPACE_ROOT / "tools" / "zig-windows-x86_64-0.14.0" / "zig.exe")
    WASM_VALIDATE: Path = Field(default_factory=lambda: WORKSPACE_ROOT / "tools" / "wabt-1.0.42" / "bin" / "wasm-validate.exe")
    WASM2WAT: Path = Field(default_factory=lambda: WORKSPACE_ROOT / "tools" / "wabt-1.0.42" / "bin" / "wasm2wat.exe")
    WAT2WASM: Path = Field(default_factory=lambda: WORKSPACE_ROOT / "tools" / "wabt-1.0.42" / "bin" / "wat2wasm.exe")

    # Compiler limits and timeouts
    MAX_SOURCE_SIZE_BYTES: int = 65536  # 64 KB
    COMPILATION_TIMEOUT_SECONDS: float = 10.0
    EXECUTION_TIMEOUT_SECONDS: float = 5.0

    # Target configuration
    TARGET_TRIPLE: str = "wasm32-unknown-unknown"
    DATA_LAYOUT: str = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"

settings = Settings()
