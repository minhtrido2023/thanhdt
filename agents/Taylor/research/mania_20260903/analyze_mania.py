import pandas as pd, numpy as np, os

W = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/mania_20260903"
d = pd.read_csv(os.path.join(W, "mania_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
d = d[d.n_total > 0].reset_index(drop=True)
d["breadth"] = d.n_above_ma200 / d.n_total

# rolling 252-session percentile of breadth, causal (uses trailing 252 sessions, excludes today)
b = d.breadth.to_numpy()
pct = np.full(len(b), np.nan)
for i in range(252, len(b)):
    pct[i] = (b[i-252:i] < b[i]).mean()
d["breadth_pct252"] = pct

# rolling 21-session cumulative return spread: highrisk - lowrisk basket (quality-blind proxy)
d["ret_lowrisk"] = d.ret_lowrisk.astype(float)
d["ret_highrisk"] = d.ret_highrisk.astype(float)
d["logret_low"] = np.log1p(d.ret_lowrisk.fillna(0))
d["logret_high"] = np.log1p(d.ret_highrisk.fillna(0))
d["cum21_low"] = d.logret_low.rolling(21).sum()
d["cum21_high"] = d.logret_high.rolling(21).sum()
d["spread21"] = d.cum21_high - d.cum21_low   # junk minus quality, trailing 21 sessions

sp = d.spread21.to_numpy()
sp_pct = np.full(len(sp), np.nan)
for i in range(252, len(sp)):
    win = sp[i-252:i]
    win = win[~np.isnan(win)]
    if len(win) > 50 and not np.isnan(sp[i]):
        sp_pct[i] = (win < sp[i]).mean()
d["spread21_pct252"] = sp_pct

# restrict to data window where breadth is meaningful (>=2008-06, allow warmup) & has enough universe names
d2 = d[(d.time >= "2008-06-01") & (d.n_total >= 30)].reset_index(drop=True)

BREADTH_TH = 0.90
SPREAD_TH = 0.75
d2["mania_flag"] = (d2.breadth_pct252 >= BREADTH_TH) & (d2.spread21_pct252 >= SPREAD_TH)

# episode detection: contiguous True runs allowing gaps <=3 sessions, require total length >=21 sessions
flag = d2.mania_flag.fillna(False).to_numpy()
times = d2.time.to_numpy()
n = len(flag)
episodes = []
i = 0
while i < n:
    if flag[i]:
        start = i
        j = i
        gap = 0
        while j + 1 < n:
            if flag[j+1]:
                j += 1
                gap = 0
            else:
                gap += 1
                if gap > 3:
                    break
                j += 1
        # trim trailing non-flag days from the gap tolerance
        end = j
        while end > start and not flag[end]:
            end -= 1
        episodes.append((start, end))
        i = j + 1
    else:
        i += 1

# merge and filter by length >=21 sessions
eps = []
for (s, e) in episodes:
    length = e - s + 1
    if length >= 21:
        eps.append((s, e, length))

print(f"Panel: {len(d2)} sessions {d2.time.min().date()}..{d2.time.max().date()}")
print(f"Raw flagged sessions: {int(flag.sum())} / {n} ({100*flag.sum()/n:.1f}%)")
print(f"Episodes (>=21 sessions, gap<=3): N={len(eps)}")
print()

vni = d2.vnindex_close.to_numpy()
rows = []
for (s, e, length) in eps:
    start_t, end_t = times[s], times[e]
    vni_start, vni_end = vni[s], vni[e]
    ep_ret = vni_end / vni_start - 1
    fwd = {}
    for name, h in [("1M", 21), ("2M", 42), ("3M", 63), ("6M", 126)]:
        idx = e + h
        if idx < n:
            fwd[name] = vni[idx] / vni_end - 1
        else:
            fwd[name] = np.nan
    # max drawdown from episode end within next 126 sessions
    window_end = min(e + 126, n - 1)
    if window_end > e:
        seg = vni[e:window_end+1]
        peak = np.maximum.accumulate(seg)
        dd = (seg / peak - 1).min()
    else:
        dd = np.nan
    rows.append(dict(start=pd.Timestamp(start_t).date(), end=pd.Timestamp(end_t).date(),
                      length_sessions=length, vni_start=vni_start, vni_end=vni_end,
                      episode_return=ep_ret, fwd1m=fwd["1M"], fwd2m=fwd["2M"], fwd3m=fwd["3M"],
                      fwd6m=fwd["6M"], maxdd_next6m=dd))

R = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(R.to_string(index=False))
R.to_csv(os.path.join(W, "mania_episodes.csv"), index=False)

print()
print("=== Forward VNINDEX outcome summary across N episodes ===")
for col in ["fwd1m","fwd2m","fwd3m","fwd6m","maxdd_next6m"]:
    v = R[col].dropna()
    print(f"{col}: n={len(v)} mean={100*v.mean():.2f}% median={100*v.median():.2f}% "
          f"min={100*v.min():.2f}% max={100*v.max():.2f}% frac_negative={100*(v<0).mean():.0f}%")
