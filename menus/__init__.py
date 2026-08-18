"""
SysClaw Modular Menu Auto-Discovery
Automatically imports and registers all menu definitions present in this package.
"""

import importlib
import pkgutil

# Auto-discover and import all valid modules inside the menus/ directory
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if not module_name.startswith("_") and module_name.replace("_", "").isalnum():
        try:
            importlib.import_module(f".{module_name}", __package__)
        except Exception:
            pass
