import type {
  CompileResponse,
  CompareResponse,
  CompilerInfo,
  ExampleProgram
} from '../types/compiler';

const API_BASE = '/api';

export async function checkHealth(): Promise<{ healthy: boolean; data?: any }> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return { healthy: false };
    const data = await res.json();
    return { healthy: true, data };
  } catch {
    return { healthy: false };
  }
}

export async function fetchCompilerInfo(): Promise<CompilerInfo | null> {
  try {
    const res = await fetch(`${API_BASE}/compiler-info`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchExamples(): Promise<ExampleProgram[]> {
  try {
    const res = await fetch(`${API_BASE}/examples`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return getDefaultExamples();
    return await res.json();
  } catch {
    return getDefaultExamples();
  }
}

export async function compileProgram(
  source: string,
  filename = 'main.mini',
  optimization = 'O2',
  execute = true
): Promise<CompileResponse> {
  const res = await fetch(`${API_BASE}/compile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, filename, optimization, execute }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errData.detail || `Server returned ${res.status}`);
  }

  return await res.json();
}

export async function compareOptimizations(
  source: string,
  filename = 'main.mini'
): Promise<CompareResponse> {
  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, filename }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Comparison request failed' }));
    throw new Error(errData.detail || `Server returned ${res.status}`);
  }

  return await res.json();
}

export function getDefaultExamples(): ExampleProgram[] {
  return [
    {
      id: 'arithmetic',
      name: 'Basic Arithmetic',
      filename: 'arithmetic.mini',
      description: 'Standard arithmetic with operator precedence: 10 + 20 * 2 = 50',
      expected_output: 50,
      source: `fn main() -> i32 {\n    let x: i32 = 10;\n    let y: i32 = 20;\n    return x + y * 2;\n}`,
    },
    {
      id: 'conditionals',
      name: 'Conditionals & Logic',
      filename: 'conditionals.mini',
      description: 'If-else branch selection and comparisons: max(45, 90) = 90',
      expected_output: 90,
      source: `fn max(a: i32, b: i32) -> i32 {\n    if a > b {\n        return a;\n    } else {\n        return b;\n    }\n}\n\nfn main() -> i32 {\n    let x: i32 = 45;\n    let y: i32 = 90;\n    return max(x, y);\n}`,
    },
    {
      id: 'loops',
      name: 'While Loops & Scopes',
      filename: 'loops.mini',
      description: 'While loop computing sum of numbers from 1 to 10 = 55',
      expected_output: 55,
      source: `fn sum_to_n(n: i32) -> i32 {\n    let sum: i32 = 0;\n    let i: i32 = 1;\n    while i <= n {\n        sum = sum + i;\n        i = i + 1;\n    }\n    return sum;\n}\n\nfn main() -> i32 {\n    return sum_to_n(10);\n}`,
    },
    {
      id: 'functions',
      name: 'Recursive Functions',
      filename: 'functions.mini',
      description: 'Recursive Fibonacci sequence computing fib(10) = 55',
      expected_output: 55,
      source: `fn fib(n: i32) -> i32 {\n    if n <= 1 {\n        return n;\n    }\n    return fib(n - 1) + fib(n - 2);\n}\n\nfn main() -> i32 {\n    return fib(10);\n}`,
    },
    {
      id: 'semantic_errors',
      name: 'Semantic Errors Demo',
      filename: 'semantic-errors.mini',
      description: 'Demonstration of duplicate declarations, type mismatches, and undeclared variables',
      expected_output: 0,
      source: `fn calculate(a: i32) -> i32 {\n    let x: i32 = 10;\n    let x: i32 = 20;\n    let z: bool = true;\n    let result: i32 = a + z;\n    return unknown_var;\n}\n\nfn main() -> i32 {\n    return calculate(5);\n}`,
    },
  ];
}
