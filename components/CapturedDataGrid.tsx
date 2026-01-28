
import React, { useState, useMemo } from 'react';
import { Search, FileText, Edit2, Filter, Grid3X3, List, Inbox, ChevronDown, ChevronRight, Layers } from 'lucide-react';
import { FinancialItem } from '../types';

interface CapturedDataGridProps {
    data: FinancialItem[];
    searchTerm?: string;
    onSourceClick?: (item: FinancialItem) => void;
}

export const CapturedDataGrid: React.FC<CapturedDataGridProps> = ({ data, searchTerm = '', onSourceClick }) => {
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
    // Default open all sections. collapsedSections stores IDs of CLOSED sections.
    const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());

    const toggleSection = (sectionId: string) => {
        const newSet = new Set(collapsedSections);
        if (newSet.has(sectionId)) {
            newSet.delete(sectionId);
        } else {
            newSet.add(sectionId);
        }
        setCollapsedSections(newSet);
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0,
        }).format(val);
    };

    const groupedData = useMemo(() => {
        const filtered = data.filter(item =>
            item.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.id.toLowerCase().includes(searchTerm.toLowerCase())
        );

        const groups: Record<string, FinancialItem[]> = {
            'income_statement': [],
            'balance_sheet': [],
            'cashflow': [],
            'other': []
        };

        filtered.forEach(item => {
            const type = item.statementType || 'other';
            if (groups[type]) {
                groups[type].push(item);
            } else {
                groups['other'].push(item);
            }
        });

        return groups;
    }, [data, searchTerm]);

    const sectionConfig = [
        { id: 'income_statement', label: 'Income Statement' },
        { id: 'balance_sheet', label: 'Balance Sheet' },
        { id: 'cashflow', label: 'Cash Flow' },
        { id: 'other', label: 'Other Items' },
    ];

    const totalItems = data.length;
    const hasAnyData = (Object.values(groupedData) as FinancialItem[][]).some(g => g.length > 0);

    return (
        <div className="flex-1 flex flex-col m-4 glass-card overflow-hidden animate-fadeIn">
            {/* Toolbar */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-default)]">
                <div className="flex items-center gap-4">
                    <h2 className="label-uppercase text-sm tracking-wide">Captured Data</h2>
                    <span className="pill pill-accent">{totalItems} items</span>
                </div>

                <div className="flex items-center gap-3">
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

                    <button className="btn-ghost">
                        <Filter className="w-4 h-4" />
                        <span>Filter</span>
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-4 pb-24">
                {!hasAnyData ? (
                    <div className="flex flex-col items-center justify-center py-20 text-tertiary animate-fadeIn">
                        <div className="w-16 h-16 rounded-2xl bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                            <Inbox className="w-8 h-8 opacity-50" />
                        </div>
                        <p className="text-sm font-medium text-secondary">No data captured yet</p>
                        <p className="text-xs mt-1">Upload a document to extract financial data</p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {sectionConfig.map(section => {
                            const items = groupedData[section.id];
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
                                                {items.map((item, index) => (
                                                    <div
                                                        key={item.id}
                                                        className="group p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)] hover:border-[var(--border-strong)] transition-all cursor-pointer"
                                                        style={{ animationDelay: `${index * 30}ms` }}
                                                    >
                                                        <div className="flex items-start justify-between mb-3">
                                                            <span className="text-xs text-tertiary truncate flex-1 pr-2" title={item.label}>{item.label}</span>
                                                            <button className="btn-icon w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity">
                                                                <Edit2 className="w-3 h-3" />
                                                            </button>
                                                        </div>
                                                        <p className="text-lg font-bold font-mono tabular-nums text-primary">
                                                            {formatCurrency(item.currentYear)}
                                                        </p>
                                                        <div className="flex items-center gap-2 mt-2">
                                                            <span className={`text-xs font-medium ${item.variation >= 0 ? 'text-success' : 'text-error'}`}>
                                                                {item.variationPercent > 0 ? '+' : ''}{item.variationPercent.toFixed(1)}%
                                                            </span>
                                                            {item.sourcePage && (
                                                                <button
                                                                    className="text-xs text-tertiary hover:text-primary flex items-center gap-1 bg-[var(--bg-base)] px-1.5 py-0.5 rounded border border-transparent hover:border-[var(--border-default)] transition-all"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        onSourceClick?.(item);
                                                                    }}
                                                                >
                                                                    <FileText className="w-3 h-3" />
                                                                    {item.sourcePage}
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            /* List View */
                                            <div className="space-y-1 ml-2">
                                                {/* Header only for first section or repeated? Let's just render rows for cleanliness */}

                                                {items.map((item, index) => (
                                                    <div
                                                        key={item.id}
                                                        className="grid grid-cols-12 px-4 py-3 rounded-xl bg-[var(--bg-surface)] hover:bg-[var(--bg-hover)] items-center group transition-colors cursor-pointer border border-transparent hover:border-[var(--border-subtle)]"
                                                    >
                                                        <div className="col-span-4 text-sm font-medium text-primary truncate pr-4" title={item.label}>
                                                            {item.label}
                                                        </div>
                                                        <div className="col-span-2 text-sm font-mono tabular-nums text-primary">
                                                            {formatCurrency(item.currentYear)}
                                                        </div>
                                                        <div className="col-span-2 text-sm font-mono tabular-nums text-secondary">
                                                            {formatCurrency(item.previousYear)}
                                                        </div>
                                                        <div className="col-span-2 flex items-center gap-2">
                                                            <span className={`text-sm font-medium ${item.variation >= 0 ? 'text-success' : 'text-error'}`}>
                                                                {item.variation >= 0 ? '↗' : '↘'}
                                                            </span>
                                                            <span className={`pill text-xs ${item.variation >= 0 ? 'pill-positive' : 'pill-negative'}`}>
                                                                {item.variationPercent > 0 ? '+' : ''}{item.variationPercent.toFixed(1)}%
                                                            </span>
                                                        </div>
                                                        <div className="col-span-2 flex items-center justify-end gap-2">
                                                            <button
                                                                className="pill pill-neutral text-xs hover:bg-[var(--bg-elevated)] hover:text-primary transition-all cursor-pointer"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    onSourceClick?.(item);
                                                                }}
                                                            >
                                                                <FileText className="w-3 h-3" />
                                                                {item.sourcePage || 'N/A'}
                                                            </button>
                                                            <button className="btn-icon w-7 h-7 opacity-0 group-hover:opacity-100 transition-opacity">
                                                                <Edit2 className="w-3.5 h-3.5" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                ))}
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
