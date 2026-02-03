
import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from parser_config import ExtractedTable, clean_text

logger = logging.getLogger(__name__)

# =============================================================================
# Graph Data Structures
# =============================================================================

@dataclass
class ColumnMetadata:
    """Metadata for a table column."""
    index: int
    header_text: str
    column_type: str = "unknown"  # 'description', 'amount_current', 'amount_previous', 'note', 'unknown'
    period_date: Optional[str] = None  # ISO format "YYYY-MM-DD"
    period_label: str = ""  # "2023", "31st March 2024", etc.
    currency_unit: str = "INR"

@dataclass
class FinancialCell:
    """A semantic 'atom' of financial data."""
    # Physical Properties
    row_idx: int
    col_idx: int
    raw_text: str
    
    # Context Properties
    row_header: str      # The "Particulars" label for this row
    col_header: str      # Column header text
    section: str         # "Current Assets", "Income", etc.
    parent_row: str      # For hierarchy (e.g. "Total Assets")
    note_ref: str        # Related note reference if found
    
    # Semantic Properties
    value: float
    sign: int            # +1 or -1
    period_date: Optional[str] # Resolved date
    period_label: str    # "Current", "2023", etc.
    metric_key: Optional[str] = None # Matched metric key

@dataclass
class FinancialTableGraph:
    """
    Semantic graph representation of a financial table.
    Bridges the gap between raw text rows and structured financial/metric objects.
    """
    source_table: ExtractedTable
    columns: List[ColumnMetadata]
    cells: List[FinancialCell]
    
    # Mappings for easy lookup
    _cells_by_pos: Dict[Tuple[int, int], FinancialCell] = field(default_factory=dict)
    
    def __post_init__(self):
        for cell in self.cells:
            self._cells_by_pos[(cell.row_idx, cell.col_idx)] = cell


# =============================================================================
# Table Graph Builder
# =============================================================================

class TableGraphBuilder:
    """
    Reconstructs the logical graph from a physical table.
    
    Gap 2 Solver: Explicitly maps columns to Periods.
    Gap 1 Solver: Explicitly maps cells to Row Context (Section, Indentation).
    """
    
    def __init__(self):
        from indian_finance_utils import IndianNumberParser, IndianDateParser
        self.number_parser = IndianNumberParser()
        self.date_parser = IndianDateParser()

    def build_graph(self, table: ExtractedTable) -> FinancialTableGraph:
        """Main entry point: Transform ExtractedTable -> FinancialTableGraph"""
        
        # 0. Detect Global Table Unit Multiplier (Phase 2.1)
        # Scan headers for unit content
        header_text = " ".join(table.headers)
        
        # Use new IndianNumberParser for scale detection
        multiplier, currency = self.number_parser.detect_scale_from_header(header_text)
        self.multiplier = multiplier
        
        if self.multiplier != 1.0:
            logger.info(f"Detected unit multiplier: {self.multiplier} ({currency}) for table on page {table.page_num}")
        
        # 1. Analyze Columns (Header Parsing)
        columns = self._analyze_columns(table.headers)
        
        # 2. Build Row Context & Cells
        cells = self._process_rows(table.rows, columns)
        
        return FinancialTableGraph(
            source_table=table,
            columns=columns,
            cells=cells
        )

    def _analyze_columns(self, headers: List[str]) -> List[ColumnMetadata]:
        """Determine what each column represents (Period, Note, Description)."""
        metas = []
        
        # Helper lists for period detection
        date_columns = []
        
        for idx, header in enumerate(headers):
            h_clean = clean_text(header).lower()
            meta = ColumnMetadata(index=idx, header_text=header)
            
            # 1. Detect Note Column
            if re.search(r'\bnotes?\b', h_clean):
                meta.column_type = "note"
            
            # 2. Detect Description Column
            elif re.search(r'particulars|description|asset|liability|equity|revenue', h_clean):
                meta.column_type = "description"
                
        # 3. Detect Period/Amount Columns
            else:
                # Use IndianDateParser
                period_info = self.date_parser.parse_period_header(header)
                
                if period_info and period_info.get('date'):
                    meta.column_type = "amount"
                    # Format date as ISO string
                    date_obj = period_info['date']
                    meta.period_date = date_obj.strftime("%Y-%m-%d") if date_obj else None
                    meta.period_label = period_info.get('label', header)
                    date_columns.append(meta)
                elif re.search(r'\b20\d{2}\b', header): # Just year like "2023"
                    # Try to normalize year-only headers to end-of-year dates for sorting
                    year_match = re.search(r'\b(20\d{2})\b', header)
                    if year_match:
                        year = year_match.group(1)
                        # Assume March 31st for sorting purposes if only year is given (common in India)
                        # But keep period_label accurate
                        meta.column_type = "amount"
                        meta.period_date = f"{year}-03-31" 
                        meta.period_label = header
                        date_columns.append(meta)
                else:
                     # Fallback check: if it comes after description, likely amount
                     if idx > 0 and metas[0].column_type == "description":
                         meta.column_type = "amount_unknown"
            
            metas.append(meta)
            
        # Post-Processing: STRICT Disambiguation of "Current" vs "Previous"
        if len(date_columns) >= 2:
            try:
                # Sort by date descending (Newest = Current)
                # Parse dates if they are full dates
                valid_dates = [m for m in date_columns if m.period_date]
                if valid_dates:
                    # ISO string compare works for YYYY-MM-DD
                    valid_dates.sort(key=lambda x: x.period_date, reverse=True)
                    
                    # Highest date is Current
                    valid_dates[0].column_type = "amount_current"
                    # Next is Previous
                    if len(valid_dates) > 1:
                        valid_dates[1].column_type = "amount_previous"
                    
                    # Remaining are just previous history
                    for m in valid_dates[2:]:
                        m.column_type = "amount_previous"
            except Exception as e:
                logger.debug(f"Date sort failed: {e}")
                
        # Fallback: If no dates found, assume standard ordering for Amount columns:
        # Col 1 (after desc) = Current, Col 2 = Previous (Common in India)
        amount_cols = [m for m in metas if "amount" in m.column_type and "current" not in m.column_type and "previous" not in m.column_type]
        
        # Only apply heuristic if we haven't already assigned via dates
        already_assigned = any("current" in m.column_type for m in metas)
        
        if not already_assigned and amount_cols:
             if len(amount_cols) >= 1:
                 amount_cols[0].column_type = "amount_current"
             if len(amount_cols) >= 2:
                 amount_cols[1].column_type = "amount_previous"

        return metas

    def _extract_date_from_header(self, header: str) -> Optional[str]:
        """Extract ISO date found in header text (e.g., 'As at 31-03-2023' -> '2023-03-31')"""
        header_clean = re.sub(r'\s+', ' ', header).strip()
        
        # Pattern 1: DD.MM.YYYY or DD-MM-YYYY or DD/MM/YYYY
        dmy_pattern = r'(\d{1,2})[\.\-\/](\d{1,2})[\.\-\/](\d{4})'
        match = re.search(dmy_pattern, header_clean)
        if match:
             d, m, y = match.groups()
             return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
             
        # Pattern 2: "March 31, 2023" or "31st March 2023"
        # Handles ordinals (st, nd, rd, th)
        # Handles optional commas
        
        # 31st March 2023
        dm_pattern = r'(\d{1,2})(?:st|nd|rd|th)?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+(\d{4})'
        match_dm = re.search(dm_pattern, header_clean, re.IGNORECASE)
        if match_dm:
            day, mon, year = match_dm.groups()
            try:
                dt = datetime.strptime(f"{day} {mon} {year}", "%d %b %Y")
                return dt.strftime("%Y-%m-%d")
            except:
                pass

        # March 31, 2023
        md_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:st|nd|rd|th)?[\s,]+(\d{4})'
        match_md = re.search(md_pattern, header_clean, re.IGNORECASE)
        if match_md:
            mon, day, year = match_md.groups()
            try:
                dt = datetime.strptime(f"{day} {mon} {year}", "%d %b %Y")
                return dt.strftime("%Y-%m-%d")
            except:
                pass
                
        return None

    def _process_rows(self, rows: List[List[str]], columns: List[ColumnMetadata]) -> List[FinancialCell]:
        """Process rows to build context and cells."""
        cells = []
        
        current_section = "Uncategorized"
        section_stack = [] # For hierarchy if needed
        
        desc_col_idx = next((c.index for c in columns if c.column_type == 'description'), 0)
        note_col_idx = next((c.index for c in columns if c.column_type == 'note'), -1)
        
        for row_idx, row in enumerate(rows):
            # 1. Get Row Header (Description)
            if desc_col_idx < len(row):
                row_header = clean_text(row[desc_col_idx])
            else:
                row_header = ""
                
            if not row_header: 
                continue

            # 2. Context Detection: Is this a Section Header?
            # Heuristic: Uppercase, or bold (if we had font info), or no numbers in row
            # For now, simplistic: if row has no numbers, it's likely a section
            has_numbers = any(re.search(r'\d', cell) for i, cell in enumerate(row) if i != desc_col_idx and i != note_col_idx)
            
            if not has_numbers and len(row_header) > 3:
                # Update current section
                current_section = row_header
                continue

            # 3. Context Detection: Sign Convention
            # "Less:", "Expenses" section -> negative
            sign = 1
            if re.search(r'\b(less|deduct)\b', row_header.lower()):
                sign = -1
            elif "expenses" in current_section.lower() and "income" not in current_section.lower():
                # Be careful, sometimes Expenses are positive in the list but subtracted in total
                # Usually better to capture as positive and let formula handle, BUT user asked for sign context.
                # Let's check for explicit "(-)" or parentheses in value
                pass 

            # 4. Extract Note Ref
            note_ref = ""
            if note_col_idx != -1 and note_col_idx < len(row):
                 note_ref = clean_text(row[note_col_idx])

            # 5. Create Cells for Amount Columns
            for col in columns:
                if col.column_type in ['amount_current', 'amount_previous', 'amount', 'amount_unknown']:
                    if col.index >= len(row): continue
                    
                    raw_val = row[col.index]
                    val_clean = re.sub(r'[^\d\.\-\(\)]', '', raw_val)
                    if not val_clean: continue
                    
                    # Detect parenthesis negative
                    if '(' in raw_val and ')' in raw_val:
                        item_sign = -1 * sign # Combine with row context sign? Usually one or other.
                    else:
                        item_sign = sign
                        
                    # Parse value
                    try:
                        # Use IndianNumberParser instance
                        value = self.number_parser.parse_indian_formatted_number(raw_val)
                        if value is None:
                             # Try parsing mixed format if simple parse fails but looks like number/decimal
                             if re.search(r'\d', raw_val):
                                 value = self.number_parser.parse_mixed_indian_us_format(raw_val)
                             else:
                                 continue

                        # Apply Multiplier (Phase 2.1)
                        if hasattr(self, 'multiplier'):
                             value *= self.multiplier
                             
                    except ValueError:
                        continue
                        
                    # Create Semantic Cell
                    cell = FinancialCell(
                        row_idx=row_idx,
                        col_idx=col.index,
                        raw_text=raw_val,
                        row_header=row_header,
                        col_header=col.header_text,
                        section=current_section,
                        parent_row="", # TODO: Implement indentation hierarchy
                        note_ref=note_ref,
                        value=value,
                        sign=item_sign,
                        period_date=col.period_date,
                        period_label=col.period_label,
                        metric_key=None # To be filled by Matching Engine
                    )
                    cells.append(cell)
                    
        return cells
