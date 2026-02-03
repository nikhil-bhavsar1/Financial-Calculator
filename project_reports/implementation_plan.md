# Implementation Plan: Financial Statement Graph Reconstruction

## Goal
Transform the current "text-based" table extraction into a "semantic graph" extraction to resolve the 60% metric loss caused by context blindness.

## key Changes
1.  **New Module**: `python/table_graph_builder.py`
    - Implements the `TableGraphBuilder` class.
    - Transforms `ExtractedTable` -> `FinancialTableGraph`.
    - Handles **Period Disambiguation** (Gap 2) via column header parsing.
    - Handles **Row Context** (Gap 1) via identifying sections, signs, and hierarchy.

2.  **Refactor**: `python/parser_table_extraction.py`
    - Enhance `ExtractedTable` to support "Rich Headers" (not just strings).
    - Ensure raw cell metadata (indentation, etc.) is preserved where possible.

3.  **Refactor**: `python/metrics_engine.py` / `python/matching_engine.py`
    - Update to consume `FinancialCell` objects instead of raw strings.
    - Use "Row Header" + "Context" for matching, not just cell text.

## Proposed Structures

### 1. Financial Cell (The Atom)
```python
@dataclass
class FinancialCell:
    # Physical Properties
    raw_text: str
    row_idx: int
    col_idx: int
    
    # Context Properties
    row_header: str     # The "Particulars" text for this row
    col_header: str     # The header text for this column
    section: str        # e.g., "Current Assets"
    parent_row: str     # For indentation hierarchy (e.g. "Total Assets")
    
    # Semantic Properties
    value: float
    sign: int           # +1 or -1 (detected from "Less:", "()", etc.)
    period_date: str    # ISO date "2023-03-31"
    metric_key: str     # Finally resolved key (e.g., "total_revenue")
```

### 2. Table Context (The Graph)
```python
@dataclass
class TableContext:
    columns: List[ColumnMetadata]  # Type, Date, Unit
    section_map: Dict[int, str]    # Row Index -> Section Name
```

## Step-by-Step Implementation

### Step 1: Create `python/table_graph_builder.py`
- Implement `detect_column_metadata(headers)`:
    - Regex for dates (DD/MM/YYYY, "As at...", "For year ended...").
    - Distinguish "Current Year" vs "Previous Year" columns.
- Implement `detect_row_context(rows)`:
    - Identify Section Headers (lines with no numbers).
    - Identify Indentation/Hierarchy (parent/child).
    - Identify Sign Context ("Less:", "Expenses").

### Step 2: Integrate into `parser_table_extraction.py`
- Modify `extract_tables` pipeline to pass raw tables through `TableGraphBuilder`.
- Return the "Graph" object alongside or instead of the raw `ExtractedTable`.

### Step 3: Update Integration Tests
- Create `test_graph_reconstruction.py`.
- Feed explicit sample tables (Balance Sheet, Income Stmt).
- Verify:
    - "2023" column is correctly dated.
    - "Cost of Goods Sold" gets -1 sign if under "Expenses".
    - "Revenue" maps to `total_revenue`.

## Verification Plan
1.  Run `test_graph_reconstruction.py` on synthetic cases.
2.  Run full pipeline on user's sample PDF (if provided) or debugging sample.
3.  Check "Raw DB View" to see if improved metadata is visible (optional, for debug).
