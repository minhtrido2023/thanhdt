import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
Qey = pd.read_csv(os.path.join(W, "quality_basket_nav.csv"), parse_dates=["time"]).set_index("time").nav_quality
Qgf = pd.read_csv(os.path.join(W, "gf_basket_nav.csv"), parse_dates=["time"]).set_index("time").nav_gf
V = pd.read_csv(os.path.join(W, "mania_daily_full.csv"), parse_dates=["time"]).set_index("time").vnindex_close
V = V / V.iloc[0]

def nearest_available(ix, d):
    ix = pd.DatetimeIndex(ix)
    le = ix[ix <= d]
    if len(le) > 0: return le.max()
    ge = ix[ix >= d]
    return ge.min() if len(ge) > 0 else None

def ret_between(series, d0, d1):
    if d0 not in series.index or d1 not in series.index: return np.nan
    v0, v1 = series.loc[d0], series.loc[d1]
    if pd.isna(v0) or pd.isna(v1) or v0 == 0: return np.nan
    return v1/v0 - 1

def base_rate_excess(basket, bench, window_days, n_samples=3000, seed=1):
    ix = pd.DatetimeIndex(basket.index)
    start_min, start_max = ix.min(), ix.max() - pd.Timedelta(days=window_days)
    rng = np.random.default_rng(seed)
    valid_days = ix[(ix >= start_min) & (ix <= start_max)]
    picks = rng.choice(valid_days, size=min(n_samples, len(valid_days)), replace=False)
    excs = []
    for d0 in picks:
        d1 = nearest_available(ix, pd.Timestamp(d0) + pd.Timedelta(days=window_days))
        d0a = nearest_available(ix, d0)
        rb = ret_between(basket, d0a, d1)
        rv = ret_between(bench, nearest_available(bench.index, d0a), nearest_available(bench.index, d1))
        if not (np.isnan(rb) or np.isnan(rv)):
            excs.append(rb - rv)
    return np.array(excs)

for basket_name, Basket in [("ey_top_decile(naive)", Qey), ("golden_floor+ey", Qgf)]:
    print(f"\n########## Basket: {basket_name} ##########")
    for tag, epfile in [("N7_main", "../mania_episodes.csv"), ("N14_wide", "episodes_n14.csv")]:
        E = pd.read_csv(os.path.join(W, epfile), parse_dates=["start", "end"])
        rows = []
        for _, row in E.iterrows():
            d_start = nearest_available(Basket.index, row.start)
            d_end = nearest_available(Basket.index, row.end)
            d_6m = nearest_available(Basket.index, row.end + pd.Timedelta(days=182))
            if d_start is None or d_end is None or d_6m is None: continue
            len_in_days = (d_end - d_start).days
            q_in, v_in = ret_between(Basket, d_start, d_end), ret_between(V, d_start, d_end)
            q_post, v_post = ret_between(Basket, d_end, d_6m), ret_between(V, d_end, d_6m)
            q_rt, v_rt = ret_between(Basket, d_start, d_6m), ret_between(V, d_start, d_6m)
            rows.append(dict(excess_in=q_in-v_in if not(np.isnan(q_in) or np.isnan(v_in)) else np.nan,
                              excess_post=q_post-v_post if not(np.isnan(q_post) or np.isnan(v_post)) else np.nan,
                              excess_rt=q_rt-v_rt if not(np.isnan(q_rt) or np.isnan(v_rt)) else np.nan,
                              len_in_days=len_in_days))
        R = pd.DataFrame(rows)
        print(f"  -- {tag}, N={len(E)} --")
        med_len_in = int(R.len_in_days.median())
        base_in = base_rate_excess(Basket, V, med_len_in)
        base_post = base_rate_excess(Basket, V, 182)
        base_rt = base_rate_excess(Basket, V, med_len_in + 182)
        for col, base in [("excess_in", base_in), ("excess_post", base_post), ("excess_rt", base_rt)]:
            v = R[col].dropna()
            if len(v) == 0: continue
            ep_mean = v.mean()
            base_mean = base.mean()
            print(f"    {col}: n={len(v)} ep_mean={100*ep_mean:+.2f}pp base_mean(unconditional)={100*base_mean:+.2f}pp "
                  f"excess_over_base={100*(ep_mean-base_mean):+.2f}pp frac_ep_positive={100*(v>0).mean():.0f}%")
