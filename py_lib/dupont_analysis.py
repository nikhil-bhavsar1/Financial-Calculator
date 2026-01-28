def three_step_dupont_analysis(net_income: float, revenue: float, total_assets: float, equity: float) -> float:
    """
    3-Step DuPont Formula
    ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
    ROE = (Net Income / Revenue) × (Revenue / Total Assets) × (Total Assets / Equity)
    """
    net_profit_margin = net_income / revenue
    asset_turnover = revenue / total_assets
    equity_multiplier = total_assets / equity
    return net_profit_margin * asset_turnover * equity_multiplier


def five_step_dupont_analysis(net_income: float, pretax_income: float, ebit: float, revenue: float, total_assets: float, shareholders_equity: float) -> float:
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
    tax_burden = net_income / pretax_income
    interest_burden = pretax_income / ebit
    ebit_margin = ebit / revenue
    asset_turnover = revenue / total_assets
    equity_multiplier = total_assets / shareholders_equity
    return tax_burden * interest_burden * ebit_margin * asset_turnover * equity_multiplier


def tax_burden(net_income: float, pretax_income: float) -> float:
    """
    Tax Burden
    Formula: Net Income / Pretax Income
    """
    return net_income / pretax_income


def interest_burden(pretax_income: float, ebit: float) -> float:
    """
    Interest Burden
    Formula: Pretax Income / EBIT
    """
    return pretax_income / ebit


def ebit_margin(ebit: float, revenue: float) -> float:
    """
    EBIT Margin
    Formula: EBIT / Revenue
    """
    return ebit / revenue


def dupont_roe(net_margin_pct: float, asset_turnover: float, equity_multiplier: float) -> float:
    """
    DuPont ROE Calculation
    Formula: (Net Margin / 100) × Asset Turnover × Equity Multiplier × 100
    """
    return (net_margin_pct / 100) * asset_turnover * equity_multiplier * 100
