"""
Tier 2 composite overlay: combine DXY + EEM (independent signals) +
lagged DXY momentum.

Signal design:
  macro_score = z(DXY_rank252) - z(EEM_ret60) + z(DXY_mom60_lag60)
              = DXY level + DXY momentum 60d ago - EM equity trend
  High score = macro tight regime → trim BA exposure

Variants:
  V1: scalar gate on composite z
  V2: state-conditional (only fire in state {1,3})
  V3: continuous gradient
"""
import pandas as pd
import numpy as np

df = pd.read_csv('tier2_macro_panel.csv', parse_dates=['time'])
ba = pd.read_csv('ba_v11_nav.csv', parse_dates=['time'])
df = df.merge(ba[['time','BA_v11']], on='time', how='left')
df['ba_ret'] = df['BA_v11'].pct_change().fillna(0.0)
df = df[df['BA_v11'].notna()].reset_index(drop=True)

# Compute composite macro_score using EXPANDING z-scores (no look-ahead)
def expanding_z(s, min_periods=252):
    mean = s.expanding(min_periods=min_periods).mean()
    sd = s.expanding(min_periods=min_periods).std()
    return (s - mean) / sd

df['DXY_rank252_z']  = expanding_z(df['DXY_rank252'])
df['EEM_ret60_z']    = expanding_z(df['EEM_ret60'])
df['DXY_mom60_lag60'] = df['DXY_mom60'].shift(60)
df['DXY_mom60_lag60_z'] = expanding_z(df['DXY_mom60_lag60'])

# Composite: tight = DXY high (positive z) + EEM weak (negative z) + DXY mom60 lag60 high
df['macro_score'] = (df['DXY_rank252_z'].fillna(0)
                     - df['EEM_ret60_z'].fillna(0)
                     + df['DXY_mom60_lag60_z'].fillna(0)) / 3

print(f"macro_score range: {df['macro_score'].min():.2f} -> {df['macro_score'].max():.2f}")
print(f"macro_score >=  1.0: {(df['macro_score']>=1.0).sum()} sessions")
print(f"macro_score >=  1.5: {(df['macro_score']>=1.5).sum()} sessions")
print(f"macro_score <= -1.0: {(df['macro_score']<=-1.0).sum()} sessions")

# Baseline NAV
nav_base = np.ones(len(df))
for i in range(1, len(df)):
    nav_base[i] = nav_base[i-1] * (1 + df['ba_ret'].iloc[i])

def stats(nav, dates, t0=None, t1=None):
    if t0 is not None:
        mask = dates>=pd.Timestamp(t0)
        if t1: mask &= dates<=pd.Timestamp(t1)
        nav = nav[mask]; dates = dates[mask]
    rets = pd.Series(nav).pct_change().dropna()
    yrs = (dates.iloc[-1]-dates.iloc[0]).days/365.25
    cagr = (nav[-1]/nav[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = pd.Series(nav).cummax(); dd = (pd.Series(nav)/cm-1).min()
    return dict(cagr=cagr*100, sh=sh, dd=dd*100, calmar=cagr/abs(dd) if dd!=0 else 0)

# Variant runners
def run_v1(df, th_high, scale_tight, th_low=None, scale_loose=1.0, states=None):
    """V1: gate on composite z."""
    nav = np.ones(len(df)); n_t, n_l = 0, 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        ms = df['macro_score'].iloc[i]
        st = df['state'].iloc[i]
        if states is not None and not pd.isna(st) and int(st) not in states:
            pass
        elif not pd.isna(ms):
            if ms >= th_high:
                r = r * scale_tight; n_t += 1
            elif th_low is not None and ms <= th_low:
                r = r * scale_loose; n_l += 1
        nav[i] = nav[i-1]*(1+r)
    return nav, n_t, n_l

def run_v3(df, k_slope, states=None):
    """V3 continuous: scale = 1 - max(0, ms)*k, clipped to [0.3, 1]"""
    nav = np.ones(len(df)); n = 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        ms = df['macro_score'].iloc[i]
        st = df['state'].iloc[i]
        if states is None or (not pd.isna(st) and int(st) in states):
            if not pd.isna(ms) and ms > 0:
                scale = max(0.3, 1 - ms*k_slope)
                if scale < 1: n += 1
                r = r * scale
        nav[i] = nav[i-1]*(1+r)
    return nav, n

# Periods
periods = [('FULL 2014-2026', None, None),
           ('IS  (2014-2018)', '2014-01-01', '2018-12-31'),
           ('OOS (2019-2026)', '2019-01-01', None)]

print(f"\n{'config':<55s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Cal':>5s} {'dCAGR':>7s} {'n':>5s}")
print('-'*112)
for plabel, t0, t1 in periods:
    sb = stats(nav_base, df['time'], t0, t1)
    print(f"{'BA v11 baseline':<55s} {plabel:<18s} {sb['cagr']:7.2f} {sb['sh']:5.2f} "
          f"{sb['dd']:7.2f} {sb['calmar']:5.2f}")
print()

# V1: threshold gate (no state filter)
print("--- V1: composite gate (no state filter) ---")
for th_h, sc_t in [(1.0, 0.7), (1.5, 0.5), (0.7, 0.7), (1.0, 0.5)]:
    nav, n_t, n_l = run_v1(df, th_h, sc_t)
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"V1 th_h={th_h} sc={sc_t}{' '*30} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d}{mark}")
    print()

# V1 + state filter
print("--- V1: state {1,3} filter ---")
for th_h, sc_t in [(1.0, 0.7), (0.7, 0.7), (1.2, 0.5)]:
    nav, n_t, n_l = run_v1(df, th_h, sc_t, states={1,3})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"V1 state={{1,3}} th_h={th_h} sc={sc_t}{' '*20} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d}{mark}")
    print()

# V1: state {1,3,5} (include EX-BULL where DXY also has good IC)
print("--- V1: state {1,3,5} filter ---")
for th_h, sc_t in [(1.0, 0.7), (0.7, 0.7), (1.2, 0.5)]:
    nav, n_t, n_l = run_v1(df, th_h, sc_t, states={1,3,5})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"V1 state={{1,3,5}} th_h={th_h} sc={sc_t}{' '*18} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d}{mark}")
    print()

# V3: continuous
print("--- V3: continuous gradient (state {1,3,5}) ---")
for k in [0.15, 0.20, 0.30, 0.10]:
    nav, n = run_v3(df, k, states={1,3,5})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"V3 state={{1,3,5}} k={k}{' '*30} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n:>5d}{mark}")
    print()

# Save
df[['time','macro_score','DXY_rank252_z','EEM_ret60_z','DXY_mom60_lag60_z','state','ba_ret']].to_csv(
    'macro_composite_signal.csv', index=False)
print("Saved: macro_composite_signal.csv")
