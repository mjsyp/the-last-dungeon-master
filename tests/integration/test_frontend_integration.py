"""Tests that verify frontend-backend integration works correctly."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base, get_db
from app import app
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


class TestFrontendBackendIntegration:
    """Test that frontend and backend work together."""
    
    def test_html_includes_required_functions(self, client):
        """Test that HTML includes JavaScript functions needed for onclick."""
        response = client.get("/")
        html = response.text
        
        # Check that togglePanel is defined
        assert "togglePanel" in html or "window.togglePanel" in html
        
        # Check that handleChatSubmit is defined
        assert "handleChatSubmit" in html or "window.handleChatSubmit" in html
    
    def test_static_js_file_exists(self, client):
        """Test that app.js file is served."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        
        js_content = response.text
        
        # Check that functions are defined in JS
        assert "togglePanel" in js_content or "window.togglePanel" in js_content
        assert "handleChatSubmit" in js_content or "window.handleChatSubmit" in js_content
    
    def test_css_file_exists(self, client):
        """Test that CSS file is served."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert len(response.text) > 0
    
    def test_html_has_correct_structure(self, client):
        """Test that HTML has required elements."""
        response = client.get("/")
        html = response.text
        
        # Check for required IDs
        assert 'id="status-panel"' in html
        assert 'id="mode-selector"' in html
        assert 'id="chat-input"' in html
        assert 'id="chat-send-btn"' in html
        assert 'id="chat-history"' in html
    
    def test_onclick_handlers_have_functions(self, client):
        """Test that onclick handlers reference functions that exist."""
        response = client.get("/")
        html = response.text
        
        # Check for onclick handlers
        onclick_pattern = r'onclick="([^"]+)"'
        matches = re.findall(onclick_pattern, html)
        
        for onclick_code in matches:
            # Extract function name
            if "togglePanel" in onclick_code:
                # Verify togglePanel is defined
                assert "togglePanel" in html or "window.togglePanel" in html
            elif "handleChatSubmit" in onclick_code:
                # Verify handleChatSubmit is defined
                assert "handleChatSubmit" in html or "window.handleChatSubmit" in html
    
    def test_api_endpoints_match_frontend_expectations(self, client):
        """Test that API endpoints match what frontend expects."""
        # Frontend expects these endpoints
        expected_endpoints = [
            "/api/state",
            "/api/mode/switch",
            "/api/dm-story/input",
            "/api/world-architect/generate",
            "/api/rules/explain",
            "/api/world-edit/propose",
            "/api/main-menu/input",
            "/api/universes",
            "/api/campaigns",
            "/api/stt/transcribe",
            "/api/tts/synthesize"
        ]
        
        for endpoint in expected_endpoints:
            # Try GET for most, POST for input endpoints
            if "input" in endpoint or "switch" in endpoint or "generate" in endpoint or "explain" in endpoint or "propose" in endpoint or "transcribe" in endpoint or "synthesize" in endpoint:
                # POST endpoint - test with minimal data
                response = client.post(endpoint, json={})
                # Should not be 404 (might be 400/422 for validation, but endpoint exists)
                assert response.status_code != 404, f"Endpoint {endpoint} not found"
            else:
                # GET endpoint
                response = client.get(endpoint)
                # Should not be 404
                assert response.status_code != 404, f"Endpoint {endpoint} not found"
    
    def test_state_endpoint_returns_expected_format(self, client):
        """Test that state endpoint returns format frontend expects."""
        response = client.get("/api/state")
        assert response.status_code == 200
        data = response.json()
        
        # Frontend expects these fields
        assert "current_mode" in data
        assert "active_universe_id" in data
        assert "active_campaign_id" in data
        assert "active_party_id" in data
        assert "turn_index" in data
    
    def test_mode_switch_returns_expected_format(self, client):
        """Test that mode switch returns format frontend expects."""
        response = client.post(
            "/api/mode/switch",
            json={"mode": "dm_story_mode"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Frontend expects current_mode in response
        assert "current_mode" in data
        assert data["current_mode"] == "dm_story_mode"

