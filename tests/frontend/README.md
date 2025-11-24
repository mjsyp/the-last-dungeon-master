# Frontend Testing Guide

## Overview

This directory contains tests for the web interface and frontend JavaScript code.

## Test Types

### 1. API Integration Tests (`test_api.py`)

Tests FastAPI endpoints using FastAPI's `TestClient`.

**Run:**
```bash
pytest tests/integration/test_api.py -v
```

**Coverage:**
- Health check endpoint
- State management endpoints
- Main menu CRUD operations
- DM Story mode endpoints
- Rules explanation endpoints
- World architect endpoints
- Session management
- Audio endpoints (STT/TTS)

### 2. JavaScript Unit Tests (`test_js_functions.js`)

Basic JavaScript function tests that can run in browser console or with a test framework.

**Run in browser console:**
```javascript
// Load the test file, then:
runFrontendTests();
```

**Or use Jest:**
```bash
cd tests/frontend
npm install
npm test
```

### 3. End-to-End Tests (`test_e2e.py`)

Full browser tests using Playwright.

**Setup:**
```bash
pip install pytest-playwright
playwright install
```

**Run:**
```bash
# Start server first
python app.py

# In another terminal
pytest tests/frontend/test_e2e.py -v
```

**Coverage:**
- Page loading
- Panel interactions
- Mode selection
- Chat functionality
- Audio controls
- API integration from browser

## Test Structure

```
tests/
├── integration/
│   └── test_api.py          # FastAPI endpoint tests
└── frontend/
    ├── test_js_functions.js  # JavaScript unit tests
    ├── test_e2e.py          # Playwright E2E tests
    ├── __tests__/
    │   └── app.test.js      # Jest tests for JS
    ├── package.json         # Node.js dependencies
    └── jest.setup.js        # Jest configuration
```

## Running All Frontend Tests

```bash
# 1. API Integration Tests
pytest tests/integration/test_api.py -v

# 2. JavaScript Tests (if using Jest)
cd tests/frontend && npm test

# 3. E2E Tests (requires running server)
pytest tests/frontend/test_e2e.py -v
```

## What Gets Tested

### API Endpoints
- ✅ All GET/POST endpoints
- ✅ Request/response formats
- ✅ Error handling
- ✅ State persistence

### Frontend JavaScript
- ✅ Panel toggling
- ✅ Mode switching
- ✅ Chat message handling
- ✅ API routing logic
- ✅ UI state updates

### E2E User Flows
- ✅ Page loads correctly
- ✅ Interactive elements work
- ✅ API calls succeed
- ✅ State updates reflect in UI

## Debugging

### API Tests
```bash
# Run with print statements
pytest tests/integration/test_api.py -v -s

# Run specific test
pytest tests/integration/test_api.py::TestHealthEndpoint::test_health_check -v
```

### E2E Tests
```bash
# Run with browser visible
pytest tests/frontend/test_e2e.py --headed

# Run in slow motion
pytest tests/frontend/test_e2e.py --slowmo 1000
```

## Continuous Integration

Add to CI/CD pipeline:
```yaml
# Example GitHub Actions
- name: Run API Tests
  run: pytest tests/integration/test_api.py

- name: Run E2E Tests
  run: |
    python app.py &
    sleep 5
    pytest tests/frontend/test_e2e.py
```

## Notes

- E2E tests require the server to be running
- Some tests mock external dependencies (OpenAI, Deepgram)
- JavaScript tests can run in browser console for quick debugging
- Playwright tests require browser binaries (installed via `playwright install`)

