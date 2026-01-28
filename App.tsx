import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DataTable } from './components/DataTable';
import { Sidebar } from './components/Sidebar';
import { UploadModal } from './components/UploadModal';
import { MetricsDashboard } from './components/MetricsDashboard';
import { CapturedDataGrid } from './components/CapturedDataGrid';
import { SettingsModal } from './components/SettingsModal';
import { KnowledgeBaseModal } from './components/KnowledgeBaseModal';
import { FinancialItem, InputStatus, MissingInputItem, MetricGroup, AppSettings, TermMapping } from './types';
import { LayoutDashboard, FileText, Sparkles, Loader2, Activity, MessageSquare, Search, Send, BrainCircuit, Zap, Database, Upload } from 'lucide-react';
import { callAiProvider } from './services/geminiService';
// import { parseFileWithPython, calculateMetricsWithPython } from './services/pythonBridge';
import { runPythonAnalysis, updateTerminologyMapping } from './services/tauriBridge';
// We still need metric definitions but calculation is now in Python sidecar via same call
import { INPUT_METRICS } from './library/metrics';
import { generateAllMetricsAsItems, generateSampleMetricsData } from './library/allMetrics';

const MOCK_DATA: FinancialItem[] = [];

const MOCK_MISSING_INPUTS: MissingInputItem[] = [];

function App() {
  const [activeTab, setActiveTab] = useState<'extracted' | 'metrics' | 'document' | 'captured'>('extracted');
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isKbOpen, setIsKbOpen] = useState(false);

  const [tableData, setTableData] = useState<FinancialItem[]>([]);
  const [metricsGroups, setMetricsGroups] = useState<MetricGroup[]>(generateAllMetricsAsItems());
  const [useSampleData, setUseSampleData] = useState(false);
  const [mappings, setMappings] = useState<TermMapping[]>(INPUT_METRICS);
  const [missingInputs, setMissingInputs] = useState<MissingInputItem[]>([]);

  // Document Context
  const [rawDocumentContent, setRawDocumentContent] = useState<string>("");
  const [generalQuery, setGeneralQuery] = useState("");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  /* 
   * Initialize with EMPTY strings so the default fallbacks in UI ("Current Year") 
   * are irrelevant until actual data is loaded or user hasn't uploaded.
   * However, standard behavior is to default to "Current Year" if nothing is found.
   */
  const [yearLabels, setYearLabels] = useState<{ current: string; previous: string }>({
    current: "", // Start empty to avoid "defaults" showing up when they shouldn't
    previous: ""
  });

  // Set default pinned metrics that will appear on the Summary Page
  // Set default pinned metrics that will appear on the Summary Page
  const [pinnedMetrics, setPinnedMetrics] = useState<Set<string>>(new Set([
    'revenue', 'net_income', 'ebitda', 'operating_cash_flow', 'total_assets', 'total_equity', // Key Raw Data
    'calc_gross_margin', 'calc_operating_margin', 'calc_net_profit_margin',
    'calc_revenue_growth', 'calc_current_ratio', 'calc_debt_to_equity'
  ]));

  const [isPythonProcessing, setIsPythonProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState<{
    fileName: string;
    percentage: number;
    currentPage: number;
    totalPages: number;
    status: string;
    startTime: number;
  } | null>(null);

  // Toggle sample data
  const toggleSampleData = () => {
    if (useSampleData) {
      setMetricsGroups(generateAllMetricsAsItems());
      setUseSampleData(false);
    } else {
      setMetricsGroups(generateSampleMetricsData());
      setUseSampleData(true);
    }
  };

  // Contextual Selection AI
  const [selection, setSelection] = useState<{ text: string, x: number, y: number } | null>(null);

  const [settings, setSettings] = useState<AppSettings>({
    theme: 'light',
    enableAI: true,
    aiProvider: 'gemini',
    apiKeys: { gemini: '', groq: '', openai: '', openrouter: '', opencode: '' },
    modelName: '',
    supabaseConfig: { url: '', key: '' }
  });

  // Theme Effect
  useEffect(() => {
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [settings.theme]);

  // Sync with Supabase (Basic Logic)
  useEffect(() => {
    const syncToSupabase = async () => {
      if (settings.supabaseConfig.url && settings.supabaseConfig.key) {
        try {
          console.log("Attempting to sync settings and mappings to Supabase...", settings.supabaseConfig.url);
        } catch (e) {
          console.error("Supabase sync failed:", e);
        }
      }
    };

    // Debounce sync
    const timeout = setTimeout(syncToSupabase, 2000);
    return () => clearTimeout(timeout);
  }, [settings, mappings]);

  // Selection Listener
  useEffect(() => {
    const handleSelection = (e: MouseEvent) => {
      // Don't modify selection state if clicking inside the popup
      if ((e.target as HTMLElement).closest('.selection-popup')) {
        return;
      }

      const sel = window.getSelection();
      // Ensure we have a valid selection and aren't currently waiting for AI
      if (sel && sel.toString().trim().length > 0 && !isAnalyzing) {
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // For fixed positioning, we use client coordinates directly (viewport relative).
        // This ensures the popup appears exactly where the user is looking, regardless of scroll.
        if (rect.width > 0 && rect.height > 0) {
          setSelection({
            text: sel.toString(),
            x: rect.left + (rect.width / 2),
            y: rect.top - 10 // Position 10px above the highlight
          });
        }
      } else {
        // Clear selection if user clicks elsewhere
        setSelection(null);
      }
    };

    // Use mouseup to detect end of selection
    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, [isAnalyzing]);

  // Clear selection on scroll to prevent floating popup detached from text
  useEffect(() => {
    const clear = () => setSelection(null);
    window.addEventListener('scroll', clear);
    return () => window.removeEventListener('scroll', clear);
  }, []);

  // Recalculate when Mappings Change
  useEffect(() => {
    if (tableData.length > 0) {
      calculateMetrics(tableData, mappings);
    }
  }, [mappings]);

  // calculateMetrics moved to Python
  const calculateMetrics = async (data: FinancialItem[], currentMappings: TermMapping[]) => {
    // If we need to re-calculate on mapping change, we need a new route in `api.py`
    // For now, we stub this or alert user.
    console.log("Re-calculating metrics... (This requires Python round-trip now)");
    // TODO: Implement 'recalculate' command in api.py receiving data + mappings
  };

  // Identify Missing Inputs dynamically
  useEffect(() => {
    // If using sample data and it hasn't been modified, keep mock missing inputs
    if (useSampleData && tableData === MOCK_DATA) {
      setMissingInputs(MOCK_MISSING_INPUTS);
      return;
    }

    const currentMappings = mappings.length > 0 ? mappings : INPUT_METRICS;
    const foundIds = new Set(tableData.map(item => item.id));

    // Filter out items that are present in the table data
    // We only want items that are completely MISSING or explicitly flagged as suspicious
    const dynamicMissing: MissingInputItem[] = currentMappings
      .filter(m => !foundIds.has(m.key))
      .map(m => ({
        id: m.key,
        label: m.label,
        value: '',
        status: InputStatus.NOT_FOUND,
        confidence: 0
      }));

    // Also check for items present but with 0 values (often extraction failures)
    // or items with warnings
    tableData.forEach(item => {
      if (item.hasWarning) {
        dynamicMissing.unshift({
          id: item.id,
          label: item.label,
          value: item.currentYear?.toString() || '',
          status: InputStatus.LOW_CONFIDENCE,
          confidence: 20
        });
      } else if (item.currentYear === 0 && !item.label.toLowerCase().includes('dividend')) {
        // Zero values for non-dividend items are suspicious
        dynamicMissing.push({
          id: item.id,
          label: item.label,
          value: '0',
          status: InputStatus.LOW_CONFIDENCE,
          confidence: 50
        });
      }
    });

    // Sort: Low Confidence first, then Not Found
    dynamicMissing.sort((a, b) => {
      if (a.status === b.status) return 0;
      return a.status === InputStatus.LOW_CONFIDENCE ? -1 : 1;
    });

    setMissingInputs(dynamicMissing);
  }, [tableData, mappings, useSampleData]);

  const handleAiAnalysis = async (promptOverride?: string, complexity: 'fast' | 'standard' | 'thinking' = 'standard') => {
    if (!settings.enableAI) return;

    setIsAnalyzing(true);
    const prompt = promptOverride || "Analyze the most significant growth areas and concerns in this financial data.";
    // Pass rawDocumentContent to AI for full context awareness
    const result = await callAiProvider(prompt, settings, tableData, rawDocumentContent, complexity);
    setAiInsight(result);
    setIsAnalyzing(false);
    setSelection(null);
  };

  // Handler for Sidebar AI Assist - Finding missing inputs
  const handleMissingInputAssist = async (label: string): Promise<string> => {
    if (!settings.enableAI) return "AI features disabled.";
    if (!rawDocumentContent) return "No document content available. Please upload a file.";

    const prompt = `
      The user is looking for the value of "${label}" in the financial document.
      Please locate this value or the section where it should be found.
      Quote the specific text or table row from the document that helps locate it.
      Keep it short (under 50 words).
    `;
    // Use 'fast' complexity for low latency responsiveness
    return await callAiProvider(prompt, settings, [], rawDocumentContent, 'fast');
  };

  /* 
   * Handle file upload by calling Python sidecar via Tauri Bridge
   * Now expects 'content' to be the FILE PATH
   */
  const handleUploadSuccess = async (filePath: string, type: string, fileName: string) => {
    setIsPythonProcessing(true);
    setProcessingProgress({
      fileName: fileName,
      percentage: 0,
      currentPage: 0,
      totalPages: 0,
      status: 'Initializing...',
      startTime: Date.now()
    });
    console.log(`[Upload] Processing file via Tauri: ${filePath}`);

    try {
      // Call Python Sidecar
      const response = await runPythonAnalysis(filePath);
      console.log("[Upload] Python response:", response);

      if (response.status === "success") {
        const extractedData = response.extractedData || {};

        // Handle different response structures
        // API returns: { data: { items: [], text: "" } } or { extractedData: { items: [], text: "" } }
        const data = (extractedData as any).data || extractedData;

        // Extract items array - check multiple possible paths
        let items: FinancialItem[] = [];
        if (Array.isArray(data)) {
          items = data;
        } else if (Array.isArray(data.items)) {
          items = data.items;
        } else if (Array.isArray((extractedData as any).items)) {
          items = (extractedData as any).items;
        }

        // Extract document text content for viewer
        let documentText = '';
        if (typeof data.text === 'string') {
          documentText = data.text;
        } else if (data.pages && Array.isArray(data.pages)) {
          // Reconstruct text from pages
          documentText = data.pages.map((page: any, idx: number) =>
            `--- Page ${page.pageNumber || idx + 1} ---\n${page.content || ''}`
          ).join('\n\n');
        } else if (typeof (extractedData as any).text === 'string') {
          documentText = (extractedData as any).text;
        }

        // Set document content for viewer (fallback to file path if no text extracted)
        if (documentText.trim()) {
          setRawDocumentContent(documentText);
        } else {
          setRawDocumentContent(`File loaded: ${fileName}\nPath: ${filePath}\n\n[No text content extracted - check if document is scanned/image-based]`);
        }

        if (items.length > 0) {
          setTableData(items);
          setAiInsight(null);

          // Handle metrics if returned
          if (response.metrics) {
            try {
              const parsedMetrics = typeof response.metrics === 'string' ? JSON.parse(response.metrics) : response.metrics;
              if (Array.isArray(parsedMetrics) && parsedMetrics.length > 0) {
                setMetricsGroups(parsedMetrics);
              }
            } catch (e) {
              console.error("Error parsing metrics JSON", e);
            }
          }

          // Check for year labels in metadata
          if (response.metadata) {
            const meta = response.metadata as any;
            if (meta.currentYear || meta.previousYear) {
              setYearLabels({
                current: meta.currentYear || '',
                previous: meta.previousYear || ''
              });
            }
          }

        } else {
          console.log("[Upload] No structured items found in response.");
          // Still show document content even if no structured data
        }
      } else {
        console.error("Python Error:", response.message);
        setRawDocumentContent(`Error processing file: ${response.message || 'Unknown error'}`);
        alert(`Error processing file: ${response.message}`);
      }

    } catch (error) {
      console.error("[Upload] Failed to call Python:", error);
      setRawDocumentContent(`Failed to process: ${filePath}\n\nError: ${error}`);
      alert("Failed to process file with Python engine.");
    } finally {
      setIsPythonProcessing(false);
      setProcessingProgress(null);
    }
  };

  const handleInputConfirm = (confirmedInputs: MissingInputItem[]) => {
    // 1. Filter out items that are still empty or skipped
    const validInputs = confirmedInputs.filter(item =>
      item.value && item.value.trim() !== '' && item.status !== InputStatus.SKIPPED
    );

    if (validInputs.length === 0) {
      alert("No new inputs provided to save.");
      return;
    }

    // 2. Merge into Table Data
    // We need to either UPDATE existing items (if recognized but zero) 
    // or ADD new items (if previously missing)
    const newTableData = [...tableData];

    let updatesCount = 0;

    validInputs.forEach(input => {
      const existingIndex = newTableData.findIndex(row => row.id === input.id);

      const cleanValue = parseFloat(input.value.replace(/,/g, '').replace(/[^0-9.-]/g, ''));

      if (isNaN(cleanValue)) {
        console.warn(`Invalid number value for ${input.label}: ${input.value}`);
        return;
      }

      const targetYear = input.targetYear || 'current';

      if (existingIndex >= 0) {
        // Update existing item
        const item = newTableData[existingIndex];
        const updatedItem = { ...item };

        if (targetYear === 'previous') {
          updatedItem.previousYear = cleanValue;
        } else {
          updatedItem.currentYear = cleanValue;
        }

        // Recalculate variation
        updatedItem.variation = updatedItem.currentYear - updatedItem.previousYear;
        updatedItem.variationPercent = updatedItem.previousYear !== 0
          ? (updatedItem.variation / updatedItem.previousYear * 100)
          : 0;

        updatedItem.hasWarning = false; // Clear warning
        newTableData[existingIndex] = updatedItem;

      } else {
        // Add new item
        const currentYear = targetYear === 'current' ? cleanValue : 0;
        const previousYear = targetYear === 'previous' ? cleanValue : 0;
        const variation = currentYear - previousYear;
        const variationPercent = previousYear !== 0 ? (variation / previousYear * 100) : 0;

        newTableData.push({
          id: input.id,
          label: input.label,
          currentYear,
          previousYear,
          variation,
          variationPercent,
          sourcePage: 'Manual Entry',
          isAutoCalc: false
        });
      }
      updatesCount++;
    });

    if (updatesCount > 0) {
      setTableData(newTableData);

      // 3. Trigger Metric Recalculation
      calculateMetrics(newTableData, mappings);
      alert(`Successfully updated ${updatesCount} metric(s). Recalculating analysis...`);
    }
  };

  const toggleMetricPin = (id: string) => {
    const newPinned = new Set(pinnedMetrics);
    if (newPinned.has(id)) {
      newPinned.delete(id);
    } else {
      newPinned.add(id);
    }
    setPinnedMetrics(newPinned);
  };

  // Construct the Summary Data based on Pinned items + Raw Data + Sorting by TOC
  const getSummaryData = (): FinancialItem[] => {
    // 1. Start with Pinned Raw Data only
    const summaryList: FinancialItem[] = tableData.filter(item => pinnedMetrics.has(item.id));

    // 2. Append Pinned Metrics (Sorted by TOC order)
    if (metricsGroups.length > 0) {
      metricsGroups.forEach(group => {
        group.items.forEach(item => {
          if (pinnedMetrics.has(item.id)) {
            // Check if it already exists (unlikely for calculated vs raw, but good safety)
            if (!summaryList.find(i => i.id === item.id)) {
              summaryList.push(item);
            }
          }
        });
      });
    }
    return summaryList;
  };

  const renderContent = () => {
    if (activeTab === 'extracted') {
      return (
        <DataTable
          data={getSummaryData()}
          onUnpin={toggleMetricPin}
        />
      );
    }
    if (activeTab === 'metrics') {
      return (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Sample Data Toggle */}
          <div className="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700 px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Test Mode:</span>
              <button
                onClick={toggleSampleData}
                className={`px-3 py-1.5 text-xs font-semibold rounded-full transition-all ${useSampleData
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-gray-100 text-gray-500 dark:bg-slate-700 dark:text-gray-400'
                  }`}
              >
                {useSampleData ? '✓ Sample Data Active' : 'Sample Data Off'}
              </button>
            </div>
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {useSampleData ? 'Showing sample values for testing' : 'Click to load sample data'}
            </span>
          </div>
          <MetricsDashboard
            groups={metricsGroups}
            pinnedIds={pinnedMetrics}
            onTogglePin={toggleMetricPin}
          />
        </div>
      );
    }
    if (activeTab === 'captured') {
      return (
        <CapturedDataGrid
          data={tableData}
        />
      );
    }
    return (
      <div className="flex-1 flex flex-col bg-gray-100 dark:bg-slate-950 min-h-[500px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-lg">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {rawDocumentContent ? "Document Content Loaded" : "No Document Loaded"}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              {rawDocumentContent
                ? "The text content of your document is in memory and ready for AI analysis."
                : "Upload a financial document (PDF, Excel, or text) to view its contents here."}
            </p>
            {!rawDocumentContent && (
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm transition-colors"
              >
                <Upload className="w-4 h-4" />
                Upload Document
              </button>
            )}
            {rawDocumentContent && (
              <div className="text-left bg-white dark:bg-slate-900 p-4 rounded-lg border border-gray-200 dark:border-slate-800 h-96 overflow-y-auto text-xs font-mono text-gray-600 dark:text-gray-400 shadow-inner">
                {rawDocumentContent.split(/--- Page (\d+) ---/).map((part, index, array) => {
                  if (index === 0) return <span key={index}>{part}</span>;
                  if (index % 2 !== 0) return null;
                  const pageNum = array[index - 1];
                  return (
                    <div key={index} id={`page-${pageNum}`} className="mb-6 border-b border-gray-100 dark:border-slate-800 pb-4">
                      <div className="font-bold text-blue-600 dark:text-blue-400 mb-2 sticky top-0 bg-white dark:bg-slate-900 py-1">
                        --- Page {pageNum} ---
                      </div>
                      <div className="whitespace-pre-wrap">{part}</div>
                    </div>
                  );
                })}
                {!rawDocumentContent.includes("--- Page") && (
                  <div className="whitespace-pre-wrap">{rawDocumentContent}</div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const handleSaveMappings = async (newMappings: TermMapping[]) => {
    setMappings(newMappings);
    try {
      await updateTerminologyMapping(newMappings);
    } catch (err) {
      console.error("Failed to sync mappings to backend:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-200">
      <Header
        onUploadClick={() => setIsUploadModalOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenKnowledgeBase={() => setIsKbOpen(true)}
      />

      {/* Tab Navigation Area */}
      <div className="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 px-6 pt-2">
        <div className="flex items-center gap-8">
          <button
            onClick={() => setActiveTab('extracted')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'extracted' ? 'text-blue-700 dark:text-blue-400 border-blue-700 dark:border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-200'}`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Company Financial Summary
          </button>
          <button
            onClick={() => setActiveTab('metrics')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'metrics' ? 'text-blue-700 dark:text-blue-400 border-blue-700 dark:border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-200'}`}
          >
            <Activity className="w-4 h-4" />
            All Metrics (Analysis)
          </button>
          <button
            onClick={() => setActiveTab('captured')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'captured' ? 'text-blue-700 dark:text-blue-400 border-blue-700 dark:border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-200'}`}
          >
            <Database className="w-4 h-4" />
            Captured Data
          </button>
          <button
            onClick={() => setActiveTab('document')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'document' ? 'text-blue-700 dark:text-blue-400 border-blue-700 dark:border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-200'}`}
          >
            <FileText className="w-4 h-4" />
            Document Viewer
          </button>
        </div>
      </div>

      <main className="flex flex-1 overflow-hidden" style={{ maxHeight: 'calc(100vh - 130px)' }}>
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col relative pb-20 overflow-auto">

          {/* AI Insight Overlay */}
          {aiInsight && settings.enableAI && (
            <div className="m-6 mb-0 p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg text-purple-900 dark:text-purple-100 text-sm relative animate-fadeIn shadow-lg">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h4 className="font-bold mb-1">AI Financial Insight</h4>
                  <div className="leading-relaxed opacity-90 whitespace-pre-wrap">
                    {aiInsight.split(/(\[Page \d+\])/g).map((part, i) => {
                      const match = part.match(/\[Page (\d+)\]/);
                      if (match) {
                        const pageNum = match[1];
                        return (
                          <button
                            key={i}
                            onClick={() => {
                              setActiveTab('document');
                              setTimeout(() => {
                                const el = document.getElementById(`page-${pageNum}`);
                                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                              }, 100);
                            }}
                            className="inline-flex items-center gap-0.5 px-1.5 py-0.5 mx-0.5 bg-purple-100 dark:bg-purple-800/50 text-purple-700 dark:text-purple-300 rounded text-xs font-bold hover:bg-purple-200 dark:hover:bg-purple-700 transition-colors cursor-pointer"
                            title={`Jump to Page ${pageNum}`}
                          >
                            {part}
                          </button>
                        );
                      }
                      return part;
                    })}
                  </div>
                </div>
                <button
                  onClick={() => setAiInsight(null)}
                  className="absolute top-3 right-3 text-purple-400 hover:text-purple-700 dark:hover:text-purple-200"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Contextual Selection Popup */}
          {selection && !isAnalyzing && settings.enableAI && (
            <div
              className="selection-popup fixed z-50 transform -translate-x-1/2 -translate-y-full mb-2 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 text-gray-800 dark:text-white p-1.5 rounded-lg shadow-xl flex items-center gap-1 animate-fadeIn ring-1 ring-black/5"
              style={{ left: selection.x, top: selection.y }}
              onMouseDown={(e) => e.stopPropagation()} // Prevent clearing selection when clicking the popup
            >
              <button
                onClick={() => handleAiAnalysis(`Explain this term clearly and simply for a non-expert: "${selection.text}"`, 'standard')}
                className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-xs font-semibold text-gray-700 dark:text-gray-200 transition-colors"
                title="Simple explanation using standard model"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                Explain (Simple)
              </button>

              <div className="w-px h-4 bg-gray-200 dark:bg-slate-700 mx-0.5"></div>

              <button
                onClick={() => handleAiAnalysis(`Provide a deep, comprehensive analysis and implications of this term: "${selection.text}"`, 'thinking')}
                className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded text-xs font-semibold text-indigo-700 dark:text-indigo-300 transition-colors"
                title="Deep analysis using Gemini Thinking mode"
              >
                <BrainCircuit className="w-3.5 h-3.5" />
                Deep Search
              </button>

              <div className="w-px h-4 bg-gray-200 dark:bg-slate-700 mx-0.5"></div>

              <button
                onClick={() => handleAiAnalysis(`Find related values or instances of this term in the document: "${selection.text}"`, 'fast')}
                className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded text-xs font-semibold text-blue-600 dark:text-blue-400 transition-colors"
                title="Fast lookup in document"
              >
                <Zap className="w-3.5 h-3.5" />
                Locate
              </button>

              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-white dark:bg-slate-800 border-b border-r border-gray-200 dark:border-slate-700"></div>
            </div>
          )}

          {/* Python Processing Loading State - Enhanced */}
          {isPythonProcessing && (
            <div className="absolute inset-0 bg-white/80 dark:bg-slate-900/80 z-10 flex items-center justify-center backdrop-blur-sm">
              <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-700 w-full max-w-md mx-4">
                {/* Header */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                    <Loader2 className="w-6 h-6 text-white animate-spin" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Processing Document</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-[280px]">
                      {processingProgress?.fileName || 'Analyzing...'}
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600 dark:text-gray-300">
                      {processingProgress?.status || 'Extracting data...'}
                    </span>
                    <span className="font-mono text-blue-600 dark:text-blue-400">
                      {processingProgress?.percentage || 0}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${processingProgress?.percentage || 5}%` }}
                    />
                  </div>
                </div>

                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-slate-900/50 rounded-xl">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900 dark:text-white font-mono">
                      {processingProgress?.currentPage || 0}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Pages Done</p>
                  </div>
                  <div className="text-center border-x border-gray-200 dark:border-slate-700">
                    <p className="text-2xl font-bold text-gray-900 dark:text-white font-mono">
                      {processingProgress?.totalPages || '—'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Total Pages</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 font-mono">
                      {processingProgress?.startTime
                        ? `${Math.floor((Date.now() - processingProgress.startTime) / 1000)}s`
                        : '—'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Elapsed</p>
                  </div>
                </div>

                {/* Animated Dots */}
                <div className="flex justify-center gap-1 mt-4">
                  <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          {renderContent()}

        </div>

        {/* Right Sidebar */}
        <Sidebar
          items={missingInputs}
          onConfirm={handleInputConfirm}
          onAiAssist={handleMissingInputAssist}
          yearLabels={yearLabels}
          isCollapsed={isSidebarCollapsed}
          onToggle={setIsSidebarCollapsed}
        />
      </main>

      {/* General AI Chat / Summary Bar - Moved outside main relative flow to be fixed viewport */}
      {!isPythonProcessing && settings.enableAI && (
        <div className="fixed bottom-6 z-20 transition-all duration-300 ease-in-out" style={{ left: '24px', right: isSidebarCollapsed ? '84px' : '424px' }}>
          <div className="max-w-3xl mx-auto flex items-center gap-2">
            {/* Generate Summary Button */}
            {!aiInsight && (
              <button
                onClick={() => handleAiAnalysis(undefined, 'thinking')}
                disabled={isAnalyzing}
                className="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-70 font-medium text-sm"
                title="Generate deep analysis with Gemini 3 Pro Thinking Mode"
              >
                {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <BrainCircuit className="w-4 h-4" />}
                {isAnalyzing ? 'Thinking...' : 'Deep Summary'}
              </button>
            )}

            {/* General Document Q&A Input */}
            <div className="flex-1 relative shadow-lg rounded-lg">
              <input
                type="text"
                value={generalQuery}
                onChange={(e) => setGeneralQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && generalQuery.trim()) {
                    handleAiAnalysis(generalQuery, 'standard');
                    setGeneralQuery("");
                  }
                }}
                placeholder={rawDocumentContent ? "Ask a question about the uploaded document..." : "Upload a document to ask questions..."}
                disabled={!rawDocumentContent || isAnalyzing}
                className="w-full pl-4 pr-12 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none text-sm transition-all disabled:bg-gray-100 dark:disabled:bg-slate-900 disabled:opacity-70"
              />
              <button
                onClick={() => {
                  if (generalQuery.trim()) {
                    handleAiAnalysis(generalQuery, 'standard');
                    setGeneralQuery("");
                  }
                }}
                disabled={!rawDocumentContent || isAnalyzing || !generalQuery.trim()}
                className="absolute right-2 top-2 p-1.5 text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-slate-700 rounded-md transition-colors disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onUpdateSettings={setSettings}
      />
      <KnowledgeBaseModal
        isOpen={isKbOpen}
        onClose={() => setIsKbOpen(false)}
        mappings={mappings}
        onSave={handleSaveMappings}
      />
    </div>
  );
}

export default App;