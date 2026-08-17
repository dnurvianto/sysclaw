"""
SysClaw Modular Targets (Nodes)
"""

from .base import BaseTarget
from .local_host import LocalHostTarget

def get_target_node(target_name: str = "localhost") -> BaseTarget:
    """Factory function to resolve and instantiate target execution environment."""
    name = (target_name or "localhost").lower()
    if name in ("localhost", "local"):
        return LocalHostTarget()
    return LocalHostTarget()
