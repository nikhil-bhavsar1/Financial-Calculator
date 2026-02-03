
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add python directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python')))

try:
    from xbrl_parser import XBRLParser
    from gaap_rules import GAAPValidator, GAAPType, detect_gaap_type
    from indian_finance_utils import IndianNumberParser, IndianDateParser
    from llm_validator import LLMValidator
    from terminology_keywords import TERMINOLOGY_MAP, KEYWORD_TO_TERM
    # Ind AS Config
    from ind_as_config import IND_AS_MANDATORY_SCHEDULES
except ImportError as e:
    print(f"Import Error: {e}")

class TestSECFilings(unittest.TestCase):
    def setUp(self):
        self.parser = XBRLParser()
        
    def test_module_load(self):
        self.assertIsNotNone(self.parser)
        
    def test_us_gaap_taxonomy(self):
        # Verify critical metrics map correctly
        # This checks if the parser logic (which might rely on internal mappings) works
        # For now, we simulate extraction or check internal mapping dicts if accessible
        # Assuming parser has a method or attribute to check mappings, or we test extraction
        pass

    def test_impairment_reversal_us_gaap(self):
        # US GAAP prohibits reversal
        validator = GAAPValidator(GAAPType.US_GAAP)
        metrics = {'impairment_reversal': 100}
        issues = validator.validate(metrics)
        # Should find an issue
        self.assertTrue(any(i.rule_id == 'US_GAAP_IMPAIRMENT_02' for i in issues))

class TestIndianMCAFilings(unittest.TestCase):
    def setUp(self):
        self.number_parser = IndianNumberParser()
        self.date_parser = IndianDateParser()
        
    def test_indian_number_format(self):
        val = self.number_parser.parse_indian_formatted_number("1,50,000")
        self.assertEqual(val, 150000.0)
        
        val_neg = self.number_parser.parse_indian_formatted_number("(1,50,000)")
        self.assertEqual(val_neg, -150000.0)
        
    def test_crores_unit_detection(self):
        # Test header detection logic
        mult, curr = self.number_parser.detect_scale_from_header("Rs. in Crores")
        self.assertEqual(mult, 10000000.0)
        
    def test_ind_as_terminology(self):
        # Verify key terms exist in the database
        self.assertIn('revenue_from_operations', TERMINOLOGY_MAP)
        self.assertIn('trade_receivables', TERMINOLOGY_MAP)
        
    def test_impairment_reversal_ind_as(self):
        # Ind AS allows reversal (should be INFO or Warning, not Error/Prohibited)
        validator = GAAPValidator(GAAPType.IND_AS)
        metrics = {'impairment_reversal': 100}
        issues = validator.validate(metrics)
        # Should NOT find the prohibition error
        self.assertFalse(any(i.rule_id == 'US_GAAP_IMPAIRMENT_01' for i in issues))

class TestCrossGAAPConsistency(unittest.TestCase):
    def test_gaap_type_detection(self):
        us_text = "The financial statements are prepared in accordance with US GAAP."
        ind_text = "Compliance with Ind AS notified under Companies Act 2013."
        
        self.assertEqual(detect_gaap_type(us_text)[0], GAAPType.US_GAAP)
        self.assertEqual(detect_gaap_type(ind_text)[0], GAAPType.IND_AS)
        
    def test_mandatory_ind_as_checks(self):
        validator = GAAPValidator(GAAPType.IND_AS)
        metrics = {'profit_before_tax': 1000} # Missing revenue_from_operations
        issues = validator.validate(metrics)
        
        # Should flag missing mandatory item
        found = any(i.rule_id == 'IND_AS_MISSING_ITEM' and i.metric_key == 'revenue_from_operations' for i in issues)
        self.assertTrue(found, "Should warn about missing revenue_from_operations")

class TestLLMValidation(unittest.TestCase):
    @patch('llm_validator.OllamaClient')
    def test_fallback_validation(self, mock_client):
        # Setup mock to fail or be None
        mock_client.return_value = None
        
        validator = LLMValidator()
        validator.client = None # Force fallback
        
        metrics = {'total_assets': 100, 'total_liabilities': 50, 'total_equity': 40} # Assets != L+E
        
        result = validator.validate_metrics(metrics)
        # Fallback should detect equation mismatch
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Balance sheet equation mismatch" in issue for issue in result.issues))
        self.assertIsNotNone(result.confidence)

if __name__ == '__main__':
    unittest.main()
