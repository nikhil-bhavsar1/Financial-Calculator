
import { TermMapping } from '../../types/terminology';

export const TAX_DETAILS_TERMS: TermMapping[] = [
    {
        id: 'deferred_tax_assets_rd',
        category: 'Tax',
        key: 'deferred_tax_assets_rd',
        label: 'DTA - Capitalized R&D',
        description: 'Deferred tax assets arising from capitalized research and development costs.',
        keywords_indas: ['capitalized research and development', 'research and development tax'],
        keywords_gaap: ['capitalized research and development', 'r&d tax credits'],
        keywords_ifrs: ['capitalized development costs', 'research and development tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_assets_credits',
        category: 'Tax',
        key: 'deferred_tax_assets_credits',
        label: 'DTA - Tax Credits',
        description: 'Deferred tax assets from tax credit carryforwards.',
        keywords_indas: ['tax credit entitlement', 'mat credit entitlement'],
        keywords_gaap: ['tax credit carryforwards', 'tax credits', 'foreign tax credits'],
        keywords_ifrs: ['tax credits', 'unused tax losses'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_assets_accrued',
        category: 'Tax',
        key: 'deferred_tax_assets_accrued',
        label: 'DTA - Accrued Liabilities',
        keywords_indas: ['accrued expenses tax', 'reserves and surplus tax'],
        keywords_gaap: ['accrued liabilities', 'other reserves'],
        keywords_ifrs: ['accrued expenses tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_assets_revenue',
        category: 'Tax',
        key: 'deferred_tax_assets_revenue',
        label: 'DTA - Deferred Revenue',
        keywords_indas: ['deferred revenue tax'],
        keywords_gaap: ['deferred revenue'],
        keywords_ifrs: ['contract liabilities tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_assets_lease',
        category: 'Tax',
        key: 'deferred_tax_assets_lease',
        label: 'DTA - Lease Liabilities',
        keywords_indas: ['lease liabilities tax'],
        keywords_gaap: ['lease liabilities', 'operating lease liabilities'],
        keywords_ifrs: ['lease liabilities tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_liabilities_depreciation',
        category: 'Tax',
        key: 'deferred_tax_liabilities_depreciation',
        label: 'DTL - Depreciation',
        keywords_indas: ['depreciation tax', 'property plant and equipment tax'],
        keywords_gaap: ['depreciation', 'accelerated depreciation'],
        keywords_ifrs: ['depreciation tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_liabilities_rou',
        category: 'Tax',
        key: 'deferred_tax_liabilities_rou',
        label: 'DTL - Right-of-Use Assets',
        keywords_indas: ['right-of-use assets tax'],
        keywords_gaap: ['right-of-use assets', 'rou assets'],
        keywords_ifrs: ['right-of-use assets tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_min_tax_foreign',
        category: 'Tax',
        key: 'deferred_tax_min_tax_foreign',
        label: 'DTL - Min Tax on Foreign Earnings',
        keywords_indas: ['foreign earnings tax'],
        keywords_gaap: ['minimum tax on foreign earnings'],
        keywords_ifrs: ['foreign earnings tax'],
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    },
    {
        id: 'deferred_tax_valuation_allowance',
        category: 'Tax',
        key: 'deferred_tax_valuation_allowance',
        label: 'Valuation Allowance',
        keywords_indas: ['valuation allowance'],
        keywords_gaap: ['valuation allowance', 'less: valuation allowance'],
        keywords_ifrs: ['valuation allowance'],
        sign_convention: 'negative',
        related_standards: { indas: ['IndAS 12'], gaap: ['ASC 740'], ifrs: ['IAS 12'] }
    }
];
