"""
Tier 2B: Vietnam policy/deposit rate as macro early-warning signal.

Hypothesis: SBV rate changes are LEADING indicator distinct from price-driven
features. Unlike DXY (real-time, already in prices), SBV decisions trigger
1-3 month transmission lag — market reacts AFTER policy shifts.

Data: SBV refinancing rate (lãi suất tái cấp vốn) — manually constructed from
publicly known policy decisions. Deposit rate proxy = refi + ~1.5% spread.

Features tested:
  refi_rate          — level
  refi_chg_90d       — change in last 90 sessions
  refi_chg_180d      — change in last 180 sessions
  refi_vol_252d      — std dev of changes in last 252d (rate VOLATILITY)
  refi_direction     — sign of last 60d change (+1 hiking, -1 cutting)
  refi_level_rank    — percentile rank of level (expanding)
  cycle_position     — months since last change (regime aging)

Composite with DXY:
  macro_v2 = z(refi_chg_90d) + z(DXY_rank252) + z(EEM_ret60 inverted)
"""
import pandas as pd
import numpy as np
import yfinance as yf
import subprocess, io
from datetime import date

# ── SBV refi rate timeline (manually constructed from public SBV announcements) ──
# Source: SBV historical decisions, public news, NHNN.gov.vn archives
# Format: (effective_date, refi_rate_percent)
sbv_refi = [
    ('2008-06-11', 14.00),  # peak anti-inflation
    ('2008-10-21', 13.00),
    ('2008-11-05', 12.00),
    ('2008-12-05', 11.00),
    ('2008-12-22', 9.50),
    ('2009-02-01', 8.00),
    ('2009-04-01', 7.00),
    ('2009-12-01', 8.00),
    ('2010-11-05', 9.00),
    ('2011-02-17', 11.00),
    ('2011-04-01', 12.00),
    ('2011-05-01', 14.00),
    ('2011-10-10', 15.00),  # peak
    ('2012-03-12', 14.00),
    ('2012-04-10', 13.00),
    ('2012-05-25', 12.00),
    ('2012-06-11', 11.00),
    ('2012-07-01', 10.00),
    ('2012-12-24', 9.00),
    ('2013-03-26', 8.00),
    ('2013-05-13', 7.00),
    ('2014-03-18', 6.50),
    ('2016-01-01', 6.50),  # stable period
    ('2017-07-10', 6.25),
    ('2019-09-16', 6.00),
    ('2020-03-17', 5.00),  # Covid emergency cut
    ('2020-05-13', 4.50),
    ('2020-10-01', 4.00),
    ('2022-09-23', 5.00),  # hike — USD pressure peak
    ('2022-10-25', 6.00),  # hike again
    ('2023-03-15', 6.00),
    ('2023-03-31', 5.50),  # cut starts
    ('2023-04-03', 5.50),
    ('2023-05-25', 5.00),
    ('2023-06-19', 4.50),
    ('2024-01-01', 4.50),  # stable
    ('2025-01-01', 4.50),
    ('2026-01-01', 4.50),
]
sbv = pd.DataFrame(sbv_refi, columns=['time','refi_rate'])
sbv['time'] = pd.to_datetime(sbv['time'])

# ── Build daily series (forward-fill from event dates) ──
date_range = pd.date_range('2008-01-01', '2026-05-19', freq='D')
daily = pd.DataFrame({'time': date_range})
daily = daily.merge(sbv, on='time', how='left')
daily['refi_rate'] = daily['refi_rate'].ffill()
daily = daily.dropna()

# Features
daily['refi_chg_90d']  = daily['refi_rate'].diff(90)
daily['refi_chg_180d'] = daily['refi_rate'].diff(180)
daily['refi_vol_252d'] = daily['refi_rate'].diff().rolling(252).std()
daily['refi_direction_60d'] = np.sign(daily['refi_rate'].diff(60))
daily['refi_level_rank'] = daily['refi_rate'].expanding(min_periods=252).rank(pct=True)
# Cycle aging: days since last change
chg_dates = sbv['time'].tolist()
def days_since_change(d):
    prev = [c for c in chg_dates if c < d]
    if not prev: return 0
    return (d - max(prev)).days
daily['cycle_age_d'] = daily['time'].apply(days_since_change)

# Filter to trading-day-like cadence — merge with VNI dates
print("Loading VNI + state + DXY...")
vni_csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=20000','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND t.time>="2011-01-01" ORDER BY t.time'],
                         capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(vni_csv), parse_dates=['time']).set_index('time')
vni.columns = ['VNI']
state = pd.read_csv('_state.csv', parse_dates=['time']).set_index('time')

# Get DXY
dxy = yf.Ticker('DX-Y.NYB').history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
dxy = dxy[['Close']].rename(columns={'Close':'DXY'})
dxy.index = pd.to_datetime(dxy.index.date)
dxy['DXY_rank252'] = dxy['DXY'].rolling(252).rank(pct=True)
dxy = dxy.reset_index().rename(columns={'index':'time'})

# Merge
df = vni.reset_index().merge(daily, on='time', how='left').merge(
    state.reset_index(), on='time', how='left').merge(
    dxy[['time','DXY','DXY_rank252']], on='time', how='left')
df = df.ffill().dropna(subset=['VNI','refi_rate','state','DXY']).reset_index(drop=True)
print(f"Merged {len(df)} sessions {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")

for h in [20, 60, 120]:
    df[f'fwd{h}'] = df['VNI'].shift(-h)/df['VNI'] - 1

# ── Spearman ──
def spearman(x, y):
    x = pd.Series(x); y = pd.Series(y)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 30: return np.nan
    rx, ry = x.rank(), y.rank()
    sx, sy = rx.std(), ry.std()
    if sx*sy == 0: return np.nan
    return ((rx-rx.mean())*(ry-ry.mean())).mean()/(sx*sy)

# ── IC analysis: lag grid ──
features = ['refi_rate','refi_chg_90d','refi_chg_180d','refi_vol_252d',
            'refi_direction_60d','refi_level_rank','cycle_age_d']
lags = [0, 5, 10, 20, 40, 60, 90, 120]

print("\n" + "="*100)
print("IC TABLE — VN refi rate features vs VNI fwd60")
print("Negative IC = rate UP -> VNI DOWN (expected for level/change features)")
print("="*100)
print(f"{'feature':22s} " + " ".join(f"{'lag'+str(l):>8s}" for l in lags))
records = []
for f in features:
    row = f"{f:22s} "
    for l in lags:
        ic = spearman(df[f].shift(l), df['fwd60'])
        row += f" {ic:+8.3f}" if not np.isnan(ic) else f" {'nan':>8s}"
        records.append({'feat':f,'lag':l,'horizon':60,'ic':ic})
    print(row)

print(f"\n--- fwd120 ---")
print(f"{'feature':22s} " + " ".join(f"{'lag'+str(l):>8s}" for l in lags))
for f in features:
    row = f"{f:22s} "
    for l in lags:
        ic = spearman(df[f].shift(l), df['fwd120'])
        row += f" {ic:+8.3f}" if not np.isnan(ic) else f" {'nan':>8s}"
        records.append({'feat':f,'lag':l,'horizon':120,'ic':ic})
    print(row)

# Top by |IC|
rec = pd.DataFrame(records)
rec['abs_ic'] = rec['ic'].abs()
print("\n--- TOP 10 (feat, lag) at fwd60 ---")
print(rec[rec['horizon']==60].nlargest(10, 'abs_ic')[['feat','lag','ic']].to_string(index=False))

# Walk-forward
print("\n--- WALK-FORWARD top candidates ---")
df_is = df[df['time'] < '2019-01-01']
df_oos = df[df['time'] >= '2019-01-01']
print(f"IS n={len(df_is)}  OOS n={len(df_oos)}")
print(f"{'feat':22s} {'lag':>4s} {'h':>4s} {'IC_full':>9s} {'IC_IS':>9s} {'IC_OOS':>9s} {'cons':>5s}")
for _, r in rec.nlargest(15, 'abs_ic').iterrows():
    f, l, h = r['feat'], int(r['lag']), int(r['horizon'])
    ic_is  = spearman(df_is[f].shift(l), df_is[f'fwd{h}'])
    ic_oos = spearman(df_oos[f].shift(l), df_oos[f'fwd{h}'])
    cons = (not np.isnan(ic_is) and not np.isnan(ic_oos)
            and np.sign(ic_is)==np.sign(ic_oos)
            and abs(ic_is)>=0.10 and abs(ic_oos)>=0.10)
    print(f"{f:22s} {l:>4d} {h:>4d} {r['ic']:+9.3f} {ic_is:+9.3f} {ic_oos:+9.3f} {'YES' if cons else 'no':>5s}")

# Partial correlation over DXY
def partial_corr(a, b, c):
    a = pd.Series(a); b = pd.Series(b); c = pd.Series(c)
    m = a.notna() & b.notna() & c.notna()
    a, b, c = a[m], b[m], c[m]
    if len(a) < 40: return np.nan
    ra, rb, rc = a.rank(), b.rank(), c.rank()
    beta_ac = ((ra-ra.mean())*(rc-rc.mean())).sum()/max(((rc-rc.mean())**2).sum(),1e-9)
    beta_bc = ((rb-rb.mean())*(rc-rc.mean())).sum()/max(((rc-rc.mean())**2).sum(),1e-9)
    res_a = ra - beta_ac*rc
    res_b = rb - beta_bc*rc
    sa, sb = res_a.std(), res_b.std()
    if sa*sb == 0: return np.nan
    return ((res_a-res_a.mean())*(res_b-res_b.mean())).mean()/(sa*sb)

print("\n--- MARGINAL IC over DXY_rank252 (fwd60) ---")
print(f"{'feat':22s} {'lag':>4s} {'raw IC':>8s} {'partial':>9s}")
for _, r in rec[rec['horizon']==60].nlargest(10, 'abs_ic').iterrows():
    f, l = r['feat'], int(r['lag'])
    pic = partial_corr(df[f].shift(l), df['fwd60'], df['DXY_rank252'])
    print(f"{f:22s} {l:>4d} {r['ic']:+8.3f} {pic:+9.3f}")

# Composite signal: combine SBV change + DXY
def expanding_z(s, min_periods=252):
    return (s - s.expanding(min_periods=min_periods).mean()) / s.expanding(min_periods=min_periods).std()

df['refi_chg_90d_z']  = expanding_z(df['refi_chg_90d'])
df['DXY_rank252_z']   = expanding_z(df['DXY_rank252'])
df['macro_v2'] = (df['refi_chg_90d_z'].fillna(0) + df['DXY_rank252_z'].fillna(0)) / 2

ic_v2_60 = spearman(df['macro_v2'], df['fwd60'])
ic_v2_120 = spearman(df['macro_v2'], df['fwd120'])
print(f"\n--- Composite macro_v2 (refi_chg_90d_z + DXY_rank252_z) ---")
print(f"IC fwd60:  {ic_v2_60:+.3f}")
print(f"IC fwd120: {ic_v2_120:+.3f}")

# Test with various lags
for l in [0, 30, 60, 90]:
    ic = spearman(df['macro_v2'].shift(l), df['fwd60'])
    print(f"  lag={l}: IC fwd60 = {ic:+.3f}")

# Walk-forward (recompute splits AFTER macro_v2 column exists)
df_is2 = df[df['time'] < '2019-01-01']
df_oos2 = df[df['time'] >= '2019-01-01']
ic_v2_is = spearman(df_is2['macro_v2'], df_is2['fwd60'])
ic_v2_oos = spearman(df_oos2['macro_v2'], df_oos2['fwd60'])
print(f"\nmacro_v2 fwd60: IS={ic_v2_is:+.3f}, OOS={ic_v2_oos:+.3f}")

# Save
df.to_csv('tier2b_sbv_panel.csv', index=False)
print("\nSaved: tier2b_sbv_panel.csv")
