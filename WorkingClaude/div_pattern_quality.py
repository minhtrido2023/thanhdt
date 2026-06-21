"""
Step 3: Weight existing indicators of BearDvg/BullDvg patterns
       using a per-fire quality score.

Method:
  1) Detect fire dates of each pattern from raw conditions
  2) Extract continuous margin past threshold for each condition
  3) Measure correlation between each margin and forward return
  4) Build composite quality score Q = sum(sign_i * z_i)
  5) Bin fires by Q-tier, validate forward return discrimination
  6) Walk-forward: train weights on 2011-2018, test 2019-2026
"""
import pandas as pd
import numpy as np
def spearmanr(x, y):
    """Minimal spearman rank correlation, returns (rho, p~0.0 placeholder)."""
    x = pd.Series(x); y = pd.Series(y)
    msk = x.notna() & y.notna()
    x, y = x[msk], y[msk]
    if len(x) < 3:
        return (np.nan, np.nan)
    rx = x.rank(); ry = y.rank()
    cov = ((rx-rx.mean())*(ry-ry.mean())).mean()
    sx = rx.std(); sy = ry.std()
    rho = cov / (sx*sy) if sx*sy>0 else np.nan
    # Simple two-tailed p via Fisher z (approximation)
    n = len(x)
    if abs(rho) >= 1 or n < 4:
        return (rho, np.nan)
    z = 0.5*np.log((1+rho)/(1-rho)) * np.sqrt(n-3)
    from math import erf, sqrt
    p = 2*(1 - 0.5*(1+erf(abs(z)/sqrt(2))))
    return (rho, p)

df = pd.read_csv('data/_vni_div.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
print(f"Loaded {len(df)} rows, {df['time'].min().date()} -> {df['time'].max().date()}")

# Forward returns
for h in [20, 60, 120, 250]:
    df[f'fwd{h}'] = df['Close'].shift(-h) / df['Close'] - 1

# ─────────────────────────────────────────────────────────────────────────
# Pattern fires (replicate filter.json formulas)
# ─────────────────────────────────────────────────────────────────────────
def fire_bear1(d):
    return ((d.D_RSI_Max1W/d.D_RSI > 1.044) & (d.D_RSI_Max3M > 0.74)
            & (d.D_RSI_Max1W < 0.72) & (d.D_RSI_Max1W > 0.61)
            & (d.D_RSI_Max1W_Close/d.D_RSI_Max3M_Close > 1.028)
            & (d.D_RSI_Max3M_MACD/d.D_RSI_Max1W_MACD > 1.11)
            & (d.D_MACDdiff < 0)
            & (d.Close/d.D_RSI_Max3M_Close > 0.96)
            & (d.D_RSI_MinT3 > 0.43) & (d.D_CMF < 0.13))

def fire_bear2(d):
    return ((d.D_RSI_Max1W/d.D_RSI > 1.016) & (d.D_RSI_Max3M > 0.77)
            & (d.D_RSI_Max1W < 0.79) & (d.D_RSI_Max1W > 0.6)
            & (d.D_RSI_Max1W_Close/d.D_RSI_Max3M_Close > 1.008)
            & (d.D_RSI_Max3M_MACD/d.D_RSI_Max1W_MACD > 1.1)
            & (d.D_MACDdiff < 0)
            & (d.Close/d.D_RSI_Max3M_Close > 0.97)
            & (d.D_RSI_MinT3 > 0.5) & (d.D_CMF < 0.15))

def fire_bull1(d):
    return ((d.D_RSI_Min1W/d.D_RSI_Min3M > 0.9) & (d.D_RSI_Min1W < 0.6)
            & (d.D_RSI_Min3M < 0.4)
            & (d.D_RSI_Min1W_Close/d.D_RSI_Min3M_Close < 1.15)
            & (d.D_MACDdiff > 0) & (d.D_RSI_MinT3 < 0.5)
            & (d.D_RSI_Max1W < 0.48) & (d.D_RSI/d.D_RSI_T1W > 1.12)
            & (d.D_CMF > 0) & (d.C_L1M < 1.21) & (d.C_L1W < 1.05))

def fire_bull12(d):
    return ((d.D_RSI_Min1W/d.D_RSI_Min3M > 0.92) & (d.D_RSI_Min1W < 0.52)
            & (d.D_RSI_Min3M < 0.38)
            & (d.D_RSI_Min1W_Close/d.D_RSI_Min3M_Close < 1.1)
            & (d.D_MACDdiff > 0) & (d.D_RSI_MinT3 < 0.56)
            & (d.D_RSI_Max1W < 0.64) & (d.D_RSI/d.D_RSI_T1W > 1.1)
            & (d.D_CMF > 0) & (d.C_L1M < 1.2) & (d.C_L1W < 1.025))

df['bear1'] = fire_bear1(df).fillna(False)
df['bear2'] = fire_bear2(df).fillna(False)
df['bull1'] = fire_bull1(df).fillna(False)
df['bull12'] = fire_bull12(df).fillna(False)

print(f"Fires: bear1={df.bear1.sum()}  bear2={df.bear2.sum()}  "
      f"bull1={df.bull1.sum()}  bull12={df.bull12.sum()}")

# ─────────────────────────────────────────────────────────────────────────
# Reduce to *clusters*: a single divergence event often fires for many
# consecutive days. Take the FIRST fire date in each cluster (>=10d gap).
# ─────────────────────────────────────────────────────────────────────────
def cluster_first(mask, gap=10):
    idx = np.where(mask)[0]
    if len(idx) == 0: return []
    keep = [idx[0]]
    for i in idx[1:]:
        if i - keep[-1] >= gap: keep.append(i)
    return keep

bear_idx = sorted(set(cluster_first(df['bear1'].values) + cluster_first(df['bear2'].values)))
bull_idx = sorted(set(cluster_first(df['bull1'].values) + cluster_first(df['bull12'].values)))

# De-duplicate across pattern variants
def dedupe(idx, gap=10):
    if not idx: return []
    keep = [idx[0]]
    for i in idx[1:]:
        if i - keep[-1] >= gap: keep.append(i)
    return keep

bear_idx = dedupe(bear_idx)
bull_idx = dedupe(bull_idx)

print(f"Clustered fires: BEAR={len(bear_idx)}  BULL={len(bull_idx)}")
print("BEAR dates:", df.loc[bear_idx,'time'].dt.date.tolist())
print("BULL dates:", df.loc[bull_idx,'time'].dt.date.tolist())

# ─────────────────────────────────────────────────────────────────────────
# Per-fire feature extraction (continuous "strength" of each condition)
# Sign convention: HIGHER = MORE BEARISH for bear pattern,
#                  HIGHER = MORE BULLISH for bull pattern
# ─────────────────────────────────────────────────────────────────────────
def bear_features(r):
    return pd.Series({
        'rsi_pullback_1w':  r.D_RSI_Max1W/r.D_RSI - 1.0,           # bigger = stronger
        'rsi_3m_peak':      r.D_RSI_Max3M,                          # bigger = more overbought 3M
        'rsi_div_lower':    r.D_RSI_Max3M - r.D_RSI_Max1W,          # bigger = stronger RSI divergence
        'price_div_higher': r.D_RSI_Max1W_Close/r.D_RSI_Max3M_Close - 1.0,  # bigger = higher high
        'macd_div':         r.D_RSI_Max3M_MACD/np.maximum(r.D_RSI_Max1W_MACD,1e-6) - 1.0,
        'macd_neg':         -r.D_MACDdiff,                          # bigger (more negative) = bearish
        'near_3m_peak':     r.Close/r.D_RSI_Max3M_Close,            # ~1.0 = at peak
        'not_oversold':     r.D_RSI_MinT3,                          # higher = not overdone selling
        'cmf_weak':         -r.D_CMF,                               # bigger (more negative CMF) = bearish
    })

def bull_features(r):
    return pd.Series({
        'rsi_higherlow_1w': r.D_RSI_Min1W/r.D_RSI_Min3M - 1.0,        # bigger = stronger
        'rsi_3m_min':       0.4 - r.D_RSI_Min3M,                       # bigger = deeper 3M oversold
        'rsi_1w_min':       0.6 - r.D_RSI_Min1W,                       # bigger = oversold 1W
        'price_lowerlow':   1.15 - r.D_RSI_Min1W_Close/r.D_RSI_Min3M_Close,  # bigger = lower low confirmed
        'macd_turn':        r.D_MACDdiff,                              # bigger = bullish turn
        'rsi_accelerate':   r.D_RSI/r.D_RSI_T1W - 1.0,                 # RSI accelerating up
        'cmf_strong':       r.D_CMF,                                   # positive money flow
        'near_low_1m':      1.21 - r.C_L1M,                            # closer to 1M low = better
        'near_low_1w':      1.05 - r.C_L1W,                            # closer to 1W low
        'not_overboughtw':  0.48 - r.D_RSI_Max1W,                      # no spike yet
    })

bear_df = pd.DataFrame([bear_features(df.iloc[i]) for i in bear_idx])
bear_df['idx'] = bear_idx
bear_df['date'] = df.loc[bear_idx,'time'].values
for h in [20, 60, 120, 250]:
    bear_df[f'fwd{h}'] = df.loc[bear_idx, f'fwd{h}'].values

bull_df = pd.DataFrame([bull_features(df.iloc[i]) for i in bull_idx])
bull_df['idx'] = bull_idx
bull_df['date'] = df.loc[bull_idx,'time'].values
for h in [20, 60, 120, 250]:
    bull_df[f'fwd{h}'] = df.loc[bull_idx, f'fwd{h}'].values

# ─────────────────────────────────────────────────────────────────────────
# Baseline: what is forward return on average?
# For BEAR: NEGATIVE forward return = good (signal of top)
# For BULL: POSITIVE forward return = good (signal of bottom)
# ─────────────────────────────────────────────────────────────────────────
print("\n=== BEAR fires: forward return distribution ===")
print(bear_df[['fwd20','fwd60','fwd120','fwd250']].describe().round(3).T)
print("BEAR: % negative fwd60:", (bear_df['fwd60']<0).mean().round(2))

print("\n=== BULL fires: forward return distribution ===")
print(bull_df[['fwd20','fwd60','fwd120','fwd250']].describe().round(3).T)
print("BULL: % positive fwd60:", (bull_df['fwd60']>0).mean().round(2))

# ─────────────────────────────────────────────────────────────────────────
# IC: each feature vs forward return (using the "right sign")
# For BEAR: feature should NEGATIVELY correlate with fwd60 (strong signal -> down)
# For BULL: feature should POSITIVELY correlate with fwd60
# ─────────────────────────────────────────────────────────────────────────
bear_feats = [c for c in bear_df.columns if c not in ('idx','date','fwd20','fwd60','fwd120','fwd250')]
bull_feats = [c for c in bull_df.columns if c not in ('idx','date','fwd20','fwd60','fwd120','fwd250')]

print("\n=== BEAR feature IC vs fwd60 (negative = correctly bearish) ===")
ic_bear = {}
for f in bear_feats:
    rho, p = spearmanr(bear_df[f], bear_df['fwd60'])
    ic_bear[f] = rho
    print(f"  {f:22s}  IC={rho:+.3f}  p={p:.3f}")

print("\n=== BULL feature IC vs fwd60 (positive = correctly bullish) ===")
ic_bull = {}
for f in bull_feats:
    rho, p = spearmanr(bull_df[f], bull_df['fwd60'])
    ic_bull[f] = rho
    print(f"  {f:22s}  IC={rho:+.3f}  p={p:.3f}")

# ─────────────────────────────────────────────────────────────────────────
# Build quality score Q. Sign convention:
# BEAR: want sum of features × NEGATIVE-of-IC-sign such that high Q = strong bear
#   Q = sum( -sign(IC_f) * z(f) )   ... we want high Q to predict negative fwd
#   Equivalent: weight = -IC_f, Q = sum(w * z)
# BULL: Q = sum(IC_f * z(f))
# ─────────────────────────────────────────────────────────────────────────
def zscore(s):
    return (s - s.mean()) / (s.std() + 1e-9)

bear_z = bear_df[bear_feats].apply(zscore)
# Weight: weight = -IC_f (we want high Q -> negative fwd return)
bear_w = pd.Series({f: -ic_bear[f] for f in bear_feats})
bear_df['Q'] = (bear_z * bear_w).sum(axis=1)

bull_z = bull_df[bull_feats].apply(zscore)
bull_w = pd.Series({f: ic_bull[f] for f in bull_feats})
bull_df['Q'] = (bull_z * bull_w).sum(axis=1)

# Bin into quality tiers
def tier_bin(q):
    return pd.qcut(q, 3, labels=['Low','Mid','High'])

bear_df['tier'] = tier_bin(bear_df['Q'])
bull_df['tier'] = tier_bin(bull_df['Q'])

print("\n=== BEAR by Q-tier: forward returns (lower = better signal) ===")
print(bear_df.groupby('tier', observed=True).agg(
    n=('Q','count'),
    Q_mean=('Q','mean'),
    fwd20=('fwd20','mean'),
    fwd60=('fwd60','mean'),
    fwd120=('fwd120','mean'),
    fwd250=('fwd250','mean'),
    pct_neg60=('fwd60', lambda s: (s<0).mean())
).round(3))

print("\n=== BULL by Q-tier: forward returns (higher = better signal) ===")
print(bull_df.groupby('tier', observed=True).agg(
    n=('Q','count'),
    Q_mean=('Q','mean'),
    fwd20=('fwd20','mean'),
    fwd60=('fwd60','mean'),
    fwd120=('fwd120','mean'),
    fwd250=('fwd250','mean'),
    pct_pos60=('fwd60', lambda s: (s>0).mean())
).round(3))

# ─────────────────────────────────────────────────────────────────────────
# Walk-forward (CRITICAL): train weights on 2011-2018, test 2019-2026
# ─────────────────────────────────────────────────────────────────────────
def walk_forward(fire_df, feats, target_sign_negative_means_good):
    train_mask = fire_df['date'] < pd.Timestamp('2019-01-01')
    test_mask  = ~train_mask
    print(f"  train n={train_mask.sum()}, test n={test_mask.sum()}")
    if train_mask.sum() < 5 or test_mask.sum() < 3:
        print("  insufficient sample for WF"); return None
    train, test = fire_df[train_mask], fire_df[test_mask]

    ics = {}
    for f in feats:
        rho, _ = spearmanr(train[f], train['fwd60'])
        if np.isnan(rho): rho = 0.0
        ics[f] = rho

    # Build score on test using TRAIN weights and TRAIN normalization
    weights = {f: -ics[f] if target_sign_negative_means_good else ics[f] for f in feats}
    train_mean = train[feats].mean()
    train_std  = train[feats].std() + 1e-9
    test_z = (test[feats] - train_mean) / train_std
    test_q = (test_z * pd.Series(weights)).sum(axis=1)
    test_out = test.copy()
    test_out['Q_WF'] = test_q.values
    # split test into high/low Q
    median_q = test_out['Q_WF'].median()
    hi = test_out[test_out['Q_WF'] >= median_q]
    lo = test_out[test_out['Q_WF'] <  median_q]
    print(f"  TEST: Q-high (n={len(hi)})  fwd60 mean = {hi['fwd60'].mean():+.3f}")
    print(f"  TEST: Q-low  (n={len(lo)})  fwd60 mean = {lo['fwd60'].mean():+.3f}")
    print(f"  TEST: all   (n={len(test_out)})  fwd60 mean = {test_out['fwd60'].mean():+.3f}")
    return test_out

print("\n=== WALK-FORWARD: BEAR (train 2011-2018, test 2019-2026) ===")
bear_wf = walk_forward(bear_df, bear_feats, target_sign_negative_means_good=True)

print("\n=== WALK-FORWARD: BULL (train 2011-2018, test 2019-2026) ===")
bull_wf = walk_forward(bull_df, bull_feats, target_sign_negative_means_good=False)

# Save outputs
bear_df.to_csv('data/div_bear_fires_quality.csv', index=False)
bull_df.to_csv('data/div_bull_fires_quality.csv', index=False)
print("\nSaved: div_bear_fires_quality.csv, div_bull_fires_quality.csv")
