def three_step_dupont_analysis(profit_for_the_year: float, total_revenue: float, total_assets: float, equity: float) -> float:
    """
    3-Step DuPont Formula
    ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
    ROE = (Net Income / Revenue) × (Revenue / Total Assets) × (Total Assets / Equity)
    """
    net_profit_margin = profit_for_the_year / total_revenue
    asset_turnover = total_revenue / total_assets
    equity_multiplier = total_assets / equity
    return net_profit_margin * asset_turnover * equity_multiplier

def five_step_dupont_analysis(profit_for_the_year: float, pretax_income: float, operating_profit: float, total_revenue: float, total_assets: float, total_equity: float) -> float:
    """
    5-Step DuPont Formula
    ROE = Tax Burden × Interest Burden × EBIT Margin × Asset Turnover × Equity Multiplier
    Where:
    Tax Burden = Net Income / Pretax Income
    Interest Burden = Pretax Income / EBIT
    EBIT Margin = EBIT / Revenue
    Asset Turnover = Revenue / Total Assets
    Equity Multiplier = Total Assets / Shareholders' Equity
    """
    tax_burden = profit_for_the_year / pretax_income
    interest_burden = pretax_income / operating_profit
    ebit_margin = operating_profit / total_revenue
    asset_turnover = total_revenue / total_assets
    equity_multiplier = total_assets / total_equity
    return tax_burden * interest_burden * ebit_margin * asset_turnover * equity_multiplier

def tax_burden(profit_for_the_year: float, pretax_income: float) -> float:
    """
    Tax Burden
    Formula: Net Income / Pretax Income
    """
    return profit_for_the_year / pretax_income

def interest_burden(pretax_income: float, operating_profit: float) -> float:
    """
    Interest Burden
    Formula: Pretax Income / EBIT
    """
    return pretax_income / operating_profit

def ebit_margin(operating_profit: float, total_revenue: float) -> float:
    """
    EBIT Margin
    Formula: EBIT / Revenue
    """
    return operating_profit / total_revenue

def dupont_roe(net_margin_pct: float, asset_turnover: float, equity_multiplier: float) -> float:
    """
    DuPont ROE Calculation
    Formula: (Net Margin / 100) × Asset Turnover × Equity Multiplier × 100
    """
    return net_margin_pct / 100 * asset_turnover * equity_multiplier * 100