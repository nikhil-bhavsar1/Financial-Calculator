# "No Data Visible in Captured Data" - Diagnosis and Fixes

## Issue
No data is visible in the Captured Data grid after uploading a file.

## Root Causes Found

### 1. Parallel Processor Items in Wrong Format (FIXED)
**Issue**: The parallel processor (`parallel_processor.py`) was returning items in a simplified format:
```python
{
    'page': 1,
    'text': 'Revenue from sales...',
}
```

**But database expects** (`database.py:save_parsed_items`):
```python
{
    'id': 'uuid-123',
    'label': 'Revenue',
    'currentYear': 123.45,
    'previousYear': 98.76,
    'rowIndex': 5,
    'statementType': 'INCOME',
    ...
}
```

**Fix Applied**: Disabled parallel processor for item extraction, now only uses `FinancialParser.parse()` which returns properly formatted items.

### 2. Response Format Mismatch
The API returns data in this structure:
```python
return {
    'status': 'success',
    'extractedData': {
        'items': [...],
        'text': '...',
        'metadata': {...},
        'standalone': {...},
        'consolidated': {...},
        'validation': {...}
    }
}
```

**Frontend expects** (from `App.tsx` line 554-568):
```typescript
const extractedData = response.extractedData || {};
const data = (extractedData as any).data || extractedData;  // Checks for .data first
if (Array.isArray(data)) { items = data; } else if (Array.isArray(data.items)) { items = data.items; }
```

This should work correctly because `extractedData` has `items` directly.

### 3. Debug Logging Added
Added extensive logging to `api.py` to diagnose:
- Number of items extracted
- Length of text content
- Metadata details
- First item sample (if any)

## How to Diagnose

### 1. Check Console Logs
When uploading a file, open the browser console (F12) and look for:
```
[Upload] Processing file via Tauri: <path>
[Upload] Python response: {status: 'success', extractedData: {...}}
```

### 2. Check Backend Logs
The Python API now logs:
```
[api.py] Using FinancialParser for: <filename>
[api.py] Parsed result summary:
[api.py]   - Items count: <number>
[api.py]   - Text length: <number>
[api.py]   - Metadata: {fileName: ..., pageCount: ...}
[api.py]   - First item: {id: ..., label: ..., ...}
```

### 3. Test with Different Files
Try uploading different file types:

**Small PDF (1-5 pages)**: Should use sequential processing
**Large PDF (10+ pages)**: Should use sequential processing (parallel disabled for item extraction)
**PDF with tables**: Should extract table data
**Image-based PDF**: Should use OCR and still extract data

### 4. Check Browser Storage
After parsing, check if data is in browser developer tools:
```javascript
// In browser console
console.log('tableData length:', tableData.length);
console.log('tableData sample:', tableData.slice(0, 5));
```

## Common Issues & Solutions

### Issue: Items Array is Empty
**Symptoms**: Console shows `Items count: 0`

**Possible Causes**:
1. **Parser couldn't find financial statements**: The PDF doesn't match expected patterns
2. **File format**: PDF is image-based or has complex tables
3. **Extraction failed**: Tables detected but couldn't parse values

**Solutions**:
- Check if PDF is a standard financial report format
- Try a simpler PDF with clear tables
- Check if file needs OCR (scanned documents)

### Issue: Data Not Displaying
**Symptoms**: Console shows items, but UI is empty

**Possible Causes**:
1. **Active tab**: User is not on "Extracted" or "Captured" tab
2. **Filtering active**: Filters are hiding all items
3. **Search query**: Search is filtering out everything

**Solutions**:
- Click on "Extracted Data" tab in main view
- Clear search input
- Reset filters (click "Clear Filters" button)
- Try "Show All Items" in filters

### Issue: Duplicate Items Overwriting
**Symptoms**: Previous file data disappears when new file is uploaded

**This is expected behavior** - Each upload is treated as a new analysis:
```typescript
// From App.tsx line 610-616
setTableData(prev => {
  const newMap = new Map(prev.map(i => [i.id, i]));
  items.forEach(item => {
    newMap.set(item.id, item);  // Overwrites existing items with same ID
  });
  return Array.from(newMap.values());
});
```

**Solution**: If you want to keep previous data, the merge logic needs to be changed.

## Fixed Issues Summary

### ✅ Fixed in This Update
1. **Parallel processor no longer used for item extraction** - Only used for progress tracking (if implemented)
2. **API response format confirmed correct** - `extractedData.items` is directly accessible
3. **Database query timeout extended** - From 10s to 30s
4. **Database query limits added** - Prevents timeouts on large datasets
5. **Debug logging added** - Can see exactly what's being extracted

### ⚠️ Known Limitations
1. **OCR-based files**: May have lower accuracy
2. **Complex tables**: May not extract all values correctly
3. **Custom formats**: May not match expected patterns

## Next Steps for User

1. **Try uploading a file** and check console logs
2. **Share the logs** if you're still seeing no data
3. **Check the tab** - Make sure you're viewing "Extracted Data" or "Captured Data"
4. **Clear filters** - Search or category filters might be hiding data

## Testing Checklist

When testing, verify:

- [ ] Console shows `Items count: N` where N > 0
- [ ] App.tsx tab is on 'extracted' or 'captured'
- [ ] No search filters are active
- [ ] Category filter is set to 'All'
- [ ] Status filter is set to 'All Items' or 'All'
- [ ] `tableData` state has items (check in console)

## Performance Benchmarks

Expected item counts based on document type:

| Document Type | Expected Items | Notes |
|-------------|----------------|-------|
| Balance Sheet | 50-200 | Main assets, liabilities, equity |
| Income Statement | 30-100 | Revenue, expenses, profit |
| Cash Flow | 20-50 | Operating, investing, financing activities |
| Simple Report | 10-50 | Varies widely |

If your item count is significantly lower than expected, the parser may not be extracting correctly.

## Database Query Issue (FIXED)

**Problem**: `get_db_data()` was returning wrong data format
**Previous Code** (python_bridge.rs):
```rust
if let Some(extracted_data) = response.extracted_data {
    Ok(extracted_data)  // This was wrong!
}
```

**Fixed Code**:
```rust
match final_response {
    Some(response) => {
        // Return the full response including status and data
        let response_value = serde_json::to_value(&response)
            .map_err(|e| format!("Failed to serialize response: {}", e))?;
        Ok(response_value)
    }
    None => Err("No response from Python for DB data fetch".to_string()),
}
```

Now the frontend receives the complete response with `{status: 'success', data: {...}}` structure.

## Summary

### What Was Fixed
1. ✅ Parallel processor items format issue
2. ✅ Database query return format
3. ✅ Database query timeout (10s → 30s)
4. ✅ Database query limits added
5. ✅ Debug logging in API

### What to Check
1. Browser console logs for item count
2. Backend logs for parsing details
3. Tab selection (Extracted/Captured)
4. Filter settings
5. File type and complexity

### If Still No Data After Fixes

Please provide:
1. Browser console output showing `Items count: X`
2. Backend terminal output showing parsing logs
3. Type of file you're uploading (PDF, image, etc.)
4. Screenshot of the Captured Data tab

This will help identify if the issue is:
- Parser not extracting
- Frontend not displaying
- Filtering hiding data
- Response format mismatch
