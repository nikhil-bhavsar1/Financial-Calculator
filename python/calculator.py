"""
Comprehensive Financial Metrics Calculator
Robust implementation with extensive error handling for financial analysis.

This module calculates financial ratios and metrics from parsed financial statement data.
Designed to work with the FinancialParser output from parsers.py.
"""

import json
import math
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

class MetricCategory(Enum):
    """Categories for organizing calculated metrics."""
    VALUATION = "01 Valuation Ratios"
    PROFITABILITY = "02 Profitability Metrics"
    CASH_FLOW = "03 Cash Flow Metrics"
    LIQUIDITY = "04 Liquidity Metrics"
    LEVERAGE = "05 Leverage/Solvency Metrics"
    EFFICIENCY = "06 Efficiency/Activity Metrics"
    GROWTH = "07 Growth Metrics"
    MARKET = "08 Market Metrics"
    DIVIDEND = "09 Dividend Metrics"
    DUPONT = "10 DuPont Analysis Components"
    STATISTICAL = "11 Statistical Metrics"
    DCF = "12 Complete DCF Valuation Framework"
    OTHER = "13 Other Key Metrics"
    DAMODARAN = "14 Aswath Damodaran Valuation Formulas"
    GRAHAM = "15 Benjamin Graham Formulas"
    MODERN_VALUE = "16 Modern Value Investing Additions"
    APPENDIX = "17 Appendix - Financial Statement Formulas"


# Default keyword mapping for matching parsed items to financial concepts
# Default keyword mapping - will be enhanced by terminology_keywords if available
DEFAULT_MAPPING: Dict[str, List[str]] = {
    # Fallback mappings for core terms (in case terminology_keywords is missing)
    'revenue': ['revenue', 'total revenue', 'revenue from operations', 'sales'],
    'cogs': ['cost of goods sold', 'cost of sales', 'cogs'],
    'gross_profit': ['gross profit', 'gross margin'],
    'operating_income': ['operating profit', 'ebit', 'profit from operations'],
    'net_income': ['net profit', 'profit after tax', 'net income', 'pat'],
    'ebitda': ['ebitda', 'operating profit before depreciation'],
    'total_assets': ['total assets'],
    'total_liabilities': ['total liabilities'],
    'equity': ['total equity', 'shareholders equity', 'net worth'],
    'cash': ['cash and cash equivalents', 'cash'],
    'debt': ['total debt', 'borrowings'],
}

# Try to load unified terminology map
try:
    # Add root directory to path to find terminology_keywords.py
    # This assumes calculator.py is in python/ subdirectory and terminology_keywords.py is in root
    root_path = str(Path(__file__).parent.parent)
    if root_path not in sys.path:
        sys.path.append(root_path)

    from terminology_keywords import TERMINOLOGY_MAP
    
    # Overwrite/Extend DEFAULT_MAPPING with unified terms
    for key, data in TERMINOLOGY_MAP.items():
        if 'keywords' in data:
            # If the key exists, extend it (preferring new keywords)
            # If not, create it
            keywords = data['keywords']
            if key in DEFAULT_MAPPING:
                # Merge unique keywords
                existing = set(DEFAULT_MAPPING[key])
                for k in keywords:
                    existing.add(k)
                DEFAULT_MAPPING[key] = list(existing)
            else:
                DEFAULT_MAPPING[key] = keywords
    
    logger.info(f"Loaded {len(DEFAULT_MAPPING)} terms from terminology database")
    
except ImportError:
    logger.warning("Could not load terminology_keywords. Using fallback mapping.")
except Exception as e:
    logger.warning(f"Error loading terminology mappings: {e}")


def update_mapping_configuration(mappings: List[Dict[str, Any]]) -> None:
    """
    Update global mapping configuration from frontend TermMapping objects.
    
    Args:
        mappings: List of dicts matching TermMapping interface:
                 {key, label, keywords_indas, keywords_gaap, keywords_ifrs, ...}
    """
    global DEFAULT_MAPPING
    
    # We don't clear existing keys that aren't in the update to preserve defaults,
    # but we will overwrite keywords for keys that ARE provided.
    
    for item in mappings:
        key = item.get('key')
        if not key:
            continue
            
        # Combine all keyword lists
        keywords = set()
        
        # Add keywords from all standards
        for field in ['keywords_indas', 'keywords_gaap', 'keywords_ifrs']:
            k_list = item.get(field, [])
            if isinstance(k_list, list):
                for k in k_list:
                    if k and isinstance(k, str):
                        keywords.add(k.lower().strip())
        
        # Also add the label itself as a keyword
        label = item.get('label')
        if label:
            keywords.add(label.lower().strip())
            
        if keywords:
            DEFAULT_MAPPING[key] = list(keywords)
            logger.info(f"Updated mapping for '{key}': {len(keywords)} keywords")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MetricResult:
    """Result of a metric calculation."""
    id: str
    label: str
    current_year: float
    previous_year: float
    variation: float
    variation_percent: float
    source_page: str = "Calculated"
    is_auto_calc: bool = True
    calculation_error: Optional[str] = None
    formula: Optional[str] = None
    inputs_used: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "label": self.label,
            "currentYear": self.current_year,
            "previousYear": self.previous_year,
            "variation": self.variation,
            "variationPercent": self.variation_percent,
            "sourcePage": self.source_page,
            "isAutoCalc": self.is_auto_calc
        }
        if self.calculation_error:
            result["calculationError"] = self.calculation_error
        if self.formula:
            result["formula"] = self.formula
        if self.inputs_used:
            result["inputsUsed"] = self.inputs_used
        return result


@dataclass
class InputStore:
    """Store for extracted financial inputs with safe access."""
    current: Dict[str, float] = field(default_factory=dict)
    previous: Dict[str, float] = field(default_factory=dict)
    
    def get(self, key: str, year: str = 'current', default: Optional[float] = None) -> Optional[float]:
        """Safely get a value from the store."""
        store = self.current if year == 'current' else self.previous
        return store.get(key, default)
    
    def set(self, key: str, value: float, year: str = 'current') -> None:
        """Set a value in the store."""
        store = self.current if year == 'current' else self.previous
        store[key] = value
    
    def has(self, key: str, year: str = 'current') -> bool:
        """Check if a key exists and is not None."""
        store = self.current if year == 'current' else self.previous
        return key in store and store[key] is not None
    
    def get_both(self, key: str) -> Tuple[Optional[float], Optional[float]]:
        """Get both current and previous year values."""
        return self.get(key, 'current'), self.get(key, 'previous')
    
    def has_all(self, keys: List[str], year: str = 'current') -> bool:
        """Check if all keys exist."""
        return all(self.has(key, year) for key in keys)


# =============================================================================
# SAFE MATH OPERATIONS
# =============================================================================

def safe_divide(numerator: Optional[float], denominator: Optional[float], 
                default: float = 0.0) -> float:
    """Safely divide two numbers, handling None and zero."""
    if numerator is None or denominator is None:
        return default
    if denominator == 0:
        return default
    try:
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def safe_multiply(*args: Optional[float], default: float = 0.0) -> float:
    """Safely multiply numbers, handling None values."""
    if any(arg is None for arg in args):
        return default
    try:
        result = 1.0
        for arg in args:
            result *= arg
        return result
    except TypeError:
        return default


def safe_add(*args: Optional[float], default: float = 0.0) -> float:
    """Safely add numbers, treating None as 0."""
    try:
        return sum(arg if arg is not None else 0 for arg in args)
    except TypeError:
        return default


def safe_subtract(a: Optional[float], b: Optional[float], default: float = 0.0) -> float:
    """Safely subtract two numbers."""
    if a is None or b is None:
        return default
    try:
        return a - b
    except TypeError:
        return default


def safe_sqrt(value: Optional[float], default: float = 0.0) -> float:
    """Safely compute square root."""
    if value is None or value < 0:
        return default
    try:
        return math.sqrt(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_percent(value: Optional[float], default: float = 0.0) -> float:
    """Convert ratio to percentage safely."""
    if value is None:
        return default
    try:
        return value * 100
    except TypeError:
        return default


# =============================================================================
# FORMULA IMPLEMENTATIONS (Robust versions of py_lib functions)
# =============================================================================

class Formulas:
    """Collection of financial formula implementations with error handling."""
    
    # -------------------------------------------------------------------------
    # Valuation Ratios
    # -------------------------------------------------------------------------
    
    @staticmethod
    def price_to_earnings(price: float, eps: float) -> float:
        """P/E Ratio = Price / EPS"""
        return safe_divide(price, eps)

    # ... (other unmodified methods) ...

    @staticmethod
    def graham_number(eps: float, bvps: float) -> float:
        """Graham Number = √(22.5 × EPS × BVPS)"""
        if eps is None or bvps is None or eps < 0 or bvps < 0:
            return 0.0
        return safe_sqrt(22.5 * eps * bvps)
    
    @staticmethod
    def graham_intrinsic_value(eps: float, growth_rate: float, 
                                aaa_yield: float = 4.4) -> float:
        """Graham Intrinsic Value = EPS × (8.5 + 2g) × 4.4 / AAA_yield"""
        if eps is None or growth_rate is None:
            return 0.0
        base_pe = 8.5 + (2 * growth_rate)
        return safe_divide(eps * base_pe * 4.4, aaa_yield)
    
    # -------------------------------------------------------------------------
    # Modern Value Investing
    # -------------------------------------------------------------------------
    
    @staticmethod
    def greenblatt_earnings_yield(ebit: float, ev: float) -> float:
        """Greenblatt Earnings Yield = EBIT / EV × 100"""
        return safe_percent(safe_divide(ebit, ev))
    
    @staticmethod
    def greenblatt_roc(ebit: float, working_capital: float, 
                       fixed_assets: float) -> float:
        """Greenblatt ROC = EBIT / (Working Capital + Net Fixed Assets)"""
        return safe_percent(safe_divide(ebit, safe_add(working_capital, fixed_assets)))
    
    # -------------------------------------------------------------------------
    # Appendix - Basic Financial Statement Formulas
    # -------------------------------------------------------------------------
    
    @staticmethod
    def gross_profit(revenue: float, cogs: float) -> float:
        """Gross Profit = Revenue - COGS"""
        return safe_float(revenue) - safe_float(cogs)
    
    @staticmethod
    def operating_income(gross_profit: float, opex: float) -> float:
        """Operating Income = Gross Profit - Operating Expenses"""
        return safe_float(gross_profit) - safe_float(opex)
    
    @staticmethod
    def ebitda_calc(operating_income: float, depreciation: float) -> float:
        """EBITDA = Operating Income + Depreciation & Amortization"""
        return safe_add(operating_income, depreciation)
    
    @staticmethod
    def net_income_calc(ebt: float, tax: float) -> float:
        """Net Income = EBT - Tax Expense"""
        return safe_float(ebt) - safe_float(tax)
    
    @staticmethod
    def shareholders_equity(total_assets: float, total_liabilities: float) -> float:
        """Equity = Total Assets - Total Liabilities"""
        return safe_float(total_assets) - safe_float(total_liabilities)
    
    @staticmethod
    def net_change_in_cash(operating_cf: float, investing_cf: float, 
                           financing_cf: float) -> float:
        """Net Change in Cash = Operating CF + Investing CF + Financing CF"""
        return safe_add(operating_cf, investing_cf, financing_cf)
    
    @staticmethod
    def ending_retained_earnings(beginning_re: float, net_income: float, 
                                  dividends: float) -> float:
        """Ending RE = Beginning RE + Net Income - Dividends"""
        return safe_add(beginning_re, net_income) - safe_float(dividends)


# =============================================================================
# MAIN CALCULATOR CLASS
# =============================================================================

class MetricsCalculator:
    """
    Comprehensive financial metrics calculator.
    
    Features:
    - Robust error handling for all calculations
    - Automatic derivation of missing values
    - Support for custom keyword mappings
    - Detailed calculation metadata
    """
    
    def __init__(self, custom_mapping: Optional[Dict[str, List[str]]] = None):
        """Initialize calculator with optional custom mapping."""
        self.mapping = DEFAULT_MAPPING.copy()
        if custom_mapping:
            self._merge_mapping(custom_mapping)
        self.inputs = InputStore()
        self.results: Dict[str, List[MetricResult]] = {}
        self._errors: List[str] = []
    
    def _merge_mapping(self, custom: Union[Dict, List]) -> None:
        """Merge custom mapping into default mapping."""
        try:
            if isinstance(custom, list):
                for entry in custom:
                    if isinstance(entry, dict) and 'key' in entry and 'keywords' in entry:
                        self.mapping[entry['key']] = entry['keywords']
            elif isinstance(custom, dict):
                self.mapping.update(custom)
        except Exception as e:
            logger.warning(f"Error merging custom mapping: {e}")
    
    def calculate(self, items_json: str, 
                  custom_mapping_json: Optional[str] = None) -> str:
        """
        Main entry point for calculating metrics.
        
        Args:
            items_json: JSON string of parsed financial items
            custom_mapping_json: Optional JSON string of custom keyword mapping
            
        Returns:
            JSON string of calculated metrics organized by category
        """
        # Reset state
        self.inputs = InputStore()
        self.results = {}
        self._errors = []
        
        # Parse inputs
        try:
            items = self._safe_json_parse(items_json, [])
        except Exception as e:
            logger.error(f"Failed to parse items JSON: {e}")
            return json.dumps([{"category": "Error", "items": [], 
                               "error": f"Invalid items JSON: {e}"}])
        
        # Merge custom mapping if provided
        if custom_mapping_json:
            try:
                custom = self._safe_json_parse(custom_mapping_json, None)
                if custom:
                    self._merge_mapping(custom)
            except Exception as e:
                logger.warning(f"Failed to parse custom mapping: {e}")
        
        # Extract inputs from items
        self._extract_inputs(items)
        
        # Derive missing values
        self._derive_missing_values()
        
        # Calculate all metric categories
        self._calculate_all_categories()
        
        # Format output
        return self._format_output()
    
    def _safe_json_parse(self, json_str: str, default: Any) -> Any:
        """Safely parse JSON string."""
        if not json_str:
            return default
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"JSON parse error: {e}")
            return default
    
    def _extract_inputs(self, items: List[Dict]) -> None:
        """Extract and map financial values from parsed items."""
        if not items or not isinstance(items, list):
            return
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            label = str(item.get('label', '')).lower().strip()
            if not label:
                continue
            
            # Find best matching key
            best_key = None
            best_score = 0
            
            for key, keywords in self.mapping.items():
                for kw in keywords:
                    kw_lower = kw.lower()
                    # Score based on match quality
                    if kw_lower == label:
                        score = 100  # Exact match
                    elif kw_lower in label:
                        score = len(kw_lower)  # Longer match = better
                    elif label in kw_lower:
                        score = len(label) * 0.5
                    else:
                        continue
                    
                    if score > best_score:
                        best_score = score
                        best_key = key
            
            if best_key:
                curr_val = safe_float(item.get('currentYear'))
                prev_val = safe_float(item.get('previousYear'))
                
                # Only set if we got valid values
                if curr_val != 0 or prev_val != 0:
                    self.inputs.set(best_key, curr_val, 'current')
                    self.inputs.set(best_key, prev_val, 'previous')
    
    def _derive_missing_values(self) -> None:
        """Derive missing values from available data."""
        for year in ['current', 'previous']:
            self._derive_for_year(year)
    
    def _derive_for_year(self, year: str) -> None:
        """Derive missing values for a specific year."""
        get = lambda k: self.inputs.get(k, year)
        has = lambda k: self.inputs.has(k, year)
        set_val = lambda k, v: self.inputs.set(k, v, year)
        
        # Gross Profit
        if not has('gross_profit') and has('revenue') and has('cogs'):
            set_val('gross_profit', Formulas.gross_profit(get('revenue'), get('cogs')))
        
        # Operating Income
        if not has('operating_income'):
            if has('gross_profit') and has('opex'):
                set_val('operating_income', Formulas.operating_income(get('gross_profit'), get('opex')))
            elif has('ebitda') and has('depreciation'):
                set_val('operating_income', safe_float(get('ebitda')) - safe_float(get('depreciation')))
        
        # EBITDA
        if not has('ebitda') and has('operating_income') and has('depreciation'):
            set_val('ebitda', Formulas.ebitda_calc(get('operating_income'), get('depreciation')))
        
        # Defaults for missing balance sheet items
        for key in ['intangible_assets', 'goodwill', 'minority_interest', 
                    'preferred_equity', 'debt', 'capex', 'dividends']:
            if not has(key):
                set_val(key, 0)
        
        # Cash default
        if not has('cash'):
            set_val('cash', 0)
        
        # EPS
        if not has('eps') and has('net_income') and has('shares'):
            shares = get('shares')
            if shares and shares > 0:
                set_val('eps', safe_divide(get('net_income'), shares))
        
        # Market Cap
        if not has('market_cap') and has('price') and has('shares'):
            set_val('market_cap', Formulas.market_capitalization(get('price'), get('shares')))
        
        # Enterprise Value
        if not has('enterprise_value') and has('market_cap'):
            set_val('enterprise_value', Formulas.enterprise_value(
                get('market_cap'), get('debt'), get('cash'),
                get('minority_interest'), get('preferred_equity')
            ))
        
        # Book Value Per Share
        if not has('book_value_per_share') and has('equity') and has('shares'):
            shares = get('shares')
            if shares and shares > 0:
                set_val('book_value_per_share', Formulas.book_value_per_share(get('equity'), shares))
        
        # Revenue Per Share
        if not has('revenue_per_share') and has('revenue') and has('shares'):
            shares = get('shares')
            if shares and shares > 0:
                set_val('revenue_per_share', Formulas.revenue_per_share(get('revenue'), shares))
        
        # Operating Cash Flow Per Share
        if not has('operating_cash_flow_per_share') and has('cash_from_operations') and has('shares'):
            shares = get('shares')
            if shares and shares > 0:
                set_val('operating_cash_flow_per_share', 
                       Formulas.operating_cf_per_share(get('cash_from_operations'), shares))
        
        # Free Cash Flow
        if not has('free_cash_flow') and has('cash_from_operations'):
            set_val('free_cash_flow', Formulas.free_cash_flow(
                get('cash_from_operations'), get('capex')))
        
        # FCF Per Share
        if not has('free_cash_flow_per_share') and has('free_cash_flow') and has('shares'):
            shares = get('shares')
            if shares and shares > 0:
                set_val('free_cash_flow_per_share', 
                       Formulas.fcf_per_share(get('free_cash_flow'), shares))
        
        # Tangible Book Value
        if not has('tangible_book_value') and has('equity'):
            set_val('tangible_book_value', Formulas.tangible_book_value(
                get('equity'), get('intangible_assets'), get('goodwill')))
        
        # Tangible BVPS
        if not has('tangible_bvps') and has('tangible_book_value') and has('shares'):
            shares = get('shares')
            if shares and shares > 0:
                set_val('tangible_bvps', Formulas.tangible_bvps(get('tangible_book_value'), shares))
        
        # Working Capital
        if not has('working_capital') and has('current_assets') and has('current_liabilities'):
            set_val('working_capital', Formulas.working_capital(
                get('current_assets'), get('current_liabilities')))
        
        # Total Liabilities (if we have current + non-current)
        if not has('total_liabilities') and has('current_liabilities'):
            total_liab = safe_add(get('current_liabilities'), get('long_term_liabilities'))
            if total_liab > 0:
                set_val('total_liabilities', total_liab)
    
    def _create_metric(self, label: str, curr: float, prev: float,
                       formula: Optional[str] = None,
                       inputs_used: Optional[Dict[str, float]] = None) -> MetricResult:
        """Create a successful metric result."""
        var = safe_subtract(curr, prev)
        var_pct = safe_percent(safe_divide(var, prev)) if prev != 0 else 0.0
        
        clean_id = f"calc_{label.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')}"
        
        return MetricResult(
            id=clean_id,
            label=label,
            current_year=round(curr, 4) if curr else 0,
            previous_year=round(prev, 4) if prev else 0,
            variation=round(var, 4) if var else 0,
            variation_percent=round(var_pct, 2),
            formula=formula,
            inputs_used=inputs_used
        )
    
    def _create_metric_error(self, label: str, reason: str = "Inputs missing") -> MetricResult:
        """Create an error metric result."""
        clean_id = f"calc_err_{label.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')}"
        
        return MetricResult(
            id=clean_id,
            label=label,
            current_year=0,
            previous_year=0,
            variation=0,
            variation_percent=0,
            calculation_error=reason
        )
    
    def _compute_metric(self, category: str, label: str, 
                        func: Callable, input_keys: List[str],
                        formula: Optional[str] = None) -> None:
        """Compute a metric and add to results."""
        if category not in self.results:
            self.results[category] = []
        
        # Check for missing inputs
        missing_curr = [k for k in input_keys if not self.inputs.has(k, 'current')]
        missing_prev = [k for k in input_keys if not self.inputs.has(k, 'previous')]
        
        if missing_curr:
            self.results[category].append(
                self._create_metric_error(label, f"Missing: {', '.join(missing_curr)}")
            )
            return
        
        # Get input values
        args_curr = [self.inputs.get(k, 'current', 0) for k in input_keys]
        args_prev = [self.inputs.get(k, 'previous', 0) for k in input_keys]
        
        # Build inputs used dict
        inputs_used = {k: self.inputs.get(k, 'current', 0) for k in input_keys}
        
        try:
            res_curr = func(*args_curr)
            res_prev = func(*args_prev)
            
            # Handle None results
            if res_curr is None:
                res_curr = 0
            if res_prev is None:
                res_prev = 0
            
            self.results[category].append(
                self._create_metric(label, res_curr, res_prev, formula, inputs_used)
            )
        except Exception as e:
            logger.warning(f"Calculation error for {label}: {e}")
            self.results[category].append(
                self._create_metric_error(label, f"Calculation error: {str(e)[:50]}")
            )
    
    def _add_passthrough_metric(self, category: str, label: str, key: str) -> None:
        """Add a passthrough metric (just displays derived value)."""
        if category not in self.results:
            self.results[category] = []
        
        curr = self.inputs.get(key, 'current')
        prev = self.inputs.get(key, 'previous')
        
        if curr is not None or prev is not None:
            self.results[category].append(
                self._create_metric(label, curr or 0, prev or 0)
            )
        else:
            self.results[category].append(
                self._create_metric_error(label, f"Missing: {key}")
            )
    
    def _calculate_all_categories(self) -> None:
        """Calculate all metric categories."""
        self._calc_valuation_ratios()
        self._calc_profitability_metrics()
        self._calc_cash_flow_metrics()
        self._calc_liquidity_metrics()
        self._calc_leverage_metrics()
        self._calc_efficiency_metrics()
        self._calc_growth_metrics()
        self._calc_market_metrics()
        self._calc_dividend_metrics()
        self._calc_dupont_analysis()
        self._calc_statistical_metrics()
        self._calc_dcf_framework()
        self._calc_other_metrics()
        self._calc_damodaran_formulas()
        self._calc_graham_formulas()
        self._calc_modern_value()
        self._calc_appendix_formulas()
    
    def _calc_valuation_ratios(self) -> None:
        """Calculate valuation ratios."""
        cat = MetricCategory.VALUATION.value
        
        self._compute_metric(cat, "P/E Ratio", Formulas.price_to_earnings, 
                            ['price', 'eps'], "Price / EPS")
        self._compute_metric(cat, "P/E Ratio (Alt)", Formulas.price_to_earnings_alt,
                            ['market_cap', 'net_income'], "Market Cap / Net Income")
        self._compute_metric(cat, "P/B Ratio", Formulas.price_to_book,
                            ['price', 'book_value_per_share'], "Price / BVPS")
        self._compute_metric(cat, "P/S Ratio", Formulas.price_to_sales,
                            ['price', 'revenue_per_share'], "Price / Revenue Per Share")
        self._compute_metric(cat, "P/S Ratio (Alt)", Formulas.price_to_sales_alt,
                            ['market_cap', 'revenue'], "Market Cap / Revenue")
        self._compute_metric(cat, "P/CF Ratio", Formulas.price_to_cash_flow,
                            ['price', 'operating_cash_flow_per_share'], "Price / CF Per Share")
        self._compute_metric(cat, "P/CF Ratio (Alt)", Formulas.price_to_cash_flow_alt,
                            ['market_cap', 'cash_from_operations'], "Market Cap / Operating CF")
        self._compute_metric(cat, "Earnings Yield (%)", Formulas.earnings_yield,
                            ['eps', 'price'], "EPS / Price × 100")
        self._compute_metric(cat, "Earnings Yield (Alt) (%)", Formulas.earnings_yield_alt,
                            ['net_income', 'market_cap'], "Net Income / Market Cap × 100")
        self._compute_metric(cat, "EV/EBITDA", Formulas.ev_to_ebitda,
                            ['enterprise_value', 'ebitda'], "EV / EBITDA")
        self._compute_metric(cat, "EV/EBIT", Formulas.ev_to_ebit,
                            ['enterprise_value', 'operating_income'], "EV / EBIT")
        self._compute_metric(cat, "EV/Sales", Formulas.ev_to_sales,
                            ['enterprise_value', 'revenue'], "EV / Revenue")
        self._compute_metric(cat, "EV/FCF", Formulas.ev_to_fcf,
                            ['enterprise_value', 'free_cash_flow'], "EV / FCF")
        self._compute_metric(cat, "Price/Tangible Book", Formulas.price_to_tangible_book,
                            ['price', 'tangible_bvps'], "Price / Tangible BVPS")
        self._compute_metric(cat, "Price/FCF", Formulas.price_to_fcf,
                            ['price', 'free_cash_flow_per_share'], "Price / FCF Per Share")
    
    def _calc_profitability_metrics(self) -> None:
        """Calculate profitability metrics."""
        cat = MetricCategory.PROFITABILITY.value
        
        self._compute_metric(cat, "Gross Margin (%)", Formulas.gross_profit_margin,
                            ['gross_profit', 'revenue'], "Gross Profit / Revenue × 100")
        self._compute_metric(cat, "Operating Margin (%)", Formulas.operating_margin,
                            ['operating_income', 'revenue'], "Operating Income / Revenue × 100")
        self._compute_metric(cat, "Net Profit Margin (%)", Formulas.net_profit_margin,
                            ['net_income', 'revenue'], "Net Income / Revenue × 100")
        self._compute_metric(cat, "EBITDA Margin (%)", Formulas.ebitda_margin,
                            ['ebitda', 'revenue'], "EBITDA / Revenue × 100")
        self._compute_metric(cat, "ROA (%)", Formulas.return_on_assets,
                            ['net_income', 'total_assets'], "Net Income / Total Assets × 100")
        self._compute_metric(cat, "ROE (%)", Formulas.return_on_equity,
                            ['net_income', 'equity'], "Net Income / Equity × 100")
    
    def _calc_cash_flow_metrics(self) -> None:
        """Calculate cash flow metrics."""
        cat = MetricCategory.CASH_FLOW.value
        
        self._add_passthrough_metric(cat, "Free Cash Flow", 'free_cash_flow')
        self._add_passthrough_metric(cat, "Operating CF / Share", 'operating_cash_flow_per_share')
        self._add_passthrough_metric(cat, "FCF / Share", 'free_cash_flow_per_share')
        self._compute_metric(cat, "Cash Flow Margin (%)", Formulas.cash_flow_margin,
                            ['cash_from_operations', 'revenue'], "Operating CF / Revenue × 100")
        self._compute_metric(cat, "FCF Yield (%)", Formulas.fcf_yield,
                            ['free_cash_flow', 'market_cap'], "FCF / Market Cap × 100")
        self._compute_metric(cat, "Cash Conversion Ratio", Formulas.cash_conversion_ratio,
                            ['cash_from_operations', 'net_income'], "Operating CF / Net Income")
    
    def _calc_liquidity_metrics(self) -> None:
        """Calculate liquidity metrics."""
        cat = MetricCategory.LIQUIDITY.value
        
        self._compute_metric(cat, "Current Ratio", Formulas.current_ratio,
                            ['current_assets', 'current_liabilities'],
                            "Current Assets / Current Liabilities")
        self._compute_metric(cat, "Quick Ratio", Formulas.quick_ratio,
                            ['current_assets', 'inventory', 'current_liabilities'],
                            "(Current Assets - Inventory) / Current Liabilities")
        self._compute_metric(cat, "Cash Ratio", Formulas.cash_ratio,
                            ['cash', 'current_liabilities'], "Cash / Current Liabilities")
        self._add_passthrough_metric(cat, "Working Capital", 'working_capital')
    
    def _calc_leverage_metrics(self) -> None:
        """Calculate leverage/solvency metrics."""
        cat = MetricCategory.LEVERAGE.value
        
        self._compute_metric(cat, "Debt to Equity", Formulas.debt_to_equity,
                            ['debt', 'equity'], "Total Debt / Equity")
        self._compute_metric(cat, "Debt to Assets", Formulas.debt_to_assets,
                            ['debt', 'total_assets'], "Total Debt / Total Assets")
        self._compute_metric(cat, "Debt to Capital", Formulas.debt_to_capital,
                            ['debt', 'equity'], "Debt / (Debt + Equity)")
        self._compute_metric(cat, "Interest Coverage", Formulas.interest_coverage,
                            ['operating_income', 'interest'], "EBIT / Interest Expense")
        self._compute_metric(cat, "Equity Multiplier", Formulas.equity_multiplier,
                            ['total_assets', 'equity'], "Total Assets / Equity")
    
    def _calc_efficiency_metrics(self) -> None:
        """Calculate efficiency/activity metrics."""
        cat = MetricCategory.EFFICIENCY.value
        
        self._compute_metric(cat, "Asset Turnover", Formulas.asset_turnover,
                            ['revenue', 'total_assets'], "Revenue / Total Assets")
        self._compute_metric(cat, "Inventory Turnover", Formulas.inventory_turnover,
                            ['cogs', 'inventory'], "COGS / Inventory")
        self._compute_metric(cat, "Fixed Asset Turnover", Formulas.fixed_asset_turnover,
                            ['revenue', 'non_current_assets'], "Revenue / Fixed Assets")
        self._add_passthrough_metric(cat, "Revenue / Share", 'revenue_per_share')
        self._add_passthrough_metric(cat, "Book Value / Share", 'book_value_per_share')
        self._add_passthrough_metric(cat, "Tangible BV / Share", 'tangible_bvps')
    
    def _calc_growth_metrics(self) -> None:
        """Calculate growth metrics."""
        cat = MetricCategory.GROWTH.value
        
        # Revenue Growth
        curr_rev = self.inputs.get('revenue', 'current')
        prev_rev = self.inputs.get('revenue', 'previous')
        if curr_rev and prev_rev:
            growth = Formulas.growth_rate(curr_rev, prev_rev)
            self.results[cat] = [self._create_metric("Revenue Growth (%)", growth, 0,
                                                     "(Current - Previous) / Previous × 100")]
        else:
            self.results[cat] = [self._create_metric_error("Revenue Growth (%)", "Missing revenue data")]
        
        # Net Income Growth
        curr_ni = self.inputs.get('net_income', 'current')
        prev_ni = self.inputs.get('net_income', 'previous')
        if curr_ni and prev_ni:
            growth = Formulas.growth_rate(curr_ni, prev_ni)
            self.results[cat].append(self._create_metric("Net Income Growth (%)", growth, 0))
        
        # EPS Growth
        curr_eps = self.inputs.get('eps', 'current')
        prev_eps = self.inputs.get('eps', 'previous')
        if curr_eps and prev_eps:
            growth = Formulas.growth_rate(curr_eps, prev_eps)
            self.results[cat].append(self._create_metric("EPS Growth (%)", growth, 0))
    
    def _calc_market_metrics(self) -> None:
        """Calculate market metrics."""
        cat = MetricCategory.MARKET.value
        
        self._add_passthrough_metric(cat, "Market Cap", 'market_cap')
        self._add_passthrough_metric(cat, "Enterprise Value", 'enterprise_value')
    
    def _calc_dividend_metrics(self) -> None:
        """Calculate dividend metrics."""
        cat = MetricCategory.DIVIDEND.value
        self.results[cat] = []
        
        # Try total dividends / market cap first
        curr_div = self.inputs.get('dividends', 'current')
        curr_mc = self.inputs.get('market_cap', 'current')
        
        if curr_div and curr_mc and curr_mc > 0:
            yield_val = safe_percent(safe_divide(curr_div, curr_mc))
            self.results[cat].append(
                self._create_metric("Dividend Yield (Total) (%)", yield_val, 0,
                                   "Total Dividends / Market Cap × 100")
            )
        else:
            # Fallback to DPS / Price
            self._compute_metric(cat, "Dividend Yield (DPS) (%)", Formulas.dividend_yield,
                                ['dps', 'price'], "DPS / Price × 100")
        
        # Payout Ratio
        self._compute_metric(cat, "Dividend Payout Ratio (%)", Formulas.dividend_payout_ratio,
                            ['dividends', 'net_income'], "Dividends / Net Income × 100")
    
    def _calc_dupont_analysis(self) -> None:
        """Calculate DuPont analysis components."""
        cat = MetricCategory.DUPONT.value
        self.results[cat] = []
        
        # Check if we have all required inputs
        required = ['net_income', 'revenue', 'total_assets', 'equity']
        if not all(self.inputs.has(k, 'current') for k in required):
            missing = [k for k in required if not self.inputs.has(k, 'current')]
            self.results[cat].append(
                self._create_metric_error("DuPont ROE", f"Missing: {', '.join(missing)}")
            )
            return
        
        curr = {k: self.inputs.get(k, 'current') for k in required}
        
        # Calculate components
        net_margin = safe_divide(curr['net_income'], curr['revenue'])
        asset_turnover = safe_divide(curr['revenue'], curr['total_assets'])
        equity_multiplier = safe_divide(curr['total_assets'], curr['equity'])
        
        # DuPont ROE
        dupont_roe = safe_multiply(net_margin, asset_turnover, equity_multiplier) * 100
        
        self.results[cat].append(
            self._create_metric("Net Profit Margin (Component)", net_margin * 100, 0)
        )
        self.results[cat].append(
            self._create_metric("Asset Turnover (Component)", asset_turnover, 0)
        )
        self.results[cat].append(
            self._create_metric("Equity Multiplier (Component)", equity_multiplier, 0)
        )
        self.results[cat].append(
            self._create_metric("DuPont ROE (%)", dupont_roe, 0,
                               "Net Margin × Asset Turnover × Equity Multiplier")
        )
    
    def _calc_statistical_metrics(self) -> None:
        """Calculate statistical metrics (placeholder)."""
        cat = MetricCategory.STATISTICAL.value
        self.results[cat] = [
            self._create_metric_error("Revenue Variance", "Feature pending - requires time series data")
        ]
    
    def _calc_dcf_framework(self) -> None:
        """Calculate DCF valuation framework (placeholder)."""
        cat = MetricCategory.DCF.value
        self.results[cat] = [
            self._create_metric_error("WACC", "Missing: Beta, Risk Free Rate, Market Risk Premium"),
            self._create_metric_error("Intrinsic Value (DCF)", "Missing: Growth projections, Terminal value inputs")
        ]
    
    def _calc_other_metrics(self) -> None:
        """Calculate other key metrics."""
        cat = MetricCategory.OTHER.value
        
        self._compute_metric(cat, "EV/Revenue", Formulas.ev_to_sales,
                            ['enterprise_value', 'revenue'], "EV / Revenue")
        self._compute_metric(cat, "EV/Operating Income", Formulas.ev_to_ebit,
                            ['enterprise_value', 'operating_income'], "EV / Operating Income")
    
    def _calc_damodaran_formulas(self) -> None:
        """Calculate Aswath Damodaran valuation formulas (placeholder)."""
        cat = MetricCategory.DAMODARAN.value
        self.results[cat] = [
            self._create_metric_error("Cost of Equity (CAPM)", 
                                      "Missing: Beta, Risk Free Rate, Equity Risk Premium"),
            self._create_metric_error("Cost of Debt", "Missing: Interest Rate, Tax Rate")
        ]
    
    def _calc_graham_formulas(self) -> None:
        """Calculate Benjamin Graham formulas."""
        cat = MetricCategory.GRAHAM.value
        
        self._compute_metric(cat, "Graham Number", Formulas.graham_number,
                            ['eps', 'book_value_per_share'], "√(22.5 × EPS × BVPS)")
    
    def _calc_modern_value(self) -> None:
        """Calculate modern value investing metrics."""
        cat = MetricCategory.MODERN_VALUE.value
        
        self._compute_metric(cat, "Greenblatt Earnings Yield (%)", 
                            Formulas.greenblatt_earnings_yield,
                            ['operating_income', 'enterprise_value'], "EBIT / EV × 100")
    
    def _calc_appendix_formulas(self) -> None:
        """Calculate appendix financial statement formulas."""
        cat = MetricCategory.APPENDIX.value
        
        self._compute_metric(cat, "Gross Profit", Formulas.gross_profit,
                            ['revenue', 'cogs'], "Revenue - COGS")
        self._compute_metric(cat, "Operating Income", Formulas.operating_income,
                            ['gross_profit', 'opex'], "Gross Profit - OpEx")
        self._compute_metric(cat, "EBITDA", Formulas.ebitda_calc,
                            ['operating_income', 'depreciation'], "Operating Income + D&A")
        self._compute_metric(cat, "Shareholders' Equity", Formulas.shareholders_equity,
                            ['total_assets', 'total_liabilities'], "Total Assets - Total Liabilities")
        self._compute_metric(cat, "Net Change in Cash", Formulas.net_change_in_cash,
                            ['cash_from_operations', 'cash_from_investing', 'cash_from_financing'],
                            "Operating CF + Investing CF + Financing CF")
    
    def _format_output(self) -> str:
        """Format results as JSON string."""
        output = []
        
        # Sort categories by their enum order
        category_order = [cat.value for cat in MetricCategory]
        
        for cat_name in category_order:
            if cat_name in self.results:
                items = [m.to_dict() for m in self.results[cat_name]]
                output.append({
                    "category": cat_name,
                    "items": items
                })
        
        return json.dumps(output, indent=None)


# =============================================================================
# PUBLIC API
# =============================================================================

def calculate_comprehensive_metrics(items_json: str, 
                                    custom_mapping_json: Optional[str] = None) -> str:
    """
    Calculate comprehensive financial metrics from parsed financial items.
    
    This is the main entry point for the metrics calculator.
    
    Args:
        items_json: JSON string containing parsed financial items from FinancialParser
        custom_mapping_json: Optional JSON string with custom keyword mappings
        
    Returns:
        JSON string containing calculated metrics organized by category
        
    Example:
        >>> from parsers import parse_annual_report
        >>> from metrics_calculator import calculate_comprehensive_metrics
        >>> 
        >>> parsed = parse_annual_report("annual_report.pdf")
        >>> items_json = json.dumps(parsed['items'])
        >>> metrics = calculate_comprehensive_metrics(items_json)
        >>> print(metrics)
    """
    calculator = MetricsCalculator()
    return calculator.calculate(items_json, custom_mapping_json)


# =============================================================================
# CLI SUPPORT
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Test with sample data
    sample_items = [
        {"label": "Revenue from Operations", "currentYear": 100000, "previousYear": 90000},
        {"label": "Cost of Materials Consumed", "currentYear": 60000, "previousYear": 55000},
        {"label": "Profit After Tax", "currentYear": 15000, "previousYear": 12000},
        {"label": "Total Assets", "currentYear": 200000, "previousYear": 180000},
        {"label": "Total Equity", "currentYear": 120000, "previousYear": 110000},
        {"label": "Current Assets", "currentYear": 80000, "previousYear": 70000},
        {"label": "Current Liabilities", "currentYear": 40000, "previousYear": 35000},
        {"label": "Inventories", "currentYear": 20000, "previousYear": 18000},
        {"label": "Total Debt", "currentYear": 40000, "previousYear": 35000},
        {"label": "Cash and Cash Equivalents", "currentYear": 15000, "previousYear": 12000},
    ]
    
    result = calculate_comprehensive_metrics(json.dumps(sample_items))
    parsed_result = json.loads(result)
    
    print("=" * 60)
    print("FINANCIAL METRICS CALCULATOR - TEST OUTPUT")
    print("=" * 60)
    
    for category in parsed_result:
        print(f"\n{category['category']}")
        print("-" * 40)
        for item in category['items']:
            if 'calculationError' in item:
                print(f"  ⚠ {item['label']}: {item['calculationError']}")
            else:
                print(f"  ✓ {item['label']}: {item['currentYear']:.2f}")