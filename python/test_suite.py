"""
Financial Term Matching System - Comprehensive Test Suite
=========================================================
Extensive test suite with 100+ test cases covering all system components.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from typing import List, Dict, Any

# Import all modules to test
from preprocessing import TextPreprocessor, preprocess_text
from abbreviations import expand_abbreviations, generate_acronyms, get_all_abbreviations
from matching_engine import MultiLayerMatchingEngine, match_financial_terms
from section_classifier import SectionClassifier, classify_financial_section
from cross_reference_resolver import CrossReferenceResolver
from keyword_expansion import KeywordExpander, expand_keywords
from relationship_mapper import RelationshipMapper, get_term_synonyms
from validation import ValidationFramework, GoldenSetTest
from __init__ import FinancialTermMatcher


class TestPreprocessing(unittest.TestCase):
    """Test preprocessing pipeline"""
    
    def setUp(self):
        self.preprocessor = TextPreprocessor()
    
    def test_abbreviation_expansion(self):
        """Test 1: Abbreviation expansion"""
        test_cases = [
            ("PPE", "property plant equipment"),
            ("CWIP", "capital work in progress"),
            ("EBITDA", "earnings before interest tax depreciation amortization"),
            ("FY 2023", "financial year 2023"),
            ("B/S", "balance sheet"),
            ("P&L", "profit loss"),
        ]
        
        for input_text, expected in test_cases:
            result = self.preprocessor.preprocess(input_text)
            self.assertIn(expected, result.canonical_form, 
                         f"Failed for: {input_text}")
    
    def test_note_reference_removal(self):
        """Test 2: Note reference removal"""
        test_cases = [
            ("Trade Receivables (Note 12)", "trade receivables"),
            ("PPE (see note 5)", "ppe"),
            ("Assets (Schedule A)", "assets"),
            ("Revenue (1)", "revenue"),
        ]
        
        for input_text, expected in test_cases:
            result = self.preprocessor.preprocess(input_text)
            self.assertEqual(result.canonical_form.strip(), expected,
                           f"Failed for: {input_text}")
    
    def test_sign_convention_detection(self):
        """Test 3: Sign convention detection"""
        test_cases = [
            ("Less: Provision", -1),
            ("(-) Loss", -1),
            ("(Cr.) Amount", -1),
            ("Dr. Balance", 1),
            ("Regular Amount", 1),
        ]
        
        for input_text, expected_sign in test_cases:
            result = self.preprocessor.preprocess(input_text)
            self.assertEqual(result.sign_multiplier, expected_sign,
                           f"Failed for: {input_text}")
    
    def test_parenthetical_numbers(self):
        """Test 4: Parenthetical number conversion"""
        test_cases = [
            ("Loss (1,234)", "loss -1234"),
            ("Amount (50,000)", "amount -50000"),
            ("Profit 1,00,000", "profit 100000"),
        ]
        
        for input_text, expected in test_cases:
            result = self.preprocessor.preprocess(input_text)
            self.assertEqual(result.canonical_form.strip(), expected,
                           f"Failed for: {input_text}")
    
    def test_unicode_normalization(self):
        """Test 5: Unicode normalization"""
        test_cases = [
            ("Property—Plant & Equipment", "property plant and equipment"),
            ('"Quoted" Text', "quoted text"),
            ("Non–Breaking", "non breaking"),
        ]
        
        for input_text, expected in test_cases:
            result = self.preprocessor.preprocess(input_text)
            self.assertEqual(result.canonical_form.strip(), expected,
                           f"Failed for: {input_text}")
    
    def test_dot_leader_removal(self):
        """Test 6: Dot leader removal"""
        result = self.preprocessor.preprocess("Assets...............1000")
        self.assertNotIn("...", result.cleaned_text)
    
    def test_date_normalization(self):
        """Test 7: Date normalization"""
        result = self.preprocessor.preprocess("As of 31.03.2023")
        self.assertIn("2023-03-31", result.canonical_form)
    
    def test_number_format_normalization(self):
        """Test 8: Number format normalization"""
        result = self.preprocessor.preprocess("Amount 1,00,000.50")
        self.assertIn("100000.50", result.canonical_form)


class TestAbbreviations(unittest.TestCase):
    """Test abbreviation handling"""
    
    def test_all_abbreviations_loaded(self):
        """Test 9: All abbreviations loaded"""
        abbr = get_all_abbreviations()
        self.assertGreater(len(abbr), 50)
    
    def test_expand_abbreviations(self):
        """Test 10: Expand abbreviations"""
        result = expand_abbreviations("PPE and CWIP")
        self.assertIn("property", result)
        self.assertIn("equipment", result)
        self.assertIn("capital", result)
    
    def test_acronym_generation(self):
        """Test 11: Acronym generation"""
        acronyms = generate_acronyms("Property Plant Equipment")
        self.assertIn("ppe", acronyms)
    
    def test_multi_word_abbreviations(self):
        """Test 12: Multi-word abbreviations"""
        result = expand_abbreviations("Ind AS 115")
        self.assertIn("indian", result.lower())
        self.assertIn("accounting", result.lower())


class TestMatchingEngine(unittest.TestCase):
    """Test matching engine"""
    
    def setUp(self):
        self.engine = MultiLayerMatchingEngine()
    
    def test_exact_matching(self):
        """Test 13: Exact matching"""
        matches = self.engine.match_text("Property Plant and Equipment")
        self.assertTrue(len(matches) > 0)
        self.assertTrue(any(m.match_type == 'exact' for m in matches))
    
    def test_fuzzy_matching(self):
        """Test 14: Fuzzy matching"""
        # Test with typo
        matches = self.engine.match_text("Property Plant Equipmant")  # typo
        self.assertTrue(len(matches) > 0)
    
    def test_acronym_matching(self):
        """Test 15: Acronym matching"""
        matches = self.engine.match_text("PPE")
        self.assertTrue(len(matches) > 0)
    
    def test_multiword_phrase_matching(self):
        """Test 16: Multi-word phrase matching"""
        matches = self.engine.match_text("Capital Work in Progress")
        self.assertTrue(len(matches) > 0)
    
    def test_hierarchical_resolution(self):
        """Test 17: Hierarchical resolution"""
        # Should prefer child over parent
        matches = self.engine.match_text("Goodwill")
        goodwill_matches = [m for m in matches if 'goodwill' in m.term_key.lower()]
        self.assertTrue(len(goodwill_matches) > 0)
    
    def test_document_processing(self):
        """Test 18: Document processing"""
        lines = [
            "Property Plant and Equipment",
            "Trade Receivables",
            "Cash and Cash Equivalents"
        ]
        session = self.engine.match_document(lines)
        self.assertEqual(len(session.results), 3)
    
    def test_confidence_scoring(self):
        """Test 19: Confidence scoring"""
        matches = self.engine.match_text("Total Revenue")
        for match in matches:
            self.assertGreater(match.confidence_score, 0)
            self.assertLessEqual(match.confidence_score, 3.0)  # Max with boost
    
    def test_deduplication(self):
        """Test 20: Deduplication"""
        # Same term shouldn't appear multiple times
        matches = self.engine.match_text("PPE and Property Plant Equipment")
        term_keys = [m.term_key for m in matches]
        self.assertEqual(len(term_keys), len(set(term_keys)))


class TestSectionClassifier(unittest.TestCase):
    """Test section classification"""
    
    def setUp(self):
        self.classifier = SectionClassifier()
    
    def test_balance_sheet_assets_detection(self):
        """Test 21: Balance Sheet Assets detection"""
        lines = [
            "ASSETS",
            "Non-Current Assets",
            "Property Plant and Equipment 1000",
            "Total Assets 5000"
        ]
        section = self.classifier.classify_section(lines)
        self.assertIsNotNone(section)
        self.assertIn('balance_sheet', section.section_type)
    
    def test_income_statement_detection(self):
        """Test 22: Income Statement detection"""
        lines = [
            "Statement of Profit and Loss",
            "Revenue from Operations 10000",
            "Total Expenses 8000",
            "Profit for the Year 2000"
        ]
        section = self.classifier.classify_section(lines)
        self.assertIsNotNone(section)
        self.assertIn('income', section.section_type)
    
    def test_cash_flow_detection(self):
        """Test 23: Cash Flow detection"""
        lines = [
            "Cash Flow Statement",
            "Operating Activities",
            "Cash from Operations 5000",
            "Cash and Equivalents at End 10000"
        ]
        section = self.classifier.classify_section(lines)
        self.assertIsNotNone(section)
        self.assertIn('cash_flow', section.section_type)
    
    def test_notes_detection(self):
        """Test 24: Notes detection"""
        lines = [
            "Notes to the Accounts",
            "Note 1: Accounting Policies",
            "Significant accounting policies are..."
        ]
        section = self.classifier.classify_section(lines)
        self.assertIsNotNone(section)
        self.assertIn('note', section.section_type)
    
    def test_section_boost(self):
        """Test 25: Section boost"""
        boost = self.classifier.get_section_boost('property_plant_equipment', 'balance_sheet_assets')
        self.assertGreater(boost, 1.0)


class TestCrossReferenceResolver(unittest.TestCase):
    """Test cross-reference resolution"""
    
    def setUp(self):
        self.resolver = CrossReferenceResolver()
    
    def test_note_reference_extraction(self):
        """Test 26: Note reference extraction"""
        lines = [
            "Trade Receivables (see note 12)",
            "PPE (Note 5)",
            "Revenue (refer to note 8)"
        ]
        refs = self.resolver.extract_references(lines, [])
        self.assertEqual(len(refs), 3)
        self.assertTrue(all(r.ref_type == 'note' for r in refs))
    
    def test_schedule_reference_extraction(self):
        """Test 27: Schedule reference extraction"""
        lines = [
            "Assets as per Schedule A",
            "Details (Schedule B)"
        ]
        refs = self.resolver.extract_references(lines, [])
        schedule_refs = [r for r in refs if r.ref_type == 'schedule']
        self.assertEqual(len(schedule_refs), 2)
    
    def test_note_section_extraction(self):
        """Test 28: Note section extraction"""
        lines = [
            "Note 1: Accounting Policies",
            "Significant accounting policies...",
            "Note 2: Revenue Recognition",
            "Revenue is recognized when..."
        ]
        notes = self.resolver.extract_note_sections(lines)
        self.assertEqual(len(notes), 2)
        self.assertIn('1', notes)
        self.assertIn('2', notes)


class TestKeywordExpansion(unittest.TestCase):
    """Test keyword expansion"""
    
    def setUp(self):
        self.expander = KeywordExpander()
    
    def test_pluralization(self):
        """Test 29: Pluralization"""
        variants = self.expander.expand_keyword("asset")
        self.assertIn("assets", variants)
    
    def test_singularization(self):
        """Test 30: Singularization"""
        variants = self.expander.expand_keyword("assets")
        self.assertIn("asset", variants)
    
    def test_regional_variants_uk_to_us(self):
        """Test 31: UK to US spelling"""
        variants = self.expander.expand_keyword("amortisation")
        self.assertIn("amortization", variants)
    
    def test_regional_variants_us_to_uk(self):
        """Test 32: US to UK spelling"""
        variants = self.expander.expand_keyword("amortization")
        self.assertIn("amortisation", variants)
    
    def test_ocr_variants(self):
        """Test 33: OCR error variants"""
        variants = self.expander.expand_keyword("equipment")
        # Should generate variants with common OCR errors
        self.assertTrue(len(variants) > 1)
    
    def test_irregular_plurals(self):
        """Test 34: Irregular plurals"""
        variants = self.expander.expand_keyword("child")
        self.assertIn("children", variants)


class TestRelationshipMapper(unittest.TestCase):
    """Test relationship mapping"""
    
    def setUp(self):
        self.mapper = RelationshipMapper()
    
    def test_synonym_lookup(self):
        """Test 35: Synonym lookup"""
        synonyms = self.mapper.get_synonyms('trade_receivables')
        self.assertIn('accounts_receivable', synonyms)
        self.assertIn('sundry_debtors', synonyms)
    
    def test_canonical_term_lookup(self):
        """Test 36: Canonical term lookup"""
        canonical = self.mapper.get_canonical_term('sundry_debtors')
        self.assertEqual(canonical, 'trade_receivables')
    
    def test_parent_child_hierarchy(self):
        """Test 37: Parent-child hierarchy"""
        children = self.mapper.get_children('total_assets')
        self.assertIn('total_non_current_assets', children)
        self.assertIn('total_current_assets', children)
    
    def test_parent_lookup(self):
        """Test 38: Parent lookup"""
        parent = self.mapper.get_parent('goodwill')
        self.assertEqual(parent, 'intangible_assets')
    
    def test_all_parents(self):
        """Test 39: All parents lookup"""
        parents = self.mapper.get_all_parents('goodwill')
        self.assertIn('intangible_assets', parents)
        self.assertIn('total_non_current_assets', parents)
    
    def test_related_terms(self):
        """Test 40: Related terms"""
        related = self.mapper.find_related_terms('trade_receivables', max_distance=2)
        self.assertTrue(len(related) > 0)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.matcher = FinancialTermMatcher()
    
    def test_end_to_end_matching(self):
        """Test 41: End-to-end matching"""
        lines = [
            "BALANCE SHEET",
            "ASSETS",
            "Non-Current Assets",
            "Property, Plant and Equipment    1,50,000",
            "Capital Work in Progress             25,000",
            "Goodwill                             10,000",
            "Total Non-Current Assets          1,85,000",
            "Current Assets",
            "Inventories                          50,000",
            "Trade Receivables                    40,000",
            "Cash and Cash Equivalents            30,000",
            "Total Current Assets                1,20,000",
            "TOTAL ASSETS                        3,05,000"
        ]
        
        session = self.matcher.match_document(lines)
        self.assertGreater(len(session.results), 5)
    
    def test_preprocessing_integration(self):
        """Test 42: Preprocessing integration"""
        result = self.matcher.preprocess("PPE & CWIP (Note 12)")
        self.assertIn("property", result.canonical_form)
        self.assertIn("equipment", result.canonical_form)
        self.assertEqual(result.sign_multiplier, 1)
    
    def test_validation_integration(self):
        """Test 43: Validation integration"""
        # This will run a quick validation
        results = self.matcher.validate()
        self.assertIn('preprocessing', results)
        self.assertIn('golden_set', results)
    
    def test_statistics_tracking(self):
        """Test 44: Statistics tracking"""
        lines = ["Property Plant Equipment", "Trade Receivables"]
        self.matcher.match_document(lines)
        
        stats = self.matcher.get_statistics()
        self.assertEqual(stats['sessions_processed'], 1)
        self.assertEqual(stats['total_lines_processed'], 2)


class TestEdgeCases(unittest.TestCase):
    """Edge case tests"""
    
    def setUp(self):
        self.preprocessor = TextPreprocessor()
        self.engine = MultiLayerMatchingEngine()
    
    def test_empty_input(self):
        """Test 45: Empty input handling"""
        result = self.preprocessor.preprocess("")
        self.assertEqual(result.canonical_form, "")
    
    def test_whitespace_only(self):
        """Test 46: Whitespace-only input"""
        result = self.preprocessor.preprocess("   \n\t  ")
        self.assertEqual(result.canonical_form, "")
    
    def test_special_characters(self):
        """Test 47: Special characters"""
        result = self.preprocessor.preprocess("Assets @#$%^&*() 1000")
        self.assertIn("assets", result.canonical_form)
        self.assertIn("1000", result.canonical_form)
    
    def test_very_long_input(self):
        """Test 48: Very long input"""
        long_text = "Property Plant and Equipment " * 100
        result = self.preprocessor.preprocess(long_text)
        self.assertTrue(len(result.canonical_form) > 0)
    
    def test_multiple_abbreviations(self):
        """Test 49: Multiple abbreviations"""
        result = self.preprocessor.preprocess("PPE, CWIP, and EBITDA")
        self.assertIn("property", result.canonical_form)
        self.assertIn("earnings", result.canonical_form)
    
    def test_nested_parentheses(self):
        """Test 50: Nested parentheses"""
        result = self.preprocessor.preprocess("Amount ((1,000))")
        # Should handle gracefully
        self.assertTrue(len(result.canonical_form) > 0)


class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def setUp(self):
        self.matcher = FinancialTermMatcher()
    
    def test_processing_speed(self):
        """Test 51: Processing speed"""
        import time
        
        lines = ["Property Plant Equipment"] * 100
        
        start = time.time()
        session = self.matcher.match_document(lines)
        elapsed = time.time() - start
        
        speed = len(lines) / elapsed
        self.assertGreater(speed, 100)  # At least 100 lines/sec
    
    def test_memory_efficiency(self):
        """Test 52: Memory efficiency"""
        import sys
        
        lines = ["Line " + str(i) for i in range(1000)]
        session = self.matcher.match_document(lines)
        
        # Check that we're not storing excessive data
        self.assertLess(len(session.unmatched_lines), 1000)


# Create comprehensive golden set tests
COMPREHENSIVE_GOLDEN_SET = [
    # Basic terms
    {"input": "Property, Plant and Equipment", "expected_terms": ["property_plant_equipment"]},
    {"input": "Trade Receivables", "expected_terms": ["trade_receivables"]},
    {"input": "Trade Payables", "expected_terms": ["trade_payables"]},
    {"input": "Cash and Cash Equivalents", "expected_terms": ["cash_and_equivalents"]},
    {"input": "Inventories", "expected_terms": ["inventories"]},
    {"input": "Goodwill", "expected_terms": ["goodwill"]},
    {"input": "Intangible Assets", "expected_terms": ["intangible_assets"]},
    {"input": "Total Assets", "expected_terms": ["total_assets"]},
    {"input": "Total Liabilities", "expected_terms": ["total_liabilities"]},
    {"input": "Total Equity", "expected_terms": ["total_equity"]},
    
    # With abbreviations
    {"input": "PPE", "expected_terms": ["property_plant_equipment"]},
    {"input": "CWIP", "expected_terms": ["capital_work_in_progress"]},
    {"input": "EBITDA", "expected_terms": ["ebitda"]},
    {"input": "EPS", "expected_terms": ["earnings_per_share"]},
    
    # With notes
    {"input": "Trade Receivables (Note 12)", "expected_terms": ["trade_receivables"]},
    {"input": "PPE (see note 5)", "expected_terms": ["property_plant_equipment"]},
    
    # With formatting
    {"input": "Property—Plant & Equipment", "expected_terms": ["property_plant_equipment"]},
    {"input": "Total Assets...............1000", "expected_terms": ["total_assets"]},
    
    # Income statement
    {"input": "Revenue from Operations", "expected_terms": ["total_revenue"]},
    {"input": "Cost of Goods Sold", "expected_terms": ["cost_of_goods_sold"]},
    {"input": "Gross Profit", "expected_terms": ["gross_profit"]},
    {"input": "Operating Profit", "expected_terms": ["operating_profit"]},
    {"input": "Profit Before Tax", "expected_terms": ["profit_before_tax"]},
    {"input": "Profit for the Year", "expected_terms": ["profit_for_the_year"]},
    {"input": "Net Income", "expected_terms": ["net_income"]},
    
    # Balance sheet liabilities
    {"input": "Long-term Borrowings", "expected_terms": ["long_term_borrowings"]},
    {"input": "Short-term Borrowings", "expected_terms": ["short_term_borrowings"]},
    {"input": "Deferred Tax", "expected_terms": ["deferred_tax_liabilities"]},
    {"input": "Provisions", "expected_terms": ["provisions"]},
    
    # Equity
    {"input": "Share Capital", "expected_terms": ["share_capital"]},
    {"input": "Reserves and Surplus", "expected_terms": ["reserves_and_surplus"]},
    {"input": "Retained Earnings", "expected_terms": ["retained_earnings"]},
    
    # Cash flow
    {"input": "Cash from Operating Activities", "expected_terms": ["net_cash_from_operating_activities"]},
    {"input": "Cash from Investing Activities", "expected_terms": ["net_cash_from_investing_activities"]},
    {"input": "Cash from Financing Activities", "expected_terms": ["net_cash_from_financing_activities"]},
    
    # Financial instruments
    {"input": "FVTPL Investments", "expected_terms": ["financial_assets_fvtpl"]},
    {"input": "FVTOCI Investments", "expected_terms": ["financial_assets_fvtoci"]},
    {"input": "Amortized Cost Investments", "expected_terms": ["financial_assets_amortized_cost"]},
    
    # Leases
    {"input": "Right-of-Use Assets", "expected_terms": ["right_of_use_assets"]},
    {"input": "Lease Liabilities", "expected_terms": ["lease_liabilities"]},
    
    # Revenue recognition
    {"input": "Contract Assets", "expected_terms": ["contract_assets"]},
    {"input": "Contract Liabilities", "expected_terms": ["contract_liabilities"]},
    
    # Tax
    {"input": "Current Tax", "expected_terms": ["current_tax"]},
    {"input": "MAT Credit", "expected_terms": ["mat_credit_entitlement"]},
    
    # Sign conventions
    {"input": "Less: Provision", "expected_terms": ["provisions"]},
    {"input": "(-) Loss", "expected_terms": ["loss"]},
    
    # Regional variants
    {"input": "Amortisation", "expected_terms": ["amortization"]},
    {"input": "Sundry Debtors", "expected_terms": ["trade_receivables"]},
    {"input": "Sundry Creditors", "expected_terms": ["trade_payables"]},
]


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPreprocessing))
    suite.addTests(loader.loadTestsFromTestCase(TestAbbreviations))
    suite.addTests(loader.loadTestsFromTestCase(TestMatchingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSectionClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossReferenceResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestKeywordExpansion))
    suite.addTests(loader.loadTestsFromTestCase(TestRelationshipMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests Failed: {len(result.failures)}")
    print(f"Tests with Errors: {len(result.errors)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("="*70)
    
    return result


if __name__ == '__main__':
    result = run_comprehensive_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
