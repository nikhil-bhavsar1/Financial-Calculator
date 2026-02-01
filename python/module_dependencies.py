"""
Financial Term Matching System - Module Dependency Map
======================================================
Shows how all modules are interlinked and their dependencies.
"""

MODULE_DEPENDENCIES = {
    "config.py": {
        "description": "Centralized configuration constants",
        "imports": [],
        "exported": ["MATCHING_CONFIG", "VALIDATION_THRESHOLDS", "SECTION_BOOST_MAP"],
        "used_by": [
            "matching_engine.py",
            "preprocessing.py",
            "validation.py",
            "__init__.py"
        ]
    },
    
    "abbreviations.py": {
        "description": "Abbreviation mappings and acronym generation",
        "imports": [],
        "exported": [
            "FINANCIAL_ABBREVIATIONS",
            "ACRONYM_PATTERNS",
            "expand_abbreviations",
            "generate_acronyms",
            "get_all_abbreviations"
        ],
        "used_by": [
            "preprocessing.py",
            "matching_engine.py",
            "test_suite.py"
        ]
    },
    
    "preprocessing.py": {
        "description": "Text preprocessing pipeline",
        "imports": [
            "abbreviations.py",
            "config.py"
        ],
        "exported": [
            "TextPreprocessor",
            "PreprocessingResult",
            "preprocess_text"
        ],
        "used_by": [
            "matching_engine.py",
            "validation.py",
            "__init__.py",
            "test_suite.py"
        ]
    },
    
    "terminology_keywords.py": {
        "description": "Unified terminology database interface",
        "imports": [],
        "exported": [
            "TERMINOLOGY_MAP",
            "KEYWORD_TO_TERM",
            "KEYWORD_BOOST",
            "find_all_matching_terms",
            "find_best_matching_term",
            "get_term_for_keyword",
            "get_boost_for_keyword",
            "get_all_keywords",
            "get_database_stats"
        ],
        "used_by": [
            "matching_engine.py",
            "validation.py",
            "__init__.py",
            "test_suite.py"
        ]
    },
    
    "matching_engine.py": {
        "description": "4-layer matching engine (exact, fuzzy, semantic, hierarchical)",
        "imports": [
            "terminology_keywords.py",
            "preprocessing.py",
            "abbreviations.py",
            "config.py"
        ],
        "exported": [
            "MultiLayerMatchingEngine",
            "MatchResult",
            "MatchingSession",
            "match_financial_terms"
        ],
        "used_by": [
            "validation.py",
            "cross_reference_resolver.py",
            "__init__.py",
            "test_suite.py"
        ]
    },
    
    "section_classifier.py": {
        "description": "ML-based section classification for context awareness",
        "imports": [],
        "exported": [
            "SectionClassifier",
            "SectionContext",
            "classify_financial_section"
        ],
        "used_by": [
            "__init__.py",
            "test_suite.py"
        ]
    },
    
    "cross_reference_resolver.py": {
        "description": "Cross-reference resolution and inter-statement validation",
        "imports": [
            "matching_engine.py"
        ],
        "exported": [
            "CrossReferenceResolver",
            "CrossReference",
            "NoteSection",
            "resolve_document_references"
        ],
        "used_by": [
            "__init__.py",
            "test_suite.py"
        ]
    },
    
    "keyword_expansion.py": {
        "description": "Automated keyword expansion (pluralization, OCR, regional)",
        "imports": [],
        "exported": [
            "KeywordExpander",
            "expand_keywords"
        ],
        "used_by": [
            "test_suite.py"
        ]
    },
    
    "relationship_mapper.py": {
        "description": "Synonym networks and parent-child hierarchies",
        "imports": [],
        "exported": [
            "RelationshipMapper",
            "get_term_synonyms",
            "get_term_parent",
            "get_related_terms"
        ],
        "used_by": [
            "test_suite.py"
        ]
    },
    
    "validation.py": {
        "description": "Testing and validation framework",
        "imports": [
            "matching_engine.py",
            "preprocessing.py",
            "terminology_keywords.py"
        ],
        "exported": [
            "ValidationFramework",
            "GoldenSetTest",
            "DEFAULT_GOLDEN_SET",
            "run_validation"
        ],
        "used_by": [
            "__init__.py",
            "test_suite.py"
        ]
    },
    
    "__init__.py": {
        "description": "Main API - FinancialTermMatcher class",
        "imports": [
            "preprocessing.py",
            "matching_engine.py",
            "validation.py",
            "config.py",
            "terminology_keywords.py"
        ],
        "exported": [
            "FinancialTermMatcher",
            "match_terms"
        ],
        "used_by": [
            "test_suite.py",
            "examples.py"
        ]
    },
    
    "test_suite.py": {
        "description": "Comprehensive test suite (52+ tests)",
        "imports": [
            "preprocessing.py",
            "abbreviations.py",
            "matching_engine.py",
            "section_classifier.py",
            "cross_reference_resolver.py",
            "keyword_expansion.py",
            "relationship_mapper.py",
            "validation.py",
            "__init__.py"
        ],
        "exported": [
            "run_comprehensive_tests",
            "COMPREHENSIVE_GOLDEN_SET"
        ],
        "used_by": []
    },
    
    "examples.py": {
        "description": "Usage examples and demonstrations",
        "imports": [
            "__init__.py"
        ],
        "exported": [],
        "used_by": []
    }
}


def print_dependency_tree():
    """Print the dependency tree of all modules"""
    print("\n" + "="*70)
    print("MODULE DEPENDENCY TREE")
    print("="*70)
    
    for module_name, info in MODULE_DEPENDENCIES.items():
        print(f"\n📄 {module_name}")
        print(f"   Description: {info['description']}")
        
        if info['imports']:
            print(f"   Imports: {', '.join(info['imports'])}")
        else:
            print(f"   Imports: (none - base module)")
        
        if info['used_by']:
            print(f"   Used by: {', '.join(info['used_by'])}")
        else:
            print(f"   Used by: (none - top-level)")
        
        print(f"   Exports {len(info['exported'])} objects")
    
    print("\n" + "="*70)


def verify_all_imports():
    """Verify all modules can be imported successfully"""
    import sys
    sys.path.insert(0, '/home/nikhil/Gemini Workspace/Financial-Calculator/python')
    
    print("\n" + "="*70)
    print("VERIFYING ALL MODULE IMPORTS")
    print("="*70 + "\n")
    
    all_success = True
    
    for module_name in MODULE_DEPENDENCIES.keys():
        module_base = module_name.replace('.py', '')
        try:
            __import__(module_base)
            print(f"✅ {module_name:30s} - Successfully imported")
        except Exception as e:
            print(f"❌ {module_name:30s} - Failed: {e}")
            all_success = False
    
    print("\n" + "="*70)
    if all_success:
        print("✅ ALL MODULES SUCCESSFULLY INTERLINKED!")
    else:
        print("❌ SOME MODULES HAVE IMPORT ISSUES")
    print("="*70 + "\n")
    
    return all_success


def get_module_stats():
    """Get statistics about the module system"""
    total_modules = len(MODULE_DEPENDENCIES)
    base_modules = sum(1 for info in MODULE_DEPENDENCIES.values() if not info['imports'])
    top_level_modules = sum(1 for info in MODULE_DEPENDENCIES.values() if not info['used_by'])
    
    total_exports = sum(len(info['exported']) for info in MODULE_DEPENDENCIES.values())
    
    return {
        'total_modules': total_modules,
        'base_modules': base_modules,
        'top_level_modules': top_level_modules,
        'total_exports': total_exports,
        'avg_exports_per_module': total_exports / total_modules if total_modules > 0 else 0
    }


if __name__ == '__main__':
    print_dependency_tree()
    
    stats = get_module_stats()
    print("\n" + "="*70)
    print("MODULE STATISTICS")
    print("="*70)
    print(f"Total Modules:        {stats['total_modules']}")
    print(f"Base Modules:         {stats['base_modules']} (no dependencies)")
    print(f"Top-Level Modules:    {stats['top_level_modules']} (not used by others)")
    print(f"Total Exports:        {stats['total_exports']}")
    print(f"Avg Exports/Module:   {stats['avg_exports_per_module']:.1f}")
    print("="*70)
    
    # Verify imports
    verify_all_imports()
