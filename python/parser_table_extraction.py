
import re
import logging
from typing import List, Tuple, Optional, Any
from enum import Enum

from parser_config import (
    ParserConfig, ReportingEntity, ExtractedTable, clean_text,
    PYMUPDF_AVAILABLE, OCRResult
)
from parser_financial_stmt_detection import FinancialStatementDetector
from parser_ocr import OCRProcessor

logger = logging.getLogger(__name__)

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
        """Find regions that likely contain tables."""
        regions = []
        in_table = False
        table_start = 0
        consecutive_data_lines = 0
        
        for i, line in enumerate(lines):
            has_numbers = bool(re.search(self.INDIAN_NUMBER_PATTERN, line))
            has_text = bool(re.search(r'[a-zA-Z]{3,}', line))
            line_length = len(line.strip())
            
            # Line looks like table data if it has both text and numbers
            is_data_line = has_numbers and has_text and line_length > 10
            
            if is_data_line:
                if not in_table:
                    # Start new table region, include a few lines before
                    table_start = max(0, i - 3)
                    in_table = True
                consecutive_data_lines += 1
            else:
                if in_table:
                    # Check if we had enough data lines
                    if consecutive_data_lines >= 3:
                        regions.append((table_start, i))
                    in_table = False
                    consecutive_data_lines = 0
        
        # Don't forget trailing table
        if in_table and consecutive_data_lines >= 3:
            regions.append((table_start, len(lines)))
        
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
