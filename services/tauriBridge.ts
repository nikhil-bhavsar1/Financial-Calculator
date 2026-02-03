import { invoke } from '@tauri-apps/api/core';
import { TermMapping } from '../types';
import { IndASService, IndASDocument, IndASProcessingOptions } from './indASService';
import { IndianNumberParser, ParsedNumber } from './indianNumberParser';

// ============================================================================
// TYPES
// ============================================================================

// ============================================================================
// TYPES
// ============================================================================

interface ExtractedData {
    text?: string;
    items?: any[];
    pages?: any[];
    tables?: any[];
    sections?: any[];
    financialData?: any;
}

export interface PythonResponse {
    status: 'success' | 'error' | 'progress';
    extractedData?: ExtractedData;
    extracted_data?: ExtractedData; // Rust uses snake_case
    metrics?: any;
    metadata?: any;
    message?: string;
    error?: string;
    progress?: number;
    currentPage?: number;
    totalPages?: number;
    currentSection?: string;
}

interface AnalysisOptions {
    timeoutMs?: number;
    onProgress?: (progress: any) => void;
    extractTables?: boolean;
    extractCharts?: boolean;
    ocrEnabled?: boolean;
    indASProcessing?: boolean; // Ind AS specific processing
    parseIndianNumbers?: boolean; // Parse Indian number formats
    detectIndASSigns?: boolean; // Detect Ind AS sign conventions
}

// ============================================================================
// MAIN ANALYSIS FUNCTION - Uses Rust invoke instead of shell plugin
// ============================================================================

export async function runPythonAnalysis(
    filePath: string,
    content?: string,
    fileName?: string,
    options: AnalysisOptions = {}
): Promise<PythonResponse> {
    const {
        extractTables = true,
        extractCharts = false,
        ocrEnabled = false,
        indASProcessing = false,
        parseIndianNumbers = false,
        detectIndASSigns = false,
    } = options;

    console.log('[TauriBridge] Starting Analysis via Rust Bridge');
    console.log('[TauriBridge] File:', fileName);

    try {
        // Call Rust command directly - no shell plugin needed
        const response = await invoke<PythonResponse>('run_python_analysis', {
            filePath,
            content: content || null,
            fileName: fileName || null,
            options: {
                extract_tables: extractTables,
                extract_charts: extractCharts,
                ocr_enabled: ocrEnabled,
                page_by_page: true,
                // Ind AS specific options
                ind_as_processing: indASProcessing,
                parse_indian_numbers: parseIndianNumbers,
                detect_ind_as_signs: detectIndASSigns
            }
        });

        console.log('[TauriBridge] Rust response:', response);

        // Normalize response (Rust uses snake_case, frontend expects camelCase)
        if (response.extracted_data && !response.extractedData) {
            response.extractedData = response.extracted_data;
        }

        return response;

    } catch (error) {
        console.error('[TauriBridge] Error:', error);
        return {
            status: 'error',
            message: error instanceof Error ? error.message : String(error)
        };
    }
}

export async function updateTerminologyMapping(mappings: TermMapping[]): Promise<void> {
    try {
        await invoke('update_terminology_mapping', { mappings });
    } catch (e) {
        console.error('Failed to sync mappings', e);
        throw e;
    }
}

export async function calculateMetrics(items: any[]): Promise<any[]> {
    try {
        const response = await invoke<PythonResponse>('run_python_analysis', {
            filePath: 'INTERNAL', // Command routing handles this
            content: null,
            fileName: null,
            options: {
                command: 'calculate_metrics',
                items_json: JSON.stringify(items)
            }
        });

        if (response.status === 'success' && response.metrics) {
            return response.metrics;
        }
        return [];
    } catch (error) {
        console.error('[TauriBridge] Metrics Calculation Error:', error);
        return [];
    }
}

// Minimal display logic helpers
export function processDocumentForDisplay(response: PythonResponse): any {
    const { extractedData, metadata, status, message } = response;
    if (status === 'error' || !extractedData) {
        return {
            summary: {
                fileName: metadata?.fileName ?? 'Unknown',
                pageCount: 0,
                status: 'error',
                message: message ?? 'Failed'
            },
            pages: [],
            tables: [],
            sections: []
        };
    }
    return {
        summary: {
            fileName: metadata?.fileName || 'Document',
            pageCount: extractedData.pages?.length || 0,
            status: 'success'
        },
        pages: extractedData.pages || [],
        tables: extractedData.tables || [],
        sections: extractedData.sections || []
    };
}

export async function searchRAG(query: string, limit: number = 5): Promise<{ page: number; text: string; score: number }[]> {
    // RAG search not yet implemented in Rust bridge
    console.warn('RAG search not implemented in Rust bridge yet');
    return [];
}

// ============================================================================
// COMPANY SCRAPER COMMANDS
// ============================================================================

export async function searchCompanies(
    query: string,
    exchange: string = 'BOTH',
    limit: number = 10
): Promise<any> {
    try {
        const result = await invoke('search_companies', { query, exchange, limit });
        return result;
    } catch (error) {
        console.error('Failed to search companies:', error);
        return { success: false, error: String(error) };
    }
}

export async function getCompanyDetails(
    symbol: string,
    exchange: string
): Promise<any> {
    try {
        const result = await invoke('get_company_details', { symbol, exchange });
        return result;
    } catch (error) {
        console.error('Failed to get company details:', error);
        return { success: false, error: String(error) };
    }
}

export async function getStockQuote(
    symbol: string,
    exchange: string
): Promise<any> {
    try {
        const result = await invoke('get_stock_quote', { symbol, exchange });
        return result;
    } catch (error) {
        console.error('Failed to get stock quote:', error);
        return { success: false, error: String(error) };
    }
}

export async function searchWeb(query: string): Promise<any> {
    try {
        const result = await invoke('search_web', { query });
        return result;
    } catch (error) {
        console.error('Failed to search web:', error);
        return { success: false, error: String(error) };
    }
}

export async function getScraperStatus(): Promise<any> {
    try {
        const result = await invoke('get_scraper_status');
        return result;
    } catch (error) {
        console.error('Failed to get scraper status:', error);
        return { success: false, error: String(error) };
    }
}

export async function getDbData(): Promise<any> {
    try {
        const result = await invoke('get_db_data');
        return result;
    } catch (error) {
        console.error('Failed to get DB data:', error);
        return { status: 'error', message: String(error) };
    }
}

// ============================================================================
// IND AS SPECIFIC FUNCTIONS
// ============================================================================

/**
 * Process document with Ind AS capabilities (Frontend implementation)
 * This uses the Ind AS service to process documents with Indian accounting standards awareness
 */
export async function processWithIndAS(
    textContent: string,
    tables: Array<{ headers: string[]; rows: string[][] }>,
    options: Partial<IndASProcessingOptions> = {}
): Promise<IndASDocument> {
    console.log('[TauriBridge] Processing document with Ind AS capabilities');

    try {
        const result = IndASService.processIndASDocument(textContent, tables, options);
        console.log('[TauriBridge] Ind AS processing complete:', {
            isIndAS: result.isIndASDocument,
            confidence: result.confidence,
            tableCount: result.tables.length
        });
        return result;
    } catch (error) {
        console.error('[TauriBridge] Ind AS processing error:', error);
        return {
            structure: IndASService.detectStructure(textContent),
            tables: [],
            isIndASDocument: false,
            confidence: 0
        };
    }
}

/**
 * Parse Indian number format string
 */
export function parseIndianNumber(input: string): ParsedNumber | null {
    return IndianNumberParser.parse(input);
}

/**
 * Parse multiple Indian number format strings
 */
export function parseIndianNumbers(inputs: string[]): (ParsedNumber | null)[] {
    return IndianNumberParser.parseArray(inputs);
}

/**
 * Check if string is Indian number format
 */
export function isIndianNumberFormat(input: string): boolean {
    return IndianNumberParser.isIndianFormat(input);
}

/**
 * Format number in Indian style
 */
export function formatIndianNumber(num: number): string {
    return IndianNumberParser.formatIndian(num);
}

/**
 * Convert number to Indian words
 */
export function toIndianWords(num: number): string {
    return IndianNumberParser.toIndianWords(num);
}

/**
 * Detect document structure (Ind AS aware)
 */
export function detectDocumentStructure(textContent: string): any {
    return IndASService.detectStructure(textContent);
}

/**
 * Check if document follows Ind AS standards
 */
export function isIndASFiling(textContent: string): boolean {
    return IndASService.isIndASFiling(textContent);
}

/**
 * Get Ind AS specific warnings for document
 */
export function getIndASWarnings(text: string): string[] {
    return IndASService.getIndASWarnings(text);
}

/**
 * Get recommended actions based on Ind AS analysis
 */
export function getRecommendedActions(document: IndASDocument): string[] {
    return IndASService.getRecommendedActions(document);
}

/**
 * Enhanced processDocumentForDisplay with Ind AS support
 */
export async function processDocumentForDisplayWithIndAS(
    response: any,
    textContent: string
): Promise<{
    summary: any;
    pages: any[];
    tables: any[];
    sections: any[];
    indASAnalysis?: {
        isIndASDocument: boolean;
        confidence: number;
        structure: any;
        warnings: string[];
        recommendedActions: string[];
    };
}> {
    // Process standard document info
    const standardDisplay = processDocumentForDisplay(response);

    // Perform Ind AS analysis
    const indASAnalysis = {
        isIndASDocument: isIndASFiling(textContent),
        confidence: 0,
        structure: detectDocumentStructure(textContent),
        warnings: getIndASWarnings(textContent),
        recommendedActions: []
    };

    // Calculate confidence based on structure
    if (indASAnalysis.structure.isIndAS) {
        indASAnalysis.confidence += 0.5;
    }
    if (indASAnalysis.structure.isStandalone || indASAnalysis.structure.isConsolidated) {
        indASAnalysis.confidence += 0.2;
    }
    if (indASAnalysis.warnings.length === 0) {
        indASAnalysis.confidence += 0.3;
    }

    // Get recommended actions if tables exist
    if (standardDisplay.tables && standardDisplay.tables.length > 0) {
        try {
            const indASDoc = await processWithIndAS(
                textContent,
                standardDisplay.tables.map((table: any) => ({
                    headers: table.headers || [],
                    rows: table.rows || []
                }))
            );
            indASAnalysis.recommendedActions = IndASService.getRecommendedActions(indASDoc);
            indASAnalysis.confidence = indASDoc.confidence;
        } catch (e) {
            console.error('Error getting Ind AS recommendations:', e);
        }
    }

    return {
        ...standardDisplay,
        indASAnalysis
    };
}

// ============================================================================
// DATABASE STREAMING FUNCTIONS
// ============================================================================

export async function startDbStreaming(): Promise<any> {
    try {
        const result = await invoke('start_db_streaming');
        return result;
    } catch (error) {
        console.error('Failed to start database streaming:', error);
        return { status: 'error', message: String(error) };
    }
}

export async function stopDbStreaming(): Promise<any> {
    try {
        const result = await invoke('stop_db_streaming');
        return result;
    } catch (error) {
        console.error('Failed to stop database streaming:', error);
        return { status: 'error', message: String(error) };
    }
}

