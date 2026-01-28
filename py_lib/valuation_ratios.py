"""
Financial Metrics Calculator
Python implementation of formulas from Financial Metrics Guide
"""


def price_to_earnings_ratio(market_price_per_share: float, eps: float) -> float:
    """
    Price-to-Earnings (P/E) Ratio
    Formula: Market Price Per Share / Earnings Per Share (EPS)
    """
    return market_price_per_share / eps


def price_to_earnings_ratio_alt(market_cap: float, net_income: float) -> float:
    """
    Price-to-Earnings (P/E) Ratio - Alternative
    Formula: Market Capitalization / Net Income
    """
    return market_cap / net_income


def book_value_per_share(total_equity: float, shares_outstanding: float) -> float:
    """
    Book Value Per Share
    Formula: Total Equity / Shares Outstanding
    """
    return total_equity / shares_outstanding


def price_to_book_ratio(market_price_per_share: float, book_value_per_share: float) -> float:
    """
    Price-to-Book (P/B) Ratio
    Formula: Market Price Per Share / Book Value Per Share
    """
    return market_price_per_share / book_value_per_share


def revenue_per_share(total_revenue: float, shares_outstanding: float) -> float:
    """
    Revenue Per Share
    Formula: Total Revenue / Shares Outstanding
    """
    return total_revenue / shares_outstanding


def price_to_sales_ratio(market_price_per_share: float, revenue_per_share: float) -> float:
    """
    Price-to-Sales (P/S) Ratio
    Formula: Market Price Per Share / Revenue Per Share
    """
    return market_price_per_share / revenue_per_share


def price_to_sales_ratio_alt(market_cap: float, total_revenue: float) -> float:
    """
    Price-to-Sales (P/S) Ratio - Alternative
    Formula: Market Capitalization / Total Revenue
    """
    return market_cap / total_revenue


def operating_cash_flow_per_share(operating_cash_flow: float, shares_outstanding: float) -> float:
    """
    Operating Cash Flow Per Share
    Formula: Operating Cash Flow / Shares Outstanding
    """
    return operating_cash_flow / shares_outstanding


def price_to_cash_flow_ratio(market_price_per_share: float, operating_cf_per_share: float) -> float:
    """
    Price-to-Cash Flow (P/CF) Ratio
    Formula: Market Price Per Share / Operating Cash Flow Per Share
    """
    return market_price_per_share / operating_cf_per_share


def price_to_cash_flow_ratio_alt(market_cap: float, operating_cash_flow: float) -> float:
    """
    Price-to-Cash Flow (P/CF) Ratio - Alternative
    Formula: Market Capitalization / Operating Cash Flow
    """
    return market_cap / operating_cash_flow


def peg_ratio(pe_ratio: float, eps_growth_rate: float) -> float:
    """
    PEG Ratio (Price/Earnings to Growth)
    Formula: P/E Ratio / Annual EPS Growth Rate (%)
    Note: Growth rate should be expressed as percentage (e.g., 15 for 15%)
    """
    return pe_ratio / eps_growth_rate


def earnings_to_price_ratio(eps: float, market_price_per_share: float) -> float:
    """
    Earnings-to-Price (E/P) Ratio (Earnings Yield)
    Formula: Earnings Per Share / Market Price Per Share
    """
    return eps / market_price_per_share


def earnings_to_price_ratio_alt(net_income: float, market_cap: float) -> float:
    """
    Earnings-to-Price (E/P) Ratio - Alternative
    Formula: Net Income / Market Capitalization
    """
    return net_income / market_cap


def enterprise_value(market_cap: float, total_debt: float, cash_and_equivalents: float,
                     minority_interest: float = 0, preferred_equity: float = 0) -> float:
    """
    Enterprise Value (EV)
    Formula: Market Cap + Total Debt + Minority Interest + Preferred Equity - Cash and Cash Equivalents
    """
    return market_cap + total_debt + minority_interest + preferred_equity - cash_and_equivalents


def ev_to_ebitda(enterprise_value: float, ebitda: float) -> float:
    """
    Enterprise Value-to-EBITDA (EV/EBITDA)
    Formula: Enterprise Value / EBITDA
    """
    return enterprise_value / ebitda


def ev_to_ebit(enterprise_value: float, ebit: float) -> float:
    """
    Enterprise Value-to-EBIT (EV/EBIT)
    Formula: Enterprise Value / EBIT
    """
    return enterprise_value / ebit


def ev_to_sales(enterprise_value: float, total_revenue: float) -> float:
    """
    Enterprise Value-to-Sales (EV/Sales)
    Formula: Enterprise Value / Total Revenue
    """
    return enterprise_value / total_revenue


def ev_to_free_cash_flow(enterprise_value: float, free_cash_flow: float) -> float:
    """
    Enterprise Value-to-Free Cash Flow (EV/FCF)
    Formula: Enterprise Value / Free Cash Flow
    """
    return enterprise_value / free_cash_flow


def tangible_book_value(total_equity: float, intangible_assets: float, goodwill: float) -> float:
    """
    Tangible Book Value
    Formula: Total Equity - Intangible Assets - Goodwill
    """
    return total_equity - intangible_assets - goodwill


def tangible_book_value_per_share(tangible_book_value: float, shares_outstanding: float) -> float:
    """
    Tangible Book Value Per Share
    Formula: Tangible Book Value / Shares Outstanding
    """
    return tangible_book_value / shares_outstanding


def price_to_tangible_book_value(market_price_per_share: float, tangible_bvps: float) -> float:
    """
    Price-to-Tangible Book Value
    Formula: Market Price Per Share / Tangible Book Value Per Share
    """
    return market_price_per_share / tangible_bvps


def free_cash_flow_per_share(free_cash_flow: float, shares_outstanding: float) -> float:
    """
    Free Cash Flow Per Share
    Formula: Free Cash Flow / Shares Outstanding
    """
    return free_cash_flow / shares_outstanding


def price_to_free_cash_flow(market_price_per_share: float, fcf_per_share: float) -> float:
    """
    Price-to-Free Cash Flow (P/FCF)
    Formula: Market Price Per Share / Free Cash Flow Per Share
    """
    return market_price_per_share / fcf_per_share


def price_to_free_cash_flow_alt(market_cap: float, free_cash_flow: float) -> float:
    """
    Price-to-Free Cash Flow (P/FCF) - Alternative
    Formula: Market Capitalization / Free Cash Flow
    """
    return market_cap / free_cash_flow


def ev_to_revenue(enterprise_value: float, total_revenue: float) -> float:
    """
    EV-to-Revenue
    Formula: Enterprise Value / Total Revenue
    """
    return enterprise_value / total_revenue


def ev_to_operating_income(enterprise_value: float, operating_income: float) -> float:
    """
    EV-to-Operating Income
    Formula: Enterprise Value / Operating Income
    """
    return enterprise_value / operating_income






