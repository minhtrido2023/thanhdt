#!/usr/bin/env python3
"""
macro_corr_study.py  (RESEARCH / DISPLAY-ONLY — job Taylor_20260706_094519)

Relationship between VNINDEX (level, returns, volatility, drawdown) and:
  - Gold (COMEX world gold, USD/oz)      -> vnstock MSN symbol_id 'auvwoc', 2016-07+
  - USD/VND                              -> data/macro_features.csv (2011+)
  - DXY (US dollar index, USD strength)  -> data/macro_features.csv (2011+)
  - SBV refi rate (policy rate)          -> sbv_refi_events.json (step fn, 2006+)
  - Foreign net flow                     -> BLOCKED (see report), not produced here.

Outputs: correlation tables (stdout + CSV), rolling corr, cross-corr lags,
sub-period stability, 2 PNG charts.  Nothing here touches production.
"""
import json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = '/home/trido/thanhdt/WorkingClaude'
OUT  = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor'

# ---------- load ----------
mf = pd.read_csv(f'{ROOT}/data/macro_features.csv', parse_dates=['time'])
mf = mf[['time','VNI','DXY','USDVND']].sort_values('time')

gold = pd.read_csv('/tmp/gold_world.csv', parse_dates=['time']).rename(columns={'close':'GOLD'})
gold = gold[['time','GOLD']].sort_values('time')

# SBV refi step function -> daily forward fill
ev = json.load(open(f'{ROOT}/sbv_refi_events.json'))['events']
ref = pd.DataFrame(ev, columns=['time','REFI']); ref['time']=pd.to_datetime(ref['time'])

df = mf.merge(gold, on='time', how='left')
df = df.merge(ref, on='time', how='left')
df['REFI'] = df['REFI'].ffill()          # policy rate persists until next change
df = df.sort_values('time').reset_index(drop=True)

# ---------- derived ----------
df['VNI_ret']    = df['VNI'].pct_change()
df['GOLD_ret']   = df['GOLD'].pct_change()
df['USDVND_ret'] = df['USDVND'].pct_change()
df['DXY_ret']    = df['DXY'].pct_change()
df['REFI_chg']   = df['REFI'].diff()      # nonzero only on change days

# VNINDEX volatility (annualized rolling std of daily returns) + drawdown
df['VNI_vol20'] = df['VNI_ret'].rolling(20).std()*np.sqrt(252)
df['VNI_vol60'] = df['VNI_ret'].rolling(60).std()*np.sqrt(252)
df['GOLD_vol20']= df['GOLD_ret'].rolling(20).std()*np.sqrt(252)
roll_max = df['VNI'].cummax()
df['VNI_dd'] = df['VNI']/roll_max - 1.0

# analysis frame: from first day gold exists
g0 = df['GOLD'].first_valid_index()
A = df.iloc[g0:].reset_index(drop=True)
print(f"[range] full macro {df.time.min().date()}..{df.time.max().date()} | "
      f"gold-overlap analysis {A.time.min().date()}..{A.time.max().date()} ({len(A)} rows)")

# ---------- 1. full-period Pearson ----------
def r(a,b,d=A):
    s=d[[a,b]].dropna();
    if len(s)<30: return np.nan,len(s)
    return s[a].corr(s[b]), len(s)

print("\n=== 1. FULL-PERIOD PEARSON (gold-overlap window) ===")
pairs = [
 ('VNI_ret','GOLD_ret','VNINDEX daily ret vs Gold daily ret'),
 ('VNI_ret','USDVND_ret','VNINDEX ret vs USD/VND ret'),
 ('VNI_ret','DXY_ret','VNINDEX ret vs DXY ret (USD strength)'),
 ('VNI_vol20','GOLD_vol20','VNINDEX vol20 vs Gold vol20'),
 ('VNI_vol20','GOLD','VNINDEX vol20 vs Gold price level'),
 ('VNI_vol20','USDVND','VNINDEX vol20 vs USD/VND level'),
 ('VNI_vol20','REFI','VNINDEX vol20 vs SBV refi level'),
 ('VNI','GOLD','VNINDEX level vs Gold level'),
 ('VNI','USDVND','VNINDEX level vs USD/VND level'),
 ('VNI','REFI','VNINDEX level vs SBV refi level'),
 ('VNI_dd','GOLD_ret','VNINDEX drawdown vs Gold ret'),
]
rows=[]
for a,b,lab in pairs:
    rv,n=r(a,b); rows.append((lab,rv,n)); print(f"  {rv:+.3f}  (n={n:5d})  {lab}")

# ---------- 2. rolling 120d corr (stability) ----------
def rollcorr(a,b,w=120): return A[a].rolling(w).corr(A[b])
roll = pd.DataFrame({'time':A['time'],
    'VNI~GOLD':rollcorr('VNI_ret','GOLD_ret'),
    'VNI~USDVND':rollcorr('VNI_ret','USDVND_ret'),
    'VNI~DXY':rollcorr('VNI_ret','DXY_ret')})
print("\n=== 2. ROLLING 120d CORR (VNI ret vs X) — mean / std / %|r|>0.3 ===")
for c in ['VNI~GOLD','VNI~USDVND','VNI~DXY']:
    s=roll[c].dropna()
    print(f"  {c:12s} mean={s.mean():+.3f} std={s.std():.3f} "
          f"min={s.min():+.3f} max={s.max():+.3f} frac|r|>0.3={np.mean(np.abs(s)>0.3):.2f}")

# ---------- 3. cross-correlation lag -10..+10 (does X lead VNI?) ----------
print("\n=== 3. CROSS-CORR lag k: corr(VNI_ret_t, X_ret_{t-k}); k>0 => X LEADS VNI ===")
def xcorr(xcol):
    out={}
    base=A[['VNI_ret',xcol]].dropna()
    for k in range(-10,11):
        out[k]=base['VNI_ret'].corr(base[xcol].shift(k))
    return out
for xcol in ['GOLD_ret','USDVND_ret','DXY_ret']:
    xc=xcorr(xcol); best=max(xc,key=lambda k:abs(xc[k]))
    print(f"  {xcol:11s} k=0:{xc[0]:+.3f}  best|r| at k={best:+d}:{xc[best]:+.3f}  "
          f"(k=-5:{xc[-5]:+.3f} k=+5:{xc[5]:+.3f})")

# ---------- 4. sub-period stability ----------
print("\n=== 4. SUB-PERIOD stability (|r|>0.3 in >=2/3 periods = 'visible & stable') ===")
subs=[('2016-2018','2016-01-01','2018-12-31'),
      ('2019-2021','2019-01-01','2021-12-31'),
      ('2022-2026','2022-01-01','2026-12-31')]
sp_pairs=[('VNI_ret','GOLD_ret'),('VNI_ret','USDVND_ret'),('VNI_ret','DXY_ret'),
          ('VNI_vol20','GOLD_vol20'),('VNI_vol20','REFI'),('VNI','REFI')]
for a,b in sp_pairs:
    vals=[]
    for nm,s,e in subs:
        d=A[(A.time>=s)&(A.time<=e)]; rv,_=r(a,b,d); vals.append(rv)
    nstab=sum(abs(v)>0.3 for v in vals if not np.isnan(v))
    flag='STABLE' if nstab>=2 else 'weak/episodic'
    print(f"  {a:9s}~{b:11s}  "+"  ".join(f"{nm}:{v:+.3f}" for (nm,_,_),v in zip(subs,vals))
          +f"   [{nstab}/3 |r|>0.3 -> {flag}]")

# ---------- save tables ----------
pd.DataFrame(rows,columns=['pair','pearson_r','n']).to_csv(f'{OUT}/macro_corr_fullperiod.csv',index=False)
roll.to_csv(f'{OUT}/macro_corr_rolling120.csv',index=False)

# ---------- 5. plots ----------
# overlay normalized
fig,ax=plt.subplots(figsize=(13,6))
norm=lambda s:(s/s.dropna().iloc[0])
for c,lab in [('VNI','VNINDEX'),('GOLD','Gold(USD/oz)'),('USDVND','USD/VND'),('DXY','DXY')]:
    ax.plot(A['time'],norm(A[c]),label=lab,lw=1.2)
ax2=ax.twinx(); ax2.plot(A['time'],A['REFI'],color='grey',ls='--',lw=1,label='SBV refi %')
ax2.set_ylabel('SBV refi rate (%)',color='grey')
ax.set_title('VNINDEX vs Gold / USD-VND / DXY (normalized=1 at start) + SBV refi rate')
ax.legend(loc='upper left'); ax.set_ylabel('normalized level'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(f'{OUT}/macro_overlay.png',dpi=110); plt.close()

# heatmap of return-corr matrix
cols=['VNI_ret','GOLD_ret','USDVND_ret','DXY_ret','REFI_chg']
cm=A[cols].corr()
fig,ax=plt.subplots(figsize=(6.5,5.5))
im=ax.imshow(cm,cmap='RdBu_r',vmin=-1,vmax=1)
ax.set_xticks(range(len(cols))); ax.set_yticks(range(len(cols)))
ax.set_xticklabels(cols,rotation=45,ha='right'); ax.set_yticklabels(cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j,i,f'{cm.iloc[i,j]:.2f}',ha='center',va='center',
                color='white' if abs(cm.iloc[i,j])>0.5 else 'black',fontsize=9)
plt.colorbar(im,fraction=0.046); ax.set_title('Daily-return correlation matrix (gold-overlap window)')
plt.tight_layout(); plt.savefig(f'{OUT}/macro_corr_heatmap.png',dpi=110); plt.close()
print(f"\n[saved] {OUT}/macro_overlay.png, macro_corr_heatmap.png, macro_corr_fullperiod.csv, macro_corr_rolling120.csv")

# rolling-corr time chart too (stability visual)
fig,ax=plt.subplots(figsize=(13,4.5))
for c in ['VNI~GOLD','VNI~USDVND','VNI~DXY']:
    ax.plot(roll['time'],roll[c],label=c,lw=1.1)
ax.axhline(0.3,color='g',ls=':',lw=.8); ax.axhline(-0.3,color='r',ls=':',lw=.8); ax.axhline(0,color='k',lw=.5)
ax.set_title('Rolling 120d correlation: VNINDEX daily return vs Gold / USD-VND / DXY')
ax.legend(); ax.grid(alpha=.3); ax.set_ylim(-1,1)
plt.tight_layout(); plt.savefig(f'{OUT}/macro_rolling_corr.png',dpi=110); plt.close()
print(f"[saved] {OUT}/macro_rolling_corr.png")
