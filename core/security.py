"""
SysClaw Security Guard - Whitelist, Silent Drop, and Rate Limiter
Enforces zero-trust access: Unauthorized requests are silently ignored without any response.
Includes an in-memory sliding rate limiter to prevent token spamming.
"""

import time
from typing import Union, Dict, List
import config

_WARN_EMPTY_WHITELIST = False
_RATE_LIMITS: Dict[str, List[float]] = {}
MAX_REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 3.0

def is_authorized(chat_id: Union[int, str]) -> bool:
    """
    Check if a given chat_id is in the whitelist.
    If no whitelist is configured, warns once and defaults to False for safety.
    """
    global _WARN_EMPTY_WHITELIST
    if not config.ALLOWED_CHAT_IDS:
        if not _WARN_EMPTY_WHITELIST:
            print("[SECURITY WARNING] ALLOWED_CHAT_IDS is empty! Denying all access by default.", flush=True)
            _WARN_EMPTY_WHITELIST = True
        return False

    try:
        numeric_id = int(chat_id)
        if numeric_id in config.ALLOWED_CHAT_IDS:
            return True
    except (ValueError, TypeError):
        pass

    return str(chat_id) in config.ALLOWED_CHAT_IDS

def is_rate_limited(chat_id: Union[int, str]) -> bool:
    """
    In-memory sliding window rate limiter.
    Returns True if user exceeds MAX_REQUESTS_PER_WINDOW within WINDOW_SECONDS.
    """
    key = str(chat_id)
    now = time.time()
    
    if key not in _RATE_LIMITS:
        _RATE_LIMITS[key] = []
    
    # Remove timestamps older than the sliding window
    _RATE_LIMITS[key] = [t for t in _RATE_LIMITS[key] if now - t < WINDOW_SECONDS]
    
    if len(_RATE_LIMITS[key]) >= MAX_REQUESTS_PER_WINDOW:
        return True
    
    _RATE_LIMITS[key].append(now)
    return False
