"""
SysClaw DeepSeek AI Provider (Zero-Dependency)
Implements DeepSeek REST API using Python standard library urllib.request.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any
import config
from .base import BaseAIProvider

class DeepSeekProvider(BaseAIProvider):
    """DeepSeek Chat / Reasoner API Adapter."""

    API_URL = "https://api.deepseek.com/chat/completions"

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.DEEPSEEK_API_KEY
        self.model = model or config.AI_MODEL or "deepseek-chat"

    def chat(self, messages: List[Dict[str, Any]], system_prompt: str = "", model: str = None, image_b64: str = None, image_mime: str = "image/jpeg", reasoning_effort: str = "high") -> str:
        if not self.api_key:
            return "⚠️ [DeepSeek Error] DEEPSEEK_API_KEY is not configured in .env!"

        active_model = model or self.model or config.AI_MODEL or "deepseek-v4-flash"

        # If an image is provided but active model is text-only, route to vision engine
        if image_b64 and "vision" not in active_model:
            active_model = "deepseek-v4-flash-vision-exp"

        # Prepare payload
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        
        # Clone messages to prevent in-place mutation of history
        for idx, m in enumerate(messages):
            if idx == len(messages) - 1 and image_b64:
                # Multimodal content for the current turn
                text_content = m.get("content", "") or "Please analyze this image/screenshot and provide technical insights or troubleshooting steps."
                payload_messages.append({
                    "role": m.get("role", "user"),
                    "content": [
                        {"type": "text", "text": text_content},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_mime};base64,{image_b64}"
                            }
                        }
                    ]
                })
            else:
                payload_messages.append(m)

        data = {
            "model": active_model,
            "messages": payload_messages,
            "stream": False,
            "reasoning_effort": reasoning_effort or "high",
            "extra_body": {
                "thinking": {
                    "type": "enabled"
                }
            }
        }

        body = json.dumps(data).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "SysClaw-Orchestrator/1.0"
        }

        req = urllib.request.Request(self.API_URL, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choice = result.get("choices", [{}])[0]
                message = choice.get("message", {})
                return message.get("content", "").strip() or "⚠️ [DeepSeek] Empty response received from AI model."
        except urllib.error.HTTPError as e:
            error_detail = e.read().decode("utf-8", errors="ignore")
            print(f"[DEEPSEEK HTTP ERROR {e.code}] {error_detail}", flush=True)
            return f"⚠️ [DeepSeek Error] Service responded with HTTP {e.code}. Please try again later."
        except urllib.error.URLError as e:
            print(f"[DEEPSEEK NETWORK ERROR] {e.reason}", flush=True)
            return "⚠️ [DeepSeek Error] Network connection to AI provider failed."
        except Exception as e:
            print(f"[DEEPSEEK EXCEPTION] {type(e).__name__}: {str(e)}", flush=True)
            return "⚠️ [DeepSeek Error] An unexpected error occurred while querying the AI provider."
