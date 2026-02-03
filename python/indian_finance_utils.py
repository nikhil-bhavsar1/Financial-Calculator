
"""
Indian Numbering, Units, and Date Parsing Utilities.
Enhanced for Ind AS compliance.
"""
import re
from datetime import datetime
from typing import Optional, Tuple, Any

class IndianNumberParser:
    """
    Handle Indian numbering: lakhs, crores, arabs with proper comma placement
    """
    
    INDIAN_UNITS = {
        'hundred': 1e2,
        'thousand': 1e3,
        'thousands': 1e3,
        'lakh': 1e5,
        'lakhs': 1e5,
        'lac': 1e5,
        'lacs': 1e5,
        'crore': 1e7,
        'crores': 1e7,
        'cr': 1e7,
        'arab': 1e9,
        'arabs': 1e9,
        'million': 1e6,
        'millions': 1e6,
        'mn': 1e6,
        'billion': 1e9,
        'billions': 1e9,
        'bn': 1e9,
    }
    
    def parse_indian_formatted_number(self, number_str: str) -> Optional[float]:
        """
        Parse numbers with Indian comma system:
        "1,25,40,500" = 12,540,500 (1 crore 25 lakhs 40 thousand 500)
        vs US: "12,540,500"
        """
        if not number_str or number_str.strip() in ['-', '', '—']:
            return 0.0
        
        # Remove currency symbols and whitespace
        clean = number_str.replace('₹', '').replace('Rs.', '').replace('Rs', '').replace('INR', '').strip()
        
        # Handle parentheses for negative (Ind AS common)
        is_negative = '(' in clean and ')' in clean
        clean = clean.replace('(', '').replace(')', '').replace(',', '')
        
        try:
            value = float(clean)
            return -value if is_negative else value
        except ValueError:
            return None
    
    def detect_scale_from_header(self, header_text: str) -> tuple:
        """
        Detect scale from table header text:
        "Rs. in Lakhs" → (100000, 'INR')
        "₹ Crores" → (10000000, 'INR')
        "Rupees in millions" → (1000000, 'INR')
        """
        header_lower = header_text.lower()
        
        # Check for Indian units
        for unit, multiplier in self.INDIAN_UNITS.items():
            if unit in header_lower:
                # Determine currency
                if any(x in header_lower for x in ['$', 'usd', 'us$', 'dollar']):
                    currency = 'USD'
                elif any(x in header_lower for x in ['€', 'euro', 'eur']):
                    currency = 'EUR'
                else:
                    # Default assumption is INR for Indian terms
                    currency = 'INR'
                return (multiplier, currency)
        
        # Default: actuals (no multiplier)
        return (1, 'INR')
    
    def convert_to_absolute(self, value: float, scale: float) -> float:
        """Apply detected scale to get absolute number"""
        return value * scale if value is not None else 0.0
    
    def parse_mixed_indian_us_format(self, number_str: str) -> float:
        """
        Handle mixed formats like "12.50" which could be:
        - 12.50 lakhs (in "Rs. Lakhs" table)
        - 12.50 crores (in "Rs. Crores" table)
        - 12.50 actuals (in "Rs." table)
        """
        # Try Indian format detection first
        if not number_str: return 0.0
        parts = number_str.split(',')
        
        if len(parts) > 2:
            # Check if Indian format (3,2,2... from right)
            # Last 3 digits, then 2, then 2...
            if len(parts[-1]) == 3 and len(parts[-2]) == 2:
                # Indian format: 1,25,40,500
                return float(number_str.replace(',', ''))
        
        # Standard international format or simple float
        try:
             return float(number_str.replace(',', ''))
        except:
             return 0.0

class IndianDateParser:
    """
    Handle Indian date formats: 31.03.2023, 31-Mar-2023, As at 31st March, 2023
    """
    
    INDIAN_DATE_PATTERNS = [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # 31.03.2023
        r'(\d{1,2})-(\w+)-(\d{4})',         # 31-Mar-2023
        r'(\d{1,2})(?:st|nd|rd|th)?\s+(\w+),?\s+(\d{4})',  # 31st March, 2023
        r'as\s+at\s+(\d{1,2})(?:\.\d{1,2}\.\d{4})?',  # As at 31.03.2023
        r'for\s+the\s+year\s+ended\s+(\d{1,2}).(\d{1,2}).(\d{4})',
        r'for\s+the\s+period\s+ended\s+(\d{1,2}).(\d{1,2}).(\d{4})',
    ]
    
    INDIAN_MONTHS = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date object using regex patterns."""
        for pattern in self.INDIAN_DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                # Basic parsing logic (simplified)
                try:
                    day, month, year = groups[0], groups[1], groups[2]
                    
                    # Convert month name to number if needed
                    if not month.isdigit():
                         month_num = self.INDIAN_MONTHS.get(month.lower()[:3], 1)
                    else:
                         month_num = int(month)
                         
                    return datetime(int(year), month_num, int(day))
                except Exception:
                    continue
        return None

    def _get_fiscal_year(self, date) -> Optional[int]:
        """Indian fiscal year: April 1 - March 31"""
        if not date:
            return None
        if date.month >= 4:
            return date.year + 1  # FY 2024 if date is Apr 2023 - Mar 2024
        return date.year

    def _get_year_start(self, date) -> Optional[datetime]:
        """Get start of fiscal year."""
        if not date: return None
        fy = self._get_fiscal_year(date)
        return datetime(fy-1, 4, 1)

    def _get_quarter(self, date) -> Optional[int]:
        """Get fiscal quarter (Apr-Jun = Q1, Jul-Sep = Q2, Oct-Dec = Q3, Jan-Mar = Q4)"""
        if not date:
            return None
        month = date.month
        if month in [4, 5, 6]:
            return 1
        elif month in [7, 8, 9]:
            return 2
        elif month in [10, 11, 12]:
            return 3
        else:
            return 4

    def parse_period_header(self, header_text: str) -> Optional[dict]:
        """
        Extract period information from column headers
        """
        header_lower = header_text.lower()
        date = self._extract_date(header_text)
        
        if not date:
            return None

        # Balance sheet date
        if 'as at' in header_lower or 'as on' in header_lower:
            return {
                'type': 'balance_sheet',
                'period_type': 'point_in_time',
                'date': date,
                'fiscal_year': self._get_fiscal_year(date),
                'label': f"As at {date.strftime('%d-%b-%Y')}"
            }
        
        # Income statement period
        if 'year ended' in header_lower or 'period ended' in header_lower:
             # Check if quarterly
             if 'quarter' in header_lower:
                quarter = self._get_quarter(date)
                return {
                    'type': 'income_statement',
                    'period_type': 'quarterly',
                    'end_date': date,
                    'quarter': quarter,
                    'fiscal_year': self._get_fiscal_year(date),
                    'label': f"Q{quarter} FY {self._get_fiscal_year(date)}"
                }
             else:
                return {
                    'type': 'income_statement',
                    'period_type': 'annual',
                    'end_date': date,
                    'start_date': self._get_year_start(date),
                    'fiscal_year': self._get_fiscal_year(date),
                    'label': f"FY {self._get_fiscal_year(date)}"
                }
        
        return None

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Public method for date parsing used by tests and other modules."""
        return self._extract_date(date_str)

class UnitDetector:
    """
    Specialized detector for financial units (Lakhs, Crores, Millions).
    """
    
    UNITS_MAP = {
        'lakh': 100000.0,
        'lakhs': 100000.0,
        'lac': 100000.0,
        'lacs': 100000.0,
        'crore': 10000000.0,
        'crores': 10000000.0,
        'cr': 10000000.0,
        'million': 1000000.0,
        'millions': 1000000.0,
        'mn': 1000000.0,
        'billion': 1000000000.0,
        'billions': 1000000000.0,
        'bn': 1000000000.0,
        'thousand': 1000.0,
        'thousands': 1000.0,
        'hundred': 100.0,
    }
    
    def detect_multiplier(self, text: str) -> float:
        """
        Detect multiplier from text like "Rs. in Crores" or "(₹ in millions)".
        Defaults to 1.0 if no unit is found.
        """
        if not text:
            return 1.0
            
        text_lower = text.lower()
        
        # Sort units by length descending to match longest possible (e.g. "millions" before "million")
        for unit in sorted(self.UNITS_MAP.keys(), key=len, reverse=True):
            if unit in text_lower:
                return self.UNITS_MAP[unit]
                
        return 1.0
