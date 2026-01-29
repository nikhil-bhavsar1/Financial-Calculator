"""
Terminology Keywords Module - Aligned with TypeScript Terminology Map
Maps financial terms to metrics with universal keywords across IndAS, GAAP, IFRS
"""

# Universalized terminology structure matching library/terms/*.ts
# Format: term_key -> { keywords: [], category, metric_ids, boost }

TERMINOLOGY_MAP = {
    # ===== INCOME STATEMENT TERMS =====
    'total_revenue': {
        'category': 'Income Statement',
        'keywords': [
            'revenue from operations', 'total revenue', 'revenue', 'turnover',
            'gross revenue', 'operating revenue', 'income from operations',
            'sales revenue', 'revenue from contracts with customers',
            'net revenue', 'net revenues', 'net sales', 'total net sales',
            'product revenue', 'service revenue', 'subscription revenue',
            'revenue from ordinary activities', 'sale of goods', 'rendering of services'
        ],
        'metric_ids': ['calc_revenue_growth', 'calc_ps_ratio', 'calc_ev_to_sales'],
        'boost': 2.2,
        'standards': {'indas': ['IndAS 115'], 'gaap': ['ASC 606'], 'ifrs': ['IFRS 15']}
    },
    'cost_of_goods_sold': {
        'category': 'Income Statement',
        'keywords': [
            'cost of materials consumed', 'cost of goods sold', 'cost of sales',
            'purchases of stock-in-trade', 'raw materials consumed', 'cogs',
            'cost of revenue', 'direct costs', 'cost of products sold',
            'cost of goods manufactured', 'manufacturing cost'
        ],
        'metric_ids': ['calc_gross_profit', 'calc_gross_margin', 'calc_inventory_turnover'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 2'], 'gaap': ['ASC 330'], 'ifrs': ['IAS 2']}
    },
    'gross_profit': {
        'category': 'Income Statement',
        'keywords': [
            'gross profit', 'gross margin', 'gross income', 'trading profit', 'gross surplus'
        ],
        'metric_ids': ['calc_gross_profit', 'calc_gross_margin', 'calc_gross_profitability'],
        'boost': 2.0
    },
    'operating_profit': {
        'category': 'Income Statement',
        'keywords': [
            'profit from operations', 'operating profit', 'ebit', 'operating income',
            'earnings before interest and tax', 'profit before finance costs',
            'income from operations', 'operating earnings'
        ],
        'metric_ids': ['calc_operating_income', 'calc_operating_margin', 'calc_ebit_margin'],
        'boost': 2.2
    },
    'ebitda': {
        'category': 'Income Statement',
        'keywords': [
            'ebitda', 'earnings before interest tax depreciation amortization',
            'operating profit before depreciation', 'adjusted ebitda'
        ],
        'metric_ids': ['calc_ebitda', 'calc_ebitda_margin', 'calc_ev_to_ebitda', 'calc_debt_to_ebitda'],
        'boost': 2.3
    },
    'depreciation_amortization': {
        'category': 'Income Statement',
        'keywords': [
            'depreciation and amortisation expense', 'depreciation and amortization',
            'depreciation expense', 'amortisation expense', 'amortization', 'd&a',
            'depreciation on property plant and equipment', 'amortisation of intangible assets'
        ],
        'metric_ids': ['calc_ebitda', 'calc_fcf', 'calc_owner_earnings'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 16', 'IndAS 38'], 'gaap': ['ASC 350', 'ASC 360'], 'ifrs': ['IAS 16', 'IAS 38']}
    },
    'finance_costs': {
        'category': 'Income Statement',
        'keywords': [
            'finance costs', 'finance cost', 'interest expense', 'interest on borrowings',
            'interest on term loans', 'borrowing costs', 'debt service cost',
            'interest on lease liabilities', 'unwinding of discount'
        ],
        'metric_ids': ['calc_interest_coverage', 'calc_tie', 'calc_dscr'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 23'], 'gaap': ['ASC 835'], 'ifrs': ['IAS 23']}
    },
    'profit_before_tax': {
        'category': 'Income Statement',
        'keywords': [
            'profit before tax', 'pbt', 'profit before taxation',
            'income before taxes', 'pretax income', 'earnings before tax', 'pre-tax profit',
            'income before provision for income taxes'
        ],
        'metric_ids': ['calc_pre_tax_margin', 'calc_tax_burden'],
        'boost': 2.0
    },
    'tax_expense': {
        'category': 'Income Statement',
        'keywords': [
            'tax expense', 'income tax expense', 'current tax', 'deferred tax',
            'provision for taxation', 'income taxes', 'tax provision', 'tax charge',
            'provision for income taxes'
        ],
        'metric_ids': ['calc_nopat', 'calc_after_tax_margin'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'profit_after_tax': {
        'category': 'Income Statement',
        'keywords': [
            'profit after tax', 'profit for the year', 'profit for the period',
            'net profit', 'pat', 'net income', 'net earnings', 'bottom line',
            'profit attributable to owners', 'income after taxes'
        ],
        'metric_ids': ['calc_net_income', 'calc_net_profit_margin', 'calc_eps', 'calc_roe', 'calc_roa'],
        'boost': 2.2
    },
    'employee_benefits_expense': {
        'category': 'Income Statement',
        'keywords': [
            'employee benefit expense', 'employee benefits expense', 'employee cost',
            'staff cost', 'personnel expenses', 'salaries and wages', 'salary expense',
            'compensation and benefits', 'payroll expense', 'stock-based compensation'
        ],
        'metric_ids': [],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 19'], 'gaap': ['ASC 715'], 'ifrs': ['IAS 19']}
    },
    'research_development': {
        'category': 'Income Statement',
        'keywords': [
            'research and development', 'r&d expense', 'r&d', 'research expense',
            'development costs', 'research and development expenses'
        ],
        'metric_ids': [],
        'boost': 1.8
    },
    'other_income': {
        'category': 'Income Statement',
        'keywords': [
            'other income', 'other operating income', 'non-operating income',
            'sundry income', 'miscellaneous income', 'interest income',
            'dividend income', 'other income net'
        ],
        'metric_ids': [],
        'boost': 1.5
    },

    # ===== BALANCE SHEET - ASSETS =====
    'total_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'total assets', 'assets total', 'gross assets',
            'total assets end of year'
        ],
        'metric_ids': ['calc_roa', 'calc_debt_to_assets', 'calc_asset_turnover', 'calc_equity_multiplier'],
        'boost': 2.0
    },
    'total_non_current_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'total non-current assets', 'non-current assets', 'non current assets',
            'fixed assets total', 'long-term assets', 'capital assets',
            'total long-term assets'
        ],
        'metric_ids': ['calc_fixed_asset_turnover'],
        'boost': 2.0
    },
    'property_plant_equipment': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'property plant and equipment', 'ppe', 'fixed assets', 'tangible assets',
            'land and buildings', 'plant and machinery', 'pp&e',
            'capital work in progress', 'cwip', 'assets under construction',
            'property and equipment net', 'net property plant and equipment'
        ],
        'metric_ids': ['calc_fixed_asset_turnover', 'calc_rotc'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 16'], 'gaap': ['ASC 360'], 'ifrs': ['IAS 16']}
    },
    'intangible_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'intangible assets', 'goodwill', 'software', 'patents', 'trademarks',
            'copyrights', 'licenses', 'brand value', 'customer relationships',
            'technical know-how', 'franchise', 'development costs',
            'acquired intangible assets', 'net intangible assets'
        ],
        'metric_ids': ['calc_tangible_book_value', 'calc_tangible_bvps'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 38'], 'gaap': ['ASC 350'], 'ifrs': ['IAS 38']}
    },
    'goodwill': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'goodwill', 'goodwill net', 'acquired goodwill',
            'goodwill on consolidation', 'goodwill arising on acquisition'
        ],
        'metric_ids': ['calc_tangible_book_value'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 103', 'IndAS 36'], 'gaap': ['ASC 350', 'ASC 805'], 'ifrs': ['IAS 36', 'IFRS 3']}
    },
    'right_of_use_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'right of use assets', 'right-of-use assets', 'rou assets',
            'leased assets', 'lease assets', 'operating lease right of use',
            'operating lease right-of-use assets'
        ],
        'metric_ids': [],
        'boost': 2.2,
        'standards': {'indas': ['IndAS 116'], 'gaap': ['ASC 842'], 'ifrs': ['IFRS 16']}
    },
    'deferred_tax_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'deferred tax assets', 'deferred tax asset', 'dta',
            'deferred income tax assets', 'net deferred tax assets'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'marketable_securities': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'marketable securities', 'short-term investments', 'current marketable securities',
            'non-current marketable securities', 'trading securities',
            'available for sale securities', 'held to maturity securities'
        ],
        'metric_ids': ['calc_quick_ratio'],
        'boost': 1.8
    },
    'vendor_non_trade_receivables': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'vendor non-trade receivables', 'other receivables',
            'non-trade receivables', 'vendor receivables'
        ],
        'metric_ids': [],
        'boost': 1.5
    },
    'other_non_current_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'other non-current assets', 'other long-term assets',
            'long-term deposits', 'capital advances', 'other assets non-current'
        ],
        'metric_ids': [],
        'boost': 1.5
    },
    'total_current_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'total current assets', 'current assets', 'current assets total'
        ],
        'metric_ids': ['calc_current_ratio', 'calc_quick_ratio', 'calc_working_capital'],
        'boost': 1.8
    },
    'inventories': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'inventories', 'inventory', 'stock in trade', 'raw materials',
            'work in progress', 'wip', 'finished goods', 'stores and spares',
            'merchandise inventory', 'goods in transit'
        ],
        'metric_ids': ['calc_inventory_turnover', 'calc_dio', 'calc_quick_ratio'],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 2'], 'gaap': ['ASC 330'], 'ifrs': ['IAS 2']}
    },
    'trade_receivables': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'trade receivables', 'sundry debtors', 'accounts receivable',
            'receivables from customers', 'bills receivable', 'customer receivables',
            'receivables', 'debtors', 'net receivables', 'accounts receivable net'
        ],
        'metric_ids': ['calc_receivables_turnover', 'calc_dso', 'calc_quick_ratio'],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 109'], 'gaap': ['ASC 310'], 'ifrs': ['IFRS 9']}
    },
    'cash_and_equivalents': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'cash and cash equivalents', 'cash and bank balances', 'bank balances',
            'cash on hand', 'balances with banks', 'cash equivalents',
            'short-term deposits', 'fixed deposits', 'liquid investments', 'cash'
        ],
        'metric_ids': ['calc_cash_ratio', 'calc_net_debt', 'calc_net_debt_to_ebitda'],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 7'], 'gaap': ['ASC 230'], 'ifrs': ['IAS 7']}
    },
    'other_current_assets': {
        'category': 'Balance Sheet - Assets',
        'keywords': [
            'other current assets', 'prepaid expenses', 'advance payments',
            'prepaid expenses and other current assets', 'other receivables'
        ],
        'metric_ids': [],
        'boost': 1.5
    },

    # ===== BALANCE SHEET - LIABILITIES =====
    'total_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'total liabilities', 'liabilities total'
        ],
        'metric_ids': ['calc_debt_to_assets', 'calc_book_value'],
        'boost': 1.8
    },
    'total_non_current_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'total non-current liabilities', 'non-current liabilities',
            'long-term liabilities', 'non current liabilities total'
        ],
        'metric_ids': ['calc_debt_to_equity'],
        'boost': 1.8
    },
    'total_current_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'total current liabilities', 'current liabilities', 'current liabilities total'
        ],
        'metric_ids': ['calc_current_ratio', 'calc_quick_ratio', 'calc_working_capital', 'calc_ocf_to_cl'],
        'boost': 1.8
    },
    'borrowings': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'borrowings', 'loans', 'term loans', 'bank borrowings',
            'long-term debt', 'short-term debt', 'total debt',
            'notes payable', 'bonds payable', 'debentures', 'term debt'
        ],
        'metric_ids': ['calc_debt_to_equity', 'calc_debt_to_ebitda', 'calc_interest_coverage'],
        'boost': 2.0
    },
    'commercial_paper': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'commercial paper', 'short-term commercial paper',
            'cp borrowings', 'unsecured commercial paper'
        ],
        'metric_ids': [],
        'boost': 1.8
    },
    'trade_payables': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'trade payables', 'sundry creditors', 'accounts payable',
            'payables to suppliers', 'creditors', 'bills payable'
        ],
        'metric_ids': ['calc_payables_turnover', 'calc_dpo', 'calc_ccc'],
        'boost': 1.8
    },
    'deferred_revenue': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'deferred revenue', 'unearned revenue', 'contract liabilities',
            'advance from customers', 'deferred income'
        ],
        'metric_ids': [],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 115'], 'gaap': ['ASC 606'], 'ifrs': ['IFRS 15']}
    },
    'lease_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'lease liabilities', 'lease liability', 'lease obligations',
            'operating lease liability', 'finance lease liability',
            'operating lease liabilities', 'finance lease liabilities'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 116'], 'gaap': ['ASC 842'], 'ifrs': ['IFRS 16']}
    },
    'deferred_tax_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'deferred tax liabilities', 'deferred tax liability', 'dtl',
            'deferred income tax liabilities', 'net deferred tax liabilities'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'other_non_current_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'other non-current liabilities', 'other long-term liabilities'
        ],
        'metric_ids': [],
        'boost': 1.5
    },
    'other_current_liabilities': {
        'category': 'Balance Sheet - Liabilities',
        'keywords': [
            'other current liabilities', 'accrued expenses',
            'other accrued liabilities', 'accrued liabilities'
        ],
        'metric_ids': [],
        'boost': 1.5
    },

    # ===== BALANCE SHEET - EQUITY =====
    'total_equity': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'total equity', 'shareholders equity', 'shareholders funds',
            'stockholders equity', 'net worth', 'owners equity',
            'equity attributable to owners', 'total shareholders equity',
            "total shareholders' equity"
        ],
        'metric_ids': ['calc_roe', 'calc_debt_to_equity', 'calc_book_value_per_share', 'calc_pb_ratio'],
        'boost': 2.0
    },
    'share_capital': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'share capital', 'equity share capital', 'issued capital',
            'paid up capital', 'common stock', 'ordinary shares', 'capital stock',
            'common stock and additional paid-in capital', 'class a common stock',
            'class b common stock'
        ],
        'metric_ids': ['calc_shares_outstanding'],
        'boost': 1.8
    },
    'additional_paid_in_capital': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'additional paid-in capital', 'share premium', 'apic',
            'capital surplus', 'paid-in capital in excess of par',
            'securities premium'
        ],
        'metric_ids': [],
        'boost': 1.5
    },
    'retained_earnings': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'retained earnings', 'accumulated profits', 'surplus',
            'accumulated deficit', 'undistributed profits', 'reserves and surplus',
            'accumulated earnings (deficit)', 'reinvested earnings'
        ],
        'metric_ids': ['calc_retention_ratio', 'calc_sgr'],
        'boost': 1.8
    },
    'accumulated_oci': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'accumulated other comprehensive income', 'aoci',
            'accumulated other comprehensive income loss',
            'other comprehensive income accumulated', 'oci reserve'
        ],
        'metric_ids': [],
        'boost': 1.8
    },
    'treasury_stock': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'treasury stock', 'treasury shares', 'shares in treasury',
            'buyback of shares', 'cost of treasury stock', 'own shares held'
        ],
        'metric_ids': [],
        'boost': 1.8
    },
    'non_controlling_interest': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'non-controlling interests', 'non controlling interest', 'nci',
            'minority interest', 'equity attributable to non-controlling interests'
        ],
        'metric_ids': [],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 110'], 'gaap': ['ASC 810'], 'ifrs': ['IFRS 10']}
    },
    'equity_beginning_balance': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'beginning balance', 'opening balance', 'balance at beginning of year',
            'balances at beginning of period', 'equity beginning of period'
        ],
        'metric_ids': [],
        'boost': 1.5
    },
    'equity_ending_balance': {
        'category': 'Balance Sheet - Equity',
        'keywords': [
            'ending balance', 'closing balance', 'balance at end of year',
            'balances at end of period', 'ending balances', 'equity ending balance'
        ],
        'metric_ids': [],
        'boost': 1.5
    },

    # ===== STATEMENT OF COMPREHENSIVE INCOME =====
    'total_comprehensive_income': {
        'category': 'Comprehensive Income',
        'keywords': [
            'total comprehensive income', 'comprehensive income',
            'comprehensive income for the year', 'comprehensive income for the period',
            'total comprehensive income for the period'
        ],
        'metric_ids': [],
        'boost': 2.0
    },
    'other_comprehensive_income': {
        'category': 'Comprehensive Income',
        'keywords': [
            'other comprehensive income', 'oci', 'other comprehensive income loss',
            'other comprehensive income net of tax'
        ],
        'metric_ids': [],
        'boost': 2.0
    },
    'change_in_unrealized_gains_marketable_securities': {
        'category': 'Comprehensive Income',
        'keywords': [
            'change in unrealized gains losses on marketable securities',
            'unrealized gains on marketable debt securities',
            'unrealized gains losses on available for sale securities',
            'net unrealized gains losses on investments',
            'change in fair value of marketable securities'
        ],
        'metric_ids': [],
        'boost': 2.0
    },
    'change_in_unrealized_gains_derivatives': {
        'category': 'Comprehensive Income',
        'keywords': [
            'change in unrealized gains losses on derivative instruments',
            'total change in unrealized gains losses on derivative instruments',
            'change in fair value of derivative instruments',
            'effective portion of gains and losses on hedging instruments',
            'cash flow hedge reserve movement', 'derivative hedging gains losses',
            'unrealized gains on derivative instruments'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 109'], 'gaap': ['ASC 815'], 'ifrs': ['IFRS 9']}
    },
    'adjustment_for_net_gains_realized': {
        'category': 'Comprehensive Income',
        'keywords': [
            'adjustment for net gains realized and included in net income',
            'reclassification adjustments', 'amounts reclassified to profit or loss',
            'reclassified to net income'
        ],
        'metric_ids': [],
        'boost': 1.8
    },
    'foreign_currency_translation': {
        'category': 'Comprehensive Income',
        'keywords': [
            'foreign currency translation adjustment', 'foreign currency translation',
            'exchange differences on translation of foreign operations',
            'cumulative translation adjustment', 'translation reserve movement'
        ],
        'metric_ids': [],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 21'], 'gaap': ['ASC 830'], 'ifrs': ['IAS 21']}
    },
    'remeasurement_pension_plans': {
        'category': 'Comprehensive Income',
        'keywords': [
            'remeasurement of defined benefit plans', 'actuarial gains losses',
            'pension adjustments', 'postretirement benefit adjustments',
            'remeasurement of post-employment benefit obligations'
        ],
        'metric_ids': [],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 19'], 'gaap': ['ASC 715'], 'ifrs': ['IAS 19']}
    },

    # ===== CASH FLOW STATEMENT =====
    'operating_cash_flow': {
        'category': 'Cash Flow Statement',
        'keywords': [
            'cash flow from operating activities', 'operating cash flow',
            'cash generated from operations', 'net cash from operating activities',
            'ocf', 'cfo', 'cash flows from operations',
            'cash generated by operating activities'
        ],
        'metric_ids': ['calc_ocf', 'calc_fcf', 'calc_ocf_ratio', 'calc_cash_roa', 'calc_earnings_quality'],
        'boost': 2.2,
        'standards': {'indas': ['IndAS 7'], 'gaap': ['ASC 230'], 'ifrs': ['IAS 7']}
    },
    'investing_cash_flow': {
        'category': 'Cash Flow Statement',
        'keywords': [
            'cash flow from investing activities', 'investing cash flow',
            'net cash used in investing activities', 'capital expenditure',
            'capex', 'purchase of fixed assets', 'acquisition of ppe',
            'cash used in investing activities'
        ],
        'metric_ids': ['calc_fcf', 'calc_fcfe', 'calc_fcff'],
        'boost': 2.0
    },
    'financing_cash_flow': {
        'category': 'Cash Flow Statement',
        'keywords': [
            'cash flow from financing activities', 'financing cash flow',
            'net cash from financing activities', 'proceeds from borrowings',
            'repayment of borrowings', 'dividend paid', 'buyback',
            'cash used in financing activities'
        ],
        'metric_ids': ['calc_fcfe', 'calc_shareholder_yield'],
        'boost': 2.0
    },
    'free_cash_flow': {
        'category': 'Cash Flow Statement',
        'keywords': [
            'free cash flow', 'fcf', 'free cash flow to firm', 'fcff',
            'free cash flow to equity', 'fcfe', 'unlevered free cash flow'
        ],
        'metric_ids': ['calc_fcf', 'calc_fcfe', 'calc_fcff', 'calc_ev_to_fcf', 'calc_fcf_margin'],
        'boost': 2.3
    },
    'capital_expenditure': {
        'category': 'Cash Flow Statement',
        'keywords': [
            'capital expenditure', 'capex', 'purchases of property plant and equipment',
            'payments for acquisition of property', 'investments in property and equipment',
            'acquisition of fixed assets'
        ],
        'metric_ids': ['calc_fcf', 'calc_capex_ratio'],
        'boost': 2.0
    },
    'dividends_paid': {
        'category': 'Cash Flow Statement',
        'keywords': [
            'dividends paid', 'dividend paid', 'cash dividends paid',
            'dividends paid to shareholders', 'distribution to shareholders'
        ],
        'metric_ids': ['calc_dividend_payout', 'calc_shareholder_yield'],
        'boost': 2.0
    },

    # ===== FINANCIAL RATIOS & PER SHARE DATA =====
    'earnings_per_share': {
        'category': 'Financial Ratios',
        'keywords': [
            'earnings per share', 'eps', 'basic eps', 'diluted eps',
            'basic earnings per share', 'diluted earnings per share'
        ],
        'metric_ids': ['calc_eps', 'calc_diluted_eps', 'calc_pe_ratio', 'calc_peg_ratio'],
        'boost': 2.2,
        'standards': {'indas': ['IndAS 33'], 'gaap': ['ASC 260'], 'ifrs': ['IAS 33']}
    },
    'dividend_per_share': {
        'category': 'Financial Ratios',
        'keywords': [
            'dividend per share', 'dps', 'dividend per equity share',
            'dividends and dividend equivalents declared per share or rsu',
            'dividends declared per share', 'cash dividends per share',
            'dividend declared per common share'
        ],
        'metric_ids': ['calc_dps', 'calc_dividend_yield', 'calc_dividend_payout'],
        'boost': 1.8
    },
    'book_value_per_share': {
        'category': 'Financial Ratios',
        'keywords': [
            'book value per share', 'bvps', 'net asset value per share', 'nav per share'
        ],
        'metric_ids': ['calc_book_value_per_share', 'calc_pb_ratio', 'calc_graham_number'],
        'boost': 1.8
    },
    'market_price': {
        'category': 'Market Data',
        'keywords': [
            'market price', 'share price', 'stock price', 'current price',
            'closing price', 'market value per share'
        ],
        'metric_ids': ['calc_pe_ratio', 'calc_pb_ratio', 'calc_ps_ratio', 'calc_market_cap'],
        'boost': 1.5
    },
    'shares_outstanding': {
        'category': 'Market Data',
        'keywords': [
            'shares outstanding', 'number of shares', 'equity shares outstanding',
            'weighted average shares', 'common shares outstanding', 'shares in issue',
            'shares used in computing diluted earnings per share',
            'shares used in computing basic earnings per share'
        ],
        'metric_ids': ['calc_eps', 'calc_market_cap', 'calc_book_value_per_share'],
        'boost': 1.8
    },

    # ===== STATEMENT OF CHANGES IN EQUITY =====
    'common_stock_issued': {
        'category': 'Changes in Equity',
        'keywords': [
            'common stock issued', 'shares issued', 'issuance of common stock',
            'proceeds from issuance of shares', 'new shares issued'
        ],
        'metric_ids': [],
        'boost': 1.5
    },
    'share_based_compensation': {
        'category': 'Changes in Equity',
        'keywords': [
            'share-based compensation', 'stock-based compensation',
            'esop expense', 'equity compensation', 'stock option expense',
            'share options outstanding'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 102'], 'gaap': ['ASC 718'], 'ifrs': ['IFRS 2']}
    },
    'repurchases_of_common_stock': {
        'category': 'Changes in Equity',
        'keywords': [
            'repurchases of common stock', 'share buyback', 'treasury stock purchases',
            'buyback of shares', 'stock repurchases', 'shares repurchased'
        ],
        'metric_ids': ['calc_shareholder_yield'],
        'boost': 1.8
    },
    'dividends_declared': {
        'category': 'Changes in Equity',
        'keywords': [
            'dividends and dividend equivalents declared',
            'dividends declared', 'cash dividends declared',
            'dividends and dividend equivalents declared per share or rsu'
        ],
        'metric_ids': ['calc_dividend_payout', 'calc_dividend_yield'],
        'boost': 2.0
    },

    # ===== SPECIAL IndAS/GAAP/IFRS TERMS =====
    'expected_credit_loss': {
        'category': 'Financial Instruments',
        'keywords': [
            'expected credit loss', 'ecl', 'ecl provision', 'impairment allowance',
            'provision for expected credit losses', 'credit loss allowance'
        ],
        'metric_ids': [],
        'boost': 2.3,
        'standards': {'indas': ['IndAS 109'], 'gaap': ['ASC 326'], 'ifrs': ['IFRS 9']}
    },
    'fair_value': {
        'category': 'Fair Value',
        'keywords': [
            'fair value', 'fair value measurement', 'fvtpl', 'fvoci',
            'level 1', 'level 2', 'level 3', 'fair value hierarchy',
            'observable inputs', 'unobservable inputs', 'valuation technique'
        ],
        'metric_ids': [],
        'boost': 2.2,
        'standards': {'indas': ['IndAS 113'], 'gaap': ['ASC 820'], 'ifrs': ['IFRS 13']}
    },
    'related_party': {
        'category': 'Related Parties',
        'keywords': [
            'related party', 'related parties', 'related party transactions',
            'related party disclosures', 'key management personnel', 'kmp'
        ],
        'metric_ids': [],
        'boost': 2.3,
        'standards': {'indas': ['IndAS 24'], 'gaap': ['ASC 850'], 'ifrs': ['IAS 24']}
    },
    'segment_reporting': {
        'category': 'Segment Reporting',
        'keywords': [
            'segment reporting', 'operating segment', 'reportable segment',
            'segment revenue', 'segment result', 'segment assets',
            'americas segment', 'europe segment', 'greater china segment',
            'japan segment', 'rest of asia pacific segment'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 108'], 'gaap': ['ASC 280'], 'ifrs': ['IFRS 8']}
    },
    'contingent_liabilities': {
        'category': 'Contingencies',
        'keywords': [
            'contingent liability', 'contingent liabilities', 'contingent asset',
            'provisions', 'onerous contract', 'warranty provision', 'legal claims'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 37'], 'gaap': ['ASC 450'], 'ifrs': ['IAS 37']}
    },
    # ===== DEFERRED TAX DETAILS =====
    'deferred_tax_assets_rd': {
        'category': 'Tax',
        'keywords': [
            'capitalized research and development', 'research and development tax', 'r&d tax credits'
        ],
        'metric_ids': [], 
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_assets_credits': {
        'category': 'Tax',
        'keywords': [
            'tax credit carryforwards', 'tax credits', 'foreign tax credits', 'loss carryforwards',
            'net operating loss carryforwards', 'nol'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_assets_accrued': {
        'category': 'Tax',
        'keywords': [
            'accrued liabilities', 'other reserves', 'accrued expenses tax', 'reserves and surplus tax'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_assets_revenue': {
        'category': 'Tax',
        'keywords': [
            'deferred revenue tax', 'contract liabilities tax'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_assets_lease': {
        'category': 'Tax',
        'keywords': [
            'lease liabilities tax', 'operating lease liabilities tax'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_liabilities_depreciation': {
        'category': 'Tax',
        'keywords': [
            'depreciation tax', 'accelerated depreciation', 'property plant and equipment tax'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_liabilities_rou': {
        'category': 'Tax',
        'keywords': [
            'right-of-use assets tax', 'rou assets tax'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_min_tax_foreign': {
        'category': 'Tax',
        'keywords': [
            'minimum tax on foreign earnings', 'foreign earnings tax'
        ],
        'metric_ids': [],
        'boost': 1.5,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'deferred_tax_valuation_allowance': {
        'category': 'Tax',
        'keywords': [
            'valuation allowance', 'less: valuation allowance'
        ],
        'metric_ids': [],
        'boost': 1.8,
        'standards': {'indas': ['IndAS 12'], 'gaap': ['ASC 740'], 'ifrs': ['IAS 12']}
    },
    'business_combination': {
        'category': 'Business Combinations',
        'keywords': [
            'business combination', 'acquisition', 'purchase consideration',
            'bargain purchase', 'acquiree', 'acquirer', 'acquisition date', 'merger'
        ],
        'metric_ids': [],
        'boost': 2.0,
        'standards': {'indas': ['IndAS 103'], 'gaap': ['ASC 805'], 'ifrs': ['IFRS 3']}
    },
}

# Build flattened keyword -> term_key lookup for fast search
KEYWORD_TO_TERM = {}
for term_key, data in TERMINOLOGY_MAP.items():
    for kw in data['keywords']:
        kw_lower = kw.lower()
        if kw_lower not in KEYWORD_TO_TERM:
            KEYWORD_TO_TERM[kw_lower] = []
        KEYWORD_TO_TERM[kw_lower].append(term_key)

# Build keyword -> boost lookup
KEYWORD_BOOST = {}
for term_key, data in TERMINOLOGY_MAP.items():
    boost = data.get('boost', 1.0)
    for kw in data['keywords']:
        kw_lower = kw.lower()
        # Keep highest boost if keyword appears in multiple terms
        if kw_lower not in KEYWORD_BOOST or KEYWORD_BOOST[kw_lower] < boost:
            KEYWORD_BOOST[kw_lower] = boost


def get_metric_ids_for_term(term_key: str) -> list:
    """Get associated metric calculation IDs for a term."""
    if term_key in TERMINOLOGY_MAP:
        return TERMINOLOGY_MAP[term_key].get('metric_ids', [])
    return []


def get_term_for_keyword(keyword: str) -> list:
    """Get term keys that match a keyword."""
    return KEYWORD_TO_TERM.get(keyword.lower(), [])


def get_boost_for_keyword(keyword: str) -> float:
    """Get boost weight for a keyword."""
    return KEYWORD_BOOST.get(keyword.lower(), 1.0)


def get_all_keywords() -> list:
    """Get all unique keywords."""
    return list(KEYWORD_BOOST.keys())


def get_standards_for_term(term_key: str) -> dict:
    """Get related accounting standards for a term."""
    if term_key in TERMINOLOGY_MAP:
        return TERMINOLOGY_MAP[term_key].get('standards', {})
    return {}

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
    Unified source matching `TERMINOLOGY_MAP`.
    """
    
    # Core financial keywords are now DERIVED dynamically from TERMINOLOGY_MAP
    # This prevents duplication and ensures strict consistency.
    
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
        """Get flattened set of all keywords from TERMINOLOGY_MAP."""
        if cls._all_keywords is None:
            cls._all_keywords = set()
            for data in TERMINOLOGY_MAP.values():
                keywords = data.get('keywords', [])
                cls._all_keywords.update(keywords)
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
        
        for data in TERMINOLOGY_MAP.values():
            for keyword in data.get('keywords', []):
                if keyword in text_lower:
                    return data.get('category')
        
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
        return list(set(data.get('category') for data in TERMINOLOGY_MAP.values() if data.get('category')))
