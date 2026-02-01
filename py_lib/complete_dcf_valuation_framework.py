def fcff(operating_profit: float, tax_rate: float, depreciation: float, capex: float, change_in_nwc: float) -> float:
    """
    Free Cash Flow to Firm (FCFF)
    Formula: EBIT(1 - Tax Rate) + Depreciation - CapEx - Change in NWC
    """
    return operating_profit * (1 - tax_rate) + depreciation - capex - change_in_nwc

def fcff_from_nopat(nopat: float, depreciation: float, capex: float, change_in_nwc: float) -> float:
    """
    Free Cash Flow to Firm (FCFF) - from NOPAT
    Formula: NOPAT + Depreciation - CapEx - Change in NWC
    """
    return nopat + depreciation - capex - change_in_nwc

def fcff_from_cfo(net_cash_from_operating_activities: float, finance_cost: float, tax_rate: float, capex: float) -> float:
    """
    Free Cash Flow to Firm (FCFF) - from CFO
    Formula: CFO + Interest Expense(1 - Tax Rate) - CapEx
    """
    return net_cash_from_operating_activities + finance_cost * (1 - tax_rate) - capex

def fcff_from_net_income(profit_for_the_year: float, finance_cost: float, tax_rate: float, depreciation: float, capex: float, change_in_nwc: float) -> float:
    """
    Free Cash Flow to Firm (FCFF) - from Net Income
    Formula: Net Income + Interest(1 - Tax Rate) + Depreciation - CapEx - Change in NWC
    """
    return profit_for_the_year + finance_cost * (1 - tax_rate) + depreciation - capex - change_in_nwc

def wacc(equity_value: float, debt_value: float, cost_of_equity: float, cost_of_debt: float, tax_rate: float) -> float:
    """
    Weighted Average Cost of Capital (WACC)
    Formula: (E/V × Re) + (D/V × Rd × (1 - Tc))
    Where:
    E = Market value of equity
    D = Market value of debt
    V = E + D (total firm value)
    Re = Cost of equity
    Rd = Cost of debt
    Tc = Corporate tax rate
    """
    total_value = equity_value + debt_value
    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value
    return equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)

def cost_of_equity_capm(risk_free_rate: float, beta: float, market_return: float) -> float:
    """
    Cost of Equity (CAPM)
    Formula: Re = Rf + β × (Rm - Rf)
    Where:
    Rf = Risk-free rate
    β = Beta (systematic risk)
    Rm = Expected market return
    (Rm - Rf) = Market risk premium
    """
    return risk_free_rate + beta * (market_return - risk_free_rate)

def terminal_value_gordon_growth(fcff_next_year: float, wacc: float, growth_rate: float) -> float:
    """
    Terminal Value - Gordon Growth Model
    Formula: TV = FCFFn+1 / (WACC - g)
    Where: FCFFn+1 = FCFF in year n+1
           g = perpetual growth rate (typically 2-3%)
    """
    return fcff_next_year / (wacc - growth_rate)

def terminal_value_exit_multiple(ev_ebitda_multiple: float, ebitda: float) -> float:
    """
    Terminal Value - Exit Multiple Method (EV/EBITDA)
    Formula: TV = EV/EBITDA multiple × EBITDAn
    """
    return ev_ebitda_multiple * ebitda

def terminal_value_pe_multiple(pe_multiple: float, earnings: float) -> float:
    """
    Terminal Value - Exit Multiple Method (P/E)
    Formula: TV = P/E multiple × Earningsn
    """
    return pe_multiple * earnings

def present_value_fcff(fcff_values: list, wacc: float) -> float:
    """
    Present Value of FCFF during projection period
    Formula: PV of FCFF = FCFF₁/(1+WACC)¹ + FCFF₂/(1+WACC)² + ... + FCFFn/(1+WACC)ⁿ
    """
    pv = 0
    for i, fcff in enumerate(fcff_values, start=1):
        pv += fcff / (1 + wacc) ** i
    return pv

def present_value_terminal_value(terminal_value: float, wacc: float, num_years: float) -> float:
    """
    Present Value of Terminal Value
    Formula: PV of TV = TV / (1 + WACC)ⁿ
    """
    return terminal_value / (1 + wacc) ** num_years

def enterprise_value(pv_fcff: float, pv_terminal_value: float) -> float:
    """
    Enterprise Value
    Formula: Enterprise Value = PV of FCFF during projection period + PV of Terminal Value
    """
    return pv_fcff + pv_terminal_value

def equity_value_from_ev(enterprise_value: float, net_debt: float, preferred_stock: float, non_operating_assets: float) -> float:
    """
    Equity Value
    Formula: Equity Value = Enterprise Value - Net Debt - Preferred Stock + Non-Operating Assets
    Where: Net Debt = Total Debt - Cash and Cash Equivalents
    """
    return enterprise_value - net_debt - preferred_stock + non_operating_assets

def net_debt(total_borrowings: float, cash_and_cash_equivalents: float) -> float:
    """
    Net Debt
    Formula: Net Debt = Total Debt - Cash and Cash Equivalents
    """
    return total_borrowings - cash_and_cash_equivalents

def fair_value_per_share(equity_value: float, number_of_shares: float) -> float:
    """
    Fair Value Per Share
    Formula: Fair Value Per Share = Equity Value / Shares Outstanding
    """
    return equity_value / number_of_shares

def fcfe(profit_for_the_year: float, capex: float, depreciation: float, change_in_nwc: float, new_debt: float, debt_repayment: float) -> float:
    """
    Free Cash Flow to Equity (FCFE)
    Formula: FCFE = Net Income - (CapEx - Depreciation) - Change in NWC + (New Debt - Debt Repayment)
    """
    return profit_for_the_year - (capex - depreciation) - change_in_nwc + (new_debt - debt_repayment)

def fcfe_from_fcff(fcff: float, finance_cost: float, tax_rate: float, net_borrowing: float) -> float:
    """
    Free Cash Flow to Equity (FCFE) - from FCFF
    Formula: FCFE = FCFF - Interest(1 - Tax Rate) + Net Borrowing
    """
    return fcff - finance_cost * (1 - tax_rate) + net_borrowing

def present_value_fcfe(fcfe_values: list, cost_of_equity: float) -> float:
    """
    Present Value of FCFE during projection period
    Formula: PV of FCFE = FCFE₁/(1+Re)¹ + FCFE₂/(1+Re)² + ... + FCFEn/(1+Re)ⁿ
    """
    pv = 0
    for i, fcfe in enumerate(fcfe_values, start=1):
        pv += fcfe / (1 + cost_of_equity) ** i
    return pv

def terminal_value_fcfe_gordon_growth(fcfe_next_year: float, cost_of_equity: float, growth_rate: float) -> float:
    """
    Terminal Value - FCFE Gordon Growth Model
    Formula: TV = FCFEn+1 / (Re - g)
    """
    return fcfe_next_year / (cost_of_equity - growth_rate)

def equity_value_from_fcfe(pv_fcfe: float, pv_terminal_value: float) -> float:
    """
    Equity Value - from FCFE
    Formula: Equity Value = PV of FCFE during projection period + PV of Terminal Value
    """
    return pv_fcfe + pv_terminal_value

def gordon_growth_ddm(dividend_next_year: float, cost_of_equity: float, growth_rate: float) -> float:
    """
    Gordon Growth Model (Constant Growth DDM)
    Formula: P₀ = D₁ / (Re - g)
    Where:
    P₀ = Current stock price
    D₁ = Expected dividend next year = D₀(1 + g)
    Re = Required rate of return (cost of equity)
    g = Constant growth rate of dividends
    """
    return dividend_next_year / (cost_of_equity - growth_rate)

def dividend_next_year(current_dividend: float, growth_rate: float) -> float:
    """
    Expected Dividend Next Year
    Formula: D₁ = D₀(1 + g)
    Where: D₀ = Current dividend
           g = Growth rate
    """
    return current_dividend * (1 + growth_rate)

def two_stage_ddm(dividends: list, cost_of_equity: float, terminal_dividend: float, stable_growth_rate: float, high_growth_years: float) -> float:
    """
    Two-Stage DDM
    Formula: P₀ = Σ[Dt/(1+Re)ᵗ] + [Pn/(1+Re)ⁿ]
    Where: Pn = Dn+1 / (Re - g) for stable growth phase
    """
    pv_dividends = 0
    for i, dividend in enumerate(dividends, start=1):
        pv_dividends += dividend / (1 + cost_of_equity) ** i
    terminal_value = terminal_dividend / (cost_of_equity - stable_growth_rate)
    pv_terminal_value = terminal_value / (1 + cost_of_equity) ** high_growth_years
    return pv_dividends + pv_terminal_value

def unlevered_firm_value(fcff_values: list, terminal_value: float, unlevered_cost_of_equity: float) -> float:
    """
    Unlevered Firm Value
    Formula: VU = Σ[FCFF/(1+Ru)ᵗ] + TV/(1+Ru)ⁿ
    Where: Ru = Unlevered cost of equity
    """
    pv_fcff = 0
    for i, fcff in enumerate(fcff_values, start=1):
        pv_fcff += fcff / (1 + unlevered_cost_of_equity) ** i
    num_years = len(fcff_values)
    pv_terminal_value = terminal_value / (1 + unlevered_cost_of_equity) ** num_years
    return pv_fcff + pv_terminal_value

def pv_tax_shield_perpetual(debt: float, tax_rate: float) -> float:
    """
    Present Value of Tax Shield (Perpetual Debt)
    Formula: PV(Tax Shield) = Debt × Tax Rate
    """
    return debt * tax_rate

def pv_tax_shield(interest_payments: list, cost_of_debt: float, tax_rate: float) -> float:
    """
    Present Value of Tax Shield
    Formula: PV(Tax Shield) = Σ[Interest × Tax Rate / (1+Rd)ᵗ]
    """
    pv = 0
    for i, interest in enumerate(interest_payments, start=1):
        pv += interest * tax_rate / (1 + cost_of_debt) ** i
    return pv

def adjusted_present_value(unlevered_value: float, pv_tax_shield: float, pv_financial_distress_costs: float) -> float:
    """
    Adjusted Present Value (APV)
    Formula: APV = Unlevered Firm Value + PV of Tax Shield - PV of Financial Distress Costs
    """
    return unlevered_value + pv_tax_shield - pv_financial_distress_costs