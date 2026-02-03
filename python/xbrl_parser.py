"""
Phase 1: XBRL/iXBRL Integration.

Provides parsers for:
- SEC iXBRL (10-K, 10-Q) using ixbrlparse
- Indian MCA XBRL (Ind AS taxonomy)
"""

import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Check for ixbrlparse availability
try:
    from ixbrlparse import IXBRL
    IXBRL_AVAILABLE = True
except ImportError:
    IXBRL_AVAILABLE = False
    logger.warning("ixbrlparse not installed. SEC iXBRL parsing disabled. Install with: pip install ixbrlparse")

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class XBRLFact:
    """Represents a single XBRL fact (data point)."""
    concept: str           # e.g., "us-gaap:Assets"
    value: Any             # Numeric or string value
    unit: Optional[str]    # e.g., "USD", "shares"
    period_start: Optional[str]  # ISO date
    period_end: Optional[str]    # ISO date
    instant: Optional[str]       # For instant (Balance Sheet) items
    context_id: str
    decimals: Optional[int] = None
    
    @property
    def period_label(self) -> str:
        """Generate human-readable period label."""
        if self.instant:
            return f"As at {self.instant}"
        elif self.period_end:
            return f"Year ended {self.period_end}"
        return "Unknown Period"

@dataclass
class XBRLDocument:
    """Parsed XBRL document with extracted facts."""
    source_file: str
    taxonomy: str          # "us-gaap", "ifrs", "ind-as"
    company_name: str
    filing_date: Optional[str]
    fiscal_year_end: Optional[str]
    facts: List[XBRLFact] = field(default_factory=list)
    contexts: Dict[str, Any] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)

# =============================================================================
# Taxonomy Mappings (Phase 1.3)
# =============================================================================

# US GAAP Concept -> Canonical Metric Key
US_GAAP_TAXONOMY_MAP = {
    # Balance Sheet - Assets
    "us-gaap:Assets": "total_assets",
    "us-gaap:AssetsCurrent": "total_current_assets",
    "us-gaap:AssetsNoncurrent": "total_non_current_assets",
    "us-gaap:CashAndCashEquivalentsAtCarryingValue": "cash_and_equivalents",
    "us-gaap:AccountsReceivableNetCurrent": "trade_receivables",
    "us-gaap:InventoryNet": "inventories",
    "us-gaap:PropertyPlantAndEquipmentNet": "property_plant_equipment",
    "us-gaap:Goodwill": "goodwill",
    "us-gaap:IntangibleAssetsNetExcludingGoodwill": "intangible_assets",
    
    # Balance Sheet - Liabilities
    "us-gaap:Liabilities": "total_liabilities",
    "us-gaap:LiabilitiesCurrent": "total_current_liabilities",
    "us-gaap:LiabilitiesNoncurrent": "total_non_current_liabilities",
    "us-gaap:AccountsPayableCurrent": "trade_payables",
    "us-gaap:LongTermDebt": "long_term_borrowings",
    "us-gaap:ShortTermBorrowings": "short_term_borrowings",
    
    # Balance Sheet - Equity
    "us-gaap:StockholdersEquity": "total_equity",
    "us-gaap:CommonStockValue": "share_capital",
    "us-gaap:RetainedEarningsAccumulatedDeficit": "retained_earnings",
    
    # Income Statement
    "us-gaap:Revenues": "total_revenue",
    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax": "revenue_from_operations",
    "us-gaap:CostOfGoodsAndServicesSold": "cost_of_goods_sold",
    "us-gaap:GrossProfit": "gross_profit",
    "us-gaap:OperatingIncomeLoss": "operating_profit",
    "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "profit_before_tax",
    "us-gaap:NetIncomeLoss": "profit_for_the_year",
    "us-gaap:EarningsPerShareBasic": "earnings_per_share_basic",
    "us-gaap:EarningsPerShareDiluted": "earnings_per_share_diluted",
    
    # Cash Flow
    "us-gaap:NetCashProvidedByUsedInOperatingActivities": "net_cash_from_operating_activities",
    "us-gaap:NetCashProvidedByUsedInInvestingActivities": "net_cash_from_investing_activities",
    "us-gaap:NetCashProvidedByUsedInFinancingActivities": "net_cash_from_financing_activities",
    "us-gaap:DepreciationDepletionAndAmortization": "depreciation_and_amortization",
}

# Ind AS Concept -> Canonical Metric Key
IND_AS_TAXONOMY_MAP = {
    # Balance Sheet - Assets (Ind AS uses IFRS-based concepts)
    "in-bse-gaap:TotalAssets": "total_assets",
    "in-bse-gaap:CurrentAssets": "total_current_assets",
    "in-bse-gaap:NoncurrentAssets": "total_non_current_assets",
    "in-bse-gaap:CashAndCashEquivalents": "cash_and_equivalents",
    "in-bse-gaap:TradeReceivables": "trade_receivables",
    "in-bse-gaap:Inventories": "inventories",
    "in-bse-gaap:PropertyPlantAndEquipment": "property_plant_equipment",
    "in-bse-gaap:CapitalWorkInProgress": "capital_work_in_progress",
    
    # Balance Sheet - Liabilities
    "in-bse-gaap:TotalLiabilities": "total_liabilities",
    "in-bse-gaap:CurrentLiabilities": "total_current_liabilities",
    "in-bse-gaap:NoncurrentLiabilities": "total_non_current_liabilities",
    "in-bse-gaap:TradePayables": "trade_payables",
    "in-bse-gaap:Borrowings": "total_borrowings",
    
    # Balance Sheet - Equity
    "in-bse-gaap:Equity": "total_equity",
    "in-bse-gaap:ShareCapital": "share_capital",
    "in-bse-gaap:ReservesAndSurplus": "reserves_and_surplus",
    
    # Income Statement
    "in-bse-gaap:RevenueFromOperations": "revenue_from_operations",
    "in-bse-gaap:OtherIncome": "other_income",
    "in-bse-gaap:TotalIncome": "total_revenue",
    "in-bse-gaap:CostOfMaterialsConsumed": "cost_of_materials_consumed",
    "in-bse-gaap:ProfitBeforeTax": "profit_before_tax",
    "in-bse-gaap:ProfitForThePeriod": "profit_for_the_year",
    "in-bse-gaap:BasicEarningsPerShare": "earnings_per_share_basic",
    
    # Cash Flow
    "in-bse-gaap:CashFlowsFromOperatingActivities": "net_cash_from_operating_activities",
    "in-bse-gaap:CashFlowsFromInvestingActivities": "net_cash_from_investing_activities",
    "in-bse-gaap:CashFlowsFromFinancingActivities": "net_cash_from_financing_activities",
}

# =============================================================================
# SEC iXBRL Parser (Phase 1.1)
# =============================================================================

class SECiXBRLParser:
    """Parser for SEC iXBRL filings (10-K, 10-Q)."""
    
    def __init__(self):
        if not IXBRL_AVAILABLE:
            raise ImportError("ixbrlparse is required. Install with: pip install ixbrlparse")
    
    def parse_file(self, filepath: str) -> XBRLDocument:
        """Parse an iXBRL file and return structured document."""
        logger.info(f"Parsing iXBRL file: {filepath}")
        
        ixbrl = IXBRL(filepath)
        
        # Extract company info from contexts
        company_name = self._extract_company_name(ixbrl)
        filing_date = self._extract_filing_date(ixbrl)
        
        # Build facts list
        facts = []
        for fact in ixbrl.numeric:
            xbrl_fact = XBRLFact(
                concept=fact.name,
                value=fact.value,
                unit=str(fact.unit) if fact.unit else None,
                period_start=str(fact.context.startdate) if hasattr(fact.context, 'startdate') and fact.context.startdate else None,
                period_end=str(fact.context.enddate) if hasattr(fact.context, 'enddate') and fact.context.enddate else None,
                instant=str(fact.context.instant) if hasattr(fact.context, 'instant') and fact.context.instant else None,
                context_id=fact.context.id if fact.context else "",
                decimals=fact.decimals
            )
            facts.append(xbrl_fact)
        
        # Also capture non-numeric facts (text blocks)
        for fact in ixbrl.nonnumeric:
            xbrl_fact = XBRLFact(
                concept=fact.name,
                value=fact.value[:500] if isinstance(fact.value, str) else fact.value,  # Truncate long text
                unit=None,
                period_start=None,
                period_end=None,
                instant=None,
                context_id=fact.context.id if fact.context else ""
            )
            facts.append(xbrl_fact)
        
        return XBRLDocument(
            source_file=filepath,
            taxonomy="us-gaap",
            company_name=company_name,
            filing_date=filing_date,
            fiscal_year_end=None,
            facts=facts
        )
    
    def _extract_company_name(self, ixbrl) -> str:
        """Extract company name from iXBRL."""
        for fact in ixbrl.nonnumeric:
            if "EntityRegistrantName" in fact.name:
                return str(fact.value)
        return "Unknown Company"
    
    def _extract_filing_date(self, ixbrl) -> Optional[str]:
        """Extract filing date."""
        for fact in ixbrl.nonnumeric:
            if "DocumentPeriodEndDate" in fact.name:
                return str(fact.value)
        return None
    
    def map_to_canonical(self, doc: XBRLDocument) -> Dict[str, Dict[str, float]]:
        """Map XBRL facts to canonical metric keys, grouped by period."""
        result = {}  # period_label -> {metric_key: value}
        
        for fact in doc.facts:
            if not isinstance(fact.value, (int, float)):
                continue
                
            # Check if concept is in taxonomy map
            metric_key = US_GAAP_TAXONOMY_MAP.get(fact.concept)
            if not metric_key:
                # Try partial match
                for concept, key in US_GAAP_TAXONOMY_MAP.items():
                    if concept.split(":")[-1] in fact.concept:
                        metric_key = key
                        break
            
            if metric_key:
                period = fact.period_label
                if period not in result:
                    result[period] = {}
                result[period][metric_key] = float(fact.value)
        
        return result

# =============================================================================
# Indian MCA XBRL Parser (Phase 1.2)
# =============================================================================

class IndianXBRLParser:
    """Parser for Indian MCA XBRL filings (Ind AS taxonomy)."""
    
    def parse_file(self, filepath: str) -> XBRLDocument:
        """Parse Indian XBRL file (.xml)."""
        logger.info(f"Parsing Indian XBRL file: {filepath}")
        
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Detect namespaces
        namespaces = {
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'in-bse-gaap': 'http://www.bseindia.com/xbrl/2021-03-31/in-bse-gaap',
            'link': 'http://www.xbrl.org/2003/linkbase',
        }
        
        # Extract contexts
        contexts = {}
        for ctx in root.findall('.//xbrli:context', namespaces):
            ctx_id = ctx.get('id')
            period = ctx.find('xbrli:period', namespaces)
            if period is not None:
                instant = period.find('xbrli:instant', namespaces)
                start = period.find('xbrli:startDate', namespaces)
                end = period.find('xbrli:endDate', namespaces)
                contexts[ctx_id] = {
                    'instant': instant.text if instant is not None else None,
                    'start': start.text if start is not None else None,
                    'end': end.text if end is not None else None,
                }
        
        # Extract facts
        facts = []
        for elem in root.iter():
            if elem.text and elem.get('contextRef'):
                ctx_id = elem.get('contextRef')
                ctx = contexts.get(ctx_id, {})
                
                try:
                    value = float(elem.text.replace(',', ''))
                except ValueError:
                    value = elem.text
                
                fact = XBRLFact(
                    concept=elem.tag,
                    value=value,
                    unit=elem.get('unitRef'),
                    period_start=ctx.get('start'),
                    period_end=ctx.get('end'),
                    instant=ctx.get('instant'),
                    context_id=ctx_id,
                    decimals=int(elem.get('decimals')) if elem.get('decimals') else None
                )
                facts.append(fact)
        
        return XBRLDocument(
            source_file=filepath,
            taxonomy="ind-as",
            company_name=self._extract_company_name(facts),
            filing_date=None,
            fiscal_year_end=None,
            facts=facts,
            contexts=contexts
        )
    
    def _extract_company_name(self, facts: List[XBRLFact]) -> str:
        """Extract company name from facts."""
        for fact in facts:
            if "NameOfCompany" in fact.concept or "EntityName" in fact.concept:
                return str(fact.value)
        return "Unknown Company"
    
    def map_to_canonical(self, doc: XBRLDocument) -> Dict[str, Dict[str, float]]:
        """Map Ind AS XBRL facts to canonical metric keys."""
        result = {}
        
        for fact in doc.facts:
            if not isinstance(fact.value, (int, float)):
                continue
            
            metric_key = None
            # Try exact match
            for concept, key in IND_AS_TAXONOMY_MAP.items():
                if concept in fact.concept or concept.split(":")[-1] in fact.concept:
                    metric_key = key
                    break
            
            if metric_key:
                period = fact.period_label
                if period not in result:
                    result[period] = {}
                result[period][metric_key] = float(fact.value)
        
        return result

# =============================================================================
# Unified XBRL Parser Interface
# =============================================================================

class XBRLParser:
    """Unified interface for XBRL parsing."""
    
    def __init__(self):
        self.sec_parser = SECiXBRLParser() if IXBRL_AVAILABLE else None
        self.indian_parser = IndianXBRLParser()
    
    def parse(self, filepath: str) -> XBRLDocument:
        """Auto-detect file type and parse."""
        filepath_lower = filepath.lower()
        
        if filepath_lower.endswith('.htm') or filepath_lower.endswith('.html'):
            # SEC iXBRL
            if not self.sec_parser:
                raise ImportError("ixbrlparse required for SEC filings")
            return self.sec_parser.parse_file(filepath)
        elif filepath_lower.endswith('.xml'):
            # Indian XBRL
            return self.indian_parser.parse_file(filepath)
        else:
            raise ValueError(f"Unsupported file type: {filepath}")
    
    def extract_metrics(self, filepath: str) -> Dict[str, Dict[str, float]]:
        """Parse file and return canonical metrics grouped by period."""
        doc = self.parse(filepath)
        
        if doc.taxonomy == "us-gaap":
            return self.sec_parser.map_to_canonical(doc)
        elif doc.taxonomy == "ind-as":
            return self.indian_parser.map_to_canonical(doc)
        else:
            return {}


if __name__ == "__main__":
    # Quick test
    print(f"XBRL Parser loaded. ixbrlparse available: {IXBRL_AVAILABLE}")
    print(f"US GAAP mappings: {len(US_GAAP_TAXONOMY_MAP)}")
    print(f"Ind AS mappings: {len(IND_AS_TAXONOMY_MAP)}")
