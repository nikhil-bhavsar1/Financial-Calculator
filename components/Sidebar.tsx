import React, { useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  Sparkles,
  Loader2,
  HelpCircle,
  AlertTriangle,
  XCircle,
  Target,
  ArrowRightCircle,
  Calendar,
  Check
} from 'lucide-react';
import { MissingInputItem, InputStatus } from '../types';

interface SidebarProps {
  items: MissingInputItem[];
  onConfirm: (items: MissingInputItem[]) => void;
  onAiAssist?: (label: string) => Promise<string>;
  yearLabels?: { current: string; previous: string };
  isCollapsed?: boolean;
  onToggle?: (collapsed: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  items,
  onConfirm,
  onAiAssist,
  yearLabels = { current: 'Current Year', previous: 'Previous Year' },
  isCollapsed = false,
  onToggle
}) => {
  const [localItems, setLocalItems] = useState<MissingInputItem[]>(items);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [aiHints, setAiHints] = useState<Record<string, string>>({});
  // Track pending values: key = `${itemId}_${year}`
  const [pendingValues, setPendingValues] = useState<Record<string, string>>({});

  React.useEffect(() => {
    setLocalItems(items);
  }, [items]);

  // Update pending value for specific year
  const handlePendingValueChange = (id: string, year: 'current' | 'previous', value: string) => {
    setPendingValues(prev => ({ ...prev, [`${id}_${year}`]: value }));
  };

  // Confirm value method
  const handleValueConfirm = (id: string, year: 'current' | 'previous') => {
    const key = `${id}_${year}`;
    const pendingValue = pendingValues[key];

    // Allow empty string to clear value? Assuming yes.
    if (pendingValue === undefined) return;

    // Find current item to check if other year is also filled
    const currentItem = localItems.find(i => i.id === id);
    if (!currentItem) return;

    // Get current stored values (fallback to legacy 'value' if first time)
    const existingValues = currentItem.values || {
      current: currentItem.value || '',
      previous: ''
    };

    const newValues = {
      ...existingValues,
      [year]: pendingValue
    };

    // Determine status: verified only if BOTH are filled? 
    // Or just if we have *some* data? 
    // Let's keep it partial (Active) until user marks "Done" or both filled?
    // For now: IF both filled, mark VERIFIED. Else stay active.
    const isComplete = newValues.current.trim() !== '' && newValues.previous.trim() !== '';
    const newStatus = isComplete ? InputStatus.VERIFIED : InputStatus.LOW_CONFIDENCE; // Keep active if partial

    const updatedItems = localItems.map(item =>
      item.id === id ? {
        ...item,
        values: newValues,
        value: newValues.current, // Sync legacy field
        status: newStatus
      } : item
    );

    setLocalItems(updatedItems);
    onConfirm(updatedItems);

    // Clear pending for this key
    setPendingValues(prev => {
      const newPending = { ...prev };
      delete newPending[key];
      return newPending;
    });
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, id: string, year: 'current' | 'previous') => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleValueConfirm(id, year);
    }
  };

  const handleTargetYearChange = (id: string, targetYear: 'current' | 'previous') => {
    const updatedItems = localItems.map(item =>
      item.id === id ? { ...item, targetYear } : item
    );
    setLocalItems(updatedItems);
    onConfirm(updatedItems);
  };

  const handleSkip = (id: string) => {
    const updatedItems = localItems.map(item =>
      item.id === id ? { ...item, status: InputStatus.SKIPPED } : item
    );
    setLocalItems(updatedItems);
    onConfirm(updatedItems);
  };

  const handleMarkDone = (id: string) => {
    const updatedItems = localItems.map(item =>
      item.id === id ? { ...item, status: InputStatus.VERIFIED } : item
    );
    setLocalItems(updatedItems);
    onConfirm(updatedItems);
  };

  const handleAiAssist = async (id: string, label: string) => {
    if (!onAiAssist) return;
    setLoadingId(id);
    try {
      const hint = await onAiAssist(label);
      setAiHints(prev => ({ ...prev, [id]: hint }));
    } catch (e) {
      console.error("AI Assist failed:", e);
    } finally {
      setLoadingId(null);
    }
  };

  const getStatusIcon = (status: InputStatus, confidence?: number) => {
    switch (status) {
      case InputStatus.NOT_FOUND:
        return <AlertCircle className="w-4 h-4 text-error" />;
      case InputStatus.LOW_CONFIDENCE:
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case InputStatus.VERIFIED:
        return <CheckCircle2 className="w-4 h-4 text-success" />;
      case InputStatus.SKIPPED:
        return <XCircle className="w-4 h-4 text-tertiary" />;
      default:
        return <HelpCircle className="w-4 h-4 text-tertiary" />;
    }
  };

  const getStatusLabel = (status: InputStatus, confidence?: number) => {
    switch (status) {
      case InputStatus.NOT_FOUND:
        return { text: 'Missing', class: 'pill-negative' };
      case InputStatus.LOW_CONFIDENCE:
        return { text: 'Partial', class: 'pill-warning' };
      case InputStatus.VERIFIED:
        return { text: 'Confirmed', class: 'pill-positive' };
      case InputStatus.SKIPPED:
        return { text: 'Skipped', class: 'pill-neutral' };
      default:
        return { text: 'Unknown', class: 'pill-neutral' };
    }
  };

  const activeItems = localItems.filter(item => item.status !== InputStatus.SKIPPED && item.status !== InputStatus.VERIFIED);
  const confirmedItems = localItems.filter(item => item.status === InputStatus.VERIFIED);
  const skippedItems = localItems.filter(item => item.status === InputStatus.SKIPPED);

  if (isCollapsed) {
    return (
      <div className="w-16 glass-sidebar flex flex-col items-center py-6 transition-all duration-300">
        <button
          onClick={() => onToggle?.(false)}
          className="btn-icon mb-6"
          title="Expand Sidebar"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <Target className="w-5 h-5 text-accent" />
            {activeItems.length > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-[var(--color-error)] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {activeItems.length}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-96 glass-sidebar flex flex-col transition-all duration-300 animate-slideInRight">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-default)]">
        <div>
          <h3 className="text-sm font-semibold text-primary">Missing Inputs</h3>
          <p className="text-xs text-tertiary mt-0.5">Enter separate values for periods</p>
        </div>
        <button
          onClick={() => onToggle?.(true)}
          className="btn-icon"
          title="Collapse Sidebar"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Items List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
        {activeItems.length === 0 && confirmedItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center animate-fadeIn">
            <div className="w-14 h-14 rounded-2xl bg-[var(--color-success-bg)] flex items-center justify-center mb-4">
              <CheckCircle2 className="w-7 h-7 text-success" />
            </div>
            <p className="text-sm font-medium text-primary">All inputs confirmed!</p>
            <p className="text-xs text-tertiary mt-1">No missing or low-confidence items</p>
          </div>
        ) : (
          <>
            {activeItems.map((item, index) => {
              const statusInfo = getStatusLabel(item.status, item.confidence);
              const activeYear = item.targetYear || 'current';
              const pendingKey = `${item.id}_${activeYear}`;

              // Resolve display value: Pending > Stored Value > Fallback
              const storedVal = item.values ? item.values[activeYear] : (activeYear === 'current' ? item.value : '');
              const displayVal = pendingValues[pendingKey] ?? storedVal ?? '';
              const hasUnsavedChanges = pendingValues[pendingKey] !== undefined;

              // Check completeness for visual feedback
              const currentFilled = item.values?.current || (item.value && !item.values);
              const prevFilled = item.values?.previous;

              return (
                <div
                  key={item.id}
                  className="glass-card p-4 space-y-3 animate-fadeIn"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Item Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(item.status, item.confidence)}
                      <div>
                        <span className="text-sm font-medium text-primary block">{item.label}</span>
                        <span className="text-[10px] text-tertiary">
                          {currentFilled ? 'Curr: ✅ ' : 'Curr: ❌ '}
                          {prevFilled ? 'Prev: ✅' : 'Prev: ❌'}
                        </span>
                      </div>
                    </div>
                    <span className={`pill text-[10px] ${statusInfo.class}`}>
                      {statusInfo.text}
                    </span>
                  </div>

                  {/* Input Field with Submit Icon */}
                  <div className="space-y-2">
                    <div className="relative">
                      <input
                        type="text"
                        value={displayVal}
                        onChange={(e) => handlePendingValueChange(item.id, activeYear, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, item.id, activeYear)}
                        placeholder={`Enter ${activeYear === 'current' ? yearLabels.current : yearLabels.previous} value...`}
                        className="glass-input w-full text-sm pr-10"
                      />
                      {/* Submit Icon Button */}
                      <button
                        onClick={() => handleValueConfirm(item.id, activeYear)}
                        disabled={!hasUnsavedChanges}
                        className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md transition-all ${hasUnsavedChanges
                            ? 'text-accent hover:bg-[var(--accent-primary)] hover:text-white cursor-pointer'
                            : 'text-tertiary opacity-50 cursor-not-allowed'
                          }`}
                        title="Submit value (Enter)"
                      >
                        <ArrowRightCircle className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Period Selector */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between items-center text-xs text-tertiary">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3 h-3" />
                          <span>Select period:</span>
                        </div>
                        {/* Done Button for partial completions */}
                        {(currentFilled || prevFilled) && (
                          <button
                            onClick={() => handleMarkDone(item.id)}
                            className="text-accent hover:underline flex items-center gap-1"
                          >
                            <Check className="w-3 h-3" /> Mark Done
                          </button>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleTargetYearChange(item.id, 'current')}
                          className={`flex-1 py-2 text-xs font-medium rounded-lg transition-all border ${activeYear === 'current'
                              ? 'bg-[var(--accent-primary)] text-white border-transparent shadow-sm'
                              : 'bg-[var(--bg-surface)] text-secondary hover:bg-[var(--bg-hover)] border-[var(--border-default)]'
                            }`}
                        >
                          {yearLabels.current || 'Current Year'}
                          {item.values?.current && <span className="ml-1 opacity-75">✓</span>}
                        </button>
                        <button
                          onClick={() => handleTargetYearChange(item.id, 'previous')}
                          className={`flex-1 py-2 text-xs font-medium rounded-lg transition-all border ${activeYear === 'previous'
                              ? 'bg-[var(--accent-primary)] text-white border-transparent shadow-sm'
                              : 'bg-[var(--bg-surface)] text-secondary hover:bg-[var(--bg-hover)] border-[var(--border-default)]'
                            }`}
                        >
                          {yearLabels.previous || 'Previous Year'}
                          {item.values?.previous && <span className="ml-1 opacity-75">✓</span>}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* AI Hint */}
                  {aiHints[item.id] && (
                    <div className="p-3 rounded-lg bg-[var(--color-info-bg)] border border-[var(--color-info-border)] animate-fadeIn">
                      <div className="flex items-start gap-2">
                        <Sparkles className="w-4 h-4 text-info flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-info leading-relaxed">{aiHints[item.id]}</p>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-1">
                    <button
                      onClick={() => handleAiAssist(item.id, item.label)}
                      disabled={loadingId === item.id}
                      className="btn-ghost text-xs text-accent"
                    >
                      {loadingId === item.id ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Sparkles className="w-3.5 h-3.5" />
                      )}
                      <span>Locate</span>
                    </button>
                    <button
                      onClick={() => handleSkip(item.id)}
                      className="btn-ghost text-xs text-tertiary"
                    >
                      <span>Mark N/A</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </>
        )}

        {/* Confirmed Items */}
        {confirmedItems.length > 0 && (
          <div className="pt-4 border-t border-[var(--border-default)]">
            <p className="label-uppercase mb-3 text-success">Confirmed ({confirmedItems.length})</p>
            <div className="space-y-2">
              {confirmedItems.map(item => (
                <div key={item.id} className="flex items-center justify-between py-2 px-3 rounded-lg bg-[var(--color-success-bg)] border border-[var(--color-success-border)]">
                  <div className="flex flex-col flex-1">
                    <span className="text-xs font-medium text-primary">{item.label}</span>
                    <div className="flex gap-4 mt-1">
                      <span className="text-xs text-secondary">
                        C: <span className="font-mono text-primary">{item.values?.current || item.value || '-'}</span>
                      </span>
                      <span className="text-xs text-secondary">
                        P: <span className="font-mono text-primary">{item.values?.previous || '-'}</span>
                      </span>
                    </div>
                  </div>
                  <CheckCircle2 className="w-4 h-4 text-success" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Skipped Items */}
        {skippedItems.length > 0 && (
          <div className="pt-4 border-t border-[var(--border-default)]">
            <p className="label-uppercase mb-3">Skipped ({skippedItems.length})</p>
            <div className="space-y-2">
              {skippedItems.map(item => (
                <div key={item.id} className="flex items-center justify-between py-2 px-3 rounded-lg bg-[var(--bg-surface)] opacity-60">
                  <span className="text-xs text-tertiary">{item.label}</span>
                  <XCircle className="w-3.5 h-3.5 text-tertiary" />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;