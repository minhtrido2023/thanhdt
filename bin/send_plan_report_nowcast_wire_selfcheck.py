#!/usr/bin/env python3
"""Selfcheck nối khối nowcast hàng hoá vào send_plan_report.sh (chạy script THẬT, sandbox + --dry-run).
Ca: ZaloPay có khối | SpaceX KHÔNG | lệnh nowcast lỗi / treo >20s / rỗng => report vẫn render, không khối."""
import json, os, subprocess, sys, tempfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.environ.get("SEND_PLAN_SCRIPT") or os.path.join(ROOT, "bin", "send_plan_report.sh")
MARK = "NOWCAST_MARK_XYZ"
res = []

def case(name, account, cmd_body, want_mark, want_report=True, max_s=None):
    sb = tempfile.mkdtemp(prefix="nowcast_wire_")
    os.makedirs(f"{sb}/data/trade_plans")
    json.dump({"plan_date": "2026-08-11", "account": account, "state_name": "NEUTRAL",
               "orders": [{"ticker": "DPM", "side": "buy"}], "summary": {"action": "TRADE"},
               "requires_user_approval": True}, open(f"{sb}/data/trade_plans/plan_{account}_2026-08-11.json", "w"))
    cmd = f"{sb}/fake_nowcast.py"
    open(cmd, "w").write(cmd_body)
    env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb, SEND_PLAN_MARKER_DIR=f"{sb}/markers", SEND_PLAN_NOWCAST_CMD=cmd)
    t = time.time()
    p = subprocess.run(["bash", SCRIPT, "--account", account, "--dry-run"], capture_output=True, text=True, env=env, timeout=120)
    dt = time.time() - t
    out = p.stdout
    ok = ((MARK in out) == want_mark) and ("DPM" in out or not want_report) and ("ESCALATE" not in out + p.stderr[:0])
    if max_s is not None:
        ok = ok and dt < max_s
    res.append((name, ok, f"{dt:.1f}s mark={MARK in out}"))

OKC = f'import sys; print("{MARK}"); print("dòng 2")\n'
case("ZaloPay: khối nowcast xuất hiện trong report", "ZaloPay", OKC, True)
case("SpaceX: KHÔNG có khối (investor-facing)", "SpaceX", OKC, False)
case("ZaloPay: lệnh nowcast exit 1 => report vẫn gửi, không khối", "ZaloPay", f'print("{MARK}"); raise SystemExit(1)\n', False)
case("ZaloPay: lệnh nowcast in rỗng => không khối", "ZaloPay", "pass\n", False)
case("ZaloPay: lệnh nowcast treo => bị cắt ~20s, report vẫn gửi", "ZaloPay", f'import time; time.sleep(60); print("{MARK}")\n', False, max_s=50)
for n, ok, info in res:
    print(("PASS " if ok else "FAIL ") + n + f"  [{info}]")
print(f"-- {sum(o for _, o, _ in res)}/{len(res)} PASS")
sys.exit(0 if all(o for _, o, _ in res) else 1)
