import os
import subprocess
import wasmtime

def test_full_pipeline():
    clang = os.path.abspath("tools/llvm-mingw-20261020-ucrt-x86_64/bin/clang.exe")
    wasm_validate = os.path.abspath("tools/wabt-1.0.42/bin/wasm-validate.exe")
    wasm2wat = os.path.abspath("tools/wabt-1.0.42/bin/wasm2wat.exe")

    print(f"Clang: {clang} (exists: {os.path.exists(clang)})")
    print(f"wasm-validate: {wasm_validate} (exists: {os.path.exists(wasm_validate)})")
    print(f"wasm2wat: {wasm2wat} (exists: {os.path.exists(wasm2wat)})")

    ir_content = """target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

define i32 @main() {
entry:
    %x = add i32 10, 40
    ret i32 %x
}
"""
    with open("temp_test.ll", "w") as f:
        f.write(ir_content)

    # 1. Compile LLVM IR to WASM via Clang
    cmd = [
        clang,
        "--target=wasm32-unknown-unknown",
        "-O2",
        "-nostdlib",
        "-Wl,--no-entry",
        "-Wl,--export-all",
        "-o", "temp_test.wasm",
        "temp_test.ll"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Clang exit code:", res.returncode)
    if res.returncode != 0:
        print("Clang stderr:", res.stderr)
        return

    wasm_size = os.path.getsize("temp_test.wasm")
    print(f"Generated temp_test.wasm: {wasm_size} bytes")

    # 2. Validate WASM using WABT wasm-validate
    v_res = subprocess.run([wasm_validate, "temp_test.wasm"], capture_output=True, text=True)
    print("wasm-validate exit code:", v_res.returncode)
    if v_res.returncode == 0:
        print("Module validation SUCCEEDED!")
    else:
        print("wasm-validate error:", v_res.stderr)

    # 3. Disassemble WASM to WAT using WABT wasm2wat
    wat_res = subprocess.run([wasm2wat, "temp_test.wasm"], capture_output=True, text=True)
    print("=== Disassembled WAT ===")
    print(wat_res.stdout)

    # 4. Execute WASM using wasmtime runtime
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    module = wasmtime.Module.from_file(engine, "temp_test.wasm")
    instance = wasmtime.Instance(store, module, [])
    main_func = instance.exports(store)["main"]
    result = main_func(store)
    print(f"=== WASMTIME EXECUTION RESULT: {result} ===")
    assert result == 50, f"Expected 50, got {result}"
    print("SUCCESS: Full toolchain verification passed! 50 returned!")

if __name__ == "__main__":
    test_full_pipeline()
