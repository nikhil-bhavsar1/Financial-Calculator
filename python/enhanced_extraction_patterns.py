"""
Enhanced Extraction Patterns for 100% Data Capture

This module adds comprehensive patterns and logic to ensure no data is missed.

Enhancements:
1. Comprehensive number formats (Indian, European, US, Asian)
2. Zero/nil value handling
3. Note reference extraction
4. Percentage and ratio capture
5. Multi-line label support
6. Better column header detection
7. Enhanced continuation detection
8. Subtotal pattern recognition
9. Currency variations
10. Bracket negative formats
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class EnhancedNumberPatterns:
    """
    Comprehensive number pattern matching for global financial formats.
    
    Covers:
    - Indian: 1,23,45,678.90 (lakh, crore)
    - European: 1.234.567,90 (dot thousand, comma decimal)
    - US: 1,234,567.90 (comma thousand, dot decimal)
    - Asian: 1,234.56 (mixed separators)
    - Negative: (123.45), [123.45], -123.45, 123.45-
    - Percentages: 12.5%, 12.5 %
    - Ratios: 2.5:1, 2.5x
    - Zero/nil: 0, -, nil, Nil, N/A, (blank)
    """
    
    # Standard patterns - from original
    STANDARD_PATTERN = r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?'
    
    # Indian format - lakh, crore notation
    INDIAN_PATTERN = r'[\(\-]?\s*\d{1,3}(?:,\d{2,3})+(?:\.\d+)?\s*\)?'
    
    # European format - dot for thousands, comma for decimal
    EUROPEAN_PATTERN = r'[\(\-]?\s*\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?\s*\)?'
    
    # Parentheses only negative
    PARENTHESIS_PATTERN = r'\(\s*[\d,]+\s*\)'
    
    # Bracket negative (square brackets)
    BRACKET_PATTERN = r'\[\s*[\d,]+\s*\]'
    
    # Percentage format
    PERCENTAGE_PATTERN = r'[\(\-]?\s*\d+(?:[\.,]\d{1,2})?\s*(?:%|\s*%)'
    
    # Ratio format (e.g., 2.5:1, 2.5x)
    RATIO_PATTERN = r'\d+(?:[\.,]\d{1,2})?\s*[:x]\s*\d+(?:[\.,]\d{1,2})?'
    
    # Zero/nil indicators
    ZERO_NIL_PATTERNS = [
        r'^\s*0\s*$',  # Just 0
        r'^\s*-\s*$',  # Just dash
        r'^\s*nil\s*$',  # Nil
        r'^\s*Nil\s*$',  # Capital Nil
        r'^\s*—\s*$',  # Em dash
        r'^\s*-\s*',  # Multiple dashes
        r'^\s*n/a\s*$',  # N/A
        r'^\s*N/A\s*$',  # N/A capitalized
        r'^\s*none\s*$',  # None
    ]
    
    # Note reference patterns
    NOTE_REF_PATTERNS = [
        r'\(\d+\)',     # (1), (2)
        r'\[\d+\]',     # [1], [2]
        r'note\s*\d+',  # Note 1, Note 2
        r'n\.\s*\d+',    # n.1, n.2
        r'^\s*\d+\s*$',  # Just a number < 100 (likely ref)
    ]
    
    @staticmethod
    def extract_all_numbers(line: str) -> List[Dict[str, Any]]:
        """
        Extract all numbers with their types and positions.
        
        Returns list of dicts: {value, raw, position, type}
        """
        numbers = []
        
        # Try all patterns
        patterns = [
            (EnhancedNumberPatterns.STANDARD_PATTERN, 'standard'),
            (EnhancedNumberPatterns.INDIAN_PATTERN, 'indian'),
            (EnhancedNumberPatterns.EUROPEAN_PATTERN, 'european'),
            (EnhancedNumberPatterns.PARENTHESIS_PATTERN, 'parenthesis'),
            (EnhancedNumberPatterns.BRACKET_PATTERN, 'bracket'),
            (EnhancedNumberPatterns.PERCENTAGE_PATTERN, 'percentage'),
            (EnhancedNumberPatterns.RATIO_PATTERN, 'ratio'),
        ]
        
        for pattern, pattern_type in patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                raw = match.group()
                # Remove formatting
                cleaned = re.sub(r'[\(\)\[\]\-\s,]', '', raw)
                
                try:
                    value = float(cleaned)
                    
                    # Determine if negative
                    is_negative = (
                        '(' in raw or '[' in raw or 
                        raw.startswith('-') or 
                        (pattern_type == 'parenthesis') or
                        (pattern_type == 'bracket')
                    )
                    if is_negative:
                        value = -abs(value)
                    
                    numbers.append({
                        'value': value,
                        'raw': raw,
                        'position': match.start(),
                        'end_position': match.end(),
                        'type': pattern_type,
                        'is_negative': is_negative,
                    })
                except ValueError:
                    pass
        
        # Remove duplicates while preserving order (same position)
        seen_positions = set()
        unique_numbers = []
        for num in numbers:
            pos = num['position']
            if pos not in seen_positions:
                seen_positions.add(pos)
                unique_numbers.append(num)
        
        return unique_numbers
    
    @staticmethod
    def extract_values_and_years(
        numbers: List[Dict[str, Any]],
        line: str
    ) -> Tuple[List[float], List[int], Optional[int]]:
        """
        Separate values from years and extract note references.
        
        Returns: (values, years, note_ref)
        """
        values = []
        years = []
        note_ref = None
        
        for num in numbers:
            val = num['value']
            
            # Check for year (1990-2050, integer, positive)
            if (1990 <= abs(val) <= 2050 and 
                val == int(val) and 
                num['type'] in ['standard', 'indian'] and
                not num['is_negative']):
                years.append(int(val))
                continue
            
            # Check for note reference (< 100, not decimal)
            if (0 < val < 100 and 
                val == int(val) and 
                not note_ref):
                note_ref = int(val)
                continue
            
            # Otherwise it's a value
            values.append(val)
        
        return values, years, note_ref
    
    @staticmethod
    def is_zero_or_nil(text: str) -> bool:
        """Check if text represents zero or nil value."""
        for pattern in EnhancedNumberPatterns.ZERO_NIL_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def parse_number_with_currency(text: str) -> Optional[float]:
        """
        Parse number from text with currency symbols.
        
        Handles: ₹, $, €, £, ¥, Rs., etc.
        """
        # Remove currency symbols
        cleaned = re.sub(r'[₹$€£¥Rs\.CR|Dr|Cr]', '', text, flags=re.IGNORECASE)
        
        # Try to parse
        numbers = EnhancedNumberPatterns.extract_all_numbers(cleaned)
        if numbers:
            return numbers[0]['value']
        return None
    
    @staticmethod
    def extract_percentage_or_ratio(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract percentage or ratio from text.
        
        Returns: {value, type, raw}
        """
        # Check percentage
        pct_match = re.search(EnhancedNumberPatterns.PERCENTAGE_PATTERN, text, re.IGNORECASE)
        if pct_match:
            raw = pct_match.group()
            clean = re.sub(r'[%\s]', '', raw)
            try:
                value = float(clean) / 100.0  # Convert to decimal
                return {
                    'value': value,
                    'type': 'percentage',
                    'raw': raw
                }
            except ValueError:
                pass
        
        # Check ratio
        ratio_match = re.search(EnhancedNumberPatterns.RATIO_PATTERN, text, re.IGNORECASE)
        if ratio_match:
            raw = ratio_match.group()
            parts = re.split(r'[:x]', raw)
            if len(parts) == 2:
                try:
                    num = float(parts[0].strip())
                    den = float(parts[1].strip())
                    return {
                        'value': num / den if den != 0 else 0,
                        'type': 'ratio',
                        'raw': raw,
                        'numerator': num,
                        'denominator': den
                    }
                except ValueError:
                    pass
        
        return None


class EnhancedLabelExtraction:
    """
    Enhanced label extraction with multi-line support and note reference handling.
    """
    
    # Patterns that indicate end of label (before values)
    LABEL_END_PATTERNS = [
        r'\s{2,}\d',          # 2+ spaces then number
        r'\s{2,}\(',          # 2+ spaces then parenthesis
        r'\s{2,}\[',          # 2+ spaces then bracket
        r'\s{2,}[-–—]',     # 2+ spaces then dash/dash
    ]
    
    @staticmethod
    def extract_label(line: str, numbers: List[Dict[str, Any]]) -> str:
        """
        Extract clean label from line, handling multi-line patterns.
        
        Preserves:
        - Indentation levels
        - Note references like (1)
        - Sub-total patterns like "  Total"
        - Parentheses in labels
        """
        if not numbers:
            return line.strip()
        
        # Find earliest number position
        first_num_pos = min(n['position'] for n in numbers)
        
        # Extract label up to first number
        label = line[:first_num_pos].strip()
        
        # Clean up label
        label = EnhancedLabelExtraction._clean_label(label)
        
        # Check if label is empty or too short
        if len(label) < 2:
            # Label might be in previous line (multi-line)
            label = f"... {line.strip()}"
        
        return label
    
    @staticmethod
    def _clean_label(label: str) -> str:
        """Clean label from artifacts."""
        # Normalize whitespace
        label = re.sub(r'\s+', ' ', label)
        
        # Remove markdown table artifacts
        label = label.replace('|', '')
        
        # Remove leading/trailing dashes
        label = re.sub(r'^[-–•]\s*', '', label)
        label = re.sub(r'\s*[-–—]+$', '', label)
        
        # Remove empty parentheses from label (like "(a)")
        label = re.sub(r'^\([a-z]\)\s*', '', label, flags=re.IGNORECASE)
        
        # Remove page/section numbers from start
        label = re.sub(r'^\d+[\.\)]\s*', '', label)
        
        # Remove common row markers
        label = re.sub(r'^[\s]*[-–•]\s*', '', label)
        
        return label.strip()
    
    @staticmethod
    def is_subtotal_label(label: str) -> bool:
        """
        Check if label indicates a subtotal or total.
        
        These should be preserved, not filtered out.
        """
        subtotal_patterns = [
            r'^total\s*$',                           # "Total" (various whitespace)
            r'^total\s+(.*)$',                         # "Total Assets", "Total Income"
            r'^sub\s*total\s*$',                      # "Sub total"
            r'^grand\s*total\s*$',                     # "Grand total"
            r'^net\s*$',                               # "Net", "Net Income"
            r'^net\s+(.*)$',                           # "Net Profit"
            r'^gross\s*$',                             # "Gross", "Gross Total"
            r'^gross\s+(.*)$',                         # "Gross Profit"
            r'\s+total\s*$',                          # "XXX Total"
            r'^\(\s*total\s*\)',                       # "(Total)"
        ]
        
        for pattern in subtotal_patterns:
            if re.search(pattern, label, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_indentation(label: str) -> int:
        """Detect indentation level of label."""
        # Count leading spaces
        spaces = len(label) - len(label.lstrip())
        return spaces


class EnhancedColumnDetection:
    """
    Enhanced column header detection for identifying current/previous year columns.
    """
    
    # Patterns that indicate current year column
    CURRENT_YEAR_PATTERNS = [
        r'\bcurrent\s*year\b',
        r'\bcurrent\s*period\b',
        r'\bcurrent\b',  # If last column
        r'\b20\d{2}\b',  # Most recent year
        r'\bthis\s*year\b',
    ]
    
    # Patterns that indicate previous year column
    PREVIOUS_YEAR_PATTERNS = [
        r'\bprevious\s*year\b',
        r'\bprevious\s*period\b',
        r'\bprevious\b',  # If not first column
        r'\b20\d{2}\b',  # Older year
        r'\blast\s*year\b',
    ]
    
    @staticmethod
    def detect_column_headers(headers: List[str]) -> Dict[str, int]:
        """
        Detect which columns are current/previous year.
        
        Returns: {'current': col_index, 'previous': col_index}
        """
        current_col = -1
        previous_col = -1
        
        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            
            # Check for current year
            for pattern in EnhancedColumnDetection.CURRENT_YEAR_PATTERNS:
                if re.search(pattern, header_lower):
                    # Prefer later columns for current year
                    if current_col < i:
                        current_col = i
                    break
            
            # Check for previous year
            for pattern in EnhancedColumnDetection.PREVIOUS_YEAR_PATTERNS:
                if re.search(pattern, header_lower):
                    # Prefer earlier columns for previous year
                    if previous_col == -1 or previous_col > i:
                        previous_col = i
                    break
        
        # Fallback: If not explicitly detected, use position
        if current_col == -1 and len(headers) >= 2:
            # Assume last numeric column is current year
            current_col = len(headers) - 1
            previous_col = len(headers) - 2
        elif current_col == -1 and len(headers) >= 1:
            current_col = len(headers) - 1
        
        return {
            'current': current_col,
            'previous': previous_col
        }


class EnhancedContinuationDetection:
    """
    Enhanced detection of multi-page statement continuation.
    """
    
    # Patterns that indicate a page continues the previous statement
    CONTINUATION_PATTERNS = [
        r'\(contd\.?\)',                    # (contd.)
        r'\(continued\)',                    # (continued)
        r'continued\s+',                      # "continued" followed by content
        r'contd\.\s+',                       # "contd." followed by content
        r'^\s*\d+\s+[\d,\(\)]',        # Starts with page number
        r'^\s*\(page\s*\d+\s*\)',        # (Page X) markers
    ]
    
    # Patterns that indicate a new section within a statement
    NEW_SECTION_PATTERNS = [
        r'^\s*note\s+\d+',             # Note X starts
        r'^\s*schedule\s+\d+',          # Schedule X starts
        r'^\s*part\s+[ivx]+\s*:',     # Part I, Part II, etc.
        r'^\s*section\s+\d+',          # Section X starts
    ]
    
    @staticmethod
    def is_continuation_page(text: str, statement_type: str) -> bool:
        """
        Check if a page continues the previous statement.
        """
        text_lower = text.lower().strip()
        
        # Check continuation markers
        for pattern in EnhancedContinuationDetection.CONTINUATION_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        
        # Check for same statement type without table
        if statement_type in ['balance_sheet', 'income_statement', 'cash_flow']:
            # If page has statement type but no table structure, might be header/continuation
            # (This is more nuanced - would need full detection logic)
            pass
        
        return False
    
    @staticmethod
    def is_new_section(text: str) -> bool:
        """Check if text indicates a new section."""
        text_lower = text.lower().strip()
        
        for pattern in EnhancedContinuationDetection.NEW_SECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        
        return False


class EnhancedItemExtractor:
    """
    Enhanced item extraction combining all improvements for 100% data capture.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.min_numbers_per_row = self.config.get('min_numbers_per_row', 1)
        self.max_label_length = self.config.get('max_label_length', 200)
    
    def extract_line_items(self, line: str, line_num: int = 0, page_num: int = 0) -> List[Dict[str, Any]]:
        """
        Extract all possible items from a line with comprehensive matching.
        
        Returns list of item dictionaries with all metadata.
        """
        items = []
        
        # Extract all numbers
        numbers = EnhancedNumberPatterns.extract_all_numbers(line)
        
        if len(numbers) < self.min_numbers_per_row:
            return []
        
        # Separate values from years
        values, years, note_ref = EnhancedNumberPatterns.extract_values_and_years(numbers, line)
        
        if not values:
            return []
        
        # Extract label
        label = EnhancedLabelExtraction.extract_label(line, numbers)
        
        # Check if label is subtotal/total (should preserve!)
        is_subtotal = EnhancedLabelExtraction.is_subtotal_label(label)
        
        # Detect indentation
        indent_level = EnhancedLabelExtraction.detect_indentation(line)
        
        # Base item
        item = {
            'id': f"p{page_num}_l{line_num}",
            'label': label,
            'raw_line': line.strip(),
            'page_num': page_num,
            'line_num': line_num,
            'indent_level': indent_level,
            'is_subtotal': is_subtotal,
            'values': values,
            'years_found': years,
            'note_ref': note_ref,
            'value_count': len(values),
            'extraction_method': 'enhanced',
        }
        
        # Add current/previous values (primary two)
        if len(values) >= 2:
            item['current_year'] = values[0]
            item['previous_year'] = values[1]
        elif len(values) == 1:
            item['current_year'] = values[0]
            item['previous_year'] = None
        
        # Check for percentage
        pct = EnhancedNumberPatterns.extract_percentage_or_ratio(line)
        if pct:
            item['percentage'] = pct.get('value')
            item['percentage_raw'] = pct.get('raw')
            item['has_percentage'] = True
        
        items.append(item)
        
        return items
    
    def extract_table_row(self, cells: List[Any], row_num: int = 0, table_num: int = 0, page_num: int = 0) -> List[Dict[str, Any]]:
        """
        Extract items from a table row with comprehensive handling.
        """
        items = []
        
        # Detect column headers
        headers = [str(c).strip() if c else '' for c in cells]
        col_detection = EnhancedColumnDetection.detect_column_headers(headers)
        
        # Find label column (first non-numeric header)
        label_col_idx = 0
        for i, header in enumerate(headers):
            header_clean = re.sub(r'[\d\s\(\)]', '', header)
            if header_clean and not re.match(r'^[\d,\.]+$', header_clean):
                label_col_idx = i
                break
        
        # Check row for values
        row_text = ' '.join(str(c) for c in cells if c)
        numbers = EnhancedNumberPatterns.extract_all_numbers(row_text)
        
        if len(numbers) < 1:
            return []
        
        # Extract label from first column
        label = str(cells[label_col_idx]).strip() if label_col_idx < len(cells) else ''
        label = EnhancedLabelExtraction._clean_label(label)
        
        # Extract values based on column detection
        current_val = None
        previous_val = None
        
        if col_detection['current'] >= 0 and col_detection['current'] < len(cells):
            current_raw = cells[col_detection['current']]
            parsed = EnhancedNumberPatterns.parse_number_with_currency(str(current_raw))
            current_val = parsed if parsed is not None else 0.0
        
        if col_detection['previous'] >= 0 and col_detection['previous'] < len(cells):
            previous_raw = cells[col_detection['previous']]
            parsed = EnhancedNumberPatterns.parse_number_with_currency(str(previous_raw))
            previous_val = parsed if parsed is not None else 0.0
        
        # Build item
        item = {
            'id': f"p{page_num}_t{table_num}_r{row_num}",
            'label': label,
            'raw_row': [str(c) for c in cells],
            'page_num': page_num,
            'table_num': table_num,
            'row_num': row_num,
            'label_col_idx': label_col_idx,
            'current_col_idx': col_detection['current'],
            'previous_col_idx': col_detection['previous'],
            'current_year': current_val,
            'previous_year': previous_val,
            'has_data': current_val is not None or previous_val is not None,
            'extraction_method': 'enhanced_table',
        }
        
        # Check for zero/nil values
        if EnhancedNumberPatterns.is_zero_or_nil(label):
            item['is_zero_or_nil'] = True
        
        items.append(item)
        return items


def create_enhanced_patterns_import_patch():
    """
    Return a patch that can be applied to parsers.py to use enhanced patterns.
    
    This function can be called to inject enhanced extraction into the existing parser.
    """
    return {
        'EnhancedNumberPatterns': EnhancedNumberPatterns,
        'EnhancedLabelExtraction': EnhancedLabelExtraction,
        'EnhancedColumnDetection': EnhancedColumnDetection,
        'EnhancedContinuationDetection': EnhancedContinuationDetection,
        'EnhancedItemExtractor': EnhancedItemExtractor,
    }


# Standalone test
if __name__ == '__main__':
    import sys
    
    print("=" * 70)
    print("Enhanced Extraction Patterns Test")
    print("=" * 70)
    print()
    print("Testing number pattern matching...")
    
    test_lines = [
        "Total Assets  1,23,45,678.90  98,76,543.20",
        "Net Income  (1,23,45,678)  1,02,34,567",
        "Profit Margin  12.5%",
        "Ratio  2.5:1",
        "Cash Equivalents  nil  -",
        "Current Assets  1.23.45.67  987.65.43",
    ]
    
    extractor = EnhancedItemExtractor()
    
    for i, line in enumerate(test_lines, 1):
        print(f"\nTest {i}: {line}")
        items = extractor.extract_line_items(line)
        if items:
            for item in items:
                print(f"  → Label: '{item['label']}'")
                print(f"     Current: {item.get('current_year')}")
                print(f"     Previous: {item.get('previous_year')}")
                print(f"     Years: {item['years_found']}")
                print(f"     Note Ref: {item.get('note_ref')}")
                if 'percentage' in item:
                    print(f"     Percentage: {item['percentage']*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("Pattern Coverage Tests")
    print("=" * 70)
    
    test_numbers = [
        "1,23,45,678.90",  # Indian
        "1.234.567,90",  # European
        "1,234,567.90",  # US
        "(123.45)",  # Parenthesis
        "[123.45]",  # Brackets
        "-123.45",  # Dash
        "12.5%",  # Percentage
        "2.5:1",  # Ratio
        "nil",  # Nil
        "-",  # Dash
        "0",  # Zero
    ]
    
    for num_str in test_numbers:
        numbers = EnhancedNumberPatterns.extract_all_numbers(num_str)
        print(f"\n  '{num_str}' → {len(numbers)} number(s) found")
        for num in numbers:
            print(f"    Value: {num['value']:.2f}, Type: {num['type']}, Negative: {num['is_negative']}")
