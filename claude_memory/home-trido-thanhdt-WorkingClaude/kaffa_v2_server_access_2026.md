---
name: kaffa-v2-server-access-2026
description: Cách SSH vào server kaffa_v2 (trido@192.168.100.7) + helper paramiko ssh_kaffa.py
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3610ea38-a57f-4356-8567-36b7b6105fa5
---

Server làm việc kaffa_v2: **trido@192.168.100.7** (host `sgms`, Linux Proxmox PVE 6.2). Dir đích `/workspace/kaffa_v2` (codebase quant/trading khác, owner `hainguyen`; có CLAUDE.md/AGENTS.md/bigquery_dictionary.json/config.json/core_utils/deeplearning).

**Mạng:** máy local KHÔNG cùng dải (Wi-Fi 192.168.1.x, VPN 10.8.x); tới 192.168.100.7 qua gateway 192.168.1.1 (route mặc định) — trễ cao (~600ms lúc đầu) nhưng ổn định. Ping ICMP timeout, nhưng cổng 22 mở (banner OpenSSH 8.9p1 Ubuntu).

**Kết nối:** shell local KHÔNG tương tác + không có sshpass → dùng **paramiko** (đã `pip install paramiko`, v5.0.0). Helper `ssh_kaffa.py` ở WORKDIR local:
- `python ssh_kaffa.py "cd /workspace/kaffa_v2 && <lệnh>"` — relay stdout/stderr/exit-code; password mặc định trong file, override qua env KAFFA_SSH_HOST/USER/PASS.

**Gotcha:** repo /workspace/kaffa_v2 owner=hainguyen, login=trido → git báo *dubious ownership* (exit 128). Fix 1 lần: `git config --global --add safe.directory /workspace/kaffa_v2`.

**Claude Code ([REDACTED]15):** đã cài trên server bằng native installer (`curl -fsSL https://claude.ai/install.sh | bash`) — v2.1.177 tại `~/.local/bin/claude`, PATH sẵn qua ~/.profile. Dùng native (KHÔNG npm) vì node server = v12.22.9 (quá cũ, cần 18+); binary độc lập nên không sao. Lần đầu cần auth (OAuth dán-code trong phiên tương tác, hoặc export ANTHROPIC_API_KEY). Server Ubuntu 22.04.4 có internet ra ngoài.
