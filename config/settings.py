"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/dm_va"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Anthropic (optional)
    anthropic_api_key: Optional[str] = None
    
    # Deepgram (STT/TTS)
    deepgram_api_key: Optional[str] = None
    
    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    
    # Application
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

