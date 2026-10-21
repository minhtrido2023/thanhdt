#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho `fund_bench_cron.sh` (N-c vòng 2): NOTIFY_CMD = stub ghi file, không gửi Discord.

    env -u TZ python3 mike/bin/fund_bench_cron_selfcheck.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, "fund_bench_cron.sh")
N_OK = 0


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def run(cmd, stub_rc=0):
    d = tempfile.mkdtemp(prefix="fbc_")
    sent = os.path.join(d, "sent.txt")
    stub = os.path.join(d, "stub.sh")
    with open(stub, "w") as f:
        f.write(f'#!/usr/bin/env bash\nprintf "%s\\n--ch=%s\\n" "$1" "$2" >> "{sent}"\nexit {stub_rc}\n')
    os.chmod(stub, 0o755)
    env = dict(os.environ, NOTIFY_CMD=stub)
    p = subprocess.run(["bash", SH, "vnindex_tr_update", "bash", "-c", cmd], capture_output=True, text=True,
                       env=env)
    msg = open(sent).read() if os.path.exists(sent) else ""
    return p.returncode, p.stdout, p.stderr, msg


def main() -> int:
    rc, out, _, msg = run("echo dựng xong; exit 0")
    ok(rc == 0 and "dựng xong" in out and msg == "", f"rc=0 ⇒ im lặng, đầu ra vẫn ra log: {rc} {msg!r}")

    rc, out, _, msg = run("for i in $(seq 1 12); do echo dòng$i; done; echo 'BuildRefused: BQ thiếu 2026-10-13' >&2; exit 2")
    ok(rc == 2, f"giữ rc của lệnh: {rc}")
    ok("rc=2" in msg and "vnindex_tr_update" in msg and "BuildRefused: BQ thiếu 2026-10-13" in msg
       and "--ch=trading_daily" in msg, f"rc≠0 ⇒ báo Trading Daily kèm bằng chứng thật:\n{msg}")
    ok("dòng12" in msg and "dòng4\n" not in msg, "chỉ 8 dòng cuối")
    ok("BuildRefused" in out, "stderr của lệnh vẫn vào log")

    rc, _, _, msg = run("exit 3")
    ok(rc == 3 and "rc=3" in msg and "(lệnh không in gì)" in msg, f"rc=3 không đầu ra: {msg!r}")

    rc, _, _, msg = run("echo '{\"n\": 1}'; echo '📋 Bảng sàn HOSE 2030-01-05 → 2030-01-12: vào [X]; ra —'")
    ok(rc == 0 and msg.startswith("📋 Bảng sàn HOSE") and "{" not in msg, f"rc=0 + diff ⇒ chỉ chuyển dòng 📋: {msg!r}")

    sb = ('{"changed": true, "seal_blocked": [{"date": "2026-10-14", "errors": ["G4: 2026-10-14 vốn hoá rổ đổi '
          '+5.00%"]}], "last": "2026-10-20"}')
    rc, _, _, msg = run(f"echo '{sb}'")
    ok(rc == 0 and "seal bị chặn" in msg and "2026-10-14" in msg and "G4: 2026-10-14" in msg
       and "--ch=trading_daily" in msg, f"rc=0 + seal_blocked ⇒ báo Trading Daily kèm bằng chứng: {msg!r}")
    rc, _, _, msg = run("echo '{\"changed\": true, \"bytes\": 10}'")
    ok(rc == 0 and msg == "", f"rc=0 không seal_blocked ⇒ im lặng: {msg!r}")

    rc, _, err, _ = run("exit 1", stub_rc=1)
    ok(rc == 1 and "NOTIFY_FAILED" in err, f"gửi lỗi ⇒ NOTIFY_FAILED, rc vẫn của lệnh: {rc} {err!r}")

    p = subprocess.run(["bash", SH, "chỉ-tên"], capture_output=True, text=True)
    ok(p.returncode == 64, "thiếu lệnh ⇒ rc=64")
    print(f"OK — {N_OK} assertion PASS (fund_bench_cron_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
