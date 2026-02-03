"""
Test script to verify API response format for parsing
"""
import sys
import json

# Simulate the response from api.py
test_response = {
    'status': 'success',
    'extractedData': {
        'items': [],
        'text': 'Test text content',
        'metadata': {
            'fileName': 'test.pdf',
            'pageCount': 1
        },
        'standalone': {},
        'consolidated': {},
        'validation': {}
    }
}

print("Test response structure:")
print(json.dumps(test_response, indent=2))

# What the frontend expects (from App.tsx line 554):
# response.extractedData should exist and have:
# - items: array
# - text: string
# - metadata: object

# Or it expects data.data to have items (line 558)

print("\n\nFrontend extraction logic:")
print("const extractedData = response.extractedData || {};")
print("const data = (extractedData as any).data || extractedData;")
print("if (Array.isArray(data)) { items = data; }")
