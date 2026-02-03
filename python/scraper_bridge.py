"""
Scraper Bridge Module
=====================
Bridge between Python scrapers and frontend.
Exposes scraper functions via Tauri commands.
"""

import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Import scrapers
try:
    from scraper_company_search import CompanySearch, Exchange, search_company, get_company_info, get_stock_price
    from scraper_web_search import WebSearchScraper, search_company_web
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Scrapers not available: {e}")
    SCRAPERS_AVAILABLE = False
    CompanySearch = None
    Exchange = None

try:
    from database import db
except ImportError:
    db = None
    logger.error("Database module not found")


class ScraperBridge:
    """
    Bridge class to expose scraper functionality to frontend.
    All methods return JSON-serializable dictionaries.
    """
    
    def __init__(self):
        self.company_search = CompanySearch() if SCRAPERS_AVAILABLE else None
        self.web_search = WebSearchScraper() if SCRAPERS_AVAILABLE else None
    
    def search_companies(self, query: str, exchange: str = "BOTH", limit: int = 10) -> Dict[str, Any]:
        """
        Search for companies across NSE and BSE.
        
        Args:
            query: Company name, symbol, or ISIN
            exchange: 'NSE', 'BSE', or 'BOTH'
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results
        """
        if not SCRAPERS_AVAILABLE or not self.company_search:
            return {
                'success': False,
                'error': 'Scrapers not available',
                'results': []
            }
        
        try:
            # Map exchange string to enum
            if exchange.upper() == "NSE":
                exch = Exchange.NSE
            elif exchange.upper() == "BSE":
                exch = Exchange.BSE
            else:
                exch = Exchange.BOTH
            
            # Perform search
            results, errors = self.company_search.search(query, exch, limit)
            
            # Log to DB
            if db:
                try:
                    db.save_scraper_result(query, 'BOTH', 'SEARCH', {
                        'results': [r.to_dict() for r in results],
                        'errors': errors
                    })
                except Exception as db_err:
                    logger.error(f"DB Log Error: {db_err}")

            return {
                'success': True,
                'query': query,
                'exchange': exchange,
                'count': len(results),
                'results': [r.to_dict() for r in results],
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error in search_companies: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_company_details(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Get detailed information about a company.
        
        Args:
            symbol: Stock symbol or scrip code
            exchange: 'NSE' or 'BSE'
            
        Returns:
            Dictionary with company details
        """
        if not SCRAPERS_AVAILABLE or not self.company_search:
            return {
                'success': False,
                'error': 'Scrapers not available'
            }
        
        try:
            # Map exchange string to enum
            if exchange.upper() == "NSE":
                exch = Exchange.NSE
            elif exchange.upper() == "BSE":
                exch = Exchange.BSE
            else:
                return {
                    'success': False,
                    'error': 'Invalid exchange. Use NSE or BSE'
                }
            
            # Get company details
            result = self.company_search.get_company_details(symbol, exch)
            
            if result:
                # Log to DB
                if db:
                    try:
                        db.save_scraper_result(symbol, exchange, 'DETAILS', result.to_dict())
                    except Exception as db_err:
                        logger.error(f"DB Log Error: {db_err}")
                        
                return {
                    'success': True,
                    'company': result.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': f'Company not found: {symbol}'
                }
                
        except Exception as e:
            logger.error(f"Error in get_company_details: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stock_quote(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Get current stock quote.
        
        Args:
            symbol: Stock symbol or scrip code
            exchange: 'NSE' or 'BSE'
            
        Returns:
            Dictionary with stock quote
        """
        if not SCRAPERS_AVAILABLE or not self.company_search:
            return {
                'success': False,
                'error': 'Scrapers not available'
            }
        
        try:
            # Map exchange string to enum
            if exchange.upper() == "NSE":
                exch = Exchange.NSE
            elif exchange.upper() == "BSE":
                exch = Exchange.BSE
            else:
                return {
                    'success': False,
                    'error': 'Invalid exchange. Use NSE or BSE'
                }
            
            # Get stock quote
            quote = self.company_search.get_stock_quote(symbol, exch)
            
            if quote:
                # Log to DB
                if db:
                    try:
                        db.save_scraper_result(symbol, exchange, 'QUOTE', quote)
                    except Exception as db_err:
                        logger.error(f"DB Log Error: {db_err}")
                        
                return {
                    'success': True,
                    'quote': quote
                }
            else:
                return {
                    'success': False,
                    'error': f'Quote not found for: {symbol}'
                }
                
        except Exception as e:
            logger.error(f"Error in get_stock_quote: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Search for company information on web.
        
        Args:
            query: Company name to search
            
        Returns:
            Dictionary with web search results
        """
        if not SCRAPERS_AVAILABLE or not self.web_search:
            return {
                'success': False,
                'error': 'Web search not available',
                'results': []
            }
        
        try:
            # Perform web search
            results = self.web_search.search_company_info(query)
            
            # Log to DB
            if db:
                try:
                    db.save_scraper_result(query, 'WEB', 'SEARCH', results)
                except Exception as db_err:
                    logger.error(f"DB Log Error: {db_err}")
            
            return {
                'success': True,
                'query': query,
                'nse_count': len(results.get('nse_results', [])),
                'bse_count': len(results.get('bse_results', [])),
                'total_count': results.get('total_results', 0),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in search_web: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_exchanges_status(self) -> Dict[str, Any]:
        """
        Get status of exchange scrapers.
        
        Returns:
            Dictionary with availability status
        """
        return {
            'success': True,
            'scrapers_available': SCRAPERS_AVAILABLE,
            'nse_available': SCRAPERS_AVAILABLE,
            'bse_available': SCRAPERS_AVAILABLE,
            'web_search_available': SCRAPERS_AVAILABLE
        }


# Global bridge instance
_bridge = None

def get_bridge() -> ScraperBridge:
    """Get or create scraper bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = ScraperBridge()
    return _bridge


# Convenience functions for direct calling
def search_companies_bridge(query: str, exchange: str = "BOTH", limit: int = 10) -> str:
    """
    Search companies - returns JSON string for Tauri.
    
    Args:
        query: Search query
        exchange: Exchange to search (NSE/BSE/BOTH)
        limit: Maximum results
        
    Returns:
        JSON string with results
    """
    bridge = get_bridge()
    result = bridge.search_companies(query, exchange, limit)
    return json.dumps(result, ensure_ascii=False)


def get_company_details_bridge(symbol: str, exchange: str) -> str:
    """
    Get company details - returns JSON string for Tauri.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange (NSE/BSE)
        
    Returns:
        JSON string with company details
    """
    bridge = get_bridge()
    result = bridge.get_company_details(symbol, exchange)
    return json.dumps(result, ensure_ascii=False)


def get_stock_quote_bridge(symbol: str, exchange: str) -> str:
    """
    Get stock quote - returns JSON string for Tauri.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange (NSE/BSE)
        
    Returns:
        JSON string with stock quote
    """
    bridge = get_bridge()
    result = bridge.get_stock_quote(symbol, exchange)
    return json.dumps(result, ensure_ascii=False)


def search_web_bridge(query: str) -> str:
    """
    Web search - returns JSON string for Tauri.
    
    Args:
        query: Search query
        
    Returns:
        JSON string with web search results
    """
    bridge = get_bridge()
    result = bridge.search_web(query)
    return json.dumps(result, ensure_ascii=False)


def get_scraper_status_bridge() -> str:
    """
    Get scraper status - returns JSON string for Tauri.
    
    Returns:
        JSON string with status
    """
    bridge = get_bridge()
    result = bridge.get_exchanges_status()
    return json.dumps(result, ensure_ascii=False)
