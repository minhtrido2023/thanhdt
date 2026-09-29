import pandas as pd, numpy as np, os
W = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/mania_20260903"
d = pd.read_csv(os.path.join(W, "mania_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
d = d[d.n_total > 0].reset_index(drop=True)
d["breadth"] = d.n_above_ma200 / d.n_total
b = d.breadth.to_numpy()
pct = np.full(len(b), np.nan)
for i in range(252, len(b)):
    pct[i] = (b[i-252:i] < b[i]).mean()
d["breadth_pct252"] = pct
d["logret_low"] = np.log1p(d.ret_lowrisk.astype(float).fillna(0))
d["logret_high"] = np.log1p(d.ret_highrisk.astype(float).fillna(0))
d["cum21_low"] = d.logret_low.rolling(21).sum()
d["cum21_high"] = d.logret_high.rolling(21).sum()
d["spread21"] = d.cum21_high - d.cum21_low
sp = d.spread21.to_numpy()
sp_pct = np.full(len(sp), np.nan)
for i in range(252, len(sp)):
    win = sp[i-252:i]
    win = win[~np.isnan(win)]
    if len(win) > 50 and not np.isnan(sp[i]):
        sp_pct[i] = (win < sp[i]).mean()
d["spread21_pct252"] = sp_pct
d2 = d[(d.time >= "2008-06-01") & (d.n_total >= 30)].reset_index(drop=True)

def detect_episodes(d2, breadth_th, spread_th, min_len=21, max_gap=3):
    d2 = d2.copy()
    d2["mania_flag"] = (d2.breadth_pct252 >= breadth_th) & (d2.spread21_pct252 >= spread_th)
    flag = d2.mania_flag.fillna(False).to_numpy()
    times = d2.time.to_numpy()
    n = len(flag)
    episodes = []
    i = 0
    while i < n:
        if flag[i]:
            start = i; j = i; gap = 0
            while j + 1 < n:
                if flag[j+1]:
                    j += 1; gap = 0
                else:
                    gap += 1
                    if gap > max_gap: break
                    j += 1
            end = j
            while end > start and not flag[end]:
                end -= 1
            episodes.append((start, end))
            i = j + 1
        else:
            i += 1
    eps = [(s, e, e - s + 1) for (s, e) in episodes if e - s + 1 >= min_len]
    return eps, times

eps, times = detect_episodes(d2, 0.85, 0.60)
print(f"N14 episodes (p85/p60): {len(eps)}")
vni = d2.vnindex_close.to_numpy()
rows = []
for (s, e, length) in eps:
    start_t, end_t = times[s], times[e]
    vni_start, vni_end = vni[s], vni[e]
    rows.append(dict(start=pd.Timestamp(start_t).date(), end=pd.Timestamp(end_t).date(),
                      length_sessions=length, start_idx=s, end_idx=e,
                      vni_start=vni_start, vni_end=vni_end, episode_return=vni_end/vni_start-1))
R = pd.DataFrame(rows)
print(R.to_string(index=False))
R.to_csv(os.path.join(W, "qualitytilt/episodes_n14.csv"), index=False)
d2.to_csv(os.path.join(W, "qualitytilt/mania_daily_full.csv"), index=False)
