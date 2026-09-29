import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
Qgf = pd.read_csv(os.path.join(W, "gf_basket_nav.csv"), parse_dates=["time"]).set_index("time").nav_gf
V = pd.read_csv(os.path.join(W, "mania_daily_full.csv"), parse_dates=["time"]).set_index("time").vnindex_close

# recompute daily MANIA_DAY flag (N7 main threshold p90/p75), reusing exact logic from analyze_mania.py
d = pd.read_csv(os.path.join(W, "mania_daily_full.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
flag = ((d.breadth_pct252 >= 0.90) & (d.spread21_pct252 >= 0.75)).fillna(False)
flag_series = pd.Series(flag.to_numpy(), index=d.time)

# common date grid = intersection of Qgf, V, flag
common = Qgf.index.intersection(V.index).intersection(flag_series.index)
common = common.sort_values()
Qgf, V, flag_series = Qgf.loc[common], V.loc[common], flag_series.loc[common]
n = len(common)

ret_q = Qgf.pct_change().fillna(0).to_numpy()
ret_v = V.pct_change().fillna(0).to_numpy()
flag_arr = flag_series.to_numpy()

def run_blend(tilt_add, flag_arr_used, base_w=0.50, cost=0.001):
    w_target = np.where(np.roll(flag_arr_used, 1), min(base_w + tilt_add, 1.0), base_w)
    w_target[0] = base_w
    nav = 1.0
    navs = [nav]
    prev_w = base_w
    for t in range(1, n):
        w = w_target[t]
        r = w * ret_q[t] + (1 - w) * ret_v[t]
        nav *= (1 + r)
        if w != prev_w:
            nav *= (1 - cost)  # transaction cost on weight change
        prev_w = w
        navs.append(nav)
    return np.array(navs)

years = (common[-1] - common[0]).days / 365.25

def summary(navs, label):
    daily_ret = np.diff(navs) / navs[:-1]
    cagr = navs[-1] ** (1/years) - 1
    sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252) if daily_ret.std() > 0 else np.nan
    peak = np.maximum.accumulate(navs)
    dd = (navs / peak - 1).min()
    print(f"  {label}: CAGR={100*cagr:+.2f}% Sharpe={sharpe:.3f} maxDD={100*dd:.1f}% final_nav={navs[-1]:.3f}")
    return cagr, sharpe, dd

print(f"Panel: {common[0].date()}..{common[-1].date()}, {n} sessions, {years:.1f}y")
print(f"MANIA_DAY flag frequency: {100*flag_arr.mean():.1f}% of days ({int(flag_arr.sum())} days)")

base_navs = run_blend(0.0, flag_arr)
summary(base_navs, "Baseline 50/50 constant (no tilt)")

for tilt in [0.25, 0.50]:
    main_navs = run_blend(tilt, flag_arr)
    summary(main_navs, f"MAIN tilt+{int(100*tilt)}pp on MANIA_DAY")
    # control: tilt on random days, same total frequency as MANIA_DAY, bootstrap n=200
    rng = np.random.default_rng(7)
    n_flag_days = int(flag_arr.sum())
    ctrl_cagrs = []
    for b in range(200):
        rand_flag = np.zeros(n, dtype=bool)
        idx = rng.choice(n, size=n_flag_days, replace=False)
        rand_flag[idx] = True
        navs_c = run_blend(tilt, rand_flag)
        ctrl_cagrs.append(navs_c[-1] ** (1/years) - 1)
    ctrl_cagrs = np.array(ctrl_cagrs)
    main_cagr = main_navs[-1] ** (1/years) - 1
    pctile = (ctrl_cagrs < main_cagr).mean()
    print(f"    CTRL (random-day tilt, same freq, n=200 boot): mean_CAGR={100*ctrl_cagrs.mean():+.2f}% "
          f"MAIN_pctile_in_ctrl_dist={pctile:.2f}")
