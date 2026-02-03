"""
Web Search Scraper Module
=========================
Provides web search functionality to find company information
from NSE and BSE websites directly.
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import quote_plus
import re

logger = logging.getLogger(__name__)


@dataclass
class WebSearchResult:
    """Web search result"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'source': self.source,
            'relevance_score': self.relevance_score
        }


class WebSearchScraper:
    """
    Web search scraper for finding company information
    from NSE and BSE websites.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_nse_website(self, query: str, limit: int = 5) -> List[WebSearchResult]:
        """
        Search NSE website for company information.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            # Search NSE companies page
            search_url = f"https://www.nseindia.com/search/autocomplete?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('symbols', [])[:limit]:
                    result = WebSearchResult(
                        title=f"{item.get('name', '')} ({item.get('symbol', '')})",
                        url=f"https://www.nseindia.com/get-quotes/equity?symbol={item.get('symbol', '')}",
                        snippet=f"Symbol: {item.get('symbol', '')}, ISIN: {item.get('isin', '')}, Sector: {item.get('sector', '')}",
                        source='NSE',
                        relevance_score=1.0
                    )
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Error searching NSE website: {e}")
        
        return results
    
    def search_bse_website(self, query: str, limit: int = 5) -> List[WebSearchResult]:
        """
        Search BSE website for company information.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            # Search BSE companies
            search_url = f"https://api.bseindia.com/BseIndiaAPI.api/GetScripData/w?SearchVal={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('scripList', [])[:limit]:
                    result = WebSearchResult(
                        title=f"{item.get('scrip_nm', '')} ({item.get('scrip_cd', '')})",
                        url=f"https://www.bseindia.com/stock-share-price/{item.get('scrip_cd', '')}/{item.get('scrip_nm', '').replace(' ', '-')}/",
                        snippet=f"Scrip Code: {item.get('scrip_cd', '')}, ISIN: {item.get('isin', '')}, Sector: {item.get('sector', '')}",
                        source='BSE',
                        relevance_score=1.0
                    )
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Error searching BSE website: {e}")
        
        return results
    
    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Search for comprehensive company information
        from both NSE and BSE.
        
        Args:
            company_name: Company name to search
            
        Returns:
            Dictionary with search results
        """
        results = {
            'query': company_name,
            'nse_results': [],
            'bse_results': [],
            'combined': []
        }
        
        # Search NSE
        nse_results = self.search_nse_website(company_name)
        results['nse_results'] = [r.to_dict() for r in nse_results]
        
        # Search BSE
        bse_results = self.search_bse_website(company_name)
        results['bse_results'] = [r.to_dict() for r in bse_results]
        
        # Combine and deduplicate
        all_results = nse_results + bse_results
        seen_titles = set()
        unique_results = []
        
        for result in all_results:
            if result.title not in seen_titles:
                seen_titles.add(result.title)
                unique_results.append(result.to_dict())
        
        results['combined'] = unique_results
        results['total_results'] = len(unique_results)
        
        return results
    
    def get_company_url(self, symbol: str, exchange: str) -> Optional[str]:
        """
        Get direct URL to company page.
        
        Args:
            symbol: Stock symbol
            exchange: 'NSE' or 'BSE'
            
        Returns:
            URL string or None
        """
        if exchange.upper() == 'NSE':
            return f"https://www.nseindia.com/get-quotes/equity?symbol={symbol.upper()}"
        elif exchange.upper() == 'BSE':
            return f"https://www.bseindia.com/stock-share-price/{symbol}/"
        return None


# Convenience functions
def search_company_web(company_name: str) -> Dict[str, Any]:
    """
    Search for company information on web.
    
    Args:
        company_name: Company name to search
        
    Returns:
        Dictionary with search results from NSE and BSE
    """
    scraper = WebSearchScraper()
    return scraper.search_company_info(company_name)


def get_nse_company_url(symbol: str) -> str:
    """Get NSE company page URL"""
    return f"https://www.nseindia.com/get-quotes/equity?symbol={symbol.upper()}"


def get_bse_company_url(scrip_code: str) -> str:
    """Get BSE company page URL"""
    return f"https://www.bseindia.com/stock-share-price/{scrip_code}/"
