"""
Phase 3: GAAP-Aware Validation.

Implements jurisdiction-specific accounting rules:
- US GAAP: Impairment reversal FORBIDDEN
- Ind AS (IFRS): Impairment reversal ALLOWED
- Lease treatment differences
- Revenue recognition variations
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum

try:
    from ind_as_config import IND_AS_MANDATORY_SCHEDULES
except ImportError:
    IND_AS_MANDATORY_SCHEDULES = {}

logger = logging.getLogger(__name__)

# =============================================================================
# GAAP Types
# =============================================================================

class GAAPType(Enum):
    """Accounting standard types."""
    US_GAAP = "us_gaap"
    IND_AS = "ind_as"
    IFRS = "ifrs"
    UNKNOWN = "unknown"

# =============================================================================
# GAAP Detection
# =============================================================================

GAAP_INDICATORS = {
    GAAPType.US_GAAP: [
        r'\bUS\s*GAAP\b',
        r'\bASC\s+\d{3}',  # ASC 606, ASC 842
        r'\bFASB\b',
        r'\bSEC\s+(?:Form|Filing)',
        r'\b10-K\b',
        r'\b10-Q\b',
        r'\b20-F\b',
    ],
    GAAPType.IND_AS: [
        r'\bInd\s*AS\b',
        r'\bIndian\s+Accounting\s+Standard',
        r'\bSchedule\s+III\b',
        r'\bCompanies\s+Act,?\s+2013\b',
        r'\bMCA\b',
        r'\bSEBI\b',
    ],
    GAAPType.IFRS: [
        r'\bIFRS\b',
        r'\bInternational\s+Financial\s+Reporting',
        r'\bIAS\s+\d+',
    ],
}

def detect_gaap_type(text: str) -> Tuple[GAAPType, float]:
    """
    Detect the GAAP framework from document text.
    Returns (GAAPType, confidence).
    """
    text_sample = text[:10000]  # First 10k chars
    
    scores = {gtype: 0 for gtype in GAAPType if gtype != GAAPType.UNKNOWN}
    
    for gtype, patterns in GAAP_INDICATORS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text_sample, re.IGNORECASE)
            scores[gtype] += len(matches) * 10
    
    max_score = max(scores.values())
    if max_score >= 10:
        winner = max(scores, key=scores.get)
        confidence = min(max_score / 50, 1.0)
        return winner, confidence
    
    return GAAPType.UNKNOWN, 0.0

# =============================================================================
# Validation Rules
# =============================================================================

@dataclass
class ValidationIssue:
    """Represents a GAAP validation issue found in extracted data."""
    severity: str  # 'error', 'warning', 'info'
    rule_id: str
    message: str
    metric_key: Optional[str] = None
    value: Optional[float] = None
    suggested_action: Optional[str] = None

class GAAPValidator:
    """
    Validates extracted financial data against GAAP-specific rules.
    """
    
    def __init__(self, gaap_type: GAAPType = GAAPType.UNKNOWN):
        self.gaap_type = gaap_type
        self.issues: List[ValidationIssue] = []
    
    def set_gaap_type(self, gaap_type: GAAPType):
        """Set the GAAP framework for validation."""
        self.gaap_type = gaap_type
        logger.info(f"GAAP validator set to: {gaap_type.value}")
    
    def validate(self, metrics: Dict[str, float], raw_text: str = "") -> List[ValidationIssue]:
        """
        Run all validation rules on extracted metrics.
        
        Args:
            metrics: Dict of metric_key -> value
            raw_text: Original document text for context checks
            
        Returns:
            List of ValidationIssues found
        """
        self.issues = []
        
        # Run universal rules
        self._check_balance_sheet_equation(metrics)
        self._check_negative_values(metrics)
        
        # Run GAAP-specific rules
        if self.gaap_type == GAAPType.US_GAAP:
            self._check_us_gaap_impairment(metrics, raw_text)
            self._check_us_gaap_lease(metrics)
        elif self.gaap_type in [GAAPType.IND_AS, GAAPType.IFRS]:
            self._check_ind_as_impairment(metrics, raw_text)
            self._check_ind_as_lease(metrics)
            if self.gaap_type == GAAPType.IND_AS:
                self._check_ind_as_mandatory_items(metrics)
        
        return self.issues
    
    # =========================================================================
    # Universal Rules
    # =========================================================================
    
    def _check_balance_sheet_equation(self, metrics: Dict[str, float]):
        """Check Assets = Liabilities + Equity."""
        assets = metrics.get('total_assets', 0)
        liabilities = metrics.get('total_liabilities', 0)
        equity = metrics.get('total_equity', 0)
        
        if assets and (liabilities or equity):
            expected = liabilities + equity
            diff = abs(assets - expected)
            tolerance = abs(assets) * 0.02  # 2% tolerance
            
            if diff > tolerance and assets > 0:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    rule_id='BAL_EQ_01',
                    message=f"Balance sheet equation mismatch: Assets ({assets:,.0f}) != Liabilities ({liabilities:,.0f}) + Equity ({equity:,.0f})",
                    suggested_action="Check for missing liabilities or equity components"
                ))
    
    def _check_negative_values(self, metrics: Dict[str, float]):
        """Flag unexpected negative values."""
        should_be_positive = [
            'total_assets', 'total_current_assets', 'inventories',
            'total_revenue', 'revenue_from_operations',
        ]
        
        for key in should_be_positive:
            value = metrics.get(key)
            if value is not None and value < 0:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    rule_id='NEG_VAL_01',
                    message=f"Unexpected negative value for {key}: {value:,.0f}",
                    metric_key=key,
                    value=value,
                    suggested_action="Verify sign convention in source document"
                ))
    
    # =========================================================================
    # US GAAP Specific Rules
    # =========================================================================
    
    def _check_us_gaap_impairment(self, metrics: Dict[str, float], raw_text: str):
        """
        US GAAP: Impairment reversals are FORBIDDEN (ASC 360).
        Check for any signs of impairment reversal in the data.
        """
        # Check for impairment reversal keywords in text
        reversal_patterns = [
            r'impairment\s+reversal',
            r'reversal\s+of\s+impairment',
            r'impairment\s+(?:loss\s+)?recovered',
            r'write[-\s]?back\s+of\s+impairment',
        ]
        
        for pattern in reversal_patterns:
            if re.search(pattern, raw_text, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='error',
                    rule_id='US_GAAP_IMPAIRMENT_01',
                    message="Impairment reversal detected in US GAAP filing. This is PROHIBITED under ASC 360.",
                    suggested_action="Remove impairment reversal item - not allowed under US GAAP"
                ))
                break
        
        # Check for positive impairment_reversal metric if extracted
        if metrics.get('impairment_reversal', 0) > 0:
            self.issues.append(ValidationIssue(
                severity='error',
                rule_id='US_GAAP_IMPAIRMENT_02',
                message=f"Impairment reversal value captured ({metrics['impairment_reversal']:,.0f}) but US GAAP prohibits reversals.",
                metric_key='impairment_reversal',
                value=metrics['impairment_reversal'],
                suggested_action="Exclude this metric for US GAAP filings"
            ))
    
    def _check_us_gaap_lease(self, metrics: Dict[str, float]):
        """US GAAP ASC 842 lease checks."""
        # Under ASC 842, operating leases create ROU assets and lease liabilities
        # Check for consistency
        rou_asset = metrics.get('right_of_use_assets', 0)
        lease_liability = metrics.get('lease_liabilities', 0)
        
        if rou_asset > 0 and lease_liability == 0:
            self.issues.append(ValidationIssue(
                severity='warning',
                rule_id='US_GAAP_LEASE_01',
                message="ROU Asset found but no Lease Liability captured",
                suggested_action="Check for missing lease liability extraction"
            ))
    
    # =========================================================================
    # Ind AS / IFRS Specific Rules
    # =========================================================================
    
    def _check_ind_as_impairment(self, metrics: Dict[str, float], raw_text: str):
        """
        Ind AS: Impairment reversals ARE allowed (IAS 36 / Ind AS 36).
        Flag if present but don't error.
        """
        reversal_patterns = [
            r'impairment\s+reversal',
            r'reversal\s+of\s+impairment',
            r'write[-\s]?back',
        ]
        
        for pattern in reversal_patterns:
            if re.search(pattern, raw_text, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='info',
                    rule_id='IND_AS_IMP_01',
                    message="Impairment reversal detected - allowed under Ind AS/IFRS",
                    suggested_action="Ensure reversal is captured as positive income adjustment"
                ))
                break
    
    def _check_ind_as_lease(self, metrics: Dict[str, float]):
        """Ind AS 116 lease checks (similar to IFRS 16)."""
        # Under Ind AS 116, all leases (except short-term/low-value) are on-balance-sheet
        rou_asset = metrics.get('right_of_use_assets', 0)
        lease_liability = metrics.get('lease_liabilities', 0)
        
        if rou_asset > 0 and lease_liability == 0:
            self.issues.append(ValidationIssue(
                severity='warning',
                rule_id='IND_AS_LEASE_01',
                message="ROU Asset found but no Lease Liability captured under Ind AS 116",
                suggested_action="Check for missing lease liability in current/non-current liabilities"
            ))

    def _check_ind_as_mandatory_items(self, metrics: Dict[str, float]):
        """Check for presence of mandatory Ind AS line items (Schedule III)."""
        if not IND_AS_MANDATORY_SCHEDULES:
            return

        # Check PL items
        pl_items = IND_AS_MANDATORY_SCHEDULES.get('statement_of_profit_loss', [])

        # We can't check ALL as some might be 0, but we should check KEY ones
        critical_ind_as_keys = [
            'revenue_from_operations', 
            'profit_before_tax', 
            'finance_costs',
            'depreciation_and_amortization'
        ]
        
        for key in critical_ind_as_keys:
             if key in pl_items and key not in metrics:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    rule_id='IND_AS_MISSING_ITEM',
                    message=f"Mandatory Ind AS line item '{key}' matches missing or unextracted data.",
                    metric_key=key,
                    suggested_action="Verify OCR quality or term mapping for this specific Ind AS line item."
                ))

# =============================================================================
# Cross-GAAP Normalization
# =============================================================================

class CrossGAAPNormalizer:
    """
    Normalizes financial data across different GAAP frameworks.
    Useful for comparing US subsidiary (US GAAP) vs Indian parent (Ind AS).
    """
    
    @staticmethod
    def normalize_to_common(
        metrics: Dict[str, float],
        source_gaap: GAAPType,
        target_gaap: GAAPType = GAAPType.IFRS
    ) -> Dict[str, float]:
        """
        Normalize metrics from source GAAP to a common basis (default IFRS).
        
        Note: This is a simplified normalization. Real cross-GAAP reconciliation
        requires detailed adjustments for:
        - Revenue recognition timing
        - Lease classification
        - Impairment testing methodology
        - Stock-based compensation
        """
        normalized = metrics.copy()
        
        if source_gaap == GAAPType.US_GAAP and target_gaap in [GAAPType.IFRS, GAAPType.IND_AS]:
            # US GAAP -> IFRS/Ind AS adjustments
            
            # Remove any captured impairment reversals (shouldn't exist under US GAAP anyway)
            if 'impairment_reversal' in normalized:
                del normalized['impairment_reversal']
            
            # Note: Add revenue recognition adjustments here if needed
            # IFRS 15 vs ASC 606 are largely converged, but timing differences exist
            
        elif source_gaap in [GAAPType.IND_AS, GAAPType.IFRS] and target_gaap == GAAPType.US_GAAP:
            # IFRS/Ind AS -> US GAAP adjustments
            
            # Impairment reversals must be removed for US GAAP
            reversal = normalized.get('impairment_reversal', 0)
            if reversal > 0:
                # Adjust net income by removing the reversal benefit
                if 'profit_for_the_year' in normalized:
                    normalized['profit_for_the_year'] -= reversal
                normalized['impairment_reversal'] = 0
        
        return normalized
    
    @staticmethod
    def generate_reconciliation_report(
        us_gaap_metrics: Dict[str, float],
        ind_as_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Generate a reconciliation report comparing US GAAP and Ind AS metrics.
        Useful for 20-F vs Indian subsidiary comparison.
        """
        report = []
        
        all_keys = set(us_gaap_metrics.keys()) | set(ind_as_metrics.keys())
        
        for key in sorted(all_keys):
            us_val = us_gaap_metrics.get(key)
            ind_val = ind_as_metrics.get(key)
            
            diff = None
            diff_pct = None
            
            if us_val is not None and ind_val is not None:
                diff = ind_val - us_val
                if us_val != 0:
                    diff_pct = (diff / abs(us_val)) * 100
            
            report.append({
                'metric': key,
                'us_gaap': us_val,
                'ind_as': ind_val,
                'difference': diff,
                'diff_percent': diff_pct,
                'status': 'match' if diff_pct is not None and abs(diff_pct) < 1 else 'differs'
            })
        
        return report


if __name__ == "__main__":
    # Quick test
    print("GAAP Validator loaded")
    
    # Test GAAP detection
    sample_text = "This 10-K filing is prepared in accordance with US GAAP and ASC 606 revenue recognition."
    gtype, conf = detect_gaap_type(sample_text)
    print(f"Detected GAAP: {gtype.value} (confidence: {conf:.2f})")
    
    # Test validation
    validator = GAAPValidator(gtype)
    test_metrics = {
        'total_assets': 1000000,
        'total_liabilities': 600000,
        'total_equity': 400000,
        'total_revenue': 500000,
    }
    issues = validator.validate(test_metrics, sample_text)
    print(f"Validation issues: {len(issues)}")
