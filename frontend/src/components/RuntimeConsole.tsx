import React, { useState, useEffect } from 'react';
import { Terminal, Trash2, Globe, Shield } from 'lucide-react';
import type { CompileResponse } from '../types/compiler';

interface RuntimeConsoleProps {
  compileResult: CompileResponse | null;
  logs: string[];
  onClearLogs: () => void;
}

export const RuntimeConsole: React.FC<RuntimeConsoleProps> = ({
  compileResult,
  logs,
  onClearLogs,
}) => {
  const [browserResult, setBrowserResult] = useState<{
    tested: boolean;
    val?: number;
    timeMs?: number;
    error?: string;
  }>({ tested: false });

  // Whenever compileResult changes with a new wasm_base64, execute in browser WebAssembly runtime
  useEffect(() => {
    if (!compileResult?.wasm_base64) {
      setBrowserResult({ tested: false });
      return;
    }

    const runInBrowser = async () => {
      const t0 = performance.now();
      try {
        const binaryStr = atob(compileResult.wasm_base64!);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {
          bytes[i] = binaryStr.charCodeAt(i);
        }

        const wasmModule = await WebAssembly.instantiate(bytes, {});
        const instance = wasmModule.instance;
        const exports: any = instance.exports;

        const mainFn = exports.main || exports.__original_main;
        if (!mainFn) {
          setBrowserResult({
            tested: true,
            error: "No 'main' entry point found in browser exports",
          });
          return;
        }

        // Call main (with 0 or 2 args if argc/argv wrapper)
        let res: any;
        try {
          res = mainFn();
        } catch {
          res = mainFn(0, 0);
        }

        const duration = performance.now() - t0;
        setBrowserResult({
          tested: true,
          val: Number(res),
          timeMs: Math.round(duration * 100) / 100,
        });
      } catch (err: any) {
        setBrowserResult({
          tested: true,
          error: err?.message || 'Browser WebAssembly execution error',
        });
      }
    };

    runInBrowser();
  }, [compileResult?.wasm_base64]);

  return (
    <div className="h-48 bg-dark-sidebar border-t border-dark-border flex flex-col font-mono text-xs select-none">
      {/* Header */}
      <div className="h-8 px-3 border-b border-dark-border flex items-center justify-between bg-dark-surface/50 text-[11px] text-text-secondary">
        <div className="flex items-center space-x-2">
          <Terminal className="w-3.5 h-3.5 text-lavender-muted" />
          <span className="font-semibold text-text-primary uppercase tracking-wider text-[10px]">
            Runtime Console & Execution
          </span>
        </div>
        <button
          onClick={onClearLogs}
          className="flex items-center space-x-1 hover:text-text-primary transition-colors text-[10px]"
          title="Clear console output"
        >
          <Trash2 className="w-3 h-3" />
          <span>Clear</span>
        </button>
      </div>

      {/* Content: Split between Results and Log stream */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Execution Status Card */}
        <div className="w-80 border-r border-dark-border p-3 overflow-y-auto space-y-2 bg-dark-surface/20">
          <div className="text-[10px] uppercase tracking-wider text-text-secondary font-semibold">
            Execution Verification
          </div>

          {compileResult?.runtime_result ? (
            <div className="space-y-2">
              {/* Backend wasmtime result */}
              <div className="p-2 rounded border border-mint-success/30 bg-mint-success/5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="flex items-center space-x-1 text-mint-success text-[11px] font-bold">
                    <Shield className="w-3.5 h-3.5" />
                    <span>wasmtime (Backend)</span>
                  </span>
                  <span className="text-[10px] text-text-secondary">
                    {compileResult.runtime_result.duration_ms} ms
                  </span>
                </div>
                <div className="text-sm font-bold text-mint-success">
                  Return code: {compileResult.runtime_result.return_value}
                </div>
              </div>

              {/* Browser V8 WebAssembly API result */}
              {browserResult.tested && (
                <div className="p-2 rounded border border-lavender-strong/30 bg-lavender-strong/5 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center space-x-1 text-lavender-strong text-[11px] font-bold">
                      <Globe className="w-3.5 h-3.5" />
                      <span>WebAssembly API (Browser)</span>
                    </span>
                    <span className="text-[10px] text-text-secondary">
                      {browserResult.timeMs} ms
                    </span>
                  </div>
                  {browserResult.error ? (
                    <div className="text-[11px] text-red-error">{browserResult.error}</div>
                  ) : (
                    <div className="text-sm font-bold text-lavender-strong">
                      Return code: {browserResult.val}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-text-secondary text-[11px] py-4 text-center">
              No module executed yet. Click "Compile & Run" to execute WebAssembly.
            </div>
          )}
        </div>

        {/* Right: Compiler Log Stream */}
        <div className="flex-1 p-3 overflow-y-auto space-y-1 text-[11px]">
          {logs.length === 0 ? (
            <div className="text-text-secondary/50">Ready. Compiler logs will appear here.</div>
          ) : (
            logs.map((log, i) => {
              const isError = log.includes('ERROR') || log.includes('FATAL');
              const isSuccess = log.includes('complete') || log.includes('succeeded') || log.includes('returned') || log.includes('PASSED');
              let textColor = 'text-text-secondary';
              if (isError) textColor = 'text-red-error font-semibold';
              else if (isSuccess) textColor = 'text-mint-success';
              return (
                <div key={i} className={`${textColor} leading-tight`}>
                  {log}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
