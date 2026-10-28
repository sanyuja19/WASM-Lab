import React from 'react';
import { X, Cpu } from 'lucide-react';
import type { CompilerInfo } from '../types/compiler';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  compilerInfo: CompilerInfo | null;
  isBackendConnected: boolean;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  compilerInfo,
  isBackendConnected,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm select-none p-4">
      <div className="w-full max-w-lg bg-dark-sidebar border border-dark-border rounded-xl shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="px-5 py-4 border-b border-dark-border flex items-center justify-between bg-dark-surface/50">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-lavender-strong" />
            <h2 className="text-sm font-bold text-text-primary tracking-tight">
              Compiler Framework & Toolchain Configuration
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-text-secondary hover:text-text-primary hover:bg-dark-hover"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 text-xs">
          {/* Status Alert */}
          <div className="p-3 rounded-lg border border-dark-border bg-dark-surface flex items-center justify-between">
            <div>
              <span className="font-semibold text-text-primary">Toolchain Status: </span>
              <span className={isBackendConnected ? 'text-mint-success font-medium' : 'text-red-error font-medium'}>
                {isBackendConnected ? 'All components verified & online' : 'Backend offline (preview mode)'}
              </span>
            </div>
            <span className="px-2 py-0.5 rounded bg-dark-bg text-lavender-muted font-mono text-[10px] border border-dark-border">
              v1.0.0
            </span>
          </div>

          {/* Details Table */}
          <div className="space-y-2 font-mono text-[11px]">
            <div className="flex justify-between py-1.5 border-b border-dark-border/50">
              <span className="text-text-secondary">LLVM Core Binding:</span>
              <span className="text-text-primary font-medium">{compilerInfo?.llvm_version || '22.1.0'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-dark-border/50">
              <span className="text-text-secondary">Native LLVM Compiler:</span>
              <span className="text-text-primary font-medium">{compilerInfo?.clang_version || 'Zig 0.14.0 (LLVM 19 backend)'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-dark-border/50">
              <span className="text-text-secondary">Target Triple:</span>
              <span className="text-lavender-muted font-medium">{compilerInfo?.target_triple || 'wasm32-unknown-unknown'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-dark-border/50">
              <span className="text-text-secondary">WABT Specification Validator:</span>
              <span className="text-text-primary font-medium">{compilerInfo?.wabt_version || '1.0.42'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-dark-border/50">
              <span className="text-text-secondary">Execution Runtime:</span>
              <span className="text-mint-success font-medium">wasmtime 50.0.1 + Browser WebAssembly</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-dark-border/50">
              <span className="text-text-secondary">Supported Optimizations:</span>
              <span className="text-text-primary">O0 (Debug), O2 (NewPM Pipeline)</span>
            </div>
          </div>

          {/* Architecture Note */}
          <div className="p-3 rounded-lg bg-dark-surface/40 border border-dark-border text-[11px] text-text-secondary leading-relaxed">
            <span className="text-text-primary font-medium">Machine Independence: </span>
            The MiniLang frontend produces target-neutral LLVM Intermediate Representation. The IR is optimized using LLVM's modern Pass Manager (mem2reg, SCCP, DCE, SimplifyCFG) before the WebAssembly backend generates freestanding wasm32 binaries.
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-dark-border bg-dark-surface/30 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-dark-hover hover:bg-dark-surface text-text-primary text-xs font-medium border border-dark-border transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
