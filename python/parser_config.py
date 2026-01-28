"""
Enhanced Financial PDF Parser for NSE/BSE Annual Statements
Version: 2.0.0

Features:
- Standalone vs Consolidated detection and separation
- OCR support for scanned documents (Tesseract/EasyOCR)
- Table structure detection with multiple fallback methods
- Statement-specific parsing with section tracking
- Multi-page statement handling
- Comprehensive validation and quality checks
- Indian financial format (Schedule III) support
- Robust error handling and logging

Dependencies:
    pip install PyMuPDF opencv-python-headless pillow numpy pandas
    pip install pytesseract  # Optional: for OCR
    pip install easyocr      # Optional: alternative OCR
"""

from __future__ import annotations

import io
import json
import logging
import re
import time
import hashlib
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, wraps
from pathlib import Path
from typing import (
    Any, Callable, Dict, Generator, List, Optional, 
    Set, Tuple, Type, TypeVar, Union
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')

# =============================================================================
# Optional Dependencies - Graceful Handling
# =============================================================================

# Core dependencies
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not installed. PDF parsing will be limited.")

# OCR dependencies
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    np = None
    logger.warning("OpenCV/PIL not installed. OCR will be disabled.")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("Pandas not installed. Excel parsing will be disabled.")


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class ParserConfig:
    """Configuration settings for the financial parser."""
    
    # OCR Settings
    use_ocr: bool = True
    ocr_engine: str = 'tesseract'  # 'tesseract' or 'easyocr'
    ocr_dpi: int = 300
    ocr_confidence_threshold: float = 30.0
    force_ocr: bool = False
    
    # Parsing Settings
    min_numbers_per_row: int = 2
    max_indent_level: int = 4
    min_label_length: int = 3
    max_label_length: int = 200
    
    # Detection Settings
    entity_detection_threshold: float = 0.3
    statement_detection_threshold: float = 0.2
    table_detection_min_rows: int = 3
    
    # Page Settings
    max_continuation_pages: int = 4
    header_scan_chars: int = 1500
    
    # Validation Settings
    validate_output: bool = True
    check_balance_sheet_equation: bool = True
    flag_extreme_variations: bool = True
    extreme_variation_threshold: float = 1000.0  # percentage
    
    # Performance Settings
    cache_ocr_results: bool = True
    max_debug_entries: int = 100
    
    # Output Settings
    include_raw_text: bool = False
    include_debug_info: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }


# =============================================================================
# Enums
# =============================================================================

class StatementType(Enum):
    """Financial statement types."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    NOTES = "notes"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, s: str) -> 'StatementType':
        """Convert string to StatementType."""
        mapping = {
            'balance_sheet': cls.BALANCE_SHEET,
            'balance sheet': cls.BALANCE_SHEET,
            'income_statement': cls.INCOME_STATEMENT,
            'income statement': cls.INCOME_STATEMENT,
            'profit_and_loss': cls.INCOME_STATEMENT,
            'profit and loss': cls.INCOME_STATEMENT,
            'cash_flow': cls.CASH_FLOW,
            'cash flow': cls.CASH_FLOW,
            'notes': cls.NOTES,
        }
        return mapping.get(s.lower().strip(), cls.UNKNOWN)


class ReportingEntity(Enum):
    """Type of reporting entity."""
    STANDALONE = "standalone"
    CONSOLIDATED = "consolidated"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, s: str) -> 'ReportingEntity':
        """Convert string to ReportingEntity."""
        s_lower = s.lower().strip()
        if 'standalone' in s_lower or 'separate' in s_lower:
            return cls.STANDALONE
        elif 'consolidated' in s_lower or 'group' in s_lower:
            return cls.CONSOLIDATED
        return cls.UNKNOWN


class OCRStatus(Enum):
    """OCR processing status."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CACHED = "cached"
    NOT_NEEDED = "not_needed"


class ValidationSeverity(Enum):
    """Validation issue severity."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class StatementIdentifier:
    """Unique identifier for a financial statement."""
    statement_type: StatementType
    reporting_entity: ReportingEntity
    
    @property
    def key(self) -> str:
        return f"{self.reporting_entity.value}_{self.statement_type.value}"
    
    def __hash__(self):
        return hash(self.key)
    
    def __eq__(self, other):
        if isinstance(other, StatementIdentifier):
            return self.key == other.key
        return False
    
    def __repr__(self):
        return f"StatementIdentifier({self.reporting_entity.value}, {self.statement_type.value})"


@dataclass
class OCRResult:
    """Result of OCR processing for a page."""
    page_num: int
    text: str
    confidence: float
    status: OCRStatus
    processing_time: float
    method: str
    error_message: Optional[str] = None
    word_count: int = 0
    number_count: int = 0
    
    def __post_init__(self):
        if self.text:
            self.word_count = len(self.text.split())
            self.number_count = len(re.findall(r'\d+', self.text))
    
    @property
    def is_successful(self) -> bool:
        return self.status in (OCRStatus.SUCCESS, OCRStatus.SKIPPED, OCRStatus.NOT_NEEDED)
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        if not self.is_successful:
            return 0.0
        
        base_score = self.confidence
        
        # Bonus for having numbers (financial documents should have many)
        if self.word_count > 0:
            number_ratio = self.number_count / self.word_count
            if number_ratio > 0.1:
                base_score = min(100, base_score + 10)
        
        return base_score


@dataclass
class ExtractedTable:
    """Represents an extracted table from a PDF page."""
    page_num: int
    headers: List[str]
    rows: List[List[str]]
    statement_type: StatementType
    reporting_entity: ReportingEntity
    confidence: float
    extraction_method: str = "unknown"
    
    @property
    def row_count(self) -> int:
        return len(self.rows)
    
    @property
    def column_count(self) -> int:
        if self.headers:
            return len(self.headers)
        elif self.rows:
            return max(len(row) for row in self.rows)
        return 0
    
    def to_dict(self) -> Dict:
        return {
            'page_num': self.page_num,
            'headers': self.headers,
            'rows': self.rows,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'statement_type': self.statement_type.value,
            'reporting_entity': self.reporting_entity.value,
            'confidence': self.confidence,
            'extraction_method': self.extraction_method
        }


@dataclass
class StatementBoundary:
    """Tracks the boundaries of a financial statement."""
    identifier: StatementIdentifier
    start_page: int
    end_page: int
    start_line: int = 0
    end_line: int = -1
    title: str = ""
    confidence: float = 0.0
    
    @property
    def page_count(self) -> int:
        return self.end_page - self.start_page + 1
    
    @property
    def pages(self) -> List[int]:
        return list(range(self.start_page, self.end_page + 1))


@dataclass
class FinancialLineItem:
    """Represents a single line item from a financial statement."""
    id: str
    label: str
    current_year: float
    previous_year: float
    statement_type: str
    reporting_entity: str
    section: str = ""
    note_ref: str = ""
    indent_level: int = 0
    is_total: bool = False
    is_subtotal: bool = False
    is_important: bool = False
    source_page: int = 0
    raw_line: str = ""
    
    @property
    def variation(self) -> float:
        return self.current_year - self.previous_year
    
    @property
    def variation_percent(self) -> float:
        if self.previous_year == 0:
            return 0.0 if self.current_year == 0 else float('inf')
        return (self.variation / abs(self.previous_year)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "currentYear": round(self.current_year, 2),
            "previousYear": round(self.previous_year, 2),
            "variation": round(self.variation, 2),
            "variationPercent": round(self.variation_percent, 2) if self.variation_percent != float('inf') else None,
            "statementType": self.statement_type,
            "reportingEntity": self.reporting_entity,
            "section": self.section,
            "noteRef": self.note_ref,
            "indentLevel": self.indent_level,
            "isTotal": self.is_total,
            "isSubtotal": self.is_subtotal,
            "isImportant": self.is_important,
            "sourcePage": self.source_page,
        }


@dataclass
class ParsedStatement:
    """Contains all parsed data for a single statement."""
    identifier: StatementIdentifier
    items: List[FinancialLineItem]
    pages: List[int]
    sections: Dict[str, List[str]]
    title: str = ""
    year_labels: Tuple[str, str] = ("Current Year", "Previous Year")
    
    @property
    def item_count(self) -> int:
        return len(self.items)
    
    def get_item_by_id(self, item_id: str) -> Optional[FinancialLineItem]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_items_by_section(self, section: str) -> List[FinancialLineItem]:
        return [item for item in self.items if item.section == section]
    
    def get_totals(self) -> List[FinancialLineItem]:
        return [item for item in self.items if item.is_total]
    
    def to_dict(self) -> Dict:
        return {
            "items": [item.to_dict() for item in self.items],
            "pages": [p + 1 for p in self.pages],  # Convert to 1-indexed
            "sections": self.sections,
            "title": self.title,
            "yearLabels": {
                "current": self.year_labels[0],
                "previous": self.year_labels[1]
            }
        }


@dataclass
class ValidationIssue:
    """Represents a validation issue found in parsed data."""
    severity: ValidationSeverity
    message: str
    location: str = ""
    details: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "details": self.details
        }


# =============================================================================
# Utility Functions
# =============================================================================

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} completed in {elapsed:.3f}s")
        return result
    return wrapper


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            # Remove commas and parentheses
            clean = re.sub(r'[,\s]', '', value)
            is_negative = '(' in value and ')' in value
            clean = re.sub(r'[^\d.\-]', '', clean)
            if not clean or clean == '-':
                return default
            result = float(clean)
            return -result if is_negative else result
        except ValueError:
            return default
    return default


def generate_hash_id(text: str, prefix: str = "") -> str:
    """Generate a short hash-based ID."""
    hash_val = hashlib.md5(text.encode()).hexdigest()[:8]
    if prefix:
        return f"{prefix}_{hash_val}"
    return hash_val


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def extract_numbers_from_text(text: str) -> List[Tuple[str, float]]:
    """Extract all numbers from text with their string representation."""
    pattern = r'[\(\-]?\s*[\d,]+(?:\.\d{1,2})?\s*\)?'
    matches = re.findall(pattern, text)
    results = []
    for match in matches:
        value = safe_float(match)
        results.append((match.strip(), value))
    return results
