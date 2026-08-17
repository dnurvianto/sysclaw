"""
SysClaw State & Context Memory Manager (Zero-Database)
Maintains an in-memory sliding window of conversation turns per user.
Zero setup, zero SQL/Redis dependencies, ultra-lightweight.
"""

from typing import List, Dict
import config

# In-memory storage dictionaries
_CHAT_BUFFERS: Dict[str, List[Dict[str, str]]] = {}
_USER_MODELS: Dict[str, str] = {}

def get_history(chat_id: str) -> List[Dict[str, str]]:
    """Retrieve conversation history for a given chat_id."""
    key = str(chat_id)
    return _CHAT_BUFFERS.get(key, [])

def add_message(chat_id: str, role: str, content: str) -> None:
    """
    Append a message to the in-memory context buffer.
    Automatically prunes older messages when buffer exceeds MAX_MEMORY_TURNS.
    """
    key = str(chat_id)
    if key not in _CHAT_BUFFERS:
        _CHAT_BUFFERS[key] = []
    
    _CHAT_BUFFERS[key].append({"role": role, "content": content})
    
    # Each turn consists of 1 user + 1 assistant message (2 items per turn)
    max_items = config.MAX_MEMORY_TURNS * 2
    if len(_CHAT_BUFFERS[key]) > max_items:
        _CHAT_BUFFERS[key] = _CHAT_BUFFERS[key][-max_items:]

def clear_history(chat_id: str) -> None:
    """Reset and clear conversation history for a given chat_id."""
    key = str(chat_id)
    if key in _CHAT_BUFFERS:
        _CHAT_BUFFERS[key] = []

def get_user_model(chat_id: str) -> str:
    """Retrieve the selected AI model for a user (defaults to config.AI_MODEL)."""
    return _USER_MODELS.get(str(chat_id), config.AI_MODEL)

def set_user_model(chat_id: str, model_name: str) -> None:
    """Set the active AI model for a specific user session."""
    _USER_MODELS[str(chat_id)] = model_name.strip()

