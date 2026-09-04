import pandas as pd, numpy as np, os
W = os.path.dirname(os.path.abspath(__file__))
Qgf = pd.read_csv(os.path.join(W, "gf_basket_nav.csv"), parse_dates=["time"]).set_index("time").nav_gf
V = pd.read_csv(os.path.join(W, "mania_daily_full.csv"), parse_dates=["time"]).set_index("time").vnindex_close
d = pd.read_csv(os.path.join(W, "mania_daily_full.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
flag = ((d.breadth_pct252 >= 0.90) & (d.spread21_pct252 >= 0.75)).fillna(False)
flag_series = pd.Series(flag.to_numpy(), index=d.time)

common = Qgf.index.intersection(V.index).intersection(flag_series.index).sort_values()
Qgf, V, flag_series = Qgf.loc[common], V.loc[common], flag_series.loc[common]
n = len(common)
ret_q = Qgf.pct_change(fill_method=None).fillna(0).to_numpy()
ret_v = V.pct_change(fill_method=None).fillna(0).to_numpy()
flag_arr = flag_series.to_numpy()

# extract contiguous True runs (episodes at raw-flag level, no gap tolerance needed here - we're
# comparing tilt-application days directly against the SAME flag structure used in run_blend)
def get_runs(arr):
    runs = []
    i = 0
    while i < len(arr):
        if arr[i]:
            j = i
            while j+1 < len(arr) and arr[j+1]:
                j += 1
            runs.append((i, j))
            i = j+1
        else:
            i += 1
    return runs

runs = get_runs(flag_arr)
n_transitions_main = 2*len(runs)
print(f"MANIA_DAY raw runs: {len(runs)}, total days={int(flag_arr.sum())}, median run length={np.median([e-s+1 for s,e in runs]):.0f}")

def run_blend(flag_arr_used, tilt_add, base_w=0.50, cost=0.001):
    w_target = np.where(np.roll(flag_arr_used, 1), min(base_w + tilt_add, 1.0), base_w)
    w_target[0] = base_w
    nav = 1.0
    navs = [nav]
    prev_w = base_w
    n_trans = 0
    for t in range(1, n):
        w = w_target[t]
        r = w * ret_q[t] + (1 - w) * ret_v[t]
        nav *= (1 + r)
        if w != prev_w:
            nav *= (1 - cost)
            n_trans += 1
        prev_w = w
        navs.append(nav)
    return np.array(navs), n_trans

years = (common[-1] - common[0]).days / 365.25
def cagr_of(navs): return navs[-1] ** (1/years) - 1
def sharpe_of(navs):
    r = np.diff(navs)/navs[:-1]
    return (r.mean()/r.std())*np.sqrt(252) if r.std()>0 else np.nan
def maxdd_of(navs):
    peak = np.maximum.accumulate(navs)
    return (navs/peak-1).min()

base_navs, _ = run_blend(np.zeros(n, dtype=bool), 0.0)
print(f"Baseline 50/50 constant: CAGR={100*cagr_of(base_navs):+.2f}% Sharpe={sharpe_of(base_navs):.3f} maxDD={100*maxdd_of(base_navs):.1f}%")

run_lengths = [e-s+1 for s,e in runs]
rng = np.random.default_rng(11)

for tilt in [0.25, 0.50]:
    main_navs, n_trans_main = run_blend(flag_arr, tilt)
    print(f"\nMAIN tilt+{int(100*tilt)}pp on MANIA_DAY: CAGR={100*cagr_of(main_navs):+.2f}% Sharpe={sharpe_of(main_navs):.3f} "
          f"maxDD={100*maxdd_of(main_navs):.1f}% n_transitions={n_trans_main}")
    ctrl_cagrs, ctrl_sharpes = [], []
    for b in range(200):
        rand_flag = np.zeros(n, dtype=bool)
        # place each run at a random non-overlapping-ish start, same run-length distribution as real episodes
        order = rng.permutation(len(run_lengths))
        occupied = np.zeros(n, dtype=bool)
        for idx in order:
            L = run_lengths[idx]
            for _try in range(50):
                s = rng.integers(0, n - L)
                if not occupied[s:s+L].any():
                    rand_flag[s:s+L] = True
                    occupied[s:s+L] = True
                    break
        navs_c, _ = run_blend(rand_flag, tilt)
        ctrl_cagrs.append(cagr_of(navs_c))
        ctrl_sharpes.append(sharpe_of(navs_c))
    ctrl_cagrs = np.array(ctrl_cagrs); ctrl_sharpes = np.array(ctrl_sharpes)
    main_cagr = cagr_of(main_navs)
    pctile = (ctrl_cagrs < main_cagr).mean()
    print(f"  CTRL (random contiguous runs, same length-distribution, n=200 boot): "
          f"mean_CAGR={100*ctrl_cagrs.mean():+.2f}% (std={100*ctrl_cagrs.std():.2f}pp) "
          f"mean_Sharpe={ctrl_sharpes.mean():.3f} MAIN_pctile_in_ctrl={pctile:.2f}")
