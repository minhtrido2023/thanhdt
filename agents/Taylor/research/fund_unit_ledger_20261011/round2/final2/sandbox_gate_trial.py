#!/usr/bin/env python3
"""Thử CLI của NHÁNH với cổng báo cáo trong SANDBOX: bản sao bin/ nhánh + bản sao dữ liệu thật
(account_inception, account_cash_flows, nav_history 2 TK) + bản sao báo cáo tuần đã gửi.
Không đọc/ghi cây canonical: report_delivery_gate.ROOT phải trỏ vào sandbox (in ra để chứng minh)."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["FU_SBX"] = "/tmp/fu_fin_gate"
import run_mutants as rm

sb = rm.build_sandbox(0)                       # /tmp/fu_fin_gate/s0/WC/mike
REP = "/home/trido/thanhdt/WorkingClaude/mike/reports"
os.makedirs(f"{sb}/reports")
env = rm.ENV
head = subprocess.run(["git", "-C", rm.WT, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
print(f"cây bin: {rm.WT}/bin @ {head} → {sb}/bin")

CODE = ("import sys, pathlib; sys.path.insert(0, 'bin'); import report_delivery_gate as g\n"
        "print('ROOT=' + str(g.ROOT))\n"
        "for name in ('_check_period_returns', '_check_nav_flow_records'):\n"
        "    try:\n        getattr(g, name)(pathlib.Path(sys.argv[1])); print(name + ': QUA')\n"
        "    except RuntimeError as exc:\n        print(name + ': CHẶN — ' + ' '.join(str(exc).split())[:330])\n")


def cli(account, date="2026-10-09"):
    p = subprocess.run([sys.executable, "bin/nav_period_returns.py", "--account", account, "--report-date", date],
                       cwd=sb, capture_output=True, text=True, env=env)
    if p.returncode:
        return f"rc={p.returncode} :: {' '.join(p.stderr.split())[:300]}"
    d = json.loads(p.stdout)
    return (f"rc=0 :: inception {d['inception']['return_pct']} / wtd {d['wtd']['return_pct']} / mtd {d['mtd']['return_pct']}"
            f" · pending={len(d['pending_flows'])} dropped={len(d['dropped_flows'])}")


def gate(report):
    p = subprocess.run([sys.executable, "-c", CODE, report], cwd=sb, capture_output=True, text=True, env=env)
    for ln in p.stdout.strip().splitlines():
        print("     " + ln)
    for ln in p.stderr.strip().splitlines():
        print("     [stderr] " + ln[:300])


def flows(obj):
    json.dump(obj, open(f"{sb}/../data/account_cash_flows.json", "w"))


real_flows = json.load(open(f"{sb}/../data/account_cash_flows.json"))
print("sổ dòng tiền thật (bản sao):", {k: len(v) for k, v in real_flows.items() if isinstance(v, list)})
print("\n== 1. dữ liệu thật, CLI nhánh")
for a in ("SpaceX", "ZaloPay"):
    print(f"   {a}: {cli(a)}")

print("\n== 2. báo cáo tuần ĐÃ GỬI (nguyên văn) qua cổng")
for a in ("SpaceX", "ZaloPay"):
    name = f"{a}_weekly_report_2026-10-05_to_2026-10-09.md"
    shutil.copy2(f"{REP}/{name}", f"{sb}/reports/{name}")
    print(f"   {name}")
    gate(f"{sb}/reports/{name}")

print("\n== 3. cùng báo cáo SpaceX, sửa dòng 'Từ khi bắt đầu hoạt động' thành +9,99%")
src = open(f"{sb}/reports/SpaceX_weekly_report_2026-10-05_to_2026-10-09.md", encoding="utf-8").read()
import re
bad, n = re.subn(r"(\|\s*\**Từ khi bắt đầu hoạt động[^|]*\|\s*\**)[^|*]+", r"\g<1>+9,99%", src, count=1)
print(f"   (đã thay {n} ô)")
os.makedirs(f"{sb}/reports/bad"); badp = f"{sb}/reports/bad/SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
open(badp, "w", encoding="utf-8").write(bad)
gate(badp)

print("\n== 4. sổ đơn vị LỆCH nằm sẵn trong thư mục dữ liệu (ca K2 của reviewer): CLI + cổng với báo cáo sai")
sys.path.insert(0, f"{sb}/bin"); sys.dont_write_bytecode = True
import nav_unit_ledger as nul
import datetime
rows = nul.load_nav_history("SpaceX", f"{sb}/../data/execution_logs")
led = nul.build_ledger(rows, [], datetime.date(2026, 7, 1), 1e9)[0]
led[-1] = dict(led[-1], nav=led[-1]["nav"] + 1234.0)
lp = f"{sb}/../data/execution_logs/nav_unit_ledger_SpaceX.csv"
open(lp, "w", encoding="utf-8").write(",".join(nul.LEDGER_FIELDS) + "\n" + "".join(nul._csv_line(x) for x in led))
print(f"   SpaceX: {cli('SpaceX')}")
gate(badp)
p = subprocess.run([sys.executable, "bin/nav_unit_ledger.py", "--account", "SpaceX", "--seal"], cwd=sb, capture_output=True, text=True, env=env)
print(f"   --seal vào thư mục dữ liệu mặc định: rc={p.returncode} :: {' '.join((p.stderr or p.stdout).split())[:260]}")
os.remove(lp)

print("\n== 5. bản ghi nạp 200tr KHÔNG khai giờ (mẫu cũ) trong sổ dòng tiền: CLI + cổng với báo cáo ĐÚNG")
flows({"SpaceX": [{"date": "2026-10-08", "amount_vnd": 200000000, "kind": "deposit", "evidence": "sao kê"}], "ZaloPay": []})
print(f"   SpaceX: {cli('SpaceX')}")
gate(f"{sb}/reports/SpaceX_weekly_report_2026-10-05_to_2026-10-09.md")

print("\n== 6. nạp 200tr 2026-10-10 (thứ Bảy) 10:00, CHƯA có dòng NAV nào sau đó ⇒ treo, phải HIỆN")
flows({"SpaceX": [{"date": "2026-10-10", "time_ict": "10:00", "amount_vnd": 200000000, "kind": "deposit", "evidence": "sao kê"}], "ZaloPay": []})
print(f"   SpaceX asof 2026-10-09: {cli('SpaceX')}")
p = subprocess.run([sys.executable, "bin/nav_period_returns.py", "--account", "SpaceX", "--report-date", "2026-10-10"], cwd=sb, capture_output=True, text=True, env=env)
print(f"   SpaceX asof 2026-10-10: rc={p.returncode} pending_flows={json.loads(p.stdout)['pending_flows'] if p.returncode == 0 else None}")
print(f"   stderr: {' '.join(p.stderr.split())[:300]}")
gate(f"{sb}/reports/SpaceX_weekly_report_2026-10-05_to_2026-10-09.md")
flows(real_flows)

print("\n== 7. selfcheck của cổng chạy TRONG sandbox (gọi nav_period_returns.py của nhánh)")
for t in (["bin/report_delivery_gate_selfcheck.py"], ["bin/nav_period_returns.py", "--selfcheck"]):
    p = subprocess.run([sys.executable] + t, cwd=sb, capture_output=True, text=True, env=env)
    tail = [ln for ln in (p.stdout + p.stderr).strip().splitlines() if ln.strip()]
    print(f"   {' '.join(t)}: rc={p.returncode} :: {tail[-1][:200] if tail else ''}")
