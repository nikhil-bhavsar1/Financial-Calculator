"""
Fyers API Scraper Module
=========================
Provides company search and stock data from Fyers API.
Fyers is an Indian discount broker with API access.
Get API access at: https://fyers.in/api/

Note: Fyers API requires authentication and is primarily for Indian markets (NSE, BSE).
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

FYERS_API_BASE = "https://api.fyers.in/api/v2"


@dataclass
class FyersCompany:
    """Fyers Company Information"""
    symbol: str
    name: str
    isin: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    face_value: Optional[float] = None
    listing_date: Optional[str] = None
    exchange: str = "FYERS"
    
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


class FyersScraper:
    """
    Scraper for Fyers API.
    Provides company search and stock data for Indian markets.
    Note: Requires Fyers API credentials (app ID and access token)
    """
    
    def __init__(self, app_id: Optional[str] = None, access_token: Optional[str] = None):
        self.session = requests.Session()
        self.app_id = app_id or os.getenv('FYERS_APP_ID')
        self.access_token = access_token or os.getenv('FYERS_ACCESS_TOKEN')
        
        if not self.app_id or not self.access_token:
            logger.warning("Fyers API credentials not provided. Get access at: https://fyers.in/api/")
        else:
            # Set authorization header
            self.session.headers.update({
                'Authorization': f'{self.app_id}:{self.access_token}',
                'Content-Type': 'application/json'
            })
    
    def search_companies(self, query: str, limit: int = 10) -> Tuple[List[FyersCompany], Optional[str]]:
        """
        Search for companies on Fyers (Indian markets only).
        
        Args:
            query: Company name or symbol to search
            limit: Maximum number of results
            
        Returns:
            Tuple of (List of FyersCompany objects, Error message or None)
        """
        if not self.app_id or not self.access_token:
            return [], "Fyers API credentials not configured"
        
        try:
            # Fyers search API - search across NSE and BSE
            url = f"{FYERS_API_BASE}/search-symbols"
            params = {
                'q': query,
                'limit': limit
            }
            
            try:
                response = self.session.get(url, params=params, timeout=10)
            except requests.Timeout:
                logger.error(f"Fyers search timeout for query: {query}")
                return [], "Fyers Connection Timed Out"
            except requests.ConnectionError:
                logger.error(f"Fyers connection error for query: {query}")
                return [], "Fyers Connection Failed"
            
            if response.status_code != 200:
                logger.warning(f"Fyers search failed: {response.status_code}")
                return [], f"Fyers API Error: HTTP {response.status_code}"
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Fyers returned invalid JSON")
                return [], "Fyers returned invalid data"
            
            # Check for API errors
            if data.get('s') == 'error':
                error_msg = data.get('message', 'Unknown error')
                logger.warning(f"Fyers API error: {error_msg}")
                return [], f"Fyers API error: {error_msg}"
            
            companies = []
            
            # Parse search results
            for symbol_data in data.get('d', [])[:limit]:
                company = FyersCompany(
                    symbol=symbol_data.get('n', ''),  # Symbol name
                    name=symbol_data.get('n', ''),  # Fyers uses symbol as name in search
                    isin='',  # Fyers doesn't provide ISIN in search
                    sector='',
                    industry='',
                    exchange=symbol_data.get('e', 'FYERS')  # Exchange (NSE, BSE, etc.)
                )
                companies.append(company)
            
            return companies, None
            
        except Exception as e:
            logger.error(f"Error searching Fyers companies: {e}")
            return [], f"Fyers Internal Error: {str(e)}"
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock quote for a company.
        
        Args:
            symbol: Stock symbol (e.g., "NSE:RELIANCE-EQ")
            
        Returns:
            Dictionary with stock quote data or None
        """
        if not self.app_id or not self.access_token:
            return None
        
        try:
            # Fyers quotes API
            url = f"{FYERS_API_BASE}/quotes"
            params = {
                'symbols': symbol
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Check for API errors
            if data.get('s') == 'error':
                return None
            
            quote_data = data.get('d', [{}])[0]
            
            return {
                'symbol': symbol,
                'price': quote_data.get('v', {}).get('lp'),  # Last price
                'change': quote_data.get('v', {}).get('ch'),  # Change
                'change_percent': quote_data.get('v', {}).get('chp'),  # Change percent
                'open': quote_data.get('v', {}).get('o'),  # Open
                'high': quote_data.get('v', {}).get('h'),  # High
                'low': quote_data.get('v', {}).get('l'),  # Low
                'volume': quote_data.get('v', {}).get('v'),  # Volume
                'exchange': 'FYERS'
            }
            
        except Exception as e:
            logger.error(f"Error getting Fyers stock quote: {e}")
            return None


# Convenience functions
def search_fyers_companies(query: str, app_id: Optional[str] = None, 
                           access_token: Optional[str] = None, limit: int = 10) -> Tuple[List[FyersCompany], Optional[str]]:
    """Search companies on Fyers"""
    scraper = FyersScraper(app_id, access_token)
    return scraper.search_companies(query, limit)


def get_fyers_stock_quote(symbol: str, app_id: Optional[str] = None, 
                          access_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get stock quote from Fyers"""
    scraper = FyersScraper(app_id, access_token)
    return scraper.get_stock_quote(symbol)
