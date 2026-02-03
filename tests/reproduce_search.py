
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from scraper_company_search import search_company
except ImportError:
    # Handle running from root vs python dir
    sys.path.append('python')
    from scraper_company_search import search_company

print("Searching for 'triveni turbine'...")
result = search_company('triveni turbine', 'BOTH', 10)

print("\n--- RESULTS ---")
print(f"Companies found: {len(result.get('companies', []))}")
for company in result.get('companies', []):
    print(f"- {company['name']} ({company['symbol']}) [{company['exchange']}]")

print("\n--- ERRORS ---")
for error in result.get('errors', []):
    print(f"- {error}")
