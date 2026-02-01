import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# =============================================================================
# ABBREVIATIONS & SYNONYMS (Consolidated from abbreviations.py and more)
# =============================================================================

FINANCIAL_ABBREVIATIONS = {
    # General
    'acc': 'accounts',
    'a/c': 'accounts',
    
    # Assets & Equipment
    'ppe': 'property plant and equipment',
    'pp&e': 'property plant and equipment',
    'cwip': 'capital work in progress',
    'cip': 'construction in progress',
    'rou': 'right of use',
    'capex': 'capital expenditure',
    'opex': 'operating expenditure',
    
    # Financial Instruments
    'ecl': 'expected credit loss',
    'fvtpl': 'fair value through profit and loss',
    'fvoci': 'fair value through other comprehensive income',
    'oci': 'other comprehensive income',
    'htm': 'held to maturity',
    'afs': 'available for sale',
    
    # Earnings & Performance
    'ebitda': 'earnings before interest taxes depreciation and amortization',
    'ebit': 'earnings before interest and taxes',
    'ebt': 'earnings before tax',
    'eps': 'earnings per share',
    'bvps': 'book value per share',
    'nav': 'net asset value',
    'cogs': 'cost of goods sold',
    'sg&a': 'selling general and administrative expenses',
    
    # Statements & Reporting
    'bs': 'balance sheet',
    'pl': 'profit and loss',
    'pnl': 'profit and loss',
    'p&l': 'profit and loss',
    'cce': 'cash and cash equivalents',
    'cash & cash eq': 'cash and cash equivalents',
    'soce': 'statement of changes in equity',
    'sofp': 'statement of financial position',
    'fy': 'financial year',
    
    # Taxation
    'dtl': 'deferred tax liability',
    'dta': 'deferred tax asset',
    'mat': 'minimum alternate tax',
    'gst': 'goods and services tax',
}

# =============================================================================
# REGEX PATTERNS
# =============================================================================

# Note references: "Note 12", "(see note 5)", "Schedule A"
NOTE_PATTERN = re.compile(r'\bnote\s*(?:no\.?)?\s*\d+\b|schedule\s*[a-z]\d*|\(\s*see\s+note\s*\d+\s*\)', re.IGNORECASE)

# Dot leaders and excessive whitespace
LEADER_PATTERN = re.compile(r'\.{3,}')
WHITESPACE_PATTERN = re.compile(r'\s+')

# Sign indicators
SIGN_INDICATORS = {
    'negative': [
        re.compile(r'^less:?\s+', re.IGNORECASE),
        re.compile(r'^\(-\)\s+'),
        re.compile(r'^[-]\s*\(\s*'),
    ],
    'parenthetical': re.compile(r'\((\d{1,3}(?:,\d{3})*(?:\.\d+)?)\)')
}

# Date patterns (simplified for normalization)
DATE_PATTERN = re.compile(r'\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b')

# =============================================================================
# NORMALIZATION PIPELINE
# =============================================================================

class TextNormalizer:
    """ Centralized text normalization for financial terms. """
    
    def __init__(self):
        # Build expansion dict with word boundaries for efficiency
        self._abbr_patterns = {
            re.compile(rf'\b{re.escape(k)}\b', re.IGNORECASE): v 
            for k, v in FINANCIAL_ABBREVIATIONS.items()
        }

    def expand_abbreviations(self, text: str) -> str:
        """ Expand common financial abbreviations. """
        result = text
        for pattern, expansion in self._abbr_patterns.items():
            result = pattern.sub(expansion, result)
        return result

    def remove_noise(self, text: str) -> str:
        """ Remove note references, leaders, and normalize whitespace. """
        # Remove note references
        text = NOTE_PATTERN.sub('', text)
        
        # Remove dot leaders
        text = LEADER_PATTERN.sub(' ', text)
        
        # Normalize whitespace
        text = WHITESPACE_PATTERN.sub(' ', text)
        
        return text.strip()

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """ Convert special unicode characters to ASCII equivalents. """
        # Normalize to NFKD to separate combined characters
        text = unicodedata.normalize('NFKD', text)
        
        # Replace specific characters
        replacements = {
            '–': '-', '—': '-', '−': '-', # dashes
            '‘': "'", '’': "'", '“': '"', '”': '"', # quotes
            '…': '...', # ellipsis
            '\xa0': ' ', # non-breaking space
            '\u00a0': ' ',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text

    def normalize_dates(self, text: str) -> str:
        """ Standardize dates to YYYY-MM-DD format where possible. """
        def replace_date(match):
            d, m, y = match.groups()
            if len(y) == 2:
                y = "20" + y # Assumption for financial docs
            try:
                # Basic validation
                dt = datetime(int(y), int(m), int(d))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return match.group(0)
        
        return DATE_PATTERN.sub(replace_date, text)

    @staticmethod
    def normalize_separators(text: str) -> str:
        """ Standardize slashes, dashes, and other separators. """
        # non-current -> non current
        text = text.replace('-', ' ')
        # trade/other -> trade other
        text = text.replace('/', ' ')
        
        # Replace symbols with words
        text = text.replace('&', ' and ')
        
        # Remove remaining punctuation except alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return WHITESPACE_PATTERN.sub(' ', text).strip()

    def detect_sign(self, text: str) -> int:
        """ 
        Detect if a line indicator suggests a negative value.
        Returns: -1 for negative, 1 for positive.
        """
        text_lower = text.lower().strip()
        for pattern in SIGN_INDICATORS['negative']:
            if pattern.search(text_lower):
                return -1
        
        if SIGN_INDICATORS['parenthetical'].search(text):
            return -1
            
        return 1

    def normalize_label(self, label: str) -> str:
        """ Full label normalization pipeline for matching. """
        if not label:
            return ""
            
        # 1. Unicode Normalization
        text = self.normalize_unicode(label)
        
        # 2. Case Standardization
        text = text.lower()
        
        # 3. Noise Removal
        text = self.remove_noise(text)
        
        # 4. Abbreviation Expansion
        text = self.expand_abbreviations(text)
        
        # 5. Date Normalization
        text = self.normalize_dates(text)
        
        # 6. Separator Normalization
        text = self.normalize_separators(text)
        
        return text

    def clean_numerical_value(self, value_str: str) -> Tuple[float, int]:
        """ 
        Clean a numerical value string and detect sign. 
        Returns (abs_value, sign_multiplier).
        """
        # Handle parenthetical negatives: (1,234)
        match = SIGN_INDICATORS['parenthetical'].search(value_str)
        is_neg = False
        if match:
            is_neg = True
            clean_str = match.group(1).replace(',', '')
        else:
            # Handle standard negatives: -1,234
            is_neg = value_str.strip().startswith('-')
            clean_str = value_str.replace(',', '').replace('-', '').strip()
            
        try:
            val = float(clean_str)
            return val, -1 if is_neg else 1
        except ValueError:
            return 0.0, 1

# Export singleton instance
normalizer = TextNormalizer()
