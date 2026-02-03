"""
Twelve Data Scraper Module
==========================
Provides company search and stock data from Twelve Data API.
Free tier: 8 API calls per day
Get free API key at: https://twelvedata.com/pricing
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

TWELVE_DATA_BASE = "https://api.twelvedata.com"


@dataclass
class TwelveDataCompany:
    """Twelve Data Company Information"""
    symbol: str
    name: str
    isin: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    face_value: Optional[float] = None
    listing_date: Optional[str] = None
    exchange: str = "TWELVE_DATA"
    
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


class TwelveDataScraper:
    """
    Scraper for Twelve Data API.
    Provides company search and stock data.
    Note: Requires free API key (8 calls/day on free tier)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        self.api_key = api_key or os.getenv('TWELVE_DATA_API_KEY')
        
        if not self.api_key:
            logger.warning("Twelve Data API key not provided. Get free key at: https://twelvedata.com/pricing")
    
    def search_companies(self, query: str, limit: int = 10) -> Tuple[List[TwelveDataCompany], Optional[str]]:
        """
        Search for companies on Twelve Data.
        
        Args:
            query: Company name or symbol to search
            limit: Maximum number of results
            
        Returns:
            Tuple of (List of TwelveDataCompany objects, Error message or None)
        """
        if not self.api_key:
            return [], "Twelve Data API key not configured"
        
        try:
            # Twelve Data symbol search API
            params = {
                'symbol': query,
                'apikey': self.api_key
            }
            
            try:
                response = self.session.get(f"{TWELVE_DATA_BASE}/symbol_search", params=params, timeout=10)
            except requests.Timeout:
                logger.error(f"Twelve Data search timeout for query: {query}")
                return [], "Twelve Data Connection Timed Out"
            except requests.ConnectionError:
                logger.error(f"Twelve Data connection error for query: {query}")
                return [], "Twelve Data Connection Failed"
            
            if response.status_code != 200:
                logger.warning(f"Twelve Data search failed: {response.status_code}")
                return [], f"Twelve Data API Error: HTTP {response.status_code}"
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Twelve Data returned invalid JSON")
                return [], "Twelve Data returned invalid data"
            
            # Check for API limit or error
            if 'code' in data and data['code'] != 200:
                logger.warning(f"Twelve Data API error: {data.get('message', 'Unknown error')}")
                return [], f"Twelve Data API error: {data.get('message', 'Unknown error')}"
            
            companies = []
            
            # Parse search results
            for match in data.get('data', [])[:limit]:
                company = TwelveDataCompany(
                    symbol=match.get('symbol', ''),
                    name=match.get('instrument_name', ''),
                    isin='',  # Twelve Data doesn't provide ISIN
                    sector='',
                    industry='',
                    exchange=match.get('exchange', 'TWELVE_DATA')
                )
                companies.append(company)
            
            return companies, None
            
        except Exception as e:
            logger.error(f"Error searching Twelve Data companies: {e}")
            return [], f"Twelve Data Internal Error: {str(e)}"
    
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
            # Twelve Data price API
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(f"{TWELVE_DATA_BASE}/price", params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Check for API limit or error
            if 'code' in data and data['code'] != 200:
                return None
            
            return {
                'symbol': symbol,
                'price': float(data.get('price', 0)) if data.get('price') else None,
                'exchange': 'TWELVE_DATA'
            }
            
        except Exception as e:
            logger.error(f"Error getting Twelve Data stock quote: {e}")
            return None


# Convenience functions
def search_twelve_data_companies(query: str, api_key: Optional[str] = None, limit: int = 10) -> Tuple[List[TwelveDataCompany], Optional[str]]:
    """Search companies on Twelve Data"""
    scraper = TwelveDataScraper(api_key)
    return scraper.search_companies(query, limit)
