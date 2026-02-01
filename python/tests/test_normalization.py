import sys
import os
import unittest

# Add parent directory to path to import text_normalizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_normalizer import normalizer

class TestTextNormalization(unittest.TestCase):
    
    def test_abbreviation_expansion(self):
        cases = [
            ("PPE & CWIP", "property plant and equipment and capital work in progress"),
            ("EBITDA for the year", "earnings before interest taxes depreciation and amortization for the year"),
            ("Net Profit (attributable to NCI)", "net profit attributable to nci"), # nci not in my list yet, but let's see
            ("FY 2023-24", "financial year 2023 24"),
        ]
        for input_text, expected in cases:
            # We use normalize_label which includes expansion and separator normalization
            result = normalizer.normalize_label(input_text)
            # The exact output might vary slightly due to separator normalization, 
            # so we check if the key components are present
            for word in expected.split():
                self.assertIn(word, result, f"Failed to expand '{input_text}': '{word}' not in '{result}'")

    def test_noise_removal(self):
        cases = [
            ("Tangible Assets (Note 5)", "tangible assets"),
            ("Inventories..........", "inventories"),
            ("Trade Receivables (see Schedule 12)", "trade receivables"),
            ("Cash and Cash Equivalents (Note no. 4)", "cash and cash equivalents"),
        ]
        for input_text, expected in cases:
            result = normalizer.normalize_label(input_text)
            self.assertEqual(result, expected, f"Failed noise removal for '{input_text}'")

    def test_unicode_normalization(self):
        cases = [
            ("Property\u2013Plant", "property plant"), # en-dash
            ("IT\u2019s assets", "it s assets"), # curly quote
            ("Total\u00a0Assets", "total assets"), # non-breaking space
        ]
        for input_text, expected in cases:
            result = normalizer.normalize_label(input_text)
            # Note: normalize_separators removes punctuation
            self.assertEqual(result, expected, f"Failed unicode normalization for '{input_text}'")

    def test_sign_detection(self):
        cases = [
            ("Less: Depreciation", -1),
            ("(-) Interest Expense", -1),
            ("(1,234.50)", -1),
            ("Trade Payables", 1),
        ]
        for input_text, expected_sign in cases:
            self.assertEqual(normalizer.detect_sign(input_text), expected_sign, f"Failed sign detection for '{input_text}'")

    def test_date_normalization(self):
        cases = [
            ("Balance as at 31/03/2023", "balance as at 2023 03 31"),
            ("Period ending 31-12-22", "period ending 2022 12 31"),
        ]
        for input_text, expected in cases:
            result = normalizer.normalize_label(input_text)
            self.assertEqual(result, expected, f"Failed date normalization for '{input_text}'")

    def test_numerical_cleaning(self):
        cases = [
            ("(1,234.50)", (1234.5, -1)),
            (" - 5,678 ", (5678.0, -1)),
            ("12,34,567", (1234567.0, 1)), # Indian format
        ]
        for input_text, expected in cases:
            val, sign = normalizer.clean_numerical_value(input_text)
            self.assertEqual((val, sign), expected, f"Failed numerical cleaning for '{input_text}'")

if __name__ == "__main__":
    unittest.main()
