/**
 * IndASService
 * Main service integrating all Ind AS (Indian Accounting Standards) features
 * Provides unified interface for Ind AS-specific document processing
 */

import { IndianNumberParser, ParsedNumber } from './indianNumberParser';
import { IndASStructureRecognizer, StatementStructure, TableStructure } from './indASStructureRecognizer';
import { IndASSignDetector, SignDetection } from './indASSignDetector';
import { MCAXBRLExtractor, XBRLFact } from './mcaXBRLExtractor';
import { IndASPDFTableExtractor, IndASTable } from './indASPDFTableExtractor';
import { IndASValidator, ValidationResult, ValidationError } from './indASValidator';

export interface IndASDocument {
  structure: StatementStructure;
  tables: IndASTable[];
  xbrlFacts?: XBRLFact[];
  validation?: {
    balanceSheet?: ValidationResult;
    profitLoss?: ValidationResult;
    cashFlow?: ValidationResult;
  };
  isIndASDocument: boolean;
  confidence: number;
}

export interface IndASProcessingOptions {
  detectIndASFormat: boolean;
  parseIndianNumbers: boolean;
  detectSigns: boolean;
  validateMandatoryChecks: boolean;
  extractXBRL: boolean;
}

export class IndASService {
  /**
   * Process document with full Ind AS capabilities
   */
  static processIndASDocument(
    textContent: string,
    tables: Array<{ headers: string[]; rows: string[][] }>,
    options: Partial<IndASProcessingOptions> = {}
  ): IndASDocument {
    const defaultOptions: IndASProcessingOptions = {
      detectIndASFormat: true,
      parseIndianNumbers: true,
      detectSigns: true,
      validateMandatoryChecks: true,
      extractXBRL: false,
      ...options
    };

    const document: IndASDocument = {
      structure: this.getDefaultStructure(),
      tables: [],
      xbrlFacts: [],
      isIndASDocument: false,
      confidence: 0
    };

    // Detect Ind AS structure
    if (defaultOptions.detectIndASFormat) {
      document.structure = IndASStructureRecognizer.recognizeStructure(textContent);
      document.isIndASDocument = document.structure.isIndAS;
      document.confidence += document.structure.confidence;
    }

    // Process tables with Ind AS awareness
    const indASTables = IndASPDFTableExtractor.extractAllTables(tables);
    document.tables = indASTables;
    document.confidence += indASTables.length > 0 ? 0.3 : 0;

    // Apply Ind AS number parsing
    if (defaultOptions.parseIndianNumbers) {
      document.tables = this.applyIndianNumberParsing(document.tables);
    }

    // Apply sign detection
    if (defaultOptions.detectSigns) {
      document.tables = this.applySignDetection(document.tables);
    }

    // Validate Ind AS mandatory checks
    if (defaultOptions.validateMandatoryChecks) {
      document.validation = this.validateIndASDocument(document.tables);
    }

    return document;
  }

  /**
   * Apply Indian number parsing to table values
   */
  private static applyIndianNumberParsing(tables: IndASTable[]): IndASTable[] {
    return tables.map(table => ({
      ...table,
      rows: table.rows.map(row => ({
        ...row,
        values: this.parseRowValuesWithIndianFormat(row.values)
      }))
    }));
  }

  /**
   * Parse row values with Indian number format
   */
  private static parseRowValuesWithIndianFormat(values: Record<string, number>): Record<string, number> {
    const parsedValues: Record<string, number> = {};

    for (const [period, value] of Object.entries(values)) {
      const valueStr = value.toString();

      // Parse with Indian number parser
      const parsed = IndianNumberParser.parse(valueStr);
      if (parsed && parsed !== null) {
        parsedValues[period] = parsed.value;
      } else {
        parsedValues[period] = value;
      }
    }

    return parsedValues;
  }

  /**
   * Apply sign detection to table values
   */
  private static applySignDetection(tables: IndASTable[]): IndASTable[] {
    return tables.map(table => ({
      ...table,
      rows: table.rows.map(row => ({
        ...row,
        values: this.detectAndApplySigns(row.lineItem, row.values, table.type)
      }))
    }));
  }

  /**
   * Detect and apply signs to values based on line item
   */
  private static detectAndApplySigns(
    lineItem: string,
    values: Record<string, number>,
    tableType: IndASTable['type']
  ): Record<string, number> {
    const signedValues: Record<string, number> = {};

    for (const [period, value] of Object.entries(values)) {
      const detection = IndASSignDetector.detectSign(lineItem, value, tableType);
      signedValues[period] = IndASSignDetector.applySign(value, detection.multiplier);
    }

    return signedValues;
  }

  /**
   * Validate Ind AS document against mandatory checks
   */
  private static validateIndASDocument(tables: IndASTable[]): {
    balanceSheet?: ValidationResult;
    profitLoss?: ValidationResult;
    cashFlow?: ValidationResult;
  } {
    const validation: {
      balanceSheet?: ValidationResult;
      profitLoss?: ValidationResult;
      cashFlow?: ValidationResult;
    } = {};

    // Find tables by type
    const balanceSheet = tables.find(t => t.type === 'balance_sheet');
    const profitLoss = tables.find(t => t.type === 'profit_loss');
    const cashFlow = tables.find(t => t.type === 'cash_flow');

    // Validate each statement
    if (balanceSheet) {
      const items = this.convertTableToValidationItems(balanceSheet);
      validation.balanceSheet = IndASValidator.validateIndASStatement(items, 'balance_sheet');
    }

    if (profitLoss) {
      const items = this.convertTableToValidationItems(profitLoss);
      validation.profitLoss = IndASValidator.validateIndASStatement(items, 'profit_loss');
    }

    if (cashFlow) {
      const items = this.convertTableToValidationItems(cashFlow);
      validation.cashFlow = IndASValidator.validateIndASStatement(items, 'cash_flow');
    }

    return validation;
  }

  /**
   * Convert table to validation items format
   */
  private static convertTableToValidationItems(table: IndASTable): Array<{ key: string; value: number; label?: string }> {
    return table.rows
      .filter(row => row.metricKey && !row.isHeader && !row.isTotal)
      .map(row => ({
        key: row.metricKey || row.lineItem,
        value: Object.values(row.values)[0] || 0, // Use first period value
        label: row.lineItem
      }));
  }

  /**
   * Get default structure
   */
  private static getDefaultStructure(): StatementStructure {
    return {
      type: 'unknown',
      isIndAS: false,
      isStandalone: false,
      isConsolidated: false,
      period: { current: undefined, previous: undefined },
      format: 'international',
      confidence: 0
    };
  }

  /**
   * Parse a single number with Indian format
   */
  static parseIndianNumber(input: string): ParsedNumber | null {
    return IndianNumberParser.parse(input);
  }

  /**
   * Parse multiple numbers with Indian format
   */
  static parseIndianNumbers(inputs: string[]): (ParsedNumber | null)[] {
    return IndianNumberParser.parseArray(inputs);
  }

  /**
   * Check if a string is likely an Indian number format
   */
  static isIndianNumberFormat(input: string): boolean {
    return IndianNumberParser.isIndianFormat(input);
  }

  /**
   * Format number in Indian style with commas
   */
  static formatIndianNumber(num: number): string {
    return IndianNumberParser.formatIndian(num);
  }

  /**
   * Detect document structure
   */
  static detectStructure(textContent: string): StatementStructure {
    return IndASStructureRecognizer.recognizeStructure(textContent);
  }

  /**
   * Detect standalone vs consolidated
   */
  static detectDocumentType(textContent: string): {
    standalone: boolean;
    consolidated: boolean;
  } {
    return IndASStructureRecognizer.extractStandaloneVsConsolidated(textContent);
  }

  /**
   * Detect sign of a value
   */
  static detectSign(lineItem: string, value: number, section?: string): SignDetection {
    return IndASSignDetector.detectSign(lineItem, value, section);
  }

  /**
   * Validate a specific statement
   */
  static validateStatement(
    items: Array<{ key: string; value: number; label?: string }>,
    statementType: 'balance_sheet' | 'profit_loss' | 'cash_flow'
  ): ValidationResult {
    return IndASValidator.validateIndASStatement(items, statementType);
  }

  /**
   * Validate mandatory items presence
   */
  static validateMandatoryItems(
    items: Array<{ key: string; value: number }>,
    statementType: 'balance_sheet' | 'profit_loss' | 'cash_flow'
  ): ValidationResult {
    return IndASValidator.validateMandatoryItems(items, statementType);
  }

  /**
   * Validate mathematical consistency
   */
  static validateMathematicalConsistency(
    items: Array<{ key: string; value: number }>
  ): ValidationResult {
    return IndASValidator.validateMathematicalConsistency(items);
  }

  /**
   * Generate validation report
   */
  static generateValidationReport(validationResults: {
    balanceSheet?: ValidationResult;
    profitLoss?: ValidationResult;
    cashFlow?: ValidationResult;
  }): string {
    return IndASValidator.generateValidationReport(validationResults);
  }

  /**
   * Extract Ind AS specific items from text
   */
  static detectIndASSpecificItems(text: string): string[] {
    return IndASStructureRecognizer.detectIndASSpecificItems(text);
  }

  /**
   * Analyze table structure
   */
  static analyzeTableStructure(headers: string[], rows: string[][]): TableStructure {
    return IndASStructureRecognizer.analyzeTableStructure(headers, rows);
  }

  /**
   * Parse value with sign detection
   */
  static parseValueWithSign(lineItem: string, valueStr: string, section?: string): number {
    return IndASSignDetector.parseValueWithSign(lineItem, valueStr, section);
  }

  /**
   * Get scale in Indian terms for a given number
   */
  static getIndianScale(value: number): { value: number; scale: string } {
    return IndianNumberParser.getIndianScale(value);
  }

  /**
   * Convert number to Indian words
   */
  static toIndianWords(num: number): string {
    return IndianNumberParser.toIndianWords(num);
  }

  /**
   * Get Ind AS terminology mapping
   */
  static getIndASTerminology(): string[] {
    return [
      'reserves_and_surplus',
      'capital_work_in_progress',
      'sundry_creditors',
      'sundry_debtors',
      'trade_payables',
      'trade_receivables',
      'current_maturities_long_term_debt',
      'contract_assets',
      'contract_liabilities',
      'expected_credit_loss',
      'mat_credit_entitlement',
      'non_controlling_interests'
    ];
  }

  /**
   * Check if document follows Ind AS standards
   */
  static isIndASFiling(textContent: string): boolean {
    return IndASStructureRecognizer.isIndASFiling(textContent);
  }

  /**
   * Get Ind AS specific warnings
   */
  static getIndASWarnings(text: string): string[] {
    const warnings: string[] = [];

    // Check for common issues
    if (!text.toLowerCase().includes('reserves and surplus')) {
      warnings.push('Reserves and surplus not found - verify equity section');
    }

    if (!text.toLowerCase().includes('notes to the') && 
        !text.toLowerCase().includes('notes to financial statements')) {
      warnings.push('No notes section detected - Ind AS requires comprehensive notes');
    }

    if (text.toLowerCase().includes('minority interest') || 
        text.toLowerCase().includes('minority interests')) {
      warnings.push('Legacy term "minority interest" detected - should be "non-controlling interests" per Ind AS');
    }

    return warnings;
  }

  /**
   * Get recommended actions based on analysis
   */
  static getRecommendedActions(document: IndASDocument): string[] {
    const actions: string[] = [];

    // Check validation results
    if (document.validation) {
      if (document.validation.balanceSheet?.errors.length || 0 > 0) {
        actions.push('Review Balance Sheet: ' + document.validation.balanceSheet.errors.length + ' errors found');
      }

      if (document.validation.profitLoss?.errors.length || 0 > 0) {
        actions.push('Review Profit & Loss: ' + document.validation.profitLoss.errors.length + ' errors found');
      }

      if (document.validation.cashFlow?.errors.length || 0 > 0) {
        actions.push('Review Cash Flow: ' + document.validation.cashFlow.errors.length + ' errors found');
      }
    }

    // Check Ind AS format
    if (!document.isIndASDocument) {
      actions.push('Document may not follow Ind AS standards - verify terminology');
    }

    // Check confidence
    if (document.confidence < 0.7) {
      actions.push('Low confidence in extraction results - manual review recommended');
    }

    return actions.length > 0 ? actions : ['No issues detected'];
  }
}

export default IndASService;