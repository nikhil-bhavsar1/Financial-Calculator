import React from 'react';
import { CloudUpload, Database, Settings, BarChart3, Sparkles } from 'lucide-react';

interface HeaderProps {
  onUploadClick?: () => void;
  onOpenSettings: () => void;
  onOpenKnowledgeBase: () => void;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ onUploadClick, onOpenSettings, onOpenKnowledgeBase, title }) => {
  return (
    <header className="glass-nav px-6 py-4 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-6">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold text-primary">DataExtract</span>
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-accent" />
              <span className="text-xs text-tertiary">AI-Powered</span>
            </div>
          </div>
        </div>

        <div className="h-8 w-px bg-[var(--border-default)]" />

        {/* Document Info */}
        <div>
          <h1 className="text-sm font-semibold text-primary">{title || "Financial Calculator"}</h1>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onOpenKnowledgeBase}
          className="btn-secondary"
        >
          <Database className="w-4 h-4 text-accent" />
          <span>Terminology Map</span>
        </button>

        <button
          onClick={onUploadClick}
          className="btn-primary"
        >
          <CloudUpload className="w-4 h-4" />
          <span>Upload</span>
        </button>

        <div className="h-6 w-px bg-[var(--border-default)] mx-1" />

        <button
          onClick={onOpenSettings}
          className="btn-icon"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};

export default Header;