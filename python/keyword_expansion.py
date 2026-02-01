"""
Financial Term Matching System - Keyword Expansion
==================================================
Automated keyword expansion with pluralization, OCR error simulation,
and regional variant injection.
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class KeywordExpander:
    """
    Expands keywords with variants for better matching coverage.
    """
    
    def __init__(self):
        # UK vs US spelling variants
        self.regional_variants = {
            # UK -> US
            'amortisation': 'amortization',
            'recognised': 'recognized',
            'recognise': 'recognize',
            'analyse': 'analyze',
            'analysed': 'analyzed',
            'organisation': 'organization',
            'organise': 'organize',
            'organised': 'organized',
            'centre': 'center',
            'favour': 'favor',
            'favourable': 'favorable',
            'behaviour': 'behavior',
            'colour': 'color',
            'honour': 'honor',
            'labour': 'labor',
            'neighbour': 'neighbor',
            'defence': 'defense',
            'offence': 'offense',
            'pretence': 'pretense',
            'practise': 'practice',
            'practised': 'practiced',
            'licence': 'license',
            'realise': 'realize',
            'realised': 'realized',
            'capitalise': 'capitalize',
            'capitalised': 'capitalized',
            'minimise': 'minimize',
            'minimised': 'minimized',
            'maximise': 'maximize',
            'maximised': 'maximized',
            'optimise': 'optimize',
            'optimised': 'optimized',
            'standardise': 'standardize',
            'standardised': 'standardized',
            'utilise': 'utilize',
            'utilised': 'utilized',
            'modelling': 'modeling',
            'travelled': 'traveled',
            'cancelled': 'canceled',
            'levelled': 'leveled',
            'totalled': 'totaled',
            'enrolment': 'enrollment',
            'instalment': 'installment',
            'cheque': 'check',
            'programme': 'program',
            'storey': 'story',
        }
        
        # Reverse mapping (US -> UK)
        self.us_to_uk = {v: k for k, v in self.regional_variants.items()}
        
        # OCR error patterns (common misreadings)
        self.ocr_error_patterns = {
            '0': ['o', 'O'],
            '1': ['l', 'I', 'i'],
            '5': ['s', 'S'],
            'rn': ['m', 'M'],
            'nn': ['m', 'M'],
            'cl': ['d', 'D'],
            'ci': ['a', 'A'],
            'fi': ['f', 'F'],
            'fl': ['f', 'F'],
            'tt': ['H'],
            'll': ['H', 'U'],
            'vv': ['w', 'W'],
            'ri': ['n', 'N'],
            'nt': ['u', 'U'],
            'li': ['h', 'H'],
        }
        
        # Irregular plurals
        self.irregular_plurals = {
            'child': 'children',
            'person': 'people',
            'man': 'men',
            'woman': 'women',
            'foot': 'feet',
            'tooth': 'teeth',
            'mouse': 'mice',
            'goose': 'geese',
            'ox': 'oxen',
            'datum': 'data',
            'analysis': 'analyses',
            'crisis': 'crises',
            'basis': 'bases',
            'hypothesis': 'hypotheses',
            'phenomenon': 'phenomena',
            'criterion': 'criteria',
            'index': 'indices',
            'matrix': 'matrices',
            'vertex': 'vertices',
            'axis': 'axes',
            'deer': 'deer',
            'sheep': 'sheep',
            'fish': 'fish',
            'series': 'series',
            'species': 'species',
            'means': 'means',
            'crossroads': 'crossroads',
        }
        
        # Words that should not be pluralized
        self.uncountable = {
            'equipment', 'machinery', 'furniture', 'information', 'knowledge',
            'money', 'cash', 'currency', 'advice', 'evidence', 'research',
            'news', 'progress', 'traffic', 'weather', 'water', 'air',
            'rice', 'sugar', 'salt', 'wheat', 'corn', 'bread', 'milk',
            'software', 'hardware', 'data', 'metadata', 'goodwill',
            'equity', 'debt', 'credit', 'interest', 'insurance',
        }
    
    def expand_keyword(self, keyword: str) -> Set[str]:
        """
        Expand a single keyword with all variants.
        
        Args:
            keyword: Base keyword
            
        Returns:
            Set of expanded keywords
        """
        variants = {keyword.lower().strip()}
        
        # Add plural forms
        variants.update(self._get_plural_variants(keyword))
        
        # Add regional variants
        variants.update(self._get_regional_variants(keyword))
        
        # Add OCR error variants
        variants.update(self._get_ocr_variants(keyword))
        
        return variants
    
    def _get_plural_variants(self, word: str) -> Set[str]:
        """
        Generate plural forms of a word.
        
        Args:
            word: Input word
            
        Returns:
            Set of plural variants
        """
        variants = set()
        word_lower = word.lower().strip()
        
        # Skip uncountable nouns
        if word_lower in self.uncountable:
            return variants
        
        # Check irregular plurals
        if word_lower in self.irregular_plurals:
            variants.add(self.irregular_plurals[word_lower])
            return variants
        
        # Check if already plural (ends in s, es, etc.)
        if word_lower.endswith('s') or word_lower.endswith('es'):
            # Try to create singular
            singular = self._singularize(word_lower)
            if singular and singular != word_lower:
                variants.add(singular)
            return variants
        
        # Generate plural
        plural = self._pluralize(word_lower)
        if plural and plural != word_lower:
            variants.add(plural)
        
        return variants
    
    def _pluralize(self, word: str) -> Optional[str]:
        """
        Convert word to plural form.
        
        Args:
            word: Singular word
            
        Returns:
            Plural form or None
        """
        if not word:
            return None
        
        # Irregular
        if word in self.irregular_plurals:
            return self.irregular_plurals[word]
        
        # Ends in s, x, z, ch, sh -> add es
        if word.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return word + 'es'
        
        # Ends in consonant + y -> ies
        if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        
        # Ends in f or fe -> ves
        if word.endswith('fe'):
            return word[:-2] + 'ves'
        if word.endswith('f') and word[-2] not in 'aeiou':
            return word[:-1] + 'ves'
        
        # Ends in o -> es (for some words)
        if word.endswith('o') and len(word) > 1 and word[-2] not in 'aeiou':
            return word + 'es'
        
        # Default: add s
        return word + 's'
    
    def _singularize(self, word: str) -> Optional[str]:
        """
        Convert word to singular form.
        
        Args:
            word: Plural word
            
        Returns:
            Singular form or None
        """
        if not word:
            return None
        
        # Check if in irregular plurals (reverse lookup)
        for singular, plural in self.irregular_plurals.items():
            if word == plural:
                return singular
        
        # Ends in ies -> y
        if word.endswith('ies') and len(word) > 3:
            return word[:-3] + 'y'
        
        # Ends in ves -> f or fe
        if word.endswith('ves'):
            stem = word[:-3]
            # Try f first, then fe
            return stem + 'f'
        
        # Ends in es -> remove es
        if word.endswith('es'):
            return word[:-2]
        
        # Ends in s -> remove s
        if word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        
        return word
    
    def _get_regional_variants(self, word: str) -> Set[str]:
        """
        Generate UK/US spelling variants.
        
        Args:
            word: Input word
            
        Returns:
            Set of regional variants
        """
        variants = set()
        word_lower = word.lower().strip()
        
        # Check if word has UK variant
        if word_lower in self.regional_variants:
            variants.add(self.regional_variants[word_lower])
        
        # Check if word has US variant
        if word_lower in self.us_to_uk:
            variants.add(self.us_to_uk[word_lower])
        
        # Check for multi-word phrases
        words = word_lower.split()
        if len(words) > 1:
            # Try replacing each word
            for i, w in enumerate(words):
                if w in self.regional_variants:
                    new_words = words.copy()
                    new_words[i] = self.regional_variants[w]
                    variants.add(' '.join(new_words))
                elif w in self.us_to_uk:
                    new_words = words.copy()
                    new_words[i] = self.us_to_uk[w]
                    variants.add(' '.join(new_words))
        
        return variants
    
    def _get_ocr_variants(self, word: str) -> Set[str]:
        """
        Generate OCR error variants (1-2 character edits).
        
        Args:
            word: Input word
            
        Returns:
            Set of OCR variants
        """
        variants = set()
        
        # Only generate OCR variants for longer words
        if len(word) < 5:
            return variants
        
        # Generate 1-character substitutions
        for i in range(len(word)):
            # Skip if character could be misread
            char = word[i]
            if char in self.ocr_error_patterns:
                for replacement in self.ocr_error_patterns[char]:
                    variant = word[:i] + replacement + word[i+1:]
                    variants.add(variant.lower())
        
        # Generate 2-character substitutions
        for i in range(len(word) - 1):
            pair = word[i:i+2]
            if pair in self.ocr_error_patterns:
                for replacement in self.ocr_error_patterns[pair]:
                    variant = word[:i] + replacement + word[i+2:]
                    variants.add(variant.lower())
        
        # Limit to prevent explosion
        return set(list(variants)[:10])
    
    def expand_terminology_database(
        self, 
        terminology_map: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        Expand all keywords in a terminology database.
        
        Args:
            terminology_map: Original terminology map
            
        Returns:
            Expanded terminology map
        """
        expanded_map = {}
        
        for term_key, term_data in terminology_map.items():
            # Copy original
            expanded_data = term_data.copy()
            
            # Get all keywords
            all_keywords = set()
            for key in ['keywords_unified', 'keywords_indas', 'keywords_gaap', 'keywords_ifrs']:
                if key in term_data:
                    all_keywords.update(term_data[key])
            
            # Expand each keyword
            expanded_keywords = set()
            for keyword in all_keywords:
                expanded_keywords.update(self.expand_keyword(keyword))
            
            # Update with expanded keywords
            expanded_data['keywords_expanded'] = list(expanded_keywords)
            expanded_data['keywords_unified'] = list(set(term_data.get('keywords_unified', [])) | expanded_keywords)
            
            expanded_map[term_key] = expanded_data
        
        return expanded_map
    
    def generate_expansion_report(
        self, 
        original_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a report on keyword expansion.
        
        Args:
            original_keywords: List of original keywords
            
        Returns:
            Report dictionary
        """
        total_original = len(original_keywords)
        total_expanded = 0
        plural_count = 0
        regional_count = 0
        ocr_count = 0
        
        expansion_details = []
        
        for keyword in original_keywords:
            expanded = self.expand_keyword(keyword)
            expansion_count = len(expanded) - 1  # Exclude original
            
            total_expanded += expansion_count
            
            # Categorize
            plural_variants = self._get_plural_variants(keyword)
            regional_variants = self._get_regional_variants(keyword)
            ocr_variants = self._get_ocr_variants(keyword)
            
            plural_count += len(plural_variants)
            regional_count += len(regional_variants)
            ocr_count += len(ocr_variants)
            
            expansion_details.append({
                'original': keyword,
                'expanded_count': expansion_count,
                'plurals': list(plural_variants),
                'regional': list(regional_variants),
                'ocr': list(ocr_variants)[:5]  # Limit for readability
            })
        
        return {
            'total_original_keywords': total_original,
            'total_expanded_variants': total_expanded,
            'expansion_ratio': total_expanded / max(total_original, 1),
            'plural_variants': plural_count,
            'regional_variants': regional_count,
            'ocr_variants': ocr_count,
            'top_expanded': sorted(
                expansion_details,
                key=lambda x: x['expanded_count'],
                reverse=True
            )[:20]
        }


# Convenience function
def expand_keywords(keywords: List[str]) -> Set[str]:
    """
    Quick function to expand a list of keywords.
    
    Args:
        keywords: List of keywords to expand
        
    Returns:
        Set of all expanded keywords
    """
    expander = KeywordExpander()
    all_expanded = set()
    
    for keyword in keywords:
        all_expanded.update(expander.expand_keyword(keyword))
    
    return all_expanded
