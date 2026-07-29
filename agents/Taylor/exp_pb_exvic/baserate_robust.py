"""Base rate co dieu kien theo PB do bang phuong phap BEN (khong bi 1 ma sieu lon lam meo)."""
import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width',220)
f=pd.read_csv(OLD+'panel_fwd.csv',parse_dates=['time'])
S=pd.read_csv(EXP+'pb_variants_final.csv',parse_dates=['time'])
df=f.merge(S[['time','pb_cw','pb_cw_exvic','pb_cw_extop1','pb_cap10','pb_ewmed','top1_w']],on='time',how='left').reset_index(drop=True)
cur=df.dropna(subset=['pb_cw']).iloc[-1]

def boot(mask,B=4000,seed=7,h='12M'):
    idx=np.array(df[mask].index)
    if len(idx)==0: return (np.nan,)*3,0,0
    br=np.concatenate([[0],np.cumsum(np.diff(idx)>21)])
    sub=df.loc[idx,'minfwd_'+h]; ok=sub.notna().values
    idx,br,sub=idx[ok],br[ok],sub[ok].values
    if len(sub)==0: return (np.nan,)*3,0,0
    eps=np.unique(br); rng=np.random.default_rng(seed); out=[]
    for _ in range(B):
        pick=rng.choice(eps,size=len(eps),replace=True)
        out.append((np.concatenate([sub[br==e] for e in pick])<=-0.20).mean())
    return np.percentile(out,[5,50,95]),len(eps),len(sub)

rows=[]
conds={'VO DIEU KIEN 2008+':df.time>='2008-01-01'}
for c in ['pb_cw','pb_cw_extop1','pb_cap10','pb_ewmed']:
    v=cur[c]; conds['%s +-5%% (%.3f)'%(c,v)]=df[c].between(v*0.95,v*1.05)
for k,m in conds.items():
    s=df[m].minfwd_12M.dropna()
    ci,ne,n=boot(m)
    r=df[m].fwd_12M.dropna()
    rows.append(dict(dieu_kien=k,n_ngay=int(m.sum()),n_ep=ne,
       P_bear=round(100*(s<=-0.20).mean(),1) if len(s) else np.nan,
       CI90='[%.0f, %.0f]'%(ci[0]*100,ci[2]*100) if np.isfinite(ci[0]) else '-',
       P_khong_roi_10=round(100*(s>-0.10).mean(),1) if len(s) else np.nan,
       fwd12M_trungvi=round(100*r.median(),1) if len(r) else np.nan))
print('=== P(bear 12M) theo tung cach do PB, dai +-5%% quanh gia tri hien tai ==='); print(pd.DataFrame(rows).to_string(index=False))

# --- do lech giua cap-weighted va median: hom nay bat thuong den dau? ---
def pit(s,minp=500): return s.expanding(minp).apply(lambda x:(x.iloc[:-1]<x.iloc[-1]).mean())
d2=df.dropna(subset=['pb_cw','pb_ewmed']).copy()
d2['p_cw']=pit(d2.pb_cw); d2['p_med']=pit(d2.pb_ewmed); d2['gap']=d2.p_cw-d2.p_med
g=d2.dropna(subset=['gap'])
print('\n=== Chenh lech phan vi PIT: cap-weighted TRU equal-weight-median ===')
print('hien tai gap = %+.3f (p_cw=%.3f, p_med=%.3f) | phan vi cua gap trong lich su = %.1f | max lich su %+.3f (%s)'%(
  g.gap.iloc[-1],g.p_cw.iloc[-1],g.p_med.iloc[-1],100*(g.gap<g.gap.iloc[-1]).mean(),g.gap.max(),g.loc[g.gap.idxmax(),'time'].date()))
print('so phien gap>0.5: %d/%d (%.1f%%) — cac nam: %s'%((g.gap>0.5).sum(),len(g),100*(g.gap>0.5).mean(),
  sorted(g[g.gap>0.5].time.dt.year.unique().tolist())))
