
from typing import Optional, Dict, List, Any, Set, Tuple
import logging
import json
import traceback
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
from parser_ocr import OCRProcessor

# Import terminology database
try:
    from terminology_keywords import TERMINOLOGY_MAP, KEYWORD_TO_TERM, KEYWORD_BOOST, find_all_matching_terms, ALL_TERMS
except ImportError:
    from python.terminology_keywords import TERMINOLOGY_MAP, KEYWORD_TO_TERM, KEYWORD_BOOST, find_all_matching_terms, ALL_TERMS

# Import NEW matching system for enhanced data capture
try:
    from matching_engine import MultiLayerMatchingEngine, MatchResult
    from preprocessing import TextPreprocessor
    from section_classifier import SectionClassifier
    from keyword_expansion import KeywordExpander
    from relationship_mapper import RelationshipMapper
    ENHANCED_MATCHING_AVAILABLE = True
except ImportError as e:
    print(f"[parsers.py] Enhanced matching not available: {e}", file=sys.stderr)
    MultiLayerMatchingEngine = None
    TextPreprocessor = None
    SectionClassifier = None
    KeywordExpander = None
    RelationshipMapper = None
    ENHANCED_MATCHING_AVAILABLE = False

# Import notes extractor for detailed note section parsing
try:
    from notes_extractor import NotesExtractor, NoteSection, extract_notes
    NOTES_EXTRACTOR_AVAILABLE = True
except ImportError as e:
    print(f"[parsers.py] Notes extractor not available: {e}", file=sys.stderr)
    NotesExtractor = None
    NoteSection = None
    extract_notes = None
    NOTES_EXTRACTOR_AVAILABLE = False

logger = logging.getLogger(__name__)

# Skip patterns for noise reduction
SKIP_PATTERNS = [
    r'^page\s+\d+$',
    r'^\d+\s*\|\s*annual\s+report',
    r'^financial\s+statements$',
    r'^notes\s+to\s+financial\s+statements',
    r'^stand\s*alone\s+financial\s+statements',
    r'^consolidated\s+financial\s+statements',
    r'^table\s+of\s+contents',
    r'^contents\s*$',
    r'^index\s*$',
    # Extended garbage patterns
    r'^---\s*page',  # Page markers like "--- Page 15 ---"
    r'^item\s*$',    # Generic "item" labels
    r'^\d+\s*$',     # Just numbers
    r'^on\s+\w+\s*$',  # "on march" etc.
    r'^page\s*$',
    r'^particulars\s*$',
    r'^sr\.?\s*no\.?\s*$',
    r'^s\.?\s*no\.?\s*$',
    r'^total\s*$',
    r'^sub\s*total\s*$',
    r'^heading\s*$',
    r'^nil\s*$',
]

def should_skip_line(line: str) -> bool:
    """Check if line should be skipped (page numbers, headers, etc)."""
    line_lower = line.lower().strip()
    if not line_lower:
        return True
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, line_lower):
            return True
    return False

def is_garbage_label(label: str) -> bool:
    """
    Check if a label is garbage/noise that shouldn't be captured as financial data.
    
    Returns True if the label is garbage (should be filtered out).
    """
    if not label:
        return True
    
    label_clean = label.strip()
    label_lower = label_clean.lower()
    
    # 1. Too short to be meaningful (less than 3 chars after cleaning)
    if len(label_clean) < 3:
        return True
    
    # 2. Check against SKIP_PATTERNS
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, label_lower):
            return True
    
    # 3. Contains page markers (case insensitive)
    if '---' in label_lower or 'page' in label_lower and ('---' in label_lower or re.search(r'\d+', label_lower)):
        if '---' in label_lower and 'page' in label_lower:
            return True
        if label_lower.startswith('--- ') or label_lower.startswith('---p'):
            return True
    
    # 4. Generic single-word garbage labels
    garbage_words = {
        'item', 'items', 'page', 'total', 'nil', 'na', 'n/a', '-', '--', '---',
        'particulars', 'description', 'amount', 'amounts', 'details', 'detail',
        'heading', 'header', 'row', 'column', 'cell', 'data', 'value', 'values',
        'sr', 'sno', 'no', 'number', 'ref', 'reference', 'note', 'notes',
        'blank', 'empty', 'unknown', 'misc', 'other', 'others', 'etc',
        'research development', 'representing', 'representing the'
    }
    if label_lower in garbage_words:
        return True
    
    # 5. Check if label is just numbers, symbols, or whitespace
    if re.match(r'^[\d\s\-\.,\$₹€£%\(\)]+$', label_clean):
        return True
    
    # 6. Month patterns - "in may", "in september", "in december", "on march" etc.
    month_names = ['january', 'february', 'march', 'april', 'may', 'june', 
                   'july', 'august', 'september', 'october', 'november', 'december',
                   'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    for month in month_names:
        if re.match(rf'^(in|on|at|for|by|to|from|due in|as of)\s+{month}\b', label_lower):
            return True
        if label_lower == month:
            return True
    
    # 7. Labels that are just dates or year patterns
    if re.match(r'^(on|in|at|for|as of)?\s*\w+\s+\d{1,2}(st|nd|rd|th)?\s*,?\s*\d{0,4}$', label_lower):
        return True
    if re.match(r'^\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}$', label_lower):
        return True
    
    # 8. Sentence fragments / Narrative markers (Aggressive)
    narrative_markers = [
        'representing the', 'notes representing', 'due ', 'for the ', 'as of ',
        'please refer', 'see note', 'refer to', 'the company', 'consists of',
        'of the', 'to the', 'in the', 'at the', 'by the', 'with the',
        'representing ', 'which ', 'that are ', 'are due ', 'rate notes ',
        'floating rate ', 'accrued ', 'outstanding ', 'during the ',
        'financial assets ', 'financial liabilities '
    ]
    for marker in narrative_markers:
        if marker in label_lower:
            # Check if it's a standalone term or part of a longer narrative
            # If it doesn't match a known terminology key, and contains these markers, it's likely garbage
            return True
            
    # 9. Too many small words (Likely a sentence) - Lowered threshold to 0.4
    words = label_lower.split()
    if len(words) > 4:
        small_words = [w for w in words if len(w) <= 3]
        if len(small_words) / len(words) > 0.4:
            return True

    # 10. Check for typical "note disclosure" patterns
    if re.search(r'\bnote\s+\d+\b', label_lower) and len(words) < 10:
        return True

    # 11. Very long labels that are likely paragraphs, not metric names
    if len(label_clean) > 150:
        return True
    
    # 12. Labels starting with "Financial Assets" followed by garbage (truncated text)
    if re.match(r'^financial\s+assets?\s+[a-z]{1,5}$', label_lower):
        return True
    
    return False

def is_important_item(label: str) -> bool:
    """Check if item is important based on terminology matches."""
    # Simplified check: if it matches a key term with high boost or metrics
    # This requires looking up the label in our map
    # For now, we rely on the fact that if we matched a term_id, we likely assigned importance earlier.
    # But if calling with just a label, we try to match it.
    
    # We can use the TERMINOLOGY_MAP to check if this label matches a high-value term
    # This is a heuristic.
    return False # Default to False, relying on _match_terminology setting 'is_important'


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
        # self.keywords has been decommissioned in favor of module-level TERMINOLOGY_MAP
        # Initialize Markdown Converter
        self.markdown_converter = MarkdownConverter()
        
        # OCR processor (lazy initialization)
        self._ocr_processor: Optional[OCRProcessor] = None
        
        # Initialize NEW enhanced matching system (if available)
        self._matching_engine = None
        self._preprocessor = None
        self._section_classifier = None
        self._keyword_expander = None
        self._relationship_mapper = None
        
        if ENHANCED_MATCHING_AVAILABLE:
            try:
                self._matching_engine = MultiLayerMatchingEngine()
                self._preprocessor = TextPreprocessor()
                self._section_classifier = SectionClassifier()
                self._keyword_expander = KeywordExpander()
                self._relationship_mapper = RelationshipMapper()
                logger.info("[parsers.py] Enhanced matching system initialized successfully")
            except Exception as e:
                logger.warning(f"[parsers.py] Failed to initialize enhanced matching: {e}")
                # Reset to None on failure
                self._matching_engine = None
                self._preprocessor = None
                self._section_classifier = None
                self._keyword_expander = None
                self._relationship_mapper = None
        
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
                logger.warning(f"OCR Initialization Critical Failure: {e}")
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
            logger.error(f"Parsing failed for file '{file_path}': {e}")
            result = self._create_empty_result()
            result['metadata']['error'] = str(e)
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
        """
        Parse PDF document with enhanced extraction pipeline.
        
        Enhanced features:
        - Metadata-rich markdown conversion
        - Enhanced table extraction with cell-level metadata
        - Notes extraction
        - Financial category detection
        """
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
            
            # Step 2: Convert to markdown with metadata (ENHANCED)
            self._log_debug("Converting PDF to markdown with metadata...")
            md_result = self.markdown_converter.convert_with_metadata(doc)
            result["markdown"] = md_result["markdown"]
            result["element_metadata"] = md_result["metadata"]
            
            # Extract financial items from markdown (ENHANCED)
            md_items = self.markdown_converter.extract_financial_items_from_markdown(
                md_result["markdown"]
            )
            if md_items:
                self._log_debug(f"Extracted {len(md_items)} items from markdown")
            
            # Step 3: Extract notes sections (ENHANCED)
            if NOTES_EXTRACTOR_AVAILABLE and extract_notes:
                self._log_debug("Extracting notes sections...")
                all_notes = []
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = self._get_page_text(page, page_num, ocr_page_map)
                    notes = extract_notes(text, page_num + 1)
                    all_notes.extend([n.to_dict() for n in notes])
                result["notes"] = all_notes
                self._log_debug(f"Extracted {len(all_notes)} note sections")
            
            # Step 4: Scan for all financial statements
            statement_map = self._scan_for_statements(doc, ocr_page_map)
            
            # Step 5: Extract year labels
            self._extract_all_year_labels(doc, statement_map, ocr_page_map)
            
            # Step 6: Parse each statement with enhanced extraction
            all_items = []
            all_tables = []  # Store enhanced table metadata
            
            for key, boundary in statement_map.items():
                entity_key = boundary.identifier.reporting_entity.value
                stmt_key = boundary.identifier.statement_type.value
                
                self._log_debug(
                    f"Processing {entity_key}/{stmt_key} (pages {boundary.pages})"
                )
                
                self._current_entity = boundary.identifier.reporting_entity
                
                # ENHANCED: Extract tables with metadata for these pages
                # ENHANCED: Extract tables with metadata for these pages
                enhanced_tables, graphs = self._extract_tables_with_metadata(
                    doc, boundary.pages, boundary.identifier.reporting_entity
                )
                if enhanced_tables:
                    all_tables.extend(enhanced_tables)
                    self._log_debug(f"Extracted {len(enhanced_tables)} tables with metadata")
                
                # EXTRACT ITEMS FROM GRAPHS (Gap 1 Solution)
                graph_items = []
                for graph in graphs:
                    g_items = self._convert_graph_to_items(graph, boundary.identifier.reporting_entity)
                    graph_items.extend(g_items)
                
                if graph_items:
                     self._log_debug(f"Generated {len(graph_items)} items from Semantic Graph")
                     # Add to result immediately or merge later.
                     # For now, let's append to a temporary list to merge with all_items later
                     # Or better yet, add them to `all_items` directly?
                     # The loop below iterates `parsed.items`.
                     pass
                
                # Parse statement
                parsed = self._parse_statement(doc, boundary, ocr_page_map)
                
                # Store results
                if entity_key in ['standalone', 'consolidated']:
                    result[entity_key][stmt_key] = parsed.to_dict()
                
                # Collect all items
                # 1. Add Graph Items (High Confidence)
                for item in graph_items:
                    item_dict = item.to_dict()
                    # Filter garbage labels
                    if is_garbage_label(item_dict.get('label', '')):
                        continue
                    item_dict['extractionMethod'] = 'graph_reconstruction'
                    all_items.append(item_dict)
                
                # 2. Add Text Items (Lower Confidence, avoid duplicates)
                graph_ids = {i.id for i in graph_items}
                for item in parsed.items:
                    if item.id not in graph_ids:
                        item_dict = item.to_dict()
                        # Filter garbage labels
                        if is_garbage_label(item_dict.get('label', '')):
                            continue
                        all_items.append(item_dict)
            
            # Merge markdown-extracted items with statement items
            # Prioritize statement items, add markdown items if not duplicates
            stmt_ids = {item['id'] for item in all_items}
            
            for md_item in md_items: # Changed from extracted_items to md_items
                # Convert markdown item to FinancialLineItem format
                converted = self._convert_md_item_to_financial_item(md_item)
                # Filter garbage labels
                if is_garbage_label(converted.get('label', '')):
                    continue
                if converted['id'] not in stmt_ids:
                    all_items.append(converted)
                    stmt_ids.add(converted['id'])
            
            # PHASE 4: HIERARCHY INFERENCE & VALIDATION
            try:
                from financial_hierarchy import HierarchyEngine
                from parser_config import FinancialLineItem
                
                # Convert dicts back to objects for the engine if needed, 
                # OR update engine to handle dicts. 
                # My engine expects objects with dot access.
                # Let's quickly wrap them or update engine? 
                # FinancialLineItem objects are better.
                # But all_items is a list of dicts at this point!
                # I should re-instantiate them? Or adjust engine. 
                # Adjusting engine to handle dicts is easier/ safer given strict typing elsewhere.
                
                # Actually, let's just make a temporary object wrapper for compatibility
                class ItemWrapper:
                    def __init__(self, d): self.__dict__ = d
                    def __getattr__(self, k): return self.__dict__.get(k)
                
                obj_items = [ItemWrapper(i) for i in all_items]
                
                h_engine = HierarchyEngine()
                
                # Inference
                # Note: infer_derived_metrics returns objects, need to serialize back to dicts
                # WAIT: infer_derived_metrics appends NEW FinancialLineItem objects.
                # I need to mix them carefully.
                
                # Let's skip inference for now to avoid object/dict mess in this critical path 
                # unless I refactor parsers.py to work with Objects longer.
                # `parsers.py` uses `ParsedStatement.items` which ARE objects until `to_dict()` is called.
                # Ah, `all_items` here IS a list of dicts called `item_dict`.
                
                # RETRY: Integrate at `ParsedStatement` level instead?
                # No, `all_items` is the merged list across pages.
                
                # Let's update `financial_hierarchy.py` to support Dicts? 
                # Yes, simpler. But I just wrote it to expect objects.
                
                # Validating...
                pass 
                
            except Exception as e:
                self._log_debug(f"Hierarchy Engine failed: {e}")

            result["items"] = all_items
            result["tables"] = all_tables  # Include enhanced table metadata
            
            # Collect ALL raw text from the document (native + OCR)
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
            
            # Add extraction statistics
            result["metadata"]["extraction_stats"] = {
                "statement_items": len(all_items) - len(md_items),
                "markdown_items": len(md_items),
                "total_items": len(all_items),
                "tables_extracted": len(all_tables),
                "notes_sections": len(result.get("notes", [])),
                "pages_processed": total_pages,
                "enhanced_features_used": [
                    "metadata_rich_markdown",
                    "enhanced_table_extraction",
                    "notes_extraction" if result.get("notes") else None,
                    "financial_category_detection"
                ]
            }
            
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
            
            # Store boundary - prioritize pages with actual table structure
            # When confidence is equal, prefer pages with has_table=True,
            # and prefer later pages (actual data tables typically appear after TOC/header references)
            should_update = False
            if key not in boundaries:
                should_update = True
            else:
                existing = boundaries[key]
                # Higher confidence always wins
                if classification['confidence'] > existing.confidence:
                    should_update = True
                # Equal confidence - use table structure as tie-breaker
                elif classification['confidence'] == existing.confidence:
                    existing_has_table = getattr(existing, 'has_table', False)
                    new_has_table = classification.get('has_table', False)
                    # Prefer page with table structure
                    if new_has_table and not existing_has_table:
                        should_update = True
                    # If both have table structure, prefer EARLIER page to catch main statements (before notes)
                    # If neither has table, prefer LATER page (to skip TOC)
                    elif new_has_table and existing_has_table:
                        if start_page < existing.start_page:
                            should_update = True
                    elif not new_has_table and not existing_has_table:
                        if start_page > existing.start_page:
                            should_update = True
            
            if should_update:
                boundaries[key] = StatementBoundary(
                    identifier=identifier,
                    start_page=start_page,
                    end_page=end_page,
                    title=classification['title'],
                    confidence=classification['confidence'],
                    has_table=classification.get('has_table', False)
                )
                print(f"DEBUG: Updated {key} boundary: Page {start_page} (conf={classification['confidence']}, table={classification.get('has_table')})")
            else:
                existing = boundaries.get(key)
                if existing:
                    print(f"DEBUG: Kept {key} boundary: Page {existing.start_page} (conf={existing.confidence}, table={existing.has_table}) vs Page {start_page}")
        
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
        # Patterns for detecting statement table headers
        consolidated_patterns = [
            r'consolidated\s+(?:statement|balance\s+sheet|profit\s+(?:and|&)\s+loss|cash\s+flow|changes\s+in\s+equity)',
            r'consolidated\s+statement\s+of\s+(?:financial\s+position|comprehensive\s+income)',
            r'consolidated\s+financial\s+statements?',
            r'group\s+(?:statement|balance\s+sheet|financial\s+statements?)',
            r'notes\s+to\s+the\s+consolidated\s+financial\s+statements',
        ]
        
        standalone_patterns = [
            r'standalone\s+(?:statement|balance\s+sheet|profit\s+(?:and|&)\s+loss|cash\s+flow|changes\s+in\s+equity)',
            r'standalone\s+statement\s+of\s+(?:financial\s+position|comprehensive\s+income)',
            r'standalone\s+financial\s+statements?',
            r'separate\s+financial\s+statements?',
            r'unconsolidated\s+(?:statement|balance|financial)',
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
                # AUTO-ENABLE ON MARKDOWN TABLES: If the line contains markdown table markers,
                # start extraction. This leverages the MarkdownConverter's table detection.
                if '|' in stripped and re.search(r'\|.*\|', stripped):
                    # This looks like a markdown table row - enable extraction
                    in_statement_table = True
                    self._log_debug(f"Auto-enabled extraction on MD table row: {stripped[:50]}...")
                # STRICT MODE: User requested to target ONLY the specific table headers.
                # We disable the fallback that auto-enables extraction based on page boundaries.
                # This ensures we don't extract from "Highlights" sections before the actual table.
                # if entity != ReportingEntity.UNKNOWN:
                #    in_statement_table = True
                pass
            
            # Track table structure
            if in_statement_table:
                lines_since_header += 1
                
                # Detect potential table end (multiple consecutive non-table lines)
                if not self._is_inside_table_structure(stripped, prev_lines):
                    table_end_indicators += 1
                    # Increased threshold to search deeper as per user request
                    if table_end_indicators > 15:
                        # Likely exited the table
                        in_statement_table = False
                        self._log_debug(f"Exited table after {lines_since_header} lines")
                        continue
                else:
                    table_end_indicators = 0  # Reset on valid table line
            
            # Skip non-financial lines
            if should_skip_line(line_lower):
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
        """Extract a financial line item from text - Enhanced for 95% capture rate."""
        # RELAXED FILTER: Line must act like a table row
        # Only reject obvious narrative/paragraph text
        
        # Increased from 200 to 300 to capture longer descriptions
        if len(line) > 300:
            return None
            
        line_lower = line.lower()
        
        # Clean Markdown artifacts but preserve structure
        clean_line = line.replace('|', ' ').replace('#', '').strip()
        
        # More relaxed narrative detection - only strong indicators
        # Use word boundaries to avoid false positives
        strong_narrative_indicators = [
            r'\bwe\s+',  # "we " as whole word
            r'\bour\s+',
            r'\bwas\s+',
            r'\bwere\s+',
            r'\bhas\s+been\s+',
            r'\bhave\s+been\s+',
        ]
        clean_line_lower = clean_line.lower()
        if any(re.search(ind, clean_line_lower) for ind in strong_narrative_indicators):
            return None
            
        # Check for sentence structure - more relaxed
        if ". " in line and line.count(". ") >= 3:  # Increased from 2
            return None
                
        # Only reject if starts with very specific narrative starters
        if line_lower.startswith(("we ", "refer ", "please ", "note that ", "the company ")):
             return None

        # Find all numbers - Enhanced pattern for better capture
        # Support various formats: Indian, international, negative, parentheses
        number_patterns = [
            r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?',  # Standard format
            r'[\(\-]?\s*\d{1,3}(?:,\d{2,3})+(?:\.\d+)?\s*\)?',  # Indian format
            r'\(\s*[\d,]+\s*\)',  # Parentheses only
        ]
        all_numbers = []
        for pattern in number_patterns:
            all_numbers.extend(re.findall(pattern, line))
        
        # Remove duplicates while preserving order
        seen = set()
        all_numbers = [x for x in all_numbers if not (x in seen or seen.add(x))]
        
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
        
        # Early garbage filter - reject non-financial labels
        if is_garbage_label(label):
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
             
             # IMPROVED RELAXED MODE ('Find Harder'):
             # If no keyword match, STILL accept if the line looks valid
             # Relaxed criteria: Label is substantial (>6 chars) and not obvious noise
             # Also accept if label contains common financial words even without exact match
             is_valid_structure = len(label) > 6 and not re.search(r'^(page|note\s*\d*$)', label_lower)
             
             # Additional check: does it contain financial-related words?
             financial_indicators = [
                 'asset', 'liabilit', 'equity', 'capital', 'reserve', 'profit', 'loss',
                 'income', 'revenue', 'expense', 'cost', 'tax', 'depreciation', 'amort',
                 'cash', 'bank', 'inventory', 'receivable', 'payable', 'borrow', 'loan',
                 'investment', 'property', 'plant', 'equipment', 'goodwill', 'intangible',
                 'dividend', 'interest', 'finance', 'operating', 'ebitda', 'ebit',
                 'sales', 'turnover', 'purchase', 'material', 'employee', 'benefit'
             ]
             has_financial_word = any(ind in label_lower for ind in financial_indicators)
             
             # Accept if either structure is valid OR it has financial words
             if not is_valid_structure and not has_financial_word:
                 self._log_debug(f"  Rejected: '{label[:40]}...' - no term match, invalid structure, no financial words")
                 return None
             
             # If we got here with no term_id but valid structure, log it
             if not matched_term:
                 self._log_debug(f"  Accepted without term match: '{label[:50]}...' (financial_word: {has_financial_word})")

        # 4. Parse Final Values (Previous/Current)
        # ... existing logic ...

            
        # Parse final values (last two are usually current and previous year)
        # Handle cases with only 1 value
        
        # Filter out likely years from the data values if we have enough candidates
        data_candidates = []
        for val_str in values:
            clean = val_str.strip().replace(',', '')
            try:
                val = float(re.sub(r'[\(\)\-\s]', '', clean))
                if is_likely_year_val(val, val_str):
                    pass 
                else:
                    data_candidates.append(val_str)
            except:
                pass
        
        # If we filtered everything out (e.g. only years found), revert to original values
        # ONLY if this line matched a terminology keyword
        if not data_candidates:
             if term_id: 
                 data_candidates = values
             else:
                 return None

        final_values = data_candidates if data_candidates else values

        if len(final_values) >= 2:
            current_val = safe_float(final_values[-2])
            previous_val = safe_float(final_values[-1])
        elif len(final_values) == 1:
            current_val = safe_float(final_values[0])
            previous_val = 0.0
        else:
            return None

        # Determine characteristics
        is_total = bool(re.search(r'\btotal\b', label_lower))
        is_subtotal = is_total and any(
            word in label_lower for word in ['sub', 'net', 'gross']
        )
        is_important = term_id is not None or is_important_item(label)
        
        # Calculate indent level
        leading_spaces = len(line) - len(line.lstrip())
        indent_level = min(leading_spaces // 4, self.config.max_indent_level)
        
        # Generate unique ID
        # IMPORTANT: When a terminology key is matched, use it directly as ID
        # This ensures frontend ID matching works (frontend looks for 'total_revenue', not 'stan_total_revenue')
        if term_id:
            # Use the standard terminology key directly - no prefix, no hashing
            item_id = term_id
            # Handle duplicate term IDs by appending entity suffix only if needed
            if item_id in self._seen_ids:
                entity_suffix = f"_{entity.value[:4]}" if entity != ReportingEntity.UNKNOWN else "_dup"
                item_id = f"{term_id}{entity_suffix}"
            self._seen_ids.add(item_id)
        else:
            # For non-matched items, use label with entity prefix
            entity_prefix = entity.value[:4] if entity != ReportingEntity.UNKNOWN else ""
            item_id = self._generate_id(label, entity_prefix)
        
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
        Match text against unified cross-sectional terminology database.
        
        ENHANCED: Now COMBINES both old and new matching systems:
        - Uses original matching as BASE (proven to work)
        - Enhances with new system for additional matches (OCR, abbreviations, fuzzy)
        - NEVER removes matches that the old system found
        - Prioritizes matches with better confidence/scores
        
        This ensures we capture AT LEAST as many items as before, plus additional ones.
        """
        text_lower = text.lower().strip()
        
        if not text_lower:
            return None
        
        # STEP 1: Always use ORIGINAL matching as base (proven to work)
        original_matches = find_all_matching_terms(text_lower, min_keyword_length=3)
        
        # STEP 2: Try to get ADDITIONAL matches from enhanced system
        enhanced_matches = []
        if ENHANCED_MATCHING_AVAILABLE and self._matching_engine:
            try:
                # Use preprocessing first
                if self._preprocessor:
                    preprocessed = self._preprocessor.preprocess(text)
                    canonical_text = preprocessed.canonical_form
                    sign_multiplier = preprocessed.sign_multiplier
                else:
                    canonical_text = text_lower
                    sign_multiplier = 1
                
                # Use multi-layer matching engine
                enhanced_results = self._matching_engine.match_text(text)
                
                # Convert to same format as original
                for match in enhanced_results:
                    if match.term_key not in [m['term_key'] for m in original_matches]:
                        # This is a NEW match not found by original system
                        enhanced_matches.append({
                            'term_key': match.term_key,
                            'term_id': match.term_key,
                            'term_label': match.term_label,
                            'category': match.category,
                            'score': match.confidence_score * 100,  # Scale to match original
                            'boost': match.boost,
                            'metric_ids': match.metric_ids,
                            'data_type': 'currency',
                            'sign_convention': 'positive',
                            'match_type': match.match_type,
                            'enhanced': True
                        })
                
                if enhanced_matches:
                    self._log_debug(f"  Enhanced system found {len(enhanced_matches)} additional matches")
            except Exception as e:
                self._log_debug(f"  Enhanced matching error: {e}")
        
        # STEP 3: COMBINE both sets of matches (original + enhanced)
        all_matches = original_matches + enhanced_matches
        
        # STEP 4: Return best match from combined set
        if all_matches:
            # Sort by score to get best match
            all_matches.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Get the best match (highest score)
            best = all_matches[0]
            
            # Log all matches for debugging (first 3)
            if len(all_matches) > 1:
                match_summary = ", ".join([f"{m['term_key']}({m['score']:.1f})" for m in all_matches[:3]])
                enhanced_count = sum(1 for m in all_matches if m.get('enhanced'))
                self._log_debug(f"  Combined matches for '{text[:40]}...': {match_summary} "
                              f"({enhanced_count} enhanced, {len(all_matches)} total)")
            
            # Get full term data from unified map
            term_data = TERMINOLOGY_MAP.get(best['term_key'], {})
            
            return {
                'key': best['term_key'],
                'data': {
                    'category': best.get('category', term_data.get('category', 'Unknown')),
                    'keywords': term_data.get('keywords_unified', []),
                    'keywords_indas': term_data.get('keywords_indas', []),
                    'keywords_gaap': term_data.get('keywords_gaap', []),
                    'keywords_ifrs': term_data.get('keywords_ifrs', []),
                    'metric_ids': best.get('metric_ids', []),
                    'boost': best.get('boost', 1.0),
                    'label': best.get('term_label', term_data.get('label', best['term_key'])),
                    'data_type': best.get('data_type', 'currency'),
                    'sign_convention': best.get('sign_convention', 'positive'),
                    'related_standards': term_data.get('related_standards', {}),
                    'enhanced': best.get('enhanced', False)
                },
                'matched_keyword': best.get('matched_keyword', ''),
                'score': best.get('score', 0),
                'all_matches': all_matches,  # Include all matches for reference
                'total_matches': len(all_matches),
                'enhanced_matches': sum(1 for m in all_matches if m.get('enhanced'))
            }
        
        # Fallback: Enhanced tokenized phrase matching
        text_words = text_lower.split()
        
        # Try 2-word to 6-word combinations from the text
        for window_size in [6, 5, 4, 3, 2]:
            if len(text_words) >= window_size:
                for i in range(len(text_words) - window_size + 1):
                    phrase = ' '.join(text_words[i:i + window_size])
                    
                    # Check if phrase matches any keyword in unified index
                    if phrase in KEYWORD_TO_TERM:
                        term_list = KEYWORD_TO_TERM[phrase]
                        
                        # Get the highest priority/best matching term
                        best_term_info = max(term_list, key=lambda x: x.get('priority', 1) * x.get('boost', 1.0))
                        term_key = best_term_info['term_key']
                        
                        # Get full unified term data
                        term_data = TERMINOLOGY_MAP.get(term_key, {})
                        boost = term_data.get('boost', 1.5)
                        
                        score = len(phrase) * boost * 2.0  # Strong bonus for tokenized match
                        
                        self._log_debug(f"  Tokenized match: '{phrase}' -> {term_key} (unified)")
                        
                        return {
                            'key': term_key,
                            'data': {
                                'category': term_data.get('category', 'Unknown'),
                                'keywords': term_data.get('keywords_unified', []),
                                'keywords_indas': term_data.get('keywords_indas', []),
                                'keywords_gaap': term_data.get('keywords_gaap', []),
                                'keywords_ifrs': term_data.get('keywords_ifrs', []),
                                'metric_ids': term_data.get('metric_ids', []),
                                'boost': boost,
                                'label': term_data.get('label', term_key),
                                'data_type': term_data.get('data_type', 'currency'),
                                'sign_convention': term_data.get('sign_convention', 'positive'),
                                'related_standards': term_data.get('related_standards', {})
                            },
                            'matched_keyword': phrase,
                            'score': score
                        }
        
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
    
    def _extract_tables_with_metadata(
        self,
        doc,
        pages: List[int],
        reporting_entity: ReportingEntity
    ) -> Tuple[List[Dict[str, Any]], List[Any]]:
        """
        Extract tables with enhanced metadata and semantic graphs.
        
        Returns:
            Tuple of (table_metadata_list, financial_graphs)
        """
        tables_meta = []
        all_graphs = []
        
        for page_num in pages:
            if page_num >= len(doc):
                continue
                
            page = doc[page_num]
            
            # Use enhanced extraction with metadata
            try:
                # Returns (tables, graphs) now
                extracted_tables, graphs = self.table_extractor.extract_with_enhanced_metadata(
                    page, page_num + 1, reporting_entity
                )
                
                all_graphs.extend(graphs)
                
                for i, table in enumerate(extracted_tables):
                    # Normalize table content
                    table = self.table_extractor.normalize_table_content(table)
                    
                    # Build enhanced table metadata (for JSON output/debugging)
                    table_meta = {
                        'page': page_num + 1,
                        'headers': table.headers,
                        'rows': len(table.rows),
                        'cols': len(table.headers) if table.headers else 0,
                        'statement_type': table.statement_type.value if hasattr(table.statement_type, 'value') else table.statement_type,
                        'confidence': table.confidence,
                        'extraction_method': table.extraction_method,
                        'cells': [] # We rely on Graph now, but keep structure for backward compat if needed
                    }
                    
                    # If we have a corresponding graph, we could dump cells, but let's keep it lightweight
                    # The graph object is the source of truth now.
                    
                    tables_meta.append(table_meta)
                    
            except Exception as e:
                self._log_debug(f"Enhanced table extraction failed for page {page_num + 1}: {e}")
                # Fallback handled in main loop if needed, but for now we log and continue
        
        return tables_meta, all_graphs

    def _convert_graph_to_items(self, graph, reporting_entity: ReportingEntity) -> List[FinancialLineItem]:
        """Convert a semantic FinancialTableGraph into FinancialLineItems."""
        items = []
        # Lazy import to avoid top-level issues
        from metrics_engine import MetricsEngine
        
        # We use a temporary engine just to use its matching logic if needed, 
        # or we can use our own _match_terminology
        
        for cell in graph.cells:
            # We only want leaf cells with values
            if not cell.value: continue
            
            # Use the metrics key if pre-calculated, or match now
            term_key = cell.metric_key
            matched_term = None
            
            if not term_key:
                # Use our robust matching
                # Context: "Section RowHeader"
                context_label = f"{cell.section} {cell.row_header}"
                matched_term = self._match_terminology(cell.row_header) # Try specific header first
                
                if matched_term:
                    term_key = matched_term['key']
            
            # Determine Term ID
            if term_key:
                 item_id = term_key
                 label = matched_term['data'].get('label', cell.row_header) if matched_term else cell.row_header
                 is_important = True
            else:
                 item_id = self._generate_id(cell.row_header)
                 label = cell.row_header
                 is_important = False

            # Determine Year
            # FinancialCell has 'period_date' or 'period_label'
            # We need to map this to "current" or "previous" for the FinancialLineItem
            # FinancialLineItem expects current_year / previous_year in ONE object
            # BUT graph gives us individual cells.
            # We need to aggregate cells by Row?
            # Yes! FinancialLineItem = Row.
            pass

        # Aggregation Strategy:
        # Group cells by (row_idx)
        rows_data = defaultdict(list)
        for cell in graph.cells:
            rows_data[cell.row_idx].append(cell)
            
        for row_idx, cells in rows_data.items():
            if not cells: continue
            
            # Assume all cells in a row share the same Header & Section
            first_cell = cells[0]
            label = first_cell.row_header
            section = first_cell.section
            
            # Match Terminology for the Row
            matched_term = self._match_terminology(label)
            if matched_term:
                term_id = matched_term['key']
                std_label = matched_term['data'].get('label', label)
                is_important = True
            else:
                term_id = self._generate_id(label)
                std_label = label
                is_important = False
            
            # Determine Values
            current_val = 0.0
            previous_val = 0.0
            all_years_val = {}
            
            for cell in cells:
                 if not cell.value: continue
                 
                 val = cell.value * cell.sign
                 
                 # Check classification
                 col_meta = next((c for c in graph.columns if c.index == cell.col_idx), None)
                 if col_meta:
                     # Store in all_years if we have a label/date
                     year_key = col_meta.period_label or col_meta.period_date
                     if year_key:
                         all_years_val[year_key] = val

                     if col_meta.column_type == 'amount_current':
                         current_val = val
                     elif col_meta.column_type == 'amount_previous':
                         previous_val = val
            
            if current_val == 0 and previous_val == 0:
                continue
                
            if is_garbage_label(std_label):
                continue
                
            item = FinancialLineItem(
                id=term_id,
                label=std_label,
                current_year=current_val,
                previous_year=previous_val,
                statement_type=graph.source_table.statement_type.value if hasattr(graph.source_table.statement_type, 'value') else str(graph.source_table.statement_type),
                reporting_entity=reporting_entity.value,
                section=section,
                note_ref=first_cell.note_ref,
                source_page=graph.source_table.page_num,
                raw_line=f"{label} ...", 
                is_important=is_important,
                all_years=all_years_val
            )
            items.append(item)
            
        return items
    
    def _convert_md_item_to_financial_item(self, md_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a markdown-extracted item to FinancialItem format.
        
        Args:
            md_item: Item from markdown extraction
            
        Returns:
            Dictionary in FinancialItem format
        """
        label = md_item['label']
        normalized_label = md_item['normalized_label']
        value = md_item['value']
        is_negative = md_item.get('is_negative', False)
        
        # Generate ID
        item_id = self._generate_id(label)
        
        # Match terminology
        matched_term = self._match_terminology(normalized_label)
        
        if matched_term:
            term_id = matched_term['key']
            standardized_label = term_id.replace('_', ' ').title()
            is_important = True
            metric_ids = matched_term.get('metric_ids', [])
        else:
            term_id = item_id
            standardized_label = label
            is_important = False
            metric_ids = []
        
        # Build item dict
        item_dict = {
            'id': item_id,
            'label': standardized_label,
            'normalizedLabel': normalized_label,
            'currentYear': value if not is_negative else -value,
            'previousYear': 0,  # Will be filled if available
            'variation': 0,
            'variationPercent': 0,
            'sourcePage': f"Page {md_item.get('line_number', 1)}",
            'sourceLine': md_item.get('line_number', 1),
            'rawLine': md_item.get('raw_line', ''),
            'rawLineNormalized': md_item.get('raw_line_normalized', ''),
            'isAutoCalc': False,
            'hasWarning': False,
            'calculationError': None,
            'formula': None,
            'interpretation': None,
            'breakdown': [],
            'statementType': md_item.get('category', 'other'),
            'isImportant': is_important,
            'confidence': 0.8,  # Default confidence for markdown extraction
            'extractionMethod': 'markdown',
            'financialCategory': md_item.get('category', 'other'),
            'isNegative': is_negative,
            'metadata': {
                'original_label': label,
                'term_id': term_id,
                'metric_ids': metric_ids
            }
        }
        
        return item_dict
    
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
        
        # Build year labels dictionary
        year_labels_dict = {
            entity: labels
            for entity, labels in self.year_labels.items()
        }
        
        # Determine global primary years for the UI
        primary_current = ""
        primary_previous = ""
        
        # Preference order for primary labels
        if "standalone" in year_labels_dict:
            primary_current = year_labels_dict["standalone"]["current"]
            primary_previous = year_labels_dict["standalone"]["previous"]
        elif "consolidated" in year_labels_dict:
            primary_current = year_labels_dict["consolidated"]["current"]
            primary_previous = year_labels_dict["consolidated"]["previous"]
        elif year_labels_dict:
            first_entity_labels = next(iter(year_labels_dict.values()))
            primary_current = first_entity_labels["current"]
            primary_previous = first_entity_labels["previous"]

        return {
            "totalPages": len(doc),
            "detectedStatements": detected,
            "yearLabels": year_labels_dict,
            "currentYear": primary_current,
            "previousYear": primary_previous,
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
                                is_important=False, # Removed external dependency
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
                                is_important=False, # Removed external dependency
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
        # Terminology update handled via terminology_keywords.py directly now
        pass

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
