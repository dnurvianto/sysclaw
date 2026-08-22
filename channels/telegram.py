"""
SysClaw Telegram Channel Adapter (Zero-Dependency)
Implements Telegram Bot API communication using pure Python standard library.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
import config
from .base import BaseChannel

class TelegramChannel(BaseChannel):
    """Telegram Bot API Client for SysClaw."""

    def __init__(self, token: str = None):
        self.token = token or config.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def _request(self, method: str, params: Dict[str, Any] = None, timeout: int = 40) -> Optional[Dict[str, Any]]:
        """Generic HTTP POST request to Telegram Bot API."""
        if not self.token:
            print("[TELEGRAM ERROR] Bot token is not configured in .env!", flush=True)
            return None

        url = f"{self.api_url}/{method}"
        data = None
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SysClaw-Orchestrator/1.0"
        }

        if params:
            data = json.dumps(params).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("ok"):
                    return res.get("result")
                else:
                    print(f"[TELEGRAM API ERROR] {res.get('description')}", flush=True)
                    return None
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="ignore")
            print(f"[TELEGRAM HTTP ERROR {e.code}] {err}", flush=True)
            return None
        except urllib.error.URLError as e:
            # Normal on polling timeouts
            if "timed out" not in str(e).lower():
                print(f"[TELEGRAM NETWORK ERROR] {e.reason}", flush=True)
            return None
        except Exception as e:
            print(f"[TELEGRAM EXCEPTION] {str(e)}", flush=True)
            return None

    def get_me(self) -> Optional[Dict[str, Any]]:
        """Validate bot token and get bot identity info."""
        return self._request("getMe", timeout=10)

    def get_updates(self, offset: int = 0, timeout: int = 30) -> List[Dict[str, Any]]:
        """Fetch incoming updates via HTTP Long Polling."""
        params = {
            "offset": offset,
            "timeout": timeout,
            "allowed_updates": ["message", "callback_query"]
        }
        res = self._request("getUpdates", params=params, timeout=timeout + 10)
        return res if isinstance(res, list) else []

    def send_message(self, chat_id: Any, text: str, reply_markup: Dict = None, parse_mode: str = None) -> bool:
        """
        Send a message to a Telegram chat.
        Automatically chunks messages exceeding Telegram's 4096 character limit.
        """
        if not text:
            return False

        # Telegram hard limit: 4096 characters per message
        chunk_size = 4000
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        success = True
        for idx, chunk in enumerate(text_chunks):
            # Only attach keyboard to the final chunk
            markup = reply_markup if idx == len(text_chunks) - 1 else None
            
            params = {
                "chat_id": chat_id,
                "text": chunk
            }
            if markup:
                params["reply_markup"] = markup
            if parse_mode:
                params["parse_mode"] = parse_mode

            res = self._request("sendMessage", params=params, timeout=15)
            if not res:
                success = False

        return success

    def send_action(self, chat_id: Any, action: str = "typing") -> None:
        """Send chat action (e.g. typing) to indicate bot is working."""
        self._request("sendChatAction", params={"chat_id": chat_id, "action": action}, timeout=5)

    def answer_callback(self, callback_id: str, text: str = None, alert: bool = False) -> None:
        """Acknowledge an inline keyboard callback query."""
        params = {"callback_query_id": callback_id}
        if text:
            params["text"] = text
            params["show_alert"] = alert
        self._request("answerCallbackQuery", params=params, timeout=5)

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata and remote path for a Telegram file."""
        return self._request("getFile", params={"file_id": file_id}, timeout=15)

    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download raw binary content of a file from Telegram servers."""
        if not self.token or not file_path:
            return None
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        req = urllib.request.Request(url, headers={"User-Agent": "SysClaw-Orchestrator/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as e:
            print(f"[TELEGRAM FILE DOWNLOAD ERROR] {str(e)}", flush=True)
            return None
