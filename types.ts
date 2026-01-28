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
  value: string;
  targetYear?: 'current' | 'previous'; // User-specified time period for this input
  status: InputStatus;
  confidence?: number;
}

export type AiProvider = 'gemini' | 'groq' | 'openai' | 'openrouter' | 'opencode';

export interface AppSettings {
  theme: 'light' | 'dark';
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
  supabaseConfig: {
    url: string;
    key: string;
  };
}

export * from './types/terminology';