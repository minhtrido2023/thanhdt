"""Why the state-linked exit does not rescue 2026: where does the freed capital go?
Reads the DAILY section (per-book ledger refs) of each leg. Diagnostic only."""
import pandas as pd
B = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
     "_etfliqcustompitg_wtnamecap_advprice_univpit_exp_baladapt%s.csv")
cols = ["ymd", "nav_bal_ref", "bal_cash_ref", "bal_stocks_ref", "bal_etf_ref", "state"]
D = {}
for leg in ["ctrl", "a", "b", "c", "d"]:
    df = pd.read_csv(B % leg, low_memory=False)
    d = df[df.record_type == "DAILY"][cols].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    for c in cols[1:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    D[leg] = d.set_index("ymd")

print("=== BAL book (25B reference ledger) monthly return %, 2026 ===")
out = {}
for leg, d in D.items():
    s = d["nav_bal_ref"].dropna()
    s = s[s.index >= "2025-12-01"]
    out[leg] = s.resample("ME").last().pct_change().mul(100)
print(pd.DataFrame(out).round(2).to_string())

print("\n=== BAL composition, month-end 2026 (% of book NAV): stocks / custom30V parking / cash ===")
for leg in ["ctrl", "a"]:
    d = D[leg]
    d = d[(d.index >= "2026-01-01")]
    m = d.resample("ME").last()
    t = pd.DataFrame({
        "stocks%": m["bal_stocks_ref"] / m["nav_bal_ref"] * 100,
        "park%": m["bal_etf_ref"] / m["nav_bal_ref"] * 100,
        "cash%": m["bal_cash_ref"] / m["nav_bal_ref"] * 100,
        "state": m["state"]}).round(1)
    print(f"--- leg {leg}\n{t.to_string()}")

print("\n=== 2021: BAL book return by quarter (the year that pays for everything) ===")
o = {}
for leg, d in D.items():
    s = d["nav_bal_ref"].dropna()
    s = s[(s.index >= "2020-12-01") & (s.index <= "2021-12-31")]
    o[leg] = s.resample("QE").last().pct_change().mul(100)
print(pd.DataFrame(o).round(2).to_string())
