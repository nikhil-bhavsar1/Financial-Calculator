import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Building2, X, Loader2, Check, Globe, TrendingUp, AlertCircle } from 'lucide-react';
import { CompanySearchResult, CompanySearchParams } from '../types';

// Custom debounced callback hook
function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const callbackRef = useRef(callback);
  useEffect(() => {
    callbackRef.current = callback;
  });

  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return useCallback(
    (...args: Parameters<T>) => {
      const timer = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);

      return () => {
        clearTimeout(timer);
      };
    },
    [delay]
  ) as T;
}

interface CompanySearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSearch: (query: string) => void;
  onSelectCompany: (company: CompanySearchResult) => void;
  isSearching: boolean;
  results: CompanySearchResult[];
  exchange: 'NSE' | 'BSE' | 'BOTH';
  onExchangeChange: (exchange: 'NSE' | 'BSE' | 'BOTH') => void;
  error?: string | null;
}

export const CompanySearchModal: React.FC<CompanySearchModalProps> = ({
  isOpen,
  onClose,
  onSearch,
  onSelectCompany,
  isSearching,
  results,
  exchange,
  onExchangeChange,
  error,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Custom debounced search hook
  const debouncedSearch = useDebouncedCallback(
    (query: string) => {
      if (query.trim().length >= 2) {
        onSearch(query);
      }
    },
    500
  );

  useEffect(() => {
    debouncedSearch(searchQuery);
  }, [searchQuery, debouncedSearch]);

  useEffect(() => {
    if (!isOpen) {
      setSearchQuery('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col m-4 border border-gray-200 dark:border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Search Companies</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Find companies on NSE and BSE exchanges
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-800">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by company name or symbol..."
                className="w-full pl-12 pr-4 py-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm transition-all dark:text-white"
                autoFocus
              />
            </div>

            {/* Exchange Selector */}
            <div className="flex items-center gap-2 bg-gray-50 dark:bg-slate-800 rounded-lg p-1 border border-gray-200 dark:border-slate-700">
              {(['NSE', 'BSE', 'BOTH'] as const).map((exc) => (
                <button
                  key={exc}
                  onClick={() => onExchangeChange(exc)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${exchange === exc
                    ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                    }`}
                >
                  {exc}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="px-6 py-3 bg-red-50 dark:bg-red-900/20 border-b border-red-100 dark:border-red-800/50 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          </div>
        )}

        {/* Results */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {isSearching ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : searchQuery.trim().length >= 2 && results.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center px-6">
              <Building2 className="w-16 h-16 text-gray-300 dark:text-slate-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No companies found
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Try adjusting your search query or exchange filter
              </p>
            </div>
          ) : searchQuery.trim().length < 2 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center px-6">
              <Search className="w-16 h-16 text-gray-300 dark:text-slate-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Search for companies
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Enter at least 2 characters to search companies on NSE and BSE
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100 dark:divide-slate-800">
              {results.map((company, index) => (
                <button
                  key={index}
                  onClick={() => onSelectCompany(company)}
                  className="w-full px-6 py-4 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors text-left flex items-center justify-between group"
                >
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-gray-100 to-gray-200 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-base font-semibold text-gray-900 dark:text-white truncate">
                          {company.name}
                        </h4>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${company.exchange === 'NSE'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                          : 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
                          }`}>
                          {company.exchange}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                        <span className="font-mono font-medium">{company.symbol}</span>
                        {company.sector && (
                          <span className="truncate max-w-[200px]">{company.sector}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {company.market_cap && (
                      <div className="text-right mr-4">
                        <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                          <TrendingUp className="w-3 h-3" />
                          <span>Market Cap</span>
                        </div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {(company.market_cap / 10000000).toFixed(2)} Cr
                        </div>
                      </div>
                    )}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <Check className="w-5 h-5 text-green-500" />
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-gray-50 dark:bg-slate-800/50 border-t border-gray-200 dark:border-slate-700 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Globe className="w-3 h-3" />
              {exchange === 'BOTH' ? 'NSE + BSE' : exchange}
            </span>
            {results.length > 0 && (
              <span>
                {results.length} result{results.length !== 1 ? 's' : ''} found
              </span>
            )}
          </div>
          <div>
            Press <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-slate-700 rounded text-[10px] font-mono">Esc</kbd> to close
          </div>
        </div>
      </div>
    </div>
  );
};