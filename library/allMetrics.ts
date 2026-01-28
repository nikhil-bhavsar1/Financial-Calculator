// Complete list of all financial metrics organized by category
// Each metric has: id (internal key), label (display name), formula (calculation logic)

export interface FormulaBreakdown {
    step: string;
    formula: string;
    description?: string;
}

export interface MetricDefinition {
    id: string;
    label: string;
    formula: string;
    breakdown?: FormulaBreakdown[];
}

export interface CategoryDefinition {
    category: string;
    metrics: MetricDefinition[];
}

export const ALL_METRIC_DEFINITIONS: CategoryDefinition[] = [
    // ============================================
    // 01 VALUATION RATIOS
    // ============================================
    {
        category: '01 Valuation Ratios',
        metrics: [
            { id: 'calc_pe_ratio', label: 'P/E Ratio', formula: 'Market Price Per Share / Earnings Per Share (EPS)' },
            { id: 'calc_pe_ratio_alt', label: 'P/E Ratio (Alt)', formula: 'Market Capitalization / Net Income' },
            { id: 'calc_book_value_per_share', label: 'Book Value Per Share', formula: 'Total Equity / Shares Outstanding' },
            { id: 'calc_pb_ratio', label: 'P/B Ratio', formula: 'Market Price Per Share / Book Value Per Share' },
            { id: 'calc_revenue_per_share', label: 'Revenue Per Share', formula: 'Total Revenue / Shares Outstanding' },
            { id: 'calc_ps_ratio', label: 'P/S Ratio', formula: 'Market Price Per Share / Revenue Per Share' },
            { id: 'calc_ps_ratio_alt', label: 'P/S Ratio (Alt)', formula: 'Market Capitalization / Total Revenue' },
            { id: 'calc_operating_cf_per_share', label: 'Operating CF Per Share', formula: 'Operating Cash Flow / Shares Outstanding' },
            { id: 'calc_pcf_ratio', label: 'P/CF Ratio', formula: 'Market Price Per Share / Operating Cash Flow Per Share' },
            { id: 'calc_pcf_ratio_alt', label: 'P/CF Ratio (Alt)', formula: 'Market Capitalization / Operating Cash Flow' },
            {
                id: 'calc_peg_ratio',
                label: 'PEG Ratio',
                formula: 'P/E Ratio / Annual EPS Growth Rate (%)',
                breakdown: [
                    {
                        step: 'Calculate P/E Ratio',
                        formula: 'Market Price Per Share / Earnings Per Share',
                        description: 'First, determine the Price-to-Earnings ratio by dividing current stock price by EPS'
                    },
                    {
                        step: 'Determine EPS Growth Rate',
                        formula: '[(Current Year EPS - Prior Year EPS) / Prior Year EPS] × 100',
                        description: 'Calculate the annual earnings growth rate as a percentage'
                    },
                    {
                        step: 'Calculate PEG Ratio',
                        formula: 'P/E Ratio / EPS Growth Rate',
                        description: 'Divide P/E by growth rate. PEG < 1 suggests undervalued, PEG > 1 suggests overvalued relative to growth'
                    }
                ]
            },
            { id: 'calc_earnings_yield', label: 'Earnings Yield', formula: 'Earnings Per Share / Market Price Per Share' },
            { id: 'calc_earnings_yield_alt', label: 'Earnings Yield (Alt)', formula: 'Net Income / Market Capitalization' },
            { id: 'calc_enterprise_value', label: 'Enterprise Value', formula: 'Market Cap + Total Debt + Minority Interest + Preferred Equity - Cash' },
            { id: 'calc_ev_to_ebitda', label: 'EV/EBITDA', formula: 'Enterprise Value / EBITDA' },
            { id: 'calc_ev_to_ebit', label: 'EV/EBIT', formula: 'Enterprise Value / EBIT' },
            { id: 'calc_ev_to_sales', label: 'EV/Sales', formula: 'Enterprise Value / Total Revenue' },
            { id: 'calc_ev_to_fcf', label: 'EV/FCF', formula: 'Enterprise Value / Free Cash Flow' },
            { id: 'calc_tangible_book_value', label: 'Tangible Book Value', formula: 'Total Equity - Intangible Assets - Goodwill' },
            { id: 'calc_tangible_bvps', label: 'Tangible BVPS', formula: 'Tangible Book Value / Shares Outstanding' },
            { id: 'calc_price_to_tangible_bv', label: 'Price/Tangible BV', formula: 'Market Price Per Share / Tangible Book Value Per Share' },
            { id: 'calc_fcf_per_share', label: 'FCF Per Share', formula: 'Free Cash Flow / Shares Outstanding' },
            { id: 'calc_price_to_fcf', label: 'Price/FCF', formula: 'Market Price Per Share / Free Cash Flow Per Share' },
            { id: 'calc_price_to_fcf_alt', label: 'Price/FCF (Alt)', formula: 'Market Capitalization / Free Cash Flow' },
            { id: 'calc_ev_to_revenue', label: 'EV/Revenue', formula: 'Enterprise Value / Total Revenue' },
            { id: 'calc_ev_to_operating_income', label: 'EV/Operating Income', formula: 'Enterprise Value / Operating Income' },
        ]
    },

    // ============================================
    // 02 PROFITABILITY METRICS
    // ============================================
    {
        category: '02 Profitability Metrics',
        metrics: [
            { id: 'calc_net_income', label: 'Net Income', formula: 'Total Revenue - Total Expenses' },
            { id: 'calc_gross_profit', label: 'Gross Profit', formula: 'Total Revenue - Cost of Goods Sold (COGS)' },
            { id: 'calc_operating_income', label: 'Operating Income (EBIT)', formula: 'Gross Profit - Operating Expenses' },
            { id: 'calc_ebitda', label: 'EBITDA', formula: 'Operating Income + Depreciation + Amortization' },
            { id: 'calc_ebitda_alt', label: 'EBITDA (Alt)', formula: 'Net Income + Interest + Taxes + Depreciation + Amortization' },
            { id: 'calc_eps', label: 'Earnings Per Share (EPS)', formula: '(Net Income - Preferred Dividends) / Weighted Average Shares Outstanding' },
            { id: 'calc_diluted_eps', label: 'Diluted EPS', formula: '(Net Income - Preferred Dividends) / (Weighted Avg Shares + Dilutive Securities)' },
            { id: 'calc_gross_margin', label: 'Gross Profit Margin', formula: '(Gross Profit / Total Revenue) × 100' },
            { id: 'calc_gross_margin_alt', label: 'Gross Profit Margin (Alt)', formula: '[(Revenue - COGS) / Revenue] × 100' },
            { id: 'calc_operating_margin', label: 'Operating Margin', formula: '(Operating Income / Total Revenue) × 100' },
            { id: 'calc_operating_margin_alt', label: 'Operating Margin (Alt)', formula: '(EBIT / Revenue) × 100' },
            { id: 'calc_net_profit_margin', label: 'Net Profit Margin', formula: '(Net Income / Total Revenue) × 100' },
            { id: 'calc_ebitda_margin', label: 'EBITDA Margin', formula: '(EBITDA / Total Revenue) × 100' },
            { id: 'calc_roa', label: 'Return on Assets (ROA)', formula: '(Net Income / Average Total Assets) × 100' },
            { id: 'calc_roa_alt', label: 'ROA (Alt)', formula: '(Net Income / Total Assets) × 100' },
            { id: 'calc_roe', label: 'Return on Equity (ROE)', formula: '(Net Income / Average Shareholders Equity) × 100' },
            { id: 'calc_roe_alt', label: 'ROE (Alt)', formula: '(Net Income / Shareholders Equity) × 100' },
            { id: 'calc_roi', label: 'Return on Investment (ROI)', formula: '[(Current Value - Cost of Investment) / Cost of Investment] × 100' },
            { id: 'calc_roi_alt', label: 'ROI (Alt)', formula: '(Net Profit / Total Investment) × 100' },
            { id: 'calc_nopat', label: 'NOPAT', formula: 'EBIT × (1 - Tax Rate)' },
            { id: 'calc_roic', label: 'Return on Invested Capital (ROIC)', formula: '[NOPAT / (Total Debt + Total Equity)] × 100' },
            { id: 'calc_roic_alt', label: 'ROIC (Alt)', formula: 'EBIT(1-t) / Invested Capital' },
            { id: 'calc_roce', label: 'Return on Capital Employed (ROCE)', formula: '[EBIT / (Total Assets - Current Liabilities)] × 100' },
            { id: 'calc_roce_alt', label: 'ROCE (Alt)', formula: 'EBIT / Capital Employed' },
            { id: 'calc_rona', label: 'Return on Net Assets (RONA)', formula: '(Net Income / (Fixed Assets + Net Working Capital)) × 100' },
            { id: 'calc_pre_tax_margin', label: 'Pre-Tax Profit Margin', formula: '(Earnings Before Tax / Total Revenue) × 100' },
            { id: 'calc_after_tax_margin', label: 'After-Tax Margin', formula: '(Net Income After Tax / Total Revenue) × 100' },
            { id: 'calc_cash_roa', label: 'Cash Return on Assets', formula: '(Operating Cash Flow / Average Total Assets) × 100' },
            { id: 'calc_cash_roe', label: 'Cash Return on Equity', formula: '(Operating Cash Flow / Average Shareholders Equity) × 100' },
        ]
    },

    // ============================================
    // 03 CASH FLOW METRICS
    // ============================================
    {
        category: '03 Cash Flow Metrics',
        metrics: [
            { id: 'calc_ocf', label: 'Operating Cash Flow (OCF)', formula: 'Net Income + Non-Cash Expenses + Changes in Working Capital' },
            { id: 'calc_ocf_alt', label: 'OCF (Alt)', formula: 'EBITDA - Taxes Paid - Change in Net Working Capital' },
            { id: 'calc_fcf', label: 'Free Cash Flow (FCF)', formula: 'Operating Cash Flow - Capital Expenditures' },
            { id: 'calc_fcfe', label: 'Free Cash Flow to Equity (FCFE)', formula: 'Net Income - (CapEx - Depreciation) - Change in NWC + (New Debt - Debt Repayment)' },
            { id: 'calc_fcfe_alt', label: 'FCFE (Alt)', formula: 'OCF - CapEx + Net Borrowing' },
            { id: 'calc_fcff', label: 'Free Cash Flow to Firm (FCFF)', formula: 'EBIT(1 - Tax Rate) + Depreciation - CapEx - Change in NWC' },
            { id: 'calc_fcff_alt1', label: 'FCFF (Alt 1)', formula: 'NOPAT + Depreciation - CapEx - Change in NWC' },
            { id: 'calc_fcff_alt2', label: 'FCFF (Alt 2)', formula: 'CFO + Interest Expense(1 - Tax Rate) - CapEx' },
            { id: 'calc_cf_per_share', label: 'Cash Flow Per Share', formula: 'Operating Cash Flow / Shares Outstanding' },
            { id: 'calc_cf_per_share_alt', label: 'Cash Flow Per Share (Alt)', formula: 'Free Cash Flow / Shares Outstanding' },
            { id: 'calc_fcf_margin', label: 'Free Cash Flow Margin', formula: '(Free Cash Flow / Total Revenue) × 100' },
            { id: 'calc_cf_to_debt', label: 'Cash Flow-to-Debt Ratio', formula: 'Operating Cash Flow / Total Debt' },
            { id: 'calc_ocf_ratio', label: 'Operating Cash Flow Ratio', formula: 'Operating Cash Flow / Current Liabilities' },
            { id: 'calc_gross_cf', label: 'Gross Cash Flow', formula: 'EBITDA - Cash Taxes' },
            { id: 'calc_cfroi', label: 'Cash Flow Return on Investment (CFROI)', formula: '[Gross Cash Flow / Gross Investment] × 100' },
            { id: 'calc_unlevered_fcf', label: 'Unlevered Free Cash Flow', formula: 'EBIT(1 - Tax Rate) + Depreciation - CapEx - Change in NWC' },
            { id: 'calc_levered_fcf', label: 'Levered Free Cash Flow', formula: 'Net Income + Depreciation - CapEx - Change in NWC - Debt Repayment + New Debt' },
            { id: 'calc_owner_earnings', label: 'Owner Earnings', formula: 'Net Income + Depreciation & Amortization - CapEx - Additional Working Capital' },
        ]
    },

    // ============================================
    // 04 LIQUIDITY METRICS
    // ============================================
    {
        category: '04 Liquidity Metrics',
        metrics: [
            { id: 'calc_current_ratio', label: 'Current Ratio', formula: 'Current Assets / Current Liabilities' },
            { id: 'calc_quick_ratio', label: 'Quick Ratio (Acid-Test)', formula: '(Current Assets - Inventory) / Current Liabilities' },
            { id: 'calc_quick_ratio_alt', label: 'Quick Ratio (Alt)', formula: '(Cash + Marketable Securities + Accounts Receivable) / Current Liabilities' },
            { id: 'calc_cash_ratio', label: 'Cash Ratio', formula: '(Cash + Cash Equivalents) / Current Liabilities' },
            { id: 'calc_working_capital', label: 'Working Capital', formula: 'Current Assets - Current Liabilities' },
            { id: 'calc_nwc_ratio', label: 'Net Working Capital Ratio', formula: '(Current Assets - Current Liabilities) / Total Assets' },
            { id: 'calc_daily_opex', label: 'Daily Operating Expenses', formula: 'Annual Operating Expenses / 365' },
            { id: 'calc_defensive_interval', label: 'Defensive Interval Ratio', formula: '(Cash + Marketable Securities + Accounts Receivable) / Daily Operating Expenses' },
            { id: 'calc_cf_coverage', label: 'Cash Flow Coverage Ratio', formula: 'Operating Cash Flow / Total Debt' },
            { id: 'calc_ocf_to_cl', label: 'OCF to Current Liabilities', formula: 'Operating Cash Flow / Current Liabilities' },
        ]
    },

    // ============================================
    // 05 LEVERAGE & SOLVENCY METRICS
    // ============================================
    {
        category: '05 Leverage/Solvency Metrics',
        metrics: [
            { id: 'calc_debt_to_equity', label: 'Debt-to-Equity Ratio', formula: 'Total Debt / Total Shareholders Equity' },
            { id: 'calc_debt_to_assets', label: 'Debt-to-Assets Ratio', formula: 'Total Debt / Total Assets' },
            { id: 'calc_debt_to_ebitda', label: 'Debt-to-EBITDA Ratio', formula: 'Total Debt / EBITDA' },
            { id: 'calc_interest_coverage', label: 'Interest Coverage Ratio', formula: 'EBIT / Interest Expense' },
            { id: 'calc_dscr', label: 'Debt Service Coverage Ratio (DSCR)', formula: 'Net Operating Income / Total Debt Service' },
            { id: 'calc_equity_multiplier', label: 'Equity Multiplier', formula: 'Total Assets / Total Shareholders Equity' },
            { id: 'calc_financial_leverage', label: 'Financial Leverage Ratio', formula: 'Total Assets / Total Equity' },
            { id: 'calc_total_debt_ratio', label: 'Total Debt Ratio', formula: 'Total Debt / Total Assets' },
            { id: 'calc_ltd_to_equity', label: 'Long-term Debt to Equity', formula: 'Long-term Debt / Total Shareholders Equity' },
            { id: 'calc_fixed_charge_coverage', label: 'Fixed Charge Coverage Ratio', formula: '(EBIT + Fixed Charges) / (Fixed Charges + Interest Expense)' },
            { id: 'calc_tie', label: 'Times Interest Earned (TIE)', formula: 'EBIT / Interest Expense' },
            { id: 'calc_debt_to_capital', label: 'Debt-to-Capital Ratio', formula: 'Total Debt / (Total Debt + Total Equity)' },
            { id: 'calc_net_debt_to_ebitda', label: 'Net Debt-to-EBITDA', formula: '(Total Debt - Cash & Cash Equivalents) / EBITDA' },
            { id: 'calc_net_debt_to_equity', label: 'Net Debt-to-Equity', formula: '(Total Debt - Cash & Cash Equivalents) / Total Equity' },
            { id: 'calc_capitalization_ratio', label: 'Capitalization Ratio', formula: 'Long-term Debt / (Long-term Debt + Shareholders Equity)' },
        ]
    },

    // ============================================
    // 06 EFFICIENCY & ACTIVITY METRICS
    // ============================================
    {
        category: '06 Efficiency/Activity Metrics',
        metrics: [
            { id: 'calc_asset_turnover', label: 'Asset Turnover Ratio', formula: 'Net Sales / Average Total Assets' },
            { id: 'calc_inventory_turnover', label: 'Inventory Turnover Ratio', formula: 'Cost of Goods Sold / Average Inventory' },
            { id: 'calc_receivables_turnover', label: 'Receivables Turnover Ratio', formula: 'Net Credit Sales / Average Accounts Receivable' },
            { id: 'calc_dso', label: 'Days Sales Outstanding (DSO)', formula: '(Accounts Receivable / Total Credit Sales) × 365' },
            { id: 'calc_dio', label: 'Days Inventory Outstanding (DIO)', formula: '(Average Inventory / COGS) × 365' },
            { id: 'calc_dpo', label: 'Days Payable Outstanding (DPO)', formula: '(Accounts Payable / COGS) × 365' },
            { id: 'calc_ccc', label: 'Cash Conversion Cycle (CCC)', formula: 'DSO + DIO - DPO' },
            { id: 'calc_payables_turnover', label: 'Payables Turnover Ratio', formula: 'COGS / Average Accounts Payable' },
            { id: 'calc_fixed_asset_turnover', label: 'Fixed Asset Turnover', formula: 'Net Sales / Net Fixed Assets' },
            { id: 'calc_total_asset_turnover', label: 'Total Asset Turnover', formula: 'Net Sales / Average Total Assets' },
            { id: 'calc_wc_turnover', label: 'Working Capital Turnover', formula: 'Net Sales / Average Working Capital' },
            { id: 'calc_capital_employed', label: 'Capital Employed', formula: 'Total Assets - Current Liabilities' },
            { id: 'calc_ce_turnover', label: 'Capital Employed Turnover', formula: 'Revenue / Capital Employed' },
            { id: 'calc_nwc_turnover', label: 'Net Working Capital Turnover', formula: 'Revenue / Net Working Capital' },
            { id: 'calc_equity_turnover', label: 'Equity Turnover', formula: 'Revenue / Average Shareholders Equity' },
        ]
    },

    // ============================================
    // 07 GROWTH METRICS
    // ============================================
    {
        category: '07 Growth Metrics',
        metrics: [
            { id: 'calc_revenue_growth', label: 'Revenue Growth Rate', formula: '[(Current Period Revenue - Previous Period Revenue) / Previous Period Revenue] × 100' },
            { id: 'calc_earnings_growth', label: 'Earnings Growth Rate', formula: '[(Current Period Earnings - Previous Period Earnings) / Previous Period Earnings] × 100' },
            { id: 'calc_eps_growth', label: 'EPS Growth Rate', formula: '[(Current EPS - Previous EPS) / Previous EPS] × 100' },
            { id: 'calc_cagr', label: 'Compound Annual Growth Rate (CAGR)', formula: '[(Ending Value / Beginning Value)^(1/Number of Years) - 1] × 100' },
            { id: 'calc_yoy_growth', label: 'Year-over-Year (YoY) Growth', formula: '[(Current Year Value - Previous Year Value) / Previous Year Value] × 100' },
            { id: 'calc_qoq_growth', label: 'Quarter-over-Quarter (QoQ) Growth', formula: '[(Current Quarter Value - Previous Quarter Value) / Previous Quarter Value] × 100' },
            { id: 'calc_sgr', label: 'Sustainable Growth Rate (SGR)', formula: 'ROE × (1 - Dividend Payout Ratio)' },
            { id: 'calc_retention_ratio', label: 'Retention Ratio', formula: '1 - Dividend Payout Ratio' },
            { id: 'calc_internal_growth_rate', label: 'Internal Growth Rate', formula: '(ROA × Retention Ratio) / (1 - ROA × Retention Ratio)' },
            { id: 'calc_dividend_growth', label: 'Dividend Growth Rate', formula: '[(Current Dividend - Previous Dividend) / Previous Dividend] × 100' },
            { id: 'calc_bv_growth', label: 'Book Value Growth Rate', formula: '[(Current Book Value - Previous Book Value) / Previous Book Value] × 100' },
        ]
    },

    // ============================================
    // 08 MARKET METRICS
    // ============================================
    {
        category: '08 Market Metrics',
        metrics: [
            { id: 'calc_market_cap', label: 'Market Capitalization', formula: 'Current Stock Price × Total Shares Outstanding' },
            { id: 'calc_book_value', label: 'Book Value', formula: 'Total Assets - Total Liabilities - Preferred Stock' },
            { id: 'calc_market_value', label: 'Market Value', formula: 'Current Market Price × Number of Units' },
            { id: 'calc_market_share', label: 'Market Share', formula: '(Company Sales / Total Industry Sales) × 100' },
            { id: 'calc_tam', label: 'Total Addressable Market (TAM)', formula: 'Annual Market Demand × Average Selling Price' },
            { id: 'calc_float', label: 'Float', formula: 'Shares Outstanding - Restricted Shares - Insider Holdings' },
            { id: 'calc_shares_outstanding', label: 'Shares Outstanding', formula: 'Issued Shares - Treasury Shares' },
            { id: 'calc_institutional_ownership', label: 'Institutional Ownership %', formula: '(Shares Held by Institutions / Total Shares Outstanding) × 100' },
        ]
    },

    // ============================================
    // 09 DIVIDEND METRICS
    // ============================================
    {
        category: '09 Dividend Metrics',
        metrics: [
            { id: 'calc_dividend_yield', label: 'Dividend Yield', formula: '(Annual Dividends Per Share / Current Stock Price) × 100' },
            { id: 'calc_dividend_payout', label: 'Dividend Payout Ratio', formula: '(Dividends Per Share / Earnings Per Share) × 100' },
            { id: 'calc_dividend_coverage', label: 'Dividend Coverage Ratio', formula: 'Earnings Per Share / Dividends Per Share' },
            { id: 'calc_dps', label: 'Dividend Per Share (DPS)', formula: 'Total Dividends Paid / Number of Shares Outstanding' },
            { id: 'calc_plowback_ratio', label: 'Retention Ratio (Plowback)', formula: '1 - Dividend Payout Ratio' },
            { id: 'calc_cash_dividend_payout', label: 'Cash Dividend Payout Ratio', formula: 'Cash Dividends Paid / Operating Cash Flow' },
        ]
    },

    // ============================================
    // 10 DUPONT ANALYSIS
    // ============================================
    {
        category: '10 DuPont Analysis Components',
        metrics: [
            { id: 'calc_dupont_3step', label: '3-Step DuPont ROE', formula: 'Net Profit Margin × Asset Turnover × Equity Multiplier' },
            {
                id: 'calc_dupont_5step',
                label: '5-Step DuPont ROE',
                formula: 'Tax Burden × Interest Burden × EBIT Margin × Asset Turnover × Equity Multiplier',
                breakdown: [
                    {
                        step: 'Tax Burden',
                        formula: 'Net Income / Pretax Income',
                        description: 'Shows percentage of pretax income retained after taxes'
                    },
                    {
                        step: 'Interest Burden',
                        formula: 'Pretax Income / EBIT',
                        description: 'Shows operating efficiency before interest'
                    },
                    {
                        step: 'EBIT Margin',
                        formula: 'EBIT / Revenue',
                        description: 'Operating profit as percentage of revenue'
                    },
                    {
                        step: 'Asset Turnover',
                        formula: 'Revenue / Total Assets',
                        description: 'Efficiency of asset utilization'
                    },
                    {
                        step: 'Equity Multiplier',
                        formula: 'Total Assets / Shareholders Equity',
                        description: 'Financial leverage multiplier'
                    }
                ]
            },
            { id: 'calc_tax_burden', label: 'Tax Burden', formula: 'Net Income / Pretax Income' },
            { id: 'calc_interest_burden', label: 'Interest Burden', formula: 'Pretax Income / EBIT' },
            { id: 'calc_ebit_margin', label: 'EBIT Margin', formula: 'EBIT / Revenue' },
        ]
    },

    // ============================================
    // 11 STATISTICAL METRICS
    // ============================================
    {
        category: '11 Statistical Metrics',
        metrics: [
            { id: 'calc_sample_variance', label: 'Sample Variance (s²)', formula: 'Σ(xi - x̄)² / (n - 1)' },
            { id: 'calc_population_variance', label: 'Population Variance (σ²)', formula: 'Σ(xi - μ)² / N' },
            { id: 'calc_portfolio_variance', label: 'Portfolio Variance (Two Assets)', formula: 'w₁²σ₁² + w₂²σ₂² + 2w₁w₂Cov(1,2)' },
            { id: 'calc_sample_std', label: 'Sample Standard Deviation (s)', formula: '√[Σ(xi - x̄)² / (n - 1)]' },
            { id: 'calc_population_std', label: 'Population Standard Deviation (σ)', formula: '√[Σ(xi - μ)² / N]' },
            { id: 'calc_volatility', label: 'Returns Standard Deviation (Volatility)', formula: '√[Σ(Ri - R̄)² / (n - 1)]' },
            { id: 'calc_sample_covariance', label: 'Sample Covariance', formula: 'Cov(X,Y) = Σ[(xi - x̄)(yi - ȳ)] / (n - 1)' },
            { id: 'calc_population_covariance', label: 'Population Covariance', formula: 'Cov(X,Y) = Σ[(xi - μx)(yi - μy)] / N' },
            { id: 'calc_correlation', label: 'Correlation Coefficient (Pearson r)', formula: 'r = Cov(X,Y) / (σx × σy)' },
            { id: 'calc_cv', label: 'Coefficient of Variation', formula: '(Standard Deviation / Mean) × 100' },
            { id: 'calc_beta', label: 'Beta', formula: 'β = Cov(Ri, Rm) / Var(Rm)' },
            { id: 'calc_beta_alt', label: 'Beta (Alt)', formula: 'β = (Correlation × σi) / σm' },
            { id: 'calc_sharpe', label: 'Sharpe Ratio', formula: '(Rp - Rf) / σp' },
            { id: 'calc_treynor', label: 'Treynor Ratio', formula: '(Rp - Rf) / βp' },
            { id: 'calc_information_ratio', label: 'Information Ratio', formula: '(Rp - Rb) / Tracking Error' },
            { id: 'calc_sortino', label: 'Sortino Ratio', formula: '(Rp - Rf) / Downside Deviation' },
            { id: 'calc_var', label: 'Parametric VaR', formula: 'VaR = Portfolio Value × z-score × σ × √t' },
            { id: 'calc_arithmetic_mean', label: 'Arithmetic Mean', formula: 'x̄ = Σxi / n' },
            { id: 'calc_weighted_avg', label: 'Weighted Average', formula: 'x̄w = Σ(wi × xi) / Σwi' },
            { id: 'calc_geometric_mean', label: 'Geometric Mean (Returns)', formula: '[(1 + R₁) × (1 + R₂) × ... × (1 + Rn)]^(1/n) - 1' },
        ]
    },

    // ============================================
    // 12 DCF VALUATION
    // ============================================
    {
        category: '12 Complete DCF Valuation Framework',
        metrics: [
            { id: 'calc_fcff_full', label: 'FCFF (Full)', formula: 'EBIT(1 - Tax Rate) + Depreciation - CapEx - Change in NWC' },
            { id: 'calc_fcff_from_nopat', label: 'FCFF from NOPAT', formula: 'NOPAT + Depreciation - CapEx - Change in NWC' },
            { id: 'calc_fcff_from_cfo', label: 'FCFF from CFO', formula: 'CFO + Interest Expense(1 - Tax Rate) - CapEx' },
            { id: 'calc_fcff_from_ni', label: 'FCFF from Net Income', formula: 'Net Income + Interest(1 - Tax Rate) + Depreciation - CapEx - Change in NWC' },
            { id: 'calc_wacc', label: 'WACC', formula: '(E/V × Re) + (D/V × Rd × (1 - Tc))' },
            { id: 'calc_cost_of_equity', label: 'Cost of Equity (CAPM)', formula: 'Re = Rf + β × (Rm - Rf)' },
            { id: 'calc_terminal_value_ggm', label: 'Terminal Value (Gordon Growth)', formula: 'TV = FCFFn+1 / (WACC - g)' },
            { id: 'calc_terminal_value_exit', label: 'Terminal Value (Exit Multiple)', formula: 'TV = EV/EBITDA multiple × EBITDAn' },
            { id: 'calc_terminal_value_pe', label: 'Terminal Value (P/E)', formula: 'TV = P/E multiple × Earningsn' },
            { id: 'calc_pv_fcff', label: 'PV of FCFF', formula: 'PV of FCFF = FCFF₁/(1+WACC)¹ + FCFF₂/(1+WACC)² + ... + FCFFn/(1+WACC)ⁿ' },
            { id: 'calc_pv_terminal', label: 'PV of Terminal Value', formula: 'PV of TV = TV / (1 + WACC)ⁿ' },
            { id: 'calc_ev_dcf', label: 'Enterprise Value (DCF)', formula: 'Enterprise Value = PV of FCFF + PV of Terminal Value' },
            { id: 'calc_equity_value', label: 'Equity Value', formula: 'Equity Value = Enterprise Value - Net Debt - Preferred Stock + Non-Operating Assets' },
            { id: 'calc_net_debt', label: 'Net Debt', formula: 'Net Debt = Total Debt - Cash and Cash Equivalents' },
            { id: 'calc_fair_value_per_share', label: 'Fair Value Per Share', formula: 'Fair Value Per Share = Equity Value / Shares Outstanding' },
            { id: 'calc_fcfe_full', label: 'FCFE (Full)', formula: 'FCFE = Net Income - (CapEx - Depreciation) - Change in NWC + (New Debt - Debt Repayment)' },
            { id: 'calc_fcfe_from_fcff', label: 'FCFE from FCFF', formula: 'FCFE = FCFF - Interest(1 - Tax Rate) + Net Borrowing' },
            { id: 'calc_pv_fcfe', label: 'PV of FCFE', formula: 'PV of FCFE = FCFE₁/(1+Re)¹ + FCFE₂/(1+Re)² + ... + FCFEn/(1+Re)ⁿ' },
            { id: 'calc_terminal_fcfe_ggm', label: 'Terminal Value FCFE (Gordon)', formula: 'TV = FCFEn+1 / (Re - g)' },
            { id: 'calc_ddm_ggm', label: 'Gordon Growth DDM', formula: 'P₀ = D₁ / (Re - g)' },
            { id: 'calc_dividend_next', label: 'Expected Dividend Next Year', formula: 'D₁ = D₀(1 + g)' },
            { id: 'calc_apv', label: 'Adjusted Present Value (APV)', formula: 'APV = Unlevered Firm Value + PV of Tax Shield - PV of Financial Distress Costs' },
        ]
    },

    // ============================================
    // 13 OTHER KEY METRICS
    // ============================================
    {
        category: '13 Other Key Metrics',
        metrics: [
            { id: 'calc_eva', label: 'Economic Value Added (EVA)', formula: 'NOPAT - (WACC × Invested Capital)' },
            { id: 'calc_eva_roic', label: 'EVA (ROIC Version)', formula: '(ROIC - WACC) × Invested Capital' },
            { id: 'calc_mva', label: 'Market Value Added (MVA)', formula: 'Market Value of Firm - Invested Capital' },
            { id: 'calc_sva', label: 'Shareholder Value Added (SVA)', formula: '(Return on Investment - Cost of Capital) × Invested Capital' },
            { id: 'calc_altman_z', label: 'Altman Z-Score', formula: 'Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E' },
            { id: 'calc_piotroski_f', label: 'Piotroski F-Score', formula: 'Sum of 9 binary signals for financial strength' },
            { id: 'calc_beneish_m', label: 'Beneish M-Score', formula: 'M = -4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI + ...' },
            { id: 'calc_jensens_alpha', label: "Jensen's Alpha", formula: 'αi = Ri - [Rf + βi(Rm - Rf)]' },
            { id: 'calc_tobins_q', label: "Tobin's Q Ratio", formula: 'Market Value of Firm / Replacement Cost of Assets' },
            { id: 'calc_tobins_q_alt', label: "Tobin's Q (Alt)", formula: '(Market Cap + Total Debt) / Total Assets' },
            { id: 'calc_earnings_quality', label: 'Earnings Quality Ratio', formula: 'Operating Cash Flow / Net Income' },
            { id: 'calc_accruals_ratio', label: 'Accruals Ratio', formula: '(Net Income - Operating Cash Flow) / Total Assets' },
        ]
    },

    // ============================================
    // 14 DAMODARAN VALUATION
    // ============================================
    {
        category: '14 Aswath Damodaran Valuation Formulas',
        metrics: [
            { id: 'calc_cost_equity_capm', label: 'Cost of Equity (CAPM)', formula: 'Re = Rf + β × ERP' },
            { id: 'calc_cost_equity_multifactor', label: 'Cost of Equity (Multi-Factor)', formula: 'Re = Rf + β₁(Factor 1 Premium) + β₂(Factor 2 Premium) + ...' },
            { id: 'calc_cost_equity_buildup', label: 'Cost of Equity (Build-Up)', formula: 'Re = Rf + Equity Risk Premium + Size Premium + Industry Risk Premium + Company Risk' },
            { id: 'calc_cost_of_debt', label: 'Cost of Debt', formula: 'Rd = Interest Expense / Average Debt Outstanding' },
            { id: 'calc_after_tax_cod', label: 'After-Tax Cost of Debt', formula: 'Rd(after-tax) = Rd × (1 - Tax Rate)' },
            { id: 'calc_wacc_complete', label: 'WACC (Complete)', formula: 'WACC = (E/V)×Re + (D/V)×Rd×(1-T) + (P/V)×Rp' },
            { id: 'calc_levered_beta', label: 'Levered Beta', formula: 'βL = βU × [1 + (1 - T) × (D/E)]' },
            { id: 'calc_unlevered_beta', label: 'Unlevered Beta', formula: 'βU = βL / [1 + (1 - T) × (D/E)]' },
            { id: 'calc_adjusted_beta', label: 'Adjusted Beta (Bloomberg)', formula: 'Adjusted β = (0.67 × Raw β) + (0.33 × 1.0)' },
            { id: 'calc_bottom_up_beta', label: 'Bottom-Up Beta', formula: 'βFirm = Σ(Segment Weightᵢ × βUnlevered,i) × [1 + (1-T) × (D/E)]' },
            { id: 'calc_country_risk_premium', label: 'Country Risk Premium', formula: 'CRP = Country Default Spread × (σEquity,Country / σBond,Country)' },
            { id: 'calc_total_coe_country', label: 'Total Cost of Equity (w/Country Risk)', formula: 'Re = Rf + β × Mature Market ERP + Country Risk Premium' },
            { id: 'calc_fundamental_growth_equity', label: 'Fundamental Growth Rate (Equity)', formula: 'g = ROE × Retention Ratio' },
            { id: 'calc_fundamental_growth_firm', label: 'Fundamental Growth Rate (Firm)', formula: 'g = Return on Capital × Reinvestment Rate' },
            { id: 'calc_reinvestment_rate_firm', label: 'Reinvestment Rate (Firm)', formula: 'Reinvestment Rate = (CapEx - Depreciation + ΔWC) / EBIT(1-T)' },
            { id: 'calc_justified_pe', label: 'Justified P/E', formula: 'P/E = Payout Ratio × (1 + g) / (Re - g)' },
            { id: 'calc_justified_pb', label: 'Justified P/B', formula: 'P/B = (ROE - g) / (Re - g)' },
            { id: 'calc_justified_ps', label: 'Justified P/S', formula: 'P/S = [Profit Margin × Payout Ratio × (1+g)] / (Re - g)' },
            { id: 'calc_justified_ev_ebitda', label: 'Justified EV/EBITDA', formula: 'EV/EBITDA = [(1-T) × (1 - Reinvestment Rate) × (1+g)] / (WACC - g)' },
            { id: 'calc_justified_ev_sales', label: 'Justified EV/Sales', formula: 'EV/Sales = [Operating Margin × (1-T) × (1 - Reinvestment Rate) × (1+g)] / (WACC - g)' },
            { id: 'calc_peg_damodaran', label: 'PEG Ratio (Damodaran)', formula: 'PEG = P/E / Expected Growth Rate' },
            { id: 'calc_bs_call', label: 'Black-Scholes Call Option', formula: 'C = S₀N(d₁) - Ke^(-rT)N(d₂)' },
            { id: 'calc_bs_put', label: 'Black-Scholes Put Option', formula: 'P = Ke^(-rT)N(-d₂) - S₀N(-d₁)' },
            { id: 'calc_lack_marketability', label: 'Lack of Marketability Discount', formula: 'Adjusted Value = Base Value × (1 - Discount)' },
            { id: 'calc_control_premium', label: 'Control Premium', formula: 'Value with Control = Minority Value × (1 + Premium)' },
        ]
    },

    // ============================================
    // 15 GRAHAM FORMULAS
    // ============================================
    {
        category: '15 Benjamin Graham Formulas',
        metrics: [
            { id: 'calc_graham_number', label: 'Graham Number', formula: '√(22.5 × EPS × BVPS)' },
            { id: 'calc_graham_iv_original', label: 'Graham Intrinsic Value (1962)', formula: 'Intrinsic Value = EPS × (8.5 + 2g)' },
            { id: 'calc_graham_iv_revised', label: 'Graham Intrinsic Value (1974)', formula: 'Intrinsic Value = [EPS × (8.5 + 2g) × 4.4] / Y' },
            { id: 'calc_ncav_per_share', label: 'NCAV Per Share', formula: 'NCAV = (Current Assets - Total Liabilities) / Shares Outstanding' },
            { id: 'calc_net_net_wc', label: 'Net-Net Working Capital', formula: 'Net-Net = (Current Assets - Total Liabilities) - (0.5 × Inventory)' },
            { id: 'calc_mos_percentage', label: 'Margin of Safety (%)', formula: 'MOS = [(Intrinsic Value - Market Price) / Intrinsic Value] × 100' },
            { id: 'calc_mos_33', label: "Graham's 33% MOS", formula: 'Market Price ≤ (0.67 × Intrinsic Value)' },
            { id: 'calc_mos_50', label: "Graham's 50% MOS", formula: 'Market Price ≤ (0.50 × Intrinsic Value)' },
            { id: 'calc_liquidation_value', label: 'Liquidation Value Per Share', formula: '(Current Assets - Total Liabilities - Preferred Stock) / Common Shares' },
            { id: 'calc_bvps_tangible', label: 'Tangible Book Value Per Share', formula: '(Total Equity - Intangible Assets - Goodwill) / Shares Outstanding' },
            { id: 'calc_epv', label: 'Earnings Power Value (EPV)', formula: 'EPV = Adjusted Earnings / Required Rate of Return' },
            { id: 'calc_nwc', label: 'Net Working Capital', formula: 'NWC = Current Assets - Current Liabilities' },
            { id: 'calc_wc_ratio', label: 'Working Capital Ratio', formula: 'WC Ratio = (Current Assets - Current Liabilities) / Total Assets' },
            { id: 'calc_graham_central_value', label: "Graham's Central Value", formula: 'Value = Assets + (Multiplier × Earning Power)' },
        ]
    },

    // ============================================
    // 16 MODERN VALUE INVESTING
    // ============================================
    {
        category: '16 Modern Value Investing Additions',
        metrics: [
            { id: 'calc_owner_earnings_buffett', label: "Owner Earnings (Buffett's)", formula: 'Owner Earnings = Net Income + D&A + Other Non-Cash Charges - Avg Annual CapEx - Additional WC' },
            { id: 'calc_look_through_earnings', label: 'Look-Through Earnings', formula: 'Look-Through = Reported Earnings + Share of Undistributed Earnings from Investees' },
            { id: 'calc_iv_growth_rate', label: 'Intrinsic Value Growth Rate', formula: 'Growth Rate = (1 - Dividend Payout Ratio) × Return on Retained Earnings' },
            { id: 'calc_return_spread', label: 'Return Spread (Moat Indicator)', formula: 'Return Spread = ROIC - WACC' },
            { id: 'calc_rotc', label: 'Return on Tangible Capital', formula: 'ROTC = NOPAT / (Net Working Capital + Net Fixed Assets)' },
            { id: 'calc_magic_earnings_yield', label: 'Magic Formula Earnings Yield', formula: 'Earnings Yield = EBIT / Enterprise Value' },
            { id: 'calc_magic_roc', label: 'Magic Formula Return on Capital', formula: 'ROC = EBIT / (Net Working Capital + Net Fixed Assets)' },
            { id: 'calc_acquirers_multiple', label: "Acquirer's Multiple", formula: "Acquirer's Multiple = Enterprise Value / Operating Earnings" },
            { id: 'calc_shareholder_yield', label: 'Shareholder Yield', formula: 'Shareholder Yield = (Dividends + Buybacks - Share Issuance) / Market Cap' },
            { id: 'calc_net_payout_yield', label: 'Net Payout Yield', formula: 'Net Payout = (Dividends + Net Buybacks) / Market Cap' },
            { id: 'calc_total_payout_yield', label: 'Total Payout Yield', formula: 'Total Payout = (Dividends + Buybacks + Debt Reduction) / Market Cap' },
            { id: 'calc_gross_profitability', label: 'Gross Profitability', formula: 'Gross Profitability = (Revenue - COGS) / Total Assets' },
            { id: 'calc_asset_growth', label: 'Asset Growth (Red Flag)', formula: 'Asset Growth = (Current Total Assets - Prior Total Assets) / Prior Total Assets' },
            { id: 'calc_accruals_quality', label: 'Accrual Ratio (Quality)', formula: 'Accruals = (Net Income - Operating Cash Flow) / Average Total Assets' },
            { id: 'calc_altman_z_private', label: 'Altman Z-Score (Private)', formula: "Z' = 0.717A + 0.847B + 3.107C + 0.420D + 0.998E" },
            { id: 'calc_normalized_earnings', label: 'Normalized Earnings', formula: 'Normalized = Average earnings over full business cycle (7-10 years)' },
            { id: 'calc_shiller_pe', label: 'Shiller P/E (CAPE)', formula: 'CAPE = Price / 10-Year Average Inflation-Adjusted Earnings' },
            { id: 'calc_graham_dodd_pe', label: 'Graham & Dodd P/E', formula: 'G&D P/E = Current Price / Average 10-Year Earnings' },
            { id: 'calc_4_factor_value', label: '4-Factor Value Score', formula: 'Score = Rank(P/E) + Rank(P/B) + Rank(P/S) + Rank(Dividend Yield)' },
            { id: 'calc_6_factor_quality', label: '6-Factor Quality Value', formula: 'Score = Rank(P/E) + Rank(P/B) + Rank(EV/EBIT) + Rank(ROE) + Rank(ROA) + Rank(ROIC)' },
            { id: 'calc_value_composite', label: "Value Composite (O'Shaughnessy)", formula: 'Value Composite = Average Percentile of: P/B, P/E, P/S, P/CF, EV/EBITDA, Shareholder Yield' },
            { id: 'calc_ohlson_o', label: 'Ohlson O-Score', formula: 'O = -1.32 - 0.407×SIZE + 6.03×TLTA - 1.43×WCTA + 0.076×CLCA - 1.72×OENEG - ...' },
            { id: 'calc_12m_momentum', label: '12-Month Price Momentum', formula: 'Momentum = (Current Price / Price 12 months ago) - 1' },
            { id: 'calc_52w_high_ratio', label: '52-Week High Ratio', formula: '52-Week Ratio = Current Price / 52-Week High' },
            { id: 'calc_1m_return', label: 'Short-Term Reversal (1-Month)', formula: '1-Month Return = (Current Price / Price 1 month ago) - 1' },
        ]
    },
];

// Helper function to extract key input terms from a formula string
function extractMissingInputsFromFormula(formula: string): string {
    // Common financial terms to look for in formulas
    const knownTerms = [
        'Market Price', 'Share Price', 'Stock Price', 'Price',
        'EPS', 'Earnings Per Share', 'Net Income', 'Earnings',
        'Total Equity', 'Shareholders Equity', 'Equity',
        'Total Revenue', 'Revenue', 'Net Sales', 'Sales',
        'Shares Outstanding', 'Shares',
        'Operating Cash Flow', 'OCF', 'Cash Flow', 'FCF',
        'Total Debt', 'Debt', 'Long-term Debt',
        'EBITDA', 'EBIT', 'Operating Income',
        'Gross Profit', 'COGS', 'Cost of Goods Sold',
        'Total Assets', 'Assets', 'Current Assets',
        'Current Liabilities', 'Liabilities',
        'Depreciation', 'Amortization', 'CapEx',
        'Dividends', 'DPS', 'Dividend Per Share',
        'Book Value', 'BVPS', 'Market Cap',
        'Interest Expense', 'Interest', 'Tax Rate', 'Taxes',
        'Inventory', 'Accounts Receivable', 'Accounts Payable',
        'Working Capital', 'NWC', 'Cash',
        'ROE', 'ROA', 'ROIC', 'WACC', 'Beta'
    ];

    const found: string[] = [];
    const lowerFormula = formula.toLowerCase();

    for (const term of knownTerms) {
        if (lowerFormula.includes(term.toLowerCase())) {
            // Avoid duplicates and prefer shorter versions if a longer one is found
            const existing = found.find(f => f.toLowerCase().includes(term.toLowerCase()) || term.toLowerCase().includes(f.toLowerCase()));
            if (!existing) {
                found.push(term);
            }
        }
    }

    // Return up to 3 terms for conciseness
    const displayTerms = found.slice(0, 3);
    return displayTerms.length > 0 ? `Missing: ${displayTerms.join(', ')}` : 'Missing inputs';
}

// Helper function to generate all metrics as FinancialItems (with empty values - shows as unavailable)
export function generateAllMetricsAsItems(): { category: string; items: Array<{ id: string; label: string; currentYear: number; previousYear: number; variation: number; variationPercent: number; sourcePage: string; calculationError?: string }> }[] {
    return ALL_METRIC_DEFINITIONS.map(cat => ({
        category: cat.category,
        items: cat.metrics.map(m => ({
            id: m.id,
            label: m.label,
            currentYear: 0,
            previousYear: 0,
            variation: 0,
            variationPercent: 0,
            sourcePage: 'Calculated',
            calculationError: extractMissingInputsFromFormula(m.formula)
        }))
    }));
}

// Generate sample data for testing - creates realistic looking values for all metrics
export function generateSampleMetricsData(): { category: string; items: Array<{ id: string; label: string; currentYear: number; previousYear: number; variation: number; variationPercent: number; sourcePage: string; isAutoCalc: boolean }> }[] {
    // Seed for pseudo-random but consistent values
    const getSampleValue = (id: string, isPercent: boolean, isRatio: boolean, isMultiple: boolean, isCurrency: boolean): { current: number, previous: number } => {
        const hash = id.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
        const rand = (hash % 100) / 100;

        if (isPercent) {
            const current = 5 + rand * 45; // 5% to 50%
            const previous = current * (0.85 + rand * 0.3);
            return { current: Math.round(current * 100) / 100, previous: Math.round(previous * 100) / 100 };
        }
        if (isRatio) {
            const current = 0.5 + rand * 3; // 0.5 to 3.5
            const previous = current * (0.9 + rand * 0.2);
            return { current: Math.round(current * 100) / 100, previous: Math.round(previous * 100) / 100 };
        }
        if (isMultiple) {
            const current = 5 + rand * 25; // 5x to 30x
            const previous = current * (0.8 + rand * 0.4);
            return { current: Math.round(current * 10) / 10, previous: Math.round(previous * 10) / 10 };
        }
        if (isCurrency) {
            const current = 1000000 + rand * 50000000; // $1M to $51M
            const previous = current * (0.8 + rand * 0.3);
            return { current: Math.round(current), previous: Math.round(previous) };
        }
        // Default
        const current = 10 + rand * 100;
        const previous = current * (0.85 + rand * 0.3);
        return { current: Math.round(current * 100) / 100, previous: Math.round(previous * 100) / 100 };
    };

    return ALL_METRIC_DEFINITIONS.map(cat => ({
        category: cat.category,
        items: cat.metrics.map(m => {
            const label = m.label.toLowerCase();
            const isPercent = label.includes('margin') || label.includes('return') || label.includes('yield') || label.includes('growth') || label.includes('ratio');
            const isRatio = label.includes('ratio') && !isPercent;
            const isMultiple = label.includes('p/e') || label.includes('p/b') || label.includes('p/s') || label.includes('ev/');
            const isCurrency = label.includes('value') || label.includes('income') || label.includes('profit') || label.includes('cash flow') || label.includes('capital');

            const { current, previous } = getSampleValue(m.id, isPercent, isRatio, isMultiple, isCurrency);
            const variation = current - previous;
            const variationPercent = previous !== 0 ? ((variation / previous) * 100) : 0;

            return {
                id: m.id,
                label: m.label,
                currentYear: current,
                previousYear: previous,
                variation: Math.round(variation * 100) / 100,
                variationPercent: Math.round(variationPercent * 100) / 100,
                sourcePage: 'Sample Data',
                isAutoCalc: true
            };
        })
    }));
}

// Advanced auto-generate breakdown steps with context-aware logic
function generateBreakdownFromFormula(formula: string): FormulaBreakdown[] {
    const breakdown: FormulaBreakdown[] = [];

    // Clean operators for consistent parsing
    let cleanFormula = formula
        .replace(/×/g, '*')
        .replace(/÷/g, '/')
        .replace(/–/g, '-'); // replace en-dash with hyphen

    // Split by main operators to identify components
    // Prioritize division/multiplication as primary steps for ratios
    let parts: string[] = [];
    const isRatio = cleanFormula.includes('/');
    const isProduct = cleanFormula.includes('*') && !isRatio;
    const isSum = (cleanFormula.includes('+') || cleanFormula.includes('-')) && !isRatio && !isProduct;

    if (isRatio) {
        // Handle Dividend / Divisor pattern
        const segments = cleanFormula.split('/');
        if (segments.length === 2) {
            const numerator = segments[0].trim();
            const denominator = segments[1].trim();

            breakdown.push({
                step: `Determining ${cleanTerm(numerator)}`,
                formula: numerator,
                description: getContextualDescription(numerator, 'numerator')
            });

            breakdown.push({
                step: `Determining ${cleanTerm(denominator)}`,
                formula: denominator,
                description: getContextualDescription(denominator, 'denominator')
            });

            breakdown.push({
                step: 'Calculate Ratio',
                formula: formula,
                description: getFinalStepDescription(formula, 'ratio')
            });
            return breakdown;
        }
    }

    // Fallback for complex formulas (multi-part)
    parts = cleanFormula.split(/[\/\*\+\-]/).filter(p => p.trim().length > 0 && !/^\d+$/.test(p.trim()));

    if (parts.length >= 2) {
        // Add step for each unique component
        const seen = new Set();
        parts.forEach((part) => {
            const clean = cleanTerm(part);
            if (clean.length > 1 && !seen.has(clean)) { // Ignore operators or single chars
                seen.add(clean);
                breakdown.push({
                    step: `Find ${clean}`,
                    formula: clean,
                    description: getContextualDescription(clean, 'component')
                });
            }
        });

        breakdown.push({
            step: 'Compute Final Metric',
            formula: formula,
            description: getFinalStepDescription(formula, 'general')
        });
    }

    return breakdown;
}

function cleanTerm(term: string): string {
    return term.replace(/[\(\)\[\]]/g, '').trim();
}

// Rich dictionary with context-aware descriptions
function getContextualDescription(term: string, role: 'numerator' | 'denominator' | 'component'): string {
    const t = term.toLowerCase();

    // Core Financial Items
    if (t.includes('market price') || t.includes('share price')) return "Current trading price of one share from market data";
    if (t.includes('earnings per share') || t.includes('eps')) return "Net income available to common shareholders per share";
    if (t.includes('net income') || t.includes('profit')) return "Bottom-line profit after all expenses, taxes, and interest";
    if (t.includes('revenue') || t.includes('sales')) return "Top-line money generated from business operations";
    if (t.includes('equity') || t.includes('book value')) return "Net residual interest in assets after deducting liabilities";
    if (t.includes('assets')) return "Total economic resources owned by the company";
    if (t.includes('liabilities') || t.includes('debt')) return "Financial obligations or debts owed to outsiders";
    if (t.includes('cash flow') || t.includes('ocf')) return "Net cash generated from the company's core business activities";
    if (t.includes('fcf')) return "Cash available for distribution after capital expenditures";
    if (t.includes('ebitda')) return "Proxy for operating cash flow before financial and tax decisions";
    if (t.includes('ebit')) return "Profit from operations before interest and tax expenses";
    if (t.includes('dividend')) return "Distribution of profits to shareholders";
    if (t.includes('shares')) return "Total number of shares currently held by all shareholders";
    if (t.includes('working capital')) return "Capital available for daily operations (Current Assets - Current Liabilities)";
    if (t.includes('cogs') || t.includes('cost of')) return "Direct costs attributable to the production of goods sold";
    if (t.includes('receivable')) return "Money owed to the company by debtors";
    if (t.includes('payable')) return "Short-term debt obligated to be paid to suppliers";
    if (t.includes('inventory')) return "Raw materials, work-in-process, and finished goods";
    if (t.includes('depreciation')) return "Allocation of cost of tangible assets over their useful lives";
    if (t.includes('capex')) return "Funds used to acquire, upgrade, and maintain physical assets";
    if (t.includes('market cap')) return "Total market value of the company's outstanding shares";

    // Generic Role-based fallback
    if (role === 'numerator') return "The primary value being measured or compared";
    if (role === 'denominator') return "The base value used to standardize the comparison";

    return "Extract this specific line item from financial statements";
}

// Smart final step descriptions based on formula type
function getFinalStepDescription(formula: string, type: 'ratio' | 'general'): string {
    const f = formula.toLowerCase();

    // Valuation Ratios
    if (f.includes('p/e') || f.includes('price')) return "Divide price by the fundamental metric. Lower values often indicate better value.";
    if (f.includes('ev/')) return "Compare enterprise value to operating metric. Lower multiples suggest undervaluation.";

    // Profitability
    if (f.includes('margin')) return "Result expresses profit as a percentage of revenue. Higher margins indicate better efficiency.";
    if (f.includes('return on') || f.includes('roe') || f.includes('roa')) return "Measures how effectively capital is being used to generate returns. Higher is better.";

    // Liquidity/Solvency
    if (f.includes('debt') && f.includes('equity')) return "Measures financial leverage. Higher values indicate higher risk.";
    if (f.includes('current ratio') || f.includes('quick ratio')) return "Measures ability to pay short-term obligations. Values > 1.0 are generally safer.";

    // Efficiency
    if (f.includes('turnover') || f.includes('inventory') || f.includes('asset')) return "Measures speed of asset usage or inventory sale. Higher turnover generally signals better efficiency.";
    if (f.includes('days') || f.includes('receivable')) return "Measures time in days. Lower days for receivables/inventory is usually better cash management.";

    // Growth
    if (f.includes('growth') || f.includes('change')) return "Shows the percentage increase or decrease over the period. Positive trend is usually desired.";

    // Default
    if (type === 'ratio') return "Divide the numerator by the denominator to get the ratio.";

    return "Apply the formula operators to calculated the final metric result.";
}

// Helper to get formula by ID - with auto-generated breakdown
export function getFormulaById(id: string): MetricDefinition | undefined {
    for (const cat of ALL_METRIC_DEFINITIONS) {
        const metric = cat.metrics.find(m => m.id === id);
        if (metric) {
            // If no breakdown defined, auto-generate one
            if (!metric.breakdown || metric.breakdown.length === 0) {
                const autoBreakdown = generateBreakdownFromFormula(metric.formula);
                if (autoBreakdown.length > 0) {
                    return { ...metric, breakdown: autoBreakdown };
                }
            }
            return metric;
        }
    }
    return undefined;
}

// Get all metric IDs
export function getAllMetricIds(): string[] {
    return ALL_METRIC_DEFINITIONS.flatMap(cat => cat.metrics.map(m => m.id));
}

// Get total count of all metrics
export function getTotalMetricCount(): number {
    return ALL_METRIC_DEFINITIONS.reduce((sum, cat) => sum + cat.metrics.length, 0);
}

