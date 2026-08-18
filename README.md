<div align="center">

# 🐾 SysClaw
### *A Lean, Zero-DB Server Orchestrator & AI ChatOps Scaffold*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero-DB](https://img.shields.io/badge/Database-Zero--DB-orange.svg)]()
[![RAM](https://img.shields.io/badge/RAM-＜25MB-success.svg)]()
[![Linux](https://img.shields.io/badge/Platform-Universal%20Linux-lightgrey.svg?logo=linux&logoColor=white)](https://www.kernel.org/)

**Pocket SRE & ChatOps Command Center for Linux Servers & Modern DevOps.**

[Why SysClaw?](#-why-sysclaw) • [Architecture](#-architecture--modularity) • [Quick Start](#-quick-start) • [CLI Utility](#-sysclaw-cli-utility) • [Knowledge Base](#-dynamic-knowledge-base-docs) • [AI Models](#-dynamic-ai-models--multi-tier-engines) • [Adding Menus](#-how-to-add-custom-menus) • [Extending SysClaw](#-pluggable-architecture-extending-sysclaw) • [Upgrade Guide](#-safe-customization--seamless-upgrades) • [Best Practices](#-security-best-practice-dedicated-management-node-stealth-mode) • [Disclaimer](#-security-notice--prudent-usage-disclaimer)

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

## 🏛️ Architecture & Modularity

SysClaw is designed with a strict **Decoupled Architecture**: the core kernel is completely agnostic, while DeepSeek and Telegram are provided as ready-to-use **Default Adapters**.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        SYSCLAW CORE KERNEL                              │
│                                                                         │
│  • Event Loop & HTTP Long Polling Engine (0 open inbound ports)         │
│  • Security Gatekeeper (Strict Whitelist Chat ID & Silent Drop)         │
│  • Dispatcher Router (Menu Grid vs Inline Actions vs AI Inquiries)      │
│  • In-Memory Context Buffer (Zero-DB RAM sliding window)                │
│  • Dynamic Knowledge Ingestion Engine (Auto-reads docs/*.md)            │
└──────────────┬──────────────┬──────────────┬──────────────┬─────────────┘
               │              │              │              │
               ▼              ▼              ▼              ▼
     [ DEFAULT ADAPTER 1 ] [ DEFAULT ADAPTER 2 ] [ MODULAR MENUS ] [ MODULAR TARGETS ]
         AI PROVIDER            CHANNEL            MENUS           TARGET NODES
     providers/deepseek.py  channels/telegram.py  menus/*.py       targets/*.py
       (DeepSeek API)        (Telegram Bot)      (Host Health)    (Local & SSH)
               │              │              │              │
          (Swappable)    (Swappable)    (Extensible)   (Extensible)
```

### Core Kernel vs Pluggable Layer:
* **`core/` (Agnostic Core)**: Contains universal logic (`security.py`, `memory.py`, `router.py`, `knowledge.py`). It does not hardcode DeepSeek or Telegram dependencies.
* **`providers/deepseek.py` (Default AI Adapter)**: Pre-configured out-of-the-box AI provider. Easily swapped with local Ollama, Claude, or OpenAI.
* **`channels/telegram.py` (Default Chat Adapter)**: Pre-configured communication channel. Easily augmented with WhatsApp or Webhooks.

---

## 🚀 Quick Start

> ℹ️ **Default State**: After cloning/installing, SysClaw is completely **OFF / Inactive** (0 running processes). It will only start after you configure credentials and explicitly invoke the CLI.

### 1. Clone & Enable CLI
```bash
git clone https://github.com/dnurvianto/sysclaw.git /opt/sysclaw
cd /opt/sysclaw
sudo ln -sf /opt/sysclaw/sysclaw /usr/local/bin/sysclaw
sudo chmod +x /opt/sysclaw/sysclaw
```

### 2. Configure Credentials (`.env`)
```bash
cp .env.example .env
nano .env
```
Fill in your credentials:
```ini
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_CHAT_IDS=8279738173
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
AI_MODEL=deepseek-v4-flash
```

### 3. Test Environment Readiness
```bash
sysclaw test
```

### 4. Turn ON Daemon (Systemd Background Service)
```bash
sudo sysclaw install-service
sudo sysclaw start
```

### 5. Verify & Inspect
```bash
sysclaw status
sysclaw logs -f
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

*When you ask Claude Code, Cursor, or Antigravity: "Add a menu to check Docker containers", the AI will automatically create this file!*

---

## 🔌 Pluggable Architecture: Extending SysClaw

SysClaw is architected for zero-bloat extensibility. Developers and AI agents can extend any layer using pure Python standard library:

### 1. Adding Custom AI Providers (`providers/`)
Create a new provider adapter by inheriting from `BaseAIProvider`:
```python
# providers/ollama.py
import json, urllib.request
from typing import List, Dict
from .base import BaseAIProvider

class OllamaProvider(BaseAIProvider):
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.api_url = "http://127.0.0.1:11434/api/chat"

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = "", model: str = None) -> str:
        payload = {"model": model or self.model, "messages": messages, "stream": False}
        req = urllib.request.Request(self.api_url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())["message"]["content"]
```
*Register your provider in `providers/__init__.py` to enable switching via `AI_PROVIDER=ollama` in `.env`.*

### 2. Adding Custom Target Nodes (`targets/`)
Create new execution targets (e.g., Remote SSH Cluster, Docker Containers) by inheriting from `BaseTarget`:
```python
# targets/remote_ssh.py
from typing import List, Dict
from .base import BaseTarget
from .local_host import LocalHostTarget

class SSHNodeTarget(BaseTarget):
    def __init__(self, host_alias: str):
        self.host_alias = host_alias

    def exec_cmd(self, cmd: List[str], timeout: int = 15) -> str:
        # Secure parameterized SSH invocation (Zero shell injection)
        ssh_args = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", self.host_alias] + cmd
        return LocalHostTarget.exec_cmd(ssh_args, timeout=timeout)
```

### 3. Adding Custom Notification Channels (`channels/`)
Implement alternative delivery channels (WhatsApp, Webhooks, Discord, Slack) by inheriting from `BaseChannel` in `channels/base.py`.

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

## 💻 SysClaw CLI Utility

SysClaw includes a zero-dependency CLI wrapper to easily control the background daemon, inspect logs, and run diagnostics without memorizing raw systemd commands.

### Enable Global CLI Access
```bash
sudo ln -sf /opt/sysclaw/sysclaw /usr/local/bin/sysclaw
sudo chmod +x /opt/sysclaw/sysclaw
```

### CLI Command Reference
| Command | Description |
| :--- | :--- |
| `sysclaw status` | Display service status, PID, and memory footprint |
| `sysclaw start` | Start the SysClaw background daemon |
| `sysclaw stop` | Gracefully stop the running daemon |
| `sysclaw restart` | Restart SysClaw service |
| `sysclaw logs -f` | Stream live real-time service logs |
| `sysclaw test` / `doctor` | Run pre-flight environment & API diagnostics |
| `sysclaw install-service` | Install and enable the systemd unit automatically |
| `sysclaw uninstall` | Stop daemon and completely remove systemd unit & CLI symlinks |
| `sysclaw version` | Show current SysClaw version (`v1.2.0`) |
| `sysclaw help` | Display available CLI commands |

---

## 🧠 Dynamic Knowledge Base (`docs/`)

SysClaw features an **autonomous Domain Knowledge Ingestion Engine** that bridges server-specific operational context directly to the AI reasoning model without fine-tuning or code changes.

### How It Works
1. Place any Markdown file (`.md`) inside the `docs/` directory:
   ```bash
   cp docs/server_topology.example.md docs/01_topology.md
   nano docs/01_topology.md
   ```
2. SysClaw automatically reads, parses, and injects all active `.md` documents into the AI system prompt on the fly.
3. Use it to feed:
   - 🗺️ **Node Topology**: Cluster server lists, public/internal IPs, custom SSH ports.
   - 📘 **SRE Playbooks & SOPs**: Step-by-step procedures for handling high memory, Nginx stalls, or backup rotations.
   - 🛡️ **Firewall & Security Policies**: Whitelisted subnets and Logwall blocker configurations.
   - 🗄️ **Database & Cron Schedules**: Critical cron timings and maintenance guidelines.

*Guardrail Protection: The ingestion engine includes an automatic 50,000-character safety ceiling to prevent token window overflow.*

---

## 🤖 Dynamic AI Models & Multi-Tier Engines

Operators can dynamically toggle between inference engines directly in Telegram via the interactive `⚡ Model AI` menu button without restarting the daemon:

| Tier / Model ID | Best For | Characteristics |
| :--- | :--- | :--- |
| **⚡ `deepseek-v4-flash`** | High Throughput / Routine DevOps | Sub-second latency (<500ms), lightweight token burn, quick configuration & log checks |
| **🔬 `deepseek-v4-pro`** | Deep Reasoning / Incident SRE | High-capacity problem solving, intricate multi-step diagnostics, root-cause forensics |

---

## 🛡️ Security Guardrails (Defense-in-Depth)

SysClaw is engineered specifically for production Linux environments, enforcing a 4-layer defense-in-depth security model:

1. **Zero-Trust Whitelist & Silent Drop**:
   - Any Telegram message or callback from a `Chat ID` not listed in `ALLOWED_CHAT_IDS` is **silently dropped** at Layer 1.
   - Zero information is leaked to unauthorized probers (no error replies, no metadata leakage).

2. **Human-in-the-Loop Conscious Consent**:
   - DeepSeek AI **never possesses autonomous direct shell privileges**.
   - Recommended actions are presented as clear, transparent command proposals requiring conscious approval via interactive inline buttons (`✅ Confirm Execution` / `❌ Cancel`).

3. **Hardened Destructive Command Guardrails**:
   - Catastrophic and irreversible commands (e.g., `rm -rf /`, `mkfs`, `dd if=/dev/zero`, unconditional disk writes, `chmod -R 777 /`) are intercepted and rejected by safety guardrails.

4. **Parameterized Execution & Isolated Timeouts**:
   - Host commands execute strictly via parameterized argument lists (`subprocess.run(["cmd", "arg"])`), completely eliminating shell injection vulnerabilities.
   - Enforced sub-process execution timeouts (default 10s–15s) and systemd memory caps (`MemoryMax=64M`) prevent resource exhaustion or frozen worker threads.

---

## 🐧 Universal Multi-Distro Support

Tested and verified out-of-the-box on:
* **Debian / Ubuntu**: Debian 10, 11, 12 | Ubuntu 18.04, 20.04, 22.04, 24.04 LTS
* **Enterprise RHEL**: AlmaLinux 8/9 | Rocky Linux 8/9 | CentOS Stream & RHEL 7/8/9
* **Others**: Fedora, Arch Linux, openSUSE, Alpine Linux

## 🧱 Safe Customization & Seamless Upgrades

SysClaw is engineered so that operators and AI agents can safely add custom menus, domain knowledge, and adapters without fear of losing custom code when updating the core framework from upstream.

### 🛡️ The 3 Zero-Conflict Customization Zones:
| Safe Zone | Location | How to Use | Why It Never Conflicts with `git pull` |
| :--- | :--- | :--- | :--- |
| **Custom Menus** | `menus/*.py` | Create new `.py` files with `@register_menu` | Auto-discovery loads new files dynamically; upstream `git pull` will not touch new user files. |
| **Knowledge Base** | `docs/*.md` | Drop SOPs, cluster topology, or runbooks | Auto-ingested by `core/knowledge.py` without modifying code. |
| **Secrets & Keys** | `.env` | Configure tokens and credentials | Permanently ignored by `.gitignore`. |

### Recommended Upgrade Workflow:
Whenever upstream releases new core features or optimizations, simply run:
```bash
cd /opt/sysclaw
git pull origin main
sudo sysclaw restart
```

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

## 💡 Security Best Practice: Dedicated Management Node (Stealth Mode)

For high-security production environments, deploying SysClaw on a **Dedicated Lightweight VPS (512MB–1GB RAM)** turns it into an isolated, tamper-proof **Management Appliance / SRE Command Center**:

### 🥷 1. Total Stealth Mode (Zero Open Inbound Ports)
Because SysClaw operates exclusively via **outbound HTTP Long Polling** to Telegram and AI APIs over TLS port 443, your server requires **ZERO open inbound web/listening ports**:
* No Nginx, Apache, or web server open to the public internet.
* Internet scanners (Shodan, Censys, botnets) will detect 0 open ports (Complete Drop).

### 🛡️ 2. Ultra-Simple 3-Line Firewall (UFW / Iptables)
You can lock down the host with a simple default-deny policy:
```bash
# Block all inbound traffic by default
sudo ufw default deny incoming

# Allow outbound API polling (Telegram & DeepSeek)
sudo ufw default allow outgoing

# Restrict SSH access strictly to your management IP / VPN
sudo ufw allow from YOUR_ADMIN_IP to any port 22 proto tcp
sudo ufw enable
```

### 🚫 3. Zero Lateral Movement Risk
Without web apps (PHP, WordPress, Node.js) or databases running on the same host, the server is completely immune to web-based remote code execution (RCE) or lateral privilege escalation.

---

## ⚠️ Security Notice & Prudent Usage Disclaimer

SysClaw is provided as an open-source server orchestration and ChatOps scaffold designed for system administrators, SREs, and DevOps practitioners.

* 🔍 **Audit & Review Code Wisely**: Users and organizations are strongly encouraged to thoroughly review, audit, and understand the source code and security guardrails before deploying to mission-critical or production environments.
* 🔄 **Routine Self-Audits**: Always conduct regular independent audits and periodic reviews of your deployed configurations, custom menus, system journals, and access whitelists to maintain continuous operational integrity.
* ⚖️ **Operator Responsibility**: The decision to adopt, deploy, and authorize command execution via SysClaw rests entirely with the individual operator. Users assume full responsibility for their server access rules, firewall policies, and operational outcomes.
* 🛡️ **Principle of Least Privilege**: Always enforce strict access controls, secure your credentials (`.env`), restrict whitelisted Chat IDs, and apply the principle of least privilege across all connected nodes.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.
