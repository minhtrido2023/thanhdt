"""
Backtest: Use BullDvg fires as size-up signal on BA v11 baseline.
Compare 3 modes:
  A) NO overlay (baseline)
  B) ALL BullDvg fires as trigger (unfiltered, n=33)
  C) BullDvg FILTERED to close_hi252 <= 0.85 (n=~16 high-quality fires)

Overlay: when fired, boost allocation = (1 + margin) for HOLD days.
Cost: borrow on margin × idle days.

Also walk-forward split: train (2011-2018) and test (2019-2026).
"""
import pandas as pd
import numpy as np
from itertools import product

# ── Load ──
ba = pd.read_csv('ba_v11_nav.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
v = pd.read_csv('_vni_full.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
v['ret'] = v['Close'].pct_change().fillna(0.0)
v['hi252'] = v['High'].rolling(252).max()
v['close_hi252'] = v['Close']/v['hi252']

bull = pd.read_csv('div_bull_with_newind.csv', parse_dates=['date'])

# Build VNI return lookup
vni_ret = v.set_index('time')['ret']

# Build BA daily return
ba['ba_ret'] = ba['BA_v11'].pct_change().fillna(0.0)
ba_ret = ba.set_index('time')['ba_ret']

# Common date range
common = sorted(set(ba['time']) & set(v['time']))
dates = pd.DatetimeIndex(common)
print(f"Common date range: {dates[0].date()} -> {dates[-1].date()}, n={len(dates)}")

# Fire trigger dates per mode
fires_all = bull[bull['date'].isin(dates)]['date'].tolist()
fires_filtered = bull[(bull['date'].isin(dates)) & (bull['close_hi252']<=0.85)]['date'].tolist()
print(f"All BULL fires in range: {len(fires_all)}")
print(f"FILTERED (close_hi252<=0.85) fires in range: {len(fires_filtered)}")
print("Filtered dates:", [d.date() for d in fires_filtered])

def run_overlay(fire_dates, margin_pct, hold_days, borrow_annual=0.10, cooldown_days=20):
    """Overlay: fire boost on listed dates. Each boost = margin × VNI return - daily borrow."""
    fire_set = set(pd.to_datetime(fire_dates))
    daily_borrow = borrow_annual/250
    nav = pd.Series(1.0, index=dates)
    overlay_left = 0
    cooldown_left = 0
    fires_used = []
    for i, d in enumerate(dates):
        if i == 0:
            nav.iloc[i] = 1.0
            continue
        r_ba = ba_ret.get(d, 0.0)
        r_vni = vni_ret.get(d, 0.0)

        if overlay_left == 0 and cooldown_left == 0 and d in fire_set:
            overlay_left = hold_days
            cooldown_left = hold_days + cooldown_days
            fires_used.append(d)

        extra = 0.0
        if overlay_left > 0:
            extra = margin_pct * (r_vni - daily_borrow)
            overlay_left -= 1
        if cooldown_left > 0:
            cooldown_left -= 1
        nav.iloc[i] = nav.iloc[i-1] * (1 + r_ba + extra)
    return nav, fires_used

def stats(nav, label=''):
    rets = nav.pct_change().dropna()
    n_years = (nav.index[-1]-nav.index[0]).days/365.25
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/n_years)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = nav.cummax()
    dd = (nav/cm-1).min()
    calmar = cagr/abs(dd) if dd!=0 else 0
    return dict(label=label, cagr=cagr*100, sharpe=sh, dd=dd*100, calmar=calmar)

# ── Baseline ──
nav_base, _ = run_overlay([], 0.0, 0)
s_base = stats(nav_base, 'Baseline BA v11')
print(f"\n{'Config':<55s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calmar':>6s} {'d vs base':>10s}")
print('-'*98)
print(f"{s_base['label']:<55s} {s_base['cagr']:7.2f} {s_base['sharpe']:5.2f} {s_base['dd']:7.2f} {s_base['calmar']:6.2f}")

# ── Grid ──
print()
print("=== ALL BULL fires (unfiltered, n=33) ===")
rows = []
for margin, hold in product([0.20, 0.30, 0.50], [60, 90, 120]):
    nav, fires_used = run_overlay(fires_all, margin, hold)
    s = stats(nav, f'ALL n={len(fires_used)} m={margin} h={hold}')
    delta = s['cagr']-s_base['cagr']
    rows.append({'mode':'ALL','margin':margin,'hold':hold,'n':len(fires_used),
                 **s,'dCAGR':delta})
    print(f"{s['label']:<55s} {s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {delta:+10.2f}pp")

print()
print("=== FILTERED BULL fires (close_hi252<=0.85, n=16) ===")
for margin, hold in product([0.20, 0.30, 0.50], [60, 90, 120]):
    nav, fires_used = run_overlay(fires_filtered, margin, hold)
    s = stats(nav, f'FILT n={len(fires_used)} m={margin} h={hold}')
    delta = s['cagr']-s_base['cagr']
    rows.append({'mode':'FILT','margin':margin,'hold':hold,'n':len(fires_used),
                 **s,'dCAGR':delta})
    print(f"{s['label']:<55s} {s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {delta:+10.2f}pp")

# ── Walk-forward: train weights on 2011-18, test on 2019-26 ──
# Threshold 0.85 chosen in-sample on full data. Need to verify it's stable in OOS-only window.
print()
print("="*98)
print("WALK-FORWARD: apply 0.85 threshold which was chosen in-sample. Test OOS impact only.")
print("="*98)
oos_start = pd.Timestamp('2019-01-01')
fires_oos_all = [d for d in fires_all if d >= oos_start]
fires_oos_filt = [d for d in fires_filtered if d >= oos_start]
print(f"OOS BULL fires ALL: {len(fires_oos_all)}, FILTERED: {len(fires_oos_filt)}")

# Restrict NAV to OOS
def stats_window(nav, t0, t1, label):
    n = nav[(nav.index>=t0)&(nav.index<=t1)]
    rets = n.pct_change().dropna()
    yrs = (n.index[-1]-n.index[0]).days/365.25
    cagr = (n.iloc[-1]/n.iloc[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = n.cummax()
    dd = (n/cm-1).min()
    calmar = cagr/abs(dd) if dd!=0 else 0
    return dict(label=label, cagr=cagr*100, sharpe=sh, dd=dd*100, calmar=calmar)

t0 = oos_start
t1 = dates[-1]
nav_base_oos = stats_window(nav_base, t0, t1, 'Baseline OOS')
print(f"\n{'Config (OOS 2019-26)':<55s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calmar':>6s} {'d':>8s}")
print('-'*92)
print(f"{nav_base_oos['label']:<55s} {nav_base_oos['cagr']:7.2f} {nav_base_oos['sharpe']:5.2f} "
      f"{nav_base_oos['dd']:7.2f} {nav_base_oos['calmar']:6.2f}")

for margin, hold in product([0.20, 0.30, 0.50], [60, 90, 120]):
    nav, _ = run_overlay(fires_all, margin, hold)
    s = stats_window(nav, t0, t1, f'OOS ALL m={margin} h={hold}')
    print(f"{s['label']:<55s} {s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} "
          f"{s['cagr']-nav_base_oos['cagr']:+8.2f}pp")

print()
for margin, hold in product([0.20, 0.30, 0.50], [60, 90, 120]):
    nav, _ = run_overlay(fires_filtered, margin, hold)
    s = stats_window(nav, t0, t1, f'OOS FILT m={margin} h={hold}')
    print(f"{s['label']:<55s} {s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} "
          f"{s['cagr']-nav_base_oos['cagr']:+8.2f}pp")

# Save full-period grid
pd.DataFrame(rows).to_csv('bull_div_filter_grid.csv', index=False)
print("\nSaved: bull_div_filter_grid.csv")
