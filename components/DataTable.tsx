import React from 'react';
import { FileText, Edit2, AlertTriangle, Calculator, Filter, XCircle, Download, Inbox } from 'lucide-react';
import { FinancialItem } from '../types';

interface DataTableProps {
  data: FinancialItem[];
  onUnpin?: (id: string) => void;
  onEdit?: (id: string) => void;
  searchTerm?: string;
  yearLabels?: { current: string; previous: string };
}

export const DataTable: React.FC<DataTableProps> = ({
  data,
  onUnpin,
  onEdit,
  searchTerm = '',
  yearLabels = { current: new Date().getFullYear().toString(), previous: (new Date().getFullYear() - 1).toString() }
}) => {
  // Filter data based on search term
  const filteredData = data.filter(item =>
    item.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.id.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const getVariationDisplay = (variation: number) => {
    const isPositive = variation > 0;
    const isNegative = variation < 0;

    return {
      arrow: isPositive ? '↗' : isNegative ? '↘' : '→',
      colorClass: isPositive
        ? 'text-success'
        : isNegative
          ? 'text-error'
          : 'text-secondary',
      pillClass: isPositive
        ? 'pill-positive'
        : isNegative
          ? 'pill-negative'
          : 'pill-neutral',
    };
  };

  return (
    <div className="flex-1 flex flex-col m-4 glass-card overflow-hidden animate-fadeIn">
      {/* Table Toolbar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-default)]">
        <h2 className="label-uppercase text-sm tracking-wide">Company Financial Summary</h2>
        <div className="flex items-center gap-2">
          <button className="btn-ghost">
            <Filter className="w-4 h-4" />
            <span>Filter</span>
          </button>
          <button className="btn-ghost">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-12 px-6 py-3 border-b border-[var(--border-default)] bg-[var(--bg-surface)]">
        <div className="col-span-3 text-xs font-bold uppercase tracking-wide text-secondary">Line Item</div>
        <div className="col-span-2 text-xs font-bold uppercase tracking-wide text-secondary">
          Current Year
          <span className="block text-tertiary font-normal normal-case text-[10px] mt-0.5">({yearLabels.current})</span>
        </div>
        <div className="col-span-2 text-xs font-bold uppercase tracking-wide text-secondary">
          Previous Year
          <span className="block text-tertiary font-normal normal-case text-[10px] mt-0.5">({yearLabels.previous})</span>
        </div>
        <div className="col-span-3 text-xs font-bold uppercase tracking-wide text-secondary">Variation</div>
        <div className="col-span-2 text-xs font-bold uppercase tracking-wide text-secondary text-right pr-4">Source</div>
      </div>

      {/* Table Body */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pb-24">
        {filteredData.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-tertiary animate-fadeIn">
            <div className="w-16 h-16 rounded-2xl bg-[var(--bg-surface)] flex items-center justify-center mb-4">
              <Inbox className="w-8 h-8 opacity-50" />
            </div>
            <p className="text-sm font-medium text-secondary">{searchTerm ? 'No matching items' : 'No items pinned to summary'}</p>
            <p className="text-xs mt-1">{searchTerm ? 'Try a different search term' : 'Go to "All Metrics" to select items'}</p>
          </div>
        ) : (
          filteredData.map((item, index) => {
            const variation = getVariationDisplay(item.variation);

            return (
              <div
                key={item.id}
                className="glass-table-row grid grid-cols-12 px-6 py-4 items-center group animate-fadeIn"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                {/* Label */}
                <div className="col-span-3 flex items-center gap-2.5">
                  <span className="font-bold text-primary text-sm">{item.label}</span>
                  {item.hasWarning && (
                    <div className="icon-badge icon-badge-orange">
                      <AlertTriangle className="w-3 h-3" />
                    </div>
                  )}
                  {item.isAutoCalc && (
                    <div className="icon-badge icon-badge-blue">
                      <Calculator className="w-3 h-3" />
                    </div>
                  )}
                </div>

                {/* Current Year */}
                <div className="col-span-2 font-mono text-primary text-sm tabular-nums">
                  {formatCurrency(item.currentYear)}
                </div>

                {/* Previous Year */}
                <div className="col-span-2 font-mono text-secondary text-sm tabular-nums">
                  {formatCurrency(item.previousYear)}
                </div>

                {/* Variation */}
                <div className="col-span-3 flex items-center gap-2">
                  <span className={`text-lg ${variation.colorClass}`}>
                    {variation.arrow}
                  </span>
                  <span className={`font-mono text-sm tabular-nums ${variation.colorClass}`}>
                    {item.variation > 0 ? '+' : ''}
                    {formatCurrency(item.variation)}
                  </span>
                  <span className={`pill ${variation.pillClass}`}>
                    {item.variationPercent > 0 ? '+' : ''}
                    {item.variationPercent.toFixed(1)}%
                  </span>
                </div>

                {/* Source / Actions */}
                <div className="col-span-2 flex items-center justify-end gap-2">
                  {item.isAutoCalc ? (
                    <span className="pill pill-info">Auto-Calc</span>
                  ) : (
                    <span className="pill pill-neutral">
                      <FileText className="w-3 h-3" />
                      {item.sourcePage}
                    </span>
                  )}

                  {/* Hover Actions */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 translate-x-2 group-hover:translate-x-0 transition-all duration-200">
                    {item.isAutoCalc && onUnpin && (
                      <button
                        onClick={() => onUnpin(item.id)}
                        className="btn-icon danger"
                        title="Remove from Summary"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => onEdit?.(item.id)}
                      className="btn-icon"
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default DataTable;
