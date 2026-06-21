"""Golden-eggs (capit) experiments (user 2026-06-16):
  Q1: RELAX the quality gate — current ROE_Min5Y>=12% judges on the worst-5Y year (excludes recovered
      one-off scars). Test through-cycle variants. Does relaxing help or DILUTE the golden edge?
  Q2: does the 8L-v2 ABSOLUTE valuation axis (1/PE) change the golden basket if used to define "cheap"
      instead of / alongside pb_z (relative dislocation)?
Universe = capit's 12 washout events; golden = deep-cheap within gate; hold 60d (profit_3M). Equal-weight
within event, then equal-weight across the 12 events (so no single big event dominates). win = profit_3M>0.
"""
import numpy as np, pandas as pd
d = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/golden_gate_test.csv", parse_dates=["time"])
d = d[d.liq >= 2e9].copy()                       # capit liquidity floor ~2B
d["ey"] = np.where(d.PE > 0, 1.0/d.PE, np.nan)

def perf(mask):
    """equal-weight within event, then mean across events; + win-rate and avg picks/event."""
    s = d[mask]
    if not len(s): return (np.nan, np.nan, 0, 0)
    per_ev = s.groupby("time")["profit_3M"]
    ev_ret = per_ev.mean()                        # basket return per event
    win = (s["profit_3M"] > 0).mean()*100         # name-level win rate
    return (ev_ret.mean(), win, s.groupby("time").size().mean(), len(s))

# quality gates
GATES = {
 "baseline ROE_Min5Y>=12 (current)": (d.ROE_Min5Y>=0.12) & (d.ROIC5Y>=0.10) & (d.FSCORE>=6),
 "relax-A ROE_Min3Y>=12 (recent-3Y floor)": (d.ROE_Min3Y>=0.12) & (d.ROIC5Y>=0.10) & (d.FSCORE>=6),
 "relax-B ROE5Y>=12 (avg, allow 1 bad yr)": (d.ROE5Y>=0.12) & (d.ROIC5Y>=0.10) & (d.FSCORE>=6),
 "relax-C ROE5Y>=12 & ROE_Min3Y>=0 (avg+recent-clean)": (d.ROE5Y>=0.12)&(d.ROE_Min3Y>=0)&(d.ROIC5Y>=0.10)&(d.FSCORE>=6),
}
GOLDEN = d.pb_z <= -1.0
print("="*92)
print("Q1: golden-eggs (pb_z<=-1 within gate) — forward profit_3M by QUALITY GATE")
print(f"{'gate':52} {'fwd':>7} {'win%':>6} {'avg/ev':>7} {'total':>6}")
print("-"*92)
for lbl, g in GATES.items():
    r = perf(g & GOLDEN)
    print(f"{lbl:52} {r[0]:>+6.2f}% {r[1]:>5.0f}% {r[2]:>6.1f} {r[3]:>6}")
print(f"\n  (reference) ALL gated baseline, NO golden filter: fwd {perf(GATES['baseline ROE_Min5Y>=12 (current)'])[0]:+.2f}%")
print(f"  (reference) universe (liq>=2B, no gate, no golden): fwd {perf(d.liq>=0)[0]:+.2f}%")

# which names does relax ADD vs baseline (golden set)?
base_g = d[GATES["baseline ROE_Min5Y>=12 (current)"] & GOLDEN]
for lbl in ["relax-B ROE5Y>=12 (avg, allow 1 bad yr)", "relax-C ROE5Y>=12 & ROE_Min3Y>=0 (avg+recent-clean)"]:
    add = d[GATES[lbl] & GOLDEN & ~d.index.isin(base_g.index)]
    print(f"  {lbl[:24]} ADDS {len(add)} golden picks baseline missed: "
          f"{', '.join(sorted(add.ticker.unique()))[:90]}  (their fwd {perf(d.index.isin(add.index))[0]:+.2f}%)")

# Q2: valuation axis — define "cheap" by pb_z vs absolute 1/PE vs both (within baseline gate)
print("\n" + "="*92)
print("Q2: within baseline gate — 'cheap' defined by RELATIVE pb_z vs ABSOLUTE 1/PE vs BOTH")
gate = GATES["baseline ROE_Min5Y>=12 (current)"]
d["ey_pct"] = d.groupby("time")["ey"].transform(lambda s: s.rank(pct=True))   # absolute-yield percentile per event
defs = {
 "pb_z<=-1 (current golden)":          gate & (d.pb_z<=-1),
 "1/PE top-25% (absolute cheap)":      gate & (d.ey_pct>=0.75),
 "BOTH pb_z<=-1 AND ey top-50%":       gate & (d.pb_z<=-1) & (d.ey_pct>=0.5),
 "EITHER pb_z<=-1 OR ey top-15%":      gate & ((d.pb_z<=-1) | (d.ey_pct>=0.85)),
}
print(f"{'cheap definition':40} {'fwd':>7} {'win%':>6} {'avg/ev':>7} {'total':>6}")
print("-"*92)
for lbl, m in defs.items():
    r = perf(m); print(f"{lbl:40} {r[0]:>+6.2f}% {r[1]:>5.0f}% {r[2]:>6.1f} {r[3]:>6}")
# overlap pb_z-golden vs absolute-cheap
pbz_set = set(d[gate & (d.pb_z<=-1)].index); ey_set = set(d[gate & (d.ey_pct>=0.75)].index)
ov = len(pbz_set & ey_set)/max(len(pbz_set),1)*100
print(f"\n  overlap: {ov:.0f}% of pb_z-golden are ALSO in 1/PE-top25% -> "
      f"{'redundant (same names)' if ov>60 else 'fairly orthogonal (different names)'}")
