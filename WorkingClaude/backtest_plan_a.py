"""
Plan A backtest: tactical deployment lift on filtered BullDvg fires.
No borrow. Uses idle cash + capacity expansion. Treat overlay as
extra exposure to VNI-correlated BA basket = approximation only.

Compare:
  - Baseline BA v11
  - Plan A lift {15%, 25%, 35%} for {45, 60, 90} sessions
  - Plan B (margin) at borrow=10% for same lift levels — for reference
"""
import pandas as pd
import numpy as np
from itertools import product

ba = pd.read_csv('data/ba_v11_nav.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
v  = pd.read_csv('data/_vni_full.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
v['ret'] = v['Close'].pct_change().fillna(0.0)
v['hi252'] = v['High'].rolling(252).max()
v['close_hi252'] = v['Close']/v['hi252']

bull = pd.read_csv('data/div_bull_with_newind.csv', parse_dates=['date'])
ba['ba_ret'] = ba['BA_v11'].pct_change().fillna(0.0)

dates = pd.DatetimeIndex(sorted(set(ba['time']) & set(v['time'])))
ba_ret_lk = ba.set_index('time')['ba_ret']
vni_ret_lk = v.set_index('time')['ret']

fires_all      = bull[bull['date'].isin(dates)]['date'].tolist()
fires_filtered = bull[(bull['date'].isin(dates)) & (bull['close_hi252']<=0.85)]['date'].tolist()

def run(fire_dates, lift_pct, hold_days, borrow_annual=0.0, cooldown_days=20):
    fire_set = set(pd.to_datetime(fire_dates))
    daily_borrow = borrow_annual/250
    nav = pd.Series(1.0, index=dates)
    overlay_left = 0
    cooldown_left = 0
    fires_used = []
    for i, d in enumerate(dates):
        if i == 0:
            continue
        r_ba  = ba_ret_lk.get(d, 0.0)
        r_vni = vni_ret_lk.get(d, 0.0)
        if overlay_left == 0 and cooldown_left == 0 and d in fire_set:
            overlay_left  = hold_days
            cooldown_left = hold_days + cooldown_days
            fires_used.append(d)
        extra = 0.0
        if overlay_left > 0:
            # Plan A approximation: extra exposure correlated with VNI
            # but execution is via BA basket (corr ~0.65 typical)
            # Simpler approx: use VNI return directly (conservative)
            extra = lift_pct * (r_vni - daily_borrow)
            overlay_left -= 1
        if cooldown_left > 0:
            cooldown_left -= 1
        nav.iloc[i] = nav.iloc[i-1] * (1 + r_ba + extra)
    return nav, fires_used

def stats_w(nav, t0, t1):
    n = nav[(nav.index>=t0)&(nav.index<=t1)]
    if len(n)<10: return None
    rets = n.pct_change().dropna()
    yrs = (n.index[-1]-n.index[0]).days/365.25
    cagr = (n.iloc[-1]/n.iloc[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = n.cummax(); dd = (n/cm-1).min()
    return dict(cagr=cagr*100, sharpe=sh, dd=dd*100, calmar=cagr/abs(dd) if dd!=0 else 0)

# Full + OOS periods
periods = [('FULL', dates[0], dates[-1]),
           ('IS  (2014-2018)', pd.Timestamp('2014-01-01'), pd.Timestamp('2018-12-31')),
           ('OOS (2019-2026)', pd.Timestamp('2019-01-01'), dates[-1])]

# Baseline
nav_base, _ = run([], 0.0, 0)

print(f"\n{'config':<42s} {'period':<18s} {'n':>3s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calm':>5s} {'dCAGR':>7s}")
print('-'*108)
for plabel,t0,t1 in periods:
    s = stats_w(nav_base, t0, t1)
    print(f"{'Baseline BA v11':<42s} {plabel:<18s} {'-':>3s} "
          f"{s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:5.2f} {'':>7s}")

print()
print("=== PLAN A (no borrow, lift via cash/capacity) — FILTERED BullDvg ===")
rows = []
for lift, hold in product([0.15, 0.25, 0.35, 0.50], [45, 60, 90]):
    nav, used = run(fires_filtered, lift, hold, borrow_annual=0.0)
    label = f"PlanA lift={int(lift*100)}% hold={hold}"
    for plabel,t0,t1 in periods:
        s = stats_w(nav, t0, t1)
        if s is None: continue
        s_base = stats_w(nav_base, t0, t1)
        dC = s['cagr']-s_base['cagr']
        rows.append({'mode':'PlanA','lift':lift,'hold':hold,'period':plabel,
                     'n_fires':len(used),**s,'dCAGR':dC})
        marker = ''
        if plabel.startswith('OOS') and dC>0 and s['sharpe']>=s_base['sharpe']-0.005 and s['dd']>=s_base['dd']-0.5:
            marker = ' *'
        print(f"{label:<42s} {plabel:<18s} {len(used):>3d} "
              f"{s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:5.2f} {dC:+7.2f}{marker}")
    print()

print()
print("=== PLAN B (margin, borrow=10%/yr) — same trigger, for reference ===")
for lift, hold in product([0.30, 0.50], [60, 90]):
    nav, used = run(fires_filtered, lift, hold, borrow_annual=0.10)
    label = f"PlanB lift={int(lift*100)}% hold={hold}"
    for plabel,t0,t1 in periods:
        s = stats_w(nav, t0, t1)
        if s is None: continue
        s_base = stats_w(nav_base, t0, t1)
        dC = s['cagr']-s_base['cagr']
        rows.append({'mode':'PlanB','lift':lift,'hold':hold,'period':plabel,
                     'n_fires':len(used),**s,'dCAGR':dC})
        print(f"{label:<42s} {plabel:<18s} {len(used):>3d} "
              f"{s['cagr']:7.2f} {s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:5.2f} {dC:+7.2f}")
    print()

# Pick winner config (OOS based)
df = pd.DataFrame(rows)
df_oos = df[df['period'].str.startswith('OOS') & (df['mode']=='PlanA')].copy()
df_oos['score'] = df_oos['dCAGR'] + (df_oos['sharpe']-1.14)*20  # composite
df_oos = df_oos.sort_values('score', ascending=False)
print("\n=== PLAN A OOS leaderboard (composite score = dCAGR + 20*(Sh - baseline)) ===")
print(df_oos[['lift','hold','n_fires','cagr','sharpe','dd','calmar','dCAGR','score']].head(10).to_string(index=False))

df.to_csv('data/plan_a_grid.csv', index=False)
print("\nSaved: plan_a_grid.csv")
