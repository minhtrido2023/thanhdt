"""
Test: which breadth predicts VNINDEX forward returns better?

3 universes:
  prune  — production (500 mixed)
  hsx    — HSX-only proxy (458)
  all    — all tickers (1272, the research mistake)

Test:
  1) Raw IC vs VNI fwd returns at multiple horizons
  2) Slope/change IC (does Δbreadth predict?)
  3) State-conditional IC (does broad help in CRISIS, HSX help in BULL?)
  4) Drawdown timing — which warns earlier before crash?
"""
import pandas as pd
import numpy as np
import subprocess, io

def spearman(x, y):
    x = pd.Series(x); y = pd.Series(y)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 50: return np.nan
    rx, ry = x.rank(), y.rank()
    sx, sy = rx.std(), ry.std()
    if sx*sy == 0: return np.nan
    return ((rx-rx.mean())*(ry-ry.mean())).mean()/(sx*sy)

# Load comparison data
df = pd.read_csv('breadth_universe_comparison.csv', parse_dates=['time'])

# Add VNI
vni_csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=20000','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND t.time>="2014-01-01" ORDER BY t.time'],
                         capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(vni_csv), parse_dates=['time']).rename(columns={'Close':'VNI'})

# Add state
state = pd.read_csv('_state.csv', parse_dates=['time'])

df = df.merge(vni, on='time').merge(state, on='time', how='left')
df['state'] = df['state'].ffill()

# Forward VNI returns
for h in [5, 20, 60, 120]:
    df[f'fwd{h}'] = df['VNI'].shift(-h)/df['VNI'] - 1

# Breadth features (raw + change)
for col in ['br_prune', 'br_hsx', 'br_all']:
    df[f'{col}_chg5']  = df[col].diff(5)
    df[f'{col}_chg20'] = df[col].diff(20)
    df[f'{col}_rank252'] = df[col].rolling(252).rank(pct=True)

print(f"Period: {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}, n={len(df)}")

# ── Test 1: Raw IC ──
print("\n" + "="*82)
print("TEST 1: Raw IC of breadth LEVEL vs VNI fwd returns")
print("="*82)
print(f"{'feature':22s} {'fwd5':>8s} {'fwd20':>8s} {'fwd60':>8s} {'fwd120':>8s}")
for col in ['br_prune','br_hsx','br_all']:
    row = f"{col:22s} "
    for h in [5,20,60,120]:
        ic = spearman(df[col], df[f'fwd{h}'])
        row += f" {ic:+8.3f}"
    print(row)

print("\n" + "="*82)
print("TEST 2: IC of breadth RANK252 (regime-adjusted)")
print("="*82)
print(f"{'feature':22s} {'fwd5':>8s} {'fwd20':>8s} {'fwd60':>8s} {'fwd120':>8s}")
for col in ['br_prune','br_hsx','br_all']:
    row = f"{col+'_rank252':22s} "
    for h in [5,20,60,120]:
        ic = spearman(df[f'{col}_rank252'], df[f'fwd{h}'])
        row += f" {ic:+8.3f}"
    print(row)

print("\n" + "="*82)
print("TEST 3: IC of breadth CHANGE (slope/momentum)")
print("="*82)
print(f"{'feature':22s} {'fwd5':>8s} {'fwd20':>8s} {'fwd60':>8s} {'fwd120':>8s}")
for col in ['br_prune','br_hsx','br_all']:
    for delta in ['chg5','chg20']:
        row = f"{col+'_'+delta:22s} "
        for h in [5,20,60,120]:
            ic = spearman(df[f'{col}_{delta}'], df[f'fwd{h}'])
            row += f" {ic:+8.3f}"
        print(row)

# State-conditional
print("\n" + "="*82)
print("TEST 4: STATE-CONDITIONAL IC of breadth LEVEL vs fwd20")
print("Hypothesis: broad better in CRISIS (state 1), HSX better in BULL (state 4,5)?")
print("="*82)
print(f"{'state':>6s} {'n':>5s}  {'IC br_prune':>12s} {'IC br_hsx':>12s} {'IC br_all':>12s}")
for s in [1,2,3,4,5]:
    sub = df[df['state']==s]
    if len(sub)<40: continue
    ic_p = spearman(sub['br_prune'], sub['fwd20'])
    ic_h = spearman(sub['br_hsx'],   sub['fwd20'])
    ic_a = spearman(sub['br_all'],   sub['fwd20'])
    print(f"{int(s):>6d} {len(sub):>5d}  {ic_p:+12.3f} {ic_h:+12.3f} {ic_a:+12.3f}")

# Drawdown timing test
print("\n" + "="*82)
print("TEST 5: CRISIS TIMING — does breadth lead VNI on drawdown entry?")
print("Compute mean breadth N days BEFORE state enters CRISIS (state=1)")
print("="*82)

# Identify CRISIS entries
df['state_prev'] = df['state'].shift(1)
df['crisis_entry'] = (df['state']==1) & (df['state_prev']!=1) & df['state_prev'].notna()
entries = df.index[df['crisis_entry']].tolist()
print(f"\nCRISIS entries detected: {len(entries)}")

print(f"\n{'days before CRISIS':>20s} {'mean br_prune':>14s} {'mean br_hsx':>14s} {'mean br_all':>14s}")
for d in [60, 40, 20, 10, 5, 0]:
    means_p, means_h, means_a = [], [], []
    for idx in entries:
        if idx-d >= 0:
            means_p.append(df.iloc[idx-d]['br_prune'])
            means_h.append(df.iloc[idx-d]['br_hsx'])
            means_a.append(df.iloc[idx-d]['br_all'])
    print(f"{'T-'+str(d):>20s} {np.mean(means_p):>14.4f} {np.mean(means_h):>14.4f} {np.mean(means_a):>14.4f}")

# BULL entry test
print("\n" + "="*82)
print("TEST 6: BULL TIMING — does breadth lead VNI on bull entry?")
print("="*82)
df['bull_entry'] = (df['state']>=4) & (df['state_prev']<4) & df['state_prev'].notna()
bull_entries = df.index[df['bull_entry']].tolist()
print(f"BULL entries detected: {len(bull_entries)}")
print(f"\n{'days before BULL':>20s} {'mean br_prune':>14s} {'mean br_hsx':>14s} {'mean br_all':>14s}")
for d in [60, 40, 20, 10, 5, 0]:
    means_p, means_h, means_a = [], [], []
    for idx in bull_entries:
        if idx-d >= 0:
            means_p.append(df.iloc[idx-d]['br_prune'])
            means_h.append(df.iloc[idx-d]['br_hsx'])
            means_a.append(df.iloc[idx-d]['br_all'])
    if means_p:
        print(f"{'T-'+str(d):>20s} {np.mean(means_p):>14.4f} {np.mean(means_h):>14.4f} {np.mean(means_a):>14.4f}")
