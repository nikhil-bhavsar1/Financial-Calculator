export interface TermMapping {
    id: string;                    // Unique identifier like REV_001
    category: TermCategory;
    subcategory?: string;
    key: string;                   // System key for internal reference
    label: string;                 // Display name
    description?: string;          // Detailed description
    keywords_indas: string[];      // Indian Accounting Standards keywords
    keywords_gaap: string[];       // US GAAP keywords
    keywords_ifrs: string[];       // IFRS keywords
    related_standards?: {
        indas?: string[];            // e.g., ["IndAS 115", "IndAS 18"]
        gaap?: string[];             // e.g., ["ASC 606", "ASC 842"]
        ifrs?: string[];             // e.g., ["IFRS 15", "IFRS 16"]
    };
    aliases?: string[];            // Common alternative names
    calculation?: string;          // Formula if applicable
    sign_convention?: 'positive' | 'negative' | 'both';
    data_type?: 'currency' | 'percentage' | 'ratio' | 'number' | 'date' | 'text';
    priority?: number;             // Matching priority (higher = more important)
    is_computed?: boolean;         // Whether this is a computed field
    components?: string[];         // Component term keys for computed fields
}

export type TermCategory =
    | 'Revenue'
    | 'Cost of Revenue'
    | 'Operating Expenses'
    | 'Other Income & Expenses'
    | 'Finance Costs'
    | 'Tax'
    | 'Profit & Loss'
    | 'Current Assets'
    | 'Non-Current Assets'
    | 'Current Liabilities'
    | 'Non-Current Liabilities'
    | 'Equity'
    | 'Cash Flow - Operating'
    | 'Cash Flow - Investing'
    | 'Cash Flow - Financing'
    | 'Per Share Data'
    | 'Ratios & Metrics'
    | 'Employee Benefits'
    | 'Share-based Payments'
    | 'Leases'
    | 'Financial Instruments'
    | 'Fair Value'
    | 'Impairment'
    | 'Consolidation'
    | 'Foreign Currency'
    | 'Segment Reporting'
    | 'Related Parties'
    | 'Contingencies'
    | 'Provisions'
    | 'Inventory'
    | 'Property Plant Equipment'
    | 'Intangible Assets'
    | 'Investments'
    | 'Receivables'
    | 'Payables'
    | 'Debt'
    | 'Derivatives'
    | 'Hedge Accounting'
    | 'Business Combinations'
    | 'Discontinued Operations'
    | 'Government Grants'
    | 'Insurance'
    | 'Agriculture'
    | 'Mining & Exploration'
    | 'Income Statement'
    | 'Balance Sheet'
    | 'Cash Flow Statement'
    | 'Balance Sheet - Assets'
    | 'Balance Sheet - Liabilities'
    | 'Balance Sheet - Equity'
    | 'Financial Ratios'
    | 'Other Comprehensive Income'
    | 'Income Statement - IFRS 18'
    | 'Disclosures'
    | 'Statement of Changes in Equity'
    | 'Misc';

export const CATEGORY_OPTIONS: TermCategory[] = [
    'Agriculture',
    'Balance Sheet',
    'Balance Sheet - Assets',
    'Balance Sheet - Equity',
    'Balance Sheet - Liabilities',
    'Business Combinations',
    'Cash Flow - Financing',
    'Cash Flow - Investing',
    'Cash Flow - Operating',
    'Cash Flow Statement',
    'Consolidation',
    'Contingencies',
    'Cost of Revenue',
    'Current Assets',
    'Current Liabilities',
    'Debt',
    'Derivatives',
    'Disclosures',
    'Discontinued Operations',
    'Employee Benefits',
    'Equity',
    'Fair Value',
    'Finance Costs',
    'Financial Instruments',
    'Financial Ratios',
    'Foreign Currency',
    'Government Grants',
    'Hedge Accounting',
    'Impairment',
    'Income Statement',
    'Income Statement - IFRS 18',
    'Insurance',
    'Intangible Assets',
    'Inventory',
    'Investments',
    'Leases',
    'Mining & Exploration',
    'Misc',
    'Non-Current Assets',
    'Non-Current Liabilities',
    'Operating Expenses',
    'Other Comprehensive Income',
    'Other Income & Expenses',
    'Payables',
    'Per Share Data',
    'Profit & Loss',
    'Property Plant Equipment',
    'Provisions',
    'Ratios & Metrics',
    'Receivables',
    'Related Parties',
    'Revenue',
    'Segment Reporting',
    'Share-based Payments',
    'Statement of Changes in Equity',
    'Tax',
];
