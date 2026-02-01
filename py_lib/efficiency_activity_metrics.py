def asset_turnover_ratio(total_revenue: float, avg_total_assets: float) -> float:
    """
    Asset Turnover Ratio
    Formula: Net Sales / Average Total Assets
    """
    return total_revenue / avg_total_assets

def inventory_turnover_ratio(cogs: float, avg_inventory: float) -> float:
    """
    Inventory Turnover Ratio
    Formula: Cost of Goods Sold / Average Inventory
    """
    return cogs / avg_inventory

def receivables_turnover_ratio(net_credit_sales: float, avg_accounts_receivable: float) -> float:
    """
    Receivables Turnover Ratio
    Formula: Net Credit Sales / Average Accounts Receivable
    """
    return net_credit_sales / avg_accounts_receivable

def days_sales_outstanding(trade_receivables: float, total_credit_sales: float) -> float:
    """
    Days Sales Outstanding (DSO)
    Formula: (Accounts Receivable / Total Credit Sales) × 365
    """
    return trade_receivables / total_credit_sales * 365

def days_inventory_outstanding(avg_inventory: float, cogs: float) -> float:
    """
    Days Inventory Outstanding (DIO)
    Formula: (Average Inventory / COGS) × 365
    """
    return avg_inventory / cogs * 365

def days_payable_outstanding(trade_payables: float, cogs: float) -> float:
    """
    Days Payable Outstanding (DPO)
    Formula: (Accounts Payable / COGS) × 365
    """
    return trade_payables / cogs * 365

def cash_conversion_cycle(dso: float, dio: float, dpo: float) -> float:
    """
    Cash Conversion Cycle (CCC)
    Formula: DSO + DIO - DPO
    """
    return dso + dio - dpo

def payables_turnover_ratio(cogs: float, avg_accounts_payable: float) -> float:
    """
    Payables Turnover Ratio
    Formula: COGS / Average Accounts Payable
    """
    return cogs / avg_accounts_payable

def fixed_asset_turnover(total_revenue: float, net_fixed_assets: float) -> float:
    """
    Fixed Asset Turnover
    Formula: Net Sales / Net Fixed Assets
    Where: Net Fixed Assets = Gross Fixed Assets - Accumulated Depreciation
    """
    return total_revenue / net_fixed_assets

def total_asset_turnover(total_revenue: float, avg_total_assets: float) -> float:
    """
    Total Asset Turnover
    Formula: Net Sales / Average Total Assets
    """
    return total_revenue / avg_total_assets

def working_capital_turnover(total_revenue: float, avg_working_capital: float) -> float:
    """
    Working Capital Turnover
    Formula: Net Sales / Average Working Capital
    """
    return total_revenue / avg_working_capital

def capital_employed(total_assets: float, current_liabilities: float) -> float:
    """
    Capital Employed
    Formula: Total Assets - Current Liabilities
    """
    return total_assets - current_liabilities

def capital_employed_turnover(total_revenue: float, capital_employed: float) -> float:
    """
    Capital Employed Turnover
    Formula: Revenue / Capital Employed
    Where: Capital Employed = Total Assets - Current Liabilities
    """
    return total_revenue / capital_employed

def net_working_capital_turnover(total_revenue: float, net_working_capital: float) -> float:
    """
    Net Working Capital Turnover
    Formula: Revenue / Net Working Capital
    """
    return total_revenue / net_working_capital

def equity_turnover(total_revenue: float, avg_shareholders_equity: float) -> float:
    """
    Equity Turnover
    Formula: Revenue / Average Shareholders' Equity
    """
    return total_revenue / avg_shareholders_equity