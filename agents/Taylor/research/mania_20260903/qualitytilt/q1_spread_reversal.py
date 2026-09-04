import pandas as pd, numpy as np, os
W = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/mania_20260903"
d = pd.read_csv(os.path.join(W, "qualitytilt/mania_daily_full.csv"), parse_dates=["time"]).reset_index(drop=True)
n = len(d)
loglow = d.logret_low.to_numpy()
loghigh = d.logret_high.to_numpy()
# quality MINUS junk daily log-return spread (opposite sign of spread21 which was junk-minus-quality)
qmj = loglow - loghigh

def fwd_cumret(end_idx, h):
    # cumulative (quality - junk) log-return spread over h sessions starting at end_idx+1 (post-episode)
    lo = end_idx + 1
    hi = end_idx + h
    if hi >= n:
        return np.nan
    return qmj[lo:hi+1].sum()

def unconditional_dist(h, step=5):
    # base rate: same-length window starting at every `step`-th session in panel (non-overlapping-ish sample)
    vals = []
    for i in range(0, n - h, step):
        v = qmj[i+1:i+1+h].sum() if i+1+h <= n else np.nan
        # actually window [i, i+h)
        v = qmj[i:i+h].sum()
        if not np.isnan(v):
            vals.append(v)
    return np.array(vals)

HORIZONS = {"1M": 21, "3M": 63, "6M": 126, "12M": 252}

for tag, epfile in [("N7_main(p90/p75)", "mania_episodes.csv"), ("N14_wide(p85/p60)", "qualitytilt/episodes_n14.csv")]:
    E = pd.read_csv(os.path.join(W, epfile))
    print(f"\n=== {tag}, N={len(E)} episodes ===")
    for hname, h in HORIZONS.items():
        ep_vals = []
        for _, row in E.iterrows():
            end_idx = int(row.end_idx) if "end_idx" in row else None
            ep_vals.append(end_idx)
        # recompute end_idx by locating end date in d.time if not present (N7 file lacks end_idx)
        if "end_idx" not in E.columns:
            time_to_idx = {pd.Timestamp(t).date(): i for i, t in enumerate(d.time)}
            ep_vals = [time_to_idx.get(pd.Timestamp(row.end).date()) for _, row in E.iterrows()]
        vals = [fwd_cumret(ei, h) for ei in ep_vals]
        vals = np.array([v for v in vals if v is not None and not np.isnan(v)])
        base = unconditional_dist(h)
        if len(vals) == 0:
            print(f"  {hname}: no episodes with full forward data")
            continue
        ep_mean = vals.mean()
        base_mean = base.mean()
        base_std = base.std()
        # percentile rank of episode mean within base distribution (bootstrap of same-size sample means)
        rng = np.random.default_rng(42)
        boot_means = np.array([base[rng.integers(0, len(base), len(vals))].mean() for _ in range(2000)])
        pctile = (boot_means < ep_mean).mean()
        print(f"  {hname}: n_ep={len(vals)} ep_mean={100*ep_mean:+.2f}% ep_median={100*np.median(vals):+.2f}% "
              f"base_mean(unconditional,n={len(base)})={100*base_mean:+.2f}% excess={100*(ep_mean-base_mean):+.2f}pp "
              f"pctile_of_ep_mean_in_null={pctile:.2f} frac_ep_positive={100*(vals>0).mean():.0f}%")
