#!/usr/bin/env python3
"""
Script to normalize keywords in py_lib to match terminology database
Uses AST for safe transformation
"""

import ast
import os
import json
from typing import Dict, List, Optional

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

# Create comprehensive normalization mapping
def create_normalization_mapping(database: Dict) -> Dict[str, str]:
    """Create mapping from current keywords to canonical term keys."""

    # Manual corrections for py_lib - carefully selected to ensure formula correctness
    manual_corrections = {
        # Income Statement - Core Items
        'revenue': 'total_revenue',
        'net_sales': 'total_revenue',
        'sales': 'total_revenue',
        'cogs': 'cost_of_goods_sold',
        'cost_of_goods_sold': 'cost_of_goods_sold',
        'ebit': 'operating_profit',
        'operating_income': 'operating_profit',
        'net_income': 'profit_for_the_year',
        'earnings_before_tax': 'profit_before_tax',
        'pbt': 'profit_before_tax',
        'net_profit': 'profit_after_tax',
        'pat': 'profit_after_tax',
        'profit_after_tax': 'profit_after_tax',
        'earnings_per_share': 'earnings_per_share_basic',
        'eps': 'earnings_per_share_basic',
        'ebitda': 'ebitda',

        # Balance Sheet - Core Items
        'current_assets': 'total_current_assets',
        'current_liabilities': 'total_current_liabilities',
        'total_equity': 'total_equity',
        'shareholders_equity': 'total_equity',
        'share_capital': 'share_capital',
        'retained_earnings': 'retained_earnings',
        'property_plant_equipment': 'property_plant_equipment',
        'ppe': 'property_plant_equipment',
        'fixed_assets': 'property_plant_equipment',
        'total_assets': 'total_assets',
        'total_liabilities': 'total_liabilities',

        # Specific Asset/Liability Items
        'accounts_receivable': 'trade_receivables',
        'trade_receivables': 'trade_receivables',
        'accounts_payable': 'trade_payables',
        'trade_payables': 'trade_payables',
        'inventory': 'inventories',
        'inventories': 'inventories',
        # Keep cash and cash_equivalents separate when they appear together
        # 'cash': 'cash_and_equivalents',  # Don't rename to avoid duplicates
        'cash_and_cash_equivalents': 'cash_and_equivalents',
        # 'cash_equivalents': 'cash_and_equivalents',  # Don't rename to avoid duplicates
        'marketable_securities': 'short_term_investments',

        # Debt & Finance
        'long_term_debt': 'long_term_borrowings',
        'short_term_debt': 'short_term_borrowings',
        'borrowings': 'total_borrowings',
        'loans': 'total_borrowings',
        'total_debt': 'total_borrowings',
        'interest': 'finance_cost',
        'interest_expense': 'finance_cost',
        'finance_cost': 'finance_cost',
        'taxes': 'tax_expense',
        'tax_expense': 'tax_expense',
        'tax_rate': 'tax_rate',

        # Cash Flow - Keep depreciation and amortization separate to avoid duplicate parameters
        'depreciation_and_amortization': 'depreciation_amortization',
        'capital_expenditures': 'capital_expenditure',
        'capex': 'capital_expenditure',
        'capital_expenditure': 'capital_expenditure',
        'operating_cash_flow': 'net_cash_from_operating_activities',
        'cfo': 'net_cash_from_operating_activities',
        'ocf': 'net_cash_from_operating_activities',

        # Market
        'market_cap': 'market_capitalization',
        'market_capitalization': 'market_capitalization',
        'shares_outstanding': 'number_of_shares',
        'share_price': 'share_price',
        'enterprise_value': 'enterprise_value',
        'ev': 'enterprise_value',
        'book_value': 'book_value',

        # Special cases - preserve these as they may be specific
        'operating_expenses': 'operating_expenses',
        'total_expenses': 'total_expenses',
        'minority_interest': 'non_controlling_interest',
    }

    # Add exact keys from database
    keyword_mapping = {}
    for term in database.get('terms', []):
        term_key = term.get('key', '')
        keyword_mapping[term_key] = term_key

    # Manual corrections take precedence
    keyword_mapping.update(manual_corrections)

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

            # Check if the new name would create a duplicate
            if new_name in used_new_names:
                # Keep the old name to avoid duplicate
                param_map_local[old_name] = old_name
                new_name = old_name
            else:
                param_map_local[old_name] = new_name
                used_new_names.add(new_name)

            new_arg = ast.arg(arg=new_name, annotation=arg.annotation)
            new_args.append(new_arg)

        # Store for this function
        self.current_function_params[node.name] = param_map_local

        node.args.args = new_args

        # Process function body with local mapping
        # Visit children
        self.generic_visit(node)

        # Clean up after processing this function
        self.current_function_params.pop(node.name, None)

        return node

    def visit_Name(self, node: ast.Name):
        # Rename variable names that match parameters
        # Only rename if it's likely a parameter (simple name, not attribute)
        # Check if it's a parameter of the current function
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

    # Preserve original comments and docstrings better
    # Simple approach: compare and merge where possible
    # For now, use the AST-generated version but ensure it's valid

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

import sys

def main():
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
    sys.exit(main())
