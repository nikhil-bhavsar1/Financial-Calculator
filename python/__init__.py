"""
Financial Term Matching System - Main Integration Module
========================================================
High-level API for the complete financial term matching system.
"""

import json
import sys
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from preprocessing import TextPreprocessor, PreprocessingResult
from matching_engine import MultiLayerMatchingEngine, MatchResult, MatchingSession
from validation import ValidationFramework, DEFAULT_GOLDEN_SET
from config import MATCHING_CONFIG, VALIDATION_THRESHOLDS
from terminology_keywords import get_database_stats, print_database_summary


class FinancialTermMatcher:
    """
    Main interface for the Financial Term Matching System.
    
    Provides a simple, high-level API for:
    - Preprocessing financial text
    - Matching terms against the unified database
    - Validating results
    - Generating reports
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the matcher.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or MATCHING_CONFIG
        self.preprocessor = TextPreprocessor(self.config)
        self.engine = MultiLayerMatchingEngine(self.config)
        self.validator = ValidationFramework()
        
        # Statistics tracking
        self.session_count = 0
        self.total_lines_processed = 0
        self.total_matches_found = 0
    
    def preprocess(self, text: str, line_number: Optional[int] = None) -> PreprocessingResult:
        """
        Preprocess financial text.
        
        Args:
            text: Raw text to preprocess
            line_number: Optional line number
            
        Returns:
            PreprocessingResult with cleaned and canonical forms
        """
        return self.preprocessor.preprocess(text, line_number)
    
    def match(self, text: str, line_number: Optional[int] = None) -> List[MatchResult]:
        """
        Match terms in a single line of text.
        
        Args:
            text: Text to match
            line_number: Optional line number
            
        Returns:
            List of match results
        """
        return self.engine.match_text(text, line_number)
    
    def match_document(
        self, 
        lines: List[str], 
        context: Optional[Dict] = None
    ) -> MatchingSession:
        """
        Match all terms in a document.
        
        Args:
            lines: List of text lines
            context: Optional context (section type, entity type, etc.)
            
        Returns:
            MatchingSession with all results
        """
        session = self.engine.match_document(lines, context)
        
        # Update statistics
        self.session_count += 1
        self.total_lines_processed += len(lines)
        self.total_matches_found += len(session.results)
        
        return session
    
    def match_file(self, file_path: Union[str, Path]) -> MatchingSession:
        """
        Match terms in a file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            MatchingSession with all results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Strip newlines
        lines = [line.strip() for line in lines if line.strip()]
        
        return self.match_document(lines)
    
    def validate(self, golden_set: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Run validation tests.
        
        Args:
            golden_set: Optional custom golden set
            
        Returns:
            Validation report
        """
        if golden_set:
            self.validator.load_golden_set(golden_set)
        else:
            self.validator.load_golden_set(DEFAULT_GOLDEN_SET)
        
        return self.validator.run_all_validations()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'sessions_processed': self.session_count,
            'total_lines_processed': self.total_lines_processed,
            'total_matches_found': self.total_matches_found,
            'average_matches_per_line': (
                self.total_matches_found / max(self.total_lines_processed, 1)
            ),
            'database_stats': get_database_stats()
        }
    
    def export_results(
        self, 
        session: MatchingSession, 
        output_path: Union[str, Path],
        format: str = 'json'
    ) -> None:
        """
        Export matching results to file.
        
        Args:
            session: MatchingSession to export
            output_path: Output file path
            format: Export format ('json' or 'csv')
        """
        output_path = Path(output_path)
        
        if format == 'json':
            results = {
                'matches': [
                    {
                        'term_key': m.term_key,
                        'term_label': m.term_label,
                        'match_type': m.match_type,
                        'confidence_score': m.confidence_score,
                        'original_text': m.original_text,
                        'line_number': m.line_number,
                        'category': m.category
                    }
                    for m in session.results
                ],
                'unmatched_lines': [
                    {'line_number': num, 'text': text}
                    for num, text in session.unmatched_lines
                ],
                'statistics': self.engine.get_match_summary(session)
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        
        elif format == 'csv':
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Line Number', 'Term Key', 'Term Label', 'Match Type',
                    'Confidence Score', 'Original Text', 'Category'
                ])
                
                for m in session.results:
                    writer.writerow([
                        m.line_number,
                        m.term_key,
                        m.term_label,
                        m.match_type,
                        f"{m.confidence_score:.3f}",
                        m.original_text,
                        m.category
                    ])
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def print_summary(self, session: MatchingSession) -> None:
        """
        Print a summary of matching results.
        
        Args:
            session: MatchingSession to summarize
        """
        summary = self.engine.get_match_summary(session)
        
        print("\n" + "="*60)
        print("MATCHING RESULTS SUMMARY")
        print("="*60)
        print(f"Total Lines Processed:    {summary['total_lines']}")
        print(f"Lines Matched:            {summary['matched_lines']}")
        print(f"Lines Unmatched:          {summary['unmatched_lines']}")
        print(f"Match Rate:               {summary['match_rate']:.1%}")
        print(f"\nTotal Matches Found:      {summary['total_matches']}")
        print(f"Unique Terms Matched:     {summary['unique_terms']}")
        print(f"\nConfidence Distribution:")
        print(f"  High (≥80%):            {summary['confidence_distribution']['high']}")
        print(f"  Medium (50-80%):        {summary['confidence_distribution']['medium']}")
        print(f"  Low (<50%):             {summary['confidence_distribution']['low']}")
        print(f"\nMatch Type Distribution:")
        for match_type, count in summary['match_type_distribution'].items():
            print(f"  {match_type:20s}: {count}")
        print("="*60 + "\n")


# Convenience function for quick matching
def match_terms(text: str) -> List[Dict[str, Any]]:
    """
    Quick function to match terms in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of match dictionaries
    """
    matcher = FinancialTermMatcher()
    matches = matcher.match(text)
    
    return [
        {
            'term_key': m.term_key,
            'term_label': m.term_label,
            'confidence': m.confidence_score,
            'match_type': m.match_type,
            'category': m.category
        }
        for m in matches
    ]


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Financial Term Matching System'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Input file or text to process'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run validation tests'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file path'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    if args.stats:
        print_database_summary()
        return
    
    if args.validate:
        matcher = FinancialTermMatcher()
        results = matcher.validate()
        print(json.dumps(results, indent=2))
        return
    
    if not args.input:
        parser.print_help()
        return
    
    # Process input
    matcher = FinancialTermMatcher()
    
    # Check if input is a file
    input_path = Path(args.input)
    if input_path.exists():
        session = matcher.match_file(input_path)
    else:
        # Treat as text
        lines = args.input.split('\n')
        session = matcher.match_document(lines)
    
    # Print summary
    matcher.print_summary(session)
    
    # Export if output path provided
    if args.output:
        matcher.export_results(session, args.output, args.format)
        print(f"Results exported to: {args.output}")


if __name__ == '__main__':
    main()
