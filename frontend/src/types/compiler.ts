export interface SourceLocation {
  line: number;
  column: number;
  end_line: number;
  end_column: number;
}

export interface Diagnostic {
  stage: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  code?: string;
  location?: SourceLocation;
}

export interface StageMetric {
  name: string;
  status: 'waiting' | 'running' | 'success' | 'failed' | 'skipped';
  duration_ms: number;
  details?: string;
}

export interface RuntimeResult {
  success: boolean;
  return_value?: number;
  duration_ms: number;
  exports: string[];
  trap?: string;
  error?: string;
}

export interface OptimizationMetrics {
  level: string;
  initial_instructions: number;
  optimized_instructions: number;
  instructions_eliminated: number;
  passes_applied: string[];
}

export interface CompileResponse {
  success: boolean;
  filename: string;
  optimization_level: string;
  total_duration_ms: number;
  diagnostics: Diagnostic[];
  stage_metrics: StageMetric[];
  ast_tree?: Record<string, any>;
  raw_ir?: string;
  optimized_ir?: string;
  wat?: string;
  wasm_base64?: string;
  wasm_size_bytes: number;
  optimization_metrics?: OptimizationMetrics;
  runtime_result?: RuntimeResult;
  compiler_logs: string[];
}

export interface CompareResponse {
  o0_result: CompileResponse;
  o2_result: CompileResponse;
  ir_diff?: string;
}

export interface ExampleProgram {
  id: string;
  name: string;
  filename: string;
  description: string;
  expected_output: number;
  source: string;
}

export interface CompilerInfo {
  llvm_version: string;
  clang_version: string;
  wabt_version: string;
  wasmtime_version: string;
  target_triple: string;
  data_layout: string;
  supported_optimizations: string[];
}
