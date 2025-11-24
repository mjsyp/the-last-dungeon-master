"""Unit tests for orchestrator."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base
from orchestrator.orchestrator import Orchestrator
from orchestrator.session_state import Mode
from unittest.mock import Mock, patch, MagicMock


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


class TestOrchestrator:
    """Tests for Orchestrator."""
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_initialization(self, mock_retriever_class, mock_brain_class, db_session):
        """Test orchestrator initialization."""
        mock_brain = Mock()
        mock_retriever = Mock()
        mock_brain_class.return_value = mock_brain
        mock_retriever_class.return_value = mock_retriever
        
        orchestrator = Orchestrator(db_session)
        
        assert orchestrator.db == db_session
        assert orchestrator.state is not None
        assert orchestrator.state.current_mode == Mode.MAIN_MENU
        assert len(orchestrator.handlers) == 6  # All 6 mode handlers
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_switch_mode(self, mock_retriever_class, mock_brain_class, db_session):
        """Test switching modes."""
        mock_brain = Mock()
        mock_retriever = Mock()
        mock_brain_class.return_value = mock_brain
        mock_retriever_class.return_value = mock_retriever
        
        orchestrator = Orchestrator(db_session)
        orchestrator.switch_mode(Mode.DM_STORY)
        
        assert orchestrator.state.current_mode == Mode.DM_STORY
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_process_input_routes_to_handler(self, mock_retriever_class, mock_brain_class, db_session):
        """Test that process_input routes to correct handler."""
        mock_brain = Mock()
        mock_retriever = Mock()
        mock_brain_class.return_value = mock_brain
        mock_retriever_class.return_value = mock_retriever
        
        orchestrator = Orchestrator(db_session)
        orchestrator.switch_mode(Mode.DM_STORY)
        
        # Get the handler (it's a real handler, not a mock)
        handler = orchestrator.handlers[Mode.DM_STORY]
        
        # Mock the handler's handle method
        original_handle = handler.handle
        handler.handle = Mock(return_value={
            "narration": "Test response",
            "log_updates": {}
        })
        
        result = orchestrator.process_input({"player_utterance": "test input"})
        
        assert result is not None
        assert "narration" in result
        handler.handle.assert_called_once()
        
        # Restore original handle
        handler.handle = original_handle
    
    @patch('orchestrator.orchestrator.DMBrain')
    @patch('orchestrator.orchestrator.RAGRetriever')
    def test_state_persistence(self, mock_retriever_class, mock_brain_class, db_session):
        """Test that state changes are persisted."""
        mock_brain = Mock()
        mock_retriever = Mock()
        mock_brain_class.return_value = mock_brain
        mock_retriever_class.return_value = mock_retriever
        
        orchestrator = Orchestrator(db_session, "test_session")
        orchestrator.state.turn_index = 5
        orchestrator.switch_mode(Mode.DM_STORY)
        
        # Create new orchestrator with same session ID
        orchestrator2 = Orchestrator(db_session, "test_session")
        
        # State should be persisted
        assert orchestrator2.state.current_mode == Mode.DM_STORY
        assert orchestrator2.state.turn_index == 5

