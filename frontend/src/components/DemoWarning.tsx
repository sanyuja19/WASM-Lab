import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface DemoWarningProps {
  onRetry: () => void;
  isRetrying: boolean;
}

export const DemoWarning: React.FC<DemoWarningProps> = ({ onRetry, isRetrying }) => {
  return (
    <div className="bg-red-error/10 border-b border-red-error/30 px-4 py-2 flex items-center justify-between text-xs select-none">
      <div className="flex items-center space-x-2 text-text-primary">
        <AlertCircle className="w-4 h-4 text-red-error flex-shrink-0" />
        <div>
          <span className="font-semibold text-red-error">Backend Compiler Disconnected: </span>
          <span className="text-text-secondary">
            Displayed artifacts are in UI preview mode. Start backend with{' '}
            <code className="px-1.5 py-0.5 rounded bg-dark-bg text-lavender-muted font-mono border border-dark-border">
              python -m uvicorn backend.app.main:app --port 8000
            </code>
          </span>
        </div>
      </div>
      <button
        onClick={onRetry}
        disabled={isRetrying}
        className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-dark-surface hover:bg-dark-hover border border-dark-border text-text-primary transition-colors text-[11px]"
      >
        <RefreshCw className={`w-3 h-3 ${isRetrying ? 'animate-spin' : ''}`} />
        <span>Reconnect</span>
      </button>
    </div>
  );
};
