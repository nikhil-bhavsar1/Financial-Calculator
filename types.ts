export interface FormulaBreakdown {
  step: string;
  formula: string;
  description?: string;
}

export interface FinancialItem {
  id: string;
  label: string;
  normalizedLabel?: string; // Lowercase, whitespace-normalized version for matching
  currentYear: number;
  previousYear: number;
  allYears?: { [year: string]: number }; // Multiple year support (e.g., {"2022": 100, "2023": 120})
  variation: number;
  variationPercent: number;
  sourcePage: string;
  sourceLine?: number; // Exact line number in source document
  rawLine?: string;
  rawLineNormalized?: string; // Normalized version of raw line
  isAutoCalc?: boolean;
  hasWarning?: boolean;
  calculationError?: string;
  formula?: string;
  interpretation?: string;
  breakdown?: FormulaBreakdown[];
  statementType?: string; // 'balance_sheet', 'income_statement', 'cashflow'
  isImportant?: boolean;
  confidence?: number; // Extraction confidence score (0-1)
  extractionMethod?: string; // 'native', 'text_pattern', 'ocr', 'hybrid'
  tableIndex?: number; // Index of table this item came from
  rowIndex?: number; // Row index within table
  colIndex?: number; // Column index within table
  financialCategory?: string; // 'assets', 'liabilities', 'equity', 'income', 'expenses'
  isHeader?: boolean; // Whether this is a header row
  isTotal?: boolean; // Whether this is a total/subtotal row
  isNegative?: boolean; // Whether value is negative
  unit?: string; // Currency unit (e.g., 'INR', 'USD')
  scale?: string; // Scale (e.g., 'thousands', 'millions', 'lakhs', 'crores')
  noteReferences?: string[]; // References to footnotes
  isIndAS?: boolean; // Whether item uses Ind AS terminology
  indianScale?: 'lakhs' | 'crores' | 'thousands' | 'millions'; // Indian number scale
  signMultiplier?: number; // Ind AS sign convention multiplier (+1 or -1)
  metadata?: {
    // Additional metadata for advanced parsing
    bbox?: { x: number; y: number; width: number; height: number }; // Bounding box
    fontSize?: number;
    isBold?: boolean;
    alignment?: 'left' | 'center' | 'right';
    [key: string]: any;
  };
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
    [year: string]: string;
  };
  status: InputStatus;
  confidence?: number;
}

export type AiProvider = 'gemini' | 'groq' | 'openai' | 'openrouter' | 'opencode' | 'local_llm' | 'cerebras' | 'nvidia';

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
    cerebras: string;
    nvidia: string;
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
  // Financial Data APIs
  financialDataApis: {
    alphaVantage: string;
    twelveData: string;
    fyersAppId: string;
    fyersAccessToken: string;
    angelOneApiKey: string;
    angelOneClientCode: string;
    angelOnePassword: string;
  };
}

export interface NSECompany {
  symbol: string;
  name: string;
  isin: string;
  sector: string;
  industry: string;
  market_cap?: number;
  face_value?: number;
  listing_date?: string;
  exchange: 'NSE';
}

export interface BSECompany {
  symbol: string;
  name: string;
  isin: string;
  sector: string;
  industry: string;
  market_cap?: number;
  face_value?: number;
  listing_date?: string;
  exchange: 'BSE';
}

export interface StockQuote {
  symbol: string;
  last_price: number;
  change: number;
  change_percent: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timestamp: string;
  exchange: 'NSE' | 'BSE';
}

export type CompanySearchResult = NSECompany | BSECompany;

export interface CompanySearchParams {
  query: string;
  exchange?: 'NSE' | 'BSE' | 'BOTH';
  limit?: number;
}

export interface ScraperResponse<T> {
  success: boolean;
  results?: T; // Can be array or object depending on endpoint
  error?: string;
  errors?: string[]; // Multiple errors from search
  query?: string;
  exchange?: string;
  count?: number;
  message?: string;
}

export * from './types/terminology';
export interface DatabaseUpdate {
  action: 'initial' | 'incremental';
  table: string;
  data: FinancialItem[];
}

