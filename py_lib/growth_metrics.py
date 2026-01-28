def revenue_growth_rate(current_period_revenue: float, previous_period_revenue: float) -> float:
    """
    Revenue Growth Rate
    Formula: [(Current Period Revenue - Previous Period Revenue) / Previous Period Revenue] × 100
    """
    return ((current_period_revenue - previous_period_revenue) / previous_period_revenue) * 100


def earnings_growth_rate(current_period_earnings: float, previous_period_earnings: float) -> float:
    """
    Earnings Growth Rate
    Formula: [(Current Period Earnings - Previous Period Earnings) / Previous Period Earnings] × 100
    """
    return ((current_period_earnings - previous_period_earnings) / previous_period_earnings) * 100


def eps_growth_rate(current_eps: float, previous_eps: float) -> float:
    """
    EPS Growth Rate
    Formula: [(Current EPS - Previous EPS) / Previous EPS] × 100
    """
    return ((current_eps - previous_eps) / previous_eps) * 100


def compound_annual_growth_rate(ending_value: float, beginning_value: float, number_of_years: float) -> float:
    """
    Compound Annual Growth Rate (CAGR)
    Formula: [(Ending Value / Beginning Value)^(1/Number of Years) - 1] × 100
    """
    return ((ending_value / beginning_value) ** (1 / number_of_years) - 1) * 100


def year_over_year_growth(current_year_value: float, previous_year_value: float) -> float:
    """
    Year-over-Year (YoY) Growth
    Formula: [(Current Year Value - Previous Year Value) / Previous Year Value] × 100
    """
    return ((current_year_value - previous_year_value) / previous_year_value) * 100


def quarter_over_quarter_growth(current_quarter_value: float, previous_quarter_value: float) -> float:
    """
    Quarter-over-Quarter (QoQ) Growth
    Formula: [(Current Quarter Value - Previous Quarter Value) / Previous Quarter Value] × 100
    """
    return ((current_quarter_value - previous_quarter_value) / previous_quarter_value) * 100


def sustainable_growth_rate(roe: float, dividend_payout_ratio: float) -> float:
    """
    Sustainable Growth Rate (SGR)
    Formula: ROE × (1 - Dividend Payout Ratio)
    Alternative: ROE × Retention Ratio
    """
    return roe * (1 - dividend_payout_ratio)


def retention_ratio(dividend_payout_ratio: float) -> float:
    """
    Retention Ratio
    Formula: 1 - Dividend Payout Ratio
    """
    return 1 - dividend_payout_ratio


def internal_growth_rate(roa: float, retention_ratio: float) -> float:
    """
    Internal Growth Rate
    Formula: (ROA × Retention Ratio) / (1 - ROA × Retention Ratio)
    Where: Retention Ratio = 1 - Dividend Payout Ratio
    """
    return (roa * retention_ratio) / (1 - roa * retention_ratio)


def dividend_growth_rate(current_dividend: float, previous_dividend: float) -> float:
    """
    Dividend Growth Rate
    Formula: [(Current Dividend - Previous Dividend) / Previous Dividend] × 100
    """
    return ((current_dividend - previous_dividend) / previous_dividend) * 100


def book_value_growth_rate(current_book_value: float, previous_book_value: float) -> float:
    """
    Book Value Growth Rate
    Formula: [(Current Book Value - Previous Book Value) / Previous Book Value] × 100
    """
    return ((current_book_value - previous_book_value) / previous_book_value) * 100


def growth_rate(current: float, previous: float) -> float:
    """
    Generic Growth Rate
    Formula: [(Current - Previous) / Previous] × 100
    """
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100
