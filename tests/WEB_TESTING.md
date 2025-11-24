# Web Interface Testing Guide

## Overview

Testing for web interfaces involves multiple layers:

1. **API Integration Tests** - Test FastAPI endpoints
2. **JavaScript Unit Tests** - Test frontend functions
3. **End-to-End (E2E) Tests** - Test full browser experience

## Why Test the UI?

- **Catch regressions** - Ensure changes don't break existing functionality
- **Document behavior** - Tests serve as documentation
- **Confidence** - Know that features work before deployment
- **Debugging** - Tests help identify where issues occur

## Test Types Explained

### 1. API Integration Tests

**What:** Test FastAPI endpoints using `TestClient`  
**Why:** Verify backend logic without browser overhead  
**Speed:** Fast (no browser needed)  
**Coverage:** Request/response formats, error handling, business logic

**Example:**
```python
def test_get_state(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    assert "current_mode" in response.json()
```

### 2. JavaScript Unit Tests

**What:** Test individual JavaScript functions  
**Why:** Verify frontend logic in isolation  
**Speed:** Very fast  
**Coverage:** Function behavior, DOM manipulation, state management

**Example:**
```javascript
test('togglePanel toggles collapsed class', () => {
    window.togglePanel('status-panel');
    expect(panel.classList.contains('collapsed')).toBe(true);
});
```

### 3. End-to-End Tests

**What:** Test full user flows in real browser  
**Why:** Verify everything works together  
**Speed:** Slower (requires browser)  
**Coverage:** User interactions, visual elements, full workflows

**Example:**
```python
def test_chat_message_send(page):
    page.fill("#chat-input", "Hello")
    page.click("#chat-send-btn")
    expect(page.locator("#chat-history")).to_contain_text("Hello")
```

## Running Tests

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd tests/frontend && npm install

# 2. Run API tests (fastest)
pytest tests/integration/test_api.py -v

# 3. Run E2E tests (requires server)
python app.py &  # Start server
pytest tests/frontend/test_e2e.py -v

# 4. Run JavaScript tests
cd tests/frontend && npm test
```

## What to Test

### Critical UI Features

1. **Page Loads**
   - HTML renders correctly
   - CSS loads
   - JavaScript executes

2. **Interactive Elements**
   - Buttons are clickable
   - Forms submit correctly
   - Panels collapse/expand

3. **State Management**
   - Mode switching works
   - Session state persists
   - UI updates reflect state

4. **API Integration**
   - Endpoints are called correctly
   - Responses are handled
   - Errors are displayed

5. **User Flows**
   - Creating a universe
   - Switching modes
   - Sending chat messages

## Common Issues & Solutions

### Issue: Tests fail because server isn't running

**Solution:** Use `pytest-playwright` fixtures or start server in test setup

### Issue: Tests are flaky (sometimes pass, sometimes fail)

**Solution:** 
- Add explicit waits
- Use `expect().to_be_visible()` instead of immediate checks
- Mock external dependencies

### Issue: JavaScript tests can't access functions

**Solution:** 
- Export functions to `window` scope
- Use proper test environment (Jest with jsdom)
- Load scripts in test setup

## Best Practices

1. **Test User Behavior, Not Implementation**
   - Test "user clicks button" not "function X is called"

2. **Keep Tests Independent**
   - Each test should work in isolation
   - Don't rely on test execution order

3. **Use Descriptive Test Names**
   - `test_user_can_create_universe` not `test_create`

4. **Mock External Dependencies**
   - Don't call real APIs in tests
   - Use mocks for OpenAI, Deepgram, etc.

5. **Test Error Cases**
   - What happens when API fails?
   - What if user input is invalid?

## Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - uses: actions/setup-node@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/integration/test_api.py
      - run: pytest tests/frontend/test_e2e.py
```

## Next Steps

1. ✅ Set up test infrastructure (DONE)
2. ⏳ Write tests for broken UI features
3. ⏳ Add tests for new features
4. ⏳ Set up CI/CD
5. ⏳ Add visual regression testing (optional)

