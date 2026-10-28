from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["compiler_ready"] is True

def test_compiler_info_endpoint():
    res = client.get("/api/compiler-info")
    assert res.status_code == 200
    data = res.json()
    assert data["target_triple"] == "wasm32-unknown-unknown"
    assert "O2" in data["supported_optimizations"]

def test_compile_endpoint_success():
    payload = {
        "source": "fn main() -> i32 { return 42; }",
        "filename": "test.mini",
        "optimization": "O2",
        "execute": True
    }
    res = client.post("/api/compile", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["runtime_result"]["return_value"] == 42
    assert len(data["wat"]) > 0

def test_compile_endpoint_empty_source_rejected():
    payload = {"source": "", "filename": "test.mini"}
    res = client.post("/api/compile", json=payload)
    assert res.status_code == 400

def test_compile_endpoint_unsupported_opt_rejected():
    payload = {"source": "fn main() -> i32 { return 0; }", "optimization": "O99"}
    res = client.post("/api/compile", json=payload)
    assert res.status_code == 422  # Pydantic validation error
