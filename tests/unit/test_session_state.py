"""Unit tests for session state management."""
import pytest
from orchestrator.session_state import SessionState, Mode
from uuid import uuid4


class TestMode:
    """Tests for Mode enum."""
    
    def test_all_modes_exist(self):
        """Test that all expected modes exist."""
        assert Mode.MAIN_MENU.value == "main_menu_mode"
        assert Mode.WORLD_ARCHITECT.value == "world_architect_mode"
        assert Mode.DM_STORY.value == "dm_story_mode"
        assert Mode.RULES_EXPLANATION.value == "rules_explanation_mode"
        assert Mode.TUTORIAL.value == "tutorial_mode"
        assert Mode.WORLD_EDIT.value == "world_edit_mode"
    
    def test_mode_from_value(self):
        """Test creating Mode from string value."""
        mode = Mode("main_menu_mode")
        assert mode == Mode.MAIN_MENU


class TestSessionState:
    """Tests for SessionState dataclass."""
    
    def test_default_initialization(self):
        """Test default SessionState initialization."""
        state = SessionState()
        
        assert state.active_universe_id is None
        assert state.active_campaign_id is None
        assert state.active_party_id is None
        assert state.current_mode == Mode.MAIN_MENU
        assert state.turn_index == 0
        assert state.recent_history == []
        assert state.metadata == {}
    
    def test_custom_initialization(self):
        """Test SessionState with custom values."""
        universe_id = uuid4()
        campaign_id = uuid4()
        
        state = SessionState(
            active_universe_id=universe_id,
            active_campaign_id=campaign_id,
            current_mode=Mode.DM_STORY,
            turn_index=5
        )
        
        assert state.active_universe_id == universe_id
        assert state.active_campaign_id == campaign_id
        assert state.current_mode == Mode.DM_STORY
        assert state.turn_index == 5
    
    def test_reset(self):
        """Test resetting session state."""
        state = SessionState(
            active_universe_id=uuid4(),
            current_mode=Mode.DM_STORY,
            turn_index=10,
            recent_history=["entry1", "entry2"]
        )
        
        state.reset()
        
        assert state.active_universe_id is None
        assert state.current_mode == Mode.MAIN_MENU
        assert state.turn_index == 0
        assert state.recent_history == []
    
    def test_add_to_history(self):
        """Test adding entries to history."""
        state = SessionState()
        
        state.add_to_history("Entry 1")
        assert len(state.recent_history) == 1
        assert state.recent_history[0] == "Entry 1"
        
        state.add_to_history("Entry 2")
        assert len(state.recent_history) == 2
    
    def test_history_max_size(self):
        """Test that history maintains max size."""
        state = SessionState()
        
        # Add more than max_history entries
        for i in range(15):
            state.add_to_history(f"Entry {i}", max_history=10)
        
        assert len(state.recent_history) == 10
        # Should keep the most recent entries
        assert state.recent_history[0] == "Entry 5"
        assert state.recent_history[-1] == "Entry 14"
    
    def test_format_recent_history_empty(self):
        """Test formatting empty history."""
        state = SessionState()
        formatted = state.format_recent_history()
        
        assert formatted == "No recent history."
    
    def test_format_recent_history(self):
        """Test formatting history with entries."""
        state = SessionState()
        state.add_to_history("First entry")
        state.add_to_history("Second entry")
        state.add_to_history("Third entry")
        
        formatted = state.format_recent_history()
        
        assert "[1] First entry" in formatted
        assert "[2] Second entry" in formatted
        assert "[3] Third entry" in formatted
        assert formatted.count("\n") == 2  # 3 entries = 2 newlines

