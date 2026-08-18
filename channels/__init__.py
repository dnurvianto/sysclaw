"""
SysClaw Modular Channels
"""

import importlib
from typing import Dict, Type
from .base import BaseChannel
from .telegram import TelegramChannel

_CHANNELS: Dict[str, Type[BaseChannel]] = {
    "telegram": TelegramChannel
}

def register_channel(name: str, channel_cls: Type[BaseChannel]):
    """Register a custom channel adapter."""
    _CHANNELS[name.lower()] = channel_cls

def get_channel(channel_name: str = "telegram") -> BaseChannel:
    """Factory function to resolve and instantiate messaging channel."""
    name = (channel_name or "telegram").lower()

    if name in _CHANNELS:
        return _CHANNELS[name]()

    # Sanitize and validate module name before dynamic import
    if not name.replace("_", "").isalnum() or name.startswith("_"):
        return TelegramChannel()

    try:
        mod = importlib.import_module(f".{name}", __package__)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseChannel) and attr is not BaseChannel:
                _CHANNELS[name] = attr
                return attr()
    except Exception:
        pass

    # Default fallback to Telegram
    return TelegramChannel()
