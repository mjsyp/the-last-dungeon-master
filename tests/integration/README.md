# Backend Integration Tests

## Overview

Comprehensive integration tests for the backend API and frontend-backend integration.

## Test Files

### 1. `test_backend.py` - Backend API Tests

Tests all FastAPI endpoints and backend functionality:

- **Health & Basic** - Health checks, static file serving
- **Session State** - State management, persistence, mode switching
- **Universe Management** - CRUD operations for universes
- **Campaign Management** - CRUD operations for campaigns
- **DM Story Mode** - Story mode input processing
- **Rules Explanation** - Rules explanation functionality
- **World Architect** - World generation
- **Main Menu** - Main menu input handling
- **Audio** - STT/TTS endpoints
- **Error Handling** - Invalid inputs, missing fields
- **Database Persistence** - Data persistence across requests

### 2. `test_frontend_integration.py` - Frontend-Backend Integration

Tests that verify frontend and backend work together:

- **HTML Structure** - Required elements and IDs
- **JavaScript Functions** - Functions available for onclick handlers
- **Static Files** - CSS/JS files are served correctly
- **API Endpoints** - Endpoints match frontend expectations
- **Response Formats** - API responses match frontend expectations

### 3. `test_api.py` - Original API Tests

Original API endpoint tests (may overlap with test_backend.py).

## Running Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run backend tests only
pytest tests/integration/test_backend.py -v

# Run frontend integration tests
pytest tests/integration/test_frontend_integration.py -v

# Run specific test class
pytest tests/integration/test_backend.py::TestSessionStateManagement -v

# Run with coverage
pytest tests/integration/ --cov=. --cov-report=html
```

## What Gets Tested

### Backend Functionality
- ✅ All API endpoints
- ✅ Request/response formats
- ✅ Error handling
- ✅ Database persistence
- ✅ State management
- ✅ Mode switching
- ✅ CRUD operations

### Frontend-Backend Integration
- ✅ HTML includes required JavaScript functions
- ✅ Static files are served
- ✅ API endpoints exist and work
- ✅ Response formats match frontend expectations
- ✅ onclick handlers have corresponding functions

## Common Issues Found

### JavaScript Function Errors
- **Issue**: `togglePanel is not defined`
- **Test**: `test_html_includes_required_functions`
- **Fix**: Ensure functions are defined in window scope before HTML loads

### Missing API Endpoints
- **Issue**: Frontend calls endpoint that doesn't exist
- **Test**: `test_api_endpoints_match_frontend_expectations`
- **Fix**: Add missing endpoint or update frontend

### Response Format Mismatches
- **Issue**: Frontend expects different response format
- **Test**: `test_state_endpoint_returns_expected_format`
- **Fix**: Update API response or frontend parsing

## Debugging

```bash
# Run with print statements
pytest tests/integration/ -v -s

# Run specific failing test
pytest tests/integration/test_backend.py::TestSessionStateManagement::test_state_persistence -v

# Show full traceback
pytest tests/integration/ -v --tb=long
```

## Continuous Integration

These tests should run in CI/CD to catch:
- Backend API regressions
- Frontend-backend integration issues
- Database persistence problems
- Missing JavaScript functions

