import math


def normal_cdf(x: float) -> float:
    """
    Cumulative Normal Distribution Function
    Approximation using the error function
    """
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def economic_value_added(nopat: float, wacc: float, invested_capital: float) -> float:
    """
    Economic Value Added (EVA)
    Formula: NOPAT - (WACC × Invested Capital)
    Alternative: (ROIC - WACC) × Invested Capital
    Where: NOPAT = Net Operating Profit After Tax
    """
    return nopat - (wacc * invested_capital)


def economic_value_added_roic(roic: float, wacc: float, invested_capital: float) -> float:
    """
    Economic Value Added (EVA) - ROIC Version
    Formula: (ROIC - WACC) × Invested Capital
    """
    return (roic - wacc) * invested_capital


def market_value_added(market_value_of_firm: float, invested_capital: float) -> float:
    """
    Market Value Added (MVA)
    Formula: Market Value of Firm - Invested Capital
    Alternative: Market Capitalization - Book Value of Equity
    """
    return market_value_of_firm - invested_capital


def shareholder_value_added(return_on_investment: float, cost_of_capital: float, invested_capital: float) -> float:
    """
    Shareholder Value Added (SVA)
    Formula: (Return on Investment - Cost of Capital) × Invested Capital
    """
    return (return_on_investment - cost_of_capital) * invested_capital


def altman_z_score_public(working_capital: float, retained_earnings: float, ebit: float, market_value_equity: float, total_liabilities: float, sales: float, total_assets: float) -> float:
    """
    Altman Z-Score (Bankruptcy Prediction) - Public Manufacturing Companies
    Formula: Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
    
    Where:
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets
    C = EBIT / Total Assets
    D = Market Value of Equity / Book Value of Total Liabilities
    E = Sales / Total Assets
    
    Interpretation:
    Z > 2.99 = Safe zone
    1.81 < Z < 2.99 = Grey zone
    Z < 1.81 = Distress zone
    """
    A = working_capital / total_assets
    B = retained_earnings / total_assets
    C = ebit / total_assets
    D = market_value_equity / total_liabilities
    E = sales / total_assets
    return 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + 1.0 * E


def piotroski_f_score(roa: float, operating_cash_flow: float, roa_previous: float, net_income: float, long_term_debt_current: float, long_term_debt_previous: float, current_ratio_current: float, current_ratio_previous: float, shares_issued: bool, gross_margin_current: float, gross_margin_previous: float, asset_turnover_current: float, asset_turnover_previous: float) -> int:
    """
    Piotroski F-Score (Quality Assessment)
    Score range: 0-9 (sum of nine binary scores)
    
    Profitability (4 points):
    1. ROA > 0 (1 point)
    2. Operating Cash Flow > 0 (1 point)
    3. ROA increase YoY (1 point)
    4. Operating Cash Flow > Net Income (1 point)
    
    Leverage, Liquidity, Source of Funds (3 points):
    5. Decrease in long-term debt (1 point)
    6. Increase in current ratio (1 point)
    7. No new shares issued (1 point)
    
    Operating Efficiency (2 points):
    8. Increase in gross margin (1 point)
    9. Increase in asset turnover (1 point)
    """
    score = 0
    
    if roa > 0:
        score += 1
    if operating_cash_flow > 0:
        score += 1
    if roa > roa_previous:
        score += 1
    if operating_cash_flow > net_income:
        score += 1
    if long_term_debt_current < long_term_debt_previous:
        score += 1
    if current_ratio_current > current_ratio_previous:
        score += 1
    if not shares_issued:
        score += 1
    if gross_margin_current > gross_margin_previous:
        score += 1
    if asset_turnover_current > asset_turnover_previous:
        score += 1
    
    return score


def beneish_m_score(dsri: float, gmi: float, aqi: float, sgi: float, depi: float, sgai: float, tata: float, lvgi: float) -> float:
    """
    Beneish M-Score (Earnings Manipulation Detection)
    Formula: M = -4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI + 0.115×DEPI - 0.172×SGAI + 4.679×TATA - 0.327×LVGI
    
    Where:
    DSRI = Days Sales in Receivables Index
    GMI = Gross Margin Index
    AQI = Asset Quality Index
    SGI = Sales Growth Index
    DEPI = Depreciation Index
    SGAI = Sales, General & Admin Expenses Index
    TATA = Total Accruals to Total Assets
    LVGI = Leverage Index
    
    Interpretation:
    M > -1.78 = Likely manipulator
    """
    return -4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi


def beta_systematic_risk(covariance_investment_market: float, variance_market: float) -> float:
    """
    Beta (Systematic Risk)
    Formula: Cov(Ri, Rm) / Var(Rm)
    Alternative: ρi,m × (σi / σm)
    Where: ρ = correlation coefficient
    """
    return covariance_investment_market / variance_market


def beta_alternative(correlation: float, standard_deviation_investment: float, standard_deviation_market: float) -> float:
    """
    Beta (Systematic Risk) - Alternative Formula
    Formula: ρi,m × (σi / σm)
    """
    return correlation * (standard_deviation_investment / standard_deviation_market)


def jensens_alpha(actual_return: float, risk_free_rate: float, beta: float, market_return: float) -> float:
    """
    Alpha (Jensen's Alpha)
    Formula: αi = Ri - [Rf + βi(Rm - Rf)]
    Where: Ri = Actual return of investment
    """
    return actual_return - (risk_free_rate + beta * (market_return - risk_free_rate))


def tobins_q_ratio(market_value_firm: float, replacement_cost_assets: float) -> float:
    """
    Tobin's Q Ratio
    Formula: Market Value of Firm / Replacement Cost of Assets
    Alternative: (Market Cap + Total Debt) / Total Assets
    
    Interpretation:
    Q > 1 = Market values firm higher than asset replacement cost
    Q < 1 = Market values firm lower than asset replacement cost
    """
    return market_value_firm / replacement_cost_assets


def tobins_q_alternative(market_cap: float, total_debt: float, total_assets: float) -> float:
    """
    Tobin's Q Ratio - Alternative Formula
    Formula: (Market Cap + Total Debt) / Total Assets
    """
    return (market_cap + total_debt) / total_assets


def earnings_quality_ratio(operating_cash_flow: float, net_income: float) -> float:
    """
    Earnings Quality Ratio
    Formula: Operating Cash Flow / Net Income
    
    Interpretation:
    > 1.0 = High quality earnings
    < 1.0 = Lower quality earnings
    """
    return operating_cash_flow / net_income


def accruals_ratio(net_income: float, operating_cash_flow: float, total_assets: float) -> float:
    """
    Accruals Ratio
    Formula: (Net Income - Operating Cash Flow) / Total Assets
    
    High accruals may indicate earnings manipulation
    """
    return (net_income - operating_cash_flow) / total_assets


def ev_to_revenue(enterprise_value: float, total_revenue: float) -> float:
    """
    EV-to-Revenue
    Formula: Enterprise Value / Total Revenue
    """
    return enterprise_value / total_revenue


def ev_to_operating_income(enterprise_value: float, operating_income: float) -> float:
    """
    EV-to-Operating Income
    Formula: Enterprise Value / Operating Income
    """
    return enterprise_value / operating_income
