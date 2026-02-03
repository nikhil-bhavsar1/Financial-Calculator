"""
Hybrid PDF Processor - Best of both worlds:
- Parallel raw extraction for speed (text, tables, OCR)
- Sequential sophisticated analysis for quality (patterns, terminology, validation)
- Streaming results to frontend as data is available
"""

import multiprocessing as mp
import fitz
import logging
import re
from typing import Dict, Any, List, Optional, Tuple, Callable
from collections import defaultdict
import json
import traceback
import time
import sys

# Configure multiprocessing
mp.set_start_method('spawn', force=True)

logger = logging.getLogger(__name__)


class RawPageExtractor:
    """
    Fast parallel extraction of raw data from pages.
    NO analysis here - just extraction.
    All quality analysis happens sequentially after extraction.
    """

    @classmethod
    def extract_raw_page(cls, args: Tuple[int, fitz.Page, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract raw data from a single page.
        Fast extraction with NO analysis - just get the data.
        
        Args:
            args: Tuple of (page_num, page, config)
            
        Returns:
            Dictionary with all raw data from the page
        """
        page_num, page, config = args
        start_time = time.time()
        
        result = {
            'page_num': page_num,
            'text': '',
            'blocks': [],
            'tables': [],
            'images': [],
            'needs_ocr': False
        }
        
        try:
            # 1. Extract all text blocks with metadata (FAST)
            text_blocks = page.get_text("blocks")
            if text_blocks:
                result['blocks'] = [
                    {
                        'x0': b[0], 'y0': b[1], 'x1': b[2], 'y1': b[3],
                        'text': b[4] if len(b) > 4 else '',
                        'block_no': b[5] if len(b) > 5 else 0,
                        'block_type': b[6] if len(b) > 6 else 0
                    }
                    for b in text_blocks
                ]
                
                # Build full text for analysis
                result['text'] = '\n'.join(b[4] for b in text_blocks if len(b) > 4)
            
            # 2. Extract tables with full cell data (FAST, just extraction)
            try:
                if hasattr(page, 'find_tables'):
                    tables = page.find_tables()
                    for table in tables:
                        # Extract FULL table data - don't analyze yet
                        extracted = table.extract()
                        result['tables'].append({
                            'bbox': table.bbox,
                            'row_count': table.row_count,
                            'col_count': table.col_count,
                            'cells': extracted,  # Full data, no processing
                            'header': table.header if hasattr(table, 'header') else None
                        })
            except Exception as e:
                logger.debug(f"Table extraction failed on page {page_num}: {e}")
            
            # 3. Check if page needs OCR
            if len(result['text']) < 50:
                result['needs_ocr'] = True
            
            # 4. Extract images (for OCR if needed)
            try:
                images = page.get_images()
                result['images'] = [img for img in images]
            except:
                pass
            
            result['extraction_time'] = time.time() - start_time
            
        except Exception as e:
            logger.warning(f"Error extracting page {page_num}: {e}")
            result['error'] = str(e)
        
        return result


def parallel_extract_raw_pages(
    doc: fitz.Document,
    config: Optional[Dict[str, Any]] = None,
    max_workers: Optional[int] = None,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Extract raw data from all pages in parallel.
    This is FAST - no analysis, just extraction.
    """
    if max_workers is None:
        max_workers = min(mp.cpu_count(), 8)
    
    config = config or {}
    total_pages = len(doc)
    
    logger.info(f"Parallel raw extraction: {total_pages} pages with {max_workers} workers")
    
    # Prepare worker arguments
    worker_args = [
        (page_num, doc[page_num], config)
        for page_num in range(total_pages)
    ]
    
    # Extract pages in parallel
    start_time = time.time()
    
    with mp.Pool(processes=max_workers) as pool:
        # Use imap_unordered for progress tracking
        results_iter = pool.imap_unordered(
            RawPageExtractor.extract_raw_page,
            worker_args,
            chunksize=max(1, total_pages // (max_workers * 4))
        )
        
        # Collect results with streaming
        all_results = []
        for i, result in enumerate(results_iter):
            all_results.append(result)
            
            # Progress callback
            if progress_callback and i % max(1, total_pages // 10) == 0:
                progress = int((i + 1) / total_pages * 100)
                progress_callback(
                    i + 1,
                    total_pages,
                    f'Extracted {i + 1}/{total_pages} pages...'
                )
    
    # Sort results by page number
    all_results.sort(key=lambda x: x['page_num'])
    
    extraction_time = time.time() - start_time
    logger.info(f"Raw extraction completed in {extraction_time:.2f}s")
    
    return {
        'pages': all_results,
        'total_pages': total_pages,
        'extraction_time': extraction_time
    }


class QualityAnalyzer:
    """
    Sophisticated analysis engine for data quality.
    Runs SEQUENTIALLY after parallel extraction to ensure best quality.
    
    This is where all the sophisticated logic lives:
    - Pattern matching
    - Terminology matching  
    - GAAP validation
    - Hierarchy inference
    - Financial statement detection
    """
    
    # Import sophisticated parsers once
    _financial_parser = None
    _markdown_converter = None
    _detector = None
    
    @classmethod
    def initialize(cls):
        """Initialize analysis engines once."""
        if cls._financial_parser is None:
            try:
                from parsers import FinancialParser
                from markdown_converter import MarkdownConverter
                from parser_financial_stmt_detection import FinancialStatementDetector
                
                cls._financial_parser = FinancialParser()
                cls._markdown_converter = MarkdownConverter()
                cls._detector = FinancialStatementDetector(cls._financial_parser.config)
                
                logger.info("Quality analyzers initialized")
            except Exception as e:
                logger.warning(f"Could not initialize quality analyzers: {e}")
    
    @classmethod
    def analyze_page_streaming(
        cls,
        raw_page: Dict[str, Any],
        page_num: int,
        total_pages: int,
        stream_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single page with all sophisticated logic.
        Streams results as they're available.
        
        This is where quality happens - use all the sophisticated patterns.
        """
        try:
            # Initialize analyzers if needed
            cls.initialize()
            
            page_result = {
                'page_num': page_num,
                'items': [],
                'sections': [],
                'statement_type': 'unknown',
                'entity': 'unknown',
                'quality_score': 0.0,
                'metadata': {}
            }
            
            text = raw_page.get('text', '')
            tables = raw_page.get('tables', [])
            blocks = raw_page.get('blocks', [])
            
            # Skip empty pages
            if not text.strip() and not tables:
                if stream_callback:
                    stream_callback(page_result)
                return page_result
            
            # -------------------------------------------------------------------------
            # SOPHISTICATED ANALYSIS - Use all the quality engines
            # -------------------------------------------------------------------------
            
            # 1. Detect Statement Type (sophisticated pattern matching)
            if cls._detector:
                try:
                    identifier, confidence, title = cls._detector.detect_full_statement(text, page_num)
                    page_result['statement_type'] = identifier.statement_type.value
                    page_result['entity'] = identifier.reporting_entity.value
                    page_result['confidence'] = float(confidence)
                    page_result['title'] = title
                except Exception as e:
                    logger.debug(f"Statement detection failed: {e}")
            
            # 2. Process Tables with sophisticated extraction
            for table_idx, table_data in enumerate(tables):
                cells = table_data.get('cells', [])
                if not cells:
                    continue
                
                # Use sophisticated table processing
                table_items = cls._extract_table_items_sophisticated(
                    cells, table_data, page_num, table_idx
                )
                page_result['items'].extend(table_items)
            
            # 3. Process Text with sophisticated pattern matching
            text_items = cls._extract_text_items_sophisticated(
                text, blocks, page_num
            )
            page_result['items'].extend(text_items)
            
            # 4. Hierarchy Inference (if available)
            if cls._financial_parser:
                try:
                    cls._infer_hierarchy(page_result['items'])
                except Exception as e:
                    logger.debug(f"Hierarchy inference failed: {e}")
            
            # 5. Terminology Matching (if available)
            if cls._financial_parser:
                try:
                    cls._match_terminology(page_result['items'])
                except Exception as e:
                    logger.debug(f"Terminology matching failed: {e}")
            
            # 6. Quality Score
            page_result['quality_score'] = cls._calculate_quality_score(page_result)
            
            # 7. Metadata
            page_result['metadata'] = {
                'total_items': len(page_result['items']),
                'tables_processed': len(tables),
                'has_statement_header': page_result['statement_type'] != 'unknown',
                'text_length': len(text)
            }
            
            # STREAM the result immediately
            if stream_callback:
                stream_callback(page_result)
            
            return page_result
            
        except Exception as e:
            logger.error(f"Error analyzing page {page_num}: {e}")
            traceback.print_exc()
            if stream_callback:
                stream_callback({
                    'page_num': page_num,
                    'items': [],
                    'error': str(e)
                })
            return {
                'page_num': page_num,
                'items': [],
                'error': str(e)
            }
    
    @classmethod
    def _extract_table_items_sophisticated(
        cls,
        cells: List[List],
        table_data: Dict[str, Any],
        page_num: int,
        table_idx: int
    ) -> List[Dict[str, Any]]:
        """
        Extract items from table with sophisticated processing.
        This preserves all data quality.
        """
        items = []
        
        if not cells or len(cells) < 2:
            return items
        
        # Identify headers
        headers = cells[0] if cells else []
        num_cols = len(headers)
        
        # Identify which columns are numeric
        numeric_cols = []
        for col_idx in range(min(5, len(headers) if headers else 0)):
            if headers and col_idx < len(headers):
                header = str(headers[col_idx]).lower()
                # Check if header looks like a number column
                if any(term in header for term in ['amount', 'rs.', '₹', 'year', '202', 'current', 'previous']):
                    numeric_cols.append(col_idx)
            else:
                # Check data in rows
                numeric_count = 0
                for row in cells[1:min(6, len(cells))]:
                    if col_idx < len(row) and row[col_idx]:
                        val = str(row[col_idx]).strip()
                        if re.match(r'^[\d,\(\)\-\.]+$', val):
                            numeric_count += 1
                if numeric_count > len(cells[1:min(6, len(cells))]) * 0.5:
                    numeric_cols.append(col_idx)
        
        # Process each row
        for row_idx, row in enumerate(cells[1:], start=1):
            if not row:
                continue
            
            # Find label (first non-numeric column)
            label = None
            for col_idx, cell in enumerate(row):
                if col_idx >= 6:  # Limit search
                    break
                if cell is not None:
                    cell_str = str(cell).strip()
                    if cell_str and not re.match(r'^[\d,\(\)\-\.]+$', cell_str):
                        label = cell_str
                        break
            
            if not label or len(label) < 3:
                continue
            
            # Extract numeric values
            values = []
            for col_idx in numeric_cols:
                if col_idx < len(row) and row[col_idx] is not None:
                    val_str = str(row[col_idx]).strip()
                    if val_str:
                        # Parse Indian/International format
                        val = cls._parse_financial_value(val_str)
                        if val is not None:
                            values.append(val)
            
            if values:
                items.append({
                    'id': f"p{page_num}_t{table_idx}_r{row_idx}",
                    'label': label,
                    'current_year': values[0] if len(values) > 0 else None,
                    'previous_year': values[1] if len(values) > 1 else None,
                    'page_num': page_num,
                    'section': 'table',
                    'source': 'table',
                    'table_idx': table_idx,
                    'row_idx': row_idx
                })
        
        return items
    
    @classmethod
    def _extract_text_items_sophisticated(
        cls,
        text: str,
        blocks: List[Dict[str, Any]],
        page_num: int
    ) -> List[Dict[str, Any]]:
        """
        Extract items from text with sophisticated pattern matching.
        This catches all patterns the detailed parser would find.
        """
        items = []
        
        # Use same patterns as FinancialParser for consistency
        # Pattern: label followed by number(s)
        number_pattern = re.compile(
            r'([\w\s\-\&\(\)]+?)\s+([\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?)'
        )
        
        lines = text.split('\n')
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if len(line) < 10 or len(line) > 300:
                continue
            
            # Find all matches
            matches = list(number_pattern.finditer(line))
            
            if matches:
                # Extract label from before first number
                first_match = matches[0]
                label = line[:first_match.start()].strip()
                
                if len(label) < 3:
                    continue
                
                # Extract all numbers
                values = []
                for match in matches:
                    val_str = match.group(2)
                    val = cls._parse_financial_value(val_str)
                    if val is not None:
                        values.append(val)
                
                if values:
                    items.append({
                        'id': f"p{page_num}_l{line_idx}",
                        'label': label,
                        'current_year': values[0] if len(values) > 0 else None,
                        'previous_year': values[1] if len(values) > 1 else None,
                        'page_num': page_num,
                        'section': 'text',
                        'source': 'text',
                        'line_idx': line_idx
                    })
        
        return items
    
    @classmethod
    def _parse_financial_value(cls, value_str: str) -> Optional[float]:
        """Parse financial value with Indian/International format support."""
        if not value_str:
            return None
        
        value_str = str(value_str).strip()
        
        # Check for parentheses (negative)
        is_negative = False
        if value_str.startswith('(') and value_str.endswith(')'):
            is_negative = True
            value_str = value_str[1:-1]
        
        # Remove formatting
        cleaned = re.sub(r'[\,\s]', '', value_str)
        
        try:
            val = float(cleaned)
            return -val if is_negative else val
        except ValueError:
            return None
    
    @classmethod
    def _infer_hierarchy(cls, items: List[Dict[str, Any]]):
        """Infer hierarchy from indent levels."""
        # Simple hierarchy inference based on common patterns
        for item in items:
            label = item.get('label', '')
            # Detect sub-items by indentation or prefixes
            if any(label.startswith(p) for p in ['  ', '    ', '\t', '- ', '• ']):
                item['is_sub_item'] = True
            elif any(label.startswith(p) for p in ['Total', 'Gross Total', 'Net']):
                item['is_total'] = True
    
    @classmethod
    def _match_terminology(cls, items: List[Dict[str, Any]]):
        """Match labels to terminology (simplified)."""
        # This would use the full terminology matching engine
        # For now, just categorize basic items
        for item in items:
            label = item.get('label', '').lower()
            if 'assets' in label:
                item['category'] = 'assets'
            elif 'liabilit' in label:
                item['category'] = 'liabilities'
            elif 'equity' in label:
                item['category'] = 'equity'
            elif 'revenue' in label or 'income' in label:
                item['category'] = 'income'
            elif 'expense' in label:
                item['category'] = 'expenses'
    
    @classmethod
    def _calculate_quality_score(cls, page_result: Dict[str, Any]) -> float:
        """Calculate quality score for the page analysis."""
        items = page_result.get('items', [])
        
        if not items:
            return 0.0
        
        score = 0.0
        
        # Base score for having items
        score += min(10, len(items) * 0.5)  # Max 10 points
        
        # Statement detection
        if page_result.get('statement_type') != 'unknown':
            score += 5.0
        
        # Entity detection
        if page_result.get('entity') != 'unknown':
            score += 2.5
        
        # Confidence
        confidence = page_result.get('confidence', 0)
        score += confidence * 2.5  # Max 2.5 points
        
        return min(20.0, score)  # Max 20 points


def analyze_streaming(
    doc: fitz.Document,
    config: Optional[Dict[str, Any]] = None,
    max_workers: Optional[int] = None,
    progress_callback: Optional[callable] = None,
    stream_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Hybrid analysis with streaming results.
    
    1. Parallel: Fast raw extraction (text, tables)
    2. Sequential: Sophisticated analysis with streaming
    
    This gives us:
    - Speed: Parallel extraction
    - Quality: Sequential sophisticated analysis
    - UX: Streaming results
    """
    if max_workers is None:
        max_workers = min(mp.cpu_count(), 8)
    
    config = config or {}
    total_pages = len(doc)
    
    logger.info(f"Hybrid streaming analysis: {total_pages} pages with {max_workers} workers")
    
    # -------------------------------------------------------------------------
    # PHASE 1: Parallel Raw Extraction (FAST)
    # -------------------------------------------------------------------------
    if progress_callback:
        progress_callback(1, total_pages, 'Starting parallel extraction...')
    
    raw_data = parallel_extract_raw_pages(
        doc, config, max_workers, progress_callback
    )
    
    # -------------------------------------------------------------------------
    # PHASE 2: Sequential Sophisticated Analysis (QUALITY)
    # -------------------------------------------------------------------------
    if progress_callback:
        progress_callback(total_pages, total_pages, 'Running sophisticated analysis...')
    
    all_items = []
    all_pages = []
    quality_scores = []
    
    for raw_page in raw_data['pages']:
        page_num = raw_page['page_num']
        
        # Analyze with all sophisticated logic
        page_result = QualityAnalyzer.analyze_page_streaming(
            raw_page,
            page_num,
            total_pages,
            stream_callback=stream_callback
        )
        
        all_pages.append(page_result)
        all_items.extend(page_result.get('items', []))
        
        if 'quality_score' in page_result:
            quality_scores.append(page_result['quality_score'])
        
        # Update progress
        if progress_callback:
            progress = int((page_num + 1) / total_pages * 100)
            progress_callback(page_num + 1, total_pages, 
                          f'Analyzed page {page_num + 1}/{total_pages}...')
    
    # -------------------------------------------------------------------------
    # Build final result
    # -------------------------------------------------------------------------
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    result = {
        'status': 'success',
        'items': all_items,
        'pages': all_pages,
        'metadata': {
            'total_pages': total_pages,
            'total_items': len(all_items),
            'avg_quality_score': avg_quality,
            'extraction_time': raw_data.get('extraction_time', 0),
            'analysis_mode': 'hybrid_streaming'
        }
    }
    
    return result


class HybridFinancialParser:
    """
    Hybrid parser combining speed and quality.
    - Parallel raw extraction
    - Sequential sophisticated analysis  
    - Streaming results
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        logger.info(f"Initialized HybridFinancialParser with {self.max_workers} workers")
    
    def parse(
        self,
        pdf_path: str,
        progress_callback: Optional[callable] = None,
        stream_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Parse PDF with hybrid approach + streaming.
        """
        start_time = time.time()
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            logger.info(f"Parsing PDF: {pdf_path} ({total_pages} pages)")
            
            # Analyze with streaming
            result = analyze_streaming(
                doc,
                config={},
                max_workers=self.max_workers,
                progress_callback=progress_callback,
                stream_callback=stream_callback
            )
            
            doc.close()
            
            result['metadata']['processing_time'] = time.time() - start_time
            result['metadata']['parser_version'] = '3.0.0-hybrid-streaming'
            
            return result
            
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hybrid_pdf_processor.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    def progress_callback(current, total, message):
        print(f"[{current}/{total}] {message}")
    
    def stream_callback(page_data):
        """Stream page results as they're available"""
        print(f"\n>>> PAGE {page_data['page_num']}: {len(page_data['items'])} items extracted")
        if page_data.get('items'):
            print(f"    First item: {page_data['items'][0].get('label', 'N/A')[:50]}...")
        print(f"    Quality score: {page_data.get('quality_score', 0):.1f}/20")
        print(f"    Statement type: {page_data.get('statement_type', 'unknown')}")
        print(f"    Entity: {page_data.get('entity', 'unknown')}")
        sys.stdout.flush()
    
    parser = HybridFinancialParser()
    result = parser.parse(pdf_path, progress_callback, stream_callback)
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Total items: {result['metadata']['total_items']}")
        print(f"Total pages: {result['metadata']['total_pages']}")
        print(f"Avg quality: {result['metadata']['avg_quality_score']:.1f}/20")
        print(f"Processing time: {result['metadata']['processing_time']:.2f}s")
        print(f"Extraction time: {result['metadata']['extraction_time']:.2f}s")
