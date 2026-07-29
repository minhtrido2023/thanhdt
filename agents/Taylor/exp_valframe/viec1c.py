# -*- coding: utf-8 -*-
"""VIEC 1c — sau khi KHU XU HUONG, cac chi so moi con lai gi?
Neu suc du bao bien mat khi khu xu the tuyen tinh => do la hoi quy gia (spurious trend),
khong phai tin hieu dinh gia."""
import numpy as np, pandas as pd
from scipy import stats
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width',250)
M=pd.read_csv(EXP+'metrics_full.csv',parse_dates=['time']).sort_values('time').reset_index(drop=True)
M['t']=(M.time-M.time.min()).dt.days/365.25
for lbl,h in (('f6M',126),('f12M',252)): M[lbl]=100*(M.vni.shift(-h)/M.vni-1)

def detrend(d,c):
    sl,ic,*_=stats.linregress(d.t,d[c]); return d[c]-(ic+sl*d.t)

def r2adj(y,Xs):
    X=np.column_stack([np.ones(len(y))]+Xs); b,*_=np.linalg.lstsq(X,y,rcond=None)
    yh=X@b; r2=1-((y-yh)**2).sum()/((y-y.mean())**2).sum(); n,k=len(y),X.shape[1]
    return 1-(1-r2)*(n-1)/(n-k)

print('=== SO SANH: THO vs KHU XU HUONG (ca bien du bao LAN forward return) ===')
for out in ['f6M','f12M']:
    for c in ['cape5','cape7','cape10','eveb_cap10','erp','pe_cap10','pb_cap10']:
        d=M[list(dict.fromkeys([c,'t','pe_cap10','pb_cap10',out]))].dropna().copy()
        if len(d)<400: continue
        d['xd']=detrend(d,c); d['yd']=detrend(d,out)
        rho_raw=stats.spearmanr(d[c],d[out])[0]; rho_dt=stats.spearmanr(d.xd,d.yd)[0]
        a=r2adj(d[out].values,[d[c].values]); b=r2adj(d.yd.values,[d.xd.values])
        print(f'  {out} ~ {c:11s} N={len(d):5d} | rho THO={rho_raw:+.3f} R2adj={a:+.3f}'
              f'  ->  KHU XU HUONG rho={rho_dt:+.3f} R2adj={b:+.3f}')
    print()

print('=== PHAN VI CAPE sau khi khu xu huong (so voi phan vi tho) ===')
for c in ['cape5','cape7','cape10','eveb_cap10','erp']:
    d=M[[c,'t','time']].dropna().copy(); d['xd']=detrend(d,c)
    cur_raw=d[c].iloc[-1]; cur_dt=d.xd.iloc[-1]
    print(f'  {c:11s} phan vi THO={100*(d[c]<cur_raw).mean():5.1f}  ->  KHU XU HUONG={100*(d.xd<cur_dt).mean():5.1f}'
          f'   (gia tri {cur_raw:.2f}, lech xu the {cur_dt:+.2f})')
