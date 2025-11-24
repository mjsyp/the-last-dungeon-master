"""Embedding utilities for RAG."""
from typing import List
import openai
from config.settings import settings


class EmbeddingService:
    """Service for generating embeddings."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or .env file")
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"  # Can be swapped to other models
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch)."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

