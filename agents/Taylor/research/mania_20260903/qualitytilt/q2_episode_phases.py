import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
Q = pd.read_csv(os.path.join(W, "quality_basket_nav.csv"), parse_dates=["time"]).set_index("time").nav_quality
vni_raw = pd.read_csv(os.path.join(W, "mania_daily_full.csv"), parse_dates=["time"]).set_index("time").vnindex_close
V = vni_raw / vni_raw.iloc[0]  # normalize to 1.0 at same start reference isn't needed; use ratio returns directly

def ret_between(series, d0, d1):
    s = series.reindex(series.index.union([d0, d1])).sort_index().ffill()
    if d0 not in s.index or d1 not in s.index:
        return np.nan
    v0, v1 = s.loc[d0], s.loc[d1]
    if pd.isna(v0) or pd.isna(v1) or v0 == 0:
        return np.nan
    return v1 / v0 - 1

def nearest_available(ix, d):
    ix = pd.DatetimeIndex(ix)
    le = ix[ix <= d]
    if len(le) > 0:
        return le.max()
    ge = ix[ix >= d]
    return ge.min() if len(ge) > 0 else None

for tag, epfile in [("N7_main(p90/p75)", "../mania_episodes.csv"), ("N14_wide(p85/p60)", "episodes_n14.csv")]:
    E = pd.read_csv(os.path.join(W, epfile), parse_dates=["start", "end"])
    print(f"\n=== {tag}, N={len(E)} ===")
    rows = []
    for _, row in E.iterrows():
        d_start = nearest_available(Q.index, row.start)
        d_end = nearest_available(Q.index, row.end)
        d_6m = nearest_available(Q.index, row.end + pd.Timedelta(days=182))
        if d_start is None or d_end is None or d_6m is None:
            continue
        q_in = ret_between(Q, d_start, d_end)
        v_in = ret_between(V, d_start, d_end)
        q_post = ret_between(Q, d_end, d_6m)
        v_post = ret_between(V, d_end, d_6m)
        q_rt = ret_between(Q, d_start, d_6m)
        v_rt = ret_between(V, d_start, d_6m)
        rows.append(dict(start=row.start.date(), end=row.end.date(),
                          q_in=q_in, v_in=v_in, excess_in=None if (q_in is None or v_in is None) else q_in - v_in,
                          q_post=q_post, v_post=v_post, excess_post=None if (q_post is None or v_post is None) else q_post - v_post,
                          q_rt=q_rt, v_rt=v_rt, excess_rt=None if (q_rt is None or v_rt is None) else q_rt - v_rt))
    R = pd.DataFrame(rows)
    pd.set_option("display.width", 220)
    print(R.applymap(lambda x: f"{100*x:+.1f}%" if isinstance(x, float) else x).to_string(index=False))
    R.to_csv(os.path.join(W, f"q2_phases_{tag.split('_')[0]}.csv"), index=False)
    for col in ["excess_in", "excess_post", "excess_rt"]:
        v = R[col].dropna()
        print(f"  {col}: n={len(v)} mean={100*v.mean():+.2f}pp median={100*v.median():+.2f}pp frac_positive={100*(v>0).mean():.0f}%")
