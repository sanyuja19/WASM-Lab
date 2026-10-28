import React from 'react';
import { Files, GitCompare, GitFork, Terminal, AlertCircle } from 'lucide-react';

interface ActivityRailProps {
  activePanel: string;
  setActivePanel: (panel: string) => void;
  errorCount: number;
}

export const ActivityRail: React.FC<ActivityRailProps> = ({
  activePanel,
  setActivePanel,
  errorCount,
}) => {
  const items = [
    { id: 'files', label: 'File Explorer', icon: Files },
    { id: 'pipeline', label: 'Pipeline Visualizer', icon: GitFork },
    { id: 'compare', label: 'Optimization Comparison (O0 vs O2)', icon: GitCompare },
    { id: 'diagnostics', label: 'Diagnostics & Errors', icon: AlertCircle, badge: errorCount > 0 ? errorCount : null },
    { id: 'console', label: 'Runtime Console', icon: Terminal },
  ];

  return (
    <aside className="w-12 bg-dark-sidebar border-r border-dark-border flex flex-col items-center py-3 space-y-2 z-10 select-none">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = activePanel === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActivePanel(item.id)}
            className={`relative p-2.5 rounded-lg transition-all ${
              isActive
                ? 'bg-lavender-strong/15 text-lavender-strong border border-lavender-strong/30'
                : 'text-text-secondary hover:text-text-primary hover:bg-dark-surface'
            }`}
            title={item.label}
          >
            <Icon className="w-5 h-5" />
            {item.badge && (
              <span className="absolute -top-1 -right-1 bg-red-error text-dark-bg font-bold text-[9px] w-4 h-4 rounded-full flex items-center justify-center">
                {item.badge}
              </span>
            )}
            {isActive && (
              <div className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-lavender-strong rounded-r" />
            )}
          </button>
        );
      })}
    </aside>
  );
};
