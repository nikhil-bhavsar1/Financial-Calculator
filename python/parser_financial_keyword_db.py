
import re
import logging
from typing import List, Set, Optional, Dict, Any

logger = logging.getLogger(__name__)

# =============================================================================
# Financial Keywords Database
# =============================================================================

class FinancialKeywords:
    """
    Comprehensive database of financial keywords for matching.
    Supports IndAS, IFRS, and US GAAP terminology.
    """
    
    # Core financial keywords organized by category
    KEYWORDS = {
        # Revenue & Sales
        'revenue': {
            'revenue', 'sales', 'turnover', 'income from operations', 'gross sales',
            'net sales', 'operating revenue', 'other operating income', 'service revenue',
            'fee income', 'commission income', 'rental income', 'royalty income',
            'revenue from contracts', 'sale of products', 'sale of services',
        },
        
        # Costs & Expenses
        'costs': {
            'cost of goods sold', 'cogs', 'cost of sales', 'cost of revenue',
            'cost of materials', 'cost of products', 'cost of services',
            'cost of materials consumed', 'purchase of stock-in-trade',
            'changes in inventories', 'raw materials consumed',
        },
        
        'operating_expenses': {
            'operating expenses', 'opex', 'employee benefit', 'employee expenses',
            'salaries', 'wages', 'staff costs', 'personnel expenses',
            'depreciation', 'amortization', 'amortisation', 'd&a',
            'interest expense', 'interest paid', 'finance costs', 'borrowing costs',
            'other expenses', 'administrative expenses', 'selling expenses',
            'general expenses', 'manufacturing expenses', 'distribution costs',
            'rent expense', 'utility expenses', 'insurance expense',
            'legal and professional', 'repairs and maintenance',
            'travelling and conveyance', 'communication expenses',
        },
        
        # Profits & Income
        'profit': {
            'gross profit', 'gross margin', 'operating profit', 'operating income',
            'ebit', 'ebitda', 'net income', 'net profit', 'profit after tax', 'pat',
            'profit before tax', 'pbt', 'profit for the year', 'profit for period',
            'net earnings', 'earnings', 'comprehensive income', 'other income',
            'profit from operations', 'profit before exceptional items',
            'profit attributable to owners', 'profit attributable to shareholders',
        },
        
        # Balance Sheet - Assets
        'non_current_assets': {
            'non-current assets', 'non current assets', 'fixed assets', 'tangible assets',
            'property plant equipment', 'property, plant and equipment', 'ppe',
            'capital work', 'capital work-in-progress', 'cwip',
            'intangible assets', 'goodwill', 'patents', 'trademarks', 'copyrights',
            'investment property', 'investments', 'long term investments',
            'right of use', 'right-of-use assets', 'rou assets', 'lease assets',
            'deferred tax assets', 'dta', 'other non-current assets',
            'biological assets', 'exploration assets',
        },
        
        'current_assets': {
            'current assets', 'total current assets',
            'inventories', 'inventory', 'stock', 'finished goods', 'raw materials',
            'work in progress', 'wip', 'stores and spares', 'packing materials',
            'trade receivables', 'receivables', 'debtors', 'accounts receivable',
            'sundry debtors', 'bills receivable',
            'cash and cash equivalents', 'cash and bank', 'bank balances',
            'cash at bank', 'cash on hand', 'cash', 'bank deposits',
            'other financial assets', 'derivative assets', 'financial instruments',
            'loans and advances', 'other current assets', 'prepaid expenses',
            'advances to suppliers', 'contract assets', 'unbilled revenue',
        },
        
        # Balance Sheet - Liabilities
        'non_current_liabilities': {
            'non-current liabilities', 'non current liabilities', 'long-term liabilities',
            'long term borrowings', 'term loans', 'debentures', 'bonds',
            'deferred tax liabilities', 'dtl', 'provisions', 'long-term provisions',
            'employee benefit obligations', 'pension liabilities', 'gratuity',
            'lease liabilities', 'other non-current liabilities',
        },
        
        'current_liabilities': {
            'current liabilities', 'total current liabilities',
            'trade payables', 'payables', 'creditors', 'accounts payable',
            'sundry creditors', 'bills payable',
            'short term borrowings', 'working capital loans', 'cash credit',
            'overdraft', 'commercial paper', 'current maturities',
            'other financial liabilities', 'derivative liabilities',
            'provisions', 'short-term provisions', 'current tax liabilities',
            'other current liabilities', 'contract liabilities', 'advance from customers',
            'deferred revenue', 'unearned revenue', 'statutory dues',
        },
        
        # Equity
        'equity': {
            'equity', 'shareholders equity', 'stockholders equity', 'net worth',
            'share capital', 'equity share capital', 'paid up capital',
            'preference share capital', 'authorized capital', 'issued capital',
            'reserves', 'reserves and surplus', 'retained earnings',
            'other reserves', 'capital reserve', 'general reserve',
            'securities premium', 'share premium', 'other equity',
            'minority interest', 'non-controlling interest', 'nci',
            'accumulated profits', 'accumulated losses', 'surplus',
            'other comprehensive income', 'oci', 'revaluation reserve',
            'share options outstanding', 'esop reserve',
        },
        
        # Cash Flow
        'cash_flow': {
            'cash flows', 'cash flow from operating', 'operating activities',
            'cash from operations', 'operating cash flow',
            'cash flow from investing', 'investing activities',
            'cash flow from financing', 'financing activities',
            'net cash from', 'net cash used', 'cash generated',
            'capital expenditure', 'capex', 'purchase of fixed assets',
            'purchase of ppe', 'dividends paid', 'dividend paid',
            'interest received', 'interest paid', 'taxes paid',
            'free cash flow', 'fcf', 'net increase in cash', 'net decrease',
            'opening cash', 'closing cash', 'cash at beginning', 'cash at end',
            'proceeds from borrowings', 'repayment of borrowings',
            'proceeds from issue of shares', 'buyback of shares',
        },
        
        # Per Share Data
        'per_share': {
            'earnings per share', 'eps', 'basic eps', 'diluted eps',
            'dividend per share', 'dps', 'book value per share',
            'face value', 'par value', 'nominal value',
        },
        
        # Totals and Structural
        'structural': {
            'total', 'sub-total', 'subtotal', 'net', 'gross',
            'total assets', 'total liabilities', 'total equity',
            'total equity and liabilities', 'total income', 'total expenses',
            'total non-current assets', 'total current assets',
            'total non-current liabilities', 'total current liabilities',
            'grand total', 'aggregate',
        },
    }
    
    # Important line items (used for highlighting)
    IMPORTANT_ITEMS = {
        'total assets',
        'total equity and liabilities',
        'total equity',
        'total liabilities',
        'net worth',
        'revenue from operations',
        'total income',
        'total expenses',
        'profit before tax',
        'profit for the year',
        'profit for the period',
        'profit after tax',
        'net profit',
        'earnings per share',
        'basic eps',
        'diluted eps',
        'net cash from operating activities',
        'net cash used in operating activities',
        'net cash from investing activities',
        'net cash used in investing activities',
        'net cash from financing activities',
        'net cash used in financing activities',
        'net increase in cash',
        'net decrease in cash',
        'cash and cash equivalents at the end',
        'ebitda',
        'operating profit',
    }
    
    # Skip patterns - lines matching these should not be extracted
    SKIP_PATTERNS = [
        r'^page\s*[\d\-]+',
        r'^\d{1,3}$',
        r'^notes?\s*(?:to|on|forming)\s*(?:the\s*)?(?:financial|standalone|consolidated)',
        r'^significant\s+accounting\s+policies',
        r'^the\s+(?:accompanying\s+)?notes\s+(?:are|form)',
        r'^see\s+(?:accompanying\s+)?notes',
        r'^in\s+(?:terms\s+of\s+)?our\s+(?:report|attached)',
        r'^for\s+and\s+on\s+behalf\s+of',
        r'^(?:for\s+)?(?:chartered\s+)?accountants?',
        r'^auditors?\s*(?:report)?',
        r'^(?:managing\s+)?directors?',
        r'^(?:chief\s+)?(?:executive|financial)\s+officer',
        r'^company\s+secretary',
        r'^(?:partner|proprietor)',
        r'^membership\s+no',
        r'^(?:firm\s+)?registration',
        r'^din\s*[:\-]',
        r'^(?:place|date)\s*[:\-]',
        r'^sd/[-–]',
        r'^\([a-z]\)$',
        r'^annual\s+report',
        r'^\d{4}[-–]\d{2,4}$',
        r'^(?:amount\s+)?(?:₹|rs\.?|inr)\s*(?:in\s+)?(?:crore|lakh|million|thousand)',
        r'^particulars?\s*$',
        r'^note\s*(?:no\.?)?\s*$',
        r'^as\s+(?:at|on)\s+',
        r'^(?:for\s+the\s+)?(?:year|period)\s+ended',
        r'^(?:standalone|consolidated)\s+(?:statement|balance)',
        r'^this\s+is\s+the',
        r'^referred\s+to\s+in',
        r'^\s*[-–—]+\s*$',
        r'^\s*[_=]+\s*$',
    ]
    
    # Compiled patterns (for performance)
    _all_keywords: Optional[Set[str]] = None
    _compiled_skip_patterns: Optional[List] = None
    
    @classmethod
    def get_all_keywords(cls) -> Set[str]:
        """Get flattened set of all keywords."""
        if cls._all_keywords is None:
            cls._all_keywords = set()
            for category_keywords in cls.KEYWORDS.values():
                cls._all_keywords.update(category_keywords)
        return cls._all_keywords
    
    @classmethod
    def get_compiled_skip_patterns(cls) -> List:
        """Get compiled skip patterns for performance."""
        if cls._compiled_skip_patterns is None:
            cls._compiled_skip_patterns = [
                re.compile(p, re.IGNORECASE) for p in cls.SKIP_PATTERNS
            ]
        return cls._compiled_skip_patterns
    
    @classmethod
    def matches_keyword(cls, text: str) -> bool:
        """Check if text matches any financial keyword."""
        text_lower = text.lower()
        
        # Check direct keyword matches
        for keyword in cls.get_all_keywords():
            if keyword in text_lower:
                return True
        
        # Check structural patterns
        structural_patterns = [
            r'\b(?:total|net|gross)\s+\w+',
            r'\b(?:current|non-current)\s+\w+',
            r'\b\w+\s+(?:expense|expenses|income|assets?|liabilities?)\b',
            r'\b(?:provision|reserve)s?\s+for\b',
            r'\b(?:less|add|adjustment)s?:?\s*\w+',
            r'\b\w+\s+(?:receivable|payable)s?\b',
            r'\b(?:opening|closing)\s+\w+',
        ]
        
        for pattern in structural_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    @classmethod
    def should_skip_line(cls, text: str) -> bool:
        """Check if line should be skipped based on skip patterns."""
        text_stripped = text.strip().lower()
        
        # Quick checks first
        if len(text_stripped) < 5:
            return True
        
        # Pure numbers
        if re.match(r'^[\d,.\s\(\)\-]+$', text_stripped):
            return True
        
        # Check compiled patterns
        for pattern in cls.get_compiled_skip_patterns():
            if pattern.search(text_stripped):
                return True
        
        return False
    
    @classmethod
    def is_important_item(cls, label: str) -> bool:
        """Check if label represents an important line item."""
        label_lower = label.lower()
        
        for important in cls.IMPORTANT_ITEMS:
            if important in label_lower:
                return True
        
        return False
    
    @classmethod
    def get_category(cls, text: str) -> Optional[str]:
        """Determine the category of a financial term."""
        text_lower = text.lower()
        
        for category, keywords in cls.KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return None
    
    @classmethod
    def add_custom_keywords(cls, keywords: List[str]) -> int:
        """Add custom keywords to the database."""
        count = 0
        all_kw = cls.get_all_keywords()
        
        for kw in keywords:
            if kw and isinstance(kw, str):
                kw_lower = kw.lower().strip()
                if kw_lower and kw_lower not in all_kw:
                    all_kw.add(kw_lower)
                    count += 1
        
        return count
    
    @classmethod
    def update_from_mappings(cls, mappings: List[Dict[str, Any]]) -> int:
        """
        Update keywords from term mappings (e.g., from frontend).
        
        Args:
            mappings: List of term mapping dicts with keywords_indas, keywords_gaap, etc.
            
        Returns:
            Number of keywords added
        """
        count = 0
        
        for item in mappings:
            # Add keywords from all standards
            for field in ['keywords_indas', 'keywords_gaap', 'keywords_ifrs']:
                keyword_list = item.get(field, [])
                if isinstance(keyword_list, list):
                    count += cls.add_custom_keywords(keyword_list)
            
            # Also add the label itself
            label = item.get('label')
            if label:
                count += cls.add_custom_keywords([label])
        
        logger.info(f"Updated keywords: added {count} new terms")
        return count
