import React, { useState } from 'react';
import {
  Layers, AlertTriangle,
  Download, Copy, Check, FileDown
} from 'lucide-react';
import type { CompileResponse, CompareResponse } from '../types/compiler';

interface ArtifactInspectorProps {
  compileResult: CompileResponse | null;
  compareResult: CompareResponse | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onJumpToLine?: (line: number, column: number) => void;
}

export const ArtifactInspector: React.FC<ArtifactInspectorProps> = ({
  compileResult,
  compareResult,
  activeTab,
  setActiveTab,
  onJumpToLine,
}) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadFile = (content: string, filename: string, mime = 'text/plain') => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadWasmBinary = () => {
    if (!compileResult?.wasm_base64) return;
    const binaryStr = atob(compileResult.wasm_base64);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: 'application/wasm' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${compileResult.filename.replace('.mini', '')}.wasm`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadReport = () => {
    if (!compileResult) return;
    const report = {
      project: "WASM Lab",
      filename: compileResult.filename,
      optimization_level: compileResult.optimization_level,
      total_duration_ms: compileResult.total_duration_ms,
      wasm_size_bytes: compileResult.wasm_size_bytes,
      stage_metrics: compileResult.stage_metrics,
      optimization_metrics: compileResult.optimization_metrics,
      runtime_result: compileResult.runtime_result,
      diagnostics: compileResult.diagnostics,
      compiler_logs: compileResult.compiler_logs,
      timestamp: new Date().toISOString(),
    };
    downloadFile(JSON.stringify(report, null, 2), `compilation_report_${compileResult.filename}.json`, 'application/json');
  };

  const tabs = [
    { id: 'opt_ir', label: 'Optimized IR', count: compileResult?.optimized_ir ? 'LLVM' : null },
    { id: 'raw_ir', label: 'Initial IR', count: compileResult?.raw_ir ? 'O0' : null },
    { id: 'wat', label: 'WebAssembly (WAT)', count: compileResult?.wat ? 'WAT' : null },
    { id: 'compare', label: 'Optimization Diff', count: compareResult?.ir_diff ? 'Diff' : null },
    { id: 'ast', label: 'AST Tree', count: compileResult?.ast_tree ? 'AST' : null },
    { id: 'diagnostics', label: 'Diagnostics', count: compileResult?.diagnostics?.length || null },
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-dark-bg border-l border-dark-border select-none">
      {/* Header Tabs & Actions */}
      <div className="h-10 px-2 bg-dark-sidebar border-b border-dark-border flex items-center justify-between text-xs">
        <div className="flex items-center space-x-1 overflow-x-auto">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-md font-mono text-[11px] font-medium transition-colors flex items-center space-x-1.5 ${
                  isActive
                    ? 'bg-dark-surface text-lavender-strong border border-dark-border'
                    : 'text-text-secondary hover:text-text-primary hover:bg-dark-surface/50'
                }`}
              >
                <span>{tab.label}</span>
                {tab.count !== null && (
                  <span className="px-1 py-0.2 rounded text-[9px] bg-dark-bg text-lavender-muted border border-dark-border">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Export / Download Menu */}
        {compileResult && (
          <div className="flex items-center space-x-1">
            <button
              onClick={() => {
                const currentContent =
                  activeTab === 'raw_ir'
                    ? compileResult.raw_ir
                    : activeTab === 'opt_ir'
                    ? compileResult.optimized_ir
                    : activeTab === 'wat'
                    ? compileResult.wat
                    : activeTab === 'compare'
                    ? compareResult?.ir_diff
                    : activeTab === 'ast'
                    ? JSON.stringify(compileResult.ast_tree, null, 2)
                    : null;
                if (currentContent) copyToClipboard(currentContent);
              }}
              className="p-1.5 rounded hover:bg-dark-surface text-text-secondary hover:text-text-primary"
              title="Copy current tab artifact to clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-mint-success" /> : <Copy className="w-3.5 h-3.5" />}
            </button>

            {compileResult.wasm_base64 && (
              <button
                onClick={downloadWasmBinary}
                className="flex items-center space-x-1 px-2 py-1 rounded bg-lavender-strong/10 hover:bg-lavender-strong/20 text-lavender-strong border border-lavender-strong/30 text-[10px] font-mono font-medium"
                title="Download genuine .wasm binary file"
              >
                <Download className="w-3 h-3" />
                <span>.WASM</span>
              </button>
            )}

            <button
              onClick={downloadReport}
              className="p-1.5 rounded hover:bg-dark-surface text-text-secondary hover:text-text-primary"
              title="Download compilation JSON benchmark report"
            >
              <FileDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Tab Content Display */}
      <div className="flex-1 overflow-auto p-3 font-mono text-xs text-text-primary leading-relaxed">
        {!compileResult ? (
          <div className="h-full flex flex-col items-center justify-center text-text-secondary space-y-2">
            <Layers className="w-8 h-8 text-dark-border" />
            <p className="text-sm">Click "Compile & Run" to inspect intermediate representations</p>
            <p className="text-xs text-text-secondary/70">LLVM IR, Optimized IR, WebAssembly text, and optimization comparisons will appear here.</p>
          </div>
        ) : (
          <>
            {/* Tab: Optimized IR */}
            {activeTab === 'opt_ir' && (
              <div className="space-y-2">
                {compileResult.optimization_metrics && (
                  <div className="p-2.5 rounded-lg bg-dark-surface border border-dark-border flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-3">
                      <div>
                        <span className="text-text-secondary">Instructions: </span>
                        <span className="text-text-primary font-bold">
                          {compileResult.optimization_metrics.initial_instructions} → {compileResult.optimization_metrics.optimized_instructions}
                        </span>
                      </div>
                      <div className="px-2 py-0.5 rounded bg-mint-success/10 text-mint-success border border-mint-success/20">
                        -{compileResult.optimization_metrics.instructions_eliminated} eliminated
                      </div>
                    </div>
                    <div className="text-[11px] text-text-secondary">
                      Target: wasm32-unknown-unknown
                    </div>
                  </div>
                )}
                <pre className="p-3 rounded-lg bg-dark-surface/60 border border-dark-border overflow-x-auto text-[12px] text-lavender-muted">
                  {compileResult.optimized_ir || '; No optimized IR emitted'}
                </pre>
              </div>
            )}

            {/* Tab: Initial IR */}
            {activeTab === 'raw_ir' && (
              <div className="space-y-2">
                <div className="text-[11px] text-text-secondary pb-1">
                  Pre-optimization LLVM Intermediate Representation (with memory allocas, stores, loads):
                </div>
                <pre className="p-3 rounded-lg bg-dark-surface/60 border border-dark-border overflow-x-auto text-[12px] text-text-primary">
                  {compileResult.raw_ir || '; No LLVM IR emitted'}
                </pre>
              </div>
            )}

            {/* Tab: WebAssembly Text (WAT) */}
            {activeTab === 'wat' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px] text-text-secondary pb-1">
                  <span>Disassembled WebAssembly Text Format (via WABT wasm2wat):</span>
                  <span className="text-mint-success font-medium">{compileResult.wasm_size_bytes} bytes binary</span>
                </div>
                <pre className="p-3 rounded-lg bg-dark-surface/60 border border-dark-border overflow-x-auto text-[12px] text-mint-success">
                  {compileResult.wat || '; No WAT disassembled'}
                </pre>
              </div>
            )}

            {/* Tab: Optimization Diff */}
            {activeTab === 'compare' && (
              <div className="space-y-3">
                <div className="p-2.5 rounded-lg bg-dark-surface border border-dark-border text-xs">
                  <div className="font-semibold text-text-primary mb-1">LLVM Pass Transformations:</div>
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-text-secondary">
                    <div>
                      <span className="font-mono text-lavender-muted">O0: </span>Preserves allocas & debugging layout
                    </div>
                    <div>
                      <span className="font-mono text-mint-success">O2: </span>mem2reg + instcombine + SCCP + DCE + SimplifyCFG
                    </div>
                  </div>
                </div>

                {compareResult?.ir_diff ? (
                  <div>
                    <div className="text-[11px] text-text-secondary mb-1">Unified Line-by-Line IR Diff:</div>
                    <pre className="p-3 rounded-lg bg-dark-surface/60 border border-dark-border overflow-x-auto text-[12px]">
                      {compareResult.ir_diff.split('\n').map((line, idx) => {
                        let color = 'text-text-secondary';
                        let bg = '';
                        if (line.startsWith('+')) {
                          color = 'text-mint-success';
                          bg = 'bg-mint-success/10';
                        } else if (line.startsWith('-')) {
                          color = 'text-red-error';
                          bg = 'bg-red-error/10';
                        } else if (line.startsWith('@@')) {
                          color = 'text-lavender-muted';
                        }
                        return (
                          <div key={idx} className={`${color} ${bg} px-1 rounded`}>
                            {line}
                          </div>
                        );
                      })}
                    </pre>
                  </div>
                ) : (
                  <div className="text-text-secondary text-center py-6">
                    Click "Compare" or compile to view side-by-side optimization diff
                  </div>
                )}
              </div>
            )}

            {/* Tab: AST Tree */}
            {activeTab === 'ast' && (
              <div className="space-y-2">
                <div className="text-[11px] text-text-secondary pb-1">
                  Abstract Syntax Tree (AST) Hierarchy:
                </div>
                <pre className="p-3 rounded-lg bg-dark-surface/60 border border-dark-border overflow-x-auto text-[12px] text-text-primary">
                  {compileResult.ast_tree
                    ? JSON.stringify(compileResult.ast_tree, null, 2)
                    : '// No AST available'}
                </pre>
              </div>
            )}

            {/* Tab: Diagnostics */}
            {activeTab === 'diagnostics' && (
              <div className="space-y-2">
                {compileResult.diagnostics.length === 0 ? (
                  <div className="text-center py-8 text-mint-success flex flex-col items-center space-y-1">
                    <span className="font-medium text-sm">No compiler errors or warnings</span>
                    <span className="text-xs text-text-secondary">Program is semantically valid and verified.</span>
                  </div>
                ) : (
                  compileResult.diagnostics.map((diag, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-red-error/10 border border-red-error/30 text-xs flex flex-col space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-1.5 font-bold text-red-error">
                          <AlertTriangle className="w-4 h-4" />
                          <span>[{diag.code || 'ERROR'}] in {diag.stage}</span>
                        </div>
                        {diag.location && onJumpToLine && (
                          <button
                            onClick={() => onJumpToLine(diag.location!.line, diag.location!.column)}
                            className="text-[11px] text-lavender-muted hover:underline font-mono"
                          >
                            Line {diag.location.line}, Col {diag.location.column} → Jump
                          </button>
                        )}
                      </div>
                      <p className="text-text-primary font-mono text-[12px]">{diag.message}</p>
                    </div>
                  ))
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
