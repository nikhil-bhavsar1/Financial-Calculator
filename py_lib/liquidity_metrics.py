"""
Liquidity Metrics
Python implementation of formulas from Section 4 of Financial Metrics Guide
"""


# =============================================================================
# LIQUIDITY METRICS
# =============================================================================


def current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    Current Ratio
    Formula: Current Assets / Current Liabilities
    """
    return current_assets / current_liabilities


def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
    """
    Quick Ratio (Acid-Test Ratio)
    Formula: (Current Assets - Inventory) / Current Liabilities
    """
    return (current_assets - inventory) / current_liabilities


def quick_ratio_alt(cash: float, marketable_securities: float, accounts_receivable: float,
                      current_liabilities: float) -> float:
    """
    Quick Ratio (Acid-Test Ratio) - Alternative
    Formula: (Cash + Marketable Securities + Accounts Receivable) / Current Liabilities
    """
    return (cash + marketable_securities + accounts_receivable) / current_liabilities


def cash_ratio(cash: float, cash_equivalents: float, current_liabilities: float) -> float:
    """
    Cash Ratio
    Formula: (Cash + Cash Equivalents) / Current Liabilities
    """
    return (cash + cash_equivalents) / current_liabilities


def working_capital(current_assets: float, current_liabilities: float) -> float:
    """
    Working Capital
    Formula: Current Assets - Current Liabilities
    """
    return current_assets - current_liabilities


def net_working_capital_ratio(current_assets: float, current_liabilities: float, total_assets: float) -> float:
    """
    Net Working Capital Ratio
    Formula: (Current Assets - Current Liabilities) / Total Assets
    """
    return (current_assets - current_liabilities) / total_assets


def daily_operating_expenses(annual_operating_expenses: float) -> float:
    """
    Daily Operating Expenses (for Defensive Interval Ratio)
    Formula: Annual Operating Expenses / 365
    """
    return annual_operating_expenses / 365


def defensive_interval_ratio(cash: float, marketable_securities: float, accounts_receivable: float,
                               daily_operating_expenses: float) -> float:
    """
    Defensive Interval Ratio
    Formula: (Cash + Marketable Securities + Accounts Receivable) / Daily Operating Expenses
    Where: Daily Operating Expenses = Annual Operating Expenses / 365
    """
    return (cash + marketable_securities + accounts_receivable) / daily_operating_expenses


def cash_flow_coverage_ratio(operating_cash_flow: float, total_debt: float) -> float:
    """
    Cash Flow Coverage Ratio
    Formula: Operating Cash Flow / Total Debt
    """
    return operating_cash_flow / total_debt


def operating_cash_flow_to_current_liabilities(operating_cash_flow: float, current_liabilities: float) -> float:
    """
    Operating Cash Flow to Current Liabilities
    Formula: Operating Cash Flow / Current Liabilities
    """
    return operating_cash_flow / current_liabilities