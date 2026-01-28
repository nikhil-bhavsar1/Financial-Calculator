import { TermMapping } from '../../types/terminology';

export const OTHER_COMPREHENSIVE_INCOME_TERMS: TermMapping[] = [
    {
        id: 'total_comprehensive_income',
        category: 'Other Comprehensive Income',
        key: 'total_comprehensive_income',
        label: 'Total Comprehensive Income',
        keywords_indas: [
            'total comprehensive income', 'comprehensive income for the year',
            'total comprehensive income for the period'
        ],
        keywords_gaap: [
            'comprehensive income', 'total comprehensive income'
        ],
        keywords_ifrs: [
            'total comprehensive income', 'comprehensive income for the year'
        ]
    },
    {
        id: 'oci_items_reclassified',
        category: 'Other Comprehensive Income',
        key: 'oci_items_reclassified',
        label: 'OCI Items to be Reclassified',
        keywords_indas: [
            'items that will be reclassified to profit or loss',
            'items that may be reclassified to profit or loss'
        ],
        keywords_gaap: [
            'other comprehensive income reclassification adjustments'
        ],
        keywords_ifrs: [
            'items that will be reclassified to profit or loss',
            'items that may be reclassified subsequently to profit or loss'
        ]
    },
    {
        id: 'oci_items_not_reclassified',
        category: 'Other Comprehensive Income',
        key: 'oci_items_not_reclassified',
        label: 'OCI Items Not to be Reclassified',
        keywords_indas: [
            'items that will not be reclassified to profit or loss'
        ],
        keywords_gaap: [
            'other comprehensive income not reclassified'
        ],
        keywords_ifrs: [
            'items that will not be reclassified to profit or loss'
        ]
    },
    {
        id: 'remeasurement_defined_benefit',
        category: 'Other Comprehensive Income',
        key: 'remeasurement_defined_benefit',
        label: 'Remeasurement of Defined Benefit Plans',
        keywords_indas: [
            'remeasurement of defined benefit plans',
            'remeasurement of post employment benefit obligations',
            'actuarial gains losses'
        ],
        keywords_gaap: [
            'pension adjustments', 'actuarial gains and losses',
            'postretirement benefit adjustments'
        ],
        keywords_ifrs: [
            'remeasurements of defined benefit liability',
            'actuarial gains and losses'
        ],
        related_standards: {
            indas: ['IndAS 19'],
            gaap: ['ASC 715'],
            ifrs: ['IAS 19']
        }
    },
    {
        id: 'fvtoci_gains_losses',
        category: 'Other Comprehensive Income',
        key: 'fvtoci_gains_losses',
        label: 'Fair Value Changes on FVTOCI Investments',
        keywords_indas: [
            'fair value changes on fvtoci investments',
            'fair value gains on equity instruments',
            'changes in fair value of equity instruments through oci'
        ],
        keywords_gaap: [
            'unrealized gains losses on available for sale securities',
            'net unrealized gains losses on investments'
        ],
        keywords_ifrs: [
            'fair value gains losses on fvtoci financial assets',
            'changes in fair value of equity investments at fvtoci'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 320'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'cash_flow_hedge_oci',
        category: 'Other Comprehensive Income',
        key: 'cash_flow_hedge_oci',
        label: 'Cash Flow Hedge Gains/Losses',
        keywords_indas: [
            'effective portion of gains and losses on hedging instruments',
            'cash flow hedge reserve movement', 'hedge effectiveness'
        ],
        keywords_gaap: [
            'cash flow hedging gains losses', 'derivative hedging activity'
        ],
        keywords_ifrs: [
            'cash flow hedges', 'effective portion of cash flow hedges'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 815'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'foreign_exchange_oci',
        category: 'Other Comprehensive Income',
        key: 'foreign_exchange_oci',
        label: 'Foreign Exchange Translation Gains/Losses',
        keywords_indas: [
            'exchange differences on translation of foreign operations',
            'foreign currency translation differences'
        ],
        keywords_gaap: [
            'foreign currency translation adjustments',
            'cumulative translation adjustment change'
        ],
        keywords_ifrs: [
            'exchange differences on translating foreign operations',
            'foreign currency translation reserve movement'
        ],
        related_standards: {
            indas: ['IndAS 21'],
            gaap: ['ASC 830'],
            ifrs: ['IAS 21']
        }
    },
    {
        id: 'revaluation_surplus_oci',
        category: 'Other Comprehensive Income',
        key: 'revaluation_surplus_oci',
        label: 'Revaluation Surplus Changes',
        keywords_indas: [
            'revaluation surplus', 'revaluation gain on property plant equipment'
        ],
        keywords_gaap: [
            'revaluation surplus'
        ],
        keywords_ifrs: [
            'revaluation surplus on property plant and equipment',
            'revaluation of land and buildings'
        ],
        related_standards: {
            indas: ['IndAS 16'],
            gaap: [],
            ifrs: ['IAS 16']
        }
    },
    {
        id: 'share_of_oci_associates',
        category: 'Other Comprehensive Income',
        key: 'share_of_oci_associates',
        label: 'Share of OCI of Associates/JVs',
        keywords_indas: [
            'share of other comprehensive income of associates',
            'share of oci of joint ventures'
        ],
        keywords_gaap: [
            'equity method other comprehensive income'
        ],
        keywords_ifrs: [
            'share of other comprehensive income of associates and joint ventures'
        ],
        related_standards: {
            indas: ['IndAS 28'],
            gaap: ['ASC 323'],
            ifrs: ['IAS 28']
        }
    }
];

export const SEGMENT_REPORTING_TERMS: TermMapping[] = [
    {
        id: 'segment_revenue',
        category: 'Segment Reporting',
        key: 'segment_revenue',
        label: 'Segment Revenue',
        keywords_indas: [
            'segment revenue', 'revenue by segment', 'segment sales',
            'geographic revenue', 'business segment revenue'
        ],
        keywords_gaap: [
            'segment revenue', 'revenue by operating segment',
            'geographic revenue'
        ],
        keywords_ifrs: [
            'segment revenue', 'revenue from external customers by segment'
        ],
        related_standards: {
            indas: ['IndAS 108'],
            gaap: ['ASC 280'],
            ifrs: ['IFRS 8']
        }
    },
    {
        id: 'segment_profit',
        category: 'Segment Reporting',
        key: 'segment_profit',
        label: 'Segment Profit/Loss',
        keywords_indas: [
            'segment result', 'segment profit', 'segment operating profit',
            'profit by segment'
        ],
        keywords_gaap: [
            'segment operating income', 'segment profit or loss'
        ],
        keywords_ifrs: [
            'segment result', 'segment profit or loss'
        ]
    },
    {
        id: 'segment_assets',
        category: 'Segment Reporting',
        key: 'segment_assets',
        label: 'Segment Assets',
        keywords_indas: [
            'segment assets', 'assets by segment', 'identifiable assets by segment'
        ],
        keywords_gaap: [
            'segment assets', 'identifiable assets'
        ],
        keywords_ifrs: [
            'segment assets', 'assets allocated to segments'
        ]
    },
    {
        id: 'segment_liabilities',
        category: 'Segment Reporting',
        key: 'segment_liabilities',
        label: 'Segment Liabilities',
        keywords_indas: [
            'segment liabilities', 'liabilities by segment'
        ],
        keywords_gaap: [
            'segment liabilities'
        ],
        keywords_ifrs: [
            'segment liabilities', 'liabilities allocated to segments'
        ]
    },
    {
        id: 'geographic_revenue',
        category: 'Segment Reporting',
        key: 'geographic_revenue',
        label: 'Revenue by Geography',
        keywords_indas: [
            'revenue by geography', 'geographical revenue', 'domestic revenue',
            'export revenue', 'revenue from india', 'revenue from overseas'
        ],
        keywords_gaap: [
            'revenue by geographic area', 'domestic revenue', 'international revenue'
        ],
        keywords_ifrs: [
            'revenue from external customers by country', 'geographic revenue'
        ]
    },
    {
        id: 'inter_segment_revenue',
        category: 'Segment Reporting',
        key: 'inter_segment_revenue',
        label: 'Inter-Segment Revenue',
        keywords_indas: [
            'inter-segment revenue', 'inter segment sales', 'elimination'
        ],
        keywords_gaap: [
            'intersegment revenue', 'intersegment sales', 'elimination'
        ],
        keywords_ifrs: [
            'inter-segment revenue', 'intersegment transactions'
        ]
    }
];

export const TAX_TERMS: TermMapping[] = [
    {
        id: 'effective_tax_rate',
        category: 'Tax',
        key: 'effective_tax_rate',
        label: 'Effective Tax Rate',
        keywords_indas: [
            'effective tax rate', 'etr', 'average tax rate'
        ],
        keywords_gaap: [
            'effective tax rate', 'etr', 'effective income tax rate'
        ],
        keywords_ifrs: [
            'effective tax rate', 'average effective tax rate'
        ]
    },
    {
        id: 'statutory_tax_rate',
        category: 'Tax',
        key: 'statutory_tax_rate',
        label: 'Statutory Tax Rate',
        keywords_indas: [
            'statutory tax rate', 'applicable tax rate', 'corporate tax rate'
        ],
        keywords_gaap: [
            'statutory tax rate', 'federal statutory rate'
        ],
        keywords_ifrs: [
            'statutory tax rate', 'standard rate of tax'
        ]
    },
    {
        id: 'tax_reconciliation',
        category: 'Tax',
        key: 'tax_reconciliation',
        label: 'Tax Reconciliation',
        keywords_indas: [
            'tax reconciliation', 'reconciliation of tax expense',
            'tax rate reconciliation'
        ],
        keywords_gaap: [
            'reconciliation of statutory tax rate', 'rate reconciliation'
        ],
        keywords_ifrs: [
            'tax rate reconciliation', 'reconciliation of effective tax rate'
        ]
    },
    {
        id: 'tax_loss_carryforward',
        category: 'Tax',
        key: 'tax_loss_carryforward',
        label: 'Tax Loss Carryforward',
        keywords_indas: [
            'unabsorbed depreciation', 'carried forward losses',
            'tax losses carried forward', 'mat credit'
        ],
        keywords_gaap: [
            'net operating loss carryforward', 'nol carryforward',
            'tax loss carryforward'
        ],
        keywords_ifrs: [
            'unused tax losses', 'tax losses carried forward'
        ]
    },
    {
        id: 'uncertain_tax_positions',
        category: 'Tax',
        key: 'uncertain_tax_positions',
        label: 'Uncertain Tax Positions',
        keywords_indas: [
            'uncertain tax positions', 'tax contingencies'
        ],
        keywords_gaap: [
            'uncertain tax positions', 'utp', 'fin 48 liability'
        ],
        keywords_ifrs: [
            'uncertain tax treatments', 'tax uncertainties'
        ],
        related_standards: {
            indas: ['IndAS 12'],
            gaap: ['ASC 740'],
            ifrs: ['IFRIC 23']
        }
    }
];
