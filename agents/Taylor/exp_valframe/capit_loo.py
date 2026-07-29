# -*- coding: utf-8 -*-
"""VIEC 2c — do BEN cua quan he PB-re -> ket qua tot: bo tung su kien / tung nam."""
import numpy as np, pandas as pd
from scipy import stats
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
E=pd.read_csv(EXP+'capit_events_gate0.3.csv',parse_dates=['event'])
pd.set_option('display.width',250)

for tag,sub in [('TOAN BO 2009+',E),('PRODUCTION 2014+',E[E.event>='2014-01-01'])]:
    for o in ['r6M','r12M','mdd12M']:
        d=sub[['event','pb_cap10_pctE',o]].dropna().reset_index(drop=True)
        if len(d)<10: continue
        r0,p0=stats.spearmanr(d.pb_cap10_pctE,d[o])
        loo=[stats.spearmanr(d.drop(i).pb_cap10_pctE,d.drop(i)[o])[0] for i in range(len(d))]
        yrs=sorted(d.event.dt.year.unique())
        lyo=[]
        for y in yrs:
            dd=d[d.event.dt.year!=y]
            if len(dd)>=8: lyo.append((y,stats.spearmanr(dd.pb_cap10_pctE,dd[o])[0]))
        worst=max(lyo,key=lambda x:x[1]) if lyo else (None,np.nan)
        print(f'{tag:18s} {o:7s} N={len(d):2d} rho={r0:+.3f}(p={p0:.3f}) | LOO-su-kien min..max={min(loo):+.3f}..{max(loo):+.3f} | '
              f'bo-1-nam xau nhat: {worst[0]} -> rho={worst[1]:+.3f}')
    print()

# su kien nao "keo" quan he? xep hang residual
d=E[['event','pb_cap10_pctE','r6M']].dropna()
d['rank_val']=stats.rankdata(d.pb_cap10_pctE); d['rank_out']=stats.rankdata(d.r6M)
d['discord']=d.rank_val+d.rank_out  # cao/thap = nhat quan voi gia thuyet "re->tot"
print('=== 5 su kien NHAT QUAN nhat & 5 NGUOC nhat voi gia thuyet (re -> forward tot) ===')
d=d.sort_values('discord')
print(d.head(5)[['event','pb_cap10_pctE','r6M']].round(1).to_string(index=False))
print('...nguoc:')
print(d.tail(5)[['event','pb_cap10_pctE','r6M']].round(1).to_string(index=False))
