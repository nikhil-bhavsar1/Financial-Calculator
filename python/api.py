import sys
import json
import os
import io
import base64
import traceback
import time

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try imports
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Try to import parsers
try:
    from parsers import FinancialParser
    DETAILED_PARSER_AVAILABLE = True
except ImportError as e:
    FinancialParser = None
    DETAILED_PARSER_AVAILABLE = False
    print(f"[api.py] Detailed parser import error: {e}", file=sys.stderr)

# Try to import XBRL parser
try:
    from xbrl_parser import XBRLParser
    XBRL_PARSER_AVAILABLE = True
except ImportError as e:
    XBRLParser = None
    XBRL_PARSER_AVAILABLE = False
    print(f"[api.py] XBRL parser import error: {e}", file=sys.stderr)

# Try hybrid processor (parallel extraction + sequential quality + streaming)
# Hybrid parser DISABLED due to pickle errors with PyMuPDF/SWIG
# try:
#     from hybrid_pdf_processor import HybridFinancialParser
#     HYBRID_PARSER_AVAILABLE = True
# except ImportError as e:
#     HybridFinancialParser = None
#     HYBRID_PARSER_AVAILABLE = False
#     print(f"[api.py] Hybrid parser not available: {e}", file=sys.stderr)
HYBRID_PARSER_AVAILABLE = False

try:
    from database import db
except ImportError:
    db = None
    print("[api.py] Database module not found", file=sys.stderr)

# Progress callback that supports streaming
def send_progress(current_page, total_pages, status_message=""):
    percentage = int((current_page / total_pages) * 100) if total_pages > 0 else 0
    progress_data = {
        'status': 'progress',
        'currentPage': current_page,
        'totalPages': total_pages,
        'percentage': percentage,
        'message': status_message or f'Processing page {current_page} of {total_pages}'
    }
    print(json.dumps(progress_data))
    sys.stdout.flush()

def send_stream_item(item_data):
    """Send individual item to frontend as it's extracted."""
    stream_data = {
        'status': 'item_stream',
        'item': item_data
    }
    print(json.dumps(stream_data))
    sys.stdout.flush()

def handle_calculate_metrics(req):
    """Handle metrics calculation from parsed items."""
    try:
        from metrics_engine import calculate_metrics_from_items

        items_json = req.get('items_json')

        if not items_json:
            return {'status': 'error', 'message': 'No items provided'}

        print(f"[api.py] Calculating metrics from parsed items", file=sys.stderr)
        metrics_result_json = calculate_metrics_from_items(items_json)
        metrics_data = json.loads(metrics_result_json)
        
        # Convert from engine format (category keys) to list format for frontend
        categorized_metrics = []
        for category, items_list in metrics_data.items():
            categorized_metrics.append({
                'category': category,
                'items': items_list
            })

        return {
            'status': 'success',
            'metrics': categorized_metrics
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Metrics calculation error: {str(e)}',
            'traceback': traceback.format_exc()
        }

def handle_xbrl_parse(filepath: str, file_name: str):
    """Handle XBRL/iXBRL file parsing."""
    try:
        if not XBRL_PARSER_AVAILABLE:
            return {
                'status': 'error',
                'message': 'XBRL parser not available. Please check installation.'
            }

        print(f"[api.py] Parsing XBRL file: {file_name}", file=sys.stderr)
        send_progress(10, 100, 'Initializing XBRL parser...')

        parser = XBRLParser()
        doc = parser.parse(filepath)

        send_progress(50, 100, 'Extracting XBRL facts...')

        # Map to canonical metrics
        metrics_by_period = parser.extract_metrics(filepath)

        # Convert to FinancialItem format
        items = []
        all_text_parts = []

        # Extract text content from document
        if doc.facts:
            for fact in doc.facts[:100]:  # Limit to first 100 facts for text extraction
                all_text_parts.append(f"{fact.concept}: {fact.value}")

        text = "\n".join(all_text_parts)

        # Convert metrics to FinancialItem format
        for period_label, period_metrics in metrics_by_period.items():
            for metric_key, value in period_metrics.items():
                items.append({
                    'id': metric_key,
                    'name': metric_key.replace('_', ' ').title(),
                    'current_year': value,
                    'previous_year': None,
                    'all_years': {period_label: value},
                    'sourcePage': 'XBRL',
                    'category': 'Financial'
                })

        send_progress(90, 100, 'Calculating metrics...')

        # Calculate metrics from extracted items
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

        send_progress(100, 100, 'XBRL analysis complete!')

        return {
            'status': 'success',
            'metrics': calculated_metrics,
            'extractedData': {
                'items': items,
                'text': text,
                'metadata': {
                    'fileName': file_name,
                    'companyName': doc.company_name,
                    'taxonomy': doc.taxonomy,
                    'filingDate': doc.filing_date,
                    'factsCount': len(doc.facts),
                    'pageCount': 0,
                    'parserVersion': '1.0.0-xbrl',
                    'analysisMode': 'xbrl',
                    'streamingEnabled': False
                },
                'standalone': {},
                'consolidated': {},
                'validation': {'issues': []}
            }
        }
    except Exception as e:
        print(f"[api.py] XBRL Parsing Error: {e}", file=sys.stderr)
        traceback.print_exc()
        return {
            'status': 'error',
            'message': f'XBRL Parsing Error: {str(e)}',
            'traceback': traceback.format_exc()
        }

def process_request(line):
    try:
        if not line.strip():
            return None
        req = json.loads(line)
        cmd = req.get('command')

        if cmd == 'parse':
            return handle_parse(req)
        elif cmd == 'rag_search':
            return handle_rag(req)
        elif cmd == 'update_mapping':
            return {'status': 'success', 'message': 'Mappings updated (mock)'}
        elif cmd == 'calculate_metrics':
            return handle_calculate_metrics(req)
        elif cmd == 'get_db_data':
            return handle_get_db_data(req)
        else:
            return {'status': 'error', 'message': f'Unknown command {cmd}'}
    except json.JSONDecodeError:
        return {'status': 'error', 'message': 'Invalid JSON input'}
    except Exception as e:
        return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

def handle_parse(req):
    file_path = req.get('file_path')
    content_b64 = req.get('content')
    file_name = req.get('file_name', 'document')
    use_streaming = req.get('streaming', True)  # Default to streaming

    # Determine actual file path
    actual_path = None
    temp_file = None

    # Determine file extension
    file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''

    if content_b64:
        # Decode base64 and save to temp file for parser
        try:
            import tempfile
            data = base64.b64decode(content_b64)
            # Use appropriate suffix based on file type
            suffix = f'.{file_ext}' if file_ext in ['xml', 'xbrl', 'pdf', 'txt'] else '.pdf'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(data)
            temp_file.close()
            actual_path = temp_file.name
        except Exception as e:
            return {'status': 'error', 'message': f'Base64 Decode Error: {str(e)}'}
    elif file_path and os.path.exists(file_path):
        actual_path = file_path
    else:
        return {'status': 'error', 'message': 'File not found or no content provided'}

    try:
        # Check if this is an XBRL/XML file
        if file_ext in ['xml', 'xbrl'] or (actual_path and (actual_path.lower().endswith('.xml') or actual_path.lower().endswith('.xbrl'))):
            return handle_xbrl_parse(actual_path, file_name)

        # Determine document size for PDF files
        import fitz
        doc = fitz.open(actual_path)
        total_pages = len(doc)
        doc.close()

        # Choose parser based on document size and availability
        # Small docs (≤5 pages): Use detailed parser for maximum quality
        # Large docs (>5 pages): Use hybrid parser (parallel + quality + streaming)
        use_hybrid = (HYBRID_PARSER_AVAILABLE and 
                     (actual_path.lower().endswith('.pdf') or actual_path.lower().endswith('.PDF')) and 
                     total_pages > 5)

        if use_hybrid:
            # HYBRID APPROACH: Parallel extraction + Sequential quality + Streaming
            print(f"[api.py] Using HybridFinancialParser for: {file_name} ({total_pages} pages) with STREAMING", file=sys.stderr)
            
            parser = HybridFinancialParser(max_workers=8)  # Use 8 workers for parallel extraction
            
            # Collect all items and full text
            all_items = []
            all_text_parts = []
            
            # Define streaming callback to send items as they're analyzed
            def stream_callback(page_data):
                """Send page results as they're available"""
                page_num = page_data.get('page_num', 0)
                items = page_data.get('items', [])
                
                print(f"[api.py] Page {page_num + 1}: {len(items)} items, quality={page_data.get('quality_score', 0):.1f}", file=sys.stderr)
                
                # Stream each item immediately
                for item in items:
                    item['stream_page_num'] = page_num + 1
                    item['stream_quality'] = page_data.get('quality_score', 0)
                    send_stream_item(item)
                    all_items.append(item)
            
            # Define progress callback wrapper
            def progress_wrapper(current, total, message):
                # Map page progress to 0-100 scale
                progress = int((current / total) * 90)  # 90% for parsing
                send_progress(progress, 100, f'{message} ({current}/{total} pages)')
            
            # Parse with hybrid approach
            start_time = time.time()
            try:
                result = parser.parse(
                    actual_path,
                    progress_callback=progress_wrapper,
                    stream_callback=stream_callback
                )
            except Exception as parse_error:
                print(f"[api.py] Hybrid parse error: {parse_error}", file=sys.stderr)
                traceback.print_exc()
                send_progress(0, 100, 'Parsing failed!')
                return {
                    'status': 'error',
                    'message': f'Hybrid parsing failed: {str(parse_error)}',
                    'traceback': traceback.format_exc()
                }
            
            if result['status'] != 'success':
                return result
            
            # Get data from result
            items = result.get('items', all_items)  # Use collected items if not in result
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            print(f"[api.py] Hybrid parsing complete:", file=sys.stderr)
            print(f"[api.py]   - Items count: {len(items)}", file=sys.stderr)
            print(f"[api.py]   - Processing time: {metadata.get('processing_time', 0):.2f}s", file=sys.stderr)
            print(f"[api.py]   - Extraction time: {metadata.get('extraction_time', 0):.2f}s", file=sys.stderr)
            print(f"[api.py]   - Avg quality: {metadata.get('avg_quality_score', 0):.1f}/20", file=sys.stderr)
            print(f"[api.py]   - Analysis mode: {metadata.get('analysis_mode', 'unknown')}", file=sys.stderr)
            
            # Database Persistence (batch save after streaming is complete)
            if db:
                try:
                    # Wipe previous session data for new analysis
                    db.init_db(wipe=True)
                    
                    # Save Document
                    doc_meta = {
                        'fileName': file_name,
                        'pageCount': metadata.get('total_pages', 0),
                        'parserVersion': metadata.get('parser_version', '3.0.0-hybrid-streaming'),
                        'processingTime': metadata.get('processing_time', 0),
                        'extractionTime': metadata.get('extraction_time', 0),
                        'avgQualityScore': metadata.get('avg_quality_score', 0)
                    }
                    doc_id = db.save_document(file_name, doc_meta)
                    print(f"[api.py] Saved document to DB with ID: {doc_id}", file=sys.stderr)
                    
                    # Save Items
                    if items:
                        db.save_parsed_items(doc_id, items)
                    
                    # Save Text Chunks (RAG)
                    if text:
                        db.save_text_chunks(doc_id, text)
                    
                except Exception as db_err:
                    print(f"[api.py] DB Save Error: {db_err}", file=sys.stderr)
            
            # Send progress for metrics calculation
            send_progress(92, 100, 'Calculating metrics...')
            
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
            
            # Send final completion
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
                        'parserVersion': metadata.get('parser_version', '3.0.0-hybrid-streaming'),
                        'processingTime': metadata.get('processing_time', 0),
                        'extractionTime': metadata.get('extraction_time', 0),
                        'avgQualityScore': metadata.get('avg_quality_score', 0),
                        'analysisMode': 'hybrid_streaming',
                        'streamingEnabled': True
                    },
                    'standalone': {},
                    'consolidated': {},
                    'validation': {'issues': []}
                }
            }
        
        # Use detailed parser for small documents (≤5 pages)
        elif DETAILED_PARSER_AVAILABLE and FinancialParser:
            print(f"[api.py] Using Detailed FinancialParser for: {file_name} ({total_pages} pages)", file=sys.stderr)
            parser = FinancialParser()

            # Send initial progress
            send_progress(5, 100, 'Initializing detailed parser...')

            # Parse document with error handling
            try:
                result = parser.parse(actual_path)
                send_progress(50, 100, 'Parsing complete, processing data...')
            except Exception as parse_error:
                print(f"[api.py] Parse error: {parse_error}", file=sys.stderr)
                send_progress(0, 100, 'Parsing failed!')
                return {
                    'status': 'error',
                    'message': f'Parsing failed: {str(parse_error)}',
                    'traceback': traceback.format_exc()
                }

            # Send completion progress
            send_progress(80, 100, 'Extracting financial data...')

            # Convert to frontend-expected format
            items = result.get('items', [])
            text = result.get('text', '')
            metadata = result.get('metadata', {})

            # Debug logging to see what we got
            print(f"[api.py] Detailed parsing complete:", file=sys.stderr)
            print(f"[api.py]   - Items count: {len(items)}", file=sys.stderr)
            print(f"[api.py]   - Text length: {len(text)}", file=sys.stderr)
            print(f"[api.py]   - Parser version: {metadata.get('parser_version', 'unknown')}", file=sys.stderr)

                # Database Persistence
            if db:
                try:
                    # Wipe previous session data for new analysis
                    db.init_db(wipe=True)

                    # Save Document
                    doc_meta = {
                        'fileName': file_name,
                        'pageCount': metadata.get('total_pages', 0),
                        'parserVersion': metadata.get('parser_version', '2.0.0')
                    }
                    doc_id = db.save_document(file_name, doc_meta)
                    print(f"[api.py] Saved document to DB with ID: {doc_id}", file=sys.stderr)

                # Save Items
                    if items:
                        db.save_parsed_items(doc_id, items)

                        # Phase 6: Extraction Checklist
                        try:
                            from metrics_coverage import MetricsCoverageEngine
                            coverage_engine = MetricsCoverageEngine()
                            checklist_results = coverage_engine.analyze_coverage(items, text)
                            db.save_extraction_checklist(doc_id, checklist_results)

                            # Add summary to metadata for immediate feedback
                            coverage_summary = coverage_engine.get_summary(checklist_results)
                            metadata['extraction_coverage'] = coverage_summary
                        except Exception as cov_err:
                            print(f"[api.py] Coverage Analysis Error: {cov_err}", file=sys.stderr)

                    # Save Text Chunks (RAG)
                    if text:
                        db.save_text_chunks(doc_id, text)

                except Exception as db_err:
                    print(f"[api.py] DB Save Error: {db_err}", file=sys.stderr)

            # Send final progress before validation
            send_progress(90, 100, 'Running validation...')

            # -----------------------------------------------------------------
            # PHASE 3 & 4: POST-PROCESSING VALIDATION
            # -----------------------------------------------------------------
            validation_report = {
                'issues': [],
                'llm_validation': None
            }

            # 1. GAAP Validation
            try:
                from gaap_rules import GAAPValidator, detect_gaap_type

                # Detect GAAP from full text
                gaap_type, conf = detect_gaap_type(text)

                # Convert items list to metrics dict for validator
                metrics_map = {item.id: item.current_year for item in items if hasattr(item, 'current_year') and item.current_year is not None}

                validator = GAAPValidator(gaap_type)
                issues = validator.validate(metrics_map, text)

                validation_report['issues'] = [i.__dict__ for i in issues]
                validation_report['gaap_type'] = gaap_type.value
            except ImportError:
                print("[api.py] GAAP Validator not found", file=sys.stderr)
            except Exception as e:
                print(f"[api.py] GAAP Validation Error: {e}", file=sys.stderr)

            # 2. LLM Validation
            try:
                from llm_validator import LLMValidator
                llm = LLMValidator()
                if llm.is_available():
                    metrics_map = {item.id: item.current_year for item in items if hasattr(item, 'current_year') and item.current_year is not None}
                    llm_result = llm.validate_metrics(metrics_map)
                    validation_report['llm_validation'] = llm_result.__dict__
            except ImportError:
                print("[api.py] LLM Validator not found", file=sys.stderr)
            except Exception as e:
                print(f"[api.py] LLM Validation Error: {e}", file=sys.stderr)

            # 3. Metrics Calculation
            calculated_metrics = []
            try:
                from metrics_engine import calculate_metrics_from_items
                # Items need to be in JSON format for current engine implementation
                items_json = json.dumps(items)
                metrics_result_json = calculate_metrics_from_items(items_json)
                metrics_data = json.loads(metrics_result_json)
                
                # Convert from engine format (category keys) to list format for frontend
                for category, items_list in metrics_data.items():
                    calculated_metrics.append({
                        'category': category,
                        'items': items_list
                    })
            except Exception as e:
                print(f"[api.py] Metrics Calculation Error: {e}", file=sys.stderr)
                traceback.print_exc()

            # Send final completion
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
                        'parserVersion': metadata.get('parser_version', '2.0.0'),
                        'analysisMode': 'detailed_sequential',
                        'streamingEnabled': False
                    },
                    'standalone': result.get('standalone', {}),
                    'consolidated': result.get('consolidated', {}),
                    'validation': validation_report
                }
            }

        # Fallback to basic pdfplumber extraction
        elif pdfplumber:
            print(f"[api.py] Fallback: using pdfplumber for: {file_name}", file=sys.stderr)
            return _fallback_parse(actual_path, file_name)

        else:
            return {'status': 'error', 'message': 'No parser available. Install PyMuPDF or pdfplumber.'}

    except Exception as e:
        return {
            'status': 'error',
            'message': f'PDF Processing Error: {str(e)}',
            'traceback': traceback.format_exc()
        }
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

def handle_rag(req):
    """Handle RAG search request using Ollama."""
    query = req.get('query')
    doc_id = req.get('docId') # Client should send docId if context needed

    if not query:
         return {'status': 'error', 'message': 'Query required'}

    # 1. Retrieve Context
    context = ""
    if db and doc_id:
        try:
             # Try to find recent document if docId not provided
             context = db.get_rag_context(doc_id, query)
        except Exception as e:
             print(f"[api.py] Context retrieval error: {e}", file=sys.stderr)

    # 2. Generate Response
    try:
        from llm_validator import OllamaClient
        client = OllamaClient()

        if not client.is_available():
             return {
                 'status': 'success',
                 'results': [{'text': "Ollama service unavailable. Please start Ollama.", 'score': 0}]
             }

        system_prompt = "You are a financial analyst assistant. Use the provided context to answer the user's question. If the answer is not in the context, say so."
        prompt = f"""Context:
 {context}

Question: {query}

Answer:"""

        response_text = client.generate(prompt, system_prompt)

        return {
            'status': 'success',
            'results': [
                {'page': 1, 'text': response_text, 'score': 1.0, 'context_used': bool(context)}
            ]
        }
    except Exception as e:
        return {'status': 'error', 'message': f"LLM Generation Error: {e}"}

def handle_get_db_data(req):
    """Handle get_db_data command."""
    try:
        from database import db
        if db:
            data = db.get_all_data()
            return {'status': 'success', 'data': data}
        else:
            return {'status': 'error', 'message': 'Database not initialized'}
    except ImportError:
        return {'status': 'error', 'message': 'Database module not available'}
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to get DB data: {str(e)}'}

def _fallback_parse(pdf_path: str, file_name: str):
    """Fallback PDF parsing using pdfplumber when FinancialParser is unavailable."""
    print(f"[api.py] Using pdfplumber fallback", file=sys.stderr)

    all_text = ""
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)  # Fix: use len(pdf.pages) instead of len(pdf)
            send_progress(1, total_pages, 'Extracting text...')

            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                all_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
                pages.append({
                    'pageNumber': page_num + 1,
                    'content': text
                })

                # Send progress for every page
                send_progress(page_num + 1, total_pages, f'Extracting page {page_num + 1} of {total_pages}')

        send_progress(total_pages, total_pages, 'Text extraction complete!')

        return {
            'status': 'success',
            'extractedData': {
                'items': [],
                'text': all_text,
                'pages': pages,
                'metadata': {
                    'fileName': file_name,
                    'pageCount': total_pages,
                    'parser': 'pdfplumber',
                    'analysisMode': 'fallback',
                    'streamingEnabled': False
                }
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'PDF parsing failed: {str(e)}',
            'traceback': traceback.format_exc()
        }

def main():
    # Process single request and exit (one-shot mode)
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = process_request(line)
            if response:
                print(json.dumps(response))
                sys.stdout.flush()
                break
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {'status': 'error', 'message': f'Fatal error: {str(e)}'}
        print(json.dumps(error_response))
        sys.stdout.flush()
        sys.exit(1)

if __name__ == '__main__':
    main()
