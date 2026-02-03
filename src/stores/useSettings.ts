import { create } from 'zustand';
import { invoke } from '@tauri-apps/api/core';
import { AppSettings, LLMSettings } from '../../types'; // Import from global types

interface SettingsState {
    settings: AppSettings;
    loading: boolean;
    saving: boolean;
    error: string | null;

    fetchSettings: () => Promise<void>;
    updateSettings: (key: string, value: any) => Promise<void>;
    updateLLMSettings: (settings: LLMSettings) => Promise<void>;
    updatePartialLLM: (update: Partial<LLMSettings>) => Promise<void>;
}

export const useSettings = create<SettingsState>((set, get) => ({
    settings: {
        theme: 'light',
        accentColor: 'violet',
        enableAI: true,
        aiProvider: 'gemini',
        apiKeys: {
            gemini: '',
            groq: '',
            openai: '',
            openrouter: '',
            opencode: '',
            cerebras: '',
            nvidia: ''
        },
        modelName: '',
        llm: {
            ollama_host: 'localhost',
            ollama_port: 11434,
            selected_model: '',
            context_window: 4096,
            temperature: 0.7,
            top_p: 0.9,
            system_prompt: 'You are a helpful assistant.',
            keep_alive: '5m',
            seed: null,
            num_gpu: -1
        },
        supabaseConfig: {
            url: '',
            key: ''
        },
        financialDataApis: {
            alphaVantage: '',
            twelveData: '',
            fyersAppId: '',
            fyersAccessToken: '',
            angelOneApiKey: '',
            angelOneClientCode: '',
            angelOnePassword: ''
        }
    },
    loading: true,
    saving: false,
    error: null,

    fetchSettings: async () => {
        const isTauri = typeof window !== 'undefined' && !!(window as any).__TAURI__;
        if (!isTauri) {
            set({ loading: false });
            return;
        }

        set({ loading: true, error: null });
        try {
            const settings = await invoke<AppSettings>('get_settings');
            set({ settings, loading: false });
        } catch (e) {
            set({ error: `Failed to load settings: ${e}`, loading: false });
        }
    },

    updateSettings: async (key, value) => {
        set({ saving: true, error: null });
        try {
            // Optimistic update
            set((state) => ({
                settings: { ...state.settings, [key]: value }
            }));

            await invoke('update_setting', { key, value });
            set({ saving: false });
        } catch (e) {
            set({ error: `Failed to update ${key}: ${e}`, saving: false });
            // Revert could be implemented here
        }
    },

    updateLLMSettings: async (llmSettings) => {
        set({ saving: true, error: null });
        try {
            // Optimistic update
            set((state) => ({
                settings: { ...state.settings, llm: llmSettings }
            }));

            await invoke('update_llm_settings', { settings: llmSettings });
            set({ saving: false });
        } catch (e) {
            set({ error: `Failed to update LLM settings: ${e}`, saving: false });
        }
    },

    updatePartialLLM: async (update) => {
        const current = get().settings.llm;
        const newSettings = { ...current, ...update };
        await get().updateLLMSettings(newSettings);
    }
}));
