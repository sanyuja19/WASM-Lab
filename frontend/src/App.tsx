import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { editor } from 'monaco-editor';

import { Navbar } from './components/Navbar';
import { StatusBar } from './components/StatusBar';
import { ActivityRail } from './components/ActivityRail';
import { FileExplorer } from './components/FileExplorer';
import { Editor } from './components/Editor';
import { PipelineVisualizer } from './components/PipelineVisualizer';
import { ArtifactInspector } from './components/ArtifactInspector';
import { RuntimeConsole } from './components/RuntimeConsole';
import { SettingsModal } from './components/SettingsModal';
import { DemoWarning } from './components/DemoWarning';

import {
  checkHealth,
  fetchCompilerInfo,
  fetchExamples,
  compileProgram,
  compareOptimizations,
  getDefaultExamples,
} from './services/api';

import type {
  CompileResponse,
  CompareResponse,
  CompilerInfo,
  ExampleProgram,
} from './types/compiler';

export const App: React.FC = () => {
  const [examples, setExamples] = useState<ExampleProgram[]>(getDefaultExamples());
  const [currentFile, setCurrentFile] = useState<string>('arithmetic.mini');
  const [sourceCode, setSourceCode] = useState<string>(examples[0].source);
  const [optimization, setOptimization] = useState<string>('O2');

  const [compileResult, setCompileResult] = useState<CompileResponse | null>(null);
  const [compareResult, setCompareResult] = useState<CompareResponse | null>(null);
  const [compilerInfo, setCompilerInfo] = useState<CompilerInfo | null>(null);

  const [isCompiling, setIsCompiling] = useState<boolean>(false);
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(true);
  const [isRetryingConnection, setIsRetryingConnection] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  const [activeRailPanel, setActiveRailPanel] = useState<string>('files');
  const [activeArtifactTab, setActiveArtifactTab] = useState<string>('opt_ir');
  const [logs, setLogs] = useState<string[]>([]);

  const editorInstanceRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  // Initialize toolchain information and health check
  const refreshToolchain = useCallback(async () => {
    setIsRetryingConnection(true);
    const health = await checkHealth();
    setIsBackendConnected(health.healthy);
    if (health.healthy) {
      const [info, exList] = await Promise.all([
        fetchCompilerInfo(),
        fetchExamples(),
      ]);
      if (info) setCompilerInfo(info);
      if (exList && exList.length > 0) setExamples(exList);
    }
    setIsRetryingConnection(false);
  }, []);

  useEffect(() => {
    refreshToolchain();
  }, [refreshToolchain]);

  // Handle compilation
  const handleCompile = useCallback(async () => {
    if (isCompiling || !sourceCode.trim()) return;

    setIsCompiling(true);
    const startTs = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${startTs}] Initiating compilation of '${currentFile}' (${optimization})...`]);

    try {
      // 1. Run compilation
      const result = await compileProgram(sourceCode, currentFile, optimization, true);
      setCompileResult(result);

      if (result.compiler_logs && result.compiler_logs.length > 0) {
        setLogs((prev) => [...prev, ...result.compiler_logs]);
      }

      if (result.success) {
        setLogs((prev) => [
          ...prev,
          `[${new Date().toLocaleTimeString()}] Compilation & execution SUCCEEDED. Return value: ${
            result.runtime_result?.return_value ?? 'N/A'
          }`,
        ]);
        setActiveArtifactTab('opt_ir');
      } else {
        setLogs((prev) => [
          ...prev,
          `[${new Date().toLocaleTimeString()}] Compilation reported diagnostic error(s).`,
        ]);
        setActiveArtifactTab('diagnostics');
      }

      // 2. Fetch O0 vs O2 comparison in background if compilation succeeded
      if (result.success) {
        compareOptimizations(sourceCode, currentFile)
          .then((comp) => setCompareResult(comp))
          .catch(() => {});
      }
    } catch (err: any) {
      setLogs((prev) => [
        ...prev,
        `[${new Date().toLocaleTimeString()}] ERROR: ${err?.message || 'Failed to communicate with compiler'}`,
      ]);
      setIsBackendConnected(false);
    } finally {
      setIsCompiling(false);
    }
  }, [currentFile, isCompiling, optimization, sourceCode]);

  // Keyboard shortcut Ctrl+Enter to compile
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleCompile();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleCompile]);

  // Jump to specific line/column in Monaco Editor
  const handleJumpToLine = (line: number, column: number) => {
    if (!editorInstanceRef.current) return;
    editorInstanceRef.current.revealLineInCenter(line);
    editorInstanceRef.current.setPosition({ lineNumber: line, column });
    editorInstanceRef.current.focus();
  };

  // Select example program
  const handleSelectExample = (ex: ExampleProgram) => {
    setCurrentFile(ex.filename);
    setSourceCode(ex.source);
    setCompileResult(null);
    setCompareResult(null);
  };

  // Create new custom file
  const handleNewFile = () => {
    const filename = `custom_${Date.now().toString().slice(-4)}.mini`;
    setCurrentFile(filename);
    setSourceCode(`fn main() -> i32 {\n    // Write MiniLang code here\n    let a: i32 = 100;\n    let b: i32 = 25;\n    return a / b;\n}\n`);
    setCompileResult(null);
    setCompareResult(null);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-dark-bg text-text-primary overflow-hidden font-sans">
      {/* Top Navigation */}
      <Navbar
        currentFile={currentFile}
        isBackendConnected={isBackendConnected}
        isCompiling={isCompiling}
        onCompile={handleCompile}
        onOpenSettings={() => setIsSettingsOpen(true)}
        activeView={activeRailPanel}
        setActiveView={setActiveRailPanel}
        optimization={optimization}
        setOptimization={setOptimization}
      />

      {/* Demo Warning Banner if backend disconnected */}
      {!isBackendConnected && (
        <DemoWarning onRetry={refreshToolchain} isRetrying={isRetryingConnection} />
      )}

      {/* Main Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Activity Rail */}
        <ActivityRail
          activePanel={activeRailPanel}
          setActivePanel={setActiveRailPanel}
          errorCount={compileResult?.diagnostics?.filter((d) => d.severity === 'error').length || 0}
        />

        {/* Collapsible Left Sidebar: File Explorer */}
        {activeRailPanel === 'files' && (
          <FileExplorer
            examples={examples}
            activeFilename={currentFile}
            onSelectFile={handleSelectExample}
            onNewFile={handleNewFile}
          />
        )}

        {/* Center Workspace: Editor & Output Panels */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Top Pipeline Stages Visualizer */}
          <PipelineVisualizer
            metrics={compileResult?.stage_metrics || []}
            isCompiling={isCompiling}
          />

          {/* Center Split: Monaco Editor (Left) & Artifact Inspector (Right) */}
          <div className="flex-1 flex min-h-0 overflow-hidden">
            {/* Source Editor Panel */}
            <div className="flex-1 flex flex-col min-w-0 bg-dark-sidebar relative">
              <div className="h-8 px-3 border-b border-dark-border flex items-center justify-between bg-dark-surface/40 text-[11px] text-text-secondary select-none">
                <span className="font-mono">{currentFile}</span>
                <span className="text-[10px] text-text-secondary/60">MiniLang Source</span>
              </div>
              <div className="flex-1 min-h-0">
                <Editor
                  value={sourceCode}
                  onChange={setSourceCode}
                  diagnostics={compileResult?.diagnostics || []}
                  onMount={(instance) => {
                    editorInstanceRef.current = instance;
                  }}
                />
              </div>
            </div>

            {/* Right Artifact Inspector Panel */}
            <div className="w-[45%] flex flex-col min-w-[320px]">
              <ArtifactInspector
                compileResult={compileResult}
                compareResult={compareResult}
                activeTab={activeArtifactTab}
                setActiveTab={setActiveArtifactTab}
                onJumpToLine={handleJumpToLine}
              />
            </div>
          </div>

          {/* Bottom Runtime Console */}
          <RuntimeConsole
            compileResult={compileResult}
            logs={logs}
            onClearLogs={() => setLogs([])}
          />
        </div>
      </div>

      {/* Secondary Status Bar */}
      <StatusBar lastResult={compileResult} optimization={optimization} />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        compilerInfo={compilerInfo}
        isBackendConnected={isBackendConnected}
      />
    </div>
  );
};
