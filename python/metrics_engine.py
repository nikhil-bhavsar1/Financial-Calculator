"""
Enhanced Calculator that uses py_lib formulas with normalized terminology
"""

import json
import sys
import os

# Add py_lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import normalized py_lib modules
try:
    from py_lib.profitability_metrics import *
    from py_lib.valuation_ratios import *
    from py_lib.cash_flow_metrics import *
    from py_lib.liquidity_metrics import *
    from py_lib.leverage_solvency_metrics import *
    from py_lib.efficiency_activity_metrics import *
    from py_lib.market_metrics import *
    from py_lib.growth_metrics import *
    from py_lib.dividend_metrics import *
    from py_lib.dupont_analysis import *
    from py_lib.benjamin_graham_formulas import *
    PY_LIB_AVAILABLE = True
except ImportError as e:
    print(f"[metrics_engine] Error importing py_lib: {e}", file=sys.stderr)
    PY_LIB_AVAILABLE = False

# Import terminology
try:
    from terminology_keywords import TERMINOLOGY_MAP, find_best_matching_term
except ImportError:
    TERMINOLOGY_MAP = {}
    find_best_matching_term = None

# Safe math operations
def safe_divide(numerator, denominator, default=0.0):
    if denominator is None or denominator == 0 or numerator is None:
        return default
    try:
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def safe_add(*args, default=0.0):
    if any(arg is None for arg in args):
        return default
    try:
        return sum(arg if arg is not None else 0 for arg in args)
    except TypeError:
        return default

def safe_subtract(a, b, default=0.0):
    if a is None or b is None:
        return default
    try:
        return a - b
    except TypeError:
        return default

def safe_percent(value, default=0.0):
    if value is None:
        return default
    try:
        return value * 100
    except TypeError:
        return default

def safe_float(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class MetricsEngine:
    """
    Metrics engine that uses py_lib formulas with normalized terminology.
    
    This provides:
    - Automatic matching of extracted items to canonical terms
    - Calculation of all metrics using py_lib formulas
    - Proper handling of missing values
    """
    
    def __init__(self):
        self.inputs_current = {}
        self.inputs_previous = {}
        self.results = {}
        
    def match_item_to_term(self, label: str, current_value: float, previous_value: float = None) -> str:
        """
        Match an extracted item label to canonical term key.
        
        Returns the canonical term key or None.
        """
        if find_best_matching_term:
            match = find_best_matching_term(label)
            if match:
                term_key = match.get('term_key', '')
                return term_key
        
        # Fallback: simple keyword matching
        label_lower = label.lower().strip()
        
        # Try to match against known canonical keys
        keyword_map = {
            # Income Statement
            'total_revenue': ['revenue', 'total revenue', 'net sales', 'sales', 'turnover'],
            'cost_of_goods_sold': ['cost of goods sold', 'cogs', 'cost of sales', 'materials consumed'],
            'gross_profit': ['gross profit', 'gross margin'],
            'operating_profit': ['operating profit', 'ebit', 'operating income', 'profit from operations'],
            'profit_before_tax': ['profit before tax', 'pbt'],
            'profit_for_the_year': ['net profit', 'profit after tax', 'net income', 'pat', 'profit for the year'],
            'ebitda': ['ebitda', 'operating profit before depreciation'],
            'operating_expenses': ['operating expenses', 'other expenses'],
            'finance_cost': ['finance cost', 'interest expense', 'interest', 'finance charges'],
            'tax_expense': ['tax expense', 'income tax', 'current tax', 'deferred tax'],
            
            # Balance Sheet
            'total_assets': ['total assets'],
            'total_current_assets': ['current assets'],
            'property_plant_equipment': ['property plant and equipment', 'ppe', 'fixed assets', 'tangible assets'],
            'capital_work_in_progress': ['capital work-in-progress', 'cwip', 'capital work in progress'],
            'inventories': ['inventories', 'inventory', 'stock-in-trade'],
            'trade_receivables': ['trade receivables', 'accounts receivable', 'sundry debtors', 'bill receivables'],
            'cash_and_equivalents': ['cash and cash equivalents', 'cash', 'cash equivalents', 'bank balances'],
            'total_liabilities': ['total liabilities'],
            'total_current_liabilities': ['current liabilities'],
            'trade_payables': ['trade payables', 'accounts payable', 'sundry creditors', 'bill payables'],
            'total_equity': ['total equity', 'shareholders equity', 'net worth'],
            'total_borrowings': ['total debt', 'borrowings', 'total borrowings', 'loans'],
            'long_term_borrowings': ['long term debt', 'non-current borrowings'],
            
            # Market
            'number_of_shares': ['shares outstanding', 'number of shares', 'shares', 'equity shares'],
            'market_capitalization': ['market cap', 'market capitalization'],
        }
        
        for term_key, keywords in keyword_map.items():
            for kw in keywords:
                if kw in label_lower or label_lower in kw:
                    return term_key
        
        return None
    
    def match_cell_to_term(self, cell) -> str:
        """
        Match a FinancialCell to a term key using enhanced context.
        """
        # 1. Try matching with full context (Section + Row Header)
        # e.g. "Non-Current Assets" -> "Property Plant Equipment"
        
        # Combine section and header for richer search if needed
        full_text = f"{cell.section} {cell.row_header}"
        
        # Try native matcher first
        if find_best_matching_term:
            match = find_best_matching_term(cell.row_header)
            if match:
                return match.get('term_key', '')
        
        # Context-aware overrides
        header_lower = cell.row_header.lower()
        section_lower = cell.section.lower()
        
        # Example: "Others" in "Current Assets" -> "other_current_assets"
        if "other" in header_lower:
            if "current assets" in section_lower:
                 return "other_current_assets"
            if "current liabilities" in section_lower:
                 return "other_current_liabilities"
                 
        return self.match_item_to_term(cell.row_header, cell.value)

    def load_from_graph(self, graph):
        """
        Load data from a FinancialTableGraph.
        """
        # Lazy import types to avoid circular dependency
        from table_graph_builder import FinancialTableGraph, FinancialCell
        
        if not isinstance(graph, FinancialTableGraph):
            return

        for cell in graph.cells:
            if not cell.value: continue
            
            # Determine Term Key
            term_key = self.match_cell_to_term(cell)
            if not term_key: continue
            
            # Determine Year (Current vs Previous)
            # Use period_date or period_label from cell
            # The engine currently expects "current" vs "previous" implicitly
            # We need a way to map dates to "Current/Previous" relative to the document
            
            # For now, rely on column_type if set by builder
            is_current = False
            is_previous = False
            
            # Check explicit column type first
            col_meta = next((c for c in graph.columns if c.index == cell.col_idx), None)
            if col_meta:
                if col_meta.column_type == 'amount_current':
                    is_current = True
                elif col_meta.column_type == 'amount_previous':
                    is_previous = True
            
            # Apply Sign
            final_value = cell.value * cell.sign
            
            if is_current:
                self.inputs_current[term_key] = final_value
            elif is_previous:
                self.inputs_previous[term_key] = final_value
    
    def add_item(self, label: str, current_value: float, previous_value: float = None):
        """Add an extracted item with current and previous year values."""
        term_key = self.match_item_to_term(label, current_value, previous_value)
        
        if term_key:
            self.inputs_current[term_key] = current_value
            if previous_value is not None:
                self.inputs_previous[term_key] = previous_value
    
    def derive_missing_values(self):
        """Derive missing values from available data."""
        # Gross Profit
        if 'gross_profit' not in self.inputs_current:
            if 'total_revenue' in self.inputs_current and 'cost_of_goods_sold' in self.inputs_current:
                self.inputs_current['gross_profit'] = gross_profit(
                    total_revenue=self.inputs_current.get('total_revenue', 0),
                    cost_of_goods_sold=self.inputs_current.get('cost_of_goods_sold', 0)
                )
        
        # Operating Profit
        if 'operating_profit' not in self.inputs_current:
            if 'gross_profit' in self.inputs_current and 'operating_expenses' in self.inputs_current:
                self.inputs_current['operating_profit'] = operating_income(
                    gross_profit=self.inputs_current.get('gross_profit', 0),
                    operating_expenses=self.inputs_current.get('operating_expenses', 0)
                )
        
        # EBITDA
        if 'ebitda' not in self.inputs_current:
            if 'operating_profit' in self.inputs_current:
                self.inputs_current['ebitda'] = ebitda(
                    operating_profit=self.inputs_current.get('operating_profit', 0),
                    depreciation=0,  # Will be set separately
                    amortization=0
                )
        
        # Profit Before Tax
        if 'profit_before_tax' not in self.inputs_current:
            if 'operating_profit' in self.inputs_current and 'finance_cost' in self.inputs_current:
                self.inputs_current['profit_before_tax'] = operating_income(
                    gross_profit=self.inputs_current.get('gross_profit', 0),
                    operating_expenses=self.inputs_current.get('operating_expenses', 0)
                ) - safe_float(self.inputs_current.get('finance_cost', 0))
        
        # Profit for the Year
        if 'profit_for_the_year' not in self.inputs_current:
            if 'profit_before_tax' in self.inputs_current and 'tax_expense' in self.inputs_current:
                self.inputs_current['profit_for_the_year'] = net_income(
                    profit_before_tax=self.inputs_current.get('profit_before_tax', 0),
                    tax_expense=self.inputs_current.get('tax_expense', 0)
                )
        
        # Working Capital
        if 'working_capital' not in self.inputs_current:
            if 'total_current_assets' in self.inputs_current and 'total_current_liabilities' in self.inputs_current:
                self.inputs_current['working_capital'] = working_capital(
                    total_current_assets=self.inputs_current.get('total_current_assets', 0),
                    total_current_liabilities=self.inputs_current.get('total_current_liabilities', 0)
                )
        
        # Market Cap
        if 'market_capitalization' not in self.inputs_current:
            if 'number_of_shares' in self.inputs_current:
                # Assume price if not available - would need from market data
                pass
        
        # Enterprise Value
        if 'enterprise_value' not in self.inputs_current:
            if 'market_capitalization' in self.inputs_current:
                ev = enterprise_value(
                    market_cap=self.inputs_current.get('market_capitalization', 0),
                    total_debt=self.inputs_current.get('total_borrowings', 0),
                    minority_interest=0,
                    preferred_equity=0,
                    cash_and_cash_equivalents=self.inputs_current.get('cash_and_equivalents', 0)
                )
                self.inputs_current['enterprise_value'] = ev
        
        # Book Value Per Share
        if 'book_value_per_share' not in self.inputs_current:
            if 'total_equity' in self.inputs_current and 'number_of_shares' in self.inputs_current:
                self.inputs_current['book_value_per_share'] = book_value_per_share(
                    total_equity=self.inputs_current.get('total_equity', 0),
                    preferred_equity=0,
                    common_shares_outstanding=self.inputs_current.get('number_of_shares', 0)
                )
        
        # Revenue Per Share
        if 'revenue_per_share' not in self.inputs_current:
            if 'total_revenue' in self.inputs_current and 'number_of_shares' in self.inputs_current:
                self.inputs_current['revenue_per_share'] = revenue_per_share(
                    total_revenue=self.inputs_current.get('total_revenue', 0),
                    number_of_shares=self.inputs_current.get('number_of_shares', 0)
                )
        
        # Free Cash Flow
        if 'free_cash_flow' not in self.inputs_current:
            if 'net_cash_from_operating_activities' in self.inputs_current:
                fcf = free_cash_flow(
                    operating_cash_flow=self.inputs_current.get('net_cash_from_operating_activities', 0),
                    capital_expenditures=0  # Will be set separately
                )
                self.inputs_current['free_cash_flow'] = fcf
    
    def calculate_all_metrics(self):
        """Calculate all metrics using py_lib formulas."""
        categories = {
            'Valuation Ratios': self._calculate_valuation(),
            'Profitability Metrics': self._calculate_profitability(),
            'Cash Flow Metrics': self._calculate_cash_flow(),
            'Liquidity Metrics': self._calculate_liquidity(),
            'Leverage/Solvency Metrics': self._calculate_leverage(),
            'Efficiency/Activity Metrics': self._calculate_efficiency(),
            'Growth Metrics': self._calculate_growth(),
            'Market Metrics': self._calculate_market(),
            'Dividend Metrics': self._calculate_dividend(),
            'DuPont Analysis': self._calculate_dupont(),
            'Benjamin Graham Formulas': self._calculate_graham(),
        }
        return categories
    
    def _get_value(self, key, year='current'):
        """Get value for a key with fallback."""
        store = self.inputs_current if year == 'current' else self.inputs_previous
        return store.get(key, 0.0)
    
    def _calculate_valuation(self):
        """Calculate valuation ratios."""
        metrics = []
        
        # P/E Ratio
        try:
            eps = self._get_value('earnings_per_share_basic')
            price = self._get_value('share_price')  # Would need market data
            if eps and eps != 0:
                pe = price_to_earnings_ratio(
                    market_price_per_share=price,
                    earnings_per_share_basic=eps
                )
                metrics.append(self._format_metric('P/E Ratio', pe))
        except:
            pass
        
        # P/B Ratio
        try:
            bvps = self._get_value('book_value_per_share')
            price = self._get_value('share_price')
            if bvps and bvps != 0:
                pb = price_to_book_ratio(
                    current_stock_price=price,
                    book_value_per_share=bvps
                )
                metrics.append(self._format_metric('P/B Ratio', pb))
        except:
            pass
        
        # EV/EBITDA
        try:
            ev = self._get_value('enterprise_value')
            ebitda = self._get_value('ebitda')
            if ebitda and ebitda != 0:
                ev_ebitda = ev_to_ebitda(
                    enterprise_value=ev,
                    ebitda=ebitda
                )
                metrics.append(self._format_metric('EV/EBITDA', ev_ebitda))
        except:
            pass
        
        return metrics
    
    def _calculate_profitability(self):
        """Calculate profitability metrics."""
        metrics = []
        
        # Gross Profit Margin
        try:
            gp = self._get_value('gross_profit')
            rev = self._get_value('total_revenue')
            if rev and rev != 0:
                gpm = gross_profit_margin(
                    gross_profit=gp,
                    total_revenue=rev
                )
                metrics.append(self._format_metric('Gross Margin (%)', gpm))
        except:
            pass
        
        # Operating Margin
        try:
            op = self._get_value('operating_profit')
            rev = self._get_value('total_revenue')
            if rev and rev != 0:
                om = operating_margin(
                    operating_profit=op,
                    total_revenue=rev
                )
                metrics.append(self._format_metric('Operating Margin (%)', om))
        except:
            pass
        
        # Net Profit Margin
        try:
            ni = self._get_value('profit_for_the_year')
            rev = self._get_value('total_revenue')
            if rev and rev != 0:
                npm = net_profit_margin(
                    net_income=ni,
                    total_revenue=rev
                )
                metrics.append(self._format_metric('Net Profit Margin (%)', npm))
        except:
            pass
        
        # EBITDA Margin
        try:
            ebitda = self._get_value('ebitda')
            rev = self._get_value('total_revenue')
            if rev and rev != 0:
                em = ebitda_margin(
                    ebitda=ebitda,
                    total_revenue=rev
                )
                metrics.append(self._format_metric('EBITDA Margin (%)', em))
        except:
            pass
        
        # ROE
        try:
            ni = self._get_value('profit_for_the_year')
            eq = self._get_value('total_equity')
            if eq and eq != 0:
                roe = return_on_equity(
                    net_income=ni,
                    avg_shareholders_equity=eq
                )
                metrics.append(self._format_metric('ROE (%)', roe))
        except:
            pass
        
        # ROA
        try:
            ni = self._get_value('profit_for_the_year')
            ta = self._get_value('total_assets')
            if ta and ta != 0:
                roa = return_on_assets(
                    net_income=ni,
                    avg_total_assets=ta
                )
                metrics.append(self._format_metric('ROA (%)', roa))
        except:
            pass
        
        return metrics
    
    def _calculate_cash_flow(self):
        """Calculate cash flow metrics."""
        metrics = []
        
        # Add FCF
        fcf = self._get_value('free_cash_flow')
        if fcf:
            metrics.append(self._format_metric('Free Cash Flow', fcf))
        
        return metrics
    
    def _calculate_liquidity(self):
        """Calculate liquidity metrics."""
        metrics = []
        
        # Current Ratio
        try:
            ca = self._get_value('total_current_assets')
            cl = self._get_value('total_current_liabilities')
            if cl and cl != 0:
                cr = current_ratio(
                    total_current_assets=ca,
                    total_current_liabilities=cl
                )
                metrics.append(self._format_metric('Current Ratio', cr))
        except:
            pass
        
        # Quick Ratio
        try:
            ca = self._get_value('total_current_assets')
            inv = self._get_value('inventories')
            cl = self._get_value('total_current_liabilities')
            if cl and cl != 0:
                qr = quick_ratio(
                    total_current_assets=ca,
                    inventories=inv,
                    total_current_liabilities=cl
                )
                metrics.append(self._format_metric('Quick Ratio', qr))
        except:
            pass
        
        return metrics
    
    def _calculate_leverage(self):
        """Calculate leverage metrics."""
        metrics = []
        
        # Debt to Equity
        try:
            debt = self._get_value('total_borrowings')
            equity = self._get_value('total_equity')
            if equity and equity != 0:
                dte = debt_to_equity_ratio(
                    total_debt=debt,
                    total_shareholders_equity=equity
                )
                metrics.append(self._format_metric('Debt to Equity', dte))
        except:
            pass
        
        return metrics
    
    def _calculate_efficiency(self):
        """Calculate efficiency metrics."""
        metrics = []
        
        # Asset Turnover
        try:
            rev = self._get_value('total_revenue')
            ta = self._get_value('total_assets')
            if ta and ta != 0:
                at = asset_turnover_ratio(
                    net_sales=rev,
                    avg_total_assets=ta
                )
                metrics.append(self._format_metric('Asset Turnover', at))
        except:
            pass
        
        return metrics
    
    def _calculate_growth(self):
        """Calculate growth metrics."""
        metrics = []
        
        # Revenue Growth
        curr_rev = self._get_value('total_revenue')
        prev_rev = self._get_value('total_revenue', 'previous')
        if prev_rev and prev_rev != 0:
            rg = ((curr_rev - prev_rev) / abs(prev_rev)) * 100
            metrics.append(self._format_metric('Revenue Growth (%)', rg))
        
        return metrics
    
    def _calculate_market(self):
        """Calculate market metrics."""
        metrics = []
        
        # Market Cap
        mc = self._get_value('market_capitalization')
        if mc:
            metrics.append(self._format_metric('Market Cap', mc))
        
        # Enterprise Value
        ev = self._get_value('enterprise_value')
        if ev:
            metrics.append(self._format_metric('Enterprise Value', ev))
        
        return metrics
    
    def _calculate_dividend(self):
        """Calculate dividend metrics."""
        metrics = []
        
        # Dividend Payout Ratio
        try:
            div = self._get_value('dividend_paid') or self._get_value('dividend_per_share')
            ni = self._get_value('profit_for_the_year')
            eps = self._get_value('earnings_per_share_basic')
            if eps and eps != 0:
                dpr = dividend_payout_ratio(
                    dividends_per_share=div or 0,
                    earnings_per_share=eps
                )
                metrics.append(self._format_metric('Dividend Payout Ratio (%)', dpr))
        except:
            pass
        
        return metrics
    
    def _calculate_dupont(self):
        """Calculate DuPont analysis."""
        metrics = []
        
        try:
            ni = self._get_value('profit_for_the_year')
            rev = self._get_value('total_revenue')
            ta = self._get_value('total_assets')
            eq = self._get_value('total_equity')
            
            if rev and rev != 0 and ta and ta != 0 and eq and eq != 0:
                net_margin = safe_divide(ni, rev)
                asset_turnover = safe_divide(rev, ta)
                equity_mult = safe_divide(ta, eq)
                
                dupont_roe = net_margin * asset_turnover * equity_mult * 100
                
                metrics.append(self._format_metric('Net Margin (Component)', net_margin))
                metrics.append(self._format_metric('Asset Turnover (Component)', asset_turnover))
                metrics.append(self._format_metric('Equity Multiplier (Component)', equity_mult))
                metrics.append(self._format_metric('DuPont ROE (%)', dupont_roe))
        except:
            pass
        
        return metrics
    
    def _calculate_graham(self):
        """Calculate Benjamin Graham formulas."""
        metrics = []
        
        try:
            eps = self._get_value('earnings_per_share_basic')
            bvps = self._get_value('book_value_per_share')
            
            if eps and bvps and eps > 0 and bvps > 0:
                gn = graham_number(
                    earnings_per_share_basic=eps,
                    book_value_per_share=bvps
                )
                metrics.append(self._format_metric('Graham Number', gn))
        except:
            pass
        
        return metrics
    
    def _format_metric(self, label, value):
        """Format a metric for output."""
        return {
            'label': label,
            'currentYear': round(value, 4) if value is not None else 0,
            'previousYear': 0,  # Would need previous values
            'variation': 0,
            'variationPercent': 0,
        }


def calculate_metrics_from_items(items_json: str):
    """
    Main entry point for calculating metrics from parsed items.
    
    Args:
        items_json: JSON string of extracted financial items
        
    Returns:
        JSON string of calculated metrics organized by category
    """
    try:
        items = json.loads(items_json)
    except json.JSONDecodeError as e:
        return json.dumps({'error': f'Invalid JSON: {e}'})
    
    engine = MetricsEngine()
    
    # Process items
    for item in items:
        label = item.get('label', '')
        current = item.get('currentYear')
        previous = item.get('previousYear')
        
        if current is not None:
            engine.add_item(label, current, previous)
    
    # Derive missing values
    engine.derive_missing_values()
    
    # Calculate all metrics
    results = engine.calculate_all_metrics()
    
    # Add passthrough items
    passthrough_items = [
        {'label': 'Gross Profit', 'key': 'gross_profit'},
        {'label': 'Operating Income', 'key': 'operating_profit'},
        {'label': 'EBITDA', 'key': 'ebitda'},
        {'label': 'Net Income', 'key': 'profit_for_the_year'},
        {'label': 'Total Assets', 'key': 'total_assets'},
        {'label': 'Total Equity', 'key': 'total_equity'},
        {'label': 'Working Capital', 'key': 'working_capital'},
        {'label': 'Market Cap', 'key': 'market_capitalization'},
        {'label': 'Enterprise Value', 'key': 'enterprise_value'},
    ]
    
    for item in passthrough_items:
        key = item['key']
        value = engine._get_value(key)
        if value != 0:
            results.get('Appendix - Financial Statement Formulas', []).append(
                engine._format_metric(item['label'], value)
            )
    
    return json.dumps(results, indent=None)


if __name__ == '__main__':
    # Test with sample data
    sample_items = json.dumps([
        {"label": "Total Revenue", "currentYear": 100000, "previousYear": 90000},
        {"label": "Cost of Goods Sold", "currentYear": 60000, "previousYear": 55000},
        {"label": "Gross Profit", "currentYear": 40000, "previousYear": 35000},
        {"label": "Operating Income", "currentYear": 25000, "previousYear": 22000},
        {"label": "Profit for the Year", "currentYear": 15000, "previousYear": 12000},
        {"label": "Total Assets", "currentYear": 200000, "previousYear": 180000},
        {"label": "Total Equity", "currentYear": 120000, "previousYear": 110000},
        {"label": "Total Current Assets", "currentYear": 80000, "previousYear": 70000},
        {"label": "Total Current Liabilities", "currentYear": 40000, "previousYear": 35000},
        {"label": "Inventories", "currentYear": 20000, "previousYear": 18000},
        {"label": "Total Borrowings", "currentYear": 40000, "previousYear": 35000},
        {"label": "Cash and Cash Equivalents", "currentYear": 15000, "previousYear": 12000},
    ])
    
    result = calculate_metrics_from_items(sample_items)
    parsed = json.loads(result)
    
    print(json.dumps(parsed, indent=2))
