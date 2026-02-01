#!/usr/bin/env python3
"""
Financial Term Matching System - Example Usage
==============================================
Demonstrates how to use the comprehensive financial term matching system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import FinancialTermMatcher, match_terms


def example_1_basic_matching():
    """Example 1: Basic term matching"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Term Matching")
    print("="*60)
    
    # Create matcher instance
    matcher = FinancialTermMatcher()
    
    # Sample financial statement lines
    sample_lines = [
        "Property, Plant and Equipment",
        "Trade Receivables (Note 12)",
        "Capital Work in Progress",
        "Goodwill on Consolidation",
        "Total Revenue from Operations",
        "PPE & CWIP",
        "EBITDA for the year",
        "Cash and Cash Equivalents",
        "Long-term Borrowings",
        "Inventories (Raw Materials)",
        "Less: Provision for Doubtful Debts",
        "(1,234) Loss on Sale"
    ]
    
    print("\nProcessing sample lines:")
    for line in sample_lines:
        print(f"\n  Input: '{line}'")
        matches = matcher.match(line)
        
        if matches:
            for match in matches:
                print(f"    → Matched: {match.term_label}")
                print(f"      Type: {match.match_type}, Confidence: {match.confidence_score:.2%}")
        else:
            print("    → No matches found")


def example_2_document_processing():
    """Example 2: Processing a full document"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Document Processing")
    print("="*60)
    
    matcher = FinancialTermMatcher()
    
    # Simulate a balance sheet section
    balance_sheet_lines = [
        "ASSETS",
        "Non-Current Assets",
        "Property, Plant and Equipment          1,50,000",
        "Capital Work-in-Progress                  25,000",
        "Intangible Assets                         15,000",
        "Goodwill                                  10,000",
        "Total Non-Current Assets                2,00,000",
        "",
        "Current Assets",
        "Inventories                               50,000",
        "Trade Receivables                         40,000",
        "Cash and Cash Equivalents                 30,000",
        "Total Current Assets                     1,20,000",
        "",
        "TOTAL ASSETS                            3,20,000"
    ]
    
    print(f"\nProcessing {len(balance_sheet_lines)} lines...")
    session = matcher.match_document(balance_sheet_lines)
    
    # Print summary
    matcher.print_summary(session)
    
    # Show top matches
    print("\nTop 10 Matches:")
    for i, match in enumerate(session.results[:10], 1):
        print(f"  {i}. {match.term_label:30s} (confidence: {match.confidence_score:.2%})")


def example_3_preprocessing():
    """Example 3: Text preprocessing"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Text Preprocessing")
    print("="*60)
    
    matcher = FinancialTermMatcher()
    
    # Sample text with various formatting issues
    test_cases = [
        "PPE & CWIP (Note 12)",
        "Trade Receivables (see note 5)",
        "Property, Plant & Equipment—Net",
        "Less: Provision for Doubtful Debts",
        "(1,234) Loss on Sale",
        "Total Assets………………………... 1,00,000"
    ]
    
    print("\nPreprocessing examples:")
    for text in test_cases:
        result = matcher.preprocess(text)
        print(f"\n  Original:   '{result.original_text}'")
        print(f"  Cleaned:    '{result.cleaned_text}'")
        print(f"  Canonical:  '{result.canonical_form}'")
        print(f"  Sign:       {result.sign_multiplier}")
        if result.detected_abbreviations:
            print(f"  Abbreviations: {result.detected_abbreviations}")


def example_4_validation():
    """Example 4: Running validation tests"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Validation Tests")
    print("="*60)
    
    matcher = FinancialTermMatcher()
    
    print("\nRunning validation suite...")
    results = matcher.validate()
    
    print(f"\nValidation Results:")
    print(f"  Overall Status: {results['overall_status']}")
    print(f"  Preprocessing Tests: {results['preprocessing']['tests_passed']}/{results['preprocessing']['tests_run']}")
    print(f"  Golden Set Precision: {results['golden_set']['precision']:.2%}")
    print(f"  Golden Set Recall: {results['golden_set']['recall']:.2%}")
    print(f"  F1 Score: {results['golden_set']['f1_score']:.2%}")
    print(f"  Processing Speed: {results['performance']['pipeline_speed']:.0f} lines/sec")


def example_5_quick_function():
    """Example 5: Using the quick match function"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Quick Match Function")
    print("="*60)
    
    # Quick one-off matching
    text = "Property Plant and Equipment"
    matches = match_terms(text)
    
    print(f"\nInput: '{text}'")
    print(f"Found {len(matches)} matches:")
    for match in matches:
        print(f"  - {match['term_label']} ({match['match_type']}, {match['confidence']:.2%})")


def example_6_statistics():
    """Example 6: Getting statistics"""
    print("\n" + "="*60)
    print("EXAMPLE 6: System Statistics")
    print("="*60)
    
    matcher = FinancialTermMatcher()
    
    # Process some documents first
    sample_lines = [
        "Property, Plant and Equipment",
        "Trade Receivables",
        "Cash and Cash Equivalents",
        "Total Assets"
    ]
    
    matcher.match_document(sample_lines)
    matcher.match_document(sample_lines)
    
    # Get statistics
    stats = matcher.get_statistics()
    
    print(f"\nProcessing Statistics:")
    print(f"  Sessions Processed: {stats['sessions_processed']}")
    print(f"  Total Lines: {stats['total_lines_processed']}")
    print(f"  Total Matches: {stats['total_matches_found']}")
    print(f"  Avg Matches/Line: {stats['average_matches_per_line']:.2f}")
    
    print(f"\nDatabase Statistics:")
    db_stats = stats['database_stats']
    print(f"  Total Terms: {db_stats.get('total_terms', 'N/A')}")
    print(f"  Total Keywords: {db_stats.get('total_keywords', 'N/A')}")
    print(f"  Categories: {len(db_stats.get('categories', []))}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("FINANCIAL TERM MATCHING SYSTEM - EXAMPLES")
    print("="*60)
    
    try:
        example_1_basic_matching()
        example_2_document_processing()
        example_3_preprocessing()
        example_4_validation()
        example_5_quick_function()
        example_6_statistics()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
