# -*- coding: utf-8 -*-
"""exp_dc3book_bootstrap_20260825.py — R&D: validate the factor x regime
(BAL/LAG/DC gross-by-state) matrix from phase-2 Part C with bootstrap CI +
OOS (3-period) stability check.

Job Taylor_20260825_153800 (dispatch from Mike), Giai doan 3 Phan 2. RESEARCH
ONLY. Reads exp_dc3book_c1_stateswap_univpit.csv (written by Part 1 of this
same job, cwd) -- state(t)/r_bal(t)/r_lag(t)/r_dc(t) already assembled there.

"gross" convention (reverse-engineered + verified exact match against
phase-2 Part C's published table, C_creative_alternatives.md): arithmetic
annualization, gross = mean(daily_return_in_state) * 252. NOT geometric
compounding. Verified: NEUTRAL/BULL/EXBULL gross_BAL/LAG/DC all match
phase-2's table to 2 decimals under this convention.

Method
------
1. Bootstrap (paired by day-index, not independent per factor -- preserves
   the real day-to-day correlation between BAL/LAG/DC returns): per state,
   resample N day-indices WITH replacement, 1000 times; for each resample
   compute gross_BAL/LAG/DC (arithmetic annualized) + pairwise diffs
   (BAL-LAG, BAL-DC, LAG-DC). Report 5th/95th pct CI for each gross AND each
   diff. A diff's CI containing 0 => "leadership not statistically settled at
   90% confidence" for that pair in that state.
2. OOS stability: split into 3 calendar periods (pre-2017-01-01,
   2017-01-01..2019-12-31, 2020-01-01+), recompute the raw (unbootstrapped)
   gross-by-state table per period, check whether the SAME factor leads in
   each state across all 3 periods (or if leadership flips between periods).
"""
import os
import sys

import numpy as np
import pandas as pd

OUTDIR = os.path.dirname(os.path.abspath(__file__))
SRC_CSV = os.path.join(OUTDIR, "exp_dc3book_c1_stateswap_univpit.csv")

STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
FACTORS = [("r_bal", "BAL"), ("r_lag", "LAG"), ("r_dc", "DC")]
N_BOOT = 1000
ANN = 252
RNG_SEED = 20260825  # fixed seed for reproducibility (not "randomness" per se -- documented, not hidden)


def gross_arith(returns_array):
    return float(np.nanmean(returns_array) * ANN)


def bootstrap_state(df_state, rng):
    """Returns dict: factor -> array of N_BOOT gross values, plus pairwise
    diff arrays, all via a SINGLE paired resample of day-indices per draw."""
    n = len(df_state)
    r_bal = df_state["r_bal"].values
    r_lag = df_state["r_lag"].values
    r_dc = df_state["r_dc"].values

    boot_bal = np.empty(N_BOOT)
    boot_lag = np.empty(N_BOOT)
    boot_dc = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        boot_bal[b] = gross_arith(r_bal[idx])
        boot_lag[b] = gross_arith(r_lag[idx])
        boot_dc[b] = gross_arith(r_dc[idx])

    return {
        "BAL": boot_bal, "LAG": boot_lag, "DC": boot_dc,
        "BAL_minus_LAG": boot_bal - boot_lag,
        "BAL_minus_DC": boot_bal - boot_dc,
        "LAG_minus_DC": boot_lag - boot_dc,
    }


def pct_ci(arr, lo=5, hi=95):
    return float(np.percentile(arr, lo)), float(np.percentile(arr, hi))


def main():
    df = pd.read_csv(SRC_CSV, parse_dates=["date"])
    df = df.dropna(subset=["r_bal", "r_lag", "r_dc"])
    rng = np.random.default_rng(RNG_SEED)

    print("=" * 100)
    print(f"BOOTSTRAP CI (N={N_BOOT} resamples, paired by day-index, 5th-95th pct) "
          f"— gross = mean(daily r)*252 arithmetic annualized")
    print("=" * 100)

    ci_rows = []
    for s in sorted(STATE_NAMES):
        sub = df[df["state"] == s]
        n = len(sub)
        if n < 5:
            print(f"{STATE_NAMES[s]}: N={n} too small, skip")
            continue
        boot = bootstrap_state(sub, rng)
        print(f"\n--- {STATE_NAMES[s]} (N={n} sessions) ---")
        point = {f: gross_arith(sub[c].values) for c, f in FACTORS}
        for fname in ["BAL", "LAG", "DC"]:
            lo, hi = pct_ci(boot[fname])
            print(f"  gross_{fname:<3}: point={point[fname]*100:>7.2f}%  "
                  f"CI[{lo*100:>7.2f}%, {hi*100:>7.2f}%]")
            ci_rows.append((STATE_NAMES[s], n, f"gross_{fname}", point[fname] * 100, lo * 100, hi * 100))
        for pair, label in [("BAL_minus_LAG", "BAL-LAG"), ("BAL_minus_DC", "BAL-DC"), ("LAG_minus_DC", "LAG-DC")]:
            lo, hi = pct_ci(boot[pair])
            contains_zero = lo <= 0 <= hi
            flag = "  <-- CI chua 0 (khong chac chan)" if contains_zero else ""
            print(f"  diff {label:<8}: CI[{lo*100:>7.2f}pp, {hi*100:>7.2f}pp]{flag}")
            ci_rows.append((STATE_NAMES[s], n, f"diff_{label}", None, lo * 100, hi * 100))

    ci_df = pd.DataFrame(ci_rows, columns=["state", "n", "metric", "point_pct", "ci_lo_pct", "ci_hi_pct"])
    ci_csv = os.path.join(OUTDIR, "exp_dc3book_bootstrap_ci.csv")
    ci_df.to_csv(ci_csv, index=False)
    print(f"\nwrote {ci_csv}")

    # ---- OOS stability: 3 calendar periods ----
    print("\n" + "=" * 100)
    print("OOS STABILITY — gross-by-state recomputed per calendar period (raw, not bootstrapped)")
    print("=" * 100)
    periods = [
        ("pre-2017", df["date"] < "2017-01-01"),
        ("2017-2020", (df["date"] >= "2017-01-01") & (df["date"] < "2020-01-01")),
        ("2020-now", df["date"] >= "2020-01-01"),
    ]
    stab_rows = []
    leadership = {}  # state -> {period: winning_factor}
    for s in sorted(STATE_NAMES):
        leadership[s] = {}
        print(f"\n--- {STATE_NAMES[s]} ---")
        for pname, mask in periods:
            sub = df[(df["state"] == s) & mask]
            n = len(sub)
            if n < 10:
                print(f"  {pname:<12} N={n:<5} too thin, skip")
                leadership[s][pname] = None
                continue
            gvals = {fname: gross_arith(sub[col].values) for col, fname in FACTORS}
            winner = max(gvals, key=gvals.get)
            leadership[s][pname] = winner
            print(f"  {pname:<12} N={n:<5} BAL={gvals['BAL']*100:>7.2f}%  "
                  f"LAG={gvals['LAG']*100:>7.2f}%  DC={gvals['DC']*100:>7.2f}%  -> leader={winner}")
            stab_rows.append((STATE_NAMES[s], pname, n, gvals["BAL"] * 100, gvals["LAG"] * 100,
                               gvals["DC"] * 100, winner))

    print("\n--- Leadership consistency across the 3 periods ---")
    for s in sorted(STATE_NAMES):
        winners = [w for w in leadership[s].values() if w is not None]
        consistent = len(set(winners)) <= 1 if winners else None
        tag = "CONSISTENT" if consistent else ("MIXED" if consistent is False else "N/A (too thin)")
        print(f"  {STATE_NAMES[s]:<8}: winners={list(leadership[s].items())} -> {tag}")

    stab_df = pd.DataFrame(stab_rows, columns=["state", "period", "n", "gross_bal_pct",
                                                "gross_lag_pct", "gross_dc_pct", "leader"])
    stab_csv = os.path.join(OUTDIR, "exp_dc3book_oos_stability.csv")
    stab_df.to_csv(stab_csv, index=False)
    print(f"\nwrote {stab_csv}")


if __name__ == "__main__":
    main()
