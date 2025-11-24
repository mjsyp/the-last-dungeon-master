"""Base class and implementations for mode handlers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from orchestrator.session_state import SessionState, Mode
from llm.dm_brain import DMBrain
from rag.retriever import RAGRetriever


class ModeHandler(ABC):
    """Abstract base class for mode handlers."""
    
    def __init__(self, db: Session, dm_brain: DMBrain, retriever: RAGRetriever):
        self.db = db
        self.dm_brain = dm_brain
        self.retriever = retriever
    
    @abstractmethod
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle input in this mode.
        
        Args:
            state: Current session state
            input_data: Input data (e.g., {"player_utterance": "..."})
        
        Returns:
            Output data (mode-specific)
        """
        pass


class DMStoryModeHandler(ModeHandler):
    """Handler for DM Story Mode (live session play)."""
    
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a turn in DM Story Mode."""
        player_utterance = input_data.get("player_utterance", "")
        
        if not player_utterance:
            return {
                "narration": "I'm listening...",
                "log_updates": {}
            }
        
        # Retrieve relevant lore context
        universe_id = str(state.active_universe_id) if state.active_universe_id else None
        campaign_id = str(state.active_campaign_id) if state.active_campaign_id else None
        
        lore_chunks = self.retriever.retrieve_lore_context(
            query=player_utterance,
            universe_id=universe_id,
            campaign_id=campaign_id,
            limit=10
        )
        lore_context = self.retriever.format_lore_context(lore_chunks)
        
        # Get recent history
        recent_history = state.format_recent_history()
        
        # Get current location info (if available)
        current_location = None
        if state.current_location_id:
            # TODO: Fetch location details from DB
            current_location = f"Location ID: {state.current_location_id}"
        
        # Get active characters
        active_characters = [str(cid) for cid in state.active_character_ids]
        
        # Call DM Brain
        result = self.dm_brain.dm_story_turn(
            lore_context=lore_context,
            recent_history=recent_history,
            player_utterance=player_utterance,
            current_location=current_location,
            active_characters=active_characters if active_characters else None
        )
        
        # Update state
        state.turn_index += 1
        state.add_to_history(f"Player: {player_utterance}")
        state.add_to_history(f"DM: {result.get('narration', '')}")
        
        # TODO: Apply log_updates to database
        # This would involve:
        # - Creating Event records
        # - Updating Character records
        # - Updating Location records
        # - Re-indexing changed entities in RAG
        
        return result


class RulesExplanationModeHandler(ModeHandler):
    """Handler for Rules Explanation Mode."""
    
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a rules question."""
        user_question = input_data.get("question", "")
        
        if not user_question:
            return {
                "explanation": "What would you like to know about the rules?",
                "examples": {},
                "related_topics": []
            }
        
        # Retrieve relevant rules context
        # TODO: Get rule_system_id from campaign/universe
        rules_chunks = self.retriever.retrieve_rules_context(
            query=user_question,
            limit=5
        )
        rules_context = self.retriever.format_rules_context(rules_chunks)
        
        # Call DM Brain
        result = self.dm_brain.explain_rules(
            rules_context=rules_context,
            user_question=user_question
        )
        
        return result


class WorldEditModeHandler(ModeHandler):
    """Handler for World Edit Mode."""
    
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a world edit request."""
        proposed_change = input_data.get("proposed_change", "")
        player_id = input_data.get("player_id", "unknown")
        
        if not proposed_change:
            return {
                "narration": "What change would you like to make to the world?",
                "world_edit": {
                    "status": "needs_discussion",
                    "proposed_change": {},
                    "detected_conflicts": [],
                    "suggested_resolutions": []
                }
            }
        
        # Retrieve relevant lore context for conflict checking
        universe_id = str(state.active_universe_id) if state.active_universe_id else None
        campaign_id = str(state.active_campaign_id) if state.active_campaign_id else None
        
        lore_chunks = self.retriever.retrieve_lore_context(
            query=proposed_change,
            universe_id=universe_id,
            campaign_id=campaign_id,
            limit=15  # More context for conflict checking
        )
        lore_context = self.retriever.format_lore_context(lore_chunks)
        
        # Call DM Brain
        result = self.dm_brain.process_world_edit(
            proposed_change=proposed_change,
            lore_context=lore_context
        )
        
        # TODO: Create/update WorldChangeRequest record in DB
        
        return result


class WorldArchitectModeHandler(ModeHandler):
    """Handler for World Architect Mode."""
    
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle world generation/creation."""
        user_requirements = input_data.get("requirements", "")
        
        if not user_requirements:
            return {
                "error": "Please provide requirements for world generation."
            }
        
        # Get existing universe context if available
        existing_context = None
        if state.active_universe_id:
            # TODO: Fetch and format existing universe context
            existing_context = f"Universe ID: {state.active_universe_id}"
        
        # Call DM Brain
        result = self.dm_brain.world_architect(
            user_requirements=user_requirements,
            existing_universe_context=existing_context
        )
        
        # TODO: Save generated world elements to database
        # This would involve creating Universe, Campaign, Location, Character, Faction, Event records
        # and indexing them in RAG
        
        return result


class TutorialModeHandler(ModeHandler):
    """Handler for Tutorial Mode."""
    
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tutorial step."""
        player_response = input_data.get("player_response")
        
        # TODO: Fetch tutorial script from DB
        tutorial_script = {
            "name": "Basic Tutorial",
            "steps": [
                {"prompt_to_user": "Welcome! Let's start with the basics.", "narration": "Welcome to the tutorial!"}
            ]
        }
        
        result = self.dm_brain.tutorial_step(
            tutorial_script=tutorial_script,
            current_step=state.tutorial_step,
            player_response=player_response
        )
        
        # Update tutorial state
        tutorial_state = result.get("tutorial_state", {})
        if tutorial_state.get("next_action") == "proceed_to_next":
            state.tutorial_step += 1
        
        return result


class MainMenuModeHandler(ModeHandler):
    """Handler for Main Menu Mode."""
    
    def handle(self, state: SessionState, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle main menu operations."""
        action = input_data.get("action", "list")
        
        # Main menu operations are handled by the main_menu module
        # This handler is a placeholder
        return {
            "message": "Main menu operations should be handled by main_menu module",
            "action": action
        }

