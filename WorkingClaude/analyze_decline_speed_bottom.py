#!/usr/bin/env python3
"""
analyze_decline_speed_bottom.py
===============================================================================
Question: when broad consensus turns DOWN and turns down FAST ("dong thuan giam
nhanh"), how long until the market BOTTOMS — and does decline-SPEED help us call
the regime transition earlier than DT5G?

Data: data/daily_comovement_dt5g.csv (prune-universe cross-section + DT5G state).
Build an equal-weight (EW) index from avg_ret; "consensus down" = breadth /
pct_down; "speed" = trailing 10d EW return (steepness). No look-ahead in the
SIGNAL (all trailing); the BOTTOM measurement is by construction forward-looking
(that's what we're estimating).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(os.path.join(WORKDIR, "data", "daily_comovement_dt5g.csv"), parse_dates=["time"])
df = df.sort_values("time").reset_index(drop=True)

# ---- equal-weight index + trailing speed / consensus features ---------------
df["ew"] = (1 + df["avg_ret"]).cumprod()
df["ret5"]  = df["ew"].pct_change(5)
df["ret10"] = df["ew"].pct_change(10)      # "toc do giam" (speed, trailing 10d)
df["ret20"] = df["ew"].pct_change(20)
df["roll_peak"] = df["ew"].cummax()
df["dd"] = df["ew"]/df["roll_peak"] - 1     # drawdown from running peak
N = len(df)

# ===========================================================================
# PART 1 — DRAWDOWN EPISODES: does a faster decline bottom sooner?
# Episode = peak -> trough -> recovery back toward peak. Keep episodes >=8% deep.
# ===========================================================================
DEPTH = 0.08
episodes = []
i = 0
while i < N:
    if df["dd"].iloc[i] < -1e-9:
        # start of a drawdown from a fresh peak: find the peak index (last roll_peak)
        peak_val = df["roll_peak"].iloc[i]
        j = i
        while j < N and df["ew"].iloc[j] < peak_val * 0.99999:  # until recovers to peak
            j += 1
        seg = df.iloc[i-1 if i>0 else i:j+1]   # include the peak day
        tro = seg["ew"].idxmin()
        depth = df["ew"].loc[tro]/peak_val - 1
        if depth <= -DEPTH:
            # peak day = last day at/above peak before the slide (use i-1)
            pk = i-1 if i>0 else i
            decline = df.iloc[pk:tro+1]
            speed = decline["ret10"].min()          # steepest 10d drop during the fall
            panic_peak_idx = decline["pct_oversold"].idxmax()
            episodes.append(dict(
                peak=df["time"].iloc[pk], trough=df["time"].loc[tro],
                depth=depth*100,
                fall_days=int(tro-pk),
                speed10=speed*100,                  # most negative trailing-10d ret
                panic_peak=df["pct_oversold"].loc[panic_peak_idx]*100,
                panic_to_trough=int(tro-panic_peak_idx),  # +ve = panic peaked BEFORE bottom
                state_at_trough=int(df["state"].loc[tro]),
            ))
        i = j+1
    else:
        i += 1

E = pd.DataFrame(episodes)
print("="*78)
print("PART 1 — Drawdown episodes (EW prune index, depth >= 8%)")
print("="*78)
show = E.copy()
for c in ["depth","speed10","panic_peak"]: show[c]=show[c].round(1)
print(show.to_string(index=False))

# fast vs slow split by steepest-10d speed
med_speed = E["speed10"].median()
E["grp"] = np.where(E["speed10"] <= med_speed, "FAST(steep)", "SLOW(grind)")
print(f"\nSpeed split at median 10d-speed = {med_speed:.1f}%")
agg = E.groupby("grp").agg(
    n=("depth","size"), avg_depth=("depth","mean"),
    avg_fall_days=("fall_days","mean"), med_fall_days=("fall_days","median"),
    avg_panic_to_trough=("panic_to_trough","mean"),
    med_panic_to_trough=("panic_to_trough","median"),
).round(1)
print(agg.to_string())
print(f"\nCorrelation steepest-10d-speed vs fall_days (more-neg speed = faster): "
      f"{E['speed10'].corr(E['fall_days']):.2f}  (positive => steeper fall = SHORTER duration)")
print(f"Panic-peak-to-trough lag: mean {E['panic_to_trough'].mean():.0f}d / "
      f"median {E['panic_to_trough'].median():.0f}d  "
      f"(+ = panic breadth peaks BEFORE price bottom)")

# ===========================================================================
# PART 2 — VELOCITY EVENT STUDY: on a fast-consensus-down day, days-to-bottom?
# Signal day = trailing-10d EW ret in its worst decile AND broad (pct_down high).
# Forward: days to the LOWEST EW within next H days, + the trough depth + 60d fwd.
# ===========================================================================
H = 90
thr_speed = df["ret10"].quantile(0.05)     # worst 5% steepest declines
df["sig"] = (df["ret10"] <= thr_speed) & (df["pct_down"] >= 0.60)
rows = []
for k in np.where(df["sig"].values)[0]:
    if k+H >= N: continue
    fwd = df["ew"].values[k:k+H+1]
    tmin = int(np.argmin(fwd))
    trough_ret = fwd[tmin]/fwd[0]-1
    r60 = df["ew"].values[min(k+60,N-1)]/df["ew"].values[k]-1
    rows.append(dict(date=df["time"].iloc[k], state=int(df["state"].iloc[k]),
                     speed10=df["ret10"].iloc[k]*100, oversold=df["pct_oversold"].iloc[k]*100,
                     days_to_bottom=tmin, further_drop=trough_ret*100, fwd60=r60*100))
S = pd.DataFrame(rows)
print("\n"+"="*78)
print(f"PART 2 — Fast-consensus-down event study (trailing10d<= {thr_speed*100:.1f}% & pct_down>=60%)")
print("="*78)
print(f"n events = {len(S)} (clustered).  Forward window H={H}d")
# collapse clustered events: keep first of each cluster (>=10d gap)
S = S.sort_values("date").reset_index(drop=True)
S["gap"] = S["date"].diff().dt.days.fillna(999)
S["cluster"] = (S["gap"] >= 10).cumsum()
first = S.groupby("cluster").first().reset_index(drop=True)
print(f"\nDe-clustered to {len(first)} distinct capitulation events (first day of each):")
fp = first[["date","state","speed10","oversold","days_to_bottom","further_drop","fwd60"]].copy()
for c in ["speed10","oversold","further_drop","fwd60"]: fp[c]=fp[c].round(1)
fp["date"]=fp["date"].dt.date
print(fp.to_string(index=False))
print(f"\nDays-from-fast-signal to bottom: mean {first['days_to_bottom'].mean():.0f}d / "
      f"median {first['days_to_bottom'].median():.0f}d "
      f"(p25={first['days_to_bottom'].quantile(.25):.0f}, p75={first['days_to_bottom'].quantile(.75):.0f})")
print(f"Further drop after signal to bottom: mean {first['further_drop'].mean():.1f}% / "
      f"median {first['further_drop'].median():.1f}%")
print(f"Forward 60d EW return from signal: mean {first['fwd60'].mean():.1f}% / "
      f"median {first['fwd60'].median():.1f}% / win {100*(first['fwd60']>0).mean():.0f}%")

# ===========================================================================
# PART 3 — Does the speed signal LEAD the DT5G transition?
# For each EW trough (episodes), compare: when did DT5G EXIT crisis vs the bottom,
# and when did the fast-signal fire vs the bottom.
# ===========================================================================
print("\n"+"="*78)
print("PART 3 — Lead/lag vs DT5G regime transition")
print("="*78)
# DT5G crisis exit dates: state goes 1 -> not-1
df["prev_state"] = df["state"].shift(1)
exits = df[(df["prev_state"]==1) & (df["state"]!=1)][["time"]].copy()
# For each episode trough, find nearest crisis-exit AFTER the trough
recs=[]
for _,ep in E.iterrows():
    tro_date = ep["trough"]
    nxt = exits[exits["time"]>=tro_date]
    exit_lag = (nxt["time"].iloc[0]-tro_date).days if len(nxt) else np.nan
    # fast signal days within +/-20d of trough
    win = df[(df["time"]>=tro_date-pd.Timedelta(days=20)) & (df["time"]<=tro_date+pd.Timedelta(days=5))]
    sig_before = win["sig"].any()
    recs.append(dict(trough=tro_date.date(), depth=round(ep["depth"],1),
                     dt5g_exit_after_bottom_days=exit_lag,
                     fast_sig_near_bottom=bool(sig_before)))
L = pd.DataFrame(recs)
print(L.to_string(index=False))
ex = L["dt5g_exit_after_bottom_days"].dropna()
print(f"\nDT5G crisis-exit lag AFTER the EW bottom: mean {ex.mean():.0f}d / median {ex.median():.0f}d "
      f"(positive => DT5G confirms recovery only AFTER the bottom is in)")
print(f"Fast-consensus-down signal present near the bottom: {100*L['fast_sig_near_bottom'].mean():.0f}% of episodes")

E.to_csv(os.path.join(WORKDIR,"data","decline_speed_episodes.csv"),index=False)
first.to_csv(os.path.join(WORKDIR,"data","decline_speed_events.csv"),index=False)
print("\nSaved: data/decline_speed_episodes.csv, data/decline_speed_events.csv")
