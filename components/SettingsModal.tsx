import React from 'react';
import { X, Moon, Sun, Zap, KeyRound, Database, Sparkles, CheckCircle } from 'lucide-react';
import { AppSettings } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AppSettings;
  onUpdateSettings: (settings: AppSettings) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, settings, onUpdateSettings }) => {
  if (!isOpen) return null;

  const handleThemeToggle = () => {
    onUpdateSettings({
      ...settings,
      theme: settings.theme === 'dark' ? 'light' : 'dark'
    });
  };

  const handleAIToggle = () => {
    onUpdateSettings({
      ...settings,
      enableAI: !settings.enableAI
    });
  };

  const handleApiKeyChange = (provider: keyof typeof settings.apiKeys, value: string) => {
    onUpdateSettings({
      ...settings,
      apiKeys: { ...settings.apiKeys, [provider]: value }
    });
  };

  const handleProviderChange = (provider: string) => {
    onUpdateSettings({
      ...settings,
      aiProvider: provider as AppSettings['aiProvider']
    });
  };

  const providers = [
    { id: 'gemini', name: 'Google Gemini', icon: '✨', description: 'Best for complex analysis' },
    { id: 'groq', name: 'Groq', icon: '⚡', description: 'Ultra-fast responses' },
    { id: 'openai', name: 'OpenAI', icon: '🤖', description: 'GPT-4 powered' },
    { id: 'openrouter', name: 'OpenRouter', icon: '🌐', description: 'Multi-model access' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fadeIn"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-xl glass-modal overflow-hidden animate-fadeInScale">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--border-default)]">
          <div>
            <h2 className="text-lg font-semibold text-primary">Settings</h2>
            <p className="text-sm text-tertiary mt-0.5">Configure your preferences</p>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar">

          {/* Appearance */}
          <section className="animate-fadeIn">
            <h3 className="label-uppercase mb-4">Appearance</h3>
            <div
              onClick={handleThemeToggle}
              className="flex items-center justify-between p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)] cursor-pointer hover:border-[var(--border-strong)] transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 dark:from-indigo-500 dark:to-purple-600 flex items-center justify-center">
                  {settings.theme === 'dark' ? (
                    <Moon className="w-5 h-5 text-white" />
                  ) : (
                    <Sun className="w-5 h-5 text-white" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-primary">Theme</p>
                  <p className="text-xs text-tertiary">{settings.theme === 'dark' ? 'Dark mode' : 'Light mode'}</p>
                </div>
              </div>
              <div className={`w-12 h-7 rounded-full p-1 transition-colors ${settings.theme === 'dark' ? 'bg-[var(--accent-primary)]' : 'bg-[var(--border-strong)]'}`}>
                <div className={`w-5 h-5 rounded-full bg-white shadow-md transition-transform ${settings.theme === 'dark' ? 'translate-x-5' : 'translate-x-0'}`} />
              </div>
            </div>

            {/* Accent Color Picker */}
            <div className="mt-4 p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
              <p className="text-sm font-medium text-primary mb-1">Accent Color</p>
              <p className="text-xs text-tertiary mb-4">Choose a theme that suits your style</p>
              <div className="grid grid-cols-6 gap-3">
                {[
                  { id: 'violet', color: 'bg-gradient-to-br from-violet-600 via-purple-600 to-fuchsia-800', label: 'Amethyst', desc: 'Royal' },
                  { id: 'sapphire', color: 'bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800', label: 'Sapphire', desc: 'Trust' },
                  { id: 'emerald', color: 'bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-700', label: 'Emerald', desc: 'Prosperity' },
                  { id: 'gold', color: 'bg-gradient-to-br from-amber-500 via-yellow-600 to-orange-600', label: 'Gold', desc: 'Wealth' },
                  { id: 'rose', color: 'bg-gradient-to-br from-rose-500 via-pink-600 to-fuchsia-700', label: 'Rose', desc: 'Elegance' },
                  { id: 'platinum', color: 'bg-gradient-to-br from-slate-400 via-gray-500 to-zinc-600', label: 'Platinum', desc: 'Premium' },
                ].map(accent => (
                  <button
                    key={accent.id}
                    onClick={() => onUpdateSettings({ ...settings, accentColor: accent.id as AppSettings['accentColor'] })}
                    className={`group relative flex flex-col items-center gap-1.5 p-2 rounded-xl transition-all ${settings.accentColor === accent.id
                      ? 'bg-[var(--bg-hover)] ring-1 ring-[var(--accent-primary)]'
                      : 'hover:bg-[var(--bg-hover)]'
                      }`}
                    title={accent.label}
                  >
                    <div className={`w-10 h-10 rounded-xl ${accent.color} shadow-lg transition-transform group-hover:scale-105 ${settings.accentColor === accent.id ? 'ring-2 ring-white shadow-xl scale-105' : ''
                      }`} />
                    <span className={`text-[10px] font-medium ${settings.accentColor === accent.id ? 'text-primary' : 'text-tertiary'}`}>
                      {accent.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* AI Features */}
          <section className="animate-fadeIn stagger-1">
            <h3 className="label-uppercase mb-4">AI Features</h3>
            <div
              onClick={handleAIToggle}
              className="flex items-center justify-between p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)] cursor-pointer hover:border-[var(--border-strong)] transition-all mb-4"
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${settings.enableAI ? 'bg-gradient-to-br from-purple-500 to-pink-500' : 'bg-[var(--bg-hover)]'}`}>
                  <Sparkles className={`w-5 h-5 ${settings.enableAI ? 'text-white' : 'text-tertiary'}`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary">AI Analysis</p>
                  <p className="text-xs text-tertiary">{settings.enableAI ? 'Enabled' : 'Disabled'}</p>
                </div>
              </div>
              <div className={`w-12 h-7 rounded-full p-1 transition-colors ${settings.enableAI ? 'bg-[var(--accent-primary)]' : 'bg-[var(--border-strong)]'}`}>
                <div className={`w-5 h-5 rounded-full bg-white shadow-md transition-transform ${settings.enableAI ? 'translate-x-5' : 'translate-x-0'}`} />
              </div>
            </div>

            {settings.enableAI && (
              <div className="space-y-3 animate-fadeIn">
                <p className="text-xs text-tertiary mb-2">Select AI Provider</p>
                <div className="grid grid-cols-2 gap-3">
                  {providers.map(provider => (
                    <button
                      key={provider.id}
                      onClick={() => handleProviderChange(provider.id)}
                      className={`relative p-4 rounded-xl border text-left transition-all ${settings.aiProvider === provider.id
                        ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5'
                        : 'border-[var(--border-default)] hover:border-[var(--border-strong)] bg-[var(--bg-surface)]'
                        }`}
                    >
                      {settings.aiProvider === provider.id && (
                        <CheckCircle className="absolute top-3 right-3 w-4 h-4 text-accent" />
                      )}
                      <span className="text-xl mb-2 block">{provider.icon}</span>
                      <p className="text-sm font-medium text-primary">{provider.name}</p>
                      <p className="text-xs text-tertiary mt-0.5">{provider.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* API Keys */}
          {settings.enableAI && (
            <section className="animate-fadeIn stagger-2">
              <h3 className="label-uppercase mb-4">API Keys</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-tertiary mb-1.5 block">
                    {providers.find(p => p.id === settings.aiProvider)?.name || 'API'} Key
                  </label>
                  <div className="relative">
                    <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary" />
                    <input
                      type="password"
                      value={settings.apiKeys[settings.aiProvider as keyof typeof settings.apiKeys] || ''}
                      onChange={(e) => handleApiKeyChange(settings.aiProvider as keyof typeof settings.apiKeys, e.target.value)}
                      placeholder="Enter your API key..."
                      className="glass-input w-full pl-11"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs text-tertiary mb-1.5 block">Model Name (Optional)</label>
                  <input
                    type="text"
                    value={settings.modelName || ''}
                    onChange={(e) => onUpdateSettings({ ...settings, modelName: e.target.value })}
                    placeholder="e.g., gemini-2.5-pro"
                    className="glass-input w-full"
                  />
                </div>
              </div>
            </section>
          )}

          {/* Supabase */}
          <section className="animate-fadeIn stagger-3">
            <h3 className="label-uppercase mb-4">Data Sync</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-tertiary mb-1.5 block">Supabase URL</label>
                <div className="relative">
                  <Database className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary" />
                  <input
                    type="text"
                    value={settings.supabaseConfig?.url || ''}
                    onChange={(e) => onUpdateSettings({
                      ...settings,
                      supabaseConfig: { ...settings.supabaseConfig, url: e.target.value }
                    })}
                    placeholder="https://your-project.supabase.co"
                    className="glass-input w-full pl-11"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-tertiary mb-1.5 block">Supabase Key</label>
                <input
                  type="password"
                  value={settings.supabaseConfig?.key || ''}
                  onChange={(e) => onUpdateSettings({
                    ...settings,
                    supabaseConfig: { ...settings.supabaseConfig, key: e.target.value }
                  })}
                  placeholder="Your anon/service key"
                  className="glass-input w-full"
                />
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[var(--border-default)]">
          <button onClick={onClose} className="btn-primary">
            <CheckCircle className="w-4 h-4" />
            <span>Done</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;