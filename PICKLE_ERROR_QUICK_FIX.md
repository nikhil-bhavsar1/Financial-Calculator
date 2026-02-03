# Quick Fix for Pickle Error

## Problem
The API uses HybridFinancialParser which uses multiprocessing with PyMuPDF objects.
PyMuPDF uses SWIG bindings which cannot be pickled.

## Solution
Use the SAFE parser instead (safe_parser.py) which disables multiprocessing.

## Manual Fix Required

### Step 1: Add import (around line 25)
Add this AFTER the detailed parser import:

```python
# Try SAFE parser wrapper (disables multiprocessing to prevent pickle errors)
try:
    from safe_parser import get_safe_parser
    SAFE_PARSER_AVAILABLE = True
except ImportError:
    SAFE_PARSER_AVAILABLE = False
    print("[api.py] Safe parser not available", file=sys.stderr)
```

### Step 2: Modify parser selection (around line 154)
Change:
```python
use_hybrid = (HYBRID_PARSER_AVAILABLE and ...)
```
To:
```python
# Priority: SAFE (no pickle) > HYBRID > DETAILED
if SAFE_PARSER_AVAILABLE and actual_path.lower().endswith('.pdf'):
    print(f"[api.py] Using Safe Parser - NO PICKLE ERRORS", file=sys.stderr)
    parser = get_safe_parser()
    result = parser.parse(actual_path)
    # ... use result ...
    return {'status': 'success', 'extractedData': {...}}
elif HYBRID_PARSER_AVAILABLE and ...:
    # ... existing hybrid code ...
else:
    # ... existing detailed code ...
```

## Alternative: Disable Hybrid Parser

Simply comment out the hybrid import (line 28):
```python
# from hybrid_pdf_processor import HybridFinancialParser
HYBRID_PARSER_AVAILABLE = False
```

This forces the API to use the original DETAILED parser which works correctly.

## What This Does

| Parser | Multiprocessing | Pickle Error | Quality |
|--------|----------------|--------------|---------|
| HYBRID | Yes | YES (broken) | High |
| SAFE | No | No | 100% |
| DETAILED | No | No | 100% |

## Recommendation

Use the DETAILED parser (original) - it works, has 100% quality, no pickle errors.
The safe_parser.py is also available if you want a simple wrapper.
