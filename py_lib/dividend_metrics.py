def dividend_yield(annual_dividends_per_share: float, current_stock_price: float) -> float:
    """
    Dividend Yield
    Formula: (Annual Dividends Per Share / Current Stock Price) × 100
    """
    return annual_dividends_per_share / current_stock_price * 100

def dividend_payout_ratio(dividends_per_share: float, earnings_per_share_basic: float) -> float:
    """
    Dividend Payout Ratio
    Formula: (Dividends Per Share / Earnings Per Share) × 100
    Alternative: (Total Dividends / Net Income) × 100
    """
    return dividends_per_share / earnings_per_share_basic * 100

def dividend_coverage_ratio(earnings_per_share_basic: float, dividends_per_share: float) -> float:
    """
    Dividend Coverage Ratio
    Formula: Earnings Per Share / Dividends Per Share
    Alternative: Net Income / Total Dividends Paid
    """
    return earnings_per_share_basic / dividends_per_share

def dividend_per_share(total_dividends_paid: float, number_of_shares_outstanding: float) -> float:
    """
    Dividend Per Share (DPS)
    Formula: Total Dividends Paid / Number of Shares Outstanding
    """
    return total_dividends_paid / number_of_shares_outstanding

def retention_ratio(dividend_payout_ratio: float) -> float:
    """
    Retention Ratio (Plowback Ratio)
    Formula: 1 - Dividend Payout Ratio
    Alternative: (Net Income - Dividends) / Net Income
    """
    return 1 - dividend_payout_ratio

def cash_dividend_payout_ratio(cash_dividends_paid: float, operating_cash_flow: float) -> float:
    """
    Cash Dividend Payout Ratio
    Formula: Cash Dividends Paid / Operating Cash Flow
    """
    return cash_dividends_paid / operating_cash_flow