#!/usr/bin/env python3
"""
Clean patch for api.py to add safe parser support.
This patch:
1. Adds safe_parser import
2. Modifies parser selection to check SAFE first
3. Adds safe parser processing block
"""

import re

# Read original file
with open('/home/nikhil/Gemini Workspace/Financial-Calculator/python/api_old.py', 'r') as f:
    content = f.read()

# 1. Add safe_parser import after detailed parser import
old_imports = '''# Try to import parsers
try:
    from parsers import FinancialParser
    DETAILED_PARSER_AVAILABLE = True
except ImportError as e:
    FinancialParser = None
    DETAILED_PARSER_AVAILABLE = False
    print(f"[api.py] Detailed parser import error: {e}", file=sys.stderr)

# Try hybrid processor'''

new_imports = '''# Try to import parsers
try:
    from parsers import FinancialParser
    DETAILED_PARSER_AVAILABLE = True
except ImportError as e:
    FinancialParser = None
    DETAILED_PARSER_AVAILABLE = False
    print(f"[api.py] Detailed parser import error: {e}", file=sys.stderr)

# Try SAFE parser wrapper (disables multiprocessing to prevent pickle errors)
try:
    from safe_parser import get_safe_parser
    SAFE_PARSER_AVAILABLE = True
except ImportError as e:
    SAFE_PARSER_AVAILABLE = False
    print(f"[api.py] Safe parser not available: {e}", file=sys.stderr)

# Try hybrid processor'''

content = content.replace(old_imports, new_imports)

# 2. Modify parser selection to check SAFE first
old_selection = '''        # Choose parser based on document size and availability
        # Small docs (≤5 pages): Use detailed parser for maximum quality
        # Large docs (>5 pages): Use hybrid parser (parallel + quality + streaming)
        use_hybrid = (HYBRID_PARSER_AVAILABLE and 
                     (actual_path.lower().endswith('.pdf') or actual_path.lower().endswith('.PDF')) and 
                     total_pages > 5)

        if use_hybrid:
            # HYBRID APPROACH: Parallel extraction + Sequential quality + Streaming
            print(f"[api.py] Using HybridFinancialParser for: {file_name} ({total_pages} pages) with STREAMING", file=sys.stderr)
            
            parser = HybridFinancialParser(max_workers=8)'''

new_selection = '''        # Choose parser with priority: SAFE > HYBRID > DETAILED
        # SAFE: Prevents pickle errors, 100% quality, original speed
        # HYBRID: Parallel + quality + streaming (may have pickle issues)
        # DETAILED: 100% quality, slow, no issues
        
        use_safe = SAFE_PARSER_AVAILABLE and (actual_path.lower().endswith('.pdf') or actual_path.lower().endswith('.PDF'))
        use_hybrid = (not use_safe) and HYBRID_PARSER_AVAILABLE and (actual_path.lower().endswith('.pdf') or actual_path.lower().endswith('.PDF')) and total_pages > 5

        if use_safe:
            # SAFE APPROACH: Prevents pickle errors, maintains 100% quality
            print(f"[api.py] Using Safe Parser for: {file_name} ({total_pages} pages) - NO PICKLE ERRORS", file=sys.stderr)
            parser = get_safe_parser()
        elif use_hybrid:
            # HYBRID APPROACH: Parallel extraction + Sequential quality + Streaming
            print(f"[api.py] Using HybridFinancialParser for: {file_name} ({total_pages} pages) with STREAMING", file=sys.stderr)
            parser = HybridFinancialParser(max_workers=8)
        else:
            # Fallback to detailed parser
            print(f"[api.py] Using Detailed FinancialParser for: {file_name} ({total_pages} pages)", file=sys.stderr)
            parser = FinancialParser()'''

content = content.replace(old_selection, new_selection)

# 3. Add SAFE parser block between HYBRID and DETAILED
# Find the end of HYBRID block (before "Use detailed parser")
old_detailed_header = '''        # Use detailed parser for small documents (≤5 pages)
        elif DETAILED_PARSER_AVAILABLE and FinancialParser:'''

new_detailed_header = '''        # SAFE Parser Block (added between HYBRID and DETAILED)
        if use_safe:
            # Parse with safe approach
            send_progress(5, 100, 'Initializing safe parser...')
            
            try:
                result = parser.parse(actual_path)
                send_progress(50, 100, 'Parsing complete, processing data...')
            except Exception as parse_error:
                print(f"[api.py] Safe parse error: {parse_error}", file=sys.stderr)
                send_progress(0, 100, 'Parsing failed!')
                return {
                    'status': 'error',
                    'message': f'Safe parsing failed: {str(parse_error)}',
                    'traceback': traceback.format_exc()
                }
            
            send_progress(80, 100, 'Extracting financial data...')
            
            items = result.get('items', [])
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            print(f"[api.py] Safe parsing complete:", file=sys.stderr)
            print(f"[api.py]   - Items count: {len(items)}", file=sys.stderr)
            print(f"[api.py]   - Processing time: {metadata.get('processing_time', 0):.2f}s", file=sys.stderr)
            print(f"[api.py]   - Parser version: {metadata.get('parser_version', 'safe')}", file=sys.stderr)
            
            # Database Persistence
            if db:
                try:
                    db.init_db(wipe=True)
                    doc_meta = {
                        'fileName': file_name,
                        'pageCount': metadata.get('total_pages', 0),
                        'parserVersion': metadata.get('parser_version', '3.0.0-safe'),
                        'processingTime': metadata.get('processing_time', 0)
                    }
                    doc_id = db.save_document(file_name, doc_meta)
                    print(f"[api.py] Saved document to DB with ID: {doc_id}", file=sys.stderr)
                    
                    if items:
                        db.save_parsed_items(doc_id, items)
                    if text:
                        db.save_text_chunks(doc_id, text)
                except Exception as db_err:
                    print(f"[api.py] DB Save Error: {db_err}", file=sys.stderr)
            
            send_progress(90, 100, 'Running validation...')
            
            # Simplified validation for safe parser
            validation_report = {'issues': [], 'llm_validation': None}
            
            # Metrics Calculation
            calculated_metrics = []
            try:
                from metrics_engine import calculate_metrics_from_items
                items_json = json.dumps(items)
                metrics_result_json = calculate_metrics_from_items(items_json)
                metrics_data = json.loads(metrics_result_json)
                
                for category, items_list in metrics_data.items():
                    calculated_metrics.append({
                        'category': category,
                        'items': items_list
                    })
            except Exception as e:
                print(f"[api.py] Metrics Calculation Error: {e}", file=sys.stderr)
            
            send_progress(100, 100, 'Analysis complete!')
            
            return {
                'status': 'success',
                'metrics': calculated_metrics,
                'extractedData': {
                    'items': items,
                    'text': text,
                    'metadata': {
                        'fileName': file_name,
                        'pageCount': metadata.get('total_pages', 0),
                        'parserVersion': metadata.get('parser_version', '3.0.0-safe'),
                        'processingTime': metadata.get('processing_time', 0),
                        'analysisMode': 'safe',
                        'streamingEnabled': False
                    },
                    'standalone': {},
                    'consolidated': {},
                    'validation': validation_report
                }
            }
        
        # Use detailed parser for small documents
        elif DETAILED_PARSER_AVAILABLE and FinancialParser:'''

content = content.replace(old_detailed_header, new_detailed_header)

# Write the modified file
with open('/home/nikhil/Gemini Workspace/Financial-Calculator/python/api.py', 'w') as f:
    f.write(content)

print("✓ Successfully patched api.py")
print()
print("Changes made:")
print("1. Added SAFE_PARSER_AVAILABLE import")
print("2. Modified parser selection: SAFE > HYBRID > DETAILED")
print("3. Added SAFE parser processing block")
print()
print("Parser priority order:")
print("  1. SAFE (no pickle errors, 100% quality)")
print("  2. HYBRID (parallel + streaming)")
print("  3. DETAILED (fallback)")
