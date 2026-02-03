"""
Unified Company Search Module
=============================
Provides unified interface to search companies using multiple free data sources:
- Yahoo Finance (no API key, unlimited)
- Alpha Vantage (free tier: 25 calls/day, needs API key)
- Twelve Data (free tier: 8 calls/day, needs API key)
- Fyers (Indian broker API, needs credentials)
- Angel One (Indian broker API, needs credentials)
- Local cache (reduces API calls, enables offline access)

Priority order:
1. Check local cache first
2. Try Yahoo Finance (no key needed)
3. Try Alpha Vantage (if API key configured)
4. Try Twelve Data (if API key configured)
5. Try Fyers (if credentials configured)
6. Try Angel One (if credentials configured)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import cache
try:
    from cache_manager import get_cached_results, cache_results
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# Import scrapers
try:
    from scraper_yahoo import YahooFinanceScraper, YahooCompany
    YAHOO_AVAILABLE = True
except ImportError:
    YAHOO_AVAILABLE = False
    YahooFinanceScraper = None
    YahooCompany = None

try:
    from scraper_alpha_vantage import AlphaVantageScraper, AlphaVantageCompany
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    AlphaVantageScraper = None
    AlphaVantageCompany = None

try:
    from scraper_twelve_data import TwelveDataScraper, TwelveDataCompany
    TWELVE_DATA_AVAILABLE = True
except ImportError:
    TWELVE_DATA_AVAILABLE = False
    TwelveDataScraper = None
    TwelveDataCompany = None

try:
    from scraper_fyers import FyersScraper, FyersCompany
    FYERS_AVAILABLE = True
except ImportError:
    FYERS_AVAILABLE = False
    FyersScraper = None
    FyersCompany = None

try:
    from scraper_angel_one import AngelOneScraper, AngelOneCompany
    ANGEL_ONE_AVAILABLE = True
except ImportError:
    ANGEL_ONE_AVAILABLE = False
    AngelOneScraper = None
    AngelOneCompany = None

logger = logging.getLogger(__name__)


class Exchange(Enum):
    """Data source enum"""
    YAHOO = "YAHOO"
    ALPHA_VANTAGE = "ALPHA_VANTAGE"
    TWELVE_DATA = "TWELVE_DATA"
    FYERS = "FYERS"
    ANGEL_ONE = "ANGEL_ONE"
    ALL = "ALL"


@dataclass
class CompanyResult:
    """Unified company search result"""
    name: str
    symbol: str
    isin: str
    exchange: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    face_value: Optional[float] = None
    listing_date: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'symbol': self.symbol,
            'isin': self.isin,
            'exchange': self.exchange,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'face_value': self.face_value,
            'listing_date': self.listing_date,
            'additional_data': self.additional_data or {}
        }


class CompanySearch:
    """
    Unified company search with multiple free sources and caching.
    Provides redundancy and reduces API usage through caching.
    """
    
    def __init__(self, alpha_vantage_key: Optional[str] = None, twelve_data_key: Optional[str] = None,
                 fyers_app_id: Optional[str] = None, fyers_access_token: Optional[str] = None,
                 angel_one_api_key: Optional[str] = None, angel_one_client_code: Optional[str] = None,
                 angel_one_password: Optional[str] = None):
        self.yahoo_scraper = YahooFinanceScraper() if YAHOO_AVAILABLE else None
        self.alpha_vantage_scraper = AlphaVantageScraper(alpha_vantage_key) if ALPHA_VANTAGE_AVAILABLE else None
        self.twelve_data_scraper = TwelveDataScraper(twelve_data_key) if TWELVE_DATA_AVAILABLE else None
        self.fyers_scraper = FyersScraper(fyers_app_id, fyers_access_token) if FYERS_AVAILABLE else None
        self.angel_one_scraper = AngelOneScraper(angel_one_api_key, angel_one_client_code, angel_one_password) if ANGEL_ONE_AVAILABLE else None
        
        if not YAHOO_AVAILABLE:
            logger.warning("Yahoo Finance scraper not available")
        if not ALPHA_VANTAGE_AVAILABLE:
            logger.warning("Alpha Vantage scraper not available")
        if not TWELVE_DATA_AVAILABLE:
            logger.warning("Twelve Data scraper not available")
        if not FYERS_AVAILABLE:
            logger.warning("Fyers scraper not available")
        if not ANGEL_ONE_AVAILABLE:
            logger.warning("Angel One scraper not available")
    
    def search(
        self,
        query: str,
        exchange: Exchange = Exchange.ALL,
        limit: int = 10
    ) -> Tuple[List[CompanyResult], List[str]]:
        """
        Search for companies across multiple sources with caching.
        
        Args:
            query: Company name, symbol, or ISIN to search
            exchange: Which source to search (YAHOO, ALPHA_VANTAGE, TWELVE_DATA, or ALL)
            limit: Maximum number of results
            
        Returns:
            Tuple of (List of CompanyResult objects, List of error messages)
        """
        results = []
        errors = []
        
        # Step 1: Check cache first
        if CACHE_AVAILABLE:
            try:
                from cache_manager import get_cached_results
                cached_results = get_cached_results(query)
                if cached_results:
                    logger.info(f"Returning cached results for: {query}")
                    # Convert cached dicts back to CompanyResult objects
                    for cached in cached_results:
                        result = CompanyResult(
                            name=cached.get('name', ''),
                            symbol=cached.get('symbol', ''),
                            isin=cached.get('isin', ''),
                            exchange=cached.get('exchange', ''),
                            sector=cached.get('sector', ''),
                            industry=cached.get('industry', ''),
                            market_cap=cached.get('market_cap'),
                            face_value=cached.get('face_value'),
                            listing_date=cached.get('listing_date'),
                            additional_data=cached.get('additional_data', {})
                        )
                        results.append(result)
                    return results[:limit], ["Results from cache"]
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        # Step 2: Try Yahoo Finance (no API key needed)
        if exchange in [Exchange.YAHOO, Exchange.ALL] and self.yahoo_scraper:
            try:
                yahoo_companies, yahoo_error = self.yahoo_scraper.search_companies(query, limit)
                
                if yahoo_error:
                    errors.append(f"Yahoo Finance: {yahoo_error}")
                
                for company in yahoo_companies:
                    result = CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='YAHOO',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'yahoo_symbol': company.symbol}
                    )
                    results.append(result)
            except Exception as e:
                logger.error(f"Error searching Yahoo Finance: {e}")
                errors.append(f"Yahoo Finance Error: {str(e)}")
        
        # Step 3: Try Alpha Vantage (if API key configured)
        if exchange in [Exchange.ALPHA_VANTAGE, Exchange.ALL] and self.alpha_vantage_scraper:
            try:
                alpha_companies, alpha_error = self.alpha_vantage_scraper.search_companies(query, limit)
                
                if alpha_error:
                    errors.append(f"Alpha Vantage: {alpha_error}")
                
                for company in alpha_companies:
                    result = CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='ALPHA_VANTAGE',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'alpha_vantage_symbol': company.symbol}
                    )
                    results.append(result)
            except Exception as e:
                logger.error(f"Error searching Alpha Vantage: {e}")
                errors.append(f"Alpha Vantage Error: {str(e)}")
        
        # Step 4: Try Twelve Data (if API key configured)
        if exchange in [Exchange.TWELVE_DATA, Exchange.ALL] and self.twelve_data_scraper:
            try:
                twelve_companies, twelve_error = self.twelve_data_scraper.search_companies(query, limit)
                
                if twelve_error:
                    errors.append(f"Twelve Data: {twelve_error}")
                
                for company in twelve_companies:
                    result = CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='TWELVE_DATA',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'twelve_data_symbol': company.symbol}
                    )
                    results.append(result)
            except Exception as e:
                logger.error(f"Error searching Twelve Data: {e}")
                errors.append(f"Twelve Data Error: {str(e)}")
        
        # Step 5: Try Fyers (if credentials configured)
        if exchange in [Exchange.FYERS, Exchange.ALL] and self.fyers_scraper:
            try:
                fyers_companies, fyers_error = self.fyers_scraper.search_companies(query, limit)
                
                if fyers_error:
                    errors.append(f"Fyers: {fyers_error}")
                
                for company in fyers_companies:
                    result = CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='FYERS',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'fyers_symbol': company.symbol}
                    )
                    results.append(result)
            except Exception as e:
                logger.error(f"Error searching Fyers: {e}")
                errors.append(f"Fyers Error: {str(e)}")
        
        # Step 6: Try Angel One (if credentials configured)
        if exchange in [Exchange.ANGEL_ONE, Exchange.ALL] and self.angel_one_scraper:
            try:
                angel_companies, angel_error = self.angel_one_scraper.search_companies(query, limit)
                
                if angel_error:
                    errors.append(f"Angel One: {angel_error}")
                
                for company in angel_companies:
                    result = CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='ANGEL_ONE',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'angel_one_symbol': company.symbol}
                    )
                    results.append(result)
            except Exception as e:
                logger.error(f"Error searching Angel One: {e}")
                errors.append(f"Angel One Error: {str(e)}")
        
        # Remove duplicates based on symbol (case-insensitive)
        seen_symbols = set()
        unique_results = []
        for result in results:
            symbol_key = result.symbol.lower()
            if symbol_key not in seen_symbols:
                seen_symbols.add(symbol_key)
                unique_results.append(result)
        
        # Step 5: Cache the results
        if CACHE_AVAILABLE and unique_results:
            try:
                from cache_manager import cache_results
                results_to_cache = [r.to_dict() for r in unique_results]
                cache_results(query, results_to_cache)
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
        
        return unique_results[:limit], errors
    
    def get_company_details(
        self,
        symbol: str,
        exchange: Exchange
    ) -> Optional[CompanyResult]:
        """
        Get detailed information about a company.
        
        Args:
            symbol: Stock symbol
            exchange: Which source
            
        Returns:
            CompanyResult object or None
        """
        if exchange == Exchange.YAHOO and self.yahoo_scraper:
            try:
                company = self.yahoo_scraper.get_company_details(symbol)
                if company:
                    return CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='YAHOO',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'yahoo_symbol': company.symbol}
                    )
            except Exception as e:
                logger.error(f"Error getting Yahoo Finance company details: {e}")
        
        elif exchange == Exchange.ALPHA_VANTAGE and self.alpha_vantage_scraper:
            try:
                company = self.alpha_vantage_scraper.get_company_details(symbol)
                if company:
                    return CompanyResult(
                        name=company.name,
                        symbol=company.symbol,
                        isin=company.isin,
                        exchange='ALPHA_VANTAGE',
                        sector=company.sector,
                        industry=company.industry,
                        market_cap=company.market_cap,
                        face_value=company.face_value,
                        listing_date=company.listing_date,
                        additional_data={'alpha_vantage_symbol': company.symbol}
                    )
            except Exception as e:
                logger.error(f"Error getting Alpha Vantage company details: {e}")
        
        return None
    
    def get_stock_quote(
        self,
        symbol: str,
        exchange: Exchange
    ) -> Optional[Dict[str, Any]]:
        """
        Get stock quote for a company.
        
        Args:
            symbol: Stock symbol
            exchange: Which source
            
        Returns:
            Dictionary with stock quote data or None
        """
        if exchange == Exchange.YAHOO and self.yahoo_scraper:
            try:
                return self.yahoo_scraper.get_stock_quote(symbol)
            except Exception as e:
                logger.error(f"Error getting Yahoo Finance quote: {e}")
        
        elif exchange == Exchange.ALPHA_VANTAGE and self.alpha_vantage_scraper:
            try:
                return self.alpha_vantage_scraper.get_stock_quote(symbol)
            except Exception as e:
                logger.error(f"Error getting Alpha Vantage quote: {e}")
        
        elif exchange == Exchange.TWELVE_DATA and self.twelve_data_scraper:
            try:
                return self.twelve_data_scraper.get_stock_quote(symbol)
            except Exception as e:
                logger.error(f"Error getting Twelve Data quote: {e}")
        
        return None


# Convenience functions for external use
def search_company(query: str, exchange: str = "ALL", limit: int = 10) -> Dict[str, Any]:
    """
    Search for companies across multiple sources.
    
    Args:
        query: Company name, symbol, or ISIN
        exchange: 'YAHOO', 'ALPHA_VANTAGE', 'TWELVE_DATA', or 'ALL'
        limit: Maximum results
        
    Returns:
        Dictionary with 'companies' list and 'errors' list
    """
    search = CompanySearch()
    
    if exchange.upper() == "YAHOO":
        exch = Exchange.YAHOO
    elif exchange.upper() == "ALPHA_VANTAGE":
        exch = Exchange.ALPHA_VANTAGE
    elif exchange.upper() == "TWELVE_DATA":
        exch = Exchange.TWELVE_DATA
    else:
        exch = Exchange.ALL
    
    results, errors = search.search(query, exch, limit)
    return {
        'companies': [r.to_dict() for r in results],
        'errors': errors
    }


def get_company_info(symbol: str, exchange: str) -> Optional[Dict[str, Any]]:
    """Get company information"""
    search = CompanySearch()
    
    if exchange.upper() == "YAHOO":
        exch = Exchange.YAHOO
    elif exchange.upper() == "ALPHA_VANTAGE":
        exch = Exchange.ALPHA_VANTAGE
    else:
        return None
    
    result = search.get_company_details(symbol, exch)
    return result.to_dict() if result else None


def get_stock_price(symbol: str, exchange: str) -> Optional[Dict[str, Any]]:
    """Get current stock price"""
    search = CompanySearch()
    
    if exchange.upper() == "YAHOO":
        exch = Exchange.YAHOO
    elif exchange.upper() == "ALPHA_VANTAGE":
        exch = Exchange.ALPHA_VANTAGE
    elif exchange.upper() == "TWELVE_DATA":
        exch = Exchange.TWELVE_DATA
    else:
        return None
    
    return search.get_stock_quote(symbol, exch)
