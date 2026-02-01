"""
Financial Term Matching System - Synonym Networks & Relationships
=================================================================
Comprehensive synonym networks, parent-child hierarchies, and cross-standard mappings.
"""

from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class RelationshipMapper:
    """
    Manages relationships between financial terms including:
    - Synonym networks
    - Parent-child hierarchies
    - Cross-standard mappings
    """
    
    def __init__(self):
        # Synonym networks - terms that mean the same thing
        self.synonym_networks = {
            'trade_receivables': {
                'synonyms': [
                    'accounts_receivable',
                    'sundry_debtors',
                    'trade_debtors',
                    'receivables_from_customers',
                    'amounts_due_from_customers'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'trade_payables': {
                'synonyms': [
                    'accounts_payable',
                    'sundry_creditors',
                    'trade_creditors',
                    'payables_to_suppliers',
                    'amounts_due_to_suppliers'
                ],
                'category': 'Balance Sheet - Liabilities'
            },
            'inventory': {
                'synonyms': [
                    'stock',
                    'stock_in_trade',
                    'merchandise',
                    'goods',
                    'raw_materials',
                    'work_in_progress',
                    'finished_goods'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'property_plant_equipment': {
                'synonyms': [
                    'ppe',
                    'fixed_assets',
                    'tangible_assets',
                    'plant_property_equipment',
                    'land_buildings_equipment'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'revenue': {
                'synonyms': [
                    'sales',
                    'turnover',
                    'gross_revenue',
                    'total_revenue',
                    'revenue_from_operations',
                    'operating_revenue'
                ],
                'category': 'Income Statement'
            },
            'profit': {
                'synonyms': [
                    'earnings',
                    'income',
                    'gain',
                    'surplus',
                    'net_profit',
                    'profit_for_the_year',
                    'profit_after_tax'
                ],
                'category': 'Income Statement'
            },
            'borrowings': {
                'synonyms': [
                    'loans',
                    'debt',
                    'credit_facilities',
                    'financing',
                    'indebtedness'
                ],
                'category': 'Balance Sheet - Liabilities'
            },
            'equity': {
                'synonyms': [
                    'shareholders_funds',
                    'net_worth',
                    'owners_equity',
                    'shareholders_equity',
                    'capital_and_reserves'
                ],
                'category': 'Balance Sheet - Equity'
            },
            'depreciation': {
                'synonyms': [
                    'amortization',
                    'amortisation',
                    'depletion',
                    'write_down',
                    'impairment'
                ],
                'category': 'Income Statement'
            },
            'cash': {
                'synonyms': [
                    'cash_and_cash_equivalents',
                    'cash_and_bank_balances',
                    'liquid_assets',
                    'cash_on_hand'
                ],
                'category': 'Balance Sheet - Assets'
            },
        }
        
        # Parent-child hierarchies
        self.parent_child_hierarchies = {
            'total_assets': {
                'children': [
                    'total_non_current_assets',
                    'total_current_assets',
                    'assets_held_for_sale'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'total_non_current_assets': {
                'children': [
                    'property_plant_equipment',
                    'capital_work_in_progress',
                    'intangible_assets',
                    'goodwill',
                    'investment_property',
                    'right_of_use_assets',
                    'financial_assets_non_current',
                    'deferred_tax_assets'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'total_current_assets': {
                'children': [
                    'inventories',
                    'trade_receivables',
                    'cash_and_equivalents',
                    'short_term_investments',
                    'other_current_assets'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'property_plant_equipment': {
                'children': [
                    'land_and_buildings',
                    'plant_and_machinery',
                    'furniture_and_fixtures',
                    'vehicles',
                    'office_equipment',
                    'capital_work_in_progress'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'intangible_assets': {
                'children': [
                    'goodwill',
                    'software',
                    'patents',
                    'trademarks',
                    'copyrights',
                    'licenses',
                    'customer_relationships'
                ],
                'category': 'Balance Sheet - Assets'
            },
            'total_liabilities': {
                'children': [
                    'total_non_current_liabilities',
                    'total_current_liabilities'
                ],
                'category': 'Balance Sheet - Liabilities'
            },
            'total_non_current_liabilities': {
                'children': [
                    'long_term_borrowings',
                    'deferred_tax_liabilities',
                    'long_term_provisions',
                    'other_non_current_liabilities'
                ],
                'category': 'Balance Sheet - Liabilities'
            },
            'total_current_liabilities': {
                'children': [
                    'short_term_borrowings',
                    'trade_payables',
                    'short_term_provisions',
                    'other_current_liabilities'
                ],
                'category': 'Balance Sheet - Liabilities'
            },
            'total_equity': {
                'children': [
                    'share_capital',
                    'reserves_and_surplus',
                    'retained_earnings',
                    'other_comprehensive_income',
                    'non_controlling_interest'
                ],
                'category': 'Balance Sheet - Equity'
            },
            'reserves_and_surplus': {
                'children': [
                    'capital_reserve',
                    'securities_premium',
                    'general_reserve',
                    'retained_earnings',
                    'statutory_reserve'
                ],
                'category': 'Balance Sheet - Equity'
            },
            'total_revenue': {
                'children': [
                    'revenue_from_operations',
                    'other_income'
                ],
                'category': 'Income Statement'
            },
            'total_expenses': {
                'children': [
                    'cost_of_materials_consumed',
                    'purchases_of_stock_in_trade',
                    'changes_in_inventories',
                    'employee_benefits_expense',
                    'finance_costs',
                    'depreciation_and_amortization',
                    'other_expenses'
                ],
                'category': 'Income Statement'
            },
        }
        
        # Cross-standard mappings (IndAS, GAAP, IFRS)
        self.cross_standard_mappings = {
            # Revenue recognition
            'IndAS 115': {
                'gaap': ['ASC 606'],
                'ifrs': ['IFRS 15'],
                'terms': [
                    'contract_assets',
                    'contract_liabilities',
                    'performance_obligations',
                    'transaction_price'
                ]
            },
            # Leases
            'IndAS 116': {
                'gaap': ['ASC 842'],
                'ifrs': ['IFRS 16'],
                'terms': [
                    'right_of_use_assets',
                    'lease_liabilities',
                    'rou_assets'
                ]
            },
            # Financial instruments
            'IndAS 109': {
                'gaap': ['ASC 320', 'ASC 325', 'ASC 815'],
                'ifrs': ['IFRS 9'],
                'terms': [
                    'financial_assets_fvtpl',
                    'financial_assets_fvtoci',
                    'financial_assets_amortized_cost',
                    'expected_credit_loss'
                ]
            },
            # Revenue (old)
            'IndAS 18': {
                'gaap': ['ASC 605'],
                'ifrs': ['IAS 18'],
                'terms': [
                    'revenue_from_sale_of_goods',
                    'revenue_from_rendering_of_services'
                ]
            },
            # PPE
            'IndAS 16': {
                'gaap': ['ASC 360'],
                'ifrs': ['IAS 16'],
                'terms': [
                    'property_plant_equipment',
                    'depreciation',
                    'useful_life',
                    'residual_value'
                ]
            },
            # Intangibles
            'IndAS 38': {
                'gaap': ['ASC 350'],
                'ifrs': ['IAS 38'],
                'terms': [
                    'intangible_assets',
                    'amortization',
                    'research_and_development'
                ]
            },
            # Business combinations
            'IndAS 103': {
                'gaap': ['ASC 805'],
                'ifrs': ['IFRS 3'],
                'terms': [
                    'goodwill',
                    'purchase_consideration',
                    'fair_value_adjustments'
                ]
            },
            # Consolidation
            'IndAS 110': {
                'gaap': ['ASC 810'],
                'ifrs': ['IFRS 10'],
                'terms': [
                    'non_controlling_interest',
                    'control',
                    'subsidiary'
                ]
            },
        }
        
        # Build reverse lookup maps
        self._build_reverse_maps()
    
    def _build_reverse_maps(self):
        """Build reverse lookup maps for efficient searching."""
        # Reverse synonym map
        self.synonym_to_canonical = {}
        for canonical, data in self.synonym_networks.items():
            for synonym in data['synonyms']:
                self.synonym_to_canonical[synonym] = canonical
        
        # Reverse parent-child map
        self.child_to_parent = {}
        for parent, data in self.parent_child_hierarchies.items():
            for child in data['children']:
                self.child_to_parent[child] = parent
        
        # Term to standard map
        self.term_to_standards = defaultdict(list)
        for indas_std, data in self.cross_standard_mappings.items():
            for term in data['terms']:
                self.term_to_standards[term].append({
                    'indas': indas_std,
                    'gaap': data['gaap'],
                    'ifrs': data['ifrs']
                })
    
    def get_synonyms(self, term_key: str) -> List[str]:
        """
        Get all synonyms for a term.
        
        Args:
            term_key: Term to look up
            
        Returns:
            List of synonyms
        """
        if term_key in self.synonym_networks:
            return self.synonym_networks[term_key]['synonyms']
        
        # Check if it's a synonym of something else
        if term_key in self.synonym_to_canonical:
            canonical = self.synonym_to_canonical[term_key]
            return self.synonym_networks[canonical]['synonyms']
        
        return []
    
    def get_canonical_term(self, synonym: str) -> Optional[str]:
        """
        Get canonical term for a synonym.
        
        Args:
            synonym: Synonym to look up
            
        Returns:
            Canonical term or None
        """
        return self.synonym_to_canonical.get(synonym)
    
    def get_children(self, parent_term: str) -> List[str]:
        """
        Get child terms for a parent.
        
        Args:
            parent_term: Parent term key
            
        Returns:
            List of child term keys
        """
        if parent_term in self.parent_child_hierarchies:
            return self.parent_child_hierarchies[parent_term]['children']
        return []
    
    def get_parent(self, child_term: str) -> Optional[str]:
        """
        Get parent term for a child.
        
        Args:
            child_term: Child term key
            
        Returns:
            Parent term key or None
        """
        return self.child_to_parent.get(child_term)
    
    def get_all_parents(self, term_key: str) -> List[str]:
        """
        Get all parent terms up to root.
        
        Args:
            term_key: Term to look up
            
        Returns:
            List of parent terms (immediate to root)
        """
        parents = []
        current = term_key
        
        while current in self.child_to_parent:
            parent = self.child_to_parent[current]
            parents.append(parent)
            current = parent
        
        return parents
    
    def get_related_standards(self, term_key: str) -> List[Dict]:
        """
        Get accounting standards related to a term.
        
        Args:
            term_key: Term to look up
            
        Returns:
            List of standard mappings
        """
        return self.term_to_standards.get(term_key, [])
    
    def get_equivalent_terms_across_standards(
        self, 
        term_key: str,
        target_standard: str
    ) -> List[str]:
        """
        Get equivalent term names in another accounting standard.
        
        Args:
            term_key: Source term
            target_standard: Target standard ('gaap' or 'ifrs')
            
        Returns:
            List of equivalent terms
        """
        equivalents = []
        
        # Check cross-standard mappings
        for indas_std, data in self.cross_standard_mappings.items():
            if term_key in data['terms']:
                if target_standard in data:
                    equivalents.extend(data[target_standard])
        
        return equivalents
    
    def should_prefer_child_over_parent(
        self, 
        child_term: str, 
        parent_term: str,
        context: Optional[Dict] = None
    ) -> bool:
        """
        Determine if child term should be preferred over parent.
        
        Args:
            child_term: Child term key
            parent_term: Parent term key
            context: Optional context information
            
        Returns:
            True if child should be preferred
        """
        # Check if valid parent-child relationship
        actual_parent = self.get_parent(child_term)
        if actual_parent != parent_term:
            return False
        
        # Check for "Total" prefix in context
        if context and 'text' in context:
            text = context['text'].lower()
            if 'total' in text and parent_term.startswith('total_'):
                # Keep parent if it's a total line
                return False
        
        # Default: prefer more specific (child) terms
        return True
    
    def get_term_specificity_score(self, term_key: str) -> int:
        """
        Get specificity score for a term (higher = more specific).
        
        Args:
            term_key: Term to score
            
        Returns:
            Specificity score
        """
        score = 0
        
        # Base score on depth in hierarchy
        parents = self.get_all_parents(term_key)
        score += len(parents) * 10
        
        # Bonus for having children
        children = self.get_children(term_key)
        if not children:
            score += 5  # Leaf nodes are most specific
        
        return score
    
    def find_related_terms(self, term_key: str, max_distance: int = 2) -> List[str]:
        """
        Find all related terms within a relationship distance.
        
        Args:
            term_key: Starting term
            max_distance: Maximum relationship distance
            
        Returns:
            List of related term keys
        """
        related = set()
        visited = {term_key}
        queue = [(term_key, 0)]
        
        while queue:
            current, distance = queue.pop(0)
            
            if distance >= max_distance:
                continue
            
            # Get synonyms
            for synonym in self.get_synonyms(current):
                if synonym not in visited:
                    visited.add(synonym)
                    related.add(synonym)
                    queue.append((synonym, distance + 1))
            
            # Get parent
            parent = self.get_parent(current)
            if parent and parent not in visited:
                visited.add(parent)
                related.add(parent)
                queue.append((parent, distance + 1))
            
            # Get children
            for child in self.get_children(current):
                if child not in visited:
                    visited.add(child)
                    related.add(child)
                    queue.append((child, distance + 1))
        
        return list(related)
    
    def generate_relationship_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive relationship report.
        
        Returns:
            Report dictionary
        """
        return {
            'synonym_networks': {
                'total_networks': len(self.synonym_networks),
                'total_synonyms': sum(
                    len(data['synonyms']) 
                    for data in self.synonym_networks.values()
                ),
                'networks': [
                    {
                        'canonical': canonical,
                        'synonym_count': len(data['synonyms']),
                        'category': data['category']
                    }
                    for canonical, data in self.synonym_networks.items()
                ]
            },
            'parent_child_hierarchies': {
                'total_parents': len(self.parent_child_hierarchies),
                'total_children': sum(
                    len(data['children'])
                    for data in self.parent_child_hierarchies.values()
                ),
                'max_depth': max(
                    len(self.get_all_parents(child))
                    for child in self.child_to_parent.keys()
                ) if self.child_to_parent else 0,
                'hierarchies': [
                    {
                        'parent': parent,
                        'child_count': len(data['children']),
                        'category': data['category']
                    }
                    for parent, data in self.parent_child_hierarchies.items()
                ]
            },
            'cross_standard_mappings': {
                'total_mappings': len(self.cross_standard_mappings),
                'standards_covered': {
                    'indas': len(self.cross_standard_mappings),
                    'gaap': sum(len(data['gaap']) for data in self.cross_standard_mappings.values()),
                    'ifrs': sum(len(data['ifrs']) for data in self.cross_standard_mappings.values()),
                },
                'mappings': [
                    {
                        'indas': indas_std,
                        'gaap': data['gaap'],
                        'ifrs': data['ifrs'],
                        'term_count': len(data['terms'])
                    }
                    for indas_std, data in self.cross_standard_mappings.items()
                ]
            }
        }


# Convenience functions
def get_term_synonyms(term_key: str) -> List[str]:
    """Quick function to get synonyms for a term."""
    mapper = RelationshipMapper()
    return mapper.get_synonyms(term_key)


def get_term_parent(term_key: str) -> Optional[str]:
    """Quick function to get parent of a term."""
    mapper = RelationshipMapper()
    return mapper.get_parent(term_key)


def get_related_terms(term_key: str, max_distance: int = 2) -> List[str]:
    """Quick function to get related terms."""
    mapper = RelationshipMapper()
    return mapper.find_related_terms(term_key, max_distance)
