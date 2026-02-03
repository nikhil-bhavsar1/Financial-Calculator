"""
Local Cache Module
==================
Simple JSON-based caching system for company search results.
Reduces API calls and enables offline access to previously searched companies.
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_FILE = CACHE_DIR / "company_search_cache.json"
CACHE_DURATION = 86400  # 24 hours in seconds


class CompanySearchCache:
    """
    Simple JSON-based cache for company search results.
    Caches search queries and their results to reduce API calls.
    """
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_file = CACHE_FILE
        self.cache_duration = CACHE_DURATION
        self._cache: Dict[str, Any] = {}
        self._ensure_cache_dir()
        self._load_cache()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating cache directory: {e}")
    
    def _load_cache(self):
        """Load cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded {len(self._cache)} cached search results")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self._cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def get(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached results for a query.
        
        Args:
            query: Search query string
            
        Returns:
            List of cached company results or None if not found/expired
        """
        query_key = query.lower().strip()
        
        if query_key not in self._cache:
            return None
        
        entry = self._cache[query_key]
        timestamp = entry.get('timestamp', 0)
        
        # Check if cache entry is expired
        if time.time() - timestamp > self.cache_duration:
            logger.info(f"Cache expired for query: {query}")
            del self._cache[query_key]
            self._save_cache()
            return None
        
        logger.info(f"Cache hit for query: {query}")
        return entry.get('results', [])
    
    def set(self, query: str, results: List[Dict[str, Any]]):
        """
        Cache results for a query.
        
        Args:
            query: Search query string
            results: List of company results to cache
        """
        query_key = query.lower().strip()
        
        self._cache[query_key] = {
            'timestamp': time.time(),
            'results': results
        }
        
        self._save_cache()
        logger.info(f"Cached {len(results)} results for query: {query}")
    
    def clear(self):
        """Clear all cached results"""
        self._cache = {}
        self._save_cache()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self._cache)
        expired_entries = 0
        
        current_time = time.time()
        for key, entry in list(self._cache.items()):
            timestamp = entry.get('timestamp', 0)
            if current_time - timestamp > self.cache_duration:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'valid_entries': total_entries - expired_entries,
            'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0
        }


# Global cache instance
_cache_instance: Optional[CompanySearchCache] = None


def get_cache() -> CompanySearchCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CompanySearchCache()
    return _cache_instance


def get_cached_results(query: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached results for a query"""
    cache = get_cache()
    return cache.get(query)


def cache_results(query: str, results: List[Dict[str, Any]]):
    """Cache results for a query"""
    cache = get_cache()
    cache.set(query, results)


def clear_cache():
    """Clear all cached results"""
    cache = get_cache()
    cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    cache = get_cache()
    return cache.get_stats()
