"""
Notes and Footnotes Extractor for Financial Statements
======================================================
Extracts detailed data from notes sections and footnotes.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class NoteSection:
    """Represents a note section with its content."""
    note_number: str
    title: str
    content: str
    page_number: int
    line_items: List[Dict] = field(default_factory=list)
    tables: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'note_number': self.note_number,
            'title': self.title,
            'content': self.content[:500] + '...' if len(self.content) > 500 else self.content,
            'page_number': self.page_number,
            'line_items_count': len(self.line_items),
            'tables_count': len(self.tables),
        }


class NotesExtractor:
    """
    Extracts note sections and footnotes from financial statements.
    Handles various formats of note references and content.
    """
    
    # Patterns for detecting note sections
    NOTE_HEADER_PATTERNS = [
        r'^\s*Note\s+(\d+)[\s\.:\-]+(.+?)$',  # "Note 1: Accounting Policies"
        r'^\s*(\d+)\.\s+(.+?)$',  # "1. Accounting Policies"
        r'^\s*Note\s*[-:]\s*(\d+)[\s\.:\-]+(.+?)$',  # "Note - 1: Accounting Policies"
        r'^\s*\d+\.\s*Note\s+(\d+)[\s\.:\-]+(.+?)$',  # "1. Note 1: Accounting Policies"
    ]
    
    # Patterns for detecting note references in line items
    NOTE_REFERENCE_PATTERNS = [
        r'\((\d+(?:\s*,\s*\d+)*)\)',  # (1), (1, 2, 3)
        r'\bNote\s+(\d+)',  # Note 1
        r'\bsee\s+note\s+(\d+)',  # see note 1
        r'\bNote\s+(\d+)\s+\w+',  # Note 1 above/below
    ]
    
    # Financial data patterns within notes
    DATA_PATTERNS = [
        r'([\w\s]+?)\s+[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?',  # Label + number
        r'(?:Rs\.?|₹|INR)?\s*[\d,]+(?:\.\d{1,2})?',  # Currency amounts
        r'\d{1,3}(?:,\d{2,3})+(?:\.\d+)?',  # Indian number format
    ]
    
    def __init__(self):
        self.notes: Dict[str, NoteSection] = {}
        self.current_note: Optional[NoteSection] = None
        
    def extract_notes_from_text(self, text: str, page_number: int = 0) -> List[NoteSection]:
        """
        Extract note sections from text content.
        
        Args:
            text: Text content to parse
            page_number: Page number for reference
            
        Returns:
            List of NoteSection objects
        """
        lines = text.split('\n')
        notes = []
        current_note = None
        current_content = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Check if this line starts a new note
            note_match = self._match_note_header(line_stripped)
            
            if note_match:
                # Save previous note if exists
                if current_note:
                    current_note.content = '\n'.join(current_content)
                    current_note.line_items = self._extract_line_items_from_note(current_content)
                    notes.append(current_note)
                
                # Start new note
                note_num, title = note_match
                current_note = NoteSection(
                    note_number=note_num,
                    title=title,
                    content='',
                    page_number=page_number
                )
                current_content = []
            elif current_note:
                # Add to current note content
                current_content.append(line)
                
                # Check for tables within note
                if self._is_table_line(line):
                    table_data = self._extract_table_from_lines(lines[i:i+20])
                    if table_data:
                        current_note.tables.append(table_data)
        
        # Don't forget the last note
        if current_note:
            current_note.content = '\n'.join(current_content)
            current_note.line_items = self._extract_line_items_from_note(current_content)
            notes.append(current_note)
        
        return notes
    
    def _match_note_header(self, line: str) -> Optional[Tuple[str, str]]:
        """Match a line against note header patterns."""
        for pattern in self.NOTE_HEADER_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                note_num = match.group(1)
                title = match.group(2).strip()
                return (note_num, title)
        return None
    
    def _is_table_line(self, line: str) -> bool:
        """Check if a line appears to be part of a table."""
        # Check for markdown table markers
        if '|' in line:
            return True
        
        # Check for multiple numbers
        numbers = re.findall(r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?', line)
        if len(numbers) >= 2:
            return True
        
        return False
    
    def _extract_table_from_lines(self, lines: List[str]) -> Optional[Dict]:
        """Extract table data from a group of lines."""
        if not lines:
            return None
        
        # Simple table extraction - look for consistent column structure
        rows = []
        for line in lines:
            if '|' in line:
                # Markdown table format
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    rows.append(cells)
            else:
                # Try to split by multiple spaces
                cells = re.split(r'\s{2,}', line.strip())
                if len(cells) >= 2:
                    rows.append(cells)
        
        if len(rows) >= 2:
            return {
                'headers': rows[0] if rows else [],
                'rows': rows[1:] if len(rows) > 1 else [],
            }
        
        return None
    
    def _extract_line_items_from_note(self, lines: List[str]) -> List[Dict]:
        """Extract financial line items from note content."""
        items = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) < 5:
                continue
            
            # Look for label + number patterns
            match = re.match(r'^([\w\s\-&]+?)\s+([\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?)', line_stripped)
            if match:
                label = match.group(1).strip()
                value_str = match.group(2).strip()
                
                # Clean and parse value
                clean_value = re.sub(r'[\(\)\s]', '', value_str).replace(',', '')
                try:
                    value = float(clean_value)
                    is_negative = '(' in value_str or '-' in value_str
                    
                    items.append({
                        'label': label,
                        'value': value,
                        'is_negative': is_negative,
                        'raw': line_stripped,
                    })
                except ValueError:
                    pass
        
        return items
    
    def extract_note_references(self, line: str) -> List[str]:
        """
        Extract note references from a line item.
        
        Args:
            line: Line text to search
            
        Returns:
            List of note numbers referenced
        """
        references = []
        
        for pattern in self.NOTE_REFERENCE_PATTERNS:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle multiple notes like "(1, 2, 3)"
                    notes = re.findall(r'\d+', match[0] if match else '')
                    references.extend(notes)
                else:
                    references.append(match)
        
        return list(set(references))  # Remove duplicates
    
    def merge_with_line_items(self, line_items: List[Dict], notes: List[NoteSection]) -> List[Dict]:
        """
        Merge note content with line items that reference them.
        
        Args:
            line_items: List of extracted line items
            notes: List of note sections
            
        Returns:
            Enhanced line items with note details
        """
        notes_dict = {note.note_number: note for note in notes}
        enhanced_items = []
        
        for item in line_items:
            # Extract note references from the line
            line_text = item.get('label', '') + ' ' + item.get('raw_value', '')
            note_refs = self.extract_note_references(line_text)
            
            if note_refs:
                item['note_references'] = note_refs
                item['note_details'] = []
                
                for ref in note_refs:
                    if ref in notes_dict:
                        note = notes_dict[ref]
                        item['note_details'].append({
                            'note_number': note.note_number,
                            'title': note.title,
                            'summary': note.content[:200] + '...' if len(note.content) > 200 else note.content,
                        })
            
            enhanced_items.append(item)
        
        return enhanced_items


# Convenience function
def extract_notes(text: str, page_number: int = 0) -> List[NoteSection]:
    """Extract notes from text."""
    extractor = NotesExtractor()
    return extractor.extract_notes_from_text(text, page_number)
