import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
df=pd.read_csv(EXP+'panel_fwd.csv',parse_dates=['time']).reset_index(drop=True)
c=df.vni_close
df['ma200']=c.rolling(200,min_periods=200).mean()
df['below200']=c<df.ma200
df['hi52']=c.rolling(252,min_periods=100).max(); df['dd52w']=c/df.hi52-1
cur=df.dropna(subset=['pe_con']).iloc[-1]
PE,PB=cur.pe_con,cur.pb_con
print('VNINDEX=%.2f MA200=%.2f  ratio=%.3f  below200=%s  dd52w=%.1f%%'%(cur.vni_close,cur.ma200,cur.vni_close/cur.ma200,cur.below200,100*cur.dd52w))

def ep(mask,gap=21):
    idx=np.array(df[mask].index)
    if len(idx)==0: return idx,np.array([])
    return idx,np.concatenate([[0],np.cumsum(np.diff(idx)>gap)])
def boot(mask,B=4000,seed=11):
    idx,br=ep(mask); s=df.loc[idx,'minfwd_12M']
    ok=s.notna().values; br=br[ok]; v=s[ok].values
    eps=np.unique(br); rng=np.random.default_rng(seed)
    o=[(v[np.isin(br,[])].size)]; o=[]
    for _ in range(B):
        pick=rng.choice(eps,size=len(eps),replace=True)
        vals=np.concatenate([v[br==e] for e in pick]); o.append((vals<=-0.20).mean())
    return np.percentile(o,[5,95]), len(eps)

conds={
 'below MA200 (any val)': df.below200==True,
 'below MA200 & PE band': (df.below200==True)&df.pe_con.between(PE-0.75,PE+0.75),
 'below MA200 & dd52w[-18,-8]': (df.below200==True)&df.dd52w.between(-0.18,-0.08),
 'FULL ANALOG: below200 & PE+-0.75 & dd52w[-20,-6]': (df.below200==True)&df.pe_con.between(PE-0.75,PE+0.75)&df.dd52w.between(-0.20,-0.06),
}
rows=[]
for k,m in conds.items():
    s=df[m]['minfwd_12M'].dropna()
    if len(s)==0: continue
    ci,ne=boot(m)
    # episode-level
    idx,br=ep(m); sv=df.loc[idx,'minfwd_12M']; ok=sv.notna().values
    br2=br[ok]; v2=sv[ok].values
    eplev=[(v2[br2==e]<=-0.20).any() for e in np.unique(br2)]
    rows.append(dict(cond=k,N_days=len(s),N_eps=ne,
      P_bear20=round(100*(s<=-0.20).mean(),0),CI90=f"[{100*ci[0]:.0f},{100*ci[1]:.0f}]",
      P_ep_bear=f"{sum(eplev)}/{len(eplev)}",
      P_corr=round(100*((s<=-0.10)&(s>-0.20)).mean(),0),P_benign=round(100*(s>-0.10).mean(),0),
      med_fwd12M=round(100*df[m].fwd_12M.median(),1),neg12M=round(100*(df[m].fwd_12M<0).mean(),0),
      years=','.join(sorted(set(df[m].time.dt.year.astype(str))))))
r=pd.DataFrame(rows); pd.set_option('display.width',300)
print(r.to_string(index=False)); r.to_csv(EXP+'baserates3.csv',index=False)
