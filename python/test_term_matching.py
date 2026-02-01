#!/usr/bin/env python3
"""
Test script to extract and match terms from Apple Report PDF
Demonstrates the term normalization and matching pipeline
"""

import sys
import json
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent))

from preprocessing import TextPreprocessor
from terminology_keywords import find_all_matching_terms, TERMINOLOGY_MAP
from text_normalizer import normalizer

def test_term_extraction(pdf_path: str, page_num: int = 31):
    """Extract and test term matching from a specific page."""
    
    print(f"=" * 80)
    print(f"TERM EXTRACTION TEST: {Path(pdf_path).name} - Page {page_num}")
    print(f"=" * 80)
    
    # Sample lines from a typical Balance Sheet page
    # These would normally come from PDF extraction
    test_lines = [
        "Accounts payable              1,234.50    987.25",
        "Trade Payables                5,678.00    4,321.00",
        "Acc payable                   2,500.00    2,100.00",
        "Property, Plant & Equipment   10,000.00   9,500.00",
        "PPE                           10,000.00   9,500.00",
        "Cash and Cash Equivalents     3,456.78    3,200.00",
        "Trade Receivables             4,567.89    4,000.00",
        "Inventories                   2,345.67    2,100.00",
        "Total Current Assets          15,000.00   14,500.00",
        "Long-term Borrowings          8,900.00    8,500.00",
        "Deferred Tax Liabilities      1,200.00    1,100.00",
    ]
    
    print(f"\nProcessing {len(test_lines)} test lines...\n")
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor()
    
    results = []
    
    for i, line in enumerate(test_lines, 1):
        print(f"\n{'─' * 80}")
        print(f"Line {i}: {line}")
        print(f"{'─' * 80}")
        
        # Step 1: Preprocess
        prep_result = preprocessor.preprocess(line)
        
        print(f"✓ Original:   '{prep_result.original_text}'")
        print(f"✓ Cleaned:    '{prep_result.cleaned_text}'")
        print(f"✓ Canonical:  '{prep_result.canonical_form}'")
        
        if prep_result.detected_abbreviations:
            print(f"✓ Expanded:   {', '.join(prep_result.detected_abbreviations)}")
        
        # Step 2: Match terms using canonical form
        matches = find_all_matching_terms(prep_result.canonical_form)
        
        if matches:
            print(f"\n✓ MATCHED {len(matches)} term(s):")
            for j, match in enumerate(matches[:3], 1):  # Show top 3
                term_data = TERMINOLOGY_MAP.get(match['term_key'], {})
                print(f"  {j}. {match['term_key']}")
                print(f"     Label: {term_data.get('label', 'N/A')}")
                print(f"     Category: {term_data.get('category', 'N/A')}")
                print(f"     Score: {match['score']:.2f}")
                print(f"     Matched keyword: '{match.get('matched_keyword', 'N/A')}'")
        else:
            print(f"\n✗ NO MATCHES FOUND")
            
            # Test with just the normalizer
            normalized = normalizer.normalize_label(line)
            print(f"  Trying with normalizer: '{normalized}'")
            norm_matches = find_all_matching_terms(normalized)
            if norm_matches:
                print(f"  → Found {len(norm_matches)} matches with normalizer!")
                match = norm_matches[0]
                print(f"     Best: {match['term_key']} (score: {match['score']:.2f})")
        
        results.append({
            'line': line,
            'canonical': prep_result.canonical_form,
            'matches': len(matches),
            'best_match': matches[0]['term_key'] if matches else None
        })
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total lines tested: {len(test_lines)}")
    print(f"Successfully matched: {sum(1 for r in results if r['matches'] > 0)}")
    print(f"No matches: {sum(1 for r in results if r['matches'] == 0)}")
    print(f"Match rate: {sum(1 for r in results if r['matches'] > 0) / len(test_lines) * 100:.1f}%")
    
    print(f"\n{'=' * 80}")
    print(f"MATCHED TERMS:")
    print(f"{'=' * 80}")
    for r in results:
        if r['best_match']:
            print(f"✓ {r['line'][:40]:40} → {r['best_match']}")
    
    print(f"\n{'=' * 80}")
    print(f"UNMATCHED LINES:")
    print(f"{'=' * 80}")
    for r in results:
        if not r['best_match']:
            print(f"✗ {r['line']}")

if __name__ == "__main__":
    pdf_path = "Apple Rep.pdf"
    test_term_extraction(pdf_path, page_num=31)
