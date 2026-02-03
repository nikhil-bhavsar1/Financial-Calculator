"""
Financial Term Matching System - Abbreviation Mappings
======================================================
Comprehensive abbreviation expansion dictionary for financial terms.
"""

from typing import Dict, List, Set

# Core financial abbreviations
FINANCIAL_ABBREVIATIONS: Dict[str, str] = {
    # General Accounting
    'acc': 'accounts',
    'acct': 'accounts',
    'a/c': 'account',
    'a/cs': 'accounts',
    
    # Assets & Equipment
    'ppe': 'property plant equipment',
    'pp&e': 'property plant equipment',
    'cwip': 'capital work in progress',
    'cip': 'construction in progress',
    'rou': 'right of use',
    'capex': 'capital expenditure',
    'opex': 'operating expenditure',
    
    # Financial Instruments
    'ecl': 'expected credit loss',
    'fvtpl': 'fair value through profit loss',
    'fvoci': 'fair value through other comprehensive income',
    'oci': 'other comprehensive income',
    'htm': 'held to maturity',
    'afs': 'available for sale',
    
    # Earnings & Performance
    'ebitda': 'earnings before interest tax depreciation amortization',
    'ebit': 'earnings before interest tax',
    'ebt': 'earnings before tax',
    'eps': 'earnings per share',
    'bvps': 'book value per share',
    'nav': 'net asset value',
    
    # Statements & Reporting
    'bs': 'balance sheet',
    'pl': 'profit loss',
    'pnl': 'profit and loss',
    'cfs': 'cash flow statement',
    'soce': 'statement of changes in equity',
    'sofp': 'statement of financial position',
    'socf': 'statement of cash flows',
    'ar': 'annual report',
    'qr': 'quarterly report',
    
    # Taxation
    'dtl': 'deferred tax liability',
    'dta': 'deferred tax asset',
    'mat': 'minimum alternate tax',
    'gst': 'goods and services tax',
    'cgst': 'central goods and services tax',
    'sgst': 'state goods and services tax',
    'igst': 'integrated goods and services tax',
    'tds': 'tax deducted at source',
    'tcs': 'tax collected at source',
    'vat': 'value added tax',
    
    # Equity & Capital
    'nci': 'non controlling interest',
    'kmp': 'key management personnel',
    'esop': 'employee stock option plan',
    'esps': 'employee stock purchase scheme',
    'sweat': 'sweat equity',
    'gdr': 'global depository receipt',
    'adr': 'american depository receipt',
    
    # Inventory & Valuation
    'nrv': 'net realisable value',
    'fifo': 'first in first out',
    'lifo': 'last in first out',
    'wip': 'work in progress',
    
    # Leases
    'lessee': 'tenant',
    'lessor': 'landlord',
    
    # Consolidation
    'jv': 'joint venture',
    'woe': 'wholly owned entity',
    
    # Other
    'fy': 'financial year',
    'yoy': 'year on year',
    'qoq': 'quarter on quarter',
    'mtd': 'month to date',
    'ytd': 'year to date',
    'qtd': 'quarter to date',
    'etc': 'et cetera',
    'ie': 'id est',
    'eg': 'exempli gratia',
    'viz': 'videlicet',
    'sr': 'senior',
    'mr': 'mister',
    'mrs': 'missus',
    'ms': 'miss',
    'dr': 'doctor',
    'cr': 'credit',
    'dr': 'debit',
}

# Reverse mapping for acronym generation
ACRONYM_PATTERNS: Dict[str, List[str]] = {
    'property plant equipment': ['ppe', 'pp&e'],
    'capital work in progress': ['cwip'],
    'construction in progress': ['cip'],
    'right of use': ['rou'],
    'expected credit loss': ['ecl'],
    'other comprehensive income': ['oci'],
    'earnings before interest tax depreciation amortization': ['ebitda'],
    'earnings per share': ['eps'],
    'fair value through profit or loss': ['fvtpl'],
    'fair value through other comprehensive income': ['fvoci'],
    'net realisable value': ['nrv'],
    'non controlling interest': ['nci'],
    'key management personnel': ['kmp'],
    'deferred tax liability': ['dtl'],
    'deferred tax asset': ['dta'],
    'minimum alternate tax': ['mat'],
    'work in progress': ['wip'],
    'profit and loss': ['pl', 'pnl'],
    'balance sheet': ['bs'],
    'cash flow statement': ['cfs'],
    'annual report': ['ar'],
    'quarterly report': ['qr'],
}

# Multi-word abbreviations that need special handling
MULTI_WORD_ABBREVIATIONS: Dict[str, str] = {
    'ind as': 'indian accounting standard',
    'indas': 'indian accounting standard',
    'ifrs': 'international financial reporting standard',
    'gaap': 'generally accepted accounting principles',
    'icai': 'institute of chartered accountants of india',
    'sec': 'securities and exchange commission',
    'sebi': 'securities and exchange board of india',
    'rbi': 'reserve bank of india',
    'irda': 'insurance regulatory and development authority',
    'pfrda': 'pension fund regulatory and development authority',
    'nse': 'national stock exchange',
    'bse': 'bombay stock exchange',
    'mcx': 'multi commodity exchange',
    'ncdex': 'national commodity and derivatives exchange',
    'cci': 'competition commission of india',
    'nfra': 'national financial reporting authority',
    'nfra': 'national financial reporting authority',
}

# Common OCR errors and their corrections
OCR_ERROR_PATTERNS: Dict[str, str] = {
    '0': 'o',  # Zero to letter O
    '1': 'l',  # One to letter L
    '5': 's',  # Five to letter S
    'rn': 'm',  # Common OCR error
    'nn': 'm',  # Common OCR error
    'cl': 'd',  # Common OCR error
}

# Sign convention indicators
SIGN_CONVENTION_INDICATORS: Dict[str, int] = {
    'less': -1,
    'less:': -1,
    '(-)': -1,
    '(cr)': -1,
    '(dr)': 1,
    'cr.': -1,
    'dr.': 1,
    'credit': -1,
    'debit': 1,
}

def expand_abbreviations(text: str) -> str:
    """
    Expand all known abbreviations in text.
    
    Args:
        text: Input text potentially containing abbreviations
        
    Returns:
        Text with abbreviations expanded
    """
    import re
    
    text_lower = text.lower()
    
    # First, check for multi-word abbreviations (like "ind as", "ifrs", etc.)
    # These need to be matched before word-by-word processing
    for abbr, expansion in MULTI_WORD_ABBREVIATIONS.items():
        # Match whole words only
        pattern = r'\b' + re.escape(abbr) + r'\b'
        text_lower = re.sub(pattern, expansion, text_lower)
    
    # Then process remaining single-word abbreviations
    words = text_lower.split()
    expanded = []
    
    for word in words:
        # Remove punctuation for lookup
        clean_word = re.sub(r'[^\w]', '', word)
        
        # Check in single-word abbreviation dictionary
        if clean_word in FINANCIAL_ABBREVIATIONS:
            expanded.append(FINANCIAL_ABBREVIATIONS[clean_word])
        else:
            expanded.append(word)
    
    return ' '.join(expanded)

def generate_acronyms(term: str) -> Set[str]:
    """
    Generate possible acronyms from a term.
    
    Args:
        term: Full term to generate acronyms from
        
    Returns:
        Set of possible acronym forms
    """
    import re
    
    acronyms = set()
    
    # Check if term has predefined acronyms
    normalized = re.sub(r'[^\w\s]', '', term.lower())
    if normalized in ACRONYM_PATTERNS:
        acronyms.update(ACRONYM_PATTERNS[normalized])
    
    # Generate standard acronym from first letters
    words = normalized.split()
    if len(words) > 1:
        standard_acronym = ''.join(word[0] for word in words if word)
        acronyms.add(standard_acronym)
        
        # Also add with & replaced
        if '&' in term or 'and' in normalized:
            alt_term = normalized.replace(' and ', ' ').replace('&', '')
            alt_words = alt_term.split()
            alt_acronym = ''.join(word[0] for word in alt_words if word)
            acronyms.add(alt_acronym)
    
    return acronyms

def get_all_abbreviations() -> Dict[str, str]:
    """
    Get combined dictionary of all abbreviations.
    
    Returns:
        Dictionary mapping all abbreviations to their expansions
    """
    all_abbr = {}
    all_abbr.update(FINANCIAL_ABBREVIATIONS)
    all_abbr.update(MULTI_WORD_ABBREVIATIONS)
    return all_abbr
