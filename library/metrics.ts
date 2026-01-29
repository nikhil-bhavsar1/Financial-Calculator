import { TermMapping } from '../types/terminology';

import { INCOME_STATEMENT_TERMS } from './terms/incomeStatement';
import { BALANCE_SHEET_ASSETS_TERMS } from './terms/balanceSheetAssets';
import { BALANCE_SHEET_LIABILITIES_TERMS } from './terms/balanceSheetLiabilities';
import { BALANCE_SHEET_EQUITY_TERMS } from './terms/balanceSheetEquity';
import { CASH_FLOW_STATEMENT_TERMS } from './terms/cashFlowStatement';
import { FINANCIAL_RATIOS_TERMS, PER_SHARE_DATA_TERMS } from './terms/ratiosAndPerShare';
import { OTHER_COMPREHENSIVE_INCOME_TERMS, SEGMENT_REPORTING_TERMS, TAX_TERMS } from './terms/ociAndSegments';
import { TAX_DETAILS_TERMS } from './terms/taxDetails';
import {
  ALL_ADDITIONAL_TERMS,
  ADDITIONAL_REVENUE_TERMS,
  ADDITIONAL_EXPENSE_TERMS,
  IFRS18_TERMS,
  ADDITIONAL_ASSET_TERMS,
  ADDITIONAL_LIABILITY_TERMS,
  ADDITIONAL_EQUITY_TERMS,
  ADDITIONAL_OCI_TERMS,
  ADDITIONAL_CASH_FLOW_TERMS,
  DISCLOSURE_TERMS,
  CHANGES_IN_EQUITY_TERMS
} from './terms/additionalComprehensiveTerms';
import { getUserTerms, saveUserTerms, isUserAddedTerm } from './terms/userTerms';

// System-defined terms (built-in, read-only at runtime)
export const SYSTEM_METRICS: TermMapping[] = [
  ...INCOME_STATEMENT_TERMS,
  ...BALANCE_SHEET_ASSETS_TERMS,
  ...BALANCE_SHEET_LIABILITIES_TERMS,
  ...BALANCE_SHEET_EQUITY_TERMS,
  ...CASH_FLOW_STATEMENT_TERMS,
  ...FINANCIAL_RATIOS_TERMS,
  ...PER_SHARE_DATA_TERMS,
  ...OTHER_COMPREHENSIVE_INCOME_TERMS,
  ...SEGMENT_REPORTING_TERMS,
  ...TAX_TERMS,
  ...TAX_DETAILS_TERMS,
  ...ALL_ADDITIONAL_TERMS
];

// Build set of system term IDs for deduplication
export const SYSTEM_TERM_IDS = new Set(SYSTEM_METRICS.map(t => t.id));

// Combined metrics: System + User terms (with deduplication)
export const METRICS: TermMapping[] = [
  ...SYSTEM_METRICS,
  ...getUserTerms().filter(t => !SYSTEM_TERM_IDS.has(t.id))
];

// For backward compatibility if needed, or alias
export const INPUT_METRICS = METRICS;

// User term management utilities
export { getUserTerms, saveUserTerms, isUserAddedTerm };

export {
  INCOME_STATEMENT_TERMS,
  BALANCE_SHEET_ASSETS_TERMS,
  BALANCE_SHEET_LIABILITIES_TERMS,
  BALANCE_SHEET_EQUITY_TERMS,
  CASH_FLOW_STATEMENT_TERMS,
  FINANCIAL_RATIOS_TERMS,
  PER_SHARE_DATA_TERMS,
  OTHER_COMPREHENSIVE_INCOME_TERMS,
  SEGMENT_REPORTING_TERMS,
  TAX_TERMS,
  TAX_DETAILS_TERMS,
  // Additional term exports
  ALL_ADDITIONAL_TERMS,
  ADDITIONAL_REVENUE_TERMS,
  ADDITIONAL_EXPENSE_TERMS,
  IFRS18_TERMS,
  ADDITIONAL_ASSET_TERMS,
  ADDITIONAL_LIABILITY_TERMS,
  ADDITIONAL_EQUITY_TERMS,
  ADDITIONAL_OCI_TERMS,
  ADDITIONAL_CASH_FLOW_TERMS,
  DISCLOSURE_TERMS,
  CHANGES_IN_EQUITY_TERMS
};