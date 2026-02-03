/**
 * IndASValidator
 * Validation rules specific to Ind AS financial statements
 * Implements Ind AS mandatory disclosures and mathematical validations
 */

export interface ValidationError {
  check: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  actualValue?: number;
  expectedValue?: number;
  formula?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  score: number; // 0-100
}

export class IndASValidator {
  // Ind AS mandatory validation rules
  private static readonly IND_AS_MANDATORY_CHECKS = {
    balance_sheet: [
      {
        name: 'assets_equal_liabilities_plus_equity',
        formula: 'total_assets == total_liabilities + total_equity',
        tolerance: 0.01
      },
      {
        name: 'equity_breakdown',
        formula: 'total_equity == share_capital + other_equity + non_controlling_interests',
        tolerance: 0.01
      },
      {
        name: 'current_assets_breakdown',
        formula: 'total_current_assets == sum(current_assets_components)',
        tolerance: 0.02
      }
    ],
    profit_loss: [
      {
        name: 'revenue_less_expenses',
        formula: 'profit_before_tax == revenue_from_operations + other_income - total_expenses',
        tolerance: 0.02
      },
      {
        name: 'exceptional_items_separate',
        formula: 'profit_before_tax == profit_before_exceptional_items + exceptional_items',
        tolerance: 0.01
      },
      {
        name: 'comprehensive_income',
        formula: 'total_comprehensive_income == profit_for_period + other_comprehensive_income',
        tolerance: 0.01
      }
    ],
    cash_flow: [
      {
        name: 'cash_reconciliation',
        formula: 'cash_at_end == cash_at_beginning + net_increase_decrease',
        tolerance: 0.01
      },
      {
        name: 'three_activities_total',
        formula: 'net_increase_decrease == net_operating + net_investing + net_financing',
        tolerance: 0.01
      }
    ]
  };

  /**
   * Validate Ind AS statement with mandatory checks
   */
  static validateIndASStatement(
    items: Array<{ key: string; value: number; label?: string }>,
    statementType: 'balance_sheet' | 'profit_loss' | 'cash_flow' | 'equity_changes'
  ): ValidationResult {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100
    };

    // Get mandatory checks for statement type
    const checks = this.IND_AS_MANDATORY_CHECKS[statementType] || [];

    for (const check of checks) {
      try {
        const checkResult = this.evaluateFormula(check.formula, items);
        if (!checkResult) {
          const error: ValidationError = {
            check: check.name,
            message: `Validation failed: ${check.formula}`,
            severity: 'high',
            formula: check.formula
          };
          result.errors.push(error);
          result.score -= 20;
        }
      } catch (e) {
        const error: ValidationError = {
          check: check.name,
          message: `Validation error: ${String(e)}`,
          severity: 'medium'
        };
        result.errors.push(error);
        result.score -= 10;
      }
    }

    // Ind AS specific checks
    if (statementType === 'balance_sheet') {
      result.errors.push(...this.checkIndASBSSpecifics(items));
    } else if (statementType === 'profit_loss') {
      result.errors.push(...this.checkIndASPLSpecifics(items));
    }

    // Calculate final validity
    result.isValid = result.errors.filter(e => e.severity === 'high').length === 0;

    return result;
  }

  /**
   * Ind AS Balance Sheet specific validations
   */
  private static checkIndASBSSpecifics(
    items: Array<{ key: string; value: number }>
  ): ValidationError[] {
    const errors: ValidationError[] = [];

    const getItemValue = (key: string) => items.find(i => i.key === key)?.value || 0;

    // Check for CWIP (mandatory if company has construction)
    const hasPPE = getItemValue('property_plant_equipment') > 0;
    const hasCWIP = getItemValue('capital_work_in_progress') > 0;

    if (hasPPE && !hasCWIP) {
      errors.push({
        check: 'ind_as_cwip_check',
        message: 'Company has PPE but no CWIP disclosed. Verify if construction in progress exists.',
        severity: 'low'
      });
    }

    // Check for current maturities disclosure (Ind AS mandatory)
    const hasLongTermDebt = getItemValue('long_term_borrowings') > 0;
    const hasCurrentMaturities = getItemValue('current_maturities_long_term_debt') > 0;

    if (hasLongTermDebt && !hasCurrentMaturities) {
      errors.push({
        check: 'ind_as_current_maturities',
        message: 'Long term borrowings present but current maturities not separately disclosed',
        severity: 'medium'
      });
    }

    // Check for reserves and surplus disclosure (Ind AS mandatory)
    const hasEquity = getItemValue('total_equity') > 0;
    const hasReserves = getItemValue('reserves_and_surplus') > 0;

    if (hasEquity && !hasReserves) {
      errors.push({
        check: 'ind_as_reserves_check',
        message: 'Total equity present but reserves and surplus not disclosed',
        severity: 'medium'
      });
    }

    // Check for non-controlling interests in consolidated statements
    const hasTotalAssets = getItemValue('total_assets') > 0;
    const hasNCI = getItemValue('non_controlling_interests') !== 0;

    if (hasTotalAssets && !hasNCI) {
      errors.push({
        check: 'ind_as_nci_check',
        message: 'Verify if non-controlling interests exist (required for consolidated statements)',
        severity: 'low'
      });
    }

    return errors;
  }

  /**
   * Ind AS Profit & Loss specific validations
   */
  private static checkIndASPLSpecifics(
    items: Array<{ key: string; value: number }>
  ): ValidationError[] {
    const errors: ValidationError[] = [];

    const getItemValue = (key: string) => items.find(i => i.key === key)?.value || 0;

    // Check for other comprehensive income (Ind AS mandatory)
    const hasProfit = getItemValue('net_profit') !== 0;
    const hasOCI = getItemValue('other_comprehensive_income') !== 0;

    if (hasProfit && !hasOCI) {
      errors.push({
        check: 'ind_as_oci_check',
        message: 'Profit reported but other comprehensive income not disclosed (Ind AS mandatory)',
        severity: 'medium'
      });
    }

    // Check for EPS disclosure (Ind AS mandatory)
    const hasProfitForPeriod = getItemValue('profit_for_period') > 0;
    const hasBasicEPS = getItemValue('basic_earnings_per_share') !== 0;
    const hasDilutedEPS = getItemValue('diluted_earnings_per_share') !== 0;

    if (hasProfitForPeriod && !hasBasicEPS) {
      errors.push({
        check: 'ind_as_eps_check',
        message: 'Profit for period reported but basic EPS not disclosed (Ind AS mandatory)',
        severity: 'high'
      });
    }

    if (hasProfitForPeriod && !hasDilutedEPS) {
      errors.push({
        check: 'ind_as_diluted_eps_check',
        message: 'Profit for period reported but diluted EPS not disclosed (Ind AS mandatory)',
        severity: 'high'
      });
    }

    return errors;
  }

  /**
   * Evaluate a validation formula
   */
  private static evaluateFormula(
    formula: string,
    items: Array<{ key: string; value: number }>
  ): boolean {
    // Simplified formula evaluation
    // In real implementation, use a proper expression parser

    const getItemValue = (key: string) => items.find(i => i.key === key)?.value || 0;

    // Replace keys with values
    let evalFormula = formula;

    // Simple replacements for common formulas
    const replacements: Record<string, string> = {
      'total_assets': getItemValue('total_assets').toString(),
      'total_liabilities': getItemValue('total_liabilities').toString(),
      'total_equity': getItemValue('total_equity').toString(),
      'share_capital': getItemValue('share_capital').toString(),
      'other_equity': getItemValue('reserves_and_surplus').toString(),
      'non_controlling_interests': getItemValue('non_controlling_interests').toString(),
      'revenue_from_operations': getItemValue('revenue_from_operations').toString(),
      'other_income': getItemValue('other_income').toString(),
      'total_expenses': getItemValue('total_expenses').toString(),
      'profit_before_tax': getItemValue('profit_before_tax').toString(),
      'profit_for_period': getItemValue('net_profit').toString(),
      'other_comprehensive_income': getItemValue('other_comprehensive_income').toString(),
      'cash_at_end': getItemValue('cash_end_of_period').toString(),
      'cash_at_beginning': getItemValue('cash_beginning_of_period').toString(),
      'net_increase_decrease': getItemValue('net_increase_decrease_cash').toString()
    };

    for (const [key, value] of Object.entries(replacements)) {
      evalFormula = evalFormula.replace(new RegExp(key, 'g'), value);
    }

    // Replace sum() function calls (simplified)
    evalFormula = evalFormula.replace(/sum\([^)]+\)/g, '0');

    try {
      // Use Function constructor for safe evaluation
      const result = new Function('return ' + evalFormula)();
      return Math.abs(result) < 0.01; // Tolerance check
    } catch (e) {
      console.error('Formula evaluation error:', e);
      return false;
    }
  }

  /**
   * Validate that all Ind AS mandatory items are present
   */
  static validateMandatoryItems(
    items: Array<{ key: string; value: number }>,
    statementType: 'balance_sheet' | 'profit_loss' | 'cash_flow'
  ): ValidationResult {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100
    };

    const mandatoryItems: Record<string, string[]> = {
      balance_sheet: [
        'total_assets',
        'total_liabilities',
        'total_equity',
        'share_capital',
        'reserves_and_surplus'
      ],
      profit_loss: [
        'revenue_from_operations',
        'total_expenses',
        'profit_for_period',
        'basic_earnings_per_share',
        'diluted_earnings_per_share'
      ],
      cash_flow: [
        'cash_from_operations',
        'cash_from_investing',
        'cash_from_financing',
        'cash_end_of_period'
      ]
    };

    const required = mandatoryItems[statementType] || [];

    for (const itemKey of required) {
      const item = items.find(i => i.key === itemKey);
      if (!item || item.value === 0) {
        result.errors.push({
          check: 'mandatory_item_missing',
          message: `Mandatory item missing: ${itemKey}`,
          severity: 'high'
        });
        result.score -= 15;
      }
    }

    result.isValid = result.errors.filter(e => e.severity === 'high').length === 0;

    return result;
  }

  /**
   * Check for mathematical consistency
   */
  static validateMathematicalConsistency(
    items: Array<{ key: string; value: number }>
  ): ValidationResult {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100
    };

    const getItemValue = (key: string) => items.find(i => i.key === key)?.value || 0;

    // Balance Sheet: Assets = Liabilities + Equity
    const assets = getItemValue('total_assets');
    const liabilities = getItemValue('total_liabilities');
    const equity = getItemValue('total_equity');
    const bsDifference = Math.abs(assets - (liabilities + equity));

    if (bsDifference > 0.01 * assets) {
      result.errors.push({
        check: 'balance_sheet_equation',
        message: `Balance sheet equation doesn't balance. Assets (${assets}) != Liabilities (${liabilities}) + Equity (${equity}). Difference: ${bsDifference}`,
        severity: 'high',
        actualValue: assets,
        expectedValue: liabilities + equity
      });
      result.score -= 30;
    }

    // Cash Flow: Opening + Changes = Closing
    const cashOpening = getItemValue('cash_beginning_of_period');
    const cashChanges = getItemValue('net_increase_decrease_cash');
    const cashClosing = getItemValue('cash_end_of_period');
    const cfDifference = Math.abs((cashOpening + cashChanges) - cashClosing);

    if (cfDifference > 0.01 * Math.abs(cashOpening)) {
      result.errors.push({
        check: 'cash_flow_equation',
        message: `Cash flow equation doesn't balance. Opening (${cashOpening}) + Changes (${cashChanges}) != Closing (${cashClosing}). Difference: ${cfDifference}`,
        severity: 'high',
        actualValue: cashClosing,
        expectedValue: cashOpening + cashChanges
      });
      result.score -= 30;
    }

    result.isValid = result.errors.filter(e => e.severity === 'high').length === 0;

    return result;
  }

  /**
   * Generate validation report
   */
  static generateValidationReport(results: {
    balanceSheet?: ValidationResult;
    profitLoss?: ValidationResult;
    cashFlow?: ValidationResult;
  }): string {
    let report = 'Ind AS Validation Report\n';
    report += '='.repeat(50) + '\n\n';

    const statements = [
      { name: 'Balance Sheet', result: results.balanceSheet },
      { name: 'Profit & Loss', result: results.profitLoss },
      { name: 'Cash Flow', result: results.cashFlow }
    ];

    for (const statement of statements) {
      if (!statement.result) continue;

      report += `${statement.name}:\n`;
      report += '-'.repeat(30) + '\n';
      report += `Status: ${statement.result.isValid ? '✓ Valid' : '✗ Invalid'}\n`;
      report += `Score: ${statement.result.score}/100\n\n`;

      if (statement.result.errors.length > 0) {
        report += 'Errors:\n';
        for (const error of statement.result.errors) {
          report += `  [${error.severity.toUpperCase()}] ${error.check}: ${error.message}\n`;
        }
        report += '\n';
      }

      if (statement.result.warnings.length > 0) {
        report += 'Warnings:\n';
        for (const warning of statement.result.warnings) {
          report += `  [${warning.severity.toUpperCase()}] ${warning.check}: ${warning.message}\n`;
        }
        report += '\n';
      }
    }

    return report;
  }
}

export default IndASValidator;