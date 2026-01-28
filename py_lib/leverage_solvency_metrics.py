def debt_to_equity_ratio(total_debt: float, total_shareholders_equity: float) -> float:
    """
    Debt-to-Equity Ratio
    Formula: Total Debt / Total Shareholders' Equity
    """
    return total_debt / total_shareholders_equity


def debt_to_assets_ratio(total_debt: float, total_assets: float) -> float:
    """
    Debt-to-Assets Ratio
    Formula: Total Debt / Total Assets
    """
    return total_debt / total_assets


def debt_to_ebitda_ratio(total_debt: float, ebitda: float) -> float:
    """
    Debt-to-EBITDA Ratio
    Formula: Total Debt / EBITDA
    """
    return total_debt / ebitda


def interest_coverage_ratio(ebit: float, interest_expense: float) -> float:
    """
    Interest Coverage Ratio
    Formula: EBIT / Interest Expense
    """
    return ebit / interest_expense


def debt_service_coverage_ratio(net_operating_income: float, principal_repayment: float, interest_payments: float) -> float:
    """
    Debt Service Coverage Ratio (DSCR)
    Formula: Net Operating Income / Total Debt Service
    Where: Total Debt Service = Principal Repayment + Interest Payments
    """
    total_debt_service = principal_repayment + interest_payments
    return net_operating_income / total_debt_service


def equity_multiplier(total_assets: float, total_shareholders_equity: float) -> float:
    """
    Equity Multiplier
    Formula: Total Assets / Total Shareholders' Equity
    """
    return total_assets / total_shareholders_equity


def financial_leverage_ratio(total_assets: float, total_equity: float) -> float:
    """
    Financial Leverage Ratio
    Formula: Total Assets / Total Equity
    """
    return total_assets / total_equity


def total_debt_ratio(total_debt: float, total_assets: float) -> float:
    """
    Total Debt Ratio
    Formula: Total Debt / Total Assets
    """
    return total_debt / total_assets


def long_term_debt_to_equity(long_term_debt: float, total_shareholders_equity: float) -> float:
    """
    Long-term Debt to Equity
    Formula: Long-term Debt / Total Shareholders' Equity
    """
    return long_term_debt / total_shareholders_equity


def fixed_charge_coverage_ratio(ebit: float, fixed_charges: float, interest_expense: float) -> float:
    """
    Fixed Charge Coverage Ratio
    Formula: (EBIT + Fixed Charges) / (Fixed Charges + Interest Expense)
    """
    return (ebit + fixed_charges) / (fixed_charges + interest_expense)


def times_interest_earned(ebit: float, interest_expense: float) -> float:
    """
    Times Interest Earned (TIE)
    Formula: EBIT / Interest Expense
    """
    return ebit / interest_expense


def debt_to_capital_ratio(total_debt: float, total_equity: float) -> float:
    """
    Debt-to-Capital Ratio
    Formula: Total Debt / (Total Debt + Total Equity)
    """
    return total_debt / (total_debt + total_equity)


def net_debt_to_ebitda(total_debt: float, cash_and_cash_equivalents: float, ebitda: float) -> float:
    """
    Net Debt-to-EBITDA
    Formula: (Total Debt - Cash & Cash Equivalents) / EBITDA
    """
    net_debt = total_debt - cash_and_cash_equivalents
    return net_debt / ebitda


def net_debt_to_equity(total_debt: float, cash_and_cash_equivalents: float, total_equity: float) -> float:
    """
    Net Debt-to-Equity
    Formula: (Total Debt - Cash & Cash Equivalents) / Total Equity
    """
    net_debt = total_debt - cash_and_cash_equivalents
    return net_debt / total_equity


def capitalization_ratio(long_term_debt: float, shareholders_equity: float) -> float:
    """
    Capitalization Ratio
    Formula: Long-term Debt / (Long-term Debt + Shareholders' Equity)
    """
    return long_term_debt / (long_term_debt + shareholders_equity)
