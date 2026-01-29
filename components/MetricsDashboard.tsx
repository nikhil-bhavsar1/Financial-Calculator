import React, { useState } from 'react';
import {
  Search,
  TrendingUp,
  TrendingDown,
  Pin,
  PinOff,
  ChevronDown,
  ChevronRight,
  Calculator,
  BarChart3,
  Layers,
  X,
  BookOpen,
  Sparkles,
  AlertCircle,
  ArrowLeft,
  Clock,
  Target,
  Lightbulb
} from 'lucide-react';
import { MetricGroup, FinancialItem } from '../types';
import { getFormulaById, MetricDefinition } from '../library/allMetrics';

interface MetricsDashboardProps {
  groups: MetricGroup[];
  pinnedIds: Set<string>;
  onTogglePin: (id: string) => void;
  searchTerm?: string;
  epsType?: 'basic' | 'diluted';
  onEpsTypeChange?: (type: 'basic' | 'diluted') => void;
}

export const MetricsDashboard: React.FC<MetricsDashboardProps> = ({ groups, pinnedIds, onTogglePin, searchTerm = '', epsType = 'basic', onEpsTypeChange }) => {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(groups.map(g => g.category)));
  const [selectedMetric, setSelectedMetric] = useState<FinancialItem | null>(null);
  const [metricDetails, setMetricDetails] = useState<MetricDefinition | null>(null);

  const toggleGroup = (category: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  const handleMetricClick = (item: FinancialItem) => {
    setSelectedMetric(item);
    const details = getFormulaById(item.id);
    setMetricDetails(details || null);
  };

  const closeDetailView = () => {
    setSelectedMetric(null);
    setMetricDetails(null);
  };

  const formatValue = (val: number, isPercent: boolean = false) => {
    if (isPercent || Math.abs(val) < 100) {
      return val.toFixed(2) + (isPercent ? '%' : 'x');
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
      notation: val > 1000000 ? 'compact' : 'standard'
    }).format(val);
  };

  const getValueColor = (variation: number) => {
    if (variation > 0) return 'text-success';
    if (variation < 0) return 'text-error';
    return 'text-secondary';
  };

  const getCategoryIcon = (category: string) => {
    const lower = category.toLowerCase();
    if (lower.includes('valuation')) return <BarChart3 className="w-4 h-4" />;
    if (lower.includes('profitability')) return <TrendingUp className="w-4 h-4" />;
    if (lower.includes('efficiency')) return <Layers className="w-4 h-4" />;
    return <Calculator className="w-4 h-4" />;
  };

  const isPercentMetric = (label: string) => {
    const lower = label.toLowerCase();
    return lower.includes('margin') ||
      lower.includes('ratio') ||
      lower.includes('yield') ||
      lower.includes('return') ||
      lower.includes('growth');
  };

  const filteredGroups = groups.map(group => ({
    ...group,
    items: group.items.filter(item =>
      item.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.id.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(group => group.items.length > 0);

  // Full Page Detail View
  if (selectedMetric) {
    const isPinned = pinnedIds.has(selectedMetric.id);

    return (
      <div className="flex-1 flex flex-col bg-[var(--bg-base)] animate-fadeIn">
        {/* Header */}
        <div className="glass-nav px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button onClick={closeDetailView} className="btn-icon">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-lg font-semibold text-primary">{selectedMetric.label}</h1>
              <p className="text-xs text-tertiary">Calculation Breakdown & Analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* EPS Toggle for relevant metrics */}
            {(selectedMetric.label.toLowerCase().includes('p/e') ||
              selectedMetric.label.toLowerCase().includes('earnings yield') ||
              selectedMetric.id === 'basic_eps' || selectedMetric.id === 'diluted_eps') && onEpsTypeChange && (
                <div className="flex items-center p-1 bg-[var(--bg-surface)] border border-[var(--border-default)] rounded-lg mr-2">
                  <button
                    onClick={() => onEpsTypeChange('basic')}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${epsType === 'basic' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-tertiary hover:text-primary'}`}
                  >
                    Basic
                  </button>
                  <button
                    onClick={() => onEpsTypeChange('diluted')}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${epsType === 'diluted' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-tertiary hover:text-primary'}`}
                  >
                    Diluted
                  </button>
                </div>
              )}

            <button
              onClick={() => onTogglePin(selectedMetric.id)}
              className={isPinned ? 'btn-secondary' : 'btn-primary'}
            >
              {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
              <span>{isPinned ? 'Unpin' : 'Pin'}</span>
            </button>
            <button onClick={closeDetailView} className="btn-icon">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-scroll custom-scrollbar p-6 pb-24 h-full">
          <div className="max-w-5xl mx-auto space-y-6">

            {/* Value Cards Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Current Value */}
              <div className="glass-card p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Target className="w-4 h-4 text-accent" />
                  <p className="label-uppercase">Current Value</p>
                </div>
                <p className={`text-4xl font-bold font-mono tabular-nums ${getValueColor(selectedMetric.variation)}`}>
                  {formatValue(selectedMetric.currentYear, isPercentMetric(selectedMetric.label))}
                </p>
                <div className="flex items-center justify-center gap-2 mt-3">
                  <span className={`pill ${selectedMetric.variation >= 0 ? 'pill-positive' : 'pill-negative'}`}>
                    {selectedMetric.variation > 0 && '+'}{selectedMetric.variationPercent.toFixed(1)}%
                  </span>
                  <span className="text-xs text-tertiary">vs prior</span>
                </div>
              </div>

              {/* Prior Value */}
              <div className="glass-card p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Clock className="w-4 h-4 text-secondary" />
                  <p className="label-uppercase">Prior Period</p>
                </div>
                <p className="text-4xl font-bold font-mono tabular-nums text-secondary">
                  {formatValue(selectedMetric.previousYear, isPercentMetric(selectedMetric.label))}
                </p>
                <p className="text-xs text-tertiary mt-3">Previous year value</p>
              </div>

              {/* Change */}
              <div className="glass-card p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-3">
                  {selectedMetric.variation >= 0
                    ? <TrendingUp className="w-4 h-4 text-success" />
                    : <TrendingDown className="w-4 h-4 text-error" />
                  }
                  <p className="label-uppercase">Change</p>
                </div>
                <p className={`text-4xl font-bold font-mono tabular-nums ${getValueColor(selectedMetric.variation)}`}>
                  {selectedMetric.variation > 0 && '+'}{formatValue(selectedMetric.variation, isPercentMetric(selectedMetric.label))}
                </p>
                <p className={`text-xs mt-3 ${getValueColor(selectedMetric.variation)}`}>
                  {selectedMetric.variation > 0 ? 'Improvement' : selectedMetric.variation < 0 ? 'Decline' : 'No change'}
                </p>
              </div>
            </div>

            {/* Formula Section */}
            {metricDetails && (
              <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-[var(--accent-primary)]/10 flex items-center justify-center">
                    <Calculator className="w-5 h-5 text-accent" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-primary">Formula</h3>
                    <p className="text-xs text-tertiary">Mathematical definition</p>
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <code className="text-lg font-mono text-primary leading-relaxed block text-center">
                    {metricDetails.formula}
                  </code>
                </div>
              </div>
            )}

            {/* Calculation Steps */}
            {metricDetails?.breakdown && metricDetails.breakdown.length > 0 && (
              <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-primary">Step-by-Step Calculation</h3>
                    <p className="text-xs text-tertiary">How this metric is calculated</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {metricDetails.breakdown.map((step, index) => (
                    <div
                      key={index}
                      className="relative flex gap-4 animate-fadeIn"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      {/* Step Number */}
                      <div className="flex flex-col items-center">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold ${index === metricDetails.breakdown!.length - 1
                          ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
                          : 'bg-[var(--bg-surface)] border-2 border-[var(--accent-primary)] text-accent'
                          }`}>
                          {index + 1}
                        </div>
                        {index < metricDetails.breakdown!.length - 1 && (
                          <div className="w-0.5 flex-1 min-h-[20px] bg-[var(--border-default)] mt-2" />
                        )}
                      </div>

                      {/* Step Content */}
                      <div className="flex-1 pb-4">
                        <h4 className="text-sm font-semibold text-primary mb-2">{step.step}</h4>
                        <div className="p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)] mb-2">
                          <code className="text-sm font-mono text-secondary">{step.formula}</code>
                        </div>
                        {step.description && (
                          <p className="text-sm text-tertiary leading-relaxed">{step.description}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Interpretation Guide */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[var(--color-info-bg)] flex items-center justify-center">
                  <Lightbulb className="w-5 h-5 text-info" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-primary">How to Interpret</h3>
                  <p className="text-xs text-tertiary">Understanding this metric</p>
                </div>
              </div>
              <div className="space-y-3 text-sm text-secondary leading-relaxed">
                {getInterpretationGuide(selectedMetric.label, selectedMetric.variation)}
              </div>
            </div>

            {/* Related Metrics */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[var(--bg-surface)] flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-secondary" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-primary">Key Considerations</h3>
                  <p className="text-xs text-tertiary">Important context for analysis</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <h4 className="text-xs font-semibold text-primary mb-2">✓ Best Practices</h4>
                  <ul className="text-xs text-tertiary space-y-1">
                    <li>• Compare against industry peers</li>
                    <li>• Track trends over multiple periods</li>
                    <li>• Consider economic context</li>
                  </ul>
                </div>
                <div className="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-default)]">
                  <h4 className="text-xs font-semibold text-primary mb-2">⚠️ Limitations</h4>
                  <ul className="text-xs text-tertiary space-y-1">
                    <li>• Point-in-time snapshot only</li>
                    <li>• May vary by accounting methods</li>
                    <li>• Use with other metrics for context</li>
                  </ul>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    );
  }

  // Grid View (Default)
  return (
    <div className="flex-1 flex flex-col p-4 overflow-hidden">
      {/* Search Bar & Toggles */}
      <div className="flex items-center justify-between gap-4 mb-4 px-1">

      </div>

      {/* Categories */}
      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4 pr-2 pb-24">
        {filteredGroups.map((group, groupIndex) => (
          <div
            key={group.category}
            className="glass-card overflow-hidden animate-fadeIn"
            style={{ animationDelay: `${groupIndex * 50}ms` }}
          >
            {/* Category Header */}
            <button
              onClick={() => toggleGroup(group.category)}
              className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--bg-hover)] transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-[var(--accent-primary)]/10 flex items-center justify-center text-accent">
                  {getCategoryIcon(group.category)}
                </div>
                <div className="text-left">
                  <h3 className="text-sm font-semibold text-primary">{group.category}</h3>
                  <p className="text-xs text-tertiary">{group.items.length} metrics</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="pill pill-accent text-xs">
                  {group.items.filter(i => pinnedIds.has(i.id)).length} pinned
                </span>

                {expandedGroups.has(group.category) ? (
                  <ChevronDown className="w-5 h-5 text-tertiary" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-tertiary" />
                )}
              </div>
            </button>

            {/* Metrics Grid */}
            {expandedGroups.has(group.category) && (
              <div className="px-4 pb-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {group.items.map((item, itemIndex) => {
                    const isPinned = pinnedIds.has(item.id);

                    return (
                      <div
                        key={item.id}
                        onClick={() => handleMetricClick(item)}
                        className={`group relative p-4 rounded-xl border cursor-pointer transition-all duration-200 animate-fadeIn hover:scale-[1.02] bg-[var(--bg-surface)] border-[var(--border-default)] hover:border-[var(--border-strong)] ${isPinned ? 'ring-1 ring-[var(--accent-primary)]/50 border-[var(--accent-primary)]/50' : ''
                          }`}
                        style={{ animationDelay: `${(groupIndex * 50) + (itemIndex * 30)}ms` }}
                      >
                        {/* Pin Button */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onTogglePin(item.id);
                          }}
                          className={`absolute top-3 right-3 w-7 h-7 rounded-lg flex items-center justify-center transition-all ${isPinned
                            ? 'bg-[var(--accent-primary)] text-white'
                            : 'bg-[var(--bg-hover)] text-tertiary opacity-0 group-hover:opacity-100'
                            }`}
                          title={isPinned ? 'Unpin' : 'Pin'}
                        >
                          {isPinned ? <PinOff className="w-3.5 h-3.5" /> : <Pin className="w-3.5 h-3.5" />}
                        </button>

                        {/* Metric Content */}
                        <div className="pr-8">
                          {/* Improved Readability: Bolder & Brighter Label */}
                          <p className="text-sm font-bold text-primary mb-1.5 truncate leading-tight tracking-tight">
                            {item.label}
                          </p>
                          <p className={`text-xl font-bold font-mono tabular-nums ${getValueColor(item.variation)}`}>
                            {formatValue(item.currentYear, isPercentMetric(item.label))}
                          </p>

                          {item.calculationError ? (
                            <div className="flex items-center gap-1.5 mt-2 text-xs text-warning">
                              <AlertCircle className="w-3 h-3" />
                              <span className="truncate">{item.calculationError}</span>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2 mt-2">
                              {item.variation !== 0 && (
                                item.variation > 0
                                  ? <TrendingUp className="w-3.5 h-3.5 text-success" />
                                  : <TrendingDown className="w-3.5 h-3.5 text-error" />
                              )}
                              <span className={`text-xs font-medium ${getValueColor(item.variation)}`}>
                                {item.variationPercent > 0 ? '+' : ''}{item.variationPercent.toFixed(1)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {/* Empty State for Category Search */}
            {group.items.length === 0 && (
              <div className="px-5 pb-5 text-center">
                <p className="text-xs text-tertiary">No metrics match your search</p>
              </div>
            )}
          </div>
        ))}

        {filteredGroups.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center animate-fadeIn">
            <Search className="w-12 h-12 text-tertiary opacity-40 mb-4" />
            <p className="text-sm font-medium text-secondary">No metrics found</p>
            <p className="text-xs text-tertiary mt-1">Try a different search term in the categories</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Interpretation guide helper
function getInterpretationGuide(label: string, variation: number): React.ReactNode {
  const l = label.toLowerCase();
  const trend = variation > 0 ? 'increased' : variation < 0 ? 'decreased' : 'remained stable';
  const trendClass = variation > 0 ? 'text-success' : variation < 0 ? 'text-error' : 'text-secondary';

  if (l.includes('p/e') || (l.includes('price') && l.includes('earnings'))) {
    return (
      <>
        <p>The <strong>P/E Ratio</strong> measures how much investors pay per dollar of earnings.</p>
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="p-2 rounded-lg bg-[var(--color-success-bg)] text-center">
            <p className="text-xs font-semibold text-success">Low (&lt;15)</p>
            <p className="text-[10px] text-success/70">Undervalued</p>
          </div>
          <div className="p-2 rounded-lg bg-[var(--color-warning-bg)] text-center">
            <p className="text-xs font-semibold text-warning">Avg (15-25)</p>
            <p className="text-[10px] text-warning/70">Fair value</p>
          </div>
          <div className="p-2 rounded-lg bg-[var(--color-error-bg)] text-center">
            <p className="text-xs font-semibold text-error">High (&gt;25)</p>
            <p className="text-[10px] text-error/70">Premium/Growth</p>
          </div>
        </div>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ This metric has {trend} vs prior period.</p>
      </>
    );
  }

  if (l.includes('peg')) {
    return (
      <>
        <p>The <strong>PEG Ratio</strong> adjusts P/E for growth, providing a more complete valuation picture.</p>
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="p-2 rounded-lg bg-[var(--color-success-bg)] text-center">
            <p className="text-xs font-semibold text-success">PEG &lt; 1.0</p>
            <p className="text-[10px] text-success/70">Undervalued</p>
          </div>
          <div className="p-2 rounded-lg bg-[var(--bg-surface)] text-center">
            <p className="text-xs font-semibold text-secondary">PEG = 1.0</p>
            <p className="text-[10px] text-tertiary">Fair value</p>
          </div>
          <div className="p-2 rounded-lg bg-[var(--color-error-bg)] text-center">
            <p className="text-xs font-semibold text-error">PEG &gt; 1.0</p>
            <p className="text-[10px] text-error/70">Overvalued</p>
          </div>
        </div>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ This metric has {trend} vs prior period.</p>
      </>
    );
  }

  if (l.includes('margin')) {
    return (
      <>
        <p><strong>Profit margins</strong> measure what percentage of revenue becomes profit at various stages.</p>
        <ul className="mt-2 space-y-1 text-tertiary">
          <li>• Higher margins indicate better cost control and pricing power</li>
          <li>• Compare against industry peers for meaningful context</li>
          <li>• Consistent or improving margins signal operational strength</li>
        </ul>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ This margin has {trend}, indicating {variation > 0 ? 'improved' : 'reduced'} profitability.</p>
      </>
    );
  }

  if (l.includes('return on') || l.includes('roe') || l.includes('roa') || l.includes('roic')) {
    return (
      <>
        <p><strong>Return metrics</strong> measure how efficiently capital is used to generate profits.</p>
        <ul className="mt-2 space-y-1 text-tertiary">
          <li>• ROE &gt; 15% is generally considered strong</li>
          <li>• Compare with cost of capital (WACC) for value creation</li>
          <li>• Consistently high returns often indicate competitive advantages</li>
        </ul>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ Returns have {trend}, suggesting {variation > 0 ? 'improved' : 'reduced'} capital efficiency.</p>
      </>
    );
  }

  if (l.includes('current ratio') || l.includes('quick ratio') || l.includes('cash ratio')) {
    return (
      <>
        <p><strong>Liquidity ratios</strong> measure ability to meet short-term obligations.</p>
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="p-2 rounded-lg bg-[var(--color-success-bg)] text-center">
            <p className="text-xs font-semibold text-success">&gt; 1.5</p>
            <p className="text-[10px] text-success/70">Strong</p>
          </div>
          <div className="p-2 rounded-lg bg-[var(--color-warning-bg)] text-center">
            <p className="text-xs font-semibold text-warning">1.0 - 1.5</p>
            <p className="text-[10px] text-warning/70">Adequate</p>
          </div>
          <div className="p-2 rounded-lg bg-[var(--color-error-bg)] text-center">
            <p className="text-xs font-semibold text-error">&lt; 1.0</p>
            <p className="text-[10px] text-error/70">Risky</p>
          </div>
        </div>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ Liquidity has {trend} compared to prior period.</p>
      </>
    );
  }

  if (l.includes('debt') || l.includes('leverage') || l.includes('coverage')) {
    return (
      <>
        <p><strong>Leverage metrics</strong> assess financial risk and debt capacity.</p>
        <ul className="mt-2 space-y-1 text-tertiary">
          <li>• Lower debt ratios generally indicate lower financial risk</li>
          <li>• Interest coverage &gt; 3x is typically considered safe</li>
          <li>• Compare with industry norms as capital intensity varies</li>
        </ul>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ Leverage has {trend} vs prior period.</p>
      </>
    );
  }

  if (l.includes('growth')) {
    return (
      <>
        <p><strong>Growth rates</strong> measure the pace of expansion in key metrics.</p>
        <ul className="mt-2 space-y-1 text-tertiary">
          <li>• Positive growth indicates business momentum</li>
          <li>• Compare growth rate to industry and economic growth</li>
          <li>• Sustainable growth rate = ROE × (1 - Payout Ratio)</li>
        </ul>
        <p className={`mt-3 font-medium ${trendClass}`}>↳ Growth pace has {trend} compared to prior period.</p>
      </>
    );
  }

  return (
    <>
      <p>This metric provides insight into the company's financial health and performance.</p>
      <ul className="mt-2 space-y-1 text-tertiary">
        <li>• Compare against historical trends for the company</li>
        <li>• Benchmark against industry peers</li>
        <li>• Consider in context of overall business strategy</li>
      </ul>
      <p className={`mt-3 font-medium ${trendClass}`}>↳ This metric has {trend} vs prior period.</p>
    </>
  );
}

export default MetricsDashboard;
