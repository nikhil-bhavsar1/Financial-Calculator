/**
 * IndASStructureRecognizer
 * Recognize Ind AS specific statement formats and structures
 * Handles Indian Accounting Standards specific financial statement layouts
 */

export interface StatementStructure {
  type: 'balance_sheet' | 'profit_loss' | 'cash_flow' | 'equity_changes' | 'unknown';
  isIndAS: boolean;
  isStandalone: boolean;
  isConsolidated: boolean;
  period: {
    current?: string;
    previous?: string;
  };
  format: 'indian' | 'international' | 'mixed';
  confidence: number;
}

export interface TableStructure {
  isFinancialTable: boolean;
  tableType?: StatementStructure['type'];
  periodColumns: string[];
  valueColumns: number[];
  noteReferenceColumn?: number;
  hasIndASHeaders: boolean;
  confidence: number;
}

export class IndASStructureRecognizer {
  // Ind AS specific statement headers
  private static readonly IND_AS_HEADERS = {
    balance_sheet: [
      'statement of financial position',
      'balance sheet',
      'statement of assets and liabilities',
      'ind-as-1',  // XBRL tag reference
      'balance sheet as at',
      'statement of financial position as at'
    ],
    profit_loss: [
      'statement of profit and loss',
      'statement of profit or loss',
      'statement of profit and loss and other comprehensive income',
      'ind-as-1-proft-and-loss',
      'profit and loss account',
      'statement of profit & loss'
    ],
    cash_flow: [
      'statement of cash flows',
      'cash flow statement',
      'ind-as-7',
      'statement of cash flow'
    ],
    equity_changes: [
      'statement of changes in equity',
      'statement of changes in shareholders fund',
      'ind-as-1-changes-in-equity',
      'statement of changes in shareholders\' equity'
    ]
  };

  // Ind AS specific indicators in document text
  private static readonly IND_AS_INDICATORS = [
    'ind as',
    'indian accounting standards',
    'ind-as',
    'notes to the standalone financial statements',
    'notes to the consolidated financial statements',
    'in accordance with indian accounting standards',
    'reserves and surplus',  // Strong indicator
    'sundry creditors',     // Strong indicator
    'sundry debtors',       // Strong indicator
    'capital work in progress',  // Strong indicator
    'cwip',
    'sundry',
    'other comprehensive income',
    'statement of changes in equity',
    'property plant and equipment'
  ];

  // Period format patterns (Indian specific)
  private static readonly INDIAN_PERIOD_PATTERNS = [
    /(\d{1,2})\.(\d{1,2})\.(\d{4})/,  // 31.03.2023
    /(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})/,  // 31-03-2023
    /as\s+at\s+(\d{1,2}[-\.\/]\d{1,2}[-\.\/]\d{4})/i,
    /for\s+the\s+year\s+ended\s+(\d{1,2}[-\.\/]\d{1,2}[-\.\/]\d{4})/i,
    /as\s+on\s+(\d{1,2}[-\.\/]\d{1,2}[-\.\/]\d{4})/i
  ];

  /**
   * Detect if document follows Ind AS standards
   */
  static isIndASFiling(textContent: string): boolean {
    const textLower = textContent.toLowerCase();
    const score = this.IND_AS_INDICATORS.filter(indicator =>
      textLower.includes(indicator)
    ).length;

    return score >= 2;  // At least 2 indicators
  }

  /**
   * Determine document type and structure
   */
  static recognizeStructure(textContent: string): StatementStructure {
    const textLower = textContent.toLowerCase();
    const structure: StatementStructure = {
      type: 'unknown',
      isIndAS: false,
      isStandalone: false,
      isConsolidated: false,
      period: { current: undefined, previous: undefined },
      format: 'international',
      confidence: 0
    };

    // Check if it's Ind AS
    structure.isIndAS = this.isIndASFiling(textContent);
    if (structure.isIndAS) {
      structure.format = 'indian';
      structure.confidence += 0.3;
    }

    // Detect standalone vs consolidated
    const standalonePatterns = [
      'standalone\\s+(?:financial\\s+statements|balance\\s+sheet|profit\\s+and\\s+loss)',
      'stand-alone'
    ];
    const consolidatedPatterns = [
      'consolidated\\s+(?:financial\\s+statements|balance\\s+sheet|profit\\s+and\\s+loss)',
      'consolidation'
    ];

    const hasStandalone = this.matchPatterns(textLower, standalonePatterns);
    const hasConsolidated = this.matchPatterns(textLower, consolidatedPatterns);

    structure.isStandalone = hasStandalone;
    structure.isConsolidated = hasConsolidated;

    if (hasStandalone || hasConsolidated) {
      structure.confidence += 0.2;
    }

    // Detect statement type
    for (const [type, headers] of Object.entries(this.IND_AS_HEADERS)) {
      for (const header of headers) {
        if (textLower.includes(header)) {
          structure.type = type as StatementStructure['type'];
          structure.confidence += 0.5 / headers.length;
          break;
        }
      }
      if (structure.type !== 'unknown') break;
    }

    // Extract periods
    structure.period = this.extractPeriods(textContent);

    return structure;
  }

  /**
   * Detect standalone vs consolidated in document
   */
  static extractStandaloneVsConsolidated(textContent: string): {
    standalone: boolean;
    consolidated: boolean;
  } {
    const textLower = textContent.toLowerCase();
    const patterns: { [key: string]: string[] } = {
      standalone: [
        'standalone\\s+(?:financial\\s+statements|balance\\s+sheet|profit\\s+and\\s+loss)',
        'stand-alone',
        'only\\s+financial\\s+statements'
      ],
      consolidated: [
        'consolidated\\s+(?:financial\\s+statements|balance\\s+sheet|profit\\s+and\\s+loss)',
        'group\\s+financial\\s+statements',
        'consolidation'
      ]
    };

    const results = {
      standalone: false,
      consolidated: false
    };

    for (const pattern of patterns.standalone) {
      if (this.matchPattern(textLower, pattern)) {
        results.standalone = true;
        break;
      }
    }

    for (const pattern of patterns.consolidated) {
      if (this.matchPattern(textLower, pattern)) {
        results.consolidated = true;
        break;
      }
    }

    return results;
  }

  /**
   * Extract period information from document
   * Handles Indian date formats (31.03.2023)
   */
  static extractPeriods(textContent: string): {
    current?: string;
    previous?: string;
  } {
    const periods: { current?: string; previous?: string } = {};

    // Find all dates in the text
    const dates: string[] = [];
    for (const pattern of this.INDIAN_PERIOD_PATTERNS) {
      const matches = textContent.match(pattern);
      if (matches) {
        dates.push(matches[0]);
      }
    }

    // Find periods mentioned in headers
    const periodPatterns = [
      /for\s+the\s+year\s+ended\s+(.+?)(?:\s+and\s+|$)/i,
      /as\s+at\s+(.+?)(?:\s+and\s+|$)/i,
      /current\s+year\s*(.+?)(?:\s+previous|$)/i,
      /previous\s+year\s*(.+?)(?:\s+|$)/i
    ];

    for (const pattern of periodPatterns) {
      const matches = textContent.match(pattern);
      if (matches && matches[1]) {
        if (!periods.current) {
          periods.current = matches[1].trim();
        } else if (!periods.previous) {
          periods.previous = matches[1].trim();
        }
      }
    }

    return periods;
  }

  /**
   * Analyze table structure and determine if it's a financial table
   */
  static analyzeTableStructure(headers: string[], rows: string[][]): TableStructure {
    const structure: TableStructure = {
      isFinancialTable: false,
      tableType: undefined,
      periodColumns: [],
      valueColumns: [],
      noteReferenceColumn: undefined,
      hasIndASHeaders: false,
      confidence: 0
    };

    // Check if it's a financial table
    const financialKeywords = [
      'particulars', 'amount', 'note', 'rs.', '₹',
      'total', 'assets', 'liabilities', 'equity',
      'revenue', 'expense', 'profit', 'loss',
      'current', 'previous', 'year'
    ];

    const headerText = headers.join(' ').toLowerCase();
    const financialScore = financialKeywords.filter(keyword => 
      headerText.includes(keyword)
    ).length;

    structure.isFinancialTable = financialScore >= 2;
    structure.confidence = financialScore / financialKeywords.length;

    if (!structure.isFinancialTable) {
      return structure;
    }

    // Check for Ind AS specific headers
    const indASHeaders = [
      'particulars', 'note', 'amount', 'rs.'
    ];
    structure.hasIndASHeaders = indASHeaders.some(header => 
      headerText.includes(header)
    );

    // Detect period columns
    for (let i = 0; i < headers.length; i++) {
      const header = headers[i].toLowerCase();
      if (this.isPeriodHeader(header)) {
        structure.periodColumns.push(headers[i]);
      }
    }

    // Detect value columns (columns with numeric data)
    if (rows.length > 0) {
      const firstRow = rows[0];
      for (let i = 0; i < firstRow.length; i++) {
        if (this.isNumericColumn(rows, i)) {
          structure.valueColumns.push(i);
        }
      }
    }

    // Detect note reference column (usually contains numbers like 1, 2, 3, etc.)
    for (let i = 0; i < headers.length; i++) {
      if (this.isNoteReferenceColumn(rows, i)) {
        structure.noteReferenceColumn = i;
        break;
      }
    }

    // Determine table type
    if (headerText.includes('balance') || headerText.includes('assets') || headerText.includes('liabilities')) {
      structure.tableType = 'balance_sheet';
    } else if (headerText.includes('profit') || headerText.includes('loss') || headerText.includes('income')) {
      structure.tableType = 'profit_loss';
    } else if (headerText.includes('cash flow') || headerText.includes('cashflow')) {
      structure.tableType = 'cash_flow';
    } else if (headerText.includes('equity') || headerText.includes('reserves')) {
      structure.tableType = 'equity_changes';
    }

    return structure;
  }

  /**
   * Check if a header represents a period column
   */
  private static isPeriodHeader(header: string): boolean {
    const periodPatterns = [
      /current\s*year/i,
      /previous\s*year/i,
      /year\s*ended/i,
      /as\s*at/i,
      /as\s*on/i,
      /\d{4}$/,
      /202[0-9]/,
      /202[0-9]-20[0-9]/  // Range
    ];

    return periodPatterns.some(pattern => pattern.test(header));
  }

  /**
   * Check if a column contains numeric data
   */
  private static isNumericColumn(rows: string[][], colIndex: number): boolean {
    const sampleSize = Math.min(rows.length, 10);
    let numericCount = 0;

    for (let i = 0; i < sampleSize; i++) {
      const cell = rows[i][colIndex]?.trim();
      if (cell && !isNaN(parseFloat(cell.replace(/[^0-9.-]/g, '')))) {
        numericCount++;
      }
    }

    return numericCount / sampleSize > 0.5;
  }

  /**
   * Check if a column contains note references (1, 2, 3, etc.)
   */
  private static isNoteReferenceColumn(rows: string[][], colIndex: number): boolean {
    const sampleSize = Math.min(rows.length, 10);
    let noteCount = 0;

    for (let i = 0; i < sampleSize; i++) {
      const cell = rows[i][colIndex]?.trim();
      if (cell && /^\d+$/.test(cell) && parseInt(cell) < 100) {
        noteCount++;
      }
    }

    return noteCount / sampleSize > 0.3;
  }

  /**
   * Match multiple patterns against text
   */
  private static matchPatterns(text: string, patterns: string[]): boolean {
    for (const pattern of patterns) {
      if (this.matchPattern(text, pattern)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Match a single pattern against text
   */
  private static matchPattern(text: string, pattern: string): boolean {
    try {
      const regex = new RegExp(pattern, 'i');
      return regex.test(text);
    } catch (e) {
      return false;
    }
  }

  /**
   * Detect Ind AS specific line items
   */
  static detectIndASSpecificItems(text: string): string[] {
    const indASSpecificItems = [
      'reserves and surplus',
      'capital work in progress',
      'sundry creditors',
      'sundry debtors',
      'other equity',
      'non-controlling interests',
      'current maturities of long term debt',
      'trade payables',
      'trade receivables',
      'contract assets',
      'contract liabilities',
      'expected credit loss',
      'mat credit entitlement'
    ];

    const textLower = text.toLowerCase();
    const foundItems: string[] = [];

    for (const item of indASSpecificItems) {
      if (textLower.includes(item)) {
        foundItems.push(item);
      }
    }

    return foundItems;
  }
}

export default IndASStructureRecognizer;