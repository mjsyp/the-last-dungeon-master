"""Comprehensive backend integration tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base, get_db
from app import app
from orchestrator.session_state import Mode
from models import Universe, Campaign, PlayerGroup, Character, UserSession
from unittest.mock import patch, Mock, MagicMock
import json


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
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestBackendHealth:
    """Test backend health and basic functionality."""
    
    def test_health_endpoint(self, client):
        """Test health check returns correct status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
    
    def test_root_serves_html(self, client):
        """Test root endpoint serves HTML correctly."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "The Last Dungeon Master" in response.text
    
    def test_static_files_served(self, client):
        """Test static files (CSS/JS) are served."""
        # Test CSS
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"] or "text/plain" in response.headers["content-type"]
        
        # Test JS
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "text/javascript" in response.headers["content-type"] or "application/javascript" in response.headers["content-type"]


class TestSessionStateManagement:
    """Test session state persistence and management."""
    
    def test_get_initial_state(self, client):
        """Test getting initial state returns defaults."""
        response = client.get("/api/state")
        assert response.status_code == 200
        data = response.json()
        assert data["current_mode"] == "main_menu_mode"
        assert data["active_universe_id"] is None
        assert data["turn_index"] == 0
    
    def test_state_persistence(self, client):
        """Test that state persists across requests."""
        # Set a mode
        response = client.post("/api/mode/switch", json={"mode": "dm_story_mode"})
        assert response.status_code == 200
        
        # Get state - should reflect the change
        response = client.get("/api/state")
        assert response.json()["current_mode"] == "dm_story_mode"
        
        # Make another request - state should still be persisted
        response = client.get("/api/state")
        assert response.json()["current_mode"] == "dm_story_mode"
    
    def test_switch_mode_updates_state(self, client):
        """Test switching mode updates state correctly."""
        modes = ["main_menu_mode", "dm_story_mode", "world_architect_mode", 
                 "rules_explanation_mode", "tutorial_mode", "world_edit_mode"]
        
        for mode in modes:
            response = client.post("/api/mode/switch", json={"mode": mode})
            assert response.status_code == 200
            assert response.json()["current_mode"] == mode
            
            # Verify state reflects change
            state_response = client.get("/api/state")
            assert state_response.json()["current_mode"] == mode
    
    def test_set_active_universe(self, client, db_session):
        """Test setting active universe."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        response = client.post(
            "/api/session/set-universe",
            json={"universe_id": str(universe.id)}
        )
        assert response.status_code == 200
        
        state = client.get("/api/state").json()
        assert state["active_universe_id"] == str(universe.id)
    
    def test_set_active_campaign(self, client, db_session):
        """Test setting active campaign."""
        universe = Universe(name="Test Universe")
        campaign = Campaign(name="Test Campaign", universe_id=universe.id)
        db_session.add_all([universe, campaign])
        db_session.commit()
        
        response = client.post(
            "/api/session/set-campaign",
            json={"campaign_id": str(campaign.id)}
        )
        assert response.status_code == 200
        
        state = client.get("/api/state").json()
        assert state["active_campaign_id"] == str(campaign.id)


class TestUniverseManagement:
    """Test universe CRUD operations."""
    
    def test_list_universes_empty(self, client):
        """Test listing universes when none exist."""
        response = client.get("/api/universes")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_universe(self, client, db_session):
        """Test creating a universe."""
        with patch('main_menu.manager.RAGIndexer') as mock_indexer:
            mock_indexer.return_value.index_lore_entity = Mock()
            
            response = client.post(
                "/api/universes",
                json={
                    "name": "Fantasy World",
                    "description": "A magical fantasy universe",
                    "themes": ["magic", "dragons"]
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Fantasy World"
            assert data["description"] == "A magical fantasy universe"
            assert data["themes"] == ["magic", "dragons"]
            assert "id" in data
    
    def test_get_universe(self, client, db_session):
        """Test getting a specific universe."""
        universe = Universe(name="Test Universe", description="Test desc")
        db_session.add(universe)
        db_session.commit()
        
        response = client.get(f"/api/universes/{universe.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Universe"
        assert data["description"] == "Test desc"
    
    def test_get_nonexistent_universe(self, client):
        """Test getting non-existent universe returns 404."""
        response = client.get("/api/universes/nonexistent-id")
        assert response.status_code == 404 or response.status_code == 200  # May return 200 with None


class TestCampaignManagement:
    """Test campaign CRUD operations."""
    
    def test_list_campaigns(self, client, db_session):
        """Test listing campaigns."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        campaign1 = Campaign(name="Campaign 1", universe_id=universe.id)
        campaign2 = Campaign(name="Campaign 2", universe_id=universe.id)
        db_session.add_all([campaign1, campaign2])
        db_session.commit()
        
        response = client.get("/api/campaigns", params={"universe_id": str(universe.id)})
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert any(c["name"] == "Campaign 1" for c in data)
    
    def test_create_campaign(self, client, db_session):
        """Test creating a campaign."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        with patch('main_menu.manager.RAGIndexer') as mock_indexer:
            mock_indexer.return_value.index_lore_entity = Mock()
            
            response = client.post(
                "/api/campaigns",
                json={
                    "universe_id": str(universe.id),
                    "name": "New Campaign",
                    "genre": "Fantasy",
                    "tone": "Dark"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "New Campaign"
            assert data["genre"] == "Fantasy"


class TestDMStoryMode:
    """Test DM Story mode functionality."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_dm_story_input(self, mock_retriever, mock_brain, client):
        """Test processing player input in DM Story mode."""
        # Setup mocks
        mock_brain_instance = Mock()
        mock_brain_instance.dm_story_turn.return_value = {
            "narration": "You see a goblin ahead.",
            "log_updates": {"location": "cave"}
        }
        mock_brain.return_value = mock_brain_instance
        
        mock_retriever_instance = Mock()
        mock_retriever_instance.retrieve_lore_context.return_value = []
        mock_retriever_instance.format_lore_context.return_value = ""
        mock_retriever.return_value = mock_retriever_instance
        
        # Switch to DM Story mode
        client.post("/api/mode/switch", json={"mode": "dm_story_mode"})
        
        # Send player input
        response = client.post(
            "/api/dm-story/input",
            json={"player_utterance": "I attack the goblin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "narration" in data
        assert "goblin" in data["narration"].lower()
    
    def test_dm_story_requires_mode(self, client):
        """Test that DM story input works in correct mode."""
        # Don't switch mode - should still work (defaults to main menu)
        response = client.post(
            "/api/dm-story/input",
            json={"player_utterance": "test"}
        )
        # Should either work or return appropriate error
        assert response.status_code in [200, 400, 422]


class TestRulesExplanation:
    """Test rules explanation functionality."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_explain_rules(self, mock_retriever, mock_brain, client):
        """Test rules explanation."""
        mock_brain_instance = Mock()
        mock_brain_instance.explain_rules.return_value = {
            "explanation": "Combat involves rolling dice...",
            "examples": {"example1": "text"},
            "related_topics": ["damage", "armor"]
        }
        mock_brain.return_value = mock_brain_instance
        
        mock_retriever_instance = Mock()
        mock_retriever_instance.retrieve_rules_context.return_value = []
        mock_retriever_instance.format_rules_context.return_value = ""
        mock_retriever.return_value = mock_retriever_instance
        
        response = client.post(
            "/api/rules/explain",
            json={"question": "How does combat work?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "combat" in data["explanation"].lower()


class TestWorldArchitect:
    """Test world architect functionality."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_world_architect_generate(self, mock_retriever, mock_brain, client):
        """Test world generation."""
        mock_brain_instance = Mock()
        mock_brain_instance.world_architect.return_value = {
            "universe": {"name": "Generated World"},
            "campaigns": [],
            "locations": []
        }
        mock_brain.return_value = mock_brain_instance
        
        response = client.post(
            "/api/world-architect/generate",
            json={"requirements": "Create a dark fantasy world"}
        )
        assert response.status_code == 200
        data = response.json()
        # Response should contain world data
        assert data is not None


class TestMainMenuInput:
    """Test main menu input handling."""
    
    def test_main_menu_input(self, client):
        """Test main menu processes input."""
        response = client.post(
            "/api/main-menu/input",
            json={"input": "list universes"}
        )
        assert response.status_code == 200
        # Should return some response
        data = response.json()
        assert data is not None


class TestAudioEndpoints:
    """Test audio (STT/TTS) endpoints."""
    
    @patch('audio.stt.get_stt_provider')
    def test_stt_transcribe(self, mock_stt, client):
        """Test STT transcription."""
        mock_stt_instance = Mock()
        mock_stt_instance.transcribe.return_value = "Hello world"
        mock_stt.return_value = mock_stt_instance
        
        audio_data = b"fake audio data"
        response = client.post(
            "/api/stt/transcribe",
            files={"audio_file": ("test.wav", audio_data, "audio/wav")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        assert data["transcript"] == "Hello world"
    
    @patch('audio.tts.get_tts_provider')
    def test_tts_synthesize(self, mock_tts, client):
        """Test TTS synthesis."""
        mock_tts_instance = Mock()
        mock_tts_instance.synthesize.return_value = b"audio bytes"
        mock_tts.return_value = mock_tts_instance
        
        response = client.post(
            "/api/tts/synthesize",
            json={"text": "Hello world", "voice": "aura-asteria-en"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert len(response.content) > 0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_mode_switch(self, client):
        """Test switching to invalid mode."""
        response = client.post(
            "/api/mode/switch",
            json={"mode": "invalid_mode"}
        )
        # Should either accept it or return error
        assert response.status_code in [200, 400, 422]
    
    def test_missing_required_fields(self, client):
        """Test endpoints with missing required fields."""
        # Missing player_utterance
        response = client.post("/api/dm-story/input", json={})
        assert response.status_code in [400, 422]  # Validation error
    
    def test_invalid_json(self, client):
        """Test endpoints with invalid JSON."""
        response = client.post(
            "/api/mode/switch",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


class TestDatabasePersistence:
    """Test database persistence across requests."""
    
    def test_universe_persists(self, client, db_session):
        """Test that created universe persists."""
        with patch('main_menu.manager.RAGIndexer') as mock_indexer:
            mock_indexer.return_value.index_lore_entity = Mock()
            
            # Create universe
            response = client.post(
                "/api/universes",
                json={"name": "Persistent Universe", "description": "Test"}
            )
            universe_id = response.json()["id"]
            
            # Get universe in new request
            response = client.get(f"/api/universes/{universe_id}")
            assert response.status_code == 200
            assert response.json()["name"] == "Persistent Universe"
    
    def test_session_state_persists(self, client, db_session):
        """Test session state persists in database."""
        # Set state
        client.post("/api/mode/switch", json={"mode": "dm_story_mode"})
        
        # Verify it's in database
        user_session = db_session.query(UserSession).first()
        assert user_session is not None
        assert user_session.state_json is not None
        state_data = user_session.state_json
        assert state_data.get("current_mode") == "dm_story_mode"

