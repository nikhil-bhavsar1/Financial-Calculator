#!/usr/bin/env python3
"""
Script to normalize keywords in py_lib to match terminology database
"""

import re
import os
import json
from typing import Dict, List, Set, Tuple
import sys

# Load terminology database
def load_database():
    """Load terms database."""
    possible_paths = [
        'python/terms_database.json',
        'terms_database.json',
        os.path.join(os.path.dirname(__file__), 'python/terms_database.json'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

# Create comprehensive normalization mapping
def create_normalization_mapping(database: Dict) -> Dict[str, str]:
    """Create mapping from current keywords to canonical term keys."""

    # Build mapping from database
    keyword_mapping = {}
    for term in database.get('terms', []):
        term_key = term.get('key', '')
        # Add exact key match
        keyword_mapping[term_key] = term_key

        # Add keyword matches
        for kw in term.get('keywords_unified', []):
            kw_normalized = kw.lower().replace('-', ' ').replace('_', ' ')
            keyword_mapping[kw_normalized] = term_key

    # Manual corrections and additions for py_lib context
    # These are carefully selected to ensure formula correctness
    manual_corrections = {
        # Income Statement
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

        # Balance Sheet
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

        # Specific asset/liability items
        'accounts_receivable': 'trade_receivables',
        'trade_receivables': 'trade_receivables',
        'accounts_payable': 'trade_payables',
        'trade_payables': 'trade_payables',
        'inventory': 'inventories',
        'inventories': 'inventories',
        'cash': 'cash_and_equivalents',
        'cash_and_cash_equivalents': 'cash_and_equivalents',
        'cash_equivalents': 'cash_and_equivalents',
        'marketable_securities': 'short_term_investments',

        # Debt/Finance
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

        # Cash Flow
        'depreciation': 'depreciation_amortization',
        'amortization': 'depreciation_amortization',
        'depreciation_and_amortization': 'depreciation_amortization',
        'capital_expenditures': 'capital_expenditure',
        'capex': 'capital_expenditure',
        'capital_expenditure': 'capital_expenditure',
        'operating_cash_flow': 'net_cash_from_operating_activities',
        'cfo': 'net_cash_from_operating_activities',
        'ocf': 'net_cash_from_operating_activities',
        'free_cash_flow': 'free_cash_flow',
        'fcf': 'free_cash_flow',

        # Market
        'market_cap': 'market_capitalization',
        'market_capitalization': 'market_capitalization',
        'shares_outstanding': 'number_of_shares',
        'share_price': 'share_price',
        'enterprise_value': 'enterprise_value',
        'ev': 'enterprise_value',
        'book_value': 'book_value',

        # Special cases
        'operating_expenses': 'operating_expenses',
        'total_expenses': 'total_expenses',
        'minority_interest': 'non_controlling_interest',
    }

    # Manual corrections take precedence
    keyword_mapping.update(manual_corrections)

    return keyword_mapping

def normalize_parameter_name(param: str, mapping: Dict[str, str]) -> str:
    """Normalize a parameter name to canonical term."""
    # Handle _avg and _total suffixes
    suffix = ''
    if param.endswith('_avg'):
        base_param = param[:-4]
        suffix = '_avg'
    elif param.endswith('_total'):
        base_param = param[:-6]
        suffix = '_total'
    else:
        base_param = param

    # Try direct match first
    if param in mapping:
        return mapping[param]

    # Try base match
    if base_param in mapping:
        return mapping[base_param] + suffix

    # Try normalized version
    normalized = base_param.lower().replace('-', ' ').replace('_', ' ')
    if normalized in mapping:
        return mapping[normalized] + suffix

    return param  # Return original if no mapping found

def normalize_py_lib_file(file_path: str, mapping: Dict[str, str], dry_run: bool = True):
    """Normalize keywords in a py_lib file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # Find function definitions
    function_pattern = r'def\s+([a-z_][a-z0-9_]*)\s*\(([^)]+)\)'

    for match in re.finditer(function_pattern, content):
        func_name = match.group(1)
        params_str = match.group(2)
        func_start = match.start()
        func_end = match.end()

        # Extract parameters
        params = []
        for param_match in re.finditer(r'([a-z_][a-z0-9_]*)\s*:\s*float', params_str):
            params.append(param_match.group(1))

        if not params:
            continue

        # Create mapping for this function
        param_mapping = {}
        for param in params:
            normalized = normalize_parameter_name(param, mapping)
            if normalized != param:
                param_mapping[param] = normalized

        if not param_mapping:
            continue

        # Track changes
        changes.append({
            'function': func_name,
            'mappings': param_mapping
        })

        # Replace parameters in function signature
        for old, new in param_mapping.items():
            # Replace in parameter list (case-sensitive, word boundaries)
            pattern = r'\b' + re.escape(old) + r'\s*:\s*float'
            replacement = new + ': float'
            content = re.sub(pattern, replacement, content, count=1)

        # Find function body
        body_start = func_end
        # Find next function definition or end of file
        next_func = re.search(r'\ndef\s+[a-z_]', content[body_start:])
        if next_func:
            body_end = body_start + next_func.start()
        else:
            body_end = len(content)

        body = content[body_start:body_end]

        # Replace parameter usage in body
        for old, new in param_mapping.items():
            # Replace parameter usage (case-sensitive, word boundaries)
            pattern = r'\b' + re.escape(old) + r'\b'
            replacement = new
            body = re.sub(pattern, replacement, body)

        content = content[:body_start] + body + content[body_end:]

    # Update docstrings
    docstring_pattern = r'"""([^"]|"(?!""))*"""'
    for match in re.finditer(docstring_pattern, content, re.MULTILINE):
        docstring = match.group(0)
        original_docstring = docstring

        # Update parameter names in docstrings
        for old, new in mapping.items():
            # Skip very short or generic words
            if len(old) < 3:
                continue

            # Try to preserve original case
            case_pattern = r'\b' + re.escape(old) + r'\b'
            if re.search(case_pattern, docstring, re.IGNORECASE):
                docstring = re.sub(case_pattern, new, docstring, flags=re.IGNORECASE)

        if docstring != original_docstring:
            content = content[:match.start()] + docstring + content[match.end():]

    if content != original_content and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
        for change in changes:
            print(f"  Function: {change['function']}")
            print(f"  Mappings: {change['mappings']}")
    elif changes and dry_run:
        print(f"DRY RUN - Would update: {file_path}")
        for change in changes:
            print(f"  Function: {change['function']}")
            print(f"  Mappings: {change['mappings']}")

    return changes

def main():
    database = load_database()
    if not database:
        print("Error: Could not load terms database")
        sys.exit(1)

    mapping = create_normalization_mapping(database)
    print(f"Created normalization mapping with {len(mapping)} entries")

    py_lib_dir = 'py_lib'
    if not os.path.exists(py_lib_dir):
        print(f"Error: py_lib directory not found: {py_lib_dir}")
        sys.exit(1)

    dry_run = '--dry-run' not in sys.argv and '-d' not in sys.argv
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    if dry_run:
        print("Running in LIVE mode - files will be modified!")
    else:
        print("Running in LIVE mode - files will be modified!")

    total_changes = 0
    files_processed = 0
    errors = []

    for filename in sorted(os.listdir(py_lib_dir)):
        if filename.endswith('.py') and not filename.startswith('_'):
            file_path = os.path.join(py_lib_dir, filename)
            print(f"\nProcessing: {filename}")

            try:
                changes = normalize_py_lib_file(file_path, mapping, dry_run=dry_run)
                if changes:
                    total_changes += len(changes)
                    files_processed += 1
                elif verbose:
                    print("  No changes needed")
            except Exception as e:
                error_msg = f"Error processing {filename}: {e}"
                print(f"  {error_msg}")
                errors.append(error_msg)
                import traceback
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Total files with changes: {files_processed}")
    print(f"Total functions with changes: {total_changes}")
    print(f"Errors: {len(errors)}")
    if errors:
        print("Errors encountered:")
        for error in errors:
            print(f"  - {error}")

if __name__ == '__main__':
    main()
