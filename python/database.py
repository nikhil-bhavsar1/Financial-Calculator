import sqlite3
import json
import os
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILENAME = "extracted_data.db"

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use parent directory (project root) for DB so both Python and Rust can find it
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, DB_FILENAME)
        else:
            self.db_path = db_path
            
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self, wipe: bool = False):
        """Initialize the database schema. Optional wipe to clear previous session data."""
        if wipe and os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
                logger.info("Previous database session wiped.")
            except OSError as e:
                logger.warning(f"Could not wipe database: {e}")

        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Documents Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT -- JSON string
            )
        ''')
        
        # Financial Items Table (Parsed Data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_items (
                id TEXT PRIMARY KEY,
                doc_id INTEGER,
                label TEXT,
                value_current REAL,
                value_previous REAL,
                row_index INTEGER,
                statement_type TEXT, -- 'INCOME', 'BALANCE', 'CASH'
                is_header BOOLEAN,
                source_page INTEGER,
                source_line_text TEXT,
                confidence REAL,
                original_json TEXT, -- Full item JSON for reconstruction
                FOREIGN KEY(doc_id) REFERENCES documents(id)
            )
        ''')
        
        # Scraper Data Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraper_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                source TEXT, -- 'NSE', 'BSE', 'WEB'
                data_type TEXT, -- 'SEARCH', 'DETAILS', 'QUOTE'
                data TEXT, -- JSON payload
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Text Chunks Table (for RAG)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                page_num INTEGER,
                chunk_index INTEGER,
                content TEXT,
                embedding TEXT, -- Placeholder for vector extension
                FOREIGN KEY(doc_id) REFERENCES documents(id)
            )
        ''')

        # Extraction Checklist Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_checklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                metric_key TEXT,
                label TEXT,
                status TEXT, -- 'EXTRACTED', 'NOT_FOUND', 'NO_VALUE_FOUND'
                reason TEXT,
                source_page INTEGER,
                FOREIGN KEY(doc_id) REFERENCES documents(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path} (with RAG chunks)")

    def save_document(self, filename: str, metadata: Dict[str, Any] = None) -> int:
        """Register a document and return its ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO documents (filename, metadata) VALUES (?, ?)',
            (filename, json.dumps(metadata) if metadata else '{}')
        )
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    def save_parsed_items(self, doc_id: int, items: List[Dict[str, Any]]):
        """Save a list of parsed financial items."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for item in items:
            # Determine statement type if present, else default or infer
            stmt_type = item.get('statementType', 'UNKNOWN').upper()
            
            # Generate ID if not present
            item_id = item.get('id', str(uuid.uuid4()))
            
            cursor.execute('''
                INSERT OR REPLACE INTO financial_items (
                    id, doc_id, label, value_current, value_previous, 
                    row_index, statement_type, is_header, source_page, 
                    source_line_text, confidence, original_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_id,
                doc_id,
                item.get('label', ''),
                item.get('currentYear', 0) or 0,
                item.get('previousYear', 0) or 0,
                item.get('rowIndex', -1),
                stmt_type,
                item.get('isHeader', False),
                item.get('page', 0), # source_page
                item.get('rawLine', ''),
                item.get('confidence', 0.0),
                json.dumps(item)
            ))
            
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(items)} items for doc_id {doc_id}")

    def save_scraper_result(self, query: str, source: str, data_type: str, data: Any):
        """Log scraper results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scraper_data (query, source, data_type, data)
            VALUES (?, ?, ?, ?)
        ''', (query, source, data_type, json.dumps(data)))
        conn.commit()
        conn.close()

    def get_items_by_statement(self, doc_id: int, statement_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve items, optionally filtered by statement type."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if statement_type:
            cursor.execute(
                'SELECT original_json FROM financial_items WHERE doc_id = ? AND statement_type = ?',
                (doc_id, statement_type.upper())
            )
        else:
            cursor.execute(
                'SELECT original_json FROM financial_items WHERE doc_id = ?',
                (doc_id,)
            )
            
        rows = cursor.fetchall()
        conn.close()
        
        return [json.loads(row['original_json']) for row in rows]

    def get_all_data(self) -> Dict[str, Any]:
        """Retrieve all data from database for debugging/viewing."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Documents
            cursor.execute("SELECT * FROM documents ORDER BY id DESC LIMIT 1")
            documents = [dict(row) for row in cursor.fetchall()]

            # Financial Items (Parsed) - Limit to prevent timeouts
            cursor.execute("SELECT * FROM financial_items ORDER BY row_index ASC LIMIT 1000")
            items = [dict(row) for row in cursor.fetchall()]

            # Scraper Data
            cursor.execute("SELECT * FROM scraper_data ORDER BY created_at DESC LIMIT 100")
            scraper_data = [dict(row) for row in cursor.fetchall()]

            # Extraction Checklist
            cursor.execute("SELECT * FROM extraction_checklist LIMIT 100")
            checklist = [dict(row) for row in cursor.fetchall()]

            return {
                'documents': documents,
                'financial_items': items,
                'scraper_data': scraper_data,
                'extraction_checklist': checklist
            }
        finally:
            conn.close()

    def save_extraction_checklist(self, doc_id: int, results: List[Dict[str, Any]]):
        """Save extraction coverage results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Clear previous checklist for this doc if it exists (re-parsing)
        cursor.execute('DELETE FROM extraction_checklist WHERE doc_id = ?', (doc_id,))
        
        for res in results:
            cursor.execute('''
                INSERT INTO extraction_checklist (
                    doc_id, metric_key, label, status, reason, source_page
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                res.get('metric_key'),
                res.get('label'),
                res.get('status'),
                res.get('reason'),
                res.get('source_page', 0)
            ))
            
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(results)} checklist items for doc_id {doc_id}")

    def get_extraction_checklist(self, doc_id: int) -> List[Dict[str, Any]]:
        """Retrieve extraction results for a document."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM extraction_checklist WHERE doc_id = ?',
            (doc_id,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def save_text_chunks(self, doc_id: int, base_text: str):
        """Split text into chunks and save to DB."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Simple splitting by double newline (paragraphs) or pages
        # For now, just splitting roughly by length to simulate chunks
        chunks = []
        chunk_size = 1000
        for i in range(0, len(base_text), chunk_size):
            chunks.append(base_text[i:i+chunk_size])
            
        for idx, content in enumerate(chunks):
            cursor.execute(
                'INSERT INTO text_chunks (doc_id, chunk_index, content) VALUES (?, ?, ?)',
                (doc_id, idx, content)
            )
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(chunks)} text chunks for doc_id {doc_id}")

    def get_rag_context(self, doc_id: int = None, query: str = "") -> str:
        """
        Retrieve context for RAG:
        1. Key extracted financial items
        2. Relevant text chunks (keyword matched)
        """
        context_parts = []
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Get Financial Metrics (Structured)
        if doc_id:
            cursor.execute('''
                SELECT label, value_current, statement_type 
                FROM financial_items 
                WHERE doc_id = ? 
                ORDER BY confidence DESC 
                LIMIT 50
            ''', (doc_id,))
            items = cursor.fetchall()
            
            if items:
                context_parts.append("--- Extracted Financial Metrics ---")
                for item in items:
                    context_parts.append(f"{item['label']}: {item['value_current']:,.0f} ({item['statement_type']})")
        
        # 2. Get Text Segments (Narrative)
        # Naive keyword search if query provided
        if doc_id:
            if query:
                # Basic SQL LIKE search
                terms = query.split()
                # construct clause: content LIKE '%term%'
                # This is a very simple approximation of search
                cursor.execute(
                    'SELECT content FROM text_chunks WHERE doc_id = ? AND content LIKE ? LIMIT 5',
                    (doc_id, f'%{terms[0] if terms else ""}%')
                )
            else:
                # Return start of document
                cursor.execute('SELECT content FROM text_chunks WHERE doc_id = ? ORDER BY chunk_index ASC LIMIT 3', (doc_id,))
            
            chunks = cursor.fetchall()
            if chunks:
                context_parts.append("\n--- Document Text Segments ---")
                for chunk in chunks:
                    context_parts.append(chunk['content'])
                    
        conn.close()
        return "\n".join(context_parts)

# Global instance for easy import
db = DatabaseManager()
