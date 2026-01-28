def owner_earnings_buffett(net_income: float, depreciation_amortization: float, non_cash_charges: float, average_annual_capex: float, additional_wc_requirements: float) -> float:
    """
    Owner Earnings (Buffett's Formula)
    Formula: Owner Earnings = Net Income + D&A + Other Non-Cash Charges - Average Annual CapEx - Additional WC Requirements
    """
    return net_income + depreciation_amortization + non_cash_charges - average_annual_capex - additional_wc_requirements


def look_through_earnings(reported_earnings: float, share_of_undistributed_earnings: float) -> float:
    """
    Look-Through Earnings
    Formula: Look-Through = Reported Earnings + Share of Undistributed Earnings from Investees
    """
    return reported_earnings + share_of_undistributed_earnings


def intrinsic_value_growth_rate(dividend_payout_ratio: float, return_on_retained_earnings: float) -> float:
    """
    Intrinsic Value Growth Rate
    Formula: Growth Rate = (1 - Dividend Payout Ratio) × Return on Retained Earnings
    """
    return (1 - dividend_payout_ratio) * return_on_retained_earnings


def return_on_retained_earnings(change_in_eps: float, cumulative_retained_earnings_per_share: float) -> float:
    """
    Return on Retained Earnings
    Formula: Return = Change in EPS / Cumulative Retained Earnings per Share
    """
    if cumulative_retained_earnings_per_share == 0:
        return 0
    return change_in_eps / cumulative_retained_earnings_per_share


def return_spread(roic: float, wacc: float) -> float:
    """
    Return Spread (Economic Moat Indicator)
    Formula: Return Spread = ROIC - WACC
    Strong moat: Spread > 5% sustained over time
    """
    return roic - wacc


def return_on_tangible_capital(nopat: float, net_working_capital: float, net_fixed_assets: float) -> float:
    """
    Return on Tangible Capital
    Formula: ROTC = NOPAT / (Net Working Capital + Net Fixed Assets)
    """
    denominator = net_working_capital + net_fixed_assets
    if denominator == 0:
        return 0
    return nopat / denominator


def pricing_power_test(price_increase_percentage: float, volume_loss_percentage: float) -> bool:
    """
    Pricing Power Test
    Formula: Pricing Power = % Price Increase with < 10% volume loss
    
    Returns True if company has pricing power
    """
    return volume_loss_percentage < 10.0


def magic_formula_earnings_yield(ebit: float, enterprise_value: float) -> float:
    """
    Earnings Yield (Magic Formula)
    Formula: Earnings Yield = EBIT / Enterprise Value
    (Higher is better)
    """
    if enterprise_value == 0:
        return 0
    return ebit / enterprise_value


def magic_formula_return_on_capital(ebit: float, net_working_capital: float, net_fixed_assets: float) -> float:
    """
    Return on Capital (Magic Formula)
    Formula: ROC = EBIT / (Net Working Capital + Net Fixed Assets)
    (Higher is better)
    """
    denominator = net_working_capital + net_fixed_assets
    if denominator == 0:
        return 0
    return ebit / denominator


def acquirers_multiple(enterprise_value: float, operating_earnings: float) -> float:
    """
    Acquirer's Multiple (Tobias Carlisle)
    Formula: Acquirer's Multiple = Enterprise Value / Operating Earnings
    Where: Operating Earnings = EBIT or NOPAT
    (Lower is better - inverse of earnings yield)
    """
    if operating_earnings == 0:
        return 0
    return enterprise_value / operating_earnings


def shareholder_yield(dividends: float, buybacks: float, share_issuance: float, market_cap: float) -> float:
    """
    Shareholder Yield
    Formula: Shareholder Yield = (Dividends + Buybacks - Share Issuance) / Market Cap
    """
    if market_cap == 0:
        return 0
    return (dividends + buybacks - share_issuance) / market_cap


def net_payout_yield(dividends: float, net_buybacks: float, market_cap: float) -> float:
    """
    Net Payout Yield
    Formula: Net Payout = (Dividends + Net Buybacks) / Market Cap
    """
    if market_cap == 0:
        return 0
    return (dividends + net_buybacks) / market_cap


def total_payout_yield(dividends: float, buybacks: float, debt_reduction: float, market_cap: float) -> float:
    """
    Total Payout Yield
    Formula: Total Payout = (Dividends + Buybacks + Debt Reduction) / Market Cap
    """
    if market_cap == 0:
        return 0
    return (dividends + buybacks + debt_reduction) / market_cap


def gross_profitability(revenue: float, cogs: float, total_assets: float) -> float:
    """
    Gross Profitability
    Formula: Gross Profitability = (Revenue - COGS) / Total Assets
    """
    if total_assets == 0:
        return 0
    return (revenue - cogs) / total_assets


def asset_growth(current_total_assets: float, prior_total_assets: float) -> float:
    """
    Asset Growth (Red Flag)
    Formula: Asset Growth = (Current Total Assets - Prior Total Assets) / Prior Total Assets
    Negative indicator: High asset growth often precedes poor returns
    """
    if prior_total_assets == 0:
        return 0
    return (current_total_assets - prior_total_assets) / prior_total_assets


def accruals_ratio_quality(net_income: float, operating_cash_flow: float, average_total_assets: float) -> float:
    """
    Accrual Ratio (Earnings Quality)
    Formula: Accruals = (Net Income - Operating Cash Flow) / Average Total Assets
    Lower accruals = Higher quality earnings
    """
    if average_total_assets == 0:
        return 0
    return (net_income - operating_cash_flow) / average_total_assets


def altman_z_score_private(working_capital: float, retained_earnings: float, ebit: float, book_value_equity: float, total_liabilities: float, sales: float, total_assets: float) -> float:
    """
    Altman Z-Score for Private Companies
    Formula: Z' = 0.717A + 0.847B + 3.107C + 0.420D + 0.998E
    
    Where:
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets
    C = EBIT / Total Assets
    D = Book Value of Equity / Total Liabilities
    E = Sales / Total Assets
    
    Interpretation:
    Z' > 2.9 = Safe
    1.23 < Z' < 2.9 = Grey
    Z' < 1.23 = Distress
    """
    A = working_capital / total_assets if total_assets != 0 else 0
    B = retained_earnings / total_assets if total_assets != 0 else 0
    C = ebit / total_assets if total_assets != 0 else 0
    D = book_value_equity / total_liabilities if total_liabilities != 0 else 0
    E = sales / total_assets if total_assets != 0 else 0
    return 0.717 * A + 0.847 * B + 3.107 * C + 0.420 * D + 0.998 * E


def normalized_earnings(earnings_over_cycle: list) -> float:
    """
    Normalized Earnings
    Formula: Normalized = Average earnings over full business cycle (7-10 years)
    """
    if not earnings_over_cycle:
        return 0
    return sum(earnings_over_cycle) / len(earnings_over_cycle)


def shiller_pe_ratio(current_price: float, average_10yr_inflation_adjusted_earnings: float) -> float:
    """
    Shiller P/E (CAPE Ratio)
    Formula: CAPE = Price / 10-Year Average Inflation-Adjusted Earnings
    """
    if average_10yr_inflation_adjusted_earnings == 0:
        return 0
    return current_price / average_10yr_inflation_adjusted_earnings


def graham_dodd_pe(current_price: float, average_10yr_earnings: float) -> float:
    """
    Graham & Dodd P/E
    Formula: G&D P/E = Current Price / Average 10-Year Earnings
    """
    if average_10yr_earnings == 0:
        return 0
    return current_price / average_10yr_earnings


def four_factor_value_score(rank_pe: float, rank_pb: float, rank_ps: float, rank_dividend_yield: float) -> float:
    """
    4-Factor Value Score
    Formula: Score = Rank(P/E) + Rank(P/B) + Rank(P/S) + Rank(Dividend Yield)
    (Lower combined rank = more undervalued)
    """
    return rank_pe + rank_pb + rank_ps + rank_dividend_yield


def six_factor_quality_value_score(rank_pe: float, rank_pb: float, rank_ev_ebit: float, rank_roe: float, rank_roa: float, rank_roic: float) -> float:
    """
    6-Factor Quality Value
    Formula: Score = Rank(P/E) + Rank(P/B) + Rank(EV/EBIT) + Rank(ROE) + Rank(ROA) + Rank(ROIC)
    """
    return rank_pe + rank_pb + rank_ev_ebit + rank_roe + rank_roa + rank_roic


def value_composite_oshaughnessy(rank_pb: float, rank_pe: float, rank_ps: float, rank_pcf: float, rank_ev_ebitda: float, rank_shareholder_yield: float) -> float:
    """
    Value Composite (O'Shaughnessy)
    Formula: Value Composite = Average Percentile of:
    - P/B Ratio
    - P/E Ratio
    - P/S Ratio
    - P/CF Ratio
    - EV/EBITDA
    - Shareholder Yield
    """
    return (rank_pb + rank_pe + rank_ps + rank_pcf + rank_ev_ebitda + rank_shareholder_yield) / 6


def ohlson_o_score(size: float, tlta: float, wcta: float, clca: float, oeneg: float, nita: float, futl: float, intwo: float, chin: float) -> float:
    """
    Ohlson O-Score
    Formula: O = -1.32 - 0.407×SIZE + 6.03×TLTA - 1.43×WCTA + 0.076×CLCA - 1.72×OENEG - 2.37×NITA - 1.83×FUTL + 0.285×INTWO - 0.521×CHIN
    
    Where: SIZE, TLTA, WCTA, CLCA, OENEG, NITA, FUTL, INTWO, CHIN are financial ratios
    
    Probability of Bankruptcy = 1 / (1 + e^(-O))
    """
    import math
    O = -1.32 - 0.407 * size + 6.03 * tlta - 1.43 * wcta + 0.076 * clca - 1.72 * oeneg - 2.37 * nita - 1.83 * futl + 0.285 * intwo - 0.521 * chin
    return 1 / (1 + math.exp(-O))


def twelve_month_price_momentum(current_price: float, price_12_months_ago: float) -> float:
    """
    12-Month Price Momentum
    Formula: Momentum = (Current Price / Price 12 months ago) - 1
    """
    if price_12_months_ago == 0:
        return 0
    return (current_price / price_12_months_ago) - 1


def fifty_two_week_high_ratio(current_price: float, fifty_two_week_high: float) -> float:
    """
    52-Week High Ratio
    Formula: 52-Week Ratio = Current Price / 52-Week High
    """
    if fifty_two_week_high == 0:
        return 0
    return current_price / fifty_two_week_high


def one_month_return(current_price: float, price_1_month_ago: float) -> float:
    """
    Short-Term Reversal (Contrarian)
    Formula: 1-Month Return = (Current Price / Price 1 month ago) - 1
    Buy recent losers, sell recent winners
    """
    if price_1_month_ago == 0:
        return 0
    return (current_price / price_1_month_ago) - 1


def greenblatt_earnings_yield(ebit: float, enterprise_value: float) -> float:
    """
    Greenblatt's Earnings Yield
    Formula: EBIT / Enterprise Value
    (Higher is better - from 'The Little Book That Still Beats the Market')
    """
    if enterprise_value == 0:
        return 0
    return (ebit / enterprise_value) * 100
