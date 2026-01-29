import React, { useEffect } from 'react';
import { useSettings } from '../stores/useSettings';
import { ModelSelector } from './ModelSelector';
import { useLocalLLM } from '../hooks/useLocalLLM';
import { invoke } from '@tauri-apps/api/core';

export const LLMSettingsPanel: React.FC = () => {
    const { settings, updatePartialLLM, saving } = useSettings();
    const { availableModels, currentlyLoaded, refreshModels, error: connectionError } = useLocalLLM();

    const handleSave = async (updates: Partial<typeof settings.llm>) => {
        await updatePartialLLM(updates);
    };

    return (
        <div className="space-y-6 animate-fadeIn">
            {/* Connection Error Notice */}
            {connectionError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex flex-col gap-1 anim-shake">
                    <div className="flex items-center gap-2 text-rose-500">
                        <span className="text-xs font-semibold uppercase tracking-wider">Connection Issue</span>
                    </div>
                    <p className="text-xs text-rose-500/80 leading-relaxed font-medium">
                        {connectionError.includes('TCP connect error')
                            ? "Could not reach Ollama. Is it running? If yes, try changing 'localhost' to '127.0.0.1'."
                            : connectionError
                        }
                    </p>
                </div>
            )}

            {/* Connection Settings */}
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                    <label className="text-xs text-tertiary">Ollama Host</label>
                    <input
                        type="text"
                        value={settings.llm.ollama_host}
                        onChange={(e) => handleSave({ ollama_host: e.target.value })}
                        className="glass-input w-full"
                        placeholder="localhost"
                    />
                </div>
                <div className="space-y-1.5">
                    <label className="text-xs text-tertiary">Port</label>
                    <input
                        type="number"
                        value={settings.llm.ollama_port}
                        onChange={(e) => handleSave({ ollama_port: parseInt(e.target.value) })}
                        className="glass-input w-full"
                    />
                </div>
            </div>

            {/* Model Selection */}
            <div className="space-y-3 p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                <div className="flex items-center justify-between mb-1">
                    <h3 className="text-sm font-medium text-primary">Model Selection</h3>
                    <button
                        onClick={refreshModels}
                        className="text-xs text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] transition-colors flex items-center gap-1"
                    >
                        Refresh
                    </button>
                </div>

                <ModelSelector
                    models={availableModels}
                    selectedModel={settings.llm.selected_model}
                    currentlyLoaded={currentlyLoaded}
                    onSelect={(model) => handleSave({ selected_model: model })}
                    onUnload={async (model) => {
                        await invoke('unload_model', { model });
                        refreshModels();
                    }}
                />

                <div className="mt-3 pt-3 border-t border-[var(--border-weak)]">
                    <label className="text-xs text-tertiary mb-1.5 block">GPU Strategy</label>
                    <select
                        value={settings.llm.keep_alive}
                        onChange={(e) => handleSave({ keep_alive: e.target.value })}
                        className="glass-input w-full appearance-none cursor-pointer"
                    >
                        <option value="0">Unload immediately (save VRAM)</option>
                        <option value="5m">Keep 5 minutes (balanced)</option>
                        <option value="1h">Keep 1 hour (performance)</option>
                        <option value="-1">Keep loaded always</option>
                    </select>
                </div>
            </div>

            {/* Advanced Parameters Toggle */}
            <div className="space-y-4">
                <h3 className="text-sm font-medium text-primary border-b border-[var(--border-default)] pb-2">Advanced Parameters</h3>

                <div className="grid grid-cols-2 gap-x-4 gap-y-6">
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <label className="text-xs text-tertiary">Context Window</label>
                            <span className="text-xs font-mono text-secondary">{settings.llm.context_window.toLocaleString()}</span>
                        </div>
                        <input
                            type="range"
                            min="2048"
                            max="128000"
                            step="1024"
                            value={settings.llm.context_window}
                            onChange={(e) => handleSave({ context_window: parseInt(e.target.value) })}
                            className="w-full accent-[var(--accent-primary)] h-1.5 bg-[var(--border-default)] rounded-lg appearance-none cursor-pointer"
                        />
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <label className="text-xs text-tertiary">Temperature</label>
                            <span className="text-xs font-mono text-secondary">{settings.llm.temperature}</span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="2"
                            step="0.1"
                            value={settings.llm.temperature}
                            onChange={(e) => handleSave({ temperature: parseFloat(e.target.value) })}
                            className="w-full accent-[var(--accent-primary)] h-1.5 bg-[var(--border-default)] rounded-lg appearance-none cursor-pointer"
                        />
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-xs text-tertiary">Top P</label>
                        <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="1"
                            value={settings.llm.top_p}
                            onChange={(e) => handleSave({ top_p: parseFloat(e.target.value) })}
                            className="glass-input w-full"
                        />
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-xs text-tertiary">Seed</label>
                        <input
                            type="number"
                            value={settings.llm.seed || ''}
                            onChange={(e) => handleSave({ seed: e.target.value ? parseInt(e.target.value) : null })}
                            className="glass-input w-full"
                            placeholder="Random"
                        />
                    </div>
                </div>

                <div className="space-y-1.5">
                    <label className="text-xs text-tertiary">System Prompt</label>
                    <textarea
                        value={settings.llm.system_prompt}
                        onChange={(e) => handleSave({ system_prompt: e.target.value })}
                        rows={3}
                        className="glass-input w-full resize-none"
                        placeholder="Define AI behavior..."
                    />
                </div>
            </div>

            {saving && <span className="text-xs text-[var(--accent-primary)] animate-pulse">Saving changes...</span>}
        </div>
    );
};
