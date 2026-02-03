import { TermMapping } from '../../types/terminology';

export const INCOME_STATEMENT_TERMS: TermMapping[] = [
    // ===== REVENUE SECTION =====
    {
        id: 'total_revenue',
        category: 'Income Statement',
        key: 'total_revenue',
        label: 'Total Revenue',
        description: 'Total income from operations',
        keywords_indas: [
            'revenue from operations', 'total revenue', 'revenue', 'turnover',
            'gross revenue', 'operating revenue', 'income from operations',
            'sales revenue', 'revenue from contracts with customers',
            'sale of products', 'sale of services', 'other operating revenue'
        ],
        keywords_gaap: [
            'total revenue', 'revenues', 'net revenue', 'net revenues',
            'total net revenue', 'gross revenue', 'operating revenues',
            'net sales', 'total net sales', 'revenue from contracts',
            'product revenue', 'service revenue', 'subscription revenue'
        ],
        keywords_ifrs: [
            'revenue', 'total revenue', 'revenue from contracts with customers',
            'operating revenue', 'turnover', 'gross revenue',
            'sale of goods', 'rendering of services', 'contract revenue',
            'revenue from ordinary activities'
        ],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 606'],
            ifrs: ['IFRS 15']
        }
    },
    {
        id: 'net_sales',
        category: 'Income Statement',
        key: 'net_sales',
        label: 'Net Sales',
        keywords_indas: [
            'net sales', 'sale of products', 'sale of goods',
            'revenue from sale of products', 'net revenue from operations'
        ],
        keywords_gaap: [
            'net sales', 'net product sales', 'product sales net',
            'net revenues from sales'
        ],
        keywords_ifrs: [
            'net sales', 'revenue from sale of goods', 'product revenue net'
        ]
    },
    {
        id: 'service_revenue',
        category: 'Income Statement',
        key: 'service_revenue',
        label: 'Service Revenue',
        keywords_indas: [
            'sale of services', 'service revenue', 'revenue from services',
            'income from services', 'rendering of services'
        ],
        keywords_gaap: [
            'service revenue', 'services revenue', 'revenue from services',
            'professional services revenue', 'consulting revenue'
        ],
        keywords_ifrs: [
            'revenue from rendering of services', 'service revenue',
            'services income', 'contract service revenue'
        ]
    },
    {
        id: 'other_operating_income',
        category: 'Income Statement',
        key: 'other_operating_income',
        label: 'Other Operating Income',
        keywords_indas: [
            'other operating revenue', 'other operating income',
            'other income', 'miscellaneous income', 'sundry income',
            'export incentives', 'government grants', 'scrap sales'
        ],
        keywords_gaap: [
            'other operating income', 'other revenues', 'other income',
            'miscellaneous income', 'sundry income'
        ],
        keywords_ifrs: [
            'other operating income', 'other income', 'other revenue',
            'miscellaneous operating income'
        ]
    },

    // ===== COST OF SALES SECTION =====
    {
        id: 'cost_of_goods_sold',
        category: 'Income Statement',
        key: 'cost_of_goods_sold',
        label: 'Cost of Goods Sold',
        keywords_indas: [
            'cost of materials consumed', 'cost of goods sold', 'cost of sales',
            'purchases of stock-in-trade', 'changes in inventories',
            'raw materials consumed', 'cost of revenue', 'direct costs',
            'cost of goods manufactured', 'manufacturing cost',
            'opening stock', 'closing stock', 'inventory adjustment'
        ],
        keywords_gaap: [
            'cost of goods sold', 'cost of sales', 'cost of revenue',
            'cost of products sold', 'cost of services',
            'cost of net revenue', 'cost of goods manufactured', 'cogs',
            'cost of merchandise sold', 'product costs'
        ],
        keywords_ifrs: [
            'cost of sales', 'cost of goods sold', 'cost of revenue',
            'raw materials and consumables used', 'changes in inventories',
            'cost of goods manufactured and sold'
        ],
        related_standards: {
            indas: ['IndAS 2'],
            gaap: ['ASC 330'],
            ifrs: ['IAS 2']
        }
    },
    {
        id: 'cost_of_materials',
        category: 'Income Statement',
        key: 'cost_of_materials',
        label: 'Cost of Materials Consumed',
        keywords_indas: [
            'cost of materials consumed', 'raw materials consumed',
            'materials consumed', 'consumption of raw materials',
            'raw material cost', 'direct material cost'
        ],
        keywords_gaap: [
            'raw materials cost', 'materials consumed', 'direct materials'
        ],
        keywords_ifrs: [
            'raw materials and consumables used', 'cost of raw materials',
            'materials consumed'
        ]
    },
    {
        id: 'purchases_stock_in_trade',
        category: 'Income Statement',
        key: 'purchases_stock_in_trade',
        label: 'Purchases of Stock-in-Trade',
        keywords_indas: [
            'purchases of stock-in-trade', 'purchase of traded goods',
            'cost of traded goods', 'purchases for resale'
        ],
        keywords_gaap: [
            'merchandise purchases', 'purchases of goods for resale'
        ],
        keywords_ifrs: [
            'purchases of goods for resale', 'merchandise cost'
        ]
    },
    {
        id: 'changes_in_inventory',
        category: 'Income Statement',
        key: 'changes_in_inventory',
        label: 'Changes in Inventories',
        keywords_indas: [
            'changes in inventories of finished goods',
            'changes in inventories of work-in-progress',
            'changes in inventories', 'inventory changes',
            'increase in inventories', 'decrease in inventories',
            'stock adjustment'
        ],
        keywords_gaap: [
            'change in inventory', 'inventory change', 'inventory adjustment'
        ],
        keywords_ifrs: [
            'changes in inventories of finished goods and work in progress',
            'inventory movement'
        ]
    },

    // ===== GROSS PROFIT SECTION =====
    {
        id: 'gross_profit',
        category: 'Income Statement',
        key: 'gross_profit',
        label: 'Gross Profit',
        keywords_indas: [
            'gross profit', 'gross margin', 'gross income',
            'trading profit', 'gross surplus'
        ],
        keywords_gaap: [
            'gross profit', 'gross margin', 'gross income',
            'gross profit on sales'
        ],
        keywords_ifrs: [
            'gross profit', 'gross margin', 'gross result'
        ]
    },

    // ===== OPERATING EXPENSES SECTION =====
    {
        id: 'employee_benefits_expense',
        category: 'Income Statement',
        key: 'employee_benefits_expense',
        label: 'Employee Benefits Expense',
        keywords_indas: [
            'employee benefit expense', 'employee benefits expense',
            'employee cost', 'staff cost', 'personnel expenses',
            'salaries and wages', 'salary expense', 'wages',
            'contribution to provident fund', 'contribution to pension fund',
            'gratuity expense', 'leave encashment', 'bonus',
            'staff welfare expenses', 'esop expense', 'share based payments'
        ],
        keywords_gaap: [
            'employee compensation', 'salaries and wages expense',
            'compensation and benefits', 'personnel costs',
            'payroll expense', 'employee related costs',
            'stock compensation expense', 'stock-based compensation',
            '401k expense', 'pension expense', 'retirement benefit costs'
        ],
        keywords_ifrs: [
            'employee benefits expense', 'employee costs',
            'staff costs', 'personnel expenses', 'wages and salaries',
            'post-employment benefits', 'share-based payment expense',
            'defined benefit expense', 'defined contribution expense'
        ],
        related_standards: {
            indas: ['IndAS 19'],
            gaap: ['ASC 715'],
            ifrs: ['IAS 19']
        }
    },
    {
        id: 'depreciation_amortization',
        category: 'Income Statement',
        key: 'depreciation_amortization',
        label: 'Depreciation and Amortization',
        keywords_indas: [
            'depreciation and amortisation expense', 'depreciation and amortization',
            'depreciation expense', 'amortisation expense', 'amortization',
            'depreciation on property plant and equipment',
            'amortisation of intangible assets', 'depletion expense'
        ],
        keywords_gaap: [
            'depreciation and amortization', 'depreciation expense',
            'amortization expense', 'd&a', 'depreciation amortization',
            'amortization of intangibles', 'accumulated depreciation charge'
        ],
        keywords_ifrs: [
            'depreciation and amortisation', 'depreciation expense',
            'amortisation expense', 'depreciation of property plant equipment',
            'amortisation of intangible assets', 'impairment and depreciation'
        ],
        related_standards: {
            indas: ['IndAS 16', 'IndAS 38'],
            gaap: ['ASC 350', 'ASC 360'],
            ifrs: ['IAS 16', 'IAS 38']
        }
    },
    {
        id: 'other_expenses',
        category: 'Income Statement',
        key: 'other_expenses',
        label: 'Other Expenses',
        keywords_indas: [
            'other expenses', 'other operating expenses', 'administrative expenses',
            'rent expense', 'rates and taxes', 'insurance expense',
            'repairs and maintenance', 'legal and professional fees',
            'travelling and conveyance', 'communication expenses',
            'printing and stationery', 'electricity charges', 'power and fuel',
            'advertisement expense', 'selling and distribution expenses',
            'commission expense', 'freight outward', 'bank charges',
            'loss on sale of assets', 'bad debts written off',
            'provision for doubtful debts', 'foreign exchange loss',
            'corporate social responsibility expense', 'csr expenditure'
        ],
        keywords_gaap: [
            'other operating expenses', 'selling general and administrative',
            'sg&a', 'sga expense', 'operating expenses', 'general expenses',
            'administrative expenses', 'other expenses', 'miscellaneous expenses'
        ],
        keywords_ifrs: [
            'other expenses', 'administrative expenses', 'distribution costs',
            'selling and distribution expenses', 'other operating expenses'
        ]
    },
    {
        id: 'research_development',
        category: 'Income Statement',
        key: 'research_development',
        label: 'Research and Development',
        keywords_indas: [
            'research and development expense', 'r&d expense', 'r&d costs',
            'product development costs', 'technology development'
        ],
        keywords_gaap: [
            'research and development', 'r&d expense', 'research and development costs',
            'product development expense', 'technology development costs'
        ],
        keywords_ifrs: [
            'research and development expenditure', 'r&d costs',
            'development costs expensed', 'research costs'
        ],
        related_standards: {
            indas: ['IndAS 38'],
            gaap: ['ASC 730'],
            ifrs: ['IAS 38']
        }
    },
    {
        id: 'selling_distribution_expense',
        category: 'Income Statement',
        key: 'selling_distribution_expense',
        label: 'Selling and Distribution Expense',
        keywords_indas: [
            'selling and distribution expenses', 'selling expenses',
            'distribution costs', 'marketing expenses', 'advertisement',
            'sales promotion', 'freight outward', 'commission on sales'
        ],
        keywords_gaap: [
            'selling expenses', 'marketing expense', 'advertising expense',
            'distribution costs', 'promotional expenses'
        ],
        keywords_ifrs: [
            'distribution costs', 'selling expenses', 'marketing costs',
            'selling and distribution costs'
        ]
    },
    {
        id: 'admin_expenses',
        category: 'Income Statement',
        key: 'admin_expenses',
        label: 'Administrative Expenses',
        keywords_indas: [
            'administrative expenses', 'general and administrative expenses',
            'office expenses', 'management expenses'
        ],
        keywords_gaap: [
            'general and administrative expenses', 'g&a', 'administrative costs',
            'corporate expenses', 'overhead expenses'
        ],
        keywords_ifrs: [
            'administrative expenses', 'general and administrative expenses',
            'corporate overhead'
        ]
    },

    // ===== OPERATING PROFIT SECTION =====
    {
        id: 'ebitda',
        category: 'Income Statement',
        key: 'ebitda',
        label: 'EBITDA',
        keywords_indas: [
            'ebitda', 'earnings before interest tax depreciation amortization',
            'operating profit before depreciation', 'profit before interest depreciation and tax'
        ],
        keywords_gaap: [
            'ebitda', 'adjusted ebitda', 'operating ebitda',
            'earnings before interest taxes depreciation amortization'
        ],
        keywords_ifrs: [
            'ebitda', 'operating profit before depreciation and amortisation'
        ]
    },
    {
        id: 'operating_profit',
        category: 'Income Statement',
        key: 'operating_profit',
        label: 'Operating Profit / EBIT',
        keywords_indas: [
            'profit from operations', 'operating profit', 'ebit',
            'earnings before interest and tax', 'profit before finance costs',
            'operating income', 'income from operations'
        ],
        keywords_gaap: [
            'operating income', 'operating profit', 'ebit', 'income from operations',
            'operating earnings', 'earnings before interest and taxes'
        ],
        keywords_ifrs: [
            'operating profit', 'operating result', 'profit from operations',
            'ebit', 'operating income'
        ]
    },

    // ===== FINANCE COSTS SECTION =====
    {
        id: 'finance_costs',
        category: 'Income Statement',
        key: 'finance_costs',
        label: 'Finance Costs',
        keywords_indas: [
            'finance costs', 'finance cost', 'interest expense',
            'interest on borrowings', 'interest on term loans',
            'interest on working capital', 'bank charges',
            'other borrowing costs', 'unwinding of discount',
            'interest on lease liabilities'
        ],
        keywords_gaap: [
            'interest expense', 'interest cost', 'finance charges',
            'interest on debt', 'debt service cost', 'interest and other expense',
            'interest expense net'
        ],
        keywords_ifrs: [
            'finance costs', 'finance expenses', 'interest expense',
            'borrowing costs', 'interest on borrowings',
            'interest on lease liabilities', 'unwinding of discount on provisions'
        ],
        related_standards: {
            indas: ['IndAS 23'],
            gaap: ['ASC 835'],
            ifrs: ['IAS 23']
        }
    },
    {
        id: 'finance_income',
        category: 'Income Statement',
        key: 'finance_income',
        label: 'Finance Income',
        keywords_indas: [
            'finance income', 'interest income', 'income from investments',
            'dividend income', 'income from financial assets',
            'interest on fixed deposits', 'interest on loans',
            'fair value gains on financial instruments'
        ],
        keywords_gaap: [
            'interest income', 'investment income', 'finance income',
            'interest and other income', 'dividend income',
            'gains on investments'
        ],
        keywords_ifrs: [
            'finance income', 'interest income', 'investment income',
            'income from financial assets', 'dividend income'
        ]
    },
    {
        id: 'net_finance_costs',
        category: 'Income Statement',
        key: 'net_finance_costs',
        label: 'Net Finance Costs',
        keywords_indas: [
            'net finance costs', 'finance costs net', 'net interest expense'
        ],
        keywords_gaap: [
            'net interest expense', 'interest expense net of income'
        ],
        keywords_ifrs: [
            'net finance costs', 'net finance expense', 'finance costs net'
        ]
    },

    // ===== PROFIT BEFORE TAX SECTION =====
    {
        id: 'profit_before_tax',
        category: 'Income Statement',
        key: 'profit_before_tax',
        label: 'Profit Before Tax',
        keywords_indas: [
            'profit before tax', 'pbt', 'profit before taxation',
            'income before tax', 'earnings before tax',
            'profit before income tax expense'
        ],
        keywords_gaap: [
            'income before taxes', 'pretax income', 'profit before tax',
            'earnings before income taxes', 'income before income tax expense',
            'pre-tax profit'
        ],
        keywords_ifrs: [
            'profit before tax', 'profit before income tax',
            'earnings before tax', 'pre-tax profit'
        ]
    },

    // ===== TAX EXPENSE SECTION =====
    {
        id: 'tax_expense',
        category: 'Income Statement',
        key: 'tax_expense',
        label: 'Tax Expense',
        keywords_indas: [
            'tax expense', 'income tax expense', 'current tax',
            'deferred tax', 'provision for taxation',
            'current tax expense', 'deferred tax expense',
            'mat credit entitlement', 'tax expense for the year'
        ],
        keywords_gaap: [
            'income tax expense', 'provision for income taxes',
            'tax expense', 'income taxes', 'current tax expense',
            'deferred tax expense', 'tax provision'
        ],
        keywords_ifrs: [
            'income tax expense', 'tax expense', 'taxation',
            'current tax', 'deferred tax', 'tax charge'
        ],
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
            'current tax', 'current tax expense', 'current income tax',
            'current year tax', 'provision for current tax'
        ],
        keywords_gaap: [
            'current tax expense', 'current income tax expense',
            'current provision for taxes'
        ],
        keywords_ifrs: [
            'current tax', 'current tax expense', 'current income tax'
        ]
    },
    {
        id: 'deferred_tax_expense',
        category: 'Income Statement',
        key: 'deferred_tax_expense',
        label: 'Deferred Tax Expense',
        keywords_indas: [
            'deferred tax', 'deferred tax expense', 'deferred income tax',
            'deferred tax charge', 'deferred tax credit'
        ],
        keywords_gaap: [
            'deferred tax expense', 'deferred income tax expense',
            'deferred tax provision'
        ],
        keywords_ifrs: [
            'deferred tax expense', 'deferred tax', 'deferred income tax expense'
        ]
    },

    // ===== NET PROFIT SECTION =====
    {
        id: 'profit_after_tax',
        category: 'Income Statement',
        key: 'profit_after_tax',
        label: 'Profit After Tax / Net Income',
        keywords_indas: [
            'profit after tax', 'profit for the year', 'profit for the period',
            'net profit', 'pat', 'profit attributable to owners',
            'total comprehensive income', 'net income', 'net earnings'
        ],
        keywords_gaap: [
            'net income', 'net earnings', 'net profit', 'profit after tax',
            'net income attributable to shareholders', 'bottom line',
            'income after taxes', 'net income from operations'
        ],
        keywords_ifrs: [
            'profit for the year', 'profit for the period', 'net profit',
            'profit after tax', 'profit attributable to equity holders',
            'total profit'
        ]
    },
    {
        id: 'profit_from_continuing_operations',
        category: 'Income Statement',
        key: 'profit_from_continuing_operations',
        label: 'Profit from Continuing Operations',
        keywords_indas: [
            'profit from continuing operations', 'income from continuing operations'
        ],
        keywords_gaap: [
            'income from continuing operations', 'earnings from continuing operations'
        ],
        keywords_ifrs: [
            'profit from continuing operations', 'result from continuing operations'
        ],
        related_standards: {
            indas: ['IndAS 105'],
            gaap: ['ASC 205'],
            ifrs: ['IFRS 5']
        }
    },
    {
        id: 'profit_from_discontinued_operations',
        category: 'Income Statement',
        key: 'profit_from_discontinued_operations',
        label: 'Profit from Discontinued Operations',
        keywords_indas: [
            'profit from discontinued operations', 'discontinued operations',
            'loss from discontinued operations'
        ],
        keywords_gaap: [
            'income from discontinued operations', 'discontinued operations net of tax',
            'loss from discontinued operations'
        ],
        keywords_ifrs: [
            'profit from discontinued operations', 'discontinued operations',
            'result from discontinued operations'
        ],
        related_standards: {
            indas: ['IndAS 105'],
            gaap: ['ASC 205'],
            ifrs: ['IFRS 5']
        }
    },

    // ===== EXCEPTIONAL ITEMS =====
    {
        id: 'exceptional_items',
        category: 'Income Statement',
        key: 'exceptional_items',
        label: 'Exceptional Items',
        keywords_indas: [
            'exceptional items', 'exceptional income', 'exceptional expense',
            'unusual items', 'non-recurring items', 'one-time items'
        ],
        keywords_gaap: [
            'unusual items', 'special items', 'non-recurring items',
            'extraordinary items', 'one-time charges', 'restructuring charges'
        ],
        keywords_ifrs: [
            'exceptional items', 'material items', 'significant items',
            'non-recurring items'
        ]
    },
    {
        id: 'impairment_loss',
        category: 'Income Statement',
        key: 'impairment_loss',
        label: 'Impairment Loss',
        keywords_indas: [
            'impairment loss', 'impairment of assets', 'impairment charge',
            'write down of assets', 'impairment of goodwill',
            'impairment of intangible assets', 'impairment of ppe'
        ],
        keywords_gaap: [
            'impairment loss', 'impairment charge', 'asset impairment',
            'goodwill impairment', 'intangible asset impairment',
            'write-down', 'impairment of long-lived assets'
        ],
        keywords_ifrs: [
            'impairment losses', 'impairment of assets', 'impairment charge',
            'impairment of goodwill', 'write-down of assets'
        ],
        related_standards: {
            indas: ['IndAS 36'],
            gaap: ['ASC 350', 'ASC 360'],
            ifrs: ['IAS 36']
        }
    },
    {
        id: 'restructuring_costs',
        category: 'Income Statement',
        key: 'restructuring_costs',
        label: 'Restructuring Costs',
        keywords_indas: [
            'restructuring costs', 'restructuring expense', 'reorganization costs',
            'severance costs', 'voluntary retirement scheme'
        ],
        keywords_gaap: [
            'restructuring charges', 'restructuring costs', 'reorganization costs',
            'severance expense', 'exit costs'
        ],
        keywords_ifrs: [
            'restructuring costs', 'restructuring provision', 'reorganisation costs'
        ],
        related_standards: {
            indas: ['IndAS 37'],
            gaap: ['ASC 420'],
            ifrs: ['IAS 37']
        }
    },
    {
        id: 'revenue_from_operations',
        category: 'Income Statement',
        key: 'revenue_from_operations',
        label: 'Revenue from Operations',
        keywords_indas: [
            'revenue from operations', 'revenue from operations net of excise duty',
            'sale of products', 'sale of goods', 'income from services',
            'operating revenue', 'net sales', 'turnover', 'sales revenue'
        ],
        keywords_gaap: [
            'revenue', 'sales', 'net sales',
            'sales revenue', 'total revenue'
        ],
        keywords_ifrs: [
            'revenue from contracts with customers', 'revenue'
        ],
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
        keywords_gaap: [
            'other income', 'non-operating income', 'interest income', 'dividend income'
        ],
        keywords_ifrs: [
            'other income', 'non-operating income'
        ],
        related_standards: {
            indas: ['IndAS 115'],
            gaap: ['ASC 225'],
            ifrs: ['IFRS 15']
        }
    },
    {
        id: 'expected_credit_loss',
        category: 'Income Statement',
        key: 'expected_credit_loss',
        label: 'Expected Credit Loss (ECL)',
        keywords_indas: [
            'expected credit loss', 'ecl provision', 'credit loss provision',
            'provision for expected credit losses', 'credit impairment',
            'allowance for credit losses'
        ],
        keywords_gaap: [
            'allowance for credit losses', 'credit loss allowance',
            'provision for credit losses'
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
        id: 'borrowing_costs_capitalized',
        category: 'Income Statement',
        key: 'borrowing_costs_capitalized',
        label: 'Borrowing Costs Capitalized',
        keywords_indas: [
            'borrowing costs capitalized', 'interest capitalized',
            'capitalized borrowing costs', 'finance cost capitalized'
        ],
        keywords_gaap: [
            'capitalized interest', 'interest expense capitalized'
        ],
        keywords_ifrs: [
            'borrowing costs capitalized', 'capitalized borrowing costs'
        ],
        related_standards: {
            indas: ['IndAS 23'],
            gaap: ['ASC 835'],
            ifrs: ['IAS 23']
        }
    },
    {
        id: 'mat_credit_entitlement',
        category: 'Income Statement',
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
    {
        id: 'impairment_loss',
        category: 'Income Statement',
        key: 'impairment_loss',
        label: 'Impairment Loss',
        keywords_indas: [
            'impairment loss', 'impairment of assets', 'provision for impairment',
            'impairment provision', 'asset impairment', 'write down of assets'
        ],
        keywords_gaap: [
            'impairment loss', 'impairment charge', 'asset impairment', 'write-down'
        ],
        keywords_ifrs: [
            'impairment loss', 'impairment of assets'
        ],
        related_standards: {
            indas: ['IndAS 36'],
            gaap: ['ASC 360'],
            ifrs: ['IAS 36']
        }
    },
    {
        id: 'other_comprehensive_income',
        category: 'Other Comprehensive Income',
        key: 'other_comprehensive_income',
        label: 'Other Comprehensive Income',
        keywords_indas: [
            'other comprehensive income', 'oci', 'items that will be reclassified',
            'items that will not be reclassified', 'cash flow hedge reserve',
            'foreign currency translation reserve', 'fvtoci reserve',
            'remeasurement of defined benefit plans'
        ],
        keywords_gaap: [
            'accumulated other comprehensive income', 'oci',
            'other comprehensive income loss', 'foreign currency translation adjustment',
            'unrealized gains losses on securities'
        ],
        keywords_ifrs: [
            'other comprehensive income', 'oci reserve',
            'accumulated other comprehensive income', 'translation reserve'
        ],
        related_standards: {
            indas: ['IndAS 1'],
            gaap: ['ASC 220'],
            ifrs: ['IAS 1']
        }
    },
    {
        id: 'total_comprehensive_income',
        category: 'Other Comprehensive Income',
        key: 'total_comprehensive_income',
        label: 'Total Comprehensive Income',
        keywords_indas: [
            'total comprehensive income', 'comprehensive income for the year',
            'profit for the year and other comprehensive income',
            'statement of comprehensive income'
        ],
        keywords_gaap: [
            'total comprehensive income', 'comprehensive income'
        ],
        keywords_ifrs: [
            'total comprehensive income', 'statement of comprehensive income'
        ],
        related_standards: {
            indas: ['IndAS 1'],
            gaap: ['ASC 220'],
            ifrs: ['IAS 1']
        }
    }
];
