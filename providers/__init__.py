"""
SysClaw Modular AI Providers
"""

import importlib
from typing import Dict, Type
from .base import BaseAIProvider
from .deepseek import DeepSeekProvider

_PROVIDERS: Dict[str, Type[BaseAIProvider]] = {
    "deepseek": DeepSeekProvider
}

def register_ai_provider(name: str, provider_cls: Type[BaseAIProvider]):
    """Register a custom AI provider adapter."""
    _PROVIDERS[name.lower()] = provider_cls

def get_ai_provider(provider_name: str = "deepseek") -> BaseAIProvider:
    """Factory function to resolve and instantiate the chosen AI provider."""
    name = (provider_name or "deepseek").lower()
    
    if name in _PROVIDERS:
        return _PROVIDERS[name]()
    
    # Sanitize and validate module name before dynamic import
    if not name.replace("_", "").isalnum() or name.startswith("_"):
        return DeepSeekProvider()

    try:
        mod = importlib.import_module(f".{name}", __package__)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseAIProvider) and attr is not BaseAIProvider:
                _PROVIDERS[name] = attr
                return attr()
    except Exception:
        pass

    # Default fallback to DeepSeek
    return DeepSeekProvider()
