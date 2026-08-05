"""Book attribution + band occupancy + funding-order trace — job Taylor_20260805_163403.

READ-ONLY. Reads the verified control CSV (md5 7d053e6201c9d107685ff4d1dd9d2d2a == the
production run that produced the pinned R3 28,86% / 1,90 / -17,8% / 1,62).

Metric formulas copied VERBATIM from exp_park_jit_20260803/agg_metrics.py:64-73 so every
number here is directly comparable to the A/D/C/E table in
research/park_unpark_live_wiring_20260803.md §E2.
"""
import math
import sys

import numpy as np
import pandas as pd

CSV = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_"
       "shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_jit_A_control_univpit.csv")
ANN = 252.0


def metrics(nav):
    nav = nav.dropna().astype(float)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    sharpe = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr * 100, sharpe=sharpe, maxdd=dd * 100,
                calmar=(cagr / abs(dd)) if dd < 0 else float("nan"),
                final=nav.iloc[-1])


def cagr_of(nav):
    nav = nav.dropna().astype(float)
    if len(nav) < 5:
        return float("nan")
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    return ((nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1) * 100


def row(label, nav):
    m = metrics(nav)
    isr = cagr_of(nav[nav.index <= "2019-12-31"])
    oos = cagr_of(nav[nav.index >= "2020-01-01"])
    print(f"{label:34s} {m['cagr']:>7.2f}% {m['sharpe']:>6.2f} {m['maxdd']:>7.1f}% "
          f"{m['calmar']:>6.2f} {m['final']/1e9:>9.2f}B {isr:>7.2f}% {oos:>7.2f}%")
    return m


df = pd.read_csv(CSV, low_memory=False)
d = df[df.record_type == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").set_index("ymd")
for c in ("nav_bal_ref", "nav_lag_ref", "bal_cash_ref", "bal_stocks_ref", "bal_etf_ref",
          "lag_cash_ref", "lag_stocks_ref", "lag_etf_ref", "w_lag_tgt", "cap_bal",
          "cap_lag", "combined_nav", "state"):
    d[c] = pd.to_numeric(d[c], errors="coerce")

print("=" * 118)
print("GATE 0 — control CSV reproduces the pin")
print("=" * 118)
meta = df[df.record_type == "METRIC"].set_index("key")["value"]
print(f"  final_nav from METRIC record : {float(meta['final_nav_vnd'])/1e9:.4f}B   (pin = 1178.0099B)")
print(f"  final combined_nav DAILY     : {d['combined_nav'].iloc[-1]/1e9:.4f}B")
print(f"  sessions                     : {len(d)}   {d.index[0].date()} -> {d.index[-1].date()}")
ctrl = metrics(d["combined_nav"])
print(f"  recomputed  CAGR {ctrl['cagr']:.2f}%  Sharpe {ctrl['sharpe']:.2f}  "
      f"MaxDD {ctrl['maxdd']:.1f}%  Calmar {ctrl['calmar']:.2f}   (pin 28.86 / 1.90 / -17.8 / 1.62)")

# ----------------------------------------------------------------------------------
print()
print("=" * 118)
print("Q3 — DOES THE 2-BOOK + BAND ALLOCATOR ACTUALLY OPERATE IN THE SIMULATION?")
print("=" * 118)
w_act = d["cap_lag"] / d["combined_nav"]
w_tgt = d["w_lag_tgt"]
gap = (w_act - w_tgt).abs()
print(f"  sessions with w_lag_tgt present : {w_tgt.notna().sum()}")
print(f"  |w_actual - w_target| <= 10pp    : {(gap <= 0.10).sum()} / {len(gap.dropna())} "
      f"= {(gap <= 0.10).mean()*100:.2f}%")
print(f"  |w_actual - w_target| >  10pp    : {(gap > 0.10).sum()}  "
      f"(max breach {gap.max()*100:.2f}pp)")
print(f"  median gap {gap.median()*100:.2f}pp   p90 {gap.quantile(.90)*100:.2f}pp   "
      f"p99 {gap.quantile(.99)*100:.2f}pp")
reb = df[df.record_type == "REBAL"]
print(f"  REBAL events logged             : {len(reb)}  "
      f"(= {len(reb)/((d.index[-1]-d.index[0]).days/365.25):.1f} / year)")
print(f"  total rebalance friction paid   : {pd.to_numeric(reb['value']).sum()/1e6:.1f}tr VND")
print()
print("  target distribution (w_lag_tgt):")
for t, n in w_tgt.value_counts().sort_index().items():
    print(f"    tgt {t:.2f} : {n:5d} sessions ({n/len(d)*100:5.1f}%)")
print()
print("  -- but 'w_LAG' counts CASH + PARK as LAG. Real PEAD-stock deployment: --")
lag_tot = d["nav_lag_ref"]
bal_tot = d["nav_bal_ref"]
comp = pd.DataFrame({
    "LAG_stocks": d["lag_stocks_ref"] / lag_tot,
    "LAG_park": d["lag_etf_ref"] / lag_tot,
    "LAG_cash": d["lag_cash_ref"] / lag_tot,
    "BAL_stocks": d["bal_stocks_ref"] / bal_tot,
    "BAL_park": d["bal_etf_ref"] / bal_tot,
    "BAL_cash": d["bal_cash_ref"] / bal_tot,
})
print(comp.describe(percentiles=[.25, .5, .75]).T[["mean", "25%", "50%", "75%"]].to_string(
    float_format=lambda x: f"{x*100:6.1f}%"))
print()
print("  LAG book stock-weight by DT5G state (mean):")
for s in sorted(d["state"].dropna().unique()):
    m = d["state"] == s
    print(f"    state {int(s)}: n={m.sum():5d}  LAG_stocks {comp['LAG_stocks'][m].mean()*100:5.1f}%  "
          f"LAG_park {comp['LAG_park'][m].mean()*100:5.1f}%  LAG_cash {comp['LAG_cash'][m].mean()*100:5.1f}%  "
          f"| BAL_stocks {comp['BAL_stocks'][m].mean()*100:5.1f}%  BAL_park {comp['BAL_park'][m].mean()*100:5.1f}%")
print()
print("  share of sessions where LAG stock weight is...")
for lo, hi in [(0, .05), (.05, .20), (.20, .40), (.40, .60), (.60, 1.01)]:
    m = (comp["LAG_stocks"] >= lo) & (comp["LAG_stocks"] < hi)
    print(f"    [{lo*100:3.0f}%,{hi*100:4.0f}%) : {m.sum():5d} ({m.mean()*100:5.1f}%)")

# ----------------------------------------------------------------------------------
print()
print("=" * 118)
print("Q2 — PER-BOOK ATTRIBUTION (exact: the allocator combines two INDEPENDENT ledgers by scalar)")
print("=" * 118)
print(f"{'leg':34s} {'CAGR':>8s} {'Sharpe':>6s} {'MaxDD':>8s} {'Calmar':>6s} {'FinalNAV':>10s} "
      f"{'IS14-19':>8s} {'OOS20+':>8s}")
print("-" * 118)
ctrl_m = row("A control = V2.4 (pinned)", d["combined_nav"])
bal_m = row("BAL book alone (w_LAG=0)", bal_tot)
lag_m = row("LAG book alone (w_LAG=1)", lag_tot)
static = (0.35 * bal_tot / bal_tot.iloc[0] + 0.65 * lag_tot / lag_tot.iloc[0]) * 5e10
static_m = row("static 35/65, no band rebal", static)
naive = (0.5 * bal_tot / bal_tot.iloc[0] + 0.5 * lag_tot / lag_tot.iloc[0]) * 5e10
naive_m = row("static 50/50, no band rebal", naive)

print()
print("  delta vs control (A):")
for lbl, m in [("BAL alone", bal_m), ("LAG alone", lag_m),
               ("static 35/65", static_m), ("static 50/50", naive_m)]:
    print(f"    {lbl:22s} dCAGR {m['cagr']-ctrl_m['cagr']:+6.2f}pp  dSharpe {m['sharpe']-ctrl_m['sharpe']:+5.2f}  "
          f"dMaxDD {m['maxdd']-ctrl_m['maxdd']:+5.1f}pp  dCalmar {m['calmar']-ctrl_m['calmar']:+5.2f}")

print()
print("  correlation of daily returns BAL vs LAG: "
      f"{bal_tot.pct_change().corr(lag_tot.pct_change()):.3f}")
print()
print("  per-year book returns (%):")
yrs = sorted(set(d.index.year))
print(f"    {'year':6s} {'BAL':>8s} {'LAG':>8s} {'V2.4':>8s} {'VNI':>8s}")
vni = pd.to_numeric(d["vni_close"], errors="coerce")
for y in yrs:
    m = d.index.year == y
    if m.sum() < 5:
        continue
    b = (bal_tot[m].iloc[-1] / bal_tot[m].iloc[0] - 1) * 100
    l = (lag_tot[m].iloc[-1] / lag_tot[m].iloc[0] - 1) * 100
    c = (d["combined_nav"][m].iloc[-1] / d["combined_nav"][m].iloc[0] - 1) * 100
    v = (vni[m].iloc[-1] / vni[m].iloc[0] - 1) * 100
    print(f"    {y:6d} {b:+8.1f} {l:+8.1f} {c:+8.1f} {v:+8.1f}")

# ----------------------------------------------------------------------------------
print()
print("=" * 118)
print("Q1 — FUNDING ORDER: does PARK take 70-80% FIRST and block BAL/LAG, or take the RESIDUAL?")
print("=" * 118)
tx = df[df.record_type == "TX"].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
tx["buy_amount"] = pd.to_numeric(tx["buy_amount"], errors="coerce").fillna(0.0)
tx["sell_amount"] = pd.to_numeric(tx["sell_amount"], errors="coerce").fillna(0.0)
is_park = tx["play_type"] == "ETF_PARK"
print(f"  TX rows: {len(tx)}  (park {is_park.sum()}, stock {(~is_park).sum()})")
print()
print("  ORDER OF OPERATIONS inside one session (simulate_holistic_nav.py, block comments):")
print("    step 4c  ETF PRE-FILL  **SELL only**   -> releases park when state target drops")
print("    step 5   execute pending BAL/LAG BUYS  -> JIT sells park mid-buy if cash short")
print("    step 6   queue today's signals for T+1")
print("    step 6b  ETF POST-FILL SWEEP **BUY**   -> parks whatever cash is LEFT OVER")
print("  => park buys are structurally LAST. Verify with the reason tags on real rows:")
print()
pr = tx[is_park].copy()
pr["tag"] = pr["reason"].astype(str)
print(pr.groupby(["action", "tag"]).size().to_string())

# concrete NEUTRAL-period trace
print()
print("  ---- CONCRETE TRACE: a NEUTRAL stretch with real buy activity ----")
neutral = d[d["state"] == 3]
# pick a window where both stock buys and park activity happen
stock_buy = tx[(~is_park) & (tx.action == "buy")]
cand = stock_buy[stock_buy.ymd.isin(neutral.index)].groupby("ymd")["buy_amount"].sum()
cand = cand[(cand.index >= "2017-01-01") & (cand.index <= "2018-12-31")].sort_values(ascending=False)
focus_days = sorted(cand.head(4).index)
for day in focus_days:
    dd = d.loc[day]
    prev = d.index[d.index.get_loc(day) - 1]
    dp = d.loc[prev]
    print()
    print(f"  === {day.date()}  state={int(dd['state'])} (NEUTRAL)  "
          f"[prev session {prev.date()}] ===")
    for book, cash_c, stk_c, etf_c in [("BAL", "bal_cash_ref", "bal_stocks_ref", "bal_etf_ref"),
                                       ("LAG", "lag_cash_ref", "lag_stocks_ref", "lag_etf_ref")]:
        print(f"    {book}: open  cash {dp[cash_c]/1e9:7.3f}B  stocks {dp[stk_c]/1e9:7.3f}B  park {dp[etf_c]/1e9:7.3f}B")
        print(f"    {book}: close cash {dd[cash_c]/1e9:7.3f}B  stocks {dd[stk_c]/1e9:7.3f}B  park {dd[etf_c]/1e9:7.3f}B")
    t = tx[tx.ymd == day]
    for _, r in t.iterrows():
        kind = "PARK" if r["play_type"] == "ETF_PARK" else "STOCK"
        amt = r["buy_amount"] if r["action"] == "buy" else -r["sell_amount"]
        print(f"      {kind:5s} {r['book']:4s} {r['action']:4s} {str(r['ticker'])[:22]:22s} "
              f"{amt/1e6:+10.1f}tr  {str(r['reason'])[:30]}")

# aggregate proof: how often does a park BUY happen on a day that also has a stock buy,
# and is the park buy funded by residual (i.e. cash after stock buys)?
print()
print("  ---- AGGREGATE: park never pre-empts a stock buy ----")
days_stock_buy = set(stock_buy["ymd"])
park_buy = pr[pr.action == "buy"]
park_sell = pr[pr.action == "sell"]
print(f"  sessions with >=1 stock buy               : {len(days_stock_buy)}")
print(f"  sessions with >=1 park BUY                : {park_buy['ymd'].nunique()}")
print(f"  ... of which also had a stock buy same day: "
      f"{park_buy[park_buy.ymd.isin(days_stock_buy)]['ymd'].nunique()}")
print(f"  sessions with >=1 park SELL               : {park_sell['ymd'].nunique()}")
print(f"  ... of which also had a stock buy same day: "
      f"{park_sell[park_sell.ymd.isin(days_stock_buy)]['ymd'].nunique()}")
print(f"  total park BUY  volume : {park_buy['buy_amount'].sum()/1e9:10.1f}B")
print(f"  total park SELL volume : {park_sell['sell_amount'].sum()/1e9:10.1f}B")
print(f"  total stock BUY volume : {stock_buy['buy_amount'].sum()/1e9:10.1f}B")
print()
print("  KEY TEST — a buy is only 'blocked' if the engine drops it. Control leg reported")
print("  skipped_buys = 0 (research/park_unpark_live_wiring_20260803.md E2). With JIT on,")
print("  park NEVER causes a dropped buy; with JIT off it drops 8,995 (leg C).")
