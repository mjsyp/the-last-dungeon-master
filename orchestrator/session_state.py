"""Session state management."""
from typing import Optional, Dict, Any
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum


class Mode(Enum):
    """Available modes of operation."""
    MAIN_MENU = "main_menu_mode"
    WORLD_ARCHITECT = "world_architect_mode"
    DM_STORY = "dm_story_mode"
    RULES_EXPLANATION = "rules_explanation_mode"
    TUTORIAL = "tutorial_mode"
    WORLD_EDIT = "world_edit_mode"


@dataclass
class SessionState:
    """Current session state."""
    # Active context
    active_universe_id: Optional[UUID] = None
    active_campaign_id: Optional[UUID] = None
    active_party_id: Optional[UUID] = None
    active_session_id: Optional[UUID] = None
    
    # Current mode
    current_mode: Mode = Mode.MAIN_MENU
    
    # Session-specific state
    turn_index: int = 0
    recent_history: list[str] = field(default_factory=list)  # Recent dialogue/events
    current_location_id: Optional[UUID] = None
    active_character_ids: list[UUID] = field(default_factory=list)
    
    # Tutorial state (if in tutorial mode)
    tutorial_script_id: Optional[UUID] = None
    tutorial_step: int = 0
    
    # World edit state (if in world edit mode)
    pending_world_change_request_id: Optional[UUID] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def reset(self):
        """Reset session state to defaults."""
        self.active_universe_id = None
        self.active_campaign_id = None
        self.active_party_id = None
        self.active_session_id = None
        self.current_mode = Mode.MAIN_MENU
        self.turn_index = 0
        self.recent_history = []
        self.current_location_id = None
        self.active_character_ids = []
        self.tutorial_script_id = None
        self.tutorial_step = 0
        self.pending_world_change_request_id = None
        self.metadata = {}
    
    def add_to_history(self, entry: str, max_history: int = 10):
        """Add an entry to recent history, maintaining max size."""
        self.recent_history.append(entry)
        if len(self.recent_history) > max_history:
            self.recent_history.pop(0)
    
    def format_recent_history(self) -> str:
        """Format recent history for LLM context."""
        if not self.recent_history:
            return "No recent history."
        return "\n".join(f"[{i+1}] {entry}" for i, entry in enumerate(self.recent_history))

