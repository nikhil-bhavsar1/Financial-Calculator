import { TermMapping } from '../../types/terminology';

/**
 * Additional Comprehensive Financial Terms
 * 
 * This file contains terms from the comprehensive reference list covering:
 * - Ind AS (Indian Accounting Standards)
 * - US GAAP
 * - IFRS (International Financial Reporting Standards) including IFRS 18
 * 
 * These complement the existing term files with additional detailed terms.
 */

// =============================================================================
// ADDITIONAL REVENUE TERMS
// =============================================================================
export const ADDITIONAL_REVENUE_TERMS: TermMapping[] = [
    {
        id: 'interest_revenue_effective_interest',
        category: 'Income Statement',
        key: 'interest_revenue_effective_interest',
        label: 'Interest Revenue (Effective Interest Method)',
        description: 'Interest calculated using effective interest rate for financial assets at amortised cost',
        keywords_indas: [
            'interest revenue calculated using the effective interest method',
            'interest revenue', 'effective interest income'
        ],
        keywords_gaap: [
            'interest income effective interest', 'interest revenue'
        ],
        keywords_ifrs: [
            'interest revenue calculated using effective interest method',
            'interest income using effective interest rate'
        ],
        related_standards: { indas: ['IndAS 109'], gaap: ['ASC 310'], ifrs: ['IFRS 9'] }
    },
    {
        id: 'rental_income',
        category: 'Income Statement',
        key: 'rental_income',
        label: 'Rental Income',
        keywords_indas: ['rental income', 'rent income', 'lease rental income'],
        keywords_gaap: ['rental revenue', 'lease income', 'rent revenue'],
        keywords_ifrs: ['rental income', 'income from investment properties']
    },
    {
        id: 'royalty_income',
        category: 'Income Statement',
        key: 'royalty_income',
        label: 'Royalty Income',
        keywords_indas: ['royalty income', 'royalties received', 'licensing income'],
        keywords_gaap: ['royalty revenue', 'royalties', 'licensing revenue'],
        keywords_ifrs: ['royalty income', 'royalties', 'license fees']
    },
    {
        id: 'export_incentives',
        category: 'Income Statement',
        key: 'export_incentives',
        label: 'Export Incentives',
        keywords_indas: ['export incentives', 'duty drawback', 'meis', 'rodtep', 'export benefits'],
        keywords_gaap: ['export subsidies', 'government grants - exports'],
        keywords_ifrs: ['export incentives', 'government grants related to income']
    },
    {
        id: 'scrap_sales',
        category: 'Income Statement',
        key: 'scrap_sales',
        label: 'Scrap Sales',
        keywords_indas: ['manufacturing scrap sales', 'scrap and wastage sale', 'scrap sales'],
        keywords_gaap: ['scrap sales', 'by-product sales'],
        keywords_ifrs: ['scrap sales', 'sale of scrap']
    },
    {
        id: 'insurance_revenue',
        category: 'Income Statement',
        key: 'insurance_revenue',
        label: 'Insurance Revenue',
        description: 'Revenue from insurance contracts (IFRS 17)',
        keywords_indas: ['insurance revenue', 'premium income'],
        keywords_gaap: ['insurance premiums earned', 'premium revenue'],
        keywords_ifrs: ['insurance revenue', 'insurance contract revenue'],
        related_standards: { ifrs: ['IFRS 17'] }
    }
];

// =============================================================================
// ADDITIONAL EXPENSE TERMS
// =============================================================================
export const ADDITIONAL_EXPENSE_TERMS: TermMapping[] = [
    {
        id: 'commitment_charges',
        category: 'Income Statement',
        key: 'commitment_charges',
        label: 'Commitment Charges',
        keywords_indas: ['commitment charges', 'commitment fees', 'facility fees'],
        keywords_gaap: ['commitment fee', 'unused line fee'],
        keywords_ifrs: ['commitment fees', 'facility commitment charges']
    },
    {
        id: 'loan_processing_charges',
        category: 'Income Statement',
        key: 'loan_processing_charges',
        label: 'Loan Processing Charges',
        keywords_indas: ['loan processing charges', 'loan origination fees', 'processing fees'],
        keywords_gaap: ['loan origination costs', 'debt issuance costs'],
        keywords_ifrs: ['transaction costs', 'loan arrangement fees']
    },
    {
        id: 'guarantee_charges',
        category: 'Income Statement',
        key: 'guarantee_charges',
        label: 'Guarantee Charges',
        keywords_indas: ['guarantee charges', 'bank guarantee commission', 'guarantee fees'],
        keywords_gaap: ['guarantee fees', 'standby letter of credit fees'],
        keywords_ifrs: ['financial guarantee fees', 'guarantee charges']
    },
    {
        id: 'rates_and_taxes',
        category: 'Income Statement',
        key: 'rates_and_taxes',
        label: 'Rates and Taxes',
        keywords_indas: ['rates and taxes', 'property tax', 'municipal taxes', 'local taxes'],
        keywords_gaap: ['property taxes', 'real estate taxes'],
        keywords_ifrs: ['property taxes', 'rates and levies']
    },
    {
        id: 'power_and_fuel',
        category: 'Income Statement',
        key: 'power_and_fuel',
        label: 'Power and Fuel',
        keywords_indas: ['power and fuel', 'electricity charges', 'fuel expense', 'energy costs'],
        keywords_gaap: ['utilities expense', 'electricity expense', 'fuel costs'],
        keywords_ifrs: ['power costs', 'energy expenses', 'utilities']
    },
    {
        id: 'carriage_inwards',
        category: 'Income Statement',
        key: 'carriage_inwards',
        label: 'Carriage Inwards',
        keywords_indas: ['carriage inwards', 'freight inward', 'inward freight'],
        keywords_gaap: ['freight-in', 'transportation-in'],
        keywords_ifrs: ['inbound freight', 'carriage inwards']
    },
    {
        id: 'carriage_outwards',
        category: 'Income Statement',
        key: 'carriage_outwards',
        label: 'Carriage Outwards',
        keywords_indas: ['carriage outwards', 'freight outward', 'outward freight', 'distribution costs'],
        keywords_gaap: ['freight-out', 'shipping costs', 'delivery expenses'],
        keywords_ifrs: ['outbound freight', 'distribution costs']
    },
    {
        id: 'csr_expenditure',
        category: 'Income Statement',
        key: 'csr_expenditure',
        label: 'CSR Expenditure',
        description: 'Corporate Social Responsibility expenditure (India specific)',
        keywords_indas: ['corporate social responsibility expenditure', 'csr expenditure', 'csr expense'],
        keywords_gaap: ['charitable contributions', 'community investment'],
        keywords_ifrs: ['corporate social responsibility costs']
    },
    {
        id: 'insurance_service_expenses',
        category: 'Income Statement',
        key: 'insurance_service_expenses',
        label: 'Insurance Service Expenses',
        description: 'Expenses from insurance contracts (IFRS 17)',
        keywords_indas: ['insurance claims', 'claims incurred'],
        keywords_gaap: ['insurance claims expense', 'losses incurred'],
        keywords_ifrs: ['insurance service expenses', 'claims and benefits'],
        related_standards: { ifrs: ['IFRS 17'] }
    },
    {
        id: 'reinsurance_income_expense',
        category: 'Income Statement',
        key: 'reinsurance_income_expense',
        label: 'Reinsurance Income/Expense',
        keywords_indas: ['reinsurance income', 'reinsurance expense'],
        keywords_gaap: ['ceded reinsurance', 'reinsurance recoveries'],
        keywords_ifrs: ['income from reinsurance contracts held', 'reinsurance contract assets'],
        related_standards: { ifrs: ['IFRS 17'] }
    }
];

// =============================================================================
// IFRS 18 SPECIFIC TERMS - NEW PROFIT OR LOSS STRUCTURE
// =============================================================================
export const IFRS18_TERMS: TermMapping[] = [
    {
        id: 'operating_profit_ifrs18',
        category: 'Income Statement - IFRS 18',
        key: 'operating_profit_ifrs18',
        label: 'Operating Profit or Loss (IFRS 18)',
        description: 'Mandatory subtotal under IFRS 18 for operating category',
        keywords_indas: ['operating profit', 'profit from operations'],
        keywords_gaap: ['operating income', 'income from operations'],
        keywords_ifrs: ['operating profit or loss', 'operating profit', 'operating result'],
        related_standards: { ifrs: ['IFRS 18'] }
    },
    {
        id: 'profit_before_financing_and_tax',
        category: 'Income Statement - IFRS 18',
        key: 'profit_before_financing_and_tax',
        label: 'Profit Before Financing and Income Taxes',
        description: 'Mandatory subtotal under IFRS 18 (after investing, before financing)',
        keywords_indas: ['profit before finance costs and tax'],
        keywords_gaap: ['income before interest and taxes'],
        keywords_ifrs: ['profit or loss before financing and income taxes', 'profit before financing'],
        related_standards: { ifrs: ['IFRS 18'] }
    },
    {
        id: 'integral_associates_jv',
        category: 'Income Statement - IFRS 18',
        key: 'integral_associates_jv',
        label: 'Share of Profit - Integral Associates/JVs',
        description: 'Share of profit from associates and JVs integral to operations (IFRS 18 operating category)',
        keywords_indas: ['share of profit of associates', 'share of profit of joint ventures'],
        keywords_gaap: ['equity in earnings of affiliates'],
        keywords_ifrs: ['share of profit of integral associates and joint ventures'],
        related_standards: { ifrs: ['IFRS 18'] }
    },
    {
        id: 'non_integral_associates_jv',
        category: 'Income Statement - IFRS 18',
        key: 'non_integral_associates_jv',
        label: 'Share of Profit - Non-integral Associates/JVs',
        description: 'Share of profit from non-integral associates and JVs (IFRS 18 investing category)',
        keywords_indas: ['share of profit of associates'],
        keywords_gaap: ['equity method investments income'],
        keywords_ifrs: ['share of profit of non-integral associates and joint ventures'],
        related_standards: { ifrs: ['IFRS 18'] }
    },
    {
        id: 'investing_category_income',
        category: 'Income Statement - IFRS 18',
        key: 'investing_category_income',
        label: 'Investing Category Income',
        description: 'Income from assets generating returns independently (IFRS 18)',
        keywords_indas: ['investment income', 'income from investments'],
        keywords_gaap: ['investment income', 'returns on investments'],
        keywords_ifrs: ['investing category', 'income from investing activities'],
        related_standards: { ifrs: ['IFRS 18'] }
    },
    {
        id: 'financing_category_expense',
        category: 'Income Statement - IFRS 18',
        key: 'financing_category_expense',
        label: 'Financing Category Expense',
        description: 'Finance costs including interest on borrowings and leases (IFRS 18)',
        keywords_indas: ['finance costs', 'interest expense'],
        keywords_gaap: ['interest expense'],
        keywords_ifrs: ['financing category', 'interest expense on borrowings and lease liabilities'],
        related_standards: { ifrs: ['IFRS 18'] }
    }
];

// =============================================================================
// ADDITIONAL BALANCE SHEET - ASSETS TERMS
// =============================================================================
export const ADDITIONAL_ASSET_TERMS: TermMapping[] = [
    {
        id: 'earmarked_bank_balances',
        category: 'Balance Sheet - Assets',
        key: 'earmarked_bank_balances',
        label: 'Earmarked Bank Balances',
        keywords_indas: ['earmarked balances with banks', 'unpaid dividend account', 'margin money deposits'],
        keywords_gaap: ['restricted cash', 'restricted bank deposits'],
        keywords_ifrs: ['restricted cash', 'pledged deposits']
    },
    {
        id: 'cheques_drafts_on_hand',
        category: 'Balance Sheet - Assets',
        key: 'cheques_drafts_on_hand',
        label: 'Cheques and Drafts on Hand',
        keywords_indas: ['cheques, drafts on hand', 'cheques on hand', 'bank drafts'],
        keywords_gaap: ['items in transit', 'checks on hand'],
        keywords_ifrs: ['cheques in hand', 'bank drafts receivable']
    },
    {
        id: 'loose_tools',
        category: 'Balance Sheet - Assets',
        key: 'loose_tools',
        label: 'Loose Tools',
        keywords_indas: ['loose tools', 'small tools', 'hand tools'],
        keywords_gaap: ['small tools and equipment'],
        keywords_ifrs: ['tools and implements']
    },
    {
        id: 'stock_in_trade',
        category: 'Balance Sheet - Assets',
        key: 'stock_in_trade',
        label: 'Stock-in-Trade',
        description: 'Goods purchased for resale',
        keywords_indas: ['stock-in-trade', 'stock in trade', 'traded goods'],
        keywords_gaap: ['merchandise inventory', 'goods for resale'],
        keywords_ifrs: ['trading inventory', 'merchandise']
    },
    {
        id: 'crypto_assets',
        category: 'Balance Sheet - Assets',
        key: 'crypto_assets',
        label: 'Crypto Assets',
        keywords_indas: ['crypto assets', 'cryptocurrency', 'digital assets'],
        keywords_gaap: ['crypto assets', 'digital assets', 'cryptocurrency (intangible)'],
        keywords_ifrs: ['crypto-assets', 'digital tokens']
    },
    {
        id: 'acquisition_in_progress',
        category: 'Balance Sheet - Assets',
        key: 'acquisition_in_progress',
        label: 'Acquisition in Progress',
        keywords_indas: ['acquisition in progress'],
        keywords_gaap: ['assets held pending acquisition', 'acquisition in progress'],
        keywords_ifrs: ['assets under acquisition']
    },
    {
        id: 'interest_accrued',
        category: 'Balance Sheet - Assets',
        key: 'interest_accrued',
        label: 'Interest Accrued',
        keywords_indas: ['interest accrued', 'accrued interest receivable', 'interest receivable'],
        keywords_gaap: ['interest receivable', 'accrued interest income'],
        keywords_ifrs: ['accrued interest', 'interest receivable']
    },
    {
        id: 'loans_to_related_parties',
        category: 'Balance Sheet - Assets',
        key: 'loans_to_related_parties',
        label: 'Loans to Related Parties',
        keywords_indas: ['loans to related parties', 'inter-corporate deposits', 'loans to subsidiaries'],
        keywords_gaap: ['loans to affiliates', 'receivables from related parties'],
        keywords_ifrs: ['loans to related parties', 'related party receivables']
    },
    {
        id: 'contract_assets',
        category: 'Balance Sheet - Assets',
        key: 'contract_assets',
        label: 'Contract Assets',
        description: 'Right to consideration for goods/services transferred (unbilled revenue)',
        keywords_indas: ['contract assets', 'unbilled revenue', 'accrued revenue'],
        keywords_gaap: ['contract assets', 'unbilled accounts receivable'],
        keywords_ifrs: ['contract assets', 'accrued income'],
        related_standards: { indas: ['IndAS 115'], gaap: ['ASC 606'], ifrs: ['IFRS 15'] }
    }
];

// =============================================================================
// ADDITIONAL BALANCE SHEET - LIABILITIES TERMS
// =============================================================================
export const ADDITIONAL_LIABILITY_TERMS: TermMapping[] = [
    {
        id: 'msme_payables',
        category: 'Balance Sheet - Liabilities',
        key: 'msme_payables',
        label: 'MSME Payables',
        description: 'Payables to Micro, Small and Medium Enterprises (India specific)',
        keywords_indas: [
            'total outstanding dues of micro enterprises and small enterprises',
            'msme payables', 'micro and small enterprise creditors'
        ],
        keywords_gaap: ['small business payables'],
        keywords_ifrs: ['trade payables - small enterprises']
    },
    {
        id: 'other_creditors',
        category: 'Balance Sheet - Liabilities',
        key: 'other_creditors',
        label: 'Other Creditors',
        keywords_indas: [
            'total outstanding dues of creditors other than micro enterprises and small enterprises',
            'other trade payables', 'other creditors'
        ],
        keywords_gaap: ['other accounts payable', 'other trade payables'],
        keywords_ifrs: ['other trade payables']
    },
    {
        id: 'loans_repayable_on_demand',
        category: 'Balance Sheet - Liabilities',
        key: 'loans_repayable_on_demand',
        label: 'Loans Repayable on Demand',
        keywords_indas: ['loans repayable on demand', 'call money borrowings', 'demand loans'],
        keywords_gaap: ['demand loans', 'call loans'],
        keywords_ifrs: ['on-demand borrowings', 'call borrowings']
    },
    {
        id: 'statutory_dues',
        category: 'Balance Sheet - Liabilities',
        key: 'statutory_dues',
        label: 'Statutory Dues',
        keywords_indas: ['statutory dues', 'gst payable', 'tds payable', 'provident fund payable', 'esi payable'],
        keywords_gaap: ['payroll taxes payable', 'sales taxes payable', 'withholding taxes'],
        keywords_ifrs: ['statutory liabilities', 'tax withholdings payable']
    },
    {
        id: 'refund_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'refund_liabilities',
        label: 'Refund Liabilities',
        keywords_indas: ['refund liabilities', 'customer refunds payable', 'sales return provision'],
        keywords_gaap: ['refund liabilities', 'customer refunds', 'returns reserve'],
        keywords_ifrs: ['refund liabilities', 'expected refunds'],
        related_standards: { indas: ['IndAS 115'], gaap: ['ASC 606'], ifrs: ['IFRS 15'] }
    },
    {
        id: 'contract_liabilities',
        category: 'Balance Sheet - Liabilities',
        key: 'contract_liabilities',
        label: 'Contract Liabilities',
        description: 'Obligation to transfer goods/services for consideration received (deferred revenue)',
        keywords_indas: ['contract liabilities', 'advance from customers', 'deferred revenue'],
        keywords_gaap: ['contract liabilities', 'deferred revenue', 'unearned revenue'],
        keywords_ifrs: ['contract liabilities', 'deferred income'],
        related_standards: { indas: ['IndAS 115'], gaap: ['ASC 606'], ifrs: ['IFRS 15'] }
    },
    {
        id: 'interest_accrued_not_due',
        category: 'Balance Sheet - Liabilities',
        key: 'interest_accrued_not_due',
        label: 'Interest Accrued but Not Due',
        keywords_indas: ['interest accrued but not due on borrowings', 'accrued interest'],
        keywords_gaap: ['accrued interest payable'],
        keywords_ifrs: ['interest payable', 'accrued finance costs']
    },
    {
        id: 'interest_accrued_due',
        category: 'Balance Sheet - Liabilities',
        key: 'interest_accrued_due',
        label: 'Interest Accrued and Due',
        keywords_indas: ['interest accrued and due on borrowings', 'overdue interest'],
        keywords_gaap: ['interest payable overdue'],
        keywords_ifrs: ['overdue interest payable']
    },
    {
        id: 'unpaid_dividends',
        category: 'Balance Sheet - Liabilities',
        key: 'unpaid_dividends',
        label: 'Unpaid Dividends',
        keywords_indas: ['unpaid dividends', 'unclaimed dividends'],
        keywords_gaap: ['dividends payable', 'unclaimed dividends'],
        keywords_ifrs: ['dividends payable', 'unpaid dividends']
    },
    {
        id: 'unpaid_matured_deposits',
        category: 'Balance Sheet - Liabilities',
        key: 'unpaid_matured_deposits',
        label: 'Unpaid Matured Deposits',
        keywords_indas: ['unpaid matured deposits', 'unclaimed fixed deposits', 'matured deposits unpaid'],
        keywords_gaap: ['matured term deposits payable'],
        keywords_ifrs: ['matured deposits payable']
    },
    {
        id: 'asset_retirement_obligations',
        category: 'Balance Sheet - Liabilities',
        key: 'asset_retirement_obligations',
        label: 'Asset Retirement Obligations',
        keywords_indas: ['decommissioning provision', 'asset retirement obligation', 'site restoration provision'],
        keywords_gaap: ['asset retirement obligations', 'aro', 'environmental liabilities'],
        keywords_ifrs: ['decommissioning provisions', 'restoration obligations'],
        related_standards: { indas: ['IndAS 37'], gaap: ['ASC 410'], ifrs: ['IAS 37'] }
    }
];

// =============================================================================
// ADDITIONAL EQUITY TERMS
// =============================================================================
export const ADDITIONAL_EQUITY_TERMS: TermMapping[] = [
    {
        id: 'authorised_capital',
        category: 'Balance Sheet - Equity',
        key: 'authorised_capital',
        label: 'Authorised Capital',
        keywords_indas: ['authorised capital', 'authorized capital', 'authorized share capital'],
        keywords_gaap: ['authorized stock', 'authorized shares'],
        keywords_ifrs: ['authorized capital', 'authorized share capital']
    },
    {
        id: 'subscribed_paid_up',
        category: 'Balance Sheet - Equity',
        key: 'subscribed_paid_up',
        label: 'Subscribed and Fully Paid Capital',
        keywords_indas: ['subscribed and fully paid', 'paid up capital', 'issued and paid up'],
        keywords_gaap: ['common stock issued', 'shares outstanding'],
        keywords_ifrs: ['issued capital', 'share capital paid up']
    },
    {
        id: 'share_application_money',
        category: 'Balance Sheet - Equity',
        key: 'share_application_money',
        label: 'Share Application Money Pending Allotment',
        keywords_indas: ['share application money pending allotment', 'share application money'],
        keywords_gaap: ['stock subscriptions receivable'],
        keywords_ifrs: ['share application money', 'amounts received for share issuance']
    },
    {
        id: 'capital_redemption_reserve',
        category: 'Balance Sheet - Equity',
        key: 'capital_redemption_reserve',
        label: 'Capital Redemption Reserve',
        keywords_indas: ['capital redemption reserve', 'crr'],
        keywords_gaap: ['appropriated retained earnings for capital redemption'],
        keywords_ifrs: ['capital redemption reserve']
    },
    {
        id: 'debenture_redemption_reserve',
        category: 'Balance Sheet - Equity',
        key: 'debenture_redemption_reserve',
        label: 'Debenture Redemption Reserve',
        keywords_indas: ['debenture redemption reserve', 'drr'],
        keywords_gaap: ['sinking fund for debentures'],
        keywords_ifrs: ['bond redemption reserve']
    },
    {
        id: 'money_against_warrants',
        category: 'Balance Sheet - Equity',
        key: 'money_against_warrants',
        label: 'Money Received Against Share Warrants',
        keywords_indas: ['money received against share warrants', 'warrant premium received'],
        keywords_gaap: ['warrants outstanding', 'proceeds from warrants'],
        keywords_ifrs: ['share warrant proceeds', 'money received for share warrants']
    },
    {
        id: 'equity_component_compound',
        category: 'Balance Sheet - Equity',
        key: 'equity_component_compound',
        label: 'Equity Component of Compound Financial Instruments',
        keywords_indas: ['equity component of compound financial instruments', 'convertible bond equity component'],
        keywords_gaap: ['beneficial conversion feature', 'equity component of convertible debt'],
        keywords_ifrs: ['equity component of compound instruments'],
        related_standards: { indas: ['IndAS 32'], gaap: ['ASC 470'], ifrs: ['IAS 32'] }
    },
    {
        id: 'additional_paid_in_capital',
        category: 'Balance Sheet - Equity',
        key: 'additional_paid_in_capital',
        label: 'Additional Paid-in Capital (APIC)',
        keywords_indas: ['securities premium', 'share premium account'],
        keywords_gaap: [
            'additional paid-in capital', 'apic', 'paid-in capital in excess of par',
            'capital surplus', 'capital in excess of stated value'
        ],
        keywords_ifrs: ['share premium', 'additional paid-in capital']
    },
    {
        id: 'treasury_stock',
        category: 'Balance Sheet - Equity',
        key: 'treasury_stock',
        label: 'Treasury Stock',
        keywords_indas: ['shares held by subsidiaries', 'treasury shares', 'buy-back shares'],
        keywords_gaap: ['treasury stock', 'treasury shares', 'common stock in treasury'],
        keywords_ifrs: ['treasury shares', 'own shares held']
    },
    {
        id: 'accumulated_deficit',
        category: 'Balance Sheet - Equity',
        key: 'accumulated_deficit',
        label: 'Accumulated Deficit',
        keywords_indas: ['accumulated losses', 'deficit in statement of profit and loss'],
        keywords_gaap: ['accumulated deficit', 'retained deficit'],
        keywords_ifrs: ['accumulated losses', 'deficit']
    }
];

// =============================================================================
// ADDITIONAL OCI TERMS
// =============================================================================
export const ADDITIONAL_OCI_TERMS: TermMapping[] = [
    {
        id: 'cost_of_hedging_reserve',
        category: 'Other Comprehensive Income',
        key: 'cost_of_hedging_reserve',
        label: 'Cost of Hedging Reserve',
        keywords_indas: ['cost of hedging', 'time value of options'],
        keywords_gaap: ['excluded components of hedges'],
        keywords_ifrs: ['cost of hedging reserve', 'time value of options hedges'],
        related_standards: { indas: ['IndAS 109'], ifrs: ['IFRS 9'] }
    },
    {
        id: 'own_credit_risk_changes',
        category: 'Other Comprehensive Income',
        key: 'own_credit_risk_changes',
        label: 'Own Credit Risk Changes',
        description: 'Fair value changes from own credit risk on liabilities at FVTPL',
        keywords_indas: ['changes in own credit risk'],
        keywords_gaap: ['debt valuation adjustment', 'dva', 'own credit adjustment'],
        keywords_ifrs: ['changes in fair value attributable to own credit risk'],
        related_standards: { indas: ['IndAS 109'], gaap: ['ASC 825'], ifrs: ['IFRS 9'] }
    },
    {
        id: 'insurance_finance_oci',
        category: 'Other Comprehensive Income',
        key: 'insurance_finance_oci',
        label: 'Insurance Finance Income/Expenses (OCI)',
        keywords_indas: ['insurance finance income in oci'],
        keywords_gaap: ['insurance contract adjustments'],
        keywords_ifrs: ['insurance finance income or expenses in oci', 'oci disaggregation for insurance'],
        related_standards: { ifrs: ['IFRS 17'] }
    }
];

// =============================================================================
// ADDITIONAL CASH FLOW TERMS
// =============================================================================
export const ADDITIONAL_CASH_FLOW_TERMS: TermMapping[] = [
    {
        id: 'cash_from_royalties_fees',
        category: 'Cash Flow Statement',
        key: 'cash_from_royalties_fees',
        label: 'Cash Receipts from Royalties, Fees, Commissions',
        keywords_indas: ['cash receipts from royalties, fees, commissions and other revenue'],
        keywords_gaap: ['royalty receipts', 'fee income collected'],
        keywords_ifrs: ['cash receipts from royalties and fees']
    },
    {
        id: 'cash_for_futures_contracts',
        category: 'Cash Flow Statement',
        key: 'cash_for_futures_contracts',
        label: 'Cash for Derivative Contracts',
        keywords_indas: ['cash payments for futures contracts', 'cash for forward contracts', 'cash for options'],
        keywords_gaap: ['derivative settlement payments', 'hedging cash payments'],
        keywords_ifrs: ['cash flows from derivative instruments']
    },
    {
        id: 'cash_from_insurance_contracts',
        category: 'Cash Flow Statement',
        key: 'cash_from_insurance_contracts',
        label: 'Cash from Insurance Contracts',
        keywords_indas: ['cash receipts and payments from insurance contracts'],
        keywords_gaap: ['insurance premiums collected', 'claims paid'],
        keywords_ifrs: ['cash flows from insurance contracts held or issued']
    },
    {
        id: 'debt_issuance_costs',
        category: 'Cash Flow Statement',
        key: 'debt_issuance_costs',
        label: 'Debt Issuance Costs',
        keywords_indas: ['share issue expenses', 'debenture issue costs'],
        keywords_gaap: ['debt issuance costs', 'loan origination fees paid'],
        keywords_ifrs: ['transaction costs on borrowings', 'share issuance costs']
    },
    {
        id: 'lease_principal_payments',
        category: 'Cash Flow Statement',
        key: 'lease_principal_payments',
        label: 'Lease Principal Payments',
        keywords_indas: ['payment of lease liabilities', 'principal portion of lease payments'],
        keywords_gaap: ['payments of lease obligations', 'finance lease principal payments'],
        keywords_ifrs: ['cash payments for principal portion of lease liability'],
        related_standards: { indas: ['IndAS 116'], gaap: ['ASC 842'], ifrs: ['IFRS 16'] }
    }
];

// =============================================================================
// DISCLOSURE AND NOTES TERMS
// =============================================================================
export const DISCLOSURE_TERMS: TermMapping[] = [
    {
        id: 'fair_value_level_1',
        category: 'Disclosures',
        key: 'fair_value_level_1',
        label: 'Fair Value Level 1',
        description: 'Quoted prices in active markets for identical assets or liabilities',
        keywords_indas: ['level 1', 'quoted prices in active markets'],
        keywords_gaap: ['level 1 inputs', 'level 1 fair value'],
        keywords_ifrs: ['level 1 of fair value hierarchy'],
        related_standards: { indas: ['IndAS 113'], gaap: ['ASC 820'], ifrs: ['IFRS 13'] }
    },
    {
        id: 'fair_value_level_2',
        category: 'Disclosures',
        key: 'fair_value_level_2',
        label: 'Fair Value Level 2',
        description: 'Observable inputs other than Level 1 quoted prices',
        keywords_indas: ['level 2', 'observable inputs'],
        keywords_gaap: ['level 2 inputs', 'level 2 fair value'],
        keywords_ifrs: ['level 2 of fair value hierarchy'],
        related_standards: { indas: ['IndAS 113'], gaap: ['ASC 820'], ifrs: ['IFRS 13'] }
    },
    {
        id: 'fair_value_level_3',
        category: 'Disclosures',
        key: 'fair_value_level_3',
        label: 'Fair Value Level 3',
        description: 'Unobservable inputs',
        keywords_indas: ['level 3', 'unobservable inputs'],
        keywords_gaap: ['level 3 inputs', 'level 3 fair value'],
        keywords_ifrs: ['level 3 of fair value hierarchy'],
        related_standards: { indas: ['IndAS 113'], gaap: ['ASC 820'], ifrs: ['IFRS 13'] }
    },
    {
        id: 'contingent_liabilities',
        category: 'Disclosures',
        key: 'contingent_liabilities',
        label: 'Contingent Liabilities',
        keywords_indas: ['contingent liabilities', 'claims against company', 'disputed tax matters'],
        keywords_gaap: ['loss contingencies', 'contingent liabilities'],
        keywords_ifrs: ['contingent liabilities', 'possible obligations'],
        related_standards: { indas: ['IndAS 37'], gaap: ['ASC 450'], ifrs: ['IAS 37'] }
    },
    {
        id: 'contingent_assets',
        category: 'Disclosures',
        key: 'contingent_assets',
        label: 'Contingent Assets',
        keywords_indas: ['contingent assets', 'claims receivable'],
        keywords_gaap: ['gain contingencies', 'contingent assets'],
        keywords_ifrs: ['contingent assets', 'possible assets'],
        related_standards: { indas: ['IndAS 37'], gaap: ['ASC 450'], ifrs: ['IAS 37'] }
    },
    {
        id: 'capital_commitments',
        category: 'Disclosures',
        key: 'capital_commitments',
        label: 'Capital Commitments',
        keywords_indas: ['capital commitments', 'estimated capital contracts', 'capital expenditure commitments'],
        keywords_gaap: ['purchase commitments', 'capital expenditure commitments'],
        keywords_ifrs: ['commitments for capital expenditure', 'contractual commitments']
    },
    {
        id: 'related_party_transactions',
        category: 'Disclosures',
        key: 'related_party_transactions',
        label: 'Related Party Transactions',
        keywords_indas: ['related party transactions', 'transactions with related parties', 'key management personnel'],
        keywords_gaap: ['related party transactions', 'transactions with affiliates'],
        keywords_ifrs: ['related party disclosures', 'transactions with related parties'],
        related_standards: { indas: ['IndAS 24'], gaap: ['ASC 850'], ifrs: ['IAS 24'] }
    },
    {
        id: 'events_after_reporting',
        category: 'Disclosures',
        key: 'events_after_reporting',
        label: 'Events After Reporting Period',
        keywords_indas: ['events after reporting period', 'subsequent events', 'events occurring after balance sheet date'],
        keywords_gaap: ['subsequent events', 'events after balance sheet date'],
        keywords_ifrs: ['events after the reporting period', 'adjusting and non-adjusting events'],
        related_standards: { indas: ['IndAS 10'], gaap: ['ASC 855'], ifrs: ['IAS 10'] }
    },
    {
        id: 'credit_risk_exposure',
        category: 'Disclosures',
        key: 'credit_risk_exposure',
        label: 'Credit Risk Exposures',
        keywords_indas: ['credit risk', 'maximum credit exposure', 'credit concentration'],
        keywords_gaap: ['credit risk concentrations', 'credit exposure'],
        keywords_ifrs: ['credit risk exposures', 'maximum exposure to credit risk'],
        related_standards: { indas: ['IndAS 107'], gaap: ['ASC 825'], ifrs: ['IFRS 7'] }
    },
    {
        id: 'liquidity_risk',
        category: 'Disclosures',
        key: 'liquidity_risk',
        label: 'Liquidity Risk',
        keywords_indas: ['liquidity risk', 'maturity analysis of financial liabilities'],
        keywords_gaap: ['liquidity risk', 'contractual maturities'],
        keywords_ifrs: ['liquidity risk', 'maturity analysis'],
        related_standards: { indas: ['IndAS 107'], gaap: ['ASC 825'], ifrs: ['IFRS 7'] }
    }
];

// =============================================================================
// CHANGES IN EQUITY TERMS
// =============================================================================
export const CHANGES_IN_EQUITY_TERMS: TermMapping[] = [
    {
        id: 'opening_balance_equity',
        category: 'Statement of Changes in Equity',
        key: 'opening_balance_equity',
        label: 'Balance at Beginning of Period',
        keywords_indas: ['balance at beginning of period', 'opening balance', 'balance as at'],
        keywords_gaap: ['beginning balance', 'balance at beginning of year'],
        keywords_ifrs: ['balance at start of period', 'opening balance']
    },
    {
        id: 'closing_balance_equity',
        category: 'Statement of Changes in Equity',
        key: 'closing_balance_equity',
        label: 'Balance at End of Period',
        keywords_indas: ['balance at end of period', 'closing balance', 'balance as at end'],
        keywords_gaap: ['ending balance', 'balance at end of year'],
        keywords_ifrs: ['balance at end of period', 'closing balance']
    },
    {
        id: 'restated_balance',
        category: 'Statement of Changes in Equity',
        key: 'restated_balance',
        label: 'Restated Balance',
        keywords_indas: ['restated balance', 'as restated', 'adjusted opening balance'],
        keywords_gaap: ['restated beginning balance', 'as adjusted'],
        keywords_ifrs: ['restated balance at beginning', 'balance after restatement']
    },
    {
        id: 'transfer_to_reserves',
        category: 'Statement of Changes in Equity',
        key: 'transfer_to_reserves',
        label: 'Transfer to Reserves',
        keywords_indas: ['transfer to reserves', 'appropriation to reserves', 'transfer to statutory reserve'],
        keywords_gaap: ['appropriation of retained earnings'],
        keywords_ifrs: ['transfers between reserves', 'appropriations']
    },
    {
        id: 'prior_period_errors',
        category: 'Statement of Changes in Equity',
        key: 'prior_period_errors',
        label: 'Prior Period Errors',
        keywords_indas: ['prior period errors', 'correction of errors', 'prior year adjustments'],
        keywords_gaap: ['error corrections', 'prior period adjustments'],
        keywords_ifrs: ['prior period errors', 'retrospective corrections'],
        related_standards: { indas: ['IndAS 8'], gaap: ['ASC 250'], ifrs: ['IAS 8'] }
    },
    {
        id: 'change_in_accounting_policy',
        category: 'Statement of Changes in Equity',
        key: 'change_in_accounting_policy',
        label: 'Changes in Accounting Policy',
        keywords_indas: ['changes in accounting policies', 'change in accounting policy', 'policy change impact'],
        keywords_gaap: ['change in accounting principle', 'cumulative effect of accounting change'],
        keywords_ifrs: ['changes in accounting policies', 'retrospective application'],
        related_standards: { indas: ['IndAS 8'], gaap: ['ASC 250'], ifrs: ['IAS 8'] }
    },
    {
        id: 'share_based_payment_equity',
        category: 'Statement of Changes in Equity',
        key: 'share_based_payment_equity',
        label: 'Share-based Payment Transactions',
        keywords_indas: ['share-based payment transactions', 'esop expense', 'stock option expense'],
        keywords_gaap: ['stock-based compensation', 'share-based payments'],
        keywords_ifrs: ['share-based payment transactions', 'equity-settled transactions'],
        related_standards: { indas: ['IndAS 102'], gaap: ['ASC 718'], ifrs: ['IFRS 2'] }
    }
];

// =============================================================================
// EXPORT ALL ADDITIONAL TERMS
// =============================================================================
export const ALL_ADDITIONAL_TERMS: TermMapping[] = [
    ...ADDITIONAL_REVENUE_TERMS,
    ...ADDITIONAL_EXPENSE_TERMS,
    ...IFRS18_TERMS,
    ...ADDITIONAL_ASSET_TERMS,
    ...ADDITIONAL_LIABILITY_TERMS,
    ...ADDITIONAL_EQUITY_TERMS,
    ...ADDITIONAL_OCI_TERMS,
    ...ADDITIONAL_CASH_FLOW_TERMS,
    ...DISCLOSURE_TERMS,
    ...CHANGES_IN_EQUITY_TERMS
];
