"""Session state persistence manager."""
from typing import Optional
from sqlalchemy.orm import Session
from models.user_session import UserSession
from orchestrator.session_state import SessionState, Mode
import json
from datetime import datetime, timezone


class SessionManager:
    """Manages persistent session state."""
    
    DEFAULT_SESSION_ID = "default_session"
    
    def __init__(self, db: Session, session_id: str = DEFAULT_SESSION_ID):
        self.db = db
        self.session_id = session_id
    
    def load_state(self) -> SessionState:
        """Load session state from database."""
        user_session = self.db.query(UserSession).filter(
            UserSession.session_id == self.session_id
        ).first()
        
        if user_session and user_session.state_json:
            return self._deserialize_state(user_session.state_json)
        else:
            # Return default state
            return SessionState()
    
    def save_state(self, state: SessionState):
        """Save session state to database."""
        state_json = self._serialize_state(state)
        
        user_session = self.db.query(UserSession).filter(
            UserSession.session_id == self.session_id
        ).first()
        
        if user_session:
            user_session.state_json = state_json
            user_session.last_activity = datetime.now(timezone.utc)
        else:
            user_session = UserSession(
                session_id=self.session_id,
                state_json=state_json
            )
            self.db.add(user_session)
        
        self.db.commit()
    
    def _serialize_state(self, state: SessionState) -> dict:
        """Serialize SessionState to JSON-serializable dict."""
        return {
            "current_mode": state.current_mode.value if state.current_mode else None,
            "active_universe_id": str(state.active_universe_id) if state.active_universe_id else None,
            "active_campaign_id": str(state.active_campaign_id) if state.active_campaign_id else None,
            "active_party_id": str(state.active_party_id) if state.active_party_id else None,
            "active_session_id": str(state.active_session_id) if state.active_session_id else None,
            "turn_index": state.turn_index,
            "recent_history": state.recent_history,
            "current_location_id": str(state.current_location_id) if state.current_location_id else None,
            "active_character_ids": [str(cid) for cid in state.active_character_ids],
            "tutorial_script_id": str(state.tutorial_script_id) if state.tutorial_script_id else None,
            "tutorial_step": state.tutorial_step,
            "pending_world_change_request_id": str(state.pending_world_change_request_id) if state.pending_world_change_request_id else None,
            "metadata": state.metadata
        }
    
    def _deserialize_state(self, state_dict: dict) -> SessionState:
        """Deserialize dict to SessionState."""
        state = SessionState()
        
        if state_dict.get("current_mode"):
            try:
                state.current_mode = Mode(state_dict["current_mode"])
            except ValueError:
                state.current_mode = Mode.MAIN_MENU
        
        if state_dict.get("active_universe_id"):
            from uuid import UUID
            try:
                state.active_universe_id = UUID(state_dict["active_universe_id"])
            except (ValueError, TypeError):
                pass
        
        if state_dict.get("active_campaign_id"):
            from uuid import UUID
            try:
                state.active_campaign_id = UUID(state_dict["active_campaign_id"])
            except (ValueError, TypeError):
                pass
        
        if state_dict.get("active_party_id"):
            from uuid import UUID
            try:
                state.active_party_id = UUID(state_dict["active_party_id"])
            except (ValueError, TypeError):
                pass
        
        if state_dict.get("active_session_id"):
            from uuid import UUID
            try:
                state.active_session_id = UUID(state_dict["active_session_id"])
            except (ValueError, TypeError):
                pass
        
        state.turn_index = state_dict.get("turn_index", 0)
        state.recent_history = state_dict.get("recent_history", [])
        
        if state_dict.get("current_location_id"):
            from uuid import UUID
            try:
                state.current_location_id = UUID(state_dict["current_location_id"])
            except (ValueError, TypeError):
                pass
        
        if state_dict.get("active_character_ids"):
            from uuid import UUID
            try:
                state.active_character_ids = [UUID(cid) for cid in state_dict["active_character_ids"]]
            except (ValueError, TypeError):
                state.active_character_ids = []
        
        if state_dict.get("tutorial_script_id"):
            from uuid import UUID
            try:
                state.tutorial_script_id = UUID(state_dict["tutorial_script_id"])
            except (ValueError, TypeError):
                pass
        
        state.tutorial_step = state_dict.get("tutorial_step", 0)
        
        if state_dict.get("pending_world_change_request_id"):
            from uuid import UUID
            try:
                state.pending_world_change_request_id = UUID(state_dict["pending_world_change_request_id"])
            except (ValueError, TypeError):
                pass
        
        state.metadata = state_dict.get("metadata", {})
        
        return state

