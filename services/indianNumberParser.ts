/**
 * IndianNumberParser
 * Handles Indian number formats including lakhs and crores
 * Indian Number System:
 * - 1 Lakh = 100,000 (10^5)
 * - 1 Crore = 10,000,000 (10^7)
 * - 1 Hundred = 100 (10^2)
 * - 1 Thousand = 1,000 (10^3)
 * - 1 Arab (rare) = 1,000,000,000 (10^9)
 */

export interface ParsedNumber {
  value: number;
  scale: string | null;
  isNegative: boolean;
  originalText: string;
}

export class IndianNumberParser {
  // Indian numeral words to numeric values
  private static readonly INDIAN_NUMERAL_WORDS = {
    'lakh': 100000,
    'lakhs': 100000,
    'lac': 100000,
    'lacs': 100000,
    'crore': 10000000,
    'crores': 10000000,
    'cr': 10000000,
    'crs': 10000000,
    'hundred': 100,
    'thousand': 1000,
    'thousands': 1000,
    'million': 1000000,
    'millions': 1000000,
    'billion': 1000000000,
    'billions': 1000000000,
    'arab': 1000000000,
    'arabs': 1000000000,
    'kharab': 100000000000,
  };

  // Indian currency symbols and prefixes
  private static readonly INDIAN_CURRENCY_INDICATORS = [
    '₹',
    'rs.',
    'rs',
    'inr',
    'rupees',
    'rupee',
    're.',
    're',
    'rupiah'
  ];

  /**
   * Parse a number string potentially containing Indian number formats
   * Examples:
   * - "1.5 cr" -> 15000000
   * - "2.35 lakhs" -> 235000
   * - "1,23,456" -> 123456
   * - "(5.2 cr)" -> -52000000
   */
  static parse(input: string): ParsedNumber | null {
    if (!input || typeof input !== 'string') {
      return null;
    }

    const cleaned = input.trim();
    const isNegative = this.detectNegative(cleaned);
    const cleanedForValue = this.cleanInput(cleaned);

    // Check for numeral words (lakh, crore, etc.)
    const wordScaleMatch = this.parseWithNumeralWords(cleanedForValue);
    if (wordScaleMatch !== null) {
      return {
        value: isNegative ? -wordScaleMatch : wordScaleMatch,
        scale: this.extractScale(cleanedForValue),
        isNegative,
        originalText: input
      };
    }

    // Check for Indian number format with commas (1,23,456)
    const indianFormatMatch = this.parseIndianFormat(cleanedForValue);
    if (indianFormatMatch !== null) {
      return {
        value: isNegative ? -indianFormatMatch : indianFormatMatch,
        scale: null,
        isNegative,
        originalText: input
      };
    }

    // Standard international format (1,234,567)
    const standardFormatMatch = this.parseStandardFormat(cleanedForValue);
    if (standardFormatMatch !== null) {
      return {
        value: isNegative ? -standardFormatMatch : standardFormatMatch,
        scale: null,
        isNegative,
        originalText: input
      };
    }

    return null;
  }

  /**
   * Detect if a number represents a negative value
   * Ind AS specific: Dr., Less:, parentheses
   */
  private static detectNegative(input: string): boolean {
    const lowerInput = input.toLowerCase();

    // Parentheses format (common in Ind AS)
    if (input.includes('(') && input.includes(')')) {
      return true;
    }

    // Negative sign
    if (input.startsWith('-') || lowerInput.startsWith('negative')) {
      return true;
    }

    // Ind AS specific indicators
    const negativeIndicators = [
      'dr',       // Debit
      'debit',
      'less:',    // Very common in Ind AS
      'less -',
      'outflow',
      'decrease',
      'expense',
      'loss'
    ];

    return negativeIndicators.some(indicator => 
      lowerInput.includes(indicator.toLowerCase())
    );
  }

  /**
   * Clean input string by removing currency symbols and extra spaces
   */
  private static cleanInput(input: string): string {
    let cleaned = input.toLowerCase();

    // Remove currency indicators
    this.INDIAN_CURRENCY_INDICATORS.forEach(indicator => {
      cleaned = cleaned.replace(indicator.toLowerCase(), '');
    });

    // Remove common words
    cleaned = cleaned
      .replace(/\b(rupee|rupees|rs\.?|inr|₹)\s*/gi, '')
      .replace(/\b(approx|approximately|about|around|~)\s*/gi, '')
      .replace(/\s+/g, ' ')
      .trim();

    return cleaned;
  }

  /**
   * Parse number with Indian numeral words (lakh, crore, etc.)
   */
  private static parseWithNumeralWords(input: string): number | null {
    const lowerInput = input.toLowerCase();

    for (const [word, multiplier] of Object.entries(this.INDIAN_NUMERAL_WORDS)) {
      if (lowerInput.includes(word)) {
        // Extract the number before the numeral word
        const regex = new RegExp(`([\\d,]+\\.?[\\d]*)\\s*${word}`, 'i');
        const match = input.match(regex);
        
        if (match) {
          const numberStr = match[1].replace(/,/g, '');
          const number = parseFloat(numberStr);
          
          if (!isNaN(number)) {
            return number * multiplier;
          }
        }
      }
    }

    return null;
  }

  /**
   * Parse Indian number format with Indian-style commas
   * Format: 1,23,45,678 (crores, lakhs, thousands, hundreds)
   */
  private static parseIndianFormat(input: string): number | null {
    // Check if it matches Indian comma pattern (groups of 2 digits except last group of 3)
    const indianCommaPattern = /^\d{1,3}(,\d{2})*(,\d{3})?$/;
    
    if (indianCommaPattern.test(input)) {
      // Remove all commas
      const withoutCommas = input.replace(/,/g, '');
      const number = parseFloat(withoutCommas);
      
      return isNaN(number) ? null : number;
    }

    return null;
  }

  /**
   * Parse standard international number format
   * Format: 1,234,567 (thousands, millions)
   */
  private static parseStandardFormat(input: string): number | null {
    // Check if it matches standard comma pattern (groups of 3 digits)
    const standardCommaPattern = /^\d{1,3}(,\d{3})*$/;
    
    if (standardCommaPattern.test(input)) {
      // Remove all commas
      const withoutCommas = input.replace(/,/g, '');
      const number = parseFloat(withoutCommas);
      
      return isNaN(number) ? null : number;
    }

    // Try parsing as plain number without commas
    const plainNumber = parseFloat(input);
    return isNaN(plainNumber) ? null : plainNumber;
  }

  /**
   * Extract the scale word from the input
   */
  private static extractScale(input: string): string | null {
    const lowerInput = input.toLowerCase();
    
    for (const word of Object.keys(this.INDIAN_NUMERAL_WORDS)) {
      if (lowerInput.includes(word)) {
        return word;
      }
    }
    
    return null;
  }

  /**
   * Convert number to Indian format with commas
   */
  static formatIndian(num: number): string {
    if (num === 0) return '0';

    const isNegative = num < 0;
    const absNum = Math.abs(num);
    
    let result = '';
    let remainder = absNum;

    // Crores (100,00,000)
    if (remainder >= 10000000) {
      const crores = Math.floor(remainder / 10000000);
      remainder = remainder % 10000000;
      result = crores + ',';
    }

    // Lakhs (1,00,000)
    if (remainder >= 100000) {
      const lakhs = Math.floor(remainder / 100000);
      remainder = remainder % 100000;
      result += lakhs + ',';
    }

    // Thousands (1,000)
    if (remainder >= 1000) {
      const thousands = Math.floor(remainder / 1000);
      remainder = remainder % 1000;
      result += thousands + ',';
    }

    // Last three digits (hundreds)
    result += remainder.toString().padStart(3, '0');

    // Remove leading zeros
    result = result.replace(/^0+/, '') || '0';

    return isNegative ? '-' + result : result;
  }

  /**
   * Format number in words (Indian style)
   */
  static toIndianWords(num: number): string {
    if (num === 0) return 'Zero';

    const isNegative = num < 0;
    const absNum = Math.abs(num);

    if (absNum >= 10000000) {
      const crores = (absNum / 10000000).toFixed(2);
      return `${isNegative ? 'Negative ' : ''}${crores} Crores`;
    } else if (absNum >= 100000) {
      const lakhs = (absNum / 100000).toFixed(2);
      return `${isNegative ? 'Negative ' : ''}${lakhs} Lakhs`;
    } else if (absNum >= 1000) {
      const thousands = (absNum / 1000).toFixed(2);
      return `${isNegative ? 'Negative ' : ''}${thousands} Thousands`;
    } else {
      return `${isNegative ? 'Negative ' : ''}${absNum.toString()}`;
    }
  }

  /**
   * Detect if a string likely contains Indian number format
   */
  static isIndianFormat(input: string): boolean {
    const lowerInput = input.toLowerCase();

    // Check for Indian numeral words
    if (Object.keys(this.INDIAN_NUMERAL_WORDS).some(word => 
      lowerInput.includes(word)
    )) {
      return true;
    }

    // Check for Indian comma pattern
    const indianCommaPattern = /^\d{1,3}(,\d{2})*(,\d{3})?$/;
    if (indianCommaPattern.test(input.replace(/[^0-9,]/g, ''))) {
      return true;
    }

    // Check for Indian currency symbols
    if (this.INDIAN_CURRENCY_INDICATORS.some(indicator => 
      input.includes(indicator)
    )) {
      return true;
    }

    return false;
  }

  /**
   * Parse array of numbers (useful for table cells)
   */
  static parseArray(inputs: string[]): (ParsedNumber | null)[] {
    return inputs.map(input => this.parse(input));
  }

  /**
   * Convert Indian scale to standard value
   * Useful for display purposes
   */
  static convertFromScale(value: number, scale: string | null): number {
    if (!scale) return value;

    const lowerScale = scale.toLowerCase();
    const multiplier = this.INDIAN_NUMERAL_WORDS[lowerScale as keyof typeof this.INDIAN_NUMERAL_WORDS];
    
    return multiplier ? value * multiplier : value;
  }

  /**
   * Get scale in Indian terms for a given number
   */
  static getIndianScale(value: number): { value: number; scale: string } {
    const absValue = Math.abs(value);

    if (absValue >= 10000000) {
      return {
        value: value / 10000000,
        scale: 'Crore'
      };
    } else if (absValue >= 100000) {
      return {
        value: value / 100000,
        scale: 'Lakh'
      };
    } else if (absValue >= 1000) {
      return {
        value: value / 1000,
        scale: 'Thousand'
      };
    } else {
      return {
        value,
        scale: 'Units'
      };
    }
  }
}

export default IndianNumberParser;