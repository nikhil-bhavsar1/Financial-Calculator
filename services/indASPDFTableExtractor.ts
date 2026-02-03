/**
 * IndASPDFTableExtractor
 * Enhanced table extraction for Ind AS specific PDF formats
 * Handles Indian financial statement table structures and formats
 */

export interface IndASTable {
  type: 'balance_sheet' | 'profit_loss' | 'cash_flow' | 'equity_changes' | 'unknown';
  periods: Record<number, string>;
  rows: IndASTableRow[];
  rawHeaders: string[];
  numericColumns: number[];
  noteReferenceColumn?: number;
  confidence: number;
}

export interface IndASTableRow {
  lineItem: string;
  metricKey?: string;
  isHeader: boolean;
  isTotal: boolean;
  isSubTotal: boolean;
  values: Record<string, number>;
  indentLevel: number;
  noteReference?: string;
}

export class IndASPDFTableExtractor {
  // Ind AS specific table indicators
  private static readonly IND_AS_TABLE_INDICATORS = [
    'particulars',
    'note',
    'amount',
    'rs.',
    '₹',
    'current year',
    'previous year',
    'as at',
    'for the year ended'
  ];

  // Table type detection patterns
  private static readonly TABLE_TYPE_PATTERNS = {
    balance_sheet: [
      'balance sheet',
      'statement of financial position',
      'statement of assets and liabilities',
      'assets', 'liabilities', 'equity'
    ],
    profit_loss: [
      'profit and loss',
      'statement of profit and loss',
      'statement of profit or loss',
      'income statement',
      'profit & loss'
    ],
    cash_flow: [
      'cash flow statement',
      'statement of cash flows',
      'cash flow'
    ],
    equity_changes: [
      'statement of changes in equity',
      'statement of changes in shareholders\' equity'
    ]
  };

  /**
   * Extract Ind AS specific table structure
   */
  static extractIndASTable(headers: string[], rows: string[][]): IndASTable | null {
    // Check if it's a financial table
    if (!this.isFinancialTable(headers, rows)) {
      return null;
    }

    const table: IndASTable = {
      type: 'unknown',
      periods: {},
      rows: [],
      rawHeaders: headers,
      numericColumns: [],
      noteReferenceColumn: undefined,
      confidence: 0
    };

    // Detect table type
    table.type = this.detectTableType(headers, rows);
    table.confidence += 0.2;

    // Extract periods from headers
    table.periods = this.extractPeriods(headers);
    table.confidence += Object.keys(table.periods).length > 0 ? 0.2 : 0;

    // Identify numeric columns
    table.numericColumns = this.identifyNumericColumns(rows);
    table.confidence += table.numericColumns.length > 0 ? 0.2 : 0;

    // Identify note reference column
    table.noteReferenceColumn = this.identifyNoteReferenceColumn(rows, headers);
    if (table.noteReferenceColumn !== undefined) {
      table.confidence += 0.1;
    }

    // Extract data rows with Ind AS awareness
    table.rows = this.extractTableRows(rows, table);
    table.confidence += table.rows.length > 0 ? 0.3 : 0;

    return table;
  }

  /**
   * Check if table contains financial data (not narrative)
   */
  private static isFinancialTable(headers: string[], rows: string[][]): boolean {
    // Check for numeric ratio
    const numericRatio = this.getNumericRatio(rows);

    // Check for financial keywords
    const financialScore = this.getFinancialKeywordScore(headers, rows);

    return numericRatio > 0.3 && financialScore >= 2;
  }

  /**
   * Calculate ratio of numeric cells in table
   */
  private static getNumericRatio(rows: string[][]): number {
    if (rows.length === 0) return 0;

    let numericCells = 0;
    let totalCells = 0;

    for (const row of rows.slice(0, 10)) { // Check first 10 rows
      for (const cell of row) {
        if (cell && cell.trim()) {
          totalCells++;
          if (this.isNumericCell(cell)) {
            numericCells++;
          }
        }
      }
    }

    return totalCells > 0 ? numericCells / totalCells : 0;
  }

  /**
   * Check if cell contains numeric data
   */
  private static isNumericCell(cell: string): boolean {
    const cleaned = cell.trim().replace(/[,\s]/g, '');
    return !isNaN(parseFloat(cleaned)) || /^\(.*\)$/.test(cleaned);
  }

  /**
   * Calculate financial keyword score
   */
  private static getFinancialKeywordScore(headers: string[], rows: string[][]): number {
    const allText = [...headers, ...rows.flat()].join(' ').toLowerCase();

    return this.IND_AS_TABLE_INDICATORS.filter(indicator =>
      allText.includes(indicator)
    ).length;
  }

  /**
   * Detect table type
   */
  private static detectTableType(headers: string[], rows: string[][]): IndASTable['type'] {
    const allText = [...headers, ...rows.flat()].join(' ').toLowerCase();

    for (const [type, patterns] of Object.entries(this.TABLE_TYPE_PATTERNS)) {
      for (const pattern of patterns) {
        if (allText.includes(pattern)) {
          return type as IndASTable['type'];
        }
      }
    }

    return 'unknown';
  }

  /**
   * Extract periods from headers
   */
  private static extractPeriods(headers: string[]): Record<number, string> {
    const periods: Record<number, string> = {};

    for (let i = 0; i < headers.length; i++) {
      const header = headers[i].toLowerCase();

      // Look for year patterns
      const yearMatch = header.match(/20\d{2}/);
      if (yearMatch && yearMatch.length > 0) {
        periods[i] = yearMatch[0];
        continue;
      }

      // Look for period keywords
      if (header.includes('current') && header.includes('year')) {
        periods[i] = 'current';
      } else if (header.includes('previous') && header.includes('year')) {
        periods[i] = 'previous';
      }
    }

    return periods;
  }

  /**
   * Identify numeric columns
   */
  private static identifyNumericColumns(rows: string[][]): number[] {
    const numericColumns: number[] = [];

    if (rows.length === 0) return numericColumns;

    const sampleRows = rows.slice(0, 10);
    const numCols = sampleRows[0]?.length || 0;

    for (let col = 0; col < numCols; col++) {
      let numericCount = 0;

      for (const row of sampleRows) {
        if (row[col] && this.isNumericCell(row[col])) {
          numericCount++;
        }
      }

      if (numericCount / sampleRows.length > 0.5) {
        numericColumns.push(col);
      }
    }

    return numericColumns;
  }

  /**
   * Identify note reference column
   */
  private static identifyNoteReferenceColumn(rows: string[][], headers: string[]): number | undefined {
    // Check if first column is note references
    for (let col = 0; col < (headers.length || 5); col++) {
      let noteCount = 0;
      let nonNoteCount = 0;

      for (const row of rows.slice(0, 10)) {
        const cell = row[col]?.trim();
        if (!cell) continue;

        if (/^\d+$/.test(cell) && parseInt(cell) < 100) {
          noteCount++;
        } else {
          nonNoteCount++;
        }
      }

      if (noteCount > nonNoteCount && noteCount > 3) {
        return col;
      }
    }

    return undefined;
  }

  /**
   * Extract table rows with Ind AS awareness
   */
  private static extractTableRows(rows: string[][], table: IndASTable): IndASTableRow[] {
    const tableRows: IndASTableRow[] = [];

    for (const row of rows) {
      const tableRow = this.parseIndASRow(row, table);
      if (tableRow) {
        tableRows.push(tableRow);
      }
    }

    return tableRows;
  }

  /**
   * Parse a single row with Ind AS specific logic
   */
  private static parseIndASRow(row: string[], table: IndASTable): IndASTableRow | null {
    if (row.length === 0) return null;

    const lineItem = row[0]?.trim() || '';
    if (!lineItem) return null;

    const tableRow: IndASTableRow = {
      lineItem,
      isHeader: this.isHeaderRow(lineItem),
      isTotal: this.isTotalRow(lineItem),
      isSubTotal: this.isSubTotalRow(lineItem),
      values: {},
      indentLevel: this.getIndentLevel(lineItem),
      noteReference: this.extractNoteReference(row, table.noteReferenceColumn)
    };

    // Match to canonical metric
    const metricMatch = this.matchIndASTerm(lineItem);
    if (metricMatch) {
      tableRow.metricKey = metricMatch.key;
    }

    // Extract values for each period column
    for (const [colIdx, period] of Object.entries(table.periods)) {
      const colIndex = parseInt(colIdx);
      if (colIndex < row.length && table.numericColumns.includes(colIndex)) {
        const value = this.parseIndianNumber(row[colIndex]);
        if (value !== null) {
          tableRow.values[period] = value;
        }
      }
    }

    return tableRow;
  }

  /**
   * Check if row is a header row
   */
  private static isHeaderRow(lineItem: string): boolean {
    const lowerItem = lineItem.toLowerCase();
    const headerIndicators = ['particulars', 'note', 'amount', 'rs.', 'total', 'assets', 'liabilities', 'equity'];
    return headerIndicators.some(indicator => lowerItem.includes(indicator));
  }

  /**
   * Check if row is a total row
   */
  private static isTotalRow(lineItem: string): boolean {
    const lowerItem = lineItem.toLowerCase();
    const totalIndicators = ['total', 'grand total', 'net', 'overall'];
    return totalIndicators.some(indicator => lowerItem.includes(indicator) && !lowerItem.includes('subtotal'));
  }

  /**
   * Check if row is a subtotal row
   */
  private static isSubTotalRow(lineItem: string): boolean {
    const lowerItem = lineItem.toLowerCase();
    return lowerItem.includes('subtotal');
  }

  /**
   * Get indent level of a line item
   */
  private static getIndentLevel(lineItem: string): number {
    const leadingSpaces = lineItem.search(/\S|$/);
    return Math.floor(leadingSpaces / 2); // Assuming 2 spaces per indent level
  }

  /**
   * Extract note reference from row
   */
  private static extractNoteReference(row: string[], noteRefColumn?: number): string | undefined {
    if (noteRefColumn === undefined || noteRefColumn >= row.length) {
      return undefined;
    }

    const cell = row[noteRefColumn]?.trim();
    if (cell && /^\d+$/.test(cell) && parseInt(cell) < 100) {
      return cell;
    }

    return undefined;
  }

  /**
   * Match Ind AS term to canonical metric
   */
  private static matchIndASTerm(lineItem: string): { key: string; confidence: number } | null {
    const cleaned = this.preprocessIndASLabel(lineItem);

    // This would use the terminology matching engine
    // For now, return null
    // In real implementation:
    // const match = matchingEngine.match(cleaned);
    // if (match && match.confidence > 0.7) {
    //   return { key: match.termKey, confidence: match.confidence };
    // }

    return null;
  }

  /**
   * Preprocess Ind AS specific label
   */
  private static preprocessIndASLabel(label: string): string {
    let cleaned = label.toLowerCase();

    // Remove common prefixes
    const prefixes = ['as at ', 'as on ', 'for the year ', 'for the period '];
    for (const prefix of prefixes) {
      if (cleaned.startsWith(prefix)) {
        cleaned = cleaned.substring(prefix.length);
      }
    }

    // Remove note references (1), (2), etc.
    cleaned = cleaned.replace(/\s*\(\d+\)\s*/g, ' ');

    // Standardize Ind AS specific terms
    const replacements: Record<string, string> = {
      'sundry creditors': 'trade payables',
      'sundry debtors': 'trade receivables',
      'cwip': 'capital work in progress',
      'reserves & surplus': 'other equity',
      'reserves and surplus': 'other equity',
      'capital work in progress': 'capital_work_in_progress',
      'current maturities of long term debt': 'current_maturities_long_term_debt'
    };

    for (const [old, newTerm] of Object.entries(replacements)) {
      cleaned = cleaned.replace(old, newTerm);
    }

    return cleaned.trim();
  }

  /**
   * Parse Indian number format
   */
  private static parseIndianNumber(value: string | undefined): number | null {
    if (!value) return null;

    const cleaned = value.trim();

    // Check for parentheses (negative in Ind AS)
    if (cleaned.startsWith('(') && cleaned.endsWith(')')) {
      const inner = cleaned.substring(1, cleaned.length - 1).replace(/,/g, '');
      const num = parseFloat(inner);
      return isNaN(num) ? null : -num;
    }

    // Check for "Less:" prefix (negative in Ind AS)
    if (cleaned.toLowerCase().startsWith('less:')) {
      const afterLess = cleaned.substring(5).trim().replace(/,/g, '');
      const num = parseFloat(afterLess);
      return isNaN(num) ? null : -num;
    }

    // Standard parsing
    const num = parseFloat(cleaned.replace(/,/g, ''));
    return isNaN(num) ? null : num;
  }

  /**
   * Extract multiple tables from document
   */
  static extractAllTables(allTables: Array<{ headers: string[]; rows: string[][] }>): IndASTable[] {
    const indASTables: IndASTable[] = [];

    for (const table of allTables) {
      const indASTable = this.extractIndASTable(table.headers, table.rows);
      if (indASTable) {
        indASTables.push(indASTable);
      }
    }

    return indASTables;
  }
}

export default IndASPDFTableExtractor;