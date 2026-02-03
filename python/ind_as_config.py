
"""
Configuration for Ind AS (Indian Accounting Standards) specific structures and schedules.
Used by metrics_engine and validators to recognize and validate Indian filings.

This file acts as a hub for the Ind AS configuration, which is split into multiple files
(ind_as_config_1.py to ind_as_config_9.py) to manage size and organization.
"""

from .ind_as_config_1 import (
    IND_AS_MANDATORY_SCHEDULES,
    BALANCE_SHEET_EQUITY,
    BALANCE_SHEET_NON_CURRENT_LIABILITIES,
    BALANCE_SHEET_CURRENT_LIABILITIES,
    BALANCE_SHEET_NON_CURRENT_ASSETS,
    BALANCE_SHEET_CURRENT_ASSETS,
    STATEMENT_OF_PROFIT_LOSS_REVENUE,
    STATEMENT_OF_PROFIT_LOSS_EXPENSES,
    STATEMENT_OF_PROFIT_LOSS_TAX_AND_PROFIT,
)

from .ind_as_config_2 import (
    OTHER_COMPREHENSIVE_INCOME,
    CASH_FLOW_OPERATING_ACTIVITIES,
    CASH_FLOW_INVESTING_ACTIVITIES,
    CASH_FLOW_FINANCING_ACTIVITIES,
    CASH_FLOW_RECONCILIATION,
    STATEMENT_OF_CHANGES_IN_EQUITY,
    PPE_NOTES,
    INTANGIBLE_ASSETS_NOTES,
    INVESTMENT_PROPERTY_NOTES,
)

from .ind_as_config_3 import (
    INVESTMENTS_NOTES,
    INVENTORIES_NOTES,
    TRADE_RECEIVABLES_NOTES,
    CASH_AND_BANK_BALANCES_NOTES,
    LOANS_AND_ADVANCES_NOTES,
    OTHER_ASSETS_NOTES,
    SHARE_CAPITAL_NOTES,
    OTHER_EQUITY_RESERVES_NOTES,
)

from .ind_as_config_4 import (
    BORROWINGS_NOTES,
    TRADE_PAYABLES_NOTES,
    OTHER_LIABILITIES_NOTES,
    PROVISIONS_NOTES,
    CONTINGENT_LIABILITIES_AND_COMMITMENTS,
    RELATED_PARTY_DISCLOSURES,
)

from .ind_as_config_5 import (
    SEGMENT_REPORTING,
    EARNINGS_PER_SHARE,
    FINANCIAL_INSTRUMENTS_CLASSIFICATION,
    FINANCIAL_INSTRUMENTS_FAIR_VALUE,
    FINANCIAL_INSTRUMENTS_RISK_MANAGEMENT,
    LEASES_IND_AS_116,
)

from .ind_as_config_6 import (
    REVENUE_FROM_CONTRACTS_IND_AS_115,
    EMPLOYEE_BENEFITS_IND_AS_19,
    DEFERRED_TAX_ASSETS_AND_LIABILITIES,
    INCOME_TAX_RECONCILIATION,
    BUSINESS_COMBINATIONS_AND_GOODWILL,
    CONSOLIDATED_FINANCIAL_STATEMENTS,
    SHARE_BASED_PAYMENTS_IND_AS_102,
    GOVERNMENT_GRANTS,
)

from .ind_as_config_7 import (
    FOREIGN_CURRENCY_TRANSACTIONS,
    BORROWING_COSTS,
    IMPAIRMENT_OF_ASSETS,
    EVENTS_AFTER_REPORTING_PERIOD,
)

from .ind_as_config_8 import (
    FIRST_TIME_ADOPTION_IND_AS,
    CSR_EXPENDITURE,
    AUDIT_REPORT_TERMS,
    DIRECTORS_REPORT_TERMS,
)

from .ind_as_config_9 import (
    XBRL_TAXONOMY_IDENTIFIERS,
    KEY_FINANCIAL_RATIOS,
    GENERAL_INFORMATION_AND_ACCOUNTING_POLICIES,
)

# =============================================================================
# MASTER CONFIGURATION AGGREGATOR
# =============================================================================

IND_AS_COMPREHENSIVE_CONFIG = {
    # Balance Sheet Components (Sections 1-5)
    'balance_sheet_equity': BALANCE_SHEET_EQUITY,
    'balance_sheet_non_current_liabilities': BALANCE_SHEET_NON_CURRENT_LIABILITIES,
    'balance_sheet_current_liabilities': BALANCE_SHEET_CURRENT_LIABILITIES,
    'balance_sheet_non_current_assets': BALANCE_SHEET_NON_CURRENT_ASSETS,
    'balance_sheet_current_assets': BALANCE_SHEET_CURRENT_ASSETS,
    
    # Statement of Profit and Loss (Sections 6-8)
    'statement_of_profit_loss_revenue': STATEMENT_OF_PROFIT_LOSS_REVENUE,
    'statement_of_profit_loss_expenses': STATEMENT_OF_PROFIT_LOSS_EXPENSES,
    'statement_of_profit_loss_tax_and_profit': STATEMENT_OF_PROFIT_LOSS_TAX_AND_PROFIT,
    
    # Other Comprehensive Income (Section 9)
    'other_comprehensive_income': OTHER_COMPREHENSIVE_INCOME,
    
    # Cash Flow Statement (Sections 10-12)
    'cash_flow_operating_activities': CASH_FLOW_OPERATING_ACTIVITIES,
    'cash_flow_investing_activities': CASH_FLOW_INVESTING_ACTIVITIES,
    'cash_flow_financing_activities': CASH_FLOW_FINANCING_ACTIVITIES,
    'cash_flow_reconciliation': CASH_FLOW_RECONCILIATION,
    
    # Statement of Changes in Equity (Section 13)
    'statement_of_changes_in_equity': STATEMENT_OF_CHANGES_IN_EQUITY,
    
    # Notes to Accounts - Assets (Sections 14-20)
    'ppe_notes': PPE_NOTES,
    'intangible_assets_notes': INTANGIBLE_ASSETS_NOTES,
    'investment_property_notes': INVESTMENT_PROPERTY_NOTES,
    'investments_notes': INVESTMENTS_NOTES,
    'inventories_notes': INVENTORIES_NOTES,
    'trade_receivables_notes': TRADE_RECEIVABLES_NOTES,
    'cash_and_bank_balances_notes': CASH_AND_BANK_BALANCES_NOTES,
    
    # Notes to Accounts - Liabilities and Equity (Sections 21-28)
    'loans_and_advances_notes': LOANS_AND_ADVANCES_NOTES,
    'other_assets_notes': OTHER_ASSETS_NOTES,
    'share_capital_notes': SHARE_CAPITAL_NOTES,
    'other_equity_reserves_notes': OTHER_EQUITY_RESERVES_NOTES,
    'borrowings_notes': BORROWINGS_NOTES,
    'trade_payables_notes': TRADE_PAYABLES_NOTES,
    'other_liabilities_notes': OTHER_LIABILITIES_NOTES,
    'provisions_notes': PROVISIONS_NOTES,
    
    # Contingencies, Related Parties, Segments, EPS (Sections 29-32)
    'contingent_liabilities_and_commitments': CONTINGENT_LIABILITIES_AND_COMMITMENTS,
    'related_party_disclosures': RELATED_PARTY_DISCLOSURES,
    'segment_reporting': SEGMENT_REPORTING,
    'earnings_per_share': EARNINGS_PER_SHARE,
    
    # Financial Instruments and Leases (Sections 33-36)
    'financial_instruments_classification': FINANCIAL_INSTRUMENTS_CLASSIFICATION,
    'financial_instruments_fair_value': FINANCIAL_INSTRUMENTS_FAIR_VALUE,
    'financial_instruments_risk_management': FINANCIAL_INSTRUMENTS_RISK_MANAGEMENT,
    'leases_ind_as_116': LEASES_IND_AS_116,
    
    # Revenue, Employee Benefits, Tax (Sections 37-40)
    'revenue_from_contracts_ind_as_115': REVENUE_FROM_CONTRACTS_IND_AS_115,
    'employee_benefits_ind_as_19': EMPLOYEE_BENEFITS_IND_AS_19,
    'deferred_tax_assets_and_liabilities': DEFERRED_TAX_ASSETS_AND_LIABILITIES,
    'income_tax_reconciliation': INCOME_TAX_RECONCILIATION,
    
    # Business Combinations, Consolidation, Share-based Payments, Grants (Sections 41-44)
    'business_combinations_and_goodwill': BUSINESS_COMBINATIONS_AND_GOODWILL,
    'consolidated_financial_statements': CONSOLIDATED_FINANCIAL_STATEMENTS,
    'share_based_payments_ind_as_102': SHARE_BASED_PAYMENTS_IND_AS_102,
    'government_grants': GOVERNMENT_GRANTS,
    
    # Foreign Currency, Borrowing Costs, Impairment, Events (Sections 45-48)
    'foreign_currency_transactions': FOREIGN_CURRENCY_TRANSACTIONS,
    'borrowing_costs': BORROWING_COSTS,
    'impairment_of_assets': IMPAIRMENT_OF_ASSETS,
    'events_after_reporting_period': EVENTS_AFTER_REPORTING_PERIOD,
    
    # First-time Adoption, CSR, Audit, Directors Report (Sections 49-52)
    'first_time_adoption_ind_as': FIRST_TIME_ADOPTION_IND_AS,
    'csr_expenditure': CSR_EXPENDITURE,
    'audit_report_terms': AUDIT_REPORT_TERMS,
    'directors_report_terms': DIRECTORS_REPORT_TERMS,
    
    # XBRL, Ratios, General Information (Sections 53-55)
    'xbrl_taxonomy_identifiers': XBRL_TAXONOMY_IDENTIFIERS,
    'key_financial_ratios': KEY_FINANCIAL_RATIOS,
    'general_information_and_accounting_policies': GENERAL_INFORMATION_AND_ACCOUNTING_POLICIES,
}


# =============================================================================
# UTILITY FUNCTIONS FOR CONFIG ACCESS
# =============================================================================

def get_all_terms():
    """
    Returns a flattened list of all terms from the configuration.
    """
    all_terms = []
    
    def extract_terms(obj, prefix=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                extract_terms(value, f"{prefix}.{key}" if prefix else key)
        elif isinstance(obj, list):
            all_terms.extend(obj)
        elif isinstance(obj, str):
            all_terms.append(obj)
    
    extract_terms(IND_AS_COMPREHENSIVE_CONFIG)
    return list(set(all_terms))


def get_terms_by_section(section_name):
    """
    Returns all terms for a specific section.
    """
    if section_name in IND_AS_COMPREHENSIVE_CONFIG:
        terms = []
        def extract_terms(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    extract_terms(value)
            elif isinstance(obj, list):
                terms.extend(obj)
            elif isinstance(obj, str):
                terms.append(obj)
        
        extract_terms(IND_AS_COMPREHENSIVE_CONFIG[section_name])
        return list(set(terms))
    return []


def search_term(term):
    """
    Searches for a term and returns all sections where it appears.
    """
    results = []
    
    def search_in_obj(obj, path=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                search_in_obj(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            if term.lower() in [t.lower() for t in obj]:
                results.append(path)
        elif isinstance(obj, str) and term.lower() == obj.lower():
            results.append(path)
    
    search_in_obj(IND_AS_COMPREHENSIVE_CONFIG)
    return results


def get_config_statistics():
    """
    Returns statistics about the configuration.
    """
    all_terms = get_all_terms()
    sections = list(IND_AS_COMPREHENSIVE_CONFIG.keys())
    
    return {
        'total_sections': len(sections),
        'total_unique_terms': len(all_terms),
        'sections': sections,
    }


# =============================================================================
# EXPORT CONFIGURATION
# =============================================================================

__all__ = [
    'IND_AS_COMPREHENSIVE_CONFIG',
    'get_all_terms',
    'get_terms_by_section',
    'search_term',
    'get_config_statistics',
    
    # Individual section exports
    'IND_AS_MANDATORY_SCHEDULES',
    'BALANCE_SHEET_EQUITY',
    'BALANCE_SHEET_NON_CURRENT_LIABILITIES',
    'BALANCE_SHEET_CURRENT_LIABILITIES',
    'BALANCE_SHEET_NON_CURRENT_ASSETS',
    'BALANCE_SHEET_CURRENT_ASSETS',
    'STATEMENT_OF_PROFIT_LOSS_REVENUE',
    'STATEMENT_OF_PROFIT_LOSS_EXPENSES',
    'STATEMENT_OF_PROFIT_LOSS_TAX_AND_PROFIT',
    'OTHER_COMPREHENSIVE_INCOME',
    'CASH_FLOW_OPERATING_ACTIVITIES',
    'CASH_FLOW_INVESTING_ACTIVITIES',
    'CASH_FLOW_FINANCING_ACTIVITIES',
    'CASH_FLOW_RECONCILIATION',
    'STATEMENT_OF_CHANGES_IN_EQUITY',
    'PPE_NOTES',
    'INTANGIBLE_ASSETS_NOTES',
    'INVESTMENT_PROPERTY_NOTES',
    'INVESTMENTS_NOTES',
    'INVENTORIES_NOTES',
    'TRADE_RECEIVABLES_NOTES',
    'CASH_AND_BANK_BALANCES_NOTES',
    'LOANS_AND_ADVANCES_NOTES',
    'OTHER_ASSETS_NOTES',
    'SHARE_CAPITAL_NOTES',
    'OTHER_EQUITY_RESERVES_NOTES',
    'BORROWINGS_NOTES',
    'TRADE_PAYABLES_NOTES',
    'OTHER_LIABILITIES_NOTES',
    'PROVISIONS_NOTES',
    'CONTINGENT_LIABILITIES_AND_COMMITMENTS',
    'RELATED_PARTY_DISCLOSURES',
    'SEGMENT_REPORTING',
    'EARNINGS_PER_SHARE',
    'FINANCIAL_INSTRUMENTS_CLASSIFICATION',
    'FINANCIAL_INSTRUMENTS_FAIR_VALUE',
    'FINANCIAL_INSTRUMENTS_RISK_MANAGEMENT',
    'LEASES_IND_AS_116',
    'REVENUE_FROM_CONTRACTS_IND_AS_115',
    'EMPLOYEE_BENEFITS_IND_AS_19',
    'DEFERRED_TAX_ASSETS_AND_LIABILITIES',
    'INCOME_TAX_RECONCILIATION',
    'BUSINESS_COMBINATIONS_AND_GOODWILL',
    'CONSOLIDATED_FINANCIAL_STATEMENTS',
    'SHARE_BASED_PAYMENTS_IND_AS_102',
    'GOVERNMENT_GRANTS',
    'FOREIGN_CURRENCY_TRANSACTIONS',
    'BORROWING_COSTS',
    'IMPAIRMENT_OF_ASSETS',
    'EVENTS_AFTER_REPORTING_PERIOD',
    'FIRST_TIME_ADOPTION_IND_AS',
    'CSR_EXPENDITURE',
    'AUDIT_REPORT_TERMS',
    'DIRECTORS_REPORT_TERMS',
    'XBRL_TAXONOMY_IDENTIFIERS',
    'KEY_FINANCIAL_RATIOS',
    'GENERAL_INFORMATION_AND_ACCOUNTING_POLICIES',
]
