import React, { useState, useEffect, useCallback, useRef, useMemo, startTransition } from 'react';
import {
    ChevronLeft, ChevronRight, Search, Maximize2, Minimize2,
    ZoomIn, ZoomOut, ArrowUp, ArrowDown, X, List,
    ChevronsLeft, ChevronsRight, Grid3X3, Bookmark, Download,
    Edit3, Eye, Columns, Save, Copy, Check, Code, FileText,
    AlignLeft, AlignCenter, AlignRight, Table, Hash, Bold,
    Italic, Link, Image, ListOrdered, Quote, Minus, RotateCcw,
    Undo, Redo, Printer, Share2, Settings, Loader2
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

interface DocumentViewerProps {
    content: string;
    className?: string;
    initialPage?: number;
    onClose?: () => void;
    onSave?: (content: string) => void;
    title?: string;
    editable?: boolean;
    showToolbar?: boolean;
    fileUrl?: string;
    fileType?: 'pdf' | 'image' | 'text';
}

import { Document, Page as PdfPage, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set worker source
// Set worker source
// Use Vite's explicit URL import for the worker to ensure it bundles correctly for Tauri/Offline use
// @ts-ignore
import pdfWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
pdfjs.GlobalWorkerOptions.workerSrc = pdfWorker;

interface Page {
    number: number;
    content: string;
    preview?: string;
}

interface TableCell {
    content: string;
    align: 'left' | 'center' | 'right';
}

interface ParsedTable {
    headers: TableCell[];
    rows: TableCell[][];
    alignments: ('left' | 'center' | 'right')[];
}

type ViewMode = 'preview' | 'edit' | 'split' | 'file';

// ============================================================================
// MARKDOWN PARSER
// ============================================================================

class MarkdownParser {
    private static escapeHtml(text: string): string {
        const htmlEntities: Record<string, string> = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, char => htmlEntities[char]);
    }

    static parseTable(tableText: string): ParsedTable | null {
        const lines = tableText.trim().split('\n').filter(line => line.trim());

        if (lines.length < 2) return null;

        // Parse header
        const headerLine = lines[0];
        const separatorLine = lines[1];

        // Validate separator line
        if (!/^\|?[\s\-:|]+\|?$/.test(separatorLine)) return null;

        const parseRow = (line: string): string[] => {
            return line
                .replace(/^\||\|$/g, '')
                .split('|')
                .map(cell => cell.trim());
        };

        const headers = parseRow(headerLine);

        // Parse alignments from separator
        const alignments: ('left' | 'center' | 'right')[] = parseRow(separatorLine).map(sep => {
            const trimmed = sep.trim();
            if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center';
            if (trimmed.endsWith(':')) return 'right';
            return 'left';
        });

        // Parse data rows
        const rows: TableCell[][] = [];
        for (let i = 2; i < lines.length; i++) {
            const cells = parseRow(lines[i]);
            const row: TableCell[] = cells.map((content, idx) => ({
                content,
                align: alignments[idx] || 'left'
            }));
            rows.push(row);
        }

        return {
            headers: headers.map((content, idx) => ({
                content,
                align: alignments[idx] || 'left'
            })),
            rows,
            alignments
        };
    }

    static parseInline(text: string): string {
        let result = this.escapeHtml(text);

        // Bold + Italic
        result = result.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
        result = result.replace(/___(.+?)___/g, '<strong><em>$1</em></strong>');

        // Bold
        result = result.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        result = result.replace(/__(.+?)__/g, '<strong>$1</strong>');

        // Italic
        result = result.replace(/\*(.+?)\*/g, '<em>$1</em>');
        result = result.replace(/_(.+?)_/g, '<em>$1</em>');

        // Strikethrough
        result = result.replace(/~~(.+?)~~/g, '<del>$1</del>');

        // Inline code
        result = result.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

        // Links
        result = result.replace(
            /\[([^\]]+)\]\(([^)]+)\)/g,
            '<a href="$2" class="md-link" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // Images
        result = result.replace(
            /!\[([^\]]*)\]\(([^)]+)\)/g,
            '<img src="$2" alt="$1" class="md-image" loading="lazy" />'
        );

        // Highlight
        result = result.replace(/==(.+?)==/g, '<mark class="md-highlight">$1</mark>');

        // Superscript
        result = result.replace(/\^([^\s^]+)\^/g, '<sup>$1</sup>');

        // Subscript
        result = result.replace(/~([^\s~]+)~/g, '<sub>$1</sub>');

        return result;
    }

    static parse(markdown: string): { html: string; toc: { level: number; text: string; id: string }[] } {
        const lines = markdown.split('\n');
        const result: string[] = [];
        const toc: { level: number; text: string; id: string }[] = [];

        let inCodeBlock = false;
        let codeBlockLang = '';
        let codeContent: string[] = [];
        let inTable = false;
        let tableLines: string[] = [];
        let inBlockquote = false;
        let blockquoteContent: string[] = [];
        let inList = false;
        let listType: 'ul' | 'ol' = 'ul';
        let listItems: string[] = [];

        const flushTable = () => {
            if (tableLines.length > 0) {
                const table = this.parseTable(tableLines.join('\n'));
                if (table) {
                    result.push(this.renderTable(table));
                }
                tableLines = [];
            }
            inTable = false;
        };

        const flushBlockquote = () => {
            if (blockquoteContent.length > 0) {
                const content = blockquoteContent.map(line => this.parseInline(line)).join('<br/>');
                result.push(`<blockquote class="md-blockquote">${content}</blockquote>`);
                blockquoteContent = [];
            }
            inBlockquote = false;
        };

        const flushList = () => {
            if (listItems.length > 0) {
                const tag = listType;
                const items = listItems.map(item => `<li>${this.parseInline(item)}</li>`).join('');
                result.push(`<${tag} class="md-list">${items}</${tag}>`);
                listItems = [];
            }
            inList = false;
        };

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmedLine = line.trim();

            // Code blocks
            if (trimmedLine.startsWith('```')) {
                if (inCodeBlock) {
                    const langClass = codeBlockLang ? ` language-${codeBlockLang}` : '';
                    const escapedCode = this.escapeHtml(codeContent.join('\n'));
                    result.push(
                        `<div class="md-code-block">` +
                        `<div class="code-header"><span class="code-lang">${codeBlockLang || 'code'}</span>` +
                        `<button class="copy-btn" data-code="${encodeURIComponent(codeContent.join('\n'))}">Copy</button></div>` +
                        `<pre><code class="${langClass}">${escapedCode}</code></pre></div>`
                    );
                    codeContent = [];
                    codeBlockLang = '';
                    inCodeBlock = false;
                } else {
                    flushTable();
                    flushBlockquote();
                    flushList();
                    codeBlockLang = trimmedLine.slice(3).trim();
                    inCodeBlock = true;
                }
                continue;
            }

            if (inCodeBlock) {
                codeContent.push(line);
                continue;
            }

            // Tables
            if (trimmedLine.startsWith('|') || (trimmedLine.includes('|') && /^[\s\-:|]+$/.test(trimmedLine))) {
                flushBlockquote();
                flushList();
                if (!inTable) inTable = true;
                tableLines.push(trimmedLine);
                continue;
            } else if (inTable) {
                flushTable();
            }

            // Blockquotes
            if (trimmedLine.startsWith('>')) {
                flushList();
                if (!inBlockquote) inBlockquote = true;
                blockquoteContent.push(trimmedLine.replace(/^>\s*/, ''));
                continue;
            } else if (inBlockquote) {
                flushBlockquote();
            }

            // Lists
            const ulMatch = trimmedLine.match(/^[-*+]\s+(.+)$/);
            const olMatch = trimmedLine.match(/^\d+\.\s+(.+)$/);
            const taskMatch = trimmedLine.match(/^[-*+]\s+\[([ xX])\]\s+(.+)$/);

            if (taskMatch) {
                flushBlockquote();
                if (inList && listType !== 'ul') flushList();
                if (!inList) { inList = true; listType = 'ul'; }
                const checked = taskMatch[1].toLowerCase() === 'x';
                listItems.push(
                    `<label class="task-item"><input type="checkbox" ${checked ? 'checked' : ''} disabled />${taskMatch[2]}</label>`
                );
                continue;
            } else if (ulMatch) {
                flushBlockquote();
                if (inList && listType !== 'ul') flushList();
                if (!inList) { inList = true; listType = 'ul'; }
                listItems.push(ulMatch[1]);
                continue;
            } else if (olMatch) {
                flushBlockquote();
                if (inList && listType !== 'ol') flushList();
                if (!inList) { inList = true; listType = 'ol'; }
                listItems.push(olMatch[1]);
                continue;
            } else if (inList && trimmedLine === '') {
                flushList();
            } else if (inList) {
                flushList();
            }

            // Empty line
            if (trimmedLine === '') {
                result.push('<br class="md-break"/>');
                continue;
            }

            // Horizontal rule
            if (/^[-*_]{3,}$/.test(trimmedLine)) {
                result.push('<hr class="md-hr"/>');
                continue;
            }

            // Headers
            const headerMatch = trimmedLine.match(/^(#{1,6})\s+(.+)$/);
            if (headerMatch) {
                const level = headerMatch[1].length;
                const text = headerMatch[2];
                const id = text.toLowerCase().replace(/[^\w]+/g, '-');
                toc.push({ level, text, id });
                result.push(
                    `<h${level} id="${id}" class="md-heading md-h${level}">${this.parseInline(text)}</h${level}>`
                );
                continue;
            }

            // Paragraph
            result.push(`<p class="md-paragraph">${this.parseInline(trimmedLine)}</p>`);
        }

        // Flush remaining content
        flushTable();
        flushBlockquote();
        flushList();

        if (inCodeBlock && codeContent.length > 0) {
            const escapedCode = this.escapeHtml(codeContent.join('\n'));
            result.push(`<div class="md-code-block"><pre><code>${escapedCode}</code></pre></div>`);
        }

        return { html: result.join('\n'), toc };
    }

    private static renderTable(table: ParsedTable): string {
        const alignStyle = (align: 'left' | 'center' | 'right') => {
            return `text-align: ${align}`;
        };

        const headerCells = table.headers
            .map(cell => `<th style="${alignStyle(cell.align)}">${this.parseInline(cell.content)}</th>`)
            .join('');

        const bodyRows = table.rows
            .map(row => {
                const cells = row
                    .map(cell => `<td style="${alignStyle(cell.align)}">${this.parseInline(cell.content)}</td>`)
                    .join('');
                return `<tr>${cells}</tr>`;
            })
            .join('');

        return `
            <div class="md-table-wrapper">
                <table class="md-table">
                    <thead><tr>${headerCells}</tr></thead>
                    <tbody>${bodyRows}</tbody>
                </table>
            </div>
        `;
    }
}

// ============================================================================
// MARKDOWN STYLES
// ============================================================================

const markdownStyles = `
    .markdown-content {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.75;
        color: var(--text-primary, #1a1a2e);
    }

    .markdown-content .md-heading {
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-top: 1.5em;
        margin-bottom: 0.75em;
        color: var(--text-primary, #1a1a2e);
        border-bottom: none;
        position: relative;
    }

    .markdown-content .md-h1 {
        font-size: 2.25em;
        border-bottom: 2px solid var(--accent-primary, #6366f1);
        padding-bottom: 0.3em;
    }

    .markdown-content .md-h2 {
        font-size: 1.75em;
        border-bottom: 1px solid var(--border-default, #e5e7eb);
        padding-bottom: 0.25em;
    }

    .markdown-content .md-h3 { font-size: 1.5em; }
    .markdown-content .md-h4 { font-size: 1.25em; }
    .markdown-content .md-h5 { font-size: 1.1em; }
    .markdown-content .md-h6 { font-size: 1em; color: var(--text-secondary, #6b7280); }

    .markdown-content .md-paragraph {
        margin-bottom: 1em;
        text-align: justify;
    }

    .markdown-content .md-break {
        display: block;
        height: 0.5em;
    }

    .markdown-content strong {
        font-weight: 600;
        color: var(--text-primary, #1a1a2e);
    }

    .markdown-content em {
        font-style: italic;
    }

    .markdown-content del {
        text-decoration: line-through;
        opacity: 0.7;
    }

    .markdown-content .inline-code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.875em;
        background: var(--bg-code, #f3f4f6);
        color: var(--accent-primary, #6366f1);
        padding: 0.2em 0.4em;
        border-radius: 4px;
        font-weight: 500;
    }

    .markdown-content .md-link {
        color: var(--accent-primary, #6366f1);
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .markdown-content .md-link:hover {
        border-bottom-color: var(--accent-primary, #6366f1);
    }

    .markdown-content .md-image {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 1em 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .markdown-content .md-highlight {
        background: linear-gradient(120deg, #fef08a 0%, #fde047 100%);
        padding: 0.1em 0.3em;
        border-radius: 3px;
    }

    .markdown-content .md-blockquote {
        margin: 1.5em 0;
        padding: 1em 1.5em;
        border-left: 4px solid var(--accent-primary, #6366f1);
        background: var(--bg-subtle, #f9fafb);
        border-radius: 0 8px 8px 0;
        color: var(--text-secondary, #4b5563);
        font-style: italic;
    }

    .markdown-content .md-list {
        margin: 1em 0;
        padding-left: 1.5em;
    }

    .markdown-content .md-list li {
        margin-bottom: 0.5em;
        position: relative;
    }

    .markdown-content .md-list li::marker {
        color: var(--accent-primary, #6366f1);
    }

    .markdown-content .task-item {
        display: flex;
        align-items: center;
        gap: 0.5em;
        cursor: default;
    }

    .markdown-content .task-item input[type="checkbox"] {
        width: 16px;
        height: 16px;
        accent-color: var(--accent-primary, #6366f1);
    }

    .markdown-content .md-hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--border-default, #e5e7eb), transparent);
        margin: 2em 0;
    }

    /* Code Block Styles */
    .markdown-content .md-code-block {
        margin: 1.5em 0;
        border-radius: 12px;
        overflow: hidden;
        background: #1e1e2e;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }

    .markdown-content .code-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75em 1em;
        background: #181825;
        border-bottom: 1px solid #313244;
    }

    .markdown-content .code-lang {
        font-size: 0.75em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #a6adc8;
    }

    .markdown-content .copy-btn {
        font-size: 0.75em;
        padding: 0.25em 0.75em;
        background: #313244;
        border: none;
        border-radius: 4px;
        color: #cdd6f4;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .markdown-content .copy-btn:hover {
        background: #45475a;
    }

    .markdown-content .md-code-block pre {
        margin: 0;
        padding: 1.25em;
        overflow-x: auto;
    }

    .markdown-content .md-code-block code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.875em;
        color: #cdd6f4;
        line-height: 1.6;
    }

    /* Table Styles */
    .markdown-content .md-table-wrapper {
        margin: 1.5em 0;
        overflow-x: auto;
        border-radius: 12px;
        border: 1px solid var(--border-default, #e5e7eb);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .markdown-content .md-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
    }

    .markdown-content .md-table th {
        background: linear-gradient(180deg, var(--bg-elevated, #f9fafb) 0%, var(--bg-subtle, #f3f4f6) 100%);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75em;
        letter-spacing: 0.05em;
        color: var(--text-secondary, #6b7280);
        padding: 1em 1.25em;
        border-bottom: 2px solid var(--border-default, #e5e7eb);
        white-space: nowrap;
    }

    .markdown-content .md-table td {
        padding: 0.875em 1.25em;
        border-bottom: 1px solid var(--border-weak, #f3f4f6);
        color: var(--text-primary, #1f2937);
        vertical-align: top;
    }

    .markdown-content .md-table tbody tr {
        transition: background 0.15s ease;
    }

    .markdown-content .md-table tbody tr:hover {
        background: var(--bg-hover, #f9fafb);
    }

    .markdown-content .md-table tbody tr:last-child td {
        border-bottom: none;
    }

    /* Alternating row colors */
    .markdown-content .md-table tbody tr:nth-child(even) {
        background: var(--bg-subtle, #fafafa);
    }

    .markdown-content .md-table tbody tr:nth-child(even):hover {
        background: var(--bg-hover, #f3f4f6);
    }

    /* Numeric cell styling */
    .markdown-content .md-table td[style*="text-align: right"] {
        font-family: 'JetBrains Mono', monospace;
        font-variant-numeric: tabular-nums;
    }

    /* Dark mode adjustments */
    .dark .markdown-content {
        color: var(--text-primary, #e5e7eb);
    }

    .dark .markdown-content .md-heading {
        color: var(--text-primary, #f3f4f6);
    }

    .dark .markdown-content .inline-code {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
    }

    .dark .markdown-content .md-blockquote {
        background: rgba(99, 102, 241, 0.1);
        border-left-color: #818cf8;
    }

    .dark .markdown-content .md-table-wrapper {
        border-color: var(--border-default, #374151);
    }

    .dark .markdown-content .md-table th {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
        color: #9ca3af;
        border-bottom-color: #374151;
    }

    .dark .markdown-content .md-table td {
        border-bottom-color: #1f2937;
        color: #e5e7eb;
    }

    .dark .markdown-content .md-table tbody tr:nth-child(even) {
        background: rgba(255, 255, 255, 0.02);
    }

    .dark .markdown-content .md-table tbody tr:hover {
        background: rgba(99, 102, 241, 0.1);
    }
`;

// ============================================================================
// MARKDOWN RENDERER COMPONENT
// ============================================================================

interface MarkdownRendererProps {
    content: string;
    className?: string;
    searchQuery?: string;
    onCopyCode?: (code: string) => void;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
    content,
    className = '',
    searchQuery = '',
    onCopyCode
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [parsedData, setParsedData] = useState({ html: '', toc: [] });
    const [isParsing, setIsParsing] = useState(false);

    // Asynchronous parsing with debounce
    useEffect(() => {
        setIsParsing(true);
        const timer = setTimeout(() => {
            // Processing in a timeout yields to the main thread, allowing UI updates first
            const result = MarkdownParser.parse(content);
            setParsedData(result);
            setIsParsing(false);
        }, 50); // Small delay to debounce and unblock UI

        return () => clearTimeout(timer);
    }, [content]);

    // Highlight search results
    const highlightedHtml = useMemo(() => {
        if (!searchQuery.trim()) return parsedData.html;

        const escapedQuery = searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedQuery})`, 'gi');

        return parsedData.html.replace(regex, '<mark class="search-highlight">$1</mark>');
    }, [parsedData.html, searchQuery]);

    // Handle copy button clicks
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const handleClick = (e: MouseEvent) => {
            const target = e.target as HTMLElement;
            if (target.classList.contains('copy-btn')) {
                const code = decodeURIComponent(target.dataset.code || '');
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = target.textContent;
                    target.textContent = 'Copied!';
                    target.classList.add('copied');
                    setTimeout(() => {
                        target.textContent = originalText;
                        target.classList.remove('copied');
                    }, 2000);
                });
                onCopyCode?.(code);
            }
        };

        container.addEventListener('click', handleClick);
        return () => container.removeEventListener('click', handleClick);
    }, [onCopyCode]);

    return (
        <>
            <style>{markdownStyles}</style>
            <style>{`
                .search-highlight {
                    background: #fef08a;
                    padding: 0.1em 0.2em;
                    border-radius: 2px;
                }
                .dark .search-highlight {
                    background: #ca8a04;
                    color: #1f2937;
                }
            `}</style>
            <div
                ref={containerRef}
                className={`markdown-content ${className} ${isParsing ? 'opacity-70 transition-opacity duration-200' : ''}`}
                dangerouslySetInnerHTML={{ __html: highlightedHtml }}
            />
        </>
    );
};

// ============================================================================
// MARKDOWN EDITOR COMPONENT
// ============================================================================

interface MarkdownEditorProps {
    value: string;
    onChange: (value: string) => void;
    className?: string;
    placeholder?: string;
    onScroll?: (e: React.UIEvent<HTMLTextAreaElement>) => void;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
    value,
    onChange,
    className = '',
    placeholder = 'Write your markdown here...',
    onScroll
}) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const lineNumbersRef = useRef<HTMLDivElement>(null);
    const [lineCount, setLineCount] = useState(1);
    const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });

    // Update line count
    useEffect(() => {
        const lines = value.split('\n').length;
        setLineCount(lines);
    }, [value]);

    // Sync scroll between textarea and line numbers
    const handleScroll = (e: React.UIEvent<HTMLTextAreaElement>) => {
        if (textareaRef.current && lineNumbersRef.current) {
            lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
        }
        if (onScroll) {
            onScroll(e);
        }
    };

    // Update cursor position
    const updateCursorPosition = () => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        const text = textarea.value.substring(0, textarea.selectionStart);
        const lines = text.split('\n');
        setCursorPosition({
            line: lines.length,
            column: lines[lines.length - 1].length + 1
        });
    };

    // Insert text at cursor
    const insertText = (before: string, after: string = '') => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = value.substring(start, end);
        const newText = value.substring(0, start) + before + selectedText + after + value.substring(end);

        onChange(newText);

        // Restore cursor position
        setTimeout(() => {
            const newCursorPos = start + before.length + (selectedText ? selectedText.length + after.length : 0);
            textarea.focus();
            textarea.setSelectionRange(
                selectedText ? start + before.length : newCursorPos,
                selectedText ? start + before.length + selectedText.length : newCursorPos
            );
        }, 0);
    };

    // Handle keyboard shortcuts
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 'b':
                    e.preventDefault();
                    insertText('**', '**');
                    break;
                case 'i':
                    e.preventDefault();
                    insertText('*', '*');
                    break;
                case 'k':
                    e.preventDefault();
                    insertText('[', '](url)');
                    break;
                case 'd':
                    e.preventDefault();
                    insertText('`', '`');
                    break;
            }
        }

        // Tab handling
        if (e.key === 'Tab') {
            e.preventDefault();
            insertText('    ');
        }
    };

    // Toolbar actions
    const toolbarActions = [
        { icon: Bold, action: () => insertText('**', '**'), title: 'Bold (Ctrl+B)' },
        { icon: Italic, action: () => insertText('*', '*'), title: 'Italic (Ctrl+I)' },
        { icon: Code, action: () => insertText('`', '`'), title: 'Inline Code (Ctrl+D)' },
        { type: 'divider' },
        { icon: Hash, action: () => insertText('## ', ''), title: 'Heading' },
        { icon: Link, action: () => insertText('[', '](url)'), title: 'Link (Ctrl+K)' },
        { icon: Image, action: () => insertText('![alt](', ')'), title: 'Image' },
        { type: 'divider' },
        { icon: List, action: () => insertText('- ', ''), title: 'Bullet List' },
        { icon: ListOrdered, action: () => insertText('1. ', ''), title: 'Numbered List' },
        { icon: Quote, action: () => insertText('> ', ''), title: 'Blockquote' },
        { type: 'divider' },
        { icon: Table, action: () => insertText('\n| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n', ''), title: 'Table' },
        { icon: Minus, action: () => insertText('\n---\n', ''), title: 'Horizontal Rule' },
    ];

    return (
        <div className={`flex flex-col h-full bg-[var(--bg-surface)] rounded-lg overflow-hidden ${className}`}>
            {/* ... toolbar ... */}
            <div className="flex items-center gap-1 px-3 py-2 border-b border-[var(--border-default)] bg-[var(--bg-elevated)] flex-wrap">
                {/* ... toolbar actions ... */}
                {toolbarActions.map((action, idx) => (
                    action.type === 'divider' ? (
                        <div key={idx} className="w-px h-5 bg-[var(--border-default)] mx-1" />
                    ) : (
                        <button
                            key={idx}
                            onClick={action.action}
                            className="p-1.5 rounded hover:bg-[var(--bg-hover)] text-secondary hover:text-primary transition-colors"
                            title={action.title}
                        >
                            {action.icon && <action.icon className="w-4 h-4" />}
                        </button>
                    )
                ))}
            </div>

            {/* Editor Area */}
            <div className="flex-1 flex overflow-hidden">
                {/* Line Numbers */}
                <div
                    ref={lineNumbersRef}
                    className="w-12 bg-[var(--bg-elevated)] border-r border-[var(--border-default)] overflow-hidden select-none shrink-0"
                >
                    <div className="py-4 text-right pr-3 font-mono text-xs text-tertiary leading-6">
                        {Array.from({ length: lineCount }, (_, i) => (
                            <div key={i + 1} className={cursorPosition.line === i + 1 ? 'text-primary font-medium' : ''}>
                                {i + 1}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Textarea */}
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onScroll={handleScroll}
                    onKeyDown={handleKeyDown}
                    onKeyUp={updateCursorPosition}
                    onClick={updateCursorPosition}
                    placeholder={placeholder}
                    className="flex-1 p-4 bg-transparent text-primary font-mono text-sm leading-6 resize-none focus:outline-none placeholder:text-tertiary"
                    spellCheck={false}
                />
            </div>

            {/* Status Bar */}
            <div className="flex items-center justify-between px-3 py-1.5 border-t border-[var(--border-default)] bg-[var(--bg-elevated)] text-xs text-tertiary">
                <div className="flex items-center gap-4">
                    <span>Ln {cursorPosition.line}, Col {cursorPosition.column}</span>
                    <span>{lineCount} lines</span>
                    <span>{value.length} characters</span>
                </div>
                <span>Markdown</span>
            </div>
        </div>
    );
};

// ... (DocumentViewer component start)

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
    // ... props
    content,
    className = '',
    initialPage = 1,
    onClose,
    onSave,
    title = 'Document',
    editable = true,
    showToolbar = true,
    fileUrl,
    fileType = 'text'
}) => {
    // ... state
    const [pages, setPages] = useState<Page[]>([]);
    const [currentPage, setCurrentPage] = useState(initialPage);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showSearch, setShowSearch] = useState(false);
    const [searchResults, setSearchResults] = useState<{ page: number; index: number }[]>([]);
    const [currentSearchIndex, setCurrentSearchIndex] = useState(0);
    const [fontSize, setFontSize] = useState(16);
    const [zoomLevel, setZoomLevel] = useState(100); // Added zoomLevel state
    const [showThumbnails, setShowThumbnails] = useState(false);
    const [showOutline, setShowOutline] = useState(false);
    const [bookmarks, setBookmarks] = useState<number[]>([]);
    const [viewMode, setViewMode] = useState<ViewMode>('preview');
    const [numPdfPages, setNumPdfPages] = useState<number | null>(null);
    const [isPdfLoaded, setIsPdfLoaded] = useState(false);

    function onPdfLoadSuccess({ numPages }: { numPages: number }) {
        setNumPdfPages(numPages);
        setIsPdfLoaded(true);
    }
    const [editedContent, setEditedContent] = useState(content);
    const [hasChanges, setHasChanges] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [copied, setCopied] = useState(false);

    // Helper for copy code
    const handleCopyCode = (code: string) => {
        // Optional: additional tracking or toast
    };

    // Derived state for current page content
    const activePageContent = useMemo(() => {
        const page = pages.find(p => p.number === currentPage);
        return page ? page.content : '';
    }, [pages, currentPage]);

    const currentPageContent = activePageContent; // Alias for consistency

    // Refs
    const containerRef = useRef<HTMLDivElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);
    const previewRef = useRef<HTMLDivElement>(null); // NEW REF

    // ... (rest of logic)

    // Scroll Sync Handler
    const handleEditorScroll = (e: React.UIEvent<HTMLTextAreaElement>) => {
        if (viewMode === 'split' && previewRef.current) {
            const textarea = e.currentTarget;
            const percentage = textarea.scrollTop / (textarea.scrollHeight - textarea.clientHeight);
            const preview = previewRef.current;
            preview.scrollTop = percentage * (preview.scrollHeight - preview.clientHeight);
        }
    };

    // Parse content into pages
    useEffect(() => {
        if (!content) {
            setPages([]);
            return;
        }

        setEditedContent(content);
        setHasChanges(false);

        const pageRegex = /(?:<!-*\s*Page\s+(\d+)\s*-*>|---\s*Page\s+(\d+)\s*---)/gi;
        const parts = content.split(pageRegex);
        const newPages: Page[] = [];

        if (parts.length > 1) {
            let currentPageNum = 0;

            for (let i = 0; i < parts.length; i++) {
                const part = parts[i];
                if (!part) continue;

                // Check if this part is a page number
                const pageNum = parseInt(part);
                if (!isNaN(pageNum) && pageNum > 0 && pageNum < 10000) {
                    currentPageNum = pageNum;
                    continue;
                }

                // This is content
                if (part.trim()) {
                    const effectivePageNum = currentPageNum || newPages.length + 1;
                    newPages.push({
                        number: effectivePageNum,
                        content: part.trim(),
                        preview: part.substring(0, 200).replace(/[#*`\[\]]/g, '').replace(/\n/g, ' ').trim() + '...'
                    });
                    currentPageNum = 0;
                }
            }
        }

        if (newPages.length === 0) {
            newPages.push({
                number: 1,
                content: content,
                preview: content.substring(0, 200).replace(/[#*`\[\]]/g, '').replace(/\n/g, ' ').trim() + '...'
            });
        }

        setPages(newPages);
        if (!newPages.some(p => p.number === currentPage)) {
            setCurrentPage(newPages[0]?.number || 1);
        }
    }, [content]);

    // Handle content changes
    const handleContentChange = useCallback((newContent: string) => {
        setEditedContent(newContent);
        setHasChanges(newContent !== content);
    }, [content]);

    // Save changes
    const handleSave = useCallback(async () => {
        if (!onSave || !hasChanges) return;

        setIsSaving(true);
        try {
            await onSave(editedContent);
            setHasChanges(false);
        } catch (error) {
            console.error('Save failed:', error);
        } finally {
            setIsSaving(false);
        }
    }, [editedContent, hasChanges, onSave]);

    // Search functionality
    useEffect(() => {
        if (!searchQuery.trim() || pages.length === 0) {
            setSearchResults([]);
            setCurrentSearchIndex(0);
            return;
        }

        const results: { page: number; index: number }[] = [];
        const query = searchQuery.toLowerCase();

        pages.forEach(page => {
            let searchContent = page.content.toLowerCase();
            let pos = searchContent.indexOf(query);
            while (pos !== -1) {
                results.push({ page: page.number, index: pos });
                pos = searchContent.indexOf(query, pos + 1);
            }
        });

        setSearchResults(results);
        if (results.length > 0) {
            const onCurrent = results.findIndex(r => r.page === currentPage);
            setCurrentSearchIndex(onCurrent !== -1 ? onCurrent : 0);
            if (onCurrent === -1 && results[0].page !== currentPage) {
                setCurrentPage(results[0].page);
            }
        }
    }, [searchQuery, pages, currentPage]);

    // Keyboard navigation
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
                // Allow Escape to work in inputs
                if (e.key === 'Escape') {
                    if (showSearch) setShowSearch(false);
                    return;
                }
                return;
            }

            switch (e.key) {
                case 'ArrowRight':
                case 'PageDown':
                    if (viewMode === 'preview') {
                        e.preventDefault();
                        nextPage();
                    }
                    break;
                case 'ArrowLeft':
                case 'PageUp':
                    if (viewMode === 'preview') {
                        e.preventDefault();
                        prevPage();
                    }
                    break;
                case 'Home':
                    if (viewMode === 'preview') {
                        e.preventDefault();
                        goToFirstPage();
                    }
                    break;
                case 'End':
                    if (viewMode === 'preview') {
                        e.preventDefault();
                        goToLastPage();
                    }
                    break;
                case 'Escape':
                    if (isFullScreen) setIsFullScreen(false);
                    else if (showSearch) setShowSearch(false);
                    break;
                case 'f':
                case 'F':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        setShowSearch(true);
                        setTimeout(() => searchInputRef.current?.focus(), 100);
                    }
                    break;
                case 's':
                case 'S':
                    if ((e.ctrlKey || e.metaKey) && hasChanges) {
                        e.preventDefault();
                        handleSave();
                    }
                    break;
                case '+':
                case '=':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        zoomIn();
                    }
                    break;
                case '-':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        zoomOut();
                    }
                    break;
                case 'e':
                case 'E':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        setViewMode(viewMode === 'edit' ? 'preview' : 'edit');
                    }
                    break;
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentPage, pages, isFullScreen, showSearch, viewMode, hasChanges]);

    // Navigation handlers
    const nextPage = useCallback(() => {
        const currIdx = pages.findIndex(p => p.number === currentPage);
        if (currIdx < pages.length - 1) {
            setCurrentPage(pages[currIdx + 1].number);
        }
    }, [currentPage, pages]);

    const prevPage = useCallback(() => {
        const currIdx = pages.findIndex(p => p.number === currentPage);
        if (currIdx > 0) {
            setCurrentPage(pages[currIdx - 1].number);
        }
    }, [currentPage, pages]);

    const goToFirstPage = () => pages.length > 0 && setCurrentPage(pages[0].number);
    const goToLastPage = () => pages.length > 0 && setCurrentPage(pages[pages.length - 1].number);
    const goToPage = (pageNum: number) => pages.some(p => p.number === pageNum) && setCurrentPage(pageNum);

    const zoomIn = () => setFontSize(Math.min(32, fontSize + 2));
    const zoomOut = () => setFontSize(Math.max(10, fontSize - 2));
    const resetZoom = () => setFontSize(16);

    const jumpToSearch = (direction: 'next' | 'prev') => {
        if (searchResults.length === 0) return;

        let newIndex = direction === 'next' ? currentSearchIndex + 1 : currentSearchIndex - 1;
        if (newIndex >= searchResults.length) newIndex = 0;
        if (newIndex < 0) newIndex = searchResults.length - 1;

        setCurrentSearchIndex(newIndex);
        const result = searchResults[newIndex];
        if (result.page !== currentPage) {
            setCurrentPage(result.page);
        }
    };

    const toggleBookmark = () => {
        if (bookmarks.includes(currentPage)) {
            setBookmarks(bookmarks.filter(b => b !== currentPage));
        } else {
            setBookmarks([...bookmarks, currentPage].sort((a, b) => a - b));
        }
    };

    const copyContent = async () => {
        const contentToCopy = viewMode === 'edit' ? editedContent : (pages.find(p => p.number === currentPage)?.content || '');
        await navigator.clipboard.writeText(contentToCopy);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // Derived values
    // activePageContent is already defined above
    const currentIdx = pages.findIndex(p => p.number === currentPage);
    const totalPages = pages.length;
    const maxPage = pages[pages.length - 1]?.number || 1;
    const isBookmarked = bookmarks.includes(currentPage);

    // Fullscreen handling
    useEffect(() => {
        if (isFullScreen) {
            containerRef.current?.requestFullscreen?.().catch(() => { });
        } else if (document.fullscreenElement) {
            document.exitFullscreen?.().catch(() => { });
        }
    }, [isFullScreen]);

    // View mode icons - only Preview and Split now
    const viewModeConfig = {
        preview: { icon: Eye, label: 'Preview' },
        split: { icon: Columns, label: 'Edit' },
        pdf: { icon: FileText, label: 'PDF' }
    };

    return (
        <div
            ref={containerRef}
            className={`flex flex-col bg-[var(--bg-base)] overflow-hidden transition-all duration-300 ${isFullScreen
                ? 'fixed inset-0 z-[100]'
                : 'h-full rounded-xl border border-[var(--border-default)] ' + className
                }`}
        >
            {/* Top Toolbar */}
            {showToolbar && (
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-[var(--border-default)] bg-[var(--bg-elevated)] backdrop-blur-xl shrink-0">
                    {/* Left Section */}
                    <div className="flex items-center gap-1">
                        {/* Thumbnails Toggle */}
                        <button
                            onClick={() => setShowThumbnails(!showThumbnails)}
                            className={`btn-icon ${showThumbnails ? 'bg-[var(--accent-primary)]/20 text-[var(--accent-primary)]' : ''}`}
                            title="Toggle Pages Panel"
                        >
                            <Grid3X3 className="w-4 h-4" />
                        </button>

                        <div className="w-px h-5 bg-[var(--border-default)] mx-1" />

                        {/* Page Navigation (only in preview mode) */}
                        {viewMode !== 'edit' && (
                            <>
                                <button onClick={goToFirstPage} disabled={currentIdx <= 0} className="btn-icon disabled:opacity-30" title="First Page">
                                    <ChevronsLeft className="w-4 h-4" />
                                </button>
                                <button onClick={prevPage} disabled={currentIdx <= 0} className="btn-icon disabled:opacity-30" title="Previous Page">
                                    <ChevronLeft className="w-5 h-5" />
                                </button>

                                <div className="flex items-center gap-2 bg-[var(--bg-surface)] px-3 py-1.5 rounded-lg border border-[var(--border-default)] mx-1">
                                    <input
                                        type="number"
                                        value={currentPage}
                                        min={1}
                                        max={maxPage}
                                        onChange={(e) => {
                                            const val = parseInt(e.target.value);
                                            if (!isNaN(val)) goToPage(val);
                                        }}
                                        className="w-10 bg-transparent text-center font-mono text-primary text-sm focus:outline-none"
                                    />
                                    <span className="text-tertiary">/</span>
                                    <span className="text-sm text-tertiary font-mono">{maxPage}</span>
                                </div>

                                <button onClick={nextPage} disabled={currentIdx >= totalPages - 1} className="btn-icon disabled:opacity-30" title="Next Page">
                                    <ChevronRight className="w-5 h-5" />
                                </button>
                                <button onClick={goToLastPage} disabled={currentIdx >= totalPages - 1} className="btn-icon disabled:opacity-30" title="Last Page">
                                    <ChevronsRight className="w-4 h-4" />
                                </button>

                                <div className="w-px h-5 bg-[var(--border-default)] mx-1" />
                            </>
                        )}

                        {/* View Mode Toggle */}
                        {editable && (
                            <div className="flex items-center bg-[var(--bg-surface)] rounded-lg border border-[var(--border-default)] p-0.5">
                                {(['preview', 'split'] as ViewMode[]).map((mode) => {
                                    const config = viewModeConfig[mode as keyof typeof viewModeConfig];
                                    if (!config) return null;
                                    const Icon = config.icon;
                                    return (
                                        <button
                                            key={mode}
                                            onClick={() => startTransition(() => setViewMode(mode))}
                                            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all duration-150 ${viewMode === mode
                                                ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                                                : 'text-tertiary hover:text-primary hover:bg-[var(--bg-hover)]'
                                                }`}
                                            title={config.label}
                                        >
                                            <Icon className="w-3.5 h-3.5" />
                                            <span className="hidden sm:inline">{config.label}</span>
                                        </button>
                                    );
                                })}

                                {/* PDF Mode with Spacer */}
                                {fileUrl && (
                                    <>
                                        <div className="w-px h-4 bg-[var(--border-default)] mx-1" />
                                        <button
                                            onClick={() => startTransition(() => setViewMode('pdf'))}
                                            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all duration-150 ${viewMode === 'pdf'
                                                ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                                                : 'text-tertiary hover:text-primary hover:bg-[var(--bg-hover)]'
                                                }`}
                                            title="View Original PDF"
                                        >
                                            <FileText className="w-3.5 h-3.5" />
                                            <span className="hidden sm:inline">PDF</span>
                                        </button>
                                    </>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Center - Title & Status */}
                    <div className="absolute left-1/2 transform -translate-x-1/2 hidden lg:flex items-center gap-2">
                        <FileText className="w-4 h-4 text-tertiary" />
                        <h2 className="text-sm font-medium text-primary truncate max-w-[200px]">{title}</h2>
                        {hasChanges && (
                            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" title="Unsaved changes" />
                        )}
                    </div>

                    {/* Right Section */}
                    <div className="flex items-center gap-1">
                        {/* Search */}
                        <div className={`flex items-center overflow-hidden transition-all duration-300 ${showSearch ? 'w-64 opacity-100' : 'w-0 opacity-0'}`}>
                            <div className="flex items-center bg-[var(--bg-surface)] rounded-lg border border-[var(--border-default)] px-3 py-1.5 mx-2 flex-1 gap-2">
                                <Search className="w-4 h-4 text-tertiary shrink-0" />
                                <input
                                    ref={searchInputRef}
                                    type="text"
                                    placeholder="Find..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="bg-transparent border-none outline-none text-sm w-full text-primary"
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') jumpToSearch(e.shiftKey ? 'prev' : 'next');
                                        if (e.key === 'Escape') setShowSearch(false);
                                    }}
                                />
                                {searchResults.length > 0 && (
                                    <div className="flex items-center gap-1 pl-2 border-l border-[var(--border-default)] shrink-0">
                                        <span className="text-xs text-tertiary font-mono">
                                            {currentSearchIndex + 1}/{searchResults.length}
                                        </span>
                                        <button onClick={() => jumpToSearch('prev')} className="btn-icon !p-1"><ArrowUp className="w-3 h-3" /></button>
                                        <button onClick={() => jumpToSearch('next')} className="btn-icon !p-1"><ArrowDown className="w-3 h-3" /></button>
                                    </div>
                                )}
                            </div>
                        </div>

                        <button
                            onClick={() => { setShowSearch(!showSearch); if (!showSearch) setTimeout(() => searchInputRef.current?.focus(), 100); }}
                            className={`btn-icon ${showSearch ? 'bg-[var(--accent-primary)]/20 text-[var(--accent-primary)]' : ''}`}
                            title="Search (Ctrl+F)"
                        >
                            <Search className="w-4 h-4" />
                        </button>

                        <div className="w-px h-5 bg-[var(--border-default)] mx-1" />

                        {/* Zoom */}
                        <button onClick={zoomOut} className="btn-icon" title="Zoom Out"><ZoomOut className="w-4 h-4" /></button>
                        <button onClick={resetZoom} className="px-2 py-1 text-xs text-tertiary hover:text-primary rounded font-mono" title="Reset Zoom">
                            {Math.round((fontSize / 16) * 100)}%
                        </button>
                        <button onClick={zoomIn} className="btn-icon" title="Zoom In"><ZoomIn className="w-4 h-4" /></button>

                        <div className="w-px h-5 bg-[var(--border-default)] mx-1" />

                        {/* Actions */}
                        <button onClick={copyContent} className="btn-icon" title="Copy Content">
                            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                        </button>

                        <button onClick={toggleBookmark} className={`btn-icon ${isBookmarked ? 'text-yellow-500' : ''}`} title="Bookmark">
                            <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
                        </button>

                        {/* Save Button */}
                        {editable && onSave && (
                            <button
                                onClick={handleSave}
                                disabled={!hasChanges || isSaving}
                                className={`btn-icon ${hasChanges ? 'text-[var(--accent-primary)]' : 'opacity-50'}`}
                                title="Save (Ctrl+S)"
                            >
                                {isSaving ? (
                                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <Save className="w-4 h-4" />
                                )}
                            </button>
                        )}

                        <button onClick={() => setIsFullScreen(!isFullScreen)} className="btn-icon" title="Fullscreen">
                            {isFullScreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                        </button>

                        {onClose && (
                            <>
                                <div className="w-px h-5 bg-[var(--border-default)] mx-1" />
                                <button onClick={onClose} className="btn-icon text-red-400 hover:bg-red-500/20" title="Close">
                                    <X className="w-4 h-4" />
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            <div className="flex flex-1 overflow-hidden">
                {/* Pages Sidebar */}
                <div className={`bg-[var(--bg-elevated)] border-r border-[var(--border-default)] overflow-hidden transition-all duration-300 shrink-0 ${showThumbnails ? 'w-56' : 'w-0'}`}>
                    <div className="h-full flex flex-col">
                        <div className="px-3 py-2 border-b border-[var(--border-default)]">
                            <h3 className="text-xs font-semibold uppercase tracking-wider text-tertiary">Pages</h3>
                        </div>
                        <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
                            {pages.map((page) => (
                                <button
                                    key={page.number}
                                    onClick={() => { setCurrentPage(page.number); setViewMode('preview'); }}
                                    className={`w-full text-left p-3 rounded-lg border transition-all ${currentPage === page.number
                                        ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 shadow-sm'
                                        : 'border-[var(--border-default)] hover:border-[var(--border-strong)] hover:bg-[var(--bg-hover)]'
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-1.5">
                                        <span className="text-xs font-mono font-medium text-secondary">Page {page.number}</span>
                                        {bookmarks.includes(page.number) && (
                                            <Bookmark className="w-3 h-3 text-yellow-500 fill-current" />
                                        )}
                                    </div>
                                    <div className="text-[11px] text-tertiary line-clamp-3 leading-relaxed">
                                        {page.preview}
                                    </div>
                                </button>
                            ))}
                        </div>

                        {/* Bookmarks Section */}
                        {bookmarks.length > 0 && (
                            <div className="border-t border-[var(--border-default)]">
                                <div className="px-3 py-2">
                                    <h3 className="text-xs font-semibold uppercase tracking-wider text-tertiary flex items-center gap-1.5">
                                        <Bookmark className="w-3 h-3" />
                                        Bookmarks
                                    </h3>
                                </div>
                                <div className="px-2 pb-2 space-y-1 max-h-32 overflow-y-auto">
                                    {bookmarks.map((pageNum) => (
                                        <button
                                            key={pageNum}
                                            onClick={() => setCurrentPage(pageNum)}
                                            className={`w-full text-left px-2 py-1 rounded text-xs transition-colors ${currentPage === pageNum
                                                ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400'
                                                : 'text-secondary hover:bg-[var(--bg-hover)]'
                                                }`}
                                        >
                                            Page {pageNum}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Content Area - Always render both panels, use CSS for visibility */}
                {/* Content Area - Always render both panels, use CSS for visibility */}
                <div ref={contentRef} className="flex-1 flex overflow-hidden bg-[var(--bg-subtle)]">

                    {/* PDF Full View Mode */}
                    {viewMode === 'pdf' && fileUrl ? (
                        <div className="flex-1 bg-gray-100 dark:bg-slate-900 overflow-y-auto flex justify-center p-4 relative">
                            <Document
                                file={fileUrl}
                                onLoadSuccess={onPdfLoadSuccess}
                                loading={<div className="absolute inset-0 flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>}
                                className="shadow-xl"
                            >
                                <PdfPage
                                    pageNumber={currentPage}
                                    scale={zoomLevel / 100}
                                    renderTextLayer={false}
                                    renderAnnotationLayer={false}
                                    className="shadow-lg mb-4"
                                />
                            </Document>
                        </div>
                    ) : (

                        /* Standard Editor Split View (Original Logic) */
                        <>
                            <div
                                className={`flex flex-col transition-all duration-300 ease-out overflow-hidden ${viewMode === 'split'
                                    ? 'w-1/2 opacity-100 border-r border-[var(--border-default)]'
                                    : 'w-0 opacity-0'
                                    }`}
                                style={{ willChange: 'width, opacity' }}
                            >
                                {viewMode === 'split' && (
                                    <MarkdownEditor
                                        value={editedContent}
                                        onChange={handleContentChange}
                                        className="flex-1"
                                        onScroll={handleEditorScroll}
                                    />
                                )}
                            </div>

                            {/* Preview Panel - always visible */}
                            <div
                                ref={previewRef}
                                className={`overflow-y-auto custom-scrollbar transition-all duration-300 ease-out ${viewMode === 'split' ? 'w-1/2' : 'flex-1'
                                    }`}
                                style={{ willChange: 'width' }}
                            >
                                <div className="min-h-full flex items-start justify-center p-4 sm:p-8 lg:p-12">
                                    <div
                                        className="w-full max-w-4xl bg-white dark:bg-[var(--bg-surface)] shadow-xl rounded-xl transition-all duration-300 relative overflow-hidden"
                                        style={{ fontSize: `${fontSize}px` }}
                                    >
                                        {/* Document Header */}
                                        <div className="sticky top-0 z-10 flex justify-between items-center px-6 sm:px-8 py-3 border-b border-[var(--border-weak)] bg-white/90 dark:bg-[var(--bg-surface)]/90 backdrop-blur-sm">
                                            <div className="flex items-center gap-3">
                                                <div className="w-2 h-2 rounded-full bg-[var(--accent-primary)]" />
                                                <span className="text-xs font-semibold uppercase tracking-widest text-[var(--accent-primary)]">
                                                    {title}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                {isBookmarked && <Bookmark className="w-4 h-4 text-yellow-500 fill-current" />}
                                                {viewMode !== 'edit' && (
                                                    <span className="text-xs text-tertiary font-mono">
                                                        Page {currentPage} of {maxPage}
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        {/* Document Content */}
                                        <div className="px-6 sm:px-8 md:px-12 py-8 md:py-10 min-h-[60vh]">
                                            <MarkdownRenderer
                                                content={viewMode === 'split' ? editedContent : activePageContent}
                                                searchQuery={searchQuery}
                                                className="prose prose-lg dark:prose-invert max-w-none"
                                            />
                                        </div>

                                        {/* Document Footer */}
                                        <div className="px-6 sm:px-8 py-3 border-t border-[var(--border-weak)] bg-[var(--bg-subtle)]/50 flex justify-between items-center text-xs text-tertiary">
                                            <span>{title}</span>
                                            {viewMode !== 'edit' && (
                                                <span className="font-mono">{currentPage} / {maxPage}</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Mobile Bottom Navigation */}
                {viewMode === 'preview' && (
                    <div className="sm:hidden flex items-center justify-between px-4 py-3 border-t border-[var(--border-default)] bg-[var(--bg-elevated)] shrink-0">
                        <button onClick={prevPage} disabled={currentIdx <= 0} className="btn-icon disabled:opacity-30">
                            <ChevronLeft className="w-6 h-6" />
                        </button>
                        <div className="flex items-center gap-2">
                            <span className="text-sm font-mono text-primary">{currentPage}</span>
                            <span className="text-tertiary">/</span>
                            <span className="text-sm font-mono text-tertiary">{maxPage}</span>
                        </div>
                        <button onClick={nextPage} disabled={currentIdx >= totalPages - 1} className="btn-icon disabled:opacity-30">
                            <ChevronRight className="w-6 h-6" />
                        </button>
                    </div>
                )}

                {/* Unsaved Changes Indicator */}
                {hasChanges && (
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-amber-500/90 text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg flex items-center gap-2 z-50">
                        <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
                        Unsaved changes
                        <button
                            onClick={handleSave}
                            className="ml-2 bg-white/20 hover:bg-white/30 px-2 py-0.5 rounded text-xs font-semibold transition-colors"
                        >
                            Save
                        </button>
                    </div>
                )}
            </div>

        </div>
    );
};

// Button style helper (add to your global CSS or component)
const buttonStyles = `
            .btn-icon {
                @apply p-2 rounded-lg text-secondary hover:text-primary hover:bg-[var(--bg-hover)] transition-colors disabled:opacity-30 disabled:cursor-not-allowed;
    }
            `;

export default DocumentViewer;