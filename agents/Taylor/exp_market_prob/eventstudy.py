import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
df=pd.read_csv(EXP+'daily_panel.csv',parse_dates=['time']).reset_index(drop=True)
df=df.dropna(subset=['vni_close']).reset_index(drop=True)
c=df.vni_close.values; n=len(df)
H={'1M':21,'3M':63,'6M':126,'12M':252}
for k,h in H.items():
    f=np.full(n,np.nan)
    f[:n-h]=c[h:]/c[:n-h]-1
    df['fwd_'+k]=f
# path minimum / maximum over next h sessions
for k,h in [('6M',126),('12M',252)]:
    mn=np.full(n,np.nan); mx=np.full(n,np.nan)
    for i in range(n-h):
        w=c[i+1:i+h+1]; mn[i]=w.min()/c[i]-1; mx[i]=w.max()/c[i]-1
    df['minfwd_'+k]=mn; df['maxfwd_'+k]=mx
df.to_csv(EXP+'panel_fwd.csv',index=False)

cur=df.dropna(subset=['pe_con']).iloc[-1]
PE,PB=cur.pe_con,cur.pb_con

def episodes(idx, gap=21):
    if len(idx)==0: return 0
    d=np.diff(idx); return 1+int((d>gap).sum())

def report(name, mask):
    sub=df[mask & df.fwd_12M.notna()]
    idx=np.array(sub.index)
    out={'cond':name,'N_days':int(mask.sum()),'N_days_with12M':len(sub),
         'N_episodes':episodes(np.array(df[mask].index)),
         'years':','.join(sorted(set(df[mask].time.dt.year.astype(str))))}
    for k in H:
        s=df[mask]['fwd_'+k].dropna()
        out['med_'+k]=round(100*s.median(),1) if len(s) else np.nan
        out['neg_'+k]=round(100*(s<0).mean(),0) if len(s) else np.nan
    for k in ['6M','12M']:
        s=df[mask]['minfwd_'+k].dropna()
        out['P_bear20_'+k]=round(100*(s<=-0.20).mean(),0) if len(s) else np.nan
        out['P_dd10_'+k]=round(100*(s<=-0.10).mean(),0) if len(s) else np.nan
        out['medMinDD_'+k]=round(100*s.median(),1) if len(s) else np.nan
    return out

rows=[]
rows.append(report('UNCONDITIONAL 2008+', df.time>='2008-01-01'))
rows.append(report('UNCONDITIONAL 2014+', df.time>='2014-01-01'))
rows.append(report('PE_con +-0.5pt (%.2f-%.2f)'%(PE-0.5,PE+0.5), df.pe_con.between(PE-0.5,PE+0.5)))
rows.append(report('PE_con <= cur (%.2f)'%PE, df.pe_con<=PE))
rows.append(report('PB_con +-5%% (%.2f-%.2f)'%(PB*0.95,PB*1.05), df.pb_con.between(PB*0.95,PB*1.05)))
rows.append(report('PB_con >= cur (%.2f)'%PB, df.pb_con>=PB))
rows.append(report('JOINT PE+-0.75 & PB+-7%', df.pe_con.between(PE-0.75,PE+0.75)&df.pb_con.between(PB*0.93,PB*1.07)))
# point-in-time expanding percentile version (no look-ahead in band definition)
pit=df.pe_con.expanding(500).apply(lambda s: (s.iloc[:-1]<s.iloc[-1]).mean(), raw=False)
df['pe_pit']=pit
curpit=df.pe_pit.dropna().iloc[-1]
rows.append(report('PIT PE pctile in [%.2f,%.2f]'%(max(0,curpit-0.10),min(1,curpit+0.10)),
                   df.pe_pit.between(max(0,curpit-0.10),min(1,curpit+0.10))))
# 2014+ restricted joint (composition-stable era)
rows.append(report('PE_con +-0.5pt, 2014+', df.pe_con.between(PE-0.5,PE+0.5)&(df.time>='2014-01-01')))
res=pd.DataFrame(rows)
pd.set_option('display.width',250)
print('current PE_con=%.2f PB_con=%.3f  PIT-pctile PE=%.1f%%'%(PE,PB,100*curpit))
print(res.to_string(index=False))
res.to_csv(EXP+'baserates.csv',index=False)
