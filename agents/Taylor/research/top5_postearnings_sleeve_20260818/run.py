#!/usr/bin/env python3
"""Primary run: frozen spec (Top-5, ey+cfy+ps, require_reported=True)."""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (load, build_selection, price_frame, simulate, metrics,
                    season_events, regimes, stats_block, next_td, OUT, CAPITAL, TC)

N_TOP = int(os.environ.get("N_TOP", 5))
LENSES = tuple(os.environ.get("LENSES", "ey,cfy,ps").split(","))
REQ = os.environ.get("REQ_REPORTED", "1") == "1"
TAG = os.environ.get("TAG", "primary")

pd.set_option("display.width", 200)
print(f"=== Top-5 post-earnings sleeve — tag={TAG} n_top={N_TOP} lenses={LENSES} "
      f"require_reported={REQ} TC={TC} capital={CAPITAL:,.0f} threads=1")

d = load()
P_raw = price_frame(d["px"])
P = P_raw.ffill()
cal = d["calendar"]["time"].sort_values().reset_index(drop=True)

sel, pool = build_selection(d, n_top=N_TOP, lenses=LENSES, require_reported=REQ)
print(f"\n[selection] seasons={sel['season'].nunique()} picks={len(sel)} "
      f"distinct tickers={sel['ticker'].nunique()}")
print(pool.groupby("season")["pool_n"].first().describe().to_string())

nav, tr, ident = simulate(sel, P, cal, d["seasons"])
print(f"\n[self-check] cash-flow identity max err = {ident['cash_identity_err_vnd']:.6f} VND")
print(f"[self-check] final NAV identity err     = {ident['nav_identity_err_vnd']:.6f} VND")
print(f"[costs] fees {ident['fees_total_vnd']:,.0f} VND on turnover "
      f"{ident['turnover_notional_vnd']:,.0f} VND "
      f"({ident['fees_total_vnd']/CAPITAL*100:.2f}% of starting capital)")

m = metrics(nav)
vni = P["VNINDEX"].reindex(nav.index).ffill()
vnav = CAPITAL * vni / vni.iloc[0]
mv = metrics(vnav)
print("\n[NAV metrics] sleeve vs VNINDEX buy&hold, same window")
print(pd.DataFrame({"sleeve": m, "VNINDEX": mv}).to_string())

ev = season_events(sel, pool, d, P, n_top=N_TOP)
ev = regimes(d, ev)
ev["era"] = np.where(ev["rebal"] < "2020-01-01", "IS(2014-19)", "OOS(2020+)")
ev.to_csv(os.path.join(OUT, f"events_{TAG}.csv"), index=False)
sel.to_csv(os.path.join(OUT, f"selection_{TAG}.csv"), index=False)
pool.to_csv(os.path.join(OUT, f"pool_{TAG}.csv"), index=False)
nav.to_csv(os.path.join(OUT, f"nav_{TAG}.csv"))

STATE = {0:"CRISIS",1:"BEAR",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}
ev["dt5g"] = ev["state"].map(lambda s: STATE.get(int(s), f"S{s}") if pd.notna(s) else None)
VN = {"CHEAP":"RE","FAIR":"TRUNG TINH","EXPENSIVE":"DAT"}
ev["radar"] = ev["label"].map(VN)

def show(df, key, title):
    print(f"\n### {title}")
    out = []
    for k, g in df.groupby(key, dropna=False):
        r = {key if isinstance(key, str) else "grp": k}
        for col, lab in [("sleeve_ret","sleeve"),("exc_vni","vs VNINDEX"),("exc_sector","vs ICB sector")]:
            b = stats_block(g[col])
            r[f"{lab}_n"] = b.get("n")
            r[f"{lab}_mean"] = round(b.get("mean", np.nan)*100, 2) if b.get("n") else None
            r[f"{lab}_med"] = round(b.get("median", np.nan)*100, 2) if b.get("n") else None
            r[f"{lab}_win"] = round(b.get("win_rate", np.nan)*100, 0) if b.get("n") else None
            r[f"{lab}_t"] = round(b["t"], 2) if b.get("t") else None
        out.append(r)
    print(pd.DataFrame(out).to_string(index=False))

for h in ["to_next","h21","h63"]:
    e = ev[ev.horizon == h]
    print(f"\n{'='*100}\nHORIZON = {h}   (N seasons = {len(e)})")
    show(e, "era", f"IS/OOS split — {h}")
    b = stats_block(e["exc_vni"]); print(f" FULL exc_vni : {b}")
    b = stats_block(e["exc_sector"]); print(f" FULL exc_sec : {b}")
    show(e, "dt5g", f"by DT5G state at T0 — {h}")
    show(e, "radar", f"by Value Radar at T0 — {h}")

# decision matrix on the primary horizon
e = ev[ev.horizon == "to_next"].copy()
print(f"\n{'='*100}\nDECISION MATRIX  DT5G x Value Radar  (horizon=to_next, N={len(e)})")
rows = []
for (st, rd), g in e.groupby(["dt5g","radar"], dropna=False):
    bv, bs = stats_block(g["exc_vni"]), stats_block(g["exc_sector"])
    rows.append({"DT5G": st, "Radar": rd, "N": len(g),
                 "sleeve_mean%": round(g["sleeve_ret"].mean()*100, 2),
                 "excVNI_mean%": round(bv.get("mean", np.nan)*100, 2) if bv.get("n") else None,
                 "excVNI_med%": round(bv.get("median", np.nan)*100, 2) if bv.get("n") else None,
                 "excVNI_win%": round(bv.get("win_rate", np.nan)*100, 0) if bv.get("n") else None,
                 "excSEC_mean%": round(bs.get("mean", np.nan)*100, 2) if bs.get("n") else None,
                 "excSEC_win%": round(bs.get("win_rate", np.nan)*100, 0) if bs.get("n") else None,
                 "seasons": ",".join(g["season"])})
mx = pd.DataFrame(rows).sort_values(["DT5G","Radar"])
print(mx.to_string(index=False))
mx.to_csv(os.path.join(OUT, f"matrix_{TAG}.csv"), index=False)

json.dump({"tag":TAG,"n_top":N_TOP,"lenses":list(LENSES),"require_reported":REQ,
           "selfcheck":ident,"nav_sleeve":m,"nav_vnindex":mv,
           "n_seasons_to_next":int((ev.horizon=="to_next").sum())},
          open(os.path.join(OUT, f"summary_{TAG}.json"), "w"), indent=2, default=str)
print("\nartifacts ->", OUT)
