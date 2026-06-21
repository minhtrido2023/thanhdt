"""Capitulation-buy reframed (user 2026-06-16): the OLD golden-eggs (deepest pb_z<=-1 + strictest quality)
adds little value, picks too FEW + ILLIQUID names (capacity trap). User's thesis: in a panic, buy GOOD,
HIGH-ATTENTION (= liquid) names that are CHEAP ENOUGH (not necessarily deepest) — liquidity lets you
deploy size AND lowers risk, and well-watched names bounce easier. Candidate universe = custom30.
Test at the 12 capit events: forward profit_3M + COUNT (deployable breadth) + LIQUIDITY, vs old golden.
"""
import numpy as np, pandas as pd
WD = "/home/trido/thanhdt/WorkingClaude"
d = pd.read_csv(f"{WD}/data/golden_gate_test.csv", parse_dates=["time"])
d = d[d.liq >= 2e9].copy()
d["ey"] = np.where(d.PE > 0, 1.0/d.PE, np.nan)
# custom30 membership as-of each event
mem = pd.read_csv(f"{WD}/data/custom30_membership.csv", parse_dates=["effective_from", "effective_to"])
mem["effective_to"] = mem.effective_to.fillna(pd.Timestamp("2100-01-01"))
iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in mem.groupby("ticker")}
d["cust30"] = d.apply(lambda r: any(f <= np.datetime64(r.time) < t for f, t in iv.get(r.ticker, [])), axis=1)
events_with_c30 = d[d.cust30].time.nunique()
print(f"custom30 covers {events_with_c30}/12 events (2014-05 event predates custom30 start 2014-08)\n")

def perf(mask):
    s = d[mask]
    if not len(s): return dict(fwd=np.nan, win=np.nan, avg=0, n=0, liq=np.nan)
    return dict(fwd=s.groupby("time")["profit_3M"].mean().mean(),
                win=(s.profit_3M > 0).mean()*100,
                avg=s.groupby("time").size().mean(), n=len(s),
                liq=s.liq.median()/1e9)   # median liquidity (bn VND/day) = deployability proxy

strict = (d.ROE_Min5Y >= 0.12) & (d.ROIC5Y >= 0.10) & (d.FSCORE >= 6)
variants = {
 "OLD golden: pb_z<=-1 + strict-quality":      strict & (d.pb_z <= -1),
 "custom30 ALL (no cheapness filter)":          d.cust30,
 "custom30 + pb_z<0 (below own avg)":           d.cust30 & (d.pb_z < 0),
 "custom30 + pb_z<=-0.5 (cheap enough)":        d.cust30 & (d.pb_z <= -0.5),
 "custom30 + pb_z<=-1 (deep, within liquid)":   d.cust30 & (d.pb_z <= -1),
 "custom30 + ey top-50% (cheap-enough abs)":    d.cust30 & (d.groupby("time")["ey"].transform(lambda s: s.rank(pct=True)) >= 0.5),
}
print(f"{'variant':46} {'fwd':>7} {'win%':>6} {'avg/ev':>7} {'total':>6} {'medLiq':>8}")
print("-"*92)
for lbl, m in variants.items():
    r = perf(m)
    print(f"{lbl:46} {r['fwd']:>+6.2f}% {r['win']:>5.0f}% {r['avg']:>6.1f} {r['n']:>6} {r['liq']:>6.1f}bn")

# liquidity contrast: old-golden picks vs custom30 picks
og = d[strict & (d.pb_z <= -1)]; c30 = d[d.cust30 & (d.pb_z < 0)]
print(f"\n  LIQUIDITY (median bn/day): OLD-golden {og.liq.median()/1e9:.1f}  vs  custom30+pb_z<0 {c30.liq.median()/1e9:.1f}  "
      f"-> {c30.liq.median()/max(og.liq.median(),1):.0f}x more deployable")
print(f"  BREADTH (picks over 12 events): OLD-golden {len(og)}  vs  custom30+pb_z<0 {len(c30)}")
# downside: worst-case per name (p25 of forward) — risk proxy
print(f"  DOWNSIDE p25 fwd: OLD-golden {og.profit_3M.quantile(.25):+.1f}%  vs  custom30+pb_z<0 {c30.profit_3M.quantile(.25):+.1f}%")
