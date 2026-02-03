import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Header } from './components/Header';
import { DataTable } from './components/DataTable';
import { UploadModal } from './components/UploadModal';
import { MetricsDashboard } from './components/MetricsDashboard';
import { CapturedDataGrid } from './components/CapturedDataGrid';
import { SettingsModal } from './components/SettingsModal';
import { KnowledgeBaseModal } from './components/KnowledgeBaseModal';
import { CompanySearchModal } from './components/CompanySearchModal';
import { DocumentViewer } from './components/DocumentViewer';
import { FinancialItem, MetricGroup, AppSettings, TermMapping, CompanySearchResult, ScraperResponse } from './types';
import { LayoutDashboard, FileText, Sparkles, Loader2, Activity, MessageSquare, Search, Send, BrainCircuit, Zap, FastForward, Database, Upload, AlertCircle, X, Building2, ExternalLink } from 'lucide-react';
import { callAiProvider } from './services/geminiService';
import { convertFileSrc } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { LLMSettingsPanel } from './src/components/LLMSettingsPanel';
// import { parseFileWithPython, calculateMetricsWithPython } from './services/pythonBridge';
import { runPythonAnalysis, updateTerminologyMapping, calculateMetrics as calculateMetricsWithPython, searchCompanies, getCompanyDetails, startDbStreaming, stopDbStreaming } from './services/tauriBridge';
// We still need metric definitions but calculation is now in Python sidecar via same call
import { INPUT_METRICS, saveUserTerms, SYSTEM_TERM_IDS } from './library/metrics';
import { generateAllMetricsAsItems, generateSampleMetricsData } from './library/allMetrics';
import { useSettings } from './src/stores/useSettings';

const MOCK_DATA: FinancialItem[] = [];

function App() {
  const [activeTab, setActiveTab] = useState<'extracted' | 'metrics' | 'document' | 'captured'>('extracted');
  const [documentPage, setDocumentPage] = useState(1);
  const [highlightLocation, setHighlightLocation] = useState<{ page: number, text: string, rawLine?: string } | null>(null);

  const [documentTitle, setDocumentTitle] = useState<string | null>(null);
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisMode, setAnalysisMode] = useState<'deep-summary' | 'analyze' | 'explain'>('explain');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isKbOpen, setIsKbOpen] = useState(false);

  const [tableData, setTableData] = useState<FinancialItem[]>([]);
  const [metricsGroups, setMetricsGroups] = useState<MetricGroup[]>(generateAllMetricsAsItems());
  const [useSampleData, setUseSampleData] = useState(false);
  const [mappings, setMappings] = useState<TermMapping[]>(INPUT_METRICS);
  /* 
   * Document Context
   */
  const [rawDocumentContent, setRawDocumentContent] = useState<string>("");
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [fileType, setFileType] = useState<'pdf' | 'image' | 'text'>('text');
  const [generalQuery, setGeneralQuery] = useState("");
  const [epsType, setEpsType] = useState<'basic' | 'diluted'>('diluted');

  /* 
   * Initialize with EMPTY strings so the default fallbacks in UI ("Current Year") 
   * are irrelevant until actual data is loaded or user hasn't uploaded.
   */
  const [yearLabels, setYearLabels] = useState<{ current: string; previous: string }>({
    current: "",
    previous: ""
  });

  const [availableYears, setAvailableYears] = useState<string[]>([]);

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
  const [elapsedTime, setElapsedTime] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isProcessingDialogExpanded, setIsProcessingDialogExpanded] = useState(false);

  // Company Search State
  const [isCompanySearchOpen, setIsCompanySearchOpen] = useState(false);
  const [companySearchQuery, setCompanySearchQuery] = useState('');
  const [companySearchResults, setCompanySearchResults] = useState<CompanySearchResult[]>([]);
  const [companySearchError, setCompanySearchError] = useState<string | null>(null);
  const [isSearchingCompanies, setIsSearchingCompanies] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<CompanySearchResult | null>(null);
  const [searchExchange, setSearchExchange] = useState<'NSE' | 'BSE' | 'BOTH'>('BOTH');

  // Live elapsed time timer
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isPythonProcessing && processingProgress?.startTime) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - processingProgress.startTime) / 1000));
      }, 1000);
    } else {
      setElapsedTime(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPythonProcessing, processingProgress?.startTime]);

  useEffect(() => {
    let unlisten: (() => void) | null = null;

    // Only listen for Tauri events when running in Tauri environment
    const isTauri = typeof window !== 'undefined' && !!(window as any).__TAURI__;
    if (isTauri) {
      listen('pdf-progress', (event) => {
        const progress = event.payload as {
          currentPage: number;
          totalPages: number;
          percentage: number;
          message: string;
          partialItems?: FinancialItem[];
          partialText?: string;
        };

        setProcessingProgress(prev => {
          // Allow creating progress even if prev is null (initial event)
          const current = prev || {
            fileName: 'Processing...',
            percentage: 0,
            currentPage: 0,
            totalPages: 0,
            status: 'Initializing...',
            startTime: Date.now()
          };

          return {
            ...current,
            currentPage: progress.currentPage,
            totalPages: progress.totalPages,
            percentage: progress.percentage,
            status: progress.message
          };
        });

        // Update UI with partial data as it arrives
        if (progress.partialItems && progress.partialItems.length > 0) {
          setTableData(prev => {
            const newMap = new Map(prev.map(i => [i.id, i]));
            progress.partialItems!.forEach(item => {
              newMap.set(item.id, item);
            });
            return Array.from(newMap.values());
          });
        }

        if (progress.partialText) {
          setRawDocumentContent(prev => {
            const pageMarker = `\n--- Page ${progress.currentPage} ---\n`;
            if (prev.includes(pageMarker)) {
              // Page already added, skip
              return prev;
            }
            return prev + `\n\n\n${pageMarker}${progress.partialText}`;
          });
        }
      }).then(fn => {
        unlisten = fn;
      });
    }

    return () => {
      if (unlisten) unlisten();
    };
  }, []);

  // Listen for database streaming updates from SQLite backend
  useEffect(() => {
    let unlisten: (() => void) | null = null;

    // Only listen for Tauri events when running in Tauri environment
    const isTauri = typeof window !== 'undefined' && !!(window as any).__TAURI__;
    if (!isTauri) {
      return;
    }

    listen('db-update', (event) => {
      const dbUpdate = event.payload as {
        action: 'initial' | 'incremental';
        table: string;
        data: FinancialItem[];
      };

      console.log('[App] Database update received:', dbUpdate);

      if (dbUpdate.action === 'initial') {
        // Initial data load - replace all
        setTableData(dbUpdate.data);
      } else if (dbUpdate.action === 'incremental') {
        // Incremental update - append new items
        setTableData(prev => {
          const newMap = new Map(prev.map(i => [i.id, i]));
          dbUpdate.data.forEach(item => {
            newMap.set(item.id, item);
          });
          return Array.from(newMap.values());
        });
      }
    }).then(fn => {
      unlisten = fn;
    });

    return () => {
      if (unlisten) unlisten();
    };
  }, []);

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



  /* 
   * Initialize Global Settings
   */
  const { settings, fetchSettings, updateSettings } = useSettings();

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleUpdateSettings = async (newSettings: AppSettings) => {
    // Iterate and update changed values
    // Since our store updates key by key, we might need to be smart or update component to support key/value
    // For now, let's assume valid merging for critical keys
    // Actually simpler: let's update all keys
    for (const [key, value] of Object.entries(newSettings)) {
      if (JSON.stringify(settings[key as keyof AppSettings]) !== JSON.stringify(value)) {
        await updateSettings(key, value);
      }
    }
  };

  // Theme Effect
  // Theme Effect
  useEffect(() => {
    const applyTheme = () => {
      // console.log("Applying theme:", settings.theme); // Debug log
      const isDark =
        settings.theme === 'dark' ||
        (settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }

      // Apply Accent Color
      if (settings.accentColor) {
        document.documentElement.setAttribute('data-accent', settings.accentColor);
      } else {
        document.documentElement.setAttribute('data-accent', 'violet');
      }
    };

    applyTheme();

    // Listener for system changes if mode is system
    if (settings.theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handler = () => applyTheme();
      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    }
  }, [settings.theme, settings.accentColor]);


  // Sync with Supabase (Basic Logic)
  useEffect(() => {
    const syncToSupabase = async () => {
      if (settings?.supabaseConfig?.url && settings?.supabaseConfig?.key) {
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
  // calculateMetrics uses Python backend for accurate formula execution
  const calculateMetrics = async (data: FinancialItem[], _currentMappings?: TermMapping[]) => {
    console.log("Recalculating metrics via Python backend...");
    try {
      const results = await calculateMetricsWithPython(data);
      if (results && results.length > 0) {
        setMetricsGroups(results);
      }
    } catch (error) {
      console.error("Failed to recalculate metrics:", error);
    }
  };

  // Identify Missing Inputs dynamically - REMOVED (Sidebar legacy)

  const handleDeepSummaryAnalysis = async (pageContext: number) => {
    if (!settings.enableAI) return;

    setIsAnalyzing(true);
    setAnalysisMode('deep-summary');
    // Initialize with a loading state that shows progress
    setAiInsight("⚡ **Initializing Deep Financial Analysis...**\n\n*Phase 1/3: Analyzing Page Structure & Terms...*");

    try {
      // 1. Context Extraction (Same logic as handleAiAnalysis)
      let contentToAnalyze = rawDocumentContent;
      if (pageContext && rawDocumentContent) {
        const pageMarkerRegex = new RegExp(`--- Page\\s+${pageContext}\\s+---([\\s\\S]*?)(?=--- Page\\s+\\d+\\s+---|$)`, 'i');
        const pageMatch = rawDocumentContent.match(pageMarkerRegex);
        if (pageMatch && pageMatch[1]) {
          contentToAnalyze = `--- Page ${pageContext} ---${pageMatch[1]}`;
        }
      }

      // 2. Define Prompts for Chained Execution
      const promptPart1 = `Analyze Page ${pageContext} and provide the following sections.
      
## 📄 PAGE OVERVIEW
- **Content Type**: (e.g., Balance Sheet, P&L, Notes, Disclosures, Narrative)  
- **Main Topic/Section**: What is this page about?

## 📚 TERMS & CONCEPTS
Present ALL financial terms found on this page in a **Markdown Table**:
| Term | Definition (1-2 lines) | Criticality |
|------|------------------------|-------------|
| ... | ... | Critical / Supplementary |

**CONSTRAINT**: ONLY return these two sections. Do not add anything else.`;

      const promptPart2 = `Analyze Page ${pageContext} and provide the Data Extraction and Financial Impact sections.

## 📊 DATA EXTRACTION
Extract ALL numbers, values, and figures from this page. Present in a **clean Markdown Table**:
| Metric | Current Period | Prior Period | Change (Abs) | Change (%) | Trend |
|--------|----------------|--------------|--------------|------------|-------|
| ... | ... | ... | ... | ... | ↑ / ↓ / → |

## 📈 FINANCIAL IMPACT
For the KEY metrics on this page, explain in a **Markdown Table**:
| Metric | Is Increase Good/Bad? | Is Decrease Good/Bad? | What It Indicates |
|--------|----------------------|----------------------|-------------------|
| ... | ... | ... | ... |

**CONSTRAINT**: ONLY return these two sections. Focus on accuracy of numbers.`;

      const promptPart3 = `Analyze Page ${pageContext} using the APEX System.

You are APEX, an elite financial intelligence combining analytical rigor, patient value-seeking wisdom, contrarian zero-to-one thinking, valuation mastery, and mental-model genius.

## CORE IDENTITY
You are a sophisticated financial advisor, investor, and strategic thinker with decades of synthesized market wisdom. You speak with authority, precision, and intellectual depth while remaining accessible.

## PHILOSOPHICAL FRAMEWORK
### Fundamental Value Foundation
- Emphasize margin of safety in all investment analysis
- Distinguish clearly between INVESTMENT and SPECULATION
- Focus on intrinsic value calculations using quantitative metrics
- Advocate for disciplined, emotion-free decision making
- Reference: P/E ratios, book value, debt-to-equity, current ratios
- Treat Mr. Market as a servant, not a guide

### Competitive Advantage Lens
- Seek companies with durable competitive advantages ("moats")
- Prioritize management quality and integrity
- Think in decades, not quarters
- Prefer wonderful companies at fair prices over fair companies at wonderful prices
- Emphasize circle of competence—know what you don't know
- Focus on owner earnings and return on equity
- "Be fearful when others are greedy, greedy when others are fearful"

### Contrarian Innovation Edge
- Challenge consensus thinking—ask "What important truth do few people agree with you on?"
- Identify potential monopolies and category-defining companies
- Evaluate founders and their definite optimism
- Consider power law dynamics—few investments drive most returns
- Look for secrets: hidden truths about technology and markets
- Zero-to-one thinking over incremental improvements
- Assess competitive dynamics: Is this a "last mover" advantage?

### Valuation Precision
- "The story must match the numbers"—narrative drives valuation inputs
- Apply DCF rigor: growth rates, reinvestment, cost of capital, terminal value
- Context matters: value drivers differ by industry, lifecycle stage, geography
- Think probabilistically—value as distribution, not single point
- Distinguish between price momentum and intrinsic value creation
- Break down value: operating assets, cash, debt, options, cross-holdings
- Update valuations as story evolves; thesis flexibility is strength

### Mental Models & Inversion
- Apply mental models from multiple disciplines (psychology, physics, biology)
- Invert, always invert—"Tell me where I'll die so I won't go there"
- Avoid stupidity rather than seeking brilliance
- Consider opportunity cost in every allocation decision
- "Take a simple idea and take it seriously"
- Watch for incentive-driven behavior and cognitive biases
- Patience: "The big money is in the waiting"

## RESPONSE FRAMEWORK
### For Stock/Company Analysis:
1. **Fundamentals Screen**: Quantitative fundamentals check
2. **Intrinsic Valuation**: DCF narrative, value drivers, probabilistic range
3. **Moat Filter**: Moat assessment, management quality, long-term economics
4. **Innovation Test**: Is this creating new value? Monopoly potential? Contrarian angle?
5. **Inversion Check**: Invert the thesis—what kills this investment?
6. **Synthesis**: Unified recommendation with confidence level

## ETHICAL BOUNDARIES
- Never guarantee returns or provide false certainty
- Always note that past performance ≠ future results
- Recommend professional financial advice for personal decisions
- Disclose limitations of analysis (data recency, incomplete information)
- Distinguish between education and personalized financial advice
- Avoid pump-and-dump language or market manipulation
- Flag speculative positions clearly as such

## OUTPUT FORMAT
When analyzing investments, structure as:

📊 FUNDAMENTAL ANALYSIS
[Quantitative metrics and value assessment]

📈 VALUATION & NARRATIVE
[DCF narrative, value drivers, fair value range with assumptions]

🏰 MOAT & QUALITY
[Competitive advantages, management, long-term economics]

🚀 CONTRARIAN VIEW
[Innovation potential, secrets, paradigm shift analysis]

🔄 THESIS INVERSION
[What could go wrong? Cognitive biases at play? Kill scenarios]

⚖️ SYNTHESIS & VERDICT
[Unified assessment with confidence level: LOW/MEDIUM/HIGH/CONVICTION]

⚠️ KEY RISKS
[Primary concerns and what would change the thesis]

**CONSTRAINT**: Adopt the APEX persona: authoritative, insightful, and deep. End your response with "[ANALYSIS_COMPLETE]" to signal completion.`;


      // 3. Execute Phase 1
      const result1 = await callAiProvider(promptPart1, settings, tableData, contentToAnalyze, 'thinking');

      // Update UI with Part 1 and loading for Part 2
      const currentInsight1 = result1 + "\n\n---\n\n";
      setAiInsight(currentInsight1 + "⏳ *Waiting briefly to respect rate limits...*\n\n" + "*Phase 2/3: Extracting Data & Analyzing Impact...*");

      // SMART MANAGEMENT: Delay 2s to avoid rate limits
      await new Promise(r => setTimeout(r, 2000));

      // 4. Execute Phase 2
      const result2 = await callAiProvider(promptPart2, settings, tableData, contentToAnalyze, 'thinking');

      // Update UI with Part 1 + 2 and loading for Part 3
      const currentInsight2 = currentInsight1 + result2 + "\n\n---\n\n";
      setAiInsight(currentInsight2 + "⏳ *Waiting briefly...*\n\n" + "*Phase 3/3: Synthesizing APEX Investor Insights...*");

      // SMART MANAGEMENT: Delay 2s
      await new Promise(r => setTimeout(r, 2000));

      // 5. Execute Phase 3
      const result3 = await callAiProvider(promptPart3, settings, tableData, contentToAnalyze, 'thinking');

      // Final Result
      setAiInsight(currentInsight2 + result3);

    } catch (error) {
      console.error("Deep Summary Failed:", error);
      setAiInsight(prev => typeof prev === 'string' ? prev + "\n\n❌ **Analysis interrupted due to error.** Please try again." : "Error occurred.");
    } finally {
      setIsAnalyzing(false);
      setSelection(null);
    }
  };

  const handleContinueAnalysis = async () => {
    if (!aiInsight || typeof aiInsight !== 'string') return;

    setIsAnalyzing(true);
    const previousContent = aiInsight;
    // Take the last 500 characters as context for continuation
    const contextTail = previousContent.slice(-500);

    try {
      const continuationPrompt = `The following analysis was cut off. Please continue and complete the thought immediately, starting exactly where it left off. Do not repeat the beginning.

        PREVIOUS CONTEXT (TAIL):
        "${contextTail}"

        INSTRUCTIONS:
        1. Complete the cut-off sentence/section.
        2. Finish the remaining sections of the standard APEX analysis (Strategy, Verdict, Example) if missing.
        3. End with "[ANALYSIS_COMPLETE]".
        `;

      const continuation = await callAiProvider(continuationPrompt, settings, undefined, undefined, 'thinking');
      setAiInsight(previousContent + " " + continuation);
    } catch (error) {
      console.error("Continuation Failed:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAiAnalysis = async (promptOverride?: string, complexity: 'fast' | 'standard' | 'thinking' = 'standard', pageContext?: number) => {
    if (!settings.enableAI) return;

    setIsAnalyzing(true);
    setAnalysisMode(complexity === 'thinking' ? 'analyze' : 'explain');
    let contextPrompt = "";
    let contentToAnalyze = rawDocumentContent;
    // If pageContext is provided, extract only that page's content
    if (pageContext && rawDocumentContent) {
      // Use a more robust regex that ignores extra spaces and handles case insensitivity
      const pageMarkerRegex = new RegExp(`--- Page\\s+${pageContext}\\s+---([\\s\\S]*?)(?=--- Page\\s+\\d+\\s+---|$)`, 'i');
      const pageMatch = rawDocumentContent.match(pageMarkerRegex);
      if (pageMatch && pageMatch[1]) {
        contentToAnalyze = `--- Page ${pageContext} ---${pageMatch[1]}`;
        contextPrompt = `\n[CONTEXT: Analyzing ONLY Page ${pageContext}. The following is the extracted content from this specific page.]\n`;
        console.log(`Extracted Page ${pageContext} content, length: ${contentToAnalyze.length}`);
      } else {
        // Fallback: Check if markers use different spacing or format
        const simpleRegex = new RegExp(`Page\\s+${pageContext}\\b`, 'i');
        if (simpleRegex.test(rawDocumentContent)) {
          console.log(`Found "Page ${pageContext}" marker with simple regex, trying alternative extraction.`);
          // We might want to try to find the text between Page X and Page X+1 manually
        }
        console.log(`Could not extract Page ${pageContext} strictly, falling back to full context (truncated).`);
      }
    }

    // Local Search Strategy: Locate selection in document content
    if (selection && rawDocumentContent && !pageContext) {
      // Normalize spaces for better matching
      const searchStr = selection.text.trim();
      const content = rawDocumentContent;

      // Find all occurrences
      const occurrences: number[] = [];
      let pos = content.indexOf(searchStr);
      while (pos !== -1) {
        // Search backwards for page marker
        const preceedingText = content.substring(0, pos);
        const pageMatches = [...preceedingText.matchAll(/--- Page (\d+) ---/g)];
        if (pageMatches.length > 0) {
          const lastMatch = pageMatches[pageMatches.length - 1];
          occurrences.push(parseInt(lastMatch[1]));
        }
        pos = content.indexOf(searchStr, pos + 1);
      }

      if (occurrences.length > 0) {
        const uniquePages = Array.from(new Set(occurrences)).slice(0, 3); // Top 3 pages
        contextPrompt = `\n[CONTEXT: The user selected text "${searchStr.substring(0, 50)}..." which was found on Page(s) ${uniquePages.join(', ')} of the document. Focus your answer on these pages.]\n`;

        // CRITICAL FIX: Extract CONTENT of these specific pages to avoid truncation
        let extractedLocalContext = "";
        uniquePages.forEach(p => {
          const pageMarkerRegex = new RegExp(`--- Page\\s+${p}\\s+---([\\s\\S]*?)(?=--- Page\\s+\\d+\\s+---|$)`, 'i');
          const match = rawDocumentContent.match(pageMarkerRegex);
          if (match && match[1]) {
            extractedLocalContext += `\n--- Page ${p} ---\n${match[1]}\n`;
          }
        });

        if (extractedLocalContext.length > 100) {
          contentToAnalyze = extractedLocalContext;
          console.log(`Local Search: Extracted ${contentToAnalyze.length} chars from Pages ${uniquePages.join(', ')}`);
        }

        console.log("Local Search Context:", contextPrompt);
      } else {
        console.log("Local Search: Text not found exactly in raw content (might be OCR mismatch).");
      }
    }

    const basePrompt = promptOverride || `You are APEX, an elite financial analyst combining quantitative rigor, patient value investing, contrarian innovation thinking, valuation precision, and mental-model wisdom.

## CORE PRINCIPLES

**Fundamentals**: Margin of safety, intrinsic value, emotion-free analysis
**Valuation**: Story must match numbers, DCF rigor, probabilistic thinking
**Moat**: Durable moats, quality management, think in decades
**Edge**: Challenge consensus, find secrets, monopoly potential
**Inversion**: Mental models, invert always, avoid stupidity

## RESPONSE STYLE

- Precise, authoritative, accessible
- Ground claims in data and principles
- Acknowledge uncertainty honestly
- Use memorable analogies
- Brief unless depth requested

## QUICK ANALYSIS FORMAT

💰 VALUE: [Intrinsic value vs price assessment]
📈 STORY: [Narrative-numbers alignment check]
🏰 MOAT: [Competitive advantage strength]
🚀 EDGE: [Contrarian/innovation angle]
🔄 INVERSION: [What kills this thesis?]
📍 VERDICT: [BUY/HOLD/AVOID + confidence level]
⚠️ RISK: [Primary concern]

## RULES

- Never guarantee returns
- Distinguish investing from speculation
- Flag speculative positions clearly
- Recommend professional advice for personal decisions
- Note data/knowledge limitations

Blend philosophies based on context: stable dividend stocks lean on Value/Moat; disruptive tech leans on Edge; complex stories need Valuation precision. Every thesis gets Inversion test. True insight is knowing the right weight.

Analyze the provided data using this QUICK ANALYSIS FORMAT.`;
    const finalPrompt = basePrompt + contextPrompt;

    // Pass contentToAnalyze (either page-specific or full) to AI
    const result = await callAiProvider(finalPrompt, settings, tableData, contentToAnalyze, complexity);
    setAiInsight(result);
    setIsAnalyzing(false);
    setSelection(null);
  };


  // Floating PDF State
  const [floatingPdf, setFloatingPdf] = useState<{ isOpen: boolean, page: number } | null>(null);

  // Handle Source Click from Captured Data Grid - Updated for Floating Viewer
  const handleSourceClick = (item: FinancialItem) => {
    if (item.sourcePage) {
      // Extract number from "Page 42" or just "42"
      // Remove "Page" text just in case it's passed differently
      const text = String(item.sourcePage).replace(/page/i, '').trim();
      const match = text.match(/(\d+)/);

      if (match) {
        const pageNum = parseInt(match[1]);
        if (!isNaN(pageNum) && pageNum > 0) {
          setFloatingPdf({
            isOpen: true,
            page: pageNum
          });
          // Do NOT change activeTab - stay on current view
        }
      }
    }
  };

  const safeString = (s: any) => (s || '').toString();

  const extractTitleFromFilename = (filename: string): string => {
    // Remove extension
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, "");

    // Split by common delimiters
    const parts = nameWithoutExt.split(/[_\-\s]+/);

    // Find year (4 digits starting with 19 or 20)
    const yearPart = parts.find(p => /^(19|20)\d{2}$/.test(p));

    // Find company name parts (length > 2, not a year, not common noise words)
    const noiseWords = ['ar', 'annual', 'report', 'financial', 'statement', 'fy', 'q1', 'q2', 'q3', 'q4'];
    const companyParts = parts.filter(p => {
      const lower = p.toLowerCase();
      return p.length > 2 && !/^\d+$/.test(p) && !noiseWords.includes(lower);
    });

    let title = "";
    if (companyParts.length > 0) {
      title = companyParts.join(" ");
    } else {
      title = nameWithoutExt;
    }

    if (yearPart) {
      title += ` ${yearPart}`;
    }

    return title;
  };

  /* 
   * Handle file upload by calling Python sidecar via Tauri Bridge
   * Now accepts 'content' which is the file content (base64 encoded for binary files)
   */
  const handleUploadSuccess = async (filePath: string, type: string, fileName: string, content?: string) => {
    // Clear transient previous document state but DON'T clear tableData if we want to merge
    setRawDocumentContent('');
    // setTableData([]); // REMOVED: Keep existing data for merging
    setDocumentPage(1);
    setAiInsight(null);
    setMetricsGroups(generateAllMetricsAsItems()); // Show skeleton metrics with placeholders

    setIsPythonProcessing(true);
    setUploadError(null); // Clear previous errors
    setProcessingProgress({
      fileName: fileName,
      percentage: 0,
      currentPage: 0,
      totalPages: 0,
      status: 'Initializing...',
      startTime: Date.now()
    });

    // Detect File Type & Set Asset URL
    const ext = fileName.split('.').pop()?.toLowerCase() || '';
    if (ext === 'pdf') {
      const url = convertFileSrc(filePath);
      setFileUrl(url);
      setFileType('pdf');
    } else if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'svg'].includes(ext)) {
      const url = convertFileSrc(filePath);
      setFileUrl(url);
      setFileType('image');
    } else {
      setFileUrl(null);
      setFileType('text');
    }

    // Set initial title from filename
    const dynamicTitle = extractTitleFromFilename(fileName);
    setDocumentTitle(dynamicTitle);

    try {
      // Call Python Sidecar
      const response = await runPythonAnalysis(filePath, content, fileName);
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

        // Set document content for viewer (replace, not append)
        if (documentText.trim()) {
          setRawDocumentContent(documentText);
        } else {
          // Set placeholder
          const msg = `File loaded: ${fileName}\nPath: ${filePath}\n\n[No text content extracted - check if document is scanned/image-based]`;
          setRawDocumentContent(msg);
        }

        if (items.length > 0) {
          // Append data instead of replace, merging if possible? 
          // For now, simpler to just append all items. The UI filters by ID often, so duplicates might be an issue.
          // However, we want to allow "Add more data".
          // We will remove duplicates based on exact ID match if the value is 0? 
          // No, just append/merge. If ID exists, maybe we should update it?
          // If we upload Balance Sheet then Income Statement, IDs are different.
          // If we upload same file twice, we get dupes. 
          // Let's merge by ID: overwrite existing with new if new is non-zero?

          setTableData(prev => {
            const newMap = new Map(prev.map(i => [i.id, i]));
            items.forEach(item => {
              const existing = newMap.get(item.id);
              if (existing) {
                // Merge item, prioritizing new values but keeping existing allYears coverage
                newMap.set(item.id, {
                  ...existing,
                  ...item,
                  allYears: { ...(existing.allYears || {}), ...(item.allYears || {}) }
                });
              } else {
                newMap.set(item.id, item);
              }
            });
            return Array.from(newMap.values());
          });

          // Update available years from all items
          setAvailableYears(prev => {
            const years = new Set(prev);
            items.forEach(item => {
              if (item.allYears) {
                Object.keys(item.allYears).forEach(y => {
                  if (y && y.trim() !== '') years.add(y);
                });
              }
            });

            // Re-sort years: newest first (chronological sort if they are dates or years)
            return Array.from(years).sort((a, b) => b.localeCompare(a));
          });

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
          const meta = (extractedData as any).metadata || {};
          if (meta.currentYear || meta.previousYear) {
            setYearLabels({
              current: meta.currentYear || '',
              previous: meta.previousYear || ''
            });
          }

        } else {
          console.log("[Upload] No structured items found in response.");
        }
      } else {
        // Handle error response
        const errorMessage = response.message || response.error || 'Unknown error occurred during parsing';
        console.error("[Upload] Python Error:", errorMessage);
        setUploadError(`Failed to parse ${fileName}: ${errorMessage}`);

        // Set error message in document content
        const errorMsg = `Error processing file: ${fileName}\nPath: ${filePath}\n\nError: ${errorMessage}`;
        setRawDocumentContent(errorMsg);
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("[Upload] Failed to call Python:", error);
      setUploadError(`Failed to process ${fileName}: ${errorMessage}`);

      // Set error in document content
      const errorMsg = `Failed to process: ${fileName}\nPath: ${filePath}\n\nError: ${errorMessage}`;
      setRawDocumentContent(errorMsg);
    } finally {
      setIsPythonProcessing(false);
      setProcessingProgress(null);
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


    // ... (existing code)

    if (activeTab === 'metrics') {
      return (
        <div className="flex-1 flex flex-col overflow-hidden min-h-0">
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
            epsType={epsType}
            onEpsTypeChange={setEpsType}
          />
        </div>
      );
    }


    if (activeTab === 'captured') {
      // Merge truly missing inputs (not in tableData) into display
      const mergedData = [...tableData];
      const existingIds = new Set(mergedData.map(d => d.id));
      const currentMappings = mappings.length > 0 ? mappings : INPUT_METRICS;

      currentMappings.forEach(m => {
        if (!existingIds.has(m.key)) {
          mergedData.push({
            id: m.key,
            label: m.label,
            currentYear: 0,
            previousYear: 0,
            allYears: {},
            variation: 0,
            variationPercent: 0,
            sourcePage: '',
            statementType: 'Required Inputs',
            isMissing: true
          } as any);
        }
      });

      return (
        <CapturedDataGrid
          data={mergedData}
          onDataUpdate={setTableData}
          onSourceClick={handleSourceClick}
          availableYears={availableYears}
        />
      );
    }
    if (activeTab === 'document') {
      return (
        <div className="flex-1 flex flex-col overflow-hidden bg-gray-100 dark:bg-slate-950 min-h-0">
          <DocumentViewer
            content={rawDocumentContent}
            title="File Viewer"
            initialPage={documentPage}
            className="flex-1 border-none rounded-none w-full h-full"
            fileType={fileType}
            fileUrl={fileUrl}
            highlightLocation={highlightLocation}
            onPageChange={(p) => setDocumentPage(p)}
          />
        </div>
      );
    }

    // We can add a new tab case 'raw_pdf' if requested, but for now DocumentViewer handles text. 
    // The user asked for "Tab to view raw pdf on right of Doc Viewer"
    // I will modify the DocumentViewer usage to be split pane if a PDF is loaded.

    // Actually, let's just return the DocumentViewer as is for now, 
    // but the user specific request "themes not working" suggests I should check theme logic first.
    // And "Tab to view raw pdf".

    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-gray-100 dark:bg-slate-950">
        <DocumentViewer
          content={rawDocumentContent}
          title="Financial Document"
          initialPage={documentPage}
          className="flex-1 border-none rounded-none"
          highlightLocation={highlightLocation} // Pass highlight prop
          onPageChange={(p) => setDocumentPage(p)}
        />

        {!rawDocumentContent && !isPythonProcessing && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
            <div className="text-center max-w-lg p-8 bg-white/90 dark:bg-slate-900/90 backdrop-blur rounded-2xl shadow-xl pointer-events-auto border border-gray-200 dark:border-slate-800">
              <FileText className="w-16 h-16 mx-auto mb-4 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
                No Document Loaded
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                Upload a financial document (PDF, Excel, or text) to view its contents here.
              </p>
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-blue-500/20"
              >
                <Upload className="w-4 h-4" />
                Upload Document
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  const handleSaveMappings = async (newMappings: TermMapping[]) => {
    setMappings(newMappings);

    // Separate user-added terms (those not in system defaults) for persistence
    const userTerms = newMappings.filter(m => !SYSTEM_TERM_IDS.has(m.id));
    saveUserTerms(userTerms);

    try {
      await updateTerminologyMapping(newMappings);
    } catch (err) {
      console.error("Failed to sync mappings to backend:", err);
    }
  };

  const handleCompanySearch = async (query: string) => {
    if (query.trim().length < 2) {
      setCompanySearchResults([]);
      setCompanySearchError(null);
      return;
    }

    setIsSearchingCompanies(true);
    setCompanySearchError(null);
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error("Search request timed out (15s)")), 15000);
      });

      // improvements: use Promise.race
      const response = await Promise.race([
        searchCompanies(query, searchExchange, 10),
        timeoutPromise
      ]) as ScraperResponse<CompanySearchResult[]>;

      if (response.success) {
        // Direct array assignment based on bridge implementation
        const results = response.results || []; // Type assertion to handle any difference
        // Filter out empty/invalid results if any
        const validResults = Array.isArray(results) ? results : [];
        setCompanySearchResults(validResults);

        // Handle warnings/partial errors if present
        if (response.errors && response.errors.length > 0) {
          setCompanySearchError(response.errors.join(". "));
        }
      } else {
        setCompanySearchResults([]);
        setCompanySearchError(response.error || "Search failed. Please try again.");
      }
    } catch (error) {
      console.error('Company search error:', error);
      setCompanySearchResults([]);
      const errorMessage = error instanceof Error ? error.message : String(error);
      setCompanySearchError(
        errorMessage.includes("timed out")
          ? "Search timed out. The exchange might be slow or blocking connections."
          : "An unexpected error occurred. Please check your connection."
      );
    } finally {
      setIsSearchingCompanies(false);
    }
  };

  const handleSelectCompany = async (company: CompanySearchResult) => {
    setSelectedCompany(company);
    setIsCompanySearchOpen(false);
    setCompanySearchQuery('');

    // Fetch company details and financials
    try {
      const response = await getCompanyDetails(company.symbol, company.exchange);

      if (response.success && response.results) {
        const data = response.results;
        // Process company financial data
        if (data.items && Array.isArray(data.items)) {
          setTableData(prev => {
            const newMap = new Map(prev.map(i => [i.id, i]));
            data.items.forEach((item: FinancialItem) => {
              newMap.set(item.id, item);
            });
            return Array.from(newMap.values());
          });

          setDocumentTitle(`${company.name} (${company.exchange})`);
        }
      }
    } catch (error) {
      console.error('Error fetching company details:', error);
    }
  };

  return (
    <div className="h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-200 flex flex-col overflow-hidden">
      <Header
        onUploadClick={() => setIsUploadModalOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenKnowledgeBase={() => setIsKbOpen(true)}
        onOpenCompanySearch={() => setIsCompanySearchOpen(true)}
        title={documentTitle || undefined}
        isProcessing={isPythonProcessing}
        processingProgress={processingProgress ? {
          percentage: processingProgress.percentage,
          currentPage: processingProgress.currentPage,
          totalPages: processingProgress.totalPages,
          message: processingProgress.status
        } : undefined}
        onProcessingIndicatorClick={() => setIsProcessingDialogExpanded(!isProcessingDialogExpanded)}
      />

      {/* Tab Navigation Area */}
      <div className="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 px-6 pt-2 flex-shrink-0">
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
            File Viewer
          </button>
        </div>
      </div>

      <main className="flex-1 flex overflow-hidden relative">
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col relative overflow-hidden">

          {/* AI Insight Modal - 70% Width Popup */}
          {aiInsight && settings.enableAI && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
              <div className="w-[70%] max-h-[80vh] flex flex-col bg-white dark:bg-slate-900 border border-purple-200 dark:border-purple-800 rounded-xl shadow-2xl relative overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-slate-800 bg-purple-50/50 dark:bg-purple-900/10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
                      <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h4 className="font-bold text-lg text-gray-900 dark:text-gray-100">AI Financial Insight</h4>
                  </div>
                  <button
                    onClick={() => setAiInsight(null)}
                    className="p-1 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-full transition-colors text-gray-500"
                  >
                    ×
                  </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 custom-scrollbar text-base leading-7 text-gray-700 dark:text-gray-300">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-xl font-bold mb-3 text-gray-900 dark:text-white mt-6">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-lg font-bold mb-2 text-gray-900 dark:text-white mt-4">{children}</h3>,
                      p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc pl-6 mb-4 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="mb-1">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900 dark:text-white">{children}</strong>,
                      em: ({ children }) => <em className="italic">{children}</em>,
                      code: ({ className, children, ...props }) => {
                        const isInline = !className || !className.startsWith('language-');
                        if (isInline) {
                          return <code className="px-1.5 py-0.5 bg-gray-100 dark:bg-slate-800 text-purple-700 dark:text-purple-300 rounded text-sm font-mono" {...props}>{children}</code>;
                        }
                        return <code className="block p-4 bg-gray-100 dark:bg-slate-800 rounded-lg text-sm font-mono overflow-x-auto my-4" {...props}>{children}</code>;
                      },
                      pre: ({ children }) => <pre className="bg-gray-100 dark:bg-slate-800 rounded-lg p-4 overflow-x-auto my-4">{children}</pre>,
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-purple-500 pl-4 py-2 my-4 bg-purple-50 dark:bg-purple-900/20 italic text-gray-700 dark:text-gray-300">
                          {children}
                        </blockquote>
                      ),
                      a: ({ href, children }) => (
                        <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-0.5">
                          {children}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ),
                      table: ({ children }) => (
                        <div className="overflow-auto my-4 border border-gray-200 dark:border-slate-700 rounded-lg max-h-[60vh] custom-scrollbar">
                          <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700 border-separate border-spacing-0">{children}</table>
                        </div>
                      ),
                      thead: ({ children }) => <thead className="bg-gray-50 dark:bg-slate-800/50">{children}</thead>,
                      tbody: ({ children }) => <tbody className="bg-white dark:bg-slate-900 divide-y divide-gray-200 dark:divide-slate-700">{children}</tbody>,
                      tr: ({ children }) => <tr className="hover:bg-gray-50 dark:hover:bg-slate-800/30 transition-colors">{children}</tr>,
                      th: ({ children }) => <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider sticky top-0 bg-gray-50 dark:bg-slate-800 z-10 border-b border-gray-200 dark:border-slate-700">{children}</th>,
                      td: ({ children }) => <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">{children}</td>,
                      hr: () => <hr className="my-6 border-gray-200 dark:border-slate-700" />,
                    }}
                  >
                    {aiInsight}
                  </ReactMarkdown>
                </div>

                {/* Footer Actions */}
                <div className="px-6 py-4 border-t border-gray-100 dark:border-slate-800 bg-gray-50 dark:bg-slate-900/50 flex justify-end gap-3">
                  {!isAnalyzing && aiInsight && typeof aiInsight === 'string' && !aiInsight.includes('[ANALYSIS_COMPLETE]') && (
                    <button
                      onClick={handleContinueAnalysis}
                      className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors shadow-sm"
                    >
                      <FastForward className="w-4 h-4" />
                      Continue Generation
                    </button>
                  )}

                  <button
                    onClick={() => {
                      if (selection) {
                        // Re-run with deeper context
                        handleAiAnalysis(`Deep dive into this specifically: "${selection.text}"`, 'thinking');
                      }
                    }}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                  >
                    <BrainCircuit className="w-4 h-4" />
                    Deep Search this Topic
                  </button>
                  <button
                    onClick={() => setAiInsight(null)}
                    className="px-4 py-2 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium transition-colors"
                  >
                    Close
                  </button>
                </div>
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
                onClick={() => handleAiAnalysis(`Term: "${selection.text}"
Instructions:
1. Define simply (1-2 lines)
2. Extract any numbers from context and present as a **small markdown table** showing Year/Period and Value, with meaning in a refined column.
3. State if value change (↑/↓) is positive/negative for company
4. Give 1 realistic example with actual numbers
Keep total under 150 words.`, 'standard')}
                className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-xs font-semibold text-gray-700 dark:text-gray-200 transition-colors"
                title="Simple explanation with data analysis"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                Explain
              </button>

              <div className="w-px h-4 bg-gray-200 dark:bg-slate-700 mx-0.5"></div>

              <button
                onClick={() => handleAiAnalysis(`Term: "${selection.text}"

Provide a comprehensive financial analysis:

**Definition & Context:**
- Clear definition of this term/concept
- How it appears in financial statements (Balance Sheet/P&L/Cash Flow)
- Relevant accounting standards (Ind AS/IFRS)

**Data Analysis:**
- Extract ALL numbers related to this from the document
- **Present in a Markdown Table**: Columns for Metric, Current Period, Previous Period, Change (Abs), Change (%)
- Ensure the table is clean and easy to read

**Financial Impact:**
- Is an INCREASE in this metric generally good or bad? Why?
- Is a DECREASE good or bad? Why?
- What does this indicate about company health?

**Investor Perspective:**
- Red flags to watch for
- Positive signals this might indicate
- How this affects valuation ratios

**Example:**
- Provide a realistic example with actual numbers showing the calculation and interpretation

Be thorough and educational.`, 'thinking')}
                className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded text-xs font-semibold text-indigo-700 dark:text-indigo-300 transition-colors"
                title="Deep analysis with full data interpretation"
              >
                <BrainCircuit className="w-3.5 h-3.5" />
                Analyze
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

          {/* Upload Error Banner */}
          {uploadError && !isPythonProcessing && (
            <div className="m-6 mb-0 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-900 dark:text-red-100 text-sm relative animate-fadeIn shadow-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h4 className="font-bold mb-1">Upload Error</h4>
                  <div className="leading-relaxed opacity-90 whitespace-pre-wrap">
                    {uploadError}
                  </div>
                </div>
                <button
                  onClick={() => setUploadError(null)}
                  className="absolute top-3 right-3 text-red-400 hover:text-red-700 dark:hover:text-red-200"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Collapsible Processing Dialog */}
          {isPythonProcessing && isProcessingDialogExpanded && (
            <div
              className="fixed inset-0 z-40 flex items-center justify-center"
              onClick={() => setIsProcessingDialogExpanded(false)}
            >
              <div
                className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-700 w-96 animate-fadeInScale"
                onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">Processing Document</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {processingProgress?.fileName || 'Analyzing...'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setIsProcessingDialogExpanded(false)}
                    className="btn-icon text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  >
                    <X className="w-5 h-5" />
                  </button>
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

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-gray-50 dark:bg-slate-900/50 rounded-xl p-3 text-center">
                    <p className="text-xl font-bold text-gray-900 dark:text-white font-mono">
                      {processingProgress?.currentPage || 0}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Pages Done</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-slate-900/50 rounded-xl p-3 text-center">
                    <p className="text-xl font-bold text-gray-900 dark:text-white font-mono">
                      {processingProgress?.totalPages || '—'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Total Pages</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-slate-900/50 rounded-xl p-3 text-center">
                    <p className="text-xl font-bold text-blue-600 dark:text-blue-400 font-mono">
                      {elapsedTime > 0 ? `${elapsedTime}s` : '—'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Elapsed</p>
                  </div>
                </div>

                {/* Info */}
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start gap-2 text-sm text-blue-700 dark:text-blue-300">
                    <Zap className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <p className="leading-relaxed">
                      Processing in background. Click outside or the <span className="font-semibold">×</span> button to minimize to top bar.
                    </p>
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
      </main>

      {/* General AI Chat / Summary Bar - Moved outside main relative flow to be fixed viewport */}
      {settings.enableAI && (
        <div className="fixed bottom-6 z-20 transition-all duration-300 ease-in-out" style={{ left: '24px', right: '24px' }}>
          <div className="max-w-3xl mx-auto flex items-center gap-2">
            {/* Generate Summary Button */}
            <button
              onClick={() => handleDeepSummaryAnalysis(documentPage)}
              disabled={isAnalyzing}
              className="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-70 font-medium text-sm"
              title="Generate deep analysis of the current page with Gemini Thinking Mode"
            >
              {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <BrainCircuit className="w-4 h-4" />}
              {isAnalyzing ? 'Thinking...' : 'Deep Summary'}
            </button>



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
                disabled={isAnalyzing}
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

      {/* Floating Document Viewer Overlay */}
      {floatingPdf && floatingPdf.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-end animate-fadeIn">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/20 backdrop-blur-sm"
            onClick={() => setFloatingPdf(null)}
          />

          {/* Floating Panel (Right Side) */}
          <div className="relative w-[50vw] h-[95vh] mr-4 bg-[var(--bg-elevated)] border border-[var(--border-default)] rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-slideLeft">

            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-default)] bg-[var(--bg-surface)]">
              <div className="flex items-center gap-3">
                <div className="bg-red-500/10 p-1.5 rounded-lg text-red-500">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-primary text-sm">Source Document</h3>
                  <p className="text-xs text-secondary">
                    Viewing Page {floatingPdf.page}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    // Open full view
                    setDocumentPage(floatingPdf.page);
                    setActiveTab('document');
                    setFloatingPdf(null);
                  }}
                  className="p-2 text-tertiary hover:text-primary transition-colors rounded-lg hover:bg-[var(--bg-hover)]"
                  title="Open in Full Tab"
                >
                  <ExternalLink className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setFloatingPdf(null)}
                  className="p-2 text-tertiary hover:text-error transition-colors rounded-lg hover:bg-[var(--bg-hover)]"
                  title="Close"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Viewer Content */}
            <div className="flex-1 relative overflow-hidden">
              <DocumentViewer
                content={rawDocumentContent}
                fileUrl={fileUrl}
                fileType={fileType}
                initialPage={floatingPdf.page}
                onPageChange={(p) => setFloatingPdf(prev => prev ? { ...prev, page: p } : null)}
                highlightLocation={highlightLocation}
              />
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
        onUpdateSettings={handleUpdateSettings}
      />
      <KnowledgeBaseModal
        isOpen={isKbOpen}
        onClose={() => setIsKbOpen(false)}
        mappings={mappings}
        onSave={handleSaveMappings}
      />
      <CompanySearchModal
        isOpen={isCompanySearchOpen}
        onClose={() => setIsCompanySearchOpen(false)}
        onSearch={handleCompanySearch}
        onSelectCompany={handleSelectCompany}
        isSearching={isSearchingCompanies}
        results={companySearchResults}
        exchange={searchExchange}
        onExchangeChange={setSearchExchange}
        error={companySearchError}
      />
    </div>
  );
};

export default App;