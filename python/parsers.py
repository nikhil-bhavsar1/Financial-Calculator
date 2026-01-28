
from typing import Optional, Dict, List, Any, Set, Tuple
import logging
import json
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
            
            # Build metadata
            result["metadata"].update(
                self._build_metadata(doc, statement_map, ocr_page_map)
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
        """Get text from page, using OCR result if available."""
        if page_num in ocr_map:
            ocr_result = ocr_map[page_num]
            if ocr_result.is_successful:
                return ocr_result.text
        
        try:
            return page.get_text("text")
        except Exception as e:
            logger.debug(f"Failed to get page text: {e}")
            return ""
    
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
    
    def _parse_statement_text(
        self,
        text: str,
        stmt_type: StatementType,
        entity: ReportingEntity,
        pages: List[int]
    ) -> Tuple[List[FinancialLineItem], Dict[str, List[str]]]:
        """Parse statement text into line items."""
        items = []
        sections: Dict[str, List[str]] = defaultdict(list)
        
        # Get section markers for this statement type
        section_markers = FinancialPatternMatcher.SECTION_MARKERS.get(stmt_type, {})
        current_section = list(section_markers.keys())[0] if section_markers else "GENERAL"
        current_page = pages[0] + 1 if pages else 1
        
        lines = text.split('\n')
        
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
            
            # Skip non-financial lines
            if self.keywords.should_skip_line(line_lower):
                continue
            
            # Detect section changes
            for section_name, patterns in section_markers.items():
                for pattern in patterns:
                    if re.search(pattern, line_lower, re.IGNORECASE):
                        current_section = section_name
                        break
            
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
        # Find all numbers in line
        number_pattern = r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?'
        all_numbers = re.findall(number_pattern, line)
        
        if len(all_numbers) < self.config.min_numbers_per_row:
            return None
        
        # Separate note references from values
        values = []
        note_ref = ""
        
        for num_str in all_numbers:
            clean = num_str.strip()
            clean = re.sub(r'[\(\)\-\s]', '', clean).replace(',', '')
            
            if not clean:
                continue
            
            try:
                val = float(clean)
                # Small integers without decimals are likely note references
                if val < 100 and '.' not in num_str and val == int(val) and not note_ref:
                    note_ref = str(int(val))
                else:
                    values.append(num_str)
            except ValueError:
                continue
        
        if len(values) < 2:
            return None
        
        # Extract label
        label = self._extract_label(line, all_numbers)
        
        if not label or len(label) < self.config.min_label_length:
            return None
        
        if len(label) > self.config.max_label_length:
            label = label[:self.config.max_label_length]
        
        label_lower = label.lower()
        
        # Skip header-like text
        header_words = ['particulars', 'note no', 'as at', 'year ended',
                       'schedule', 'ref', 'sr. no', 'amount', 'notes']
        if any(hw in label_lower for hw in header_words):
            return None
        
        # Must match financial keywords
        if not self.keywords.matches_keyword(label_lower):
            return None
        
        try:
            # Parse values (last two are usually current and previous year)
            current_val = safe_float(values[-2])
            previous_val = safe_float(values[-1])
            
            # Determine characteristics
            is_total = bool(re.search(r'\btotal\b', label_lower))
            is_subtotal = is_total and any(
                word in label_lower for word in ['sub', 'net', 'gross']
            )
            is_important = self.keywords.is_important_item(label)
            
            # Calculate indent level
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = min(leading_spaces // 4, self.config.max_indent_level)
            
            # Generate unique ID
            entity_prefix = entity.value[:4] if entity != ReportingEntity.UNKNOWN else ""
            item_id = self._generate_id(label, entity_prefix)
            
            return FinancialLineItem(
                id=item_id,
                label=label,
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
            
        except Exception as e:
            self._log_debug(f"Parse error: {line[:50]}... - {e}")
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
