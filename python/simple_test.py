#!/usr/bin/env python3
"""Simple term matching test"""

import sys
import os

# Set path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("TERM MATCHING TEST FOR APPLE REPORT")
print("=" * 80)

# Test 1: Direct terminology lookup
print("\n1. Testing terminology database access...")
try:
    from terminology_keywords import TERMINOLOGY_MAP, find_all_matching_terms
    print(f"   ✓ Loaded {len(TERMINOLOGY_MAP)} terms")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Test matching function
print("\n2. Testing term matching on sample lines...")
test_cases = [
    "Accounts payable",
    "acc payable",  
    "Trade Payables",
    "Property Plant Equipment",
    "PPE",
    "Cash and Cash Equivalents",
]

for test in test_cases:
    matches = find_all_matching_terms(test)
    if matches:
        best = matches[0]
        print(f"   ✓ '{test:30}' → {best['term_key']:30} (score: {best['score']:.1f})")
    else:
        print(f"   ✗ '{test:30}' → NO MATCH")

# Test 3: Test abbreviation expansion
print("\n3. Testing abbreviation expansion...")
try:
    from abbreviations import expand_abbreviations
    
    abbr_tests = [
        ("acc payable", "accounts payable"),
        ("ppe", "property plant equipment"),
        ("cwip", "capital work in progress"),
    ]
    
    for orig, expected_expansion in abbr_tests:
        expanded = expand_abbreviations(orig)
        success = expected_expansion in expanded
        symbol = "✓" if success else "✗"
        print(f"   {symbol} '{orig}' → '{expanded}'")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
