#!/usr/bin/env python3
"""
Script to normalize keywords in py_lib to match terminology database
Uses AST for safe transformation with conservative approach
"""

import ast
import os
import json
from typing import Dict, List, Optional, Set

# Load terminology database
def load_database():
    """Load terms database."""
    possible_paths = [
        'python/terms_database.json',
        'terms_database.json',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

# Create conservative normalization mapping
def create_normalization_mapping(database: Dict) -> Dict[str, str]:
    """Create mapping from current keywords to canonical term keys."""

    # Manual, carefully curated corrections for py_lib
    # These are selected to ensure formula correctness while using canonical terms
    # NOTE: Very conservative approach - only rename when clearly correct

    manual_corrections = {
        # Income Statement - Core Items
        'net_sales': 'total_revenue',
        'revenue': 'total_revenue',
        'ebit': 'operating_profit',
        'operating_income': 'operating_profit',
        'net_income': 'profit_for_the_year',
        'earnings_before_tax': 'profit_before_tax',
        'pbt': 'profit_before_tax',
        'net_profit': 'profit_after_tax',
        'pat': 'profit_after_tax',
        'earnings_per_share': 'earnings_per_share_basic',
        'eps': 'earnings_per_share_basic',

        # Balance Sheet - Core Items
        'shareholders_equity': 'total_equity',
        'property_plant_equipment': 'property_plant_equipment',
        'ppe': 'property_plant_equipment',
        'fixed_assets': 'property_plant_equipment',

        # Specific Asset/Liability Items
        'accounts_receivable': 'trade_receivables',
        'accounts_payable': 'trade_payables',

        # Debt & Finance
        'long_term_debt': 'long_term_borrowings',
        'short_term_debt': 'short_term_borrowings',
        'loans': 'total_borrowings',
        'total_debt': 'total_borrowings',
        'interest': 'finance_cost',
        'interest_expense': 'finance_cost',
        'taxes': 'tax_expense',

        # Cash Flow abbreviations
        'cfo': 'net_cash_from_operating_activities',
        'ocf': 'net_cash_from_operating_activities',

        # Market
        'market_cap': 'market_capitalization',
        'shares_outstanding': 'number_of_shares',
        'minority_interest': 'non_controlling_interest',
    }

    # These should NOT be renamed to preserve formula correctness
    preserve_names = {
        # Keep as-is - these are specific line items
        'cogs', 'cost_of_goods_sold',  # COGS is specific term
        'inventory', 'inventories',  # Both are valid
        'cash', 'cash_equivalents', 'cash_and_equivalents',  # Different components
        'current_assets', 'total_current_assets',  # Context-dependent
        'current_liabilities', 'total_current_liabilities',  # Context-dependent
        'operating_expenses', 'total_expenses',  # These are valid terms
        'depreciation', 'amortization',  # Keep separate for formulas
        'capital_expenditures', 'capex', 'capital_expenditure',  # Keep variations
        'borrowings', 'total_borrowings',  # Valid term
        'total_revenue',  # Already canonical
        'ebitda',  # Already canonical
        'total_assets', 'total_equity', 'total_liabilities',  # Already canonical
        'share_capital', 'retained_earnings',  # Already canonical
        'trade_receivables', 'trade_payables',  # Already canonical
        'finance_cost', 'tax_expense',  # Already canonical
        'market_capitalization', 'enterprise_value', 'book_value',  # Already canonical
    }

    # Build mapping
    keyword_mapping = {}

    # Add manual corrections (except those to preserve)
    for old_name, new_name in manual_corrections.items():
        if old_name not in preserve_names:
            keyword_mapping[old_name] = new_name

    return keyword_mapping

class ParameterRenamer(ast.NodeTransformer):
    """AST transformer to rename function parameters and their usage."""

    def __init__(self, param_mapping: Dict[str, str]):
        self.param_mapping = param_mapping
        self.current_function_params = {}  # Track current function's parameter renames

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Process parameters
        new_args = []
        param_map_local = {}  # Local mapping for this function
        used_new_names = set()  # Track which new names are already used

        for arg in node.args.args:
            old_name = arg.arg
            new_name = self.param_mapping.get(old_name, old_name)

            # Check if new name would create a duplicate
            if new_name in used_new_names:
                # Keep old name to avoid duplicate - DON'T RENAME
                param_map_local[old_name] = old_name
                used_new_names.add(old_name)
            else:
                param_map_local[old_name] = new_name
                used_new_names.add(new_name)

            new_arg = ast.arg(arg=new_name, annotation=arg.annotation)
            new_args.append(new_arg)

        # Only update if there are actual renames
        if new_args != node.args.args:
            node.args.args = new_args
            self.current_function_params[node.name] = param_map_local

        # Process function body with local mapping
        self.generic_visit(node)

        # Clean up after processing this function
        self.current_function_params.pop(node.name, None)

        return node

    def visit_Name(self, node: ast.Name):
        # Rename variable names that match parameters
        for func_name, param_map in self.current_function_params.items():
            if node.id in param_map:
                node.id = param_map[node.id]
                return node
        return node

def normalize_py_lib_file(file_path: str, mapping: Dict[str, str], dry_run: bool = True):
    """Normalize keywords in a py_lib file using AST."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try to parse
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"  ERROR: Could not parse {file_path}: {e}")
        return []

    # Track which parameters will be renamed
    param_renamings = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                old_name = arg.arg
                new_name = mapping.get(old_name, old_name)
                if old_name != new_name:
                    if node.name not in param_renamings:
                        param_renamings[node.name] = {}
                    param_renamings[node.name][old_name] = new_name

    if not param_renamings:
        return []

    # Apply transformations
    renamer = ParameterRenamer(mapping)
    new_tree = renamer.visit(tree)
    ast.fix_missing_locations(new_tree)

    # Generate new code
    new_content = ast.unparse(new_tree)

    if dry_run:
        print(f"DRY RUN - Would update: {file_path}")
        for func_name, renames in param_renamings.items():
            print(f"  Function: {func_name}")
            print(f"  Renames: {renames}")
        return param_renamings
    else:
        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")
        for func_name, renames in param_renamings.items():
            print(f"  Function: {func_name}")
            print(f"  Renames: {renames}")
        return param_renamings

def main():
    import sys
    database = load_database()
    if not database:
        print("Error: Could not load terms database")
        return 1

    mapping = create_normalization_mapping(database)
    print(f"Created normalization mapping with {len(mapping)} entries")

    py_lib_dir = 'py_lib'
    if not os.path.exists(py_lib_dir):
        print(f"Error: py_lib directory not found: {py_lib_dir}")
        return 1

    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv

    if dry_run:
        print("Running in DRY RUN mode - no files will be modified")
    else:
        print("Running in LIVE mode - files will be modified")

    total_functions = 0
    files_processed = 0

    for filename in sorted(os.listdir(py_lib_dir)):
        if filename.endswith('.py') and not filename.startswith('_'):
            file_path = os.path.join(py_lib_dir, filename)
            print(f"\nProcessing: {filename}")

            try:
                renames = normalize_py_lib_file(file_path, mapping, dry_run=dry_run)
                if renames:
                    total_functions += len(renames)
                    files_processed += 1
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Total files with changes: {files_processed}")
    print(f"Total functions changed: {total_functions}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
