"""User principle (2026-06-16): usable 5Y through-cycle floors (ROE_Min5Y, ROIC_Min5Y, ROE5Y, ROIC5Y...)
— if GOOD, ADD points (proven long track record = credibility/stability); if missing/weak, NO bonus but
NOT excluded. Data decides WHICH floors are worth rewarding (forward return AND downside/crash, like P3).
"""
import numpy as np, pandas as pd
WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/zone_bt_panel.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]")
d = df[df.turnover >= 5e9].copy()
FWD = "profit_3M"
uni_f = d.groupby("ym")[FWD].mean().mean()
uni_c = (d[FWD] < -20).mean()*100
print(f"universe: fwd {uni_f:+.2f}%  P(crash<-20%) {uni_c:.1f}%   (n={len(d)})\n")
print(f"{'5Y-good floor':32} {'pass%':>6} {'fwd':>7} {'Δfwd':>6} {'crash%':>7} {'Δcrash':>7}")
print("-"*74)
floors = {
    "ROE_Min5Y > 0  (5Y no-loss)":     d.ROE_Min5Y > 0,
    "ROE_Min5Y > 0.10":                d.ROE_Min5Y > 0.10,
    "ROE_Min3Y > 0  (3Y no-loss)":     d.ROE_Min3Y > 0,
    "ROIC_Min5Y > 0.08":               d.ROIC_Min5Y > 0.08,
    "ROIC_Min5Y > 0.12":               d.ROIC_Min5Y > 0.12,
    "ROE5Y > 0.15  (high 5Y avg)":     d.ROE5Y > 0.15,
    "ROIC5Y > 0.12":                   d.ROIC5Y > 0.12,
}
res = {}
for lbl, m in floors.items():
    s = d[m]
    f = s.groupby("ym")[FWD].mean().mean()
    c = (s[FWD] < -20).mean()*100
    res[lbl] = (m, f, c)
    print(f"{lbl:32} {m.mean()*100:>5.0f}% {f:>+6.2f}% {f-uni_f:>+5.2f} {c:>6.1f}% {c-uni_c:>+6.1f}")

# combined track-record COUNT (how many of the strong floors a name passes)
strong = [d.ROE_Min5Y > 0, d.ROIC_Min5Y > 0.10, d.ROE5Y > 0.15, d.ROIC5Y > 0.12, d.CF_OA_5Y > 0]
d["track"] = sum(x.astype(int) for x in strong)   # 0..5
print(f"\ntrack-record COUNT (0-5 strong 5Y floors passed) — fwd + crash by count:")
for k in range(6):
    s = d[d.track == k]
    if len(s) < 100: continue
    f = s.groupby("ym")[FWD].mean().mean(); c = (s[FWD] < -20).mean()*100
    print(f"  count={k}: n={len(s):>6}  fwd {f:>+6.2f}%  crash {c:>5.1f}%")
print("  -> if fwd rises &/or crash falls with count, a graded track-record BONUS is justified")
