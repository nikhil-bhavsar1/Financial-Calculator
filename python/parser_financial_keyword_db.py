
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
    Updated with comprehensive terms from all three accounting standards.
    """
    
    # Core financial keywords organized by category
    KEYWORDS = {
        # =====================================================================
        # REVENUE & INCOME
        # =====================================================================
        'revenue': {
            # General
            'revenue', 'sales', 'turnover', 'income from operations', 'gross sales',
            'net sales', 'operating revenue', 'total net sales', 'service revenue',
            'fee income', 'commission income', 'rental income', 'royalty income',
            'revenue from contracts', 'sale of products', 'sale of services',
            'revenue from operations', 'other operating revenues',
            # Ind AS Specific
            'export incentives', 'manufacturing scrap sales',
            'interest revenue calculated using the effective interest method',
            'interest revenue',
            # US GAAP Specific
            'revenue from sale of goods', 'revenue from rendering of services',
            'revenue from long-term contracts', 'licensing revenue',
            # IFRS Specific
            'insurance revenue', 'interest income',
        },
        
        # =====================================================================
        # COSTS & EXPENSES
        # =====================================================================
        'costs': {
            'cost of goods sold', 'cogs', 'cost of sales', 'cost of revenue',
            'cost of materials', 'cost of products', 'cost of services',
            'cost of materials consumed', 'purchase of stock-in-trade',
            'purchases of stock-in-trade', 'changes in inventories',
            'raw materials consumed', 'changes in inventories of finished goods',
            'work-in-progress and stock-in-trade',
            # US GAAP
            'direct material costs', 'direct labor costs', 'manufacturing overhead',
            'shipping and handling costs',
        },
        
        'operating_expenses': {
            'operating expenses', 'opex', 'employee benefit expenses', 'employee expenses',
            'salaries and wages', 'salaries', 'wages', 'staff costs', 'personnel expenses',
            'depreciation', 'amortization', 'amortisation', 'd&a',
            'depreciation and amortisation expense', 'depreciation on ppe',
            'depreciation on investment property', 'amortisation of intangible assets',
            'other expenses', 'administrative expenses', 'selling expenses',
            'general and administrative expenses', 'general expenses',
            'manufacturing expenses', 'distribution costs',
            'rent', 'rent expense', 'utility expenses', 'utilities',
            'insurance', 'insurance expense',
            'legal and professional', 'professional fees', 'repairs and maintenance',
            'repairs - buildings', 'repairs - machinery',
            'travelling and conveyance', 'communication expenses',
            'power and fuel', 'consumption of stores and spare parts',
            'carriage inwards', 'carriage outwards', 'commission',
            'other selling and distribution expenses',
            # Ind AS Specific
            'contribution to provident and other funds', 'share-based payments to employees',
            'esop', 'espp', 'staff welfare expenses', 'gratuity', 'leave encashment',
            'corporate social responsibility expenditure', 'csr expenditure',
            'research and development expenses', 'r&d expenses',
            'bad debts and advances written off', 'provision for doubtful debts',
            'provision for obsolete inventory', 'liquidated damages', 'penalties',
            # US GAAP
            'sales commissions', 'advertising costs', 'marketing costs',
            'administrative salaries', 'office rent', 'office supplies',
            'research and development expenses',
        },
        
        'finance_costs': {
            'interest expense', 'interest paid', 'finance costs', 'borrowing costs',
            'finance cost', 'other borrowing costs',
            # Ind AS Specific
            'dividend on redeemable preference shares',
            'exchange differences regarded as adjustment to borrowing cost',
            'commitment charges', 'loan processing charges', 'guarantee charges',
            'amortisation of ancillary borrowing costs',
            # IFRS Specific
            'interest expense on borrowings and lease liabilities',
            'foreign exchange gains/losses on financing',
        },
        
        # =====================================================================
        # PROFITS & INCOME LEVELS
        # =====================================================================
        'profit': {
            'gross profit', 'gross margin', 'operating profit', 'operating income',
            'ebit', 'ebitda', 'net income', 'net profit', 'profit after tax', 'pat',
            'profit before tax', 'pbt', 'profit for the year', 'profit for period',
            'net earnings', 'earnings', 'comprehensive income', 'other income',
            'profit from operations', 'profit before exceptional items',
            'profit attributable to owners', 'profit attributable to shareholders',
            'profit or loss', 'net profit for the period',
            # IFRS 18 Subtotals
            'operating profit or loss', 'profit or loss before financing and income taxes',
            # Other
            'income/loss from operations of discontinued component',
            'gain/loss on disposal of discontinued component',
        },
        
        'other_income': {
            'other income', 'interest income', 'dividend income',
            'other non-operating income', 'net gains on fair value changes',
            # Gains/Losses
            'gains on disposal of assets', 'losses on disposal of assets',
            'gain on sale of investments', 'loss on sale of investments',
            'gain on sale of assets', 'loss on sale of assets',
            'foreign currency gains', 'foreign currency losses',
            'foreign exchange loss', 'foreign exchange gain',
            'derivative gains', 'derivative losses',
            'fair value gains', 'fair value losses',
        },
        
        # =====================================================================
        # BALANCE SHEET - NON-CURRENT ASSETS
        # =====================================================================
        'non_current_assets': {
            'non-current assets', 'non current assets', 'fixed assets', 'tangible assets',
            'total non-current assets',
            # PPE
            'property plant equipment', 'property, plant and equipment', 'ppe',
            'land and land improvements', 'buildings and building improvements',
            'machinery and equipment', 'furniture and fixtures', 'vehicles',
            'construction in progress', 'accumulated depreciation',
            # Capital WIP
            'capital work', 'capital work-in-progress', 'cwip',
            # Intangibles
            'intangible assets', 'intangible assets under development',
            'goodwill', 'patents', 'trademarks', 'copyrights',
            'intellectual property', 'computer software',
            'trade and distribution assets', 'contracts and rights',
            'franchise rights', 'customer lists', 'licenses and permits',
            'accumulated amortisation',
            # Investment Property
            'investment property',
            # Financial Assets (Non-current)
            'investments', 'long term investments', 'non-current investments',
            'equity instruments at fvtpl', 'equity instruments at fvoci',
            'debt instruments at amortised cost', 'debt instruments at fvoci',
            'investments accounted for using the equity method',
            'investments in associates', 'investments in joint ventures',
            # Right of Use
            'right of use', 'right-of-use assets', 'rou assets', 'lease assets',
            'operating lease assets', 'finance lease assets',
            # Deferred Tax
            'deferred tax assets', 'dta',
            # Biological Assets
            'biological assets',
            # Other
            'other non-current assets', 'exploration assets',
            'crypto assets', 'acquisition in progress',
        },
        
        # =====================================================================
        # BALANCE SHEET - CURRENT ASSETS
        # =====================================================================
        'current_assets': {
            'current assets', 'total current assets',
            # Inventories
            'inventories', 'inventory', 'stock', 'finished goods', 'raw materials',
            'raw material, parts and supplies', 'work in progress', 'wip',
            'stock-in-trade', 'stores and spares', 'loose tools',
            'packing materials', 'merchandise', 'manufacturing supplies', 'supplies',
            # Trade Receivables
            'trade receivables', 'receivables', 'debtors', 'accounts receivable',
            'sundry debtors', 'bills receivable', 'notes receivable',
            'receivables from related parties', 'interest receivable', 'dividends receivable',
            'outstanding for a period exceeding six months',
            # Other Financial Assets
            'other financial assets', 'derivative assets', 'financial instruments',
            'interest accrued', 'loans to related parties',
            'short-term investments', 'other short-term investments',
            # Cash
            'cash and cash equivalents', 'cash and bank', 'bank balances',
            'bank deposits', 'cash at bank', 'cash on hand', 'cash',
            'cheques, drafts on hand', 'earmarked balances with banks',
            'restricted cash',
            # Other
            'other current assets', 'prepaid expenses', 'advances to suppliers',
            'contract assets', 'unbilled revenue', 'loans and advances',
            # Assets Held for Sale
            'assets held for sale', 'assets included in disposal groups classified as held for sale',
            'assets of disposal groups classified as held for sale',
        },
        
        # =====================================================================
        # BALANCE SHEET - NON-CURRENT LIABILITIES
        # =====================================================================
        'non_current_liabilities': {
            'non-current liabilities', 'non current liabilities', 'long-term liabilities',
            'total non-current liabilities',
            # Borrowings
            'long term borrowings', 'borrowings', 'term loans', 'debentures', 'bonds',
            'notes payable', 'bonds payable', 'loans payable', 'other long-term borrowings',
            # Lease Liabilities
            'lease liabilities', 'long-term lease obligations',
            # Provisions
            'provisions', 'long-term provisions', 'provision for employee benefits',
            'provision for warranty', 'provision for decommissioning', 'other provisions',
            'asset retirement obligations',
            # Employee Benefits
            'employee benefit obligations', 'pension liabilities', 'gratuity',
            'pension and other post-retirement benefit obligations',
            # Deferred Tax
            'deferred tax liabilities', 'dtl', 'deferred tax liabilities (net)',
            # Other
            'other non-current liabilities', 'other financial liabilities',
            'derivative liabilities', 'deferred revenue (long-term)', 'contract liabilities',
            'liabilities of disposal groups classified as held for sale',
        },
        
        # =====================================================================
        # BALANCE SHEET - CURRENT LIABILITIES
        # =====================================================================
        'current_liabilities': {
            'current liabilities', 'total current liabilities',
            # Trade Payables
            'trade payables', 'payables', 'creditors', 'accounts payable', 'accounts payable (trade)',
            'sundry creditors', 'bills payable',
            'total outstanding dues of micro enterprises and small enterprises',
            'total outstanding dues of creditors other than micro enterprises and small enterprises',
            # Borrowings
            'short term borrowings', 'short-term borrowings', 'working capital loans',
            'cash credit', 'overdraft', 'bank overdraft and cash credit',
            'commercial paper', 'loans repayable on demand',
            'current maturities', 'current portion of long-term debt',
            'current maturity of long-term debt',
            # Lease Liabilities
            'current lease liabilities', 'lease liabilities (current portion)',
            # Other Financial Liabilities
            'other financial liabilities', 'derivative liabilities',
            # Other Current Liabilities
            'other current liabilities', 'accrued expenses',
            'salaries and wages payable', 'payroll taxes payable', 'sales taxes payable',
            'interest payable', 'rent payable', 'utilities payable', 'insurance payable',
            'interest accrued but not due on borrowings', 'interest accrued and due on borrowings',
            'unpaid dividends', 'unpaid matured deposits', 'dividends payable',
            'statutory dues', 'gst', 'tds',
            'advance from customers', 'customer deposits',
            'contract liabilities', 'refund liabilities',
            'unearned revenue', 'deferred revenue',
            # Provisions
            'current tax liabilities', 'current tax liabilities (net)',
            'provisions', 'short-term provisions',
            'provision for employee benefits', 'provision for warranty (short-term)',
        },
        
        # =====================================================================
        # EQUITY / SHAREHOLDERS' EQUITY
        # =====================================================================
        'equity': {
            'equity', 'shareholders equity', 'stockholders equity', 'net worth',
            'total equity', 'total equity and liabilities',
            # Share Capital
            'share capital', 'equity share capital', 'paid up capital',
            'preference share capital', 'authorized capital', 'authorised capital',
            'issued capital', 'subscribed and fully paid', 'subscribed but not fully paid',
            'shares held by subsidiaries', 'treasury shares', 'common stock',
            'preferred stock', 'common stock in treasury', 'preferred stock in treasury',
            # Reserves
            'reserves', 'reserves and surplus', 'retained earnings',
            'other reserves', 'capital reserve', 'general reserve',
            'securities premium', 'securities premium reserve', 'share premium',
            'other equity', 'capital redemption reserve', 'debenture redemption reserve',
            'share application money pending allotment',
            'equity component of compound financial instruments',
            'revaluation surplus', 'money received against share warrants',
            # US GAAP Specific
            'additional paid-in capital', 'apic',
            'paid-in capital in excess of par - common', 'paid-in capital in excess of par - preferred',
            'paid-in capital from treasury stock', 'paid-in capital from stock warrants',
            'appropriated retained earnings', 'unappropriated retained earnings',
            'accumulated deficit', 'retained earnings in suspense',
            # Other
            'minority interest', 'non-controlling interest', 'nci',
            'non-controlling interests',
            'accumulated profits', 'accumulated losses', 'surplus',
            'share options outstanding', 'esop reserve',
            'stock-based compensation',
            # Partners/LLC
            'partners capital', 'members equity', 'non-share equity',
        },
        
        # =====================================================================
        # OTHER COMPREHENSIVE INCOME (OCI)
        # =====================================================================
        'oci': {
            'other comprehensive income', 'oci',
            'accumulated other comprehensive income', 'aoci',
            'total comprehensive income', 'comprehensive income',
            # Items NOT reclassified to P&L
            'changes in revaluation surplus',
            'remeasurements of defined benefit plans',
            'equity instruments at fair value through other comprehensive income',
            'equity instruments at fvoci',
            # Items WILL BE reclassified to P&L
            'exchange differences on translating financial statements of foreign operations',
            'foreign currency translation adjustments',
            'effective portion of cash flow hedges', 'effective portion of gains/losses on hedging instruments',
            'cash flow hedges',
            'debt instruments at fair value through other comprehensive income',
            'debt instruments at fvoci',
            # US GAAP
            'unrealized gains/losses on available-for-sale debt securities',
            'unrealized gains/losses on available-for-sale equity securities',
            'gains/losses on cash flow hedges',
            'actuarial gains/losses on pension plans',
            'changes in fair value attributable to instrument-specific credit risk',
            # Share of OCI
            'share of oci of associates and joint ventures',
        },
        
        # =====================================================================
        # CASH FLOW STATEMENT
        # =====================================================================
        'cash_flow_operating': {
            'cash flows', 'cash flow from operating', 'operating activities',
            'cash from operations', 'operating cash flow',
            'net cash from operating activities', 'net cash used in operating activities',
            'cash generated from operations',
            # Receipts
            'cash receipts from sale of goods and rendering of services',
            'cash receipts from royalties, fees, commissions and other revenue',
            'cash collected from customers', 'cash received from customers',
            # Payments
            'cash payments to suppliers for goods and services',
            'cash payments to and on behalf of employees', 'cash paid to employees',
            'cash paid to suppliers', 'cash paid for operating expenses',
            # Insurance
            'cash receipts and payments from insurance contracts',
            'insurance premiums and claims',
            # Taxes
            'cash payments or refunds of income taxes', 'income taxes paid', 'taxes paid',
            # Interest
            'interest paid', 'interest received',
            # Dividends
            'dividends received',
        },
        
        'cash_flow_investing': {
            'cash flow from investing', 'investing activities',
            'net cash from investing activities', 'net cash used in investing activities',
            # Acquisitions
            'cash payments to acquire property, plant and equipment',
            'purchase of ppe', 'purchase of fixed assets',
            'capital expenditure', 'capex',
            'cash payments to acquire intangibles', 'purchase of intangible assets',
            'acquisition of investment property',
            'acquisition of subsidiaries', 'acquisitions, net of cash acquired',
            # Disposals
            'cash receipts from sale of property, plant and equipment',
            'proceeds from sale of ppe', 'proceeds from disposal of assets',
            'proceeds from sale of investments', 'disposal of businesses',
            'disposals of subsidiaries',
            # Investments
            'cash payments to acquire equity or debt instruments',
            'purchase of investments',
            'cash receipts from sale of equity or debt instruments',
            # Loans
            'cash advances and loans made to other parties', 'loans made',
            'loans made to others', 'advances to related parties',
            'cash receipts from repayment of advances and loans', 'collection of loans',
            # Derivatives
            'cash payments for futures contracts', 'cash payments for forward contracts',
            'cash payments for option contracts', 'cash payments for swap contracts',
            'cash receipts from futures contracts', 'cash receipts from forward contracts',
        },
        
        'cash_flow_financing': {
            'cash flow from financing', 'financing activities',
            'net cash from financing activities', 'net cash used in financing activities',
            # Share Issuance
            'cash proceeds from issuing shares', 'proceeds from issue of shares',
            'proceeds from issue of share capital', 'proceeds from issuance of common stock',
            'proceeds from issuance of preferred stock', 'share issue expenses',
            # Buyback
            'cash payments to owners to acquire or redeem shares', 'buyback of shares',
            'repurchases of treasury stock',
            # Borrowings
            'cash proceeds from issuing debentures', 'proceeds from debt issuance',
            'proceeds from borrowings', 'proceeds from long-term borrowings',
            'cash repayments of amounts borrowed', 'repayment of borrowings',
            'repayments of debt', 'repayment of long-term borrowings',
            # Lease
            'cash payments by a lessee for reduction of outstanding liability relating to a lease',
            'payment of lease liabilities', 'payments of lease obligations',
            # Dividends
            'dividends paid', 'dividend paid', 'payments of dividends',
            # Other
            'debt issuance costs', 'redemption of preference shares',
        },
        
        'cash_flow_summary': {
            'net cash', 'net increase in cash', 'net decrease in cash',
            'opening cash', 'closing cash', 'cash at beginning', 'cash at end',
            'cash and cash equivalents at the beginning',
            'cash and cash equivalents at the end',
            'free cash flow', 'fcf',
        },
        
        # =====================================================================
        # TAX
        # =====================================================================
        'tax': {
            'tax expense', 'income tax expense', 'income taxes',
            'current tax', 'current tax expense', 'current income tax',
            'deferred tax', 'deferred tax expense', 'deferred tax benefit',
            'excess/short provision of earlier years',
            'tax expense on discontinued operations',
            'income tax relating to items that will not be reclassified',
            'income tax relating to items that will be reclassified',
            # US GAAP
            'rate reconciliation',
        },
        
        # =====================================================================
        # DISCONTINUED OPERATIONS
        # =====================================================================
        'discontinued': {
            'profit from discontinued operations', 'loss from discontinued operations',
            'discontinued operations', 'income from discontinued operations',
            'gain from disposal of assets attributable to discontinued operations',
            'loss from disposal of assets attributable to discontinued operations',
            'gain/loss from disposal of discontinued component',
        },
        
        # =====================================================================
        # SHARE OF ASSOCIATES/JVs
        # =====================================================================
        'associates_jv': {
            'share of profit of associates', 'share of loss of associates',
            'share of profit of joint ventures', 'share of loss of joint ventures',
            'share of profit/(loss) of associates and joint ventures',
            'investments accounted for using the equity method',
            'equity method investments',
            'integral associates and joint ventures',
            'non-integral associates and joint ventures',
        },
        
        # =====================================================================
        # PER SHARE DATA
        # =====================================================================
        'per_share': {
            'earnings per share', 'eps', 'basic eps', 'diluted eps',
            'basic earnings per share', 'diluted earnings per share',
            'dividend per share', 'dps', 'book value per share',
            'face value', 'par value', 'nominal value',
            # Detailed
            'basic eps (continuing operations)', 'diluted eps (continuing operations)',
            'basic eps (discontinued operations)', 'diluted eps (discontinued operations)',
            'eps from continuing operations', 'eps from discontinued operations',
        },
        
        # =====================================================================
        # IMPAIRMENT & EXCEPTIONAL ITEMS
        # =====================================================================
        'impairment_exceptional': {
            'impairment losses', 'impairment loss', 'expected credit losses',
            'impairment losses on investments', 'asset write-downs',
            'reversal of impairment', 'impairment losses (including reversals)',
            'exceptional items', 'restructuring charges',
            'gains and losses arising from derecognition of financial assets',
        },
        
        # =====================================================================
        # IFRS 18 SPECIFIC CATEGORIES
        # =====================================================================
        'ifrs18_operating': {
            # Operating Category
            'operating category', 'operating profit or loss',
        },
        
        'ifrs18_investing': {
            # Investing Category
            'investing category',
            'income from investment properties',
            'gains/losses on derecognition of financial assets',
        },
        
        'ifrs18_financing': {
            # Financing Category
            'financing category',
            'gains/losses from changes in interest rates',
            'income/expenses from other financing activities',
        },
        
        # =====================================================================
        # INSURANCE (IFRS 17)
        # =====================================================================
        'insurance': {
            'insurance service expenses', 'insurance revenue',
            'income/expenses from reinsurance contracts held',
            'insurance finance income', 'insurance finance expenses',
            'finance income/expenses from reinsurance contracts held',
        },
        
        # =====================================================================
        # SEGMENT REPORTING
        # =====================================================================
        'segment': {
            'segment reporting', 'operating segments',
            'reportable segments', 'segment revenue', 'segment profit',
            'segment assets', 'segment liabilities',
        },
        
        # =====================================================================
        # DISCLOSURES & NOTES
        # =====================================================================
        'disclosures': {
            'significant accounting policies', 'estimates and judgements',
            'fair value measurement', 'fair value measurements',
            'level 1', 'level 2', 'level 3',
            'financial instruments by category',
            'measured at amortised cost', 'measured at fair value through profit or loss',
            'measured at fair value through oci', 'fvtpl', 'fvoci',
            'related party transactions', 'related party disclosures',
            'contingent liabilities', 'contingent assets', 'commitments',
            'events after reporting period', 'subsequent events',
            'operating leases', 'lease liabilities',
            'derivative instruments and hedging activities',
            'concentration risks', 'credit risk exposures', 'liquidity risk',
        },
        
        # =====================================================================
        # CHANGES IN EQUITY
        # =====================================================================
        'changes_in_equity': {
            'statement of changes in equity',
            'balance at beginning of period', 'balance at end of period',
            'changes in accounting policy', 'prior period errors',
            'restated balance', 'total comprehensive income for the period',
            'dividends declared', 'dividends paid',
            'transfer to reserves', 'transfer from reserves',
            'issue of share capital', 'buy-back of shares',
            'share-based payment transactions',
            'transfers between components of equity',
            'effects of changes in accounting policies',
            'effects of corrections of prior period errors',
        },
        
        # =====================================================================
        # TOTALS AND STRUCTURAL
        # =====================================================================
        'structural': {
            'total', 'sub-total', 'subtotal', 'net', 'gross',
            'total assets', 'total liabilities', 'total equity',
            'total equity and liabilities', 'total income', 'total expenses',
            'total non-current assets', 'total current assets',
            'total non-current liabilities', 'total current liabilities',
            'grand total', 'aggregate',
            'particulars', 'description', 'note', 'note no',
        },
    }
    
    # Important line items (used for highlighting)
    IMPORTANT_ITEMS = {
        # Balance Sheet Totals
        'total assets', 'total equity and liabilities', 'total equity',
        'total liabilities', 'net worth',
        'total non-current assets', 'total current assets',
        'total non-current liabilities', 'total current liabilities',
        # Income Statement
        'revenue from operations', 'total net sales', 'net sales',
        'total income', 'total expenses', 'gross profit',
        'operating profit', 'operating profit or loss', 'operating income',
        'profit before tax', 'profit for the year', 'profit for the period',
        'profit after tax', 'net profit', 'net income',
        'ebitda', 'ebit',
        'total comprehensive income',
        # EPS
        'earnings per share', 'basic eps', 'diluted eps',
        # Cash Flow
        'net cash from operating activities', 'net cash used in operating activities',
        'net cash from investing activities', 'net cash used in investing activities',
        'net cash from financing activities', 'net cash used in financing activities',
        'net increase in cash', 'net decrease in cash',
        'cash and cash equivalents at the end', 'free cash flow',
        # Key Items
        'cash and cash equivalents', 'trade receivables', 'inventories',
        'property, plant and equipment', 'goodwill',
        'trade payables', 'borrowings', 'lease liabilities',
        'share capital', 'retained earnings',
        # IFRS 18
        'profit or loss before financing and income taxes',
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
            r'\b(?:profit|loss)\s+(?:before|after|from)\b',
            r'\bcash\s+(?:flow|from|used)\b',
            r'\b(?:fair\s+value|fvtpl|fvoci)\b',
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
    
    @classmethod
    def get_keyword_count(cls) -> int:
        """Get total number of keywords in database."""
        return len(cls.get_all_keywords())
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get list of all keyword categories."""
        return list(cls.KEYWORDS.keys())
