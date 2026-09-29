# -*- coding: utf-8 -*-
"""build_exitkey_series.py — rebuild the LAG edge-health trailing-12M series keyed on
EXIT date (= the date the return becomes knowable) instead of ENTRY date.

Defect being measured (found 2026-09-10, job Taylor_20260910_131906, documented in
research/bal_edge_gate_20260910/CONCLUSION_*.md muc 2):
  data/lag_edge_health.csv keys its trailing-12M stats on ENTRY date, but an event's
  return is only knowable 25 sessions AFTER entry (edge_health_monitor.py:160-165:
  entry pos = T+5 after release, exit pos+25). LIVE that is harmless (the file only
  ever holds COMPLETED events, last row ~5 weeks old, allocator ffills a stale-but-real
  value). In BACKTEST it is not: pt_v23_audit_2014.py:2057-2059 reindexes the
  entry-keyed series across all of 2014-2026 with ffill, so on historical day d the
  gate reads a mean12 that required data from d+25 sessions.

DESIGN — deliberately minimal, so the A/B differs in ONE thing only:
  We do NOT rebuild the cohort. We take the (entry, ret) pairs VERBATIM from
  data/lag_edge_health.csv and only compute, for each entry date, the exit date via
  the SAME price calendar the producer used (earnings_px.pkl pivot index, +25
  sessions). Therefore treatment and control share identical events and identical
  returns; the ONLY difference is the date axis the trailing-12M window is keyed on.
  (Rebuilding the cohort here would re-run a daily-refreshed cache and risk a
  cohort-drift confound on top of the keying effect we are trying to size.)

Reuses the exit-keyed windowing logic from
research/bal_edge_gate_20260910/make_causal_ledger.py (mean12_av/win12_av/n12_av).

Output: lag_edge_health_exitkey.csv  columns entry,exit,ret,mean12,win12,n12,
        mean12_av,win12_av,n12_av
  - mean12/win12/n12  = production entry-keyed values, copied through unchanged
                        (kept for like-for-like diffing; NOT read by the treatment leg)
  - *_av              = exit-keyed (causally available) values; the treatment leg
                        reads mean12_av indexed on `exit`.

NEVER writes data/lag_edge_health.csv (that schema is a production contract).
"""
import os, pickle
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
SRC = os.path.join(WORKDIR, "data", "lag_edge_health.csv")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lag_edge_health_exitkey.csv")
HOLD = 25   # book hold horizon, verbatim from edge_health_monitor.py::lag_edge_health()

# --- price calendar, identical construction to the producer -------------------
with open(os.path.join(WORKDIR, "data", "earnings_px.pkl"), "rb") as f:
    px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
pxc = (px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first")
         .sort_index().ffill(limit=5))
idx = pxc.index
print(f"calendar sessions={len(idx):,}  {idx[0].date()} -> {idx[-1].date()}")

d = pd.read_csv(SRC, parse_dates=["entry"])
print(f"source rows={len(d):,}  entries {d['entry'].min().date()} -> {d['entry'].max().date()}")

# --- entry -> exit via the SAME calendar --------------------------------------
uniq = pd.DatetimeIndex(sorted(d["entry"].unique()))
pos = idx.get_indexer(uniq)
assert (pos >= 0).all(), f"{(pos<0).sum()} entry dates not on the price calendar"
assert (pos + HOLD < len(idx)).all(), "an entry lacks a complete 25-session hold"
emap = dict(zip(uniq, idx[pos + HOLD]))
d["exit"] = d["entry"].map(emap)
lag_days = (d["exit"] - d["entry"]).dt.days
print(f"exit lag calendar-days: min={lag_days.min()} median={lag_days.median():.0f} max={lag_days.max()}")

# --- exit-keyed trailing-12M (logic reused from make_causal_ledger.py) --------
d = d.sort_values(["exit", "entry"]).reset_index(drop=True)
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

d[["entry", "exit", "ret", "mean12", "win12", "n12",
   "mean12_av", "win12_av", "n12_av"]].to_csv(DST, index=False)
print(f"wrote {DST}  rows={len(d):,}")

# --- self-check A: the entry-keyed window recomputed on OUR frame must equal the
#     production column (proves the windowing code is faithful; any delta later is
#     the KEYING, not the window arithmetic).
d2 = d.sort_values(["entry"]).reset_index(drop=True)
en = d2["entry"].values.astype("datetime64[ns]")
r2 = d2["ret"].values
lo2 = np.searchsorted(en, en - yr, side="right")
hi2 = np.searchsorted(en, en, side="right")
cs2 = np.concatenate([[0.0], np.cumsum(r2)])
n2 = (hi2 - lo2).astype(float)
m_re = (cs2[hi2] - cs2[lo2]) / np.where(n2 > 0, n2, np.nan)
dev = np.nanmax(np.abs(m_re - d2["mean12"].values))
print(f"SELF-CHECK A  max|recomputed entry-keyed mean12 - production mean12| = {dev:.3e}"
      f"   -> {'PASS' if dev < 1e-9 else 'FAIL'}")

# --- self-check B: gate-relevant comparison on the allocator's own axis --------
common = idx[(idx >= "2014-01-01") & (idx <= "2026-06-19")]
s_en = d.drop_duplicates("entry").set_index("entry").sort_index()["mean12"].reindex(common, method="ffill")
s_ex = d.drop_duplicates("exit").set_index("exit").sort_index()["mean12_av"].reindex(common, method="ffill")
g_en = (s_en.notna() & (s_en >= 4.0))
g_ex = (s_ex.notna() & (s_ex >= 4.0))
print(f"\nALLOCATOR AXIS 2014-01-01..2026-06-19  N={len(common):,} sessions")
print(f"  entry-keyed  >=4%: {g_en.mean()*100:5.1f}% of sessions   NaN={s_en.isna().sum()}")
print(f"  exit-keyed   >=4%: {g_ex.mean()*100:5.1f}% of sessions   NaN={s_ex.isna().sum()}")
print(f"  sessions where the gate DISAGREES: {(g_en != g_ex).sum():,} "
      f"({(g_en != g_ex).mean()*100:.1f}%)")
print(f"  mean|delta mean12| = {np.nanmean(np.abs(s_en - s_ex)):.3f} pp, "
      f"max = {np.nanmax(np.abs(s_en - s_ex)):.3f} pp")
flip = pd.DataFrame({"entry_keyed": g_en, "exit_keyed": g_ex})
flip["blk"] = (flip["entry_keyed"] != flip["exit_keyed"]).ne(
    (flip["entry_keyed"] != flip["exit_keyed"]).shift()).cumsum()
dis = flip[flip["entry_keyed"] != flip["exit_keyed"]]
print(f"  disagreement runs (independent episodes) = {dis['blk'].nunique()}")
if len(dis):
    seg = dis.groupby("blk").apply(
        lambda g: pd.Series({"from": g.index[0].date(), "to": g.index[-1].date(),
                             "n_sess": len(g), "entry_says_tilt": bool(g["entry_keyed"].iloc[0])}),
        include_groups=False)
    print(seg.to_string())
