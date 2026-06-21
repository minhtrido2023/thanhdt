# -*- coding: utf-8 -*-
"""
crisis_release.py — Unconfirmed-CRISIS release overlay (price-confirm + time-box).

Problem (diagnosed 2026-06-02): the Ngu Hanh r_score classification fires CRISIS
on a sharp-but-brief dip and then HOLDS it for months even as price recovers, with
no macro confirmation. Recurrent false positives: 2016-08, 2023-10, 2024-05 (the last
held 78 sessions at 0% while VNINDEX rose +3.3%, max intra-window DD only -4.4%).

Rule (point-in-time, NO look-ahead): inside a raw-CRISIS segment, downgrade to NEUTRAL
on any session where ALL hold:
  (1) time-box:   d >= K sessions since CRISIS segment start
  (2) price-confirm broken: Close has recovered to/above the de-risk entry level
                  (Close >= entry_px) and held there for the last P sessions
  (3) no macro:   macro_confirmed flag is False on that session (optional layer;
                  default all-False when no macro feed supplied -> price arm only)
Re-evaluated DAILY and symmetric: if price falls back below entry, CRISIS resumes.
Real crises (2008/2018/2020/2022) keep making lower lows -> Close never reclaims entry
-> CRISIS preserved. COVID-2020 (held far too late by base system) gets released into
the recovery once price reclaims entry — a bonus, not a regression.

Pure function so it can wrap any state series in the family (Tinh Te / DT / v3.4b / DT5G).
"""
import numpy as np
import pandas as pd

CRISIS, BEAR, NEUTRAL = 1, 2, 3


def apply_crisis_release(state: pd.Series, close: pd.Series,
                         K: int = 20, margin: float = 0.0, hold: int = 3,
                         downgrade_to: int = NEUTRAL,
                         macro_confirmed: pd.Series | None = None) -> pd.Series:
    """state, close indexed by DATE (aligned). Returns a new state Series.

    K       : time-box — min sessions in CRISIS before release is even considered
    margin  : price must reclaim entry_px*(1+margin) to count as recovered
    hold    : recovery must persist this many consecutive sessions
    """
    state = state.copy()
    idx = state.index
    close = close.reindex(idx).ffill()
    if macro_confirmed is None:
        macro_confirmed = pd.Series(False, index=idx)
    else:
        macro_confirmed = macro_confirmed.reindex(idx).fillna(False).astype(bool)

    out = state.values.copy()
    s = state.values
    c = close.values
    mc = macro_confirmed.values

    entry_px = np.nan
    d = 0                      # sessions since segment start
    recov_run = 0             # consecutive sessions Close >= entry threshold
    in_crisis = False
    for i in range(len(s)):
        if s[i] == CRISIS:
            if not in_crisis:           # segment start
                in_crisis = True
                entry_px = c[i]
                d = 0
                recov_run = 0
            else:
                d += 1
            thr = entry_px * (1.0 + margin)
            recov_run = recov_run + 1 if c[i] >= thr else 0
            unconfirmed = (d >= K) and (recov_run >= hold) and (not mc[i])
            if unconfirmed:
                out[i] = downgrade_to
            # else keep CRISIS
        else:
            in_crisis = False
            entry_px = np.nan
            d = 0
            recov_run = 0
    return pd.Series(out, index=idx, name=state.name)


def segments(state: pd.Series, value=CRISIS):
    """Yield (start_date, end_date, n_sessions) for each contiguous run == value."""
    s = state.values
    idx = state.index
    i = 0
    n = len(s)
    while i < n:
        if s[i] == value:
            j = i
            while j + 1 < n and s[j + 1] == value:
                j += 1
            yield (idx[i], idx[j], j - i + 1)
            i = j + 1
        else:
            i += 1


if __name__ == "__main__":
    import sys
    WORK = r"/home/trido/thanhdt/WorkingClaude"
    vix = pd.read_csv(f"{WORK}/data/VNINDEX.csv", parse_dates=["time"])
    close = vix.set_index("time")["Close"].sort_index()

    families = {
        "canonical_TinhTe": "data/vnindex_5state.csv",
        "DT_10_25_25":      "data/vnindex_5state_dt_10_25_25.csv",
        "v3.4b":            "data/vnindex_5state_tam_quan_v3_4b_full_history.csv",
        "DT5G(state_raw)":  "data/vnindex_5state_dt5g_live.csv",
    }
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    margin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    hold = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    print(f"=== CRISIS-RELEASE overlay  K={K}  margin={margin:.1%}  hold={hold} ===\n")
    REAL = {"2008-01-22", "2018-03-19", "2020-03-16", "2021-12-27", "2022-11-01",
            "2011-03-04", "2007-03-15"}
    FALSE = {"2016-08-30", "2023-10-23", "2024-05-14"}
    for name, f in families.items():
        d = pd.read_csv(f"{WORK}/{f}")
        col = "state_raw" if name.startswith("DT5G") else ("state" if "state" in d.columns else d.columns[1])
        st = d.assign(time=pd.to_datetime(d[d.columns[0]])).set_index("time")[col].astype(int)
        st = st[~st.index.duplicated(keep="last")].sort_index()
        new = apply_crisis_release(st, close, K=K, margin=margin, hold=hold)
        before = list(segments(st)); after = list(segments(new))
        bdays = int((st == CRISIS).sum()); adays = int((new == CRISIS).sum())
        print(f"--- {name} ---  CRISIS days {bdays} -> {adays}  (released {bdays-adays}); "
              f"segments {len(before)} -> {len([s for s in after])}")
        # per-segment: how many CRISIS days remain after overlay, tagged false/real
        for (s0, s1, n) in before:
            rem = int((new.loc[s0:s1] == CRISIS).sum())
            tag = ""
            key = str(s0.date())
            if key in FALSE: tag = "  <-- FALSE-POS (should shrink)"
            if key in REAL:  tag = "  <-- REAL crisis (should be ~unchanged)"
            if tag:
                print(f"      {s0.date()}->{s1.date()}  {n:3d} CRISIS days  -> {rem:3d} after overlay{tag}")
        print()
