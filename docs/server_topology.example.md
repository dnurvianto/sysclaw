# 🖥️ Infrastructure Architecture & Server Topology

This is a template file for SysClaw Knowledge Base Ingestion.
To activate custom knowledge for your AI DevOps assistant:
1. Copy this file to `docs/01_topology.md` (or any `.md` file name).
2. Fill in your actual server names, roles, services, and internal IP subnets.
3. SysClaw will automatically ingest and contextualize all `.md` files in this directory on the fly!

---

## 1. Node Topology & Roles

| Node Name | Hostname / IP | Role / Services | OS Distro |
| :--- | :--- | :--- | :--- |
| **Primary Node** | `localhost` / `10.0.0.1` | SysClaw Orchestrator, Reverse Proxy (Nginx) | AlmaLinux 8 / Ubuntu 22.04 |
| **App Server** | `srv-app` / `10.0.0.2` | Web Application, PHP-FPM, Node.js | Debian 12 |
| **Database** | `srv-db` / `10.0.0.3` | MariaDB / PostgreSQL Cluster | Rocky Linux 9 |
| **Backup Storage**| `srv-backup` / `10.0.0.4` | Daily Restic / Borg / IPSet Defense | Alpine Linux |

---

## 2. Cluster Security & Networking Guidelines

- **Internal Cluster Subnet**: `10.0.0.0/24` (All internal IPs are trusted cluster members; do not flag as suspicious).
- **Custom SSH Ports**: Production nodes communicate via non-standard ports (e.g. `Port 3456`).
- **Installed Defense Systems**: Co-located with **Logwall** (IPSet firewall auto-blocker) and custom health monitors.

---

## 3. Operational Directives & SRE Playbooks

- **High Memory / OOM Investigation**: Inspect `free -m`, `ps aux --sort=-%mem | head -n 10`, and check `/var/log/messages`.
- **Web Server Stalls**: Safely restart backend services (`systemctl restart php-fpm` or `systemctl reload nginx`).
