def gross_profit(total_revenue: float, cogs: float) -> float:
    """
    Gross Profit
    Formula: Revenue - Cost of Goods Sold (COGS)
    """
    return total_revenue - cogs

def operating_income(gross_profit: float, operating_expenses: float) -> float:
    """
    Operating Income (EBIT)
    Formula: Gross Profit - Operating Expenses (SG&A, R&D)
    """
    return gross_profit - operating_expenses

def earnings_before_tax(operating_profit: float, other_income_expense: float) -> float:
    """
    Earnings Before Tax (EBT)
    Formula: Operating Income +/- Other Income/Expense
    """
    return operating_profit + other_income_expense

def net_income(profit_before_tax: float, income_tax: float) -> float:
    """
    Net Income
    Formula: Earnings Before Tax - Income Tax
    """
    return profit_before_tax - income_tax

def net_income_available_to_common_shareholders(profit_for_the_year: float, preferred_dividends: float) -> float:
    """
    Net Income Available to Common Shareholders
    Formula: Net Income - Preferred Dividends
    """
    return profit_for_the_year - preferred_dividends

def shareholders_equity(total_assets: float, total_liabilities: float) -> float:
    """
    Shareholders' Equity
    Formula: Assets = Liabilities + Shareholders' Equity
    => Shareholders' Equity = Total Assets - Total Liabilities
    """
    return total_assets - total_liabilities

def net_change_in_cash(cash_from_operations: float, cash_from_investing: float, cash_from_financing: float) -> float:
    """
    Net Change in Cash
    Formula: Cash from Operating Activities + Cash from Investing Activities + Cash from Financing Activities
    """
    return cash_from_operations + cash_from_investing + cash_from_financing

def ending_retained_earnings(beginning_retained_earnings: float, profit_for_the_year: float, dividends_paid: float) -> float:
    """
    Ending Retained Earnings
    Formula: Beginning Retained Earnings + Net Income - Dividends Paid
    """
    return beginning_retained_earnings + profit_for_the_year - dividends_paid

def balance_sheet_equation(total_assets: float, total_liabilities: float, equity: float) -> bool:
    """
    Balance Sheet Equation Verification
    Formula: Assets = Liabilities + Shareholders' Equity
    Returns True if the equation balances
    """
    return total_assets == total_liabilities + equity

def current_plus_non_current_assets(current_assets: float, non_current_assets: float) -> float:
    """
    Current Assets + Non-Current Assets
    Formula: Total Assets = Current Assets + Non-Current Assets
    """
    return current_assets + non_current_assets

def current_plus_long_term_liabilities_plus_equity(current_liabilities: float, long_term_liabilities: float, equity: float) -> float:
    """
    Current Liabilities + Long-term Liabilities + Equity
    Formula: Total Liabilities and Equity = Current Liabilities + Long-term Liabilities + Equity
    """
    return current_liabilities + long_term_liabilities + equity