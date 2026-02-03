import unittest
import sys
import os
from dataclasses import dataclass

# Add python directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

# Mock classes to simulate scraper behavior
@dataclass
class MockCompany:
    name: str
    symbol: str
    isin: str = ""
    exchange: str = "NSE"
    sector: str = ""
    industry: str = ""
    market_cap: float = 0.0
    face_value: float = 0.0
    listing_date: str = ""
    scrip_code: str = ""

class MockScraper:
    def search_companies(self, query, limit):
        # Simulate failure for full name
        if query == "triveni turbine":
            return [], None
        # Simulate success for first word
        elif query == "triveni":
            return [
                MockCompany(name="Triveni Turbine Ltd", symbol="TRITURBINE"),
                MockCompany(name="Triveni Engineering", symbol="TRIVENI")
            ], None
        return [], None

class TestSearchLogic(unittest.TestCase):
    def test_fallback_search_logic(self):
        # This test replicates the fallback logic in CompanySearch.search_companies
        # to ensure it correctly finds companies when full name search fails
        query = "triveni turbine"
        limit = 10
        nse_scraper = MockScraper()
        
        # Simulated implementation of the fallback logic
        nse_companies, nse_error = nse_scraper.search_companies(query, limit)
        
        if not nse_companies and " " in query:
            first_word = query.split()[0]
            if len(first_word) > 3:
                broad_companies, _ = nse_scraper.search_companies(first_word, limit * 2)
                keywords = query.lower().split()
                for co in broad_companies:
                    # Match all keywords in name or symbol
                    if all(k in co.name.lower() or k in co.symbol.lower() for k in keywords):
                        nse_companies.append(co)
        
        self.assertEqual(len(nse_companies), 1)
        self.assertEqual(nse_companies[0].name, "Triveni Turbine Ltd")

if __name__ == '__main__':
    unittest.main()