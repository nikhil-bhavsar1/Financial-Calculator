import React, { useState } from 'react';
import { X, Moon, Sun, Zap, KeyRound, Database, Sparkles, CheckCircle, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import { AppSettings } from '../types';
import { LLMSettingsPanel } from '../src/components/LLMSettingsPanel';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AppSettings;
  onUpdateSettings: (settings: AppSettings) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, settings, onUpdateSettings }) => {
  const [isFinancialApisExpanded, setIsFinancialApisExpanded] = useState(false);

  if (!isOpen) return null;

  const handleThemeToggle = () => {
    const nextThemeMap: Record<string, 'light' | 'dark' | 'system'> = {
      'light': 'dark',
      'dark': 'system',
      'system': 'light'
    };
    onUpdateSettings({
      ...settings,
      theme: nextThemeMap[settings.theme] || 'light'
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
    { id: 'cerebras', name: 'Cerebras', icon: '🧠', description: 'CS-3 powered inference' },
    { id: 'nvidia', name: 'NVIDIA NIM', icon: '🟢', description: 'Enterprise-grade NIM' },
    { id: 'local_llm', name: 'Local LLM', icon: '🏠', description: 'Private & Offline (Ollama)' },
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
                  <p className="text-xs text-tertiary">
                    {settings.theme === 'dark' ? 'Dark mode' : settings.theme === 'light' ? 'Light mode' : 'Follow system'}
                  </p>
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
          {settings.enableAI && settings.aiProvider !== 'local_llm' && (
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

                {settings.aiProvider === 'gemini' && (
                  <div className="mb-4 animate-fadeIn">
                    <label className="text-xs text-tertiary mb-1.5 block">Select Gemini Model</label>
                    <select
                      value={settings.modelName || 'gemini-1.5-flash'}
                      onChange={(e) => onUpdateSettings({ ...settings, modelName: e.target.value })}
                      className="glass-input w-full appearance-none cursor-pointer"
                    >
                      <option value="gemini-2.0-flash">Gemini 2.0 Flash (Fast & Smart)</option>
                      <option value="gemini-1.5-flash">Gemini 1.5 Flash (Efficient)</option>
                      <option value="gemini-1.5-pro">Gemini 1.5 Pro (High Logic)</option>
                      <option value="gemini-2.0-flash-thinking-exp-1219">Gemini 2.0 Thinking (Experimental)</option>
                    </select>
                  </div>
                )}

                {settings.aiProvider === 'groq' && (
                  <div className="mb-4 animate-fadeIn">
                    <label className="text-xs text-tertiary mb-1.5 block">Select Groq Model</label>
                    <select
                      value={settings.modelName || 'llama-3.3-70b-versatile'}
                      onChange={(e) => onUpdateSettings({ ...settings, modelName: e.target.value })}
                      className="glass-input w-full appearance-none cursor-pointer"
                    >
                      <optgroup label="Llama Series">
                        <option value="llama-3.3-70b-versatile">Llama 3.3 70B Versatile (12k TPM)</option>
                        <option value="llama-3.1-8b-instant">Llama 3.1 8B Instant (6k TPM)</option>
                        <option value="meta-llama/llama-4-maverick-17b-128e-instruct">Llama 4 Maverick 17B (6k TPM)</option>
                        <option value="meta-llama/llama-4-scout-17b-16e-instruct">Llama 4 Scout 17B (30k TPM)</option>
                        <option value="allam-2-7b">Allam 2 7B (6k TPM)</option>
                      </optgroup>
                      <optgroup label="Groq Originals">
                        <option value="groq/compound">Groq Compound (70k TPM)</option>
                        <option value="groq/compound-mini">Groq Compound Mini (70k TPM)</option>
                      </optgroup>
                      <optgroup label="Moonshot AI">
                        <option value="moonshotai/kimi-k2-instruct">Kimi K2 Instruct (10k TPM)</option>
                        <option value="moonshotai/kimi-k2-instruct-0905">Kimi K2 Instruct 0905 (10k TPM)</option>
                      </optgroup>
                      <optgroup label="GPT-OSS Series">
                        <option value="openai/gpt-oss-120b">GPT-OSS 120B (8k TPM)</option>
                        <option value="openai/gpt-oss-20b">GPT-OSS 20B (8k TPM)</option>
                        <option value="openai/gpt-oss-safeguard-20b">GPT-OSS Safeguard 20B (8k TPM)</option>
                      </optgroup>
                      <optgroup label="Other">
                        <option value="qwen/qwen3-32b">Qwen 3 32B (6k TPM)</option>
                        <option value="meta-llama/llama-guard-4-12b">Llama Guard 4 12B (15k TPM)</option>
                        <option value="meta-llama/llama-prompt-guard-2-22m">Llama Prompt Guard 22M (15k TPM)</option>
                        <option value="meta-llama/llama-prompt-guard-2-86m">Llama Prompt Guard 86M (15k TPM)</option>
                      </optgroup>
                    </select>
                  </div>
                )}

                {settings.aiProvider === 'cerebras' && (
                  <div className="mb-4 animate-fadeIn">
                    <label className="text-xs text-tertiary mb-1.5 block">Select Cerebras Model</label>
                    <select
                      value={settings.modelName || 'llama-3.3-70b'}
                      onChange={(e) => onUpdateSettings({ ...settings, modelName: e.target.value })}
                      className="glass-input w-full appearance-none cursor-pointer"
                    >
                      <option value="llama-3.3-70b">Llama 3.3 70B</option>
                      <option value="llama3.1-8b">Llama 3.1 8B</option>
                      <option value="gpt-oss-120b">GPT OSS 120B</option>
                      <option value="qwen-3-235b-a22b-instruct-2507">Qwen 3 235B Instruct</option>
                      <option value="qwen-3-32b">Qwen 3 32B</option>
                      <option value="zai-glm-4.7">Z.ai GLM 4.7</option>
                    </select>
                  </div>
                )}

                {settings.aiProvider === 'nvidia' && (
                  <div className="mb-4 animate-fadeIn">
                    <label className="text-xs text-tertiary mb-1.5 block">Select NVIDIA NIM Model</label>
                    <select
                      value={settings.modelName || 'meta/llama-3.1-405b-instruct'}
                      onChange={(e) => onUpdateSettings({ ...settings, modelName: e.target.value })}
                      className="glass-input w-full appearance-none cursor-pointer"
                    >
                      <option value="meta/llama-3.1-405b-instruct">Llama 3.1 405B Instruct (SOTA)</option>
                      <option value="meta/llama-3.1-70b-instruct">Llama 3.1 70B Instruct</option>
                      <option value="meta/llama-3.1-8b-instruct">Llama 3.1 8B Instruct</option>
                      <option value="nvidia/llama-3.1-nemotron-70b-instruct">Nemotron 70B Instruct</option>
                    </select>
                  </div>
                )}

                {settings.aiProvider !== 'groq' && settings.aiProvider !== 'gemini' && settings.aiProvider !== 'cerebras' && settings.aiProvider !== 'nvidia' && (
                  <div>
                    <label className="text-xs text-tertiary mb-1.5 block">Model Name (Optional)</label>
                    <input
                      type="text"
                      value={settings.modelName || ''}
                      onChange={(e) => onUpdateSettings({ ...settings, modelName: e.target.value })}
                      placeholder="e.g., gpt-4o"
                      className="glass-input w-full"
                    />
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Local LLM Settings */}
          {settings.enableAI && settings.aiProvider === 'local_llm' && (
            <section className="animate-fadeIn stagger-2">
              <LLMSettingsPanel />
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

          {/* Financial Data APIs - Collapsible Section */}
          <section className="animate-fadeIn stagger-3">
            <div
              onClick={() => setIsFinancialApisExpanded(!isFinancialApisExpanded)}
              className="flex items-center justify-between p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)] cursor-pointer hover:border-[var(--border-strong)] transition-all mb-4"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary">Financial Data APIs</p>
                  <p className="text-xs text-tertiary">
                    {isFinancialApisExpanded ? 'Click to collapse' : 'Configure stock market data providers'}
                  </p>
                </div>
              </div>
              <div className="text-tertiary">
                {isFinancialApisExpanded ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>
            </div>

            {isFinancialApisExpanded && (
              <div className="space-y-4 animate-fadeIn">
                <p className="text-xs text-tertiary mb-4 px-1">
                  Configure API keys for stock market data providers. These are optional - Yahoo Finance works without API keys.
                </p>

                {/* Alpha Vantage */}
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">📊</span>
                    <span className="text-sm font-medium text-primary">Alpha Vantage</span>
                    <span className="text-xs text-tertiary">(25 calls/day free)</span>
                  </div>
                  <div>
                    <label className="text-xs text-tertiary mb-1.5 block">API Key</label>
                    <input
                      type="password"
                      value={settings.financialDataApis?.alphaVantage || ''}
                      onChange={(e) => onUpdateSettings({
                        ...settings,
                        financialDataApis: { ...settings.financialDataApis, alphaVantage: e.target.value }
                      })}
                      placeholder="Enter Alpha Vantage API key..."
                      className="glass-input w-full"
                    />
                    <p className="text-[10px] text-tertiary mt-1">
                      Get free key at: <a href="https://www.alphavantage.co/support/#api-key" target="_blank" rel="noopener noreferrer" className="text-[var(--accent-primary)] hover:underline">alphavantage.co</a>
                    </p>
                  </div>
                </div>

                {/* Twelve Data */}
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">📈</span>
                    <span className="text-sm font-medium text-primary">Twelve Data</span>
                    <span className="text-xs text-tertiary">(8 calls/day free)</span>
                  </div>
                  <div>
                    <label className="text-xs text-tertiary mb-1.5 block">API Key</label>
                    <input
                      type="password"
                      value={settings.financialDataApis?.twelveData || ''}
                      onChange={(e) => onUpdateSettings({
                        ...settings,
                        financialDataApis: { ...settings.financialDataApis, twelveData: e.target.value }
                      })}
                      placeholder="Enter Twelve Data API key..."
                      className="glass-input w-full"
                    />
                    <p className="text-[10px] text-tertiary mt-1">
                      Get free key at: <a href="https://twelvedata.com/pricing" target="_blank" rel="noopener noreferrer" className="text-[var(--accent-primary)] hover:underline">twelvedata.com</a>
                    </p>
                  </div>
                </div>

                {/* Fyers */}
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">🏦</span>
                    <span className="text-sm font-medium text-primary">Fyers</span>
                    <span className="text-xs text-tertiary">(Indian markets)</span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-tertiary mb-1.5 block">App ID</label>
                      <input
                        type="text"
                        value={settings.financialDataApis?.fyersAppId || ''}
                        onChange={(e) => onUpdateSettings({
                          ...settings,
                          financialDataApis: { ...settings.financialDataApis, fyersAppId: e.target.value }
                        })}
                        placeholder="Enter Fyers App ID..."
                        className="glass-input w-full"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-tertiary mb-1.5 block">Access Token</label>
                      <input
                        type="password"
                        value={settings.financialDataApis?.fyersAccessToken || ''}
                        onChange={(e) => onUpdateSettings({
                          ...settings,
                          financialDataApis: { ...settings.financialDataApis, fyersAccessToken: e.target.value }
                        })}
                        placeholder="Enter Fyers Access Token..."
                        className="glass-input w-full"
                      />
                    </div>
                    <p className="text-[10px] text-tertiary">
                      Get API access at: <a href="https://fyers.in/api/" target="_blank" rel="noopener noreferrer" className="text-[var(--accent-primary)] hover:underline">fyers.in</a>
                    </p>
                  </div>
                </div>

                {/* Angel One */}
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">👼</span>
                    <span className="text-sm font-medium text-primary">Angel One</span>
                    <span className="text-xs text-tertiary">(Indian markets)</span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-tertiary mb-1.5 block">API Key</label>
                      <input
                        type="password"
                        value={settings.financialDataApis?.angelOneApiKey || ''}
                        onChange={(e) => onUpdateSettings({
                          ...settings,
                          financialDataApis: { ...settings.financialDataApis, angelOneApiKey: e.target.value }
                        })}
                        placeholder="Enter Angel One API Key..."
                        className="glass-input w-full"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-tertiary mb-1.5 block">Client Code</label>
                      <input
                        type="text"
                        value={settings.financialDataApis?.angelOneClientCode || ''}
                        onChange={(e) => onUpdateSettings({
                          ...settings,
                          financialDataApis: { ...settings.financialDataApis, angelOneClientCode: e.target.value }
                        })}
                        placeholder="Enter Angel One Client Code..."
                        className="glass-input w-full"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-tertiary mb-1.5 block">Password</label>
                      <input
                        type="password"
                        value={settings.financialDataApis?.angelOnePassword || ''}
                        onChange={(e) => onUpdateSettings({
                          ...settings,
                          financialDataApis: { ...settings.financialDataApis, angelOnePassword: e.target.value }
                        })}
                        placeholder="Enter Angel One Password..."
                        className="glass-input w-full"
                      />
                    </div>
                    <p className="text-[10px] text-tertiary">
                      Get API access at: <a href="https://www.angelone.in/smartapi" target="_blank" rel="noopener noreferrer" className="text-[var(--accent-primary)] hover:underline">angelone.in</a>
                    </p>
                  </div>
                </div>
              </div>
            )}
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