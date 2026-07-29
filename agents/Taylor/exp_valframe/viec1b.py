# -*- coding: utf-8 -*-
"""VIEC 1b — 2 cau hoi song con cho cac chi so MOI:
  (a) CAPE co bi TROI CO HOC theo thoi gian khong (phan vi se vo nghia neu co)?
  (b) Chi so moi co THEM suc du bao forward return so voi PE+PB khong (va co du N doc lap khong)?
"""
import numpy as np, pandas as pd
from scipy import stats
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width',250)
M=pd.read_csv(EXP+'metrics_full.csv',parse_dates=['time'])
M['t']=(M.time-M.time.min()).dt.days/365.25

print('=== (a) TROI CO HOC: hoi quy chi so ~ thoi gian (nam) ===')
for c in ['cape5','cape7','cape10','pe_cap10','pb_cap10','eveb_cap10','erp']:
    d=M[[c,'t']].dropna()
    sl,ic,r,p,se=stats.linregress(d.t,d[c])
    print(f'  {c:11s} N={len(d):5d} doc={sl:+.3f}/nam (R2={r*r:.3f}, p={p:.2g}) '
          f'| dau ky TB={d[c].head(250).mean():.2f} cuoi ky TB={d[c].tail(250).mean():.2f}')

# forward return VNINDEX
M=M.sort_values('time').reset_index(drop=True)
for lbl,h in (('f6M',126),('f12M',252)):
    M[lbl]=100*(M.vni.shift(-h)/M.vni-1)

def r2adj(y,Xs):
    X=np.column_stack([np.ones(len(y))]+Xs); b,*_=np.linalg.lstsq(X,y,rcond=None)
    yh=X@b; r2=1-((y-yh)**2).sum()/((y-y.mean())**2).sum()
    n,k=len(y),X.shape[1]; return r2,1-(1-r2)*(n-1)/(n-k)

print('\n=== (b) SUC DU BAO TANG THEM (R2 hieu chinh, mau CHONG LAP nang) ===')
print('    LUU Y: N ngay KHONG phai N doc lap — 3.700 ngay ~ 15 nam ~ <15 quan sat doc lap.')
for out in ['f6M','f12M']:
    for c in ['cape5','cape7','cape10','eveb_cap10','erp']:
        d=M[[c,'pe_cap10','pb_cap10',out]].dropna()
        if len(d)<400: continue
        y=d[out].values
        _,a=r2adj(y,[np.log(d.pe_cap10),np.log(d.pb_cap10)])
        x=np.log(d[c]) if d[c].min()>0 else d[c]
        _,b=r2adj(y,[np.log(d.pe_cap10),np.log(d.pb_cap10),x])
        _,s=r2adj(y,[x])
        rho,pv=stats.spearmanr(d[c],y)
        print(f'  {out} ~ {c:11s} N={len(d):5d} nam~{len(d)/250:.0f} | PE+PB R2adj={a:+.3f} -> +{c} {b:+.3f} '
              f'(d={b-a:+.3f}) | mot minh {s:+.3f} | rho={rho:+.3f}')

print('\n=== (c) so nam DOC LAP that su co cho moi chi so ===')
for c in ['cape5','cape7','cape10','eveb_cap10','erp','pe_cap10','pb_cap10']:
    d=M[[c,'time']].dropna()
    print(f'  {c:11s}: {d.time.min().date()} -> {d.time.max().date()}  = {(d.time.max()-d.time.min()).days/365.25:.1f} nam')
