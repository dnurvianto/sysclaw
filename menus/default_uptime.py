"""
SysClaw Default Menu Handlers
Provides the out-of-the-box system overview menu and memory reset action.
"""

from datetime import datetime
from core.router import register_menu, register_action
from core.memory import clear_history
from targets import get_target_node

@register_menu("⏱️ Host Overview", row=1)
def handle_uptime_menu(chat_id: str) -> str:
    """Collects and formats the local host server health metrics."""
    target = get_target_node("localhost")
    os_name = target.get_os_info()
    uptime_str = target.get_uptime()
    load_str = target.get_load_avg()
    mem = target.get_memory_info()
    disk = target.get_disk_info("/")
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    msg = (
        f"🖥️ **[SysClaw — Host Overview]**\n"
        f"🕒 Timestamp: `{now_str}`\n"
        f"🐧 OS: `{os_name}`\n"
        f"⏱️ Uptime: `{uptime_str}`\n\n"
        f"📊 **Resource Metrics:**\n"
        f"• CPU Load Avg : `{load_str}`\n"
        f"• RAM Usage    : `{mem['used']} / {mem['total']}` (Available: `{mem['available']}`)\n"
        f"• Root Disk    : `{disk['used']} / {disk['total']} ({disk['percent']})`\n\n"
        f"🟢 *Status: Host Operating Normally*"
    )
    return msg

@register_menu("🧹 Clear Memory", row=2)
def handle_reset_memory(chat_id: str) -> str:
    """Clears the conversational context buffer in RAM."""
    clear_history(chat_id)
    return "🧹 **[Memory Reset]** Conversational context memory buffer in RAM has been cleared."
