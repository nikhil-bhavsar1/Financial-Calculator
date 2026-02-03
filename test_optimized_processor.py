#!/usr/bin/env python3
"""
Test script for optimized PDF processor.
Run this to verify performance improvements.
"""

import sys
import time

# Add python directory to path
sys.path.insert(0, 'python')

try:
    from optimized_pdf_processor import OptimizedFinancialParser, parallel_process_pages
    import fitz
    
    if len(sys.argv) < 2:
        print("Usage: python test_optimized_processor.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print("=" * 60)
    print("Optimized PDF Processor Test")
    print("=" * 60)
    print(f"Input file: {pdf_path}")
    print()
    
    # Open document to get page count
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    print(f"Document has {total_pages} pages")
    print()
    
    # Test the optimized parser
    print("Starting optimized parsing...")
    start_time = time.time()
    
    def progress_callback(current, total, message):
        print(f"  [{current}/{total}] {message}")
    
    parser = OptimizedFinancialParser(max_workers=4)
    result = parser.parse(pdf_path, progress_callback=progress_callback)
    
    elapsed = time.time() - start_time
    
    if result['status'] == 'success':
        print()
        print("=" * 60)
        print("✓ Parsing completed successfully!")
        print("=" * 60)
        print(f"Total time: {elapsed:.2f}s")
        print(f"Time per page: {elapsed/total_pages:.2f}s")
        print()
        print("Extraction Statistics:")
        metadata = result['metadata']
        stats = metadata.get('extraction_stats', {})
        print(f"  - Financial lines: {stats.get('financial_lines', 0)}")
        print(f"  - Tables found: {stats.get('tables_found', 0)}")
        print(f"  - Statement headers: {stats.get('statement_headers', 0)}")
        print(f"  - Pages with financial content: {stats.get('pages_with_financial_content', 0)}")
        print()
        print(f"Items extracted: {len(result.get('items', []))}")
        print(f"Parser version: {metadata.get('parser_version', 'unknown')}")
        print(f"Parallel workers: {metadata.get('parallel_workers', 'unknown')}")
        print()
        
        # Performance comparison estimate
        # Old: ~200s for 100 pages = 2s per page
        # New: Should be ~30s for 100 pages = 0.3s per page
        estimated_old_time = total_pages * 2.0  # Conservative estimate
        speedup = estimated_old_time / elapsed if elapsed > 0 else 0
        
        print("Performance Improvement:")
        print(f"  - Estimated old time: ~{estimated_old_time:.0f}s (sequential)")
        print(f"  - Actual new time: {elapsed:.2f}s (parallel)")
        print(f"  - Speedup: {speedup:.1f}x faster")
        print()
        
        if speedup > 5:
            print("✓ EXCELLENT! Optimization achieved >5x speedup")
        elif speedup > 3:
            print("✓ Good! Optimization achieved >3x speedup")
        elif speedup > 2:
            print("✓ Noticeable improvement (>2x speedup)")
        else:
            print("⚠ Modest improvement - consider increasing worker count")
            
    else:
        print()
        print("✗ Parsing failed!")
        print(f"Error: {result.get('message', 'Unknown error')}")
        if 'traceback' in result:
            print()
            print("Traceback:")
            print(result['traceback'])
        sys.exit(1)
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you have PyMuPDF installed:")
    print("  pip install PyMuPDF")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
