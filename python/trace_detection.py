#!/usr/bin/env python3
"""Trace statement detection and extraction using FinancialParser directly."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import fitz
from parsers import FinancialParser, ParserConfig

pdf_path = "/home/nikhil/Gemini Workspace/Financial-Calculator/Apple Rep.pdf"
doc = fitz.open(pdf_path)

# Create parser with debug enabled
config = ParserConfig(include_debug_info=True)
parser = FinancialParser(config)

print("="*80)
print("TRACING STATEMENT DETECTION")
print("="*80)

# Check pages 32-45 (where actual statements are)
for page_num in range(30, 45):
    if page_num >= len(doc):
        break
        
    page = doc[page_num]
    text = page.get_text()
    
    # Use parser's detector
    identifier, conf, title = parser.detector.detect_full_statement(text, page_num)
    entity, entity_conf = parser.detector.detect_reporting_entity(text)
    
    stmt_type = identifier.statement_type.value
    
    # Check for key patterns
    has_balance = "balance sheet" in text.lower()
    has_consolidated = "consolidated" in text.lower()
    has_total_assets = "total assets" in text.lower()
    has_income = "income statement" in text.lower() or "operations" in text.lower()
    has_cash_flow = "cash flow" in text.lower()
    
    marker = ""
    if stmt_type != "unknown":
        marker = " <== DETECTED"
    
    print(f"\nPage {page_num + 1}:{marker}")
    print(f"  Type: {stmt_type} ({conf:.2f})")
    print(f"  Entity: {entity.value} ({entity_conf:.2f})")
    print(f"  Title: {title[:70]}..." if title and len(title) > 70 else f"  Title: {title}")
    print(f"  Flags: BS={has_balance}, CONS={has_consolidated}, Assets={has_total_assets}, IS={has_income}, CF={has_cash_flow}")

doc.close()

print("\n" + "="*80)
print("CHECKING ACTUAL PARSING")
print("="*80)

# Now actually parse and see what we get
result = parser.parse(pdf_path)

# Check metadata for statement boundaries
if 'metadata' in result:
    if 'statement_boundaries' in result['metadata']:
        print("\nDetected Statement Boundaries:")
        for key, boundary in result['metadata'].get('statement_boundaries', {}).items():
            print(f"  {key}: pages {boundary}")
    else:
        print("\nNo statement_boundaries in metadata")
        print("Metadata keys:", list(result.get('metadata', {}).keys()))

# Check items
items = result.get('items', [])
print(f"\nTotal items extracted: {len(items)}")

# Check for key items
key_ids = ['total_assets', 'total_liabilities', 'cash_and_equivalents', 'revenue', 'net_income']
print("\nKey items check:")
for key_id in key_ids:
    item = next((i for i in items if i.get('id') == key_id), None)
    if item:
        print(f"  ✓ {key_id}: {item.get('currentYear', 0):,.0f} / {item.get('previousYear', 0):,.0f}")
    else:
        print(f"  ✗ {key_id}: NOT FOUND")

# Show which statements were populated
print("\nStatement population check:")
for entity in ['consolidated', 'standalone']:
    for stmt in ['balance_sheet', 'income_statement', 'cash_flow']:
        if entity in result and stmt in result[entity]:
            stmt_items = result[entity][stmt].get('items', [])
            pages = result[entity][stmt].get('pages', [])
            print(f"  {entity}/{stmt}: {len(stmt_items)} items, pages {pages}")
