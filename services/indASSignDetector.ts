/**
 * IndASSignDetector
 * Detect negative values in Ind AS financial statements
 * Handles Ind AS specific sign conventions different from US GAAP
 */

export interface SignDetection {
  multiplier: number;
  confidence: number;
  reason: string;
}

export class IndASSignDetector {
  // Ind AS specific negative indicators
  private static readonly NEGATIVE_INDICATORS = {
    prefix_words: [
      'less', 'less:', 'less-',
      'negative', 'dr', 'debit',
      'outflow', 'payment',
      'decrease', 'decreasing',
      'reduction', 'minus'
    ],
    suffix_words: [
      'dr', '(dr)', '[dr]',
      'expense', 'loss', 'outflow',
      'payment', 'debit'
    ],
    parentheses: true,  // (100) = -100
    minus_sign: true,
    red_color: false,  // Can't detect in text extraction
  };

  // Ind AS specific items that are typically negative
  private static readonly NEGATIVE_NATURE_ITEMS = [
    'provision', 'allowance', 'reserve', 'impairment',
    'accumulated depreciation', 'accumulated amortisation',
    'accumulated losses', 'contra account',
    'discount on issue', 'preliminary expenses written off',
    'share issue expenses written off'
  ];

  // Items that are typically positive in Ind AS despite being "negative" in accounting
  private static readonly POSITIVE_NATURE_ITEMS = [
    'accumulated depreciation',  // Usually shown as positive with label indicating deduction
    'accumulated amortisation',  // Usually shown as positive with label indicating deduction
  ];

  /**
   * Detect sign of a value in Ind AS context
   * Returns +1 or -1 multiplier along with confidence and reasoning
   */
  static detectSign(lineItem: string, value: number, section?: string): SignDetection {
    const lineLower = lineItem.toLowerCase();
    let multiplier = 1;
    let confidence = 0.5;
    let reason = 'No specific indicators detected, assumed positive';

    // Check for negative indicators in label
    for (const negWord of this.NEGATIVE_INDICATORS.prefix_words) {
      if (lineLower.startsWith(negWord) || lineLower.includes(` ${negWord} `)) {
        multiplier = -1;
        confidence = 0.9;
        reason = `Found negative prefix indicator: "${negWord}"`;
        break;
      }
    }

    // Check for "Less:" specifically (very common in Ind AS)
    if (lineLower.includes('less:') || lineLower.includes('less -')) {
      multiplier = -1;
      confidence = 0.95;
      reason = 'Found "Less:" indicator (Ind AS specific)';
    }

    // Check for parentheses around value
    if (this.hasParentheses(value.toString())) {
      multiplier = -1;
      confidence = 0.85;
      reason = 'Value is in parentheses, indicating negative';
    }

    // Check for explicit negative sign
    if (value < 0) {
      multiplier = -1;
      confidence = 0.99;
      reason = 'Value is explicitly negative';
    }

    // Ind AS specific: Allowances, provisions, reserves are typically negative
    // unless they're accumulated depreciation/amortisation
    for (const negativeItem of this.NEGATIVE_NATURE_ITEMS) {
      if (lineLower.includes(negativeItem) && !this.isPositiveNatureItem(lineLower)) {
        // These are contra-assets or negative equity items
        if (section === 'assets' || section === 'equity' || section === 'income') {
          multiplier = -1;
          confidence = 0.8;
          reason = `Item is typically contra asset/equity: "${negativeItem}"`;
        }
        break;
      }
    }

    // Expense items in P&L (though usually shown as positive with "expense" label)
    if (section === 'expenses' || section === 'finance costs') {
      // Values are typically stored positive in tables
      multiplier = 1;
      confidence = 0.7;
      reason = 'Expense section items typically shown as positive in Ind AS tables';
    }

    // Cash flow outflows
    if (lineLower.includes('outflow') || lineLower.includes('cash paid') || lineLower.includes('cash flow used')) {
      multiplier = -1;
      confidence = 0.85;
      reason = 'Cash flow outflow detected';
    }

    return {
      multiplier,
      confidence,
      reason
    };
  }

  /**
   * Apply sign multiplier to a value
   */
  static applySign(value: number, multiplier: number): number {
    return value * multiplier;
  }

  /**
   * Check if a value is in parentheses
   */
  private static hasParentheses(valueStr: string): boolean {
    return valueStr.startsWith('(') && valueStr.endsWith(')');
  }

  /**
   * Check if an item is actually positive despite being in negative nature items list
   */
  private static isPositiveNatureItem(lineItem: string): boolean {
    const lineLower = lineItem.toLowerCase();
    return this.POSITIVE_NATURE_ITEMS.some(item => lineLower.includes(item));
  }

  /**
   * Parse value with sign detection
   */
  static parseValueWithSign(lineItem: string, valueStr: string, section?: string): number {
    // Clean the value string
    const cleanedValue = this.cleanValueString(valueStr);
    const value = parseFloat(cleanedValue);

    if (isNaN(value)) {
      return 0;
    }

    // Detect sign
    const detection = this.detectSign(lineItem, value, section);

    // Apply sign
    return this.applySign(value, detection.multiplier);
  }

  /**
   * Clean value string for parsing
   */
  private static cleanValueString(valueStr: string): string {
    let cleaned = valueStr.trim();

    // Remove parentheses
    if (cleaned.startsWith('(') && cleaned.endsWith(')')) {
      cleaned = cleaned.substring(1, cleaned.length - 1);
    }

    // Remove commas
    cleaned = cleaned.replace(/,/g, '');

    // Remove currency symbols
    cleaned = cleaned.replace(/[₹Rs.\s]/g, '');

    return cleaned;
  }

  /**
   * Detect sign from cell content alone (without line item context)
   */
  static detectSignFromCell(cellValue: string): SignDetection {
    const cleaned = this.cleanValueString(cellValue);

    // Check for parentheses
    if (this.hasParentheses(cellValue)) {
      return {
        multiplier: -1,
        confidence: 0.9,
        reason: 'Cell value in parentheses'
      };
    }

    // Check for leading negative sign
    if (cellValue.trim().startsWith('-')) {
      return {
        multiplier: -1,
        confidence: 0.99,
        reason: 'Cell value has explicit negative sign'
      };
    }

    // Check for text indicators in cell
    const cellLower = cellValue.toLowerCase();
    if (cellLower.includes('dr') || cellLower.includes('debit')) {
      return {
        multiplier: -1,
        confidence: 0.85,
        reason: 'Cell contains debit indicator'
      };
    }

    return {
      multiplier: 1,
      confidence: 0.7,
      reason: 'No negative indicators in cell, assumed positive'
    };
  }

  /**
   * Normalize signs in a dataset
   * Ensures consistent sign conventions across extracted data
   */
  static normalizeDataset(data: Array<{ lineItem: string; value: number; section?: string }>): Array<{ lineItem: string; value: number; section?: string; signInfo: SignDetection }> {
    return data.map(item => {
      const detection = this.detectSign(item.lineItem, item.value, item.section);
      return {
        ...item,
        value: this.applySign(item.value, detection.multiplier),
        signInfo: detection
      };
    });
  }

  /**
   * Check for sign inconsistencies in related items
   */
  static detectSignInconsistencies(items: Array<{ lineItem: string; value: number }>): Array<{ index: number; message: string }> {
    const inconsistencies: Array<{ index: number; message: string }> = [];

    for (let i = 0; i < items.length; i++) {
      const current = items[i];
      const detection = this.detectSign(current.lineItem, current.value);

      // Check if item should be negative but is positive
      if (this.NEGATIVE_NATURE_ITEMS.some(item => current.lineItem.toLowerCase().includes(item)) &&
          !this.isPositiveNatureItem(current.lineItem) &&
          current.value > 0) {
        inconsistencies.push({
          index: i,
          message: `Item "${current.lineItem}" should be negative but is positive`
        });
      }

      // Check for total/subtotal relationships
      if (i > 0) {
        const previous = items[i - 1];
        const prevDetection = this.detectSign(previous.lineItem, previous.value);

        // Check for abrupt sign changes in related items
        if (detection.multiplier !== prevDetection.multiplier &&
            detection.confidence > 0.8 && prevDetection.confidence > 0.8) {
          inconsistencies.push({
            index: i,
            message: `Possible sign inconsistency between "${previous.lineItem}" and "${current.lineItem}"`
          });
        }
      }
    }

    return inconsistencies;
  }

  /**
   * Get sign convention for a section
   */
  static getSectionSignConvention(section: string): 'positive' | 'negative' | 'mixed' {
    const sectionLower = section.toLowerCase();

    if (sectionLower.includes('expense') || sectionLower.includes('cost') || sectionLower.includes('outflow')) {
      return 'negative';
    } else if (sectionLower.includes('income') || sectionLower.includes('revenue') || sectionLower.includes('inflow')) {
      return 'positive';
    }

    return 'mixed';
  }

  /**
   * Validate sign conventions in a dataset
   */
  static validateSigns(data: Array<{ lineItem: string; value: number; section?: string }>): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    const normalizedData = this.normalizeDataset(data);

    // Check for sign inconsistencies
    const inconsistencies = this.detectSignInconsistencies(data);
    inconsistencies.forEach(inc => {
      errors.push(inc.message);
    });

    // Check section-level sign conventions
    const sections = [...new Set(data.map(d => d.section).filter(Boolean))];
    sections.forEach(section => {
      const convention = this.getSectionSignConvention(section || '');
      if (convention === 'positive' || convention === 'negative') {
        const expectedSign = convention === 'positive' ? 1 : -1;
        const sectionItems = data.filter(d => d.section === section);

        sectionItems.forEach(item => {
          const detection = this.detectSign(item.lineItem, item.value, section);
          if (detection.confidence > 0.8 && detection.multiplier !== expectedSign) {
            errors.push(
              `Item "${item.lineItem}" in section "${section}" has unexpected sign (expected: ${expectedSign}, detected: ${detection.multiplier})`
            );
          }
        });
      }
    });

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

export default IndASSignDetector;