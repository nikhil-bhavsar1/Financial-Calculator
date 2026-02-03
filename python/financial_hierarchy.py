"""
Phase 4: Hierarchical Metric Inference & Validation.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class HierarchyEngine:
    """
    Validates and infers hierarchical relationships in financial data.
    """
    
    # Validation Rules (Phase 4.1)
    VALIDATION_RULES = [
        {
            "parent": "total_assets",
            "children": ["total_non_current_assets", "total_current_assets"],
            "tolerance": 0.02  # 2%
        },
        {
            "parent": "total_equity_and_liabilities",
            "children": ["total_equity", "total_non_current_liabilities", "total_current_liabilities"],
            "tolerance": 0.02
        },
        {
            "parent": "total_revenue",
            "children": ["revenue_from_operations", "other_income"],
             "tolerance": 0.02
        }
    ]

    # Inference Rules (Phase 4.2)
    # Mapping of target <- calc(inputs)
    # This overlaps with MetricsEngine, but intended for LineItem enrichment
    
    def validate_hierarchy(self, items: List[Any]) -> List[Dict]:
        """
        Validate parent-child relationships.
        items: List of FinancialLineItem objects (must have .id and .current_year attributes)
        """
        issues = []
        
        # Convert items to dict for fast lookup
        # Summing duplicates if any (though should be unique IDs ideally)
        data_map = {}
        for item in items:
            if item.id not in data_map:
                data_map[item.id] = 0.0
            data_map[item.id] += float(item.current_year or 0.0)
            
        for rule in self.VALIDATION_RULES:
            parent_key = rule['parent']
            child_keys = rule['children']
            
            if parent_key not in data_map: continue
            
            parent_val = data_map[parent_key]
            
            # Check if we have children
            available_children = [k for k in child_keys if k in data_map]
            if not available_children: continue
            
            # If we expect ALL children to sum up exactly:
            children_sum = sum(data_map[k] for k in available_children)
            
            # If missing some children, exact sum might not be possible, 
            # but if we have ALL, we check tolerance.
            if len(available_children) < len(child_keys):
                # Cannot strictly validate if missing components
                continue
                
            diff = abs(parent_val - children_sum)
            tolerance_val = abs(parent_val * rule['tolerance'])
            
            if diff > tolerance_val and parent_val > 0:
                issues.append({
                    "severity": "warning",
                    "message": f"Hierarchy Mismatch: {parent_key} ({parent_val:,.2f}) != Sum of children ({children_sum:,.2f})",
                    "details": {
                        "parent": parent_key,
                        "parent_val": parent_val,
                        "children_sum": children_sum,
                        "diff": diff
                    }
                })
                
        return issues

    def infer_derived_metrics(self, items: List[Any]):
        """
        Infer missing metrics and add them to the list (Phase 4.2).
        """
        # Create map
        data_map = {}
        for item in items:
            data_map[item.id] = item
            
        new_items = []
        
        # 1. Net Current Assets (Working Capital)
        if 'total_current_assets' in data_map and 'total_current_liabilities' in data_map and 'net_current_assets' not in data_map:
             ca = data_map['total_current_assets']
             cl = data_map['total_current_liabilities']
             
             # Create new item based on existing ones
             val = (ca.current_year or 0) - (cl.current_year or 0)
             prev = (ca.previous_year or 0) - (cl.previous_year or 0)
             
             # Create a clone of CA to reuse metadata
             # Assuming item is a dataclass or similar
             from parser_config import FinancialLineItem
             
             new_item = FinancialLineItem(
                 id='net_current_assets',
                 label='Net Current Assets (Inferred)',
                 current_year=val,
                 previous_year=prev,
                 statement_type=ca.statement_type,
                 reporting_entity=ca.reporting_entity,
                 section=ca.section,
                 is_subtotal=True,
                 raw_line="Inferred from CA - CL"
             )
             new_items.append(new_item)
             
        # Add new items to main list
        items.extend(new_items)
        return items
