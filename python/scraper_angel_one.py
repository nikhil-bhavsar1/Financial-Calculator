"""
Angel One API Scraper Module
=============================
Provides company search and stock data from Angel One Smart API.
Angel One is a popular Indian broker with comprehensive API access.
Get API access at: https://www.angelone.in/smartapi

Note: Angel One API requires authentication and provides excellent coverage of Indian markets.
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ANGEL_ONE_API_BASE = "https://apiconnect.angelbroking.com/rest/secure"


@dataclass
class AngelOneCompany:
    """Angel One Company Information"""
    symbol: str
    name: str
    isin: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    face_value: Optional[float] = None
    listing_date: Optional[str] = None
    exchange: str = "ANGEL_ONE"
    token: Optional[str] = None  # Angel One uses tokens for trading
    
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
            'exchange': self.exchange,
            'token': self.token
        }


class AngelOneScraper:
    """
    Scraper for Angel One Smart API.
    Provides company search and stock data for Indian markets.
    Note: Requires Angel One API credentials (API key, client code, and password)
    """
    
    def __init__(self, api_key: Optional[str] = None, client_code: Optional[str] = None,
                 password: Optional[str] = None):
        self.session = requests.Session()
        self.api_key = api_key or os.getenv('ANGEL_ONE_API_KEY')
        self.client_code = client_code or os.getenv('ANGEL_ONE_CLIENT_CODE')
        self.password = password or os.getenv('ANGEL_ONE_PASSWORD')
        self.access_token: Optional[str] = None
        
        if not self.api_key or not self.client_code or not self.password:
            logger.warning("Angel One API credentials not provided. Get access at: https://www.angelone.in/smartapi")
        else:
            # Set headers for Angel One
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-UserType': 'USER',
                'X-SourceID': 'WEB',
                'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
                'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
                'X-MACAddress': 'MAC_ADDRESS',
                'X-PrivateKey': self.api_key
            })
            # Try to authenticate
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Angel One API and get access token"""
        try:
            auth_url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
            
            payload = {
                'clientcode': self.client_code,
                'password': self.password
            }
            
            response = self.session.post(auth_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    self.access_token = data.get('data', {}).get('jwtToken')
                    if self.access_token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.access_token}'
                        })
                        logger.info("Angel One authentication successful")
                        return True
                
            logger.error(f"Angel One authentication failed: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error authenticating with Angel One: {e}")
            return False
    
    def search_companies(self, query: str, limit: int = 10) -> Tuple[List[AngelOneCompany], Optional[str]]:
        """
        Search for companies on Angel One (Indian markets only).
        
        Args:
            query: Company name or symbol to search
            limit: Maximum number of results
            
        Returns:
            Tuple of (List of AngelOneCompany objects, Error message or None)
        """
        if not self.api_key or not self.client_code:
            return [], "Angel One API credentials not configured"
        
        if not self.access_token:
            return [], "Angel One authentication failed"
        
        try:
            # Angel One search API - search across NSE and BSE
            url = f"{ANGEL_ONE_API_BASE}/angelbroking/order/v1/searchScrip"
            
            payload = {
                'exchange': 'NSE',  # Can be NSE, BSE, NFO, etc.
                'searchscrip': query
            }
            
            try:
                response = self.session.post(url, json=payload, timeout=10)
            except requests.Timeout:
                logger.error(f"Angel One search timeout for query: {query}")
                return [], "Angel One Connection Timed Out"
            except requests.ConnectionError:
                logger.error(f"Angel One connection error for query: {query}")
                return [], "Angel One Connection Failed"
            
            if response.status_code != 200:
                logger.warning(f"Angel One search failed: {response.status_code}")
                return [], f"Angel One API Error: HTTP {response.status_code}"
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Angel One returned invalid JSON")
                return [], "Angel One returned invalid data"
            
            # Check for API errors
            if not data.get('status'):
                error_msg = data.get('message', 'Unknown error')
                logger.warning(f"Angel One API error: {error_msg}")
                return [], f"Angel One API error: {error_msg}"
            
            companies = []
            
            # Parse search results
            for symbol_data in data.get('data', [])[:limit]:
                company = AngelOneCompany(
                    symbol=symbol_data.get('tradingsymbol', ''),
                    name=symbol_data.get('name', symbol_data.get('tradingsymbol', '')),
                    isin='',
                    sector='',
                    industry='',
                    exchange=symbol_data.get('exchange', 'ANGEL_ONE'),
                    token=str(symbol_data.get('token', ''))
                )
                companies.append(company)
            
            return companies, None
            
        except Exception as e:
            logger.error(f"Error searching Angel One companies: {e}")
            return [], f"Angel One Internal Error: {str(e)}"
    
    def get_stock_quote(self, symbol: str, token: str, exchange: str = 'NSE') -> Optional[Dict[str, Any]]:
        """
        Get stock quote for a company.
        
        Args:
            symbol: Trading symbol
            token: Symbol token (required by Angel One)
            exchange: Exchange (NSE, BSE, etc.)
            
        Returns:
            Dictionary with stock quote data or None
        """
        if not self.access_token:
            return None
        
        try:
            # Angel One market data API
            url = f"{ANGEL_ONE_API_BASE}/angelbroking/market/v1/quote"
            
            payload = {
                'mode': 'FULL',
                'exchangeTokens': {
                    exchange: [token]
                }
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Check for API errors
            if not data.get('status'):
                return None
            
            quote_data = data.get('data', {}).get('fetched', [{}])[0]
            
            return {
                'symbol': symbol,
                'price': quote_data.get('ltp'),  # Last traded price
                'change': quote_data.get('change'),
                'change_percent': quote_data.get('percentChange'),
                'open': quote_data.get('open'),
                'high': quote_data.get('high'),
                'low': quote_data.get('low'),
                'close': quote_data.get('close'),
                'volume': quote_data.get('volume'),
                'exchange': exchange
            }
            
        except Exception as e:
            logger.error(f"Error getting Angel One stock quote: {e}")
            return None


# Convenience functions
def search_angel_one_companies(query: str, api_key: Optional[str] = None,
                               client_code: Optional[str] = None, password: Optional[str] = None,
                               limit: int = 10) -> Tuple[List[AngelOneCompany], Optional[str]]:
    """Search companies on Angel One"""
    scraper = AngelOneScraper(api_key, client_code, password)
    return scraper.search_companies(query, limit)


def get_angel_one_stock_quote(symbol: str, token: str, exchange: str = 'NSE',
                              api_key: Optional[str] = None, client_code: Optional[str] = None,
                              password: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get stock quote from Angel One"""
    scraper = AngelOneScraper(api_key, client_code, password)
    return scraper.get_stock_quote(symbol, token, exchange)
