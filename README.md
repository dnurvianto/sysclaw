<div align="center">

# 🐾 SysClaw
### *A Lean, Zero-DB Server Orchestrator & AI ChatOps Scaffold*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero-DB](https://img.shields.io/badge/Database-Zero--DB-orange.svg)]()
[![RAM](https://img.shields.io/badge/RAM-＜25MB-success.svg)]()
[![Linux](https://img.shields.io/badge/Platform-Universal%20Linux-lightgrey.svg?logo=linux&logoColor=white)](https://www.kernel.org/)

**Pocket SRE & ChatOps Command Center for Linux Servers & Modern DevOps.**

[Features](#-key-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Adding Menus](#-how-to-add-custom-menus) • [Pre-Flight Check](#-pre-flight-check) • [Deployment](#-systemd-daemon-deployment)

---

</div>

## 💡 Why SysClaw?

Modern AI agent frameworks (AutoGPT, CrewAI, OpenClaw) are often **too bloated, complex, and resource-heavy** for simple server monitoring. They burn thousands of tokens, consume hundreds of MBs of RAM, and introduce dangerous hallucination risks on production Linux boxes.

**`SysClaw`** is built on the philosophy of **Pragmatic Engineering**:
* ⚡ **Dual-Track Hybrid Model**:
  - **Track 1 (Fast & 0 Token)**: Instant deterministic metrics (<200ms) for Uptime, RAM, CPU Load, and Disk via Telegram reply buttons.
  - **Track 2 (Smart LLM)**: DeepSeek AI reasoning is only invoked for free-form troubleshooting, log analysis, and technical Q&A.
* 🪶 **Zero External Dependencies**: Pure Python 3 standard library. No `pip install` conflicts, no external database, no Redis.
* 🛡️ **Co-Located Server Safe**: Uses HTTP Long Polling (no open inbound ports) + systemd memory caps (`MemoryMax=64M`) so it never triggers OOM Killer or conflicts with Nginx/Apache.
* 🤖 **AI-Agent Ready**: Clean modular architecture designed so that developer tools like **Claude Code, Cursor, or Antigravity** can add new menus in 5 lines of code.

---

## 🏛️ Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                          BASE SYSTEM (Built-in)                         │
│                                                                         │
│  • Event Loop & HTTP Long Polling (No Inbound Port Binding)             │
│  • Security Guard (Strict Whitelist Chat ID & Silent Drop)              │
│  • Dispatcher Router (Menu Buttons vs Inline Actions vs AI Chat)        │
│  • Storage & Context Buffer (In-Memory RAM / Zero-Database)             │
└──────────────┬──────────────┬──────────────┬──────────────┬─────────────┘
               │              │              │              │
               ▼              ▼              ▼              ▼
          [ MODUL 1 ]    [ MODUL 2 ]    [ MODUL 3 ]    [ MODUL 4 ]
           AI PROVIDER      CHANNEL         MENUS         TARGETS
          (DeepSeek API)  (Telegram)    (Host Uptime)  (Local Host)
               │              │              │              │
          (Pluggable)    (Pluggable)    (Pluggable)    (Pluggable)
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/dnurvianto/sysclaw.git /opt/sysclaw
cd /opt/sysclaw
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```
Fill in your credentials:
```ini
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_CHAT_IDS=8279738173
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
AI_MODEL=deepseek-chat
```

### 3. Run Pre-Flight Diagnostic
```bash
bash preflight.sh
```

### 4. Start SysClaw
```bash
python3 bot.py
```

---

## 🔍 Pre-Flight Check

SysClaw comes with a built-in diagnostic tool to ensure your environment is 100% ready before launch:

```bash
bash preflight.sh
```

```text
=====================================================
 🐾 SysClaw Pre-Flight Diagnostic Check
=====================================================
[1/6] Checking Python 3 runtime... OK (v3.10.12)
[2/6] Checking outbound connection to Telegram API... OK (Port 443 Reachable)
[3/6] Checking outbound connection to DeepSeek API... OK (Port 443 Reachable)
[4/6] Checking available RAM memory... OK (3420 MB Available)
[5/6] Checking systemd service unit name 'sysclaw'... OK (Service unit name is clean and available)
[6/6] Checking .env configuration file... OK (.env detected)
=====================================================
🎉 RESULT: Server is 100% READY for SysClaw deployment!
```

---

## 🎛️ How to Add Custom Menus

Adding new buttons to SysClaw is as simple as creating a Python function with the `@register_menu` decorator in `menus/`:

```python
# menus/my_custom_menu.py
from core.router import register_menu
from targets.local_host import LocalHostTarget

@register_menu("🐳 Docker Status", row=2)
def handle_docker_status(chat_id: str) -> str:
    # Run a safe command on the host
    output = LocalHostTarget.exec_cmd(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"])
    return f"🐳 **Docker Containers:**\n```\n{output}\n```"
```

*When you ask Claude Code or Cursor: "Add a menu to check Docker containers", the AI will automatically create this file!*

---

## ⚙️ Systemd Daemon Deployment

To run SysClaw continuously in the background with auto-restart and memory safety limits:

```bash
# 1. Copy service unit to systemd directory
sudo cp systemd/sysclaw.service /etc/systemd/system/

# 2. Reload daemon and enable on boot
sudo systemctl daemon-reload
sudo systemctl enable --now sysclaw

# 3. Check status & live logs
sudo systemctl status sysclaw
sudo journalctl -u sysclaw -f
```

---

## 🛡️ Security Guardrails

1. **Zero-Trust Whitelist & Silent Drop**:
   Any Telegram user whose `Chat ID` is not in `ALLOWED_CHAT_IDS` is **silently ignored** without any response. No information is leaked to unauthorized probers.
2. **Safe Shell Execution**:
   All host commands are executed using parameterized argument lists (`subprocess.run(["cmd", "arg"])`), completely eliminating shell injection vulnerabilities.
3. **No Direct Autonomous Shell Access for LLM**:
   DeepSeek AI acts strictly as an **analyst/advisor**. Destructive actions require conscious confirmation via inline buttons.

---

## 🐧 Universal Multi-Distro Support

Tested and verified out-of-the-box on:
* **Debian / Ubuntu**: Debian 10, 11, 12 | Ubuntu 18.04, 20.04, 22.04, 24.04 LTS
* **Enterprise RHEL**: AlmaLinux 8/9 | Rocky Linux 8/9 | CentOS Stream & RHEL 7/8/9
* **Others**: Fedora, Arch Linux, openSUSE, Alpine Linux

---

## 💡 Real-World Use Case: Managing Logwall via SysClaw

While SysClaw is completely standalone and vendor-agnostic, its modular architecture makes it effortless to monitor and control server defense tools like **[Logwall](https://github.com/dnurvianto/logwall)** (Kernel & IPSet-level security blocker).

### Example Integration (`menus/logwall_status.py`):
```python
from core.router import register_menu
from targets.local_host import LocalHostTarget

@register_menu("🛡️ Logwall Status", row=2)
def handle_logwall_status(chat_id: str) -> str:
    # Query active blocked IPs from Logwall IPSet
    output = LocalHostTarget.exec_cmd(["ipset", "list", "BLACKLIST_SET", "-terse"])
    return f"🛡️ **[Logwall Defense Status]**\n```\n{output}\n```"
```

*SysClaw's auto-discovery automatically picks up this new file without touching any core code!*

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
