export interface FormulaBreakdown {
  step: string;
  formula: string;
  description?: string;
}

export interface FinancialItem {
  id: string;
  label: string;
  currentYear: number;
  previousYear: number;
  variation: number;
  variationPercent: number;
  sourcePage: string;
  rawLine?: string;
  isAutoCalc?: boolean;
  hasWarning?: boolean;
  calculationError?: string;
  formula?: string;
  interpretation?: string;
  breakdown?: FormulaBreakdown[];
  statementType?: string; // 'balance_sheet', 'income_statement', 'cashflow'
  isImportant?: boolean;
}

export interface MetricGroup {
  category: string;
  items: FinancialItem[];
}

export enum InputStatus {
  REQUIRED = 'REQUIRED',
  LOW_CONFIDENCE = 'LOW_CONFIDENCE',
  NOT_FOUND = 'NOT_FOUND',
  VERIFIED = 'VERIFIED',
  SKIPPED = 'SKIPPED'
}

export interface MissingInputItem {
  id: string;
  label: string;
  value: string; // Legacy/Single value
  targetYear?: 'current' | 'previous'; // Legacy target
  values?: {
    current: string;
    previous: string;
  };
  status: InputStatus;
  confidence?: number;
}

export type AiProvider = 'gemini' | 'groq' | 'openai' | 'openrouter' | 'opencode' | 'local_llm';

export interface LLMSettings {
  ollama_host: string;
  ollama_port: number;
  selected_model: string;
  context_window: number;
  temperature: number;
  top_p: number;
  system_prompt: string;
  seed?: number | null;
  keep_alive: string;
  num_gpu: number;
}

export interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  accentColor: 'violet' | 'sapphire' | 'emerald' | 'gold' | 'rose' | 'platinum';
  enableAI: boolean;
  aiProvider: AiProvider;
  apiKeys: {
    gemini: string;
    groq: string;
    openai: string;
    openrouter: string;
    opencode: string;
  };
  modelName: string;
  // Local LLM Specific Settings
  llm: {
    ollama_host: string;
    ollama_port: number;
    selected_model: string;
    context_window: number;
    temperature: number;
    top_p: number;
    system_prompt: string;
    seed?: number | null;
    keep_alive: string;
    num_gpu: number;
  };
  supabaseConfig: {
    url: string;
    key: string;
  };
}

export * from './types/terminology';