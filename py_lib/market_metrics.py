def market_capitalization(current_stock_price: float, total_shares_outstanding: float) -> float:
    """
    Market Capitalization
    Formula: Current Stock Price × Total Shares Outstanding
    """
    return current_stock_price * total_shares_outstanding


def enterprise_value(market_cap: float, total_debt: float, minority_interest: float, preferred_equity: float, cash_and_cash_equivalents: float) -> float:
    """
    Enterprise Value (EV)
    Formula: Market Cap + Total Debt + Minority Interest + Preferred Equity - Cash and Cash Equivalents
    Simplified: Market Cap + Net Debt
    """
    return market_cap + total_debt + minority_interest + preferred_equity - cash_and_cash_equivalents


def book_value(total_assets: float, total_liabilities: float, preferred_stock: float) -> float:
    """
    Book Value
    Formula: Total Assets - Total Liabilities - Preferred Stock
    Alternative: Total Shareholders' Equity
    """
    return total_assets - total_liabilities - preferred_stock


def book_value_per_share(total_equity: float, preferred_equity: float, common_shares_outstanding: float) -> float:
    """
    Book Value Per Share
    Formula: (Total Equity - Preferred Equity) / Common Shares Outstanding
    """
    return (total_equity - preferred_equity) / common_shares_outstanding


def market_value(current_market_price: float, number_of_units: float) -> float:
    """
    Market Value
    Formula: Current Market Price × Number of Units
    """
    return current_market_price * number_of_units


def market_share(company_sales: float, total_industry_sales: float) -> float:
    """
    Market Share
    Formula: (Company's Sales / Total Industry Sales) × 100
    """
    return (company_sales / total_industry_sales) * 100


def total_addressable_market(annual_market_demand: float, average_selling_price: float) -> float:
    """
    Total Addressable Market (TAM)
    Formula: Annual Market Demand × Average Selling Price
    """
    return annual_market_demand * average_selling_price


def float_shares(shares_outstanding: float, restricted_shares: float, insider_holdings: float) -> float:
    """
    Float
    Formula: Shares Outstanding - Restricted Shares - Insider Holdings
    """
    return shares_outstanding - restricted_shares - insider_holdings


def shares_outstanding(issued_shares: float, treasury_shares: float) -> float:
    """
    Shares Outstanding
    Formula: Issued Shares - Treasury Shares
    """
    return issued_shares - treasury_shares


def institutional_ownership_percentage(shares_held_by_institutions: float, total_shares_outstanding: float) -> float:
    """
    Institutional Ownership Percentage
    Formula: (Shares Held by Institutions / Total Shares Outstanding) × 100
    """
    return (shares_held_by_institutions / total_shares_outstanding) * 100


def shares_outstanding_from_capital(paid_up_equity_share_capital: float, face_value_per_share: float) -> float:
    """
    Shares Outstanding (Alternative - from Capital Structure)
    Formula: Paid-Up Equity Share Capital / Face Value Per Share
    Note: Common in markets where share capital is reported on balance sheet
    Where: Paid-Up Capital = Total subscribed and paid-up equity capital
           Face Value = Par value or nominal value per share
    """
    return paid_up_equity_share_capital / face_value_per_share
