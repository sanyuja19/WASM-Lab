import React from 'react';
import { FileCode, Plus, Folder } from 'lucide-react';
import type { ExampleProgram } from '../types/compiler';

interface FileExplorerProps {
  examples: ExampleProgram[];
  activeFilename: string;
  onSelectFile: (example: ExampleProgram) => void;
  onNewFile: () => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  examples,
  activeFilename,
  onSelectFile,
  onNewFile,
}) => {
  return (
    <div className="w-64 bg-dark-sidebar border-r border-dark-border flex flex-col h-full select-none text-xs">
      {/* Header */}
      <div className="h-10 px-3 border-b border-dark-border flex items-center justify-between font-semibold text-text-secondary tracking-wider uppercase text-[10px]">
        <div className="flex items-center space-x-1.5">
          <Folder className="w-3.5 h-3.5 text-lavender-muted" />
          <span>Explorer</span>
        </div>
        <button
          onClick={onNewFile}
          className="p-1 rounded hover:bg-dark-surface text-text-secondary hover:text-text-primary"
          title="Create New MiniLang File"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Examples Tree */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="px-2 py-1 text-[10px] uppercase tracking-wider text-text-secondary font-mono">
          Sample Programs
        </div>
        {examples.map((ex) => {
          const isActive = activeFilename === ex.filename;
          return (
            <button
              key={ex.id}
              onClick={() => onSelectFile(ex)}
              className={`w-full text-left px-2.5 py-2 rounded-lg flex flex-col space-y-1 transition-all border ${
                isActive
                  ? 'bg-dark-surface border-lavender-strong/40 text-text-primary shadow-sm'
                  : 'border-transparent text-text-secondary hover:bg-dark-hover hover:text-text-primary'
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center space-x-2 font-mono">
                  <FileCode className={`w-3.5 h-3.5 ${isActive ? 'text-lavender-strong' : 'text-text-secondary'}`} />
                  <span className="font-medium text-xs">{ex.filename}</span>
                </div>
                {ex.expected_output !== 0 && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-dark-bg text-mint-success border border-dark-border">
                    ={ex.expected_output}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-text-secondary line-clamp-1 pl-5">
                {ex.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Language badge */}
      <div className="p-3 border-t border-dark-border bg-dark-surface/50 text-[11px] text-text-secondary flex items-center justify-between">
        <span>Language: MiniLang</span>
        <span className="text-lavender-muted font-mono text-[10px] bg-dark-bg px-1.5 py-0.5 rounded border border-dark-border">
          v1.0
        </span>
      </div>
    </div>
  );
};
