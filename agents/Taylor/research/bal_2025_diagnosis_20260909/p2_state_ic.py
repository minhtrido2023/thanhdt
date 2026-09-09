import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('p2_panel_exp.csv',parse_dates=['time']); d=d[d.adv_vnd>=1e9].copy()
st=pd.read_csv('dt5g_states_exp.csv',parse_dates=['time'])
d=d.merge(st,on='time',how='left'); d['state']=d.state.ffill()
FEAT=['prox52','idiovol_ann','ey','pe_z','mom12_1','trend_atr','eff_ratio60','bb_pctb_centered','rsi','fip','cmf','volratio','residmom_scaled','mom3m','macddiff','px_ma50']
def nw_t(x,l=1):
    x=np.asarray(x,float);n=len(x)
    if n<4: return np.nan
    e=x-x.mean();s=(e*e).sum()/n
    for L in range(1,l+1): s+=2*(1-L/(l+1))*((e[L:]*e[:-L]).sum()/n)
    return x.mean()/np.sqrt(s/n) if s>0 else np.nan
rows=[]
for lab,mask in {'BULL/EXBULL (state 4-5)': d.state.isin([4,5]), 'NEUTRAL (state 3)': d.state==3}.items():
    s=d[mask]
    for f in FEAT:
        ics={}
        for t,g in s.groupby('time'):
            g=g[[f,'profit_1M']].dropna()
            if len(g)>=20: ics[t]=stats.spearmanr(g[f],g['profit_1M']).statistic
        ics=pd.Series(ics)
        if len(ics)<8: continue
        rows.append(dict(feature=f,regime=lab,n_months=len(ics),ic=ics.mean(),t=nw_t(ics.values),hit=(ics>0).mean()))
R=pd.DataFrame(rows)
pd.set_option('display.width',200)
for lab in R.regime.unique():
    print('===',lab,'===')
    print(R[R.regime==lab].sort_values('ic').round(4).to_string(index=False)); print()
R.to_csv('p2_ic_by_regime.csv',index=False)
