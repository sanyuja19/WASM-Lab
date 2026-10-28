import React from 'react';
import {
  FileText, ShieldCheck, Binary, CheckCircle2,
  Cpu, Cog, CheckSquare, Play
} from 'lucide-react';
import type { StageMetric } from '../types/compiler';

interface PipelineVisualizerProps {
  metrics: StageMetric[];
  isCompiling: boolean;
}

const STAGE_CONFIGS: Record<string, { label: string; icon: any; description: string }> = {
  frontend: {
    label: '1. Frontend (Lex & Parse)',
    icon: FileText,
    description: 'MiniLang EBNF grammar to Abstract Syntax Tree',
  },
  semantic: {
    label: '2. Semantic Analysis',
    icon: ShieldCheck,
    description: 'Type checking, scopes & symbol resolution',
  },
  ir_generation: {
    label: '3. LLVM IR Generation',
    icon: Binary,
    description: 'Typed SSA IR construction (wasm32 triple)',
  },
  llvm_verification: {
    label: '4. LLVM Verification',
    icon: CheckSquare,
    description: 'Official LLVM module and CFG verification',
  },
  optimization: {
    label: '5. LLVM Optimization',
    icon: Cpu,
    description: 'NewPM passes (mem2reg, instcombine, SCCP)',
  },
  wasm_codegen: {
    label: '6. WASM Codegen',
    icon: Cog,
    description: 'Native LLVM backend emitting wasm32 binary',
  },
  wasm_validation: {
    label: '7. WABT Validation',
    icon: CheckCircle2,
    description: 'WABT wasm-validate & wasm2wat disassembly',
  },
  runtime: {
    label: '8. Runtime Execution',
    icon: Play,
    description: 'Execution in wasmtime runtime and browser',
  },
};

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({
  metrics,
  isCompiling,
}) => {
  // If no metrics yet, create initial default waiting stages
  const displayStages = Object.keys(STAGE_CONFIGS).map((key) => {
    const existing = metrics.find((m) => m.name === key);
    return (
      existing || {
        name: key,
        status: 'waiting' as const,
        duration_ms: 0,
      }
    );
  });

  return (
    <div className="bg-dark-sidebar border-b border-dark-border p-3 select-none">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-text-primary uppercase tracking-wider font-mono">
            Compilation Pipeline
          </span>
          <span className="text-[11px] text-text-secondary">
            (8 verifiable machine-independent stages)
          </span>
        </div>
        {isCompiling && (
          <span className="text-xs text-lavender-muted font-mono flex items-center space-x-1 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-lavender-strong" />
            <span>Processing pipeline...</span>
          </span>
        )}
      </div>

      {/* Pipeline Grid / Flow */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
        {displayStages.map((stage) => {
          const config = STAGE_CONFIGS[stage.name] || {
            label: stage.name,
            icon: Cog,
            description: '',
          };
          const Icon = config.icon;

          let statusBg = 'bg-dark-surface border-dark-border text-text-secondary';
          let iconColor = 'text-text-secondary';
          let statusText = 'Waiting';

          if (stage.status === 'success') {
            statusBg = 'bg-mint-success/5 border-mint-success/30 text-text-primary shadow-sm';
            iconColor = 'text-mint-success';
            statusText = `${stage.duration_ms.toFixed(1)} ms`;
          } else if (stage.status === 'running') {
            statusBg = 'bg-lavender-strong/10 border-lavender-strong/40 text-lavender-strong animate-pulse';
            iconColor = 'text-lavender-strong';
            statusText = 'Running';
          } else if (stage.status === 'failed') {
            statusBg = 'bg-red-error/10 border-red-error/40 text-red-error';
            iconColor = 'text-red-error';
            statusText = 'Failed';
          } else if (stage.status === 'skipped') {
            statusBg = 'bg-dark-surface/40 border-dark-border/40 text-text-secondary/50';
            iconColor = 'text-text-secondary/40';
            statusText = 'Skipped';
          }

          return (
            <div
              key={stage.name}
              className={`p-2 rounded-lg border flex flex-col justify-between transition-all ${statusBg}`}
              title={config.description}
            >
              <div className="flex items-center justify-between mb-1">
                <Icon className={`w-4 h-4 ${iconColor}`} />
                <span className="text-[10px] font-mono font-medium">
                  {statusText}
                </span>
              </div>
              <div>
                <p className="text-[11px] font-medium tracking-tight truncate">
                  {config.label}
                </p>
                <p className="text-[9px] text-text-secondary truncate mt-0.5">
                  {config.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
