"""
Derive frozen (IS-only, no OOS peeking) T1-accruals floor parameters for the R3 backtest, from the
SAME panel already fetched+used by Phase 0/0b (../panel_raw.csv, ../sector_liquidity_raw.csv) —
no new BQ query, no re-estimation on data the R3 engine will later score.

Reproduces phase0b_analyze.py's V1(a) absolute cutoff and V1(c) sector-demean cutoff EXACTLY
(same IS window release_year 2014-2019, same ICB_Code grouping, same quantile(0.80)) and ALSO
dumps the per-ICB_Code IS mean (sector_mean_is) needed by the R3 engine to demean an OOS
observation's accr_q before comparing to the demean cutoff — phase0b_analyze.py computed this
mean internally but never persisted it, so it must be rederived here, not re-invented.
"""
import json
import pandas as pd

df = pd.read_csv("../panel_raw.csv")
df["Release_Date"] = pd.to_datetime(df["Release_Date"])
sl = pd.read_csv("../sector_liquidity_raw.csv")
sl["Release_Date"] = pd.to_datetime(sl["Release_Date"])

merged = df.merge(sl[["ticker", "quarter", "ICB_Code", "adv_30d", "n_days_30d"]],
                   on=["ticker", "quarter"], how="left")
assert len(merged) == len(df), "merge changed row count"
work = merged[merged["release_year"] >= 2014].copy()
t1 = work.dropna(subset=["accr_q", "persist_2q"]).copy()

t1_is = t1[t1["release_year"].between(2014, 2019)]

IS_CUTOFF_ABS = float(t1_is["accr_q"].quantile(0.80))
assert abs(IS_CUTOFF_ABS - 0.04503380316885901) < 1e-9, f"abs cutoff drifted: {IS_CUTOFF_ABS}"

sector_mean_is = t1_is.dropna(subset=["ICB_Code"]).groupby("ICB_Code")["accr_q"].mean()
t1_is_c = t1_is.dropna(subset=["ICB_Code"]).copy()
t1_is_c["accr_q_demean"] = t1_is_c["accr_q"] - t1_is_c["ICB_Code"].map(sector_mean_is)
DEMEAN_CUTOFF = float(t1_is_c["accr_q_demean"].quantile(0.80))
assert abs(DEMEAN_CUTOFF - 0.03926703369961876) < 1e-9, f"demean cutoff drifted: {DEMEAN_CUTOFF}"

params = {
    "is_window": "release_year 2014-2019 (phase0b prereg IS window)",
    "abs_cutoff": IS_CUTOFF_ABS,
    "demean_cutoff": DEMEAN_CUTOFF,
    "sector_mean_is": {str(int(k)): float(v) for k, v in sector_mean_is.items()},
    "n_sectors_with_is_mean": int(len(sector_mean_is)),
    "note": "unseen ICB_Code (not in sector_mean_is) at OOS lookup -> demean uses raw accr_q "
            "(mean=0.0 fallback), identical convention to phase0b_analyze.py line 120.",
}
with open("t1floor_params.json", "w") as f:
    json.dump(params, f, indent=2)
print(f"abs_cutoff={IS_CUTOFF_ABS:.6f}  demean_cutoff={DEMEAN_CUTOFF:.6f}  "
      f"n_sectors={len(sector_mean_is)}  -> wrote t1floor_params.json")
