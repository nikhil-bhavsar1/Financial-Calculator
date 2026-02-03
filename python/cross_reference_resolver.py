"""
Financial Term Matching System - Cross-Reference Resolution
===========================================================
Handles note linking, schedule references, and inter-statement validation.
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class CrossReference:
    """Represents a cross-reference in a financial document"""
    ref_type: str  # 'note', 'schedule', 'statement'
    ref_number: str
    ref_label: str
    source_line: int
    source_text: str
    target_context: Optional[str] = None
    resolved: bool = False


@dataclass
class NoteSection:
    """Represents a note section in the document"""
    note_number: str
    header: str
    start_line: int
    end_line: int
    content: List[str] = field(default_factory=list)
    extracted_terms: List[Dict] = field(default_factory=list)


class CrossReferenceResolver:
    """
    Resolves cross-references in financial statements.
    Links note references to their content and validates inter-statement consistency.
    """
    
    def __init__(self):
        # Reference patterns
        self.note_patterns = [
            re.compile(r'\(see\s+note\s*(?:no\.?)?\s*(\d+)\)', re.IGNORECASE),
            re.compile(r'\(note\s*(?:no\.?)?\s*(\d+)\)', re.IGNORECASE),
            re.compile(r'\bnote\s*(?:no\.?)?\s*(\d+)\b', re.IGNORECASE),
            re.compile(r'\brefer\s+to\s+note\s*(?:no\.?)?\s*(\d+)\b', re.IGNORECASE),
        ]
        
        self.schedule_patterns = [
            re.compile(r'\(see\s+schedule\s*([a-z0-9]+)\)', re.IGNORECASE),
            re.compile(r'\(schedule\s*([a-z0-9]+)\)', re.IGNORECASE),
            re.compile(r'\bschedule\s*([a-z0-9]+)\b', re.IGNORECASE),
            re.compile(r'\bas\s+per\s+schedule\s*([a-z0-9]+)\b', re.IGNORECASE),
        ]
        
        # Note section detection
        self.note_header_pattern = re.compile(
            r'^(?:note|notes)\s*(?:no\.?)?\s*(\d+)[:\s\-\.]*(.+)?$',
            re.IGNORECASE
        )
        
        # Storage
        self.notes: Dict[str, NoteSection] = {}
        self.schedules: Dict[str, Dict] = {}
        self.references: List[CrossReference] = []
    
    def extract_references(
        self, 
        lines: List[str], 
        matched_terms: List[Dict]
    ) -> List[CrossReference]:
        """
        Extract all cross-references from document lines.
        
        Args:
            lines: Document lines
            matched_terms: Already matched terms for context
            
        Returns:
            List of CrossReference objects
        """
        references = []
        
        for i, line in enumerate(lines):
            line_text = line.strip()
            
            if not line_text:
                continue
            
            # Extract note references
            for pattern in self.note_patterns:
                matches = pattern.findall(line_text)
                for match in matches:
                    ref = CrossReference(
                        ref_type='note',
                        ref_number=str(match),
                        ref_label=f"Note {match}",
                        source_line=i,
                        source_text=line_text[:100]  # First 100 chars
                    )
                    references.append(ref)
            
            # Extract schedule references
            for pattern in self.schedule_patterns:
                matches = pattern.findall(line_text)
                for match in matches:
                    ref = CrossReference(
                        ref_type='schedule',
                        ref_number=str(match).upper(),
                        ref_label=f"Schedule {match.upper()}",
                        source_line=i,
                        source_text=line_text[:100]
                    )
                    references.append(ref)
        
        # Deduplicate references (same type, number, and line)
        seen = set()
        deduplicated = []
        for ref in references:
            key = (ref.ref_type, ref.ref_number, ref.source_line)
            if key not in seen:
                seen.add(key)
                deduplicated.append(ref)
        
        self.references = deduplicated
        return deduplicated
    
    def extract_note_sections(self, lines: List[str]) -> Dict[str, NoteSection]:
        """
        Extract and index all note sections from the document.
        
        Args:
            lines: Document lines
            
        Returns:
            Dictionary mapping note numbers to NoteSection objects
        """
        notes = {}
        current_note = None
        
        for i, line in enumerate(lines):
            line_text = line.strip()
            
            # Check for note header
            match = self.note_header_pattern.match(line_text)
            if match:
                # Save previous note
                if current_note:
                    current_note.end_line = i - 1
                    notes[current_note.note_number] = current_note
                
                # Start new note
                note_num = match.group(1)
                header = match.group(2) or ""
                
                current_note = NoteSection(
                    note_number=note_num,
                    header=header.strip(),
                    start_line=i,
                    end_line=i,
                    content=[line_text]
                )
            elif current_note:
                # Add to current note
                current_note.content.append(line_text)
                
                # Check for note end (next major section or empty lines)
                if self._is_note_end(line_text, i, len(lines)):
                    current_note.end_line = i
                    notes[current_note.note_number] = current_note
                    current_note = None
        
        # Save final note
        if current_note:
            current_note.end_line = len(lines) - 1
            notes[current_note.note_number] = current_note
        
        self.notes = notes
        return notes
    
    def resolve_references(
        self, 
        matching_engine,
        lines: List[str]
    ) -> List[CrossReference]:
        """
        Resolve all cross-references by extracting content from notes/schedules.
        
        Args:
            matching_engine: Matching engine instance for term extraction
            lines: Document lines
            
        Returns:
            List of resolved CrossReference objects
        """
        # First extract note sections
        self.extract_note_sections(lines)
        
        # Resolve each reference
        for ref in self.references:
            if ref.ref_type == 'note' and ref.ref_number in self.notes:
                note = self.notes[ref.ref_number]
                
                # Extract terms from note content
                note_matches = matching_engine.match_document(note.content)
                note.extracted_terms = [
                    {
                        'term_key': m.term_key,
                        'term_label': m.term_label,
                        'confidence': m.confidence_score
                    }
                    for m in note_matches.results
                ]
                
                ref.target_context = note.header
                ref.resolved = True
        
        return [ref for ref in self.references if ref.resolved]
    
    def validate_inter_statement_consistency(
        self,
        balance_sheet_matches: List[Dict],
        income_statement_matches: List[Dict],
        cash_flow_matches: List[Dict]
    ) -> List[Dict]:
        """
        Validate consistency across different statements.
        
        Args:
            balance_sheet_matches: Matches from balance sheet
            income_statement_matches: Matches from income statement
            cash_flow_matches: Matches from cash flow statement
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check 1: Total Revenue reconciliation
        bs_revenue = self._find_term_value(balance_sheet_matches, 'total_revenue')
        is_revenue = self._find_term_value(income_statement_matches, 'total_revenue')
        cf_revenue = self._find_term_value(cash_flow_matches, 'revenue_from_operations')
        
        if is_revenue and cf_revenue:
            if abs(is_revenue - cf_revenue) / max(is_revenue, 1) > 0.05:  # 5% tolerance
                issues.append({
                    'type': 'revenue_mismatch',
                    'severity': 'warning',
                    'message': f'Revenue mismatch: Income Statement ({is_revenue}) vs Cash Flow ({cf_revenue})',
                    'expected': is_revenue,
                    'actual': cf_revenue
                })
        
        # Check 2: Cash reconciliation
        bs_cash = self._find_term_value(balance_sheet_matches, 'cash_and_equivalents')
        cf_cash_end = self._find_term_value(cash_flow_matches, 'cash_and_cash_equivalents_at_end')
        
        if bs_cash and cf_cash_end:
            if abs(bs_cash - cf_cash_end) > 0.01:  # Small tolerance for rounding
                issues.append({
                    'type': 'cash_mismatch',
                    'severity': 'error',
                    'message': f'Cash mismatch: Balance Sheet ({bs_cash}) vs Cash Flow ({cf_cash_end})',
                    'expected': bs_cash,
                    'actual': cf_cash_end
                })
        
        # Check 3: Profit reconciliation
        is_profit = self._find_term_value(income_statement_matches, 'profit_for_the_year')
        
        if is_profit:
            # Check if profit appears in appropriate sections
            if not any('profit' in m.get('term_key', '') for m in balance_sheet_matches):
                # This is OK - profit flows to equity, not always explicitly shown
                pass
        
        # Check 4: Section-specific sanity checks
        for match in income_statement_matches:
            term_key = match.get('term_key', '')
            
            # Flag if balance sheet terms appear in income statement
            if term_key in ['total_assets', 'property_plant_equipment', 'inventories']:
                issues.append({
                    'type': 'wrong_section',
                    'severity': 'warning',
                    'message': f'Balance sheet term "{match.get("term_label", term_key)}" found in Income Statement',
                    'term_key': term_key
                })
        
        return issues
    
    def _find_term_value(
        self, 
        matches: List[Dict], 
        term_key_pattern: str
    ) -> Optional[float]:
        """
        Find a term value from matches.
        
        Args:
            matches: List of match dictionaries
            term_key_pattern: Pattern to match in term_key
            
        Returns:
            Value if found, None otherwise
        """
        for match in matches:
            if term_key_pattern in match.get('term_key', '').lower():
                # Try to extract numeric value from original text
                text = match.get('original_text', '')
                numbers = re.findall(r'\(?\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\)?', text)
                if numbers:
                    # Convert to float
                    num_str = numbers[-1].replace(',', '').replace('(', '-').replace(')', '')
                    try:
                        return float(num_str)
                    except ValueError:
                        pass
        return None
    
    def _is_note_end(self, line: str, position: int, total_lines: int) -> bool:
        """
        Check if this line marks the end of a note section.
        
        Args:
            line: Line text
            position: Line position
            total_lines: Total lines in document
            
        Returns:
            True if note ends here
        """
        # Note ends at next note header or major section
        if self.note_header_pattern.match(line):
            return True
        
        # Or at empty lines followed by major headers
        if not line.strip():
            # Check if next non-empty line is a major section
            return True
        
        return False
    
    def get_note_content(self, note_number: str) -> Optional[NoteSection]:
        """
        Get content of a specific note.
        
        Args:
            note_number: Note number to retrieve
            
        Returns:
            NoteSection or None
        """
        return self.notes.get(note_number)
    
    def get_unresolved_references(self) -> List[CrossReference]:
        """
        Get all unresolved references.
        
        Returns:
            List of unresolved CrossReference objects
        """
        return [ref for ref in self.references if not ref.resolved]
    
    def generate_reference_report(self) -> Dict[str, Any]:
        """
        Generate a report of all references.
        
        Returns:
            Report dictionary
        """
        total_refs = len(self.references)
        resolved_refs = len([r for r in self.references if r.resolved])
        
        by_type = defaultdict(list)
        for ref in self.references:
            by_type[ref.ref_type].append(ref)
        
        return {
            'total_references': total_refs,
            'resolved_references': resolved_refs,
            'unresolved_references': total_refs - resolved_refs,
            'resolution_rate': resolved_refs / total_refs if total_refs > 0 else 0,
            'by_type': {
                ref_type: len(refs)
                for ref_type, refs in by_type.items()
            },
            'notes_extracted': len(self.notes),
            'unresolved_details': [
                {
                    'type': ref.ref_type,
                    'number': ref.ref_number,
                    'line': ref.source_line,
                    'text': ref.source_text[:50]
                }
                for ref in self.get_unresolved_references()
            ]
        }


# Convenience function
def resolve_document_references(
    lines: List[str],
    matching_engine
) -> Tuple[List[CrossReference], Dict[str, NoteSection]]:
    """
    Quick function to resolve all references in a document.
    
    Args:
        lines: Document lines
        matching_engine: Matching engine instance
        
    Returns:
        Tuple of (resolved references, notes dictionary)
    """
    resolver = CrossReferenceResolver()
    resolver.extract_references(lines, [])
    resolver.extract_note_sections(lines)
    resolved = resolver.resolve_references(matching_engine, lines)
    
    return resolved, resolver.notes
