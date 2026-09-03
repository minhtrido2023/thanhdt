import pandas as pd, numpy as np, os

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # mania_20260903
CW = os.path.dirname(os.path.abspath(__file__))                   # mania_20260903/crack

daily = pd.read_csv(os.path.join(W, "mania_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
daily = daily[daily.n_total > 0].reset_index(drop=True)
daily["breadth"] = daily.n_above_ma200 / daily.n_total

b = daily.breadth.to_numpy()
pct = np.full(len(b), np.nan)
for i in range(252, len(b)):
    pct[i] = (b[i-252:i] < b[i]).mean()
daily["breadth_pct252"] = pct

disp = pd.read_csv(os.path.join(CW, "sector_dispersion.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)

d = daily.merge(disp[["time", "conc_spread", "n_sectors"]], on="time", how="inner")
d = d[d.time >= "2008-06-01"].reset_index(drop=True)

cs = d.conc_spread.to_numpy()
cs_pct = np.full(len(cs), np.nan)
for i in range(252, len(cs)):
    win = cs[i-252:i]
    win = win[~np.isnan(win)]
    if len(win) > 50 and not np.isnan(cs[i]):
        cs_pct[i] = (win < cs[i]).mean()
d["conc_spread_pct252"] = cs_pct

vni = d.vnindex_close.to_numpy()
new_high_126 = np.full(len(vni), False)
for i in range(126, len(vni)):
    new_high_126[i] = vni[i] >= np.nanmax(vni[i-125:i+1])
d["new_high_126"] = new_high_126

bp = d.breadth_pct252.to_numpy()
breadth_recent_max_63 = np.full(len(bp), np.nan)
for i in range(63, len(bp)):
    breadth_recent_max_63[i] = np.nanmax(bp[i-62:i+1])
d["breadth_recent_max_63"] = breadth_recent_max_63

# Divergence: price at a 6M high while breadth has fallen (dropped) from its own recent high —
# a RELATIVE drop, not an absolute low level (an absolute-level test misses 2022-01-06: breadth
# was still pct252=0.62 that day, above median, but had crashed from 0.99 five weeks earlier).
DIVERGE_DROP_MIN = 0.30
d["breadth_drop"] = d.breadth_recent_max_63 - d.breadth_pct252
d["diverge_day"] = d.new_high_126 & (d.breadth_drop >= DIVERGE_DROP_MIN)

# Concentration: one/few sectors carrying the tape, spread vs sector median unusually wide (vs own trailing history)
CONC_TH = 0.90
d["conc_day"] = d.conc_spread_pct252 >= CONC_TH

d["crack_day"] = d.diverge_day & d.conc_day

d.to_csv(os.path.join(CW, "crack_daily.csv"), index=False)

print(f"Panel: {len(d)} sessions {d.time.min().date()}..{d.time.max().date()}")
print(f"diverge_day flagged: {int(d.diverge_day.sum())} ({100*d.diverge_day.mean():.1f}%)")
print(f"conc_day flagged: {int(d.conc_day.sum())} ({100*d.conc_day.mean():.1f}%)")
print(f"crack_day (both): {int(d.crack_day.sum())} ({100*d.crack_day.mean():.1f}%)")
print()

def cluster_events(flag_col, gap=10):
    flag = d[flag_col].fillna(False).to_numpy()
    times = d.time.to_numpy()
    n = len(flag)
    events = []
    i = 0
    while i < n:
        if flag[i]:
            start = i
            j = i
            while j + 1 < n:
                # look ahead up to `gap` sessions for next flagged day
                nxt = None
                for k in range(j+1, min(j+1+gap, n)):
                    if flag[k]:
                        nxt = k
                        break
                if nxt is None:
                    break
                j = nxt
            events.append((start, j))
            i = j + 1
        else:
            i += 1
    return events

n = len(d)
vni = d.vnindex_close.to_numpy()

def outcome_row(e):
    out = {}
    for name, h in [("1M", 21), ("2M", 42), ("3M", 63), ("6M", 126)]:
        idx = e + h
        out[name] = vni[idx] / vni[e] - 1 if idx < n else np.nan
    window_end = min(e + 126, n - 1)
    if window_end > e:
        seg = vni[e:window_end+1]
        peak = np.maximum.accumulate(seg)
        out["maxdd_6m"] = (seg / peak - 1).min()
    else:
        out["maxdd_6m"] = np.nan
    return out

all_events = {}
for label, col in [("DIVERGE (chan 1 only)", "diverge_day"), ("CONC (chan 2 only)", "conc_day"), ("CRACK (both, AND)", "crack_day")]:
    evs = cluster_events(col)
    all_events[label] = evs
    print(f"=== {label}: {len(evs)} event(s) (clustered, gap<=10 sessions) ===")
    rows = []
    for (s, e) in evs:
        t0 = pd.Timestamp(d.time.iloc[s]).date()
        t1 = pd.Timestamp(d.time.iloc[e]).date()
        vni0 = d.vnindex_close.iloc[s]
        vni1 = d.vnindex_close.iloc[e]
        out = outcome_row(e)
        rows.append(dict(start=t0, end=t1, span=e - s + 1, vni_start=vni0, vni_end=vni1, **out))
        print(f"  {t0} .. {t1}  ({e-s+1} sessions)  VNI {vni0:.1f}->{vni1:.1f}  "
              f"+1M={out['1M']*100 if pd.notna(out['1M']) else float('nan'):.1f}%  "
              f"+3M={out['3M']*100 if pd.notna(out['3M']) else float('nan'):.1f}%  "
              f"+6M={out['6M']*100 if pd.notna(out['6M']) else float('nan'):.1f}%  "
              f"maxDD6M={out['maxdd_6m']*100 if pd.notna(out['maxdd_6m']) else float('nan'):.1f}%")
    R = pd.DataFrame(rows)
    if len(R):
        fname = os.path.join(CW, f"events_{col}.csv")
        R.to_csv(fname, index=False)
        for c in ["1M", "3M", "6M", "maxdd_6m"]:
            v = R[c].dropna()
            if len(v):
                print(f"    -> {c}: n={len(v)} mean={100*v.mean():.1f}% median={100*v.median():.1f}% frac_neg={100*(v<0).mean():.0f}%")
    print()

print("=== Sanity checks (must-catch cases) ===")
diverge_dates = set(pd.Timestamp(t).date() for t in d.loc[d.diverge_day, "time"])
print("2022-01-06 (VNINDEX all-time peak) flagged by DIVERGE:", pd.Timestamp("2022-01-06").date() in diverge_dates)
apr2018 = d[(d.time >= "2018-03-01") & (d.time <= "2018-05-15")]
print("2018-04 window diverge_day count:", int(apr2018.diverge_day.sum()), "/ conc_day count:", int(apr2018.conc_day.sum()))
