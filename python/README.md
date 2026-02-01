# Financial Term Matching System

A robust, multi-layered extraction pipeline that matches financial terms from annual statements to a unified terminology database with >95% recall and <5% false positive rate.

## Features

### Phase 1: Data Preprocessing & Normalization
- **Abbreviation Expansion**: Comprehensive dictionary for financial abbreviations (PPE, CWIP, EBITDA, FY, etc.)
- **Note Reference Removal**: Strips note numbers and schedule references using regex patterns
- **Sign Convention Detection**: Automatically detects negative indicators (Less:, (-), Cr., Dr.)
- **Date & Number Normalization**: Standardizes formats for consistent matching
- **Unicode Normalization**: Converts smart quotes, em-dashes, special spaces to ASCII

### Phase 2: Multi-Layer Matching Pipeline
- **Layer A - Exact Matching**: Word-boundary regex with O(1) keyword index lookup
- **Layer B - Fuzzy Matching**: Levenshtein distance matching for OCR errors and typos (rapidfuzz)
- **Layer C - Semantic Matching**: Vector similarity using sentence-transformers
- **Layer D - Hierarchical Resolution**: Prefers child terms over parent terms

### Phase 3: Context Awareness
- Section type detection (Balance Sheet, Income Statement, Cash Flow)
- Category-based score boosting
- Cross-reference resolution for notes and schedules

### Phase 4: Conflict Resolution
- Substring suppression (prevents "Equipment" matching when "Property Plant Equipment" matches)
- Score-based deduplication
- Hierarchical pruning

### Phase 5: Database Enhancement
- Synonym networks (Sundry Debtors ↔ Accounts Receivable)
- Parent-child hierarchies
- Cross-standard mapping (IndAS, GAAP, IFRS)

## Installation

```bash
# Required dependencies
pip install rapidfuzz sentence-transformers scikit-learn

# Or install all optional dependencies for full functionality
pip install rapidfuzz sentence-transformers scikit-learn numpy
```

## Quick Start

```python
from python import FinancialTermMatcher

# Create matcher instance
matcher = FinancialTermMatcher()

# Match a single line
matches = matcher.match("Property, Plant and Equipment")
for match in matches:
    print(f"Matched: {match.term_label} (confidence: {match.confidence_score:.2%})")

# Process a document
lines = [
    "Property, Plant and Equipment",
    "Trade Receivables (Note 12)",
    "Capital Work in Progress",
    "Total Revenue from Operations"
]

session = matcher.match_document(lines)
matcher.print_summary(session)
```

## Usage Examples

### Example 1: Basic Matching
```python
from python import match_terms

# Quick one-off matching
matches = match_terms("PPE & CWIP (Note 12)")
for match in matches:
    print(f"{match['term_label']}: {match['confidence']:.2%}")
```

### Example 2: Preprocessing
```python
result = matcher.preprocess("PPE & CWIP (Note 12)")
print(f"Original: {result.original_text}")
print(f"Canonical: {result.canonical_form}")
print(f"Sign: {result.sign_multiplier}")
```

### Example 3: Document Processing
```python
# Process a file
session = matcher.match_file("financial_statement.txt")

# Export results
matcher.export_results(session, "matches.json", format="json")
```

### Example 4: Validation
```python
# Run validation tests
results = matcher.validate()
print(f"Precision: {results['golden_set']['precision']:.2%}")
print(f"Recall: {results['golden_set']['recall']:.2%}")
print(f"F1 Score: {results['golden_set']['f1_score']:.2%}")
```

## Configuration

The system can be configured via the `MATCHING_CONFIG` dictionary:

```python
MATCHING_CONFIG = {
    "preprocessing": {
        "expand_abbreviations": True,
        "remove_notes": True,
        "normalize_unicode": True
    },
    "matching": {
        "exact_weight": 1.0,
        "fuzzy_threshold": 85,
        "fuzzy_weight": 0.7,
        "semantic_threshold": 0.75,
        "semantic_weight": 0.5,
        "max_ngram": 6
    },
    "context": {
        "section_boost": 1.5,
        "category_penalty": 0.3
    },
    "conflict_resolution": {
        "prefer_specific": True,
        "deduplicate_by_term_key": True
    }
}
```

## Project Structure

```
python/
├── __init__.py              # Main API and FinancialTermMatcher class
├── config.py                # Configuration constants
├── abbreviations.py         # Abbreviation expansion and acronym generation
├── preprocessing.py         # Text cleaning and normalization
├── terminology_keywords.py  # Unified terminology database
├── matching_engine.py       # Multi-layer matching implementation
├── validation.py            # Testing and validation framework
└── examples.py              # Usage examples
```

## Database Statistics

The system includes a comprehensive financial terminology database:

- **256 Terms** across 13 categories
- **1,899 Unique Keywords** covering IndAS, GAAP, and IFRS standards
- **Categories**:
  - Balance Sheet (Assets, Liabilities, Equity)
  - Income Statement
  - Cash Flow Statement
  - Financial Ratios
  - Tax Details
  - Segment Reporting
  - And more...

## Performance

- **Processing Speed**: >1000 lines/second (target)
- **Memory Usage**: Optimized with lazy loading and caching
- **Matching Layers**: Cascading precision from exact to semantic

## Validation

Run the validation suite:

```bash
python python/__init__.py --validate
```

Or programmatically:

```python
from python import FinancialTermMatcher

matcher = FinancialTermMatcher()
results = matcher.validate()
```

## Command Line Usage

```bash
# Show database statistics
python python/__init__.py --stats

# Run validation tests
python python/__init__.py --validate

# Process a file
python python/__init__.py input.txt --output results.json

# Process text directly
python python/__init__.py "Property, Plant and Equipment"
```

## Success Metrics

The system targets:
- **Recall Rate**: >95%
- **False Positive Rate**: <5%
- **F1 Score**: >0.92
- **Processing Speed**: >1000 lines/second

## Troubleshooting

### Issue: "sentence-transformers not installed"
**Solution**: Install optional dependencies:
```bash
pip install sentence-transformers
```

### Issue: "rapidfuzz not installed"
**Solution**: Install fuzzy matching library:
```bash
pip install rapidfuzz
```

### Issue: Low recall rate
**Diagnosis**: Check if terminology database covers your specific terms.
**Fix**: Add custom terms to the database or use fuzzy matching with lower threshold.

### Issue: Too many false positives
**Diagnosis**: Matching threshold may be too low.
**Fix**: Increase `fuzzy_threshold` to 90+ or enable `prefer_specific` in conflict resolution.

## Contributing

To add new financial terms:

1. Edit the appropriate TypeScript file in `library/terms/`
2. Rebuild the terminology database
3. Run validation tests
4. Submit a pull request

## License

This project is part of the Financial Calculator application.

## Support

For issues and questions:
- Check the troubleshooting guide above
- Review the examples in `python/examples.py`
- Run validation tests to identify problems
