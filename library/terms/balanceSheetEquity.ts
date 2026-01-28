import { TermMapping } from '../../types/terminology';

export const BALANCE_SHEET_EQUITY_TERMS: TermMapping[] = [
    {
        id: 'total_equity',
        category: 'Balance Sheet - Equity',
        key: 'total_equity',
        label: 'Total Equity',
        keywords_indas: [
            'total equity', 'equity total', 'shareholders funds',
            'shareholders equity', 'stockholders equity', 'net worth',
            'equity and liabilities', 'owners equity'
        ],
        keywords_gaap: [
            'total stockholders equity', 'total shareholders equity',
            'stockholders equity total', 'total equity', 'net worth'
        ],
        keywords_ifrs: [
            'total equity', 'equity total', 'shareholders equity',
            'total equity attributable to owners'
        ]
    },
    {
        id: 'share_capital',
        category: 'Balance Sheet - Equity',
        key: 'share_capital',
        label: 'Share Capital',
        keywords_indas: [
            'equity share capital', 'share capital', 'paid-up capital',
            'issued capital', 'subscribed capital', 'called-up capital',
            'ordinary share capital', 'preference share capital',
            'authorized capital', 'face value of shares'
        ],
        keywords_gaap: [
            'common stock', 'common shares', 'preferred stock',
            'capital stock', 'par value shares', 'stated capital',
            'shares issued', 'class a common stock', 'class b common stock'
        ],
        keywords_ifrs: [
            'share capital', 'issued share capital', 'ordinary shares',
            'preference shares', 'paid-in capital'
        ],
        related_standards: {
            indas: ['IndAS 32'],
            gaap: ['ASC 505'],
            ifrs: ['IAS 32']
        }
    },
    {
        id: 'share_premium',
        category: 'Balance Sheet - Equity',
        key: 'share_premium',
        label: 'Share Premium / Additional Paid-in Capital',
        keywords_indas: [
            'securities premium', 'securities premium account',
            'share premium', 'premium on issue of shares'
        ],
        keywords_gaap: [
            'additional paid-in capital', 'apic', 'paid-in capital in excess of par',
            'capital surplus', 'capital in excess of par value'
        ],
        keywords_ifrs: [
            'share premium', 'share premium account',
            'additional paid-in capital'
        ]
    },
    {
        id: 'retained_earnings',
        category: 'Balance Sheet - Equity',
        key: 'retained_earnings',
        label: 'Retained Earnings',
        keywords_indas: [
            'retained earnings', 'surplus in statement of profit and loss',
            'accumulated profits', 'profit and loss balance', 'revenue reserves',
            'general reserve', 'undistributed profits'
        ],
        keywords_gaap: [
            'retained earnings', 'accumulated earnings', 'earned surplus',
            'reinvested earnings', 'accumulated profits',
            'retained earnings deficit'
        ],
        keywords_ifrs: [
            'retained earnings', 'accumulated profits', 'revenue reserves',
            'profit and loss reserve'
        ]
    },
    {
        id: 'other_reserves',
        category: 'Balance Sheet - Equity',
        key: 'other_reserves',
        label: 'Other Reserves',
        keywords_indas: [
            'other equity', 'reserves and surplus', 'capital reserve',
            'capital redemption reserve', 'debenture redemption reserve',
            'revaluation reserve', 'share options outstanding account',
            'special reserve', 'amalgamation reserve', 'statutory reserve'
        ],
        keywords_gaap: [
            'accumulated other comprehensive income', 'aoci',
            'treasury stock', 'other comprehensive income accumulated'
        ],
        keywords_ifrs: [
            'other reserves', 'revaluation surplus', 'capital reserve',
            'hedging reserve', 'fair value reserve', 'translation reserve'
        ]
    },
    {
        id: 'treasury_shares',
        category: 'Balance Sheet - Equity',
        key: 'treasury_shares',
        label: 'Treasury Shares',
        keywords_indas: [
            'treasury shares', 'buyback of shares', 'shares bought back'
        ],
        keywords_gaap: [
            'treasury stock', 'treasury shares', 'shares in treasury',
            'cost of treasury stock'
        ],
        keywords_ifrs: [
            'treasury shares', 'own shares held'
        ]
    },
    {
        id: 'accumulated_oci',
        category: 'Balance Sheet - Equity',
        key: 'accumulated_oci',
        label: 'Accumulated Other Comprehensive Income',
        keywords_indas: [
            'other comprehensive income', 'oci', 'items that will be reclassified',
            'items that will not be reclassified', 'cash flow hedge reserve',
            'foreign currency translation reserve', 'fvtoci reserve',
            'remeasurement of defined benefit plans'
        ],
        keywords_gaap: [
            'accumulated other comprehensive income', 'aoci',
            'other comprehensive income loss', 'foreign currency translation adjustment',
            'unrealized gains losses on securities', 'pension adjustment'
        ],
        keywords_ifrs: [
            'other comprehensive income', 'oci reserve',
            'accumulated other comprehensive income', 'translation reserve',
            'hedging reserve', 'fair value reserve'
        ]
    },
    {
        id: 'revaluation_reserve',
        category: 'Balance Sheet - Equity',
        key: 'revaluation_reserve',
        label: 'Revaluation Reserve',
        keywords_indas: [
            'revaluation reserve', 'revaluation surplus', 'asset revaluation reserve'
        ],
        keywords_gaap: [
            'revaluation surplus'
        ],
        keywords_ifrs: [
            'revaluation surplus', 'revaluation reserve',
            'property revaluation reserve'
        ],
        related_standards: {
            indas: ['IndAS 16'],
            gaap: [],
            ifrs: ['IAS 16']
        }
    },
    {
        id: 'hedging_reserve',
        category: 'Balance Sheet - Equity',
        key: 'hedging_reserve',
        label: 'Hedging Reserve',
        keywords_indas: [
            'cash flow hedge reserve', 'hedging reserve',
            'effective portion of cash flow hedges'
        ],
        keywords_gaap: [
            'cash flow hedge reserve', 'derivative hedging reserve'
        ],
        keywords_ifrs: [
            'hedging reserve', 'cash flow hedge reserve'
        ],
        related_standards: {
            indas: ['IndAS 109'],
            gaap: ['ASC 815'],
            ifrs: ['IFRS 9']
        }
    },
    {
        id: 'foreign_currency_translation_reserve',
        category: 'Balance Sheet - Equity',
        key: 'foreign_currency_translation_reserve',
        label: 'Foreign Currency Translation Reserve',
        keywords_indas: [
            'foreign currency translation reserve', 'fctr',
            'exchange differences on translating foreign operations'
        ],
        keywords_gaap: [
            'foreign currency translation adjustment', 'cumulative translation adjustment',
            'cta'
        ],
        keywords_ifrs: [
            'foreign currency translation reserve', 'translation reserve',
            'exchange reserve'
        ],
        related_standards: {
            indas: ['IndAS 21'],
            gaap: ['ASC 830'],
            ifrs: ['IAS 21']
        }
    },
    {
        id: 'share_based_payment_reserve',
        category: 'Balance Sheet - Equity',
        key: 'share_based_payment_reserve',
        label: 'Share-based Payment Reserve',
        keywords_indas: [
            'share options outstanding account', 'esop reserve',
            'share based payment reserve', 'stock option reserve'
        ],
        keywords_gaap: [
            'stock compensation reserve', 'equity compensation reserve'
        ],
        keywords_ifrs: [
            'share-based payment reserve', 'equity-settled share-based payment reserve'
        ],
        related_standards: {
            indas: ['IndAS 102'],
            gaap: ['ASC 718'],
            ifrs: ['IFRS 2']
        }
    },
    {
        id: 'capital_reserve',
        category: 'Balance Sheet - Equity',
        key: 'capital_reserve',
        label: 'Capital Reserve',
        keywords_indas: [
            'capital reserve', 'capital reserves', 'forfeiture of shares reserve'
        ],
        keywords_gaap: [
            'capital surplus', 'paid-in capital other'
        ],
        keywords_ifrs: [
            'capital reserve', 'capital reserves'
        ]
    },
    {
        id: 'general_reserve',
        category: 'Balance Sheet - Equity',
        key: 'general_reserve',
        label: 'General Reserve',
        keywords_indas: [
            'general reserve', 'revenue reserve', 'free reserves'
        ],
        keywords_gaap: [
            'general reserve', 'appropriated retained earnings'
        ],
        keywords_ifrs: [
            'general reserve', 'legal reserve'
        ]
    },
    {
        id: 'non_controlling_interest',
        category: 'Balance Sheet - Equity',
        key: 'non_controlling_interest',
        label: 'Non-Controlling Interest',
        keywords_indas: [
            'non-controlling interests', 'non controlling interest', 'nci',
            'minority interest', 'equity attributable to non-controlling interests'
        ],
        keywords_gaap: [
            'noncontrolling interest', 'minority interest',
            'non-controlling interests in subsidiaries'
        ],
        keywords_ifrs: [
            'non-controlling interests', 'minority interest', 'nci'
        ],
        related_standards: {
            indas: ['IndAS 110'],
            gaap: ['ASC 810'],
            ifrs: ['IFRS 10']
        }
    },
    {
        id: 'equity_attributable_to_owners',
        category: 'Balance Sheet - Equity',
        key: 'equity_attributable_to_owners',
        label: 'Equity Attributable to Owners of Parent',
        keywords_indas: [
            'equity attributable to owners of the parent',
            'equity attributable to shareholders of the company'
        ],
        keywords_gaap: [
            'equity attributable to parent', 'shareholders equity of parent'
        ],
        keywords_ifrs: [
            'equity attributable to owners of parent',
            'equity attributable to equity holders of the parent'
        ]
    }
];
