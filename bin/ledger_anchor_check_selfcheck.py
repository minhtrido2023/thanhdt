#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck ledger_anchor_check.py — CLI giả (stub), KHÔNG chạm data/ thật. Chạy: env -u TZ python3 ..."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "ledger_anchor_check.py")
A1 = "SEAL_MD5 SpaceX " + "a" * 32 + " " + "b" * 32
A2 = "SEAL_MD5 SpaceX " + "c" * 32 + " " + "d" * 32
fails = []


def run(anchors_text, cli_body, tag):
    with tempfile.TemporaryDirectory() as d:
        ap, cp = os.path.join(d, "anchors.txt"), os.path.join(d, "cli.py")
        if anchors_text is not None:
            open(ap, "w").write(anchors_text)
        open(cp, "w").write(cli_body)
        env = dict(os.environ, LEDGER_ANCHORS_FILE=ap, NAV_UNIT_LEDGER_CLI=cp, LEDGER_DIR=d)
        r = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr


def check(name, cond):
    print(("  OK  " if cond else "  FAIL ") + name)
    if not cond:
        fails.append(name)


OK_CLI = "import sys; print('khop'); sys.exit(0)"
BAD_CLI = "import sys; print('AnchorError'); sys.exit(2)"
ECHO_CLI = "import sys; print(sys.argv[-1]); sys.exit(0)"

rc, out = run(A1 + "\n", OK_CLI, "ok")
check("mốc khớp ⇒ rc=0", rc == 0 and "OK SpaceX" in out)
rc, out = run(A1 + "\n", BAD_CLI, "bad")
check("CLI từ chối ⇒ rc=1 + LỆCH", rc == 1 and "LỆCH SpaceX" in out)
rc, out = run("# chỉ chú thích\n", OK_CLI, "empty")
check("không có dòng SEAL_MD5 ⇒ rc=3", rc == 3)
rc, out = run(None, OK_CLI, "missing")
check("thiếu file mốc ⇒ rc=3", rc == 3)
rc, out = run(A1 + "\n" + A2 + "\n", ECHO_CLI, "latest")
check("dùng mốc MỚI NHẤT (dòng sau đè dòng trước)", rc == 0 and ("c" * 32) in out and ("a" * 32) not in out)
rc, out = run("SEAL_MD5 SpaceX " + "a" * 31 + " " + "b" * 32 + "\n", OK_CLI, "malformed")
check("dòng hỏng md5 ⇒ bị bỏ ⇒ rc=3 (không đoán)", rc == 3)
print("PASS" if not fails else f"FAIL {len(fails)}: {fails}")
sys.exit(1 if fails else 0)
