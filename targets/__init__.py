"""
SysClaw Modular Targets (Nodes)
"""

import importlib
from typing import Dict, Type
from .base import BaseTarget
from .local_host import LocalHostTarget

_TARGETS: Dict[str, Type[BaseTarget]] = {
    "localhost": LocalHostTarget,
    "local": LocalHostTarget
}

def register_target(name: str, target_cls: Type[BaseTarget]):
    """Register a custom target node adapter."""
    _TARGETS[name.lower()] = target_cls

def get_target_node(target_name: str = "localhost") -> BaseTarget:
    """Factory function to resolve and instantiate target execution environment."""
    name = (target_name or "localhost").lower()

    if name in _TARGETS:
        return _TARGETS[name]()

    # Sanitize and validate target name before dynamic import
    if not name.replace("_", "").isalnum() or name.startswith("_"):
        return LocalHostTarget()

    try:
        mod = importlib.import_module(f".{name}", __package__)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseTarget) and attr is not BaseTarget:
                _TARGETS[name] = attr
                return attr()
    except Exception:
        pass

    # Default fallback to LocalHost
    return LocalHostTarget()
