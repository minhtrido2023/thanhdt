"""
Sensitivity + robustness for SBV+DXY composite overlay.

Tests:
  1) Lag grid: {30, 60, 75, 90, 105, 120, 150}
  2) Threshold grid: th_h × th_l × scale combinations
  3) Min-hold grid: {10, 15, 20, 25, 30, 40, 60}
  4) Sub-period stability: 2014-18 / 2019-21 / 2022-26 split
  5) Drop-one-event: remove each rate change, re-run with best config
  6) Date noise: ±5 day perturbation on event dates
  7) Alternative variable: use deposit rate proxy = refi + 1.5%
"""
import pandas as pd
import numpy as np
import yfinance as yf
import subprocess, io
from itertools import product

# ── Build SBV with corrected dates ──
sbv_refi_corrected = [
    ('2008-06-11', 14.00), ('2008-10-21', 13.00), ('2008-11-05', 12.00),
    ('2008-12-05', 11.00), ('2008-12-22', 9.50),  ('2009-02-01', 8.00),
    ('2009-04-01', 7.00),  ('2009-12-01', 8.00),  ('2010-11-05', 9.00),
    ('2011-02-17', 11.00), ('2011-04-01', 12.00), ('2011-05-01', 14.00),
    ('2011-10-10', 15.00), ('2012-03-12', 14.00), ('2012-04-10', 13.00),
    ('2012-05-25', 12.00), ('2012-06-11', 11.00), ('2012-07-01', 10.00),
    ('2012-12-24', 9.00),  ('2013-03-26', 8.00),  ('2013-05-13', 7.00),
    ('2014-03-18', 6.50),  ('2017-07-10', 6.25),  ('2019-09-16', 6.00),
    ('2020-03-17', 5.00),  ('2020-05-13', 4.50),  ('2020-10-01', 4.00),
    ('2022-09-23', 5.00),  ('2022-10-25', 6.00),
    # CORRECTED: 2023-03-31 -> 2023-04-03
    ('2023-04-03', 5.50),  ('2023-05-25', 5.00),  ('2023-06-19', 4.50),
]

def build_refi_series(events, start='2008-01-01', end='2026-05-19'):
    sbv = pd.DataFrame(events, columns=['time','refi_rate'])
    sbv['time'] = pd.to_datetime(sbv['time'])
    dr = pd.date_range(start, end, freq='D')
    d = pd.DataFrame({'time': dr}).merge(sbv, on='time', how='left')
    d['refi_rate'] = d['refi_rate'].ffill()
    return d.dropna()

# ── Load VNI + state + DXY ──
print("Loading market data...")
vni_csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=20000','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND t.time>="2011-01-01" ORDER BY t.time'],
                         capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(vni_csv), parse_dates=['time']).rename(columns={'Close':'VNI'})
state = pd.read_csv('_state.csv', parse_dates=['time'])
ba = pd.read_csv('ba_v11_nav.csv', parse_dates=['time'])

dxy = yf.Ticker('DX-Y.NYB').history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
dxy = dxy[['Close']].rename(columns={'Close':'DXY'})
dxy.index = pd.to_datetime(dxy.index.date)
dxy['DXY_rank252'] = dxy['DXY'].rolling(252).rank(pct=True)
dxy = dxy.reset_index().rename(columns={'index':'time'})

def build_panel(events):
    daily = build_refi_series(events)
    daily['refi_chg_90d']  = daily['refi_rate'].diff(90)
    df = vni.merge(daily, on='time', how='left').merge(state, on='time', how='left').merge(
         dxy[['time','DXY','DXY_rank252']], on='time', how='left').merge(
         ba[['time','BA_v11']], on='time', how='left')
    df = df.ffill().dropna(subset=['VNI','refi_rate','state','DXY','BA_v11']).reset_index(drop=True)
    df['ba_ret'] = df['BA_v11'].pct_change().fillna(0.0)
    return df

def ez(s, mp=252):
    return (s - s.expanding(min_periods=mp).mean()) / s.expanding(min_periods=mp).std()

def make_signal(df, lag, weight_dxy=1.0):
    s = df.copy()
    s['z_refi'] = ez(s['refi_chg_90d'].shift(lag))
    s['z_dxy']  = ez(s['DXY_rank252'])
    s['macro'] = (s['z_refi'].fillna(0) + weight_dxy*s['z_dxy'].fillna(0)) / (1+weight_dxy)
    return s

def run_overlay(df, th_h, sc_t, th_l, sc_l, min_hold=20, signal_col='macro'):
    nav = np.ones(len(df))
    cur_sc = 1.0; cur_hold = 0
    n_t, n_l = 0, 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        ms = df[signal_col].iloc[i]
        if cur_hold > 0:
            r = r * cur_sc
            if cur_sc < 1: n_t += 1
            elif cur_sc > 1: n_l += 1
            cur_hold -= 1
        elif not pd.isna(ms):
            if ms >= th_h:
                cur_sc = sc_t; cur_hold = min_hold-1; r = r*sc_t; n_t += 1
            elif ms <= th_l:
                cur_sc = sc_l; cur_hold = min_hold-1; r = r*sc_l; n_l += 1
            else:
                cur_sc = 1.0
        nav[i] = nav[i-1]*(1+r)
    return nav, n_t, n_l

def stats(nav, dates, t0=None, t1=None):
    if t0 is not None:
        mask = dates>=pd.Timestamp(t0)
        if t1: mask &= dates<=pd.Timestamp(t1)
        nav = nav[mask]; dates = dates[mask]
    if len(nav) < 30: return None
    rets = pd.Series(nav).pct_change().dropna()
    yrs = (dates.iloc[-1]-dates.iloc[0]).days/365.25
    cagr = (nav[-1]/nav[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = pd.Series(nav).cummax(); dd = (pd.Series(nav)/cm-1).min()
    return dict(cagr=cagr*100, sh=sh, dd=dd*100, calmar=cagr/abs(dd) if dd!=0 else 0)

df = build_panel(sbv_refi_corrected)
print(f"Panel: {len(df)} rows {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")

# Baseline
nav_base = np.ones(len(df))
for i in range(1, len(df)):
    nav_base[i] = nav_base[i-1] * (1 + df['ba_ret'].iloc[i])

periods = [('FULL', None, None),
           ('IS', '2014-01-01', '2018-12-31'),
           ('OOS1 2019-21', '2019-01-01', '2021-12-31'),
           ('OOS2 2022-26', '2022-01-01', None)]

print(f"\n=== BASELINE BA v11 ===")
for plabel, t0, t1 in periods:
    s = stats(nav_base, df['time'], t0, t1)
    if s: print(f"  {plabel:<14s} CAGR={s['cagr']:6.2f}  Sh={s['sh']:5.2f}  DD={s['dd']:6.2f}  Calmar={s['calmar']:5.2f}")

# ── Test 1: Lag sensitivity (anchor: th=1.0/-1.0, sc=0.7/1.2, min_hold=20) ──
print(f"\n{'='*100}\nTEST 1: LAG SENSITIVITY (anchor th=±1.0 sc=0.7/1.2 min_hold=20)\n{'='*100}")
print(f"{'lag':>6s}  {'OOS1 dCAGR':>12s} {'OOS2 dCAGR':>12s} {'IS dCAGR':>10s} {'FULL dCAGR':>12s} {'OOS_Sh':>8s}")
for lag in [30, 60, 75, 90, 105, 120, 150]:
    d = make_signal(df, lag)
    nav, _, _ = run_overlay(d, 1.0, 0.7, -1.0, 1.2)
    out = []
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        out.append((s, sb))
    full = out[0]; is_ = out[1]; oos1 = out[2]; oos2 = out[3]
    oos_sh = (oos1[0]['sh'] + oos2[0]['sh']) / 2 if oos1[0] and oos2[0] else 0
    print(f"{lag:>6d}  {oos1[0]['cagr']-oos1[1]['cagr']:+12.2f} {oos2[0]['cagr']-oos2[1]['cagr']:+12.2f} "
          f"{is_[0]['cagr']-is_[1]['cagr']:+10.2f} {full[0]['cagr']-full[1]['cagr']:+12.2f} {oos_sh:>8.2f}")

# ── Test 2: Threshold sensitivity ──
print(f"\n{'='*100}\nTEST 2: THRESHOLD SENSITIVITY (anchor lag=90 min_hold=20)\n{'='*100}")
print(f"{'th_h':>6s} {'th_l':>6s} {'sc_t':>5s} {'sc_l':>5s}  "
      f"{'OOS1 d':>8s} {'OOS2 d':>8s} {'IS d':>7s} {'FULL d':>8s} {'OOS_Sh':>7s} {'n_tight':>7s} {'n_loose':>7s}")
d = make_signal(df, 90)
for th_h, th_l, sc_t, sc_l in product([0.5, 0.7, 1.0], [-0.5, -0.7, -1.0], [0.7], [1.15, 1.2]):
    nav, n_t, n_l = run_overlay(d, th_h, sc_t, th_l, sc_l)
    out = [stats(nav, df['time'], t0, t1) for _, t0, t1 in periods]
    base_out = [stats(nav_base, df['time'], t0, t1) for _, t0, t1 in periods]
    if any(x is None for x in out): continue
    print(f"{th_h:>6.1f} {th_l:>6.1f} {sc_t:>5.1f} {sc_l:>5.2f}  "
          f"{out[2]['cagr']-base_out[2]['cagr']:+8.2f} "
          f"{out[3]['cagr']-base_out[3]['cagr']:+8.2f} "
          f"{out[1]['cagr']-base_out[1]['cagr']:+7.2f} "
          f"{out[0]['cagr']-base_out[0]['cagr']:+8.2f} "
          f"{(out[2]['sh']+out[3]['sh'])/2:>7.2f} {n_t:>7d} {n_l:>7d}")

# ── Test 3: Min-hold sensitivity ──
print(f"\n{'='*100}\nTEST 3: MIN-HOLD SENSITIVITY (anchor lag=90 th=±1.0)\n{'='*100}")
print(f"{'min_hold':>9s} {'FULL d':>8s} {'IS d':>7s} {'OOS1 d':>8s} {'OOS2 d':>8s} {'OOS_Sh':>7s}")
d = make_signal(df, 90)
for mh in [5, 10, 15, 20, 25, 30, 40, 60]:
    nav, _, _ = run_overlay(d, 1.0, 0.7, -1.0, 1.2, min_hold=mh)
    out = [stats(nav, df['time'], t0, t1) for _, t0, t1 in periods]
    base_out = [stats(nav_base, df['time'], t0, t1) for _, t0, t1 in periods]
    if any(x is None for x in out): continue
    print(f"{mh:>9d} {out[0]['cagr']-base_out[0]['cagr']:+8.2f} "
          f"{out[1]['cagr']-base_out[1]['cagr']:+7.2f} "
          f"{out[2]['cagr']-base_out[2]['cagr']:+8.2f} "
          f"{out[3]['cagr']-base_out[3]['cagr']:+8.2f} "
          f"{(out[2]['sh']+out[3]['sh'])/2:>7.2f}")

# ── Test 4: Date noise (perturb each event ±5 days, 20 trials) ──
print(f"\n{'='*100}\nTEST 4: DATE NOISE — perturb each event date by uniform ±5 days, 20 trials\n{'='*100}")
np.random.seed(42)
trials = []
for trial in range(20):
    noisy = []
    for date_str, rate in sbv_refi_corrected:
        d = pd.Timestamp(date_str)
        d_noisy = d + pd.Timedelta(days=int(np.random.randint(-5, 6)))
        noisy.append((d_noisy.strftime('%Y-%m-%d'), rate))
    noisy = sorted(noisy)
    df_n = build_panel(noisy)
    sig = make_signal(df_n, 90)
    nav, _, _ = run_overlay(sig, 1.0, 0.7, -1.0, 1.2)
    nav_b = np.ones(len(df_n))
    for i in range(1, len(df_n)):
        nav_b[i] = nav_b[i-1]*(1+df_n['ba_ret'].iloc[i])
    s_full = stats(nav, df_n['time'])
    sb_full = stats(nav_b, df_n['time'])
    s_oos = stats(nav, df_n['time'], '2019-01-01', None)
    sb_oos = stats(nav_b, df_n['time'], '2019-01-01', None)
    trials.append({'full_d': s_full['cagr']-sb_full['cagr'], 'oos_d': s_oos['cagr']-sb_oos['cagr']})

t = pd.DataFrame(trials)
print(f"Date noise robustness (20 trials, ±5d uniform):")
print(f"  FULL dCAGR: mean={t['full_d'].mean():+.2f}  std={t['full_d'].std():.2f}  "
      f"min={t['full_d'].min():+.2f}  max={t['full_d'].max():+.2f}")
print(f"  OOS  dCAGR: mean={t['oos_d'].mean():+.2f}  std={t['oos_d'].std():.2f}  "
      f"min={t['oos_d'].min():+.2f}  max={t['oos_d'].max():+.2f}")
print(f"  Trials with positive FULL: {(t['full_d']>0).sum()}/20")
print(f"  Trials with positive OOS:  {(t['oos_d']>0).sum()}/20")

# ── Test 5: Drop-one-event ──
print(f"\n{'='*100}\nTEST 5: DROP-ONE-EVENT — remove each rate change post-2014\n{'='*100}")
print(f"{'dropped_event':<22s} {'FULL d':>8s} {'IS d':>7s} {'OOS d':>7s}")
events_to_test = [e for e in sbv_refi_corrected if pd.Timestamp(e[0]) >= pd.Timestamp('2014-01-01')]
for drop_event in events_to_test:
    reduced = [e for e in sbv_refi_corrected if e != drop_event]
    df_r = build_panel(reduced)
    sig = make_signal(df_r, 90)
    nav, _, _ = run_overlay(sig, 1.0, 0.7, -1.0, 1.2)
    nav_b = np.ones(len(df_r))
    for i in range(1, len(df_r)):
        nav_b[i] = nav_b[i-1]*(1+df_r['ba_ret'].iloc[i])
    s_full = stats(nav, df_r['time'])
    sb_full = stats(nav_b, df_r['time'])
    s_is = stats(nav, df_r['time'], '2014-01-01', '2018-12-31')
    sb_is = stats(nav_b, df_r['time'], '2014-01-01', '2018-12-31')
    s_oos = stats(nav, df_r['time'], '2019-01-01', None)
    sb_oos = stats(nav_b, df_r['time'], '2019-01-01', None)
    print(f"{drop_event[0]+' '+str(drop_event[1])+'%':<22s} {s_full['cagr']-sb_full['cagr']:+8.2f} "
          f"{s_is['cagr']-sb_is['cagr']:+7.2f} {s_oos['cagr']-sb_oos['cagr']:+7.2f}")

# Final report on robust config
print(f"\n{'='*100}\nROBUST CONFIG SUMMARY\n{'='*100}")
sig = make_signal(df, 90)
nav, n_t, n_l = run_overlay(sig, 1.0, 0.7, -1.0, 1.2, min_hold=20)
for plabel, t0, t1 in periods:
    s = stats(nav, df['time'], t0, t1)
    sb = stats(nav_base, df['time'], t0, t1)
    if s: print(f"  {plabel:<14s} CAGR={s['cagr']:6.2f}({s['cagr']-sb['cagr']:+.2f})  "
                f"Sh={s['sh']:5.2f}({s['sh']-sb['sh']:+.2f})  "
                f"DD={s['dd']:6.2f}  Calmar={s['calmar']:5.2f}")
print(f"  Fires: tight={n_t}, loose={n_l}")
