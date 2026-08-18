"""
SysClaw Security Guard - Whitelist, Silent Drop, and Rate Limiter
Enforces zero-trust access: Unauthorized requests are silently ignored without any response.
Includes an in-memory sliding rate limiter to prevent token spamming.
"""

import time
import threading
from typing import Union, Dict, List
import config

_WARN_EMPTY_WHITELIST = False
_SECURITY_LOCK = threading.Lock()
_RATE_LIMITS: Dict[str, List[float]] = {}
MAX_REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 3.0
_LAST_CLEANUP_TIME = 0.0

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
    Thread-safe in-memory sliding window rate limiter with auto-eviction.
    Returns True if user exceeds MAX_REQUESTS_PER_WINDOW within WINDOW_SECONDS.
    """
    global _LAST_CLEANUP_TIME
    key = str(chat_id)
    now = time.time()

    with _SECURITY_LOCK:
        # Periodic cleanup of stale rate limit entries (every 60 seconds)
        if now - _LAST_CLEANUP_TIME > 60.0:
            stale_keys = [k for k, ts in _RATE_LIMITS.items() if not ts or (now - ts[-1] > WINDOW_SECONDS * 5)]
            for k in stale_keys:
                _RATE_LIMITS.pop(k, None)
            _LAST_CLEANUP_TIME = now

        if key not in _RATE_LIMITS:
            _RATE_LIMITS[key] = []

        # Remove timestamps older than sliding window
        _RATE_LIMITS[key] = [t for t in _RATE_LIMITS[key] if now - t < WINDOW_SECONDS]

        if len(_RATE_LIMITS[key]) >= MAX_REQUESTS_PER_WINDOW:
            return True

        _RATE_LIMITS[key].append(now)
        return False
