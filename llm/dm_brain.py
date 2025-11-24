"""DM Brain: High-level interface for LLM interactions in different modes."""
from typing import Dict, Any, Optional, List
import json
from llm.client import LLMClient
from llm.prompts import PromptTemplates


class DMBrain:
    """Main interface for LLM interactions across all modes."""
    
    def __init__(self, provider: str = "openai"):
        """Initialize the DM Brain."""
        self.client = LLMClient(provider=provider)
        self.templates = PromptTemplates()
    
    def dm_story_turn(
        self,
        lore_context: str,
        recent_history: str,
        player_utterance: str,
        current_location: Optional[str] = None,
        active_characters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a turn in DM Story Mode.
        
        Returns:
            {
                "narration": str,
                "log_updates": Dict[str, Any]
            }
        """
        system_prompt, user_prompt = self.templates.dm_story_mode(
            lore_context=lore_context,
            recent_history=recent_history,
            player_utterance=player_utterance,
            current_location=current_location,
            active_characters=active_characters
        )
        
        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            # This is a safety net for cases where LLM doesn't follow format exactly
            return {
                "narration": response,
                "log_updates": {}
            }
    
    def world_architect(
        self,
        user_requirements: str,
        existing_universe_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate world elements in World Architect Mode.
        
        Returns:
            Dict with universe, campaign, locations, characters, factions, seed_events
        """
        system_prompt, user_prompt = self.templates.world_architect_mode(
            user_requirements=user_requirements,
            existing_universe_context=existing_universe_context
        )
        
        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.9,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse world generation response"}
    
    def explain_rules(
        self,
        rules_context: str,
        user_question: str
    ) -> Dict[str, Any]:
        """
        Explain rules in Rules Explanation Mode.
        
        Returns:
            {
                "explanation": str,
                "examples": Dict[str, str],
                "related_topics": List[str]
            }
        """
        system_prompt, user_prompt = self.templates.rules_explanation_mode(
            rules_context=rules_context,
            user_question=user_question
        )
        
        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "explanation": response,
                "examples": {},
                "related_topics": []
            }
    
    def process_world_edit(
        self,
        proposed_change: str,
        lore_context: str,
        conflict_analysis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a world edit request in World Edit Mode.
        
        Returns:
            {
                "narration": str,
                "world_edit": {
                    "status": str,
                    "proposed_change": Dict,
                    "detected_conflicts": List[Dict],
                    "suggested_resolutions": List[Dict]
                }
            }
        """
        system_prompt, user_prompt = self.templates.world_edit_mode(
            proposed_change=proposed_change,
            lore_context=lore_context,
            conflict_analysis=conflict_analysis
        )
        
        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "narration": response,
                "world_edit": {
                    "status": "needs_discussion",
                    "proposed_change": {},
                    "detected_conflicts": [],
                    "suggested_resolutions": []
                }
            }
    
    def tutorial_step(
        self,
        tutorial_script: Dict[str, Any],
        current_step: int,
        player_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a step in Tutorial Mode.
        
        Returns:
            {
                "narration": str,
                "tutorial_state": Dict
            }
        """
        system_prompt, user_prompt = self.templates.tutorial_mode(
            tutorial_script=tutorial_script,
            current_step=current_step,
            player_response=player_response
        )
        
        response = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "narration": response,
                "tutorial_state": {
                    "current_step": current_step,
                    "next_action": "wait_for_player",
                    "checks_to_run": []
                }
            }

