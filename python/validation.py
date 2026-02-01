"""
Financial Term Matching System - Validation Framework
======================================================
Quality assurance and testing framework for the matching system.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from matching_engine import MultiLayerMatchingEngine, MatchResult
from preprocessing import TextPreprocessor


@dataclass
class ValidationResult:
    """Result of validation test"""
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoldenSetTest:
    """Golden set test case"""
    input_text: str
    expected_terms: List[str]
    line_number: int = 0
    section_context: Optional[str] = None


class ValidationFramework:
    """
    Comprehensive validation framework for the matching system.
    """
    
    def __init__(self):
        self.engine = MultiLayerMatchingEngine()
        self.preprocessor = TextPreprocessor()
        self.golden_set: List[GoldenSetTest] = []
        self.validation_history: List[Dict] = []
    
    def load_golden_set(self, test_cases: List[Dict]) -> None:
        """
        Load golden set test cases.
        
        Args:
            test_cases: List of test case dictionaries
        """
        self.golden_set = []
        for case in test_cases:
            self.golden_set.append(GoldenSetTest(
                input_text=case['input'],
                expected_terms=case['expected_terms'],
                line_number=case.get('line_number', 0),
                section_context=case.get('section_context')
            ))
    
    def run_golden_set_tests(self) -> Dict[str, Any]:
        """
        Run all golden set tests and calculate metrics.
        
        Returns:
            Dictionary with test results and metrics
        """
        results = []
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for test in self.golden_set:
            matches = self.engine.match_text(test.input_text, test.line_number)
            matched_terms = [m.term_key for m in matches]
            
            # Calculate metrics
            expected_set = set(test.expected_terms)
            matched_set = set(matched_terms)
            
            tp = len(expected_set & matched_set)
            fp = len(matched_set - expected_set)
            fn = len(expected_set - matched_set)
            
            true_positives += tp
            false_positives += fp
            false_negatives += fn
            
            results.append({
                'input': test.input_text,
                'expected': test.expected_terms,
                'matched': matched_terms,
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn,
                'passed': fp == 0 and fn == 0
            })
        
        # Calculate aggregate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'total_tests': len(self.golden_set),
            'passed_tests': sum(1 for r in results if r['passed']),
            'failed_tests': sum(1 for r in results if not r['passed']),
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'detailed_results': results
        }
    
    def run_preprocessing_tests(self) -> List[ValidationResult]:
        """
        Run preprocessing validation tests.
        
        Returns:
            List of validation results
        """
        test_cases = [
            {
                'name': 'Abbreviation Expansion',
                'input': 'PPE & CWIP (Note 12)',
                'expected_canonical': 'property plant equipment and capital work in progress',
                'expected_abbr': ['ppe', 'cwip']
            },
            {
                'name': 'Note Reference Removal',
                'input': 'Trade Receivables (see note 5)',
                'expected_canonical': 'trade receivables',
                'expected_notes_removed': ['note_ref:(see note 5)']
            },
            {
                'name': 'Sign Convention Detection',
                'input': 'Less: Provision for Doubtful Debts',
                'expected_sign': -1
            },
            {
                'name': 'Parenthetical Numbers',
                'input': 'Loss on Sale (1,234)',
                'expected_canonical_contains': '-1234'
            },
            {
                'name': 'Unicode Normalization',
                'input': 'Property, Plant & Equipment—Net',
                'expected_canonical': 'property plant and equipment net'
            }
        ]
        
        results = []
        for test in test_cases:
            preprocessed = self.preprocessor.preprocess(test['input'])
            
            passed = True
            details = {}
            
            if 'expected_canonical' in test:
                passed = passed and (preprocessed.canonical_form == test['expected_canonical'])
                details['canonical'] = preprocessed.canonical_form
            
            if 'expected_abbr' in test:
                detected = preprocessed.detected_abbreviations
                passed = passed and all(abbr in detected for abbr in test['expected_abbr'])
                details['detected_abbr'] = detected
            
            if 'expected_sign' in test:
                passed = passed and (preprocessed.sign_multiplier == test['expected_sign'])
                details['sign_multiplier'] = preprocessed.sign_multiplier
            
            results.append(ValidationResult(
                test_name=test['name'],
                passed=passed,
                expected=test,
                actual=details
            ))
        
        return results
    
    def run_performance_tests(self, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Run performance benchmarks.
        
        Args:
            sample_size: Number of lines to process for benchmark
            
        Returns:
            Performance metrics
        """
        # Generate sample lines
        sample_lines = [
            f"Line {i}: Property Plant and Equipment {i * 1000}"
            for i in range(sample_size)
        ]
        
        # Test preprocessing performance
        start_time = time.time()
        for line in sample_lines:
            self.preprocessor.preprocess(line)
        preprocessing_time = time.time() - start_time
        
        # Test matching performance
        start_time = time.time()
        for line in sample_lines:
            self.engine.match_text(line)
        matching_time = time.time() - start_time
        
        # Test full pipeline performance
        start_time = time.time()
        session = self.engine.match_document(sample_lines)
        pipeline_time = time.time() - start_time
        
        return {
            'sample_size': sample_size,
            'preprocessing_time': preprocessing_time,
            'matching_time': matching_time,
            'pipeline_time': pipeline_time,
            'preprocessing_speed': sample_size / preprocessing_time,
            'matching_speed': sample_size / matching_time,
            'pipeline_speed': sample_size / pipeline_time,
            'target_speed_met': (sample_size / pipeline_time) >= 1000  # Target: 1000 lines/sec
        }
    
    def generate_coverage_report(self, unmatched_terms: List[Tuple[int, str]]) -> Dict[str, Any]:
        """
        Generate coverage report for unmatched terms.
        
        Args:
            unmatched_terms: List of (line_number, text) tuples
            
        Returns:
            Coverage report
        """
        # Count frequency of unmatched terms
        term_frequency = defaultdict(int)
        for line_num, text in unmatched_terms:
            # Extract key words from unmatched text
            words = text.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    term_frequency[word] += 1
        
        # Get top 20 unmatched terms
        top_unmatched = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            'total_unmatched': len(unmatched_terms),
            'unique_unmatched_terms': len(term_frequency),
            'top_unmatched_terms': top_unmatched,
            'coverage_percentage': 0  # Will be calculated with context
        }
    
    def run_all_validations(self) -> Dict[str, Any]:
        """
        Run all validation tests.
        
        Returns:
            Complete validation report
        """
        print("\n" + "="*60)
        print("RUNNING COMPREHENSIVE VALIDATION SUITE")
        print("="*60)
        
        # 1. Preprocessing tests
        print("\n1. Running Preprocessing Tests...")
        preprocessing_results = self.run_preprocessing_tests()
        preprocessing_passed = sum(1 for r in preprocessing_results if r.passed)
        preprocessing_total = len(preprocessing_results)
        print(f"   Passed: {preprocessing_passed}/{preprocessing_total}")
        
        # 2. Golden set tests
        print("\n2. Running Golden Set Tests...")
        golden_results = self.run_golden_set_tests()
        print(f"   Precision: {golden_results['precision']:.2%}")
        print(f"   Recall: {golden_results['recall']:.2%}")
        print(f"   F1 Score: {golden_results['f1_score']:.2%}")
        print(f"   Tests Passed: {golden_results['passed_tests']}/{golden_results['total_tests']}")
        
        # 3. Performance tests
        print("\n3. Running Performance Tests...")
        performance_results = self.run_performance_tests()
        print(f"   Processing Speed: {performance_results['pipeline_speed']:.0f} lines/sec")
        print(f"   Target Met: {performance_results['target_speed_met']}")
        
        # Compile report
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'preprocessing': {
                'tests_run': preprocessing_total,
                'tests_passed': preprocessing_passed,
                'success_rate': preprocessing_passed / preprocessing_total if preprocessing_total > 0 else 0,
                'details': [
                    {
                        'name': r.test_name,
                        'passed': r.passed
                    }
                    for r in preprocessing_results
                ]
            },
            'golden_set': golden_results,
            'performance': performance_results,
            'overall_status': 'PASS' if (
                preprocessing_passed == preprocessing_total and
                golden_results['recall'] >= 0.95 and
                golden_results['precision'] >= 0.95 and
                performance_results['target_speed_met']
            ) else 'FAIL'
        }
        
        self.validation_history.append(report)
        
        print("\n" + "="*60)
        print(f"OVERALL STATUS: {report['overall_status']}")
        print("="*60 + "\n")
        
        return report


# Default golden set for testing
DEFAULT_GOLDEN_SET = [
    {
        'input': 'Property, Plant and Equipment',
        'expected_terms': ['property_plant_equipment'],
        'line_number': 1
    },
    {
        'input': 'Trade Receivables (Note 12)',
        'expected_terms': ['trade_receivables'],
        'line_number': 2
    },
    {
        'input': 'Capital Work in Progress',
        'expected_terms': ['capital_work_in_progress'],
        'line_number': 3
    },
    {
        'input': 'Goodwill on Consolidation',
        'expected_terms': ['goodwill'],
        'line_number': 4
    },
    {
        'input': 'Total Revenue from Operations',
        'expected_terms': ['total_revenue'],
        'line_number': 5
    },
    {
        'input': 'PPE & CWIP',
        'expected_terms': ['property_plant_equipment', 'capital_work_in_progress'],
        'line_number': 6
    },
    {
        'input': 'EBITDA for the year',
        'expected_terms': ['ebitda'],
        'line_number': 7
    },
    {
        'input': 'Cash and Cash Equivalents',
        'expected_terms': ['cash_and_equivalents'],
        'line_number': 8
    },
    {
        'input': 'Long-term Borrowings',
        'expected_terms': ['long_term_borrowings'],
        'line_number': 9
    },
    {
        'input': 'Inventories (Raw Materials)',
        'expected_terms': ['inventories'],
        'line_number': 10
    }
]


def run_validation():
    """Run complete validation suite."""
    framework = ValidationFramework()
    framework.load_golden_set(DEFAULT_GOLDEN_SET)
    return framework.run_all_validations()


if __name__ == '__main__':
    results = run_validation()
    print(json.dumps(results, indent=2))
