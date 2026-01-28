import { TermMapping } from '../../types/terminology';

export const BALANCE_SHEET_ASSETS_TERMS: TermMapping[] = [
    // ===== NON-CURRENT ASSETS =====
    {
        id: 'total_non_current_assets',
        category: 'Balance Sheet - Assets',
        key: 'total_non_current_assets',
        label: 'Total Non-Current Assets',
        keywords_indas: [
            'total non-current assets', 'non-current assets', 'fixed assets total',
            'long-term assets', 'capital assets'
        ],
        keywords_gaap: [
            'total non-current assets', 'total long-term assets', 'non-current assets',
            'property and equipment total', 'total fixed assets'
        ],
        keywords_ifrs: [
            'total non-current assets', 'non-current assets total',
            'long-term assets'
        ]
    },
    {
        id: 'property_plant_equipment',
        category: 'Balance Sheet - Assets',
        key: 'property_plant_equipment',
        label: 'Property, Plant and Equipment',
        keywords_indas: [
            'property plant and equipment', 'ppe', 'fixed assets',
            'tangible assets', 'land and buildings', 'plant and machinery',
            'furniture and fixtures', 'vehicles', 'office equipment',
            'capital work in progress', 'cwip', 'assets under construction',
            'leasehold improvements', 'factory building', 'computers'
        ],
        keywords_gaap: [
            'property plant and equipment', 'ppe', 'pp&e', 'fixed assets',
            'land and building', 'machinery and equipment',
            'construction in progress', 'cip', 'leasehold improvements',
            'furniture and equipment', 'property and equipment net'
        ],
        keywords_ifrs: [
            'property plant and equipment', 'ppe', 'tangible fixed assets',
            'land and buildings', 'plant and equipment',
            'assets under construction', 'capital work in progress'
        ],
        related_standards: {
            indas: ['IndAS 16'],
            gaap: ['ASC 360'],
            ifrs: ['IAS 16']
        }
    },
    {
        id: 'land_and_buildings',
        category: 'Balance Sheet - Assets',
        key: 'land_and_buildings',
        label: 'Land and Buildings',
        keywords_indas: [
            'land', 'buildings', 'land and buildings', 'freehold land',
            'leasehold land', 'freehold buildings', 'leasehold buildings'
        ],
        keywords_gaap: [
            'land', 'buildings', 'land and building', 'real estate'
        ],
        keywords_ifrs: [
            'land', 'buildings', 'land and buildings'
        ]
    },
    {
        id: 'plant_and_machinery',
        category: 'Balance Sheet - Assets',
        key: 'plant_and_machinery',
        label: 'Plant and Machinery',
        keywords_indas: [
            'plant and machinery', 'plant and equipment', 'manufacturing equipment',
            'production equipment'
        ],
        keywords_gaap: [
            'machinery and equipment', 'plant and machinery',
            'manufacturing equipment'
        ],
        keywords_ifrs: [
            'plant and machinery', 'plant and equipment'
        ]
    },
    {
        id: 'capital_work_in_progress',
        category: 'Balance Sheet - Assets',
        key: 'capital_work_in_progress',
        label: 'Capital Work in Progress',
        keywords_indas: [
            'capital work in progress', 'cwip', 'capital work-in-progress',
            'assets under construction', 'construction in progress'
        ],
        keywords_gaap: [
            'construction in progress', 'cip', 'assets under construction'
        ],
        keywords_ifrs: [
            'assets under construction', 'capital work in progress'
        ]
    },
    {
        id: 'investment_property',
        category: 'Balance Sheet - Assets',
        key: 'investment_property',
        label: 'Investment Property',
        keywords_indas: [
            'investment property', 'investment properties',
            'properties held for investment', 'rental properties'
        ],
        keywords_gaap: [
            'investment property', 'real estate held for investment',
            'rental property'
        ],
        keywords_ifrs: [
            'investment property', 'investment properties'
        ],
        related_standards: {
            indas: ['IndAS 40'],
            gaap: ['ASC 970'],
            ifrs: ['IAS 40']
        }
    },
    {
        id: 'intangible_assets',
        category: 'Balance Sheet - Assets',
        key: 'intangible_assets',
        label: 'Intangible Assets',
        keywords_indas: [
            'intangible assets', 'goodwill', 'software', 'patents',
            'trademarks', 'copyrights', 'licenses', 'brand value',
            'customer relationships', 'technical know-how', 'franchise',
            'computer software', 'development costs', 'mining rights',
            'intangible assets under development', 'non-compete agreements'
        ],
        keywords_gaap: [
            'intangible assets', 'intangibles', 'goodwill', 'software',
            'patents', 'trademarks', 'copyrights', 'licenses',
            'customer relationships', 'trade names', 'technology',
            'capitalized software', 'acquired intangibles',
            'indefinite-lived intangibles', 'finite-lived intangibles'
        ],
        keywords_ifrs: [
            'intangible assets', 'goodwill', 'software', 'patents',
            'trademarks', 'licences', 'customer relationships',
            'development costs', 'brands', 'intellectual property'
        ],
        related_standards: {
            indas: ['IndAS 38'],
            gaap: ['ASC 350'],
            ifrs: ['IAS 38']
        }
    },
    {
        id: 'goodwill',
        category: 'Balance Sheet - Assets',
        key: 'goodwill',
        label: 'Goodwill',
        keywords_indas: [
            'goodwill', 'goodwill on consolidation', 'goodwill arising on acquisition'
        ],
        keywords_gaap: [
            'goodwill', 'acquired goodwill', 'goodwill net'
        ],
        keywords_ifrs: [
            'goodwill', 'goodwill arising on business combination'
        ],
        related_standards: {
            indas: ['IndAS 103', 'IndAS 36'],
            gaap: ['ASC 350', 'ASC 805'],
            ifrs: ['IAS 36', 'IFRS 3']
        }
    },
    {
        id: 'right_of_use_assets',
        category: 'Balance Sheet - Assets',
        key: 'right_of_use_assets',
        label: 'Right-of-Use Assets',
        keywords_indas: [
            'right of use assets', 'right-of-use assets', 'rou assets',
            'leased assets', 'lease assets', 'operating lease right of use'
        ],
        keywords_gaap: [
            'right of use assets', 'rou assets', 'operating lease rou assets',
            'finance lease rou assets', 'lease right of use'
        ],
        keywords_ifrs: [
            'right-of-use assets', 'rou assets', 'leased assets'
        ],
        related_standards: {
            indas: ['IndAS 116'],
            gaap: ['ASC 842'],
            ifrs: ['IFRS 16']
        }
    },
    {
        id: 'biological_assets',
        category: 'Balance Sheet - Assets',
        key: 'biological_assets',
        label: 'Biological Assets',
        keywords_indas: [
            'biological assets', 'bearer plants', 'livestock',
            'agricultural produce', 'growing crops'
        ],
        keywords_gaap: [
            'biological assets', 'livestock', 'timber', 'agricultural assets'
        ],
        keywords_ifrs: [
            'biological assets', 'bearer plants', 'agricultural assets'
        ],
        related_standards: {
            indas: ['IndAS 41'],
            gaap: ['ASC 905'],
            ifrs: ['IAS 41']
        }
    },

    // ===== FINANCIAL ASSETS - NON-CURRENT =====
    {
        id: 'investments_in_subsidiaries',
        category: 'Balance Sheet - Assets',
        key: 'investments_in_subsidiaries',
        label: 'Investments in Subsidiaries',
        keywords_indas: [
            'investments in subsidiaries', 'investment in subsidiary companies',
            'equity investments in subsidiaries'
        ],
        keywords_gaap: [
            'investment in subsidiaries', 'investments in affiliates',
            'equity method investments'
        ],
        keywords_ifrs: [
            'investments in subsidiaries', 'investments in subsidiary undertakings'
        ],
        related_standards: {
            indas: ['IndAS 27', 'IndAS 110'],
            gaap: ['ASC 810'],
            ifrs: ['IAS 27', 'IFRS 10']
        }
    },
    {
        id: 'investments_in_associates',
        category: 'Balance Sheet - Assets',
        key: 'investments_in_associates',
        label: 'Investments in Associates',
        keywords_indas: [
            'investments in associates', 'investment in associate companies',
            'investment in joint ventures', 'equity method investments'
        ],
        keywords_gaap: [
            'equity method investments', 'investments in affiliates',
            'investment in associates and joint ventures'
        ],
        keywords_ifrs: [
            'investments in associates', 'investments in joint ventures',
            'equity accounted investments'
        ],
        related_standards: {
            indas: ['IndAS 28'],
            gaap: ['ASC 323'],
            ifrs: ['IAS 28']
        }
    },
    {
        id: 'financial_assets_fvtoci',
        category: 'Balance Sheet - Assets',
        key: 'financial_assets_fvtoci',
        label: 'Financial Assets at FVTOCI',
        keywords_indas: [
            'investments at fair value through oci', 'fvtoci investments',
            'equity instruments at fvtoci', 'debt instruments at fvtoci',
            'available for sale investments'
        ],
        keywords_gaap: [
            'available for sale securities', 'afs securities',
            'equity securities at fv-oci'
        ],
        keywords_ifrs: [
            'financial assets at fvtoci', 'fvtoci investments',
            'fair value through other comprehensive income investments'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 320'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'financial_assets_fvtpl',
        category: 'Balance Sheet - Assets',
        key: 'financial_assets_fvtpl',
        label: 'Financial Assets at FVTPL',
        keywords_indas: [
            'investments at fair value through profit or loss', 'fvtpl investments',
            'trading investments', 'financial assets held for trading',
            'derivatives assets'
        ],
        keywords_gaap: [
            'trading securities', 'securities at fair value',
            'derivative assets', 'fv investments'
        ],
        keywords_ifrs: [
            'financial assets at fvtpl', 'fvtpl investments',
            'trading financial assets', 'derivative financial assets'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 320'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'financial_assets_amortized_cost',
        category: 'Balance Sheet - Assets',
        key: 'financial_assets_amortized_cost',
        label: 'Financial Assets at Amortized Cost',
        keywords_indas: [
            'investments at amortised cost', 'amortized cost investments',
            'held to maturity investments', 'debt securities at amortised cost'
        ],
        keywords_gaap: [
            'held to maturity securities', 'htm investments',
            'debt securities at amortized cost'
        ],
        keywords_ifrs: [
            'financial assets at amortised cost', 'debt instruments at amortised cost'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 320'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'long_term_loans',
        category: 'Balance Sheet - Assets',
        key: 'long_term_loans',
        label: 'Long-term Loans and Advances',
        keywords_indas: [
            'loans', 'long-term loans', 'loans to related parties',
            'loans to employees', 'inter-corporate deposits',
            'security deposits', 'advances recoverable'
        ],
        keywords_gaap: [
            'long-term loans receivable', 'notes receivable long-term',
            'loans to affiliates'
        ],
        keywords_ifrs: [
            'loans and receivables', 'long-term loans', 'loans to related parties'
        ]
    },
    {
        id: 'deferred_tax_assets',
        category: 'Balance Sheet - Assets',
        key: 'deferred_tax_assets',
        label: 'Deferred Tax Assets',
        keywords_indas: [
            'deferred tax assets', 'deferred tax asset', 'dta',
            'mat credit entitlement', 'deferred income tax assets'
        ],
        keywords_gaap: [
            'deferred tax assets', 'deferred income tax assets', 'dta',
            'deferred tax asset net'
        ],
        keywords_ifrs: [
            'deferred tax assets', 'deferred income tax assets'
        ],
        related_standards: {
            indas: ['IndAS 12'],
            gaap: ['ASC 740'],
            ifrs: ['IAS 12']
        }
    },
    {
        id: 'other_non_current_assets',
        category: 'Balance Sheet - Assets',
        key: 'other_non_current_assets',
        label: 'Other Non-Current Assets',
        keywords_indas: [
            'other non-current assets', 'long-term deposits',
            'capital advances', 'prepaid expenses non-current',
            'advances for capital goods', 'balance with government authorities'
        ],
        keywords_gaap: [
            'other non-current assets', 'other long-term assets',
            'long-term prepaid expenses'
        ],
        keywords_ifrs: [
            'other non-current assets', 'other long-term assets'
        ]
    },

    // ===== CURRENT ASSETS =====
    {
        id: 'total_current_assets',
        category: 'Balance Sheet - Assets',
        key: 'total_current_assets',
        label: 'Total Current Assets',
        keywords_indas: [
            'total current assets', 'current assets', 'current assets total'
        ],
        keywords_gaap: [
            'total current assets', 'current assets total'
        ],
        keywords_ifrs: [
            'total current assets', 'current assets'
        ]
    },
    {
        id: 'inventories',
        category: 'Balance Sheet - Assets',
        key: 'inventories',
        label: 'Inventories',
        keywords_indas: [
            'inventories', 'inventory', 'stock in trade', 'raw materials',
            'work in progress', 'wip', 'finished goods', 'stores and spares',
            'packing materials', 'goods in transit', 'stock', 'merchandise'
        ],
        keywords_gaap: [
            'inventories', 'inventory', 'merchandise inventory',
            'raw materials inventory', 'work in process', 'finished goods inventory',
            'supplies inventory', 'goods in transit'
        ],
        keywords_ifrs: [
            'inventories', 'inventory', 'raw materials and consumables',
            'work in progress', 'finished goods', 'goods for resale'
        ],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    {
        id: 'trade_receivables',
        category: 'Balance Sheet - Assets',
        key: 'trade_receivables',
        label: 'Trade Receivables',
        keywords_indas: [
            'trade receivables', 'sundry debtors', 'accounts receivable',
            'receivables from customers', 'receivable for goods sold',
            'trade and other receivables', 'bills receivable',
            'receivables', 'debtors', 'amounts due from customers'
        ],
        keywords_gaap: [
            'accounts receivable', 'trade receivables', 'receivables net',
            'trade accounts receivable', 'customer receivables',
            'accounts receivable net of allowance', 'net receivables'
        ],
        keywords_ifrs: [
            'trade receivables', 'trade and other receivables',
            'accounts receivable', 'receivables from contracts with customers'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 310'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'allowance_for_doubtful_debts',
        category: 'Balance Sheet - Assets',
        key: 'allowance_for_doubtful_debts',
        label: 'Allowance for Doubtful Debts',
        keywords_indas: [
            'provision for doubtful debts', 'allowance for doubtful debts',
            'expected credit loss', 'ecl provision', 'impairment allowance',
            'provision for expected credit losses'
        ],
        keywords_gaap: [
            'allowance for doubtful accounts', 'allowance for credit losses',
            'bad debt reserve', 'accounts receivable allowance'
        ],
        keywords_ifrs: [
            'expected credit loss allowance', 'impairment allowance',
            'provision for impairment of receivables'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 326'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'contract_assets',
        category: 'Balance Sheet - Assets',
        key: 'contract_assets',
        label: 'Contract Assets',
        keywords_indas: [
            'contract assets', 'unbilled revenue', 'accrued income',
            'unbilled receivables', 'revenue accruals'
        ],
        keywords_gaap: [
            'contract assets', 'unbilled receivables', 'unbilled revenue',
            'accrued revenue'
        ],
        keywords_ifrs: [
            'contract assets', 'accrued income', 'unbilled revenue'
        ],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 606'],
            ifrs: ['IFRS 15']
        }
    },
    {
        id: 'cash_and_equivalents',
        category: 'Balance Sheet - Assets',
        key: 'cash_and_equivalents',
        label: 'Cash and Cash Equivalents',
        keywords_indas: [
            'cash and cash equivalents', 'cash and bank balances',
            'bank balances', 'cash on hand', 'cash in hand',
            'balances with banks', 'deposits with banks',
            'cash equivalents', 'short-term deposits', 'current investments',
            'fixed deposits', 'term deposits', 'liquid investments'
        ],
        keywords_gaap: [
            'cash and cash equivalents', 'cash', 'cash equivalents',
            'cash and short-term investments', 'cash on hand and in banks',
            'restricted cash', 'bank balances', 'money market funds'
        ],
        keywords_ifrs: [
            'cash and cash equivalents', 'cash and bank balances',
            'cash at bank and on hand', 'short-term deposits', 'cash'
        ],
        related_standards: {
            indas: ['IndAS 7'],
            gaap: ['ASC 230'],
            ifrs: ['IAS 7']
        }
    },
    {
        id: 'bank_balances_other',
        category: 'Balance Sheet - Assets',
        key: 'bank_balances_other',
        label: 'Bank Balances (Other)',
        keywords_indas: [
            'bank balances other than cash and cash equivalents',
            'unpaid dividend account', 'margin money deposits',
            'restricted bank balances', 'earmarked balances'
        ],
        keywords_gaap: [
            'restricted cash', 'other bank balances', 'cash held for specific purposes'
        ],
        keywords_ifrs: [
            'bank balances other than cash equivalents', 'restricted cash'
        ]
    },
    {
        id: 'short_term_investments',
        category: 'Balance Sheet - Assets',
        key: 'short_term_investments',
        label: 'Short-term Investments',
        keywords_indas: [
            'current investments', 'short-term investments',
            'investments in mutual funds', 'liquid mutual funds',
            'treasury bills', 'commercial paper investments'
        ],
        keywords_gaap: [
            'short-term investments', 'marketable securities',
            'trading securities', 'temporary investments'
        ],
        keywords_ifrs: [
            'current financial assets', 'short-term investments',
            'current investments'
        ]
    },
    {
        id: 'other_financial_assets_current',
        category: 'Balance Sheet - Assets',
        key: 'other_financial_assets_current',
        label: 'Other Financial Assets (Current)',
        keywords_indas: [
            'other financial assets', 'advances to suppliers',
            'interest accrued', 'claims receivable', 'derivatives',
            'security deposits', 'loans to employees'
        ],
        keywords_gaap: [
            'other current financial assets', 'derivative assets current',
            'interest receivable'
        ],
        keywords_ifrs: [
            'other current financial assets', 'derivative financial assets current'
        ]
    },
    {
        id: 'prepaid_expenses',
        category: 'Balance Sheet - Assets',
        key: 'prepaid_expenses',
        label: 'Prepaid Expenses',
        keywords_indas: [
            'prepaid expenses', 'prepayments', 'advance payments',
            'prepaid insurance', 'prepaid rent'
        ],
        keywords_gaap: [
            'prepaid expenses', 'prepaid assets', 'prepayments'
        ],
        keywords_ifrs: [
            'prepayments', 'prepaid expenses'
        ]
    },
    {
        id: 'other_current_assets',
        category: 'Balance Sheet - Assets',
        key: 'other_current_assets',
        label: 'Other Current Assets',
        keywords_indas: [
            'other current assets', 'advances other than capital advances',
            'balance with government authorities', 'gst input credit',
            'advance tax', 'tax refund receivable', 'export incentives receivable',
            'prepaid expenses', 'other advances'
        ],
        keywords_gaap: [
            'other current assets', 'prepaid expenses and other current assets',
            'income tax receivable', 'other receivables'
        ],
        keywords_ifrs: [
            'other current assets', 'tax receivable', 'other receivables'
        ]
    },
    {
        id: 'assets_held_for_sale',
        category: 'Balance Sheet - Assets',
        key: 'assets_held_for_sale',
        label: 'Assets Held for Sale',
        keywords_indas: [
            'assets held for sale', 'non-current assets held for sale',
            'disposal group held for sale'
        ],
        keywords_gaap: [
            'assets held for sale', 'discontinued operations assets',
            'assets of disposal group'
        ],
        keywords_ifrs: [
            'non-current assets held for sale', 'assets classified as held for sale',
            'disposal group'
        ],
        related_standards: {
            indas: ['IndAS 105'],
            gaap: ['ASC 360'],
            ifrs: ['IFRS 5']
        }
    },
    {
        id: 'total_assets',
        category: 'Balance Sheet - Assets',
        key: 'total_assets',
        label: 'Total Assets',
        keywords_indas: [
            'total assets', 'assets total', 'gross assets'
        ],
        keywords_gaap: [
            'total assets', 'assets total', 'total assets end of year'
        ],
        keywords_ifrs: [
            'total assets', 'assets total'
        ]
    }
];
