"""
SysClaw Abstract Base AI Provider
Defines the clean, universal interface required by any AI provider adapter.
"""

from typing import List, Dict, Any

class BaseAIProvider:
    """Universal interface for LLM providers."""

    def chat(self, messages: List[Dict[str, Any]], system_prompt: str = "", model: str = None, image_b64: str = None, image_mime: str = "image/jpeg") -> str:
        """
        Send a conversation turn to the LLM and return the assistant text reply.
        
        Args:
            messages: List of dicts with 'role' and 'content' keys.
            system_prompt: High-level system instruction defining bot behavior.
            model: Optional model override.
            image_b64: Optional base64-encoded image string for vision reasoning.
            image_mime: MIME type of the uploaded image.
            
        Returns:
            The string response from the AI model.
        """
        raise NotImplementedError("Each AI provider must implement the chat() method.")
