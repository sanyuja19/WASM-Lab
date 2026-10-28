import React from 'react';
import { Target, Binary, Layers } from 'lucide-react';
import type { CompileResponse } from '../types/compiler';

interface StatusBarProps {
  lastResult: CompileResponse | null;
  optimization: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({ lastResult, optimization }) => {
  return (
    <footer className="h-7 bg-dark-sidebar border-t border-dark-border px-3 flex items-center justify-between text-[11px] font-mono text-text-secondary z-20 select-none">
      <div className="flex items-center space-x-4">
        {/* Target Triple */}
        <div className="flex items-center space-x-1.5" title="Machine-Independent Target Triple">
          <Target className="w-3.5 h-3.5 text-lavender-muted" />
          <span>wasm32-unknown-unknown</span>
        </div>

        {/* LLVM IR Engine */}
        <div className="flex items-center space-x-1.5" title="LLVM Intermediate Representation Engine">
          <Layers className="w-3.5 h-3.5 text-lavender-muted" />
          <span>LLVM IR (NewPM {optimization})</span>
        </div>

        {/* Runtime Engine */}
        <div className="flex items-center space-x-1.5" title="Execution Environments">
          <Binary className="w-3.5 h-3.5 text-mint-success" />
          <span>Runtime: wasmtime + WebAssembly API</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {lastResult && (
          <>
            <div className="flex items-center space-x-1">
              <span className="text-text-secondary">Binary Size:</span>
              <span className="text-text-primary font-medium">{lastResult.wasm_size_bytes} B</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-text-secondary">Pipeline Time:</span>
              <span className="text-mint-success font-medium">{lastResult.total_duration_ms.toFixed(1)} ms</span>
            </div>
            {lastResult.runtime_result?.return_value !== undefined && (
              <div className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-mint-success/10 text-mint-success border border-mint-success/20">
                <span>Result: {lastResult.runtime_result.return_value}</span>
              </div>
            )}
          </>
        )}
        <div className="text-text-secondary hidden sm:inline">
          UTF-8
        </div>
      </div>
    </footer>
  );
};
