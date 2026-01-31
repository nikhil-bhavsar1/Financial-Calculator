#!/usr/bin/env python3
"""
Extract TypeScript term files and export to unified JSON for Python consumption.
Creates a comprehensive cross-sectional database with all keywords unified.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any

TERMS_DIR = Path("/home/nikhil/Gemini Workspace/Financial-Calculator/library/terms")
OUTPUT_FILE = Path("/home/nikhil/Gemini Workspace/Financial-Calculator/python/terms_database.json")

# Map of files to their export variable names
FILE_EXPORTS = {
    "balanceSheetAssets.ts": "BALANCE_SHEET_ASSETS_TERMS",
    "balanceSheetLiabilities.ts": "BALANCE_SHEET_LIABILITIES_TERMS",
    "balanceSheetEquity.ts": "BALANCE_SHEET_EQUITY_TERMS",
    "incomeStatement.ts": "INCOME_STATEMENT_TERMS",
    "cashFlowStatement.ts": "CASH_FLOW_STATEMENT_TERMS",
    "additionalComprehensiveTerms.ts": [
        "ADDITIONAL_REVENUE_TERMS",
        "ADDITIONAL_EXPENSE_TERMS",
        "IFRS18_TERMS",
        "ADDITIONAL_ASSET_TERMS",
        "ADDITIONAL_LIABILITY_TERMS",
        "ADDITIONAL_EQUITY_TERMS",
        "ADDITIONAL_OCI_TERMS",
        "ADDITIONAL_CASH_FLOW_TERMS",
        "DISCLOSURE_TERMS",
        "CHANGES_IN_EQUITY_TERMS",
    ],
    "ratiosAndPerShare.ts": ["FINANCIAL_RATIOS_TERMS", "PER_SHARE_DATA_TERMS"],
    "taxDetails.ts": "TAX_DETAILS_TERMS",
    "ociAndSegments.ts": ["OTHER_COMPREHENSIVE_INCOME_TERMS", "SEGMENT_REPORTING_TERMS", "TAX_TERMS"],
}


def parse_typescript_array(content: str, array_name: str) -> list:
    """Parse a TypeScript array export and extract objects."""
    # Find the array declaration
    pattern = rf"export const {array_name}: TermMapping\[\] = (\[.*?\]);"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    array_content = match.group(1)

    # Parse individual objects - this is a simplified parser
    # We'll look for object patterns between { and }
    objects = []
    depth = 0
    current_obj = ""
    in_object = False

    for char in array_content:
        if char == "{":
            if depth == 0:
                in_object = True
                current_obj = ""
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and in_object:
                current_obj += char
                # Parse this object
                parsed = parse_object(current_obj)
                if parsed:
                    objects.append(parsed)
                in_object = False
                current_obj = ""
            elif in_object:
                current_obj += char
        elif in_object:
            current_obj += char

    return objects


def parse_object(obj_str: str) -> dict | None:
    """Parse a single TypeScript object string into a Python dict."""
    result = {
        "id": "",
        "key": "",
        "label": "",
        "category": "",
        "description": "",
        "keywords_indas": [],
        "keywords_gaap": [],
        "keywords_ifrs": [],
        "keywords_unified": [],  # All keywords combined
        "related_standards": {},
        "aliases": [],
        "calculation": "",
        "sign_convention": "positive",
        "data_type": "currency",
        "priority": 1,
        "is_computed": False,
        "components": []
    }

    # Extract id
    id_match = re.search(r"id:\s*'([^']+)'", obj_str)
    if id_match:
        result["id"] = id_match.group(1)

    # Extract key
    key_match = re.search(r"key:\s*'([^']+)'", obj_str)
    if key_match:
        result["key"] = key_match.group(1)

    # Extract label
    label_match = re.search(r"label:\s*'([^']+)'", obj_str)
    if label_match:
        result["label"] = label_match.group(1)
    
    # Extract category
    category_match = re.search(r"category:\s*'([^']+)'", obj_str)
    if category_match:
        result["category"] = category_match.group(1)
    
    # Extract description
    desc_match = re.search(r"description:\s*'([^']+)'", obj_str)
    if desc_match:
        result["description"] = desc_match.group(1)

    # Extract keywords arrays
    keywords_indas = []
    keywords_gaap = []
    keywords_ifrs = []

    # keywords_indas
    indas_match = re.search(r"keywords_indas:\s*\[([^\]]+)\]", obj_str, re.DOTALL)
    if indas_match:
        keywords_indas = extract_strings(indas_match.group(1))
        result["keywords_indas"] = keywords_indas

    # keywords_gaap
    gaap_match = re.search(r"keywords_gaap:\s*\[([^\]]+)\]", obj_str, re.DOTALL)
    if gaap_match:
        keywords_gaap = extract_strings(gaap_match.group(1))
        result["keywords_gaap"] = keywords_gaap

    # keywords_ifrs
    ifrs_match = re.search(r"keywords_ifrs:\s*\[([^\]]+)\]", obj_str, re.DOTALL)
    if ifrs_match:
        keywords_ifrs = extract_strings(ifrs_match.group(1))
        result["keywords_ifrs"] = keywords_ifrs

    # Create unified keywords - combine all with deduplication
    all_keywords = []
    seen = set()
    
    # Add all keywords from all standards
    for kw in keywords_indas + keywords_gaap + keywords_ifrs:
        kw_lower = kw.lower().strip()
        if kw_lower and kw_lower not in seen:
            seen.add(kw_lower)
            all_keywords.append(kw_lower)
    
    # Add the label itself as a keyword
    if result["label"]:
        label_lower = result["label"].lower().strip()
        if label_lower not in seen:
            seen.add(label_lower)
            all_keywords.append(label_lower)
    
    # Add the key as a keyword (with underscores replaced by spaces)
    if result["key"]:
        key_as_kw = result["key"].replace("_", " ").lower().strip()
        if key_as_kw not in seen:
            seen.add(key_as_kw)
            all_keywords.append(key_as_kw)
    
    result["keywords_unified"] = all_keywords

    # Extract related_standards
    standards_match = re.search(r"related_standards:\s*\{([^\}]+)\}", obj_str, re.DOTALL)
    if standards_match:
        standards_content = standards_match.group(1)
        
        # Extract indas standards
        indas_std_match = re.search(r"indas:\s*\[([^\]]+)\]", standards_content)
        if indas_std_match:
            result["related_standards"]["indas"] = extract_strings(indas_std_match.group(1))
        
        # Extract gaap standards
        gaap_std_match = re.search(r"gaap:\s*\[([^\]]+)\]", standards_content)
        if gaap_std_match:
            result["related_standards"]["gaap"] = extract_strings(gaap_std_match.group(1))
        
        # Extract ifrs standards
        ifrs_std_match = re.search(r"ifrs:\s*\[([^\]]+)\]", standards_content)
        if ifrs_std_match:
            result["related_standards"]["ifrs"] = extract_strings(ifrs_std_match.group(1))
    
    # Extract aliases
    aliases_match = re.search(r"aliases:\s*\[([^\]]+)\]", obj_str, re.DOTALL)
    if aliases_match:
        result["aliases"] = extract_strings(aliases_match.group(1))
    
    # Extract calculation
    calc_match = re.search(r"calculation:\s*'([^']+)'", obj_str)
    if calc_match:
        result["calculation"] = calc_match.group(1)
    
    # Extract sign_convention
    sign_match = re.search(r"sign_convention:\s*'([^']+)'", obj_str)
    if sign_match:
        result["sign_convention"] = sign_match.group(1)
    
    # Extract data_type
    dtype_match = re.search(r"data_type:\s*'([^']+)'", obj_str)
    if dtype_match:
        result["data_type"] = dtype_match.group(1)
    
    # Extract priority
    priority_match = re.search(r"priority:\s*(\d+)", obj_str)
    if priority_match:
        result["priority"] = int(priority_match.group(1))
    
    # Extract is_computed
    computed_match = re.search(r"is_computed:\s*(true|false)", obj_str)
    if computed_match:
        result["is_computed"] = computed_match.group(1) == "true"
    
    # Extract components
    components_match = re.search(r"components:\s*\[([^\]]+)\]", obj_str, re.DOTALL)
    if components_match:
        result["components"] = extract_strings(components_match.group(1))

    return result if result["id"] else None


def extract_strings(array_content: str) -> list:
    """Extract quoted strings from array content."""
    strings = []
    # Match single-quoted strings
    for match in re.finditer(r"'([^']+)'", array_content):
        strings.append(match.group(1))
    return strings


def create_keyword_index(all_terms: List[Dict]) -> Dict[str, List[Dict]]:
    """Create a cross-sectional keyword index mapping keywords to terms."""
    keyword_index: Dict[str, List[Dict]] = {}
    
    for term in all_terms:
        term_key = term.get("key", "")
        if not term_key:
            continue
        
        # Index all unified keywords
        for keyword in term.get("keywords_unified", []):
            if keyword not in keyword_index:
                keyword_index[keyword] = []
            
            # Check if this term is already in the list for this keyword
            if not any(t["term_key"] == term_key for t in keyword_index[keyword]):
                keyword_index[keyword].append({
                    "term_key": term_key,
                    "term_id": term.get("id", ""),
                    "label": term.get("label", ""),
                    "category": term.get("category", ""),
                    "priority": term.get("priority", 1)
                })
    
    return keyword_index


def create_category_index(all_terms: List[Dict]) -> Dict[str, List[Dict]]:
    """Create an index of terms by category."""
    category_index: Dict[str, List[Dict]] = {}
    
    for term in all_terms:
        category = term.get("category", "Misc")
        if category not in category_index:
            category_index[category] = []
        
        category_index[category].append({
            "term_key": term.get("key", ""),
            "term_id": term.get("id", ""),
            "label": term.get("label", ""),
            "priority": term.get("priority", 1)
        })
    
    return category_index


def create_standards_index(all_terms: List[Dict]) -> Dict[str, Dict[str, List[str]]]:
    """Create an index mapping accounting standards to terms."""
    standards_index: Dict[str, Dict[str, List[str]]] = {
        "indas": {},
        "gaap": {},
        "ifrs": {}
    }
    
    for term in all_terms:
        term_key = term.get("key", "")
        related = term.get("related_standards", {})
        
        # Index IndAS standards
        for std in related.get("indas", []):
            if std not in standards_index["indas"]:
                standards_index["indas"][std] = []
            if term_key not in standards_index["indas"][std]:
                standards_index["indas"][std].append(term_key)
        
        # Index GAAP standards
        for std in related.get("gaap", []):
            if std not in standards_index["gaap"]:
                standards_index["gaap"][std] = []
            if term_key not in standards_index["gaap"][std]:
                standards_index["gaap"][std].append(term_key)
        
        # Index IFRS standards
        for std in related.get("ifrs", []):
            if std not in standards_index["ifrs"]:
                standards_index["ifrs"][std] = []
            if term_key not in standards_index["ifrs"][std]:
                standards_index["ifrs"][std].append(term_key)
    
    return standards_index


def main():
    all_terms = []

    for filename, export_names in FILE_EXPORTS.items():
        filepath = TERMS_DIR / filename
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            continue

        content = filepath.read_text()

        # Handle single or multiple export names
        if isinstance(export_names, str):
            export_names = [export_names]

        for export_name in export_names:
            terms = parse_typescript_array(content, export_name)
            all_terms.extend(terms)
            print(f"Extracted {len(terms)} terms from {filename}::{export_name}")

    # Create comprehensive indexes
    keyword_index = create_keyword_index(all_terms)
    category_index = create_category_index(all_terms)
    standards_index = create_standards_index(all_terms)
    
    # Calculate statistics
    total_keywords = sum(len(term.get("keywords_unified", [])) for term in all_terms)
    unique_keywords = len(keyword_index)
    
    # Create output structure
    output = {
        "metadata": {
            "version": "2.0",
            "description": "Unified Comprehensive Financial Terminology Database",
            "total_terms": len(all_terms),
            "total_keywords": total_keywords,
            "unique_keywords": unique_keywords,
            "categories": list(category_index.keys()),
            "accounting_standards": {
                "indas": list(standards_index["indas"].keys()),
                "gaap": list(standards_index["gaap"].keys()),
                "ifrs": list(standards_index["ifrs"].keys())
            }
        },
        "terms": all_terms,
        "indexes": {
            "by_keyword": keyword_index,
            "by_category": category_index,
            "by_standard": standards_index
        }
    }

    # Write to JSON file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully exported unified database:")
    print(f"  - {len(all_terms)} terms")
    print(f"  - {total_keywords} total keywords")
    print(f"  - {unique_keywords} unique keywords")
    print(f"  - {len(category_index)} categories")
    print(f"  - {len(standards_index['indas'])} IndAS standards")
    print(f"  - {len(standards_index['gaap'])} GAAP standards")
    print(f"  - {len(standards_index['ifrs'])} IFRS standards")
    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
