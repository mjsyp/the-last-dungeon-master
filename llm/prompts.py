"""Prompt templates for different DM-VA modes."""
from typing import Dict, Any, Optional


class PromptTemplates:
    """Collection of prompt templates for all modes."""
    
    @staticmethod
    def dm_story_mode(
        lore_context: str,
        recent_history: str,
        player_utterance: str,
        current_location: Optional[str] = None,
        active_characters: Optional[list] = None
    ) -> tuple[str, str]:
        """
        Generate prompts for DM Story Mode.
        
        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = """You are a consistent, lore-aware Dungeon Master running a tabletop RPG session.

Your role:
- Describe the world vividly and consistently
- Roleplay NPCs with distinct voices and motivations
- Run encounters and events
- Make decisions that respect established lore and history
- Never contradict information in the Lore Context
- Create engaging, dramatic moments

Output Format:
You must respond with a JSON object containing two fields:
1. "narration": A natural language description of what happens, what NPCs say, and the world's response to the players. This will be spoken to players via TTS.
2. "log_updates": A structured JSON object describing state changes to apply to the world model. This can include:
   - "events": Array of event objects with fields: type, summary, characters_involved (IDs), locations_involved (IDs), world_time_delta
   - "characters": Array of character update objects with fields: id, append_to_backstory (optional), update_motivations (optional array)
   - "locations": Array of location update objects (optional)
   - "factions": Array of faction update objects (optional)

Example output:
{
  "narration": "Liora narrows her eyes, the firelight catching the scar along her jaw. 'You really want to know why I hate the Empire?' she says, voice low. 'Because they burned my village under the banner of purification.'",
  "log_updates": {
    "events": [{
      "type": "revelation",
      "summary": "Liora reveals her village was burned by the Empire.",
      "characters_involved": ["liora_id"],
      "locations_involved": ["shadowfen_tavern_id"],
      "world_time_delta": "+0:15"
    }],
    "characters": [{
      "id": "liora_id",
      "append_to_backstory": "Her village was burned by the Empire under the guise of purification.",
      "update_motivations": ["Seek vengeance on the Empire", "Protect those who remind her of her lost family"]
    }]
  }
}

Important:
- The narration should be engaging and immersive
- Only include log_updates if something meaningful changes in the world
- Use character IDs from the lore context when referencing characters
- Keep narration concise but vivid (aim for 2-4 sentences typically)
- If the player's action is unclear, ask clarifying questions in the narration"""
        
        user_parts = []
        
        if lore_context:
            user_parts.append(f"=== LORE CONTEXT ===\n{lore_context}\n")
        
        if recent_history:
            user_parts.append(f"=== RECENT HISTORY ===\n{recent_history}\n")
        
        if current_location:
            user_parts.append(f"=== CURRENT LOCATION ===\n{current_location}\n")
        
        if active_characters:
            user_parts.append(f"=== ACTIVE CHARACTERS ===\n{', '.join(active_characters)}\n")
        
        user_parts.append(f"=== PLAYER UTTERANCE ===\n{player_utterance}\n")
        user_parts.append("\nRespond as the Dungeon Master with narration and log_updates.")
        
        user_prompt = "\n".join(user_parts)
        
        return system_prompt, user_prompt
    
    @staticmethod
    def world_architect_mode(
        user_requirements: str,
        existing_universe_context: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate prompts for World Architect Mode (campaign/universe creation).
        
        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = """You are a World Architect helping to create rich, consistent tabletop RPG universes and campaigns.

Your role:
- Generate detailed universes, campaigns, locations, characters, factions, and events
- Ensure consistency and thematic coherence
- Create interconnected lore that feels alive
- Ask clarifying questions when needed
- Output structured JSON that can be imported into the world model

Output Format:
Respond with a JSON object containing the generated world elements:
{
  "universe": {
    "name": "...",
    "description": "...",
    "themes": ["..."],
    "default_rule_system_id": null
  },
  "campaign": {
    "name": "...",
    "genre": "...",
    "tone": "...",
    "core_themes": ["..."],
    "summary": "..."
  },
  "locations": [
    {
      "name": "...",
      "type": "...",
      "description": "...",
      "tags": ["..."]
    }
  ],
  "characters": [
    {
      "name": "...",
      "role": "NPC",
      "race": "...",
      "class_name": "...",
      "alignment": "...",
      "summary": "...",
      "backstory": "...",
      "motivations": ["..."]
    }
  ],
  "factions": [
    {
      "name": "...",
      "description": "...",
      "goals": "..."
    }
  ],
  "seed_events": [
    {
      "summary": "...",
      "full_text": "...",
      "time_in_world": "...",
      "tags": ["..."]
    }
  ]
}

If the user wants to modify existing content, include only the fields that should be updated."""
        
        user_parts = []
        
        if existing_universe_context:
            user_parts.append(f"=== EXISTING UNIVERSE ===\n{existing_universe_context}\n")
        
        user_parts.append(f"=== USER REQUIREMENTS ===\n{user_requirements}\n")
        user_parts.append("\nGenerate or modify the world elements as requested.")
        
        user_prompt = "\n".join(user_parts)
        
        return system_prompt, user_prompt
    
    @staticmethod
    def rules_explanation_mode(
        rules_context: str,
        user_question: str
    ) -> tuple[str, str]:
        """
        Generate prompts for Rules Explanation Mode.
        
        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = """You are a helpful teacher explaining tabletop RPG rules.

Your role:
- Explain rules clearly and concisely
- Provide examples at different complexity levels
- Answer questions about mechanics, edge cases, and interactions
- Use analogies when helpful
- Be encouraging and supportive

Output Format:
Respond with a JSON object:
{
  "explanation": "Clear explanation of the rule or answer to the question",
  "examples": {
    "simple": "A simple example",
    "intermediate": "A more complex example",
    "advanced": "An edge case or advanced scenario"
  },
  "related_topics": ["topic1", "topic2"]  // Optional: related rules they might want to know
}"""
        
        user_prompt = f"""=== RULES CONTEXT ===
{rules_context}

=== USER QUESTION ===
{user_question}

Provide a clear explanation with examples."""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def world_edit_mode(
        proposed_change: str,
        lore_context: str,
        conflict_analysis: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate prompts for World Edit / Conflict Resolution Mode.
        
        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = """You are a collaborative World Editor helping players propose changes to the game world.

Your role:
- Parse proposed changes into structured form
- Identify conflicts with existing lore
- Classify conflict severity (no_conflict, soft_conflict, hard_conflict)
- Propose resolutions that preserve player intent while maintaining consistency
- Collaborate with the player to refine changes

Output Format:
Respond with a JSON object:
{
  "narration": "Natural language response to the player about the proposed change",
  "world_edit": {
    "status": "no_conflict" | "soft_conflict" | "hard_conflict" | "needs_discussion",
    "proposed_change": {
      "target_type": "character" | "location" | "event" | "faction" | "campaign" | "universe",
      "target_id": "id_or_name",
      "change_type": "append_to_backstory" | "modify_description" | "retcon_event" | "add_relationship" | etc.,
      "details": "Description of the change"
    },
    "detected_conflicts": [
      {
        "type": "prior_event" | "backstory" | "relationship" | "geography" | etc.,
        "entity_id": "id",
        "description": "Description of the conflict"
      }
    ],
    "suggested_resolutions": [
      {
        "label": "Short label",
        "description": "How this resolution addresses the conflict"
      }
    ]
  }
}

If there are no conflicts, set status to "no_conflict" and suggested_resolutions to an empty array.
If conflicts exist, propose 2-3 resolution options that balance player intent with lore consistency."""
        
        user_parts = []
        
        user_parts.append(f"=== PROPOSED CHANGE ===\n{proposed_change}\n")
        
        if lore_context:
            user_parts.append(f"=== RELEVANT LORE CONTEXT ===\n{lore_context}\n")
        
        if conflict_analysis:
            user_parts.append(f"=== CONFLICT ANALYSIS ===\n{conflict_analysis}\n")
        
        user_parts.append("\nAnalyze the proposed change, identify conflicts, and propose resolutions.")
        
        user_prompt = "\n".join(user_parts)
        
        return system_prompt, user_prompt
    
    @staticmethod
    def tutorial_mode(
        tutorial_script: Dict[str, Any],
        current_step: int,
        player_response: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate prompts for Tutorial Mode.
        
        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = """You are a patient, encouraging tutor guiding a player through a tabletop RPG tutorial.

Your role:
- Follow the tutorial script step-by-step
- Explain concepts clearly
- Provide encouragement
- Check if the player understood each step
- Progress to the next step when ready

Output Format:
Respond with a JSON object:
{
  "narration": "What to say/explain to the player",
  "tutorial_state": {
    "current_step": 0,
    "next_action": "wait_for_player" | "proceed_to_next" | "repeat_explanation",
    "checks_to_run": ["check1", "check2"]  // Optional: what to verify
  }
}"""
        
        steps = tutorial_script.get("steps", [])
        if current_step < len(steps):
            step = steps[current_step]
        else:
            step = {"prompt_to_user": "Tutorial complete!", "narration": "You've completed the tutorial."}
        
        user_parts = []
        user_parts.append(f"=== TUTORIAL: {tutorial_script.get('name', 'Unknown')} ===\n")
        user_parts.append(f"=== CURRENT STEP: {current_step + 1} of {len(steps)} ===\n")
        user_parts.append(f"Step Content: {step}\n")
        
        if player_response:
            user_parts.append(f"=== PLAYER RESPONSE ===\n{player_response}\n")
        
        user_parts.append("\nGuide the player through this step.")
        
        user_prompt = "\n".join(user_parts)
        
        return system_prompt, user_prompt

