"""
Financial Term Matching System - Section Classifier
===================================================
ML-based and regex-based section classification for context awareness.
"""

import re
import math
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter


@dataclass
class SectionContext:
    """Context information for a document section"""
    section_type: str
    confidence: float
    start_line: int
    end_line: int
    header_text: str
    indicators: List[str] = field(default_factory=list)
    boost_terms: List[str] = field(default_factory=list)


class SectionClassifier:
    """
    Hybrid section classifier using regex patterns and statistical features.
    Detects Balance Sheet, Income Statement, Cash Flow, and Notes sections.
    """
    
    def __init__(self):
        # Section type patterns with confidence weights
        self.section_patterns = {
            'balance_sheet_assets': {
                'patterns': [
                    (r'\bassets?\b', 1.0),
                    (r'\bnon[-\s]?current\s+assets?\b', 2.0),
                    (r'\bcurrent\s+assets?\b', 2.0),
                    (r'\bproperty[\s,]+plant[\s,]+equipment\b', 2.5),
                    (r'\bppe\b', 2.0),
                    (r'\binventor(y|ies)\b', 1.5),
                    (r'\breceivables?\b', 1.5),
                    (r'\bcash\s+and\s+cash\s+equivalents\b', 2.0),
                    (r'\btotal\s+assets\b', 2.5),
                    (r'\bfixed\s+assets?\b', 2.0),
                    (r'\bintangible\s+assets?\b', 2.0),
                    (r'\bgoodwill\b', 1.5),
                    (r'\binvestments?\b', 1.0),
                ],
                'headers': [
                    r'\bassets?\b',
                    r'\bnon[-\s]?current\s+assets?\b',
                    r'\bcurrent\s+assets?\b',
                ],
                'boost_terms': [
                    'total_assets', 'ppe', 'inventory', 'receivables', 'cash',
                    'investments', 'intangible_assets', 'goodwill', 'cwip'
                ]
            },
            'balance_sheet_liabilities': {
                'patterns': [
                    (r'\bliabilit(y|ies)\b', 1.0),
                    (r'\bnon[-\s]?current\s+liabilit(y|ies)\b', 2.0),
                    (r'\bcurrent\s+liabilit(y|ies)\b', 2.0),
                    (r'\bborrowings?\b', 1.5),
                    (r'\blong[-\s]?term\s+borrowings?\b', 2.0),
                    (r'\bshort[-\s]?term\s+borrowings?\b', 2.0),
                    (r'\btrade\s+payables?\b', 2.0),
                    (r'\bprovisions?\b', 1.5),
                    (r'\bdeferred\s+tax\b', 2.0),
                    (r'\btotal\s+liabilit(y|ies)\b', 2.5),
                ],
                'headers': [
                    r'\bliabilit(y|ies)\b',
                    r'\bequity\s+and\s+liabilit(y|ies)\b',
                ],
                'boost_terms': [
                    'borrowings', 'trade_payables', 'provisions', 'deferred_tax',
                    'long_term_borrowings', 'short_term_borrowings'
                ]
            },
            'balance_sheet_equity': {
                'patterns': [
                    (r'\bequity\b', 1.0),
                    (r'\bshareholders?\s+(equity|funds?)\b', 2.5),
                    (r'\bshare\s+capital\b', 2.0),
                    (r'\breserves?\s+and\s+surplus\b', 2.0),
                    (r'\bretained\s+earnings?\b', 2.0),
                    (r'\bother\s+comprehensive\s+income\b', 2.0),
                    (r'\btotal\s+equity\b', 2.5),
                    (r'\bowners?\s+equity\b', 2.0),
                ],
                'headers': [
                    r'\bequity\b',
                    r'\bshareholders?\s+funds?\b',
                ],
                'boost_terms': [
                    'share_capital', 'reserves', 'retained_earnings',
                    'other_comprehensive_income', 'total_equity'
                ]
            },
            'income_statement': {
                'patterns': [
                    (r'\brevenue\b', 1.5),
                    (r'\brevenue\s+from\s+operations\b', 2.5),
                    (r'\bsales\b', 1.5),
                    (r'\bturnover\b', 1.5),
                    (r'\bexpenses?\b', 1.0),
                    (r'\bcost\s+of\s+(goods\s+sold|revenue)\b', 2.0),
                    (r'\bgross\s+profit\b', 2.0),
                    (r'\boperating\s+profit\b', 2.0),
                    (r'\bebitda\b', 2.5),
                    (r'\bebit\b', 2.0),
                    (r'\bprofit\s+before\s+tax\b', 2.0),
                    (r'\btax\s+expense\b', 1.5),
                    (r'\bprofit\s+for\s+the\s+year\b', 2.5),
                    (r'\bnet\s+(profit|income)\b', 2.5),
                    (r'\bearnings?\s+per\s+share\b', 2.0),
                    (r'\beps\b', 2.0),
                ],
                'headers': [
                    r'\bstatement\s+of\s+profit\s+and\s+loss\b',
                    r'\bprofit\s+and\s+loss\b',
                    r'\bincome\s+statement\b',
                    r'\bstatement\s+of\s+income\b',
                ],
                'boost_terms': [
                    'revenue', 'expenses', 'profit', 'ebitda', 'ebit',
                    'net_profit', 'gross_profit', 'operating_profit'
                ]
            },
            'cash_flow': {
                'patterns': [
                    (r'\bcash\s+flow\b', 2.0),
                    (r'\boperating\s+activities\b', 2.0),
                    (r'\binvesting\s+activities\b', 2.0),
                    (r'\bfinancing\s+activities\b', 2.0),
                    (r'\bnet\s+cash\s+from\b', 2.0),
                    (r'\bcapex\b', 1.5),
                    (r'\bcapital\s+expenditure\b', 1.5),
                    (r'\bdividends?\s+paid\b', 1.5),
                    (r'\bcash\s+and\s+cash\s+equivalents\s+at\s+(end|beginning)\b', 2.5),
                ],
                'headers': [
                    r'\bcash\s+flow\s+statement\b',
                    r'\bstatement\s+of\s+cash\s+flows?\b',
                ],
                'boost_terms': [
                    'cash_from_operations', 'cash_from_investing', 'cash_from_financing',
                    'capex', 'dividends_paid', 'net_cash_flow'
                ]
            },
            'notes': {
                'patterns': [
                    (r'\bnote\s*\d+\b', 1.5),
                    (r'\bnotes\s+to\s+(the\s+)?accounts\b', 2.5),
                    (r'\bsignificant\s+accounting\s+policies\b', 2.0),
                    (r'\bdisclosures?\b', 1.0),
                    (r'\bcontingent\s+liabilit(y|ies)\b', 1.5),
                    (r'\bcommitments?\b', 1.0),
                    (r'\brelated\s+part(y|ies)\b', 1.5),
                    (r'\bsegment\s+reporting\b', 1.5),
                ],
                'headers': [
                    r'\bnotes\s+to\s+the\s+accounts\b',
                    r'\bsignificant\s+accounting\s+policies\b',
                    r'^note\s*\d+',
                ],
                'boost_terms': [
                    'accounting_policies', 'disclosures', 'contingencies',
                    'commitments', 'related_parties'
                ]
            },
        }
        
        # Line position weights (sections typically appear in order)
        self.position_weights = {
            'balance_sheet_assets': 0.1,
            'balance_sheet_liabilities': 0.2,
            'balance_sheet_equity': 0.25,
            'income_statement': 0.4,
            'cash_flow': 0.6,
            'notes': 0.8,
        }
        
        # Minimum confidence threshold
        self.min_confidence = 0.3
    
    def classify_section(
        self, 
        lines: List[str], 
        start_line: int = 0,
        context_window: int = 5
    ) -> Optional[SectionContext]:
        """
        Classify a section of document lines.
        
        Args:
            lines: List of text lines in the section
            start_line: Starting line number
            context_window: Number of lines to analyze around headers
            
        Returns:
            SectionContext or None if no clear classification
        """
        if not lines:
            return None
        
        # Calculate scores for each section type
        scores = defaultdict(float)
        indicators = defaultdict(list)
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Skip empty lines
            if not line_lower:
                continue
            
            # Check for headers (higher weight)
            is_header = self._is_likely_header(line_lower, i, len(lines))
            header_weight = 2.0 if is_header else 1.0
            
            # Score each section type
            for section_type, config in self.section_patterns.items():
                # Check patterns
                for pattern, weight in config['patterns']:
                    if re.search(pattern, line_lower):
                        match_weight = weight * header_weight
                        scores[section_type] += match_weight
                        indicators[section_type].append(f"line_{i}:{pattern}")
                
                # Check explicit headers
                for header_pattern in config['headers']:
                    if re.search(header_pattern, line_lower):
                        scores[section_type] += 3.0  # Strong header bonus
                        indicators[section_type].append(f"header:{header_pattern}")
        
        # Normalize by line count
        for section_type in scores:
            scores[section_type] /= max(len(lines), 1)
        
        # Apply position bias
        relative_position = start_line / 1000  # Normalize
        for section_type, base_position in self.position_weights.items():
            position_diff = abs(relative_position - base_position)
            position_penalty = max(0, 1.0 - position_diff * 2)
            scores[section_type] *= (0.8 + 0.2 * position_penalty)
        
        # Find best match
        if not scores:
            return None
        
        best_section = max(scores, key=scores.get)
        best_score = scores[best_section]
        
        # Normalize to 0-1 confidence
        max_possible_score = 5.0  # Theoretical maximum per line
        confidence = min(best_score / max_possible_score, 1.0)
        
        if confidence < self.min_confidence:
            return None
        
        # Get boost terms
        boost_terms = self.section_patterns[best_section]['boost_terms']
        
        # Find header text
        header_text = ""
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            if self._is_likely_header(line.lower(), i, len(lines)):
                header_text = line.strip()
                break
        
        return SectionContext(
            section_type=best_section,
            confidence=confidence,
            start_line=start_line,
            end_line=start_line + len(lines) - 1,
            header_text=header_text,
            indicators=indicators[best_section][:10],  # Top 10 indicators
            boost_terms=boost_terms
        )
    
    def classify_document(
        self, 
        lines: List[str],
        min_section_lines: int = 3
    ) -> List[SectionContext]:
        """
        Classify all sections in a document.
        
        Args:
            lines: All lines in the document
            min_section_lines: Minimum lines to consider a section
            
        Returns:
            List of SectionContext objects
        """
        sections = []
        current_section_lines = []
        current_section_start = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this is a section break
            if self._is_section_break(line_stripped):
                # Classify previous section
                if len(current_section_lines) >= min_section_lines:
                    section = self.classify_section(
                        current_section_lines, 
                        current_section_start
                    )
                    if section:
                        sections.append(section)
                
                # Start new section
                current_section_lines = [line]
                current_section_start = i
            else:
                current_section_lines.append(line)
        
        # Classify final section
        if len(current_section_lines) >= min_section_lines:
            section = self.classify_section(
                current_section_lines, 
                current_section_start
            )
            if section:
                sections.append(section)
        
        return sections
    
    def _is_likely_header(
        self, 
        line: str, 
        position: int, 
        total_lines: int
    ) -> bool:
        """
        Determine if a line is likely a section header.
        
        Args:
            line: Line text (lowercase)
            position: Line position in section
            total_lines: Total lines in section
            
        Returns:
            True if likely a header
        """
        # Headers are typically:
        # 1. In first few lines of section
        # 2. All caps or title case
        # 3. Short (1-5 words)
        # 4. No numbers (except Note numbers)
        
        if position > 3:
            return False
        
        words = line.split()
        if len(words) > 6:
            return False
        
        # Check for all caps or title case
        if line.isupper():
            return True
        
        if line.istitle():
            return True
        
        # Check for common header patterns
        header_indicators = [
            r'^assets?$',
            r'^liabilit(y|ies)$',
            r'^equity$',
            r'^income$',
            r'^revenue$',
            r'^expenses?$',
            r'^note\s*\d+$',
            r'^cash\s+flow$',
        ]
        
        for pattern in header_indicators:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_section_break(self, line: str) -> bool:
        """
        Check if a line indicates a section break.
        
        Args:
            line: Line text
            
        Returns:
            True if section break
        """
        if not line:
            return False
        
        line_lower = line.lower().strip()
        
        # Check for major section headers
        section_headers = [
            r'^\s*assets?\s*$',
            r'^\s*liabilit(y|ies)\s*$',
            r'^\s*equity\s*$',
            r'^\s*income\s*$',
            r'^\s*revenue\s*$',
            r'^\s*expenses?\s*$',
            r'^\s*cash\s+flow\s*$',
            r'^\s*notes?\s+to\s+',
            r'^\s*statement\s+of\s+',
            r'^\s*note\s*\d+\s*$',
            r'^\s*significant\s+accounting\s+policies\s*$',
        ]
        
        for pattern in section_headers:
            if re.match(pattern, line_lower):
                return True
        
        # Check for empty line after content
        # (handled by caller)
        
        return False
    
    def get_section_boost(
        self, 
        term_key: str, 
        section_type: str
    ) -> float:
        """
        Get boost multiplier for a term in a given section.
        
        Args:
            term_key: Term key to check
            section_type: Section type context
            
        Returns:
            Boost multiplier (1.0 = no boost)
        """
        if not section_type or section_type not in self.section_patterns:
            return 1.0
        
        boost_terms = self.section_patterns[section_type]['boost_terms']
        
        # Check if term matches any boost term
        for boost_term in boost_terms:
            if boost_term.lower() in term_key.lower():
                return 1.5  # 50% boost
        
        return 1.0


# Convenience function
def classify_financial_section(
    lines: List[str], 
    start_line: int = 0
) -> Optional[SectionContext]:
    """
    Quick function to classify a financial document section.
    
    Args:
        lines: Section lines
        start_line: Starting line number
        
    Returns:
        SectionContext or None
    """
    classifier = SectionClassifier()
    return classifier.classify_section(lines, start_line)
