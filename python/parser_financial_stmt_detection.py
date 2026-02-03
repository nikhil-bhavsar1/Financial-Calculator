
import re
from typing import Dict, List, Optional, Tuple, Any

from parser_config import (
    ParserConfig, ReportingEntity, StatementType, StatementIdentifier, clean_text
)

# =============================================================================
# Financial Statement Detection
# =============================================================================

class FinancialPatternMatcher:
    """
    Contains all patterns for detecting financial statements.
    Centralized pattern management for easy maintenance.
    """
    
    # Reporting entity patterns
    ENTITY_PATTERNS = {
        ReportingEntity.STANDALONE: [
            r'\bstandalone\b',
            r'\bstand[-\s]?alone\b',
            r'\bunconsolidated\b',
            r'\bseparate\s+financial',
            r'\bcompany\s+(?:level\s+)?financial',
        ],
        ReportingEntity.CONSOLIDATED: [
            r'\bconsolidated\b',
            r'\bgroup\s+financial',
            r'\bcombined\s+financial',
            r'\bgroup\s+(?:level\s+)?financial',
        ],
    }
    
    # Primary statement type patterns (for headers)
    PRIMARY_PATTERNS = {
        StatementType.BALANCE_SHEET: [
            r'balance\s+sheet\s+as\s+(?:at|on)',
            r'balance\s+sheet\s*$',
            r'statement\s+of\s+(?:financial\s+)?position',
            r'(?:statement\s+of\s+)?assets?\s+and\s+liabilities',
        ],
        StatementType.INCOME_STATEMENT: [
            r'statement\s+of\s+profit\s+and\s+loss',
            r'profit\s+and\s+loss\s+(?:statement|account)',
            r'(?:statement\s+of\s+)?income\s+statement',
            r'statement\s+of\s+(?:comprehensive\s+)?income',
            r'statement\s+of\s+operations',
            r'statement\s+of\s+earnings',
        ],
        StatementType.CASH_FLOW: [
            r'(?:statement\s+of\s+)?cash\s+flows?(?:\s+statement)?',
            r'cash\s+flow\s+statement',
            r'statement\s+showing\s+changes\s+in\s+cash',
        ],
        StatementType.NOTES: [
            r'notes\s+to\s+(?:the\s+)?financial\s+statements',
            r'notes\s+to\s+(?:the\s+)?accounts',
            r'summary\s+of\s+significant\s+accounting\s+policies',
            r'accompanying\s+notes',
            r'notes\s+forming\s+part\s+of',
        ],
    }
    
    # Combined patterns for detecting both entity and statement type together
    COMBINED_PATTERNS = {
        (ReportingEntity.STANDALONE, StatementType.BALANCE_SHEET): [
            r'standalone\s+balance\s+sheet',
            r'stand[-\s]?alone\s+balance\s+sheet',
            r'standalone\s+statement\s+of\s+(?:financial\s+)?position',
        ],
        (ReportingEntity.STANDALONE, StatementType.INCOME_STATEMENT): [
            r'standalone\s+statement\s+of\s+profit\s+and\s+loss',
            r'stand[-\s]?alone\s+statement\s+of\s+profit\s+and\s+loss',
            r'standalone\s+profit\s+and\s+loss',
            r'standalone\s+statement\s+of\s+(?:comprehensive\s+)?income',
        ],
        (ReportingEntity.STANDALONE, StatementType.CASH_FLOW): [
            r'standalone\s+(?:statement\s+of\s+)?cash\s+flows?',
            r'stand[-\s]?alone\s+(?:statement\s+of\s+)?cash\s+flows?',
            r'standalone\s+cash\s+flow\s+statement',
        ],
        (ReportingEntity.STANDALONE, StatementType.NOTES): [
            r'notes\s+to\s+(?:the\s+)?standalone\s+financial\s+statements',
            r'standalone\s+notes',
        ],
        (ReportingEntity.CONSOLIDATED, StatementType.BALANCE_SHEET): [
            r'consolidated\s+balance\s+sheet',
            r'consolidated\s+statement\s+of\s+(?:financial\s+)?position',
        ],
        (ReportingEntity.CONSOLIDATED, StatementType.INCOME_STATEMENT): [
            r'consolidated\s+statement\s+of\s+profit\s+and\s+loss',
            r'consolidated\s+profit\s+and\s+loss',
            r'consolidated\s+statement\s+of\s+(?:comprehensive\s+)?income',
        ],
        (ReportingEntity.CONSOLIDATED, StatementType.CASH_FLOW): [
            r'consolidated\s+(?:statement\s+of\s+)?cash\s+flows?',
            r'consolidated\s+cash\s+flow\s+statement',
        ],
        (ReportingEntity.CONSOLIDATED, StatementType.NOTES): [
            r'notes\s+to\s+(?:the\s+)?consolidated\s+financial\s+statements',
            r'consolidated\s+notes',
        ],
    }
    
    # Content indicators for each statement type
    CONTENT_INDICATORS = {
        StatementType.BALANCE_SHEET: {
            'strong': [
                'total equity and liabilities',
                'total assets',
                'non-current assets',
                'current assets',
                'equity and liabilities',
                'shareholders funds',
                'shareholders\' funds',
                'share application money',
                'total non-current assets',
                'total current assets',
                'total non-current liabilities',
                'total current liabilities',
            ],
            'moderate': [
                'property, plant and equipment',
                'property plant and equipment',
                'trade receivables',
                'trade payables',
                'share capital',
                'reserves and surplus',
                'inventories',
                'borrowings',
                'other financial assets',
                'other financial liabilities',
                'deferred tax assets',
                'deferred tax liabilities',
                'capital work-in-progress',
                'intangible assets',
                'goodwill',
                'right-of-use assets',
                'lease liabilities',
            ],
        },
        StatementType.INCOME_STATEMENT: {
            'strong': [
                'revenue from operations',
                'profit before tax',
                'profit for the year',
                'profit for the period',
                'total income',
                'total expenses',
                'earnings per share',
                'basic eps',
                'diluted eps',
                'profit/(loss) for the year',
                'profit / (loss) for the year',
                'net profit for the year',
                'total comprehensive income',
            ],
            'moderate': [
                'other income',
                'cost of materials consumed',
                'cost of goods sold',
                'employee benefit expense',
                'employee benefits expense',
                'depreciation and amortisation',
                'depreciation and amortization',
                'finance costs',
                'tax expense',
                'current tax',
                'deferred tax',
                'exceptional items',
                'other comprehensive income',
                'changes in inventories',
                'purchase of stock-in-trade',
            ],
        },
        StatementType.CASH_FLOW: {
            'strong': [
                'cash flows from operating activities',
                'cash flows from investing activities',
                'cash flows from financing activities',
                'net increase in cash',
                'net decrease in cash',
                'cash generated from operations',
                'net cash from operating activities',
                'net cash used in operating activities',
                'net cash from investing activities',
                'net cash used in investing activities',
                'net cash from financing activities',
                'net cash used in financing activities',
            ],
            'moderate': [
                'cash and cash equivalents at the beginning',
                'cash and cash equivalents at the end',
                'operating profit before working capital',
                'adjustments for',
                'interest received',
                'interest paid',
                'dividends paid',
                'dividend paid',
                'income tax paid',
                'purchase of property, plant and equipment',
                'proceeds from sale of',
                'repayment of borrowings',
                'proceeds from borrowings',
            ],
        },
        StatementType.NOTES: {
            'strong': [
                'significant accounting policies',
                'property, plant and equipment schedule',
                'maturity analysis for lease liabilities',
                'reconciliation of tax expense',
                'financial risk management',
                'capital management',
                'fair value measurements',
            ],
            'moderate': [
                'depreciation method',
                'estimated useful lives',
                'defined benefit plan',
                'contingent liabilities',
                'commitments',
                'related party disclosures',
                'earnings per share',
                'audit fees',
            ],
        },
    }
    
    # Section markers within statements
    SECTION_MARKERS = {
        StatementType.BALANCE_SHEET: {
            'ASSETS': [
                r'^(?:i\.?\s*)?assets?\s*$',
                r'non[-\s]?current\s+assets',
                r'^current\s+assets',
            ],
            'NON_CURRENT_ASSETS': [
                r'non[-\s]?current\s+assets',
            ],
            'CURRENT_ASSETS': [
                r'(?<!non[-\s])current\s+assets',
            ],
            'EQUITY': [
                r'equity(?:\s+and\s+liabilities)?',
                r"shareholders?[''`]?\s*funds?",
            ],
            'NON_CURRENT_LIABILITIES': [
                r'non[-\s]?current\s+liabilities',
            ],
            'CURRENT_LIABILITIES': [
                r'(?<!non[-\s])current\s+liabilities',
            ],
        },
        StatementType.INCOME_STATEMENT: {
            'INCOME': [
                r'(?:i\.?\s*)?(?:revenue|income)',
                r'revenue\s+from\s+operations',
            ],
            'EXPENSES': [
                r'(?:ii\.?\s*)?expenses?',
            ],
            'PROFIT': [
                r'profit\s+(?:before|after)',
                r'profit\s+for\s+the',
            ],
            'OTHER_COMPREHENSIVE_INCOME': [
                r'other\s+comprehensive\s+income',
            ],
            'EPS': [
                r'earnings?\s+per\s+(?:equity\s+)?share',
            ],
        },
        StatementType.CASH_FLOW: {
            'OPERATING': [
                r'(?:cash\s+flows?\s+from\s+)?operating\s+activities',
                r'(?:a\)?\s*)?cash\s+flow\s+from\s+operating',
            ],
            'INVESTING': [
                r'(?:cash\s+flows?\s+from\s+)?investing\s+activities',
                r'(?:b\)?\s*)?cash\s+flow\s+from\s+investing',
            ],
            'FINANCING': [
                r'(?:cash\s+flows?\s+from\s+)?financing\s+activities',
                r'(?:c\)?\s*)?cash\s+flow\s+from\s+financing',
            ],
            'NET_CHANGE': [
                r'net\s+(?:increase|decrease|change)\s+in\s+cash',
            ],
        },
        StatementType.NOTES: {
            'ACCOUNTING_POLICIES': [
                r'accounting\s+policies',
                r'basis\s+of\s+preparation',
            ],
            'PPE': [
                r'property,\s+plant\s+and\s+equipment',
                r'tangible\s+assets',
            ],
            'INVESTMENTS': [
                r'investments',
            ],
            'TRADE_RECEIVABLES': [
                r'trade\s+receivables',
            ],
            'CASH': [
                r'cash\s+and\s+cash\s+equivalents',
            ],
        },
    }


class FinancialStatementDetector:
    """
    Detects and classifies financial statements within documents.
    """
    
    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()
        self.patterns = FinancialPatternMatcher()
    
    def detect_reporting_entity(self, text: str) -> Tuple[ReportingEntity, float]:
        """
        Detect if text refers to Standalone or Consolidated statements.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (ReportingEntity, confidence)
        """
        text_lower = text.lower()
        header_text = text_lower[:500]
        
        scores = {
            ReportingEntity.STANDALONE: 0.0,
            ReportingEntity.CONSOLIDATED: 0.0,
        }
        
        for entity, patterns in self.patterns.ENTITY_PATTERNS.items():
            for pattern in patterns:
                # Higher weight for matches in header
                if re.search(pattern, header_text, re.IGNORECASE):
                    scores[entity] += 30.0
                elif re.search(pattern, text_lower, re.IGNORECASE):
                    scores[entity] += 10.0
        
        # Determine winner
        max_entity = max(scores, key=scores.get)
        max_score = scores[max_entity]
        
        if max_score >= 10:
            confidence = min(max_score / 50, 1.0)
            return max_entity, confidence
        
        return ReportingEntity.UNKNOWN, 0.0
    
    def detect_statement_type(self, text: str) -> Tuple[StatementType, float]:
        """
        Detect the type of financial statement from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (StatementType, confidence)
        """
        text_lower = text.lower()
        header_text = text_lower[:self.config.header_scan_chars]
        
        scores = {st: 0.0 for st in StatementType if st != StatementType.UNKNOWN}
        
        # Check primary patterns (headers) - high weight
        for stmt_type, patterns in self.patterns.PRIMARY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, header_text, re.IGNORECASE):
                    scores[stmt_type] += 50.0
        
        # Check content indicators
        for stmt_type, indicators in self.patterns.CONTENT_INDICATORS.items():
            for indicator in indicators.get('strong', []):
                if indicator in text_lower:
                    scores[stmt_type] += 10.0
            for indicator in indicators.get('moderate', []):
                if indicator in text_lower:
                    scores[stmt_type] += 3.0
        
        # Find best match
        max_score = max(scores.values())
        
        if max_score >= 20:
            for stmt_type, score in scores.items():
                if score == max_score:
                    confidence = min(score / 100, 1.0)
                    return stmt_type, confidence
        
        return StatementType.UNKNOWN, 0.0
    
    def detect_full_statement(
        self,
        text: str,
        page_num: int = 0
    ) -> Tuple[StatementIdentifier, float, str]:
        """
        Detect both statement type and reporting entity.
        
        Args:
            text: Text to analyze
            page_num: Page number for context
            
        Returns:
            Tuple of (StatementIdentifier, confidence, detected_title)
        """
        text_lower = text.lower()
        
        # First, try combined patterns (most accurate)
        for (entity, stmt_type), patterns in self.patterns.COMBINED_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower[:1000], re.IGNORECASE)
                if match:
                    # Extract title from original text
                    title = text[match.start():match.end()].strip()
                    return (
                        StatementIdentifier(stmt_type, entity),
                        0.95,
                        clean_text(title)
                    )
        
        # Fall back to separate detection
        entity, entity_conf = self.detect_reporting_entity(text)
        stmt_type, stmt_conf = self.detect_statement_type(text)
        
        if stmt_type != StatementType.UNKNOWN:
            title = self._extract_title(text)
            combined_conf = (entity_conf + stmt_conf) / 2
            
            # Default to standalone if entity unknown
            if entity == ReportingEntity.UNKNOWN:
                entity = ReportingEntity.STANDALONE
                combined_conf *= 0.8  # Reduce confidence
            
            return (
                StatementIdentifier(stmt_type, entity),
                combined_conf,
                title
            )
        
        return (
            StatementIdentifier(StatementType.UNKNOWN, ReportingEntity.UNKNOWN),
            0.0,
            ""
        )
    
    def _extract_title(self, text: str) -> str:
        """Extract statement title from text."""
        lines = text.split('\n')[:30]
        
        title_keywords = [
            'balance sheet', 'profit and loss', 'cash flow',
            'income statement', 'financial position', 'comprehensive income'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in title_keywords):
                title = clean_text(line)
                if len(title) < 200:
                    return title
        
        return ""
    
    def has_table_structure(self, text: str) -> bool:
        """Check if text contains financial table structure."""
        text_lower = text.lower()
        
        # Check for Index/TOC indicators - usually these are NOT the actual statement
        # "Index to Consolidated..."
        if re.search(r'index\W+to\W+consolidated', text_lower[:500]):
            return False
            
        # "Page" column header
        if re.search(r'\bpage\b\s*$', text_lower[:300], re.MULTILINE):
            # But ensure it's not a "Page 1 of 5" footer at the top
            if "index" in text_lower[:500] or "content" in text_lower[:500]:
                return False

        # Check for markdown table markers (from MarkdownConverter output)
        # Markdown tables have pipe characters for column separators
        pipe_count = text.count('|')
        if pipe_count >= 10:  # Multiple rows with pipes = likely a table
            return True
        
        # Check for markdown table row pattern: | cell | cell |
        if re.search(r'\|[^|]+\|[^|]+\|', text):
            return True
        
        # For non-markdown tables, require stronger indicators
        # Financial tables usually declare units (in millions, etc.)
        has_units = bool(re.search(r'(?:in\s+millions|in\s+thousands|currency\s+in)', text_lower[:1000]))
        
        # Check for column headers typical in financial statements
        has_headers = bool(re.search(
            r'(?:particulars|description|assets|liabilities|equity)',
            text_lower[:2000]  # Check header area
        ))
        
        has_date = bool(re.search(
            r'(?:as\s+(?:at|on)|year\s+ended|31.*?(?:march|mar)|september|december|20\d{2})',
            text_lower
        ))
        
        numbers = re.findall(r'[\d,]+(?:\.\d{2})?', text)
        has_numbers = len(numbers) >= 4
        
        result = (has_units and has_numbers) or (has_headers and has_date and has_numbers)
        return result
        
        # Check for markdown table row pattern: | cell | cell |
        if re.search(r'\|[^|]+\|[^|]+\|', text):
            return True
        
        # For non-markdown tables, require stronger indicators
        # Financial tables usually declare units (in millions, etc.)
        has_units = bool(re.search(r'(?:in\s+millions|in\s+thousands|currency\s+in)', text_lower[:1000]))
        
        # Check for column headers typical in financial statements
        has_headers = bool(re.search(
            r'(?:particulars|description|assets|liabilities|equity)',
            text_lower[:2000]  # Check header area
        ))
        
        has_date = bool(re.search(
            r'(?:as\s+(?:at|on)|year\s+ended|31.*?(?:march|mar)|september|december|20\d{2})',
            text_lower
        ))
        
        numbers = re.findall(r'[\d,]+(?:\.\d{2})?', text)
        has_numbers = len(numbers) >= 4
        
        result = (has_units and has_numbers) or (has_headers and has_date and has_numbers)
        
        # DEBUG: Trace why specific pages are being flagged
        snippet = text_lower[:100].replace('\n', ' ')
        
        reason = []
        if pipe_count >= 10: reason.append("pipes>=10")
        if re.search(r'\|[^|]+\|[^|]+\|', text): reason.append("md_row")
        if has_units and has_numbers: reason.append("units+nums")
        if has_headers and has_date and has_numbers: reason.append("heuristic")
        
        # Re-check TOC for debug
        is_toc = False
        header_text = text_lower[:1000]
        if re.search(r'(?:index\s+to|table\s+of\s+contents|financial\s+statement\s+schedule|supplementary\s+data)', header_text):
            is_toc = True
            
        print(f"DEBUG TABLE DETECT: '{snippet}...' -> Res={result} (TOC={is_toc}, Reasons={reason})")
            
        return result
            
        return result
    
    def detect_year_labels(self, text: str) -> Tuple[str, str]:
        """
        Extract year labels from text.
        
        Returns:
            Tuple of (current_year_label, previous_year_label)
        """
        text_sample = text[:3000]
        years_found = []
        
        patterns = [
            r'(?:31|30)\s*(?:st|nd|rd|th)?\s*(?:March|Mar|December|Dec)[,\s]*(20\d{2})',
            r'(?:March|December)\s+(?:31|30)[,\s]*(20\d{2})',
            r'\b(20\d{2})\s*[-–]\s*(\d{2,4})\b',
            r'FY\s*(20\d{2})',
            r'(?:year|period)\s+ended.*?(20\d{2})',
            r'\b(20\d{2})\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_sample, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        if m:
                            try:
                                year = int(m) if len(m) == 4 else int(f"20{m}")
                                if 2015 <= year <= 2030:
                                    years_found.append(year)
                            except ValueError:
                                pass
                else:
                    try:
                        year = int(match)
                        if 2015 <= year <= 2030:
                            years_found.append(year)
                    except ValueError:
                        pass
        
        if not years_found:
            return ("Current Year", "Previous Year")
        
        unique_years = sorted(set(years_found), reverse=True)
        
        if len(unique_years) >= 2:
            return (f"FY {unique_years[0]}", f"FY {unique_years[1]}")
        else:
            return (f"FY {unique_years[0]}", f"FY {unique_years[0] - 1}")
