/**
 * MCAXBRLExtractor
 * Extract from Indian MCA XBRL filings (Ind AS taxonomy)
 * Handles Ind AS specific XBRL instance documents from Ministry of Corporate Affairs
 */

export interface XBRLFact {
  concept: string;
  value: number | string;
  unit?: string;
  context: string;
  period: string;
  dimensions: Record<string, string>;
  decimals?: number;
  isNil?: boolean;
}

export interface XBRLContext {
  id: string;
  entity: {
    identifier: string;
    scheme: string;
  };
  period: {
    instant?: string;
    startDate?: string;
    endDate?: string;
  };
  dimensions: Record<string, string>;
}

export interface XBRLUnit {
  id: string;
  measure: string;
  division?: number[];
}

export class MCAXBRLExtractor {
  private static readonly IND_AS_TAXONOMY_PREFIX = 'ind-as:';
  private static readonly MCA_EXTENSION_PREFIX = 'in-mca:';

  // Define Ind AS namespaces
  private static readonly NAMESPACES = {
    'ind-as': 'http://xbrl.org/in/gaap/in-as/2020-03-31',
    'in-mca': 'http://www.mca.gov.in/xbrl/in-mca',
    'xbrli': 'http://www.xbrl.org/2003/instance',
    'xlink': 'http://www.w3.org/1999/xlink',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
  };

  /**
   * Extract from Ind AS XBRL instance document
   * This would typically be implemented in the backend (Python/Rust)
   * This is a TypeScript interface for the functionality
   */
  static async extractFromXBRL(xbrlPath: string): Promise<XBRLFact[]> {
    // This would need to be implemented in the backend
    // For now, returning empty array as this is a frontend interface
    console.log('MCAXBRLExtractor: extractFromXBRL called with', xbrlPath);

    // In a real implementation, this would:
    // 1. Parse the XML file
    // 2. Extract all facts with Ind AS namespace
    // 3. Parse values, units, contexts
    // 4. Return structured data

    return [];
  }

  /**
   * Parse Ind AS XBRL value formatting
   */
  static parseValue(valueStr: string | null, decimals?: string): number {
    if (!valueStr) {
      return 0.0;
    }

    // Handle negative values (often in parentheses in Ind AS XBRL)
    if (valueStr.includes('(') && valueStr.includes(')')) {
      valueStr = valueStr.replace('(', '').replace(')', '');
      return -parseFloat(valueStr);
    }

    return parseFloat(valueStr);
  }

  /**
   * Map Ind AS taxonomy concept to canonical metric key
   */
  static mapIndASToCanonical(indAsConcept: string): string | null {
    const mapping: Record<string, string> = {
      // Balance Sheet - Assets
      'OtherEquity': 'reserves_and_surplus',
      'CapitalWorkInProgress': 'capital_work_in_progress',
      'PropertyPlantEquipment': 'property_plant_equipment',
      'IntangibleAssets': 'intangible_assets',
      'InvestmentProperty': 'investment_properties',
      'BiologicalAssets': 'biological_assets',
      'InvestmentsInSubsidiaries': 'investments_in_subsidiaries',
      'InvestmentsInAssociates': 'investments_in_associates',
      'InvestmentsInJointVentures': 'investments_in_joint_ventures',
      'FinancialAssetsFVTPL': 'financial_assets_fvtpl',
      'FinancialAssetsFVTOCI': 'financial_assets_fvtoci',
      'FinancialAssetsAmortizedCost': 'financial_assets_amortized_cost',
      'DeferredTaxAssets': 'deferred_tax_assets',
      'Inventories': 'inventories',
      'TradeReceivables': 'trade_receivables',
      'ContractAssets': 'contract_assets',
      'CashAndCashEquivalents': 'cash_and_equivalents',
      'BankBalancesOtherThanCash': 'bank_balances_other',
      'CurrentInvestments': 'short_term_investments',
      'PrepaidExpenses': 'prepaid_expenses',
      'LoansAndAdvances': 'loans_to_directors',
      'CurrentMaturitiesOfLongTermDebt': 'current_maturities_long_term_debt',

      // Balance Sheet - Liabilities & Equity
      'ShareCapital': 'share_capital',
      'SharePremium': 'share_capital_issued',
      'RetainedEarnings': 'reserves_and_surplus',
      'NonControllingInterests': 'non_controlling_interests',
      'TradePayables': 'trade_payables',
      'OtherFinancialLiabilities': 'other_financial_liabilities',
      'ContractLiabilities': 'contract_liabilities',
      'Provisions': 'provisions',
      'DeferredTaxLiabilities': 'deferred_tax_liabilities',
      'LongTermBorrowings': 'long_term_borrowings',
      'ShortTermBorrowings': 'short_term_borrowings',
      'EmployeeBenefitsObligation': 'employee_benefits_obligation',
      'OtherCurrentLiabilities': 'other_current_liabilities',

      // Income Statement
      'RevenueFromOperations': 'revenue_from_operations',
      'OtherIncome': 'other_income',
      'TotalIncome': 'total_income',
      'CostOfMaterialsConsumed': 'cost_of_materials_consumed',
      'EmployeeBenefitExpense': 'employee_benefit_expense',
      'FinanceCosts': 'finance_cost',
      'DepreciationAndAmortisationExpense': 'depreciation_and_amortization',
      'OtherExpenses': 'other_expenses',
      'TotalExpenses': 'total_expenses',
      'ProfitBeforeTax': 'profit_before_tax',
      'CurrentTax': 'current_tax',
      'DeferredTax': 'deferred_tax',
      'ProfitForTheYear': 'net_profit',
      'OtherComprehensiveIncome': 'other_comprehensive_income',
      'TotalComprehensiveIncome': 'total_comprehensive_income',
      'BasicEarningsPerShare': 'basic_earnings_per_share',
      'DilutedEarningsPerShare': 'diluted_earnings_per_share',

      // Cash Flow Statement
      'CashFromOperatingActivities': 'cash_from_operations',
      'CashFromInvestingActivities': 'cash_from_investing',
      'CashFromFinancingActivities': 'cash_from_financing',
      'NetIncreaseDecreaseInCashAndCashEquivalents': 'net_increase_decrease_cash',
      'CashAndCashEquivalentsAtBeginning': 'cash_beginning_of_period',
      'CashAndCashEquivalentsAtEnd': 'cash_end_of_period'
    };

    return mapping[indAsConcept] || null;
  }

  /**
   * Get unit from XBRL element
   */
  static getUnit(fact: any, namespaces: typeof MCAXBRLExtractor.NAMESPACES): string {
    // Extract unit reference from fact
    const unitRef = fact.getAttribute?.('unitRef');
    if (unitRef) {
      // In real implementation, look up unit from unit definitions
      return unitRef;
    }
    return '';
  }

  /**
   * Get context from XBRL fact
   */
  static getContext(fact: any, root: any, namespaces: typeof MCAXBRLExtractor.NAMESPACES): string {
    const contextRef = fact.getAttribute?.('contextRef');
    return contextRef || '';
  }

  /**
   * Get period from context
   */
  static getPeriod(contextId: string, root: any, namespaces: typeof MCAXBRLExtractor.NAMESPACES): string {
    // In real implementation, look up context and extract period
    return '';
  }

  /**
   * Get dimensions from context
   */
  static getDimensions(fact: any, root: any, namespaces: typeof MCAXBRLExtractor.NAMESPACES): Record<string, string> {
    const dimensions: Record<string, string> = {};

    // Extract dimensional information for segment reporting
    // This would include dimensions like:
    // - Segment (Business segment, Geographic segment)
    // - Consolidated vs Standalone
    // - Current year vs Previous year

    return dimensions;
  }

  /**
   * Validate XBRL document structure
   */
  static validateXBRLStructure(xmlContent: string): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check for required namespaces
    const requiredNamespaces = ['xbrli', 'ind-as'];
    for (const ns of requiredNamespaces) {
      if (!xmlContent.includes(`xmlns:${ns}`) && !xmlContent.includes(`xmlns="${this.NAMESPACES[ns as keyof typeof this.NAMESPACES]}"`)) {
        errors.push(`Missing required namespace: ${ns}`);
      }
    }

    // Check for MCA extensions
    if (!xmlContent.includes('in-mca')) {
      warnings.push('Document may be missing MCA-specific extensions');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Extract dimension information
   */
  static extractDimensions(xbrlFacts: XBRLFact[]): {
    hasSegmentData: boolean;
    hasStandaloneData: boolean;
    hasConsolidatedData: boolean;
    segments: string[];
    years: string[];
  } {
    const result = {
      hasSegmentData: false,
      hasStandaloneData: false,
      hasConsolidatedData: false,
      segments: [] as string[],
      years: [] as string[]
    };

    for (const fact of xbrlFacts) {
      // Check dimensions
      Object.keys(fact.dimensions).forEach(dimKey => {
        if (dimKey.includes('Segment')) {
          result.hasSegmentData = true;
          const segment = fact.dimensions[dimKey];
          if (segment && !result.segments.includes(segment)) {
            result.segments.push(segment);
          }
        }

        if (dimKey.includes('Consolidated')) {
          result.hasConsolidatedData = true;
        }

        if (dimKey.includes('Standalone')) {
          result.hasStandaloneData = true;
        }
      });

      // Extract years from periods
      if (fact.period && !result.years.includes(fact.period)) {
        result.years.push(fact.period);
      }
    }

    return result;
  }

  /**
   * Convert XBRL facts to financial items format
   */
  static convertToFinancialItems(facts: XBRLFact[]): Array<{
    id: string;
    label: string;
    value: number;
    period: string;
    unit: string;
    concept: string;
    dimensions: Record<string, string>;
  }> {
    return facts.map(fact => {
      const canonicalKey = this.mapIndASToCanonical(fact.concept);

      return {
        id: canonicalKey || fact.concept,
        label: fact.concept.replace(/([A-Z])/g, ' $1').trim(),
        value: typeof fact.value === 'number' ? fact.value : 0,
        period: fact.period,
        unit: fact.unit || 'INR',
        concept: fact.concept,
        dimensions: fact.dimensions
      };
    });
  }

  /**
   * Handle MCA specific XBRL extensions
   */
  static handleMCAExtensions(concept: string): {
    isMCAExtension: boolean;
    extensionType?: string;
    canonicalKey?: string;
  } {
    if (concept.startsWith(this.MCA_EXTENSION_PREFIX)) {
      const mcaConcept = concept.replace(this.MCA_EXTENSION_PREFIX, '');

      // Map MCA extensions to canonical keys
      const mcaMapping: Record<string, string> = {
        'MATCredit': 'mat_credit_entitlement',
        'StatutoryDues': 'statutory_dues',
        'ExportIncentives': 'export_incentives_receivable',
        'InterCorporateDeposits': 'inter_corporate_deposits'
      };

      return {
        isMCAExtension: true,
        extensionType: 'mca-specific',
        canonicalKey: mcaMapping[mcaConcept]
      };
    }

    return {
      isMCAExtension: false
    };
  }
}

export default MCAXBRLExtractor;