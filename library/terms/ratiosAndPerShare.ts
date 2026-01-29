import { TermMapping } from '../../types/terminology';

export const FINANCIAL_RATIOS_TERMS: TermMapping[] = [
    // ===== LIQUIDITY RATIOS =====
    {
        id: 'current_ratio',
        category: 'Financial Ratios',
        key: 'current_ratio',
        label: 'Current Ratio',
        keywords_indas: [
            'current ratio', 'working capital ratio', 'liquidity ratio'
        ],
        keywords_gaap: [
            'current ratio', 'working capital ratio'
        ],
        keywords_ifrs: [
            'current ratio', 'liquidity ratio'
        ]
    },
    {
        id: 'quick_ratio',
        category: 'Financial Ratios',
        key: 'quick_ratio',
        label: 'Quick Ratio',
        keywords_indas: [
            'quick ratio', 'acid test ratio', 'liquid ratio'
        ],
        keywords_gaap: [
            'quick ratio', 'acid test ratio'
        ],
        keywords_ifrs: [
            'quick ratio', 'acid test ratio'
        ]
    },
    {
        id: 'cash_ratio',
        category: 'Financial Ratios',
        key: 'cash_ratio',
        label: 'Cash Ratio',
        keywords_indas: [
            'cash ratio', 'absolute liquidity ratio'
        ],
        keywords_gaap: [
            'cash ratio'
        ],
        keywords_ifrs: [
            'cash ratio'
        ]
    },

    // ===== PROFITABILITY RATIOS =====
    {
        id: 'gross_profit_margin',
        category: 'Financial Ratios',
        key: 'gross_profit_margin',
        label: 'Gross Profit Margin',
        keywords_indas: [
            'gross profit margin', 'gross margin', 'gpm'
        ],
        keywords_gaap: [
            'gross profit margin', 'gross margin percentage'
        ],
        keywords_ifrs: [
            'gross profit margin', 'gross margin'
        ]
    },
    {
        id: 'operating_profit_margin',
        category: 'Financial Ratios',
        key: 'operating_profit_margin',
        label: 'Operating Profit Margin',
        keywords_indas: [
            'operating profit margin', 'operating margin', 'ebit margin'
        ],
        keywords_gaap: [
            'operating margin', 'operating income margin'
        ],
        keywords_ifrs: [
            'operating profit margin', 'operating margin'
        ]
    },
    {
        id: 'net_profit_margin',
        category: 'Financial Ratios',
        key: 'net_profit_margin',
        label: 'Net Profit Margin',
        keywords_indas: [
            'net profit margin', 'net margin', 'profit margin', 'pat margin'
        ],
        keywords_gaap: [
            'net profit margin', 'net income margin', 'profit margin'
        ],
        keywords_ifrs: [
            'net profit margin', 'net margin'
        ]
    },
    {
        id: 'ebitda_margin',
        category: 'Financial Ratios',
        key: 'ebitda_margin',
        label: 'EBITDA Margin',
        keywords_indas: [
            'ebitda margin'
        ],
        keywords_gaap: [
            'ebitda margin', 'adjusted ebitda margin'
        ],
        keywords_ifrs: [
            'ebitda margin'
        ]
    },
    {
        id: 'return_on_assets',
        category: 'Financial Ratios',
        key: 'return_on_assets',
        label: 'Return on Assets (ROA)',
        keywords_indas: [
            'return on assets', 'roa', 'return on total assets'
        ],
        keywords_gaap: [
            'return on assets', 'roa', 'asset return'
        ],
        keywords_ifrs: [
            'return on assets', 'roa'
        ]
    },
    {
        id: 'return_on_equity',
        category: 'Financial Ratios',
        key: 'return_on_equity',
        label: 'Return on Equity (ROE)',
        keywords_indas: [
            'return on equity', 'roe', 'return on shareholders funds',
            'return on net worth'
        ],
        keywords_gaap: [
            'return on equity', 'roe', 'return on shareholders equity'
        ],
        keywords_ifrs: [
            'return on equity', 'roe'
        ]
    },
    {
        id: 'return_on_capital_employed',
        category: 'Financial Ratios',
        key: 'return_on_capital_employed',
        label: 'Return on Capital Employed (ROCE)',
        keywords_indas: [
            'return on capital employed', 'roce', 'return on invested capital'
        ],
        keywords_gaap: [
            'return on invested capital', 'roic', 'roce'
        ],
        keywords_ifrs: [
            'return on capital employed', 'roce', 'roic'
        ]
    },

    // ===== LEVERAGE RATIOS =====
    {
        id: 'debt_to_equity',
        category: 'Financial Ratios',
        key: 'debt_to_equity',
        label: 'Debt to Equity Ratio',
        keywords_indas: [
            'debt equity ratio', 'debt to equity', 'd/e ratio', 'gearing ratio'
        ],
        keywords_gaap: [
            'debt to equity ratio', 'debt equity ratio', 'leverage ratio'
        ],
        keywords_ifrs: [
            'debt to equity', 'gearing ratio', 'debt equity ratio'
        ]
    },
    {
        id: 'debt_to_assets',
        category: 'Financial Ratios',
        key: 'debt_to_assets',
        label: 'Debt to Assets Ratio',
        keywords_indas: [
            'debt to assets ratio', 'debt ratio'
        ],
        keywords_gaap: [
            'debt to total assets', 'debt ratio'
        ],
        keywords_ifrs: [
            'debt to assets ratio'
        ]
    },
    {
        id: 'interest_coverage_ratio',
        category: 'Financial Ratios',
        key: 'interest_coverage_ratio',
        label: 'Interest Coverage Ratio',
        keywords_indas: [
            'interest coverage ratio', 'times interest earned', 'icr'
        ],
        keywords_gaap: [
            'interest coverage', 'times interest earned ratio'
        ],
        keywords_ifrs: [
            'interest coverage ratio', 'interest cover'
        ]
    },
    {
        id: 'debt_service_coverage_ratio',
        category: 'Financial Ratios',
        key: 'debt_service_coverage_ratio',
        label: 'Debt Service Coverage Ratio',
        keywords_indas: [
            'debt service coverage ratio', 'dscr'
        ],
        keywords_gaap: [
            'debt service coverage ratio', 'dscr'
        ],
        keywords_ifrs: [
            'debt service coverage ratio'
        ]
    },

    // ===== EFFICIENCY RATIOS =====
    {
        id: 'asset_turnover',
        category: 'Financial Ratios',
        key: 'asset_turnover',
        label: 'Asset Turnover Ratio',
        keywords_indas: [
            'asset turnover ratio', 'total asset turnover'
        ],
        keywords_gaap: [
            'asset turnover', 'total asset turnover ratio'
        ],
        keywords_ifrs: [
            'asset turnover ratio'
        ]
    },
    {
        id: 'inventory_turnover',
        category: 'Financial Ratios',
        key: 'inventory_turnover',
        label: 'Inventory Turnover Ratio',
        keywords_indas: [
            'inventory turnover ratio', 'stock turnover'
        ],
        keywords_gaap: [
            'inventory turnover', 'inventory turns'
        ],
        keywords_ifrs: [
            'inventory turnover ratio'
        ]
    },
    {
        id: 'receivables_turnover',
        category: 'Financial Ratios',
        key: 'receivables_turnover',
        label: 'Receivables Turnover Ratio',
        keywords_indas: [
            'receivables turnover ratio', 'debtor turnover'
        ],
        keywords_gaap: [
            'accounts receivable turnover', 'receivable turnover'
        ],
        keywords_ifrs: [
            'trade receivables turnover'
        ]
    },
    {
        id: 'payables_turnover',
        category: 'Financial Ratios',
        key: 'payables_turnover',
        label: 'Payables Turnover Ratio',
        keywords_indas: [
            'payables turnover ratio', 'creditor turnover'
        ],
        keywords_gaap: [
            'accounts payable turnover', 'payable turnover'
        ],
        keywords_ifrs: [
            'trade payables turnover'
        ]
    },
    {
        id: 'working_capital_days',
        category: 'Financial Ratios',
        key: 'working_capital_days',
        label: 'Working Capital Days',
        keywords_indas: [
            'net working capital days', 'cash conversion cycle'
        ],
        keywords_gaap: [
            'cash conversion cycle', 'working capital cycle'
        ],
        keywords_ifrs: [
            'cash conversion cycle', 'working capital days'
        ]
    }
];

export const PER_SHARE_DATA_TERMS: TermMapping[] = [
    {
        id: 'basic_eps',
        category: 'Per Share Data',
        key: 'basic_eps',
        label: 'Basic EPS',
        keywords_indas: [
            'basic earnings per share', 'basic eps', 'earnings per share basic',
            'basic profit per share', 'eps (basic)'
        ],
        keywords_gaap: [
            'basic earnings per share', 'basic eps', 'earnings per share basic',
            'net income per share - basic'
        ],
        keywords_ifrs: [
            'basic earnings per share', 'basic eps'
        ],
        related_standards: {
            indas: ['IndAS 33'],
            gaap: ['ASC 260'],
            ifrs: ['IAS 33']
        }
    },
    {
        id: 'diluted_eps',
        category: 'Per Share Data',
        key: 'diluted_eps',
        label: 'Diluted EPS',
        keywords_indas: [
            'diluted earnings per share', 'diluted eps', 'earnings per share diluted',
            'eps (diluted)'
        ],
        keywords_gaap: [
            'diluted earnings per share', 'diluted eps', 'earnings per share diluted',
            'net income per share - diluted'
        ],
        keywords_ifrs: [
            'diluted earnings per share', 'diluted eps'
        ],
        related_standards: {
            indas: ['IndAS 33'],
            gaap: ['ASC 260'],
            ifrs: ['IAS 33']
        }
    },
    {
        id: 'book_value_per_share',
        category: 'Per Share Data',
        key: 'book_value_per_share',
        label: 'Book Value Per Share',
        keywords_indas: [
            'book value per share', 'net asset value per share', 'nav per share'
        ],
        keywords_gaap: [
            'book value per share', 'tangible book value per share'
        ],
        keywords_ifrs: [
            'book value per share', 'net asset value per share'
        ]
    },
    {
        id: 'dividend_per_share',
        category: 'Per Share Data',
        key: 'dividend_per_share',
        label: 'Dividend Per Share',
        keywords_indas: [
            'dividend per share', 'dps', 'dividend per equity share',
            'dividends declared per share', 'cash dividends per share'
        ],
        keywords_gaap: [
            'dividends per share', 'dividend per share', 'dps',
            'dividends and dividend equivalents declared per share or rsu',
            'dividends and dividend equivalents declared', 'dividend declared per share',
            'cash dividends declared per common share'
        ],
        keywords_ifrs: [
            'dividend per share', 'dps', 'dividends declared per share'
        ]
    },
    {
        id: 'face_value',
        category: 'Per Share Data',
        key: 'face_value',
        label: 'Face Value per Share',
        keywords_indas: [
            'face value', 'face value per share', 'nominal value', 'par value'
        ],
        keywords_gaap: [
            'par value', 'par value per share', 'stated value'
        ],
        keywords_ifrs: [
            'nominal value', 'par value', 'face value'
        ]
    },
    {
        id: 'shares_outstanding',
        category: 'Per Share Data',
        key: 'shares_outstanding',
        label: 'Shares Outstanding',
        keywords_indas: [
            'number of shares outstanding', 'shares outstanding',
            'weighted average number of shares', 'equity shares outstanding'
        ],
        keywords_gaap: [
            'shares outstanding', 'common shares outstanding',
            'weighted average shares outstanding',
            'shares used in computing basic earnings per share',
            'shares used in computing diluted earnings per share'
        ],
        keywords_ifrs: [
            'ordinary shares outstanding', 'shares in issue',
            'weighted average number of ordinary shares'
        ]
    }
];
