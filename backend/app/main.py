from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .config import settings

app = FastAPI(
    title="WASM Lab API",
    description="Machine-Independent Compiler Framework Targeting WebAssembly Using LLVM",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Machine-Independent Compiler Framework Targeting WebAssembly Using LLVM",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "compiler_info": "/api/compiler-info",
            "compile": "/api/compile",
            "compare": "/api/compare",
            "examples": "/api/examples",
            "run": "/api/run"
        }
    }
