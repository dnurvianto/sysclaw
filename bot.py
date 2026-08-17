#!/usr/bin/env python3
"""
==============================================================================
 SysClaw - Lean, Zero-DB Server Orchestrator & AI ChatOps Scaffold
 https://github.com/dnurvianto/sysclaw
==============================================================================
"""

import sys
import time
import signal
import traceback
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import config
from core.security import is_authorized, is_rate_limited
from core.memory import get_history, add_message, clear_history
from core.router import get_main_keyboard, get_menu_handler, get_action_handler
from providers import get_ai_provider
from channels import get_channel
from targets import get_target_node

# Auto-import all menus via package auto-discovery
import menus

# Initialize Core Services via Factory
telegram = get_channel("telegram")
ai_provider = get_ai_provider(config.AI_PROVIDER)
target_node = get_target_node("localhost")
executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="sysclaw-worker")

RUNNING = True

def signal_handler(sig, frame):
    """Graceful shutdown on SIGINT / SIGTERM."""
    global RUNNING
    print("\n[SYSCLAW] Shutdown signal received, terminating workers...", flush=True)
    RUNNING = False
    executor.shutdown(wait=False)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def build_system_prompt() -> str:
    """Constructs dynamic context prompt for the AI reasoning engine."""
    os_name = target_node.get_os_info()
    return (
        f"You are SysClaw, an intelligent AI DevOps assistant and Pocket SRE for Linux servers.\n"
        f"Host Environment: {os_name}\n"
        f"Server Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"Operational Directives:\n"
        f"1. Answer technical questions, system diagnostics, and log analysis concisely, accurately, and to the point.\n"
        f"2. Provide safe, verified, and parameterized Linux shell recommendations.\n"
        f"3. Automatically respond in the same language used by the user (English, Indonesian, etc.).\n"
        f"4. If the user asks for general assistance, explain the available menu buttons on the Telegram keyboard."
    )

def handle_incoming_message(chat_id: int, text: str, message_id: int = None):
    """Worker task to process a single user message asynchronously."""
    text = (text or "").strip()
    if not text:
        return

    # Check for /start, /help
    if text.startswith("/start") or text.startswith("/help"):
        welcome = (
            f"🐾 **Welcome to SysClaw!**\n"
            f"*A Lean, Zero-DB Server Orchestrator & AI ChatOps Scaffold*\n\n"
            f"Use the menu buttons below to inspect server health metrics, "
            f"or send any text query to consult with AI ({config.AI_MODEL})."
        )
        telegram.send_message(chat_id, welcome, reply_markup=get_main_keyboard(), parse_mode="Markdown")
        return

    # Check for /reset, /clear
    if text.startswith("/reset") or text.startswith("/clear"):
        clear_history(str(chat_id))
        telegram.send_message(chat_id, "🧹 **[Memory Reset]** Conversational context memory buffer in RAM has been cleared.", reply_markup=get_main_keyboard(), parse_mode="Markdown")
        return

    # Check for deterministic menu match (Track 1: Fast & 0 Token)
    menu_func = get_menu_handler(text)
    if menu_func:
        try:
            reply = menu_func(str(chat_id))
            telegram.send_message(chat_id, reply, reply_markup=get_main_keyboard(), parse_mode="Markdown")
        except Exception as e:
            print(f"[MENU ERROR] {traceback.format_exc()}", flush=True)
            telegram.send_message(chat_id, "⚠️ [Menu Error] An error occurred while executing the menu action.", reply_markup=get_main_keyboard())
        return

    # Rate Limiting Check for AI Calls (Prevent Token Flooding)
    if is_rate_limited(chat_id):
        telegram.send_message(chat_id, "⏳ Rate limit reached. Please wait a moment before sending your next AI request.", reply_markup=get_main_keyboard())
        return

    # Track 2: Smart LLM Reasoning (DeepSeek AI)
    telegram.send_action(chat_id, "typing")
    
    # Save user message to memory
    add_message(str(chat_id), "user", text)
    
    history = get_history(str(chat_id))
    system_prompt = build_system_prompt()
    
    try:
        # Query AI provider
        ai_reply = ai_provider.chat(history, system_prompt=system_prompt)
    except Exception as e:
        print(f"[AI PROVIDER EXCEPTION] {traceback.format_exc()}", flush=True)
        ai_reply = "⚠️ [AI Error] Failed to reach the configured AI provider. Please check server logs."

    # Save assistant response to memory
    add_message(str(chat_id), "assistant", ai_reply)
    
    telegram.send_message(chat_id, ai_reply, reply_markup=get_main_keyboard(), parse_mode="Markdown")

def handle_incoming_callback(callback_query: dict):
    """Worker task to process inline keyboard clicks."""
    cb_id = callback_query.get("id")
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    # Layer 1 Security: Strict Silent Drop on Unauthorized Callback
    if not is_authorized(chat_id):
        # Silent drop: Do not reply, do not acknowledge
        return

    handler = get_action_handler(data)
    if handler:
        try:
            res = handler(str(chat_id), data)
            telegram.answer_callback(cb_id)
            if res:
                telegram.send_message(chat_id, res, reply_markup=get_main_keyboard(), parse_mode="Markdown")
        except Exception as e:
            print(f"[ACTION ERROR] {traceback.format_exc()}", flush=True)
            telegram.answer_callback(cb_id, text="Action execution failed.", alert=True)
    else:
        telegram.answer_callback(cb_id, text="Unknown action.")

def main():
    """Main execution loop (HTTP Long Polling)."""
    print("=" * 65)
    print(" 🐾 SysClaw - Server Orchestrator & AI ChatOps Scaffold")
    print(f" 🚀 Version: 1.0.0 | AI Provider: {config.AI_PROVIDER.upper()} ({config.AI_MODEL})")
    print(f" 🐧 Host OS: {target_node.get_os_info()}")
    print("=" * 65, flush=True)

    if not config.TELEGRAM_BOT_TOKEN:
        print("[FATAL ERROR] TELEGRAM_BOT_TOKEN is not configured in .env!", flush=True)
        print("Please copy .env.example to .env and configure your bot credentials.")
        sys.exit(1)

    # Validate bot connectivity
    bot_info = telegram.get_me()
    if not bot_info:
        print("[FATAL ERROR] Failed to connect to Telegram API. Please verify token and internet access.", flush=True)
        sys.exit(1)

    bot_name = bot_info.get("first_name", "Bot")
    username = bot_info.get("username", "Unknown")
    print(f"[✓] Connected to Telegram Bot: {bot_name} (@{username})")
    print(f"[✓] Whitelisted Chat IDs: {list(config.ALLOWED_CHAT_IDS) or '[WARNING: Empty Whitelist]'}")
    print("[✓] SysClaw Polling Engine is active... Listening for incoming events.\n", flush=True)

    offset = 0
    poll_error_count = 0

    while RUNNING:
        try:
            updates = telegram.get_updates(offset=offset, timeout=25)
            poll_error_count = 0  # Reset on successful poll
            
            for update in updates:
                offset = update.get("update_id", offset) + 1

                # 1. Handle Standard Text Messages
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")
                    msg_id = msg.get("message_id")

                    # Layer 1: Strict Whitelist & Silent Drop
                    if not is_authorized(chat_id):
                        # Silent drop: No reply, no leak
                        continue

                    # Dispatch to thread worker
                    executor.submit(handle_incoming_message, chat_id, text, msg_id)

                # 2. Handle Inline Button Callbacks
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    executor.submit(handle_incoming_callback, cb)

        except Exception as e:
            poll_error_count += 1
            backoff = min(30, 2 ** min(poll_error_count, 5))
            print(f"[POLL EXCEPTION] {str(e)} (Backing off for {backoff}s)", flush=True)
            time.sleep(backoff)

if __name__ == "__main__":
    main()
