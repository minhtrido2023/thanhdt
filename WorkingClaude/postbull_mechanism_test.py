"""Fair test of the postbull MECHANISM (not the threshold) on long VNINDEX history 2000-2026 (incl 2008).
User's claim (2026-06-17): after a prolonged hot run (2Y return high) the market mean-reverts, often with
a SHARP correction; so buying a washout that hasn't corrected much yet (shallow dd) is dangerous.
Signal (production thresholds): dangerous = ret2y >= 0.60 AND dd-from-52w-high > -15% (shallow).
Test: forward outcome after 'dangerous' vs normal — does it lead to DEEPER subsequent drawdown / worse
return? And WHICH episodes fire (2007-pre-2008? 2018? 2021? 2025?)? This separates 'mechanism sound'
(holds across episodes) from 'threshold overfit' (helps only 2-3 in-window events).
"""
import numpy as np, pandas as pd
v = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/vnindex_full.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)
c = v["Close"].values; n = len(c)
RET2Y_THR, DD_THR = 0.60, -15.0
FWD = 250   # ~1 trading year forward

ret2y = np.full(n, np.nan); dd52 = np.full(n, np.nan)
fwd_trough = np.full(n, np.nan); fwd_ret = np.full(n, np.nan)
for t in range(n):
    if t >= 504: ret2y[t] = c[t]/c[t-504] - 1
    lo = max(0, t-251); hi52 = c[lo:t+1].max(); dd52[t] = (c[t]/hi52 - 1)*100
    if t+FWD < n:
        fwd_trough[t] = (c[t+1:t+FWD+1].min()/c[t] - 1)*100   # worst point over next 1y vs entry (further fall)
        fwd_ret[t]    = (c[t+FWD]/c[t] - 1)*100               # 1y forward return
v["ret2y"], v["dd52"], v["fwd_trough"], v["fwd_ret"] = ret2y, dd52, fwd_trough, fwd_ret
v["yr"] = v.time.dt.year
m = v.dropna(subset=["ret2y","dd52","fwd_trough","fwd_ret"]).copy()

danger = (m.ret2y >= RET2Y_THR) & (m.dd52 > DD_THR)          # hot 2Y bull + shallow dip
deep   = m.dd52 <= -25                                        # already deeply corrected (the 'safe' washout)
normal = ~danger

print(f"VNINDEX {v.time.min().date()}->{v.time.max().date()}, {len(m)} eval days\n")
print(f"{'cohort':40} {'n':>5} {'fwd-trough(further fall)':>24} {'fwd-1y-ret':>11}")
print("-"*84)
for lbl, mask in [("DANGEROUS (ret2y>=60% & dd>-15% shallow)", danger),
                  ("normal (everything else)", normal),
                  ("deep-washout (dd<=-25%, 'safe' buy)", deep),
                  ("ALL", pd.Series(True, index=m.index))]:
    s = m[mask]
    print(f"{lbl:40} {len(s):>5} {s.fwd_trough.mean():>10.1f}% (median {s.fwd_trough.median():>5.1f}%) "
          f"{s.fwd_ret.mean():>+9.1f}%")

# probability of a SHARP subsequent correction (further fall worse than -20%)
ps = lambda mask: (m[mask].fwd_trough <= -20).mean()*100
print(f"\nP(further fall < -20% within 1y): DANGEROUS {ps(danger):.0f}%  vs  normal {ps(normal):.0f}%  "
      f"vs deep-washout {ps(deep):.0f}%")

# WHICH episodes fire — group dangerous days into episodes by year
print("\nDANGEROUS-signal episodes (by year) + their realized forward outcome:")
for yr, g in m[danger].groupby("yr"):
    print(f"  {yr}: {len(g):>3} days | ret2y {g.ret2y.mean()*100:>3.0f}% dd {g.dd52.mean():>4.0f}% "
          f"-> fwd-trough {g.fwd_trough.mean():>6.1f}%  fwd-1y {g.fwd_ret.mean():>+6.1f}%")
