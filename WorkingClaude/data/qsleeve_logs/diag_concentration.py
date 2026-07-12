#!/usr/bin/env python
"""Q-SLEEVE concentration + capacity diagnostic (gate §7, plan_quality_sleeve_20260712.md).
Rebuilds the trial sleeve per-name daily decomposition offline (same build_pit env) and
attributes the sleeve-vs-custom30V excess on DEPLOYED capital per name.
Usage: BQ_LOCAL_CACHE=data/bq_cache <env of trial> python diag_concentration.py <trial_tag> <topn> <gate|none> <qfloor 0|1>
"""
import sys, os, glob, math
import numpy as np, pandas as pd

os.chdir("/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
import custom_basket as cb

DATA = "data"
tag, topn, gate_s, qfloor = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
gate = None if gate_s == "none" else int(gate_s)
if qfloor == "1": os.environ["BASKET_QFLOOR"] = "1"

def find_csv(t):
    g = glob.glob(f"{DATA}/v23_golive_audit_2014_now_*_exp_qsleeve_{t}.csv")
    assert len(g) == 1, (t, g)
    return g[0]

START, END = "2014-01-02", "2026-06-19"
# trial sleeve (ew) — env BASKET_SELECT/LIQ_FLOOR set by caller
lvl_t, adv_t, mem_t, bx_t = cb.build_pit(bq, START, END, top_n=topn, quality="none",
                                         rebal="q2m5", gate_rating=gate, weight_scheme="ew")
# incumbent custom30V (production params: top30, gate 3, namecap 0.10) — clean env for floors
os.environ.pop("BASKET_QFLOOR", None); os.environ.pop("BASKET_LIQ_FLOOR_B", None)
lvl_c, _, _, _ = cb.build_pit(bq, START, END, top_n=30, quality="none",
                              rebal="q2m5", gate_rating=3, weight_scheme="namecap")

# daily panel of trial members
px = bx_t.pivot_table(index="time", columns="ticker", values="Close").sort_index()
ret = px.pct_change()
mem_t["rebal_date"] = pd.to_datetime(mem_t["rebal_date"])
rebals = sorted(mem_t["rebal_date"].unique())
mem_by_rd = {rd: list(mem_t[mem_t["rebal_date"] == rd]["ticker"]) for rd in rebals}

sc = pd.Series(lvl_c).sort_index()
rc = sc.pct_change()

# park deployment from the trial run CSV
df = pd.read_csv(find_csv(tag), low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").groupby("ymd").last()
for c in ("bal_etf_ref", "lag_etf_ref", "bal_cash_ref", "lag_cash_ref", "combined_nav", "state"):
    d[c] = pd.to_numeric(d[c], errors="coerce")
d["park"] = d["bal_etf_ref"].fillna(0) + d["lag_etf_ref"].fillna(0)
d["cash"] = d["bal_cash_ref"].fillna(0) + d["lag_cash_ref"].fillna(0)

contrib = {}          # ticker -> VND contribution to sleeve-vs-c30v excess on deployed capital
max_name_pct_nav = []  # daily max single-name %NAV
ri = 0
days = [t for t in d.index if t in ret.index]
for t in days:
    while ri + 1 < len(rebals) and rebals[ri + 1] <= t: ri += 1
    if rebals[ri] > t: continue
    members = mem_by_rd[rebals[ri]]
    r_row = ret.loc[t, [m for m in members if m in ret.columns]].dropna()
    if r_row.empty: continue
    n = len(r_row); w = 1.0 / n
    pv = d.loc[t, "park"]
    if not np.isfinite(pv) or pv <= 0:
        max_name_pct_nav.append(0.0); continue
    rc_t = rc.get(t, np.nan)
    if not np.isfinite(rc_t): continue
    for m, rv in r_row.items():
        contrib[m] = contrib.get(m, 0.0) + pv * w * (rv - rc_t)
    max_name_pct_nav.append(pv * w / d.loc[t, "combined_nav"] * 100)

cs = pd.Series(contrib).sort_values(ascending=False)
tot = cs.sum()
print(f"=== {tag}: per-name attribution of sleeve-vs-custom30V excess (deployed capital) ===")
print(f"total excess (VND B): {tot/1e9:+.2f}")
top = cs.head(12) / 1e9
for k, v in top.items():
    share = cs[k] / tot * 100 if tot != 0 else float("nan")
    print(f"  {k:6s} {v:+8.2f}B  share {share:+6.1f}%")
neg = cs.tail(5) / 1e9
print("worst 5:", "  ".join(f"{k}:{v:+.2f}B" for k, v in neg.items()))
if tot > 0:
    mx = cs.max() / tot * 100
    print(f"MAX single-name share of total edge: {cs.idxmax()} = {mx:.1f}%  -> {'FAIL (>40%)' if mx > 40 else 'PASS (<=40%)'}")
else:
    print("total excess <= 0 -> edge-share test moot (no positive edge to concentrate)")
mp = pd.Series(max_name_pct_nav)
print(f"max single-name %NAV: max {mp.max():.2f}%  p99 {mp.quantile(0.99):.2f}%  mean-when-deployed {mp[mp>0].mean():.2f}%")

# capacity: park fill vs 0.7*(cash+park) on NEUTRAL days, trial vs its own target
neu = d[d["state"] == 3]
tgt = 0.7 * (neu["cash"] + neu["park"])
sh = ((tgt - neu["park"]).clip(lower=0) / tgt.replace(0, np.nan)).dropna()
print(f"NEUTRAL park fill-shortfall: mean {sh.mean()*100:.2f}%  p95 {sh.quantile(0.95)*100:.2f}%  days>5%: {(sh>0.05).sum()}/{len(sh)}")

# turnover: membership churn per rebal
prev = None; churn = []
for rd in rebals:
    cur = set(mem_by_rd[rd])
    if prev is not None and prev:
        churn.append(len(cur - prev) / max(len(prev), 1))
    prev = cur
print(f"membership churn per rebal: mean {np.mean(churn)*100:.0f}%  median {np.median(churn)*100:.0f}%")
