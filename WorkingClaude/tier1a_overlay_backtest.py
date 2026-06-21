"""
Tier 1A overlay backtest.

Test DXY-based macro override on top of 5-state machine + BA stack.

Overlay design:
  RULE: When DXY rank252 >= TH_HIGH AND state in (4,5) → cap state at NEUTRAL (3)
        When DXY rank252 <= TH_LOW AND state in (1,2) → upgrade state to NEUTRAL (3) [early exit CRISIS]
        Otherwise: state unchanged

Stage 1: State-machine standalone backtest (VNINDEX allocation by state)
  allocations: state 1 → 0%, state 2 → 20%, state 3 → 70%, state 4 → 100%, state 5 → 130%
  baseline B&H = always 100%

Stage 2: BA v11 stack — overlay DXY as multiplier on max_positions or as binary gate
  Simulation proxy: when override cap fires, scale BA NAV daily return down by 0.5
  (approx: half the position size during macro-tight regime)
"""
import pandas as pd
import numpy as np
import yfinance as yf
import subprocess, io

# ── Load all data ──
ba = pd.read_csv('data/ba_v11_nav.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
state = pd.read_csv('data/_state.csv', parse_dates=['time'])
vni_csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=20000','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND t.time>="2011-01-01" ORDER BY t.time'],
                          capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(vni_csv), parse_dates=['time']).rename(columns={'Close':'VNI'})

print("Pulling DXY...")
dxy = yf.Ticker('DX-Y.NYB').history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
dxy = dxy[['Close']].rename(columns={'Close':'DXY'})
dxy.index = pd.to_datetime(dxy.index.date)
dxy['dxy_rank252'] = dxy['DXY'].rolling(252).rank(pct=True)
dxy = dxy.reset_index().rename(columns={'index':'time'})

df = vni.merge(state, on='time', how='left').merge(dxy[['time','DXY','dxy_rank252']], on='time', how='left')
df['DXY'] = df['DXY'].ffill()
df['dxy_rank252'] = df['dxy_rank252'].ffill()
df['state'] = df['state'].ffill()
df['vni_ret'] = df['VNI'].pct_change().fillna(0.0)

# State allocations (per CLAUDE.md)
ALLOC = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}

def apply_override(state_arr, dxy_rank, th_high, th_low):
    """Override state based on DXY rank. Returns new state series + override flags."""
    out = state_arr.copy()
    flags = np.zeros(len(state_arr), dtype=int)
    for i in range(len(out)):
        if np.isnan(dxy_rank[i]):
            continue
        if dxy_rank[i] >= th_high and out[i] in (4,5):
            out[i] = 3  # cap at NEUTRAL
            flags[i] = -1  # downgrade
        elif dxy_rank[i] <= th_low and out[i] in (1,2):
            out[i] = 3  # upgrade to NEUTRAL
            flags[i] = +1  # upgrade
    return out, flags

def state_nav(state_arr, vni_ret, t1_lag=1):
    """Simulate NAV with state-based allocation. T+1 execution."""
    alloc = np.array([ALLOC[int(s)] if not np.isnan(s) else 0.7 for s in state_arr])
    # Lag allocation by 1 day (T+1 execution)
    alloc_lag = np.roll(alloc, t1_lag); alloc_lag[:t1_lag] = 0.0
    # Borrow on state 5 (>100%), deposit on idle
    daily_borrow = 0.10/250
    daily_deposit = 0.06/250
    nav = np.ones(len(vni_ret))
    for i in range(1, len(nav)):
        w = alloc_lag[i]
        idle = max(0, 1-w); excess = max(0, w-1)
        r = w*vni_ret[i] + idle*daily_deposit - excess*daily_borrow
        nav[i] = nav[i-1] * (1+r)
    return nav

def stats(nav, dates, t0=None, t1=None):
    if t0 is not None:
        mask = (dates>=pd.Timestamp(t0)) & (dates<=pd.Timestamp(t1) if t1 else True)
        nav = nav[mask]; dates = dates[mask]
    rets = pd.Series(nav).pct_change().dropna()
    yrs = (dates.iloc[-1]-dates.iloc[0]).days/365.25
    cagr = (nav[-1]/nav[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = pd.Series(nav).cummax()
    dd = (pd.Series(nav)/cm-1).min()
    return dict(cagr=cagr*100, sh=sh, dd=dd*100, calmar=cagr/abs(dd) if dd!=0 else 0)

# ── Baseline: state machine no override ──
nav_base = state_nav(df['state'].values, df['vni_ret'].values)
df['nav_base'] = nav_base

# Buy & hold for reference
nav_bnh = np.ones(len(df))
for i in range(1, len(nav_bnh)):
    nav_bnh[i] = nav_bnh[i-1]*(1+df['vni_ret'].iloc[i])
df['nav_bnh'] = nav_bnh

print(f"\n{'config':<55s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calmar':>6s}")
print('-'*102)
for plabel, t0, t1 in [('FULL 2011-2026', None, None),
                        ('IS  (2011-2018)', '2011-01-01', '2018-12-31'),
                        ('OOS (2019-2026)', '2019-01-01', None)]:
    s_bnh = stats(nav_bnh, df['time'], t0, t1)
    s_base = stats(nav_base, df['time'], t0, t1)
    print(f"{'VNI Buy & Hold':<55s} {plabel:<18s} {s_bnh['cagr']:7.2f} {s_bnh['sh']:5.2f} {s_bnh['dd']:7.2f} {s_bnh['calmar']:6.2f}")
    print(f"{'State machine baseline':<55s} {plabel:<18s} {s_base['cagr']:7.2f} {s_base['sh']:5.2f} {s_base['dd']:7.2f} {s_base['calmar']:6.2f}")
print()

# ── Grid: DXY override thresholds ──
print(f"{'config':<55s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calmar':>6s} {'dCAGR':>7s}")
print('-'*108)

best = None
for th_high, th_low in [(0.85, 0.15), (0.85, 0.20), (0.80, 0.20), (0.90, 0.10),
                         (0.75, 0.20), (0.85, None), (0.80, None)]:
    th_l = -1 if th_low is None else th_low  # disable lower override
    state_new, flags = apply_override(df['state'].values, df['dxy_rank252'].values,
                                       th_high, th_l)
    nav = state_nav(state_new, df['vni_ret'].values)
    label = f"DXY override TH_HIGH={th_high} TH_LOW={th_low}"
    for plabel, t0, t1 in [('FULL 2011-2026', None, None),
                            ('IS  (2011-2018)', '2011-01-01', '2018-12-31'),
                            ('OOS (2019-2026)', '2019-01-01', None)]:
        s = stats(nav, df['time'], t0, t1)
        s_base_p = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-s_base_p['cagr']
        marker = ''
        if plabel.startswith('OOS') and d>0 and s['sh']>=s_base_p['sh']-0.02:
            marker = ' *'
        print(f"{label:<55s} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f}{marker}")
    n_down = int((flags==-1).sum()); n_up = int((flags==1).sum())
    print(f"    overrides: downgrade={n_down}, upgrade={n_up}\n")

# ── Stage 2: BA stack overlay simulation (DXY tight → scale daily return by 0.7) ──
print(f"\n{'='*108}\nSTAGE 2: BA v11 stack with DXY overlay (proxy: scale BA daily return by 0.7 when overlay active)\n{'='*108}")
ba['ba_ret'] = ba['BA_v11'].pct_change().fillna(0.0)
df = df.merge(ba[['time','ba_ret']], on='time', how='left')

def ba_overlay_nav(df_in, th_high, scale=0.7):
    """Scale BA daily return when DXY rank > th_high. Conservative proxy for cap-at-NEUTRAL override."""
    nav = np.ones(len(df_in))
    for i in range(1, len(nav)):
        r = df_in['ba_ret'].iloc[i] if not pd.isna(df_in['ba_ret'].iloc[i]) else 0.0
        dxr = df_in['dxy_rank252'].iloc[i]
        st  = df_in['state'].iloc[i]
        if not pd.isna(dxr) and dxr >= th_high and st in (4,5):
            r = r * scale  # cap exposure
        nav[i] = nav[i-1]*(1+r)
    return nav

# Restrict to BA NAV range
df_ba = df[df['ba_ret'].notna()].reset_index(drop=True)
ba_base_nav = np.ones(len(df_ba))
for i in range(1, len(ba_base_nav)):
    ba_base_nav[i] = ba_base_nav[i-1]*(1+df_ba['ba_ret'].iloc[i])

print(f"\n{'config':<55s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calmar':>6s} {'dCAGR':>7s}")
print('-'*108)
for plabel, t0, t1 in [('FULL 2014-2026', None, None),
                        ('IS  (2014-2018)', '2014-01-01', '2018-12-31'),
                        ('OOS (2019-2026)', '2019-01-01', None)]:
    sb = stats(ba_base_nav, df_ba['time'], t0, t1)
    print(f"{'BA v11 baseline':<55s} {plabel:<18s} {sb['cagr']:7.2f} {sb['sh']:5.2f} {sb['dd']:7.2f} {sb['calmar']:6.2f}")

for th_high, scale in [(0.85, 0.7), (0.85, 0.5), (0.80, 0.7), (0.90, 0.5)]:
    nav = ba_overlay_nav(df_ba, th_high, scale)
    label = f"BA + DXY overlay TH={th_high} scale={scale}"
    for plabel, t0, t1 in [('FULL 2014-2026', None, None),
                            ('IS  (2014-2018)', '2014-01-01', '2018-12-31'),
                            ('OOS (2019-2026)', '2019-01-01', None)]:
        s = stats(nav, df_ba['time'], t0, t1)
        sb = stats(ba_base_nav, df_ba['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        marker = ''
        if plabel.startswith('OOS') and d>0 and s['sh']>=sb['sh']-0.02 and s['dd']>=sb['dd']-0.5:
            marker = ' *'
        print(f"{label:<55s} {plabel:<18s} {s['cagr']:7.2f} {s['sh']:5.2f} "
              f"{s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f}{marker}")
    print()

# Save outputs
df.to_csv('data/macro_overlay_data.csv', index=False)
print("Saved: macro_overlay_data.csv")
