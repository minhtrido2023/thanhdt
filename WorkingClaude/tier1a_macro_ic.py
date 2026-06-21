"""
Tier 1A research: DXY + USDVND as macro overlay candidates for 5-state.

Approach:
  1) Pull DXY + USDVND daily 2010-2026
  2) Pull VNINDEX + 5-state from BQ
  3) Construct candidate features:
       - dxy_mom20: 20d % change in DXY
       - dxy_z60:   DXY z-score on 60d (expanding)
       - vnd_mom20: 20d % change in USDVND
       - vnd_rank60: USDVND percentile rank vs trailing 60d
       - dxy_vnd_compound: dxy_mom20 + vnd_mom20 (both up = double pressure)
  4) Measure IC at fwd 5/20/60/120d:
       - vs raw VNI returns
       - vs (raw - state-conditional baseline)
  5) Walk-forward: IS 2011-18 / OOS 2019-26
  6) Composite: best 2-3 features → overlay design
"""
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

# ── spearman (no scipy) ──
def spearman(x, y):
    x = pd.Series(x); y = pd.Series(y)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 30: return (np.nan, len(x))
    rx, ry = x.rank(), y.rank()
    sx, sy = rx.std(), ry.std()
    if sx*sy == 0: return (np.nan, len(x))
    rho = ((rx-rx.mean())*(ry-ry.mean())).mean()/(sx*sy)
    return (rho, len(x))

# ── Pull macro ──
print("Pulling DXY + USDVND from yfinance...")
dxy = yf.Ticker('DX-Y.NYB').history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
dxy = dxy[['Close']].rename(columns={'Close':'DXY'})
dxy.index = pd.to_datetime(dxy.index.date)

vnd = yf.Ticker('USDVND=X').history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
vnd = vnd[['Close']].rename(columns={'Close':'USDVND'})
vnd.index = pd.to_datetime(vnd.index.date)

# ── Pull VNI + state ──
import subprocess, io
sql_vni = ('SELECT t.time, t.Close FROM tav2_bq.ticker AS t '
           'WHERE t.ticker="VNINDEX" AND t.time >= "2010-01-01" ORDER BY t.time')
csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                      '--format=csv','--max_rows=20000','-q',sql_vni],
                     capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(csv), parse_dates=['time']).rename(columns={'Close':'VNI'})
vni.set_index('time', inplace=True)

state = pd.read_csv('_state.csv', parse_dates=['time']).set_index('time')

# ── Merge ──
df = vni.join(dxy, how='left').join(vnd, how='left').join(state, how='left')
df['DXY'] = df['DXY'].ffill()
df['USDVND'] = df['USDVND'].ffill()
df['state'] = df['state'].ffill()
df = df.dropna(subset=['VNI','DXY','USDVND','state'])
df = df[df.index >= '2011-01-01']
print(f"Merged {len(df)} rows, {df.index[0].date()} -> {df.index[-1].date()}")

# ── Features ──
df['dxy_mom20']  = df['DXY'].pct_change(20)
df['dxy_mom60']  = df['DXY'].pct_change(60)
df['vnd_mom20']  = df['USDVND'].pct_change(20)
df['vnd_mom60']  = df['USDVND'].pct_change(60)
# z-scores on 252d expanding
df['dxy_z252']   = (df['DXY'] - df['DXY'].rolling(252).mean()) / df['DXY'].rolling(252).std()
df['vnd_z252']   = (df['USDVND'] - df['USDVND'].rolling(252).mean()) / df['USDVND'].rolling(252).std()
# rank on 252d expanding
df['dxy_rank252'] = df['DXY'].rolling(252).rank(pct=True)
df['vnd_rank252'] = df['USDVND'].rolling(252).rank(pct=True)
# composite pressure (both rising)
df['macro_pressure'] = df['dxy_mom20'] + df['vnd_mom20']

# ── Forward VNI returns ──
for h in [5, 20, 60, 120]:
    df[f'fwd{h}'] = df['VNI'].shift(-h)/df['VNI'] - 1

feats = ['dxy_mom20','dxy_mom60','vnd_mom20','vnd_mom60',
         'dxy_z252','vnd_z252','dxy_rank252','vnd_rank252','macro_pressure']

# ── IC analysis ──
def ic_table(df_in, label):
    print(f"\n{'='*80}\n{label}\n{'='*80}")
    print(f"{'feature':18s} {'IC5':>8s} {'IC20':>8s} {'IC60':>8s} {'IC120':>8s} {'n':>6s}")
    out = []
    for f in feats:
        row = [f]
        for h in [5,20,60,120]:
            r,n = spearman(df_in[f], df_in[f'fwd{h}'])
            row.append(r)
        ic_n = spearman(df_in[f], df_in['fwd20'])[1]
        print(f"{f:18s} "+" ".join(f"{v:+8.3f}" if not np.isnan(v) else f"{'nan':>8s}" for v in row[1:])
              +f" {ic_n:>6d}")
        out.append({'feat':f, 'ic5':row[1],'ic20':row[2],'ic60':row[3],'ic120':row[4]})
    return pd.DataFrame(out)

# Full sample
ic_full = ic_table(df, "FULL SAMPLE 2011-2026 — Raw IC vs VNI fwd returns")

# IS / OOS
df_is  = df[df.index < '2019-01-01']
df_oos = df[df.index >= '2019-01-01']
ic_is  = ic_table(df_is,  "IS 2011-2018 — Raw IC")
ic_oos = ic_table(df_oos, "OOS 2019-2026 — Raw IC")

# ── Combine into single comparison ──
print(f"\n{'='*100}\nWALK-FORWARD CONSISTENCY (sign + magnitude on fwd20)\n{'='*100}")
print(f"{'feature':18s} {'IS IC20':>10s} {'OOS IC20':>10s} {'consistent?':>15s}")
for f in feats:
    ri = ic_is[ic_is['feat']==f]['ic20'].iloc[0]
    ro = ic_oos[ic_oos['feat']==f]['ic20'].iloc[0]
    cons = (not np.isnan(ri) and not np.isnan(ro) and np.sign(ri)==np.sign(ro)
            and abs(ri)>=0.05 and abs(ro)>=0.05)
    print(f"{f:18s} {ri:+10.3f} {ro:+10.3f} {'YES' if cons else 'no':>15s}")

# ── State-conditional: does macro pressure predict best when state allows it? ──
# i.e., macro tightening should hurt MORE in BULL state (state 4-5) than CRISIS
print(f"\n{'='*80}\nSTATE-CONDITIONAL IC: dxy_mom20 vs fwd20 by state\n{'='*80}")
for s in [1,2,3,4,5]:
    sub = df[df['state']==s]
    if len(sub)<30: continue
    r,_ = spearman(sub['dxy_mom20'], sub['fwd20'])
    rv,_ = spearman(sub['vnd_mom20'], sub['fwd20'])
    rc,_ = spearman(sub['macro_pressure'], sub['fwd20'])
    print(f"  state={s} (n={len(sub):4d})  IC(dxy_mom20)={r:+.3f}  "
          f"IC(vnd_mom20)={rv:+.3f}  IC(macro_pressure)={rc:+.3f}")

# ── Extreme bucket analysis: macro_pressure high vs low ──
print(f"\n{'='*80}\nDXY mom20 extreme buckets vs fwd20 (full sample)\n{'='*80}")
df['dxy_bin'] = pd.qcut(df['dxy_mom20'].dropna(), 5, labels=['Q1 low','Q2','Q3 mid','Q4','Q5 high'])
print(df.groupby('dxy_bin', observed=True).agg(
    n=('VNI','count'),
    fwd5_mean=('fwd5','mean'),
    fwd20_mean=('fwd20','mean'),
    fwd60_mean=('fwd60','mean'),
    fwd120_mean=('fwd120','mean'),
).round(4))

print(f"\n{'='*80}\nUSDVND mom20 extreme buckets vs fwd20 (full sample)\n{'='*80}")
df['vnd_bin'] = pd.qcut(df['vnd_mom20'].dropna(), 5, labels=['Q1 low','Q2','Q3 mid','Q4','Q5 high'])
print(df.groupby('vnd_bin', observed=True).agg(
    n=('VNI','count'),
    fwd5_mean=('fwd5','mean'),
    fwd20_mean=('fwd20','mean'),
    fwd60_mean=('fwd60','mean'),
    fwd120_mean=('fwd120','mean'),
).round(4))

# Save merged data for follow-up overlay backtest
df.to_csv('macro_features.csv')
print("\nSaved: macro_features.csv")
