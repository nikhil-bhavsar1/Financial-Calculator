
import React, { useState, useMemo } from 'react';
import { Search, FileText, Edit2, Filter, Grid3X3, List, Inbox, ChevronDown, ChevronRight, Layers, CheckCircle2, AlertTriangle, XCircle, X, Check, ArrowUpDown, ArrowDownAZ, ArrowUpAZ, TrendingUp, TrendingDown, SlidersHorizontal } from 'lucide-react';
import { FinancialItem, TermMapping, CATEGORY_OPTIONS } from '../types';
import { INPUT_METRICS } from '../library/metrics';

interface CapturedDataGridProps {
    data: FinancialItem[];
    searchTerm?: string;
    onSourceClick?: (item: FinancialItem) => void;
    onDataUpdate?: (updatedData: FinancialItem[]) => void;
    terminologyMap?: TermMapping[];
}

// Valid statement types from structured financial statements only
const VALID_STATEMENT_TYPES = new Set([
    'income_statement',
    'balance_sheet',
    'cashflow',
    'cash_flow',  // alternate naming
    'statement_of_changes_in_equity',
    'comprehensive_income'
]);

// Build a lookup set of valid term keys from terminology map
function buildValidTermKeys(mappings: TermMapping[]): Set<string> {
    const validKeys = new Set<string>();
    mappings.forEach(m => {
        validKeys.add(m.key.toLowerCase());
        // Also add all keywords as valid patterns
        [...m.keywords_indas, ...m.keywords_gaap, ...m.keywords_ifrs].forEach(kw => {
            validKeys.add(kw.toLowerCase());
        });
    });
    return validKeys;
}

// Check if an item matches any term in the terminology map
function isValidTermItem(item: FinancialItem, validTerms: Set<string>): boolean {
    const itemId = (item.id || '').toLowerCase();
    const itemLabel = (item.label || '').toLowerCase();

    // Direct ID match
    if (validTerms.has(itemId)) return true;

    // Keyword match in label
    for (const term of validTerms) {
        if (itemLabel.includes(term) || term.includes(itemLabel)) {
            return true;
        }
    }

    return false;
}

export const CapturedDataGrid: React.FC<CapturedDataGridProps> = ({
    data,
    searchTerm = '',
    onSourceClick,
    onDataUpdate,
    terminologyMap = INPUT_METRICS
}) => {
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
    const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());
    const [showOnlyMapped, setShowOnlyMapped] = useState(false); // Default: show ALL extracted items

    // Sorting state
    type SortMode = 'alpha-asc' | 'alpha-desc' | 'value-high' | 'value-low' | 'category';
    const [sortMode, setSortMode] = useState<SortMode>('category');
    const [showSortMenu, setShowSortMenu] = useState(false);

    // Filter state
    const [showFilterPanel, setShowFilterPanel] = useState(false);
    const [filterCategory, setFilterCategory] = useState<string>('all');
    const [filterStatus, setFilterStatus] = useState<'all' | 'with-data' | 'missing'>('all');
    const [searchQuery, setSearchQuery] = useState('');

    // Editing state for page numbers
    const [editingPageId, setEditingPageId] = useState<string | null>(null);
    const [editingPageValue, setEditingPageValue] = useState<string>('');

    // Editing state for values
    const [editingValueId, setEditingValueId] = useState<string | null>(null);
    const [editValues, setEditValues] = useState<{ current: string, previous: string }>({ current: '', previous: '' });

    const handleStartEditValue = (item: FinancialItem) => {
        setEditingValueId(item.id);
        setEditValues({
            current: item.currentYear !== 0 ? item.currentYear.toString() : '',
            previous: item.previousYear !== 0 ? item.previousYear.toString() : ''
        });
    };

    const handleSaveValueEdit = (item: FinancialItem) => {
        if (!onDataUpdate) return;

        const currentVal = parseFloat(editValues.current.replace(/[^0-9.-]/g, '')) || 0;
        const previousVal = parseFloat(editValues.previous.replace(/[^0-9.-]/g, '')) || 0;

        // Calculate variation
        const variation = currentVal - previousVal;
        const variationPercent = previousVal !== 0 ? (variation / previousVal * 100) : 0;

        // Create updated item
        const updatedItem: FinancialItem = {
            ...item,
            currentYear: currentVal,
            previousYear: previousVal,
            variation,
            variationPercent,
        };
        // Remove transient flags before saving
        delete (updatedItem as any).isMissing;

        // If item existed in data, update it. If not, add it.
        const exists = data.some(d => d.id === item.id);
        let newData;
        if (exists) {
            newData = data.map(d => d.id === item.id ? updatedItem : d);
        } else {
            newData = [...data, updatedItem];
        }

        onDataUpdate(newData);
        setEditingValueId(null);
    };

    const handleValueKeyDown = (e: React.KeyboardEvent, item: FinancialItem) => {
        if (e.key === 'Enter') {
            handleSaveValueEdit(item);
        } else if (e.key === 'Escape') {
            setEditingValueId(null);
        }
    };

    const validTermKeys = useMemo(() => buildValidTermKeys(terminologyMap), [terminologyMap]);

    const toggleSection = (sectionId: string) => {
        const newSet = new Set(collapsedSections);
        if (newSet.has(sectionId)) {
            newSet.delete(sectionId);
        } else {
            newSet.add(sectionId);
        }
        setCollapsedSections(newSet);
    };

    // Start editing page number
    const handleStartEditPage = (item: FinancialItem) => {
        setEditingPageId(item.id);
        setEditingPageValue(item.sourcePage || '');
    };

    // Save page number edit
    const handleSavePageEdit = (itemId: string) => {
        if (onDataUpdate) {
            const updatedData = data.map(item =>
                item.id === itemId ? { ...item, sourcePage: editingPageValue } : item
            );
            onDataUpdate(updatedData);
        }
        setEditingPageId(null);
        setEditingPageValue('');
    };

    // Cancel page number edit
    const handleCancelPageEdit = () => {
        setEditingPageId(null);
        setEditingPageValue('');
    };

    // Clear page number
    const handleClearPage = (itemId: string) => {
        if (onDataUpdate) {
            const updatedData = data.map(item =>
                item.id === itemId ? { ...item, sourcePage: '' } : item
            );
            onDataUpdate(updatedData);
        }
    };

    // Handle Enter key for page edit
    const handlePageKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, itemId: string) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSavePageEdit(itemId);
        } else if (e.key === 'Escape') {
            handleCancelPageEdit();
        }
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0,
        }).format(val);
    };

    const groupedData = useMemo(() => {
        // 1. Initialize groups based on Terminology Categories
        const groups: Record<string, FinancialItem[]> = {};

        // Define standard category order for financial statements
        const categoryOrder = [
            'Revenue', 'Cost of Revenue', 'Operating Expenses',
            'Finance Costs', 'Other Income & Expenses', 'Tax', 'Profit & Loss',
            'Income Statement', 'Income Statement - IFRS 18',

            'Non-Current Assets', 'Current Assets', 'Balance Sheet - Assets',
            'Balance Sheet',

            'Non-Current Liabilities', 'Current Liabilities', 'Balance Sheet - Liabilities',

            'Equity', 'Balance Sheet - Equity', 'Statement of Changes in Equity',

            'Cash Flow - Operating', 'Cash Flow - Investing', 'Cash Flow - Financing', 'Cash Flow Statement',

            'Per Share Data', 'Ratios & Metrics', 'Disclosures', 'Misc'
        ];

        // Initialize empty arrays
        categoryOrder.forEach(cat => groups[cat] = []);

        // 2. Map actual data to a lookup map for fast access
        const dataMap = new Map<string, FinancialItem>();
        data.forEach(item => {
            // Priority: ID match > Key match > Label match
            if (item.id) dataMap.set(item.id.toLowerCase(), item);
            if (item.label) dataMap.set(item.label.toLowerCase(), item); // Secondary lookup
        });

        // Track consumed IDs to find unmapped items later
        const consumedIds = new Set<string>();

        // 3. Iterate Terminology Map to build structured view (including missing items)
        terminologyMap.forEach(term => {
            // Find finding logic
            let foundItem: FinancialItem | undefined =
                dataMap.get(term.key.toLowerCase()) ||
                dataMap.get(term.id.toLowerCase());

            // Try explicit matching if ID match failed
            if (!foundItem) {
                foundItem = data.find(d =>
                    d.id.toLowerCase() === term.key.toLowerCase() ||
                    d.id.toLowerCase() === term.id.toLowerCase() ||
                    d.label.toLowerCase() === term.label.toLowerCase()
                );
            }

            if (foundItem) {
                // Determine effective category - prefer term category over item statement type
                const category = term.category || 'Misc';
                if (!groups[category]) groups[category] = [];

                // Avoid duplicates in the same group? 
                // We add it to the displayed list
                groups[category].push({
                    ...foundItem,
                    label: term.label // Use standardized label
                });
                consumedIds.add(foundItem.id);
            } else {
                // Create MISSING placeholder
                const category = term.category || 'Misc';
                if (!groups[category]) groups[category] = [];

                groups[category].push({
                    id: term.key,
                    label: term.label,
                    currentYear: 0,
                    previousYear: 0,
                    variation: 0,
                    variationPercent: 0,
                    sourcePage: '-',
                    rowType: 'data',
                    isMissing: true // Flag for UI styling
                } as any);
            }
        });

        // 4. Handle Unmapped Data (Extracted but not in Terminology Map)
        const unmappedcategory = 'Unmapped / Other';
        groups[unmappedcategory] = [];

        data.forEach(item => {
            if (!consumedIds.has(item.id)) {
                groups[unmappedcategory].push(item);
            }
        });

        // 5. Clean up empty groups if desired, but user wants full statement view, 
        // so we likely keep them if they have missing placeholders. 
        // But we might remove completely empty ones (no terms defined).
        Object.keys(groups).forEach(key => {
            if (groups[key].length === 0) delete groups[key];
        });

        return groups;
    }, [data, terminologyMap]); // Removed searchTerm dependency to keep structure stable

    // Dynamic Section Config based on active groups
    const sectionConfig = useMemo(() => {
        const standardOrder = [
            'Revenue', 'Cost of Revenue', 'Operating Expenses',
            'Finance Costs', 'Tax', 'Profit & Loss',
            'Non-Current Assets', 'Current Assets',
            'Non-Current Liabilities', 'Current Liabilities',
            'Equity',
            'Cash Flow - Operating', 'Cash Flow - Investing', 'Cash Flow - Financing',
            'Disclosures', 'Unmapped / Other'
        ];

        const existingKeys = Object.keys(groupedData);

        // Sort keys based on standard order
        const sortedKeys = existingKeys.sort((a, b) => {
            const idxA = standardOrder.indexOf(a);
            const idxB = standardOrder.indexOf(b);
            // If both in standard list, compare indices
            if (idxA !== -1 && idxB !== -1) return idxA - idxB;
            // If only A is standard, it comes first
            if (idxA !== -1) return -1;
            // If only B is standard, it comes first
            if (idxB !== -1) return 1;
            // Otherwise alphabetical
            return a.localeCompare(b);
        });

        return sortedKeys.map(key => ({
            id: key,
            label: key,
            icon: getCategoryIcon(key),
            count: groupedData[key].length
        }));
    }, [groupedData]);

    // Apply filters, search, and sorting to grouped data
    const filteredAndSortedData = useMemo(() => {
        const result: Record<string, FinancialItem[]> = {};

        Object.entries(groupedData).forEach(([category, items]: [string, FinancialItem[]]) => {
            // Category filter
            if (filterCategory !== 'all' && category !== filterCategory) return;

            let filtered = items.filter((item: FinancialItem) => {
                // Status filter
                const isMissing = (item as any).isMissing;
                if (filterStatus === 'with-data' && isMissing) return false;
                if (filterStatus === 'missing' && !isMissing) return false;

                // Search filter
                if (searchQuery.trim()) {
                    const query = searchQuery.toLowerCase();
                    return item.label.toLowerCase().includes(query) ||
                        item.id.toLowerCase().includes(query);
                }
                return true;
            });

            // Sorting within each category
            if (sortMode === 'alpha-asc') {
                filtered = filtered.sort((a, b) => a.label.localeCompare(b.label));
            } else if (sortMode === 'alpha-desc') {
                filtered = filtered.sort((a, b) => b.label.localeCompare(a.label));
            } else if (sortMode === 'value-high') {
                filtered = filtered.sort((a, b) => b.currentYear - a.currentYear);
            } else if (sortMode === 'value-low') {
                filtered = filtered.sort((a, b) => a.currentYear - b.currentYear);
            }
            // 'category' mode keeps original order

            if (filtered.length > 0) {
                result[category] = filtered;
            }
        });

        return result;
    }, [groupedData, filterCategory, filterStatus, searchQuery, sortMode]);

    // Available categories for filter dropdown
    const availableCategories = useMemo(() => {
        return Object.keys(groupedData).sort();
    }, [groupedData]);

    function getCategoryIcon(cat: string) {
        if (cat.includes('Revenue') || cat.includes('Income')) return '💰';
        if (cat.includes('Expense') || cat.includes('Cost')) return '📉';
        if (cat.includes('Profit') || cat.includes('Equity')) return '📈';
        if (cat.includes('Asset')) return '🏢';
        if (cat.includes('Liabilities') || cat.includes('Debt')) return '💳';
        if (cat.includes('Cash')) return '💵';
        if (cat.includes('Disclosures')) return '📋';
        return '📁';
    }

    // Count statistics - use filtered data
    const totalFiltered = Object.values(filteredAndSortedData).flat().length;
    const totalRaw = data.length;
    const mappedCount = data.filter(item => isValidTermItem(item, validTermKeys)).length;
    const hasAnyData = totalFiltered > 0;

    return (
        <div className="flex-1 flex flex-col m-4 glass-card overflow-hidden animate-fadeIn">
            {/* Toolbar */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-default)]">
                <div className="flex items-center gap-4">
                    <h2 className="label-uppercase text-sm tracking-wide">Captured Data</h2>
                    <div className="flex items-center gap-2">
                        <span className="pill pill-accent">{totalFiltered} items</span>
                        {totalRaw !== totalFiltered && (
                            <span className="text-xs text-tertiary">
                                ({totalRaw - totalFiltered} filtered)
                            </span>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* Search Input */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary" />
                        <input
                            type="text"
                            placeholder="Search items..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="glass-input pl-9 pr-3 py-1.5 w-48 text-sm"
                        />
                    </div>

                    {/* Sort Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => { setShowSortMenu(!showSortMenu); setShowFilterPanel(false); }}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${sortMode !== 'category'
                                ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/30'
                                : 'bg-[var(--bg-surface)] text-secondary border border-[var(--border-default)] hover:border-[var(--border-strong)]'
                                }`}
                        >
                            <ArrowUpDown className="w-3.5 h-3.5" />
                            <span>Sort</span>
                            <ChevronDown className="w-3 h-3" />
                        </button>
                        {showSortMenu && (
                            <div className="absolute right-0 top-full mt-2 w-48 bg-[var(--bg-elevated)] border border-[var(--border-default)] rounded-xl shadow-xl z-50 py-2 animate-fadeIn">
                                {[
                                    { key: 'alpha-asc' as const, label: 'A → Z', icon: ArrowDownAZ },
                                    { key: 'alpha-desc' as const, label: 'Z → A', icon: ArrowUpAZ },
                                    { key: 'value-high' as const, label: 'Value (High → Low)', icon: TrendingDown },
                                    { key: 'value-low' as const, label: 'Value (Low → High)', icon: TrendingUp },
                                    { key: 'category' as const, label: 'By Category', icon: Layers },
                                ].map(option => (
                                    <button
                                        key={option.key}
                                        onClick={() => { setSortMode(option.key); setShowSortMenu(false); }}
                                        className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-[var(--bg-hover)] transition-colors ${sortMode === option.key ? 'text-accent font-medium' : 'text-secondary'
                                            }`}
                                    >
                                        <option.icon className="w-4 h-4" />
                                        {option.label}
                                        {sortMode === option.key && <Check className="w-4 h-4 ml-auto" />}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Filter Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => { setShowFilterPanel(!showFilterPanel); setShowSortMenu(false); }}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filterCategory !== 'all' || filterStatus !== 'all'
                                ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/30'
                                : 'bg-[var(--bg-surface)] text-secondary border border-[var(--border-default)] hover:border-[var(--border-strong)]'
                                }`}
                        >
                            <SlidersHorizontal className="w-3.5 h-3.5" />
                            <span>Filter</span>
                            {(filterCategory !== 'all' || filterStatus !== 'all') && (
                                <span className="w-5 h-5 rounded-full bg-purple-500 text-white text-[10px] flex items-center justify-center font-bold">
                                    {(filterCategory !== 'all' ? 1 : 0) + (filterStatus !== 'all' ? 1 : 0)}
                                </span>
                            )}
                        </button>
                        {showFilterPanel && (
                            <div className="absolute right-0 top-full mt-2 w-72 bg-[var(--bg-elevated)] border border-[var(--border-default)] rounded-xl shadow-xl z-50 p-4 space-y-4 animate-fadeIn">
                                <div className="space-y-2">
                                    <label className="label-uppercase text-xs">Category</label>
                                    <select
                                        value={filterCategory}
                                        onChange={(e) => setFilterCategory(e.target.value)}
                                        className="glass-input w-full text-sm"
                                    >
                                        <option value="all">All Categories</option>
                                        {availableCategories.map(cat => (
                                            <option key={cat} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="label-uppercase text-xs">Status</label>
                                    <select
                                        value={filterStatus}
                                        onChange={(e) => setFilterStatus(e.target.value as any)}
                                        className="glass-input w-full text-sm"
                                    >
                                        <option value="all">All Items</option>
                                        <option value="with-data">With Data Only</option>
                                        <option value="missing">Missing Only</option>
                                    </select>
                                </div>
                                {(filterCategory !== 'all' || filterStatus !== 'all') && (
                                    <button
                                        onClick={() => { setFilterCategory('all'); setFilterStatus('all'); }}
                                        className="w-full text-xs text-error hover:underline flex items-center justify-center gap-1 pt-2 border-t border-[var(--border-subtle)]"
                                    >
                                        <X className="w-3 h-3" /> Clear Filters
                                    </button>
                                )}
                            </div>
                        )}
                    </div>

                    {/* View Toggle */}
                    <div className="flex items-center bg-[var(--bg-surface)] rounded-lg p-1">
                        <button
                            onClick={() => setViewMode('list')}
                            className={`p-2 rounded-md transition-all ${viewMode === 'list'
                                ? 'bg-[var(--bg-elevated)] text-primary shadow-sm'
                                : 'text-tertiary hover:text-secondary'
                                }`}
                        >
                            <List className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('grid')}
                            className={`p-2 rounded-md transition-all ${viewMode === 'grid'
                                ? 'bg-[var(--bg-elevated)] text-primary shadow-sm'
                                : 'text-tertiary hover:text-secondary'
                                }`}
                        >
                            <Grid3X3 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-4 pb-24">
                {!hasAnyData ? (
                    <div className="flex flex-col items-center justify-center py-20 text-tertiary animate-fadeIn">
                        <div className="w-16 h-16 rounded-2xl bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                            <Inbox className="w-8 h-8 opacity-50" />
                        </div>
                        <p className="text-sm font-medium text-secondary">
                            {showOnlyMapped ? 'No mapped financial terms found' : 'No data captured yet'}
                        </p>
                        <p className="text-xs mt-1">
                            {showOnlyMapped && totalRaw > 0
                                ? `${totalRaw} items extracted but none match terminology map. Try disabling Strict Mode.`
                                : 'Upload a document to extract financial data'
                            }
                        </p>
                        {showOnlyMapped && totalRaw > 0 && (
                            <button
                                onClick={() => setShowOnlyMapped(false)}
                                className="mt-4 px-4 py-2 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-lg text-sm font-medium hover:bg-amber-500/20 transition-colors"
                            >
                                Show All Items
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="space-y-6">
                        {sectionConfig.filter(s => filteredAndSortedData[s.id]?.length > 0).map(section => {
                            const items = filteredAndSortedData[section.id];
                            if (!items || items.length === 0) return null;
                            const isCollapsed = collapsedSections.has(section.id);

                            return (
                                <div key={section.id} className="animate-fadeIn">
                                    {/* Section Header */}
                                    <button
                                        onClick={() => toggleSection(section.id)}
                                        className="flex items-center gap-2 w-full text-left mb-3 group"
                                    >
                                        <div className={`p-1 rounded bg-[var(--bg-surface)] group-hover:bg-[var(--bg-elevated)] transition-colors text-tertiary`}>
                                            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <h3 className="text-sm font-semibold text-primary">{section.label}</h3>
                                            <span className="text-xs text-tertiary bg-[var(--bg-surface)] px-2 py-0.5 rounded-full border border-[var(--border-default)]">
                                                {items.length}
                                            </span>
                                        </div>
                                        <div className="h-px bg-[var(--border-default)] flex-1 ml-4 group-hover:bg-[var(--border-strong)] transition-colors" />
                                    </button>

                                    {/* Section Content */}
                                    {!isCollapsed && (
                                        viewMode === 'grid' ? (
                                            /* Grid View */
                                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 ml-2">
                                                {items.map((item, index) => {
                                                    const isMissing = (item as any).isMissing;
                                                    const isEditing = editingValueId === item.id;

                                                    return (
                                                        <div
                                                            key={item.id}
                                                            className={`group p-4 rounded-xl border transition-all relative overflow-hidden ${isMissing
                                                                ? 'bg-[var(--bg-surface)] border-[var(--border-subtle)] border-dashed hover:border-[var(--border-default)]'
                                                                : 'bg-[var(--bg-surface)] border-[var(--border-default)] hover:border-[var(--border-strong)]'
                                                                }`}
                                                            style={{ animationDelay: `${index * 30}ms` }}
                                                        >
                                                            <div className="flex items-start justify-between mb-3">
                                                                <span className="text-xs truncate flex-1 pr-2 text-secondary font-medium" title={item.label}>
                                                                    {item.label}
                                                                </span>
                                                                <button
                                                                    className={`btn-icon w-6 h-6 transition-opacity ${isEditing ? 'opacity-100 text-[var(--accent-primary)]' : 'opacity-0 group-hover:opacity-100 text-tertiary hover:text-primary'}`}
                                                                    onClick={() => !isEditing && handleStartEditValue(item)}
                                                                >
                                                                    <Edit2 className="w-3 h-3" />
                                                                </button>
                                                            </div>

                                                            {isEditing ? (
                                                                <div className="space-y-2">
                                                                    <div>
                                                                        <label className="text-[10px] text-tertiary uppercase">Current</label>
                                                                        <input
                                                                            className="w-full text-sm font-mono bg-[var(--bg-base)] border border-[var(--border-strong)] rounded px-1 py-0.5 focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                                                                            value={editValues.current}
                                                                            onChange={(e) => setEditValues({ ...editValues, current: e.target.value })}
                                                                            onKeyDown={(e) => handleValueKeyDown(e, item)}
                                                                            autoFocus
                                                                            placeholder="0.00"
                                                                        />
                                                                    </div>
                                                                    <div>
                                                                        <label className="text-[10px] text-tertiary uppercase">Previous</label>
                                                                        <input
                                                                            className="w-full text-sm font-mono bg-[var(--bg-base)] border border-[var(--border-strong)] rounded px-1 py-0.5 focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                                                                            value={editValues.previous}
                                                                            onChange={(e) => setEditValues({ ...editValues, previous: e.target.value })}
                                                                            onKeyDown={(e) => handleValueKeyDown(e, item)}
                                                                            placeholder="0.00"
                                                                        />
                                                                    </div>
                                                                    <div className="flex justify-end gap-1 mt-1">
                                                                        <button onClick={() => handleSaveValueEdit(item)} className="p-1 text-success hover:bg-green-500/10 rounded"><Check className="w-3 h-3" /></button>
                                                                        <button onClick={() => setEditingValueId(null)} className="p-1 text-error hover:bg-red-500/10 rounded"><X className="w-3 h-3" /></button>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <div onClick={() => handleStartEditValue(item)} className="cursor-text">
                                                                    <p className={`text-lg font-bold font-mono tabular-nums ${isMissing ? 'text-tertiary' : 'text-primary'}`}>
                                                                        {isMissing && item.currentYear === 0 ? '—' : formatCurrency(item.currentYear)}
                                                                    </p>
                                                                    {(!isMissing || item.previousYear !== 0) && (
                                                                        <p className="text-xs font-mono text-tertiary mt-1">
                                                                            Prev: {formatCurrency(item.previousYear)}
                                                                        </p>
                                                                    )}
                                                                </div>
                                                            )}

                                                            {!isMissing && !isEditing && (
                                                                <div className="flex items-center gap-2 mt-3 pt-2 border-t border-[var(--border-subtle)]">
                                                                    <span className={`text-xs font-medium ${(item.variation || 0) >= 0 ? 'text-success' : 'text-error'}`}>
                                                                        {(item.variationPercent || 0) > 0 ? '+' : ''}{(item.variationPercent || 0).toFixed(1)}%
                                                                    </span>
                                                                    <div className="flex-1"></div>
                                                                    {item.sourcePage && (
                                                                        <button
                                                                            className="text-xs text-tertiary hover:text-primary flex items-center gap-1 bg-[var(--bg-base)] px-1.5 py-0.5 rounded border border-transparent hover:border-[var(--border-default)] transition-all"
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                onSourceClick?.(item);
                                                                            }}
                                                                            title={item.rawLine ? `Source: ${item.rawLine}` : `Page ${item.sourcePage}`}
                                                                        >
                                                                            <FileText className="w-3 h-3" />
                                                                            {item.sourcePage}
                                                                        </button>
                                                                    )}
                                                                </div>
                                                            )}
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                        ) : (
                                            /* List View */
                                            <div className="space-y-1 ml-2">
                                                {items.map((item, index) => {
                                                    const isMissing = (item as any).isMissing;
                                                    const isEditing = editingValueId === item.id;

                                                    return (
                                                        <div
                                                            key={item.id}
                                                            className={`grid grid-cols-12 px-4 py-3 rounded-xl items-center group transition-colors border ${isMissing
                                                                ? 'bg-[var(--bg-surface)] border-dashed border-[var(--border-subtle)] hover:border-[var(--border-default)]'
                                                                : 'bg-[var(--bg-surface)] hover:bg-[var(--bg-hover)] border-transparent hover:border-[var(--border-subtle)]'
                                                                }`}
                                                        >
                                                            <div className="col-span-4 text-sm font-medium text-primary truncate pr-4 flex items-center gap-2" title={item.label}>
                                                                {item.label}
                                                                {isMissing && <span className="w-1.5 h-1.5 rounded-full bg-[var(--border-strong)]" title="Missing data"></span>}
                                                            </div>

                                                            {isEditing ? (
                                                                <>
                                                                    <div className="col-span-2 flex justify-center px-1">
                                                                        <input
                                                                            className="w-full max-w-[120px] text-sm font-mono bg-[var(--bg-base)] border border-[var(--border-strong)] rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] shadow-sm"
                                                                            value={editValues.current}
                                                                            onChange={(e) => setEditValues({ ...editValues, current: e.target.value })}
                                                                            onKeyDown={(e) => handleValueKeyDown(e, item)}
                                                                            autoFocus
                                                                            placeholder="Curr"
                                                                        />
                                                                    </div>
                                                                    <div className="col-span-2 flex justify-center px-1">
                                                                        <input
                                                                            className="w-full max-w-[120px] text-sm font-mono bg-[var(--bg-base)] border border-[var(--border-strong)] rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] shadow-sm"
                                                                            value={editValues.previous}
                                                                            onChange={(e) => setEditValues({ ...editValues, previous: e.target.value })}
                                                                            onKeyDown={(e) => handleValueKeyDown(e, item)}
                                                                            placeholder="Prev"
                                                                        />
                                                                    </div>
                                                                    <div className="col-span-2"></div>
                                                                    <div className="col-span-2 flex items-center justify-end gap-2">
                                                                        <button onClick={() => handleSaveValueEdit(item)} className="p-1.5 text-white bg-green-500 hover:bg-green-600 rounded-lg shadow-sm transition-colors" title="Save">
                                                                            <Check className="w-4 h-4" />
                                                                        </button>
                                                                        <button onClick={() => setEditingValueId(null)} className="p-1.5 text-gray-500 hover:bg-red-100 hover:text-red-600 rounded-lg transition-colors" title="Cancel">
                                                                            <X className="w-4 h-4" />
                                                                        </button>
                                                                    </div>
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <div
                                                                        className={`col-span-2 text-sm font-mono tabular-nums cursor-text hover:bg-[var(--bg-base)] rounded px-2 py-1 transition-colors text-center ${isMissing ? 'text-tertiary' : 'text-primary'}`}
                                                                        onClick={() => handleStartEditValue(item)}
                                                                    >
                                                                        {isMissing && item.currentYear === 0 ? '—' : formatCurrency(item.currentYear)}
                                                                    </div>
                                                                    <div
                                                                        className={`col-span-2 text-sm font-mono tabular-nums cursor-text hover:bg-[var(--bg-base)] rounded px-2 py-1 transition-colors text-center ${isMissing ? 'text-tertiary' : 'text-secondary'}`}
                                                                        onClick={() => handleStartEditValue(item)}
                                                                    >
                                                                        {isMissing && item.previousYear === 0 ? '—' : formatCurrency(item.previousYear)}
                                                                    </div>

                                                                    <div className="col-span-2 flex items-center gap-2 justify-center">
                                                                        {!isMissing && (
                                                                            <>
                                                                                <span className={`text-sm font-medium ${(item.variation || 0) >= 0 ? 'text-success' : 'text-error'}`}>
                                                                                    {(item.variation || 0) >= 0 ? '↗' : '↘'}
                                                                                </span>
                                                                                <span className={`pill text-xs ${(item.variation || 0) >= 0 ? 'pill-positive' : 'pill-negative'}`}>
                                                                                    {(item.variationPercent || 0) > 0 ? '+' : ''}{(item.variationPercent || 0).toFixed(1)}%
                                                                                </span>
                                                                            </>
                                                                        )}
                                                                    </div>

                                                                    <div className="col-span-2 flex items-center justify-end gap-1">
                                                                        {!isMissing ? (
                                                                            editingPageId === item.id ? (
                                                                                <div className="flex items-center gap-1">
                                                                                    <input
                                                                                        type="text"
                                                                                        value={editingPageValue}
                                                                                        onChange={(e) => setEditingPageValue(e.target.value)}
                                                                                        onKeyDown={(e) => handlePageKeyDown(e, item.id)}
                                                                                        placeholder="#"
                                                                                        className="w-12 px-1 py-1 text-xs rounded border border-[var(--border-strong)] bg-[var(--bg-base)] focus:outline-none"
                                                                                        autoFocus
                                                                                    />
                                                                                    <button onClick={() => handleSavePageEdit(item.id)} className="text-success hover:bg-green-500/10 p-1 rounded"><Check className="w-3 h-3" /></button>
                                                                                </div>
                                                                            ) : (
                                                                                <button
                                                                                    className="pill pill-neutral text-xs hover:bg-[var(--bg-elevated)] hover:text-primary transition-all ml-auto"
                                                                                    onClick={(e) => {
                                                                                        e.stopPropagation();
                                                                                        item.sourcePage ? onSourceClick?.(item) : handleStartEditPage(item);
                                                                                    }}
                                                                                    title={item.rawLine ? `Source: ${item.rawLine}` : (item.sourcePage ? `Page ${item.sourcePage}` : 'Click to add page')}
                                                                                >
                                                                                    <FileText className="w-3 h-3" />
                                                                                    {item.sourcePage || 'Page'}
                                                                                </button>
                                                                            )
                                                                        ) : (
                                                                            <button
                                                                                onClick={() => handleStartEditValue(item)}
                                                                                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-accent bg-accent/10 hover:bg-accent/20 rounded-lg transition-colors ml-auto"
                                                                            >
                                                                                <Edit2 className="w-3.5 h-3.5" /> Add Value
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                </>
                                                            )}
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                        )
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CapturedDataGrid;
