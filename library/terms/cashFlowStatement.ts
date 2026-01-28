import { TermMapping } from '../../types/terminology';

export const CASH_FLOW_STATEMENT_TERMS: TermMapping[] = [
    // ===== OPERATING ACTIVITIES =====
    {
        id: 'cash_from_operations',
        category: 'Cash Flow Statement',
        key: 'cash_from_operations',
        label: 'Cash Flow from Operating Activities',
        keywords_indas: [
            'cash flows from operating activities', 'operating cash flow',
            'cash generated from operations', 'net cash from operating activities',
            'net cash generated from operations', 'cash from operations'
        ],
        keywords_gaap: [
            'net cash provided by operating activities', 'operating cash flow',
            'cash flows from operating activities', 'cash from operations',
            'net cash from operating activities'
        ],
        keywords_ifrs: [
            'cash flows from operating activities', 'operating activities',
            'net cash from operating activities', 'cash generated from operations'
        ],
        related_standards: {
            indas: ['IndAS 7'],
            gaap: ['ASC 230'],
            ifrs: ['IAS 7']
        }
    },
    {
        id: 'profit_before_tax_cf',
        category: 'Cash Flow Statement',
        key: 'profit_before_tax_cf',
        label: 'Profit Before Tax (CF Starting Point)',
        keywords_indas: [
            'profit before tax', 'operating profit before working capital changes'
        ],
        keywords_gaap: [
            'net income', 'income before taxes'
        ],
        keywords_ifrs: [
            'profit before tax', 'profit before income tax'
        ]
    },
    {
        id: 'depreciation_cf',
        category: 'Cash Flow Statement',
        key: 'depreciation_cf',
        label: 'Depreciation (Add Back)',
        keywords_indas: [
            'depreciation and amortisation', 'add: depreciation',
            'depreciation expense'
        ],
        keywords_gaap: [
            'depreciation and amortization', 'add back depreciation'
        ],
        keywords_ifrs: [
            'depreciation and amortisation', 'depreciation add back'
        ]
    },
    {
        id: 'working_capital_changes',
        category: 'Cash Flow Statement',
        key: 'working_capital_changes',
        label: 'Working Capital Changes',
        keywords_indas: [
            'working capital changes', 'changes in working capital',
            'movement in working capital', 'operating working capital changes'
        ],
        keywords_gaap: [
            'changes in operating assets and liabilities',
            'working capital changes', 'change in operating working capital'
        ],
        keywords_ifrs: [
            'working capital changes', 'changes in working capital'
        ]
    },
    {
        id: 'change_in_receivables',
        category: 'Cash Flow Statement',
        key: 'change_in_receivables',
        label: 'Change in Receivables',
        keywords_indas: [
            'increase in trade receivables', 'decrease in trade receivables',
            'change in receivables', 'movement in trade receivables'
        ],
        keywords_gaap: [
            'increase decrease in accounts receivable',
            'change in accounts receivable'
        ],
        keywords_ifrs: [
            'change in trade receivables', 'increase decrease in receivables'
        ]
    },
    {
        id: 'change_in_inventory',
        category: 'Cash Flow Statement',
        key: 'change_in_inventory',
        label: 'Change in Inventory',
        keywords_indas: [
            'increase in inventories', 'decrease in inventories',
            'change in inventories', 'movement in inventory'
        ],
        keywords_gaap: [
            'increase decrease in inventory', 'change in inventories'
        ],
        keywords_ifrs: [
            'change in inventories', 'increase decrease in inventory'
        ]
    },
    {
        id: 'change_in_payables',
        category: 'Cash Flow Statement',
        key: 'change_in_payables',
        label: 'Change in Payables',
        keywords_indas: [
            'increase in trade payables', 'decrease in trade payables',
            'change in payables', 'movement in trade payables'
        ],
        keywords_gaap: [
            'increase decrease in accounts payable',
            'change in accounts payable'
        ],
        keywords_ifrs: [
            'change in trade payables', 'increase decrease in payables'
        ]
    },
    {
        id: 'income_tax_paid',
        category: 'Cash Flow Statement',
        key: 'income_tax_paid',
        label: 'Income Tax Paid',
        keywords_indas: [
            'income tax paid', 'taxes paid', 'direct taxes paid',
            'payment of income tax'
        ],
        keywords_gaap: [
            'income taxes paid', 'taxes paid'
        ],
        keywords_ifrs: [
            'income tax paid', 'taxes paid'
        ]
    },

    // ===== INVESTING ACTIVITIES =====
    {
        id: 'cash_from_investing',
        category: 'Cash Flow Statement',
        key: 'cash_from_investing',
        label: 'Cash Flow from Investing Activities',
        keywords_indas: [
            'cash flows from investing activities', 'investing activities',
            'net cash from investing activities', 'net cash used in investing activities'
        ],
        keywords_gaap: [
            'net cash used in investing activities', 'investing cash flow',
            'cash flows from investing activities', 'net cash from investing'
        ],
        keywords_ifrs: [
            'cash flows from investing activities', 'investing activities',
            'net cash used in investing activities'
        ]
    },
    {
        id: 'capex',
        category: 'Cash Flow Statement',
        key: 'capex',
        label: 'Capital Expenditure',
        keywords_indas: [
            'purchase of property plant and equipment', 'capex',
            'capital expenditure', 'acquisition of fixed assets',
            'purchase of tangible assets', 'purchase of intangible assets',
            'additions to fixed assets'
        ],
        keywords_gaap: [
            'capital expenditures', 'capex', 'purchases of property and equipment',
            'payments for acquisition of property plant and equipment'
        ],
        keywords_ifrs: [
            'purchases of property plant and equipment', 'capital expenditure',
            'acquisition of property plant and equipment'
        ]
    },
    {
        id: 'sale_of_ppe',
        category: 'Cash Flow Statement',
        key: 'sale_of_ppe',
        label: 'Proceeds from Sale of PPE',
        keywords_indas: [
            'sale of property plant and equipment', 'proceeds from disposal of fixed assets',
            'sale of tangible assets', 'disposal of fixed assets'
        ],
        keywords_gaap: [
            'proceeds from sale of property and equipment',
            'proceeds from disposal of assets'
        ],
        keywords_ifrs: [
            'proceeds from sale of property plant and equipment',
            'disposal of property plant and equipment'
        ]
    },
    {
        id: 'acquisition_of_subsidiaries',
        category: 'Cash Flow Statement',
        key: 'acquisition_of_subsidiaries',
        label: 'Acquisition of Subsidiaries',
        keywords_indas: [
            'acquisition of subsidiaries', 'purchase of subsidiary',
            'investment in subsidiary', 'acquisition net of cash'
        ],
        keywords_gaap: [
            'acquisitions net of cash acquired', 'purchase of businesses',
            'acquisition of subsidiaries'
        ],
        keywords_ifrs: [
            'acquisition of subsidiaries net of cash',
            'acquisition of businesses'
        ],
        related_standards: {
            indas: ['IndAS 103'],
            gaap: ['ASC 805'],
            ifrs: ['IFRS 3']
        }
    },
    {
        id: 'purchase_of_investments',
        category: 'Cash Flow Statement',
        key: 'purchase_of_investments',
        label: 'Purchase of Investments',
        keywords_indas: [
            'purchase of investments', 'investment in mutual funds',
            'investment in fixed deposits', 'purchase of current investments',
            'investment in non-current investments'
        ],
        keywords_gaap: [
            'purchases of investments', 'purchase of marketable securities',
            'investments in securities'
        ],
        keywords_ifrs: [
            'acquisition of investments', 'purchase of financial assets'
        ]
    },
    {
        id: 'sale_of_investments',
        category: 'Cash Flow Statement',
        key: 'sale_of_investments',
        label: 'Proceeds from Sale of Investments',
        keywords_indas: [
            'sale of investments', 'redemption of investments',
            'proceeds from sale of current investments',
            'maturity of fixed deposits'
        ],
        keywords_gaap: [
            'proceeds from sale of investments', 'maturities of investments',
            'sales of marketable securities'
        ],
        keywords_ifrs: [
            'proceeds from sale of investments', 'disposal of financial assets'
        ]
    },
    {
        id: 'interest_received',
        category: 'Cash Flow Statement',
        key: 'interest_received',
        label: 'Interest Received',
        keywords_indas: [
            'interest received', 'interest income received'
        ],
        keywords_gaap: [
            'interest received'
        ],
        keywords_ifrs: [
            'interest received', 'interest income received'
        ]
    },
    {
        id: 'dividends_received',
        category: 'Cash Flow Statement',
        key: 'dividends_received',
        label: 'Dividends Received',
        keywords_indas: [
            'dividends received', 'dividend income received'
        ],
        keywords_gaap: [
            'dividends received'
        ],
        keywords_ifrs: [
            'dividends received', 'dividend income received'
        ]
    },

    // ===== FINANCING ACTIVITIES =====
    {
        id: 'cash_from_financing',
        category: 'Cash Flow Statement',
        key: 'cash_from_financing',
        label: 'Cash Flow from Financing Activities',
        keywords_indas: [
            'cash flows from financing activities', 'financing activities',
            'net cash from financing activities', 'net cash used in financing activities'
        ],
        keywords_gaap: [
            'net cash provided by financing activities', 'financing cash flow',
            'cash flows from financing activities', 'net cash from financing'
        ],
        keywords_ifrs: [
            'cash flows from financing activities', 'financing activities',
            'net cash used in financing activities'
        ]
    },
    {
        id: 'proceeds_from_borrowings',
        category: 'Cash Flow Statement',
        key: 'proceeds_from_borrowings',
        label: 'Proceeds from Borrowings',
        keywords_indas: [
            'proceeds from borrowings', 'proceeds from long-term borrowings',
            'proceeds from short-term borrowings', 'loans taken',
            'issue of debentures', 'proceeds from term loans'
        ],
        keywords_gaap: [
            'proceeds from issuance of debt', 'proceeds from long-term debt',
            'proceeds from borrowings', 'issuance of notes payable'
        ],
        keywords_ifrs: [
            'proceeds from borrowings', 'proceeds from loans',
            'cash inflows from borrowings'
        ]
    },
    {
        id: 'repayment_of_borrowings',
        category: 'Cash Flow Statement',
        key: 'repayment_of_borrowings',
        label: 'Repayment of Borrowings',
        keywords_indas: [
            'repayment of borrowings', 'repayment of long-term borrowings',
            'repayment of short-term borrowings', 'loan repaid',
            'redemption of debentures', 'prepayment of loans'
        ],
        keywords_gaap: [
            'repayments of debt', 'repayment of long-term debt',
            'payments on long-term debt', 'debt repayments'
        ],
        keywords_ifrs: [
            'repayment of borrowings', 'repayments of loans',
            'cash outflows for borrowings'
        ]
    },
    {
        id: 'lease_payments',
        category: 'Cash Flow Statement',
        key: 'lease_payments',
        label: 'Payment of Lease Liabilities',
        keywords_indas: [
            'payment of lease liabilities', 'lease payments',
            'repayment of lease liabilities', 'finance lease payments'
        ],
        keywords_gaap: [
            'payments on finance lease obligations', 'lease payments',
            'principal payments on operating leases'
        ],
        keywords_ifrs: [
            'payment of lease liabilities', 'lease liability payments',
            'repayment of lease obligations'
        ],
        related_standards: {
            indas: ['IndAS 116'],
            gaap: ['ASC 842'],
            ifrs: ['IFRS 16']
        }
    },
    {
        id: 'proceeds_from_share_issue',
        category: 'Cash Flow Statement',
        key: 'proceeds_from_share_issue',
        label: 'Proceeds from Issue of Shares',
        keywords_indas: [
            'proceeds from issue of equity shares', 'issue of share capital',
            'equity contribution', 'proceeds from share allotment',
            'proceeds from exercise of stock options'
        ],
        keywords_gaap: [
            'proceeds from issuance of common stock', 'issuance of stock',
            'proceeds from stock option exercises'
        ],
        keywords_ifrs: [
            'proceeds from issue of shares', 'issue of share capital',
            'cash received from issue of equity'
        ]
    },
    {
        id: 'buyback_of_shares',
        category: 'Cash Flow Statement',
        key: 'buyback_of_shares',
        label: 'Buyback of Shares',
        keywords_indas: [
            'buyback of shares', 'purchase of treasury shares',
            'share buyback', 'repurchase of shares'
        ],
        keywords_gaap: [
            'repurchases of common stock', 'stock buyback',
            'purchases of treasury stock'
        ],
        keywords_ifrs: [
            'purchase of own shares', 'share buyback',
            'acquisition of treasury shares'
        ]
    },
    {
        id: 'dividends_paid',
        category: 'Cash Flow Statement',
        key: 'dividends_paid',
        label: 'Dividends Paid',
        keywords_indas: [
            'dividends paid', 'dividend paid', 'payment of dividend',
            'dividend distribution', 'interim dividend paid', 'final dividend paid'
        ],
        keywords_gaap: [
            'dividends paid', 'payment of dividends', 'cash dividends paid'
        ],
        keywords_ifrs: [
            'dividends paid', 'dividends paid to equity holders'
        ]
    },
    {
        id: 'interest_paid',
        category: 'Cash Flow Statement',
        key: 'interest_paid',
        label: 'Interest Paid',
        keywords_indas: [
            'interest paid', 'finance cost paid', 'payment of interest'
        ],
        keywords_gaap: [
            'interest paid'
        ],
        keywords_ifrs: [
            'interest paid', 'finance costs paid'
        ]
    },

    // ===== NET CHANGE =====
    {
        id: 'net_change_in_cash',
        category: 'Cash Flow Statement',
        key: 'net_change_in_cash',
        label: 'Net Change in Cash',
        keywords_indas: [
            'net increase in cash', 'net decrease in cash',
            'net change in cash and cash equivalents',
            'net increase decrease in cash'
        ],
        keywords_gaap: [
            'net change in cash', 'net increase decrease in cash',
            'change in cash and cash equivalents', 'increase decrease in cash'
        ],
        keywords_ifrs: [
            'net increase decrease in cash', 'net change in cash',
            'net movement in cash'
        ]
    }
];
