"""Robustness: split cohort by liquidity (illiquid tercile vs rest) per episode, since the
actual sleeve candidates (TV1 UPCOM, DGC-post-shock) are specifically thin/illiquid names --
stale/thin pricing can artificially LOWER or artificially cluster measured correlation."""
import numpy as np, pandas as pd, json

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/discretionary_sleeve_correlation_20260830"

full = pd.read_parquet(f"{D}/full_with_peak.parquet")
full["time"] = pd.to_datetime(full["time"])
episodes = pd.read_csv(f"{D}/episodes.csv", parse_dates=["arm_date", "trough_date", "end_date"])
cohort = pd.read_csv(f"{D}/cohort_by_episode.csv")

full["tv"] = full["Close"] * full["Volume"]

def pairwise_corr_stats(sub):
    sub = sub.dropna(axis=1, thresh=15)
    if sub.shape[1] < 2:
        return None
    corr = sub.corr(min_periods=15)
    n = corr.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    vals = corr.values[mask]
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return None
    return dict(n_tickers=n, n_pairs=len(vals), mean_corr=float(np.mean(vals)),
                median_corr=float(np.median(vals)))

results = {}
for _, ep in episodes.iterrows():
    epc = cohort[cohort["episode"] == ep["episode"]].copy()
    win = full[(full["time"] >= ep["arm_date"]) & (full["time"] <= ep["end_date"])]
    # median ADV per ticker within window, for cohort members only
    adv = win[win["ticker"].isin(epc["ticker"])].groupby("ticker")["tv"].median()
    epc = epc.set_index("ticker")
    epc["adv"] = adv
    epc = epc.dropna(subset=["adv"])
    tercile = epc["adv"].quantile([1/3, 2/3])
    illiquid = epc[epc["adv"] <= tercile.iloc[0]].index.tolist()
    liquid = epc[epc["adv"] > tercile.iloc[1]].index.tolist()

    ret = win[win["ticker"].isin(epc.index)].sort_values(["ticker", "time"]).copy()
    ret["ret"] = ret.groupby("ticker")["Close"].pct_change()
    wide = ret.pivot(index="time", columns="ticker", values="ret")

    r_illiq = pairwise_corr_stats(wide[[c for c in illiquid if c in wide.columns]])
    r_liq = pairwise_corr_stats(wide[[c for c in liquid if c in wide.columns]])
    r_all = pairwise_corr_stats(wide)
    results[ep["episode"]] = dict(all=r_all, illiquid_tercile=r_illiq, liquid_tercile=r_liq,
                                   n_cohort=len(epc), adv_p33=float(tercile.iloc[0]), adv_p67=float(tercile.iloc[1]))
    print(ep["episode"], "ALL:", r_all, " ILLIQ:", r_illiq, " LIQ:", r_liq, flush=True)

with open(f"{D}/robustness_illiquid.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
