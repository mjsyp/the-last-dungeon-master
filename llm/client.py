"""LLM client wrapper for OpenAI/Anthropic."""
from typing import Dict, Any, Optional
import openai
from config.settings import settings


class LLMClient:
    """Unified LLM client interface."""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize LLM client.
        
        Args:
            provider: "openai" or "anthropic"
        """
        self.provider = provider
        
        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be set")
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4-turbo-preview"  # Can be configured
        elif provider == "anthropic":
            # Future: add Anthropic support
            raise NotImplementedError("Anthropic support coming soon")
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., {"type": "json_object"})
        
        Returns:
            Generated text
        """
        if self.provider == "openai":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        
        raise NotImplementedError(f"Provider {self.provider} not implemented")

