"""Integration tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base, get_db
from app import app
from orchestrator.session_state import Mode
from models import Universe, Campaign, PlayerGroup
from unittest.mock import patch, Mock


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


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestStateEndpoint:
    """Tests for state management endpoints."""
    
    def test_get_state(self, client):
        """Test getting current state."""
        response = client.get("/api/state")
        assert response.status_code == 200
        data = response.json()
        assert "current_mode" in data
        assert "active_universe_id" in data
        assert "active_campaign_id" in data
        assert "turn_index" in data
    
    def test_switch_mode(self, client):
        """Test switching modes."""
        response = client.post(
            "/api/mode/switch",
            json={"mode": "dm_story_mode"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_mode"] == "dm_story_mode"
        
        # Verify state was updated
        state_response = client.get("/api/state")
        assert state_response.json()["current_mode"] == "dm_story_mode"


class TestMainMenuEndpoints:
    """Tests for main menu API endpoints."""
    
    def test_list_universes_empty(self, client):
        """Test listing universes when none exist."""
        response = client.get("/api/universes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_universe(self, client, db_session):
        """Test creating a universe."""
        with patch('main_menu.manager.RAGIndexer') as mock_indexer:
            mock_indexer.return_value.index_lore_entity = Mock()
            
            response = client.post(
                "/api/universes",
                json={
                    "name": "Test Universe",
                    "description": "A test universe",
                    "themes": ["fantasy"]
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Test Universe"
            assert "id" in data
    
    def test_get_universe(self, client, db_session):
        """Test getting a specific universe."""
        # Create universe first
        universe = Universe(name="Test Universe", description="Test")
        db_session.add(universe)
        db_session.commit()
        
        response = client.get(f"/api/universes/{universe.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Universe"
    
    def test_list_campaigns(self, client, db_session):
        """Test listing campaigns."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        campaign = Campaign(name="Test Campaign", universe_id=universe.id)
        db_session.add(campaign)
        db_session.commit()
        
        response = client.get("/api/campaigns", params={"universe_id": str(universe.id)})
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(c["name"] == "Test Campaign" for c in data)


class TestDMStoryEndpoints:
    """Tests for DM Story mode endpoints."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_dm_story_input(self, mock_retriever, mock_brain, client):
        """Test DM story input processing."""
        # Mock the orchestrator's dependencies
        mock_brain_instance = Mock()
        mock_brain_instance.dm_story_turn.return_value = {
            "narration": "You see a goblin",
            "log_updates": {}
        }
        mock_brain.return_value = mock_brain_instance
        
        response = client.post(
            "/api/dm-story/input",
            json={"player_utterance": "I attack the goblin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "narration" in data


class TestRulesEndpoints:
    """Tests for rules explanation endpoints."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_explain_rules(self, mock_retriever, mock_brain, client):
        """Test rules explanation."""
        mock_brain_instance = Mock()
        mock_brain_instance.explain_rules.return_value = {
            "explanation": "Combat works like this...",
            "examples": {},
            "related_topics": []
        }
        mock_brain.return_value = mock_brain_instance
        
        response = client.post(
            "/api/rules/explain",
            json={"question": "How does combat work?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data


class TestWorldArchitectEndpoints:
    """Tests for world architect endpoints."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_world_architect_generate(self, mock_retriever, mock_brain, client):
        """Test world generation."""
        mock_brain_instance = Mock()
        mock_brain_instance.world_architect.return_value = {
            "universe": {"name": "Test World"},
            "campaigns": []
        }
        mock_brain.return_value = mock_brain_instance
        
        response = client.post(
            "/api/world-architect/generate",
            json={"requirements": "Create a fantasy world"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "universe" in data or "world" in str(data).lower()


class TestSessionEndpoints:
    """Tests for session management endpoints."""
    
    def test_set_universe(self, client, db_session):
        """Test setting active universe."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        response = client.post(
            "/api/session/set-universe",
            json={"universe_id": str(universe.id)}
        )
        assert response.status_code == 200
        
        # Verify state was updated
        state_response = client.get("/api/state")
        assert state_response.json()["active_universe_id"] == str(universe.id)
    
    def test_set_campaign(self, client, db_session):
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
        
        state_response = client.get("/api/state")
        assert state_response.json()["active_campaign_id"] == str(campaign.id)


class TestAudioEndpoints:
    """Tests for audio endpoints."""
    
    @patch('audio.stt.get_stt_provider')
    def test_stt_transcribe(self, mock_stt, client):
        """Test STT transcription."""
        mock_stt_instance = Mock()
        mock_stt_instance.transcribe.return_value = "Hello world"
        mock_stt.return_value = mock_stt_instance
        
        # Create a fake audio file
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


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_serves_html(self, client):
        """Test that root endpoint serves HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "The Last Dungeon Master" in response.text

