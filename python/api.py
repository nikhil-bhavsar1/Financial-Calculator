#!/usr/bin/env python3
"""
api.py - Unified Python Backend for Financial Calculator
Supports both:
  - Desktop Sidecar Mode: STDIN/STDOUT JSON messaging (Tauri)
  - Web Server Mode: Flask HTTP API (--server <port>)

Integrates:
  - parsers.py: Enhanced document parsing (Standalone/Consolidated)
  - calculator.py: Financial metrics calculation
"""

import sys
import json
import os
import argparse
import time
import traceback
import tempfile
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

# Configure logging to stderr (doesn't interfere with JSON stdout)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS - Local Modules
# =============================================================================

# Import parsers module
PARSER_IMPORT_ERROR = None
try:
    from parsers import FinancialParser, parse_file, parse_annual_report
    PARSER_AVAILABLE = True
    logger.info("parsers module loaded successfully")
except ImportError as e:
    PARSER_AVAILABLE = False
    PARSER_IMPORT_ERROR = str(e)
    import traceback
    traceback.print_exc()
    logger.warning(f"parsers module not available: {e}")

# Import calculator module
try:
    from calculator import calculate_comprehensive_metrics, DEFAULT_MAPPING, update_mapping_configuration
    CALCULATOR_AVAILABLE = True
    logger.info("calculator module loaded successfully")
except ImportError as e:
    CALCULATOR_AVAILABLE = False
    logger.warning(f"calculator module not available: {e}")

# Flask imports (for server mode)
FLASK_AVAILABLE = False
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
    logger.info("Flask loaded successfully")
except ImportError:
    logger.warning("Flask not available - server mode disabled")

# Import PyMuPDF for RAG text extraction
try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

# Import RAG Engine (located in parent directory)
try:
    # Add parent directory to path for rag_engine import
    _parent_dir = str(Path(__file__).parent.parent)
    if _parent_dir not in sys.path:
        sys.path.insert(0, _parent_dir)
    from rag_engine import RAGEngine
    RAG_AVAILABLE = True
    logger.info("RAG Engine loaded successfully")
except ImportError as e:
    RAG_AVAILABLE = False
    logger.warning(f"RAG Engine not available: {e}")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class APIResponse:
    """Standard API response structure."""
    status: str  # 'success', 'error', 'progress'
    data: Optional[Dict] = None
    message: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        result = {"status": self.status}
        if self.data is not None:
            result["data"] = self.data
        if self.message:
            result["message"] = self.message
        if self.error:
            result["error"] = self.error
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


# =============================================================================
# BACKEND SERVICE - Core Logic
# =============================================================================

class BackendService:
    """
    Central service that handles all backend operations.
    Used by both Sidecar mode and Server mode.
    """
    
    def __init__(self):
        self.parser = FinancialParser() if PARSER_AVAILABLE else None
        self.rag_engine = RAGEngine() if RAG_AVAILABLE else None
    
    def _extract_text_for_rag(self, file_path: str, file_type: str) -> Optional[str]:
        """Extract text from file for RAG indexing."""
        if not os.path.exists(file_path):
            return None
            
        try:
            if file_type == 'pdf' and FITZ_AVAILABLE:
                doc = fitz.open(file_path)
                text = ""
                for i, page in enumerate(doc):
                    text += f"--- Page {i+1} ---\n{page.get_text()}\n"
                doc.close()
                return text
            elif file_type in ['txt', 'csv', 'md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            # Add other types if needed (xlsx could be converted to csv-like text)
            return None
        except Exception as e:
            logger.warning(f"RAG text extraction failed: {e}")
            return None

    def search_rag(self, query: str) -> Dict:
        """Search the indexed document using RAG."""
        if not self.rag_engine:
            return {"error": "RAG Engine not available"}
        
        try:
            results_json = self.rag_engine.search(query)
            return {"results": json.loads(results_json)}
        except Exception as e:
            return {"error": str(e)}

    def parse_file(self, file_path: str, file_type: Optional[str] = None) -> Dict:
        """
        Parse a financial document.
        
        Args:
            file_path: Path to the file
            file_type: Optional file type override
        
        Returns:
            Parsed document data with standalone/consolidated structure
        """
        if not PARSER_AVAILABLE:
            return {"error": f"Parser module not available. Import Error: {PARSER_IMPORT_ERROR}"}
        
        try:
            # Detect file type if not provided
            if file_type is None:
                file_type = Path(file_path).suffix.lower().lstrip('.')
            
            logger.info(f"Parsing file: {file_path} (type: {file_type})")
            
            # Use the enhanced parser
            result = parse_file(file_path, file_type)
            
            logger.info(f"Parsed {len(result.get('items', []))} items")
            
            # Index for RAG if available
            if self.rag_engine:
                text = self._extract_text_for_rag(file_path, file_type)
                if text:
                    count_json = self.rag_engine.index_document(text)
                    logger.info(f"RAG Indexing complete: {count_json}")
            
            return result
            
        except Exception as e:
            logger.error(f"Parse error: {traceback.format_exc()}")
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    def parse_content(
        self, 
        content: str, 
        file_name: str = "document",
        file_type: Optional[str] = None
    ) -> Dict:
        """
        Parse content directly (for uploaded files).
        
        Args:
            content: File content (base64 encoded for binary, raw for text)
            file_name: Original filename for type detection
            file_type: Optional file type override
        """
        if not PARSER_AVAILABLE:
            return {"error": f"Parser module not available. Import Error: {PARSER_IMPORT_ERROR}"}
        
        try:
            # Detect file type
            if file_type is None:
                file_type = Path(file_name).suffix.lower().lstrip('.')
            
            # Handle base64 encoded content
            decoded_content = None
            is_base64 = False
            
            try:
                if content.startswith("data:"):
                    content = content.split(",", 1)[-1]
                decoded_content = base64.b64decode(content)
                is_base64 = True
            except Exception:
                decoded_content = content.encode('utf-8') if isinstance(content, str) else content
            
            # write to temp file for all types to ensure parsers get a valid file path
            suffix = f'.{file_type}' if file_type else ''
            
            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
                mode='wb'
            ) as tmp:
                # Ensure we write bytes
                if isinstance(decoded_content, str):
                    tmp.write(decoded_content.encode('utf-8'))
                else:
                    tmp.write(decoded_content)
                tmp_path = tmp.name
            
            try:
                # Use the service's parse_file method which handles everything
                # This returns a Dict, so no json.loads needed
                result = self.parse_file(tmp_path, file_type)
            finally:
                # Cleanup
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Parse content error: {traceback.format_exc()}")
            return {"error": str(e)}
    
    def calculate_metrics(
        self, 
        items: List[Dict], 
        mapping: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate financial metrics from extracted items.
        
        Args:
            items: List of financial line items
            mapping: Optional keyword mapping override
        """
        if not CALCULATOR_AVAILABLE:
            return {"error": "Calculator module not available"}
        
        try:
            logger.info(f"Calculating metrics for {len(items)} items")
            
            # Use default mapping if not provided
            if mapping is None:
                mapping = DEFAULT_MAPPING
            
            # Calculate metrics
            result = calculate_comprehensive_metrics(items, mapping)
            
            logger.info(f"Calculated {len(result)} metric groups")
            
            return {"metrics": result}
            
        except Exception as e:
            logger.error(f"Calculate error: {traceback.format_exc()}")
            return {"error": str(e)}
    
    def update_mapping(self, mappings: List[Dict]) -> Dict:
        """Update backend configuration mappings."""
        try:
            # Update calculator mapping
            if CALCULATOR_AVAILABLE:
                update_mapping_configuration(mappings)
            
            # Update parser keywords
            if self.parser:
                self.parser.update_keywords(mappings)
                
            logger.info(f"Configuration updated with {len(mappings)} terms")
            return {"status": "success", "message": "Mappings updated"}
        except Exception as e:
            logger.error(f"Update mapping error: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict:
        """Return service health status."""
        return {
            "status": "healthy",
            "parser_available": PARSER_AVAILABLE,
            "calculator_available": CALCULATOR_AVAILABLE,
            "flask_available": FLASK_AVAILABLE,
        }


# =============================================================================
# SIDECAR MODE - STDIN/STDOUT Handler
# =============================================================================

class SidecarHandler:
    """
    Handles Tauri sidecar communication via STDIN/STDOUT.
    Reads JSON commands from stdin, writes JSON responses to stdout.
    """
    
    def __init__(self, service: BackendService):
        self.service = service
    
    def run(self):
        """Main loop for sidecar mode."""
        logger.info("Starting sidecar mode...")
        
        while True:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                
                if not line:
                    # EOF - exit gracefully
                    logger.info("Sidecar: EOF received, exiting")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse and handle the command
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    self._send_error(f"Invalid JSON: {e}")
                    continue
                
                # Handle the request
                response = self._handle_request(request)
                self._send_response(response)
                
            except KeyboardInterrupt:
                logger.info("Sidecar: Interrupted")
                break
            except Exception as e:
                logger.error(f"Sidecar error: {traceback.format_exc()}")
                self._send_error(str(e))
    
    def _handle_request(self, request: Dict) -> Dict:
        """Process a single request."""
        command = request.get("command", "").lower()
        
        if command == "ping":
            return {"status": "success", "message": "pong"}
        
        elif command == "health":
            return {"status": "success", "data": self.service.health_check()}
        
        elif command == "parse":
            file_path = request.get("file_path")
            content = request.get("content")
            file_name = request.get("file_name", "document")
            file_type = request.get("file_type")
            
            if content:
                result = self.service.parse_content(content, file_name, file_type)
            elif file_path:
                result = self.service.parse_file(file_path, file_type)
            else:
                return {"status": "error", "error": "No file_path or content provided"}
            
            if "error" in result:
                return {"status": "error", "error": result["error"]}
            
            return {"status": "success", "data": result}
        
        elif command == "calculate":
            items = request.get("items", [])
            mapping = request.get("mapping")
            
            result = self.service.calculate_metrics(items, mapping)
            
            if "error" in result:
                return {"status": "error", "error": result["error"]}
            
            return {"status": "success", "data": result}
        
        elif command == "update_mapping":
            mappings = request.get("mappings", [])
            result = self.service.update_mapping(mappings)
            if "error" in result:
                return {"status": "error", "error": result["error"]}
            return {"status": "success", "message": "Mappings updated"}
        
        elif command == "search":
            query = request.get("query", "")
            result = self.service.search_rag(query)
            if "error" in result:
                return {"status": "error", "error": result["error"]}
            return {"status": "success", "data": result}
        
        else:
            return {"status": "error", "error": f"Unknown command: {command}"}
    
    def _send_response(self, response: Dict):
        """Send JSON response to stdout."""
        print(json.dumps(response, default=str), flush=True)
    
    def _send_error(self, message: str):
        """Send error response to stdout."""
        self._send_response({"status": "error", "error": message})


# =============================================================================
# SERVER MODE - Flask HTTP API
# =============================================================================

def create_flask_app(service: BackendService) -> 'Flask':
    """Create and configure Flask application."""
    if not FLASK_AVAILABLE:
        raise RuntimeError("Flask is not available")
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify(service.health_check())
    
    @app.route('/api/health', methods=['GET'])
    def api_health():
        return jsonify(service.health_check())
    
    # Search endpoint
    @app.route('/search', methods=['POST'])
    @app.route('/api/search', methods=['POST'])
    def search():
        try:
            data = request.get_json() or {}
            query = data.get("query", "")
            
            if not query:
                return jsonify({"error": "No query provided"}), 400
            
            result = service.search_rag(query)
            
            if "error" in result:
                return jsonify(result), 500
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Search endpoint error: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500

    # Parse endpoint
    @app.route('/parse', methods=['POST'])
    @app.route('/api/parse', methods=['POST'])
    def parse():
        try:
            data = request.get_json() or {}
            
            file_path = data.get("file_path")
            content = data.get("content")
            file_name = data.get("file_name", "document")
            file_type = data.get("file_type") or data.get("fileType")
            
            if content:
                result = service.parse_content(content, file_name, file_type)
            elif file_path:
                result = service.parse_file(file_path, file_type)
            else:
                return jsonify({"error": "No file_path or content provided"}), 400
            
            if "error" in result:
                return jsonify(result), 500
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Parse endpoint error: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500
    
    # Calculate endpoint
    @app.route('/calculate', methods=['POST'])
    @app.route('/api/calculate', methods=['POST'])
    def calculate():
        try:
            data = request.get_json() or {}
            
            items = data.get("items", [])
            mapping = data.get("mapping")
            
            if not items:
                return jsonify({"error": "No items provided"}), 400
            
            result = service.calculate_metrics(items, mapping)
            
            if "error" in result:
                return jsonify(result), 500
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Calculate endpoint error: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500
    
    # Mapping endpoint (returns default mapping)
    @app.route('/mapping', methods=['GET'])
    @app.route('/api/mapping', methods=['GET'])
    def get_mapping():
        if CALCULATOR_AVAILABLE:
            return jsonify(DEFAULT_MAPPING)
        return jsonify({"error": "Calculator not available"}), 500
    
    # Mapping update endpoint
    @app.route('/mapping', methods=['POST'])
    @app.route('/api/mapping', methods=['POST'])
    def update_mapping_endpoint():
        try:
            mappings = request.get_json() or []
            result = service.update_mapping(mappings)
            if "error" in result:
                return jsonify(result), 500
            return jsonify(result)
        except Exception as e:
            logger.error(f"Mapping update error: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500
    
    # Catch-all for debugging
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "service": "Financial Calculator API",
            "version": "2.0.0",
            "endpoints": [
                "GET /health",
                "POST /parse",
                "POST /calculate",
                "GET /mapping"
            ],
            "status": service.health_check()
        })
    
    return app


def run_server(port: int, service: BackendService):
    """Run Flask server."""
    if not FLASK_AVAILABLE:
        logger.error("Flask is not available. Install with: pip install flask flask-cors")
        sys.exit(1)
    
    app = create_flask_app(service)
    
    logger.info(f"Starting Flask server on port {port}...")
    logger.info(f"API available at: http://localhost:{port}")
    
    # Run with threading for concurrent requests
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point - determines mode and runs appropriate handler."""
    parser = argparse.ArgumentParser(
        description='Financial Calculator Backend API'
    )
    parser.add_argument(
        '--server', 
        type=int, 
        metavar='PORT',
        help='Run as HTTP server on specified port'
    )
    parser.add_argument(
        '--sidecar',
        action='store_true',
        help='Run in sidecar mode (STDIN/STDOUT)'
    )
    
    args = parser.parse_args()
    
    # Initialize the service
    service = BackendService()
    
    # Log startup info
    logger.info("=" * 50)
    logger.info("Financial Calculator Backend")
    logger.info("=" * 50)
    logger.info(f"Parser available: {PARSER_AVAILABLE}")
    logger.info(f"Calculator available: {CALCULATOR_AVAILABLE}")
    logger.info(f"Flask available: {FLASK_AVAILABLE}")
    
    # Determine mode
    if args.server:
        # Server mode
        logger.info(f"Mode: HTTP Server (port {args.server})")
        run_server(args.server, service)
    else:
        # Default to sidecar mode
        logger.info("Mode: Sidecar (STDIN/STDOUT)")
        handler = SidecarHandler(service)
        handler.run()


if __name__ == "__main__":
    main()