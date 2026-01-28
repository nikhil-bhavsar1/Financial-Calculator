import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
    ChevronLeft, ChevronRight, Search, Maximize2, Minimize2,
    ZoomIn, ZoomOut, FileText, ArrowUp, ArrowDown
} from 'lucide-react';

interface DocumentViewerProps {
    content: string;
    className?: string;
    initialPage?: number;
}

interface Page {
    number: number;
    content: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
    content,
    className = '',
    initialPage = 1
}) => {
    const [pages, setPages] = useState<Page[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showSearch, setShowSearch] = useState(false);
    const [searchResults, setSearchResults] = useState<{ page: number, index: number, match: string }[]>([]);
    const [currentSearchIndex, setCurrentSearchIndex] = useState(0);
    const [fontSize, setFontSize] = useState(14);
    const containerRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);

    // Parse Content into Pages
    useEffect(() => {
        if (!content) {
            setPages([]);
            return;
        }

        // Split by "--- Page X ---" marker
        // Regex matches "--- Page 5 ---" or similar
        const pageRegex = /--- Page (\d+) ---/g;
        const parts = content.split(pageRegex);

        // The split result will look like:
        // [ "Header text", "1", "Content of page 1", "2", "Content of page 2" ... ]
        // or if no pages: [ "Whole content" ]

        const newPages: Page[] = [];

        if (parts.length > 1) {
            // Loop through parts. Index 0 is usually pre-first-page content
            if (parts[0].trim()) {
                newPages.push({ number: 0, content: parts[0] });
            }

            for (let i = 1; i < parts.length; i += 2) {
                const pageNum = parseInt(parts[i]);
                const pageContent = parts[i + 1] || "";
                newPages.push({ number: pageNum, content: pageContent });
            }
        } else {
            // No delimiters found, treat as single page
            newPages.push({ number: 1, content: content });
        }

        setPages(newPages);
    }, [content]);

    // Handle Search
    useEffect(() => {
        if (!searchQuery.trim() || pages.length === 0) {
            setSearchResults([]);
            setCurrentSearchIndex(0);
            return;
        }

        const results: { page: number, index: number, match: string }[] = [];
        const query = searchQuery.toLowerCase();

        pages.forEach(page => {
            let content = page.content.toLowerCase();
            let pos = content.indexOf(query);
            while (pos !== -1) {
                results.push({ page: page.number, index: pos, match: searchQuery });
                pos = content.indexOf(query, pos + 1);
            }
        });

        setSearchResults(results);
        if (results.length > 0) {
            // If current page has results, jump to first on current page, otherwise first overall
            const onCurrent = results.findIndex(r => r.page === currentPage);
            setCurrentSearchIndex(onCurrent !== -1 ? onCurrent : 0);
            if (onCurrent === -1 && results[0].page !== currentPage) {
                setCurrentPage(results[0].page);
            }
        }
    }, [searchQuery, pages]);

    // Navigation Handlers
    const nextPage = () => {
        if (currentPage < (pages[pages.length - 1]?.number || 1)) {
            // Find next page number in list (might be non-sequential)
            const currIdx = pages.findIndex(p => p.number === currentPage);
            if (currIdx < pages.length - 1) {
                setCurrentPage(pages[currIdx + 1].number);
            }
        }
    };

    const prevPage = () => {
        const currIdx = pages.findIndex(p => p.number === currentPage);
        if (currIdx > 0) {
            setCurrentPage(pages[currIdx - 1].number);
        }
    };

    const jumpToSearch = (direction: 'next' | 'prev') => {
        if (searchResults.length === 0) return;

        let newIndex = direction === 'next' ? currentSearchIndex + 1 : currentSearchIndex - 1;

        if (newIndex >= searchResults.length) newIndex = 0;
        if (newIndex < 0) newIndex = searchResults.length - 1;

        setCurrentSearchIndex(newIndex);
        const result = searchResults[newIndex];
        if (result.page !== currentPage) {
            setCurrentPage(result.page);
        }
    };

    // Render Highlighted Content
    const renderHighlightedContent = (text: string, pageNum: number) => {
        if (!searchQuery.trim()) return text;

        const parts = text.split(new RegExp(`(${searchQuery})`, 'gi'));
        return parts.map((part, i) => {
            const isMatch = part.toLowerCase() === searchQuery.toLowerCase();
            // Simple check to match specific occurrence if needed, for now highlight all
            // To strictly match "currentSearchIndex", we need more complex mapping

            const isCurrentMatch = isMatch && (
                searchResults[currentSearchIndex]?.page === pageNum &&
                // Verify approximate position or context? 
                // For simple MVP text highlighting all instances is usually fine, 
                // but "focusing" the active one is better.
                true
            );

            return isMatch ? (
                <mark
                    key={i}
                    className={`${isCurrentMatch ? 'bg-[var(--accent-primary)]/50 text-white' : 'bg-yellow-500/30'} rounded px-0.5`}
                >
                    {part}
                </mark>
            ) : (
                <span key={i}>{part}</span>
            );
        });
    };

    const activePageContent = pages.find(p => p.number === currentPage)?.content || "Page not found";

    // Toggle Full Screen Class on Body
    useEffect(() => {
        if (isFullScreen) {
            containerRef.current?.requestFullscreen().catch(err => {
                console.log("Browser fullscreen blocked", err);
                // Fallback to absolute positioning CSS already handled by state
            });
        } else {
            if (document.fullscreenElement) {
                document.exitFullscreen().catch(console.error);
            }
        }
    }, [isFullScreen]);

    return (
        <div
            ref={containerRef}
            className={`flex flex-col bg-[var(--bg-surface)] rounded-xl border border-[var(--border-default)] overflow-hidden transition-all duration-300 ${isFullScreen ? 'fixed inset-0 z-50 rounded-none' : 'h-full ' + className}`}
        >
            {/* Toolbar */}
            <div className="flex items-center justify-between p-3 border-b border-[var(--border-default)] bg-[var(--bg-elevated)]">
                <div className="flex items-center gap-2">
                    <button
                        onClick={prevPage}
                        disabled={currentPage <= (pages[0]?.number || 1)}
                        className="btn-icon disabled:opacity-30"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>

                    <div className="flex items-center gap-2 bg-[var(--bg-surface)] px-3 py-1.5 rounded-lg border border-[var(--border-default)]">
                        <span className="text-sm text-secondary whitespace-nowrap">Page</span>
                        <input
                            type="number"
                            value={currentPage}
                            onChange={(e) => {
                                const val = parseInt(e.target.value);
                                if (!isNaN(val) && pages.some(p => p.number === val)) setCurrentPage(val);
                            }}
                            className="w-12 bg-transparent text-center font-mono text-primary text-sm focus:outline-none"
                        />
                        <span className="text-sm text-tertiary">/ {pages.length > 0 ? pages[pages.length - 1].number : 1}</span>
                    </div>

                    <button
                        onClick={nextPage}
                        disabled={currentPage >= (pages[pages.length - 1]?.number || 1)}
                        className="btn-icon disabled:opacity-30"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex items-center gap-1">
                    {/* Search Toggle */}
                    <div className={`flex items-center overflow-hidden transition-all duration-300 ${showSearch ? 'w-64 opacity-100' : 'w-0 opacity-0'}`}>
                        <div className="flex items-center bg-[var(--bg-surface)] rounded-lg border border-[var(--border-default)] px-2 py-1 mx-2 flex-1">
                            <Search className="w-3 h-3 text-tertiary mr-2" />
                            <input
                                ref={searchInputRef}
                                type="text"
                                placeholder="Find in document..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="bg-transparent border-none outline-none text-xs w-full text-primary"
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') jumpToSearch(e.shiftKey ? 'prev' : 'next');
                                }}
                            />
                            {searchResults.length > 0 && (
                                <div className="flex items-center gap-1 ml-1 pl-2 border-l border-[var(--border-default)]">
                                    <span className="text-[10px] text-tertiary whitespace-nowrap">
                                        {currentSearchIndex + 1}/{searchResults.length}
                                    </span>
                                    <button onClick={() => jumpToSearch('next')} className="hover:bg-[var(--bg-hover)] rounded p-0.5"><ArrowDown className="w-3 h-3" /></button>
                                    <button onClick={() => jumpToSearch('prev')} className="hover:bg-[var(--bg-hover)] rounded p-0.5"><ArrowUp className="w-3 h-3" /></button>
                                </div>
                            )}
                        </div>
                    </div>

                    <button onClick={() => {
                        setShowSearch(!showSearch);
                        if (!showSearch) setTimeout(() => searchInputRef.current?.focus(), 100);
                    }} className={`btn-icon ${showSearch ? 'text-accent' : ''}`}>
                        <Search className="w-4 h-4" />
                    </button>

                    <div className="w-px h-4 bg-[var(--border-default)] mx-1" />

                    <button onClick={() => setFontSize(Math.max(10, fontSize - 2))} className="btn-icon" title="Zoom Out">
                        <ZoomOut className="w-4 h-4" />
                    </button>
                    <span className="text-xs text-tertiary min-w-[3ch] text-center">{fontSize}</span>
                    <button onClick={() => setFontSize(Math.min(32, fontSize + 2))} className="btn-icon" title="Zoom In">
                        <ZoomIn className="w-4 h-4" />
                    </button>

                    <div className="w-px h-4 bg-[var(--border-default)] mx-1" />

                    <button onClick={() => setIsFullScreen(!isFullScreen)} className="btn-icon">
                        {isFullScreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                    </button>
                </div>
            </div>

            {/* Content Viewport */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-8 lg:p-12 relative bg-[var(--bg-base)]">
                <div
                    className="max-w-4xl mx-auto shadow-sm min-h-[800px] bg-[var(--bg-surface)] border border-[var(--border-weak)] rounded-lg p-8 md:p-12 transition-all duration-300"
                    style={{ fontSize: `${fontSize}px` }}
                >
                    <div className="flex justify-between items-center mb-8 border-b border-[var(--border-default)] pb-4 opacity-50">
                        <span className="text-xs font-mono uppercase tracking-widest text-[#9d2435]">Confidential</span>
                        <span className="text-xs text-tertiary">Page {currentPage}</span>
                    </div>

                    <div className="whitespace-pre-wrap leading-relaxed text-primary font-serif">
                        {renderHighlightedContent(activePageContent, currentPage)}
                    </div>

                    <div className="mt-16 pt-8 border-t border-[var(--border-default)] flex justify-between items-center text-xs text-tertiary">
                        <span>Generated by Financial Calculator</span>
                        <span>{currentPage} / {pages.length}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
