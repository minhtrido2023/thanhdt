"""
Lag analysis for macro overlay — proper version.

Hypothesis: Vietnamese market reacts to macro with LAG (foreign fast,
retail slow). Test: for each macro X, find lag k such that X[t-k] best
predicts VNI[t+h] - VNI[t].

Indicators (daily, expanded set):
  - DXY, USDVND
  - US 10Y yield (^TNX) — global rate stress
  - EMB (EM USD bond ETF) — EM credit stress (lower price = higher EM yield = stress)
  - EMLC (EM local currency bond) — EM local rate + FX stress
  - Spread metrics: DXY/EMLC ratio, US10Y - DXY decorrelated

Lag grid: k ∈ {0, 5, 10, 20, 40, 60, 90} sessions
Horizon:  h ∈ {20, 60, 120} sessions
"""
import pandas as pd
import numpy as np
import yfinance as yf
import subprocess, io
from itertools import product

def spearman(x, y):
    x = pd.Series(x); y = pd.Series(y)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 30: return np.nan
    rx, ry = x.rank(), y.rank()
    sx, sy = rx.std(), ry.std()
    if sx*sy == 0: return np.nan
    return ((rx-rx.mean())*(ry-ry.mean())).mean()/(sx*sy)

# ── Pull all macro daily ──
print("Pulling daily macro data...")
syms = {'DXY':'DX-Y.NYB', 'USDVND':'USDVND=X', 'US10Y':'^TNX',
        'EMB':'EMB', 'EMLC':'EMLC'}
mac = {}
for k, s in syms.items():
    h = yf.Ticker(s).history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
    h = h[['Close']].copy()
    h.columns = [k]
    h.index = pd.to_datetime(h.index.date)
    mac[k] = h

macro = mac['DXY']
for k in ['USDVND','US10Y','EMB','EMLC']:
    macro = macro.join(mac[k], how='outer')
macro = macro.ffill().dropna()

# Derived features
macro['DXY_mom20']   = macro['DXY'].pct_change(20)
macro['DXY_mom60']   = macro['DXY'].pct_change(60)
macro['USDVND_mom20']= macro['USDVND'].pct_change(20)
macro['US10Y_d20']   = macro['US10Y'].diff(20)
macro['US10Y_d60']   = macro['US10Y'].diff(60)
macro['EMB_ret20']   = macro['EMB'].pct_change(20)
macro['EMB_ret60']   = macro['EMB'].pct_change(60)
macro['EMLC_ret20']  = macro['EMLC'].pct_change(20)
macro['EMLC_ret60']  = macro['EMLC'].pct_change(60)
macro['DXY_rank252'] = macro['DXY'].rolling(252).rank(pct=True)
macro['US10Y_rank252'] = macro['US10Y'].rolling(252).rank(pct=True)
macro['EMLC_rank252_inv'] = 1 - macro['EMLC'].rolling(252).rank(pct=True)  # inv: high = stress

# Composite stress: high DXY + high US10Y + low EMLC (high EM stress)
macro['stress_composite'] = (macro['DXY_rank252'] + macro['US10Y_rank252']
                              + macro['EMLC_rank252_inv'])/3

# ── Pull VNI ──
vni_csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=20000','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND t.time>="2011-01-01" ORDER BY t.time'],
                         capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(vni_csv), parse_dates=['time']).set_index('time')
vni.columns = ['VNI']
state = pd.read_csv('data/_state.csv', parse_dates=['time']).set_index('time')

df = vni.join(macro, how='left').join(state, how='left')
df['state'] = df['state'].ffill()
df = df.ffill().dropna()
print(f"Merged {len(df)} rows {df.index[0].date()} -> {df.index[-1].date()}")

# Forward VNI returns
for h in [20, 60, 120]:
    df[f'fwd{h}'] = df['VNI'].shift(-h)/df['VNI'] - 1

# Features to test
features = ['DXY_mom20','DXY_mom60','DXY_rank252',
            'USDVND_mom20',
            'US10Y_d20','US10Y_d60','US10Y_rank252',
            'EMB_ret20','EMB_ret60',
            'EMLC_ret20','EMLC_ret60','EMLC_rank252_inv',
            'stress_composite']
lags = [0, 5, 10, 20, 40, 60, 90]
horizons = [20, 60, 120]

print("\n" + "="*100)
print("LAG IC TABLE — full sample 2011-2026 — IC(macro[t-k], VNI_fwd_h[t])")
print("Negative IC at lag>0 means: macro RISING k days ago -> VNI FALLING in next h days")
print("="*100)

# Build big table
records = []
for feat in features:
    for k in lags:
        for h in horizons:
            ser = df[feat].shift(k)  # macro k days ago
            ic = spearman(ser, df[f'fwd{h}'])
            records.append({'feat':feat, 'lag':k, 'horizon':h, 'ic':ic})
rec = pd.DataFrame(records)

# Pivot: rows=feat, cols=lag×horizon
for h in horizons:
    sub = rec[rec['horizon']==h].pivot(index='feat', columns='lag', values='ic')
    print(f"\n--- horizon = fwd{h}d ---")
    sub = sub.reindex(features)
    print(sub.round(3).to_string())

# Find optimal (feat, lag) pair per horizon
print("\n" + "="*100)
print("BEST (feat, lag) PER HORIZON (by |IC|)")
print("="*100)
for h in horizons:
    sub = rec[rec['horizon']==h].copy()
    sub['abs_ic'] = sub['ic'].abs()
    best = sub.nlargest(6, 'abs_ic')
    print(f"\nhorizon = {h}d")
    print(best[['feat','lag','ic']].to_string(index=False))

# ── Walk-forward consistency for best candidates ──
print("\n" + "="*100)
print("WALK-FORWARD: IS 2011-2018 vs OOS 2019-2026")
print("="*100)
df_is  = df[df.index <  '2019-01-01']
df_oos = df[df.index >= '2019-01-01']
top_cands = rec.copy()
top_cands['abs_ic'] = top_cands['ic'].abs()
top_cands = top_cands.nlargest(20, 'abs_ic')

print(f"{'feat':22s} {'lag':>4s} {'h':>4s} {'IC_full':>8s} {'IC_IS':>8s} {'IC_OOS':>8s} {'consistent':>11s}")
for _, r in top_cands.iterrows():
    f, k, h = r['feat'], int(r['lag']), int(r['horizon'])
    ic_full = r['ic']
    ic_is  = spearman(df_is[f].shift(k),  df_is[f'fwd{h}'])
    ic_oos = spearman(df_oos[f].shift(k), df_oos[f'fwd{h}'])
    cons = (not np.isnan(ic_is) and not np.isnan(ic_oos)
            and np.sign(ic_is)==np.sign(ic_oos)
            and abs(ic_is)>=0.10 and abs(ic_oos)>=0.10)
    print(f"{f:22s} {k:>4d} {h:>4d} {ic_full:+8.3f} {ic_is:+8.3f} {ic_oos:+8.3f} {'YES' if cons else 'no':>11s}")

# Save
df.to_csv('data/macro_lag_data.csv')
rec.to_csv('data/macro_lag_ic.csv', index=False)
print("\nSaved: macro_lag_data.csv, macro_lag_ic.csv")
