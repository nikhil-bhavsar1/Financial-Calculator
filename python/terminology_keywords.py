"""
Unified Comprehensive Terminology Keywords Module
Maps financial terms to metrics with all synonyms from the complete cross-sectional database.
All keywords from all accounting standards (IndAS, GAAP, IFRS) are unified and cross-referenced.
"""

import json
import os
import re
import sys
from typing import Dict, List, Optional, Set, Any

# =============================================================================
# DATABASE LOADING
# =============================================================================

def load_unified_database():
    """Load the unified comprehensive terms database with all indexes."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'terms_database.json'),
        os.path.join(os.path.dirname(__file__), 'python', 'terms_database.json'),
        'terms_database.json',
        'python/terms_database.json',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    print(f"[Terminology] Loaded unified database:", file=sys.stderr)
                    print(f"[Terminology]   - {metadata.get('total_terms', 0)} terms", file=sys.stderr)
                    print(f"[Terminology]   - {metadata.get('unique_keywords', 0)} unique keywords", file=sys.stderr)
                    print(f"[Terminology]   - {len(metadata.get('categories', []))} categories", file=sys.stderr)
                    return data
            except Exception as e:
                print(f"[Terminology] Error loading {path}: {e}", file=sys.stderr)
                continue
    
    print("[Terminology] Warning: Could not load terms_database.json", file=sys.stderr)
    return {"terms": [], "indexes": {}}

# Load the unified database
DATABASE = load_unified_database()
ALL_TERMS = DATABASE.get("terms", [])
INDEXES = DATABASE.get("indexes", {})

# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================

# Build comprehensive terminology map from unified database
TERMINOLOGY_MAP: Dict[str, Dict] = {}
KEYWORD_TO_TERM: Dict[str, List[Dict]] = {}

# Define boost values based on term importance for matching priority
BOOST_VALUES = {
    # Income Statement - Critical items
    'total_revenue': 3.0,
    'net_sales': 2.8,
    'cost_of_goods_sold': 2.7,
    'gross_profit': 2.7,
    'operating_profit': 2.8,
    'ebitda': 2.9,
    'profit_before_tax': 2.7,
    'tax_expense': 2.5,
    'profit_for_the_year': 3.0,
    'net_income': 3.0,
    'earnings_per_share': 2.8,
    'total_income': 2.6,
    'total_expenses': 2.6,
    
    # Balance Sheet Assets - Critical items
    'total_assets': 3.0,
    'total_non_current_assets': 2.7,
    'property_plant_equipment': 2.6,
    'total_current_assets': 2.7,
    'inventories': 2.5,
    'trade_receivables': 2.5,
    'cash_and_equivalents': 2.6,
    'cash_and_bank_balances': 2.6,
    
    # Balance Sheet Liabilities - Critical items
    'total_equity_and_liabilities': 3.0,
    'total_non_current_liabilities': 2.6,
    'total_current_liabilities': 2.6,
    'trade_payables': 2.5,
    'borrowings': 2.6,
    'long_term_borrowings': 2.6,
    'short_term_borrowings': 2.5,
    'total_liabilities': 2.8,
    
    # Balance Sheet Equity - Critical items
    'total_equity': 2.8,
    'share_capital': 2.6,
    'reserves_and_surplus': 2.6,
    'retained_earnings': 2.5,
    
    # Cash Flow - Critical items
    'net_cash_from_operating_activities': 2.8,
    'net_cash_from_investing_activities': 2.7,
    'net_cash_from_financing_activities': 2.7,
    'cash_and_cash_equivalents_at_end': 2.7,
    
    # Financial Ratios - Important
    'earnings_per_share_basic': 2.7,
    'earnings_per_share_diluted': 2.7,
    'book_value_per_share': 2.5,
    'dividend_per_share': 2.5,
}

# Additional keyword-specific boosts
KEYWORD_BOOST = {
    'total revenue': 1.8,
    'revenue from operations': 1.7,
    'profit for the year': 1.8,
    'profit before tax': 1.7,
    'total assets': 1.8,
    'total equity and liabilities': 1.8,
    'ebitda': 1.9,
    'earnings per share': 1.8,
    'net cash from operating activities': 1.7,
    'net income': 1.8,
    'gross profit': 1.7,
    'operating profit': 1.7,
}

# =============================================================================
# BUILD MAPS FROM UNIFIED DATABASE
# =============================================================================

def build_terminology_maps():
    """Build TERMINOLOGY_MAP and KEYWORD_TO_TERM from unified database."""
    global TERMINOLOGY_MAP, KEYWORD_TO_TERM
    
    # Build from terms list
    for term in ALL_TERMS:
        term_key = term.get('key', '')
        if not term_key:
            continue
        
        # Get unified keywords
        keywords = term.get('keywords_unified', [])
        if not keywords:
            # Fallback: combine individual standard keywords
            keywords = (
                term.get('keywords_indas', []) +
                term.get('keywords_gaap', []) +
                term.get('keywords_ifrs', [])
            )
            # Deduplicate
            seen = set()
            unique_keywords = []
            for kw in keywords:
                kw_lower = kw.lower().strip()
                if kw_lower and kw_lower not in seen:
                    seen.add(kw_lower)
                    unique_keywords.append(kw_lower)
            keywords = unique_keywords
        
        # Get boost value
        boost = BOOST_VALUES.get(term_key, 1.5)
        
        # Build metric IDs based on term type
        metric_ids = []
        if 'revenue' in term_key or 'sales' in term_key:
            metric_ids = ['calc_revenue_growth', 'calc_ps_ratio']
        elif 'profit' in term_key and 'gross' in term_key:
            metric_ids = ['calc_gross_margin', 'calc_gross_profit']
        elif 'operating' in term_key and 'profit' in term_key:
            metric_ids = ['calc_operating_margin', 'calc_ebit_margin']
        elif 'ebitda' in term_key:
            metric_ids = ['calc_ebitda', 'calc_ebitda_margin', 'calc_ev_to_ebitda']
        elif 'total_assets' in term_key:
            metric_ids = ['calc_roa', 'calc_asset_turnover']
        elif 'equity' in term_key and 'total' in term_key:
            metric_ids = ['calc_roe', 'calc_book_value']
        elif 'receivable' in term_key:
            metric_ids = ['calc_dso', 'calc_receivables_turnover']
        elif 'inventory' in term_key or 'inventories' in term_key:
            metric_ids = ['calc_dio', 'calc_inventory_turnover']
        elif 'payable' in term_key:
            metric_ids = ['calc_dpo', 'calc_payables_turnover']
        elif 'cash' in term_key and 'operating' in term_key:
            metric_ids = ['calc_operating_cash_flow', 'calc_fcf']
        elif 'eps' in term_key or 'earnings_per_share' in term_key:
            metric_ids = ['calc_eps', 'calc_pe_ratio']
        
        # Add to terminology map
        TERMINOLOGY_MAP[term_key] = {
            'id': term.get('id', term_key),
            'key': term_key,
            'label': term.get('label', term_key),
            'category': term.get('category', 'Financial Terms'),
            'description': term.get('description', ''),
            'keywords': keywords,
            'keywords_indas': term.get('keywords_indas', []),
            'keywords_gaap': term.get('keywords_gaap', []),
            'keywords_ifrs': term.get('keywords_ifrs', []),
            'keywords_unified': keywords,
            'related_standards': term.get('related_standards', {}),
            'aliases': term.get('aliases', []),
            'calculation': term.get('calculation', ''),
            'sign_convention': term.get('sign_convention', 'positive'),
            'data_type': term.get('data_type', 'currency'),
            'priority': term.get('priority', 1),
            'is_computed': term.get('is_computed', False),
            'components': term.get('components', []),
            'metric_ids': metric_ids,
            'boost': boost
        }
        
        # Build reverse keyword map (cross-sectional)
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            if keyword_lower:
                if keyword_lower not in KEYWORD_TO_TERM:
                    KEYWORD_TO_TERM[keyword_lower] = []
                
                # Check if already added
                if not any(t['term_key'] == term_key for t in KEYWORD_TO_TERM[keyword_lower]):
                    KEYWORD_TO_TERM[keyword_lower].append({
                        'term_key': term_key,
                        'term_id': term.get('id', ''),
                        'label': term.get('label', ''),
                        'category': term.get('category', ''),
                        'boost': boost,
                        'priority': term.get('priority', 1)
                    })
    
    # Also populate from keyword index if available
    keyword_index = INDEXES.get('by_keyword', {})
    for keyword, term_list in keyword_index.items():
        if keyword not in KEYWORD_TO_TERM:
            KEYWORD_TO_TERM[keyword] = term_list

# Build the maps
build_terminology_maps()

# =============================================================================
# CROSS-SECTIONAL MATCHING FUNCTIONS
# =============================================================================

def find_all_matching_terms(text: str, min_keyword_length: int = 3) -> List[Dict]:
    """
    Find ALL matching terms in text using cross-sectional keyword matching.
    Returns a list of all matches with their scores.
    
    This function searches through ALL unified keywords from ALL accounting standards.
    """
    matches = []
    text_lower = text.lower().strip()
    
    if not text_lower:
        return matches
    
    # Method 1: Direct keyword matching with word boundaries
    for keyword, term_list in KEYWORD_TO_TERM.items():
        if len(keyword) < min_keyword_length:
            continue
        
        # Use word-boundary matching
        escaped_kw = re.escape(keyword)
        pattern = r'(?:^|[\s\-\(\[\/\,;:.])' + escaped_kw + r'(?:[\s\-\)\]\/\,;:.]|$)'
        
        if re.search(pattern, text_lower):
            for term_info in term_list:
                term_key = term_info.get('term_key', '')
                if not term_key:
                    continue
                
                term_data = TERMINOLOGY_MAP.get(term_key, {})
                if not term_data:
                    continue
                
                boost = term_data.get('boost', 1.5)
                length_score = len(keyword)
                
                # Bonus for exact match
                exact_bonus = 15 if text_lower == keyword else 0
                
                # Bonus for starting match
                start_bonus = 8 if text_lower.startswith(keyword) else 0
                
                # Additional boost for specific keywords
                keyword_boost = KEYWORD_BOOST.get(keyword, 0)
                
                # Priority bonus
                priority_bonus = term_data.get('priority', 1) * 0.5
                
                score = (length_score * boost) + exact_bonus + start_bonus + keyword_boost + priority_bonus
                
                matches.append({
                    'term_key': term_key,
                    'term_id': term_data.get('id', term_key),
                    'term_label': term_data.get('label', term_key),
                    'matched_keyword': keyword,
                    'category': term_data.get('category', 'Unknown'),
                    'score': score,
                    'boost': boost,
                    'metric_ids': term_data.get('metric_ids', []),
                    'data_type': term_data.get('data_type', 'currency'),
                    'sign_convention': term_data.get('sign_convention', 'positive')
                })
    
    # Method 2: Tokenized phrase matching (for multi-word terms)
    text_words = text_lower.split()
    for window_size in [6, 5, 4, 3, 2]:
        if len(text_words) >= window_size:
            for i in range(len(text_words) - window_size + 1):
                phrase = ' '.join(text_words[i:i + window_size])
                
                if phrase in KEYWORD_TO_TERM:
                    for term_info in KEYWORD_TO_TERM[phrase]:
                        term_key = term_info.get('term_key', '')
                        term_data = TERMINOLOGY_MAP.get(term_key, {})
                        
                        if term_data:
                            boost = term_data.get('boost', 1.5)
                            score = len(phrase) * boost * 2.0  # Strong bonus for tokenized match
                            
                            matches.append({
                                'term_key': term_key,
                                'term_id': term_data.get('id', term_key),
                                'term_label': term_data.get('label', term_key),
                                'matched_keyword': phrase,
                                'category': term_data.get('category', 'Unknown'),
                                'score': score,
                                'boost': boost,
                                'metric_ids': term_data.get('metric_ids', []),
                                'data_type': term_data.get('data_type', 'currency'),
                                'sign_convention': term_data.get('sign_convention', 'positive')
                            })
    
    # Remove duplicates (same term_key)
    seen_terms = set()
    unique_matches = []
    for match in matches:
        if match['term_key'] not in seen_terms:
            seen_terms.add(match['term_key'])
            unique_matches.append(match)
    
    # Sort by score descending
    unique_matches.sort(key=lambda x: x['score'], reverse=True)
    
    return unique_matches


def find_best_matching_term(text: str, min_keyword_length: int = 3) -> Optional[Dict]:
    """
    Find the single best matching term for the given text.
    Returns the highest-scoring match or None.
    """
    all_matches = find_all_matching_terms(text, min_keyword_length)
    return all_matches[0] if all_matches else None


def get_terms_by_category(category: str) -> List[Dict]:
    """Get all terms belonging to a specific category."""
    category_index = INDEXES.get('by_category', {})
    term_refs = category_index.get(category, [])
    
    terms = []
    for ref in term_refs:
        term_key = ref.get('term_key', '')
        if term_key in TERMINOLOGY_MAP:
            terms.append(TERMINOLOGY_MAP[term_key])
    
    return terms


def get_terms_by_standard(standard: str, standard_code: str) -> List[Dict]:
    """
    Get all terms related to a specific accounting standard.
    
    Args:
        standard: 'indas', 'gaap', or 'ifrs'
        standard_code: e.g., 'IndAS 115', 'ASC 606', 'IFRS 15'
    """
    standards_index = INDEXES.get('by_standard', {})
    standard_index = standards_index.get(standard, {})
    term_keys = standard_index.get(standard_code, [])
    
    terms = []
    for term_key in term_keys:
        if term_key in TERMINOLOGY_MAP:
            terms.append(TERMINOLOGY_MAP[term_key])
    
    return terms


def search_terms_by_keyword(keyword: str) -> List[Dict]:
    """Search for terms that match a given keyword (partial matching supported)."""
    keyword_lower = keyword.lower().strip()
    matches = []
    
    for term_key, term_data in TERMINOLOGY_MAP.items():
        # Check in unified keywords
        for kw in term_data.get('keywords_unified', []):
            if keyword_lower in kw or kw in keyword_lower:
                matches.append(term_data)
                break
        
        # Check in label
        if keyword_lower in term_data.get('label', '').lower():
            if term_data not in matches:
                matches.append(term_data)
    
    return matches


def get_related_terms(term_key: str) -> List[Dict]:
    """Get terms related to the given term (same category or shared standards)."""
    if term_key not in TERMINOLOGY_MAP:
        return []
    
    term_data = TERMINOLOGY_MAP[term_key]
    category = term_data.get('category', '')
    standards = term_data.get('related_standards', {})
    
    related = []
    for other_key, other_data in TERMINOLOGY_MAP.items():
        if other_key == term_key:
            continue
        
        # Same category
        if other_data.get('category') == category:
            related.append(other_data)
            continue
        
        # Shared standards
        other_standards = other_data.get('related_standards', {})
        for std_type in ['indas', 'gaap', 'ifrs']:
            if std_type in standards and std_type in other_standards:
                if any(s in other_standards[std_type] for s in standards[std_type]):
                    if other_data not in related:
                        related.append(other_data)
    
    return related


# =============================================================================
# STATISTICS AND INFO
# =============================================================================

def get_database_stats() -> Dict[str, Any]:
    """Get comprehensive statistics about the unified database."""
    metadata = DATABASE.get('metadata', {})
    
    stats = {
        'total_terms': len(ALL_TERMS),
        'total_keywords': metadata.get('total_keywords', 0),
        'unique_keywords': metadata.get('unique_keywords', 0),
        'categories': metadata.get('categories', []),
        'terms_in_terminology_map': len(TERMINOLOGY_MAP),
        'keywords_in_index': len(KEYWORD_TO_TERM),
        'accounting_standards': metadata.get('accounting_standards', {})
    }
    
    return stats


def print_database_summary():
    """Print a summary of the unified database."""
    stats = get_database_stats()
    
    print("\n" + "="*60, file=sys.stderr)
    print("UNIFIED FINANCIAL TERMINOLOGY DATABASE", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"Total Terms:              {stats['total_terms']}", file=sys.stderr)
    print(f"Total Keywords:           {stats['total_keywords']}", file=sys.stderr)
    print(f"Unique Keywords:          {stats['unique_keywords']}", file=sys.stderr)
    print(f"Categories:               {len(stats['categories'])}", file=sys.stderr)
    print(f"Terms in Map:             {stats['terms_in_terminology_map']}", file=sys.stderr)
    print(f"Keywords Indexed:         {stats['keywords_in_index']}", file=sys.stderr)
    print("\nCategories:", file=sys.stderr)
    for cat in sorted(stats['categories']):
        print(f"  - {cat}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)

# Print summary on load
print_database_summary()

# =============================================================================
# BACKWARDS COMPATIBILITY
# =============================================================================

# =============================================================================
# BACKWARDS COMPATIBILITY FUNCTIONS (for rag_engine.py)
# =============================================================================

def get_metric_ids_for_term(term_key: str) -> List[str]:
    """Get metric IDs associated with a term (backwards compatibility)."""
    term_data = TERMINOLOGY_MAP.get(term_key, {})
    return term_data.get('metric_ids', [])


def get_term_for_keyword(keyword: str) -> Optional[str]:
    """Get term key for a given keyword (backwards compatibility)."""
    keyword_lower = keyword.lower().strip()
    if keyword_lower in KEYWORD_TO_TERM:
        term_list = KEYWORD_TO_TERM[keyword_lower]
        if term_list:
            return term_list[0].get('term_key')
    return None


def get_boost_for_keyword(keyword: str) -> float:
    """Get boost weight for a keyword (backwards compatibility)."""
    keyword_lower = keyword.lower().strip()
    return KEYWORD_BOOST.get(keyword_lower, 1.0)


def get_all_keywords() -> List[str]:
    """Get all keywords in the terminology database (backwards compatibility)."""
    return list(KEYWORD_TO_TERM.keys())


def get_standards_for_term(term_key: str) -> Dict[str, List[str]]:
    """Get accounting standards associated with a term (backwards compatibility)."""
    term_data = TERMINOLOGY_MAP.get(term_key, {})
    return term_data.get('related_standards', {})


def get_term_details(term_key: str) -> Optional[Dict]:
    """Get full details for a term."""
    return TERMINOLOGY_MAP.get(term_key)


__all__ = [
    'TERMINOLOGY_MAP',
    'KEYWORD_TO_TERM',
    'KEYWORD_BOOST',
    'ALL_TERMS',
    'DATABASE',
    'INDEXES',
    'find_all_matching_terms',
    'find_best_matching_term',
    'get_terms_by_category',
    'get_terms_by_standard',
    'search_terms_by_keyword',
    'get_related_terms',
    'get_database_stats',
    'print_database_summary',
    # Backwards compatibility functions
    'get_metric_ids_for_term',
    'get_term_for_keyword',
    'get_boost_for_keyword',
    'get_all_keywords',
    'get_standards_for_term',
    'get_term_details'
]
