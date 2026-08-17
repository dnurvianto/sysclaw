"""
SysClaw Dispatcher & Router Engine
Coordinates between deterministic Menu buttons, Inline Actions, and AI LLM chat.
"""

from typing import Callable, Dict, List, Tuple

# Registry collections
# _MENUS: { button_text: (handler_func, row_index) }
_MENUS: Dict[str, Tuple[Callable, int]] = {}

# _ACTIONS: { action_name: handler_func }
_ACTIONS: Dict[str, Callable] = {}

def register_menu(button_text: str, row: int = 1):
    """
    Decorator to register a custom deterministic menu button.
    Example:
        @register_menu("⏱️ Uptime Host", row=1)
        def handle_uptime(chat_id):
            return "Uptime is 14 days"
    """
    def decorator(func: Callable):
        _MENUS[button_text] = (func, row)
        return func
    return decorator

def register_action(action_id: str):
    """
    Decorator to register an inline keyboard action handler.
    Example:
        @register_action("confirm_reboot")
        def handle_reboot(chat_id, callback_data):
            return "System is rebooting..."
    """
    def decorator(func: Callable):
        _ACTIONS[action_id] = func
        return func
    return decorator

def get_main_keyboard() -> Dict:
    """
    Dynamically generates the Telegram reply keyboard grid from registered menus.
    """
    rows_dict: Dict[int, List[Dict[str, str]]] = {}
    
    for button_text, (_, row_idx) in _MENUS.items():
        if row_idx not in rows_dict:
            rows_dict[row_idx] = []
        rows_dict[row_idx].append({"text": button_text})
    
    keyboard = [rows_dict[r] for r in sorted(rows_dict.keys())]
    
    # Add a default helper row at the bottom if not empty
    return {
        "keyboard": keyboard,
        "resize_keyboard": True
    }

def get_menu_handler(text: str) -> Callable:
    """Retrieve the menu handler if text matches a registered button."""
    item = _MENUS.get(text)
    return item[0] if item else None

def get_action_handler(action_id: str) -> Callable:
    """Retrieve the action handler for a given callback_data."""
    # Matches exact action_id or prefix
    if action_id in _ACTIONS:
        return _ACTIONS[action_id]
    
    # Check for parameterized actions e.g. "reboot:server1" -> "reboot"
    prefix = action_id.split(":")[0]
    return _ACTIONS.get(prefix)
