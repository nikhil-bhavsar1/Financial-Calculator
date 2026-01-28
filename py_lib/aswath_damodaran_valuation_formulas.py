import math


def cost_of_equity_capm(risk_free_rate: float, beta: float, equity_risk_premium: float) -> float:
    """
    Cost of Equity (CAPM)
    Formula: Re = Rf + β × ERP
    Where: ERP = Equity Risk Premium = (Rm - Rf)
    """
    return risk_free_rate + beta * equity_risk_premium


def cost_of_equity_multifactor(risk_free_rate: float, factor_betas: list, factor_premiums: list) -> float:
    """
    Cost of Equity (Multi-Factor Model)
    Formula: Re = Rf + β₁(Factor 1 Premium) + β₂(Factor 2 Premium) + ...
    """
    cost = risk_free_rate
    for beta, premium in zip(factor_betas, factor_premiums):
        cost += beta * premium
    return cost


def cost_of_equity_build_up(risk_free_rate: float, equity_risk_premium: float, size_premium: float, industry_risk_premium: float, company_specific_risk: float) -> float:
    """
    Cost of Equity (Build-Up Method)
    Formula: Re = Rf + Equity Risk Premium + Size Premium + Industry Risk Premium + Company-Specific Risk
    """
    return risk_free_rate + equity_risk_premium + size_premium + industry_risk_premium + company_specific_risk


def cost_of_debt(interest_expense: float, average_debt_outstanding: float) -> float:
    """
    Cost of Debt
    Formula: Rd = Interest Expense / Average Debt Outstanding
    Alternative: Rd = YTM on company's bonds
    """
    return interest_expense / average_debt_outstanding


def after_tax_cost_of_debt(cost_of_debt: float, tax_rate: float) -> float:
    """
    After-Tax Cost of Debt
    Formula: Rd(after-tax) = Rd × (1 - Tax Rate)
    """
    return cost_of_debt * (1 - tax_rate)


def wacc_complete(equity_value: float, debt_value: float, preferred_value: float, cost_of_equity: float, cost_of_debt: float, cost_of_preferred: float, tax_rate: float) -> float:
    """
    Weighted Average Cost of Capital (WACC) - Complete
    Formula: WACC = (E/V)×Re + (D/V)×Rd×(1-T) + (P/V)×Rp
    Where: P = Preferred stock, Rp = Cost of preferred stock
    """
    total_value = equity_value + debt_value + preferred_value
    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value
    preferred_weight = preferred_value / total_value
    return (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate)) + (preferred_weight * cost_of_preferred)


def levered_beta(unlevered_beta: float, tax_rate: float, debt_to_equity: float) -> float:
    """
    Levered Beta (Adding Financial Leverage)
    Formula: βL = βU × [1 + (1 - T) × (D/E)]
    Where: βL = Levered beta
           βU = Unlevered beta
           T = Tax rate
           D/E = Debt-to-equity ratio
    """
    return unlevered_beta * (1 + (1 - tax_rate) * debt_to_equity)


def unlevered_beta(levered_beta: float, tax_rate: float, debt_to_equity: float) -> float:
    """
    Unlevered Beta (Removing Financial Leverage)
    Formula: βU = βL / [1 + (1 - T) × (D/E)]
    """
    return levered_beta / (1 + (1 - tax_rate) * debt_to_equity)


def adjusted_beta_bloomberg(raw_beta: float) -> float:
    """
    Adjusted Beta (Bloomberg Method)
    Formula: Adjusted β = (0.67 × Raw β) + (0.33 × 1.0)
    """
    return (0.67 * raw_beta) + (0.33 * 1.0)


def bottom_up_beta(segment_weights: list, unlevered_betas: list, tax_rate: float, debt_to_equity: float) -> float:
    """
    Bottom-Up Beta
    Formula: βFirm = Σ(Business Segment Weightᵢ × βUnlevered,i) × [1 + (1-T) × (D/E)]
    """
    unlevered_firm_beta = sum(w * b for w, b in zip(segment_weights, unlevered_betas))
    return unlevered_firm_beta * (1 + (1 - tax_rate) * debt_to_equity)


def country_risk_premium(country_default_spread: float, equity_volatility_country: float, bond_volatility_country: float) -> float:
    """
    Country Risk Premium (Relative Volatility Method)
    Formula: CRP = Country Default Spread × (σEquity,Country / σBond,Country)
    """
    return country_default_spread * (equity_volatility_country / bond_volatility_country)


def total_cost_of_equity_country(risk_free_rate: float, beta: float, mature_market_erp: float, country_risk_premium: float) -> float:
    """
    Total Cost of Equity (with Country Risk)
    Formula: Re = Rf + β × Mature Market ERP + Country Risk Premium
    """
    return risk_free_rate + beta * mature_market_erp + country_risk_premium


def fundamental_growth_rate_equity(roe: float, retention_ratio: float) -> float:
    """
    Fundamental Growth Rate (Equity Perspective)
    Formula: g = ROE × Retention Ratio
    Where: Retention Ratio = 1 - Payout Ratio
    """
    return roe * retention_ratio


def fundamental_growth_rate_firm(return_on_capital: float, reinvestment_rate: float) -> float:
    """
    Fundamental Growth Rate (Firm Perspective)
    Formula: g = Return on Capital × Reinvestment Rate
    """
    return return_on_capital * reinvestment_rate


def expected_growth_rate_historical(ending_value: float, beginning_value: float, num_years: float) -> float:
    """
    Expected Growth Rate (Historical)
    Formula: g = (Ending Value / Beginning Value)^(1/n) - 1
    """
    return (ending_value / beginning_value) ** (1 / num_years) - 1


def reinvestment_rate_firm(capex: float, depreciation: float, delta_working_capital: float, ebit: float, tax_rate: float) -> float:
    """
    Reinvestment Rate (Firm Perspective)
    Formula: Reinvestment Rate = (CapEx - Depreciation + ΔWC) / EBIT(1-T)
    Alternative: (Net CapEx + ΔWC) / NOPAT
    """
    return (capex - depreciation + delta_working_capital) / (ebit * (1 - tax_rate))


def reinvestment_rate_equity(net_capex: float, delta_working_capital: float, nopat: float) -> float:
    """
    Reinvestment Rate (Alternative Formula)
    Formula: Reinvestment Rate = (Net CapEx + ΔWC) / NOPAT
    """
    return (net_capex + delta_working_capital) / nopat


def justified_pe_stable(payout_ratio: float, growth_rate: float, cost_of_equity: float) -> float:
    """
    Justified P/E (Stable Growth)
    Formula: P/E = Payout Ratio × (1 + g) / (Re - g)
    Alternative: P/E = (1 - Retention Ratio) × (1 + g) / (Re - g)
    """
    return payout_ratio * (1 + growth_rate) / (cost_of_equity - growth_rate)


def justified_pb_ratio(roe: float, growth_rate: float, cost_of_equity: float) -> float:
    """
    Justified P/B Ratio
    Formula: P/B = (ROE - g) / (Re - g)
    """
    return (roe - growth_rate) / (cost_of_equity - growth_rate)


def justified_ps_ratio(profit_margin: float, payout_ratio: float, growth_rate: float, cost_of_equity: float) -> float:
    """
    Justified P/S Ratio
    Formula: P/S = [Profit Margin × Payout Ratio × (1+g)] / (Re - g)
    """
    return (profit_margin * payout_ratio * (1 + growth_rate)) / (cost_of_equity - growth_rate)


def justified_ev_ebitda(tax_rate: float, reinvestment_rate: float, growth_rate: float, wacc: float) -> float:
    """
    Justified EV/EBITDA
    Formula: EV/EBITDA = [(1-T) × (1 - Reinvestment Rate) × (1+g)] / (WACC - g)
    """
    return ((1 - tax_rate) * (1 - reinvestment_rate) * (1 + growth_rate)) / (wacc - growth_rate)


def justified_ev_sales(operating_margin: float, tax_rate: float, reinvestment_rate: float, growth_rate: float, wacc: float) -> float:
    """
    Justified EV/Sales
    Formula: EV/Sales = [Operating Margin × (1-T) × (1 - Reinvestment Rate) × (1+g)] / (WACC - g)
    """
    return (operating_margin * (1 - tax_rate) * (1 - reinvestment_rate) * (1 + growth_rate)) / (wacc - growth_rate)


def peg_ratio_damodaran(pe_ratio: float, expected_growth_rate: float) -> float:
    """
    PEG Ratio (Damodaran Version)
    Formula: PEG = P/E / Expected Growth Rate
    Fair Value PEG ≈ 1.0 (assuming standard risk and payout)
    """
    return pe_ratio / expected_growth_rate


def eva_invested_capital(roic: float, wacc: float, invested_capital: float) -> float:
    """
    Economic Value Added (EVA)
    Formula: EVA = (ROIC - WACC) × Invested Capital
    """
    return (roic - wacc) * invested_capital


def value_of_firm_eva(invested_capital: float, pv_expected_eva: float) -> float:
    """
    Value of Firm (EVA Model)
    Formula: Firm Value = Invested Capital + PV of Expected EVA
    """
    return invested_capital + pv_expected_eva


def normal_cdf(x: float) -> float:
    """
    Cumulative Normal Distribution Function
    Approximation using the error function
    """
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def black_scholes_call(stock_price: float, strike_price: float, risk_free_rate: float, time_to_expiration: float, volatility: float) -> float:
    """
    Black-Scholes Call Option Value
    Formula: C = S₀N(d₁) - Ke^(-rT)N(d₂)
    
    Where:
    d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
    d₂ = d₁ - σ√T
    S₀ = Current stock price
    K = Strike price
    r = Risk-free rate
    T = Time to expiration
    σ = Volatility
    N(d) = Cumulative normal distribution
    """
    d1 = (math.log(stock_price / strike_price) + (risk_free_rate + (volatility ** 2) / 2) * time_to_expiration) / (volatility * math.sqrt(time_to_expiration))
    d2 = d1 - volatility * math.sqrt(time_to_expiration)
    
    N_d1 = normal_cdf(d1)
    N_d2 = normal_cdf(d2)
    
    return stock_price * N_d1 - strike_price * math.exp(-risk_free_rate * time_to_expiration) * N_d2


def black_scholes_put(stock_price: float, strike_price: float, risk_free_rate: float, time_to_expiration: float, volatility: float) -> float:
    """
    Black-Scholes Put Option Value
    Formula: P = Ke^(-rT)N(-d₂) - S₀N(-d₁)
    """
    d1 = (math.log(stock_price / strike_price) + (risk_free_rate + (volatility ** 2) / 2) * time_to_expiration) / (volatility * math.sqrt(time_to_expiration))
    d2 = d1 - volatility * math.sqrt(time_to_expiration)
    
    N_neg_d1 = normal_cdf(-d1)
    N_neg_d2 = normal_cdf(-d2)
    
    return strike_price * math.exp(-risk_free_rate * time_to_expiration) * N_neg_d2 - stock_price * N_neg_d1


def option_to_expand_value(pv_cash_flows: float, investment_cost: float, risk_free_rate: float, time_to_expiration: float, volatility: float) -> float:
    """
    Option to Expand
    Formula: Value = PV(Expected Cash Flows) × N(d₁) - Investment Cost × e^(-rT) × N(d₂)
    """
    return black_scholes_call(pv_cash_flows, investment_cost, risk_free_rate, time_to_expiration, volatility)


def option_to_abandon_value(pv_continuing: float, abandonment_value: float, risk_free_rate: float, time_to_expiration: float, volatility: float) -> float:
    """
    Option to Abandon
    Formula: Value = Abandonment Value × e^(-rT) × N(-d₂) - PV(Continuing) × N(-d₁)
    """
    return black_scholes_put(pv_continuing, abandonment_value, risk_free_rate, time_to_expiration, volatility)


def lack_of_marketability_discount(base_value: float, discount_percentage: float) -> float:
    """
    Lack of Marketability Discount
    Formula: Adjusted Value = Base Value × (1 - Discount)
    Discount = 20-35% (typical range)
    """
    return base_value * (1 - discount_percentage / 100)


def control_premium_value(minority_value: float, premium_percentage: float) -> float:
    """
    Control Premium
    Formula: Value with Control = Minority Value × (1 + Premium)
    Premium = 20-40% (typical range)
    """
    return minority_value * (1 + premium_percentage / 100)
