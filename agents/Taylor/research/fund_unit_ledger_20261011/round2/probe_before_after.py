#!/usr/bin/env python3
"""Tái hiện TRƯỚC/SAU các lỗi của arch-review @feaa33b5 trên MỘT cây bin cho trước.
Dựng lại từ probe/p1.py, p2.py, p3.py của reviewer (cùng kịch bản, cùng số), viết sao cho chạy
được trên CẢ cây trước (feaa33b5) lẫn cây sau (vòng 2) dù schema bản ghi khác nhau.

    python3 probe_before_after.py <thư mục bin của cây cần thử> <thư mục fixture dữ liệu>
Không đọc/ghi data/ thật: mọi thứ ở tempdir.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TREE, FIX = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, TREE)
sys.dont_write_bytecode = True
import account_cash_flows as acf       # noqa: E402
import nav_period_returns as npr       # noqa: E402
import nav_unit_ledger as nul          # noqa: E402

D = datetime.date
INC = {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000}
TMP = Path(tempfile.mkdtemp(prefix="fu_probe_"))


def rows(*recs):
    return [nul.NavRow(D.fromisoformat(d), v, False, f"{d}T19:10:00") for d, v in recs]


def load(recs):
    p = TMP / "flows.json"
    p.write_text(json.dumps({"SpaceX": recs}), encoding="utf-8")
    return acf.load_flows("SpaceX", str(p))


def show(label, fn):
    try:
        print(f"  {label}: {fn()}")
    except Exception as exc:                                    # noqa: BLE001
        print(f"  {label}: {type(exc).__name__}: {str(exc)[:150]}")


def pct(r, rec, rd, per="inception"):
    out = npr.compute_period_returns("SpaceX", rd, r, INC, load([rec]))
    p = out[per]
    extra = f" pending={len(out['pending_flows'])}" if "pending_flows" in out else " (không có khoá pending)"
    return f"{per} {p['return_pct']:+.3f}% pnl {p.get('pnl_vnd', float('nan')):+,.0f}{extra}"


def rec(date, amount, **kw):
    return dict({"date": date, "amount_vnd": amount, "kind": "deposit" if amount > 0 else "withdraw",
                 "evidence": "sao kê"}, **kw)


print("== K1. Thị trường ĐỨNG YÊN, NAV chụp 19:10, tiền vào/ra 20:00 thứ Sáu 07-03. Sự thật: 0,0% mọi ngày")
dep_rows = rows(("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 1.2e9), ("2026-07-07", 1.2e9))
wd_rows = rows(("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 0.8e9), ("2026-07-07", 0.8e9))
for label, r, record in (
        ("nạp 200tr — mẫu cũ (chỉ ngày, không giờ)", dep_rows, rec("2026-07-03", 200e6)),
        ("nạp 200tr — bod + 20:00 (mặc định cũ)", dep_rows, rec("2026-07-03", 200e6, timing="bod", time_ict="20:00")),
        ("nạp 200tr — ngày + giờ 20:00 (schema mới)", dep_rows, rec("2026-07-03", 200e6, time_ict="20:00")),
        ("rút 200tr — mẫu cũ (chỉ ngày, không giờ)", wd_rows, rec("2026-07-03", -200e6)),
        ("rút 200tr — ngày + giờ 20:00 (schema mới)", wd_rows, rec("2026-07-03", -200e6, time_ict="20:00")),
        ("nạp 200tr — eod + 20:00", dep_rows, rec("2026-07-03", 200e6, timing="eod", time_ict="20:00"))):
    for rd in (D(2026, 7, 3), D(2026, 7, 6), D(2026, 7, 7)):
        show(f"[{label}] asof {rd}", lambda: pct(r, record, rd))

print("== N1. Bản ghi gõ nhầm ngày 07-13 (thay vì 07-03), NAV 07-03 đã +40tr (4%)")
r = rows(("2026-07-02", 1e9), ("2026-07-03", 1.04e9), ("2026-07-06", 1.04e9))
for label, record in (("mẫu cũ", rec("2026-07-13", 40e6)), ("ngày + giờ", rec("2026-07-13", 40e6, time_ict="10:00"))):
    show(f"[{label}] asof 07-06", lambda: pct(r, record, D(2026, 7, 6)))

print("== N3/N4. Nạp 100tr thứ Bảy 07-04, thị trường đứng yên; thứ Hai NAV 1,1 tỷ")
fri = rows(("2026-07-02", 1e9), ("2026-07-03", 1e9))
mon = rows(("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 1.1e9))
for label, record in (("mẫu cũ", rec("2026-07-04", 100e6)),
                      ("bod + 10:00 (gợi ý của thông báo lỗi cũ)", rec("2026-07-04", 100e6, timing="bod", time_ict="10:00")),
                      ("ngày + giờ 10:00", rec("2026-07-04", 100e6, time_ict="10:00"))):
    show(f"[{label}] Chủ nhật", lambda: pct(fri, record, D(2026, 7, 5)))
    show(f"[{label}] thứ Hai", lambda: pct(mon, record, D(2026, 7, 6)))
    show(f"[{label}] cổng 5% thứ Hai", lambda: [(str(j["date"]), round(j["change_pct"], 2))
                                                 for j in acf.unexplained_nav_jumps(mon, load([record]))])
try:
    import daily_nav_snapshot as dns
    hist = [{"date": "2026-07-02", "nav": "1000000000", "balance_ts": "2026-07-02T19:10:00"},
            {"date": "2026-07-03", "nav": "1000000000", "balance_ts": "2026-07-03T19:10:00"}]
    for label, record in (("mẫu cũ", rec("2026-07-04", 200e6)), ("ngày + giờ 10:00", rec("2026-07-04", 200e6, time_ict="10:00"))):
        p = TMP / "f3.json"
        p.write_text(json.dumps({"SpaceX": [record]}), encoding="utf-8")
        kw = {"balance_ts": "2026-07-06T19:10:00"} if "balance_ts" in dns.nav_jump_verdict.__code__.co_varnames else {}
        ok, msg = dns.nav_jump_verdict("SpaceX", "2026-07-06", 1e9, 1.2e9, 15.0, hist, components={},
                                       flows_path=str(p), **kw)
        print(f"  [{label}] daily_nav_snapshot cổng 15% thứ Hai (+20%): ok={ok} :: {(msg or '').strip().splitlines()[0][:170]}")
except Exception as exc:                                        # noqa: BLE001
    print(f"  daily_nav_snapshot không import được ở cây này: {type(exc).__name__}: {str(exc)[:120]}")

print("== N2. nav_history có 2 dòng trùng ngày + dòng tiền ngày đó")
dup = rows(("2026-07-02", 1e9), ("2026-07-03", 1.2e9), ("2026-07-03", 1.2e9))
for label, record in (("mẫu cũ", rec("2026-07-03", 200e6)), ("ngày + giờ 16:00", rec("2026-07-03", 200e6, time_ict="16:00"))):
    show(f"[{label}] giá đơn vị từng dòng", lambda: [
        (str(x["date"]), round(x["unit_price"], 2))
        for x in nul.build_ledger(dup, load([record]), D(2026, 7, 1), 1e9)[0]])

print("== N7. Ghi chú IRR")
show("0 nghiệm do lỗ >99,9% (dòng tiền KHÔNG đổi dấu)", lambda: npr.money_weighted_return(1000.0, 0.1, [(0.5, 10.0)]))
show("2 nghiệm", lambda: npr.money_weighted_return(1000.0, 78.0, [(0.5, -2120.0), (0.0, 1200.0)]))
wk = rows(("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 1.224e9), ("2026-07-10", 1.224e9))
show("nạp thứ Bảy 07-04 09:00 ⇒ mwr asof 07-10 (w=7/9 tính từ giá chốt thứ Sáu ⇒ 2,078; w=5/9 từ CN ⇒ 2,161)",
     lambda: npr.compute_period_returns("SpaceX", D(2026, 7, 10), wk, INC, load(
         [rec("2026-07-04", 200e6, timing="bod", time_ict="09:00")]))["inception"]["mwr_pct"])

print("== N8. Cột suy ra trong sổ đã chốt bị sửa thành nan/inf")
led = nul.build_ledger(rows(("2026-07-02", 1.01e9), ("2026-07-03", 1.02e9)), [], D(2026, 7, 1), 1e9)[0]
for bad in (float("nan"), float("inf")):
    sealed = [dict(x) for x in led]
    sealed[1]["unit_price"] = bad
    show(f"unit_price={bad}", lambda: nul.diff_against_sealed(led, sealed) or "KHÔNG phát hiện lệch")
show("annualize_or_null(1.4641, 1461 ngày = 4×365,25) (N9: 365,25 ⇒ đúng 10,0)", lambda: npr.annualize_or_null(1.4641, 1461))

print("== K2. Sandbox: sổ đơn vị LỆCH nằm trong thư mục dữ liệu ⇒ CLI + cổng báo cáo (+9,99% là số SAI)")
wc = TMP / "WC"
(wc / "data" / "execution_logs").mkdir(parents=True)
(wc / "mike" / "bin").mkdir(parents=True)
(wc / "wc_env.sh").write_text("")
(wc / "mike" / "MIKE.md").write_text("x")
for f in ("nav_period_returns.py", "nav_unit_ledger.py", "account_cash_flows.py", "report_delivery_gate.py", "wc_paths.py"):
    shutil.copy2(f"{TREE}/{f}", wc / "mike" / "bin" / f)
shutil.copy2(FIX / "account_inception.json", wc / "data")
(wc / "data" / "account_cash_flows.json").write_text(json.dumps({"SpaceX": [], "ZaloPay": []}))
for a in ("SpaceX", "ZaloPay"):
    shutil.copy2(FIX / f"nav_history_{a}.csv", wc / "data" / "execution_logs")
env = {k: v for k, v in os.environ.items() if k not in ("TZ", "WC_ROOT", "MIKE_ROOT", "NAV_UNIT_LEDGER_DIR")}
real = nul.load_nav_history("SpaceX", str(wc / "data" / "execution_logs"))
ledger = nul.build_ledger(real, [], D(2026, 7, 1), 1e9)[0]
ledger[-1] = dict(ledger[-1], nav=ledger[-1]["nav"] + 1234.0)
(wc / "data" / "execution_logs" / "nav_unit_ledger_SpaceX.csv").write_text(
    ",".join(nul.LEDGER_FIELDS) + "\n" + "".join(nul._csv_line(x) for x in ledger), encoding="utf-8")
p = subprocess.run([sys.executable, "bin/nav_period_returns.py", "--account", "SpaceX", "--report-date", "2026-10-09"],
                   cwd=wc / "mike", capture_output=True, text=True, env=env)
print(f"  CLI nav_period_returns: rc={p.returncode} ::",
      (json.loads(p.stdout)["inception"]["return_pct"] if p.returncode == 0 else p.stderr.strip().splitlines()[0][:150]))
report = TMP / "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
report.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | +9,99% | x | y |\n", encoding="utf-8")
code = ("import sys, pathlib; sys.path.insert(0, 'bin'); import report_delivery_gate as g\n"
        "try:\n    g._check_period_returns(pathlib.Path(sys.argv[1])); print('KHÔNG chặn (đi tiếp)')\n"
        "except RuntimeError as exc:\n    print('CHẶN: ' + str(exc)[:150])\n")
p = subprocess.run([sys.executable, "-c", code, str(report)], cwd=wc / "mike", capture_output=True, text=True, env=env)
print("  cổng tỉ suất với báo cáo ghi +9,99%:", p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-200:])
p = subprocess.run([sys.executable, "bin/nav_unit_ledger.py", "--account", "SpaceX", "--seal"],
                   cwd=wc / "mike", capture_output=True, text=True, env=env)
print(f"  nav_unit_ledger.py --seal (thư mục dữ liệu mặc định): rc={p.returncode} ::", (p.stderr or p.stdout).strip().splitlines()[0][:150])
shutil.rmtree(TMP, ignore_errors=True)
