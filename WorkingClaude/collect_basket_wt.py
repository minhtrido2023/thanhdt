# -*- coding: utf-8 -*-
"""collect_basket_wt.py — compare V2.3 metrics across basket weight schemes (capwt/ew/namecap/
sectorcap) at scale, V0 policy. Reads the audit CSVs; capwt = the no-_wt baseline."""
import pandas as pd, numpy as np, os, re, glob
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
DATA = os.path.join(WORKDIR, "data")
PAT = "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg*.csv"

def parse(fn):
    if "custompitgq" in fn or "_park" in fn:      # only V0-policy custompitg files
        return None
    nm = re.search(r"_nav(\d+)B", fn); nav = int(nm.group(1)) if nm else 50
    wm = re.search(r"_wt(ew|namecap|sectorcap)", fn); sc = wm.group(1) if wm else "capwt"
    return nav, sc

ORDER = {"capwt": 0, "ew": 1, "namecap": 2, "sectorcap": 3}
rows = []
for fn in glob.glob(os.path.join(DATA, PAT)):
    p = parse(os.path.basename(fn))
    if p is None: continue
    nav, sc = p
    if nav not in (200, 500): continue
    df = pd.read_csv(fn, low_memory=False)
    M = df[df["record_type"] == "METRIC"].set_index("key")["value"]
    def g(k): return float(M.get(k, np.nan))
    selfck = max(abs(g("cash_flow_identity_max_err_vnd_BAL")), abs(g("cash_flow_identity_max_err_vnd_LAG")))
    D = df[df["record_type"] == "DAILY"].copy()
    for c in ["nav_bal_ref","nav_lag_ref","bal_etf_ref","lag_etf_ref","bal_cash_ref","lag_cash_ref"]:
        D[c] = pd.to_numeric(D[c], errors="coerce")
    nr = D["nav_bal_ref"] + D["nav_lag_ref"]
    park = ((D["bal_etf_ref"]+D["lag_etf_ref"]) / nr * 100).mean()
    idle = ((D["bal_cash_ref"]+D["lag_cash_ref"]) / nr * 100).mean()
    rows.append(dict(nav=nav, scheme=sc, CAGR=g("cagr")*100, Sharpe=g("sharpe_252"),
                     MaxDD=g("max_dd")*100, Calmar=g("calmar"), park=park, idle=idle, selfck=selfck))

t = pd.DataFrame(rows)
if t.empty:
    print("no files yet"); raise SystemExit
t["o"] = t["scheme"].map(ORDER); t = t.sort_values(["nav","o"])
print("="*86); print(" V2.3 theo SƠ ĐỒ TRỌNG SỐ rổ parking (V0 policy {3:0.7}, vehicle custompitg)"); print("="*86)
for nav in sorted(t["nav"].unique()):
    sub = t[t["nav"] == nav]
    base = sub[sub["scheme"] == "capwt"]["CAGR"]
    b = float(base.iloc[0]) if len(base) else np.nan
    print(f"\n--- NAV {nav}B  (Δ = vs capwt) ---")
    print(f"  {'scheme':<11}{'CAGR':>7}{'Δ':>7}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}{'park%':>7}{'idle%':>7}  selfck")
    for _, r in sub.iterrows():
        dlt = r["CAGR"] - b if not np.isnan(b) else np.nan
        print(f"  {r['scheme']:<11}{r['CAGR']:7.2f}{dlt:+7.2f}{r['Sharpe']:8.2f}{r['MaxDD']:8.1f}"
              f"{r['Calmar']:8.2f}{r['park']:7.1f}{r['idle']:7.1f}   {r['selfck']:,.0f}")
