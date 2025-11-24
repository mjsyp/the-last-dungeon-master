# Static Files Testing Guide

## Overview

Comprehensive tests for static file serving (CSS, JS, favicon) and related functionality.

## Issues Fixed

### 1. Static Files Returning 404

**Problem:** `/static/css/style.css`, `/static/js/app.js`, and `/favicon.ico` were returning 404.

**Root Cause:** 
- Static file mounting might not have been using absolute paths
- Mount order might conflict with other routes

**Solution:**
- Use `resolve()` to get absolute paths for static file mounting
- Ensure static files are mounted before other routes
- Added explicit favicon endpoint

### 2. JavaScript Functions Not Defined

**Problem:** `togglePanel is not defined` and `handleChatSubmit is not defined` errors.

**Root Cause:** Functions defined in external JS file might not load before onclick handlers execute.

**Solution:**
- Added inline script definitions in HTML as fallback
- Functions are now available immediately when HTML loads

## Test Files

### `test_static_files.py`
Basic static file serving tests:
- CSS/JS/favicon are served
- Content types are correct
- Files are not served as HTML
- HTML references static files
- JavaScript functions are defined
- Error handling (404s)

### `test_static_files_comprehensive.py`
Comprehensive tests covering:
- File existence on disk
- Content validation
- Onclick handler validation
- Path traversal prevention
- Content type verification
- Function availability checks

## Running Tests

```bash
# Run all static file tests
pytest tests/integration/test_static_files*.py -v

# Run specific test class
pytest tests/integration/test_static_files.py::TestStaticFileServing -v

# Run with detailed output
pytest tests/integration/test_static_files.py -v -s
```

## What Gets Tested

### Static File Serving
- ✅ CSS file is served at `/static/css/style.css`
- ✅ JS file is served at `/static/js/app.js`
- ✅ Favicon is served at `/favicon.ico`
- ✅ Files return 200 status code
- ✅ Files have correct content types
- ✅ Files are not served as HTML (common misconfiguration)

### HTML References
- ✅ HTML includes CSS link tag
- ✅ HTML includes JS script tag
- ✅ HTML includes favicon link (optional)

### JavaScript Functions
- ✅ `togglePanel` is defined in HTML (inline script)
- ✅ `handleChatSubmit` is defined in HTML (inline script)
- ✅ Functions are also in `app.js` file
- ✅ Onclick handlers reference valid functions

### Error Handling
- ✅ Nonexistent files return 404
- ✅ Path traversal attempts are blocked (404/403)
- ✅ Invalid paths are handled gracefully

### Content Validation
- ✅ CSS contains expected selectors
- ✅ JS contains required functions
- ✅ Files are not empty
- ✅ Content looks correct (not HTML)

## Debugging Static File Issues

### Issue: Files return 404

**Check:**
1. Files exist on disk: `ls -la web/static/css/ web/static/js/`
2. Mount path is correct: Check `app.py` static file mounting
3. Server is running from correct directory
4. Path resolution: Use `resolve()` for absolute paths

**Test:**
```python
from fastapi.testclient import TestClient
from app import app
client = TestClient(app)
response = client.get("/static/css/style.css")
print(f"Status: {response.status_code}")
```

### Issue: Files served as HTML

**Check:**
1. Static file mount is before other routes
2. `html=False` parameter in `StaticFiles()`
3. No route conflicts with `/static/*`

**Test:**
```python
response = client.get("/static/css/style.css")
assert not response.text.startswith("<!DOCTYPE")
```

### Issue: JavaScript functions not defined

**Check:**
1. Functions are in `window` scope
2. Inline script defines functions before external JS loads
3. External JS file loads successfully

**Test:**
```python
response = client.get("/")
html = response.text
assert "window.togglePanel" in html
```

## Best Practices

1. **Use Absolute Paths**: Always use `resolve()` for static file paths
2. **Mount Before Routes**: Mount static files before defining other routes
3. **Inline Fallbacks**: Define critical functions inline as fallback
4. **Test Content**: Don't just test status codes, verify content
5. **Error Handling**: Test that missing files return 404, not 500

## Continuous Integration

These tests should run in CI to catch:
- Static file serving regressions
- Missing file issues
- Content type problems
- JavaScript function availability
- Path traversal vulnerabilities

