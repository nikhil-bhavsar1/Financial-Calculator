import json
import re
import math
import requests
import textwrap
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any, Generator
from dataclasses import dataclass, field

# Import unified terminology map
try:
    from python.terminology_keywords import (
        TERMINOLOGY_MAP, KEYWORD_BOOST, KEYWORD_TO_TERM,
        get_metric_ids_for_term, get_term_for_keyword, get_boost_for_keyword,
        get_all_keywords, get_standards_for_term
    )
    USE_TERMINOLOGY_MAP = True
except ImportError:
    USE_TERMINOLOGY_MAP = False


@dataclass
class ExplanationContext:
    """Structured context for LLM explanations"""
    query: str
    primary_chunks: List[Dict]
    supporting_chunks: List[Dict]
    indas_standards: List[Dict]
    entity_type: str  # standalone/consolidated
    statement_type: Optional[str]
    page_range: Tuple[int, int]
    related_notes: List[Dict]
    financial_summary: Dict
    iteration: int = 0
    confidence: float = 0.0


@dataclass
class LLMResponse:
    """Structured LLM response with metadata"""
    explanation: str
    citations: List[Dict]
    suggested_followups: List[str]
    confidence: float
    model_used: str
    tokens_used: int


class FinancialExplainer:
    """
    Handles LLM interactions for financial document explanation.
    Integrates with local Ollama instance.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2"  # Default model
        self.context_window = 8192  # Conservative for most local models
        self.max_retries = 3
        
    def set_model(self, model_name: str, context_window: int = 8192):
        """Configure which local model to use"""
        self.model = model_name
        self.context_window = context_window
    
    def explain(
        self, 
        context: ExplanationContext,
        explanation_type: str = "general",
        stream: bool = False
    ) -> LLMResponse:
        """
        Generate explanation based on retrieved context.
        
        Args:
            context: Structured context from RAG
            explanation_type: Type of explanation (indas, line_item, note, trend, ratio)
            stream: Whether to stream the response
        """
        # Build optimized prompt
        prompt = self._build_explanation_prompt(context, explanation_type)
        
        # Check if we need to iterate for better context
        if context.confidence < 0.7 and context.iteration < 2:
            return self._iterate_explanation(context, explanation_type)
        
        # Call local LLM
        response = self._call_ollama(prompt, stream)
        
        # Parse and structure response
        return self._structure_response(response, context)
    
    def _build_explanation_prompt(
        self, 
        context: ExplanationContext, 
        exp_type: str
    ) -> str:
        """Construct context-aware prompt for the LLM"""
        
        # Calculate available tokens for context (rough estimate)
        reserved_tokens = 1000  # For instructions, query, formatting
        available_tokens = self.context_window - reserved_tokens
        char_per_token = 4  # Conservative estimate
        max_chars = available_tokens * char_per_token
        
        # Build context string
        context_parts = []
        
        # 1. Document metadata
        meta_text = f"""Document Type: {context.entity_type.title()} Financial Statements
Statement Type: {context.statement_type or 'General'}
Pages: {context.page_range[0]} - {context.page_range[1]}
Query: {context.query}
"""
        context_parts.append(meta_text)
        
        # 2. Relevant IndAS Standards
        if context.indas_standards:
            standards_text = "Applicable Accounting Standards (Ind AS):\n"
            for std in context.indas_standards[:5]:  # Top 5 relevant
                standards_text += f"- Ind AS {std['number']}: {std['name']}\n"
            context_parts.append(standards_text)
        
        # 3. Primary Evidence (most relevant chunks)
        evidence_text = "Primary Evidence from Document:\n"
        for i, chunk in enumerate(context.primary_chunks[:5], 1):
            evidence_text += f"\n[Excerpt {i} - Page {chunk['page']}"
            if chunk.get('section_header'):
                evidence_text += f", {chunk['section_header']}"
            evidence_text += f"]:\n{chunk['text'][:800]}\n"
        context_parts.append(evidence_text)
        
        # 4. Supporting Context
        if context.supporting_chunks:
            support_text = "Additional Context:\n"
            for chunk in context.supporting_chunks[:3]:
                support_text += f"- Page {chunk['page']}: {chunk['text'][:300]}\n"
            context_parts.append(support_text)
        
        # 5. Related Notes (for note references)
        if context.related_notes and exp_type in ["note", "indas"]:
            notes_text = "Related Disclosures (Notes):\n"
            for note in context.related_notes[:3]:
                notes_text += f"- Note {note.get('note_number')}: {note.get('header', '')}\n"
            context_parts.append(notes_text)
        
        # Combine and truncate if necessary
        full_context = "\n".join(context_parts)
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "\n[Context truncated due to length]"
        
        # Type-specific instructions
        instructions = self._get_explanation_instructions(exp_type)
        
        prompt = f"""You are a Financial Analysis Assistant specializing in Indian Accounting Standards (Ind AS). 
Analyze the following document context and provide a detailed explanation.

{instructions}

{full_context}

Based on the above context from the uploaded financial document, provide a comprehensive explanation.
Cite specific page numbers and note references where applicable.
If the context is insufficient to answer accurately, state what additional information would be needed.

Response Format:
1. **Direct Answer**: Clear, concise explanation
2. **Detailed Analysis**: In-depth breakdown with specific numbers/dates from context
3. **Accounting Treatment**: How this is treated under applicable Ind AS standards
4. **Source References**: Page numbers and note numbers cited
5. **Related Concepts**: Other relevant areas in the document to examine

Explanation:"""
        
        return prompt
    
    def _get_explanation_instructions(self, exp_type: str) -> str:
        """Get specific instructions based on explanation type"""
        
        instructions = {
            "general": """Provide a comprehensive explanation of the query based on the document content. 
Focus on accuracy and cite specific data points.""",
            
            "indas": """Explain the specific Ind AS standard treatment shown in the document.
Include:
- Key requirements of the standard as applied
- How the company has implemented it (specific numbers/policies)
- Any disclosures made under this standard
- Comparison with previous year if applicable""",
            
            "line_item": """Explain this specific financial statement line item:
- Definition and composition per the document
- Amount and change from previous year
- Accounting policy applied
- Related notes for detailed breakdown
- Significance in context of overall financials""",
            
            "note": """Explain this specific note to the accounts:
- Purpose and content summary
- Key disclosures and numbers
- Accounting judgments/estimates involved
- Impact on financial statements
- Compliance with disclosure requirements""",
            
            "trend": """Analyze the trend or change:
- Calculate YoY or QoQ change percentages
- Explain reasons cited in the document
- Contextual significance (materiality)
- Impact on financial health/ratios
- Management commentary if available""",
            
            "ratio": """Explain this financial metric or ratio:
- Calculation methodology used
- Current vs previous period comparison
- Industry context if available
- Implications for liquidity/profitability/solvency"""
        }
        
        return instructions.get(exp_type, instructions["general"])
    
    def _iterate_explanation(
        self, 
        context: ExplanationContext, 
        exp_type: str
    ) -> LLMResponse:
        """Iterate query refinement when confidence is low"""
        
        # Expand query with synonyms and related terms
        expanded_queries = self._expand_query_for_iteration(context.query)
        
        # This would typically re-query the RAG engine, but since we're in the explainer,
        # we signal that more context is needed
        return LLMResponse(
            explanation=f"Insufficient context found for '{context.query}'. "
                       f"Attempting to search with expanded terms: {', '.join(expanded_queries[:3])}",
            citations=[],
            suggested_followups=expanded_queries,
            confidence=0.0,
            model_used=self.model,
            tokens_used=0
        )
    
    def _expand_query_for_iteration(self, query: str) -> List[str]:
        """Generate alternative queries for better context retrieval"""
        
        variations = [query]
        
        # Add IndAS standard references if applicable
        indas_match = re.search(r'ind\s*as\s*(\d+)', query, re.IGNORECASE)
        if not indas_match:
            # Try to map keywords to standards
            if 'revenue' in query.lower():
                variations.append(f"{query} Ind AS 115")
            elif 'lease' in query.lower():
                variations.append(f"{query} Ind AS 116")
            elif 'financial instrument' in query.lower():
                variations.append(f"{query} Ind AS 109")
        
        # Add entity type variations
        if 'standalone' not in query.lower() and 'consolidated' not in query.lower():
            variations.append(f"standalone {query}")
            variations.append(f"consolidated {query}")
        
        # Add year variations if not present
        if not re.search(r'\d{4}', query):
            variations.append(f"{query} current year")
            variations.append(f"{query} previous year")
        
        return variations
    
    def _call_ollama(self, prompt: str, stream: bool = False) -> Dict:
        """Call local Ollama instance"""
        
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 0.3,  # Lower for factual accuracy
                "num_predict": 2048,  # Reasonable length for explanations
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
        
        try:
            if stream:
                # Handle streaming in real implementation
                response = requests.post(url, json=payload, stream=True)
            else:
                response = requests.post(url, json=payload)
                return response.json()
        except requests.exceptions.ConnectionError:
            return {
                "error": "Could not connect to Ollama. Ensure it's running at " + self.ollama_url,
                "response": ""
            }
        except Exception as e:
            return {
                "error": str(e),
                "response": ""
            }
    
    def _structure_response(
        self, 
        api_response: Dict, 
        context: ExplanationContext
    ) -> LLMResponse:
        """Structure the raw LLM response with citations"""
        
        raw_text = api_response.get("response", "")
        
        # Extract citations (simple regex-based extraction)
        citations = []
        
        # Look for page references
        page_refs = re.findall(r'[Pp]age[s]?\s*(\d+)', raw_text)
        for page in page_refs:
            chunk = next((c for c in context.primary_chunks if str(c['page']) == page), None)
            if chunk:
                citations.append({
                    "type": "page",
                    "ref": page,
                    "text": chunk['text'][:200]
                })
        
        # Look for note references
        note_refs = re.findall(r'[Nn]ote[s]?\s*(\d+)', raw_text)
        for note_num in note_refs:
            note = next((n for n in context.related_notes if n.get('note_number') == note_num), None)
            if note:
                citations.append({
                    "type": "note",
                    "ref": note_num,
                    "text": note.get('header', '')
                })
        
        # Generate follow-up suggestions
        followups = self._generate_followups(context, raw_text)
        
        return LLMResponse(
            explanation=raw_text,
            citations=citations,
            suggested_followups=followups,
            confidence=context.confidence,
            model_used=self.model,
            tokens_used=api_response.get("eval_count", 0)
        )
    
    def _generate_followups(
        self, 
        context: ExplanationContext, 
        response_text: str
    ) -> List[str]:
        """Generate intelligent follow-up questions"""
        
        followups = []
        
        # Based on entity type
        if context.entity_type == "standalone":
            followups.append("How does this compare with the consolidated figures?")
        else:
            followups.append("What is the standalone position for this item?")
        
        # Based on content
        if "Ind AS" in response_text:
            followups.append("What are the disclosure requirements under this standard?")
        
        if "previous year" in response_text.lower():
            followups.append("What were the main reasons for this change?")
        
        if "note" in response_text.lower():
            followups.append("Show me the detailed breakdown from the related note")
        
        # Add specific followups based on statement type
        if context.statement_type == "balance_sheet":
            followups.append("How does this affect the debt-equity ratio?")
        elif context.statement_type == "income_statement":
            followups.append("What is the impact on operating margins?")
        
        return followups[:3]  # Limit to top 3


class RAGEngine:
    def __init__(self):
        self.chunks = []
        self.corpus_stats = {}
        self.explainer = FinancialExplainer()
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
        
    def explain_query(
        self, 
        query: str, 
        explanation_type: str = "general",
        page_context: Optional[Tuple[int, int]] = None,
        entity_filter: Optional[str] = None
    ) -> Dict:
        """
        High-level method to explain a query using document context + LLM.
        
        Args:
            query: User question
            explanation_type: Type of explanation needed
            page_context: Optional (start_page, end_page) to limit search
            entity_filter: 'standalone' or 'consolidated' to filter context
        """
        if not self.chunks:
            return {"error": "No document indexed. Please upload a file first."}
        
        # Step 1: Intelligent context retrieval (iterative)
        context = self._gather_explanation_context(
            query, 
            explanation_type, 
            page_context,
            entity_filter
        )
        
        # Step 2: Generate explanation via LLM
        try:
            explanation = self.explainer.explain(context, explanation_type)
            
            return {
                "success": True,
                "explanation": explanation.explanation,
                "citations": explanation.citations,
                "suggested_followups": explanation.suggested_followups,
                "context_meta": {
                    "pages_used": list(set(c['page'] for c in context.primary_chunks)),
                    "indas_standards": [s['number'] for s in context.indas_standards],
                    "confidence": explanation.confidence,
                    "model": explanation.model_used
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "context": {
                    "primary_chunks_found": len(context.primary_chunks),
                    "standards_found": len(context.indas_standards)
                }
            }
    
    def _gather_explanation_context(
        self,
        query: str,
        exp_type: str,
        page_range: Optional[Tuple[int, int]],
        entity_filter: Optional[str]
    ) -> ExplanationContext:
        """
        Gather comprehensive context for explanation with iterative refinement.
        """
        
        # Iteration 1: Direct search
        primary_results = json.loads(self.search(
            query, 
            top_k=10,
            page_range=page_range
        ))
        
        # Filter by entity type if specified
        if entity_filter:
            primary_results = [
                r for r in primary_results 
                if entity_filter.lower() in r.get('text', '').lower() or 
                self._detect_entity_in_chunk(r) == entity_filter
            ]
        
        confidence = self._calculate_context_confidence(primary_results, query)
        
        # Iteration 2: If low confidence, expand query
        supporting_results = []
        if confidence < 0.6:
            expanded_queries = self._get_expanded_queries(query, exp_type)
            for eq in expanded_queries[:2]:  # Limit to avoid too many calls
                additional = json.loads(self.search(eq, top_k=5))
                supporting_results.extend(additional)
            
            # Remove duplicates
            seen_ids = {r['id'] for r in primary_results}
            supporting_results = [r for r in supporting_results if r['id'] not in seen_ids]
        
        # Iteration 3: Gather related notes if applicable
        related_notes = []
        if exp_type in ["note", "indas", "line_item"]:
            # Extract note references from primary results
            for chunk in primary_results:
                if chunk.get('section_type') == 'note':
                    related_notes.append({
                        'note_number': self._extract_note_number(chunk.get('section_header', '')),
                        'header': chunk.get('section_header', ''),
                        'page': chunk['page']
                    })
            
            # Also look for notes referenced in text
            for chunk in primary_results:
                note_refs = re.findall(r'[Nn]ote\s*(\d+)', chunk.get('text', ''))
                for ref in note_refs:
                    note_chunk = self._get_note_by_number(ref)
                    if note_chunk and note_chunk['id'] not in [n.get('chunk_id') for n in related_notes]:
                        related_notes.append({
                            'note_number': ref,
                            'header': note_chunk.get('section_header', ''),
                            'page': note_chunk['page'],
                            'chunk_id': note_chunk['id']
                        })
        
        # Extract IndAS standards from context
        indas_standards = []
        for chunk in primary_results + supporting_results:
            for ref in chunk.get('indas_refs', []):
                if ref not in [s['full_ref'] for s in indas_standards]:
                    std_num = re.search(r'(\d+)', ref)
                    if std_num:
                        indas_standards.append({
                            'number': std_num.group(1),
                            'full_ref': ref,
                            'name': self.indas_standards.get(std_num.group(1), '')
                        })
        
        # Detect entity and statement type from context
        entity_type = entity_filter or self._detect_entity_from_chunks(primary_results)
        stmt_type = self._detect_statement_type_from_chunks(primary_results)
        
        # Calculate page range
        all_pages = [c['page'] for c in primary_results + supporting_results if 'page' in c]
        page_min = min(all_pages) if all_pages else 1
        page_max = max(all_pages) if all_pages else 1
        
        # Re-calculate final confidence
        final_confidence = self._calculate_context_confidence(
            primary_results + supporting_results, 
            query
        )
        
        return ExplanationContext(
            query=query,
            primary_chunks=primary_results,
            supporting_chunks=supporting_results,
            indas_standards=indas_standards,
            entity_type=entity_type,
            statement_type=stmt_type,
            page_range=(page_min, page_max),
            related_notes=related_notes,
            financial_summary=self._get_relevant_summary(primary_results),
            iteration=2 if supporting_results else 1,
            confidence=final_confidence
        )
    
    def _calculate_context_confidence(
        self, 
        chunks: List[Dict], 
        query: str
    ) -> float:
        """Calculate how confident we are in the retrieved context"""
        
        if not chunks:
            return 0.0
        
        scores = [c.get('score', 0) for c in chunks[:5]]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Normalize score (assuming BM25 scores typically 0-50 range)
        normalized = min(avg_score / 20, 1.0)
        
        # Check for exact keyword matches
        query_terms = set(self._tokenize(query))
        match_ratio = 0
        for chunk in chunks[:3]:
            chunk_text = chunk.get('text', '').lower()
            matches = sum(1 for term in query_terms if term in chunk_text)
            match_ratio = max(match_ratio, matches / len(query_terms) if query_terms else 0)
        
        return (normalized * 0.6) + (match_ratio * 0.4)
    
    def _get_expanded_queries(self, query: str, exp_type: str) -> List[str]:
        """Generate expanded queries for better context retrieval"""
        
        variations = []
        
        # Add financial terminology variations
        for term, synonyms in self.synonyms.items():
            if term in query.lower():
                for syn in synonyms:
                    variations.append(query.replace(term, syn))
        
        # Add IndAS context
        if exp_type == "indas":
            standards = self._extract_standards_from_query(query)
            for std in standards:
                variations.append(f"Ind AS {std} disclosure requirements")
                variations.append(f"Ind AS {std} accounting policy")
        
        # Add entity variations
        if "standalone" not in query.lower() and "consolidated" not in query.lower():
            variations.append(f"standalone {query}")
        
        return list(set(variations))[:5]  # Limit variations
    
    def _detect_entity_in_chunk(self, chunk: Dict) -> str:
        """Detect if chunk refers to standalone or consolidated"""
        text = chunk.get('text', '').lower()
        if 'consolidated' in text and 'standalone' not in text:
            return 'consolidated'
        elif 'standalone' in text:
            return 'standalone'
        return 'unknown'
    
    def _detect_entity_from_chunks(self, chunks: List[Dict]) -> str:
        """Determine predominant entity type from chunks"""
        if not chunks:
            return "unknown"
        
        consol_count = sum(1 for c in chunks if 'consolidated' in c.get('text', '').lower())
        standalone_count = sum(1 for c in chunks if 'standalone' in c.get('text', '').lower())
        
        return "consolidated" if consol_count > standalone_count else "standalone"
    
    def _detect_statement_type_from_chunks(self, chunks: List[Dict]) -> Optional[str]:
        """Detect if context is from balance sheet, P&L, etc."""
        if not chunks:
            return None
        
        type_counts = Counter(c.get('section_type') for c in chunks)
        
        # Check for statement indicators in text
        bs_indicators = ['total assets', 'liabilities and equity', 'balance sheet']
        pl_indicators = ['revenue from operations', 'profit for the year', 'total comprehensive income']
        cf_indicators = ['cash flow from operating', 'cash and cash equivalents at end']
        
        for chunk in chunks[:3]:
            text = chunk.get('text', '').lower()
            if any(i in text for i in bs_indicators):
                return "balance_sheet"
            elif any(i in text for i in pl_indicators):
                return "income_statement"
            elif any(i in text for i in cf_indicators):
                return "cash_flow"
        
        return type_counts.most_common(1)[0][0] if type_counts else None
    
    def _extract_note_number(self, header: str) -> str:
        """Extract note number from header"""
        match = re.search(r'(\d+)', header)
        return match.group(1) if match else "Unknown"
    
    def _get_note_by_number(self, note_num: str) -> Optional[Dict]:
        """Retrieve specific note chunk by number"""
        for chunk in self.chunks:
            if chunk.get('section_type') == 'note':
                header = chunk.get('section_header', '')
                if re.search(rf'^{note_num}\b', header) or re.search(rf'\b{note_num}\b', header):
                    return chunk
        return None
    
    def _extract_standards_from_query(self, query: str) -> List[str]:
        """Extract Ind AS numbers from query"""
        matches = re.findall(r'ind\s*as\s*(\d+)', query, re.IGNORECASE)
        return matches
    
    def _get_relevant_summary(self, chunks: List[Dict]) -> Dict:
        """Generate summary statistics from context chunks"""
        if not chunks:
            return {}
        
        pages = [c['page'] for c in chunks]
        return {
            "total_chunks": len(chunks),
            "page_range": f"{min(pages)}-{max(pages)}" if pages else "N/A",
            "sections": list(set(c.get('section_type') for c in chunks if c.get('section_type'))),
            "has_tables": any(c.get('has_table') for c in chunks)
        }


# Maintain backward compatibility
rag = RAGEngine()

# Add new method to rag instance for API exposure
rag.explain = rag.explain_query