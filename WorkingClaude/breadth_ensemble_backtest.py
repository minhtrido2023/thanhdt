"""
Ensemble breadth test: replace single 12% breadth with 6% prune + 6% HSX.

Pipeline:
  1) Load VNINDEX + breadth × 3 (prune, hsx_proxy, ensemble)
  2) Compute 7 factors (P3M, P1M, MA200, RSI, MACD, CMF, + 1 or 2 breadth)
  3) For each config (baseline / hsx-only / ensemble-split / ensemble-avg):
       - Expanding rank per factor
       - Composite score
       - EMA smooth + mode(15) + min_stay(7)
       - State classification (5 states)
  4) Backtest each: NAV with state-based allocation (T+1, costs)
  5) Compare CAGR / Sharpe / DD / state count

Replicates vnindex_5state_system.py logic at minimum needed.
"""
import pandas as pd
import numpy as np
import subprocess, io
from collections import Counter

# ══ Parameters (match production exactly) ══
W_PRUNE_ONLY = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10,
                "CMF":0.08, "Breadth_prune":0.12}
W_HSX_ONLY   = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10,
                "CMF":0.08, "Breadth_hsx":0.12}
W_ENSEMBLE   = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10,
                "CMF":0.08, "Breadth_prune":0.06, "Breadth_hsx":0.06}
W_AVG_BREADTH = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10,
                "CMF":0.08, "Breadth_avg":0.12}

MIN_LB = 252
MIN_FACTORS = 3
MODE_WIN = 15
MIN_STAY = 7
EMA_ALPHA = 0.40
ALLOC = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}

# ══ Load data ══
print("Loading data...")
vni = pd.read_csv('data/VNINDEX.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
vni = vni[vni['time']>='2014-01-01'].reset_index(drop=True)
br_data = pd.read_csv('data/breadth_universe_comparison.csv', parse_dates=['time'])
vni = vni.merge(br_data[['time','br_prune','br_hsx']], on='time', how='left')
# Average breadth
vni['br_avg'] = (vni['br_prune'] + vni['br_hsx']) / 2
print(f"  {len(vni)} sessions {vni['time'].iloc[0].date()} -> {vni['time'].iloc[-1].date()}")

# ══ Compute price-based factors (same as production) ══
print("Computing factors...")
n = len(vni)
close = vni['Close'].values
high  = vni['High'].values
low   = vni['Low'].values
vol   = vni['Volume'].values

# P3M, P1M
p3m = np.full(n, np.nan); p1m = np.full(n, np.nan)
for i in range(n):
    if i >= 63: p3m[i] = close[i]/close[i-63] - 1
    if i >= 21: p1m[i] = close[i]/close[i-21] - 1

# MA200 dev
ma200_dev = np.full(n, np.nan)
for i in range(199, n):
    ma = np.mean(close[i-199:i+1])
    ma200_dev[i] = close[i]/ma - 1

# RSI Wilder 14
rsi = np.full(n, np.nan)
gains = np.zeros(n); losses = np.zeros(n)
for i in range(1, n):
    d = close[i]-close[i-1]
    gains[i] = max(d, 0); losses[i] = max(-d, 0)
ag = np.full(n, np.nan); al = np.full(n, np.nan)
ag[14] = np.mean(gains[1:15]); al[14] = np.mean(losses[1:15])
for i in range(15, n):
    ag[i] = (ag[i-1]*13 + gains[i])/14
    al[i] = (al[i-1]*13 + losses[i])/14
    if al[i] == 0: rsi[i] = 1.0
    else:
        rs = ag[i]/al[i]
        rsi[i] = 1 - 1/(1+rs)

# MACD histogram (12,26,9)
ema12 = pd.Series(close).ewm(span=12, adjust=False).mean().values
ema26 = pd.Series(close).ewm(span=26, adjust=False).mean().values
macd_line_arr = ema12 - ema26
signal = pd.Series(macd_line_arr).ewm(span=9, adjust=False).mean().values
macd_hist = np.full(n, np.nan)
for i in range(33, n):
    macd_hist[i] = macd_line_arr[i] - signal[i]

# CMF 14
hl = high - low
mfm = np.where(hl > 0, ((close - low) - (high - close))/hl, 0)
mfv = mfm * vol
cmf = np.full(n, np.nan)
for i in range(14, n):
    vs = np.sum(vol[i-14:i])
    if vs > 0: cmf[i] = np.sum(mfv[i-14:i])/vs

# ══ Expanding rank ══
def exp_rank(arr, min_lb=MIN_LB):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        hist = arr[:t+1]
        valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

print("Computing ranks...")
factors = {
    'P3M': p3m, 'P1M': p1m, 'MA200': ma200_dev, 'RSI': rsi,
    'MACD': macd_hist, 'CMF': cmf,
    'Breadth_prune': vni['br_prune'].values,
    'Breadth_hsx':   vni['br_hsx'].values,
    'Breadth_avg':   vni['br_avg'].values,
}
ranks = {k: exp_rank(v) for k, v in factors.items()}

# ══ State classification per config ══
def compute_states(ranks, weights):
    n = len(close)
    score = np.full(n, np.nan)
    for t in range(n):
        avail = {k: ranks[k][t] for k in weights if not np.isnan(ranks[k][t])}
        if len(avail) < MIN_FACTORS: continue
        wsum = sum(weights[k] for k in avail)
        score[t] = sum(avail[k]*weights[k] for k in avail)/wsum
    # Rank score
    r_score = exp_rank(score)
    # EMA smooth
    r_ema = np.full(n, np.nan)
    for t in range(n):
        v = r_score[t]; prev = r_ema[t-1] if t>0 else np.nan
        if np.isnan(v): r_ema[t] = prev
        elif np.isnan(prev): r_ema[t] = v
        else: r_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev
    # Classify raw states
    state_raw = np.full(n, np.nan)
    for t in range(n):
        v = r_ema[t]
        if np.isnan(v): continue
        if v < 0.10: state_raw[t] = 1
        elif v < 0.55: state_raw[t] = 2 if v < 0.30 else 3
        elif v < 0.75: state_raw[t] = 3
        else: state_raw[t] = 4 if v < 0.90 else 5
    # Mode filter 15-day
    state_mode = np.full(n, np.nan)
    for t in range(n):
        if t < MODE_WIN-1: continue
        window = state_raw[t-MODE_WIN+1:t+1]
        valid = window[~np.isnan(window)]
        if len(valid) == 0: continue
        state_mode[t] = Counter(valid).most_common(1)[0][0]
    # Min-stay filter
    state_final = state_mode.copy()
    i = 0
    while i < n:
        if np.isnan(state_final[i]): i += 1; continue
        j = i+1
        while j < n and state_final[j] == state_final[i]: j += 1
        seg_len = j - i
        if seg_len < MIN_STAY and i > 0 and not np.isnan(state_final[i-1]):
            state_final[i:j] = state_final[i-1]
        i = j
    return state_final, r_ema

# ══ NAV simulation ══
def stats(nav, dates):
    rets = pd.Series(nav).pct_change().dropna()
    yrs = (dates.iloc[-1]-dates.iloc[0]).days/365.25
    cagr = (nav[-1]/nav[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = pd.Series(nav).cummax(); dd = (pd.Series(nav)/cm-1).min()
    return dict(cagr=cagr*100, sh=sh, dd=dd*100, calmar=cagr/abs(dd) if dd!=0 else 0)

def backtest(states, vni_close, t1_lag=1, borrow_a=0.10, dep_a=0.06):
    n = len(states)
    rets = pd.Series(vni_close).pct_change().fillna(0).values
    # Clip extreme daily returns (data corruption: 1 day with close=1.59 instead of ~1500)
    rets = np.clip(rets, -0.10, 0.10)
    alloc = np.array([ALLOC[int(s)] if not np.isnan(s) else 0.7 for s in states])
    alloc_lag = np.roll(alloc, t1_lag); alloc_lag[:t1_lag] = 0.0
    nav = np.ones(n); db = borrow_a/250; dd = dep_a/250
    for i in range(1, n):
        w = alloc_lag[i]
        idle = max(0, 1-w); excess = max(0, w-1)
        r = w*rets[i] + idle*dd - excess*db
        nav[i] = nav[i-1]*(1+r)
    return nav

# ══ Run all configs ══
configs = {
    'A. baseline prune (production)': W_PRUNE_ONLY,
    'B. HSX-only breadth':            W_HSX_ONLY,
    'C. ensemble split (6+6)':        W_ENSEMBLE,
    'D. ensemble average':            W_AVG_BREADTH,
}

# B&H reference (with clip for data corruption)
rets_bnh = pd.Series(close).pct_change().fillna(0).values
rets_bnh = np.clip(rets_bnh, -0.10, 0.10)
nav_bnh = np.ones(n)
for i in range(1, n):
    nav_bnh[i] = nav_bnh[i-1]*(1 + rets_bnh[i])

print("\n" + "="*100)
print(f"{'config':<38s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Cal':>5s} {'transitions':>11s}")
print("="*100)
s_bnh = stats(nav_bnh, vni['time'])
print(f"{'VNI Buy & Hold':<38s} {'FULL 2014-2026':<18s} "
      f"{s_bnh['cagr']:7.2f} {s_bnh['sh']:5.2f} {s_bnh['dd']:7.2f} {s_bnh['calmar']:5.2f}")
print()

results = {}
for label, weights in configs.items():
    states, r_ema = compute_states(ranks, weights)
    nav = backtest(states, close)
    # Count transitions
    trans = sum(1 for i in range(1,n) if (not np.isnan(states[i])) and (not np.isnan(states[i-1])) and states[i] != states[i-1])
    # Stats overall + IS/OOS split
    for plabel, t0, t1 in [('FULL 2014-2026', None, None),
                            ('IS  (2014-2018)', '2014-01-01', '2018-12-31'),
                            ('OOS (2019-2026)', '2019-01-01', None)]:
        if t0 is not None:
            mask = vni['time']>=pd.Timestamp(t0)
            if t1: mask &= vni['time']<=pd.Timestamp(t1)
            n_sub = nav[mask.values]; d_sub = vni['time'][mask]
        else:
            n_sub = nav; d_sub = vni['time']
        s = stats(n_sub, d_sub.reset_index(drop=True))
        extra = f' trans={trans}' if plabel.startswith('FULL') else ''
        print(f"{label:<38s} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {extra}")
    print()
    results[label] = {'states': states, 'nav': nav, 'trans': trans}

# ══ State agreement analysis ══
print("="*100)
print("STATE AGREEMENT vs baseline (prune)")
print("="*100)
baseline_states = results['A. baseline prune (production)']['states']
for label in ['B. HSX-only breadth', 'C. ensemble split (6+6)', 'D. ensemble average']:
    other = results[label]['states']
    same = sum(1 for i in range(n) if (not np.isnan(baseline_states[i])) and (not np.isnan(other[i])) and baseline_states[i]==other[i])
    valid = sum(1 for i in range(n) if (not np.isnan(baseline_states[i])) and (not np.isnan(other[i])))
    agree = 100*same/valid if valid else 0
    print(f"  {label}: agreement {agree:.2f}% ({same}/{valid})")

# Save state series for further BA stack test
out = pd.DataFrame({'time': vni['time']})
for label, r in results.items():
    short = label.split('.')[0]
    out[f'state_{short}'] = r['states']
out.to_csv('data/breadth_ensemble_states.csv', index=False)
print("\nSaved: breadth_ensemble_states.csv")
