import { TermMapping } from '../../types/terminology';

export const IND_AS_SPECIFIC_TERMS: TermMapping[] = [
    // ===== Ind AS 1: PRESENTATION OF FINANCIAL STATEMENTS =====
    {
        id: 'reserves_and_surplus',
        category: 'Balance Sheet - Equity',
        key: 'reserves_and_surplus',
        label: 'Reserves and Surplus',
        keywords_indas: [
            'reserves and surplus', 'reserves & surplus', 'reserves and surplus and other equity',
            'other equity', 'share premium', 'securities premium', 'general reserve',
            'revaluation reserve', 'capital reserve', 'retained earnings', 'surplus in profit and loss account'
        ],
        keywords_gaap: ['retained earnings', 'accumulated deficit', 'paid-in capital'],
        keywords_ifrs: ['reserves', 'retained earnings', 'other equity'],
        related_standards: {
            indas: ['IndAS 1'],
            gaap: ['ASC 210'],
            ifrs: ['IAS 1']
        }
    },
    {
        id: 'share_capital_issued',
        category: 'Balance Sheet - Equity',
        key: 'share_capital_issued',
        label: 'Issued Capital',
        keywords_indas: [
            'issued capital', 'issued share capital', 'share capital',
            'equity share capital', 'subscribed share capital', 'paid up capital',
            'capital issued', 'face value of shares', 'authorised share capital'
        ],
        keywords_gaap: ['common stock', 'capital stock', 'issued capital'],
        keywords_ifrs: ['issued capital', 'share capital'],
        related_standards: {
            indas: ['IndAS 1', 'IndAS 32'],
            gaap: ['ASC 210'],
            ifrs: ['IAS 32']
        }
    },
    {
        id: 'non_controlling_interests',
        category: 'Balance Sheet - Equity',
        key: 'non_controlling_interests',
        label: 'Non-Controlling Interests',
        keywords_indas: [
            'non-controlling interests', 'minority interest', 'nci',
            'interest in subsidiaries not attributable to owners',
            'minority shareholders interest', 'external interest in subsidiaries'
        ],
        keywords_gaap: ['minority interest', 'noncontrolling interest'],
        keywords_ifrs: ['non-controlling interest', 'minority interest'],
        related_standards: {
            indas: ['IndAS 1', 'IndAS 27'],
            gaap: ['ASC 810'],
            ifrs: ['IAS 27']
        }
    },
    {
        id: 'current_maturities_long_term_debt',
        category: 'Balance Sheet - Liabilities',
        key: 'current_maturities_long_term_debt',
        label: 'Current Maturities of Long Term Debt',
        keywords_indas: [
            'current maturities of long term debt', 'current maturities of long term borrowings',
            'current portion of long term debt', 'current portion of long term borrowings',
            'short-term portion of long-term debt', 'due within one year of long-term borrowings'
        ],
        keywords_gaap: ['current portion of long-term debt', 'short-term debt'],
        keywords_ifrs: ['current maturities of long-term borrowings'],
        related_standards: {
            indas: ['IndAS 1'],
            gaap: ['ASC 470'],
            ifrs: ['IAS 1']
        }
    },
    {
        id: 'trade_payables',
        category: 'Balance Sheet - Liabilities',
        key: 'trade_payables',
        label: 'Trade Payables',
        keywords_indas: [
            'trade payables', 'sundry creditors', 'accounts payable',
            'trade and other payables', 'creditors for goods and services',
            'trade creditors', 'accounts payable trade', 'bills payable'
        ],
        keywords_gaap: ['accounts payable', 'trade payables', 'accounts payable and accrued expenses'],
        keywords_ifrs: ['trade payables', 'trade and other payables'],
        related_standards: {
            indas: ['IndAS 1', 'IndAS 109'],
            gaap: ['ASC 210'],
            ifrs: ['IAS 1', 'IFRS 9']
        }
    },
    {
        id: 'other_current_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'other_current_liabilities',
        label: 'Other Current Liabilities',
        keywords_indas: [
            'other current liabilities', 'other payables', 'current liabilities other',
            'short-term provisions', 'provisions current', 'unclaimed dividends',
            'dividend payable', 'statutory dues payable', 'advance from customers'
        ],
        keywords_gaap: ['other current liabilities', 'accrued expenses'],
        keywords_ifrs: ['other current liabilities', 'trade and other payables'],
        related_standards: {
            indas: ['IndAS 1'],
            gaap: ['ASC 210'],
            ifrs: ['IAS 1']
        }
    },
    {
        id: 'statutory_dues',
        category: 'Balance Sheet - Liabilities',
        key: 'statutory_dues',
        label: 'Statutory Dues',
        keywords_indas: [
            'statutory dues', 'provident fund', 'employee state insurance',
            'gratuity', 'income tax payable', 'gst payable', 'tcs receivable',
            'tds payable', 'professional tax', 'payroll taxes'
        ],
        keywords_gaap: ['accrued payroll taxes', 'income taxes payable'],
        keywords_ifrs: ['trade and other payables', 'tax liabilities'],
        related_standards: {
            indas: ['IndAS 1', 'IndAS 19'],
            gaap: ['ASC 210', 'ASC 740'],
            ifrs: ['IAS 19']
        }
    },
    
    // ===== Ind AS 2: INVENTORIES =====
    {
        id: 'stock_in_trade',
        category: 'Balance Sheet - Assets',
        key: 'stock_in_trade',
        label: 'Stock in Trade',
        keywords_indas: [
            'stock in trade', 'merchandise inventory', 'trading inventory',
            'goods for sale', 'resale goods', 'merchandise stock'
        ],
        keywords_gaap: ['merchandise inventory'],
        keywords_ifrs: ['inventories'],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    {
        id: 'raw_materials_inventory',
        category: 'Balance Sheet - Assets',
        key: 'raw_materials_inventory',
        label: 'Raw Materials',
        keywords_indas: [
            'raw materials', 'raw materials and components', 'raw materials and stores',
            'raw materials and spares', 'material inventory', 'feedstock'
        ],
        keywords_gaap: ['raw materials inventory'],
        keywords_ifrs: ['raw materials and consumables'],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    {
        id: 'work_in_progress_inventory',
        category: 'Balance Sheet - Assets',
        key: 'work_in_progress_inventory',
        label: 'Work in Progress',
        keywords_indas: [
            'work in progress', 'wip', 'stock in process', 'semi-finished goods',
            'work in process', 'partially finished goods'
        ],
        keywords_gaap: ['work in process inventory'],
        keywords_ifrs: ['work in progress'],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    {
        id: 'finished_goods_inventory',
        category: 'Balance Sheet - Assets',
        key: 'finished_goods_inventory',
        label: 'Finished Goods',
        keywords_indas: [
            'finished goods', 'finished products', 'completed products',
            'manufactured goods', 'products ready for sale'
        ],
        keywords_gaap: ['finished goods inventory'],
        keywords_ifrs: ['finished goods'],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    {
        id: 'stores_and_spares',
        category: 'Balance Sheet - Assets',
        key: 'stores_and_spares',
        label: 'Stores and Spares',
        keywords_indas: [
            'stores and spares', 'consumables', 'maintenance stores',
            'spare parts', 'packing materials', 'operating supplies'
        ],
        keywords_gaap: ['supplies inventory', 'spare parts inventory'],
        keywords_ifrs: ['raw materials and consumables'],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    
    // ===== Ind AS 7: CASH FLOW STATEMENTS =====
    {
        id: 'cash_from_operations',
        category: 'Cash Flow Statement',
        key: 'cash_from_operations',
        label: 'Cash Flow from Operations',
        keywords_indas: [
            'cash flow from operating activities', 'cash from operating activities',
            'cash generated from operations', 'net cash from operating activities',
            'cash flow operations', 'operating cash flow'
        ],
        keywords_gaap: ['cash from operating activities'],
        keywords_ifrs: ['cash flows from operating activities'],
        related_standards: {
            indas: ['IndAS 7'],
            gaap: ['ASC 230'],
            ifrs: ['IAS 7']
        }
    },
    {
        id: 'cash_from_investing',
        category: 'Cash Flow Statement',
        key: 'cash_from_investing',
        label: 'Cash Flow from Investing',
        keywords_indas: [
            'cash flow from investing activities', 'cash from investing activities',
            'net cash from investing activities', 'cash flow investing'
        ],
        keywords_gaap: ['cash from investing activities'],
        keywords_ifrs: ['cash flows from investing activities'],
        related_standards: {
            indas: ['IndAS 7'],
            gaap: ['ASC 230'],
            ifrs: ['IAS 7']
        }
    },
    {
        id: 'cash_from_financing',
        category: 'Cash Flow Statement',
        key: 'cash_from_financing',
        label: 'Cash Flow from Financing',
        keywords_indas: [
            'cash flow from financing activities', 'cash from financing activities',
            'net cash from financing activities', 'cash flow financing'
        ],
        keywords_gaap: ['cash from financing activities'],
        keywords_ifrs: ['cash flows from financing activities'],
        related_standards: {
            indas: ['IndAS 7'],
            gaap: ['ASC 230'],
            ifrs: ['IAS 7']
        }
    },
    {
        id: 'cash_and_bank_balances',
        category: 'Balance Sheet - Assets',
        key: 'cash_and_bank_balances',
        label: 'Cash and Bank Balances',
        keywords_indas: [
            'cash and bank balances', 'cash in hand and at bank', 'cash on hand and bank balances',
            'cash and bank', 'bank balances and cash', 'balances with banks and cash on hand'
        ],
        keywords_gaap: ['cash and cash equivalents', 'cash'],
        keywords_ifrs: ['cash and cash equivalents'],
        related_standards: {
            indas: ['IndAS 7'],
            gaap: ['ASC 230'],
            ifrs: ['IAS 7']
        }
    },
    
    // ===== Ind AS 10: EVENTS AFTER REPORTING PERIOD =====
    {
        id: 'dividend_declared_after_balance_sheet',
        category: 'Statement of Changes in Equity',
        key: 'dividend_declared_after_balance_sheet',
        label: 'Dividend Declared After Balance Sheet',
        keywords_indas: [
            'dividend declared after balance sheet date', 'dividend for previous year',
            'final dividend', 'interim dividend', 'proposed dividend',
            'dividend proposed by directors'
        ],
        keywords_gaap: ['dividends declared after balance sheet'],
        keywords_ifrs: ['dividend declared after the reporting period'],
        related_standards: {
            indas: ['IndAS 10'],
            gaap: ['ASC 505'],
            ifrs: ['IAS 10']
        }
    },
    
    // ===== Ind AS 12: INCOME TAXES =====
    {
        id: 'deferred_tax_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'deferred_tax_liabilities',
        label: 'Deferred Tax Liabilities',
        keywords_indas: [
            'deferred tax liabilities', 'deferred tax liability', 'dtl',
            'deferred income tax liabilities', 'mat payable', 'minimum alternate tax credit payable'
        ],
        keywords_gaap: ['deferred tax liabilities', 'dtl'],
        keywords_ifrs: ['deferred tax liabilities'],
        related_standards: {
            indas: ['IndAS 12'],
            gaap: ['ASC 740'],
            ifrs: ['IAS 12']
        }
    },
    {
        id: 'deferred_tax_assets',
        category: 'Balance Sheet - Assets',
        key: 'deferred_tax_assets',
        label: 'Deferred Tax Assets',
        keywords_indas: [
            'deferred tax assets', 'deferred tax asset', 'dta',
            'mat credit entitlement', 'mat credit', 'minimum alternate tax credit',
            'deferred income tax assets', 'unabsorbed depreciation'
        ],
        keywords_gaap: ['deferred tax assets', 'dtl'],
        keywords_ifrs: ['deferred tax assets'],
        related_standards: {
            indas: ['IndAS 12'],
            gaap: ['ASC 740'],
            ifrs: ['IAS 12']
        }
    },
    {
        id: 'current_tax',
        category: 'Income Statement',
        key: 'current_tax',
        label: 'Current Tax',
        keywords_indas: [
            'current tax', 'income tax expense', 'income tax for the year',
            'provision for taxation', 'tax expense', 'tax on profit'
        ],
        keywords_gaap: ['current tax expense', 'income tax expense'],
        keywords_ifrs: ['current tax expense'],
        related_standards: {
            indas: ['IndAS 12'],
            gaap: ['ASC 740'],
            ifrs: ['IAS 12']
        }
    },
    {
        id: 'mat_credit_entitlement',
        category: 'Balance Sheet - Assets',
        key: 'mat_credit_entitlement',
        label: 'MAT Credit Entitlement',
        keywords_indas: [
            'mat credit entitlement', 'minimum alternate tax credit',
            'mat credit', 'mat set off', 'mat asset'
        ],
        keywords_gaap: [],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 12']
        }
    },
    
    // ===== Ind AS 16: PROPERTY, PLANT & EQUIPMENT =====
    {
        id: 'assets_under_construction',
        category: 'Balance Sheet - Assets',
        key: 'assets_under_construction',
        label: 'Assets Under Construction',
        keywords_indas: [
            'assets under construction', 'construction in progress',
            'capital work in progress', 'cwip', 'development expenditure',
            'building under construction', 'machinery under installation'
        ],
        keywords_gaap: ['construction in progress', 'cip'],
        keywords_ifrs: ['assets under construction'],
        related_standards: {
            indas: ['IndAS 16'],
            gaap: ['ASC 360'],
            ifrs: ['IAS 16']
        }
    },
    
    // ===== Ind AS 18: REVENUE =====
    {
        id: 'revenue_from_operations',
        category: 'Income Statement',
        key: 'revenue_from_operations',
        label: 'Revenue from Operations',
        keywords_indas: [
            'revenue from operations', 'revenue from operations net of excise duty',
            'sale of products', 'sale of goods', 'revenue from services',
            'income from operations', 'operating revenue', 'net sales'
        ],
        keywords_gaap: ['revenue', 'sales', 'net sales'],
        keywords_ifrs: ['revenue from contracts with customers'],
        related_standards: {
            indas: ['IndAS 18', 'IndAS 115'],
            gaap: ['ASC 606'],
            ifrs: ['IFRS 15']
        }
    },
    {
        id: 'other_income',
        category: 'Income Statement',
        key: 'other_income',
        label: 'Other Income',
        keywords_indas: [
            'other income', 'non-operating income', 'miscellaneous income',
            'interest income', 'dividend income', 'foreign exchange gain',
            'profit on sale of assets', 'income from investments'
        ],
        keywords_gaap: ['other income', 'non-operating income'],
        keywords_ifrs: ['other income'],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 225'],
            ifrs: ['IFRS 15']
        }
    },
    
    // ===== Ind AS 23: BORROWING COSTS =====
    {
        id: 'borrowing_costs_capitalized',
        category: 'Income Statement',
        key: 'borrowing_costs_capitalized',
        label: 'Borrowing Costs Capitalized',
        keywords_indas: [
            'borrowing costs capitalized', 'interest capitalized',
            'capitalized borrowing costs', 'finance cost capitalized'
        ],
        keywords_gaap: ['capitalized interest'],
        keywords_ifrs: ['borrowing costs capitalized'],
        related_standards: {
            indas: ['IndAS 23'],
            gaap: ['ASC 835'],
            ifrs: ['IAS 23']
        }
    },
    
    // ===== Ind AS 33: EARNINGS PER SHARE =====
    {
        id: 'basic_earnings_per_share',
        category: 'Income Statement',
        key: 'basic_earnings_per_share',
        label: 'Basic Earnings Per Share',
        keywords_indas: [
            'basic earnings per share', 'basic eps', 'basic earnings per share (rs)',
            'earnings per share basic'
        ],
        keywords_gaap: ['basic earnings per share', 'basic eps'],
        keywords_ifrs: ['basic earnings per share'],
        related_standards: {
            indas: ['IndAS 33'],
            gaap: ['ASC 260'],
            ifrs: ['IAS 33']
        }
    },
    {
        id: 'diluted_earnings_per_share',
        category: 'Income Statement',
        key: 'diluted_earnings_per_share',
        label: 'Diluted Earnings Per Share',
        keywords_indas: [
            'diluted earnings per share', 'diluted eps', 'diluted earnings per share (rs)',
            'earnings per share diluted'
        ],
        keywords_gaap: ['diluted earnings per share', 'diluted eps'],
        keywords_ifrs: ['diluted earnings per share'],
        related_standards: {
            indas: ['IndAS 33'],
            gaap: ['ASC 260'],
            ifrs: ['IAS 33']
        }
    },
    
    // ===== Ind AS 36: IMPAIRMENT =====
    {
        id: 'impairment_loss',
        category: 'Income Statement',
        key: 'impairment_loss',
        label: 'Impairment Loss',
        keywords_indas: [
            'impairment loss', 'impairment of assets', 'provision for impairment',
            'impairment provision', 'asset impairment', 'write down of assets'
        ],
        keywords_gaap: ['impairment loss', 'impairment charge'],
        keywords_ifrs: ['impairment loss'],
        related_standards: {
            indas: ['IndAS 36'],
            gaap: ['ASC 360'],
            ifrs: ['IAS 36']
        }
    },
    
    // ===== Ind AS 37: PROVISIONS =====
    {
        id: 'provisions',
        category: 'Balance Sheet - Liabilities',
        key: 'provisions',
        label: 'Provisions',
        keywords_indas: [
            'provisions', 'provision for warranties', 'provision for restructuring',
            'provision for doubtful debts', 'provision for gratuity',
            'provision for leave encashment', 'provision for pension',
            'other provisions'
        ],
        keywords_gaap: ['provisions', 'accrued liabilities'],
        keywords_ifrs: ['provisions'],
        related_standards: {
            indas: ['IndAS 37'],
            gaap: ['ASC 210'],
            ifrs: ['IAS 37']
        }
    },
    
    // ===== Ind AS 40: INVESTMENT PROPERTY =====
    {
        id: 'investment_properties',
        category: 'Balance Sheet - Assets',
        key: 'investment_properties',
        label: 'Investment Properties',
        keywords_indas: [
            'investment properties', 'investment property', 'rental properties',
            'properties held for rental income', 'real estate for investment'
        ],
        keywords_gaap: ['investment property'],
        keywords_ifrs: ['investment property'],
        related_standards: {
            indas: ['IndAS 40'],
            gaap: ['ASC 970'],
            ifrs: ['IAS 40']
        }
    },
    
    // ===== Ind AS 109: FINANCIAL INSTRUMENTS =====
    {
        id: 'expected_credit_loss',
        category: 'Balance Sheet - Assets',
        key: 'expected_credit_loss',
        label: 'Expected Credit Loss',
        keywords_indas: [
            'expected credit loss', 'ecl provision', 'credit loss provision',
            'ecl allowance', 'provision for expected credit losses',
            'credit impairment'
        ],
        keywords_gaap: ['allowance for credit losses', 'credit loss allowance'],
        keywords_ifrs: ['expected credit loss allowance'],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 326'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'fair_value_changes',
        category: 'Income Statement',
        key: 'fair_value_changes',
        label: 'Fair Value Changes',
        keywords_indas: [
            'fair value changes', 'fair value gain loss', 'fvtpl fair value changes',
            'fair value through profit or loss', 'mark to market gains losses'
        ],
        keywords_gaap: ['fair value changes'],
        keywords_ifrs: ['fair value gains/losses'],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 820'],
            ifrs: ['IFRS 9']
        }
    },
    
    // ===== Ind AS 115: REVENUE FROM CONTRACTS =====
    {
        id: 'contract_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'contract_liabilities',
        label: 'Contract Liabilities',
        keywords_indas: [
            'contract liabilities', 'deferred revenue', 'advance from customers',
            'unearned revenue', 'customer advances', 'advances from customers'
        ],
        keywords_gaap: ['deferred revenue', 'contract liabilities'],
        keywords_ifrs: ['contract liabilities'],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 606'],
            ifrs: ['IFRS 15']
        }
    },
    {
        id: 'contract_assets',
        category: 'Balance Sheet - Assets',
        key: 'contract_assets',
        label: 'Contract Assets',
        keywords_indas: [
            'contract assets', 'unbilled revenue', 'accrued income',
            'unbilled receivables', 'revenue accruals', 'accrued revenue'
        ],
        keywords_gaap: ['contract assets', 'unbilled receivables'],
        keywords_ifrs: ['contract assets'],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 606'],
            ifrs: ['IFRS 15']
        }
    },
    
    // ===== Indian Specific Terms =====
    {
        id: 'long_term_borrowings',
        category: 'Balance Sheet - Liabilities',
        key: 'long_term_borrowings',
        label: 'Long Term Borrowings',
        keywords_indas: [
            'long term borrowings', 'long-term borrowings', 'long term debt',
            'term loans', 'secured loans', 'unsecured loans',
            'foreign currency borrowings', 'external commercial borrowings',
            'debentures', 'bonds', 'term loan from banks'
        ],
        keywords_gaap: ['long-term debt', 'long-term borrowings'],
        keywords_ifrs: ['long-term borrowings'],
        related_standards: {
            indas: ['IndAS 1', 'IndAS 109'],
            gaap: ['ASC 470'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'short_term_borrowings',
        category: 'Balance Sheet - Liabilities',
        key: 'short_term_borrowings',
        label: 'Short Term Borrowings',
        keywords_indas: [
            'short term borrowings', 'short-term borrowings', 'short term debt',
            'working capital loans', 'cash credit', 'bank overdraft',
            'short-term loans', 'commercial paper'
        ],
        keywords_gaap: ['short-term debt'],
        keywords_ifrs: ['short-term borrowings'],
        related_standards: {
            indas: ['IndAS 1', 'IndAS 109'],
            gaap: ['ASC 470'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'inter_corporate_deposits',
        category: 'Balance Sheet - Assets',
        key: 'inter_corporate_deposits',
        label: 'Inter-Corporate Deposits',
        keywords_indas: [
            'inter-corporate deposits', 'inter corporate deposits', 'icd',
            'deposits with other companies', 'deposits with corporates'
        ],
        keywords_gaap: [],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 109']
        }
    },
    {
        id: 'loans_to_directors',
        category: 'Balance Sheet - Assets',
        key: 'loans_to_directors',
        label: 'Loans to Directors',
        keywords_indas: [
            'loans to directors', 'loans to key managerial personnel',
            'loans to related parties', 'advances to directors'
        ],
        keywords_gaap: ['loans to related parties'],
        keywords_ifrs: ['loans to related parties'],
        related_standards: {
            indas: ['IndAS 109', 'IndAS 24']
        }
    },
    {
        id: 'capital_advances',
        category: 'Balance Sheet - Assets',
        key: 'capital_advances',
        label: 'Capital Advances',
        keywords_indas: [
            'capital advances', 'advances for capital goods',
            'advances for machinery', 'advances for equipment'
        ],
        keywords_gaap: [],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 16']
        }
    },
    {
        id: 'balance_with_government',
        category: 'Balance Sheet - Assets',
        key: 'balance_with_government',
        label: 'Balance with Government',
        keywords_indas: [
            'balance with government', 'balance with government authorities',
            'deposits with government', 'government dues receivable'
        ],
        keywords_gaap: [],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 1']
        }
    },
    {
        id: 'export_incentives_receivable',
        category: 'Balance Sheet - Assets',
        key: 'export_incentives_receivable',
        label: 'Export Incentives Receivable',
        keywords_indas: [
            'export incentives receivable', 'duty drawback receivable',
            'incentives from government', 'export promotion incentives'
        ],
        keywords_gaap: [],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 1']
        }
    },
    {
        id: 'unclaimed_dividends',
        category: 'Balance Sheet - Liabilities',
        key: 'unclaimed_dividends',
        label: 'Unclaimed Dividends',
        keywords_indas: [
            'unclaimed dividends', 'dividends unpaid', 'unpaid dividend account',
            'dividend not claimed'
        ],
        keywords_gaap: [],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 1']
        }
    },
    {
        id: 'employee_benefits_obligation',
        category: 'Balance Sheet - Liabilities',
        key: 'employee_benefits_obligation',
        label: 'Employee Benefits Obligation',
        keywords_indas: [
            'employee benefits obligation', 'gratuity obligation',
            'leave encashment obligation', 'pension obligation',
            'post-employment benefit obligation'
        ],
        keywords_gaap: ['pension liability', 'post-employment benefits'],
        keywords_ifrs: ['employee benefits'],
        related_standards: {
            indas: ['IndAS 19'],
            gaap: ['ASC 715'],
            ifrs: ['IAS 19']
        }
    },
    {
        id: 'securitisation_receivables',
        category: 'Balance Sheet - Assets',
        key: 'securitisation_receivables',
        label: 'Securitisation Receivables',
        keywords_indas: [
            'securitisation receivables', 'securitised assets',
            'assignment receivables', 'factored receivables'
        ],
        keywords_gaap: ['securitized receivables'],
        keywords_ifrs: [],
        related_standards: {
            indas: ['IndAS 109']
        }
    }
];