"""
SysClaw Local Host Target (Zero-Dependency & Optimized)
Executes safe system inspection and metric collection on the local server.
Prioritizes direct /proc/ virtual filesystem reads for maximum efficiency (Zero process spawning).
Cross-distro compatible (Ubuntu, Debian, AlmaLinux, Rocky, CentOS, Arch, Alpine).
"""

import os
import platform
import shutil
import subprocess
from typing import Dict, List
from .base import BaseTarget

class LocalHostTarget(BaseTarget):
    """Target Node implementation for the host machine running SysClaw."""

    _CACHED_OS_INFO: str = None

    @classmethod
    def get_os_info(cls) -> str:
        """Read and cache OS distribution name and version."""
        if cls._CACHED_OS_INFO is not None:
            return cls._CACHED_OS_INFO

        if os.path.isfile("/etc/os-release"):
            try:
                with open("/etc/os-release", "r", encoding="utf-8") as f:
                    data = {}
                    for line in f:
                        if "=" in line:
                            k, _, v = line.partition("=")
                            data[k.strip()] = v.strip().strip('"\'')
                    cls._CACHED_OS_INFO = data.get("PRETTY_NAME", f"{data.get('NAME', 'Linux')} {data.get('VERSION_ID', '')}")
                    return cls._CACHED_OS_INFO
            except Exception:
                pass
        
        cls._CACHED_OS_INFO = f"{platform.system()} {platform.release()}"
        return cls._CACHED_OS_INFO

    def get_uptime(self) -> str:
        """
        Get system uptime string.
        Optimized: Reads /proc/uptime directly first (0 subprocess spawn).
        """
        # Primary: Fast /proc/uptime read
        if os.path.isfile("/proc/uptime"):
            try:
                with open("/proc/uptime", "r") as f:
                    seconds = float(f.readline().split()[0])
                days = int(seconds // 86400)
                hours = int((seconds % 86400) // 3600)
                minutes = int((seconds % 3600) // 60)
                parts = []
                if days: parts.append(f"{days} days" if days > 1 else "1 day")
                if hours: parts.append(f"{hours} hours" if hours > 1 else "1 hour")
                parts.append(f"{minutes} mins" if minutes > 1 else f"{minutes} min")
                return "up " + ", ".join(parts)
            except Exception:
                pass

        # Fallback: 'uptime -p'
        try:
            res = subprocess.run(["uptime", "-p"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

        return f"up (platform: {platform.system()})"

    def get_load_avg(self) -> str:
        """
        Get 1, 5, 15 minute CPU load averages.
        Optimized: Reads /proc/loadavg directly first.
        """
        if os.path.isfile("/proc/loadavg"):
            try:
                with open("/proc/loadavg", "r") as f:
                    parts = f.read().split()[:3]
                    return ", ".join(parts)
            except Exception:
                pass

        if hasattr(os, "getloadavg"):
            try:
                l1, l5, l15 = os.getloadavg()
                return f"{l1:.2f}, {l5:.2f}, {l15:.2f}"
            except Exception:
                pass

        return "N/A"

    def get_memory_info(self) -> Dict[str, str]:
        """
        Get RAM usage summary.
        Optimized: Reads /proc/meminfo directly first (0 subprocess spawn).
        """
        # Primary: Fast /proc/meminfo read
        if os.path.isfile("/proc/meminfo"):
            try:
                mem_data = {}
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if ":" in line:
                            k, v = line.split(":", 1)
                            mem_data[k.strip()] = v.strip()
                total_kb = int(mem_data.get("MemTotal", "0 kB").split()[0])
                avail_kb = int(mem_data.get("MemAvailable", "0 kB").split()[0])
                used_kb = max(0, total_kb - avail_kb)
                return {
                    "total": f"{total_kb / 1024 / 1024:.1f} GB",
                    "used": f"{used_kb / 1024 / 1024:.1f} GB",
                    "available": f"{avail_kb / 1024 / 1024:.1f} GB"
                }
            except Exception:
                pass

        # Fallback: 'free -h'
        try:
            res = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout:
                lines = res.stdout.strip().split("\n")
                if len(lines) >= 2:
                    mem_parts = lines[1].split()
                    if len(mem_parts) >= 7:
                        return {
                            "total": mem_parts[1],
                            "used": mem_parts[2],
                            "available": mem_parts[6]
                        }
        except Exception:
            pass

        return {"total": "N/A", "used": "N/A", "available": "N/A"}

    def get_disk_info(self, path: str = "/") -> Dict[str, str]:
        """Get disk usage metrics for the given mount path."""
        try:
            usage = shutil.disk_usage(path)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent = (usage.used / usage.total) * 100
            return {
                "total": f"{total_gb:.1f} GB",
                "used": f"{used_gb:.1f} GB",
                "free": f"{free_gb:.1f} GB",
                "percent": f"{percent:.1f}%"
            }
        except Exception:
            return {"total": "N/A", "used": "N/A", "free": "N/A", "percent": "N/A"}

    def exec_cmd(self, cmd: List[str], timeout: int = 10) -> str:
        """
        Safely execute a command on the host using parameterized arguments (no shell=True).
        SECURITY WARNING: Never pass unsanitized user input directly into the cmd list.
        """
        if not cmd or not isinstance(cmd, list):
            return "⚠️ [Security Error] Command must be a valid argument list."

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            out = res.stdout if res.returncode == 0 else res.stderr
            return out.strip() or "[Empty Output]"
        except subprocess.TimeoutExpired:
            return f"⚠️ [Timeout] Command '{cmd[0]}' exceeded timeout limit of {timeout}s."
        except FileNotFoundError:
            return f"⚠️ [Not Found] Command '{cmd[0]}' was not found on the system."
        except Exception as e:
            return f"⚠️ [Error] {str(e)}"
