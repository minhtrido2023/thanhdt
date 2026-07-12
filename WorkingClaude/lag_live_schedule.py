# -*- coding: utf-8 -*-
"""
lag_live_schedule.py
====================
Point-in-time LAG/PEAD candidate builder for the LIVE recommender path.

WHY THIS EXISTS (audit Taylor_20260712_121642, R1 CRITICAL): the historical
event file `data/earnings_events_classified.csv` (written by
refresh_lagged_caches.py) only contains an event once ALL FOUR price marks
exist — including Close at release+30 sessions. A freshly released event
therefore appears in that CSV ~30 trading sessions (~6 weeks) AFTER release,
while the LAG entry is release+5 sessions. Any live consumer scheduling
entries off that CSV is structurally blind to every new event until the entry
window has long passed (silently — no error). During an earnings season this
suppresses 100% of new LAG entries in the money-path
(golive_recommend_v23.py -> DollarBill plan).

FIX: candidacy only needs facts knowable ON the release date —
  Release_Date + NP_R          -> earnings_surprise_data.pkl (full re-pull daily,
                                  row exists from Release_Date; verified fresh)
  surprise_B_MA (NP_P0 vs mean NP_P1..P4)
                               -> same pkl
  prior_n_good / pa_HL3        -> history of the ticker's PRIOR good events'
                                  post_ret. Priors are >= 1 quarter (~60
                                  sessions) old, so they always have their full
                                  price windows and live in the classified CSV.
So this module takes event IDENTITY from the pkl (visible same-day) and PRIOR
HISTORY from the CSV (always mature for priors) — no waiting for the new
event's own release+30 price.

SCOPE: LIVE scheduling only. The classified CSV keeps its exact old semantics
(full windows, used by backtests pt_v23_audit_2014.py / pt_v22_dt5g.py full
replay) — this module does not touch it and nothing in the backtest path
imports this module. Formulas below (surprise_B_MA, prior_n_good, pa_HL3,
gates) are verbatim mirrors of the pinned R3 logic
(pt_v23_audit_2014.py / old golive_recommend_v23.py block, refresh_lagged_caches.py).

Parity guarantee (see lag_live_schedule_selfcheck.py): restricted to events the
old CSV-only path could see, this module returns the IDENTICAL qualify decision
for all 51,209 historical events, with identical prior_n_good / pa_HL3 / tier
everywhere EXCEPT same-day-sibling releases (a ticker publishing two quarters on
one date — 2 events in the full history: BOT 2026-01-28, CT6 2026-02-02). The
old walk counted the same-day sibling as "prior" using its post_ret (a value not
knowable until release+30 — a 30-session look-ahead inside the prior feature,
and CSV-row-order-dependent for the tie). This module uses strictly-earlier
priors only (`<`), which is the only definition computable ON the release date;
neither event's qualify decision changes. On top of parity it also sees events
released after the CSV's maturity horizon (the point of the fix).
"""
import os, pickle
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# gates — verbatim from the pinned R3 LAG spec (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5)
NP_R_MIN, PRIOR_N_MIN, PA_HL3_MIN = 15.0, 4, 5.0
FLOOR = 1e9                    # surprise_B_MA denominator floor (same as old block)
LN2, HL = np.log(2), 3.0       # pa_HL3 half-life = 3 years


def live_lag_candidates(start=None, workdir=WORKDIR, pkl_path=None, csv_path=None):
    """Return the point-in-time LAG candidacy table for events known TODAY.

    start: optional inclusive lower bound on Release_Date (e.g. golive's 120d window).
    Returns a DataFrame with one row per event:
      ticker, quarter, Release_Date, NP_R (in %, like the classified CSV),
      surprise_B_MA, prior_n_good, pa_HL3, tier (LAG_HI/LAG_LO), qualify (bool).
    Raises on missing/unreadable inputs — callers (golive) wrap in try/except
    and fail loud with a WARNING, same as the old CSV path.
    """
    pkl_path = pkl_path or os.path.join(workdir, "data", "earnings_surprise_data.pkl")
    csv_path = csv_path or os.path.join(workdir, "data", "earnings_events_classified.csv")

    # event identity + same-day-knowable fields, from the daily-fresh pkl
    with open(pkl_path, "rb") as f:
        fin = pickle.load(f)
    fin = fin[fin["Release_Date"].notna()].copy()
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    fin["exp_B_MA"] = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
    fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"])
                            / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
    fin["NP_R_pct"] = fin["NP_R"] * 100.0   # classified CSV stores NP_R in %; keep that unit

    if start is not None:
        fin = fin[fin["Release_Date"] >= pd.Timestamp(start)].copy()
    fin = fin.sort_values(["ticker", "Release_Date", "quarter"]).reset_index(drop=True)

    # prior history: the ticker's GOOD mature events (NP_R>=15, post_ret known) from the
    # classified CSV — same accumulation rule as the old walk, vectorized per ticker
    ev = pd.read_csv(csv_path, parse_dates=["Release_Date"])
    good = ev[ev["NP_R"].notna() & (ev["NP_R"] >= NP_R_MIN) & ev["post_ret"].notna()]
    good = good.sort_values(["ticker", "Release_Date"], kind="stable")
    hist = {tk: (g["Release_Date"].values.astype("datetime64[ns]"), g["post_ret"].to_numpy(float))
            for tk, g in good.groupby("ticker")}

    n_prior = np.zeros(len(fin), dtype=int)
    pa_hl3 = np.full(len(fin), np.nan)
    for i, r in enumerate(fin.itertuples()):
        da, pa = hist.get(r.ticker, (None, None))
        if da is None:
            continue
        m = da < np.datetime64(r.Release_Date)   # strictly-prior good events only
        k = int(m.sum())
        n_prior[i] = k
        if k:
            yrs = (np.datetime64(r.Release_Date) - da[m]) / np.timedelta64(1, "D") / 365.25
            w = np.exp(-LN2 * yrs / HL)
            if w.sum() > 0:
                pa_hl3[i] = float((pa[m] * w).sum() / w.sum())

    out = fin[["ticker", "quarter", "Release_Date"]].copy()
    out["NP_R"] = fin["NP_R_pct"]
    out["surprise_B_MA"] = fin["surprise_B_MA"].fillna(0)   # old path: merge+fillna(0)
    out["prior_n_good"] = n_prior
    out["pa_HL3"] = pa_hl3
    out["tier"] = np.where(out["surprise_B_MA"] > 0.5, "LAG_HI", "LAG_LO")
    out["qualify"] = (out["NP_R"].fillna(-999) >= NP_R_MIN) \
        & (out["prior_n_good"] >= PRIOR_N_MIN) \
        & (out["pa_HL3"].fillna(-999) >= PA_HL3_MIN)
    return out
