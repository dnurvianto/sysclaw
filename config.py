"""
SysClaw - Central Configuration Loader (Zero-Dependency)
Reads .env or OS environment variables without requiring external packages.
"""

import os
from pathlib import Path

# Base Directory of SysClaw
BASE_DIR = Path(__file__).resolve().parent

def load_dotenv(env_path: Path = None):
    """Simple, pure-Python .env file parser."""
    if env_path is None:
        env_path = BASE_DIR / ".env"
    
    if not env_path.is_file():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'\"")
                # Only set if not already present in OS environment
                if key and key not in os.environ:
                    os.environ[key] = val

# Load .env file automatically
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Security Whitelist
raw_chat_ids = os.getenv("ALLOWED_CHAT_IDS", "").strip()
ALLOWED_CHAT_IDS = set()
if raw_chat_ids:
    for cid in raw_chat_ids.split(","):
        cid = cid.strip()
        if cid:
            try:
                ALLOWED_CHAT_IDS.add(int(cid))
            except ValueError:
                ALLOWED_CHAT_IDS.add(cid)

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek").strip().lower()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat").strip()

# Memory Configuration
try:
    MAX_MEMORY_TURNS = int(os.getenv("MAX_MEMORY_TURNS", "10"))
except ValueError:
    MAX_MEMORY_TURNS = 10
