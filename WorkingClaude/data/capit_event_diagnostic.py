# -*- coding: utf-8 -*-
"""capit_event_diagnostic.py — per-event economics of the CAPIT sleeve, straight from the
auditable V2.3C ledger (data/v23c_golive_audit_2014_now.csv). Answers: is crisis-capitulation
buying actually a good opportunity, event by event, under T+1 Open fills on live BQ data?

For each CAPIT tier (one per washout event, per book): capital deployed, realized+MTM proceeds,
net P&L, return %, holding window. Also reconstructs the basket's RAW forward return (signal
quality, ignoring cash constraints) so we separate the SIGNAL from the SLEEVE implementation.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

A = pd.read_csv("data/v23c_golive_audit_2014_now.csv", low_memory=False)
A_ymd = pd.to_datetime(A["ymd"], errors="coerce")
tx = A[A["record_type"] == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx["ymd"])
ev = A[A["record_type"] == "EVENT_CAPIT"].copy(); ev["ymd"] = pd.to_datetime(ev["ymd"])
print("EVENT_CAPIT rows (washout events detected):")
ev_list = ev.reset_index(drop=True)
for i, r in ev_list.iterrows():
    print(f"  E{i}: {r['ymd'].date()}  state={int(r['state'])}  size={float(r['value']):.2f}  [{r['reason']}]")

cap = tx[tx["play_type"].astype(str).str.startswith("CAPIT")].copy()
print(f"\nCAPIT transactions: {len(cap)} rows across {cap['play_type'].nunique()} event-tiers")
if cap.empty:
    print("No CAPIT tx — abort."); sys.exit(0)

# event index from play_type CAPIT{B|L}_E{i}
cap["evidx"] = cap["play_type"].str.extract(r"_E(\d+)$").astype(int)
cap["bookc"] = cap["play_type"].str.extract(r"CAPIT([BL])_")

rows = []
for (evidx, book), g in cap.groupby(["evidx", "bookc"]):
    buys = g[g["action"] == "buy"]
    sells = g[g["action"] == "sell"]
    realized = sells[sells["reason"].astype(str).str.startswith("MTM") == False]
    mtm = sells[sells["reason"].astype(str).str.startswith("MTM")]
    cost = float((buys["buy_amount"] + buys["fee"]).sum())            # cash out
    proceeds = float((realized["sell_amount"] - realized["fee"]).sum())  # cash in from real exits
    mtm_val = float(mtm["sell_amount"].sum())                         # still-open marks
    total_back = proceeds + mtm_val
    if cost <= 0: continue
    entry = buys["ymd"].min(); exit_ = sells["ymd"].max()
    rows.append({"evidx": evidx, "book": "BAL" if book == "B" else "LAG",
                 "entry": entry, "exit": exit_,
                 "n_names": buys["ticker"].nunique(),
                 "cost_vnd": cost, "back_vnd": total_back,
                 "pnl_vnd": total_back - cost, "ret_pct": (total_back / cost - 1) * 100,
                 "still_open_pct": mtm_val / total_back * 100 if total_back > 0 else 0})
d = pd.DataFrame(rows).sort_values(["evidx", "book"])

# attach event meta
emeta = {i: (r["ymd"], int(r["state"]), float(r["value"])) for i, r in ev_list.iterrows()}
d["ev_date"] = d["evidx"].map(lambda i: emeta.get(i, (pd.NaT,))[0])
d["state"] = d["evidx"].map(lambda i: emeta.get(i, (None, None))[1])
d["size"] = d["evidx"].map(lambda i: emeta.get(i, (None, None, None))[2])

print("\n" + "=" * 104)
print(f"{'ev':>3} {'date':>11} {'st':>2} {'book':>4} {'n':>3} {'cost(M)':>10} {'pnl(M)':>10} {'ret%':>8} {'hold_d':>7} {'open%':>6}")
print("-" * 104)
for r in d.itertuples():
    hold = (r.exit - r.entry).days
    print(f"{r.evidx:>3} {str(r.ev_date.date()):>11} {r.state:>2} {r.book:>4} {r.n_names:>3} "
          f"{r.cost_vnd/1e6:>10,.0f} {r.pnl_vnd/1e6:>+10,.0f} {r.ret_pct:>+8.1f} {hold:>7} {r.still_open_pct:>6.0f}")

print("-" * 104)
tot_cost = d["cost_vnd"].sum(); tot_pnl = d["pnl_vnd"].sum()
print(f"TOTAL CAPIT deployed {tot_cost/1e9:.2f}B  net P&L {tot_pnl/1e9:+.3f}B  "
      f"aggregate return {tot_pnl/tot_cost*100:+.1f}%")
win = (d["pnl_vnd"] > 0).mean() * 100
print(f"event-legs: {len(d)}  win-rate {win:.0f}%  best {d['ret_pct'].max():+.1f}%  worst {d['ret_pct'].min():+.1f}%")

# per-event (book-summed) net
print("\nPer-event (BAL+LAG summed), sorted by P&L:")
pe = d.groupby(["evidx", "ev_date", "state", "size"]).agg(
    cost=("cost_vnd", "sum"), pnl=("pnl_vnd", "sum")).reset_index()
pe["retpct"] = pe["pnl"] / pe["cost"] * 100
for r in pe.sort_values("pnl").itertuples():
    flag = "  <== BIG LOSS" if r.pnl < -200e6 else ("  <== big win" if r.pnl > 500e6 else "")
    print(f"  E{r.evidx} {str(r.ev_date.date())} st{r.state} sz{r.size:.2f}: "
          f"cost {r.cost/1e9:>5.2f}B  pnl {r.pnl/1e6:>+8,.0f}M  ret {r.retpct:>+6.1f}%{flag}")

# counterfactual: CAPIT economics EXCLUDING the single worst event
worst = pe.loc[pe["pnl"].idxmin()]
keep = pe[pe["evidx"] != worst["evidx"]]
print("\n" + "=" * 70)
print(f"COUNTERFACTUAL — drop the single worst event (E{int(worst['evidx'])} "
      f"{worst['ev_date'].date()}, {worst['pnl']/1e9:+.2f}B):")
print(f"  ALL events : deploy {pe['cost'].sum()/1e9:.1f}B  net {pe['pnl'].sum()/1e9:+.2f}B  "
      f"({pe['pnl'].sum()/pe['cost'].sum()*100:+.1f}%)  win {(pe['pnl']>0).mean()*100:.0f}%")
print(f"  ex-worst   : deploy {keep['cost'].sum()/1e9:.1f}B  net {keep['pnl'].sum()/1e9:+.2f}B  "
      f"({keep['pnl'].sum()/keep['cost'].sum()*100:+.1f}%)  win {(keep['pnl']>0).mean()*100:.0f}%")

# raw signal quality: VNINDEX forward return after each event (knife vs bottom)
print("\n" + "=" * 70)
print("RAW SIGNAL CHECK — VNINDEX return AFTER each washout event (sleeve-free):")
vni = bq("SELECT t.time, t.Close FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' "
         "AND t.time BETWEEN DATE '2014-01-01' AND DATE '2026-06-11' ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")["Close"]
vd = list(vni.index)
def fwd(d0, h):
    import bisect as _b
    i = _b.bisect_left(vd, pd.Timestamp(d0))
    if i >= len(vd) or i + h >= len(vd): return np.nan
    return (vni.iloc[i + h] / vni.iloc[i] - 1) * 100
print(f"{'ev':>3} {'date':>11} {'st':>2} {'sz':>4}  {'fwd20':>7} {'fwd60':>7} {'fwd120':>7}")
for r in ev_list.itertuples():
    if float(r.value) <= 0.005: continue
    print(f"E{r.Index:>2} {str(r.ymd.date()):>11} {int(r.state):>2} {float(r.value):>4.2f}  "
          f"{fwd(r.ymd,20):>+7.1f} {fwd(r.ymd,60):>+7.1f} {fwd(r.ymd,120):>+7.1f}")

print("\nNOTE: sleeve ret% = realized under T+1 Open + cash-sizing + 60d hold (NOT raw basket fwd-ret).")
