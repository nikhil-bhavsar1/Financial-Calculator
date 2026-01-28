import React, { useState, useEffect, useMemo } from 'react';
import {
  X, Database, Plus, Trash2, Save, Search, BookOpen, Edit2,
  ArrowLeft, Check, ChevronDown, ChevronRight, Tag, Inbox
} from 'lucide-react';
import { TermMapping, CATEGORY_OPTIONS } from '../types';

interface KnowledgeBaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  mappings: TermMapping[];
  onSave: (newMappings: TermMapping[]) => void;
  inline?: boolean;
}

export const KnowledgeBaseModal: React.FC<KnowledgeBaseModalProps> = ({
  isOpen, onClose, mappings, onSave, inline = false
}) => {
  const [localMappings, setLocalMappings] = useState<TermMapping[]>(() => JSON.parse(JSON.stringify(mappings)));
  const [searchFilter, setSearchFilter] = useState('');
  const [activeTermIndex, setActiveTermIndex] = useState<number | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (isOpen || inline) {
      setLocalMappings(JSON.parse(JSON.stringify(mappings)));
      setSearchFilter('');
      setActiveTermIndex(null);
      const categories = new Set(mappings.map(m => m.category || 'Misc'));
      setExpandedCategories(categories);
    }
  }, [isOpen, mappings, inline]);

  const groupedMappings = useMemo(() => {
    const filtered = localMappings.filter(
      m => m.label.toLowerCase().includes(searchFilter.toLowerCase()) ||
        m.key.toLowerCase().includes(searchFilter.toLowerCase()) ||
        (m.category && m.category.toLowerCase().includes(searchFilter.toLowerCase())) ||
        m.keywords_indas?.some(k => k.toLowerCase().includes(searchFilter.toLowerCase())) ||
        m.keywords_gaap?.some(k => k.toLowerCase().includes(searchFilter.toLowerCase())) ||
        m.keywords_ifrs?.some(k => k.toLowerCase().includes(searchFilter.toLowerCase()))
    );

    const groups: Record<string, TermMapping[]> = {};
    filtered.forEach(item => {
      const cat = item.category || 'Misc';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(item);
    });
    return groups;
  }, [localMappings, searchFilter]);

  const categories = useMemo(() => Object.keys(groupedMappings).sort(), [groupedMappings]);

  if (!isOpen && !inline) return null;

  const handleKeywordChange = (index: number, field: 'keywords_indas' | 'keywords_gaap' | 'keywords_ifrs', newKeywordsStr: string) => {
    const newKeywords = newKeywordsStr.split(',');
    setLocalMappings(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: newKeywords };
      return updated;
    });
  };

  const handleFieldChange = (index: number, field: keyof TermMapping, value: any) => {
    setLocalMappings(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleRelatedStandardChange = (index: number, standard: 'indas' | 'gaap' | 'ifrs', value: string) => {
    setLocalMappings(prev => {
      const updated = [...prev];
      const current = updated[index].related_standards || {};
      updated[index] = {
        ...updated[index],
        related_standards: {
          ...current,
          [standard]: value.split(',').map(s => s.trim()).filter(Boolean)
        }
      };
      return updated;
    });
  };

  const addNewTerm = () => {
    const newTerm: TermMapping = {
      id: `TERM_${Date.now()}`,
      category: 'Misc',
      key: 'new_term',
      label: 'New Term',
      description: '',
      keywords_indas: [],
      keywords_gaap: [],
      keywords_ifrs: [],
      sign_convention: 'both',
      data_type: 'currency',
      priority: 1
    };
    setLocalMappings(prev => [newTerm, ...prev]);
    setActiveTermIndex(0);
  };

  const removeTerm = (index: number) => {
    setLocalMappings(prev => {
      const updated = [...prev];
      updated.splice(index, 1);
      return updated;
    });
    if (activeTermIndex === index) setActiveTermIndex(null);
  };

  const saveAndClose = () => {
    const sanitized = localMappings.map(m => ({
      ...m,
      category: m.category || 'Misc',
      keywords_indas: (m.keywords_indas || []).map(k => k.trim()).filter(k => k.length > 0),
      keywords_gaap: (m.keywords_gaap || []).map(k => k.trim()).filter(k => k.length > 0),
      keywords_ifrs: (m.keywords_ifrs || []).map(k => k.trim()).filter(k => k.length > 0),
    }));
    onSave(sanitized);
    if (!inline) onClose();
  };

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  // Editor View
  if (activeTermIndex !== null) {
    const term = localMappings[activeTermIndex];
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fadeIn" onClick={() => setActiveTermIndex(null)} />

        <div className="relative w-full max-w-4xl glass-modal overflow-hidden animate-fadeInScale max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--border-default)]">
            <div className="flex items-center gap-4">
              <button onClick={() => setActiveTermIndex(null)} className="btn-icon">
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
                  <Edit2 className="w-5 h-5 text-accent" />
                  Edit Terminology
                </h3>
                <p className="text-xs text-tertiary mt-0.5">Configure standard term ID and keyword matching rules</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="label-uppercase">ID</label>
                <input
                  value={term.id || ''}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'id', e.target.value)}
                  className="glass-input w-full font-mono text-xs"
                  placeholder="e.g. REV_001"
                />
              </div>
              <div className="space-y-2">
                <label className="label-uppercase">System Key</label>
                <input
                  value={term.key}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'key', e.target.value)}
                  className="glass-input w-full font-mono text-sm"
                  placeholder="e.g. total_revenue"
                />
              </div>
              <div className="col-span-2 space-y-2">
                <label className="label-uppercase">Display Name</label>
                <input
                  value={term.label}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'label', e.target.value)}
                  className="glass-input w-full font-medium"
                  placeholder="e.g. Total Revenue"
                />
              </div>
            </div>

            {/* Description & Category */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="label-uppercase">Category</label>
                <div className="relative">
                  <select
                    value={term.category || 'Misc'}
                    onChange={(e) => handleFieldChange(activeTermIndex, 'category', e.target.value)}
                    className="glass-input w-full appearance-none cursor-pointer pr-10"
                  >
                    {CATEGORY_OPTIONS.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary pointer-events-none" />
                </div>
              </div>
              <div className="space-y-2">
                <label className="label-uppercase">Subcategory (Optional)</label>
                <input
                  value={term.subcategory || ''}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'subcategory', e.target.value)}
                  className="glass-input w-full"
                  placeholder="e.g. Operating"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="label-uppercase">Description</label>
              <textarea
                value={term.description || ''}
                onChange={(e) => handleFieldChange(activeTermIndex, 'description', e.target.value)}
                className="glass-input w-full h-20 resize-none text-sm"
                placeholder="Describe this term..."
              />
            </div>

            {/* Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-[var(--bg-surface)] rounded-xl border border-[var(--border-subtle)]">
              <div className="space-y-2">
                <label className="label-uppercase">Sign Convention</label>
                <select
                  value={term.sign_convention || 'both'}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'sign_convention', e.target.value)}
                  className="glass-input w-full"
                >
                  <option value="positive">Always Positive</option>
                  <option value="negative">Always Negative</option>
                  <option value="both">Both / Neutral</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="label-uppercase">Data Type</label>
                <select
                  value={term.data_type || 'currency'}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'data_type', e.target.value)}
                  className="glass-input w-full"
                >
                  <option value="currency">Currency</option>
                  <option value="percentage">Percentage</option>
                  <option value="ratio">Ratio</option>
                  <option value="number">Number</option>
                  <option value="date">Date</option>
                  <option value="text">Text</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="label-uppercase">Priority</label>
                <input
                  type="number"
                  value={term.priority ?? 1}
                  onChange={(e) => handleFieldChange(activeTermIndex, 'priority', parseInt(e.target.value))}
                  className="glass-input w-full"
                />
              </div>
            </div>

            {/* Related Standards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="label-uppercase text-orange-600">Related IndAS</label>
                <input
                  value={term.related_standards?.indas?.join(', ') || ''}
                  onChange={(e) => handleRelatedStandardChange(activeTermIndex, 'indas', e.target.value)}
                  className="glass-input w-full text-xs"
                  placeholder="e.g. IndAS 115"
                />
              </div>
              <div className="space-y-2">
                <label className="label-uppercase text-blue-600">Related GAAP</label>
                <input
                  value={term.related_standards?.gaap?.join(', ') || ''}
                  onChange={(e) => handleRelatedStandardChange(activeTermIndex, 'gaap', e.target.value)}
                  className="glass-input w-full text-xs"
                  placeholder="e.g. ASC 606"
                />
              </div>
              <div className="space-y-2">
                <label className="label-uppercase text-purple-600">Related IFRS</label>
                <input
                  value={term.related_standards?.ifrs?.join(', ') || ''}
                  onChange={(e) => handleRelatedStandardChange(activeTermIndex, 'ifrs', e.target.value)}
                  className="glass-input w-full text-xs"
                  placeholder="e.g. IFRS 15"
                />
              </div>
            </div>

            {/* Keywords Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-orange-500" />
                  <label className="label-uppercase">IndAS Keywords</label>
                </div>
                <textarea
                  value={(term.keywords_indas || []).join(', ')}
                  onChange={(e) => handleKeywordChange(activeTermIndex, 'keywords_indas', e.target.value)}
                  className="glass-input w-full h-32 resize-none text-sm"
                  placeholder="Enter keywords..."
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500" />
                  <label className="label-uppercase">US GAAP Keywords</label>
                </div>
                <textarea
                  value={(term.keywords_gaap || []).join(', ')}
                  onChange={(e) => handleKeywordChange(activeTermIndex, 'keywords_gaap', e.target.value)}
                  className="glass-input w-full h-32 resize-none text-sm"
                  placeholder="Enter keywords..."
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500" />
                  <label className="label-uppercase">IFRS Keywords</label>
                </div>
                <textarea
                  value={(term.keywords_ifrs || []).join(', ')}
                  onChange={(e) => handleKeywordChange(activeTermIndex, 'keywords_ifrs', e.target.value)}
                  className="glass-input w-full h-32 resize-none text-sm"
                  placeholder="Enter keywords..."
                />
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[var(--border-default)]">
            <button onClick={() => setActiveTermIndex(null)} className="btn-primary">
              <Check className="w-4 h-4" />
              <span>Done Editing</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // List View
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fadeIn" onClick={onClose} />

      <div className="relative w-full max-w-6xl glass-modal overflow-hidden animate-fadeInScale max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[var(--border-default)]">
          <div>
            <h3 className="text-lg font-semibold text-primary flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-accent" />
              Financial Terminology Map
            </h3>
            <p className="text-sm text-tertiary mt-0.5">Configure semantic mapping for automatic extraction across GAAP, IFRS, and IndAS standards</p>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-4 px-6 py-4 border-b border-[var(--border-default)]">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary" />
            <input
              type="text"
              placeholder="Search by Key, Category, or Keywords..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="glass-input w-full pl-11"
            />
          </div>
          <button onClick={addNewTerm} className="btn-primary">
            <Plus className="w-4 h-4" />
            <span>Add Term</span>
          </button>
        </div>

        {/* Column Headers */}
        <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-[var(--bg-surface)] border-b border-[var(--border-default)]">
          <div className="col-span-3 label-uppercase">Key / Label</div>
          <div className="col-span-3 label-uppercase text-orange-600 dark:text-orange-400">IndAS Keywords</div>
          <div className="col-span-3 label-uppercase text-blue-600 dark:text-blue-400">US GAAP Keywords</div>
          <div className="col-span-3 label-uppercase text-purple-600 dark:text-purple-400">IFRS Keywords</div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
          {categories.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-tertiary animate-fadeIn">
              <div className="w-16 h-16 rounded-2xl bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                <Inbox className="w-8 h-8 opacity-50" />
              </div>
              <p className="text-sm font-medium text-secondary">No mappings found</p>
              <p className="text-xs mt-1">Try a different search term</p>
            </div>
          ) : (
            categories.map((category, catIndex) => {
              const isExpanded = expandedCategories.has(category);
              const items = groupedMappings[category];

              return (
                <div
                  key={category}
                  className="glass-card overflow-hidden animate-fadeIn"
                  style={{ animationDelay: `${catIndex * 50}ms` }}
                >
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--bg-hover)] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-tertiary" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-tertiary" />
                      )}
                      <span className="text-sm font-semibold text-primary">{category}</span>
                      <span className="pill pill-accent text-xs">{items.length}</span>
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="border-t border-[var(--border-default)]">
                      {items.map((m, itemIndex) => {
                        const realIndex = localMappings.findIndex(lm => lm.key === m.key);
                        const kIndas = m.keywords_indas || [];
                        const kGaap = m.keywords_gaap || [];
                        const kIfrs = m.keywords_ifrs || [];

                        return (
                          <div
                            key={m.key}
                            className="grid grid-cols-12 gap-4 px-5 py-4 border-b border-[var(--border-subtle)] last:border-b-0 group hover:bg-[var(--bg-hover)] transition-colors animate-fadeIn"
                            style={{ animationDelay: `${(catIndex * 50) + (itemIndex * 20)}ms` }}
                          >
                            {/* Key/Label */}
                            <div className="col-span-3 flex items-start justify-between">
                              <div>
                                <p className="text-sm font-medium text-primary">{m.label}</p>
                                <div className="flex items-center gap-1.5 mt-1">
                                  <Tag className="w-3 h-3 text-tertiary" />
                                  <code className="text-xs font-mono text-tertiary">{m.key}</code>
                                </div>
                              </div>
                              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                  onClick={() => setActiveTermIndex(realIndex)}
                                  className="btn-icon w-7 h-7"
                                  title="Edit"
                                >
                                  <Edit2 className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => removeTerm(realIndex)}
                                  className="btn-icon danger w-7 h-7"
                                  title="Delete"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>

                            {/* IndAS */}
                            <div className="col-span-3">
                              <div className="flex flex-wrap gap-1">
                                {kIndas.length > 0 ? (
                                  kIndas.slice(0, 5).map((k, i) => (
                                    <span key={i} className="pill pill-neutral text-[10px]">{k}</span>
                                  ))
                                ) : (
                                  <span className="text-xs text-tertiary italic">No keywords</span>
                                )}
                                {kIndas.length > 5 && (
                                  <span className="pill pill-neutral text-[10px]">+{kIndas.length - 5}</span>
                                )}
                              </div>
                            </div>

                            {/* GAAP */}
                            <div className="col-span-3">
                              <div className="flex flex-wrap gap-1">
                                {kGaap.length > 0 ? (
                                  kGaap.slice(0, 5).map((k, i) => (
                                    <span key={i} className="pill pill-neutral text-[10px]">{k}</span>
                                  ))
                                ) : (
                                  <span className="text-xs text-tertiary italic">No keywords</span>
                                )}
                                {kGaap.length > 5 && (
                                  <span className="pill pill-neutral text-[10px]">+{kGaap.length - 5}</span>
                                )}
                              </div>
                            </div>

                            {/* IFRS */}
                            <div className="col-span-3">
                              <div className="flex flex-wrap gap-1">
                                {kIfrs.length > 0 ? (
                                  kIfrs.slice(0, 5).map((k, i) => (
                                    <span key={i} className="pill pill-neutral text-[10px]">{k}</span>
                                  ))
                                ) : (
                                  <span className="text-xs text-tertiary italic">No keywords</span>
                                )}
                                {kIfrs.length > 5 && (
                                  <span className="pill pill-neutral text-[10px]">+{kIfrs.length - 5}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[var(--border-default)]">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={saveAndClose} className="btn-primary">
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseModal;