# -*- coding: utf-8 -*-
"""make_causal_ledger.py — add CAUSALLY-AVAILABLE rolling stats to the BAL shadow ledger.

WHY (defect found 2026-09-10, job Taylor_20260910_131906):
lag_edge_health.csv indexes its trailing-12M stats on ENTRY date, but an event's return is
only knowable 25 sessions AFTER entry. LIVE that is harmless (the file only ever contains
COMPLETED events, so the last row is ~5 weeks old and the allocator ffills a stale-but-real
value). In BACKTEST it is not: pt_v23_audit_2014.py reindexes the same entry-indexed series
across all of 2014-2026, so on historical day d the gate reads a mean12 that required data
from d+25 sessions. For BAL the hold is 45 sessions, so the same construction would leak
~9 weeks. This script therefore keys the gate series on EXIT date (= availability date).

Adds: mean12_av / win12_av / n12_av  = trailing-12M stats over events whose EXIT <= d,
evaluated on the exit-date axis. These are the ONLY columns a gate may read.
Keeps entry-indexed mean12/win12/n12 for like-for-like comparison with lag_edge_health.csv.
"""
import sys
import numpy as np, pandas as pd

src, dst = sys.argv[1], sys.argv[2]
d = pd.read_csv(src, parse_dates=["entry", "exit"])
d = d.sort_values(["exit", "entry", "ticker"]).reset_index(drop=True)

ex = d["exit"].values.astype("datetime64[ns]")
r = d["ret"].values
yr = np.timedelta64(365, "D")
lo = np.searchsorted(ex, ex - yr, side="right")
hi = np.searchsorted(ex, ex, side="right")          # inclusive of same-exit-day siblings
cs = np.concatenate([[0.0], np.cumsum(r)])
cw = np.concatenate([[0.0], np.cumsum((r > 0).astype(float))])
n = (hi - lo).astype(float)
d["n12_av"] = n
d["mean12_av"] = (cs[hi] - cs[lo]) / np.where(n > 0, n, np.nan)
d["win12_av"] = (cw[hi] - cw[lo]) / np.where(n > 0, n, np.nan) * 100.0
d.to_csv(dst, index=False)

print(f"wrote {dst}  rows={len(d):,}")
print(f"latest exit={d['exit'].iloc[-1].date()}  mean12_av={d['mean12_av'].iloc[-1]:.2f}%"
      f"  n12_av={int(d['n12_av'].iloc[-1])}  win12_av={d['win12_av'].iloc[-1]:.1f}%")

# what a gate keyed on exit-date would READ at the open of each signal episode
d2 = d.sort_values("entry").reset_index(drop=True)
epi = (d2["entry"].diff().dt.days.fillna(0) > 60).cumsum()
av = d.sort_values("exit")
rows = []
for k, g in d2.groupby(epi):
    d0 = g["entry"].iloc[0]
    prior = av[av["exit"] < d0]
    if len(prior):
        w = prior[prior["exit"] > d0 - pd.Timedelta(days=365)]["ret"]
        m12 = w.mean() if len(w) else np.nan
        nn = len(w)
        age = (d0 - prior["exit"].iloc[-1]).days
    else:
        m12, nn, age = np.nan, 0, np.nan
    rows.append(dict(episode=k, open=d0.date(), gate_mean12_av=round(float(m12), 2) if pd.notna(m12) else None,
                     gate_n12_av=nn, staleness_days=age,
                     episode_n=len(g), episode_mean_ret=round(g["ret"].mean(), 2),
                     episode_win=round((g["ret"] > 0).mean() * 100, 1)))
print("\nGATE READING AT EPISODE OPEN (causal, exit-indexed) vs WHAT THE EPISODE ACTUALLY DID:")
print(pd.DataFrame(rows).to_string(index=False))
