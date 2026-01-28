def net_income(total_revenue: float, total_expenses: float) -> float:
    """
    Net Income
    Formula: Total Revenue - Total Expenses
    """
    return total_revenue - total_expenses


def net_income_alt(gross_profit: float, operating_expenses: float, interest: float, taxes: float) -> float:
    """
    Net Income - Alternative
    Formula: Gross Profit - Operating Expenses - Interest - Taxes
    """
    return gross_profit - operating_expenses - interest - taxes


def gross_profit(total_revenue: float, cogs: float) -> float:
    """
    Gross Profit
    Formula: Total Revenue - Cost of Goods Sold (COGS)
    """
    return total_revenue - cogs


def operating_income(gross_profit: float, operating_expenses: float) -> float:
    """
    Operating Income (EBIT)
    Formula: Gross Profit - Operating Expenses
    """
    return gross_profit - operating_expenses


def operating_income_alt(revenue: float, cogs: float, operating_expenses: float) -> float:
    """
    Operating Income (EBIT) - Alternative
    Formula: Revenue - COGS - Operating Expenses (excluding interest & taxes)
    """
    return revenue - cogs - operating_expenses


def ebitda(operating_income: float, depreciation: float, amortization: float) -> float:
    """
    EBITDA
    Formula: Operating Income + Depreciation + Amortization
    """
    return operating_income + depreciation + amortization


def ebitda_alt(net_income: float, interest: float, taxes: float, depreciation: float, amortization: float) -> float:
    """
    EBITDA - Alternative
    Formula: Net Income + Interest + Taxes + Depreciation + Amortization
    """
    return net_income + interest + taxes + depreciation + amortization


def earnings_per_share(net_income: float, preferred_dividends: float, weighted_avg_shares: float) -> float:
    """
    Earnings Per Share (EPS)
    Formula: (Net Income - Preferred Dividends) / Weighted Average Shares Outstanding
    """
    return (net_income - preferred_dividends) / weighted_avg_shares


def diluted_eps(net_income: float, preferred_dividends: float, weighted_avg_shares: float, dilutive_securities: float) -> float:
    """
    Diluted EPS
    Formula: (Net Income - Preferred Dividends) / (Weighted Avg Shares + Dilutive Securities)
    """
    return (net_income - preferred_dividends) / (weighted_avg_shares + dilutive_securities)


def gross_profit_margin(gross_profit: float, total_revenue: float) -> float:
    """
    Gross Profit Margin
    Formula: (Gross Profit / Total Revenue) × 100
    """
    return (gross_profit / total_revenue) * 100


def gross_profit_margin_alt(revenue: float, cogs: float) -> float:
    """
    Gross Profit Margin - Alternative
    Formula: [(Revenue - COGS) / Revenue] × 100
    """
    return ((revenue - cogs) / revenue) * 100


def operating_margin(operating_income: float, total_revenue: float) -> float:
    """
    Operating Margin
    Formula: (Operating Income / Total Revenue) × 100
    """
    return (operating_income / total_revenue) * 100


def operating_margin_alt(ebit: float, revenue: float) -> float:
    """
    Operating Margin - Alternative
    Formula: (EBIT / Revenue) × 100
    """
    return (ebit / revenue) * 100


def net_profit_margin(net_income: float, total_revenue: float) -> float:
    """
    Net Profit Margin
    Formula: (Net Income / Total Revenue) × 100
    """
    return (net_income / total_revenue) * 100


def ebitda_margin(ebitda: float, total_revenue: float) -> float:
    """
    EBITDA Margin
    Formula: (EBITDA / Total Revenue) × 100
    """
    return (ebitda / total_revenue) * 100


def return_on_assets(net_income: float, avg_total_assets: float) -> float:
    """
    Return on Assets (ROA)
    Formula: (Net Income / Average Total Assets) × 100
    """
    return (net_income / avg_total_assets) * 100


def return_on_assets_alt(net_income: float, total_assets: float) -> float:
    """
    Return on Assets (ROA) - Alternative
    Formula: (Net Income / Total Assets) × 100
    """
    return (net_income / total_assets) * 100


def return_on_equity(net_income: float, avg_shareholders_equity: float) -> float:
    """
    Return on Equity (ROE)
    Formula: (Net Income / Average Shareholders' Equity) × 100
    """
    return (net_income / avg_shareholders_equity) * 100


def return_on_equity_alt(net_income: float, shareholders_equity: float) -> float:
    """
    Return on Equity (ROE) - Alternative
    Formula: (Net Income / Shareholders' Equity) × 100
    """
    return (net_income / shareholders_equity) * 100


def return_on_investment(current_value: float, cost_investment: float) -> float:
    """
    Return on Investment (ROI)
    Formula: [(Current Value of Investment - Cost of Investment) / Cost of Investment] × 100
    """
    return ((current_value - cost_investment) / cost_investment) * 100


def return_on_investment_alt(net_profit: float, total_investment: float) -> float:
    """
    Return on Investment (ROI) - Alternative
    Formula: (Net Profit / Total Investment) × 100
    """
    return (net_profit / total_investment) * 100


def nopat(ebit: float, tax_rate: float) -> float:
    """
    Net Operating Profit After Tax (NOPAT)
    Formula: EBIT × (1 - Tax Rate)
    """
    return ebit * (1 - tax_rate)


def return_on_invested_capital(nopat: float, total_debt: float, total_equity: float) -> float:
    """
    Return on Invested Capital (ROIC)
    Formula: [NOPAT / (Total Debt + Total Equity)] × 100
    """
    return (nopat / (total_debt + total_equity)) * 100


def return_on_invested_capital_alt(ebit: float, tax_rate: float, invested_capital: float) -> float:
    """
    Return on Invested Capital (ROIC) - Alternative
    Formula: EBIT(1-t) / Invested Capital
    """
    return (ebit * (1 - tax_rate) / invested_capital) * 100


def return_on_capital_employed(ebit: float, total_assets: float, current_liabilities: float) -> float:
    """
    Return on Capital Employed (ROCE)
    Formula: [EBIT / (Total Assets - Current Liabilities)] × 100
    """
    return (ebit / (total_assets - current_liabilities)) * 100


def return_on_capital_employed_alt(ebit: float, capital_employed: float) -> float:
    """
    Return on Capital Employed (ROCE) - Alternative
    Formula: EBIT / Capital Employed
    """
    return (ebit / capital_employed) * 100


def return_on_net_assets(net_income: float, fixed_assets: float, net_working_capital: float) -> float:
    """
    Return on Net Assets (RONA)
    Formula: (Net Income / (Fixed Assets + Net Working Capital)) × 100
    """
    return (net_income / (fixed_assets + net_working_capital)) * 100


def pre_tax_profit_margin(earnings_before_tax: float, total_revenue: float) -> float:
    """
    Pre-Tax Profit Margin
    Formula: (Earnings Before Tax / Total Revenue) × 100
    """
    return (earnings_before_tax / total_revenue) * 100


def after_tax_margin(net_income_after_tax: float, total_revenue: float) -> float:
    """
    After-Tax Margin
    Formula: (Net Income After Tax / Total Revenue) × 100
    """
    return (net_income_after_tax / total_revenue) * 100


def cash_return_on_assets(operating_cash_flow: float, avg_total_assets: float) -> float:
    """
    Cash Return on Assets
    Formula: (Operating Cash Flow / Average Total Assets) × 100
    """
    return (operating_cash_flow / avg_total_assets) * 100


def cash_return_on_equity(operating_cash_flow: float, avg_shareholders_equity: float) -> float:
    """
    Cash Return on Equity
    Formula: (Operating Cash Flow / Average Shareholders' Equity) × 100
    """
    return (operating_cash_flow / avg_shareholders_equity) * 100
