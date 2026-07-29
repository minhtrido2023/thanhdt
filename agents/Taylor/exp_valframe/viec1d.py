# -*- coding: utf-8 -*-
"""VIEC 1d — da cong tuyen SAU KHI KHU XU HUONG + composite z-score (chi neu >=2 song sot)."""
import numpy as np, pandas as pd
from scipy import stats
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width',250)
M=pd.read_csv(EXP+'metrics_full.csv',parse_dates=['time']).sort_values('time').reset_index(drop=True)
M['t']=(M.time-M.time.min()).dt.days/365.25
for lbl,h in (('f6M',126),('f12M',252)): M[lbl]=100*(M.vni.shift(-h)/M.vni-1)
def dt_(d,c):
    sl,ic,*_=stats.linregress(d.t,d[c]); return d[c].values-(ic+sl*d.t.values)
def r2(y,Xs):
    X=np.column_stack([np.ones(len(y))]+Xs); b,*_=np.linalg.lstsq(X,y,rcond=None)
    return 1-((y-X@b)**2).sum()/((y-y.mean())**2).sum()

print('=== DA CONG TUYEN SAU KHU XU HUONG: chi so moi ~ PE + PB (deu da khu xu huong) ===')
for c in ['cape5','cape7','cape10','eveb_cap10','erp']:
    d=M[[c,'t','pe_cap10','pb_cap10']].dropna().copy()
    y=dt_(d,c); xpe=dt_(d,'pe_cap10'); xpb=dt_(d,'pb_cap10')
    R=r2(y,[xpe,xpb])
    print(f'  {c:11s} N={len(d):5d}  R2|PE={r2(y,[xpe]):.3f}  R2|PB={r2(y,[xpb]):.3f}  R2|PE+PB={R:.3f}'
          f'  -> con MOI {1-R:.0%}')

print('\n=== COMPOSITE Z-SCORE (z tren chuoi DA KHU XU HUONG, cua so day du) ===')
comp=['pe_cap10','pb_cap10','cape7','erp']       # erp dao dau (cao=re)
d=M[['time','t','f6M','f12M']+comp].dropna().copy()
Z=pd.DataFrame({'time':d.time.values})
for c in comp:
    x=dt_(d,c); z=(x-x.mean())/x.std()
    Z[c]= -z if c=='erp' else z                  # dau duong = DAT
Z['comp']=Z[comp].mean(axis=1)
d=d.reset_index(drop=True); d['comp']=Z.comp.values
print(f'  N={len(d)} ({d.time.min().date()} -> {d.time.max().date()}, {(d.time.max()-d.time.min()).days/365.25:.1f} nam)')
print('  tuong quan giua cac thanh phan (da khu xu huong):')
print(Z[comp].corr().round(2).to_string())
cur=d.iloc[-1]
print(f"\n  composite HIEN TAI={cur.comp:+.2f} z  -> phan vi {100*(d.comp<cur.comp).mean():.1f}")
for o in ['f6M','f12M']:
    dd=d[['comp',o]].dropna()
    rho,p=stats.spearmanr(dd.comp,dd[o])
    print(f'  composite ~ {o}: rho={rho:+.3f} (N ngay={len(dd)}, ~{len(dd)/250:.0f} nam) | '
          f'so sanh PB rieng: rho={stats.spearmanr(d.pb_cap10,d[o])[0]:+.3f}')
d[['time','comp','pe_cap10','pb_cap10','cape7','erp','f6M','f12M']].to_csv(EXP+'composite.csv',index=False)
