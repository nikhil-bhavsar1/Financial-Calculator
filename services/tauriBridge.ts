import { Command, Child } from '@tauri-apps/plugin-shell';
import { TermMapping } from '../types';

// ============================================================================
// TYPES
// ============================================================================

interface ExtractedData {
    text?: string;
    pages?: PageData[];
    tables?: TableData[];
    sections?: SectionData[];
    financialData?: FinancialMetrics;
}

interface PageData {
    pageNumber: number;
    content: string;
    tables?: TableData[];
}

interface TableData {
    pageNumber: number;
    headers: string[];
    rows: string[][];
    tableType?: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'notes' | 'other';
}

interface SectionData {
    title: string;
    startPage: number;
    endPage: number;
    content: string;
}

interface FinancialMetrics {
    totalAssets?: number;
    totalLiabilities?: number;
    revenue?: number;
    netIncome?: number;
    currency?: string;
}

interface ProcessingMetrics {
    pagesProcessed: number;
    totalPages: number;
    processingTimeMs: number;
    fileSizeBytes?: number;
    tablesFound: number;
    sectionsFound: number;
}

interface DocumentMetadata {
    fileName: string;
    fileType: string;
    creationDate?: string;
    author?: string;
    title?: string;
    pageCount: number;
}

interface PythonResponse {
    status: 'success' | 'error' | 'progress';
    extractedData?: ExtractedData;
    metrics?: ProcessingMetrics;
    metadata?: DocumentMetadata;
    message?: string;
    // Progress-specific fields
    progress?: number;
    currentPage?: number;
    totalPages?: number;
    currentSection?: string;
}

interface AnalysisOptions {
    timeoutMs?: number;
    onProgress?: (progress: ProgressUpdate) => void;
    extractTables?: boolean;
    extractCharts?: boolean;
    ocrEnabled?: boolean;
}

interface ProgressUpdate {
    percentage: number;
    currentPage: number;
    totalPages: number;
    currentSection?: string;
    estimatedTimeRemaining?: number;
}

// ============================================================================
// JSON STREAM PARSER - Handles large chunked responses
// ============================================================================

class JSONStreamParser {
    private buffer: string = '';
    private depth: number = 0;
    private inString: boolean = false;
    private escapeNext: boolean = false;
    private jsonStarted: boolean = false;

    /**
     * Append a chunk and return complete JSON if found
     */
    appendChunk(chunk: string): string | null {
        for (let i = 0; i < chunk.length; i++) {
            const char = chunk[i];

            // Handle escape sequences
            if (this.escapeNext) {
                this.buffer += char;
                this.escapeNext = false;
                continue;
            }

            if (char === '\\' && this.inString) {
                this.buffer += char;
                this.escapeNext = true;
                continue;
            }

            // Toggle string mode on quotes
            if (char === '"') {
                this.buffer += char;
                this.inString = !this.inString;
                continue;
            }

            // Track bracket depth outside strings
            if (!this.inString) {
                if (char === '{') {
                    if (!this.jsonStarted) {
                        this.jsonStarted = true;
                        this.buffer = ''; // Clear any garbage before first {
                    }
                    this.depth++;
                    this.buffer += char;
                } else if (char === '}') {
                    this.buffer += char;
                    this.depth--;

                    // Complete JSON object found
                    if (this.depth === 0 && this.jsonStarted) {
                        const result = this.buffer;
                        this.reset();
                        return result;
                    }
                } else if (this.jsonStarted) {
                    this.buffer += char;
                }
                // Skip chars before first {
            } else {
                this.buffer += char;
            }
        }
        return null;
    }

    reset(): void {
        this.buffer = '';
        this.depth = 0;
        this.inString = false;
        this.escapeNext = false;
        this.jsonStarted = false;
    }

    getBufferLength(): number {
        return this.buffer.length;
    }

    getBufferPreview(maxLength: number = 200): string {
        if (this.buffer.length <= maxLength) return this.buffer;
        return this.buffer.substring(0, maxLength) + '...';
    }

    isPartialJson(): boolean {
        return this.jsonStarted && this.depth > 0;
    }
}

// ============================================================================
// RESPONSE VALIDATOR
// ============================================================================

function validatePythonResponse(data: unknown): data is PythonResponse {
    if (!data || typeof data !== 'object') return false;

    const response = data as Record<string, unknown>;

    if (typeof response.status !== 'string') return false;
    if (!['success', 'error', 'progress'].includes(response.status)) return false;

    return true;
}

function sanitizeResponse(response: PythonResponse): PythonResponse {
    // Ensure all expected fields have defaults
    return {
        status: response.status,
        message: response.message,
        extractedData: response.extractedData ?? undefined,
        metrics: response.metrics ?? undefined,
        metadata: response.metadata ?? undefined,
        progress: response.progress,
        currentPage: response.currentPage,
        totalPages: response.totalPages,
        currentSection: response.currentSection,
    };
}

// ============================================================================
// MAIN ANALYSIS FUNCTION
// ============================================================================

export async function runPythonAnalysis(
    filePath: string,
    content?: string,
    fileName?: string,
    options: AnalysisOptions = {}
): Promise<PythonResponse> {
    const {
        timeoutMs = 5 * 60 * 1000, // 5 minutes for large documents
        onProgress,
        extractTables = true,
        extractCharts = false,
        ocrEnabled = false,
    } = options;

    // WEB FALLBACK: Check if running in browser (non-Tauri) environment
    // Check if running in browser (non-Tauri) OR if local server is available
    // @ts-ignore
    const isTauri = !!(window.__TAURI_INTERNALS__ || window.__TAURI__);

    // Always try to use the persistent server first (preserves RAG state)
    let useServer = !isTauri;
    if (isTauri) {
        try {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 500);
            const health = await fetch('http://localhost:8765/health', { signal: controller.signal });
            clearTimeout(id);
            if (health.ok) useServer = true;
        } catch (e) {
            // Server not running, fall back to spawn 
        }
    }

    if (useServer) {
        const apiUrl = isTauri ? 'http://localhost:8765/api/parse' : '/api/parse';
        console.log(`[TauriBridge] Using Server at ${apiUrl}`);

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    file_path: filePath,
                    content: content,
                    file_name: fileName
                })
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`API error (${response.status}): ${text}`);
            }

            const result = await response.json();

            // Map API response from python/api.py to the shape the React app expects.
            // Backend returns a rich object: { items, text, metadata, ... }.
            // The UI expects: response.extractedData.{ items, text }.
            const items = Array.isArray(result.items) ? result.items : [];
            const text = typeof result.text === 'string' ? result.text : '';

            return {
                status: "success",
                extractedData: {
                    items,
                    text,
                    // Pass through any additional structured fields when present
                    pages: result.pages,
                    tables: result.tables,
                    sections: result.sections,
                    financialData: result.financialData,
                },
                metadata: result.metadata || { fileName: fileName || 'document', fileType: 'pdf', pageCount: result.metadata?.totalPages ?? 0 },
                metrics: result.metrics || {},
                message: "Processed via Server API"
            };
        } catch (e) {
            console.error("[TauriBridge] Server API error:", e);
            if (!isTauri) {
                return {
                    status: "error",
                    message: e instanceof Error ? e.message : String(e)
                };
            }
            // If in Tauri and server failed, fall through to spawn
            console.log("[TauriBridge] Falling back to spawned process...");
        }
    }

    const startTime = Date.now();

    console.log('[TauriBridge] ══════════════════════════════════════════');
    console.log('[TauriBridge] Starting Python Analysis');
    console.log('[TauriBridge] ──────────────────────────────────────────');
    console.log('[TauriBridge] File:', filePath || fileName || 'Content Upload');
    console.log('[TauriBridge] Content size:', content ? `${(content.length / 1024).toFixed(2)} KB` : 'N/A');
    console.log('[TauriBridge] Timeout:', `${timeoutMs / 1000}s`);
    console.log('[TauriBridge] Options:', { extractTables, extractCharts, ocrEnabled });
    console.log('[TauriBridge] ══════════════════════════════════════════');

    return new Promise(async (resolve, reject) => {
        let resolved = false;
        let child: Child | null = null;
        let timeoutId: NodeJS.Timeout | null = null;

        const jsonParser = new JSONStreamParser();
        const progressHistory: ProgressUpdate[] = [];
        let lastProgressTime = startTime;

        // ────────────────────────────────────────────────────────────────────
        // CLEANUP & SAFE RESOLUTION
        // ────────────────────────────────────────────────────────────────────

        const cleanup = async () => {
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
        };

        const safeResolve = async (response: any) => {
            if (resolved) return;
            resolved = true;
            await cleanup();

            // Normalise sidecar responses from python/api.py, which use `{ status, data: {...} }`
            // into the shape the React app expects: `response.extractedData`.
            if (response && typeof response === 'object') {
                const r: any = response;
                if (r.status === 'success' && r.data && !r.extractedData) {
                    r.extractedData = r.data;
                }
            }

            const elapsed = Date.now() - startTime;
            console.log(`[TauriBridge] ✓ Resolved with status: ${response.status} (${elapsed}ms)`);

            resolve(sanitizeResponse(response as PythonResponse));
        };

        const safeReject = async (error: Error) => {
            if (resolved) return;
            resolved = true;
            await cleanup();

            console.error('[TauriBridge] ✗ Rejected:', error.message);
            reject(error);
        };

        // ────────────────────────────────────────────────────────────────────
        // TIMEOUT HANDLER
        // ────────────────────────────────────────────────────────────────────

        timeoutId = setTimeout(() => {
            console.error('[TauriBridge] ⏱ TIMEOUT after', timeoutMs / 1000, 'seconds');
            console.error('[TauriBridge] Buffer state:', {
                length: jsonParser.getBufferLength(),
                preview: jsonParser.getBufferPreview(300),
                isPartial: jsonParser.isPartialJson()
            });

            safeResolve({
                status: 'error',
                message: `Analysis timed out after ${timeoutMs / 1000}s. Document may be too large or complex.`,
                metrics: {
                    pagesProcessed: progressHistory.length > 0
                        ? progressHistory[progressHistory.length - 1].currentPage
                        : 0,
                    totalPages: progressHistory.length > 0
                        ? progressHistory[progressHistory.length - 1].totalPages
                        : 0,
                    processingTimeMs: timeoutMs,
                    tablesFound: 0,
                    sectionsFound: 0
                }
            });
        }, timeoutMs);

        // ────────────────────────────────────────────────────────────────────
        // PROCESS SPAWNING
        // ────────────────────────────────────────────────────────────────────

        try {
            const command = Command.create('python3', ['python/api.py']);

            // ── STDOUT HANDLER ──────────────────────────────────────────────

            command.stdout.on('data', (chunk) => {
                if (resolved) return;

                const chunkStr = typeof chunk === 'string' ? chunk : String(chunk);

                console.log(`[TauriBridge] 📥 Chunk received: ${chunkStr.length} bytes`);
                console.log(`[TauriBridge] 📊 Buffer: ${jsonParser.getBufferLength()} bytes`);

                // Parse complete JSON objects from stream
                let completeJson = jsonParser.appendChunk(chunkStr);

                while (completeJson !== null) {
                    try {
                        console.log(`[TauriBridge] 🔍 Parsing JSON (${completeJson.length} chars)...`);

                        const response = JSON.parse(completeJson);

                        if (!validatePythonResponse(response)) {
                            console.warn('[TauriBridge] ⚠ Invalid response structure:',
                                Object.keys(response));
                            completeJson = jsonParser.appendChunk('');
                            continue;
                        }

                        console.log('[TauriBridge] ✓ Valid response:', {
                            status: response.status,
                            hasData: !!response.extractedData,
                            hasMetrics: !!response.metrics,
                            pages: response.totalPages
                        });

                        // Handle progress updates
                        if (response.status === 'progress') {
                            const now = Date.now();
                            const progressUpdate: ProgressUpdate = {
                                percentage: response.progress ?? 0,
                                currentPage: response.currentPage ?? 0,
                                totalPages: response.totalPages ?? 0,
                                currentSection: response.currentSection,
                            };

                            // Calculate ETA
                            if (progressHistory.length > 0 && progressUpdate.percentage > 0) {
                                const elapsed = now - startTime;
                                const estimatedTotal = elapsed / (progressUpdate.percentage / 100);
                                progressUpdate.estimatedTimeRemaining = Math.max(0, estimatedTotal - elapsed);
                            }

                            progressHistory.push(progressUpdate);
                            lastProgressTime = now;

                            console.log(`[TauriBridge] 📈 Progress: ${progressUpdate.percentage.toFixed(1)}%`,
                                `(Page ${progressUpdate.currentPage}/${progressUpdate.totalPages})`);

                            if (onProgress) {
                                onProgress(progressUpdate);
                            }

                            // Continue parsing for more messages
                            completeJson = jsonParser.appendChunk('');
                            continue;
                        }

                        // Final response (success or error)
                        safeResolve(response);
                        return;

                    } catch (parseError) {
                        console.error('[TauriBridge] ❌ JSON parse error:', parseError);
                        console.error('[TauriBridge] Raw data preview:',
                            completeJson.substring(0, 500));

                        // Try next JSON object if any
                        completeJson = jsonParser.appendChunk('');
                    }
                }
            });

            // ── STDERR HANDLER ──────────────────────────────────────────────

            command.stderr.on('data', (line) => {
                const errorStr = typeof line === 'string' ? line : String(line);
                console.error('[TauriBridge] 🐍 Python stderr:', errorStr);

                // Log but don't fail on warnings
                if (errorStr.includes('Warning') || errorStr.includes('warning')) {
                    console.warn('[TauriBridge] ⚠ Python warning (non-fatal)');
                }
            });

            // ── CLOSE HANDLER ───────────────────────────────────────────────

            command.on('close', (data) => {
                console.log('[TauriBridge] 🔚 Process closed:', data);

                if (resolved) return;

                const elapsed = Date.now() - startTime;

                // Try to salvage any remaining buffer content
                const bufferPreview = jsonParser.getBufferPreview(500);
                console.log('[TauriBridge] Remaining buffer:', bufferPreview);

                if (data.code === 0) {
                    safeResolve({
                        status: 'error',
                        message: 'Python process completed but no valid JSON response received',
                        metrics: {
                            pagesProcessed: 0,
                            totalPages: 0,
                            processingTimeMs: elapsed,
                            tablesFound: 0,
                            sectionsFound: 0
                        }
                    });
                } else {
                    safeResolve({
                        status: 'error',
                        message: `Python process exited with code ${data.code}. Check Python logs for details.`,
                        metrics: {
                            pagesProcessed: 0,
                            totalPages: 0,
                            processingTimeMs: elapsed,
                            tablesFound: 0,
                            sectionsFound: 0
                        }
                    });
                }
            });

            // ── ERROR HANDLER ───────────────────────────────────────────────

            command.on('error', (err) => {
                console.error('[TauriBridge] 💥 Command error:', err);
                safeReject(err instanceof Error ? err : new Error(String(err)));
            });

            // ── SPAWN PROCESS ───────────────────────────────────────────────

            child = await command.spawn();
            console.log('[TauriBridge] 🚀 Process spawned, PID:', child.pid);

            // ── SEND REQUEST ────────────────────────────────────────────────

            const request = {
                command: 'parse',
                file_path: filePath,
                content: content,
                file_name: fileName,
                options: {
                    extract_tables: extractTables,
                    extract_charts: extractCharts,
                    ocr_enabled: ocrEnabled,
                    page_by_page: true,
                    include_progress: !!onProgress,
                }
            };

            const requestJson = JSON.stringify(request);

            console.log('[TauriBridge] 📤 Sending request:', {
                command: request.command,
                file_path: request.file_path?.substring(0, 50),
                content_length: content?.length ?? 0,
                options: request.options
            });

            await child.write(requestJson + '\n');
            console.log('[TauriBridge] ✓ Request sent');

        } catch (error) {
            const err = error instanceof Error ? error : new Error(String(error));
            console.error('[TauriBridge] 💥 Setup error:', err);
            safeReject(err);
        }
    });
}

// ============================================================================
// CONFIGURATION SYNC
// ============================================================================

export async function updateTerminologyMapping(mappings: TermMapping[]): Promise<void> {
    console.log('[TauriBridge] Syncing terminology mappings...', mappings.length);

    // 1. Try HTTP Server (Preferred - persistent)
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);

        const response = await fetch('http://localhost:8765/api/mapping', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mappings),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
            console.log('[TauriBridge] ✓ Mappings synced via HTTP');
            return;
        }
    } catch (e) {
        console.warn('[TauriBridge] HTTP sync failed, trying Sidecar fallback...', e);
    }

    // 2. Sidecar Fallback (Fire and forget for now as reading response is complex here)
    try {
        const command = Command.sidecar('binaries/api');
        const child = await command.spawn();

        const request = {
            command: 'update_mapping',
            mappings: mappings
        };

        await child.write(JSON.stringify(request) + '\n');
        console.log('[TauriBridge] ✓ Mappings sent via Sidecar');

    } catch (e) {
        console.error('[TauriBridge] ❌ Failed to sync mappings:', e);
        throw e;
    }
}

// ============================================================================
// HELPER: DISPLAY FINANCIAL DATA
// ============================================================================

export interface DisplayableDocument {
    summary: DocumentSummary;
    pages: DisplayablePage[];
    tables: DisplayableTable[];
    sections: DisplayableSection[];
    rawData?: PythonResponse;
}

export interface DocumentSummary {
    fileName: string;
    pageCount: number;
    processingTime: string;
    tableCount: number;
    sectionCount: number;
    status: 'success' | 'partial' | 'error';
    message?: string;
}

export interface DisplayablePage {
    number: number;
    content: string;
    hasTables: boolean;
    tableCount: number;
}

export interface DisplayableTable {
    id: string;
    pageNumber: number;
    type: string;
    headers: string[];
    rows: string[][];
    title?: string;
}

export interface DisplayableSection {
    id: string;
    title: string;
    pageRange: string;
    preview: string;
}

export function processDocumentForDisplay(response: PythonResponse): DisplayableDocument {
    const { extractedData, metrics, metadata, status, message } = response;

    // Handle error cases
    if (status === 'error' || !extractedData) {
        return {
            summary: {
                fileName: metadata?.fileName ?? 'Unknown',
                pageCount: 0,
                processingTime: '0s',
                tableCount: 0,
                sectionCount: 0,
                status: 'error',
                message: message ?? 'Failed to extract document data'
            },
            pages: [],
            tables: [],
            sections: []
        };
    }

    // Process pages
    const pages: DisplayablePage[] = (extractedData.pages ?? []).map((page, idx) => ({
        number: page.pageNumber ?? idx + 1,
        content: page.content ?? '',
        hasTables: (page.tables?.length ?? 0) > 0,
        tableCount: page.tables?.length ?? 0
    }));

    // Process tables
    const tables: DisplayableTable[] = (extractedData.tables ?? []).map((table, idx) => ({
        id: `table-${idx}`,
        pageNumber: table.pageNumber,
        type: table.tableType ?? 'other',
        headers: table.headers,
        rows: table.rows,
        title: detectTableTitle(table)
    }));

    // Process sections
    const sections: DisplayableSection[] = (extractedData.sections ?? []).map((section, idx) => ({
        id: `section-${idx}`,
        title: section.title,
        pageRange: `Pages ${section.startPage}-${section.endPage}`,
        preview: section.content.substring(0, 200) + (section.content.length > 200 ? '...' : '')
    }));

    // Build summary
    const processingTimeSeconds = ((metrics?.processingTimeMs ?? 0) / 1000).toFixed(2);

    return {
        summary: {
            fileName: metadata?.fileName ?? 'Document',
            pageCount: metrics?.totalPages ?? pages.length,
            processingTime: `${processingTimeSeconds}s`,
            tableCount: tables.length,
            sectionCount: sections.length,
            status: 'success'
        },
        pages,
        tables,
        sections,
        rawData: response
    };
}

function detectTableTitle(table: TableData): string {
    switch (table.tableType) {
        case 'balance_sheet': return 'Balance Sheet';
        case 'income_statement': return 'Income Statement';
        case 'cash_flow': return 'Cash Flow Statement';
        case 'notes': return 'Notes';
        default: return `Table (Page ${table.pageNumber})`;
    }
}

// ============================================================================
// UTILITY: PROGRESS DISPLAY COMPONENT DATA
// ============================================================================

export interface ProgressDisplayData {
    percentage: number;
    currentPage: number;
    totalPages: number;
    eta: string;
    status: string;
}

export function formatProgressForDisplay(progress: ProgressUpdate): ProgressDisplayData {
    let eta = 'Calculating...';

    if (progress.estimatedTimeRemaining !== undefined) {
        const seconds = Math.ceil(progress.estimatedTimeRemaining / 1000);
        if (seconds < 60) {
            eta = `${seconds}s remaining`;
        } else {
            const minutes = Math.ceil(seconds / 60);
            eta = `~${minutes}m remaining`;
        }
    }

    return {
        percentage: Math.round(progress.percentage),
        currentPage: progress.currentPage,
        totalPages: progress.totalPages,
        eta,
        status: progress.currentSection ?? `Processing page ${progress.currentPage}...`
    };
}

// ============================================================================
// RAG SEARCH
// ============================================================================

export async function searchRAG(query: string): Promise<any[]> {
    console.log('[TauriBridge] Searching RAG:', query);
    try {
        // Try HTTP Server
        const response = await fetch('http://localhost:8765/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        if (response.ok) {
            const result = await response.json();
            // result is { status: "success", data: { results: [...] } } or { results: ... } depending on implementation
            // The API implementation returns: { results: json.loads(...) } directly inside 'data' wrapper if via sidecar, 
            // but Flask 'return jsonify(result)' where result = {"results": ...} 

            // Wait, Flask endpoint returns jsonify(result).
            // backend service search_rag returns: {"results": [...]}
            // So response body is {"results": [...]}

            if (result.results) {
                return result.results;
            }
            if (result.data && result.data.results) {
                return result.data.results;
            }
        }
    } catch (e) {
        console.warn('[TauriBridge] RAG search failed usually means server not running or docs not indexed:', e);
    }
    return [];
}