"""
Correlation-risk quantification for discretionary margin sleeve (job Taylor_20260830_035805).

Method:
1. Cohort = "fear-buy profile" stocks: at some point within a dd52<=-20% VNINDEX episode,
   the stock itself fell >=30% from its own trailing local peak (pre-crisis high, up to 400
   calendar days back) AND traded at PB<1.0 near the episode trough. This approximates the
   TV1/DGC profile (illiquid, deep-value, panic-sold) without cherry-picking specific tickers
   that didn't co-exist historically.
2. Crisis correlation = pairwise correlation of daily returns among cohort members, computed
   ONLY on days where VNINDEX dd52<=-0.20 (the exact 7 episodes, pooled).
3. Normal correlation = pairwise correlation of the SAME cohort tickers' daily returns on days
   where VNINDEX dd52>-0.10 (clear non-crisis), full 2007-2023 history, pooled.
4. Compare crisis vs normal correlation -> quantifies "correlation goes up in a panic" for
   exactly this stock profile, not a generic claim.
"""
import numpy as np, pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/discretionary_sleeve_correlation_20260830"
EXT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"

panel = pd.read_parquet(f"{D}/full_panel.parquet")
panel["time"] = pd.to_datetime(panel["time"])
panel = panel.sort_values(["ticker", "time"]).reset_index(drop=True)

episodes = pd.read_csv(f"{D}/episodes.csv", parse_dates=["arm_date", "trough_date", "end_date"])

vni = pd.read_csv(f"{EXT}/daily_panel.csv", usecols=["time", "dd52"])
vni["time"] = pd.to_datetime(vni["time"])

# ---------- Step 1: per-ticker rolling local peak (400 calendar days back), then dd_stock ----------
panel = panel.set_index("time")
peaks = []
for tkr, g in panel.groupby("ticker"):
    g = g.sort_index()
    peak = g["Close"].rolling("400D", min_periods=20).max()
    peaks.append(pd.DataFrame({"ticker": tkr, "time": g.index, "Close": g["Close"].values,
                                "Volume": g["Volume"].values, "PB": g["PB"].values,
                                "peak400": peak.values}))
full = pd.concat(peaks, ignore_index=True)
full["dd_stock"] = full["Close"] / full["peak400"] - 1.0
panel = panel.reset_index()

full.to_parquet(f"{D}/full_with_peak.parquet", index=False)
print("peak calc done", full.shape, flush=True)
