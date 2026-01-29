
from typing import Optional, Dict, List, Any, Set, Tuple
import logging
import json
import sys
import re
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET

# Optional dependencies
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import fitz
except ImportError:
    fitz = None


# Local imports
from parser_config import (
    ParserConfig, StatementBoundary, ExtractedTable, ParsedStatement, 
    FinancialLineItem, ReportingEntity, StatementType, StatementIdentifier, 
    ValidationIssue, ValidationSeverity, clean_text, safe_float, 
    PYMUPDF_AVAILABLE, PANDAS_AVAILABLE, OCRResult
)
from markdown_converter import MarkdownConverter
from parser_financial_stmt_detection import FinancialStatementDetector, FinancialPatternMatcher
from parser_table_extraction import TableExtractor
from parser_financial_keyword_db import FinancialKeywords
from parser_ocr import OCRProcessor

logger = logging.getLogger(__name__)

# =============================================================================
# Main Financial Parser
# =============================================================================

class FinancialParser:
    """
    Enhanced Parser for NSE/BSE Annual Report PDFs.
    
    Features:
    - Separates Standalone and Consolidated statements
    - OCR support for scanned documents
    - Multiple table extraction methods
    - Comprehensive validation
    - Robust error handling
    
    Output structure:
    {
        "standalone": {
            "balance_sheet": {...},
            "income_statement": {...},
            "cash_flow": {...}
        },
        "consolidated": {
            "balance_sheet": {...},
            "income_statement": {...},
            "cash_flow": {...}
        },
        "items": [...],
        "metadata": {...}
    }
    """
    
    def __init__(self, config: Optional[ParserConfig] = None):
        """
        Initialize the parser.
        
        Args:
            config: Parser configuration (uses defaults if not provided)
        """
        self.config = config or ParserConfig()
        self.detector = FinancialStatementDetector(self.config)
        self.table_extractor = TableExtractor(self.config)
        self.keywords = FinancialKeywords()
        # Initialize Markdown Converter
        self.markdown_converter = MarkdownConverter()
        
        # OCR processor (lazy initialization)
        self._ocr_processor: Optional[OCRProcessor] = None
        
        # State
        self._reset_state()
    
    def _reset_state(self):
        """Reset parser state for new document."""
        self.statement_boundaries: Dict[str, StatementBoundary] = {}
        self.extracted_tables: List[ExtractedTable] = []
        self.year_labels: Dict[str, Tuple[str, str]] = {
            'standalone': ("Current Year", "Previous Year"),
            'consolidated': ("Current Year", "Previous Year"),
        }
        self.debug_info: List[str] = []
        self._seen_ids: Set[str] = set()
        self._current_entity: ReportingEntity = ReportingEntity.UNKNOWN
        self._validation_issues: List[ValidationIssue] = []
        # Cache for converted pages to avoid re-conversion
        self.markdown_cache: Dict[int, str] = {}
    
    @property
    def ocr_processor(self) -> Optional[OCRProcessor]:
        """Lazy initialization of OCR processor."""
        if self._ocr_processor is None and self.config.use_ocr:
            try:
                self._ocr_processor = OCRProcessor(self.config)
                if self._ocr_processor.is_available:
                    logger.info(f"OCR initialized: {self._ocr_processor.ocr_engine.get_active_engine()}")
                else:
                    logger.warning("OCR not available")
                    self._ocr_processor = None
            except Exception as e:
                logger.warning(f"Failed to initialize OCR: {e}")
                self._ocr_processor = None
        return self._ocr_processor
    
    def _log_debug(self, message: str):
        """Add debug message."""
        if len(self.debug_info) < self.config.max_debug_entries:
            self.debug_info.append(message)
        logger.debug(message)
    
    # =========================================================================
    # Main Entry Points
    # =========================================================================
    
    def parse(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for parsing financial documents.
        
        Args:
            file_path: Path to the file
            file_type: File type ('pdf', 'xlsx', 'csv', 'xbrl'). Auto-detected if None.
            
        Returns:
            Parsed financial data dictionary
        """
        self._reset_state()
        
        # Determine file type
        if file_type is None:
            file_type = Path(file_path).suffix.lower().lstrip('.')
        
        file_type = file_type.lower()
        
        # Route to appropriate parser
        try:
            if file_type == 'pdf':
                result = self._parse_pdf(file_path)
            elif file_type in ('xlsx', 'xls'):
                result = self._parse_excel(file_path)
            elif file_type in ('csv', 'txt'):
                result = self._parse_text_file(file_path)
            elif file_type in ('md', 'markdown'):
                result = self._parse_markdown_file(file_path)
            elif file_type in ('xml', 'xbrl'):
                result = self._parse_xbrl(file_path)
            else:
                result = self._create_empty_result()
                result['metadata']['error'] = f"Unsupported file type: {file_type}"
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            result = self._create_empty_result()
            result['metadata']['error'] = str(e)
            import traceback
            result['metadata']['traceback'] = traceback.format_exc()
        
        # Validate if enabled
        if self.config.validate_output and result.get('items'):
            self._validate_result(result)
            result['metadata']['validation'] = {
                'issues': [issue.to_dict() for issue in self._validation_issues],
                'is_valid': not any(
                    issue.severity == ValidationSeverity.ERROR 
                    for issue in self._validation_issues
                )
            }
        
        return result
    
    def parse_to_json(self, file_path: str, file_type: Optional[str] = None) -> str:
        """Parse and return JSON string."""
        result = self.parse(file_path, file_type)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    # =========================================================================
    # Result Structure
    # =========================================================================
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result structure."""
        statement_template = {
            "items": [],
            "pages": [],
            "sections": {},
            "title": "",
            "yearLabels": {
                "current": "Current Year",
                "previous": "Previous Year"
            }
        }
        
        return {
            "standalone": {
                "balance_sheet": dict(statement_template),
                "income_statement": dict(statement_template),
                "cash_flow": dict(statement_template),
            },
            "consolidated": {
                "balance_sheet": dict(statement_template),
                "income_statement": dict(statement_template),
                "cash_flow": dict(statement_template),
            },
            "items": [],
            "metadata": {
                "parser_version": "2.0.0",
                "config": self.config.to_dict() if self.config.include_debug_info else {}
            },
        }
    
    # =========================================================================
    # PDF Parsing
    # =========================================================================
    
    def _parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse PDF document."""
        if not PYMUPDF_AVAILABLE:
            result = self._create_empty_result()
            result['metadata']['error'] = "PyMuPDF not installed. Run: pip install PyMuPDF"
            return result
        
        result = self._create_empty_result()
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            self._log_debug(f"Opened PDF: {pdf_path} ({total_pages} pages)")
            
            # Step 1: Determine which pages need OCR
            ocr_page_map = self._identify_ocr_pages(doc, pdf_path)
            
            # Step 2: Scan for all financial statements
            statement_map = self._scan_for_statements(doc, ocr_page_map)
            
            # Step 3: Extract year labels
            self._extract_all_year_labels(doc, statement_map, ocr_page_map)
            
            # Step 4: Parse each statement
            all_items = []
            
            for key, boundary in statement_map.items():
                entity_key = boundary.identifier.reporting_entity.value
                stmt_key = boundary.identifier.statement_type.value
                
                self._log_debug(
                    f"Processing {entity_key}/{stmt_key} (pages {boundary.pages})"
                )
                
                self._current_entity = boundary.identifier.reporting_entity
                
                # Parse statement
                parsed = self._parse_statement(doc, boundary, ocr_page_map)
                
                # Store results
                if entity_key in ['standalone', 'consolidated']:
                    result[entity_key][stmt_key] = parsed.to_dict()
                
                # Collect all items
                for item in parsed.items:
                    item_dict = item.to_dict()
                    all_items.append(item_dict)
            
            result["items"] = all_items
            
            # Collect ALL raw text from the document (native + OCR)
            # This ensures users can see the extracted content even if no structured data was found
            all_text_parts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = self._get_page_text(page, page_num, ocr_page_map)
                if page_text.strip():
                    all_text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            result["text"] = "\n\n".join(all_text_parts)
            
            # Build metadata
            result["metadata"].update(
                self._build_metadata(doc, statement_map, ocr_page_map)
            )
            
            # Add OCR status to metadata
            if ocr_page_map:
                ocr_stats = {
                    "pages_ocr_processed": len(ocr_page_map),
                    "total_chars_extracted": sum(len(r.text) for r in ocr_page_map.values()),
                    "avg_confidence": sum(r.confidence for r in ocr_page_map.values()) / len(ocr_page_map) if ocr_page_map else 0,
                    "engine": list(ocr_page_map.values())[0].method if ocr_page_map else "none"
                }
                result["metadata"]["ocr_status"] = ocr_stats
                
                # Warn if OCR quality is poor
                if ocr_stats["avg_confidence"] < 30:
                    result["metadata"]["warning"] = (
                        f"Low OCR confidence ({ocr_stats['avg_confidence']:.1f}%). "
                        "Document may be heavily formatted, watermarked, or low quality. "
                        "Consider using a cleaner scan."
                    )
            
            doc.close()
            
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            result["metadata"]["error"] = str(e)
            import traceback
            result["metadata"]["traceback"] = traceback.format_exc()
        
        return result
    
    def _identify_ocr_pages(
        self,
        doc,
        pdf_path: str
    ) -> Dict[int, OCRResult]:
        """Identify which pages need OCR and process them."""
        ocr_results = {}
        
        if not self.config.use_ocr or not self.ocr_processor:
            return ocr_results
        
        pages_needing_ocr = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            if self.config.force_ocr or self.ocr_processor.needs_ocr(page):
                pages_needing_ocr.append(page_num)
                self._log_debug(f"Page {page_num + 1} marked for OCR")
        
        if pages_needing_ocr:
            self._log_debug(f"Processing {len(pages_needing_ocr)} pages with OCR")
            
            results = self.ocr_processor.process_pages(
                doc,
                pages_needing_ocr,
                pdf_path,
                force_ocr=self.config.force_ocr
            )
            
            for result in results:
                ocr_results[result.page_num] = result
        
        return ocr_results
    
    def _get_page_text(
        self,
        page,
        page_num: int,
        ocr_map: Dict[int, OCRResult]
    ) -> str:
        """Get text from page, using Markdown Conversion or OCR result."""
        
        # 1. Check Cache
        if page_num in self.markdown_cache:
            return self.markdown_cache[page_num]

        # 2. Check OCR
        if page_num in ocr_map:
            ocr_result = ocr_map[page_num]
            if ocr_result.is_successful:
                return ocr_result.text
        
        # 3. Convert PDF Page to Markdown (Now Primary Extraction Method)
        # This ensures all table/structure logic is unified in MarkdownConverter
        try:
            md_text = self.markdown_converter.convert_page(page, page_num)
            self.markdown_cache[page_num] = md_text
            return md_text
        except Exception as e:
            logger.debug(f"Markdown conversion failed for page {page_num}: {e}")
            # Fallback to standard text
            return page.get_text("text")
    
    def _scan_for_statements(
        self,
        doc,
        ocr_map: Dict[int, OCRResult]
    ) -> Dict[str, StatementBoundary]:
        """Scan document to locate all financial statements."""
        boundaries: Dict[str, StatementBoundary] = {}
        total_pages = len(doc)
        
        current_entity = ReportingEntity.UNKNOWN
        page_classifications = []
        
        # First pass: Classify each page
        for page_num in range(total_pages):
            page = doc[page_num]
            text = self._get_page_text(page, page_num, ocr_map)
            
            # Detect entity transitions
            entity, entity_conf = self.detector.detect_reporting_entity(text)
            if entity != ReportingEntity.UNKNOWN and entity_conf > self.config.entity_detection_threshold:
                if entity != current_entity:
                    current_entity = entity
                    self._log_debug(f"Entity: {entity.value} at page {page_num + 1}")
            
            # Detect statement type
            identifier, confidence, title = self.detector.detect_full_statement(text, page_num)
            
            if (identifier.statement_type != StatementType.UNKNOWN and 
                confidence > self.config.statement_detection_threshold):
                
                # Use detected entity or current context
                if identifier.reporting_entity == ReportingEntity.UNKNOWN:
                    identifier = StatementIdentifier(
                        identifier.statement_type,
                        current_entity if current_entity != ReportingEntity.UNKNOWN
                        else ReportingEntity.STANDALONE
                    )
                
                page_classifications.append({
                    'page': page_num,
                    'identifier': identifier,
                    'confidence': confidence,
                    'title': title,
                    'has_table': self.detector.has_table_structure(text)
                })
                
                self._log_debug(
                    f"Page {page_num + 1}: {identifier.key} (conf: {confidence:.2f})"
                )
        
        # Second pass: Determine boundaries
        for i, classification in enumerate(page_classifications):
            identifier = classification['identifier']
            key = identifier.key
            start_page = classification['page']
            end_page = start_page
            
            # Find continuation pages
            for next_page in range(start_page + 1, min(start_page + self.config.max_continuation_pages, total_pages)):
                # Check if it's a new statement
                is_new_statement = any(
                    c['page'] == next_page for c in page_classifications
                )
                
                if is_new_statement:
                    break
                
                # Check if it continues this statement
                page = doc[next_page]
                text = self._get_page_text(page, next_page, ocr_map)
                
                if self._is_continuation_page(text, identifier.statement_type):
                    end_page = next_page
                else:
                    break
            
            # Store boundary
            if key not in boundaries or classification['confidence'] > boundaries[key].confidence:
                boundaries[key] = StatementBoundary(
                    identifier=identifier,
                    start_page=start_page,
                    end_page=end_page,
                    title=classification['title'],
                    confidence=classification['confidence']
                )
        
        # Check TOC for missed statements
        toc_boundaries = self._check_toc_for_statements(doc)
        for key, boundary in toc_boundaries.items():
            if key not in boundaries:
                boundaries[key] = boundary
                self._log_debug(f"Added from TOC: {key}")
        
        return boundaries
    
    def _check_toc_for_statements(self, doc) -> Dict[str, StatementBoundary]:
        """Check document TOC for statement references."""
        boundaries = {}
        
        try:
            toc = doc.get_toc()
            
            for level, title, page_num in toc:
                identifier, confidence, _ = self.detector.detect_full_statement(title)
                
                if identifier.statement_type != StatementType.UNKNOWN:
                    key = identifier.key
                    if key not in boundaries:
                        boundaries[key] = StatementBoundary(
                            identifier=identifier,
                            start_page=max(0, page_num - 1),
                            end_page=min(page_num + 1, len(doc) - 1),
                            title=title,
                            confidence=confidence * 0.8
                        )
        except Exception as e:
            logger.debug(f"TOC extraction failed: {e}")
        
        return boundaries
    
    def _is_continuation_page(self, text: str, stmt_type: StatementType) -> bool:
        """Check if page continues a statement."""
        text_lower = text.lower()
        
        # Should NOT have new statement header
        for patterns in FinancialPatternMatcher.PRIMARY_PATTERNS.values():
            for pattern in patterns:
                if re.search(pattern, text_lower[:500], re.IGNORECASE):
                    return False
        
        # Should have numbers
        numbers = re.findall(r'[\d,]+(?:\.\d{2})?', text)
        if len(numbers) < 5:
            return False
        
        # Should have content indicators
        indicators = FinancialPatternMatcher.CONTENT_INDICATORS.get(stmt_type, {})
        moderate = indicators.get('moderate', [])
        count = sum(1 for ind in moderate if ind in text_lower)
        
        return count >= 1
    
    def _extract_all_year_labels(
        self,
        doc,
        statement_map: Dict[str, StatementBoundary],
        ocr_map: Dict[int, OCRResult]
    ):
        """Extract year labels for each entity."""
        entity_pages = defaultdict(list)
        
        for key, boundary in statement_map.items():
            entity = boundary.identifier.reporting_entity.value
            entity_pages[entity].extend(boundary.pages)
        
        for entity, pages in entity_pages.items():
            # Collect text from first few pages
            combined_text = ""
            for page_num in pages[:3]:
                if page_num < len(doc):
                    page = doc[page_num]
                    combined_text += self._get_page_text(page, page_num, ocr_map)
            
            years = self.detector.detect_year_labels(combined_text)
            if years[0] != "Current Year":
                self.year_labels[entity] = years
    
    def _parse_statement(
        self,
        doc,
        boundary: StatementBoundary,
        ocr_map: Dict[int, OCRResult]
    ) -> ParsedStatement:
        """Parse a specific financial statement."""
        pages = boundary.pages
        
        # Combine text from all pages
        combined_text = ""
        for page_num in pages:
            if page_num < len(doc):
                page = doc[page_num]
                text = self._get_page_text(page, page_num, ocr_map)
                combined_text += f"\n### PAGE {page_num + 1} ###\n{text}"
        
        # Parse based on statement type
        stmt_type = boundary.identifier.statement_type
        entity = boundary.identifier.reporting_entity
        
        items, sections = self._parse_statement_text(
            combined_text, stmt_type, entity, pages
        )
        
        return ParsedStatement(
            identifier=boundary.identifier,
            items=items,
            pages=pages,
            sections=sections,
            title=boundary.title,
            year_labels=self.year_labels.get(entity.value, ("Current Year", "Previous Year"))
        )
    
    def _is_statement_table_header(self, line: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if a line is a Consolidated or Standalone statement table header.
        
        Returns:
            Tuple of (is_table_header, entity_type) where entity_type is 'consolidated', 
            'standalone', or None
        """
        line_lower = line.lower().strip()
        
        # Patterns for detecting statement table headers
        consolidated_patterns = [
            r'consolidated\s+(?:statement|balance\s+sheet|profit\s+and\s+loss|cash\s+flow)',
            r'consolidated\s+financial\s+statements?',
            r'group\s+(?:statement|balance\s+sheet)',
        ]
        
        standalone_patterns = [
            r'standalone\s+(?:statement|balance\s+sheet|profit\s+and\s+loss|cash\s+flow)',
            r'standalone\s+financial\s+statements?',
            r'separate\s+financial\s+statements?',
            r'unconsolidated\s+(?:statement|balance)',
            r'company\s+(?:statement|balance\s+sheet)',
        ]
        
        for pattern in consolidated_patterns:
            if re.search(pattern, line_lower):
                return True, 'consolidated'
        
        for pattern in standalone_patterns:
            if re.search(pattern, line_lower):
                return True, 'standalone'
        
        return False, None
    
    def _is_inside_table_structure(self, line: str, prev_lines: List[str]) -> bool:
        """
        Detect if we're likely inside a table structure based on content patterns.
        
        Returns:
            True if line appears to be part of a financial table
        """
        line_lower = line.lower().strip()
        
        # Signs we're in a table:
        # 1. Markdown table markers (|)
        if '|' in line:
            return True
        
        # 2. Multiple numbers in the line
        numbers = re.findall(r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?', line)
        text_content = re.sub(r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?', '', line).strip()
        
        # Must have numbers AND text (label + values)
        if len(numbers) >= 2 and len(text_content) > 5:
            return True
        
        # 3. Check for table-like patterns
        table_indicators = [
            r'\b(?:particulars|description)\s*$',
            r'^\s*(?:total|sub-?total|net|gross)',
            r'\b(?:assets?|liabilities?|equity|income|expenses?|revenue|profit|loss)\b',
        ]
        
        for pattern in table_indicators:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def _parse_statement_text(
        self,
        text: str,
        stmt_type: StatementType,
        entity: ReportingEntity,
        pages: List[int]
    ) -> Tuple[List[FinancialLineItem], Dict[str, List[str]]]:
        """
        Parse statement text into line items.
        
        Enhanced to:
        - Look for Consolidated/Standalone statement table headers first
        - Only extract data from within identified statement tables
        - Use terminology database for keyword matching
        """
        items = []
        sections: Dict[str, List[str]] = defaultdict(list)
        
        # Get section markers for this statement type
        section_markers = FinancialPatternMatcher.SECTION_MARKERS.get(stmt_type, {})
        current_section = list(section_markers.keys())[0] if section_markers else "GENERAL"
        current_page = pages[0] + 1 if pages else 1
        
        lines = text.split('\n')
        
        # Track state for table boundary detection
        in_statement_table = False
        explicit_table_mode = False
        expected_entity = entity.value  # 'standalone' or 'consolidated'
        lines_since_header = 0
        prev_lines = []
        table_end_indicators = 0
        
        for line in lines:
            # Track page changes
            page_match = re.search(r'### PAGE (\d+) ###', line)
            if page_match:
                current_page = int(page_match.group(1))
                continue
            
            stripped = line.strip()
            if not stripped or len(stripped) < 3:
                continue
            
            line_lower = stripped.lower()
            
            # Check for statement table header
            is_header, detected_entity = self._is_statement_table_header(stripped)
            if is_header:
                explicit_table_mode = True
                # Only process tables matching our expected entity
                if detected_entity == expected_entity or expected_entity == 'unknown':
                    in_statement_table = True
                    lines_since_header = 0
                    table_end_indicators = 0
                    self._log_debug(f"Entered {detected_entity} table on page {current_page}")
                else:
                    # Wrong entity type - skip this table
                    in_statement_table = False
                    self._log_debug(f"Skipping {detected_entity} table (expected {expected_entity})")
                continue
            
            # If we haven't found a table yet but entity is already identified,
            # still process but be more strict about matching
            if not in_statement_table and not explicit_table_mode:
                # Be more lenient if the boundary already identifies the entity
                if entity != ReportingEntity.UNKNOWN:
                    in_statement_table = True
            
            # Track table structure
            if in_statement_table:
                lines_since_header += 1
                
                # Detect potential table end (multiple consecutive non-table lines)
                if not self._is_inside_table_structure(stripped, prev_lines):
                    table_end_indicators += 1
                    if table_end_indicators > 5:
                        # Likely exited the table
                        in_statement_table = False
                        self._log_debug(f"Exited table after {lines_since_header} lines")
                        continue
                else:
                    table_end_indicators = 0  # Reset on valid table line
            
            # Skip non-financial lines
            if self.keywords.should_skip_line(line_lower):
                prev_lines.append(stripped)
                if len(prev_lines) > 5:
                    prev_lines.pop(0)
                continue
            
            # Detect section changes
            for section_name, patterns in section_markers.items():
                for pattern in patterns:
                    if re.search(pattern, line_lower, re.IGNORECASE):
                        current_section = section_name
                        break
            
            # Only extract line items if we're in a valid statement table
            if in_statement_table:
                # Extract line item
                item = self._extract_line_item(
                    stripped,
                    stmt_type.value,
                    current_section,
                    current_page,
                    entity
                )
                
                if item:
                    items.append(item)
                    sections[current_section].append(item.id)
            
            # Update prev_lines buffer
            prev_lines.append(stripped)
            if len(prev_lines) > 5:
                prev_lines.pop(0)
        
        return items, dict(sections)
    
    def _extract_line_item(
        self,
        line: str,
        statement_type: str,
        section: str,
        page_num: int,
        entity: ReportingEntity
    ) -> Optional[FinancialLineItem]:
        """Extract a financial line item from text."""
        # RELAXED FILTER: Line must act like a table row
        # Only reject obvious narrative/paragraph text
        
        if len(line) > 200: # Narrative paragraphs are usually very long
            return None
            
        line_lower = line.lower()
        
        # Clean Markdown artifacts
        clean_line = line.replace('|', ' ').replace('#', '').strip()
        
        # Only reject lines with strong narrative patterns (more relaxed)
        # Removed ' the ', 'in ' as they appear in valid terms like "Cash in hand", "Change in working capital"
        strong_narrative_indicators = [' we ', ' our ', ' was ', ' were ', ' has been ', ' have been ']
        if any(ind in clean_line.lower() for ind in strong_narrative_indicators):
            return None
            
        # Check for sentence structure - only reject if clearly a sentence with multiple clauses
        if ". " in line and line.count(". ") >= 2:
            return None
                
        # Only reject if starts with very specific narrative starters
        if line_lower.startswith(("we ", "refer ", "please ", "note that ")):
             return None

        # Find all numbers
        # Use simpler regex that catches all numbers, validation happens later
        number_pattern = r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?'
        all_numbers = re.findall(number_pattern, line)
        
        if len(all_numbers) < self.config.min_numbers_per_row:
            return None
            
        # 1. Parse Values & Detect Years (Pass 1)
        values = []
        note_ref = ""
        
        raw_year_like_count = 0
        raw_data_like_count = 0
        
        parsed_vals = []
        
        def is_likely_year_val(v, raw):
            # Negative numbers are never years
            if '-' in raw or '(' in raw: return False
            # Check integer range
            return 1990 <= v <= 2040 and v == int(v)

        for num_str in all_numbers:
            clean = num_str.strip()
            clean_val_str = re.sub(r'[\(\)\-\s]', '', clean).replace(',', '')
            if not clean_val_str: continue
            
            try:
                val = float(clean_val_str)
                # Note ref logic
                if val < 100 and '.' not in clean_val_str and val == int(val) and not note_ref:
                     note_ref = str(int(val))
                     continue
                     
                is_yr = is_likely_year_val(val, num_str)
                if is_yr: raw_year_like_count += 1
                else: raw_data_like_count += 1
                
                parsed_vals.append(val)
                values.append(num_str)
            except ValueError:
                continue

        if len(values) < 1:
            return None

        # 2. Extract Label
        label = self._extract_label(line, all_numbers)
        if not label or len(label) < self.config.min_label_length:
            return None
            
        label_lower = label.lower()
        
        # YEAR HEADER CHECK: If label is "Particulars" or similar and row has years, reject
        clean_label = re.sub(r'[^a-z]', '', label_lower)
        if clean_label in ['particulars', 'description', 'yearended', 'aslat', 'items']:
             if raw_year_like_count > 0:
                 return None

        # 3. Match Terminology
        matched_term = self._match_terminology(label_lower)
        term_id = None
        
        if matched_term:
            term_id = matched_term['key']
            standardized_label = term_id.replace('_', ' ').title()
            if standardized_label.endswith(" Eps"): standardized_label = standardized_label[:-3] + " EPS"
            if standardized_label.startswith("Ebitda"): standardized_label = "EBITDA" 
            if standardized_label.startswith("Ebit"): standardized_label = "EBIT"
            label = standardized_label
        else:
             # Logic to reject if only years found AND no term match
             if raw_data_like_count == 0 and raw_year_like_count > 0:
                 # Likely a header row (2024  2023)
                 return None
             
             # RELAXED MODE ('Find Harder'):
             # If no keyword match, STILL accept if the line looks valid
             # Criteria: Label is substantial (>8 chars) and not obvious noise
             is_valid_structure = len(label) > 8 and not re.search(r'^(page|note|total\s*$)', label_lower)
             
             if not self.keywords.matches_keyword(label_lower) and not is_valid_structure:
                 return None

        # 4. Parse Final Values (Previous/Current)
        # ... existing logic ...

            
        # Parse final values (last two are usually current and previous year)
        # Handle cases with only 1 value
        if len(values) >= 2:
            current_val = safe_float(values[-2])
            previous_val = safe_float(values[-1])
        elif len(values) == 1:
            current_val = safe_float(values[0])
            previous_val = 0.0
        else:
            return None

        # Determine characteristics
        is_total = bool(re.search(r'\btotal\b', label_lower))
        is_subtotal = is_total and any(
            word in label_lower for word in ['sub', 'net', 'gross']
        )
        is_important = term_id is not None or self.keywords.is_important_item(label)
        
        # Calculate indent level
        leading_spaces = len(line) - len(line.lstrip())
        indent_level = min(leading_spaces // 4, self.config.max_indent_level)
        
        # Generate unique ID
        entity_prefix = entity.value[:4] if entity != ReportingEntity.UNKNOWN else ""
        
        # Use Standard Term Key as base for ID if available
        base_id_str = term_id if term_id else label
        
        item_id = self._generate_id(base_id_str, entity_prefix)
        
        return FinancialLineItem(
            id=item_id,
            label=label, # Keep original label for UI display
            current_year=current_val,
            previous_year=previous_val,
            statement_type=statement_type,
            reporting_entity=entity.value,
            section=section,
            note_ref=note_ref,
            indent_level=indent_level,
            is_total=is_total,
            is_subtotal=is_subtotal,
            is_important=is_important,
            source_page=page_num,
            raw_line=line[:200] if self.config.include_raw_text else ""
        )

    def _match_terminology(self, text: str) -> Optional[Dict]:
        """
        Match text against unified terminology map.
        
        Enhanced matching:
        - Uses word boundary matching to avoid partial word matches
        - Requires minimum keyword length to prevent matching single words incorrectly
        - Prioritizes longer/more specific matches
        - Uses the full terminology database from terminology_keywords.py
        """
        try:
            # Try importing here to avoid circular imports at top level if any
            sys.path.append(str(Path(__file__).parent.parent)) 
            from terminology_keywords import TERMINOLOGY_MAP, KEYWORD_TO_TERM, KEYWORD_BOOST
            
            best_match = None
            max_score = 0
            text_lower = text.lower().strip()
            
            # MINIMUM KEYWORD LENGTH to prevent single-word/short matches
            MIN_KEYWORD_LEN = 3
            
            # Strategy 1: Try exact phrase matches first (highest priority)
            for key, data in TERMINOLOGY_MAP.items():
                for kw in data.get('keywords', []):
                    kw_lower = kw.lower().strip()
                    
                    # Skip very short keywords (prevents partial matches)
                    if len(kw_lower) < MIN_KEYWORD_LEN:
                        continue
                    
                    # Check for word-boundary match (not partial word)
                    # This prevents "revenue" matching in "non-revenue" or "tax" in "taxation"
                    pattern = r'(?:^|[\s\-\(\[,;:])' + re.escape(kw_lower) + r'(?:[\s\-\)\],;:]|$)'
                    if re.search(pattern, text_lower):
                        # Score based on:
                        # 1. Keyword length (longer = more specific)
                        # 2. Boost from terminology database
                        # 3. Exact match bonus
                        boost = data.get('boost', 1.0)
                        length_score = len(kw_lower)
                        
                        # Bonus for exact match (entire text matches keyword)
                        exact_bonus = 10 if text_lower == kw_lower else 0
                        
                        # Bonus for starting match (keyword at start of text)
                        start_bonus = 5 if text_lower.startswith(kw_lower) else 0
                        
                        score = (length_score * boost) + exact_bonus + start_bonus
                        
                        if score > max_score:
                            max_score = score
                            best_match = {'key': key, 'data': data, 'matched_keyword': kw_lower, 'score': score}
            
            # Strategy 2: If no match found, try with word tokenization
            if not best_match:
                # Split text into words and try matching multi-word phrases
                words = re.findall(r'[a-z]+(?:\s+[a-z]+)*', text_lower)
                text_words = text_lower.split()
                
                # Try 2-word, 3-word, 4-word combinations from the text
                for window_size in [4, 3, 2]:
                    if len(text_words) >= window_size:
                        for i in range(len(text_words) - window_size + 1):
                            phrase = ' '.join(text_words[i:i + window_size])
                            
                            # Look up in keyword-to-term map
                            if phrase in KEYWORD_TO_TERM:
                                term_keys = KEYWORD_TO_TERM[phrase]
                                if term_keys:
                                    key = term_keys[0]
                                    data = TERMINOLOGY_MAP.get(key, {})
                                    boost = KEYWORD_BOOST.get(phrase, 1.0)
                                    score = len(phrase) * boost
                                    
                                    if score > max_score:
                                        max_score = score
                                        best_match = {'key': key, 'data': data, 'matched_keyword': phrase, 'score': score}
            
            return best_match
            
        except ImportError:
            # Fallback if map not available
            return None
        except Exception as e:
            logger.debug(f"Terminology matching error: {e}")
            return None
    
    def _extract_label(self, line: str, numbers: List[str]) -> str:
        """Extract clean label from line."""
        if not numbers:
            return clean_text(line)
        
        # Find first number position
        first_pos = len(line)
        for num in numbers:
            pos = line.find(num.strip())
            if 0 <= pos < first_pos:
                first_pos = pos
        
        label = line[:first_pos] if first_pos > 0 else line
        
        # Clean up
        label = re.sub(r'\s+', ' ', label)
        # Remove markdown table artifacts (pipes)
        label = label.replace('|', '').strip()
        
        label = re.sub(r'[:\-–—]+$', '', label).strip()
        label = re.sub(r'^\([a-z]\)\s*', '', label, flags=re.IGNORECASE)
        label = re.sub(r'^\d+\.\s*', '', label)
        label = re.sub(r'^\d+\s+(?=[A-Z])', '', label)
        label = re.sub(r'^[-–•]\s*', '', label)
        
        return label.strip()
    
    def _generate_id(self, label: str, prefix: str = "") -> str:
        """Generate unique ID from label."""
        clean = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')[:50]
        
        if prefix:
            clean = f"{prefix}_{clean}"
        
        if not clean:
            clean = f"item_{len(self._seen_ids)}"
        
        # Ensure uniqueness
        original = clean
        counter = 1
        while clean in self._seen_ids:
            clean = f"{original}_{counter}"
            counter += 1
        
        self._seen_ids.add(clean)
        return clean
    
    def _build_metadata(
        self,
        doc,
        statement_map: Dict[str, StatementBoundary],
        ocr_map: Dict[int, OCRResult]
    ) -> Dict[str, Any]:
        """Build metadata dictionary."""
        detected = {
            "standalone": {},
            "consolidated": {},
        }
        
        stmt_type_map = {
            StatementType.BALANCE_SHEET: "balanceSheet",
            StatementType.INCOME_STATEMENT: "incomeStatement",
            StatementType.CASH_FLOW: "cashFlow",
        }
        
        for key, boundary in statement_map.items():
            entity = boundary.identifier.reporting_entity.value
            stmt_name = stmt_type_map.get(boundary.identifier.statement_type)
            
            if entity in detected and stmt_name:
                detected[entity][stmt_name] = {
                    "found": True,
                    "pages": [p + 1 for p in boundary.pages],
                    "title": boundary.title,
                    "confidence": round(boundary.confidence, 2)
                }
        
        # OCR statistics
        ocr_stats = {}
        if self.ocr_processor:
            ocr_stats = self.ocr_processor.get_statistics()
        
        return {
            "totalPages": len(doc),
            "detectedStatements": detected,
            "yearLabels": {
                entity: {"current": labels[0], "previous": labels[1]}
                for entity, labels in self.year_labels.items()
            },
            "tablesExtracted": len(self.extracted_tables),
            "ocr": ocr_stats,
            "hasStandalone": bool(detected.get("standalone")),
            "hasConsolidated": bool(detected.get("consolidated")),
            "debugInfo": self.debug_info if self.config.include_debug_info else [],
        }
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    def _validate_result(self, result: Dict[str, Any]):
        """Validate parsed results."""
        self._validation_issues = []
        
        for entity in ['standalone', 'consolidated']:
            entity_data = result.get(entity, {})
            
            for stmt_type in ['balance_sheet', 'income_statement', 'cash_flow']:
                stmt_data = entity_data.get(stmt_type, {})
                items = stmt_data.get('items', [])
                
                if not items:
                    continue
                
                self._validate_statement(items, stmt_type, entity)
        
        # Check balance sheet equation
        if self.config.check_balance_sheet_equation:
            for entity in ['standalone', 'consolidated']:
                self._validate_balance_sheet_equation(result, entity)
    
    def _validate_statement(
        self,
        items: List[Dict],
        stmt_type: str,
        entity: str
    ):
        """Validate a single statement."""
        location = f"{entity}/{stmt_type}"
        
        # Check for required totals
        labels = [item.get('label', '').lower() for item in items]
        label_text = ' '.join(labels)
        
        required_totals = {
            'balance_sheet': ['total assets'],
            'income_statement': ['profit'],
            'cash_flow': ['net']
        }
        
        for required in required_totals.get(stmt_type, []):
            if required not in label_text:
                self._validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing expected term: {required}",
                    location=location
                ))
        
        # Check for extreme variations
        if self.config.flag_extreme_variations:
            for item in items:
                var_pct = item.get('variationPercent')
                if var_pct is not None and abs(var_pct) > self.config.extreme_variation_threshold:
                    self._validation_issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Extreme variation: {var_pct:.1f}%",
                        location=f"{location}/{item.get('label', 'Unknown')}",
                        details={"item": item.get('label'), "variation": var_pct}
                    ))
    
    def _validate_balance_sheet_equation(self, result: Dict, entity: str):
        """Validate Assets = Liabilities + Equity."""
        bs_items = result.get(entity, {}).get('balance_sheet', {}).get('items', [])
        
        if not bs_items:
            return
        
        def find_total(items: List[Dict], keywords: List[str]) -> Optional[float]:
            for item in items:
                label_lower = item.get('label', '').lower()
                if any(kw in label_lower for kw in keywords):
                    return item.get('currentYear')
            return None
        
        total_assets = find_total(bs_items, ['total assets'])
        total_liab_eq = find_total(bs_items, ['total equity and liabilities', 'total liabilities and equity'])
        
        if total_assets is not None and total_liab_eq is not None:
            diff = abs(total_assets - total_liab_eq)
            if diff > 0.01:
                self._validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Balance sheet doesn't balance: Assets ({total_assets}) != Liabilities+Equity ({total_liab_eq})",
                    location=f"{entity}/balance_sheet",
                    details={
                        "total_assets": total_assets,
                        "total_liabilities_equity": total_liab_eq,
                        "difference": diff
                    }
                ))
    
    # =========================================================================
    # Excel Parsing
    # =========================================================================
    
    def _parse_excel(self, file_path: str) -> Dict[str, Any]:
        """Parse Excel file."""
        if not PANDAS_AVAILABLE:
            result = self._create_empty_result()
            result['metadata']['error'] = "Pandas not installed. Run: pip install pandas openpyxl"
            return result
        
        result = self._create_empty_result()
        all_items = []
        
        try:
            xl = pd.ExcelFile(file_path)
            
            for sheet_name in xl.sheet_names:
                sheet_lower = sheet_name.lower()
                
                # Detect entity from sheet name
                if 'consolidated' in sheet_lower:
                    entity = ReportingEntity.CONSOLIDATED
                elif 'standalone' in sheet_lower or 'separate' in sheet_lower:
                    entity = ReportingEntity.STANDALONE
                else:
                    entity = ReportingEntity.STANDALONE
                
                # Detect statement type
                if any(kw in sheet_lower for kw in ['balance', 'position', 'assets']):
                    stmt_type = StatementType.BALANCE_SHEET
                elif any(kw in sheet_lower for kw in ['profit', 'loss', 'income', 'p&l']):
                    stmt_type = StatementType.INCOME_STATEMENT
                elif any(kw in sheet_lower for kw in ['cash', 'flow']):
                    stmt_type = StatementType.CASH_FLOW
                else:
                    stmt_type = StatementType.UNKNOWN
                
                # Read sheet
                df = xl.parse(sheet_name, header=None)
                
                # Find header row
                header_row = None
                for idx, row in df.iterrows():
                    row_text = ' '.join(str(cell) for cell in row if pd.notna(cell)).lower()
                    if 'particulars' in row_text or 'description' in row_text:
                        header_row = idx
                        break
                
                if header_row is not None:
                    df.columns = df.iloc[header_row]
                    df = df.iloc[header_row + 1:]
                
                # Parse rows
                for idx, row in df.iterrows():
                    values = [v for v in row if pd.notna(v)]
                    if len(values) >= 3:
                        try:
                            label = str(values[0])
                            curr = float(values[-2])
                            prev = float(values[-1])
                            
                            entity_prefix = entity.value[:4]
                            item_id = self._generate_id(label, entity_prefix)
                            
                            item = FinancialLineItem(
                                id=item_id,
                                label=label,
                                current_year=curr,
                                previous_year=prev,
                                statement_type=stmt_type.value,
                                reporting_entity=entity.value,
                                section="",
                                note_ref="",
                                indent_level=0,
                                is_total='total' in label.lower(),
                                is_subtotal=False,
                                is_important=self.keywords.is_important_item(label),
                                source_page=0,
                            )
                            
                            item_dict = item.to_dict()
                            all_items.append(item_dict)
                            
                            # Store in appropriate location
                            entity_key = entity.value
                            stmt_key = stmt_type.value
                            
                            if entity_key in result and stmt_key in result[entity_key]:
                                result[entity_key][stmt_key]['items'].append(item_dict)
                            
                        except (ValueError, TypeError):
                            continue
            
            result['items'] = all_items
            result['metadata']['sheets_processed'] = xl.sheet_names
            
        except Exception as e:
            logger.error(f"Excel parsing failed: {e}")
            result['metadata']['error'] = str(e)
        
        return result
    
    # =========================================================================
    # Text/CSV Parsing
    # =========================================================================
    
    def _parse_text_file(self, file_path: str) -> Dict[str, Any]:
        """Parse text or CSV file."""
        result = self._create_empty_result()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect year labels
            years = self.detector.detect_year_labels(content)
            entity = ReportingEntity.STANDALONE
            
            items = []
            lines = content.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Try CSV format
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        try:
                            label = parts[0]
                            curr = safe_float(parts[1])
                            prev = safe_float(parts[2])
                            
                            item_id = self._generate_id(label)
                            
                            item = FinancialLineItem(
                                id=item_id,
                                label=label,
                                current_year=curr,
                                previous_year=prev,
                                statement_type="unknown",
                                reporting_entity=entity.value,
                                section="",
                                note_ref="",
                                indent_level=0,
                                is_total='total' in label.lower(),
                                is_subtotal=False,
                                is_important=self.keywords.is_important_item(label),
                                source_page=1,
                            )
                            
                            items.append(item.to_dict())
                            
                        except ValueError:
                            continue
            
            result['items'] = items
            result['standalone']['balance_sheet']['items'] = items
            self.year_labels['standalone'] = years
            
        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            result['metadata']['error'] = str(e)
        
        return result
    
    # =========================================================================
    # XBRL Parsing
    # =========================================================================
    
    def _parse_xbrl(self, file_path: str) -> Dict[str, Any]:
        """Parse XBRL/XML file."""
        result = self._create_empty_result()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove namespaces for easier parsing
            content = re.sub(r'\sxmlns(?::[a-z]+)?="[^"]+"', '', content)
            
            root = ET.fromstring(content)
            
            items = []
            entity = ReportingEntity.STANDALONE
            
            for elem in root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                if tag.lower() in ['root', 'data', 'financials', 'document']:
                    continue
                
                # Try to get current and previous values
                curr = elem.get('current') or elem.get('cy')
                prev = elem.get('previous') or elem.get('py')
                
                if curr is None:
                    for child in elem:
                        child_tag = child.tag.split('}')[-1].lower()
                        if child_tag in ['current', 'cy', 'currentyear']:
                            curr = child.text
                        elif child_tag in ['previous', 'py', 'previousyear', 'prior']:
                            prev = child.text
                
                if curr is not None and prev is not None:
                    try:
                        curr_val = float(curr)
                        prev_val = float(prev)
                        
                        label = tag.replace('_', ' ').replace('-', ' ').title()
                        item_id = self._generate_id(tag)
                        
                        item = FinancialLineItem(
                            id=item_id,
                            label=label,
                            current_year=curr_val,
                            previous_year=prev_val,
                            statement_type="unknown",
                            reporting_entity=entity.value,
                            section="",
                            note_ref="",
                            indent_level=0,
                            is_total='total' in tag.lower(),
                            is_subtotal=False,
                            is_important=False,
                            source_page=0,
                        )
                        
                        items.append(item.to_dict())
                        
                    except ValueError:
                        continue
            
            result['items'] = items
            
        except ET.ParseError as e:
            result['metadata']['error'] = f"XML Parse Error: {e}"
        except Exception as e:
            result['metadata']['error'] = str(e)
        
        return result
    
    def _parse_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a Markdown document."""
        result = self._create_empty_result()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Mock a 'doc' structure by splitting content into pages if possible
            # But since it's a flat file, we treat it as single or multiple pages if delimiter found
            
            # Re-use _scan_for_statements logic? 
            # It expects a 'doc' object (PyMuPDF). 
            # We can refactor scanning OR wrap content in a Mock object.
            
            # Simple approach: Treat whole content as text for detection
            
            # Since _scan_for_statements relies on page-by-page iteration via 'doc',
            # we will CREATE a mock doc object
            
            class MockPage:
                def __init__(self, text):
                    self.text = text
                def get_text(self, option="text"):
                    return self.text
            
            class MockDoc:
                def __init__(self, text_content):
                    # Split by page delimiter if present
                    pages_text = text_content.split('--- Page')
                    self.pages = []
                    if len(pages_text) > 1:
                        # Reconstruct pages
                        for p in pages_text:
                            if not p.strip(): continue
                            # p might start with " 1 ---\n"
                            clean_p = p
                            if re.match(r'\s*\d+\s*---\n', p):
                                clean_p = re.sub(r'^\s*\d+\s*---\n', '', p)
                            self.pages.append(MockPage(clean_p))
                    else:
                        self.pages = [MockPage(text_content)]
                        
                def __len__(self): return len(self.pages)
                def __getitem__(self, idx): return self.pages[idx]
                def get_toc(self): return []
                def close(self): pass

            # Use the Mock Doc with standard pipeline
            # Note: We skip OCR since it's text
            mock_doc = MockDoc(content)
            
            # Cache the markdown directly since it's already MD
            for i, p in enumerate(mock_doc.pages):
                self.markdown_cache[i] = p.text

            # Run standard pipeline
            statement_map = self._scan_for_statements(mock_doc, {})
            self._extract_all_year_labels(mock_doc, statement_map, {})
            
            all_items = []
            for key, boundary in statement_map.items():
                entity_key = boundary.identifier.reporting_entity.value
                stmt_key = boundary.identifier.statement_type.value
                self._current_entity = boundary.identifier.reporting_entity
                
                parsed = self._parse_statement(mock_doc, boundary, {})
                
                if entity_key in ['standalone', 'consolidated']:
                    result[entity_key][stmt_key] = parsed.to_dict()
                
                for item in parsed.items:
                    all_items.append(item.to_dict())
            
            result["items"] = all_items
            result["text"] = content
            
        except Exception as e:
            logger.error(f"Markdown parsing failed: {e}")
            result["metadata"]["error"] = str(e)
            
        return result
    
    # =========================================================================
    # Keyword Management
    # =========================================================================
    
    def update_keywords(self, mappings: List[Dict[str, Any]]) -> int:
        """
        Update financial keywords from term mappings.
        
        Args:
            mappings: List of term mapping dictionaries
            
        Returns:
            Number of keywords added
        """
        return self.keywords.update_from_mappings(mappings)

# =============================================================================
# Helper Functions
# =============================================================================

def parse_file(file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Wrapper function to parse a file using FinancialParser.
    Creates a new parser instance for each call to ensure thread safety.
    """
    parser = FinancialParser()
    return parser.parse(file_path, file_type)

def parse_annual_report(file_path: str) -> Dict[str, Any]:
    """
    Legacy wrapper for parsing annual reports.
    """
    return parse_file(file_path, file_type='pdf')
