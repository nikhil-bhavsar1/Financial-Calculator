
import re
import logging
from typing import List, Tuple, Optional, Any, Dict, Set
from enum import Enum
from dataclasses import dataclass, field

from parser_config import (
    ParserConfig, ReportingEntity, ExtractedTable, clean_text,
    PYMUPDF_AVAILABLE, OCRResult
)
from parser_financial_stmt_detection import FinancialStatementDetector
from parser_ocr import OCRProcessor
from indian_finance_utils import IndianNumberParser

logger = logging.getLogger(__name__)


# =============================================================================
# Enhanced Table Cell with Metadata (Docling-style)
# =============================================================================

@dataclass
class EnhancedTableCell:
    """Enhanced table cell with metadata for better parsing"""
    text: str
    normalized_text: str
    row: int
    col: int
    is_header: bool = False
    is_numeric: bool = False
    is_negative: bool = False
    numeric_value: Optional[float] = None
    colspan: int = 1
    rowspan: int = 1
    confidence: float = 1.0
    financial_category: Optional[str] = None  # 'assets', 'liabilities', 'equity', 'income', 'expenses'
    
    def __post_init__(self):
        if not self.normalized_text:
            self.normalized_text = self._normalize_text(self.text)
        self._detect_numeric()
        self._detect_financial_category()
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text: lowercase, clean whitespace"""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _detect_numeric(self):
        """Detect if cell contains numeric value using Indian formats"""
        parser = IndianNumberParser()
        val = parser.parse_indian_formatted_number(self.text)
        
        # Check explicit None or 0 with care (parser returns 0.0 for invalid)
        # But parser returns 0.0 for empty/invalid.
        # We only want to enable is_numeric if it successfully parsed.
        # But wait, 0.0 IS numeric.
        # Check text if it has digits.
        has_digits = bool(re.search(r'\d', self.text))
        
        if not has_digits:
             return

        if val is not None: # parse_indian returns float or None (in User provided code? No, user provided code returns 0.0 for invalid? Check user code again)
            # User Code: 
            # if not number_str ... return 0.0
            # try: float(clean) catch: return None
            # So valid 0.0 is possible. Invalid is 0.0 or None depending on path.
            # safe way: use parse_mixed if simple fails?
            pass
            
        # Simplified robust logic:
        # 1. Try format
        val = parser.parse_indian_formatted_number(self.text)
        if val is not None:
             self.numeric_value = val
             self.is_numeric = True
             self.is_negative = val < 0
        elif has_digits:
             # Fallback
             val_mixed = parser.parse_mixed_indian_us_format(self.text)
             self.numeric_value = val_mixed
             self.is_numeric = True
             self.is_negative = val_mixed < 0
    
    def _detect_financial_category(self):
        """Detect financial category from text"""
        text_lower = self.normalized_text
        
        categories = {
            'assets': ['assets', 'asset', 'ppe', 'inventory', 'inventories', 'receivables', 
                      'cash', 'investments', 'property', 'equipment', 'goodwill', 'intangible',
                      'fixed', 'current assets', 'non-current'],
            'liabilities': ['liabilities', 'liability', 'borrowings', 'payables', 'debt', 
                           'loans', 'provisions', 'creditors', 'dues', 'current liabilities',
                           'non-current liabilities', 'long term', 'short term'],
            'equity': ['equity', 'capital', 'share', 'reserves', 'retained', 'earnings', 
                      'surplus', 'warrants', 'shareholders', 'owners'],
            'income': ['revenue', 'sales', 'income', 'turnover', 'gross', 'net', 'profit', 
                      'loss', 'earnings', 'ebitda', 'ebit', 'operating', 'total income'],
            'expenses': ['expenses', 'expense', 'cost', 'cogs', 'overhead', 'administrative', 
                        'selling', 'finance', 'depreciation', 'amortization', 'tax'],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    self.financial_category = category
                    return


# =============================================================================
# Financial Keywords for Detection
# =============================================================================

FINANCIAL_KEYWORDS = {
    'assets': ['assets', 'asset', 'ppe', 'inventory', 'inventories', 'receivables', 
               'cash', 'investments', 'property', 'equipment', 'goodwill', 'intangible',
               'fixed', 'current assets', 'non-current', 'cwip', 'work in progress'],
    'liabilities': ['liabilities', 'liability', 'borrowings', 'payables', 'debt', 
                   'loans', 'provisions', 'creditors', 'dues', 'current liabilities',
                   'non-current liabilities', 'long term', 'short term'],
    'equity': ['equity', 'capital', 'share', 'reserves', 'retained', 'earnings', 
              'surplus', 'warrants', 'shareholders', 'owners', 'funds'],
    'income': ['revenue', 'sales', 'income', 'turnover', 'gross', 'net', 'profit', 
              'loss', 'earnings', 'ebitda', 'ebit', 'operating', 'total income'],
    'expenses': ['expenses', 'expense', 'cost', 'cogs', 'overhead', 'administrative', 
                'selling', 'finance', 'depreciation', 'amortization', 'tax', 'interest'],
}

# =============================================================================
# Table Extraction
# =============================================================================

class TableExtractionMethod(Enum):
    """Methods for table extraction."""
    PYMUPDF_NATIVE = "pymupdf_native"
    TEXT_PATTERN = "text_pattern"
    OCR = "ocr"
    HYBRID = "hybrid"


class TableExtractor:
    """
    Extracts tabular data from PDF pages.
    Uses multiple methods with fallbacks for robustness.
    """
    
    # Pattern for Indian number format
    INDIAN_NUMBER_PATTERN = r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?'
    
    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()
        self.detector = FinancialStatementDetector(config)
    
    def extract_from_page(
        self,
        page,
        page_num: int,
        reporting_entity: ReportingEntity = ReportingEntity.UNKNOWN,
        ocr_processor: Optional[OCRProcessor] = None
    ) -> List[ExtractedTable]:
        """
        Extract tables from a PDF page using multiple methods.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number
            reporting_entity: Known reporting entity
            ocr_processor: Optional OCR processor for image-based pages
            
        Returns:
            List of ExtractedTable objects
        """
        tables = []
        
        # Method 1: PyMuPDF native table finder (most accurate for digital PDFs)
        native_tables = self._extract_pymupdf_native(page, page_num, reporting_entity)
        if native_tables:
            tables.extend(native_tables)
        
        # Method 2: Text-based extraction
        try:
            text = page.get_text("text")
            text_tables = self._extract_from_text(text, page_num, reporting_entity)
            
            # Only add text tables if no native tables found
            if not tables and text_tables:
                tables.extend(text_tables)
        except Exception as e:
            logger.debug(f"Text extraction failed: {e}")
        
        # Method 3: OCR fallback for image-based pages
        if not tables and ocr_processor and ocr_processor.is_available:
            ocr_tables = self._extract_with_ocr(
                page, page_num, reporting_entity, ocr_processor
            )
            tables.extend(ocr_tables)
        
        return tables
    
    def _extract_pymupdf_native(
        self,
        page,
        page_num: int,
        reporting_entity: ReportingEntity
    ) -> List[ExtractedTable]:
        """Extract tables using PyMuPDF's built-in table finder."""
        tables = []
        
        if not PYMUPDF_AVAILABLE:
            return tables
        
        try:
            if hasattr(page, 'find_tables'):
                found_tables = page.find_tables()
                
                for table in found_tables:
                    if table.row_count >= self.config.table_detection_min_rows:
                        extracted = self._process_pymupdf_table(
                            table, page_num, reporting_entity
                        )
                        if extracted:
                            tables.append(extracted)
        except Exception as e:
            logger.debug(f"PyMuPDF table extraction failed: {e}")
        
        return tables
    
    def _process_pymupdf_table(
        self,
        table,
        page_num: int,
        reporting_entity: ReportingEntity
    ) -> Optional[ExtractedTable]:
        """Process a table found by PyMuPDF."""
        try:
            data = table.extract()
            
            if not data or len(data) < self.config.table_detection_min_rows:
                return None
            
            # Clean headers and rows
            headers = [
                clean_text(str(cell)) if cell else ""
                for cell in data[0]
            ]
            
            rows = []
            for row_data in data[1:]:
                row = [
                    clean_text(str(cell)) if cell else ""
                    for cell in row_data
                ]
                # Only include rows with some content
                if any(cell.strip() for cell in row):
                    rows.append(row)
            
            if not rows:
                return None
            
            # Detect statement type from table content
            all_text = ' '.join(headers + [' '.join(row) for row in rows])
            stmt_type, confidence = self.detector.detect_statement_type(all_text)
            
            return ExtractedTable(
                page_num=page_num,
                headers=headers,
                rows=rows,
                statement_type=stmt_type,
                reporting_entity=reporting_entity,
                confidence=confidence,
                extraction_method=TableExtractionMethod.PYMUPDF_NATIVE.value
            )
            
        except Exception as e:
            logger.debug(f"Table processing failed: {e}")
            return None
    
    def _extract_from_text(
        self,
        text: str,
        page_num: int,
        reporting_entity: ReportingEntity
    ) -> List[ExtractedTable]:
        """Extract tables from text using pattern matching."""
        tables = []
        lines = text.split('\n')
        
        # Find table regions
        table_regions = self._find_table_regions(lines)
        
        for start_idx, end_idx in table_regions:
            table_lines = lines[start_idx:end_idx]
            headers, rows = self._parse_table_lines(table_lines)
            
            if rows and len(rows) >= 2:
                all_text = ' '.join([' '.join(headers)] + [' '.join(r) for r in rows])
                stmt_type, confidence = self.detector.detect_statement_type(all_text)
                
                tables.append(ExtractedTable(
                    page_num=page_num,
                    headers=headers,
                    rows=rows,
                    statement_type=stmt_type,
                    reporting_entity=reporting_entity,
                    confidence=confidence * 0.8,  # Slightly lower confidence for text extraction
                    extraction_method=TableExtractionMethod.TEXT_PATTERN.value
                ))
        
        return tables
    
    def _find_table_regions(self, lines: List[str]) -> List[Tuple[int, int]]:
        """Find regions that likely contain tables - Enhanced for better capture."""
        regions = []
        in_table = False
        table_start = 0
        consecutive_data_lines = 0
        potential_table_lines = 0
        
        # Enhanced patterns for table detection
        number_patterns = [
            r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?',  # Standard format
            r'\d{1,3}(?:,\d{2,3})+(?:\.\d+)?',  # Indian format
        ]
        
        # Financial term indicators that suggest table content
        financial_indicators = [
            r'\b(?:assets?|liabilities?|equity|income|expenses?|revenue|profit|loss|sales|cost)\b',
            r'\b(?:total|sub-?total|net|gross)\s+\w+',
            r'\b(?:cash|bank|investments?|receivables?|payables?|inventory|stock)\b',
            r'\b(?:borrowings?|debt|loans?|advances?|deposits?)\b',
            r'\b(?:share|capital|reserves?|retained|earnings?)\b',
        ]
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_lower = line.lower()
            line_length = len(line_stripped)
            
            # Check for numbers using multiple patterns
            has_numbers = any(re.search(pattern, line) for pattern in number_patterns)
            
            # Check for text - more relaxed (2+ chars instead of 3+)
            has_text = bool(re.search(r'[a-zA-Z]{2,}', line))
            
            # Check for financial indicators
            has_financial_terms = any(re.search(pattern, line_lower) for pattern in financial_indicators)
            
            # Line looks like table data if it has both text and numbers
            # OR if it has financial terms and numbers
            # OR if it's a short line with numbers (could be a subtotal/total)
            is_data_line = (has_numbers and has_text and line_length > 5) or \
                          (has_numbers and has_financial_terms) or \
                          (has_numbers and line_length < 50 and has_text)
            
            if is_data_line:
                if not in_table:
                    # Start new table region, include more context lines before
                    table_start = max(0, i - 5)  # Increased from 3
                    in_table = True
                    potential_table_lines = 0
                consecutive_data_lines += 1
                potential_table_lines = 0
            else:
                # Check if this could be a header or separator line
                is_header_line = any(re.search(pattern, line_lower) for pattern in [
                    r'particulars', r'description', r'notes?', r'year\s*ended',
                    r'as\s+(?:at|of)', r'\d{4}'
                ])
                
                if is_header_line and in_table:
                    # Continue table, this is likely a header
                    consecutive_data_lines += 1
                    potential_table_lines = 0
                elif in_table:
                    potential_table_lines += 1
                    # Allow up to 2 non-data lines within a table (for spacing, headers)
                    if potential_table_lines > 2:
                        # Check if we had enough data lines - lowered from 3 to 2
                        if consecutive_data_lines >= 2:
                            regions.append((table_start, i - potential_table_lines + 1))
                        in_table = False
                        consecutive_data_lines = 0
                        potential_table_lines = 0
        
        # Don't forget trailing table - lowered threshold from 3 to 2
        if in_table and consecutive_data_lines >= 2:
            regions.append((table_start, len(lines) - potential_table_lines))
        
        return regions
    
    def _parse_table_lines(
        self,
        lines: List[str]
    ) -> Tuple[List[str], List[List[str]]]:
        """Parse table lines into headers and data rows with enhanced year detection."""
        headers = []
        rows = []
        
        # PHASE 1: Detect year header row
        # Financial statements often have a row like "2025   2024   2023" or dates
        year_header_idx = -1
        year_header_content = []
        date_prefix = ""
        
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line_stripped = line.strip()
            
            # Check for date prefix like "September 30," or "As at"
            if re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{0,2}\s*,?\s*$', line_stripped, re.I):
                date_prefix = line_stripped
                continue
            if re.search(r'^As\s+(at|of)\s*$', line_stripped, re.I):
                date_prefix = line_stripped
                continue
            if re.search(r'^For\s+the\s+(year|period)\s+ended?\s*$', line_stripped, re.I):
                date_prefix = line_stripped
                continue
            
            # Check if this line is entirely years
            years_in_line = re.findall(r'\b(20\d{2}|19\d{2})\b', line_stripped)
            non_year_content = re.sub(r'\b(20\d{2}|19\d{2})\b', '', line_stripped).strip()
            non_year_content = re.sub(r'[\s\$\|\-]+', '', non_year_content)
            
            # If line has 2+ years and almost nothing else, it's a year header
            if len(years_in_line) >= 2 and len(non_year_content) < 15:
                year_header_idx = i
                year_header_content = years_in_line
                break
        
        # PHASE 2: Find description/particulars header row
        header_idx = -1
        header_patterns = [
            r'particulars',
            r'description',
            r'items?\s*$',
            r'note\s*(?:no\.?)?\s*$'
        ]
        
        for i, line in enumerate(lines[:8]):
            line_lower = line.lower()
            if any(re.search(p, line_lower) for p in header_patterns):
                header_idx = i
                break
        
        # PHASE 3: Build headers
        if header_idx >= 0:
            base_headers = self._split_table_line(lines[header_idx])
            
            # If we found year headers, combine them
            if year_header_content:
                # First column is the label column, rest are years
                if base_headers:
                    headers = [base_headers[0]] + year_header_content
                else:
                    headers = ["Particulars"] + year_header_content
            else:
                headers = base_headers
            
            # Data starts after the header row (and year row if present)
            data_start = max(header_idx + 1, year_header_idx + 1 if year_header_idx >= 0 else header_idx + 1)
            data_lines = lines[data_start:]
        elif year_header_content:
            # No label header found, but we have years
            headers = ["Particulars"] + year_header_content
            data_lines = lines[year_header_idx + 1:]
        else:
            data_lines = lines
        
        # PHASE 4: Parse data rows
        for line in data_lines:
            if not line.strip():
                continue
            
            # Skip lines that are ONLY years (already used as headers)
            years_in_line = re.findall(r'\b(20\d{2}|19\d{2})\b', line)
            non_year_text = re.sub(r'\b(20\d{2}|19\d{2})\b', '', line).strip()
            non_year_text = re.sub(r'[\s\$\|\-]+', '', non_year_text)
            if len(years_in_line) >= 2 and len(non_year_text) < 5:
                continue
            
            # Check if line has enough numbers to be a data row
            numbers = re.findall(self.INDIAN_NUMBER_PATTERN, line)
            
            if len(numbers) >= self.config.min_numbers_per_row:
                row = self._split_table_line(line)
                if row and len(row) >= 2:
                    rows.append(row)
            elif len(numbers) == 1:
                row = self._split_table_line(line)
                if row and len(row) >= 2:
                    label_text = row[0].strip()
                    if len(label_text) > 8 and not re.match(r'^Page\s*\d+$', label_text, re.I):
                        rows.append(row)
        
        return headers, rows
    
    def _split_table_line(self, line: str) -> List[str]:
        """Split a table line into columns."""
        # Try multiple splitting strategies
        
        # Strategy 1: Multiple spaces
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 2:
            return [p.strip() for p in parts if p.strip()]
        
        # Strategy 2: Tabs
        parts = line.split('\t')
        if len(parts) >= 2:
            return [p.strip() for p in parts if p.strip()]
        
        # Strategy 3: Split before numbers
        # Find where numbers start and split there
        number_match = re.search(self.INDIAN_NUMBER_PATTERN, line)
        if number_match:
            label = line[:number_match.start()].strip()
            numbers_part = line[number_match.start():].strip()
            
            # Split numbers
            numbers = re.findall(self.INDIAN_NUMBER_PATTERN, numbers_part)
            if label and numbers:
                return [label] + numbers
        
        # Fallback: return as single cell
        return [line.strip()] if line.strip() else []
    
    def _extract_with_ocr(
        self,
        page,
        page_num: int,
        reporting_entity: ReportingEntity,
        ocr_processor: OCRProcessor
    ) -> List[ExtractedTable]:
        """Extract tables using OCR for image-based pages."""
        tables = []
        
        try:
            ocr_result = ocr_processor.process_page(page, page_num, force_ocr=True)
            
            if ocr_result.is_successful and ocr_result.text:
                text_tables = self._extract_from_text(
                    ocr_result.text,
                    page_num,
                    reporting_entity
                )
                
                # Adjust confidence based on OCR confidence
                ocr_factor = ocr_result.confidence / 100
                for table in text_tables:
                    table.confidence *= ocr_factor
                    table.extraction_method = TableExtractionMethod.OCR.value
                
                tables.extend(text_tables)
                
        except Exception as e:
            logger.debug(f"OCR table extraction failed: {e}")
        
        return tables
    
    # =============================================================================
    # Enhanced Extraction Methods (Docling-style)
    # =============================================================================
    
    # =============================================================================
    # Enhanced Extraction Methods (Graph Reconstruction)
    # =============================================================================
    
    def extract_with_enhanced_metadata(
        self,
        page,
        page_num: int,
        reporting_entity: ReportingEntity = ReportingEntity.UNKNOWN
    ) -> Tuple[List[ExtractedTable], List[Any]]:
        """
        Extract tables and rebuild them as semantic graphs.
        
        Returns:
            Tuple of (tables, financial_graphs)
        """
        # Lazy import to avoid circular dep at module level if any
        from table_graph_builder import TableGraphBuilder, FinancialTableGraph
        
        tables = self.extract_from_page(page, page_num, reporting_entity)
        graphs = []
        
        builder = TableGraphBuilder()
        
        for table in tables:
            # Reconstruct Graph (Gap 1 & 2)
            graph = builder.build_graph(table)
            graphs.append(graph)
            
        return tables, graphs

    
    def detect_table_structure(
        self,
        lines: List[str],
        page_num: int
    ) -> Optional[Dict[str, Any]]:
        """
        Detect table structure with detailed analysis.
        
        Returns:
            Dictionary with table structure info or None
        """
        regions = self._find_table_regions(lines)
        
        if not regions:
            return None
        
        structures = []
        for start_idx, end_idx in regions:
            table_lines = lines[start_idx:end_idx]
            headers, rows = self._parse_table_lines(table_lines)
            
            # Analyze structure
            structure = {
                'page': page_num,
                'start_line': start_idx,
                'end_line': end_idx,
                'headers': headers,
                'row_count': len(rows),
                'col_count': len(headers) if headers else (len(rows[0]) if rows else 0),
                'has_year_headers': any(re.search(r'20\d{2}|19\d{2}', h) for h in headers),
                'has_particulars': any('particulars' in h.lower() or 'description' in h.lower() for h in headers),
                'financial_categories': self._detect_categories_in_rows(rows),
                'confidence': self._calculate_structure_confidence(headers, rows)
            }
            structures.append(structure)
        
        return structures[0] if structures else None
    
    def _detect_categories_in_rows(self, rows: List[List[str]]) -> Set[str]:
        """Detect financial categories present in table rows"""
        categories = set()
        
        for row in rows:
            if not row:
                continue
            label = row[0] if row else ""
            label_lower = label.lower()
            
            for category, keywords in FINANCIAL_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in label_lower:
                        categories.add(category)
                        break
        
        return categories
    
    def _calculate_structure_confidence(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> float:
        """Calculate confidence score for table structure"""
        if not rows:
            return 0.0
        
        scores = []
        
        # Check header quality
        if headers:
            has_particulars = any('particulars' in h.lower() or 'description' in h.lower() for h in headers)
            has_years = any(re.search(r'20\d{2}|19\d{2}', h) for h in headers)
            if has_particulars and has_years:
                scores.append(1.0)
            elif has_particulars or has_years:
                scores.append(0.7)
            else:
                scores.append(0.4)
        
        # Check row consistency
        col_counts = [len(row) for row in rows]
        if col_counts:
            avg_cols = sum(col_counts) / len(col_counts)
            consistency = 1.0 - (max(col_counts) - min(col_counts)) / max(col_counts) if max(col_counts) > 0 else 0
            scores.append(consistency)
        
        # Check for financial keywords
        financial_rows = 0
        for row in rows:
            if not row:
                continue
            label = row[0] if row else ""
            for keywords in FINANCIAL_KEYWORDS.values():
                if any(kw in label.lower() for kw in keywords):
                    financial_rows += 1
                    break
        
        if rows:
            financial_ratio = financial_rows / len(rows)
            scores.append(financial_ratio)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def normalize_table_content(self, table: ExtractedTable) -> ExtractedTable:
        """
        Normalize table content: lowercase headers and cells, clean whitespace.
        """
        # Normalize headers
        table.headers = [
            self._normalize_cell_text(h) for h in table.headers
        ]
        
        # Normalize rows
        normalized_rows = []
        for row in table.rows:
            normalized_row = [
                self._normalize_cell_text(cell) for cell in row
            ]
            normalized_rows.append(normalized_row)
        
        table.rows = normalized_rows
        return table
    
    def _normalize_cell_text(self, text: str) -> str:
        """Normalize cell text: lowercase and clean whitespace"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip
        text = text.strip()
        return text
