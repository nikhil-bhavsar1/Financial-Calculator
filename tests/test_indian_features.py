
import unittest
import sys
import os

# Add python directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

try:
    from indian_finance_utils import IndianNumberParser, IndianDateParser, UnitDetector
except ImportError:
    pass

class TestIndianUtils(unittest.TestCase):
    def setUp(self):
        self.num_parser = IndianNumberParser()
        self.date_parser = IndianDateParser()
        self.unit_detector = UnitDetector()

    def test_lakh_parsing(self):
        # 1,50,000 -> 150000
        self.assertEqual(self.num_parser.parse_indian_formatted_number("1,50,000"), 150000.0)
        self.assertEqual(self.num_parser.parse_indian_formatted_number("10,00,000"), 1000000.0)

    def test_crore_parsing(self):
        # 1,00,00,000 -> 10000000
        self.assertEqual(self.num_parser.parse_indian_formatted_number("1,00,00,000"), 10000000.0)
        
    def test_negative_parens(self):
        self.assertEqual(self.num_parser.parse_indian_formatted_number("(50,000)"), -50000.0)

    def test_unit_detection(self):
        self.assertEqual(self.unit_detector.detect_multiplier("Rupees in Lakhs"), 100000.0)
        self.assertEqual(self.unit_detector.detect_multiplier("Rs. in Crores"), 10000000.0)
        self.assertEqual(self.unit_detector.detect_multiplier("(₹ in millions)"), 1000000.0)

    def test_date_parsing_dmy(self):
        d = self.date_parser.parse_date("31-03-2023")
        self.assertEqual(d.year, 2023)
        self.assertEqual(d.month, 3)
        self.assertEqual(d.day, 31)

    def test_mixed_format_fallback(self):
        # US style inside Indian context
        # 100,000.00
        self.assertEqual(self.num_parser.parse_mixed_indian_us_format("100,000.00"), 100000.0)

if __name__ == '__main__':
    unittest.main()
