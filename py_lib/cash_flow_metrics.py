"""
Cash Flow Metrics
Python implementation of formulas from Section 3 of Financial Metrics Guide
"""


# =============================================================================
# CASH FLOW METRICS
# =============================================================================


def operating_cash_flow(net_income: float, non_cash_expenses: float, change_in_working_capital: float) -> float:
    """
    Operating Cash Flow (OCF)
    Formula: Net Income + Non-Cash Expenses + Changes in Working Capital
    """
    return net_income + non_cash_expenses + change_in_working_capital


def operating_cash_flow_alt(ebitda: float, taxes_paid: float, change_in_nwc: float) -> float:
    """
    Operating Cash Flow (OCF) - Alternative
    Formula: EBITDA - Taxes Paid - Change in Net Working Capital
    """
    return ebitda - taxes_paid - change_in_nwc


def free_cash_flow(operating_cash_flow: float, capital_expenditures: float) -> float:
    """
    Free Cash Flow (FCF)
    Formula: Operating Cash Flow - Capital Expenditures
    """
    return operating_cash_flow - capital_expenditures


def free_cash_flow_alt(ocf: float, capex: float) -> float:
    """
    Free Cash Flow (FCF) - Alternative
    Formula: OCF - CapEx
    """
    return ocf - capex


def free_cash_flow_to_equity(net_income: float, capex: float, depreciation: float, change_in_nwc: float,
                              new_debt: float, debt_repayment: float) -> float:
    """
    Free Cash Flow to Equity (FCFE)
    Formula: Net Income - (CapEx - Depreciation) - Change in NWC + (New Debt - Debt Repayment)
    """
    return net_income - (capex - depreciation) - change_in_nwc + (new_debt - debt_repayment)


def free_cash_flow_to_equity_alt(ocf: float, capex: float, net_borrowing: float) -> float:
    """
    Free Cash Flow to Equity (FCFE) - Alternative
    Formula: OCF - CapEx + Net Borrowing
    """
    return ocf - capex + net_borrowing


def free_cash_flow_to_firm(ebit: float, tax_rate: float, depreciation: float, capex: float, change_in_nwc: float) -> float:
    """
    Free Cash Flow to Firm (FCFF)
    Formula: EBIT(1 - Tax Rate) + Depreciation - CapEx - Change in NWC
    """
    return (ebit * (1 - tax_rate)) + depreciation - capex - change_in_nwc


def free_cash_flow_to_firm_alt1(nopat: float, depreciation: float, capex: float, change_in_nwc: float) -> float:
    """
    Free Cash Flow to Firm (FCFF) - Alternative 1
    Formula: NOPAT + Depreciation - CapEx - Change in NWC
    """
    return nopat + depreciation - capex - change_in_nwc


def free_cash_flow_to_firm_alt2(cfo: float, interest_expense: float, tax_rate: float, capex: float) -> float:
    """
    Free Cash Flow to Firm (FCFF) - Alternative 2
    Formula: CFO + Interest Expense(1 - Tax Rate) - CapEx
    """
    return cfo + (interest_expense * (1 - tax_rate)) - capex


def cash_flow_per_share(operating_cash_flow: float, shares_outstanding: float) -> float:
    """
    Cash Flow Per Share
    Formula: Operating Cash Flow / Shares Outstanding
    """
    return operating_cash_flow / shares_outstanding


def cash_flow_per_share_alt(free_cash_flow: float, shares_outstanding: float) -> float:
    """
    Cash Flow Per Share - Alternative
    Formula: Free Cash Flow / Shares Outstanding
    """
    return free_cash_flow / shares_outstanding


def free_cash_flow_margin(free_cash_flow: float, total_revenue: float) -> float:
    """
    Free Cash Flow Margin
    Formula: (Free Cash Flow / Total Revenue) × 100
    """
    return (free_cash_flow / total_revenue) * 100


def cash_flow_to_debt_ratio(operating_cash_flow: float, total_debt: float) -> float:
    """
    Cash Flow-to-Debt Ratio
    Formula: Operating Cash Flow / Total Debt
    """
    return operating_cash_flow / total_debt


def operating_cash_flow_ratio(operating_cash_flow: float, current_liabilities: float) -> float:
    """
    Operating Cash Flow Ratio
    Formula: Operating Cash Flow / Current Liabilities
    """
    return operating_cash_flow / current_liabilities


def gross_cash_flow(ebitda: float, cash_taxes: float) -> float:
    """
    Gross Cash Flow (for CFROI)
    Formula: EBITDA - Cash Taxes
    """
    return ebitda - cash_taxes


def cash_flow_return_on_investment(gross_cash_flow: float, gross_investment: float) -> float:
    """
    Cash Flow Return on Investment (CFROI)
    Formula: [Gross Cash Flow / Gross Investment] × 100
    Where: Gross Cash Flow = EBITDA - Cash Taxes
           Gross Investment = Total Assets adjusted for depreciation
    """
    return (gross_cash_flow / gross_investment) * 100


def unlevered_free_cash_flow(ebit: float, tax_rate: float, depreciation: float, capex: float, change_in_nwc: float) -> float:
    """
    Unlevered Free Cash Flow
    Formula: EBIT(1 - Tax Rate) + Depreciation - CapEx - Change in NWC
    """
    return (ebit * (1 - tax_rate)) + depreciation - capex - change_in_nwc


def levered_free_cash_flow(net_income: float, depreciation: float, capex: float, change_in_nwc: float,
                           debt_repayment: float, new_debt: float) -> float:
    """
    Levered Free Cash Flow
    Formula: Net Income + Depreciation - CapEx - Change in NWC - Debt Repayment + New Debt
    """
    return net_income + depreciation - capex - change_in_nwc - debt_repayment + new_debt


def owner_earnings(net_income: float, depreciation_amortization: float, capex: float, additional_working_capital: float) -> float:
    """
    Owner Earnings (Buffett's metric)
    Formula: Net Income + Depreciation & Amortization - CapEx - Additional Working Capital
    """
    return net_income + depreciation_amortization - capex - additional_working_capital


def free_cash_flow_per_share(free_cash_flow: float, shares_outstanding: float) -> float:
    """
    Free Cash Flow Per Share
    Formula: Free Cash Flow / Shares Outstanding
    """
    return free_cash_flow / shares_outstanding