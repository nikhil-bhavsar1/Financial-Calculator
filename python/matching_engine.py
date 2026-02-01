"""
Financial Term Matching System - Multi-Layer Matching Engine
============================================================
Phase 2: Multi-Layer Matching Pipeline
Implements cascading precision from exact matches to semantic similarity.
"""

import re
import math
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict
import sys

# Import terminology database
from terminology_keywords import (
    TERMINOLOGY_MAP, KEYWORD_TO_TERM, KEYWORD_BOOST,
    get_term_for_keyword, get_boost_for_keyword, get_all_keywords,
    find_all_matching_terms, find_best_matching_term
)

from preprocessing import PreprocessingResult, TextPreprocessor
from abbreviations import generate_acronyms, ACRONYM_PATTERNS
from config import MATCHING_CONFIG, VALIDATION_THRESHOLDS

# Try to import fuzzy matching library
try:
    from rapidfuzz import fuzz, process
    USE_RAPIDFUZZ = True
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process
        USE_RAPIDFUZZ = False
    except ImportError:
        USE_RAPIDFUZZ = False
        print("Warning: No fuzzy matching library installed. Install rapidfuzz or fuzzywuzzy.", file=sys.stderr)

# Try to import sentence transformers for semantic matching
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    USE_SEMANTIC = True
    SEMANTIC_MODEL = None  # Lazy loaded
except ImportError:
    USE_SEMANTIC = False
    print("Warning: sentence-transformers not installed. Semantic matching disabled.", file=sys.stderr)


@dataclass
class MatchResult:
    """Result of a single term match"""
    term_key: str
    term_label: str
    matched_keyword: str
    match_type: str  # 'exact', 'fuzzy', 'semantic', 'acronym'
    confidence_score: float
    original_text: str
    canonical_text: str
    line_number: Optional[int] = None
    position: Optional[Tuple[int, int]] = None
    category: str = ''
    boost: float = 1.0
    metric_ids: List[str] = field(default_factory=list)
    sign_convention: str = 'positive'
    fuzzy_score: Optional[float] = None
    semantic_score: Optional[float] = None


@dataclass
class MatchingSession:
    """Session state for a matching operation"""
    results: List[MatchResult] = field(default_factory=list)
    unmatched_lines: List[Tuple[int, str]] = field(default_factory=list)
    processing_stats: Dict[str, Any] = field(default_factory=dict)
    section_context: Optional[str] = None


class MultiLayerMatchingEngine:
    """
    Multi-layer matching engine implementing cascading precision.
    
    Layer A: Exact & Hybrid Matching (Priority 1)
    Layer B: Fuzzy Matching (Priority 2)
    Layer C: Semantic/Vector Matching (Priority 3)
    Layer D: Hierarchical Pattern Matching
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize matching engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or MATCHING_CONFIG
        self.preprocessor = TextPreprocessor()
        
        # Pre-computed data structures for O(1) lookup
        self.keyword_index = self._build_keyword_index()
        self.acronym_index = self._build_acronym_index()
        
        # Semantic model (lazy loaded)
        self.semantic_model = None
        self.term_embeddings = None
        
        # Cache for performance
        self._embedding_cache = {}
        self._fuzzy_cache = {}
        
    def _build_keyword_index(self) -> Dict[str, List[Dict]]:
        """
        Build optimized keyword index for O(1) lookup.
        
        Returns:
            Dictionary mapping normalized keywords to term information
        """
        index = defaultdict(list)
        
        for term_key, term_data in TERMINOLOGY_MAP.items():
            keywords = term_data.get('keywords_unified', [])
            
            for keyword in keywords:
                # Normalize keyword
                normalized = self._normalize_for_index(keyword)
                
                index[normalized].append({
                    'term_key': term_key,
                    'term_label': term_data.get('label', ''),
                    'category': term_data.get('category', ''),
                    'boost': term_data.get('boost', 1.0),
                    'metric_ids': term_data.get('metric_ids', []),
                    'sign_convention': term_data.get('sign_convention', 'positive'),
                    'original_keyword': keyword
                })
        
        return dict(index)
    
    def _build_acronym_index(self) -> Dict[str, List[Dict]]:
        """
        Build acronym index for acronym resolution.
        
        Returns:
            Dictionary mapping acronyms to term information
        """
        index = defaultdict(list)
        
        for term_key, term_data in TERMINOLOGY_MAP.items():
            label = term_data.get('label', '')
            keywords = term_data.get('keywords_unified', [])
            
            # Generate acronyms from label and keywords
            all_terms = [label] + keywords
            
            for term in all_terms:
                acronyms = generate_acronyms(term)
                for acronym in acronyms:
                    index[acronym.lower()].append({
                        'term_key': term_key,
                        'term_label': term_data.get('label', ''),
                        'category': term_data.get('category', ''),
                        'boost': term_data.get('boost', 1.0),
                        'metric_ids': term_data.get('metric_ids', []),
                        'sign_convention': term_data.get('sign_convention', 'positive'),
                        'source_term': term
                    })
        
        return dict(index)
    
    def _normalize_for_index(self, text: str) -> str:
        """Normalize text for indexing."""
        # Remove all non-alphanumeric characters except spaces
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _initialize_semantic_model(self):
        """Lazy initialization of semantic model."""
        if not USE_SEMANTIC or self.semantic_model is not None:
            return
        
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Pre-compute embeddings for all term labels
            term_labels = []
            term_keys = []
            
            for term_key, term_data in TERMINOLOGY_MAP.items():
                label = term_data.get('label', '')
                if label:
                    term_labels.append(label)
                    term_keys.append(term_key)
            
            if term_labels:
                self.term_embeddings = self.semantic_model.encode(term_labels)
                self._term_keys = term_keys
                
        except Exception as e:
            print(f"Warning: Could not initialize semantic model: {e}", file=sys.stderr)
            self.semantic_model = None
    
    def match_text(self, text: str, line_number: Optional[int] = None) -> List[MatchResult]:
        """
        Match text using all layers.
        
        Args:
            text: Input text to match
            line_number: Optional line number for tracking
            
        Returns:
            List of match results
        """
        results = []
        
        # Step 1: Preprocess
        preprocessed = self.preprocessor.preprocess(text, line_number)
        canonical = preprocessed.canonical_form
        
        # Step 2: Layer A - Exact & Hybrid Matching
        exact_matches = self._layer_a_exact_matching(preprocessed)
        results.extend(exact_matches)
        
        # Step 3: Layer B - Fuzzy Matching (if enabled and no exact matches)
        if self.config['matching'].get('fuzzy_threshold', 85) > 0:
            if not exact_matches or self.config['matching'].get('always_fuzzy', False):
                fuzzy_matches = self._layer_b_fuzzy_matching(preprocessed)
                results.extend(fuzzy_matches)
        
        # Step 4: Layer C - Semantic Matching (if enabled)
        if self.config['matching'].get('semantic_threshold', 0.75) > 0:
            if len(results) < 2:  # Only if we have few matches
                semantic_matches = self._layer_c_semantic_matching(preprocessed)
                results.extend(semantic_matches)
        
        # Step 5: Layer D - Hierarchical Resolution
        results = self._layer_d_hierarchical_resolution(results)
        
        # Step 6: Deduplication and scoring
        results = self._deduplicate_and_score(results)
        
        return results
    
    def _layer_a_exact_matching(self, preprocessed: PreprocessingResult) -> List[MatchResult]:
        """
        Layer A: Exact & Hybrid Matching with word-boundary regex.
        
        Args:
            preprocessed: Preprocessed text result
            
        Returns:
            List of exact match results
        """
        results = []
        canonical = preprocessed.canonical_form
        original = preprocessed.original_text
        
        # Method 1: Direct keyword lookup with word boundaries
        for keyword, term_list in self.keyword_index.items():
            # Use word-boundary matching
            escaped_kw = re.escape(keyword)
            pattern = r'(?:^|[\s\-])' + escaped_kw + r'(?:[\s\-]|$)'
            
            if re.search(pattern, canonical):
                for term_info in term_list:
                    match = MatchResult(
                        term_key=term_info['term_key'],
                        term_label=term_info['term_label'],
                        matched_keyword=keyword,
                        match_type='exact',
                        confidence_score=1.0 * term_info['boost'],
                        original_text=original,
                        canonical_text=canonical,
                        line_number=preprocessed.metadata.get('line_number'),
                        category=term_info['category'],
                        boost=term_info['boost'],
                        metric_ids=term_info['metric_ids'],
                        sign_convention=term_info['sign_convention']
                    )
                    results.append(match)
        
        # Method 2: N-gram matching for multi-word phrases
        max_ngram = self.config['matching'].get('max_ngram', 6)
        min_ngram = self.config['matching'].get('min_ngram', 2)
        words = canonical.split()
        
        for n in range(min(max_ngram, len(words)), min_ngram - 1, -1):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                
                if ngram in self.keyword_index:
                    for term_info in self.keyword_index[ngram]:
                        # Check if already matched
                        if not any(r.term_key == term_info['term_key'] for r in results):
                            match = MatchResult(
                                term_key=term_info['term_key'],
                                term_label=term_info['term_label'],
                                matched_keyword=ngram,
                                match_type='exact_ngram',
                                confidence_score=1.0 * term_info['boost'] * (1 + n * 0.1),
                                original_text=original,
                                canonical_text=canonical,
                                line_number=preprocessed.metadata.get('line_number'),
                                category=term_info['category'],
                                boost=term_info['boost'],
                                metric_ids=term_info['metric_ids'],
                                sign_convention=term_info['sign_convention']
                            )
                            results.append(match)
        
        # Method 3: Acronym matching
        if self.config['matching'].get('enable_acronym_matching', True):
            words = canonical.split()
            for word in words:
                if word in self.acronym_index:
                    for term_info in self.acronym_index[word]:
                        if not any(r.term_key == term_info['term_key'] for r in results):
                            match = MatchResult(
                                term_key=term_info['term_key'],
                                term_label=term_info['term_label'],
                                matched_keyword=word,
                                match_type='acronym',
                                confidence_score=0.95 * term_info['boost'],
                                original_text=original,
                                canonical_text=canonical,
                                line_number=preprocessed.metadata.get('line_number'),
                                category=term_info['category'],
                                boost=term_info['boost'],
                                metric_ids=term_info['metric_ids'],
                                sign_convention=term_info['sign_convention']
                            )
                            results.append(match)
        
        return results
    
    def _layer_b_fuzzy_matching(self, preprocessed: PreprocessingResult) -> List[MatchResult]:
        """
        Layer B: Fuzzy Matching for OCR errors and typos.
        
        Args:
            preprocessed: Preprocessed text result
            
        Returns:
            List of fuzzy match results
        """
        results = []
        
        if not USE_RAPIDFUZZ:
            return results
        
        canonical = preprocessed.canonical_form
        original = preprocessed.original_text
        threshold = self.config['matching'].get('fuzzy_threshold', 85)
        
        # Get all keywords for fuzzy matching
        all_keywords = list(self.keyword_index.keys())
        
        # Method 1: Token Set Ratio for word-order variations
        for keyword in all_keywords:
            if len(keyword) < 4:  # Skip short keywords
                continue
            
            # Check cache
            cache_key = f"{canonical}:{keyword}"
            if cache_key in self._fuzzy_cache:
                score = self._fuzzy_cache[cache_key]
            else:
                score = fuzz.token_set_ratio(canonical, keyword)
                self._fuzzy_cache[cache_key] = score
            
            if score >= threshold:
                for term_info in self.keyword_index[keyword]:
                    # Check if already matched exactly
                    if any(r.term_key == term_info['term_key'] and r.match_type == 'exact' 
                           for r in results):
                        continue
                    
                    # Calculate weighted score
                    fuzzy_weight = self.config['matching'].get('fuzzy_weight', 0.7)
                    confidence = (score / 100.0) * fuzzy_weight * term_info['boost']
                    
                    match = MatchResult(
                        term_key=term_info['term_key'],
                        term_label=term_info['term_label'],
                        matched_keyword=keyword,
                        match_type='fuzzy',
                        confidence_score=confidence,
                        original_text=original,
                        canonical_text=canonical,
                        line_number=preprocessed.metadata.get('line_number'),
                        category=term_info['category'],
                        boost=term_info['boost'],
                        metric_ids=term_info['metric_ids'],
                        sign_convention=term_info['sign_convention'],
                        fuzzy_score=score
                    )
                    results.append(match)
        
        # Method 2: Partial ratio for substring matches
        partial_threshold = max(threshold, 90)
        for keyword in all_keywords:
            if len(keyword) < 6:
                continue
            
            score = fuzz.partial_ratio(canonical, keyword)
            
            if score >= partial_threshold:
                for term_info in self.keyword_index[keyword]:
                    if any(r.term_key == term_info['term_key'] for r in results):
                        continue
                    
                    fuzzy_weight = self.config['matching'].get('fuzzy_weight', 0.7)
                    confidence = (score / 100.0) * fuzzy_weight * term_info['boost']
                    
                    match = MatchResult(
                        term_key=term_info['term_key'],
                        term_label=term_info['term_label'],
                        matched_keyword=keyword,
                        match_type='fuzzy_partial',
                        confidence_score=confidence,
                        original_text=original,
                        canonical_text=canonical,
                        line_number=preprocessed.metadata.get('line_number'),
                        category=term_info['category'],
                        boost=term_info['boost'],
                        metric_ids=term_info['metric_ids'],
                        sign_convention=term_info['sign_convention'],
                        fuzzy_score=score
                    )
                    results.append(match)
        
        return results
    
    def _layer_c_semantic_matching(self, preprocessed: PreprocessingResult) -> List[MatchResult]:
        """
        Layer C: Semantic/Vector Matching for conceptual gaps.
        
        Args:
            preprocessed: Preprocessed text result
            
        Returns:
            List of semantic match results
        """
        results = []
        
        if not USE_SEMANTIC:
            return results
        
        # Initialize model if needed
        self._initialize_semantic_model()
        
        if self.semantic_model is None or self.term_embeddings is None:
            return results
        
        canonical = preprocessed.canonical_form
        original = preprocessed.original_text
        threshold = self.config['matching'].get('semantic_threshold', 0.75)
        
        # Encode input text
        try:
            text_embedding = self.semantic_model.encode([canonical])
            
            # Calculate cosine similarity with all term embeddings
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(text_embedding, self.term_embeddings)[0]
            
            # Find matches above threshold
            for idx, similarity in enumerate(similarities):
                if similarity >= threshold:
                    term_key = self._term_keys[idx]
                    term_data = TERMINOLOGY_MAP.get(term_key, {})
                    
                    if not any(r.term_key == term_key for r in results):
                        semantic_weight = self.config['matching'].get('semantic_weight', 0.5)
                        confidence = similarity * semantic_weight * term_data.get('boost', 1.0)
                        
                        match = MatchResult(
                            term_key=term_key,
                            term_label=term_data.get('label', ''),
                            matched_keyword=term_data.get('label', ''),
                            match_type='semantic',
                            confidence_score=confidence,
                            original_text=original,
                            canonical_text=canonical,
                            line_number=preprocessed.metadata.get('line_number'),
                            category=term_data.get('category', ''),
                            boost=term_data.get('boost', 1.0),
                            metric_ids=term_data.get('metric_ids', []),
                            sign_convention=term_data.get('sign_convention', 'positive'),
                            semantic_score=similarity
                        )
                        results.append(match)
        
        except Exception as e:
            print(f"Warning: Semantic matching failed: {e}", file=sys.stderr)
        
        return results
    
    def _layer_d_hierarchical_resolution(self, matches: List[MatchResult]) -> List[MatchResult]:
        """
        Layer D: Hierarchical Pattern Matching.
        Prefer child terms over parent terms.
        
        Args:
            matches: List of matches to resolve
            
        Returns:
            Resolved matches
        """
        if not self.config['conflict_resolution'].get('prefer_specific', True):
            return matches
        
        # Group by term_key
        term_groups = defaultdict(list)
        for match in matches:
            term_groups[match.term_key].append(match)
        
        # Detect parent-child relationships
        # If "Goodwill" matches, don't just match "Intangible Assets"
        parent_child_map = {
            'intangible_assets': ['goodwill', 'software', 'patents'],
            'property_plant_equipment': ['land_and_buildings', 'plant_and_machinery', 'capital_work_in_progress'],
            'total_assets': ['property_plant_equipment', 'intangible_assets', 'inventories', 'trade_receivables'],
            'total_liabilities': ['borrowings', 'trade_payables', 'provisions'],
        }
        
        # Identify parent terms that have child matches
        parents_to_remove = set()
        for parent, children in parent_child_map.items():
            if parent in term_groups:
                for child in children:
                    if child in term_groups:
                        parents_to_remove.add(parent)
                        break
        
        # Remove parent matches unless they have "Total" prefix
        filtered_matches = []
        for match in matches:
            if match.term_key in parents_to_remove:
                # Check if it's a total line
                if 'total' not in match.original_text.lower():
                    continue
            filtered_matches.append(match)
        
        return filtered_matches
    
    def _deduplicate_and_score(self, matches: List[MatchResult]) -> List[MatchResult]:
        """
        Deduplicate matches and calculate final scores.
        
        Args:
            matches: List of matches
            
        Returns:
            Deduplicated and scored matches
        """
        if not matches:
            return []
        
        # Group by term_key
        term_groups = defaultdict(list)
        for match in matches:
            term_groups[match.term_key].append(match)
        
        # Keep highest scoring match for each term
        deduplicated = []
        for term_key, match_list in term_groups.items():
            # Sort by confidence score
            match_list.sort(key=lambda x: x.confidence_score, reverse=True)
            best_match = match_list[0]
            
            # Apply specificity boost
            word_count = len(best_match.matched_keyword.split())
            if word_count > 1:
                specificity_multiplier = 1.0 + (word_count - 1) * 0.2
                best_match.confidence_score *= specificity_multiplier
            
            deduplicated.append(best_match)
        
        # Sort by confidence score descending
        deduplicated.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return deduplicated
    
    def match_document(
        self, 
        lines: List[str], 
        context: Optional[Dict] = None
    ) -> MatchingSession:
        """
        Match all lines in a document.
        
        Args:
            lines: List of text lines
            context: Optional context information
            
        Returns:
            MatchingSession with all results
        """
        session = MatchingSession()
        session.section_context = context.get('section_type') if context else None
        
        stats = {
            'total_lines': len(lines),
            'matched_lines': 0,
            'unmatched_lines': 0,
            'exact_matches': 0,
            'fuzzy_matches': 0,
            'semantic_matches': 0,
            'acronym_matches': 0
        }
        
        for i, line in enumerate(lines):
            if not line or not line.strip():
                continue
            
            matches = self.match_text(line, i + 1)
            
            if matches:
                session.results.extend(matches)
                stats['matched_lines'] += 1
                
                for match in matches:
                    if match.match_type == 'exact':
                        stats['exact_matches'] += 1
                    elif match.match_type == 'fuzzy':
                        stats['fuzzy_matches'] += 1
                    elif match.match_type == 'semantic':
                        stats['semantic_matches'] += 1
                    elif match.match_type == 'acronym':
                        stats['acronym_matches'] += 1
            else:
                session.unmatched_lines.append((i + 1, line))
                stats['unmatched_lines'] += 1
        
        session.processing_stats = stats
        return session
    
    def get_match_summary(self, session: MatchingSession) -> Dict[str, Any]:
        """
        Get summary statistics for a matching session.
        
        Args:
            session: MatchingSession to analyze
            
        Returns:
            Summary statistics dictionary
        """
        stats = session.processing_stats
        
        total_matches = len(session.results)
        unique_terms = len(set(r.term_key for r in session.results))
        
        # Calculate confidence distribution
        confidence_buckets = {
            'high': len([r for r in session.results if r.confidence_score >= 0.8]),
            'medium': len([r for r in session.results if 0.5 <= r.confidence_score < 0.8]),
            'low': len([r for r in session.results if r.confidence_score < 0.5])
        }
        
        # Match type distribution
        type_distribution = defaultdict(int)
        for match in session.results:
            type_distribution[match.match_type] += 1
        
        return {
            'total_lines': stats.get('total_lines', 0),
            'matched_lines': stats.get('matched_lines', 0),
            'unmatched_lines': stats.get('unmatched_lines', 0),
            'total_matches': total_matches,
            'unique_terms': unique_terms,
            'match_rate': stats.get('matched_lines', 0) / max(stats.get('total_lines', 1), 1),
            'confidence_distribution': confidence_buckets,
            'match_type_distribution': dict(type_distribution),
            'unmatched_count': len(session.unmatched_lines)
        }


# Convenience function
def match_financial_terms(text: str, line_number: Optional[int] = None) -> List[MatchResult]:
    """
    Quick function to match financial terms in text.
    
    Args:
        text: Text to analyze
        line_number: Optional line number
        
    Returns:
        List of match results
    """
    engine = MultiLayerMatchingEngine()
    return engine.match_text(text, line_number)
