import { invoke } from '@tauri-apps/api/core';
import { TermMapping } from '../types';

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
