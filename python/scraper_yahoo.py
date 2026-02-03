"""
Yahoo Finance Scraper Module
============================
Provides company search and stock data from Yahoo Finance.
Used as a fallback when NSE/BSE scrapers fail.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

YAHOO_FINANCE_BASE = "https://query1.finance.yahoo.com"
YAHOO_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
}


@dataclass
class YahooCompany:
    """Yahoo Finance Company Information"""
    symbol: str
    name: str
    isin: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    face_value: Optional[float] = None
    listing_date: Optional[str] = None
    exchange: str = "YAHOO"
    
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


class YahooFinanceScraper:
    """
    Scraper for Yahoo Finance data.
    Provides company search and stock data as fallback for NSE/BSE.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(YAHOO_HEADERS)
    
    def search_companies(self, query: str, limit: int = 10) -> Tuple[List[YahooCompany], Optional[str]]:
        """
        Search for companies on Yahoo Finance.
        
        Args:
            query: Company name or symbol to search
            limit: Maximum number of results
            
        Returns:
            Tuple of (List of YahooCompany objects, Error message or None)
        """
        try:
            # Yahoo Finance search API
            url = f"{YAHOO_FINANCE_BASE}/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': limit,
                'newsCount': 0,
                'enableFuzzyQuery': 'true',
                'quotesQueryId': 'tss_match_phrase_query'
            }
            
            try:
                response = self.session.get(url, params=params, timeout=10)
            except requests.Timeout:
                logger.error(f"Yahoo Finance search timeout for query: {query}")
                return [], "Yahoo Finance Connection Timed Out"
            except requests.ConnectionError:
                logger.error(f"Yahoo Finance connection error for query: {query}")
                return [], "Yahoo Finance Connection Failed"
            
            if response.status_code != 200:
                logger.warning(f"Yahoo Finance search failed: {response.status_code}")
                return [], f"Yahoo Finance API Error: HTTP {response.status_code}"
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Yahoo Finance returned invalid JSON")
                return [], "Yahoo Finance returned invalid data"
            
            companies = []
            
            # Parse search results
            for quote in data.get('quotes', [])[:limit]:
                # Only include equities (stocks)
                if quote.get('quoteType') not in ['EQUITY', 'ETF']:
                    continue
                    
                company = YahooCompany(
                    symbol=quote.get('symbol', ''),
                    name=quote.get('shortname') or quote.get('longname') or quote.get('symbol', ''),
                    isin='',  # Yahoo doesn't provide ISIN in search results
                    sector=quote.get('sector', ''),
                    industry=quote.get('industry', ''),
                    exchange=quote.get('exchange', 'YAHOO')
                )
                companies.append(company)
            
            return companies, None
            
        except Exception as e:
            logger.error(f"Error searching Yahoo Finance companies: {e}")
            return [], f"Yahoo Finance Internal Error: {str(e)}"
    
    def get_company_details(self, symbol: str) -> Optional[YahooCompany]:
        """
        Get detailed information about a company.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            YahooCompany object or None
        """
        try:
            # Yahoo Finance quote summary API
            url = f"{YAHOO_FINANCE_BASE}/v10/finance/quoteSummary/{symbol}"
            params = {
                'modules': 'assetProfile,summaryDetail'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            result = data.get('quoteSummary', {}).get('result', [{}])[0]
            
            if not result:
                return None
            
            profile = result.get('assetProfile', {})
            summary = result.get('summaryDetail', {})
            
            return YahooCompany(
                symbol=symbol,
                name=profile.get('longBusinessSummary', '')[:50] or symbol,
                isin='',
                sector=profile.get('sector', ''),
                industry=profile.get('industry', ''),
                market_cap=summary.get('marketCap', {}).get('raw') if isinstance(summary.get('marketCap'), dict) else None
            )
            
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance company details: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock quote for a company.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock quote data or None
        """
        try:
            # Yahoo Finance quote API
            url = f"{YAHOO_FINANCE_BASE}/v8/finance/chart/{symbol}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            result = data.get('chart', {}).get('result', [{}])[0]
            
            if not result:
                return None
            
            meta = result.get('meta', {})
            
            return {
                'symbol': symbol,
                'price': meta.get('regularMarketPrice'),
                'change': meta.get('regularMarketChange'),
                'change_percent': meta.get('regularMarketChangePercent'),
                'open': meta.get('regularMarketOpen'),
                'high': meta.get('regularMarketDayHigh'),
                'low': meta.get('regularMarketDayLow'),
                'previous_close': meta.get('previousClose'),
                'volume': meta.get('regularMarketVolume'),
                'exchange': meta.get('exchangeName', 'YAHOO')
            }
            
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance stock quote: {e}")
            return None


# Convenience functions
def search_yahoo_companies(query: str, limit: int = 10) -> Tuple[List[YahooCompany], Optional[str]]:
    """Search companies on Yahoo Finance"""
    scraper = YahooFinanceScraper()
    return scraper.search_companies(query, limit)


def get_yahoo_company_info(symbol: str) -> Optional[YahooCompany]:
    """Get company information from Yahoo Finance"""
    scraper = YahooFinanceScraper()
    return scraper.get_company_details(symbol)
