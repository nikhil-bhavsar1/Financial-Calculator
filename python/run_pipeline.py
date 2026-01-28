
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import argparse

# Local imports
from parser_config import ParserConfig
from parsers import FinancialParser

# =============================================================================
# Convenience Functions
# =============================================================================

def parse_annual_report(
    pdf_path: str,
    use_ocr: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Parse an NSE/BSE annual report PDF.
    
    Args:
        pdf_path: Path to the PDF file
        use_ocr: Enable OCR for scanned pages
        validate: Validate the output
        
    Returns:
        Parsed financial data dictionary
    """
    config = ParserConfig(use_ocr=use_ocr, validate_output=validate)
    parser = FinancialParser(config)
    return parser.parse(pdf_path, 'pdf')


def parse_file(
    file_path: str,
    file_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Parse any supported file type.
    
    Args:
        file_path: Path to the file
        file_type: File type (auto-detected if None)
        **kwargs: Additional config options
        
    Returns:
        Parsed financial data dictionary
    """
    config = ParserConfig(**kwargs)
    parser = FinancialParser(config)
    return parser.parse(file_path, file_type)


def get_standalone_statements(pdf_path: str) -> Dict[str, Any]:
    """Extract only standalone financial statements."""
    result = parse_annual_report(pdf_path)
    return result.get("standalone", {})


def get_consolidated_statements(pdf_path: str) -> Dict[str, Any]:
    """Extract only consolidated financial statements."""
    result = parse_annual_report(pdf_path)
    return result.get("consolidated", {})


def compare_statements(
    pdf_path: str,
    entity1: str = "standalone",
    entity2: str = "consolidated"
) -> Dict[str, Any]:
    """
    Compare two entity statements (e.g., standalone vs consolidated).
    
    Args:
        pdf_path: Path to PDF
        entity1: First entity type
        entity2: Second entity type
        
    Returns:
        Comparison dictionary
    """
    result = parse_annual_report(pdf_path)
    
    comparison = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": [],
    }
    
    for stmt_type in comparison.keys():
        items1 = {
            item.get("label", "").lower(): item
            for item in result.get(entity1, {}).get(stmt_type, {}).get("items", [])
        }
        items2 = {
            item.get("label", "").lower(): item
            for item in result.get(entity2, {}).get(stmt_type, {}).get("items", [])
        }
        
        all_labels = set(items1.keys()) | set(items2.keys())
        
        for label in sorted(all_labels):
            item1 = items1.get(label, {})
            item2 = items2.get(label, {})
            
            if item1 or item2:
                comparison[stmt_type].append({
                    "label": item1.get("label") or item2.get("label"),
                    entity1: {
                        "currentYear": item1.get("currentYear", 0),
                        "previousYear": item1.get("previousYear", 0),
                    },
                    entity2: {
                        "currentYear": item2.get("currentYear", 0),
                        "previousYear": item2.get("previousYear", 0),
                    },
                    "difference": {
                        "currentYear": (
                            item2.get("currentYear", 0) - item1.get("currentYear", 0)
                        ),
                        "previousYear": (
                            item2.get("previousYear", 0) - item1.get("previousYear", 0)
                        ),
                    }
                })
    
    return comparison


def batch_parse(
    file_paths: List[str],
    output_dir: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Parse multiple files in batch.
    
    Args:
        file_paths: List of file paths
        output_dir: Optional directory to save JSON outputs
        **kwargs: Additional config options
        
    Returns:
        List of results (or summary if output_dir is provided)
    """
    config = ParserConfig(**kwargs)
    parser = FinancialParser(config)
    
    results = []
    
    for file_path in file_paths:
        try:
            result = parser.parse(file_path)
            result['_source_file'] = file_path
            result['_status'] = 'success'
            
            if output_dir:
                output_path = Path(output_dir) / f"{Path(file_path).stem}_parsed.json"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                result = {
                    'file': file_path,
                    'output': str(output_path),
                    'status': 'success',
                    'items_count': len(result.get('items', []))
                }
            
            results.append(result)
            
        except Exception as e:
            results.append({
                'file': file_path,
                'status': 'error',
                'error': str(e)
            })
    
    return results


# =============================================================================
# CLI
# =============================================================================

def print_statement_summary(name: str, data: Dict):
    """Print formatted statement summary."""
    items = data.get("items", [])
    pages = data.get("pages", [])
    title = data.get("title", "")
    
    if not items:
        print("    ⚠️  Not found")
        return
    
    print(f"    📄 Pages: {pages}")
    if title:
        print(f"    📋 Title: {title[:60]}{'...' if len(title) > 60 else ''}")
    print(f"    📊 Items: {len(items)}")
    
    # Show key totals
    print("    📈 Key Items:")
    for item in items:
        if item.get("isImportant") or item.get("isTotal"):
            label = item.get("label", "")[:40]
            curr = item.get("currentYear", 0)
            prev = item.get("previousYear", 0)
            var_pct = item.get("variationPercent", 0)
            
            if var_pct is None:
                var_str = "N/A"
            elif var_pct > 0:
                var_str = f"+{var_pct:.1f}%"
            else:
                var_str = f"{var_pct:.1f}%"
            
            print(f"       • {label:<40} {curr:>15,.2f} {prev:>15,.2f} {var_str:>10}")


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced Financial Statement Parser for NSE/BSE Annual Reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python parser.py report.pdf
  python parser.py report.pdf --json
  python parser.py report.pdf --ocr --force-ocr
  python parser.py report.pdf --compare
  python parser.py *.pdf --batch --output ./parsed
        """
    )
    
    parser.add_argument('files', nargs='+', help='Input file(s)')
    parser.add_argument('-t', '--type', choices=['pdf', 'xlsx', 'csv', 'xbrl'],
                       help='File type (auto-detected if not specified)')
    parser.add_argument('-o', '--output', help='Output directory for JSON files')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output full JSON result')
    parser.add_argument('--ocr', action='store_true', default=True,
                       help='Enable OCR (default: enabled)')
    parser.add_argument('--no-ocr', action='store_true',
                       help='Disable OCR')
    parser.add_argument('--force-ocr', action='store_true',
                       help='Force OCR on all pages')
    parser.add_argument('--ocr-engine', choices=['tesseract', 'easyocr'],
                       default='tesseract', help='OCR engine to use')
    parser.add_argument('--compare', '-c', action='store_true',
                       help='Compare standalone vs consolidated')
    parser.add_argument('--validate', '-v', action='store_true', default=True,
                       help='Validate output (default: enabled)')
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Batch processing mode')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet mode (minimal output)')
    
    args = parser.parse_args()
    
    # Build config
    use_ocr = not args.no_ocr
    config = ParserConfig(
        use_ocr=use_ocr,
        ocr_engine=args.ocr_engine,
        force_ocr=args.force_ocr,
        validate_output=args.validate
    )
    
    # Batch mode
    if args.batch or len(args.files) > 1:
        results = batch_parse(args.files, args.output, **config.to_dict())
        
        print(f"\n{'='*80}")
        print("📦 BATCH PROCESSING RESULTS")
        print(f"{'='*80}")
        
        success = sum(1 for r in results if r.get('status') == 'success')
        failed = len(results) - success
        
        print(f"\n  ✅ Successful: {success}")
        print(f"  ❌ Failed: {failed}")
        
        if not args.quiet:
            for result in results:
                status = "✅" if result.get('status') == 'success' else "❌"
                file_name = Path(result.get('file', '')).name
                items = result.get('items_count', 'N/A')
                print(f"  {status} {file_name}: {items} items")
        
        return
    
    # Single file mode
    file_path = args.files[0]
    
    if not args.quiet:
        print(f"\n{'='*80}")
        print(f"📄 FINANCIAL STATEMENT PARSER v2.0")
        print(f"{'='*80}")
        print(f"File: {file_path}")
        print(f"OCR: {'Enabled' if use_ocr else 'Disabled'} ({args.ocr_engine})")
        print(f"{'='*80}\n")
    
    # Parse
    fp = FinancialParser(config)
    result = fp.parse(file_path, args.type)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    if args.output:
        output_path = Path(args.output)
        if output_path.is_dir():
            output_path = output_path / f"{Path(file_path).stem}_parsed.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Output saved to: {output_path}")
        return
    
    metadata = result.get("metadata", {})
    
    # Print summary
    print("📊 DOCUMENT OVERVIEW")
    print(f"  Total Pages: {metadata.get('totalPages', 'N/A')}")
    print(f"  Has Standalone: {'✅' if metadata.get('hasStandalone') else '❌'}")
    print(f"  Has Consolidated: {'✅' if metadata.get('hasConsolidated') else '❌'}")
    
    # Year labels
    year_labels = metadata.get("yearLabels", {})
    print(f"\n📅 YEAR LABELS")
    for entity in ["standalone", "consolidated"]:
        labels = year_labels.get(entity, {})
        curr = labels.get("current", "N/A")
        prev = labels.get("previous", "N/A")
        print(f"  {entity.title()}: {curr} / {prev}")
    
    # OCR info
    ocr_info = metadata.get("ocr", {})
    if ocr_info:
        print(f"\n🔍 OCR PROCESSING")
        print(f"  Engine: {ocr_info.get('engine', 'N/A')}")
        print(f"  Pages OCR'd: {ocr_info.get('ocr_successes', 0)}")
        print(f"  Cache Hits: {ocr_info.get('cache_hits', 0)}")
    
    # Statements
    for entity in ["standalone", "consolidated"]:
        entity_data = result.get(entity, {})
        has_data = any(
            entity_data.get(st, {}).get("items")
            for st in ["balance_sheet", "income_statement", "cash_flow"]
        )
        
        if has_data:
            print(f"\n{'─'*80}")
            print(f"📑 {entity.upper()} FINANCIAL STATEMENTS")
            print(f"{'─'*80}")
            
            for stmt_name in ["balance_sheet", "income_statement", "cash_flow"]:
                print(f"\n  {stmt_name.replace('_', ' ').upper()}:")
                print_statement_summary(stmt_name, entity_data.get(stmt_name, {}))
    
    # Summary
    all_items = result.get("items", [])
    print(f"\n{'─'*80}")
    print("📈 SUMMARY")
    print(f"{'─'*80}")
    print(f"  Total Line Items: {len(all_items)}")
    
    standalone_count = sum(1 for i in all_items if i.get("reportingEntity") == "standalone")
    consolidated_count = sum(1 for i in all_items if i.get("reportingEntity") == "consolidated")
    print(f"  Standalone Items: {standalone_count}")
    print(f"  Consolidated Items: {consolidated_count}")
    
    # Validation
    validation = metadata.get("validation", {})
    if validation:
        issues = validation.get("issues", [])
        if issues:
            print(f"\n⚠️  VALIDATION ISSUES ({len(issues)}):")
            for issue in issues[:5]:
                severity = issue.get("severity", "info").upper()
                message = issue.get("message", "")
                print(f"    [{severity}] {message}")
            if len(issues) > 5:
                print(f"    ... and {len(issues) - 5} more")
    
    # Compare mode
    if args.compare:
        print(f"\n{'='*80}")
        print("🔄 STANDALONE vs CONSOLIDATED COMPARISON")
        print(f"{'='*80}")
        
        comparison = compare_statements(file_path)
        
        for stmt_type, items in comparison.items():
            if items:
                print(f"\n{stmt_type.replace('_', ' ').upper()}:")
                print(f"{'Label':<40} {'Standalone':>15} {'Consolidated':>15} {'Difference':>15}")
                print("-" * 90)
                
                for item in items[:15]:
                    label = item.get("label", "")[:38]
                    s_curr = item.get("standalone", {}).get("currentYear", 0)
                    c_curr = item.get("consolidated", {}).get("currentYear", 0)
                    diff = item.get("difference", {}).get("currentYear", 0)
                    
                    if s_curr != 0 or c_curr != 0:
                        print(f"{label:<40} {s_curr:>15,.2f} {c_curr:>15,.2f} {diff:>15,.2f}")


if __name__ == "__main__":
    main()
