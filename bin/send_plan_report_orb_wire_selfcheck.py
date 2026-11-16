#!/usr/bin/env python3
"""Selfcheck nối khối 'ORB futures sleeve' vào send_plan_report.sh (script THẬT, sandbox + --dry-run).
Ca: SpaceX có khối | ZaloPay KHÔNG | lệnh lỗi / rỗng / treo => report VẪN render + đúng 1 dòng cảnh báo.
Job Taylor_20261116_162132."""
import json, os, stat, subprocess, sys, tempfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.environ.get("SEND_PLAN_SCRIPT") or os.path.join(ROOT, "bin", "send_plan_report.sh")
MARK = "ORB_MARK_XYZ"
WARN = "ORB futures sleeve: KHÔNG KIỂM ĐƯỢC"
res = []


def case(name, account, body, want_mark, want_warn, max_s=None):
    sb = tempfile.mkdtemp(prefix="orb_wire_")
    os.makedirs(f"{sb}/data/trade_plans")
    json.dump({"plan_date": "2026-08-11", "account": account, "state_name": "NEUTRAL",
               "orders": [{"ticker": "DPM", "side": "buy"}], "summary": {"action": "TRADE"},
               "requires_user_approval": True}, open(f"{sb}/data/trade_plans/plan_{account}_2026-08-11.json", "w"))
    cmd = f"{sb}/fake_orb"
    open(cmd, "w").write("#!/usr/bin/env python3\n" + body)
    os.chmod(cmd, os.stat(cmd).st_mode | stat.S_IXUSR)
    env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb, SEND_PLAN_MARKER_DIR=f"{sb}/markers",
               SEND_PLAN_ORB_CMD=cmd, SEND_PLAN_ORB_TIMEOUT="5")
    for k in ("SEND_PLAN_NOWCAST_CMD", "SEND_PLAN_DDZONE_CMD"):
        env.pop(k, None)
    t = time.time()
    p = subprocess.run(["bash", SCRIPT, "--account", account, "--dry-run", "--plan-date", "2026-08-11"],
                       capture_output=True, text=True, env=env, timeout=120)
    el = time.time() - t
    out = p.stdout
    ok = ((MARK in out) == want_mark) and ((out.count(WARN) == 1) == want_warn) and "DPM" in out
    if max_s is not None:
        ok = ok and el < max_s
    res.append((name, ok, f"{el:.1f}s mark={MARK in out} warn={out.count(WARN)} rc={p.returncode}"))


OKC = f'print("{MARK}"); print("dòng 2")\n'
case("SpaceX: khối xuất hiện", "SpaceX", OKC, True, False)
case("ZaloPay: KHÔNG có khối, không cảnh báo", "ZaloPay", OKC, False, False)
case("SpaceX: lệnh exit 1 => 1 dòng cảnh báo, report vẫn gửi", "SpaceX",
     f'import sys; print("{MARK}"); print("boom", file=sys.stderr); raise SystemExit(1)\n', False, True)
case("SpaceX: lệnh in rỗng => 1 dòng cảnh báo", "SpaceX", "pass\n", False, True)
case("SpaceX: lệnh treo => cắt theo timeout, 1 dòng cảnh báo", "SpaceX",
     f'import time; time.sleep(60); print("{MARK}")\n', False, True, max_s=40)
for n, ok, info in res:
    print(("PASS " if ok else "FAIL ") + n + f"  [{info}]")
print(f"-- {sum(o for _, o, _ in res)}/{len(res)} PASS")
sys.exit(0 if all(o for _, o, _ in res) else 1)
