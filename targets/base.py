"""
SysClaw Abstract Base Target
Defines the contract for host and node targets (Localhost, SSH Multi-VPS, Docker, etc.).
"""

from typing import Dict, Any, List

class BaseTarget:
    """Universal interface for server nodes and target execution environments."""

    def get_os_info(self) -> str:
        """Retrieve OS name, distribution, and kernel version."""
        raise NotImplementedError

    def get_uptime(self) -> str:
        """Retrieve uptime duration string."""
        raise NotImplementedError

    def get_load_avg(self) -> str:
        """Retrieve CPU load average (1, 5, 15 min)."""
        raise NotImplementedError

    def get_memory_info(self) -> Dict[str, str]:
        """Retrieve RAM usage metrics (total, used, available)."""
        raise NotImplementedError

    def get_disk_info(self, path: str = "/") -> Dict[str, str]:
        """Retrieve disk space metrics (total, used, free, percent)."""
        raise NotImplementedError

    def exec_cmd(self, cmd: List[str], timeout: int = 10) -> str:
        """Safely execute a command on the target environment."""
        raise NotImplementedError
