"""Example usage of Deepgram STT and TTS."""
from audio.stt import get_stt_provider
from audio.tts import get_tts_provider


def example_stt():
    """Example: Transcribe audio using Deepgram."""
    # Get Deepgram STT provider
    stt = get_stt_provider("deepgram")
    
    # Read audio file (or get from microphone)
    with open("audio_file.wav", "rb") as f:
        audio_data = f.read()
    
    # Transcribe
    transcript = stt.transcribe(audio_data, language="en")
    print(f"Transcribed: {transcript}")
    
    return transcript


def example_tts():
    """Example: Synthesize speech using Deepgram."""
    # Get Deepgram TTS provider
    tts = get_tts_provider("deepgram")
    
    # Synthesize text
    text = "Hello, this is a test of Deepgram text-to-speech."
    audio_bytes = tts.synthesize(text, voice="aura-asteria-en")
    
    # Save to file
    with open("output.wav", "wb") as f:
        f.write(audio_bytes)
    
    print("Audio saved to output.wav")
    
    return audio_bytes


def example_multi_voice():
    """Example: Use different voices for different characters."""
    from audio.tts import MultiVoiceTTS, DeepgramTTS
    
    # Create multi-voice TTS
    tts = MultiVoiceTTS(DeepgramTTS())
    
    # Register voices for characters
    tts.register_voice("npc_1", "aura-asteria-en")
    tts.register_voice("npc_2", "aura-luna-en")
    tts.register_voice("npc_3", "aura-stella-en")
    
    # Synthesize with character-specific voices
    audio1 = tts.synthesize("Hello from NPC 1", character_id="npc_1")
    audio2 = tts.synthesize("Hello from NPC 2", character_id="npc_2")
    
    return audio1, audio2


if __name__ == "__main__":
    print("Deepgram STT/TTS Examples")
    print("=" * 40)
    print("\nNote: Make sure DEEPGRAM_API_KEY is set in your .env file")
    print("\nAvailable Deepgram voices:")
    print("  - aura-asteria-en (default)")
    print("  - aura-luna-en")
    print("  - aura-stella-en")
    print("  - aura-athena-en")
    print("  - aura-hera-en")
    print("  - aura-orion-en")
    print("  - aura-arcas-en")
    print("  - aura-perseus-en")
    print("  - aura-angus-en")
    print("  - aura-orpheus-en")
    print("  - aura-zeus-en")
    print("  - aura-odin-en")

