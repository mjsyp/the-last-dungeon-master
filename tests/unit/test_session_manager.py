"""Unit tests for session manager."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base
from orchestrator.session_manager import SessionManager
from orchestrator.session_state import SessionState, Mode
from models.user_session import UserSession
from uuid import uuid4


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


class TestSessionManager:
    """Tests for SessionManager."""
    
    def test_load_state_default(self, db_session):
        """Test loading default state when none exists."""
        manager = SessionManager(db_session, "test_session")
        state = manager.load_state()
        
        assert isinstance(state, SessionState)
        assert state.current_mode == Mode.MAIN_MENU
        assert state.active_universe_id is None
    
    def test_load_state_from_db(self, db_session):
        """Test loading state that exists in database."""
        from models.user_session import UserSession
        import json
        
        # Create a saved state
        state_dict = {
            "current_mode": "dm_story_mode",
            "turn_index": 3,
            "recent_history": ["test"],
            "active_universe_id": None,
            "active_campaign_id": None,
            "active_party_id": None,
            "active_session_id": None,
            "current_location_id": None,
            "active_character_ids": [],
            "tutorial_script_id": None,
            "tutorial_step": 0,
            "pending_world_change_request_id": None,
            "metadata": {}
        }
        
        user_session = UserSession(
            session_id="test_session",
            state_json=state_dict
        )
        db_session.add(user_session)
        db_session.commit()
        
        manager = SessionManager(db_session, "test_session")
        state = manager.load_state()
        
        assert state.current_mode == Mode.DM_STORY
        assert state.turn_index == 3
        assert state.recent_history == ["test"]
    
    def test_save_and_load_state(self, db_session):
        """Test saving and loading state."""
        manager = SessionManager(db_session, "test_session")
        
        # Create and save state
        state = SessionState(
            current_mode=Mode.DM_STORY,
            turn_index=5,
            recent_history=["entry1", "entry2"]
        )
        universe_id = uuid4()
        state.active_universe_id = universe_id
        
        manager.save_state(state)
        
        # Load state
        loaded_state = manager.load_state()
        
        assert loaded_state.current_mode == Mode.DM_STORY
        assert loaded_state.turn_index == 5
        assert loaded_state.recent_history == ["entry1", "entry2"]
        assert str(loaded_state.active_universe_id) == str(universe_id)
    
    def test_serialize_state(self, db_session):
        """Test state serialization."""
        manager = SessionManager(db_session, "test_session")
        state = SessionState(
            current_mode=Mode.DM_STORY,
            turn_index=10,
            recent_history=["test"]
        )
        universe_id = uuid4()
        state.active_universe_id = universe_id
        
        serialized = manager._serialize_state(state)
        
        assert serialized["current_mode"] == "dm_story_mode"
        assert serialized["turn_index"] == 10
        assert serialized["recent_history"] == ["test"]
        assert serialized["active_universe_id"] == str(universe_id)
    
    def test_deserialize_state(self, db_session):
        """Test state deserialization."""
        manager = SessionManager(db_session, "test_session")
        universe_id = uuid4()
        
        state_dict = {
            "current_mode": "dm_story_mode",
            "turn_index": 5,
            "recent_history": ["entry1"],
            "active_universe_id": str(universe_id),
            "active_campaign_id": None,
            "active_party_id": None,
            "active_session_id": None,
            "current_location_id": None,
            "active_character_ids": [],
            "tutorial_script_id": None,
            "tutorial_step": 0,
            "pending_world_change_request_id": None,
            "metadata": {}
        }
        
        state = manager._deserialize_state(state_dict)
        
        assert state.current_mode == Mode.DM_STORY
        assert state.turn_index == 5
        assert state.recent_history == ["entry1"]
        assert str(state.active_universe_id) == str(universe_id)
    
    def test_deserialize_invalid_mode(self, db_session):
        """Test deserialization with invalid mode falls back to MAIN_MENU."""
        manager = SessionManager(db_session, "test_session")
        
        state_dict = {
            "current_mode": "invalid_mode",
            "turn_index": 0,
            "recent_history": [],
            "active_universe_id": None,
            "active_campaign_id": None,
            "active_party_id": None,
            "active_session_id": None,
            "current_location_id": None,
            "active_character_ids": [],
            "tutorial_script_id": None,
            "tutorial_step": 0,
            "pending_world_change_request_id": None,
            "metadata": {}
        }
        
        state = manager._deserialize_state(state_dict)
        
        assert state.current_mode == Mode.MAIN_MENU  # Should fall back
    
    def test_multiple_sessions(self, db_session):
        """Test that different session IDs maintain separate state."""
        manager1 = SessionManager(db_session, "session1")
        manager2 = SessionManager(db_session, "session2")
        
        state1 = SessionState(current_mode=Mode.DM_STORY, turn_index=1)
        state2 = SessionState(current_mode=Mode.WORLD_ARCHITECT, turn_index=2)
        
        manager1.save_state(state1)
        manager2.save_state(state2)
        
        loaded1 = manager1.load_state()
        loaded2 = manager2.load_state()
        
        assert loaded1.current_mode == Mode.DM_STORY
        assert loaded2.current_mode == Mode.WORLD_ARCHITECT

