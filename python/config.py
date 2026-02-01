"""
Financial Term Matching System - Configuration
==============================================
Centralized configuration for all matching parameters.
"""

from typing import Dict, Any

MATCHING_CONFIG = {
    "preprocessing": {
        "expand_abbreviations": True,
        "remove_notes": True,
        "normalize_unicode": True,
        "remove_leaders": True,
        "detect_sign_conventions": True,
        "normalize_dates": True,
        "normalize_numbers": True
    },
    "matching": {
        "exact_weight": 1.0,
        "fuzzy_threshold": 85,
        "fuzzy_weight": 0.7,
        "semantic_threshold": 0.75,
        "semantic_weight": 0.5,
        "max_ngram": 6,
        "min_ngram": 2,
        "enable_acronym_matching": True,
        "enable_multiword_phrases": True
    },
    "context": {
        "section_boost": 1.5,
        "category_penalty": 0.3,
        "enable_section_detection": True,
        "enable_cross_references": True
    },
    "conflict_resolution": {
        "prefer_specific": True,
        "deduplicate_by_term_key": True,
        "substring_suppression": True,
        "hierarchical_pruning": True,
        "min_confidence_threshold": 0.3
    },
    "performance": {
        "cache_embeddings": True,
        "max_cache_size": 10000,
        "parallel_processing": True,
        "batch_size": 100
    }
}

# Validation thresholds
VALIDATION_THRESHOLDS = {
    "min_recall_rate": 0.95,
    "max_false_positive_rate": 0.05,
    "target_f1_score": 0.92,
    "min_processing_speed": 1000,  # lines per second
    "confidence_high": 0.95,
    "confidence_medium": 0.70,
    "confidence_low": 0.50
}

# Section type mappings for context boosting
SECTION_BOOST_MAP = {
    'balance_sheet_assets': [
        'total_assets', 'ppe', 'inventory', 'receivables', 'cash',
        'investments', 'intangible_assets', 'goodwill'
    ],
    'balance_sheet_liabilities': [
        'borrowings', 'payables', 'provisions', 'deferred_tax',
        'long_term_debt', 'short_term_debt'
    ],
    'balance_sheet_equity': [
        'share_capital', 'reserves', 'retained_earnings', 
        'other_comprehensive_income', 'total_equity'
    ],
    'income_statement': [
        'revenue', 'expenses', 'profit', 'ebitda', 'ebit', 
        'net_profit', 'gross_profit', 'operating_profit'
    ],
    'cash_flow': [
        'cash_from_operations', 'cash_from_investing', 'cash_from_financing',
        'capex', 'dividends_paid', 'net_cash_flow'
    ],
    'notes': [
        'accounting_policies', 'disclosures', 'contingencies',
        'commitments', 'related_parties'
    ]
}
