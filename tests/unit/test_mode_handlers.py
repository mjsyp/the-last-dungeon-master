"""Unit tests for mode handlers."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base
from orchestrator.mode_handler import (
    DMStoryModeHandler,
    RulesExplanationModeHandler,
    WorldEditModeHandler,
    WorldArchitectModeHandler,
    TutorialModeHandler,
    MainMenuModeHandler
)
from unittest.mock import Mock, patch, MagicMock
from orchestrator.session_state import Mode


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
def mock_dm_brain():
    """Mock DMBrain."""
    return Mock()


@pytest.fixture
def mock_retriever():
    """Mock RAGRetriever."""
    return Mock()


class TestDMStoryModeHandler:
    """Tests for DMStoryModeHandler."""
    
    def test_process(self, db_session, mock_dm_brain, mock_retriever):
        """Test DM story mode processing."""
        handler = DMStoryModeHandler(db_session, mock_dm_brain, mock_retriever)
        
        # Mock retriever
        from rag.retriever import RetrievedChunk
        mock_retriever.retrieve_lore_context.return_value = [
            RetrievedChunk("Lore text", {}, 0.9)
        ]
        
        # Mock DM brain
        mock_dm_brain.dm_story_turn.return_value = {
            "narration": "You see a goblin",
            "log_updates": {"location": "cave"}
        }
        
        from orchestrator.session_state import SessionState
        state = SessionState()
        result = handler.handle(state, {"player_utterance": "I attack the goblin"})
        
        assert "narration" in result
        assert result["narration"] == "You see a goblin"
        mock_dm_brain.dm_story_turn.assert_called_once()


class TestRulesExplanationModeHandler:
    """Tests for RulesExplanationModeHandler."""
    
    def test_process(self, db_session, mock_dm_brain, mock_retriever):
        """Test rules explanation mode processing."""
        handler = RulesExplanationModeHandler(db_session, mock_dm_brain, mock_retriever)
        
        # Mock retriever
        from rag.retriever import RetrievedChunk
        mock_retriever.retrieve_rules_context.return_value = [
            RetrievedChunk("Rules text", {}, 0.9)
        ]
        
        # Mock DM brain
        mock_dm_brain.explain_rules.return_value = {
            "explanation": "Combat works like this...",
            "examples": {},
            "related_topics": []
        }
        
        from orchestrator.session_state import SessionState
        state = SessionState()
        result = handler.handle(state, {"question": "How does combat work?"})
        
        assert "explanation" in result
        assert "combat" in result["explanation"].lower()
        mock_dm_brain.explain_rules.assert_called_once()


class TestWorldEditModeHandler:
    """Tests for WorldEditModeHandler."""
    
    def test_process(self, db_session, mock_dm_brain, mock_retriever):
        """Test world edit mode processing."""
        handler = WorldEditModeHandler(db_session, mock_dm_brain, mock_retriever)
        
        # Mock retriever
        from rag.retriever import RetrievedChunk
        mock_retriever.retrieve_lore_context.return_value = [
            RetrievedChunk("Lore text", {}, 0.9)
        ]
        
        # Mock DM brain
        mock_dm_brain.process_world_edit.return_value = {
            "narration": "Change analyzed",
            "world_edit": {
                "status": "needs_review",
                "proposed_change": {},
                "detected_conflicts": [],
                "suggested_resolutions": []
            }
        }
        
        from orchestrator.session_state import SessionState
        state = SessionState()
        result = handler.handle(state, {"proposed_change": "Add a new city"})
        
        assert "world_edit" in result
        assert result["world_edit"]["status"] == "needs_review"
        mock_dm_brain.process_world_edit.assert_called_once()


class TestWorldArchitectModeHandler:
    """Tests for WorldArchitectModeHandler."""
    
    def test_process(self, db_session, mock_dm_brain, mock_retriever):
        """Test world architect mode processing."""
        handler = WorldArchitectModeHandler(db_session, mock_dm_brain, mock_retriever)
        
        # Mock DM brain
        mock_dm_brain.world_architect.return_value = {
            "universe": {"name": "Test World"},
            "campaigns": [],
            "locations": []
        }
        
        from orchestrator.session_state import SessionState
        state = SessionState()
        result = handler.handle(state, {"requirements": "Create a fantasy world"})
        
        assert "universe" in result or "world" in str(result).lower()
        mock_dm_brain.world_architect.assert_called_once()


class TestMainMenuModeHandler:
    """Tests for MainMenuModeHandler."""
    
    def test_process(self, db_session, mock_dm_brain, mock_retriever):
        """Test main menu mode processing."""
        handler = MainMenuModeHandler(db_session, mock_dm_brain, mock_retriever)
        
        from orchestrator.session_state import SessionState
        state = SessionState()
        result = handler.handle(state, {"input": "list universes"})
        
        # Main menu handler should return a response
        assert result is not None
        assert "message" in result or "response" in result or "narration" in result

