import { TermMapping } from '../../types/terminology';

export const BALANCE_SHEET_LIABILITIES_TERMS: TermMapping[] = [
    // ===== NON-CURRENT LIABILITIES =====
    {
        id: 'total_non_current_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'total_non_current_liabilities',
        label: 'Total Non-Current Liabilities',
        keywords_indas: [
            'total non-current liabilities', 'non-current liabilities',
            'long-term liabilities'
        ],
        keywords_gaap: [
            'total non-current liabilities', 'long-term liabilities',
            'total long-term debt and liabilities'
        ],
        keywords_ifrs: [
            'total non-current liabilities', 'non-current liabilities'
        ]
    },
    {
        id: 'long_term_borrowings',
        category: 'Balance Sheet - Liabilities',
        key: 'long_term_borrowings',
        label: 'Long-term Borrowings',
        keywords_indas: [
            'long-term borrowings', 'term loans', 'secured loans',
            'unsecured loans', 'debentures', 'bonds',
            'non-convertible debentures', 'ncd', 'external commercial borrowings',
            'ecb', 'foreign currency loans', 'rupee term loans',
            'borrowings from banks', 'borrowings from financial institutions'
        ],
        keywords_gaap: [
            'long-term debt', 'notes payable long-term', 'bonds payable',
            'senior notes', 'senior unsecured notes', 'term loan',
            'credit facility', 'convertible notes', 'mortgage payable'
        ],
        keywords_ifrs: [
            'long-term borrowings', 'bank borrowings', 'loans and borrowings',
            'bonds', 'debentures', 'interest-bearing loans'
        ],
        related_standards: {
            indas: ['IndAS 109', 'IndAS 32'],
            gaap: ['ASC 470'],
            ifrs: ['IFRS 9', 'IAS 32']
        }
    },
    {
        id: 'lease_liabilities_non_current',
        category: 'Balance Sheet - Liabilities',
        key: 'lease_liabilities_non_current',
        label: 'Lease Liabilities (Non-Current)',
        keywords_indas: [
            'lease liabilities', 'finance lease obligations',
            'operating lease liabilities', 'lease liability non-current'
        ],
        keywords_gaap: [
            'operating lease liabilities', 'finance lease liabilities',
            'capital lease obligations', 'lease obligations long-term'
        ],
        keywords_ifrs: [
            'lease liabilities', 'lease obligations', 'finance lease liabilities'
        ],
        related_standards: {
            indas: ['IndAS 116'],
            gaap: ['ASC 842'],
            ifrs: ['IFRS 16']
        }
    },
    {
        id: 'deferred_tax_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'deferred_tax_liabilities',
        label: 'Deferred Tax Liabilities',
        keywords_indas: [
            'deferred tax liabilities', 'deferred tax liability', 'dtl',
            'deferred income tax liabilities'
        ],
        keywords_gaap: [
            'deferred tax liabilities', 'deferred income taxes', 'dtl',
            'deferred tax liability net'
        ],
        keywords_ifrs: [
            'deferred tax liabilities', 'deferred income tax liabilities'
        ],
        related_standards: {
            indas: ['IndAS 12'],
            gaap: ['ASC 740'],
            ifrs: ['IAS 12']
        }
    },
    {
        id: 'provisions_non_current',
        category: 'Balance Sheet - Liabilities',
        key: 'provisions_non_current',
        label: 'Provisions (Non-Current)',
        keywords_indas: [
            'provisions', 'provision for employee benefits',
            'provision for gratuity', 'provision for leave encashment',
            'provision for warranties', 'provision for decommissioning',
            'asset retirement obligation', 'environmental provisions'
        ],
        keywords_gaap: [
            'provisions', 'accrued liabilities long-term',
            'asset retirement obligations', 'environmental liabilities',
            'warranty reserve long-term', 'pension liabilities'
        ],
        keywords_ifrs: [
            'provisions', 'employee benefit obligations', 'warranty provisions',
            'decommissioning provisions', 'restoration provisions'
        ],
        related_standards: {
            indas: ['IndAS 37', 'IndAS 19'],
            gaap: ['ASC 410', 'ASC 450'],
            ifrs: ['IAS 37', 'IAS 19']
        }
    },
    {
        id: 'employee_benefit_obligations',
        category: 'Balance Sheet - Liabilities',
        key: 'employee_benefit_obligations',
        label: 'Employee Benefit Obligations',
        keywords_indas: [
            'employee benefit obligations', 'defined benefit obligation',
            'gratuity liability', 'pension liability', 'leave encashment liability',
            'post-employment benefit obligations'
        ],
        keywords_gaap: [
            'pension liability', 'postretirement benefit obligation',
            'defined benefit liability', 'opeb liability'
        ],
        keywords_ifrs: [
            'employee benefit obligations', 'retirement benefit obligations',
            'defined benefit liability', 'post-employment benefit liability'
        ],
        related_standards: {
            indas: ['IndAS 19'],
            gaap: ['ASC 715'],
            ifrs: ['IAS 19']
        }
    },
    {
        id: 'deferred_revenue_non_current',
        category: 'Balance Sheet - Liabilities',
        key: 'deferred_revenue_non_current',
        label: 'Deferred Revenue (Non-Current)',
        keywords_indas: [
            'deferred revenue', 'contract liabilities non-current',
            'deferred income', 'unearned revenue non-current'
        ],
        keywords_gaap: [
            'deferred revenue long-term', 'unearned revenue long-term',
            'contract liabilities non-current'
        ],
        keywords_ifrs: [
            'deferred income', 'contract liabilities non-current',
            'deferred revenue'
        ]
    },
    {
        id: 'other_non_current_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'other_non_current_liabilities',
        label: 'Other Non-Current Liabilities',
        keywords_indas: [
            'other non-current liabilities', 'other long-term liabilities',
            'government grants deferred', 'derivative liabilities non-current'
        ],
        keywords_gaap: [
            'other non-current liabilities', 'other long-term liabilities'
        ],
        keywords_ifrs: [
            'other non-current liabilities', 'other long-term liabilities'
        ]
    },

    // ===== CURRENT LIABILITIES =====
    {
        id: 'total_current_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'total_current_liabilities',
        label: 'Total Current Liabilities',
        keywords_indas: [
            'total current liabilities', 'current liabilities'
        ],
        keywords_gaap: [
            'total current liabilities', 'current liabilities total'
        ],
        keywords_ifrs: [
            'total current liabilities', 'current liabilities'
        ]
    },
    {
        id: 'short_term_borrowings',
        category: 'Balance Sheet - Liabilities',
        key: 'short_term_borrowings',
        label: 'Short-term Borrowings',
        keywords_indas: [
            'short-term borrowings', 'working capital loans', 'cash credit',
            'overdraft', 'short-term loans', 'packing credit',
            'bills discounted', 'current maturities of long-term debt',
            'commercial paper', 'inter-corporate deposits payable'
        ],
        keywords_gaap: [
            'short-term debt', 'current portion of long-term debt',
            'notes payable', 'commercial paper', 'line of credit',
            'revolving credit facility', 'short-term borrowings'
        ],
        keywords_ifrs: [
            'short-term borrowings', 'bank overdrafts', 'current portion of borrowings',
            'short-term loans'
        ]
    },
    {
        id: 'current_portion_long_term_debt',
        category: 'Balance Sheet - Liabilities',
        key: 'current_portion_long_term_debt',
        label: 'Current Portion of Long-term Debt',
        keywords_indas: [
            'current maturities of long-term debt', 'current maturities of long-term borrowings',
            'current portion of long-term debt'
        ],
        keywords_gaap: [
            'current portion of long-term debt', 'current maturities of long-term debt',
            'long-term debt due within one year'
        ],
        keywords_ifrs: [
            'current portion of long-term borrowings', 'current maturities'
        ]
    },
    {
        id: 'lease_liabilities_current',
        category: 'Balance Sheet - Liabilities',
        key: 'lease_liabilities_current',
        label: 'Lease Liabilities (Current)',
        keywords_indas: [
            'lease liabilities current', 'current lease liabilities',
            'operating lease liability current'
        ],
        keywords_gaap: [
            'operating lease liabilities current', 'finance lease liabilities current',
            'current lease obligations'
        ],
        keywords_ifrs: [
            'lease liabilities current', 'current portion of lease liabilities'
        ],
        related_standards: {
            indas: ['IndAS 116'],
            gaap: ['ASC 842'],
            ifrs: ['IFRS 16']
        }
    },
    {
        id: 'trade_payables',
        category: 'Balance Sheet - Liabilities',
        key: 'trade_payables',
        label: 'Trade Payables',
        keywords_indas: [
            'trade payables', 'accounts payable', 'sundry creditors',
            'trade and other payables', 'creditors for goods',
            'creditors for expenses', 'bills payable',
            'payable to micro and small enterprises', 'msme payables',
            'payables to vendors', 'suppliers payable'
        ],
        keywords_gaap: [
            'accounts payable', 'trade payables', 'trade accounts payable',
            'payables', 'accounts payable and accrued expenses'
        ],
        keywords_ifrs: [
            'trade payables', 'trade and other payables', 'accounts payable',
            'payables to suppliers'
        ]
    },
    {
        id: 'contract_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'contract_liabilities',
        label: 'Contract Liabilities',
        keywords_indas: [
            'contract liabilities', 'advance from customers',
            'customer advances', 'deferred revenue', 'unearned revenue',
            'billings in excess of costs'
        ],
        keywords_gaap: [
            'contract liabilities', 'deferred revenue', 'unearned revenue',
            'customer deposits', 'advance payments from customers'
        ],
        keywords_ifrs: [
            'contract liabilities', 'deferred income', 'advances from customers',
            'revenue received in advance'
        ],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 606'],
            ifrs: ['IFRS 15']
        }
    },
    {
        id: 'other_financial_liabilities_current',
        category: 'Balance Sheet - Liabilities',
        key: 'other_financial_liabilities_current',
        label: 'Other Financial Liabilities (Current)',
        keywords_indas: [
            'other financial liabilities', 'interest accrued but not due',
            'unpaid dividends', 'payable to employees', 'capital creditors',
            'security deposits received', 'derivative liabilities'
        ],
        keywords_gaap: [
            'other current financial liabilities', 'accrued interest payable',
            'dividends payable', 'derivative liabilities current'
        ],
        keywords_ifrs: [
            'other financial liabilities', 'derivative financial liabilities current'
        ]
    },
    {
        id: 'provisions_current',
        category: 'Balance Sheet - Liabilities',
        key: 'provisions_current',
        label: 'Provisions (Current)',
        keywords_indas: [
            'provisions current', 'provision for employee benefits current',
            'provision for warranties current', 'provision for onerous contracts',
            'provision for taxes', 'provision for litigation'
        ],
        keywords_gaap: [
            'accrued liabilities', 'accrued expenses', 'warranty reserve current',
            'litigation reserves', 'restructuring reserves'
        ],
        keywords_ifrs: [
            'current provisions', 'provisions for liabilities'
        ],
        related_standards: {
            indas: ['IndAS 37'],
            gaap: ['ASC 450'],
            ifrs: ['IAS 37']
        }
    },
    {
        id: 'income_tax_payable',
        category: 'Balance Sheet - Liabilities',
        key: 'income_tax_payable',
        label: 'Income Tax Payable',
        keywords_indas: [
            'current tax liabilities', 'provision for income tax',
            'income tax payable', 'tax payable'
        ],
        keywords_gaap: [
            'income taxes payable', 'current income tax liability',
            'accrued income taxes'
        ],
        keywords_ifrs: [
            'current tax liabilities', 'income tax payable'
        ]
    },
    {
        id: 'other_current_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'other_current_liabilities',
        label: 'Other Current Liabilities',
        keywords_indas: [
            'other current liabilities', 'statutory dues payable',
            'gst payable', 'tds payable', 'pf payable', 'esi payable',
            'advance from customers', 'other payables'
        ],
        keywords_gaap: [
            'other current liabilities', 'accrued expenses',
            'other accrued liabilities'
        ],
        keywords_ifrs: [
            'other current liabilities', 'other payables'
        ]
    },
    {
        id: 'liabilities_held_for_sale',
        category: 'Balance Sheet - Liabilities',
        key: 'liabilities_held_for_sale',
        label: 'Liabilities Held for Sale',
        keywords_indas: [
            'liabilities associated with assets held for sale',
            'liabilities of disposal group'
        ],
        keywords_gaap: [
            'liabilities held for sale', 'liabilities of discontinued operations'
        ],
        keywords_ifrs: [
            'liabilities directly associated with assets held for sale',
            'liabilities of disposal group'
        ],
        related_standards: {
            indas: ['IndAS 105'],
            gaap: ['ASC 360'],
            ifrs: ['IFRS 5']
        }
    },
    {
        id: 'total_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'total_liabilities',
        label: 'Total Liabilities',
        keywords_indas: [
            'total liabilities', 'liabilities total'
        ],
        keywords_gaap: [
            'total liabilities', 'liabilities total'
        ],
        keywords_ifrs: [
            'total liabilities', 'liabilities total'
        ]
    }
];
