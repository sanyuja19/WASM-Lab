import React from 'react';
import { Cpu, Settings as SettingsIcon, Play, RefreshCw } from 'lucide-react';

interface NavbarProps {
  currentFile: string;
  isBackendConnected: boolean;
  isCompiling: boolean;
  onCompile: () => void;
  onOpenSettings: () => void;
  activeView: string;
  setActiveView: (view: string) => void;
  optimization: string;
  setOptimization: (opt: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentFile,
  isBackendConnected,
  isCompiling,
  onCompile,
  onOpenSettings,
  optimization,
  setOptimization,
}) => {
  return (
    <header className="h-14 border-b border-dark-border bg-dark-sidebar flex items-center justify-between px-4 z-20 select-none">
      {/* Brand & Breadcrumbs */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-lavender-strong/10 border border-lavender-strong/30 flex items-center justify-center text-lavender-strong">
          <Cpu className="w-5 h-5" />
        </div>
        <div className="flex items-center space-x-2">
          <span className="font-bold text-text-primary tracking-tight text-base">WASM Lab</span>
          <span className="text-dark-border text-sm">/</span>
          <span className="text-text-secondary text-xs font-mono uppercase tracking-wider bg-dark-surface px-2 py-0.5 rounded border border-dark-border">
            workspace
          </span>
          <span className="text-dark-border text-sm">/</span>
          <span className="text-lavender-muted text-xs font-mono font-medium">
            {currentFile}
          </span>
        </div>
      </div>

      {/* Center Controls: Optimization & Compile Action */}
      <div className="flex items-center space-x-3">
        {/* Optimization Level Toggle */}
        <div className="flex items-center bg-dark-surface p-1 rounded-lg border border-dark-border text-xs">
          <button
            onClick={() => setOptimization('O0')}
            className={`px-2.5 py-1 rounded font-mono font-semibold transition-colors ${
              optimization === 'O0'
                ? 'bg-dark-hover text-lavender-muted border border-dark-border'
                : 'text-text-secondary hover:text-text-primary'
            }`}
            title="O0: Minimal optimization (preserves variables and alloca layout for debugging)"
          >
            O0 (Debug)
          </button>
          <button
            onClick={() => setOptimization('O2')}
            className={`px-2.5 py-1 rounded font-mono font-semibold transition-colors ${
              optimization === 'O2'
                ? 'bg-lavender-strong/20 text-lavender-strong border border-lavender-strong/30'
                : 'text-text-secondary hover:text-text-primary'
            }`}
            title="O2: Aggressive LLVM optimization (mem2reg, instcombine, SCCP, DCE, SimplifyCFG)"
          >
            O2 (Standard)
          </button>
        </div>

        {/* Primary Compile Action */}
        <button
          onClick={onCompile}
          disabled={isCompiling}
          className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg font-medium text-xs shadow-sm transition-all ${
            isCompiling
              ? 'bg-dark-hover text-text-secondary cursor-not-allowed border border-dark-border'
              : 'bg-lavender-strong hover:bg-lavender-strong/90 text-dark-bg font-semibold active:scale-[0.98]'
          }`}
          title="Compile and run program (Ctrl + Enter)"
        >
          {isCompiling ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Compiling...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Compile & Run</span>
              <kbd className="hidden sm:inline-block ml-1 px-1.5 py-0.5 text-[10px] bg-dark-bg/20 rounded font-mono">
                ^Enter
              </kbd>
            </>
          )}
        </button>
      </div>

      {/* Right Controls: Health Status & Tools */}
      <div className="flex items-center space-x-3">
        {/* Connection Status Pill */}
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono border ${
            isBackendConnected
              ? 'bg-mint-success/10 text-mint-success border-mint-success/20'
              : 'bg-red-error/10 text-red-error border-red-error/20'
          }`}
          title={isBackendConnected ? 'Connected to local FastAPI + LLVM toolchain' : 'Backend is unreachable - running in preview mode'}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isBackendConnected ? 'bg-mint-success animate-pulse' : 'bg-red-error'
            }`}
          />
          <span className="text-[11px] font-medium">
            {isBackendConnected ? 'Backend Online' : 'Backend Offline'}
          </span>
        </div>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          className="p-1.5 rounded-lg text-text-secondary hover:text-text-primary hover:bg-dark-surface border border-transparent hover:border-dark-border transition-colors"
          title="Compiler & Toolchain Settings"
        >
          <SettingsIcon className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
