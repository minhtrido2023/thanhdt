import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
df=pd.read_csv(EXP+'panel_fwd.csv',parse_dates=['time']).reset_index(drop=True)
c=df.vni_close
df['hi52']=c.rolling(252,min_periods=100).max()
df['dd52w']=c/df.hi52-1
cur=df.dropna(subset=['pe_con']).iloc[-1]
PE,PB,DD=cur.pe_con,cur.pb_con,cur.dd52w
print('CHECK current dd52w = %.1f%% (golive_v23_status says -12.8%%)'%(100*DD))

def buckets(mask, h='12M'):
    s=df[mask]['minfwd_'+h].dropna()
    if len(s)==0: return None
    bear=(s<=-0.20).mean(); corr=((s<=-0.10)&(s>-0.20)).mean(); benign=(s>-0.10).mean()
    return bear,corr,benign,len(s)

def ep_ids(mask,gap=21):
    idx=np.array(df[mask].index); 
    if len(idx)==0: return np.array([])
    br=np.concatenate([[0],np.cumsum(np.diff(idx)>gap)])
    return idx,br

def boot(mask,h='12M',B=4000,seed=7):
    idx,br=ep_ids(mask)
    sub=df.loc[idx,'minfwd_'+h]
    ok=sub.notna().values; idx=idx[ok]; br=br[ok]; sub=sub[ok].values
    eps=np.unique(br); rng=np.random.default_rng(seed); out=[]
    for _ in range(B):
        pick=rng.choice(eps,size=len(eps),replace=True)
        vals=np.concatenate([sub[br==e] for e in pick])
        out.append((vals<=-0.20).mean())
    return np.percentile(out,[5,50,95]), len(eps)

conds={
 'UNCOND 2008+': df.time>='2008-01-01',
 'UNCOND 2014+': df.time>='2014-01-01',
 'PE band (11.9-12.9)': df.pe_con.between(PE-0.5,PE+0.5),
 'PB band (1.71-1.89)': df.pb_con.between(PB*0.95,PB*1.05),
 'JOINT PE&PB band': df.pe_con.between(PE-0.75,PE+0.75)&df.pb_con.between(PB*0.93,PB*1.07),
 'dd52w in [-18%,-8%]': df.dd52w.between(-0.18,-0.08),
 'JOINT PE band & dd52w[-18,-8]': df.pe_con.between(PE-0.75,PE+0.75)&df.dd52w.between(-0.18,-0.08),
}
rows=[]
for k,m in conds.items():
    b=buckets(m)
    if b is None: continue
    ci,neps=boot(m)
    rows.append(dict(cond=k,N_days=b[3],N_eps=neps,
        P_bear20_12M=round(100*b[0],0), P_corr10_20=round(100*b[1],0), P_benign=round(100*b[2],0),
        CI90_bear=f"[{100*ci[0]:.0f}%, {100*ci[2]:.0f}%]",
        med_fwd12M=round(100*df[m].fwd_12M.median(),1),
        neg_fwd12M=round(100*(df[m].fwd_12M<0).mean(),0)))
r=pd.DataFrame(rows); pd.set_option('display.width',250)
print(r.to_string(index=False)); r.to_csv(EXP+'baserates2.csv',index=False)

# list episodes for the joint condition to show WHICH periods
m=conds['JOINT PE&PB band']
sub=df[m]
grp=(sub.index.to_series().diff()>21).cumsum()
print('\nEpisodes (JOINT PE&PB band) — start, end, n_days, min-fwd-12M at start:')
for g,gd in sub.groupby(grp.values):
    i0=gd.index[0]
    print('  %s -> %s  n=%3d  minfwd12M@start=%s  fwd12M@start=%s'%(gd.time.iloc[0].date(),gd.time.iloc[-1].date(),len(gd),
        ('%.1f%%'%(100*df.minfwd_12M.iloc[i0])) if pd.notna(df.minfwd_12M.iloc[i0]) else 'NA',
        ('%.1f%%'%(100*df.fwd_12M.iloc[i0])) if pd.notna(df.fwd_12M.iloc[i0]) else 'NA'))
