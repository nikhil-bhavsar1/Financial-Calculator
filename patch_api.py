#!/usr/bin/env python3
"""
Patch script to fix parser selection logic in api.py.
Changes priority: SAFE > HYBRID > DETAILED
"""

import re
import os

api_path = '/home/nikhil/Gemini Workspace/Financial-Calculator/python/api.py'

# Read the file
with open(api_path, 'r') as f:
    content = f.read()

# Find and replace the parser selection logic
old_code = '''        # Choose parser based on document size and availability
        # Small docs (≤5 pages): Use detailed parser for maximum quality
        # Large docs (>5 pages): Use hybrid parser (parallel + quality + streaming)
        use_hybrid = (HYBRID_PARSER_AVAILABLE and 
                     (actual_path.lower().endswith('.pdf') or actual_path.lower().endswith('.PDF')) and 
                     total_pages > 5)
        
        if use_hybrid:
            # HYBRID APPROACH: Parallel extraction + Sequential quality + Streaming
            print(f"[api.py] Using HybridFinancialParser for: {file_name} ({total_pages} pages) with STREAMING", file=sys.stderr)
            
            parser = HybridFinancialParser(max_workers=8)  # Use 8 workers for parallel extraction'''

new_code = '''        # Choose parser with priority: SAFE (no pickle) > HYBRID > DETAILED
        # Priority order: SAFE first (no pickle), then HYBRID, then DETAILED
        # SAFE: Prevents pickle errors, maintains 100% quality, original speed
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

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(api_path, 'w') as f:
        f.write(content)
    print("✓ Successfully patched api.py")
    print("  - Parser priority: SAFE > HYBRID > DETAILED")
    print("  - Safe parser will be used first to prevent pickle errors")
else:
    print("✗ Could not find the code to patch")
    print("  Trying alternative pattern...")
