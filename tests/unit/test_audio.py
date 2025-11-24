"""Unit tests for audio providers."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from audio.stt import STTProvider, DeepgramSTT, get_stt_provider
from audio.tts import TTSProvider, DeepgramTTS, get_tts_provider
import io


class TestDeepgramSTT:
    """Tests for Deepgram STT provider."""
    
    @patch('audio.stt.settings')
    def test_transcribe(self, mock_settings):
        """Test audio transcription."""
        mock_settings.deepgram_api_key = "test_key"
        
        # Create STT instance and mock the client
        stt = DeepgramSTT()
        
        # Mock the client's API structure
        mock_response = Mock()
        mock_response.results = Mock()
        mock_response.results.channels = [Mock()]
        mock_response.results.channels[0].alternatives = [Mock(transcript="Hello world")]
        
        mock_v1 = Mock()
        mock_v1.transcribe_file = Mock(return_value=mock_response)
        mock_rest = Mock()
        mock_rest.v = Mock(return_value=mock_v1)
        mock_listen = Mock()
        mock_listen.rest = mock_rest
        stt.client = Mock()
        stt.client.listen = mock_listen
        
        result = stt.transcribe(b"audio data")
        
        assert result == "Hello world"
    
    @patch('audio.stt.settings')
    def test_transcribe_empty_result(self, mock_settings):
        """Test transcription with empty result."""
        mock_settings.deepgram_api_key = "test_key"
        
        stt = DeepgramSTT()
        
        # Mock empty response
        mock_response = Mock()
        mock_response.results = None
        
        mock_v1 = Mock()
        mock_v1.transcribe_file = Mock(return_value=mock_response)
        mock_rest = Mock()
        mock_rest.v = Mock(return_value=mock_v1)
        mock_listen = Mock()
        mock_listen.rest = mock_rest
        stt.client = Mock()
        stt.client.listen = mock_listen
        
        result = stt.transcribe(b"audio data")
        
        assert result == ""
    
    def test_get_stt_provider(self):
        """Test STT provider factory function."""
        with patch('audio.stt.DeepgramSTT') as mock_deepgram:
            provider = get_stt_provider("deepgram")
            mock_deepgram.assert_called_once()
        
        with pytest.raises(ValueError):
            get_stt_provider("invalid_provider")


class TestDeepgramTTS:
    """Tests for Deepgram TTS provider."""
    
    @patch('audio.tts.settings')
    def test_synthesize(self, mock_settings):
        """Test text-to-speech synthesis."""
        mock_settings.deepgram_api_key = "test_key"
        
        tts = DeepgramTTS()
        
        # Mock the client's API structure
        mock_response = b"audio bytes"
        mock_v1 = Mock()
        mock_v1.save = Mock(return_value=mock_response)
        mock_speak = Mock()
        mock_speak.v = Mock(return_value=mock_v1)
        tts.client = Mock()
        tts.client.speak = mock_speak
        
        result = tts.synthesize("Hello world")
        
        assert result == b"audio bytes"
        assert mock_v1.save.called
    
    @patch('audio.tts.settings')
    def test_synthesize_with_voice(self, mock_settings):
        """Test synthesis with custom voice."""
        mock_settings.deepgram_api_key = "test_key"
        
        tts = DeepgramTTS()
        
        # Mock the client's API structure
        mock_response = b"audio bytes"
        mock_v1 = Mock()
        mock_v1.save = Mock(return_value=mock_response)
        mock_speak = Mock()
        mock_speak.v = Mock(return_value=mock_v1)
        tts.client = Mock()
        tts.client.speak = mock_speak
        
        result = tts.synthesize("Hello", voice="aura-luna-en")
        
        assert result == b"audio bytes"
        # Verify save was called (voice is in options)
        assert mock_v1.save.called
    
    def test_get_tts_provider(self):
        """Test TTS provider factory function."""
        with patch('audio.tts.DeepgramTTS') as mock_deepgram:
            provider = get_tts_provider("deepgram")
            mock_deepgram.assert_called_once()
        
        with pytest.raises(ValueError):
            get_tts_provider("invalid_provider")

