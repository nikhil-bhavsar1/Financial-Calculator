import math


def graham_number(eps: float, bvps: float) -> float:
    """
    Graham Number (Maximum Fair Value)
    Formula: √(22.5 × EPS × BVPS)
    Where: BVPS = Book Value Per Share
    
    Interpretation: Stock is undervalued if trading below Graham Number
    
    Derivation: Based on max P/E of 15 and max P/B of 1.5
    15 × 1.5 = 22.5
    """
    return math.sqrt(22.5 * eps * bvps)


def graham_intrinsic_value_original(eps: float, expected_growth_rate: float) -> float:
    """
    Original Graham Formula (1962)
    Formula: Intrinsic Value = EPS × (8.5 + 2g)
    
    Where:
    EPS = Trailing 12-month earnings per share
    8.5 = P/E base for no-growth company
    g = Expected annual growth rate (next 7-10 years)
    """
    return eps * (8.5 + 2 * expected_growth_rate)


def graham_intrinsic_value_revised(eps: float, expected_growth_rate: float, aaa_bond_yield: float) -> float:
    """
    Revised Graham Formula (1974 - with bond yields)
    Formula: Intrinsic Value = [EPS × (8.5 + 2g) × 4.4] / Y
    
    Where:
    Y = Current yield on AAA corporate bonds
    4.4 = Average AAA bond yield when formula created
    
    This adjusts for interest rate environment
    """
    return (eps * (8.5 + 2 * expected_growth_rate) * 4.4) / aaa_bond_yield


def ncav_per_share(current_assets: float, total_liabilities: float, shares_outstanding: float) -> float:
    """
    NCAV Per Share
    Formula: NCAV = (Current Assets - Total Liabilities) / Shares Outstanding
    """
    return (current_assets - total_liabilities) / shares_outstanding


def graham_ncav_buy_rule(stock_price: float, ncav: float, multiple: float = 0.67) -> bool:
    """
    Graham's NCAV Buy Rule
    Buy when: Stock Price < (2/3 × NCAV)
    Conservative variation: Price < 0.5 × NCAV
    
    Returns True if stock should be bought
    """
    return stock_price < (multiple * ncav)


def net_net_working_capital(current_assets: float, total_liabilities: float, inventory: float, shares_outstanding: float) -> float:
    """
    Net-Net Working Capital (Per Share)
    Formula: Net-Net = (Current Assets - Total Liabilities) - (0.5 × Inventory)
    Per Share = Net-Net / Shares Outstanding
    """
    net_net = (current_assets - total_liabilities) - (0.5 * inventory)
    return net_net / shares_outstanding


def graham_defensive_company_size(annual_sales: float, minimum_sales: float = 500000000) -> bool:
    """
    Defensive Investor Criteria - Company Size
    Formula: Annual sales > $100 million (adjust for inflation)
    Today's equivalent: > $500 million
    
    Returns True if company meets size criteria
    """
    return annual_sales > minimum_sales


def graham_defensive_current_ratio(current_assets: float, current_liabilities: float) -> bool:
    """
    Defensive Investor Criteria - Financial Condition
    Formula: Current Ratio ≥ 2.0
    Formula: Current Assets / Current Liabilities ≥ 2.0
    
    Returns True if company meets current ratio criteria
    """
    return (current_assets / current_liabilities) >= 2.0


def graham_defensive_debt_level(long_term_debt: float, current_assets: float, current_liabilities: float) -> bool:
    """
    Defensive Investor Criteria - Debt Level
    Formula: Long-term Debt < 2 × Net Current Assets
    Formula: LT Debt / (Current Assets - Current Liabilities) < 2.0
    
    Returns True if company meets debt level criteria
    """
    net_current_assets = current_assets - current_liabilities
    if net_current_assets <= 0:
        return False
    return long_term_debt < (2.0 * net_current_assets)


def graham_defensive_earnings_growth(current_3yr_avg_eps: float, eps_10_years_ago: float) -> bool:
    """
    Defensive Investor Criteria - Earnings Growth
    Formula: (Current 3-yr avg EPS / 3-yr avg EPS 10 years ago) ≥ 1.33
    
    Returns True if company meets earnings growth criteria
    """
    if eps_10_years_ago <= 0:
        return False
    return (current_3yr_avg_eps / eps_10_years_ago) >= 1.33


def graham_defensive_pe_ratio(stock_price: float, three_year_avg_eps: float) -> bool:
    """
    Defensive Investor Criteria - P/E Ratio
    Formula: Current P/E ≤ 15
    Formula: Stock Price / (3-year average EPS) ≤ 15
    
    Returns True if company meets P/E criteria
    """
    if three_year_avg_eps <= 0:
        return False
    return (stock_price / three_year_avg_eps) <= 15.0


def graham_defensive_pb_ratio(stock_price: float, book_value_per_share: float) -> bool:
    """
    Defensive Investor Criteria - P/B Ratio
    Formula: P/B ≤ 1.5
    Formula: Stock Price / Book Value Per Share ≤ 1.5
    
    Returns True if company meets P/B criteria
    """
    if book_value_per_share <= 0:
        return False
    return (stock_price / book_value_per_share) <= 1.5


def graham_defensive_combined_pe_pb(pe_ratio: float, pb_ratio: float) -> bool:
    """
    Defensive Investor Criteria - Combined P/E and P/B
    Formula: P/E × P/B ≤ 22.5
    Allows some flexibility: high P/E with low P/B, or vice versa
    
    Returns True if company meets combined criteria
    """
    return (pe_ratio * pb_ratio) <= 22.5


def graham_enterprising_current_ratio(current_assets: float, current_liabilities: float) -> bool:
    """
    Enterprising Investor Criteria - Financial Condition
    Formula: Current Ratio ≥ 1.5
    
    Returns True if company meets current ratio criteria
    """
    return (current_assets / current_liabilities) >= 1.5


def graham_enterprising_debt_to_working_capital(total_debt: float, current_assets: float, current_liabilities: float) -> bool:
    """
    Enterprising Investor Criteria - Debt to Working Capital
    Formula: Total Debt / (Current Assets - Current Liabilities) < 1.1
    
    Returns True if company meets debt to working capital criteria
    """
    net_current_assets = current_assets - current_liabilities
    if net_current_assets <= 0:
        return False
    return total_debt < (1.1 * net_current_assets)


def graham_enterprising_price_limit(stock_price: float, book_value: float, intangible_assets: float) -> bool:
    """
    Enterprising Investor Criteria - Price Limit
    Formula: Price < 120% of Net Tangible Assets
    Formula: Price / (Book Value - Intangibles) < 1.2
    
    Returns True if company meets price limit criteria
    """
    net_tangible_assets = book_value - intangible_assets
    if net_tangible_assets <= 0:
        return False
    return stock_price < (1.2 * net_tangible_assets)


def margin_of_safety_percentage(intrinsic_value: float, market_price: float) -> float:
    """
    Margin of Safety (Percentage)
    Formula: MOS = [(Intrinsic Value - Market Price) / Intrinsic Value] × 100
    """
    if intrinsic_value <= 0:
        return 0
    return ((intrinsic_value - market_price) / intrinsic_value) * 100


def graham_margin_of_safety_33(intrinsic_value: float, market_price: float) -> bool:
    """
    Graham's Minimum MOS (33%)
    Formula: Market Price ≤ (0.67 × Intrinsic Value) [33% MOS]
    
    Returns True if stock has adequate margin of safety
    """
    return market_price <= (0.67 * intrinsic_value)


def graham_margin_of_safety_50(intrinsic_value: float, market_price: float) -> bool:
    """
    Graham's Preferred MOS (50%)
    Formula: Market Price ≤ (0.50 × Intrinsic Value) [50% MOS]
    
    Returns True if stock has preferred margin of safety
    """
    return market_price <= (0.50 * intrinsic_value)


def liquidation_value_per_share(current_assets: float, total_liabilities: float, preferred_stock: float, common_shares: float, receivables: float, inventory: float, cash: float) -> float:
    """
    Liquidation Value Per Share
    Formula: (Current Assets - Total Liabilities - Preferred Stock) / Common Shares
    
    Conservative estimate:
    Liquidation = (0.75 × Receivables) + (0.5 × Inventory) + Cash - Total Liabilities
    """
    conservative_liquidation = (0.75 * receivables) + (0.5 * inventory) + cash - total_liabilities
    return conservative_liquidation / common_shares


def book_value_per_share_tangible(total_equity: float, intangible_assets: float, goodwill: float, shares_outstanding: float) -> float:
    """
    Book Value Per Share (Tangible)
    Formula: (Total Equity - Intangible Assets - Goodwill) / Shares Outstanding
    """
    tangible_equity = total_equity - intangible_assets - goodwill
    return tangible_equity / shares_outstanding


def earnings_power_value(adjusted_earnings: float, required_rate_of_return: float) -> float:
    """
    Earnings Power Value (EPV)
    Formula: EPV = Adjusted Earnings / Required Rate of Return
    EPV = Adjusted Earnings × (1 / R)
    """
    return adjusted_earnings / required_rate_of_return


def net_working_capital(current_assets: float, current_liabilities: float) -> float:
    """
    Net Working Capital
    Formula: NWC = Current Assets - Current Liabilities
    """
    return current_assets - current_liabilities


def working_capital_ratio(current_assets: float, current_liabilities: float, total_assets: float) -> float:
    """
    Working Capital Ratio
    Formula: WC Ratio = (Current Assets - Current Liabilities) / Total Assets
    """
    return (current_assets - current_liabilities) / total_assets


def graham_working_capital_rule(net_working_capital: float, total_debt: float) -> bool:
    """
    Graham's Working Capital Rule
    For industrials: NWC should be ≥ 50% of total debt
    
    Returns True if company meets working capital rule
    """
    return net_working_capital >= (0.5 * total_debt)


def graham_central_value(assets: float, earning_power: float, multiplier: float = 10.0) -> float:
    """
    Graham's Central Value Concept (Simplified)
    Formula: Value = Assets + (Multiplier × Earning Power)
    
    Where typical multiplier = 10-15 for average company
    """
    return assets + (multiplier * earning_power)
