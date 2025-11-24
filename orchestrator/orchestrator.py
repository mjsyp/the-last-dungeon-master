"""Main orchestrator for managing modes and session flow."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from orchestrator.session_state import SessionState, Mode
from orchestrator.mode_handler import (
    ModeHandler,
    DMStoryModeHandler,
    RulesExplanationModeHandler,
    WorldEditModeHandler,
    WorldArchitectModeHandler,
    TutorialModeHandler,
    MainMenuModeHandler
)
from llm.dm_brain import DMBrain
from rag.retriever import RAGRetriever


class Orchestrator:
    """Main orchestrator for the DM-VA system."""
    
    def __init__(self, db: Session):
        """Initialize the orchestrator."""
        self.db = db
        self.state = SessionState()
        self.dm_brain = DMBrain()
        self.retriever = RAGRetriever()
        
        # Register mode handlers
        self.handlers: Dict[Mode, ModeHandler] = {
            Mode.MAIN_MENU: MainMenuModeHandler(db, self.dm_brain, self.retriever),
            Mode.WORLD_ARCHITECT: WorldArchitectModeHandler(db, self.dm_brain, self.retriever),
            Mode.DM_STORY: DMStoryModeHandler(db, self.dm_brain, self.retriever),
            Mode.RULES_EXPLANATION: RulesExplanationModeHandler(db, self.dm_brain, self.retriever),
            Mode.TUTORIAL: TutorialModeHandler(db, self.dm_brain, self.retriever),
            Mode.WORLD_EDIT: WorldEditModeHandler(db, self.dm_brain, self.retriever),
        }
    
    def switch_mode(self, new_mode: Mode):
        """Switch to a new mode."""
        self.state.current_mode = new_mode
        
        # Reset mode-specific state
        if new_mode != Mode.TUTORIAL:
            self.state.tutorial_script_id = None
            self.state.tutorial_step = 0
        
        if new_mode != Mode.WORLD_EDIT:
            self.state.pending_world_change_request_id = None
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input in the current mode.
        
        Args:
            input_data: Input data (mode-specific)
        
        Returns:
            Output data (mode-specific)
        """
        handler = self.handlers.get(self.state.current_mode)
        if not handler:
            return {"error": f"No handler for mode: {self.state.current_mode}"}
        
        return handler.handle(self.state, input_data)
    
    def get_state(self) -> SessionState:
        """Get current session state."""
        return self.state
    
    def set_active_universe(self, universe_id: str):
        """Set the active universe."""
        from uuid import UUID
        self.state.active_universe_id = UUID(universe_id)
    
    def set_active_campaign(self, campaign_id: str):
        """Set the active campaign."""
        from uuid import UUID
        self.state.active_campaign_id = UUID(campaign_id)
    
    def set_active_party(self, party_id: str):
        """Set the active party."""
        from uuid import UUID
        self.state.active_party_id = UUID(party_id)

