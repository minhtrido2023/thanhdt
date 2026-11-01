#!/usr/bin/env python3
"""Selfcheck nối khối 'Mã DD dưới vùng giá hợp lý' vào send_plan_report.sh (script THẬT, sandbox + --dry-run).
Ca: ZaloPay có khối | SpaceX KHÔNG | lệnh lỗi / rỗng / treo => report VẪN render + đúng 1 dòng cảnh báo."""
import json, os, subprocess, sys, tempfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.environ.get("SEND_PLAN_SCRIPT") or os.path.join(ROOT, "bin", "send_plan_report.sh")
MARK = "DDZONE_MARK_XYZ"
WARN = "Mã DD dưới vùng giá hợp lý: KHÔNG KIỂM ĐƯỢC"
res = []


def case(name, account, body, want_mark, want_warn, max_s=None):
    sb = tempfile.mkdtemp(prefix="ddzone_wire_")
    os.makedirs(f"{sb}/data/trade_plans")
    json.dump({"plan_date": "2026-08-11", "account": account, "state_name": "NEUTRAL",
               "orders": [{"ticker": "DPM", "side": "buy"}], "summary": {"action": "TRADE"},
               "requires_user_approval": True}, open(f"{sb}/data/trade_plans/plan_{account}_2026-08-11.json", "w"))
    cmd = f"{sb}/fake_ddz.py"
    open(cmd, "w").write(body)
    env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb, SEND_PLAN_MARKER_DIR=f"{sb}/markers",
               SEND_PLAN_DDZONE_CMD=cmd, SEND_PLAN_DDZONE_TIMEOUT="5")
    env.pop("SEND_PLAN_NOWCAST_CMD", None)
    t = time.time()
    p = subprocess.run(["bash", SCRIPT, "--account", account, "--dry-run", "--plan-date", "2026-08-11"],
                       capture_output=True, text=True, env=env, timeout=120)
    el = time.time() - t
    out = p.stdout
    ok = ((MARK in out) == want_mark) and ((out.count(WARN) == 1) == want_warn) and "DPM" in out
    if max_s is not None:
        ok = ok and el < max_s
    res.append((name, ok, f"{el:.1f}s mark={MARK in out} warn={out.count(WARN)}"))


OKC = f'import sys; assert sys.argv[1:] == ["run", "--report-block"], sys.argv; print("{MARK}"); print("dòng 2")\n'
case("ZaloPay: khối xuất hiện, gọi đúng 'run --report-block'", "ZaloPay", OKC, True, False)
case("SpaceX: KHÔNG có khối, không cảnh báo", "SpaceX", OKC, False, False)
case("ZaloPay: lệnh exit 1 => 1 dòng cảnh báo, report vẫn gửi", "ZaloPay",
     f'import sys; print("{MARK}"); print("boom", file=sys.stderr); raise SystemExit(1)\n', False, True)
case("ZaloPay: lệnh in rỗng => 1 dòng cảnh báo", "ZaloPay", "pass\n", False, True)
case("ZaloPay: lệnh treo => cắt theo timeout, 1 dòng cảnh báo", "ZaloPay",
     f'import time; time.sleep(60); print("{MARK}")\n', False, True, max_s=40)
for n, ok, info in res:
    print(("PASS " if ok else "FAIL ") + n + f"  [{info}]")
print(f"-- {sum(o for _, o, _ in res)}/{len(res)} PASS")
sys.exit(0 if all(o for _, o, _ in res) else 1)
