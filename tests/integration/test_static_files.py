"""Tests for static file serving."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base, get_db
from app import app
from pathlib import Path


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


class TestStaticFileServing:
    """Test static file serving."""
    
    def test_css_file_served(self, client):
        """Test that CSS file is served correctly."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200, f"CSS file not found. Status: {response.status_code}"
        
        # Verify it's CSS content
        assert "text/css" in response.headers.get("content-type", "") or \
               len(response.text) > 0, "CSS file is empty or wrong content type"
        
        # Verify CSS content exists
        assert len(response.text) > 100, "CSS file seems too small"
        # Check for common CSS patterns
        assert "{" in response.text or ";" in response.text, "Doesn't look like CSS"
    
    def test_js_file_served(self, client):
        """Test that JavaScript file is served correctly."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200, f"JS file not found. Status: {response.status_code}"
        
        # Verify it's JavaScript content
        content_type = response.headers.get("content-type", "")
        assert "javascript" in content_type or "text/plain" in content_type or \
               len(response.text) > 0, "JS file is empty or wrong content type"
        
        # Verify JS content exists
        assert len(response.text) > 100, "JS file seems too small"
        # Check for common JS patterns
        assert "function" in response.text or "const" in response.text or \
               "window" in response.text, "Doesn't look like JavaScript"
    
    def test_favicon_served(self, client):
        """Test that favicon is served."""
        response = client.get("/favicon.ico")
        assert response.status_code == 200, f"Favicon not found. Status: {response.status_code}"
        
        # Should return some content
        assert len(response.content) > 0, "Favicon is empty"
    
    def test_static_files_have_correct_paths(self, client):
        """Test that static files are accessible at expected paths."""
        static_files = [
            "/static/css/style.css",
            "/static/js/app.js"
        ]
        
        for file_path in static_files:
            response = client.get(file_path)
            assert response.status_code == 200, \
                f"Static file {file_path} not found (status: {response.status_code})"
            assert len(response.content) > 0, f"Static file {file_path} is empty"
    
    def test_nonexistent_static_file_returns_404(self, client):
        """Test that nonexistent static files return 404."""
        response = client.get("/static/css/nonexistent.css")
        assert response.status_code == 404, "Nonexistent file should return 404"
    
    def test_static_files_content_type(self, client):
        """Test that static files have correct content types."""
        # CSS should have CSS content type
        css_response = client.get("/static/css/style.css")
        assert css_response.status_code == 200
        # Content type might vary, but should not be HTML
        content_type = css_response.headers.get("content-type", "")
        assert "html" not in content_type.lower(), "CSS should not be served as HTML"
        
        # JS should have JavaScript content type
        js_response = client.get("/static/js/app.js")
        assert js_response.status_code == 200
        content_type = js_response.headers.get("content-type", "")
        assert "html" not in content_type.lower(), "JS should not be served as HTML"
    
    def test_static_files_are_not_html(self, client):
        """Test that static files are not being served as HTML (common misconfiguration)."""
        css_response = client.get("/static/css/style.css")
        assert css_response.status_code == 200
        # Should not start with HTML tags
        content = css_response.text[:100]
        assert not content.strip().startswith("<!DOCTYPE"), \
            "CSS file is being served as HTML"
        assert not content.strip().startswith("<html"), \
            "CSS file is being served as HTML"
        
        js_response = client.get("/static/js/app.js")
        assert js_response.status_code == 200
        content = js_response.text[:100]
        assert not content.strip().startswith("<!DOCTYPE"), \
            "JS file is being served as HTML"
        assert not content.strip().startswith("<html"), \
            "JS file is being served as HTML"


class TestHTMLReferences:
    """Test that HTML correctly references static files."""
    
    def test_html_references_css(self, client):
        """Test that HTML includes CSS link."""
        response = client.get("/")
        html = response.text
        
        # Should have link to CSS
        assert 'href="/static/css/style.css"' in html or \
               'href="static/css/style.css"' in html, \
               "HTML should reference CSS file"
    
    def test_html_references_js(self, client):
        """Test that HTML includes JavaScript script tag."""
        response = client.get("/")
        html = response.text
        
        # Should have script tag for JS
        assert 'src="/static/js/app.js"' in html or \
               'src="static/js/app.js"' in html, \
               "HTML should reference JS file"
    
    def test_html_has_favicon_link(self, client):
        """Test that HTML includes favicon link (optional but good practice)."""
        response = client.get("/")
        html = response.text
        
        # Favicon link is optional, but if present should be correct
        if 'favicon' in html.lower():
            assert '/favicon.ico' in html or 'favicon.ico' in html, \
                "Favicon reference should point to /favicon.ico"


class TestJavaScriptFunctions:
    """Test that JavaScript functions are available."""
    
    def test_js_file_contains_togglePanel(self, client):
        """Test that togglePanel function is defined in JS."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        js_content = response.text
        
        # Should have togglePanel function
        assert "togglePanel" in js_content or "window.togglePanel" in js_content, \
            "togglePanel function should be in app.js"
    
    def test_js_file_contains_handleChatSubmit(self, client):
        """Test that handleChatSubmit function is defined in JS."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        js_content = response.text
        
        # Should have handleChatSubmit function
        assert "handleChatSubmit" in js_content or "window.handleChatSubmit" in js_content, \
            "handleChatSubmit function should be in app.js"
    
    def test_html_defines_functions_inline(self, client):
        """Test that HTML has inline script defining functions (fallback)."""
        response = client.get("/")
        html = response.text
        
        # Should have inline script with togglePanel
        assert "window.togglePanel" in html or "togglePanel" in html, \
            "HTML should define togglePanel function"
        
        # Should have inline script with handleChatSubmit
        assert "window.handleChatSubmit" in html or "handleChatSubmit" in html, \
            "HTML should define handleChatSubmit function"


class TestStaticFilePaths:
    """Test static file path resolution."""
    
    def test_static_directory_structure(self):
        """Test that static directory structure exists."""
        base_path = Path(__file__).parent.parent
        static_dir = base_path / "web" / "static"
        css_path = static_dir / "css" / "style.css"
        js_path = static_dir / "js" / "app.js"
        
        assert static_dir.exists(), f"Static directory should exist at {static_dir}"
        assert css_path.exists(), f"CSS file should exist at {css_path}"
        assert js_path.exists(), f"JS file should exist at {js_path}"
    
    def test_static_files_are_readable(self):
        """Test that static files can be read."""
        base_path = Path(__file__).parent.parent
        css_path = base_path / "web" / "static" / "css" / "style.css"
        js_path = base_path / "web" / "static" / "js" / "app.js"
        
        if css_path.exists():
            css_content = css_path.read_text()
            assert len(css_content) > 0, "CSS file should not be empty"
        
        if js_path.exists():
            js_content = js_path.read_text()
            assert len(js_content) > 0, "JS file should not be empty"


class TestErrorHandling:
    """Test error handling for static files."""
    
    def test_missing_static_file_handled_gracefully(self, client):
        """Test that missing static files return 404, not 500."""
        response = client.get("/static/css/missing.css")
        assert response.status_code == 404, "Missing file should return 404, not 500"
    
    def test_invalid_static_path_returns_404(self, client):
        """Test that invalid static paths return 404."""
        invalid_paths = [
            "/static/../app.py",  # Path traversal attempt
            "/static/../../etc/passwd",  # Path traversal attempt
            "/static/css/",  # Directory listing (should be 404 or 403)
        ]
        
        for path in invalid_paths:
            response = client.get(path)
            assert response.status_code in [404, 403], \
                f"Invalid path {path} should return 404 or 403, got {response.status_code}"

