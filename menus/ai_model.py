"""
==============================================================================
 SysClaw - Modular AI Model Selector Menu (Zero-DB)
 https://github.com/dnurvianto/sysclaw
==============================================================================
Provides dynamic, zero-downtime switching between AI inference engines.
"""

from typing import Dict, Any
from core.router import register_menu, register_action
from core.memory import get_user_model, set_user_model, get_user_effort, set_user_effort
from channels import get_channel

# Channel instance for dispatching inline keyboards
_telegram = get_channel("telegram")

# Supported Production AI Models (DeepSeek API Engine)
SUPPORTED_MODELS: Dict[str, Dict[str, str]] = {
    "deepseek-v4-flash": {
        "name": "⚡ DeepSeek V4 Flash",
        "badge": "Flash Tier (High Throughput)",
        "description": "Ultra-fast inference speed (<500ms). Optimized for rapid server health inspections, configuration checks, and standard DevOps Q&A."
    },
    "deepseek-v4-pro": {
        "name": "🔬 DeepSeek V4 Pro",
        "badge": "Pro Tier (Deep Reasoning)",
        "description": "Deep architectural reasoning and advanced problem-solving. Ideal for complex incident diagnostics, root-cause troubleshooting, and intricate shell scripting."
    },
    "deepseek-v4-flash-vision-exp": {
        "name": "👁️ DeepSeek V4 Vision",
        "badge": "Vision Tier (Multimodal)",
        "description": "Multimodal visual reasoning. Analyzes uploaded screenshots, charts, error logs, and infrastructure diagrams."
    }
}

SUPPORTED_EFFORTS: Dict[str, Dict[str, str]] = {
    "low": {"name": "⚡ Low (Fastest)", "desc": "Lightweight reasoning, fastest response time."},
    "high": {"name": "🔬 High (Standard)", "desc": "Deep reasoning, thorough analysis (Default)."},
    "max": {"name": "🔥 Max (Deepest)", "desc": "Exhaustive reasoning, maximum problem-solving capacity."}
}

def build_model_inline_keyboard(active_model: str, active_effort: str = "high") -> Dict[str, Any]:
    """Generates an interactive inline keyboard displaying available model & reasoning effort choices."""
    buttons = []
    # 1. Model Rows
    for model_id, details in SUPPORTED_MODELS.items():
        is_selected = (model_id == active_model)
        prefix = "✅ " if is_selected else "🔹 "
        button_text = f"{prefix}{details['name']}"
        buttons.append([{"text": button_text, "callback_data": f"set_model:{model_id}"}])
    
    # 2. Reasoning Effort Row
    effort_row = []
    for eff_id, eff_meta in SUPPORTED_EFFORTS.items():
        prefix = "🎯 " if eff_id == active_effort else ""
        btn_label = f"{prefix}{eff_id.upper()}"
        effort_row.append({"text": btn_label, "callback_data": f"set_effort:{eff_id}"})
    
    buttons.append(effort_row)
    return {"inline_keyboard": buttons}

def get_dynamic_model_label(chat_id: str) -> str:
    """Returns dynamic label showing currently selected AI model and effort on the keyboard."""
    active = get_user_model(chat_id)
    effort = get_user_effort(chat_id)
    return f"⚡ AI Model: {active} [{effort.upper()}]"

@register_menu(get_dynamic_model_label, row=2, prefix="⚡ AI Model")
def handle_ai_model_menu(chat_id: str) -> str:
    """
    Renders the active AI engine status card and attaches interactive inline selection buttons.
    """
    current_model = get_user_model(chat_id)
    current_effort = get_user_effort(chat_id)
    model_meta = SUPPORTED_MODELS.get(current_model, {
        "name": current_model,
        "badge": "Custom Engine",
        "description": "Custom model defined via environment configuration."
    })
    effort_meta = SUPPORTED_EFFORTS.get(current_effort, {})

    message_body = (
        f"🤖 **[SysClaw — AI Engine & Reasoning Config]**\n\n"
        f"🎯 **Active Engine:** `{current_model}`\n"
        f"🏷️ **Classification:** *{model_meta.get('badge', 'Standard')}*\n"
        f"🧠 **Reasoning Effort:** `{current_effort.upper()}` (*{effort_meta.get('name', current_effort)}*)\n"
        f"📋 **Profile:** {model_meta.get('description', '')}\n\n"
        f"💡 *Tap an engine or reasoning level below to switch dynamically:*"
    )

    # Send message with interactive inline keyboard attached
    _telegram.send_message(
        chat_id=chat_id,
        text=message_body,
        reply_markup=build_model_inline_keyboard(current_model, current_effort),
        parse_mode="Markdown"
    )
    return ""  # Response already dispatched via telegram channel

@register_action("set_model")
def handle_set_model_action(chat_id: str, callback_data: str) -> str:
    """
    Handles interactive callback when an operator clicks an inline model option.
    """
    parts = callback_data.split(":", 1)
    if len(parts) != 2:
        return "⚠️ [Error] Malformed model selection payload."

    selected_model = parts[1].strip()
    if not selected_model or selected_model not in SUPPORTED_MODELS:
        return f"⚠️ [Error] Model `{selected_model}` is not recognized."

    # Update active engine in RAM for this chat session
    set_user_model(chat_id, selected_model)
    effort = get_user_effort(chat_id)
    model_meta = SUPPORTED_MODELS.get(selected_model, {})
    model_name = model_meta.get("name", selected_model)
    badge = model_meta.get("badge", "Active")

    return (
        f"✅ **[AI Engine Switched Successfully]**\n\n"
        f"• **New Active Model:** `{selected_model}`\n"
        f"• **Designation:** {model_name} (*{badge}*)\n"
        f"• **Reasoning Effort:** `{effort.upper()}`\n"
        f"• **State:** Active. All subsequent conversations will run on this engine."
    )

@register_action("set_effort")
def handle_set_effort_action(chat_id: str, callback_data: str) -> str:
    """
    Handles interactive callback when an operator clicks an inline reasoning effort option.
    """
    parts = callback_data.split(":", 1)
    if len(parts) != 2:
        return "⚠️ [Error] Malformed reasoning effort payload."

    selected_effort = parts[1].strip().lower()
    if selected_effort not in SUPPORTED_EFFORTS:
        return f"⚠️ [Error] Reasoning effort `{selected_effort}` is not valid."

    set_user_effort(chat_id, selected_effort)
    model = get_user_model(chat_id)
    meta = SUPPORTED_EFFORTS[selected_effort]

    return (
        f"🧠 **[Reasoning Effort Updated]**\n\n"
        f"• **Active Model:** `{model}`\n"
        f"• **New Effort Level:** `{selected_effort.upper()}` ({meta['name']})\n"
        f"• **Behavior:** {meta['desc']}"
    )
