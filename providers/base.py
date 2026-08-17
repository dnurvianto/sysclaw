"""
SysClaw Abstract Base AI Provider
Defines the clean, universal interface required by any AI provider adapter.
"""

from typing import List, Dict

class BaseAIProvider:
    """Universal interface for LLM providers."""

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        """
        Send a conversation turn to the LLM and return the assistant text reply.
        
        Args:
            messages: List of dicts with 'role' and 'content' keys.
            system_prompt: High-level system instruction defining bot behavior.
            
        Returns:
            The string response from the AI model.
        """
        raise NotImplementedError("Each AI provider must implement the chat() method.")
