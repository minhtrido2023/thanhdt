# -*- coding: utf-8 -*-
"""exp_dc3book_capacity_20260825.py — R&D: capacity sizing for the 16-name DC
universe at 100B and 200B NAV.

Job Taylor_20260825_153800 (dispatch from Mike), Giai doan 3 Phan 3. RESEARCH
ONLY. Reads data/bq_cache/ticker/2026.parquet (local cache, no live BQ query).

ADV proxy: Trading_Value column (Price*Volume, derived -- CLAUDE.md flags it
as NOT valid for VWAP, but it IS the standard proxy for a currency-denominated
average-daily-value capacity check, which is what this is). ADV_60d = mean of
the last 60 sessions in-cache (through 2026-08-24); ADV_20d also reported as
the more conservative/recent reference the dispatch asked for.

Sizing convention: max_pos_5pct_adv = 0.05 * ADV_60d (position that could be
built/unwound in ONE session without exceeding 5% of that session's average
value traded -- standard conservative single-day capacity threshold).
max_pos_10pct_adv reported alongside as the looser reference.

Implied position under the current per-name cap rule (cap 0.20 of book,
CLAUDE.md custom30 convention) at two DC book-weight scenarios:
  - w_DC=0.333 (static 3-book 1/3-1/3-1/3, phase-2 Part A/C4's own scenario --
    phase 2 already flagged DHG 890%/MSH 205% ADV under this exact scenario;
    recomputed here fresh from a fresh cache pull for cross-check).
  - w_DC=0.46  (C1 BULL-only swap, this job's Part A -- nav_lag_share matches
    the real w_lag_tgt(t) during BULL, ~0.46-0.65 depending on era; 0.46 used
    as the conservative/typical value quoted in the dispatch and phase-2 C1).
Implied position = 0.20 * w_DC * NAV; recommendation compares it against the
5%-ADV threshold, not against the static cap-driven number alone -- a name
can pass "cap doesn't force overshoot" yet still be a genuinely thin market.
"""
import os

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUTDIR = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(WORKDIR, "data", "bq_cache", "ticker", "2026.parquet")

DC_UNIVERSE = ["MBB", "ACB", "HDB", "TCB", "VCB", "SSI", "VCI", "VND", "HCM",
               "FPT", "PVT", "HAH", "CTR", "MSH", "DHG", "DBC"]

CAP_PER_NAME = 0.20
W_DC_SCENARIOS = {"w033_static3book": 1.0 / 3.0, "w046_c1_bullswap": 0.46}
NAV_SCALES = {"100B": 100e9, "200B": 200e9}
ADV_THRESHOLD = 0.05  # 5% ADV/session, standard
ADV_THRESHOLD_REF = 0.10  # 10% reference


def main():
    df = pd.read_parquet(CACHE, columns=["time", "ticker", "Close", "Volume", "Trading_Value"])
    df = df[df["ticker"].isin(DC_UNIVERSE)].copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(["ticker", "time"])

    print(f"Cache window: {df['time'].min().date()} -> {df['time'].max().date()}, "
          f"{df['ticker'].nunique()}/{len(DC_UNIVERSE)} DC tickers found")
    missing = set(DC_UNIVERSE) - set(df["ticker"].unique())
    if missing:
        print(f"⚠️ MISSING from cache: {sorted(missing)}")

    rows = []
    for tk in DC_UNIVERSE:
        sub = df[df["ticker"] == tk].sort_values("time")
        if sub.empty:
            rows.append(dict(ticker=tk, n_sessions=0, adv_60d=np.nan, adv_20d=np.nan))
            continue
        adv_60d = sub["Trading_Value"].tail(60).mean()
        adv_20d = sub["Trading_Value"].tail(20).mean()
        rows.append(dict(ticker=tk, n_sessions=len(sub), adv_60d=adv_60d, adv_20d=adv_20d))

    adv_df = pd.DataFrame(rows).set_index("ticker")

    adv_df["max_pos_5pct_adv"] = adv_df["adv_60d"] * ADV_THRESHOLD
    adv_df["max_pos_10pct_adv"] = adv_df["adv_60d"] * ADV_THRESHOLD_REF
    for nav_label, nav_val in NAV_SCALES.items():
        adv_df[f"max_pos_5pct_pct_nav_{nav_label}"] = adv_df["max_pos_5pct_adv"] / nav_val * 100

    for scen_label, w_dc in W_DC_SCENARIOS.items():
        for nav_label, nav_val in NAV_SCALES.items():
            implied_pos = CAP_PER_NAME * w_dc * nav_val
            col = f"implied_pos_{scen_label}_{nav_label}"
            adv_df[col] = implied_pos
            adv_df[f"pct_adv_{scen_label}_{nav_label}"] = implied_pos / adv_df["adv_60d"] * 100

    def recommend(row):
        # worst case across both scenarios/NAV scales (conservative -- if it
        # fails the most aggressive combo, flag it)
        worst_pct_adv = max(
            row["pct_adv_w033_static3book_100B"], row["pct_adv_w033_static3book_200B"],
            row["pct_adv_w046_c1_bullswap_100B"], row["pct_adv_w046_c1_bullswap_200B"])
        max_pos_pct_nav_200B = row["max_pos_5pct_pct_nav_200B"]
        if worst_pct_adv <= 100.0:  # implied position stays within 100% ADV even worst case
            if worst_pct_adv <= 5.0:
                return "OK"
            return "CAP_NEEDED"
        # worst case blows past 100% ADV -- check if a 5%-ADV-safe position is even meaningful
        if max_pos_pct_nav_200B < 0.5:
            return "EXCLUDE"
        return "CAP_NEEDED"

    adv_df["recommendation"] = adv_df.apply(recommend, axis=1)

    print("\n" + "=" * 130)
    print("CAPACITY SIZING — DC universe (16 mã), ADV_60d proxy = Trading_Value (Price*Volume)")
    print("=" * 130)
    disp = adv_df[["n_sessions", "adv_60d", "adv_20d", "max_pos_5pct_adv",
                    "max_pos_5pct_pct_nav_100B", "max_pos_5pct_pct_nav_200B",
                    "pct_adv_w033_static3book_100B", "pct_adv_w033_static3book_200B",
                    "pct_adv_w046_c1_bullswap_100B", "pct_adv_w046_c1_bullswap_200B",
                    "recommendation"]].copy()
    for c in ["adv_60d", "adv_20d", "max_pos_5pct_adv"]:
        disp[c] = disp[c] / 1e9  # VND -> billion VND for readability
    disp = disp.rename(columns={"adv_60d": "adv_60d_B", "adv_20d": "adv_20d_B",
                                 "max_pos_5pct_adv": "max_pos_5pctADV_B"})
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print(disp.round(2).to_string())

    outcsv = os.path.join(OUTDIR, "exp_dc3book_capacity_sizing.csv")
    adv_df.reset_index().to_csv(outcsv, index=False)
    print(f"\nwrote {outcsv}")

    print("\n--- Recommendation summary ---")
    print(adv_df["recommendation"].value_counts())
    print("\nEXCLUDE candidates:", list(adv_df[adv_df["recommendation"] == "EXCLUDE"].index))
    print("CAP_NEEDED candidates:", list(adv_df[adv_df["recommendation"] == "CAP_NEEDED"].index))

    print("\n--- Securities sub-group (SSI/VCI/VND/HCM) re-confirm at both NAV scales ---")
    sec = adv_df.loc[[t for t in ["SSI", "VCI", "VND", "HCM"] if t in adv_df.index]]
    print(sec[["adv_60d", "pct_adv_w046_c1_bullswap_100B", "pct_adv_w046_c1_bullswap_200B",
               "recommendation"]].round(2))


if __name__ == "__main__":
    main()
