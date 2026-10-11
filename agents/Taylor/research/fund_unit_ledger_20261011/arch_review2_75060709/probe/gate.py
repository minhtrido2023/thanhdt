import sys, os, json, subprocess, pathlib
WC = pathlib.Path("/tmp/ar2/g/WC"); FP = WC / "data" / "account_cash_flows.json"
ORIG = FP.read_text()
env = {k: v for k, v in os.environ.items() if k not in ("TZ", "WC_ROOT", "MIKE_ROOT", "ACCOUNT_CASH_FLOWS_PATH")}
def cli():
    p = subprocess.run([sys.executable, "bin/nav_period_returns.py", "--account", "SpaceX", "--report-date", "2026-10-09"], cwd=WC / "mike", capture_output=True, text=True, env=env)
    try: inc = json.loads(p.stdout)["inception"]["return_pct"]
    except Exception: inc = None
    return p.returncode, inc, p.stderr.strip().splitlines()[-1][:170] if p.stderr.strip() else ""
def gate(pct_text):
    report = pathlib.Path("/tmp/ar2/g/SpaceX_weekly_report_2026-10-05_to_2026-10-09.md")
    report.write_text(f"### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | {pct_text} | x | y |\n", encoding="utf-8")
    code = ("import sys, pathlib; sys.path.insert(0, 'bin'); import report_delivery_gate as g\n"
            "assert str(g.ROOT) == '/tmp/ar2/g/WC/mike', g.ROOT\n"
            "for fn in (g._check_period_returns, g._check_nav_flow_records):\n"
            "    try:\n        fn(pathlib.Path(sys.argv[1])); print(fn.__name__ + ': PASS')\n"
            "    except RuntimeError as exc:\n        print(fn.__name__ + ': BLOCK ' + str(exc)[:160].replace('\\n', ' '))\n")
    p = subprocess.run([sys.executable, "-c", code, str(report)], cwd=WC / "mike", capture_output=True, text=True, env=env)
    warn = [l for l in p.stderr.splitlines() if "WARN" in l]
    return p.stdout.strip().replace("\n", " || ") + (" || " + warn[0][:150] if warn else "") + ((" || STDERR " + p.stderr[-200:]) if p.returncode else "")
def trial(label, flows=None, raw=None, remove=False):
    if remove: FP.unlink()
    elif raw is not None: FP.write_text(raw)
    else: FP.write_text(json.dumps({"SpaceX": flows, "ZaloPay": []}))
    rc, inc, err = cli()
    print(f"### {label}\n   CLI rc={rc} inception={inc} {('| ' + err) if err else ''}\n   báo cáo ghi +9,99% (SAI): {gate('+9,99%')}")
    FP.write_text(ORIG)
G = {"kind": "deposit", "evidence": "x"}
trial("0. không dòng tiền", [])
trial("1. bản ghi thiếu time_ict", [dict(G, date="2026-10-05", amount_vnd=5e7)])
trial("2. flow trong cửa sổ dòng 08-24 chụp 04:49", [dict(G, date="2026-08-24", time_ict="16:00", amount_vnd=5e7)])
trial("3. rút 2 tỷ (> NAV) 10:00 05/10 ⇒ ledger ValueError", [dict(kind="withdraw", evidence="x", date="2026-10-05", time_ict="10:00", amount_vnd=-2e9)])
trial("4. amount NaN", raw='{"SpaceX":[{"date":"2026-10-05","time_ict":"10:00","amount_vnd":NaN,"kind":"deposit","evidence":"x"}],"ZaloPay":[]}')
trial("5. thiếu file sổ dòng tiền", remove=True)
trial("6. flow treo 20:00 09/10", [dict(G, date="2026-10-09", time_ict="20:00", amount_vnd=5e7)])
trial("7. flow date=null (TypeError)", [dict(G, date=None, time_ict="10:00", amount_vnd=5e7)])
trial("8. nạp 16:00 ngày 08-06 (phiên THIẾU dòng)", [dict(G, date="2026-08-06", time_ict="16:00", amount_vnd=1e8)])
