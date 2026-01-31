import sys
import json
import os
import io
import base64

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try imports
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Try to import the full parser
try:
    from parsers import FinancialParser
    PARSER_AVAILABLE = True
except ImportError as e:
    FinancialParser = None
    PARSER_AVAILABLE = False
    print(f"[api.py] Parser import error: {e}", file=sys.stderr)

def send_progress(current_page, total_pages, status_message=""):
    """Send progress update to stdout"""
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
        else:
            return {'status': 'error', 'message': f'Unknown command {cmd}'}
    except json.JSONDecodeError:
        return {'status': 'error', 'message': 'Invalid JSON input'}
    except Exception as e:
        import traceback
        return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

def handle_parse(req):
    file_path = req.get('file_path')
    content_b64 = req.get('content')
    file_name = req.get('file_name', 'document')
    
    # Determine actual file path
    actual_path = None
    temp_file = None
    
    if content_b64:
        # Decode base64 and save to temp file for parser
        try:
            import tempfile
            data = base64.b64decode(content_b64)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
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
        # Use full FinancialParser if available (for proper data extraction)
        if PARSER_AVAILABLE and FinancialParser:
            print(f"[api.py] Using FinancialParser for: {file_name}", file=sys.stderr)
            parser = FinancialParser()
            
            # Send initial progress
            send_progress(0, 100, 'Initializing parser...')
            
            # Parse the document
            result = parser.parse(actual_path)
            
            # Send completion progress
            send_progress(100, 100, 'Analysis complete!')
            
            # Convert to frontend-expected format
            items = result.get('items', [])
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            return {
                'status': 'success',
                'extractedData': {
                    'items': items,
                    'text': text,
                    'metadata': {
                        'fileName': file_name,
                        'pageCount': metadata.get('total_pages', 0),
                        'parserVersion': metadata.get('parser_version', '2.0.0'),
                        'statementsFound': list(result.get('standalone', {}).keys()) + list(result.get('consolidated', {}).keys())
                    },
                    'standalone': result.get('standalone', {}),
                    'consolidated': result.get('consolidated', {})
                }
            }
        
        # Fallback to basic pdfplumber extraction
        elif pdfplumber:
            print(f"[api.py] Fallback: using pdfplumber for: {file_name}", file=sys.stderr)
            return _fallback_parse(actual_path, file_name)
        
        else:
            return {'status': 'error', 'message': 'No parser available. Install PyMuPDF or pdfplumber.'}
    
    except Exception as e:
        import traceback
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

def _fallback_parse(file_path, file_name):
    """Fallback parser using pdfplumber when FinancialParser is unavailable."""
    text_content = ""
    pages_data = []
    
    with pdfplumber.open(file_path) as pdf:
        max_pages = 200
        total_pages = len(pdf.pages)
        pages_to_process = min(total_pages, max_pages)
        
        send_progress(0, pages_to_process, f'Found {total_pages} pages, processing {pages_to_process}...')
        
        for i in range(pages_to_process):
            try:
                page = pdf.pages[i]
                page_text = page.extract_text() or ""
                text_content += f"\n--- Page {i+1} ---\n{page_text}"
                pages_data.append({
                    'pageNumber': i+1,
                    'content': page_text
                })
                
                if (i + 1) % 5 == 0 or i == pages_to_process - 1:
                    send_progress(i + 1, pages_to_process, f'Processing page {i+1} of {pages_to_process}...')
                
            except Exception as page_error:
                pages_data.append({
                    'pageNumber': i+1,
                    'content': f"[Error extracting page: {str(page_error)}]"
                })
        
        send_progress(pages_to_process, pages_to_process, 'Analysis complete!')
    
    return {
        'status': 'success',
        'extractedData': {
            'text': text_content,
            'pages': pages_data,
            'items': [],  # Fallback does not extract structured items
            'metadata': {
                'fileName': file_name,
                'pageCount': len(pages_data),
                'totalPagesInFile': total_pages,
                'parserMode': 'fallback_pdfplumber'
            }
        }
    }

def handle_rag(req):
    query = req.get('query')
    return {
        'status': 'success', 
        'results': [
            {'page': 1, 'text': f'Mock result for "{query}"', 'score': 0.9}
        ]
    }

def main():
    # Force unbuffered stdout/stdin
    if sys.version_info[0] == 3:
        sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    
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
