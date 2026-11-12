#!/usr/bin/env python3
"""GD0 viec 2 — bang 'VS TIET KIEM'. TWR/VN-Index lay NGUYEN tu mike/bin/nav_period_returns.py (§31), khong tu tinh.
Chay: /home/trido/thanhdt/wc_venv/bin/python vs_savings_table.py"""
import sys, os, datetime as dt, calendar, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, HERE)
import nav_period_returns as N
from hurdle_pit import accrual_pct, flat_pct
END = dt.date(2026, 11, 11)
bm = N._benchmark_fn()
rows_out = []
def run(acct, series):
    rows = N.load_nav_history(acct); inc = N.load_inception(acct)
    def calc(rd):
        if series == "bot":
            return N.compute_sleeve_period_returns(acct, rd, rows, inc, benchmark=bm)
        return N.compute_period_returns(acct, rd, rows, inc, benchmark=bm)
    wins = [("inception->11/11", END, "inception"), ("MTD Nov (->11/11)", END, "mtd")]
    for m in (7, 8, 9, 10):
        wins.append((f"thang {m}", dt.date(2026, m, calendar.monthrange(2026, m)[1]), "mtd"))
    for name, rd, key in wins:
        try:
            r = calc(rd)[key]
        except Exception as e:
            rows_out.append(dict(account=acct, series=series, window=name, note=f"ERR {e}")); continue
        b = r.get("benchmark") or {}
        h = accrual_pct(r["from_date"], r["to_date"])
        live = r["return_pct"]
        rows_out.append(dict(account=acct, series=series, window=name, from_date=r["from_date"], to_date=r["to_date"],
            days=r["days"], live_twr_pct=live, vnindex_price_pct=b.get("vnindex_price_pct"),
            hurdle_pit_pct=round(h, 3), hurdle_flat74_pct=round(flat_pct(r["from_date"], r["to_date"]), 3),
            excess_vs_hurdle_pp=round(live - h, 3),
            excess_vs_vnindex_pp=(round(live - b["vnindex_price_pct"], 3) if b.get("vnindex_price_pct") is not None else None),
            net_flow_vnd=r.get("net_flow_vnd", 0), note=""))
run("SpaceX", "account"); run("ZaloPay", "account"); run("ZaloPay", "bot"); run("SpaceX", "bot")
cols = ["account","series","window","from_date","to_date","days","live_twr_pct","vnindex_price_pct","hurdle_pit_pct","hurdle_flat74_pct","excess_vs_hurdle_pp","excess_vs_vnindex_pp","net_flow_vnd","note"]
with open(os.path.join(HERE, "vs_savings_table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); [w.writerow({c: r.get(c, "") for c in cols}) for r in rows_out]
with open(os.path.join(HERE, "vs_savings_table.md"), "w") as f:
    f.write("| TK | chuoi | cua so | tu→den | ngay | live TWR% | VNI% | hurdle PIT% | hurdle phang7.4% | excess vs hurdle pp | excess vs VNI pp |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows_out:
        if r.get("note"): f.write(f"| {r['account']} | {r['series']} | {r['window']} | {r['note']} |\n"); continue
        f.write(f"| {r['account']} | {r['series']} | {r['window']} | {r['from_date']}→{r['to_date']} | {r['days']} | {r['live_twr_pct']} | {r['vnindex_price_pct']} | {r['hurdle_pit_pct']} | {r['hurdle_flat74_pct']} | {r['excess_vs_hurdle_pp']} | {r['excess_vs_vnindex_pp']} |\n")
print(open(os.path.join(HERE, "vs_savings_table.md")).read())
