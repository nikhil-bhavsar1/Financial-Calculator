#!/usr/bin/env python3
"""
Update calculator.py to use normalized py_lib parameter names
"""

import re

# Read current calculator.py
with open('python/calculator.py', 'r') as f:
    content = f.read()

# Update DEFAULT_MAPPING to use normalized canonical keys
# This aligns with py_lib normalized parameters
old_mapping_keys = {
    'revenue': 'revenue',
    'cogs': 'cogs',
    'gross_profit': 'gross_profit',
    'operating_income': 'operating_income',
    'net_income': 'net_income',
    'ebitda': 'ebitda',
    'total_assets': 'total_assets',
    'total_liabilities': 'total_liabilities',
    'equity': 'equity',
    'cash': 'cash',
    'debt': 'debt',
}

new_mapping_keys = {
    'total_revenue': 'total_revenue',
    'cost_of_goods_sold': 'cost_of_goods_sold',
    'gross_profit': 'gross_profit',
    'operating_profit': 'operating_profit',
    'profit_for_the_year': 'profit_for_the_year',
    'profit_before_tax': 'profit_before_tax',
    'ebitda': 'ebitda',
    'total_assets': 'total_assets',
    'total_equity': 'total_equity',
    'total_liabilities': 'total_liabilities',
    'cash_and_equivalents': 'cash_and_equivalents',
    'total_borrowings': 'total_borrowings',
    'property_plant_equipment': 'property_plant_equipment',
    'inventories': 'inventories',
    'trade_receivables': 'trade_receivables',
    'trade_payables': 'trade_payables',
    'finance_cost': 'finance_cost',
    'tax_expense': 'tax_expense',
    'depreciation_amortization': 'depreciation_amortization',
    'capital_expenditure': 'capital_expenditure',
    'number_of_shares': 'number_of_shares',
    'market_capitalization': 'market_capitalization',
    'enterprise_value': 'enterprise_value',
    'earnings_per_share_basic': 'earnings_per_share_basic',
    'dividend_per_share': 'dividend_per_share',
    'shares_outstanding': 'number_of_shares',  # Alternative key
    'operating_expenses': 'operating_expenses',
    'total_expenses': 'total_expenses',
    'current_assets': 'total_current_assets',
    'current_liabilities': 'total_current_liabilities',
    'long_term_borrowings': 'long_term_borrowings',
    'working_capital': 'working_capital',
    'net_cash_from_operating_activities': 'net_cash_from_operating_activities',
    'free_cash_flow': 'free_cash_flow',
}

# Update formula key mappings in _derive_missing_values
old_formula_calls = [
    ("revenue'", "get('revenue')"),
    ("cogs'", "get('cogs')"),
    ("opex'", "get('opex')"),
    ("operating_income'", "get('operating_income')"),
    ("ebitda'", "get('ebitda')"),
    ("depreciation'", "get('depreciation')"),
    ("net_income'", "get('net_income')"),
    ("ebt'", "get('ebt')"),
    ("tax'", "get('tax')"),
    ("equity'", "get('equity')"),
    ("cash'", "get('cash')"),
    ("debt'", "get('debt')"),
    ("shares'", "get('shares')"),
    ("price'", "get('price')"),
    ("minority_interest'", "get('minority_interest')"),
    ("preferred_equity'", "get('preferred_equity')"),
    ("capex'", "get('capex')"),
    ("dividends'", "get('dividends')"),
    ("book_value_per_share'", "get('book_value_per_share')"),
    ("revenue_per_share'", "get('revenue_per_share')"),
    ("cash_from_operations'", "get('cash_from_operations')"),
    ("free_cash_flow'", "get('free_cash_flow')"),
    ("free_cash_flow_per_share'", "get('free_cash_flow_per_share')"),
    ("intangible_assets'", "get('intangible_assets')"),
    ("goodwill'", "get('goodwill')"),
    ("tangible_book_value'", "get('tangible_book_value')"),
    ("tangible_bvps'", "get('tangible_bvps')"),
    ("working_capital'", "get('working_capital')"),
    ("total_liabilities'", "get('total_liabilities')"),
    ("long_term_liabilities'", "get('long_term_liabilities')"),
    ("current_assets'", "get('current_assets')"),
    ("current_liabilities'", "get('current_liabilities')"),
    ("non_current_assets'", "get('non_current_assets')"),
]

new_formula_calls = [
    ("total_revenue'", "get('total_revenue')"),
    ("cost_of_goods_sold'", "get('cost_of_goods_sold')"),
    ("operating_expenses'", "get('operating_expenses')"),
    ("operating_profit'", "get('operating_profit')"),
    ("ebitda'", "get('ebitda')"),
    ("depreciation_amortization'", "get('depreciation_amortization')"),
    ("profit_for_the_year'", "get('profit_for_the_year')"),
    ("finance_cost'", "get('finance_cost')"),
    ("tax_expense'", "get('tax_expense')"),
    ("total_equity'", "get('total_equity')"),
    ("cash_and_equivalents'", "get('cash_and_equivalents')"),
    ("total_borrowings'", "get('total_borrowings')"),
    ("number_of_shares'", "get('number_of_shares')"),
    ("share_price'", "get('share_price')"),
    ("non_controlling_interest'", "get('non_controlling_interest')"),
    ("share_capital'", "get('share_capital')"),
    ("capital_expenditure'", "get('capital_expenditure')"),
    ("dividend_paid'", "get('dividend_paid')"),
    ("enterprise_value'", "get('enterprise_value')"),
    ("working_capital'", "get('working_capital')"),
    ("net_cash_from_operating_activities'", "get('net_cash_from_operating_activities')"),
    ("free_cash_flow'", "get('free_cash_flow')"),
    ("long_term_borrowings'", "get('long_term_borrowings')"),
    ("total_current_assets'", "get('total_current_assets')"),
    ("total_current_liabilities'", "get('total_current_liabilities')"),
]

# Update Formulas class to use normalized parameter names
formula_updates = [
    # Update gross_profit to use cost_of_goods_sold
    ("def gross_profit(revenue: float, cogs: float)",
     "def gross_profit(total_revenue: float, cost_of_goods_sold: float)"),

    # Update operating_income to use operating_profit
    ("def operating_profit(gross_profit: float, opex: float)",
     "def operating_income(operating_profit_param: float, operating_expenses: float)"),

    # Update ebitda to use operating_profit
    ("def ebitda(operating_profit: float, depreciation: float)",
     "def ebitda(operating_profit: float, depreciation_amortization: float)"),

    # Update net_income to use profit_for_the_year
    ("def net_income(ebt: float, tax: float)",
     "def net_income(profit_before_tax: float, tax_expense: float)"),
]

# Apply updates to content
for old, new in formula_updates:
    content = content.replace(old, new)

print("Updated formula signatures")
print(f"Original length: {len(content)}")
