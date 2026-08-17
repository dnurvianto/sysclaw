"""
SysClaw Abstract Base Channel
Defines the contract for messaging platform adapters (Telegram, Discord, Slack, etc.).
"""

from typing import Dict, Any, List, Optional

class BaseChannel:
    """Universal interface for chat and messaging channels."""

    def get_me(self) -> Optional[Dict[str, Any]]:
        """Validate connection and retrieve bot profile information."""
        raise NotImplementedError

    def get_updates(self, offset: int = 0, timeout: int = 30) -> List[Dict[str, Any]]:
        """Retrieve incoming messages or events."""
        raise NotImplementedError

    def send_message(self, chat_id: Any, text: str, reply_markup: Dict = None, parse_mode: str = None) -> bool:
        """Send a message to a destination chat."""
        raise NotImplementedError

    def send_action(self, chat_id: Any, action: str = "typing") -> None:
        """Indicate activity status (e.g. typing indicator)."""
        pass
