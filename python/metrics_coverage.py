
import re
from typing import List, Dict, Any, Optional
import sys
import os

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from terminology_keywords import TERMINOLOGY_MAP, KEYWORD_TO_TERM, ALL_TERMS
except ImportError:
    TERMINOLOGY_MAP = {}
    KEYWORD_TO_TERM = {}
    ALL_TERMS = []

class MetricsCoverageEngine:
    """
    Analyzes extraction coverage against expected mandatory metrics.
    Identifies why items were missed (Not in text vs Failed to extract).
    """
    
    # Priority metrics that should ideally be in every annual report
    MANDATORY_METRICS = {
        'total_revenue': 'Total Revenue',
        'cost_of_goods_sold': 'Cost of Goods Sold',
        'gross_profit': 'Gross Profit',
        'operating_profit': 'Operating Profit',
        'profit_before_tax': 'Profit Before Tax',
        'profit_for_the_year': 'Net Profit',
        'total_assets': 'Total Assets',
        'total_current_assets': 'Current Assets',
        'property_plant_equipment': 'PPE / Fixed Assets',
        'total_liabilities': 'Total Liabilities',
        'total_current_liabilities': 'Current Liabilities',
        'total_equity': 'Total Equity',
        'cash_and_equivalents': 'Cash & Equivalents'
    }

    def analyze_coverage(self, items: List[Dict[str, Any]], raw_text: str) -> List[Dict[str, Any]]:
        """
        Check which mandatory metrics are present and why others are missing.
        """
        results = []
        
        # 1. Map extracted items to their term IDs
        extracted_keys = set()
        extracted_items_by_key = {}
        
        for item in items:
            term_id = item.get('id')
            if term_id:
                extracted_keys.add(term_id)
                extracted_items_by_key[term_id] = item

        # 2. Process each mandatory metric
        for metric_key, label in self.MANDATORY_METRICS.items():
            if metric_key in extracted_keys:
                item = extracted_items_by_key[metric_key]
                results.append({
                    'metric_key': metric_key,
                    'label': label,
                    'status': 'EXTRACTED',
                    'reason': 'Successfully captured',
                    'source_page': item.get('sourcePage', 0)
                })
            else:
                # Metric is missing. Determine why.
                reason, status = self._determine_missing_reason(metric_key, raw_text)
                results.append({
                    'metric_key': metric_key,
                    'label': label,
                    'status': status,
                    'reason': reason,
                    'source_page': 0
                })
                
        return results

    def _determine_missing_reason(self, metric_key: str, raw_text: str) -> tuple:
        """
        Scan text to see if the metric keywords appear.
        """
        # Get keywords for this metric from terminology database
        keywords = []
        
        # Find term in internal map
        term_data = None
        for term in ALL_TERMS:
            if term.get('id') == metric_key:
                term_data = term
                break
        
        if term_data:
            keywords = term_data.get('keywords', [])
        
        if not keywords:
            # Fallback if terminology db has issues
            keywords = [metric_key.replace('_', ' ')]

        # Search for any keyword in the raw text
        found_in_text = False
        sample_context = ""
        
        for kw in keywords:
            # Use regex for word boundaries
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            match = re.search(pattern, raw_text.lower())
            if match:
                found_in_text = True
                # Capture a bit of context for the reason
                start = max(0, match.start() - 30)
                end = min(len(raw_text), match.end() + 30)
                sample_context = raw_text[start:end].replace('\n', ' ').strip()
                break
        
        if found_in_text:
            return (
                f"Label found in text ('...{sample_context}...') but no valid numeric value could be associated.",
                'NO_VALUE_FOUND'
            )
        else:
            return (
                "Neither the label nor its synonyms were detected in the document text.",
                'NOT_FOUND'
            )

    def get_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary object for the API response."""
        extracted = [r for r in results if r['status'] == 'EXTRACTED']
        return {
            'total_mandatory': len(self.MANDATORY_METRICS),
            'extracted_count': len(extracted),
            'missing_count': len(self.MANDATORY_METRICS) - len(extracted),
            'success_rate': (len(extracted) / len(self.MANDATORY_METRICS)) * 100 if self.MANDATORY_METRICS else 0
        }
