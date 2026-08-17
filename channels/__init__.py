"""
SysClaw Modular Channels
"""

from .base import BaseChannel
from .telegram import TelegramChannel

def get_channel(channel_name: str = "telegram") -> BaseChannel:
    """Factory function to resolve and instantiate messaging channel."""
    name = (channel_name or "telegram").lower()
    if name == "telegram":
        return TelegramChannel()
    return TelegramChannel()
