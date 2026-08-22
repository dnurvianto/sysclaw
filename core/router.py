"""
SysClaw Dispatcher & Router Engine
Coordinates between deterministic Menu buttons, Inline Actions, and AI LLM chat.
"""

from typing import Callable, Dict, List, Tuple, Union

# Registry collections
_MENU_ENTRIES: List[Dict] = []
_MENUS: Dict[str, Tuple[Callable, int]] = {}
_ACTIONS: Dict[str, Callable] = {}

def register_menu(label: Union[str, Callable], row: int = 1, prefix: str = None):
    """
    Decorator to register a custom deterministic menu button.
    `label` can be a static string (e.g. "🖥️ Host Overview") 
    or a dynamic function `label(chat_id) -> str` (e.g. lambda cid: f"⚡ AI Model: {get_user_model(cid)}").
    """
    def decorator(func: Callable):
        entry_prefix = prefix
        if isinstance(label, str):
            _MENUS[label] = (func, row)
            if not entry_prefix and ":" in label:
                entry_prefix = label.split(":")[0].strip()

        _MENU_ENTRIES.append({
            "label": label,
            "handler": func,
            "row": row,
            "prefix": entry_prefix
        })
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

def get_main_keyboard(chat_id: str = None) -> Dict:
    """
    Dynamically generates the Telegram reply keyboard grid from registered menus.
    Evaluates dynamic labels contextually for the given chat_id.
    """
    rows_dict: Dict[int, List[Dict[str, str]]] = {}
    
    for entry in _MENU_ENTRIES:
        label_val = entry["label"]
        if callable(label_val):
            try:
                button_text = label_val(chat_id)
            except Exception as e:
                print(f"[KEYBOARD ERROR] Dynamic label evaluation failed: {e}", flush=True)
                button_text = entry.get("prefix") or "Menu"
        else:
            button_text = str(label_val)

        row_idx = entry["row"]
        if row_idx not in rows_dict:
            rows_dict[row_idx] = []
        rows_dict[row_idx].append({"text": button_text})
    
    keyboard = [rows_dict[r] for r in sorted(rows_dict.keys())]
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": True
    }

def get_menu_handler(text: str) -> Callable:
    """Retrieve the menu handler if text matches a registered button."""
    text = (text or "").strip()
    if not text:
        return None

    # 1. Exact match in static dictionary
    if text in _MENUS:
        return _MENUS[text][0]

    # 2. Match entries with prefix (e.g. "⚡ AI Model: ...")
    for entry in _MENU_ENTRIES:
        prefix = entry.get("prefix")
        if prefix and text.startswith(prefix):
            return entry["handler"]
        if isinstance(entry["label"], str) and entry["label"] == text:
            return entry["handler"]

    return None

def get_action_handler(action_id: str) -> Callable:
    """Retrieve the action handler for a given callback_data."""
    # Matches exact action_id or prefix
    if action_id in _ACTIONS:
        return _ACTIONS[action_id]
    
    # Check for parameterized actions e.g. "reboot:server1" -> "reboot"
    prefix = action_id.split(":")[0]
    return _ACTIONS.get(prefix)
