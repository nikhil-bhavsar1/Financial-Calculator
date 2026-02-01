"""
Financial Term Matching System - Text Preprocessing
===================================================
Phase 1: Data Preprocessing & Normalization
Standardizes input text to eliminate mismatch noise.
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from abbreviations import expand_abbreviations, SIGN_CONVENTION_INDICATORS


@dataclass
class PreprocessingResult:
    """Result of text preprocessing pipeline"""
    original_text: str
    cleaned_text: str
    canonical_form: str
    sign_multiplier: int
    detected_abbreviations: List[str]
    removed_elements: Dict[str, List[str]]
    metadata: Dict[str, Any]


class TextPreprocessor:
    """
    Comprehensive text preprocessing pipeline for financial documents.
    Handles OCR errors, abbreviations, formatting variations, and sign conventions.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize preprocessor with configuration.
        
        Args:
            config: Configuration dictionary (uses default if None)
        """
        self.config = config or {}
        
        # Regex patterns for text cleaning
        self.patterns = {
            'note_references': re.compile(
                r'\bnote\s*(?:no\.?)?\s*\d+\b|'
                r'\(see\s+note\s*\d+\)|'
                r'\(note\s*\d+\)|'
                r'schedule\s*[a-z]\d*|'
                r'\(\d+\)',
                re.IGNORECASE
            ),
            'dot_leaders': re.compile(r'\.{3,}'),
            'excess_whitespace': re.compile(r'\s+'),
            'parenthetical_numbers': re.compile(r'\((\d{1,3}(?:,\d{3})*(?:\.\d+)?)\)'),
            'sign_indicators': re.compile(
                r'^(?:less[:]?|[-]\s*\(\s*|\(cr\)|\(dr\)|cr\.|dr\.|credit|debit)',
                re.IGNORECASE
            ),
            'date_formats': re.compile(
                r'\b(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{2,4})\b'
            ),
            'number_formats': re.compile(
                r'\b(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?)\b'  # Indian format: 1,00,000
            ),
            'thousand_separators': re.compile(r'(\d),(\d{3})'),
        }
    
    def preprocess(self, text: str, line_number: Optional[int] = None) -> PreprocessingResult:
        """
        Execute full preprocessing pipeline on a single text line.
        
        Args:
            text: Raw text line from financial statement
            line_number: Optional line number for metadata
            
        Returns:
            PreprocessingResult with cleaned and canonical forms
        """
        original = text.strip()
        removed_elements = {
            'notes': [],
            'schedules': [],
            'sign_indicators': [],
            'dates': [],
            'numbers': []
        }
        
        # Step 1: Detect sign conventions before cleaning
        sign_multiplier = self._detect_sign_convention(original)
        if sign_multiplier == -1:
            removed_elements['sign_indicators'].append('negative_indicator')
        
        # Step 2: Remove note and schedule references
        cleaned, notes_removed = self._remove_note_references(original)
        removed_elements['notes'].extend(notes_removed)
        
        # Step 3: Remove dot leaders and normalize whitespace
        cleaned = self._clean_formatting(cleaned)
        
        # Step 4: Convert parenthetical numbers to signed format
        cleaned, numbers_converted = self._convert_parenthetical_numbers(cleaned)
        removed_elements['numbers'].extend(numbers_converted)
        
        # Step 5: Expand abbreviations
        cleaned, detected_abbr = self._expand_abbreviations_in_text(cleaned)
        
        # Step 6: Create canonical form
        canonical = self._create_canonical_form(cleaned)
        
        # Step 7: Normalize dates
        canonical, dates_normalized = self._normalize_dates(canonical)
        removed_elements['dates'].extend(dates_normalized)
        
        # Step 8: Normalize number formats
        canonical = self._normalize_numbers(canonical)
        
        return PreprocessingResult(
            original_text=original,
            cleaned_text=cleaned,
            canonical_form=canonical,
            sign_multiplier=sign_multiplier,
            detected_abbreviations=detected_abbr,
            removed_elements=removed_elements,
            metadata={
                'line_number': line_number,
                'original_length': len(original),
                'cleaned_length': len(cleaned),
                'canonical_length': len(canonical)
            }
        )
    
    def _detect_sign_convention(self, text: str) -> int:
        """
        Detect sign convention indicators in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            1 for positive, -1 for negative
        """
        text_lower = text.lower().strip()
        
        # Check for explicit negative indicators at start
        for indicator, multiplier in SIGN_CONVENTION_INDICATORS.items():
            if text_lower.startswith(indicator.lower()):
                return multiplier
        
        # Check for parenthetical numbers (typically negative)
        if self.patterns['parenthetical_numbers'].search(text):
            return -1
        
        return 1
    
    def _remove_note_references(self, text: str) -> Tuple[str, List[str]]:
        """
        Remove note and schedule references from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (cleaned_text, list_of_removed_references)
        """
        removed = []
        
        # Find all matches
        matches = self.patterns['note_references'].findall(text)
        
        # Remove them
        cleaned = self.patterns['note_references'].sub('', text)
        
        # Track what was removed
        for match in matches:
            match_clean = match.strip().lower()
            if 'note' in match_clean:
                removed.append(f'note_ref:{match}')
            elif 'schedule' in match_clean:
                removed.append(f'schedule_ref:{match}')
        
        return cleaned, removed
    
    def _clean_formatting(self, text: str) -> str:
        """
        Clean formatting artifacts like dot leaders and excess whitespace.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove dot leaders
        text = self.patterns['dot_leaders'].sub(' ', text)
        
        # Normalize whitespace
        text = self.patterns['excess_whitespace'].sub(' ', text)
        
        return text.strip()
    
    def _convert_parenthetical_numbers(self, text: str) -> Tuple[str, List[str]]:
        """
        Convert parenthetical numbers to negative signed format.
        Example: (1,234) → -1234
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (converted_text, list_of_converted_numbers)
        """
        converted = []
        
        def replace_parenthetical(match):
            number = match.group(1)
            converted.append(number)
            # Remove commas and add negative sign
            clean_number = number.replace(',', '')
            return f'-{clean_number}'
        
        result = self.patterns['parenthetical_numbers'].sub(replace_parenthetical, text)
        
        return result, converted
    
    def _expand_abbreviations_in_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Expand abbreviations in text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (expanded_text, list_of_detected_abbreviations)
        """
        detected = []
        
        # Simple word-by-word expansion
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            # Check if it's an abbreviation
            expanded = expand_abbreviations(clean_word)
            if expanded != clean_word:
                detected.append(clean_word)
                expanded_words.append(expanded)
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words), detected
    
    def _create_canonical_form(self, text: str) -> str:
        """
        Create canonical form for matching:
        - Lowercase
        - Unicode normalization
        - Separator standardization
        - Remove non-alphanumeric except spaces
        
        Args:
            text: Input text
            
        Returns:
            Canonical form text
        """
        # Unicode normalization (NFKD to decompose characters)
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace smart quotes and special characters
        replacements = {
            ''': "'", ''': "'", '"': '"', '"': '"',
            '–': '-', '—': '-', '−': '-',
            ' ': ' ', ' ': ' ', '\xa0': ' ',
            '&': ' and ',
            '/': ' ',
            '-': ' ',
            '_': ' '
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove remaining non-alphanumeric except spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Normalize multiple spaces
        text = self.patterns['excess_whitespace'].sub(' ', text)
        
        return text.strip()
    
    def _normalize_dates(self, text: str) -> Tuple[str, List[str]]:
        """
        Normalize date formats to ISO format (YYYY-MM-DD).
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (normalized_text, list_of_normalized_dates)
        """
        normalized_dates = []
        
        def replace_date(match):
            day, month, year = match.groups()
            
            # Handle 2-digit vs 4-digit year
            if len(year) == 2:
                year_int = int(year)
                if year_int >= 50:
                    year = '19' + year
                else:
                    year = '20' + year
            
            try:
                date_obj = datetime(int(year), int(month), int(day))
                iso_date = date_obj.strftime('%Y-%m-%d')
                normalized_dates.append(iso_date)
                return iso_date
            except ValueError:
                return match.group(0)
        
        result = self.patterns['date_formats'].sub(replace_date, text)
        
        return result, normalized_dates
    
    def _normalize_numbers(self, text: str) -> str:
        """
        Normalize number formats by removing thousand separators.
        Preserves decimal points.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized numbers
        """
        # Remove thousand separators (commas between digits)
        # But preserve decimal points
        def replace_separator(match):
            return match.group(1) + match.group(2)
        
        # Keep doing it until no more changes (handles Indian format 1,00,000)
        prev_text = None
        while prev_text != text:
            prev_text = text
            text = self.patterns['thousand_separators'].sub(replace_separator, text)
        
        return text
    
    def preprocess_batch(
        self, 
        texts: List[str], 
        line_numbers: Optional[List[int]] = None
    ) -> List[PreprocessingResult]:
        """
        Preprocess multiple text lines in batch.
        
        Args:
            texts: List of text lines
            line_numbers: Optional list of line numbers
            
        Returns:
            List of PreprocessingResult objects
        """
        results = []
        
        for i, text in enumerate(texts):
            line_num = line_numbers[i] if line_numbers and i < len(line_numbers) else i + 1
            result = self.preprocess(text, line_num)
            results.append(result)
        
        return results


# Convenience function for quick preprocessing
def preprocess_text(text: str, line_number: Optional[int] = None) -> PreprocessingResult:
    """
    Quick preprocessing function.
    
    Args:
        text: Text to preprocess
        line_number: Optional line number
        
    Returns:
        PreprocessingResult
    """
    preprocessor = TextPreprocessor()
    return preprocessor.preprocess(text, line_number)
