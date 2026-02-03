"""
Alpha Vantage Scraper Module
=============================
Provides company search and stock data from Alpha Vantage API.
Free tier: 25 API calls per day
Get free API key at: https://www.alphavantage.co/support/#api-key
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"


@dataclass
class AlphaVantageCompany:
    """Alpha Vantage Company Information"""
    symbol: str
    name: str
    isin: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    face_value: Optional[float] = None
    listing_date: Optional[str] = None
    exchange: str = "ALPHA_VANTAGE"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'isin': self.isin,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'face_value': self.face_value,
            'listing_date': self.listing_date,
            'exchange': self.exchange
        }


class AlphaVantageScraper:
    """
    Scraper for Alpha Vantage API.
    Provides company search and stock data.
    Note: Requires free API key (25 calls/day on free tier)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        
        if not self.api_key:
            logger.warning("Alpha Vantage API key not provided. Get free key at: https://www.alphavantage.co/support/#api-key")
    
    def search_companies(self, query: str, limit: int = 10) -> Tuple[List[AlphaVantageCompany], Optional[str]]:
        """
        Search for companies on Alpha Vantage.
        
        Args:
            query: Company name or symbol to search
            limit: Maximum number of results
            
        Returns:
            Tuple of (List of AlphaVantageCompany objects, Error message or None)
        """
        if not self.api_key:
            return [], "Alpha Vantage API key not configured"
        
        try:
            # Alpha Vantage symbol search API
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': query,
                'apikey': self.api_key
            }
            
            try:
                response = self.session.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            except requests.Timeout:
                logger.error(f"Alpha Vantage search timeout for query: {query}")
                return [], "Alpha Vantage Connection Timed Out"
            except requests.ConnectionError:
                logger.error(f"Alpha Vantage connection error for query: {query}")
                return [], "Alpha Vantage Connection Failed"
            
            if response.status_code != 200:
                logger.warning(f"Alpha Vantage search failed: {response.status_code}")
                return [], f"Alpha Vantage API Error: HTTP {response.status_code}"
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Alpha Vantage returned invalid JSON")
                return [], "Alpha Vantage returned invalid data"
            
            # Check for API limit message
            if 'Note' in data and 'API call frequency' in data['Note']:
                logger.warning(f"Alpha Vantage API limit reached: {data['Note']}")
                return [], "Alpha Vantage API limit reached (25 calls/day on free tier)"
            
            companies = []
            
            # Parse search results
            for match in data.get('bestMatches', [])[:limit]:
                company = AlphaVantageCompany(
                    symbol=match.get('1. symbol', ''),
                    name=match.get('2. name', ''),
                    isin='',  # Alpha Vantage doesn't provide ISIN
                    sector='',
                    industry='',
                    exchange=match.get('4. region', 'ALPHA_VANTAGE')
                )
                companies.append(company)
            
            return companies, None
            
        except Exception as e:
            logger.error(f"Error searching Alpha Vantage companies: {e}")
            return [], f"Alpha Vantage Internal Error: {str(e)}"
    
    def get_company_details(self, symbol: str) -> Optional[AlphaVantageCompany]:
        """
        Get detailed information about a company.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            AlphaVantageCompany object or None
        """
        if not self.api_key:
            return None
        
        try:
            # Alpha Vantage company overview API
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Check for API limit or error
            if 'Note' in data or 'Error Message' in data:
                return None
            
            return AlphaVantageCompany(
                symbol=symbol,
                name=data.get('Name', symbol),
                isin='',
                sector=data.get('Sector', ''),
                industry=data.get('Industry', ''),
                market_cap=float(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else None
            )
            
        except Exception as e:
            logger.error(f"Error getting Alpha Vantage company details: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock quote for a company.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock quote data or None
        """
        if not self.api_key:
            return None
        
        try:
            # Alpha Vantage global quote API
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(ALPHA_VANTAGE_BASE, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Check for API limit or error
            if 'Note' in data or 'Error Message' in data:
                return None
            
            quote = data.get('Global Quote', {})
            
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)) if quote.get('05. price') else None,
                'change': float(quote.get('09. change', 0)) if quote.get('09. change') else None,
                'change_percent': quote.get('10. change percent', '').replace('%', '') if quote.get('10. change percent') else None,
                'volume': int(quote.get('06. volume', 0)) if quote.get('06. volume') else None,
                'exchange': 'ALPHA_VANTAGE'
            }
            
        except Exception as e:
            logger.error(f"Error getting Alpha Vantage stock quote: {e}")
            return None


# Convenience functions
def search_alpha_vantage_companies(query: str, api_key: Optional[str] = None, limit: int = 10) -> Tuple[List[AlphaVantageCompany], Optional[str]]:
    """Search companies on Alpha Vantage"""
    scraper = AlphaVantageScraper(api_key)
    return scraper.search_companies(query, limit)


def get_alpha_vantage_company_info(symbol: str, api_key: Optional[str] = None) -> Optional[AlphaVantageCompany]:
    """Get company information from Alpha Vantage"""
    scraper = AlphaVantageScraper(api_key)
    return scraper.get_company_details(symbol)
