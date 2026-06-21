# -*- coding: utf-8 -*-
"""collect_parkstate.py — assemble the park-state experiment comparison from the audit CSVs.
Reads data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg{_park...}_nav{N}B.csv,
prints: (1) headline metrics matrix (NAV x policy), (2) state-conditional composition in BULL(4)/
EXBULL(5) days (parked% / idle-cash% / stk% — confirms the mechanic), (3) bull-year returns.
ALL numbers come straight from the BQ-audited files (self-check 0 VND already verified per run)."""
import os, re, glob
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
DATA = os.path.join(WORKDIR, "data")
PAT = "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg*.csv"

def policy_of(fn):
    if "custompitgq" in fn:          # quality-tilt variant from earlier work — not this experiment
        return None
    nm = re.search(r"_nav(\d+)B", fn)
    nav = int(nm.group(1)) if nm else 50      # 50B is the default NAV (no _navNB tag emitted)
    pm = re.search(r"_park([0-9_-]+?)(?:_nav\d+B)?\.csv$", fn)
    ptag = pm.group(1) if pm else None
    if not ptag:
        return nav, "V0 {3:0.7} NEUTRAL-only", {3: 0.7}
    # decode tag like 3-70_4-100_5-50  (state-pct pairs)
    d = {}
    for pair in ptag.split("_"):
        s, pct = pair.split("-")
        d[int(s)] = int(pct) / 100.0
    lbl = {(frozenset({(3,0.7),(4,1.0)})):       "V1 {3:.7,4:1.0} +BULL",
           (frozenset({(3,0.7),(4,0.7)})):       "V2 {3:.7,4:.7} +BULLmod",
           (frozenset({(3,0.7),(4,1.0),(5,0.5)})):"V3 {3:.7,4:1.0,5:.5} +B+EXB"}.get(
               frozenset(d.items()), "{" + ",".join(f"{k}:{v}" for k, v in sorted(d.items())) + "}")
    return nav, lbl, d

rows, comp_rows, year_rows = [], [], []
files = sorted(glob.glob(os.path.join(DATA, PAT)))
print(f"found {len(files)} audit files\n")
for fn in files:
    if "custompitgq" in fn:
        continue   # quality-tilt variant from earlier work — not part of this experiment
    pol = policy_of(os.path.basename(fn))
    if pol is None:
        continue
    nav, lbl, _ = pol
    df = pd.read_csv(fn, low_memory=False)
    M = df[df["record_type"] == "METRIC"].set_index("key")["value"]
    def g(k): return float(M.get(k, np.nan))
    sc = max(abs(g("cash_flow_identity_max_err_vnd_BAL")), abs(g("cash_flow_identity_max_err_vnd_LAG")),
             abs(g("combination_replay_err_vnd")))
    # composition (reference ledgers): stk%=in stocks, park%=in basket beta,
    # idle%=cash earning 0% (THE drag = "tiền rảnh"). stk+park+idle = 100%.
    D = df[df["record_type"] == "DAILY"].copy()
    for c in ["state","nav_bal_ref","nav_lag_ref","bal_cash_ref","bal_stocks_ref","bal_etf_ref",
              "lag_cash_ref","lag_stocks_ref","lag_etf_ref"]:
        D[c] = pd.to_numeric(D[c], errors="coerce")
    navref = D["nav_bal_ref"] + D["nav_lag_ref"]
    D["stk%"] = (D["bal_stocks_ref"]+D["lag_stocks_ref"])/navref*100
    D["park%"] = (D["bal_etf_ref"]+D["lag_etf_ref"])/navref*100
    D["idle%"] = (D["bal_cash_ref"]+D["lag_cash_ref"])/navref*100
    rows.append(dict(nav=nav, policy=lbl, CAGR=g("cagr")*100, Sharpe=g("sharpe_252"),
                     MaxDD=g("max_dd")*100, Calmar=g("calmar"), Sortino=g("sortino_252"),
                     idle_all=D["idle%"].mean(), park_all=D["park%"].mean(), stk_all=D["stk%"].mean(),
                     selfcheck_VND=sc, nrebal=int(g("n_allocator_rebalances"))))
    for st, nm in [(4,"BULL"),(5,"EXBULL")]:
        sub = D[D["state"] == st]
        if len(sub):
            comp_rows.append(dict(nav=nav, policy=lbl, state=nm, days=len(sub),
                                  stk=sub["stk%"].mean(), park=sub["park%"].mean(), idle=sub["idle%"].mean()))
    # annual returns
    A = df[df["record_type"] == "ANNUAL"]
    for _, a in A.iterrows():
        year_rows.append(dict(nav=nav, policy=lbl, year=int(a["key"]), ret=float(a["value"])*100))

met = pd.DataFrame(rows).sort_values(["nav","policy"])
pd.set_option("display.width", 200, "display.max_columns", 30)

print("="*92); print(" (1) HEADLINE METRICS — NAV x parking policy (vehicle=custompitg, deploy config)"); print("="*92)
for nav in sorted(met["nav"].unique()):
    print(f"\n--- NAV {nav}B ---")
    sub = met[met["nav"] == nav][["policy","CAGR","Sharpe","MaxDD","Calmar","idle_all","park_all","stk_all","selfcheck_VND"]]
    sub = sub.rename(columns={"idle_all":"idle%avg","park_all":"park%avg","stk_all":"stk%avg"})
    print(sub.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

comp = pd.DataFrame(comp_rows)
print("\n"+"="*92); print(" (2) COMPOSITION in BULL/EXBULL days (% of book ref-NAV) — confirms the mechanic"); print("="*92)
for nav in sorted(comp["nav"].unique()):
    print(f"\n--- NAV {nav}B ---")
    sub = comp[comp["nav"] == nav][["policy","state","days","stk","park","idle"]]
    print(sub.to_string(index=False, float_format=lambda x: f"{x:.1f}"))

yr = pd.DataFrame(year_rows)
print("\n"+"="*92); print(" (3) BULL-YEAR returns (%) — where park-BULL should land (2020/2021 broad, 2025 VIC-led)"); print("="*92)
for nav in sorted(yr["nav"].unique()):
    piv = yr[(yr["nav"]==nav) & (yr["year"].isin([2020,2021,2022,2023,2024,2025]))].pivot_table(
        index="policy", columns="year", values="ret")
    print(f"\n--- NAV {nav}B ---")
    print(piv.to_string(float_format=lambda x: f"{x:+.1f}"))

met.to_csv(os.path.join(DATA, "parkstate_experiment_summary.csv"), index=False)
print(f"\n-> data/parkstate_experiment_summary.csv")
