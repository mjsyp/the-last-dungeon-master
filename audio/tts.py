"""Text-to-Speech (TTS) interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import openai
from config.settings import settings


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    def synthesize(self, text: str, voice: Optional[str] = None, **kwargs) -> bytes:
        """
        Synthesize text to speech audio.
        
        Args:
            text: Text to synthesize
            voice: Optional voice identifier
            **kwargs: Additional voice parameters (speed, pitch, etc.)
        
        Returns:
            Audio data as bytes
        """
        pass


class OpenAITTS(TTSProvider):
    """OpenAI TTS API implementation."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.default_voice = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
    
    def synthesize(self, text: str, voice: Optional[str] = None, **kwargs) -> bytes:
        """
        Synthesize text using OpenAI TTS API.
        
        Args:
            text: Text to synthesize
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            **kwargs: Additional parameters (model, speed, etc.)
        """
        voice = voice or self.default_voice
        model = kwargs.get("model", "tts-1")  # tts-1 or tts-1-hd
        speed = kwargs.get("speed", 1.0)
        
        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed
        )
        
        # Return audio bytes
        return response.content


class MultiVoiceTTS:
    """Wrapper for multi-voice TTS (different voices for different NPCs)."""
    
    def __init__(self, base_provider: TTSProvider):
        self.base_provider = base_provider
        self.voice_map: Dict[str, str] = {}  # character_id -> voice_name
    
    def register_voice(self, character_id: str, voice_name: str):
        """Register a voice for a character."""
        self.voice_map[character_id] = voice_name
    
    def synthesize(self, text: str, character_id: Optional[str] = None, **kwargs) -> bytes:
        """
        Synthesize text with optional character-specific voice.
        
        Args:
            text: Text to synthesize
            character_id: Optional character ID to use character-specific voice
            **kwargs: Additional parameters
        """
        voice = None
        if character_id and character_id in self.voice_map:
            voice = self.voice_map[character_id]
        
        return self.base_provider.synthesize(text, voice=voice, **kwargs)


def get_tts_provider(provider: str = "openai", multi_voice: bool = False) -> TTSProvider:
    """
    Factory function to get a TTS provider.
    
    Args:
        provider: "openai" or other future providers
        multi_voice: Whether to wrap in MultiVoiceTTS
    
    Returns:
        TTSProvider instance
    """
    if provider == "openai":
        base = OpenAITTS()
        if multi_voice:
            return MultiVoiceTTS(base)
        return base
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")

