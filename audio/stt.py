"""Speech-to-Text (STT) interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
import io
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


class DeepgramSTT(STTProvider):
    """Deepgram STT implementation."""
    
    def __init__(self):
        try:
            from deepgram import DeepgramClient
            self.DeepgramClient = DeepgramClient
        except ImportError:
            raise ImportError("deepgram-sdk is required. Install with: pip install deepgram-sdk")
        
        if not settings.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY must be set")
        
        # DeepgramClient v5 uses access_token parameter or env var
        import os
        # Set env var for this session (Deepgram SDK reads from env)
        os.environ['DEEPGRAM_API_KEY'] = settings.deepgram_api_key
        self.client = DeepgramClient(access_token=settings.deepgram_api_key)
    
    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Transcribe audio using Deepgram API.
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language code (e.g., "en", "es")
        
        Returns:
            Transcribed text
        """
        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        
        # Configure options for Deepgram SDK v5
        options = {
            "model": "nova-2",
            "language": language or "en",
            "smart_format": True,
            "punctuate": True,
        }
        
        # Transcribe using Deepgram SDK v5 API
        response = self.client.listen.rest.v("1").transcribe_file(
            {"buffer": audio_file},
            options
        )
        
        # Extract transcript from response
        if hasattr(response, 'results') and response.results:
            if hasattr(response.results, 'channels') and response.results.channels:
                channel = response.results.channels[0]
                if hasattr(channel, 'alternatives') and channel.alternatives:
                    return channel.alternatives[0].transcript
        
        return ""
    
    def transcribe_stream(self, audio_stream) -> str:
        """
        Transcribe streaming audio using Deepgram.
        
        Args:
            audio_stream: Streaming audio source (file-like object or bytes)
        
        Returns:
            Transcribed text
        """
        # For streaming, we'd use Deepgram's live transcription
        # For now, collect the stream and use prerecorded API
        if hasattr(audio_stream, 'read'):
            audio_data = audio_stream.read()
        else:
            audio_data = audio_stream
        
        return self.transcribe(audio_data)


def get_stt_provider(provider: str = "deepgram") -> STTProvider:
    """
    Factory function to get an STT provider.
    
    Args:
        provider: "deepgram", "openai", or "local"
    
    Returns:
        STTProvider instance
    """
    if provider == "deepgram":
        return DeepgramSTT()
    elif provider == "openai":
        return OpenAIWhisperSTT()
    elif provider == "local":
        return LocalWhisperSTT()
    else:
        raise ValueError(f"Unknown STT provider: {provider}")

