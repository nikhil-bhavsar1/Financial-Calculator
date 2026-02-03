
# =============================================================================
# SECTION 45: FOREIGN CURRENCY TRANSACTIONS
# =============================================================================

FOREIGN_CURRENCY_TRANSACTIONS = {
    'functional_currency': {
        'determination_of_functional_currency': [
            'functional_currency',
            'primary_economic_environment',
            'currency_influencing_sales_prices',
            'currency_of_country_whose_competitive_forces_determine_sales_prices',
            'currency_influencing_labor_material_costs',
            'currency_in_which_funds_generated',
            'currency_in_which_receipts_retained',
            'change_in_functional_currency',
            'prospective_application_of_change',
        ],
        'foreign_operations': [
            'foreign_operation',
            'subsidiaries_with_different_functional_currency',
            'branches_with_different_functional_currency',
            'degree_of_autonomy',
            'frequency_of_transactions_with_reporting_entity',
            'cash_flow_interdependence',
            'sufficiency_of_cash_flows_for_debt_service',
        ],
    },
    'reporting_foreign_currency_transactions': {
        'initial_recognition': [
            'foreign_currency_transaction',
            'spot_exchange_rate',
            'exchange_rate_at_date_of_transaction',
            'average_rate_approximation',
        ],
        'reporting_at_subsequent_dates': [
            'monetary_items',
            'non_monetary_items_at_historical_cost',
            'non_monetary_items_at_fair_value',
            'closing_rate',
            'exchange_rate_at_date_of_valuation',
        ],
        'recognition_of_exchange_differences': [
            'exchange_differences',
            'foreign_exchange_gain_loss',
            'realized_gain_loss',
            'unrealized_gain_loss',
            'settlement_of_monetary_items',
            'retranslation_of_monetary_items',
            'recognition_in_profit_or_loss',
            'recognition_in_oci_for_non_monetary_items',
            'long_term_foreign_currency_monetary_items',
            'fcmitr',
            'foreign_currency_monetary_item_translation_difference_account',
            'amortization_of_exchange_differences',
        ],
    },
    'translation_to_presentation_currency': {
        'translation_procedures': [
            'presentation_currency',
            'translation_from_functional_to_presentation',
            'assets_at_closing_rate',
            'liabilities_at_closing_rate',
            'income_at_exchange_rates_at_dates_of_transactions',
            'expenses_at_exchange_rates_at_dates_of_transactions',
            'resulting_exchange_differences_in_oci',
            'foreign_currency_translation_reserve',
            'fctr',
        ],
        'disposal_of_foreign_operation': [
            'disposal_of_foreign_operation',
            'partial_disposal',
            'reclassification_of_fctr_to_profit_or_loss',
            'cumulative_exchange_differences',
        ],
    },
    'hyperinflationary_economies': [
        'financial_reporting_in_hyperinflationary_economies',
        'restatement_of_financial_statements',
        'selection_of_general_price_index',
        'gain_or_loss_on_net_monetary_position',
    ],
    'disclosures': {
        'exchange_differences': [
            'amount_of_exchange_differences_in_profit_or_loss',
            'net_exchange_differences_in_oci',
            'reconciliation_of_fctr',
        ],
        'currency_information': [
            'functional_currency_of_entity',
            'presentation_currency_of_entity',
            'reason_for_using_different_presentation_currency',
            'reason_for_change_in_functional_currency',
        ],
        'hedging_information': [
            'foreign_currency_risk_management',
            'hedging_of_foreign_currency_exposure',
            'derivative_financial_instruments',
            'forward_exchange_contracts',
            'currency_options',
            'currency_swaps',
            'unhedged_foreign_currency_exposure',
        ],
    },
}

# =============================================================================
# SECTION 46: BORROWING COSTS
# =============================================================================

BORROWING_COSTS = {
    'recognition_principles': {
        'general_rule': [
            'expensing_borrowing_costs',
            'capitalization_of_borrowing_costs',
            'directly_attributable_to_acquisition_construction_production',
            'qualifying_asset_requirement',
        ],
        'qualifying_assets': [
            'qualifying_assets',
            'assets_requiring_substantial_period_to_get_ready',
            'inventories_requiring_substantial_period',
            'manufacturing_plants',
            'power_generation_facilities',
            'intangible_assets_in_development',
            'investment_properties_under_construction',
        ],
    },
    'borrowing_costs_components': [
        'borrowing_costs',
        'interest_expense_effective_interest_method',
        'finance_charges_for_leases',
        'exchange_differences_as_adjustment_to_interest',
        'commitment_charges',
        'processing_fees',
        'guarantee_fees',
        'ancillary_costs_for_borrowings',
    ],
    'measurement_of_capitalization': {
        'specific_borrowings': [
            'capitalization_of_actual_borrowing_costs',
            'less_investment_income_on_temporary_investment',
            'borrowings_specifically_for_qualifying_asset',
        ],
        'general_borrowings': [
            'capitalization_rate',
            'weighted_average_of_borrowing_costs',
            'expenditure_on_qualifying_asset',
            'amount_capitalized_cannot_exceed_costs_incurred',
        ],
    },
    'commencement_suspension_and_cessation': {
        'commencement': [
            'commencement_of_capitalization',
            'expenditures_for_asset_incurred',
            'borrowing_costs_incurred',
            'activities_necessary_to_prepare_asset',
        ],
        'suspension': [
            'suspension_of_capitalization',
            'extended_periods_of_interruption',
            'active_development_suspended',
        ],
        'cessation': [
            'cessation_of_capitalization',
            'substantially_all_activities_complete',
            'physical_construction_complete',
            'ready_for_intended_use_or_sale',
            'part_ready_for_use_capitalization_ceases_for_part',
        ],
    },
    'disclosures': [
        'amount_of_borrowing_costs_capitalized',
        'capitalization_rate_used',
        'accounting_policy_for_borrowing_costs',
        'qualifying_assets_description',
    ],
}

# =============================================================================
# SECTION 47: IMPAIRMENT OF ASSETS
# =============================================================================

IMPAIRMENT_OF_ASSETS = {
    'identifying_impaired_assets': {
        'impairment_indicators': {
            'external_sources': [
                'market_value_declines',
                'significant_changes_in_environment',
                'market_interest_rates_increase',
                'carrying_amount_exceeds_market_capitalization',
            ],
            'internal_sources': [
                'obsolescence_or_physical_damage',
                'asset_is_idle',
                'plans_to_discontinue_operations',
                'plans_to_dispose_of_asset',
                'internal_reporting_suggests_poor_performance',
            ],
        },
        'annual_testing_requirements': [
            'annual_impairment_testing',
            'impairment_test_for_goodwill',
            'impairment_test_for_intangibles_with_indefinite_life',
            'impairment_test_for_intangibles_not_yet_available_for_use',
        ],
    },
    'measurement_of_recoverable_amount': {
        'recoverable_amount': [
            'recoverable_amount_calculation',
            'higher_of_fair_value_less_costs_of_disposal',
            'value_in_use',
            'measurement_principles',
        ],
        'fair_value_less_costs_of_disposal': [
            'fair_value_measurement',
            'costs_of_disposal',
            'legal_costs',
            'stamp_duty',
            'transaction_taxes',
            'costs_of_removing_asset',
            'incremental_costs_to_dispose',
        ],
        'value_in_use': {
            'calculation_elements': [
                'expected_future_cash_flows',
                'variations_in_amount_or_timing',
                'time_value_of_money',
                'price_for_bearing_uncertainty',
                'other_factors_liquidity_etc',
            ],
            'cash_flow_projections': [
                'reasonable_and_supportable_assumptions',
                'most_recent_financial_budgets_forecasts',
                'maximum_five_year_projections',
                'extrapolation_using_growth_rate',
                'foreign_currency_cash_flows',
                'pre_tax_cash_flows',
            ],
            'discount_rate': [
                'pre_tax_discount_rate',
                'reflects_current_market_assessments',
                'time_value_of_money_risk',
                'risks_specific_to_asset_not_adjusted_in_cash_flows',
                'wacc',
                'incremental_borrowing_rate',
            ],
        },
    },
    'recognition_of_impairment_loss': {
        'individual_assets': [
            'impairment_loss_recognition',
            'carrying_amount_exceeds_recoverable_amount',
            'recognition_in_profit_or_loss',
            'adjustment_to_revaluation_surplus',
            'revalued_assets_impairment',
            'revised_depreciation_after_impairment',
        ],
        'cash_generating_units': {
            'cgu_identification': [
                'cash_generating_unit',
                'smallest_identifiable_group_of_assets',
                'independent_cash_inflows',
                'cgu_determination',
                'consistency_in_cgu_identification',
            ],
            'allocation_of_goodwill': [
                'allocation_of_goodwill_to_cgus',
                'lowest_level_at_which_goodwill_monitored',
                'operating_segments',
                'reassignment_of_goodwill',
                'goodwill_on_disposal_of_operation',
            ],
            'corporate_assets': [
                'corporate_assets',
                'group_headquarters_assets',
                'it_equipment_for_group',
                'research_center_assets',
                'allocation_to_cgus',
            ],
            'allocation_of_impairment_loss': [
                'allocation_to_goodwill_first',
                'pro_rata_allocation_to_other_assets',
                'carrying_amount_floor',
            ],
        },
    },
    'reversal_of_impairment_loss': [
        'reversal_of_impairment_loss_assessment',
        'indicators_for_reversal',
        'reversal_for_individual_assets',
        'reversal_for_cgus',
        'no_reversal_for_goodwill',
        'limitations_on_reversal',
        'increase_in_carrying_amount_on_reversal',
        'recognition_in_profit_or_loss_or_oci',
    ],
    'disclosures_for_impairment': {
        'by_class_of_assets': [
            'impairment_losses_recognized',
            'impairment_losses_reversed',
            'line_items_in_profit_or_loss',
            'oci_adjustments',
        ],
        'for_significant_losses': [
            'events_and_circumstances_leading_to_loss',
            'amount_of_loss_or_reversal',
            'nature_of_asset_or_cgu',
            'reporting_segment',
            'basis_for_recoverable_amount',
            'fair_value_hierarchy_info',
            'valuation_techniques_used',
            'discount_rates_used',
        ],
        'goodwill_and_indefinite_life_intangibles': [
            'carrying_amount_allocated_to_cgus',
            'basis_on_which_recoverable_amount_determined',
            'key_assumptions_used',
            'growth_rates',
            'discount_rates',
            'sensitivity_analysis',
            'changes_in_assumptions_needed_to_cause_impairment',
        ],
    },
}

# =============================================================================
# SECTION 48: EVENTS AFTER REPORTING PERIOD
# =============================================================================

EVENTS_AFTER_REPORTING_PERIOD = {
    'classification': {
        'adjusting_events': [
            'adjusting_events',
            'evidence_of_conditions_existing_at_reporting_date',
            'settlement_of_court_case',
            'bankruptcy_after_reporting_date',
            'sale_of_inventories_after_reporting_date',
            'determination_of_cost_or_proceeds_after_reporting_date',
            'determination_of_profit_sharing_or_bonus',
            'discovery_of_fraud_or_errors',
        ],
        'non_adjusting_events': [
            'non_adjusting_events',
            'conditions_arising_after_reporting_date',
            'decline_in_market_value_of_investments',
            'major_business_combination',
            'disposal_of_major_subsidiary',
            'announcing_plan_to_discontinue_operation',
            'major_purchases_of_assets',
            'expropriation_of_major_assets',
            'destruction_of_major_plant_by_fire',
            'announcing_major_restructuring',
            'major_ordinary_share_transactions',
            'abnormally_large_changes_in_asset_prices',
            'changes_in_tax_rates_or_laws',
            'entering_into_significant_commitments',
            'commencing_major_litigation',
        ],
    },
    'recognition_and_measurement': [
        'adjustment_of_amounts_in_financial_statements',
        'updating_disclosures_about_conditions_at_reporting_date',
        'no_adjustment_for_non_adjusting_events',
        'going_concern_assessment_impact',
        'deterioration_in_operating_results_after_reporting_date',
    ],
    'dividends': [
        'dividends_declared_after_reporting_date',
        'not_recognized_as_liability_at_reporting_date',
        'disclosure_in_notes',
        'proposed_dividends',
    ],
    'going_concern': [
        'going_concern_no_longer_appropriate',
        'intention_to_liquidate_entity',
        'no_realistic_alternative_to_liquidation',
        'preparation_on_other_than_going_concern_basis',
    ],
    'disclosures': [
        'date_of_authorization_for_issue',
        'who_gave_the_authorization',
        'power_to_amend_financial_statements',
        'disclosure_of_non_adjusting_events',
        'nature_of_event',
        'estimate_of_financial_effect',
        'statement_that_effect_cannot_be_estimated',
        'updating_disclosures_about_conditions_at_reporting_date',
    ],
}
