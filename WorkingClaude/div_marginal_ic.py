"""
Step 1+2: For each BEAR/BULL fire, compute NEW independent indicators
          and measure their marginal IC vs forward return.

Independent indicators tested:
  1. PE rank (expanding, no look-ahead)
  2. State at fire (1-5 from vnindex_5state)
  3. Realized vol 20d percentile (expanding)
  4. ADX(14)
  5. Bollinger %B (20, 2σ)
  6. Distance from MA200: Close/MA200
  7. OBV slope (5d) - divergence vs price slope
  8. RSI percentile (expanding)
  9. Breadth %>MA50 trend (5d change)
  10. Breadth divergence vs price (price up, breadth down)
  11. Distance from 52w high (1.0 = at high)
"""
import pandas as pd
import numpy as np

# ── spearman (no scipy) ──
def spearman(x, y):
    x = pd.Series(x); y = pd.Series(y)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 4: return (np.nan, np.nan)
    rx, ry = x.rank(), y.rank()
    sx, sy = rx.std(), ry.std()
    if sx*sy == 0: return (np.nan, np.nan)
    rho = ((rx-rx.mean())*(ry-ry.mean())).mean()/(sx*sy)
    n = len(x)
    if abs(rho)>=1: return (rho, 0.0)
    z = 0.5*np.log((1+rho)/(1-rho))*np.sqrt(n-3)
    from math import erf, sqrt
    p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    return (rho, p)

# ── Load VNINDEX ──
v = pd.read_csv('data/_vni_full.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
# Merge PE from VNINDEX.csv (BQ ticker doesn't have VNINDEX PE)
vcsv = pd.read_csv('data/VNINDEX.csv', parse_dates=['time'])
v = v.merge(vcsv[['time','Pe']], on='time', how='left')
v['Pe'] = pd.to_numeric(v['Pe'], errors='coerce')

# Breadth
br = pd.read_csv('data/_breadth.csv', parse_dates=['time'])
br['pct_above_ma50'] = br['above_ma50'] / br['total']
br['pct_above_ma200'] = br['above_ma200'] / br['total']
v = v.merge(br[['time','pct_above_ma50','pct_above_ma200']], on='time', how='left')

# State
st = pd.read_csv('data/_state.csv', parse_dates=['time'])
v = v.merge(st, on='time', how='left')

# Forward returns
for h in [20,60,120,250]:
    v[f'fwd{h}'] = v['Close'].shift(-h)/v['Close'] - 1

# Daily returns + 20d realized vol
v['ret'] = v['Close'].pct_change()
v['rvol20'] = v['ret'].rolling(20).std()*np.sqrt(250)
v['rvol_rank'] = v['rvol20'].expanding(min_periods=252).rank(pct=True)

# PE rank (expanding)
v['pe_rank'] = v['Pe'].expanding(min_periods=252).rank(pct=True)

# RSI rank (expanding)
v['rsi_rank'] = v['D_RSI'].expanding(min_periods=252).rank(pct=True)

# Close / MA200
v['close_ma200'] = v['Close']/v['MA200']

# 52w high distance
v['hi252'] = v['High'].rolling(252).max()
v['close_hi252'] = v['Close']/v['hi252']

# Bollinger %B (20, 2σ)
mid = v['Close'].rolling(20).mean()
sd  = v['Close'].rolling(20).std()
v['bb_pctB'] = (v['Close'] - (mid - 2*sd)) / (4*sd)

# ADX(14)
def adx(high, low, close, n=14):
    tr = pd.concat([(high-low), (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
    plus_dm = (high.diff().where((high.diff()>0) & (high.diff()>-low.diff()), 0)).clip(lower=0)
    minus_dm = ((-low.diff()).where((-low.diff()>0) & (-low.diff()>high.diff()), 0)).clip(lower=0)
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    plus_di = 100*plus_dm.ewm(alpha=1/n, adjust=False).mean()/atr
    minus_di = 100*minus_dm.ewm(alpha=1/n, adjust=False).mean()/atr
    dx = 100*(plus_di-minus_di).abs()/(plus_di+minus_di)
    return dx.ewm(alpha=1/n, adjust=False).mean()
v['adx14'] = adx(v['High'], v['Low'], v['Close'], 14)

# OBV
v['obv'] = (np.sign(v['ret']).fillna(0) * v['Volume']).cumsum()
# OBV slope 5d vs Price slope 5d (divergence if opposite signs)
def slope5(s): return s - s.shift(5)
v['obv_slope5'] = slope5(v['obv'])
v['price_slope5'] = slope5(v['Close'])
v['obv_div'] = np.where((v['price_slope5']>0) & (v['obv_slope5']<0), -1,
                np.where((v['price_slope5']<0) & (v['obv_slope5']>0), +1, 0))

# Breadth slope 5d
v['breadth_slope5'] = slope5(v['pct_above_ma50'])
v['breadth_div'] = np.where((v['price_slope5']>0) & (v['breadth_slope5']<0), -1,
                    np.where((v['price_slope5']<0) & (v['breadth_slope5']>0), +1, 0))

# ── Load fires from prior analysis ──
bear = pd.read_csv('data/div_bear_fires_quality.csv', parse_dates=['date'])
bull = pd.read_csv('data/div_bull_fires_quality.csv', parse_dates=['date'])

# Look up each new indicator at fire date
new_cols = ['pe_rank','state','rvol_rank','adx14','bb_pctB','close_ma200',
            'close_hi252','rsi_rank','pct_above_ma50','breadth_slope5',
            'obv_div','breadth_div']
lookup = v.set_index('time')[new_cols]

bear = bear.merge(lookup, left_on='date', right_index=True, how='left')
bull = bull.merge(lookup, left_on='date', right_index=True, how='left')

print("BEAR fires features (head):")
print(bear[['date','state','pe_rank','rvol_rank','adx14','bb_pctB',
            'close_ma200','close_hi252','fwd60']].round(3).to_string(index=False))
print()
print("BULL fires features (head):")
print(bull[['date','state','pe_rank','rvol_rank','adx14','bb_pctB',
            'close_ma200','close_hi252','fwd60']].round(3).to_string(index=False))

# ── Marginal IC ──
print("\n" + "="*78)
print("BEAR: Marginal IC vs fwd60 (negative = correctly bearish)")
print("="*78)
print(f"{'indicator':22s} {'IC60':>8s} {'IC120':>8s} {'IC250':>8s} {'p60':>7s}  hint")
ic_bear = {}
hint_map = {'pe_rank':'+=high PE => bigger down','state':'+=BULL state => stays up?',
            'rvol_rank':'+=high vol => already crashed','adx14':'+=strong trend => continues',
            'bb_pctB':'+=stretched up => more down','close_ma200':'+=overheated => more down',
            'close_hi252':'+=at high => more down','rsi_rank':'+=high RSI => more down',
            'pct_above_ma50':'+=broad rally => more down','breadth_slope5':'+=breadth rising => UP',
            'obv_div':'-1 obv bear div','breadth_div':'-1 breadth bear div'}
for c in new_cols:
    r60,p60 = spearman(bear[c], bear['fwd60'])
    r120,_ = spearman(bear[c], bear['fwd120'])
    r250,_ = spearman(bear[c], bear['fwd250'])
    ic_bear[c] = r60
    print(f"  {c:22s} {r60:+8.3f} {r120:+8.3f} {r250:+8.3f} {p60:7.3f}  {hint_map[c]}")

print("\n" + "="*78)
print("BULL: Marginal IC vs fwd60 (positive = correctly bullish)")
print("="*78)
ic_bull = {}
for c in new_cols:
    r60,p60 = spearman(bull[c], bull['fwd60'])
    r120,_ = spearman(bull[c], bull['fwd120'])
    r250,_ = spearman(bull[c], bull['fwd250'])
    ic_bull[c] = r60
    print(f"  {c:22s} {r60:+8.3f} {r120:+8.3f} {r250:+8.3f} {p60:7.3f}")

# ── Walk-forward consistency: train 2011-2018, test 2019-2026 ──
def wf_check(fire_df, c, target_sign):
    tr = fire_df[fire_df['date']<'2019-01-01']
    te = fire_df[fire_df['date']>='2019-01-01']
    rt,_ = spearman(tr[c], tr['fwd60'])
    re,_ = spearman(te[c], te['fwd60'])
    return rt, re

print("\n" + "="*78)
print("WALK-FORWARD IC (train 2011-18 / test 2019-26)")
print("="*78)
print(f"{'indicator':22s} {'BEAR train':>11s} {'BEAR test':>11s} {'BULL train':>11s} {'BULL test':>11s}  consistent?")
robust = []
for c in new_cols:
    bt, be = wf_check(bear, c, -1)
    lt, le = wf_check(bull, c, +1)
    # Consistency: same sign train and test
    b_consist = (not np.isnan(bt) and not np.isnan(be) and np.sign(bt)==np.sign(be) and abs(bt)>0.15 and abs(be)>0.15)
    l_consist = (not np.isnan(lt) and not np.isnan(le) and np.sign(lt)==np.sign(le) and abs(lt)>0.15 and abs(le)>0.15)
    mark = ''
    if b_consist: mark += 'BEAR '
    if l_consist: mark += 'BULL'
    print(f"  {c:22s} {bt:+11.3f} {be:+11.3f} {lt:+11.3f} {le:+11.3f}  {mark}")
    if b_consist or l_consist:
        robust.append((c, b_consist, l_consist))

print()
print("ROBUST indicators (consistent sign + |IC|>0.15 in both folds):")
for r in robust:
    print("  ", r)

# ── Binary filter test for ALL marginal robust indicators ──
# For each robust indicator, define a binary filter at sensible threshold
# and measure fwd60 with filter ON vs OFF
print("\n" + "="*78)
print("BINARY FILTER TEST (in-sample diagnostic)")
print("="*78)

def filter_test(df, cond_name, cond_mask, target):
    n_on = cond_mask.sum()
    n_off = (~cond_mask).sum()
    if n_on == 0 or n_off == 0:
        print(f"  {cond_name}: skip (n_on={n_on}, n_off={n_off})")
        return
    on = df[cond_mask][target].mean()
    off = df[~cond_mask][target].mean()
    hit_on = (df[cond_mask][target] > 0).mean() if 'BULL' in cond_name else (df[cond_mask][target] < 0).mean()
    hit_off = (df[~cond_mask][target] > 0).mean() if 'BULL' in cond_name else (df[~cond_mask][target] < 0).mean()
    print(f"  {cond_name:48s} n_on={n_on:2d}/{n_on+n_off:2d}  "
          f"fwd60_on={on:+.3f}  fwd60_off={off:+.3f}  hit_on={hit_on:.2f}  hit_off={hit_off:.2f}")

# BEAR filters: want fwd60 to be MORE NEGATIVE when filter is ON
print("\nBEAR — filters that may IMPROVE signal:")
for thr in [0.50, 0.70, 0.85]:
    filter_test(bear, f'BEAR + pe_rank >= {thr}', bear['pe_rank']>=thr, 'fwd60')
for thr in [0.50, 0.70]:
    filter_test(bear, f'BEAR + close_hi252 >= {thr}'+' (near 52w high)', bear['close_hi252']>=thr, 'fwd60')
filter_test(bear, 'BEAR + state in (4,5) (BULL/EX-BULL)', bear['state'].isin([4,5]), 'fwd60')
filter_test(bear, 'BEAR + state == 5 (EX-BULL only)', bear['state']==5, 'fwd60')
filter_test(bear, 'BEAR + adx14 >= 25 (strong trend)', bear['adx14']>=25, 'fwd60')
filter_test(bear, 'BEAR + bb_pctB >= 0.9 (stretched up)', bear['bb_pctB']>=0.9, 'fwd60')
filter_test(bear, 'BEAR + close_ma200 >= 1.15 (overheated)', bear['close_ma200']>=1.15, 'fwd60')

print("\nBULL — filters that may IMPROVE signal:")
for thr in [0.30, 0.15, 0.10]:
    filter_test(bull, f'BULL + pe_rank <= {thr}', bull['pe_rank']<=thr, 'fwd60')
filter_test(bull, 'BULL + rvol_rank >= 0.70 (high vol = capit.)', bull['rvol_rank']>=0.70, 'fwd60')
filter_test(bull, 'BULL + state in (1,2) (CRISIS/BEAR)', bull['state'].isin([1,2]), 'fwd60')
filter_test(bull, 'BULL + close_ma200 <= 0.95 (below MA200)', bull['close_ma200']<=0.95, 'fwd60')
filter_test(bull, 'BULL + close_hi252 <= 0.85 (deep below 52w)', bull['close_hi252']<=0.85, 'fwd60')
filter_test(bull, 'BULL + bb_pctB <= 0.1 (deep oversold band)', bull['bb_pctB']<=0.1, 'fwd60')

# Save
bear.to_csv('data/div_bear_with_newind.csv', index=False)
bull.to_csv('data/div_bull_with_newind.csv', index=False)
print("\nSaved: div_bear_with_newind.csv, div_bull_with_newind.csv")
