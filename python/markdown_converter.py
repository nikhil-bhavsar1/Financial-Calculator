
try:
    import fitz
except ImportError:
    fitz = None

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class MarkdownConverter:
    """
    Converts PDF documents to Markdown format, preserving tables and structure.
    Enhanced to handle multi-line date headers common in financial statements.
    """
    
    # Patterns for date/year detection
    DATE_PATTERNS = [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{0,2}\s*,?\s*$',
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s*\d{0,2}\s*,?\s*$',
        r'\d{1,2}\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*$',
        r'As\s+(?:at|of)\s*$',
        r'For\s+the\s+(?:year|period)\s+ended?\s*$',
        r'Fiscal\s+Year\s+Ended?\s*$',
    ]
    
    YEAR_PATTERN = r'^(20\d{2}|19\d{2})$'
    
    def __init__(self):
        if not fitz:
            logger.warning("PyMuPDF (fitz) not available. Markdown conversion will fail.")
        
    def convert_document(self, doc: Any) -> str:
        """
        Convert entire PDF document to Markdown.
        """
        if not fitz: return ""
        full_markdown = []
        
        for page_num, page in enumerate(doc):
            page_md = self.convert_page(page, page_num)
            full_markdown.append(f"--- Page {page_num + 1} ---\n\n{page_md}")
            
        return "\n\n".join(full_markdown)
    
    def convert_page(self, page: Any, page_num: int) -> str:
        """
        Convert a single PDF page to Markdown, handling tables and headers.
        Enhanced to handle multi-line date headers.
        """
        if not fitz: return ""

        # 1. Extract Tables to Markdown
        tables = []
        try:
            if hasattr(page, 'find_tables'):
                tables = page.find_tables()
        except Exception as e:
            logger.warning(f"Table detection failed on page {page_num}: {e}")

        text_blocks = page.get_text("blocks")
        # Format: (x0, y0, x1, y1, "lines\n", block_no, block_type)
        
        # Filter out blocks that are inside tables
        table_rects = [t.bbox for t in tables]
        
        cleaned_blocks = []
        for b in text_blocks:
            bbox = fitz.Rect(b[:4])
            # Check if block is significantly inside a table
            is_in_table = False
            for t_rect in table_rects:
                if fitz.Rect(t_rect).contains(bbox) or fitz.Rect(t_rect).intersect(bbox).get_area() > 0.5 * bbox.get_area():
                    is_in_table = True
                    break
            
            if not is_in_table:
                cleaned_blocks.append(b)

        # NEW: Merge date fragments with year blocks
        cleaned_blocks = self._merge_date_year_blocks(cleaned_blocks)
        
        # Now sort cleaned blocks and tables by vertical position (y0)
        content_items = []
        
        # Add Text Blocks
        for b in cleaned_blocks:
            content_items.append({
                'y0': b[1],
                'x0': b[0],
                'type': 'text',
                'content': b[4] if len(b) > 4 else '',
                'bbox': b[:4]
            })
            
        # Add Tables with enhanced header detection
        for table in tables:
            md_table = self._table_to_markdown(table, cleaned_blocks)
            content_items.append({
                'y0': table.bbox[1],
                'x0': table.bbox[0], 
                'type': 'table',
                'content': md_table,
                'bbox': table.bbox
            })
            
        # Sort by Y position (top to bottom), then X (left to right)
        content_items.sort(key=lambda x: (x['y0'], x['x0']))
        
        # Generate MD - filter out year-only lines that were merged into tables
        md_output = []
        
        for item in content_items:
            if item['type'] == 'text':
                text = item['content'].strip()
                if not text: continue
                
                # Skip standalone year lines (they're part of table headers)
                if self._is_year_line(text):
                    continue
                
                # Skip date fragments that should be part of headers
                if self._is_date_fragment(text) and self._looks_like_header_context(text):
                    continue
                
                # Clean text
                text = re.sub(r'\s+', ' ', text)
                
                # Header heuristics
                is_header = False
                if len(text) < 100:
                    if text.isupper() and not text.endswith('.'):
                        is_header = True
                    elif re.match(r'^(Note|Schedule)\s+\d+', text, re.I):
                        is_header = True
                
                if is_header:
                    md_output.append(f"\n## {text}\n")
                else:
                    md_output.append(f"{text}\n")
                    
            elif item['type'] == 'table':
                md_output.append(f"\n{item['content']}\n")
                
        return "\n".join(md_output)
    
    def _merge_date_year_blocks(self, blocks: List) -> List:
        """
        Merge date fragments (e.g., 'September 30,') with subsequent year blocks.
        This handles the common pattern in financial statements where column headers
        span multiple lines.
        """
        if len(blocks) < 2:
            return blocks
        
        merged = []
        i = 0
        skip_indices = set()
        
        while i < len(blocks):
            if i in skip_indices:
                i += 1
                continue
                
            block = blocks[i]
            text = block[4].strip() if len(block) > 4 else ''
            
            # Check if this is a date fragment
            if self._is_date_fragment(text):
                # Look ahead for year blocks in the next few blocks
                years_found = []
                look_ahead_limit = min(i + 6, len(blocks))
                j = i + 1
                
                # Collect all year blocks that are vertically close
                base_y = block[1]
                consumed_indices = []
                
                while j < look_ahead_limit:
                    if j in skip_indices:
                        j += 1
                        continue
                        
                    next_block = blocks[j]
                    next_text = next_block[4].strip() if len(next_block) > 4 else ''
                    next_y = next_block[1]
                    
                    # Check vertical proximity (within ~100 points)
                    if abs(next_y - base_y) < 100:
                        if self._is_year_line(next_text):
                            years_found.append(next_text)
                            consumed_indices.append(j)
                            j += 1
                            continue
                    
                    break
                
                if years_found:
                    # Merge: create a combined header text
                    combined_text = f"{text} {' | '.join(years_found)}"
                    new_block = (block[0], block[1], block[2], block[3], combined_text, block[5] if len(block) > 5 else 0, block[6] if len(block) > 6 else 0)
                    merged.append(new_block)
                    for idx in consumed_indices:
                        skip_indices.add(idx)
                    i += 1
                    continue
            
            merged.append(block)
            i += 1
        
        return merged
    
    def _is_date_fragment(self, text: str) -> bool:
        """Check if text looks like a date fragment (month + day, ends with comma)."""
        text = text.strip()
        if not text:
            return False
        for pattern in self.DATE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_year_line(self, text: str) -> bool:
        """Check if text is just a year (e.g., '2025', '2024')."""
        text = text.strip()
        if not text:
            return False
        # Handle multiple years on same line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(self.YEAR_PATTERN, line):
                return True
        # Also check if it's just a year
        if re.match(r'^(20\d{2}|19\d{2})$', text):
            return True
        return False
    
    def _looks_like_header_context(self, text: str) -> bool:
        """Check if this date fragment is likely a table header context."""
        # Date fragments ending with comma and having fiscal year context
        if text.strip().endswith(','):
            return True
        if re.search(r'(As\s+(?:at|of)|ended?|year)', text, re.I):
            return True
        return False

    def _table_to_markdown(self, table, nearby_blocks: List = None) -> str:
        """Convert a PyMuPDF table object to a Markdown table string with enhanced header handling."""
        try:
            rows = table.extract()
            
            if not rows: return ""
            
            # Clean cells and handle multi-line content
            cleaned_rows = []
            for row in rows:
                cleaned_row = []
                for cell in row:
                    if cell is None:
                        cleaned_row.append("")
                    else:
                        # Join multi-line cell content
                        cell_text = str(cell).replace('\n', ' ').strip()
                        # Clean up extra spaces
                        cell_text = re.sub(r'\s+', ' ', cell_text)
                        cleaned_row.append(cell_text)
                cleaned_rows.append(cleaned_row)
                
            if not cleaned_rows: return ""
            
            # Detect and enhance headers
            headers = cleaned_rows[0]
            body = cleaned_rows[1:]
            
            # Check for year pattern in headers - common in financial statements
            # If we see years like 2024, 2023 etc, format them nicely
            enhanced_headers = []
            for h in headers:
                h_clean = h.strip()
                # If it's a year, keep it
                if re.match(r'^(20\d{2}|19\d{2})$', h_clean):
                    enhanced_headers.append(h_clean)
                # If it contains $ symbol, it's likely a currency column
                elif '$' in h_clean:
                    enhanced_headers.append(h_clean)
                else:
                    enhanced_headers.append(h_clean)
            
            headers = enhanced_headers
            
            # Build MD table
            md_lines = []
            
            # Create separator
            num_cols = len(headers)
            sep = ["---"] * num_cols
            
            # Helper to join row with proper padding
            def join_row(r):
                # Pad row to header length
                while len(r) < num_cols:
                    r.append("")
                return "| " + " | ".join(r[:num_cols]) + " |"
            
            md_lines.append(join_row(headers))
            md_lines.append(join_row(sep))
            for r in body:
                md_lines.append(join_row(r))
                
            return "\n".join(md_lines)
            
        except Exception as e:
            logger.warning(f"Table markdown conversion error: {e}")
            return "[Table Conversion Failed]"