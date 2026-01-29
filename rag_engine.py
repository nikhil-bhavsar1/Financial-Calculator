import json
import re
import math
from collections import Counter

# Import unified terminology map
try:
    from terminology_keywords import (
        TERMINOLOGY_MAP, KEYWORD_BOOST, KEYWORD_TO_TERM,
        get_metric_ids_for_term, get_term_for_keyword, get_boost_for_keyword,
        get_all_keywords, get_standards_for_term
    )
    USE_TERMINOLOGY_MAP = True
except ImportError:
    USE_TERMINOLOGY_MAP = False


class RAGEngine:
    def __init__(self):
        self.chunks = []
        self.corpus_stats = {}  # For IDF
        
        # Use unified terminology map if available, else fallback to legacy
        if USE_TERMINOLOGY_MAP:
            self.financial_keywords = KEYWORD_BOOST
            self.terminology_map = TERMINOLOGY_MAP
        else:
            # Legacy fallback - IndAS/Financial Statement specific keywords with boost weights
            self.financial_keywords = {
                # IndAS Standards
                'indas': 2.5, 'ind as': 2.5, 'indian accounting standard': 2.5,
                'ifrs': 2.0, 'gaap': 2.0, 'icai': 1.8,
                
                # Core Financial Statements
                'balance sheet': 2.2, 'statement of profit and loss': 2.2,
                'profit and loss': 2.0, 'income statement': 2.0,
                'cash flow statement': 2.2, 'cash flow': 2.0,
                'statement of changes in equity': 2.2, 'notes to accounts': 2.0,
                'financial statements': 2.0, 'consolidated': 1.8, 'standalone': 1.5,
                'annual report': 1.5, 'quarterly report': 1.5,
                
                # Revenue & Income (IndAS 115)
                'revenue recognition': 2.5, 'revenue from contracts': 2.5,
                'performance obligation': 2.3, 'contract asset': 2.2,
                'contract liability': 2.2, 'transaction price': 2.2,
                'variable consideration': 2.2, 'revenue': 1.8,
                
                # Leases (IndAS 116)
                'lease': 2.0, 'lease liability': 2.3, 'right of use asset': 2.3,
                'rou asset': 2.2, 'operating lease': 2.0, 'finance lease': 2.0,
                'lease term': 1.8, 'lease payments': 1.8, 'lessee': 1.8, 'lessor': 1.8,
                
                # Financial Instruments (IndAS 109, 107, 32)
                'financial instruments': 2.3, 'financial assets': 2.2,
                'financial liabilities': 2.2, 'expected credit loss': 2.5,
                'ecl': 2.3, 'fvtpl': 2.3, 'fvoci': 2.3, 'amortised cost': 2.2,
                'amortized cost': 2.2, 'hedge accounting': 2.3, 'hedging': 2.0,
                'derivative': 2.0, 'derivatives': 2.0, 'fair value hedge': 2.2,
                'cash flow hedge': 2.2, 'credit risk': 2.0, 'liquidity risk': 2.0,
                'market risk': 2.0, 'impairment of financial assets': 2.3,
                
                # Fair Value (IndAS 113)
                'fair value': 2.2, 'fair value measurement': 2.3,
                'level 1': 1.8, 'level 2': 1.8, 'level 3': 1.8,
                'fair value hierarchy': 2.2, 'observable inputs': 2.0,
                'unobservable inputs': 2.0, 'valuation technique': 2.0,
                
                # PPE & Intangibles (IndAS 16, 38)
                'property plant and equipment': 2.2, 'ppe': 2.0,
                'depreciation': 2.0, 'useful life': 1.8, 'residual value': 1.8,
                'intangible assets': 2.2, 'amortization': 2.0, 'amortisation': 2.0,
                'goodwill': 2.2, 'impairment': 2.2, 'impairment loss': 2.3,
                'recoverable amount': 2.2, 'value in use': 2.0,
                'carrying amount': 2.0, 'carrying value': 1.8,
                
                # Inventory (IndAS 2)
                'inventory': 2.0, 'inventories': 2.0, 'cost of inventory': 2.0,
                'net realisable value': 2.2, 'nrv': 2.0, 'fifo': 1.8,
                'weighted average': 1.8, 'cost formula': 1.8,
                
                # Provisions & Contingencies (IndAS 37)
                'provisions': 2.0, 'contingent liability': 2.3,
                'contingent liabilities': 2.3, 'contingent asset': 2.2,
                'onerous contract': 2.0, 'restructuring provision': 2.0,
                'legal claims': 1.8, 'warranty provision': 1.8,
                
                # Employee Benefits (IndAS 19)
                'employee benefits': 2.2, 'defined benefit': 2.2,
                'defined contribution': 2.0, 'gratuity': 2.0,
                'leave encashment': 1.8, 'actuarial': 2.0,
                'actuarial valuation': 2.2, 'pension': 1.8,
                'post employment benefits': 2.0, 'remeasurement': 2.0,
                
                # Income Taxes (IndAS 12)
                'deferred tax': 2.3, 'deferred tax asset': 2.2,
                'deferred tax liability': 2.2, 'current tax': 2.0,
                'income tax': 2.0, 'tax expense': 1.8, 'temporary difference': 2.2,
                'temporary differences': 2.2, 'tax base': 2.0,
                'mat credit': 2.0, 'minimum alternate tax': 2.0,
                
                # Business Combinations (IndAS 103)
                'business combination': 2.3, 'acquisition': 2.0,
                'purchase consideration': 2.2, 'bargain purchase': 2.0,
                'acquisition date': 2.0, 'acquiree': 1.8, 'acquirer': 1.8,
                
                # Consolidation (IndAS 110, 111, 112, 28)
                'consolidation': 2.0, 'subsidiary': 2.0, 'subsidiaries': 2.0,
                'associate': 2.0, 'joint venture': 2.0, 'joint arrangement': 2.0,
                'equity method': 2.2, 'non controlling interest': 2.2,
                'nci': 2.0, 'control': 1.8, 'significant influence': 2.0,
                
                # Related Parties (IndAS 24)
                'related party': 2.3, 'related parties': 2.3,
                'related party transactions': 2.5, 'related party disclosures': 2.3,
                'key management personnel': 2.2, 'kmp': 2.0,
                
                # Segment Reporting (IndAS 108)
                'segment reporting': 2.3, 'operating segment': 2.2,
                'reportable segment': 2.0, 'segment revenue': 2.0,
                'segment result': 2.0, 'segment assets': 2.0,
                
                # EPS (IndAS 33)
                'earnings per share': 2.3, 'eps': 2.0, 'basic eps': 2.0,
                'diluted eps': 2.0, 'weighted average shares': 2.0,
                
                # Other Comprehensive Income
                'other comprehensive income': 2.2, 'oci': 2.0,
                'total comprehensive income': 2.0, 'reclassification': 1.8,
                
                # General Financial Terms
                'assets': 1.5, 'liabilities': 1.5, 'equity': 1.8,
                'reserves': 1.5, 'retained earnings': 1.8, 'share capital': 1.8,
                'borrowings': 1.8, 'debt': 1.5, 'trade receivables': 1.8,
                'trade payables': 1.8, 'capital': 1.5, 'dividend': 1.5,
                'profit': 1.5, 'loss': 1.5, 'expense': 1.3, 'income': 1.3,
                
                # Accounting Policies & Disclosures
                'significant accounting policies': 2.3, 'accounting policy': 2.0,
                'accounting policies': 2.0, 'disclosure': 1.8, 'disclosures': 1.8,
                'recognition': 1.8, 'measurement': 1.8, 'derecognition': 2.0,
                'presentation': 1.5, 'critical estimates': 2.2,
                'critical accounting judgments': 2.2, 'judgments': 1.8,
                'estimates': 1.5, 'assumptions': 1.5,
                
                # First-time Adoption (IndAS 101)
                'first time adoption': 2.3, 'transition': 2.0,
                'opening balance sheet': 2.0, 'deemed cost': 2.0,
                
                # Events after Reporting Period (IndAS 10)
                'events after reporting period': 2.3, 'subsequent events': 2.2,
                'adjusting events': 2.0, 'non adjusting events': 2.0,
            }
            self.terminology_map = {}
        
        # IndAS Standard Number Mappings for context
        self.indas_standards = {
            '1': 'Presentation of Financial Statements',
            '2': 'Inventories',
            '7': 'Statement of Cash Flows',
            '8': 'Accounting Policies, Changes in Accounting Estimates and Errors',
            '10': 'Events after the Reporting Period',
            '12': 'Income Taxes',
            '16': 'Property, Plant and Equipment',
            '19': 'Employee Benefits',
            '20': 'Accounting for Government Grants',
            '21': 'Effects of Changes in Foreign Exchange Rates',
            '23': 'Borrowing Costs',
            '24': 'Related Party Disclosures',
            '27': 'Separate Financial Statements',
            '28': 'Investments in Associates and Joint Ventures',
            '32': 'Financial Instruments: Presentation',
            '33': 'Earnings per Share',
            '34': 'Interim Financial Reporting',
            '36': 'Impairment of Assets',
            '37': 'Provisions, Contingent Liabilities and Contingent Assets',
            '38': 'Intangible Assets',
            '40': 'Investment Property',
            '41': 'Agriculture',
            '101': 'First-time Adoption of Indian Accounting Standards',
            '102': 'Share-based Payment',
            '103': 'Business Combinations',
            '104': 'Insurance Contracts',
            '105': 'Non-current Assets Held for Sale and Discontinued Operations',
            '106': 'Exploration for and Evaluation of Mineral Resources',
            '107': 'Financial Instruments: Disclosures',
            '108': 'Operating Segments',
            '109': 'Financial Instruments',
            '110': 'Consolidated Financial Statements',
            '111': 'Joint Arrangements',
            '112': 'Disclosure of Interests in Other Entities',
            '113': 'Fair Value Measurement',
            '114': 'Regulatory Deferral Accounts',
            '115': 'Revenue from Contracts with Customers',
            '116': 'Leases',
            '117': 'Insurance Contracts',
        }
        
        # Financial abbreviations/acronyms expansion
        self.acronym_map = {
            'ppe': 'property plant equipment',
            'rou': 'right of use',
            'ecl': 'expected credit loss',
            'oci': 'other comprehensive income',
            'eps': 'earnings per share',
            'fvtpl': 'fair value through profit loss',
            'fvoci': 'fair value through other comprehensive income',
            'cfs': 'cash flow statement',
            'bs': 'balance sheet',
            'pl': 'profit loss',
            'pnl': 'profit and loss',
            'mat': 'minimum alternate tax',
            'dtl': 'deferred tax liability',
            'dta': 'deferred tax asset',
            'nrv': 'net realisable value',
            'nci': 'non controlling interest',
            'kmp': 'key management personnel',
            'cgst': 'central goods services tax',
            'sgst': 'state goods services tax',
            'igst': 'integrated goods services tax',
            'gst': 'goods services tax',
            'tds': 'tax deducted source',
            'esop': 'employee stock option',
        }
        
        # Synonyms for query expansion
        self.synonyms = {
            'revenue': ['income', 'sales', 'turnover', 'receipts'],
            'profit': ['earnings', 'income', 'gain', 'surplus'],
            'loss': ['deficit', 'impairment', 'write off', 'writedown'],
            'asset': ['property', 'resource', 'holding'],
            'liability': ['obligation', 'debt', 'payable', 'dues'],
            'depreciation': ['amortization', 'amortisation', 'writedown'],
            'receivable': ['debtor', 'dues', 'outstanding'],
            'payable': ['creditor', 'dues', 'outstanding'],
            'inventory': ['stock', 'inventories', 'goods'],
            'fair value': ['market value', 'current value'],
            'carrying amount': ['book value', 'carrying value', 'net book value'],
            'impairment': ['writedown', 'diminution', 'loss in value'],
            'provision': ['reserve', 'allowance', 'accrual'],
            'borrowing': ['loan', 'debt', 'credit facility'],
            'subsidiary': ['sub', 'group company', 'controlled entity'],
        }
        
        # Section type patterns for financial documents
        self.section_patterns = [
            (r'^(?:Note|Notes)\s*(?:No\.?)?\s*(\d+)', 'note'),
            (r'^Schedule\s*[A-Z0-9]+', 'schedule'),
            (r'^(?:Significant\s+)?Accounting\s+Polic(?:y|ies)', 'accounting_policy'),
            (r'^Related\s+Party', 'related_party'),
            (r'^Segment\s+(?:Information|Reporting|Report)', 'segment'),
            (r'^Contingent\s+(?:Liabilities?|Assets?)', 'contingent'),
            (r'^(?:Deferred\s+)?(?:Income\s+)?Tax', 'tax'),
            (r'^(?:Property,?\s*Plant\s*(?:and|&)\s*Equipment|PPE|Fixed\s+Assets)', 'ppe'),
            (r'^(?:Intangible\s+Assets?)', 'intangible'),
            (r'^(?:Financial\s+Instruments?)', 'financial_instruments'),
            (r'^(?:Fair\s+Value)', 'fair_value'),
            (r'^(?:Inventories?)', 'inventory'),
            (r'^(?:Trade\s+(?:Receivables?|Payables?))', 'trade'),
            (r'^(?:Borrowings?|Loans?|Debt)', 'borrowings'),
            (r'^(?:Revenue|Revenue\s+from)', 'revenue'),
            (r'^(?:Employee\s+Benefits?|Gratuity|Leave)', 'employee_benefits'),
            (r'^(?:Earnings?\s+[Pp]er\s+[Ss]hare|EPS)', 'eps'),
            (r'^(?:Leases?|Right.of.Use)', 'lease'),
            (r'^(?:Provisions?)', 'provisions'),
            (r'^(?:Share\s+Capital|Equity)', 'equity'),
            (r'^(?:Cash\s+(?:and\s+Cash\s+)?Equivalents?|Bank\s+Balances?)', 'cash'),
            (r'^(?:Investment|Investments)', 'investments'),
            (r'^(?:Goodwill)', 'goodwill'),
            (r'^(?:Business\s+Combination|Acquisition)', 'business_combination'),
        ]
        
        # Domain stopwords
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
            'their', 'we', 'our', 'you', 'your', 'he', 'she', 'him', 'her',
            'which', 'who', 'whom', 'what', 'when', 'where', 'why', 'how',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
            'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'also', 'now', 'here', 'there', 'then', 'once',
            'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
            'again', 'further', 'any', 'if', 'because', 'until', 'while',
            'during', 'before', 'after', 'between', 'into', 'through',
            'about', 'against', 'including', 'without', 'within', 'along',
            'following', 'across', 'behind', 'beyond', 'plus', 'except',
            'being', 'having', 'doing', 'made', 'found', 'based', 'given',
            'per', 'etc', 'ie', 'eg', 'viz', 'sr', 'no', 'nos', 'mr', 'mrs', 'ms',
        }

    def index_document(self, full_text):
        """
        Splits document into page-based chunks and builds index.
        Expects '--- Page X ---' delimiters.
        Enhanced for IndAS Financial Statements.
        """
        self.chunks = []
        
        # Preprocess text for financial documents
        full_text = self._preprocess_financial_text(full_text)
        
        # Split by page delimiter
        parts = re.split(r'--- Page (\d+) ---\n', full_text)
        
        current_chunks = []
        
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                page_num = parts[i]
                content = parts[i+1] if i+1 < len(parts) else ""
                
                # Enhanced chunking for financial documents
                sections = self._split_financial_sections(content)
                
                for s_idx, section in enumerate(sections):
                    if not section['text'].strip():
                        continue
                    
                    chunk = self._create_chunk(
                        chunk_id=f"p{page_num}_s{s_idx}",
                        page=int(page_num),
                        section=section
                    )
                    current_chunks.append(chunk)
        else:
            # Fallback for plain text without page markers
            sections = self._split_financial_sections(full_text)
            for s_idx, section in enumerate(sections):
                if not section['text'].strip():
                    continue
                
                chunk = self._create_chunk(
                    chunk_id=f"raw_{s_idx}",
                    page=1,
                    section=section
                )
                current_chunks.append(chunk)
                 
        self.chunks = current_chunks
        self._build_stats()
        return json.dumps({"count": len(self.chunks)})

    def _create_chunk(self, chunk_id, page, section):
        """Create a chunk with all metadata."""
        tokens = self._tokenize(section['text'])
        financial_terms = self._extract_financial_terms(section['text'])
        
        return {
            "id": chunk_id,
            "page": page,
            "text": section['text'],
            "section_type": section.get('type', 'general'),
            "section_header": section.get('header', ''),
            "tokens": Counter(tokens),
            "financial_terms": financial_terms,
            "len": len(tokens),
            "numbers": self._extract_financial_numbers(section['text']),
            "indas_refs": self._extract_indas_references(section['text']),
            "has_table": self._is_table_content(section['text']),
        }

    def _preprocess_financial_text(self, text):
        """Preprocess text for better financial document handling."""
        # Normalize Ind AS variations
        text = re.sub(r'Ind[\s\-]*AS[\s\-]*(\d+)', r'IndAS \1', text, flags=re.IGNORECASE)
        text = re.sub(r'IND[\s\-]*AS[\s\-]*(\d+)', r'IndAS \1', text, flags=re.IGNORECASE)
        
        # Normalize currency symbols
        text = re.sub(r'₹\s*', 'INR ', text)
        text = re.sub(r'Rs\.?\s*', 'INR ', text)
        text = re.sub(r'\$\s*', 'USD ', text)
        text = re.sub(r'€\s*', 'EUR ', text)
        
        # Normalize common financial abbreviations
        text = re.sub(r'\bP\s*&\s*L\b', 'Profit and Loss', text, flags=re.IGNORECASE)
        text = re.sub(r'\bB/S\b', 'Balance Sheet', text, flags=re.IGNORECASE)
        text = re.sub(r'\bPBT\b', 'Profit Before Tax', text, flags=re.IGNORECASE)
        text = re.sub(r'\bPAT\b', 'Profit After Tax', text, flags=re.IGNORECASE)
        text = re.sub(r'\bEBITDA\b', 'Earnings Before Interest Tax Depreciation Amortization', text, flags=re.IGNORECASE)
        
        # Handle Indian number notation
        text = re.sub(r'(\d+(?:[,\d]*)?(?:\.\d+)?)\s*(?:lakhs?|lacs?)\b', r'\1 lakhs', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+(?:[,\d]*)?(?:\.\d+)?)\s*(?:crores?|crs?\.?)\b', r'\1 crores', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+(?:[,\d]*)?(?:\.\d+)?)\s*(?:millions?|mn\.?)\b', r'\1 million', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+(?:[,\d]*)?(?:\.\d+)?)\s*(?:billions?|bn\.?)\b', r'\1 billion', text, flags=re.IGNORECASE)
        
        # Normalize fiscal year references
        text = re.sub(r'FY\s*[\'"]?(\d{2,4})[-/]?(\d{2,4})?', r'FY\1\2', text, flags=re.IGNORECASE)
        
        return text

    def _split_financial_sections(self, content):
        """
        Split content into sections recognizing financial document structure.
        """
        sections = []
        
        # First try to split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for para in paragraphs:
            section_type = 'general'
            header = ''
            
            # Check if paragraph starts with a known section pattern
            for pattern, s_type in self.section_patterns:
                match = re.match(pattern, para, re.IGNORECASE | re.MULTILINE)
                if match:
                    section_type = s_type
                    header = match.group(0)
                    break
            
            # Check for table-like content
            if self._is_table_content(para):
                if section_type == 'general':
                    section_type = 'table'
            
            # Check for note numbers in content
            note_match = re.search(r'\((?:Refer\s+)?Note\s*(?:No\.?)?\s*(\d+)\)', para, re.IGNORECASE)
            
            sections.append({
                'text': para,
                'type': section_type,
                'header': header,
                'referenced_note': note_match.group(1) if note_match else None
            })
        
        return sections if sections else [{'text': content, 'type': 'general', 'header': ''}]

    def _is_table_content(self, text):
        """Detect if content appears to be tabular data."""
        lines = text.split('\n')
        if len(lines) < 2:
            return False
        
        number_lines = 0
        for line in lines:
            numbers = re.findall(r'[\d,]+(?:\.\d+)?', line)
            if len(numbers) >= 2:
                number_lines += 1
        
        return number_lines >= len(lines) * 0.4

    def _tokenize(self, text):
        """Enhanced tokenization for financial documents."""
        text_lower = text.lower()
        
        # Preserve important financial terms before cleaning
        preserved = []
        
        # Preserve Ind AS references
        for match in re.finditer(r'indas\s*\d+', text_lower):
            preserved.append(match.group().replace(' ', ''))
        
        # Preserve percentages
        for match in re.finditer(r'\d+(?:\.\d+)?%', text_lower):
            preserved.append('pct_' + match.group().replace('%', ''))
        
        # Preserve financial numbers with units
        for match in re.finditer(r'\d+(?:\.\d+)?\s*(?:lakhs?|crores?|million|billion)', text_lower):
            preserved.append(match.group().replace(' ', '_'))
        
        # Preserve fiscal year references
        for match in re.finditer(r'fy\d{2,4}', text_lower):
            preserved.append(match.group())
        
        # Clean text for regular tokenization
        text_clean = re.sub(r'[^a-z0-9\s]', ' ', text_lower)
        tokens = text_clean.split()
        
        # Add preserved terms
        tokens.extend(preserved)
        
        # Expand acronyms
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(token)
            if token in self.acronym_map:
                expanded_tokens.extend(self.acronym_map[token].split())
        
        # Remove stopwords but keep financial terms
        filtered_tokens = []
        for token in expanded_tokens:
            if len(token) < 2:
                continue
            if token not in self.stopwords or self._is_financial_term(token):
                filtered_tokens.append(token)
        
        return filtered_tokens

    def _is_financial_term(self, token):
        """Check if a token is a significant financial term."""
        if token in self.financial_keywords:
            return True
        for kw in self.financial_keywords:
            if token in kw.split():
                return True
        return False

    def _extract_financial_terms(self, text):
        """Extract and count significant financial terms from text with metric mappings."""
        text_lower = text.lower()
        found_terms = {}
        
        # Check for multi-word financial terms first (longer terms first)
        for term, boost in sorted(self.financial_keywords.items(), 
                                   key=lambda x: len(x[0]), reverse=True):
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.findall(pattern, text_lower)
            count = len(matches)
            if count > 0:
                term_data = {'count': count, 'boost': boost}
                
                # Add metric mappings if using terminology map
                if USE_TERMINOLOGY_MAP and term in KEYWORD_TO_TERM:
                    term_keys = KEYWORD_TO_TERM[term]
                    term_data['term_keys'] = term_keys
                    # Collect all associated metrics
                    metrics = []
                    for tk in term_keys:
                        metrics.extend(get_metric_ids_for_term(tk))
                    term_data['metric_ids'] = list(set(metrics))
                
                found_terms[term] = term_data
        
        return found_terms
    
    def extract_terms_with_metrics(self, text):
        """
        Extract financial terms and return structured data with metric associations.
        Returns dict mapping term_key -> {keywords_found, metric_ids, category, standards}
        """
        if not USE_TERMINOLOGY_MAP:
            return {}
        
        text_lower = text.lower()
        results = {}
        
        for term_key, data in TERMINOLOGY_MAP.items():
            keywords_found = []
            for kw in data['keywords']:
                pattern = r'\b' + re.escape(kw.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    keywords_found.append(kw)
            
            if keywords_found:
                results[term_key] = {
                    'keywords_found': keywords_found,
                    'category': data['category'],
                    'metric_ids': data.get('metric_ids', []),
                    'standards': data.get('standards', {}),
                    'boost': data.get('boost', 1.0)
                }
        
        return results
    
    def get_metrics_for_extracted_terms(self, text):
        """
        Get list of applicable metric calculations based on terms found in text.
        Returns list of unique metric_ids that can be calculated from the data.
        """
        terms_data = self.extract_terms_with_metrics(text)
        all_metrics = set()
        
        for term_key, data in terms_data.items():
            for metric_id in data.get('metric_ids', []):
                all_metrics.add(metric_id)
        
        return list(all_metrics)

    def _extract_financial_numbers(self, text):
        """Extract financial numbers with context."""
        numbers = []
        
        # Pattern for numbers with optional currency and units
        patterns = [
            r'(?:INR|USD|EUR)\s*([\d,]+(?:\.\d+)?)\s*(?:lakhs?|crores?|million|billion)?',
            r'([\d,]+(?:\.\d+)?)\s*(?:lakhs?|crores?|million|billion)',
            r'([\d,]+(?:\.\d+)?)\s*%',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                numbers.append(match.group())
        
        return numbers[:20]  # Limit to avoid bloat

    def _extract_indas_references(self, text):
        """Extract Ind AS standard references with context."""
        refs = []
        pattern = r'(?:Ind[\s\-]*AS|IndAS)\s*(\d+)'
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            std_num = match.group(1)
            std_name = self.indas_standards.get(std_num, '')
            refs.append({
                'number': std_num,
                'full_ref': f"IndAS {std_num}",
                'name': std_name
            })
        
        # Deduplicate by number
        seen = set()
        unique_refs = []
        for ref in refs:
            if ref['number'] not in seen:
                seen.add(ref['number'])
                unique_refs.append(ref)
        
        return unique_refs

    def _build_stats(self):
        """Calculate IDF with financial term boosting."""
        doc_count = len(self.chunks)
        self.corpus_stats = {}
        if doc_count == 0: 
            return

        # Count document frequency for each token
        for chunk in self.chunks:
            for token in chunk['tokens']:
                self.corpus_stats[token] = self.corpus_stats.get(token, 0) + 1
        
        # Convert doc counts to IDF score with financial boosting
        for token, count in self.corpus_stats.items():
            base_idf = math.log((doc_count + 1) / (count + 1)) + 1
            
            # Apply boost for financial terms
            boost = 1.0
            if token in self.financial_keywords:
                boost = self.financial_keywords[token]
            elif self._is_financial_term(token):
                boost = 1.3
            
            self.corpus_stats[token] = base_idf * boost

    def _expand_query(self, query_tokens):
        """Expand query with synonyms and related financial terms."""
        expanded = list(query_tokens)
        
        for token in query_tokens:
            # Add synonyms
            if token in self.synonyms:
                expanded.extend(self.synonyms[token])
            
            # Expand acronyms
            if token in self.acronym_map:
                expanded.extend(self.acronym_map[token].split())
        
        return list(set(expanded))

    def search(self, query, top_k=5, section_filter=None, page_range=None, 
               include_tables=True, boost_indas=True):
        """
        Enhanced BM25 ranking with financial term boosting.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            section_filter: Optional filter for section types
            page_range: Optional tuple (start_page, end_page)
            include_tables: Whether to include table sections
            boost_indas: Whether to boost Ind AS references
        """
        if not self.chunks:
            return json.dumps([])

        query_lower = query.lower()
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return json.dumps([])

        # Expand query with synonyms
        expanded_tokens = self._expand_query(query_tokens)
        
        # Check for Ind AS specific search
        indas_search = []
        for match in re.finditer(r'(?:ind\s*as|indas)\s*(\d+)', query_lower):
            indas_search.append(match.group(1))
        
        # Check for section-specific queries
        query_section_hints = self._detect_section_hints(query_lower)
        
        scores = []
        avg_doc_len = sum(c['len'] for c in self.chunks) / len(self.chunks) if self.chunks else 1
        
        # BM25 parameters (tuned for financial docs)
        k1 = 1.2
        b = 0.75

        for chunk in self.chunks:
            # Apply filters
            if section_filter and chunk.get('section_type') != section_filter:
                continue
            if page_range:
                if chunk['page'] < page_range[0] or chunk['page'] > page_range[1]:
                    continue
            if not include_tables and chunk.get('has_table'):
                continue
            
            score = 0
            doc_len = chunk['len']
            
            # BM25 scoring with expanded tokens
            for q_token in expanded_tokens:
                if q_token not in chunk['tokens']:
                    continue
                
                term_freq = chunk['tokens'][q_token]
                idf = self.corpus_stats.get(q_token, 0)
                
                # BM25 term weight
                numerator = idf * term_freq * (k1 + 1)
                denominator = term_freq + k1 * (1 - b + b * (doc_len / avg_doc_len))
                score += numerator / denominator
            
            # Boost for financial term matches
            for term, data in chunk.get('financial_terms', {}).items():
                term_words = set(term.split())
                query_words = set(query_tokens)
                if term in query_lower or term_words & query_words:
                    score += data['count'] * data['boost'] * 0.5
            
            # Boost for Ind AS reference matches
            if boost_indas and indas_search:
                for ref in chunk.get('indas_refs', []):
                    if ref['number'] in indas_search:
                        score += 5.0  # Strong boost for exact Ind AS match
            
            # Section type relevance boost
            section_type = chunk.get('section_type', 'general')
            if section_type != 'general':
                score *= 1.15
                
                # Extra boost if query hints at the section type
                if section_type in query_section_hints:
                    score *= 1.4
            
            # Slight boost for chunks with Ind AS references (more authoritative)
            if chunk.get('indas_refs'):
                score *= 1.05
            
            if score > 0:
                scores.append((score, chunk))

        # Sort by score desc
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Return Top K
        results = []
        for score, chunk in scores[:top_k]:
            indas_refs_simple = [ref['full_ref'] for ref in chunk.get('indas_refs', [])]
            
            results.append({
                "id": chunk['id'],
                "page": chunk['page'],
                "text": chunk['text'],
                "score": round(score, 4),
                "section_type": chunk.get('section_type', 'general'),
                "section_header": chunk.get('section_header', ''),
                "indas_refs": indas_refs_simple,
                "financial_terms": list(chunk.get('financial_terms', {}).keys())[:10],
                "has_table": chunk.get('has_table', False)
            })
            
        return json.dumps(results)

    def _detect_section_hints(self, query):
        """Detect which section types the query might be targeting."""
        hints = set()
        
        section_keywords = {
            'note': ['note', 'notes', 'disclosure'],
            'accounting_policy': ['accounting policy', 'policies', 'significant accounting'],
            'related_party': ['related party', 'related parties', 'kmp', 'key management'],
            'segment': ['segment', 'segments', 'operating segment'],
            'tax': ['tax', 'deferred tax', 'income tax', 'mat'],
            'revenue': ['revenue', 'income', 'sales', 'turnover'],
            'ppe': ['property', 'plant', 'equipment', 'ppe', 'fixed assets', 'depreciation'],
            'intangible': ['intangible', 'goodwill', 'amortization'],
            'fair_value': ['fair value', 'level 1', 'level 2', 'level 3', 'valuation'],
            'lease': ['lease', 'rou', 'right of use', 'lessee', 'lessor'],
            'provisions': ['provision', 'contingent', 'warranty'],
            'employee_benefits': ['employee benefit', 'gratuity', 'leave', 'pension', 'actuarial'],
            'borrowings': ['borrowing', 'loan', 'debt', 'credit facility'],
            'inventory': ['inventory', 'inventories', 'stock', 'nrv'],
            'financial_instruments': ['financial instrument', 'derivative', 'hedge', 'ecl'],
            'eps': ['earnings per share', 'eps', 'diluted'],
            'equity': ['share capital', 'equity', 'reserves', 'retained earnings'],
        }
        
        for section_type, keywords in section_keywords.items():
            for kw in keywords:
                if kw in query:
                    hints.add(section_type)
                    break
        
        return hints

    def search_by_indas(self, standard_number, top_k=10):
        """
        Search specifically for content related to a particular Ind AS standard.
        """
        if not self.chunks:
            return json.dumps([])
        
        standard_number = str(standard_number)
        results = []
        
        for chunk in self.chunks:
            indas_refs = chunk.get('indas_refs', [])
            matching_refs = [r for r in indas_refs if r['number'] == standard_number]
            
            if matching_refs:
                # Score based on reference count and financial term density
                score = len(matching_refs) * 3.0
                score += len(chunk.get('financial_terms', {})) * 0.2
                score += 1 if chunk.get('section_type') != 'general' else 0
                
                results.append({
                    "id": chunk['id'],
                    "page": chunk['page'],
                    "text": chunk['text'],
                    "score": round(score, 4),
                    "section_type": chunk.get('section_type', 'general'),
                    "indas_refs": [r['full_ref'] for r in indas_refs],
                    "standard_name": self.indas_standards.get(standard_number, '')
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return json.dumps(results[:top_k])

    def search_by_topic(self, topic, top_k=10):
        """
        Search by financial topic (maps to relevant Ind AS standards).
        """
        topic_mapping = {
            'revenue': ['115'],
            'lease': ['116'],
            'financial instruments': ['109', '107', '32'],
            'impairment': ['36'],
            'tax': ['12'],
            'employee benefits': ['19'],
            'ppe': ['16'],
            'intangible': ['38'],
            'inventory': ['2'],
            'provisions': ['37'],
            'related party': ['24'],
            'segment': ['108'],
            'fair value': ['113'],
            'consolidation': ['110', '111', '112'],
            'business combination': ['103'],
            'eps': ['33'],
            'presentation': ['1'],
            'cash flow': ['7'],
        }
        
        topic_lower = topic.lower()
        relevant_standards = []
        
        for key, standards in topic_mapping.items():
            if key in topic_lower or topic_lower in key:
                relevant_standards.extend(standards)
        
        if not relevant_standards:
            # Fall back to regular search
            return self.search(topic, top_k=top_k)
        
        # Search for all relevant standards
        all_results = []
        for std in set(relevant_standards):
            results = json.loads(self.search_by_indas(std, top_k=top_k))
            all_results.extend(results)
        
        # Also add regular search results
        regular_results = json.loads(self.search(topic, top_k=top_k))
        all_results.extend(regular_results)
        
        # Deduplicate by chunk id and sort
        seen_ids = set()
        unique_results = []
        for r in sorted(all_results, key=lambda x: x['score'], reverse=True):
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                unique_results.append(r)
        
        return json.dumps(unique_results[:top_k])

    def get_document_summary(self):
        """
        Get a summary of the indexed document structure.
        """
        if not self.chunks:
            return json.dumps({})
        
        summary = {
            'total_chunks': len(self.chunks),
            'total_pages': len(set(c['page'] for c in self.chunks)),
            'page_range': {
                'min': min(c['page'] for c in self.chunks),
                'max': max(c['page'] for c in self.chunks)
            },
            'section_types': {},
            'indas_standards_referenced': [],
            'top_financial_terms': [],
            'table_chunks': sum(1 for c in self.chunks if c.get('has_table'))
        }
        
        # Count section types
        for chunk in self.chunks:
            s_type = chunk.get('section_type', 'general')
            summary['section_types'][s_type] = summary['section_types'].get(s_type, 0) + 1
        
        # Collect all Ind AS references with names
        all_refs = {}
        for chunk in self.chunks:
            for ref in chunk.get('indas_refs', []):
                if ref['number'] not in all_refs:
                    all_refs[ref['number']] = ref
        
        summary['indas_standards_referenced'] = sorted(
            [{'number': r['number'], 'name': r['name']} for r in all_refs.values()],
            key=lambda x: int(x['number'])
        )
        
        # Get top financial terms
        term_counts = Counter()
        for chunk in self.chunks:
            for term, data in chunk.get('financial_terms', {}).items():
                term_counts[term] += data['count']
        
        summary['top_financial_terms'] = [
            {'term': t[0], 'count': t[1]} 
            for t in term_counts.most_common(30)
        ]
        
        return json.dumps(summary)

    def get_notes_index(self):
        """
        Get an index of all notes found in the document.
        """
        if not self.chunks:
            return json.dumps([])
        
        notes = []
        for chunk in self.chunks:
            if chunk.get('section_type') == 'note':
                header = chunk.get('section_header', '')
                note_match = re.search(r'(\d+)', header)
                note_num = note_match.group(1) if note_match else 'Unknown'
                
                notes.append({
                    'note_number': note_num,
                    'header': header,
                    'page': chunk['page'],
                    'chunk_id': chunk['id'],
                    'preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
                })
        
        # Sort by note number
        notes.sort(key=lambda x: int(x['note_number']) if x['note_number'].isdigit() else 999)
        
        return json.dumps(notes)


rag = RAGEngine()