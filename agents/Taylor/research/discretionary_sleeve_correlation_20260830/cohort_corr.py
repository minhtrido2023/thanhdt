"""
Step 2: cohort selection per episode + crisis-vs-normal correlation.
"""
import numpy as np, pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/discretionary_sleeve_correlation_20260830"
EXT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"

full = pd.read_parquet(f"{D}/full_with_peak.parquet")
full["time"] = pd.to_datetime(full["time"])
episodes = pd.read_csv(f"{D}/episodes.csv", parse_dates=["arm_date", "trough_date", "end_date"])
vni = pd.read_csv(f"{EXT}/daily_panel.csv", usecols=["time", "dd52"])
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.set_index("time")["dd52"]

# ---------- cohort selection: within each episode window, ticker dd_stock<=-30% at some point
# AND PB<1.0 within +/-15 calendar days of that trough point (deep value confirmed near the low) ----------
cohort_rows = []
for _, ep in episodes.iterrows():
    win = full[(full["time"] >= ep["arm_date"]) & (full["time"] <= ep["end_date"])].copy()
    win = win.dropna(subset=["dd_stock"])
    if win.empty:
        print(f"{ep['episode']}: NO DATA in window"); continue
    # per ticker: worst dd_stock in window, and PB at that worst point
    idx = win.groupby("ticker")["dd_stock"].idxmin()
    worst = win.loc[idx, ["ticker", "time", "dd_stock", "PB", "Close"]].rename(
        columns={"time": "worst_time", "PB": "pb_at_worst"})
    qualify = worst[(worst["dd_stock"] <= -0.30) & (worst["pb_at_worst"] > 0) & (worst["pb_at_worst"] < 1.0)]
    qualify = qualify.copy()
    qualify["episode"] = ep["episode"]
    cohort_rows.append(qualify)
    print(f"{ep['episode']}: window rows={len(win)}, tickers_in_window={win['ticker'].nunique()}, "
          f"qualify(dd<=-30%,PB<1)={len(qualify)}", flush=True)

cohort = pd.concat(cohort_rows, ignore_index=True)
cohort.to_csv(f"{D}/cohort_by_episode.csv", index=False)
print("\ntotal cohort rows (ticker x episode):", len(cohort))
print("distinct tickers pooled:", cohort["ticker"].nunique())

# ---------- daily returns for cohort tickers, full period ----------
cohort_tickers = sorted(cohort["ticker"].unique())
ret_panel = full[full["ticker"].isin(cohort_tickers)].copy()
ret_panel = ret_panel.sort_values(["ticker", "time"])
ret_panel["ret"] = ret_panel.groupby("ticker")["Close"].pct_change()
ret_panel = ret_panel.dropna(subset=["ret"])
ret_panel = ret_panel.merge(vni.rename("vni_dd52"), left_on="time", right_index=True, how="left")

wide = ret_panel.pivot(index="time", columns="ticker", values="ret")
wide_dd52 = ret_panel.groupby("time")["vni_dd52"].first().reindex(wide.index)

crisis_days = wide_dd52 <= -0.20
normal_days = wide_dd52 > -0.10

def pairwise_corr_stats(sub):
    sub = sub.dropna(axis=1, thresh=30)  # need >=30 obs to trust a pair
    if sub.shape[1] < 2:
        return None
    corr = sub.corr(min_periods=30)
    n = corr.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    vals = corr.values[mask]
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return None
    return dict(n_tickers=n, n_pairs=len(vals), mean_corr=float(np.mean(vals)),
                median_corr=float(np.median(vals)), p10=float(np.percentile(vals, 10)),
                p90=float(np.percentile(vals, 90)), n_obs_days=int(sub.notna().any(axis=1).sum()))

print("\n--- POOLED crisis correlation (all 7 episodes, dd52<=-0.20 days) ---")
res_crisis = pairwise_corr_stats(wide.loc[crisis_days.fillna(False)])
print(res_crisis)

print("\n--- POOLED normal correlation (SAME cohort tickers, dd52>-0.10 days, full 2007-2023) ---")
res_normal = pairwise_corr_stats(wide.loc[normal_days.fillna(False)])
print(res_normal)

# ---------- per-episode crisis correlation ----------
print("\n--- per-episode crisis correlation ---")
per_ep = {}
for _, ep in episodes.iterrows():
    m = (wide.index >= ep["arm_date"]) & (wide.index <= ep["end_date"])
    r = pairwise_corr_stats(wide.loc[m])
    per_ep[ep["episode"]] = r
    print(ep["episode"], r)

import json
with open(f"{D}/corr_results.json", "w") as f:
    json.dump({"crisis_pooled": res_crisis, "normal_pooled": res_normal, "per_episode": per_ep,
               "cohort_tickers": cohort_tickers}, f, indent=2, default=str)
print("\nsaved corr_results.json")
