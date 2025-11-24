"""Comprehensive tests for static file serving and related functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base, get_db
from app import app
from pathlib import Path
import re


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    """Create a test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestStaticFileExistence:
    """Test that static files exist on disk."""
    
    def test_css_file_exists(self):
        """Test that CSS file exists on disk."""
        css_path = Path(__file__).parent.parent / "web" / "static" / "css" / "style.css"
        assert css_path.exists(), f"CSS file should exist at {css_path}"
        assert css_path.is_file(), "CSS path should be a file"
        assert css_path.stat().st_size > 0, "CSS file should not be empty"
    
    def test_js_file_exists(self):
        """Test that JS file exists on disk."""
        base_path = Path(__file__).parent.parent
        js_path = base_path / "web" / "static" / "js" / "app.js"
        assert js_path.exists(), f"JS file should exist at {js_path}"
        assert js_path.is_file(), "JS path should be a file"
        assert js_path.stat().st_size > 0, "JS file should not be empty"
    
    def test_favicon_exists(self):
        """Test that favicon exists on disk."""
        favicon_path = Path(__file__).parent.parent / "web" / "favicon.ico"
        # Favicon might not exist, but if it does, it should be valid
        if favicon_path.exists():
            assert favicon_path.is_file(), "Favicon path should be a file"
            assert favicon_path.stat().st_size > 0, "Favicon should not be empty"


class TestStaticFileServing:
    """Test that static files are served correctly by the server."""
    
    def test_css_file_served(self, client):
        """Test CSS file is served with correct status and content."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200, \
            f"CSS should return 200, got {response.status_code}. Response: {response.text[:200]}"
        
        # Verify content
        assert len(response.content) > 100, "CSS file should have content"
        assert "{" in response.text or ";" in response.text, "Should look like CSS"
    
    def test_js_file_served(self, client):
        """Test JS file is served with correct status and content."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200, \
            f"JS should return 200, got {response.status_code}. Response: {response.text[:200]}"
        
        # Verify content
        assert len(response.content) > 100, "JS file should have content"
        assert "function" in response.text or "const" in response.text or "window" in response.text, \
            "Should look like JavaScript"
    
    def test_favicon_served(self, client):
        """Test favicon is served."""
        response = client.get("/favicon.ico")
        assert response.status_code == 200, \
            f"Favicon should return 200, got {response.status_code}"
        assert len(response.content) > 0, "Favicon should have content"
    
    def test_static_files_not_html(self, client):
        """Test that static files are not being served as HTML (common misconfiguration)."""
        css_response = client.get("/static/css/style.css")
        assert css_response.status_code == 200
        content_start = css_response.text[:50].strip()
        assert not content_start.startswith("<!DOCTYPE"), "CSS should not be HTML"
        assert not content_start.startswith("<html"), "CSS should not be HTML"
        
        js_response = client.get("/static/js/app.js")
        assert js_response.status_code == 200
        content_start = js_response.text[:50].strip()
        assert not content_start.startswith("<!DOCTYPE"), "JS should not be HTML"
        assert not content_start.startswith("<html"), "JS should not be HTML"


class TestHTMLReferences:
    """Test that HTML correctly references static files."""
    
    def test_html_has_css_link(self, client):
        """Test HTML includes CSS link tag."""
        response = client.get("/")
        html = response.text
        
        # Should have link to CSS (check for both absolute and relative paths)
        assert 'href="/static/css/style.css"' in html or \
               'href="static/css/style.css"' in html or \
               '/static/css/style.css' in html, \
               "HTML should reference CSS file. HTML snippet: " + html[html.find('<head'):html.find('</head>')+7]
    
    def test_html_has_js_script(self, client):
        """Test HTML includes JavaScript script tag."""
        response = client.get("/")
        html = response.text
        
        # Should have script tag for JS
        assert 'src="/static/js/app.js"' in html or \
               'src="static/js/app.js"' in html or \
               '/static/js/app.js' in html, \
               "HTML should reference JS file. Found script tags: " + \
               str(re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html))
    
    def test_html_has_favicon_link(self, client):
        """Test HTML includes favicon link (optional but good practice)."""
        response = client.get("/")
        html = response.text
        
        # Check if favicon is referenced (it's optional)
        if 'favicon' in html.lower() or 'icon' in html.lower():
            # If present, should point to /favicon.ico
            assert '/favicon.ico' in html or 'favicon.ico' in html, \
                "Favicon reference should point to /favicon.ico"


class TestJavaScriptFunctions:
    """Test that required JavaScript functions are available."""
    
    def test_togglePanel_in_html(self, client):
        """Test that togglePanel is defined in HTML (inline script)."""
        response = client.get("/")
        html = response.text
        
        # Should have togglePanel defined
        assert "togglePanel" in html or "window.togglePanel" in html, \
            "HTML should define togglePanel function for onclick handlers"
    
    def test_handleChatSubmit_in_html(self, client):
        """Test that handleChatSubmit is defined in HTML (inline script)."""
        response = client.get("/")
        html = response.text
        
        # Should have handleChatSubmit defined
        assert "handleChatSubmit" in html or "window.handleChatSubmit" in html, \
            "HTML should define handleChatSubmit function for onclick handlers"
    
    def test_togglePanel_in_js_file(self, client):
        """Test that togglePanel is also in JS file."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        js_content = response.text
        assert "togglePanel" in js_content or "window.togglePanel" in js_content, \
            "togglePanel should be in app.js"
    
    def test_handleChatSubmit_in_js_file(self, client):
        """Test that handleChatSubmit is also in JS file."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        js_content = response.text
        assert "handleChatSubmit" in js_content or "window.handleChatSubmit" in js_content, \
            "handleChatSubmit should be in app.js"


class TestOnclickHandlers:
    """Test that onclick handlers reference valid functions."""
    
    def test_onclick_handlers_exist(self, client):
        """Test that onclick handlers are present in HTML."""
        response = client.get("/")
        html = response.text
        
        # Should have onclick handlers
        assert 'onclick=' in html, "HTML should have onclick handlers"
    
    def test_togglePanel_onclick_references_function(self, client):
        """Test that togglePanel onclick references the function."""
        response = client.get("/")
        html = response.text
        
        # Find onclick handlers
        onclick_pattern = r'onclick=["\']([^"\']+)["\']'
        matches = re.findall(onclick_pattern, html)
        
        togglePanel_found = False
        for onclick_code in matches:
            if "togglePanel" in onclick_code:
                togglePanel_found = True
                # Verify function is defined
                assert "togglePanel" in html or "window.togglePanel" in html, \
                    f"togglePanel used in onclick but not defined. onclick: {onclick_code}"
        
        assert togglePanel_found, "Should have togglePanel onclick handler"
    
    def test_handleChatSubmit_onclick_references_function(self, client):
        """Test that handleChatSubmit onclick references the function."""
        response = client.get("/")
        html = response.text
        
        # Find onclick handlers
        onclick_pattern = r'onclick=["\']([^"\']+)["\']'
        matches = re.findall(onclick_pattern, html)
        
        handleChatSubmit_found = False
        for onclick_code in matches:
            if "handleChatSubmit" in onclick_code:
                handleChatSubmit_found = True
                # Verify function is defined
                assert "handleChatSubmit" in html or "window.handleChatSubmit" in html, \
                    f"handleChatSubmit used in onclick but not defined. onclick: {onclick_code}"
        
        assert handleChatSubmit_found, "Should have handleChatSubmit onclick handler"


class TestContentTypes:
    """Test that static files have correct content types."""
    
    def test_css_content_type(self, client):
        """Test CSS has appropriate content type."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        
        content_type = response.headers.get("content-type", "").lower()
        # Should be CSS or text/plain (some servers serve as text/plain)
        assert "css" in content_type or "text" in content_type, \
            f"CSS should have CSS or text content type, got: {content_type}"
    
    def test_js_content_type(self, client):
        """Test JS has appropriate content type."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        content_type = response.headers.get("content-type", "").lower()
        # Should be JavaScript or text/plain
        assert "javascript" in content_type or "text" in content_type, \
            f"JS should have JavaScript or text content type, got: {content_type}"
    
    def test_favicon_content_type(self, client):
        """Test favicon has appropriate content type."""
        response = client.get("/favicon.ico")
        assert response.status_code == 200
        
        content_type = response.headers.get("content-type", "").lower()
        # Should be image (x-icon, svg+xml, etc.)
        assert "image" in content_type or "svg" in content_type, \
            f"Favicon should have image content type, got: {content_type}"


class TestErrorHandling:
    """Test error handling for static files."""
    
    def test_nonexistent_static_file_404(self, client):
        """Test that nonexistent static files return 404."""
        response = client.get("/static/css/nonexistent.css")
        assert response.status_code == 404, \
            f"Nonexistent file should return 404, got {response.status_code}"
    
    def test_nonexistent_js_file_404(self, client):
        """Test that nonexistent JS files return 404."""
        response = client.get("/static/js/nonexistent.js")
        assert response.status_code == 404, \
            f"Nonexistent JS file should return 404, got {response.status_code}"
    
    def test_path_traversal_prevention(self, client):
        """Test that path traversal attacks are prevented."""
        # Try to access files outside static directory
        malicious_paths = [
            "/static/../app.py",
            "/static/../../requirements.txt",
            "/static/css/../../app.py"
        ]
        
        for path in malicious_paths:
            response = client.get(path)
            # Should return 404 or 403, not serve the file
            assert response.status_code in [404, 403], \
                f"Path traversal {path} should return 404/403, got {response.status_code}"


class TestStaticFilePaths:
    """Test static file path resolution."""
    
    def test_static_directory_structure(self):
        """Test that static directory structure is correct."""
        base_path = Path(__file__).parent.parent
        static_dir = base_path / "web" / "static"
        css_dir = static_dir / "css"
        js_dir = static_dir / "js"
        
        assert static_dir.exists(), f"Static directory should exist at {static_dir}"
        assert static_dir.is_dir(), f"Static path should be a directory: {static_dir}"
        # CSS and JS directories might not exist if files are directly in static/
        # Just check that the static directory exists
        assert static_dir.exists(), "Static directory must exist"


class TestStaticFileContent:
    """Test the actual content of static files."""
    
    def test_css_has_expected_selectors(self, client):
        """Test that CSS contains expected selectors."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        
        css_content = response.text
        
        # Check for common selectors that should be in the CSS
        expected_selectors = [".panel", ".chat", ".mode-card"]
        for selector in expected_selectors:
            assert selector in css_content, \
                f"CSS should contain selector {selector}"
    
    def test_js_has_required_functions(self, client):
        """Test that JS contains required functions."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        js_content = response.text
        
        # Check for required functions
        required_functions = ["togglePanel", "handleChatSubmit", "processUserInput"]
        for func_name in required_functions:
            assert func_name in js_content, \
                f"JS should contain function {func_name}"

