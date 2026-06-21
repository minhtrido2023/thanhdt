#!/usr/bin/env python3
"""ssh_kaffa.py — chạy lệnh trên server kaffa_v2 (trido@192.168.100.7) qua SSH/paramiko.

Shell ở local không tương tác + máy không có sshpass -> dùng paramiko để chạy lệnh
không cần gõ mật khẩu tay. Creds mặc định theo thông tin được cấp; có thể override
bằng biến môi trường KAFFA_SSH_HOST / KAFFA_SSH_USER / KAFFA_SSH_PASS.

Dùng:
    python ssh_kaffa.py "ls -la /workspace/kaffa_v2"
    python ssh_kaffa.py "cd /workspace/kaffa_v2 && git log --oneline -5"
    echo "lệnh" | python ssh_kaffa.py      # đọc lệnh từ stdin nếu không có arg
"""
import os, sys
import paramiko

HOST = os.environ.get("KAFFA_SSH_HOST", "192.168.100.7")
USER = os.environ.get("KAFFA_SSH_USER", "trido")
PASS = os.environ.get("KAFFA_SSH_PASS", "trido")
WORKDIR_REMOTE = "/workspace/kaffa_v2"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def run(cmd, timeout=120):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=22, username=USER, password=PASS,
              timeout=30, banner_timeout=30, auth_timeout=30,
              look_for_keys=False, allow_agent=False)
    try:
        si, so, se = c.exec_command(cmd, timeout=timeout)
        out = so.read().decode(errors="replace")
        err = se.read().decode(errors="replace")
        code = so.channel.recv_exit_status()
    finally:
        c.close()
    return code, out, err


def main():
    cmd = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else sys.stdin.read().strip()
    if not cmd:
        print("Cần truyền lệnh: python ssh_kaffa.py \"<command>\"")
        sys.exit(2)
    code, out, err = run(cmd)
    if out:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")
    if err.strip():
        sys.stderr.write("[stderr]\n" + err)
    sys.exit(code)


if __name__ == "__main__":
    main()
