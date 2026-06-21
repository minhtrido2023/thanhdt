"""
Tier 2B overlay: SBV refi rate change (lagged 90d) + DXY composite.

Strongest signal: refi_chg_90d at lag=90 → fwd120 IC -0.276 walk-forward consistent.
Partial IC over DXY -0.199 — meaningful marginal info.

Overlay design:
  signal = z(refi_chg_90d_lag90) + z(DXY_rank252)
  When signal > th_tight  → scale BA daily return by sc_tight (defensive)
  When signal < th_loose → scale by sc_loose (>1 = aggressive)
  Hold for HOLD_DAYS sessions then re-evaluate (avoid daily flip-flop)

Test integrated BA stack.
"""
import pandas as pd
import numpy as np

df = pd.read_csv('tier2b_sbv_panel.csv', parse_dates=['time'])
ba = pd.read_csv('ba_v11_nav.csv', parse_dates=['time'])
df = df.merge(ba[['time','BA_v11']], on='time', how='left')
df['ba_ret'] = df['BA_v11'].pct_change().fillna(0.0)
df = df[df['BA_v11'].notna()].reset_index(drop=True)

# Build features
def ez(s, mp=252):
    return (s - s.expanding(min_periods=mp).mean()) / s.expanding(min_periods=mp).std()

df['refi_chg_90d_lag90']  = df['refi_chg_90d'].shift(90)
df['refi_chg_180d_lag60'] = df['refi_chg_180d'].shift(60)
df['refi_dir60_lag120']   = df['refi_direction_60d'].shift(120)

# Standardized composites
df['z_refi'] = ez(df['refi_chg_90d_lag90'])
df['z_dxy']  = ez(df['DXY_rank252'])
df['z_refi_long'] = ez(df['refi_chg_180d_lag60'])

# v2 composite: rate change + DXY
df['macro_v2'] = (df['z_refi'].fillna(0) + df['z_dxy'].fillna(0)) / 2
# v2b composite: 3-way (rate short, rate long, DXY)
df['macro_v2b'] = (df['z_refi'].fillna(0) + df['z_dxy'].fillna(0) + df['z_refi_long'].fillna(0)) / 3
# v2c: rate-only
df['macro_v2c'] = df['z_refi'].fillna(0)

print(f"macro_v2 range: {df['macro_v2'].min():.2f} to {df['macro_v2'].max():.2f}")
print(f"  >= 1.0: {(df['macro_v2']>=1.0).sum()} sessions")
print(f"  <= -1.0: {(df['macro_v2']<=-1.0).sum()} sessions")
print(f"macro_v2c range: {df['macro_v2c'].min():.2f} to {df['macro_v2c'].max():.2f}")

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

def run_overlay(df, col, th_tight, sc_tight, th_loose=None, sc_loose=1.0,
                states=None, min_hold=20):
    """Two-sided overlay with min-hold to avoid daily flip."""
    nav = np.ones(len(df))
    cur_scale = 1.0; cur_hold = 0
    n_t, n_l = 0, 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        ms = df[col].iloc[i]
        st = df['state'].iloc[i]
        if cur_hold > 0:
            r = r * cur_scale
            if cur_scale < 1: n_t += 1
            elif cur_scale > 1: n_l += 1
            cur_hold -= 1
        elif (states is None or (not pd.isna(st) and int(st) in states)) and not pd.isna(ms):
            if ms >= th_tight:
                cur_scale = sc_tight; cur_hold = min_hold-1
                r = r * sc_tight; n_t += 1
            elif th_loose is not None and ms <= th_loose:
                cur_scale = sc_loose; cur_hold = min_hold-1
                r = r * sc_loose; n_l += 1
            else:
                cur_scale = 1.0
        nav[i] = nav[i-1]*(1+r)
    return nav, n_t, n_l

periods = [('FULL 2014-2026', None, None),
           ('IS  (2014-2018)', '2014-01-01', '2018-12-31'),
           ('OOS (2019-2026)', '2019-01-01', None)]

print(f"\n{'config':<60s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Cal':>5s} {'dCAGR':>7s} {'tight':>5s} {'loose':>5s}")
print('-'*120)
for plabel, t0, t1 in periods:
    sb = stats(nav_base, df['time'], t0, t1)
    print(f"{'BA v11 baseline':<60s} {plabel:<18s} {sb['cagr']:7.2f} {sb['sh']:5.2f} "
          f"{sb['dd']:7.2f} {sb['calmar']:5.2f}")
print()

# Test 1: rate-only composite
print("--- macro_v2c (refi_chg_90d_lag90 only) ---")
for th_h, sc in [(0.5, 0.7), (1.0, 0.7), (0.5, 0.5), (1.0, 0.5)]:
    nav, n_t, n_l = run_overlay(df, 'macro_v2c', th_h, sc, min_hold=20)
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"v2c th={th_h} sc={sc} (one-side){' '*22} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d} {n_l:>5d}{mark}")
    print()

# Test 1b: two-sided rate-only
print("--- macro_v2c two-sided (tight + loose boost) ---")
for th_h, sc, th_l, sc_l in [(0.5,0.7,-0.5,1.15), (1.0,0.7,-1.0,1.2), (0.5,0.8,-0.5,1.10)]:
    nav, n_t, n_l = run_overlay(df, 'macro_v2c', th_h, sc, th_l, sc_l, min_hold=20)
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"v2c th_h={th_h} sc_t={sc} th_l={th_l} sc_l={sc_l}{' '*5} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d} {n_l:>5d}{mark}")
    print()

# Test 2: macro_v2 (rate + DXY composite)
print("--- macro_v2 (rate + DXY, two-sided) ---")
for th_h, sc, th_l, sc_l in [(0.5,0.7,-0.5,1.15), (1.0,0.7,-1.0,1.2), (0.7,0.7,-0.7,1.15),
                              (0.5,0.5,-0.5,1.2)]:
    nav, n_t, n_l = run_overlay(df, 'macro_v2', th_h, sc, th_l, sc_l, min_hold=20)
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"v2 th_h={th_h} sc_t={sc} th_l={th_l} sc_l={sc_l}{' '*8} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d} {n_l:>5d}{mark}")
    print()

# Test 3: state-conditional
print("--- macro_v2 state={1,3} ---")
for th_h, sc, th_l, sc_l in [(0.5,0.7,-0.5,1.15), (1.0,0.7,-1.0,1.2)]:
    nav, n_t, n_l = run_overlay(df, 'macro_v2', th_h, sc, th_l, sc_l, states={1,3}, min_hold=20)
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        mark = ' *' if (plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02
                        and s['dd']>=sb['dd']-0.5) else ''
        print(f"v2 state{{1,3}} th_h={th_h} sc_t={sc} th_l={th_l} sc_l={sc_l} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:5.2f} {d:+7.2f} {n_t:>5d} {n_l:>5d}{mark}")
    print()

# Save
df.to_csv('tier2b_overlay_data.csv', index=False)
