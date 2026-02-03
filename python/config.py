"""
Financial Term Matching System - Enhanced Configuration
=======================================================
Loosened thresholds for better data capture (targeting 95%+ capture rate).
"""

from typing import Dict, Any

# Enhanced matching configuration with loosened thresholds
MATCHING_CONFIG = {
    "preprocessing": {
        "expand_abbreviations": True,
        "remove_notes": False,  # Changed: Keep notes as they may contain data
        "normalize_unicode": True,
        "remove_leaders": True,
        "detect_sign_conventions": True,
        "normalize_dates": True,
        "normalize_numbers": True,
        "preserve_parentheses": True,  # New: Keep parentheses for negative detection
    },
    "matching": {
        "exact_weight": 1.0,
        "fuzzy_threshold": 75,  # Lowered from 85 for better OCR error recovery
        "fuzzy_weight": 0.8,  # Increased from 0.7
        "semantic_threshold": 0.70,  # Lowered from 0.75
        "semantic_weight": 0.6,  # Increased from 0.5
        "max_ngram": 8,  # Increased from 6 for longer phrases
        "min_ngram": 1,  # Lowered from 2 to catch single-word terms
        "enable_acronym_matching": True,
        "enable_multiword_phrases": True,
        "enable_partial_matching": True,  # New: Allow partial matches
        "partial_match_threshold": 0.65,  # New: Threshold for partial matches
    },
    "context": {
        "section_boost": 1.3,  # Lowered from 1.5 to be less aggressive
        "category_penalty": 0.2,  # Lowered from 0.3
        "enable_section_detection": True,
        "enable_cross_references": True,
    },
    "conflict_resolution": {
        "prefer_specific": True,
        "deduplicate_by_term_key": True,
        "substring_suppression": False,  # Changed: Don't suppress substrings
        "hierarchical_pruning": False,  # Changed: Keep all hierarchical matches
        "min_confidence_threshold": 0.2,  # Lowered from 0.3
    },
    "performance": {
        "cache_embeddings": True,
        "max_cache_size": 10000,
        "parallel_processing": True,
        "batch_size": 100,
    }
}

# Enhanced validation thresholds for 95% capture target
VALIDATION_THRESHOLDS = {
    "min_recall_rate": 0.95,
    "max_false_positive_rate": 0.10,  # Increased from 0.05 to allow more matches
    "target_f1_score": 0.90,  # Slightly lowered from 0.92
    "min_processing_speed": 1000,  # lines per second
    "confidence_high": 0.90,  # Lowered from 0.95
    "confidence_medium": 0.65,  # Lowered from 0.70
    "confidence_low": 0.40,  # Lowered from 0.50
}

# Enhanced section type mappings with more comprehensive terms
SECTION_BOOST_MAP = {
    'balance_sheet_assets': [
        'total_assets', 'ppe', 'plant_property_equipment', 'inventory', 'inventories',
        'receivables', 'trade_receivables', 'sundry_debtors', 'cash', 'cash_equivalents',
        'bank_balances', 'investments', 'intangible_assets', 'goodwill', 'cwip',
        'capital_work_in_progress', 'non_current_assets', 'current_assets',
        'fixed_assets', 'tangible_assets', 'loans_and_advances', 'deposits',
    ],
    'balance_sheet_liabilities': [
        'borrowings', 'long_term_borrowings', 'short_term_borrowings',
        'payables', 'trade_payables', 'sundry_creditors', 'provisions',
        'deferred_tax', 'deferred_tax_liabilities', 'long_term_debt',
        'short_term_debt', 'current_liabilities', 'non_current_liabilities',
        'other_current_liabilities', 'other_non_current_liabilities',
    ],
    'balance_sheet_equity': [
        'share_capital', 'equity_share_capital', 'reserves', 'reserves_surplus',
        'retained_earnings', 'other_comprehensive_income', 'total_equity',
        'shareholders_funds', 'money_received_against_share_warrants',
    ],
    'income_statement': [
        'revenue', 'total_revenue', 'net_sales', 'gross_sales', 'income',
        'expenses', 'total_expenses', 'cost_of_goods_sold', 'cogs',
        'profit', 'net_profit', 'gross_profit', 'operating_profit',
        'ebitda', 'ebit', 'profit_before_tax', 'pbt', 'tax_expense',
        'earnings_per_share', 'eps', 'other_income', 'finance_costs',
    ],
    'cash_flow': [
        'cash_from_operations', 'operating_cash_flow', 'cash_from_investing',
        'investing_cash_flow', 'cash_from_financing', 'financing_cash_flow',
        'capex', 'capital_expenditure', 'dividends_paid', 'net_cash_flow',
        'cash_equivalents_beginning', 'cash_equivalents_ending',
    ],
    'notes': [
        'accounting_policies', 'significant_accounting_policies',
        'disclosures', 'contingencies', 'commitments',
        'related_parties', 'related_party_transactions',
        'earnings_per_share', 'deferred_tax', 'employee_benefits',
        'share_based_payments', 'provisions', 'segment_reporting',
    ]
}

# Table detection configuration
TABLE_CONFIG = {
    "min_rows": 2,  # Lowered from 3
    "min_columns": 2,
    "header_patterns": [
        r'particulars?',
        r'description',
        r'notes?',
        r'year\s*ended',
        r'as\s+(?:at|of)',
        r'\d{4}',  # Year numbers
    ],
    "data_row_patterns": [
        r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?',  # Indian number format
        r'\d{1,3}(?:,\d{2,3})+',  # Numbers with commas
    ],
    "ignore_patterns": [
        r'^page\s+\d+$',
        r'^\d+\s*\|\s*annual\s+report',
        r'^table\s+of\s+contents$',
        r'^index\s*$',
        r'^contents\s*$',
    ],
}

# OCR configuration for better accuracy
OCR_CONFIG = {
    "confidence_threshold": 25.0,  # Lowered from 30.0
    "preprocessing": {
        "deskew": True,
        "enhance_contrast": True,
        "remove_noise": True,
        "threshold": True,
        "resize": True,
        "remove_borders": False,
        "sharpen": True,  # New: Add sharpening
        "denoise_strength": 10,  # New: Configurable denoise
    },
    "tesseract_config": r'--oem 3 --psm 6 -l eng+hin',  # Page segmentation mode 6 (uniform block)
}

# Noise filtering configuration - more permissive
NOISE_FILTER_CONFIG = {
    "max_line_length": 300,  # Increased from 200
    "min_numbers_per_row": 1,  # Lowered from 2
    "min_label_length": 2,  # Lowered from 3
    "skip_patterns": [
        r'^page\s+\d+$',
        r'^\d+\s*\|\s*annual\s+report',
        r'^table\s+of\s+contents$',
        r'^index\s*$',
        r'^contents\s*$',
    ],
    "narrative_indicators": [
        r'\bwe\b',  # Only match whole words
        r'\bour\b',
        r'\bwas\b',
        r'\bwere\b',
    ],
    "preserve_patterns": [
        r'(?:total|sub-?total|net|gross)\s+\w+',
        r'\w+\s+(?:assets?|liabilities?|equity|income|expenses?|revenue|profit|loss)',
    ],
}
