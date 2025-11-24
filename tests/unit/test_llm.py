"""Unit tests for LLM integration."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from llm.client import LLMClient
from llm.dm_brain import DMBrain
from llm.prompts import PromptTemplates
import json


class TestLLMClient:
    """Tests for LLMClient."""
    
    @patch('llm.client.openai.OpenAI')
    def test_generate(self, mock_openai_class):
        """Test text generation."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        client = LLMClient(provider="openai")
        result = client.generate(
            system_prompt="You are a helpful assistant",
            user_prompt="Say hello"
        )
        
        assert result == "Generated text"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('llm.client.openai.OpenAI')
    def test_generate_with_response_format(self, mock_openai_class):
        """Test generation with JSON response format."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"key": "value"}'))]
        mock_client.chat.completions.create.return_value = mock_response
        
        client = LLMClient(provider="openai")
        result = client.generate(
            system_prompt="System",
            user_prompt="User",
            response_format={"type": "json_object"}
        )
        
        assert result == '{"key": "value"}'
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}


class TestDMBrain:
    """Tests for DMBrain."""
    
    @patch('llm.dm_brain.LLMClient')
    def test_dm_story_turn(self, mock_client_class):
        """Test DM story turn processing."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        response_data = {
            "narration": "You see a goblin",
            "log_updates": {"location": "cave"}
        }
        mock_client.generate.return_value = json.dumps(response_data)
        
        brain = DMBrain()
        result = brain.dm_story_turn(
            lore_context="Context",
            recent_history="History",
            player_utterance="I attack"
        )
        
        assert result["narration"] == "You see a goblin"
        assert result["log_updates"] == {"location": "cave"}
    
    @patch('llm.dm_brain.LLMClient')
    def test_dm_story_turn_invalid_json(self, mock_client_class):
        """Test handling of invalid JSON response."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Return non-JSON response
        mock_client.generate.return_value = "Just plain text"
        
        brain = DMBrain()
        result = brain.dm_story_turn(
            lore_context="Context",
            recent_history="History",
            player_utterance="I attack"
        )
        
        # Should fall back to plain text narration
        assert result["narration"] == "Just plain text"
        assert result["log_updates"] == {}
    
    @patch('llm.dm_brain.LLMClient')
    def test_world_architect(self, mock_client_class):
        """Test world architect generation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        response_data = {
            "universe": {"name": "Test World"},
            "campaigns": [],
            "locations": []
        }
        mock_client.generate.return_value = json.dumps(response_data)
        
        brain = DMBrain()
        result = brain.world_architect("Create a fantasy world")
        
        assert "universe" in result
        assert result["universe"]["name"] == "Test World"
    
    @patch('llm.dm_brain.LLMClient')
    def test_explain_rules(self, mock_client_class):
        """Test rules explanation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        response_data = {
            "explanation": "Combat works like this...",
            "examples": {"example1": "text"},
            "related_topics": ["topic1"]
        }
        mock_client.generate.return_value = json.dumps(response_data)
        
        brain = DMBrain()
        result = brain.explain_rules("Rules context", "How does combat work?")
        
        assert "explanation" in result
        assert "examples" in result
        assert "related_topics" in result


class TestPromptTemplates:
    """Tests for PromptTemplates."""
    
    def test_dm_story_mode_template(self):
        """Test DM story mode prompt template."""
        templates = PromptTemplates()
        system, user = templates.dm_story_mode(
            lore_context="Lore",
            recent_history="History",
            player_utterance="I attack"
        )
        
        assert "lore" in system.lower() or "context" in system.lower()
        assert "I attack" in user
        assert "History" in user or "recent" in user.lower()
    
    def test_world_architect_mode_template(self):
        """Test world architect mode prompt template."""
        templates = PromptTemplates()
        system, user = templates.world_architect_mode(
            user_requirements="Create a dark fantasy world"
        )
        
        assert "world" in system.lower() or "universe" in system.lower()
        assert "dark fantasy" in user.lower()
    
    def test_rules_explanation_mode_template(self):
        """Test rules explanation mode prompt template."""
        templates = PromptTemplates()
        system, user = templates.rules_explanation_mode(
            rules_context="Rules",
            user_question="How does combat work?"
        )
        
        assert "rules" in system.lower() or "explain" in system.lower()
        assert "combat" in user.lower()

