"""
SysClaw State & Context Memory Manager (Zero-Database)
Maintains an in-memory sliding window of conversation turns per user.
Zero setup, zero SQL/Redis dependencies, ultra-lightweight.
"""

import threading
from typing import List, Dict
import config

_MEMORY_LOCK = threading.Lock()
# In-memory storage dictionaries
_CHAT_BUFFERS: Dict[str, List[Dict[str, str]]] = {}
_USER_MODELS: Dict[str, str] = {}
MAX_MESSAGE_CHARS = 4000

def get_history(chat_id: str) -> List[Dict[str, str]]:
    """Retrieve conversation history for a given chat_id."""
    key = str(chat_id)
    with _MEMORY_LOCK:
        return list(_CHAT_BUFFERS.get(key, []))

def add_message(chat_id: str, role: str, content: str) -> None:
    """
    Append a message to the in-memory context buffer.
    Validates role strictly to 'user' or 'assistant' and limits character length.
    Automatically prunes older messages when buffer exceeds MAX_MEMORY_TURNS.
    """
    # Strict role validation to prevent system prompt injection
    safe_role = role if role in ("user", "assistant") else "user"
    # Content length guardrail
    safe_content = (content or "").strip()[:MAX_MESSAGE_CHARS]
    if not safe_content:
        return

    key = str(chat_id)
    with _MEMORY_LOCK:
        if key not in _CHAT_BUFFERS:
            _CHAT_BUFFERS[key] = []
        
        _CHAT_BUFFERS[key].append({"role": safe_role, "content": safe_content})
        
        # Each turn consists of 1 user + 1 assistant message (2 items per turn)
        max_items = config.MAX_MEMORY_TURNS * 2
        if len(_CHAT_BUFFERS[key]) > max_items:
            _CHAT_BUFFERS[key] = _CHAT_BUFFERS[key][-max_items:]

def clear_history(chat_id: str) -> None:
    """Reset and clear conversation history for a given chat_id."""
    key = str(chat_id)
    with _MEMORY_LOCK:
        if key in _CHAT_BUFFERS:
            _CHAT_BUFFERS[key] = []

def get_user_model(chat_id: str) -> str:
    """Retrieve the selected AI model for a user (defaults to config.AI_MODEL)."""
    key = str(chat_id)
    with _MEMORY_LOCK:
        return _USER_MODELS.get(key, config.AI_MODEL)

def set_user_model(chat_id: str, model_name: str) -> None:
    """Set the active AI model for a specific user session."""
    key = str(chat_id)
    clean_model = (model_name or "").strip()
    if clean_model:
        with _MEMORY_LOCK:
            _USER_MODELS[key] = clean_model

