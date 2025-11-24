"""Speech-to-Text (STT) interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional
import openai
from config.settings import settings


class STTProvider(ABC):
    """Abstract base class for STT providers."""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language code (e.g., "en", "es")
        
        Returns:
            Transcribed text
        """
        pass
    
    @abstractmethod
    def transcribe_stream(self, audio_stream) -> str:
        """
        Transcribe streaming audio.
        
        Args:
            audio_stream: Streaming audio source
        
        Returns:
            Transcribed text
        """
        pass


class OpenAIWhisperSTT(STTProvider):
    """OpenAI Whisper API STT implementation."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio using OpenAI Whisper API."""
        # Note: OpenAI Whisper API expects a file-like object
        # In a real implementation, you'd save audio_data to a temp file or use BytesIO
        # For now, this is a placeholder structure
        # TODO: Implement proper file handling
        raise NotImplementedError("File handling for audio_data needs to be implemented")
    
    def transcribe_stream(self, audio_stream) -> str:
        """Transcribe streaming audio."""
        # OpenAI Realtime API or similar would be used here
        # For now, placeholder
        raise NotImplementedError("Streaming transcription needs to be implemented")


class LocalWhisperSTT(STTProvider):
    """Local Whisper model STT implementation (future)."""
    
    def __init__(self, model_name: str = "base"):
        # Would use whisper library here
        raise NotImplementedError("Local Whisper not yet implemented")
    
    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        raise NotImplementedError("Local Whisper not yet implemented")
    
    def transcribe_stream(self, audio_stream) -> str:
        raise NotImplementedError("Local Whisper not yet implemented")


def get_stt_provider(provider: str = "openai") -> STTProvider:
    """
    Factory function to get an STT provider.
    
    Args:
        provider: "openai" or "local"
    
    Returns:
        STTProvider instance
    """
    if provider == "openai":
        return OpenAIWhisperSTT()
    elif provider == "local":
        return LocalWhisperSTT()
    else:
        raise ValueError(f"Unknown STT provider: {provider}")

