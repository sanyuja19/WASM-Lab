import React, { useEffect, useRef } from 'react';
import MonacoEditor from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import {
  MINILANG_LANGUAGE_ID,
  miniLangConfig,
  miniLangTokensProvider
} from '../languages/minilang';
import type { Diagnostic } from '../types/compiler';

interface EditorProps {
  value: string;
  onChange: (value: string) => void;
  diagnostics: Diagnostic[];
  onMount?: (editor: editor.IStandaloneCodeEditor) => void;
}

export const Editor: React.FC<EditorProps> = ({
  value,
  onChange,
  diagnostics,
  onMount,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<any>(null);

  const handleEditorWillMount = (monaco: any) => {
    monacoRef.current = monaco;

    // Register custom MiniLang language in Monaco
    if (!monaco.languages.getLanguages().some((l: any) => l.id === MINILANG_LANGUAGE_ID)) {
      monaco.languages.register({ id: MINILANG_LANGUAGE_ID });
      monaco.languages.setLanguageConfiguration(MINILANG_LANGUAGE_ID, miniLangConfig);
      monaco.languages.setMonarchTokensProvider(MINILANG_LANGUAGE_ID, miniLangTokensProvider);
    }

    // Define custom Dark Graphite theme
    monaco.editor.defineTheme('wasmlab-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: 'B6A4FF', fontStyle: 'bold' },
        { token: 'type', foreground: '9D84FF', fontStyle: 'bold' },
        { token: 'number', foreground: '82D9B2' },
        { token: 'operator', foreground: 'E9E8EE' },
        { token: 'delimiter', foreground: '8E8B9B' },
        { token: 'comment', foreground: '5E5B6D', fontStyle: 'italic' },
        { token: 'identifier', foreground: 'E9E8EE' },
      ],
      colors: {
        'editor.background': '#17171C',
        'editor.foreground': '#E9E8EE',
        'editorLineNumber.foreground': '#4E4C5A',
        'editorLineNumber.activeForeground': '#B6A4FF',
        'editorCursor.foreground': '#9D84FF',
        'editor.selectionBackground': '#2E2B3D',
        'editor.lineHighlightBackground': '#1C1C22',
        'editorIndentGuide.background': '#24232B',
        'editorIndentGuide.activeBackground': '#3E3D4A',
      },
    });
  };

  const handleEditorDidMount = (editorInstance: editor.IStandaloneCodeEditor, monaco: any) => {
    editorRef.current = editorInstance;
    monacoRef.current = monaco;
    if (onMount) onMount(editorInstance);
  };

  // Update diagnostic markers in Monaco whenever compiler diagnostics change
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;
    const monaco = monacoRef.current;
    const model = editorRef.current.getModel();
    if (!model) return;

    const markers: editor.IMarkerData[] = diagnostics
      .filter((d) => d.location)
      .map((d) => ({
        severity:
          d.severity === 'error'
            ? monaco.MarkerSeverity.Error
            : monaco.MarkerSeverity.Warning,
        message: d.message,
        startLineNumber: d.location!.line,
        startColumn: d.location!.column,
        endLineNumber: d.location!.end_line || d.location!.line,
        endColumn: (d.location!.end_column || d.location!.column) + 1,
      }));

    monaco.editor.setModelMarkers(model, 'minilang-compiler', markers);
  }, [diagnostics]);

  return (
    <div className="w-full h-full relative overflow-hidden bg-dark-sidebar">
      <MonacoEditor
        height="100%"
        language={MINILANG_LANGUAGE_ID}
        theme="wasmlab-dark"
        value={value}
        onChange={(val) => onChange(val || '')}
        beforeMount={handleEditorWillMount}
        onMount={handleEditorDidMount}
        options={{
          fontSize: 14,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontLigatures: true,
          tabSize: 4,
          insertSpaces: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          lineNumbers: 'on',
          renderLineHighlight: 'all',
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
          bracketPairColorization: { enabled: true },
        }}
      />
    </div>
  );
};
