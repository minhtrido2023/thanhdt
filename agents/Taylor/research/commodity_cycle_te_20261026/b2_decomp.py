"""B2b: tách surprise (np_d) thành phần hàng hoá GIẢI THÍCH được (biết trước công bố) vs phần dư; phần nào thị trường phản ứng/ drift?
Đơn vị: ticker-quý; hồi quy chuẩn hoá theo rank trong họ; SE bootstrap theo QUÝ (cụm)."""
import pandas as pd, numpy as np, json
rng=np.random.default_rng(7)
D=pd.read_csv('b2_panel.csv'); D=D[D.tier=='A'].dropna(subset=['c_yoy','np_d','ann']).copy()
D['IS']=D.quarter<'2023Q1'
r=lambda s: s.rank(pct=True)-.5
# phần giải thích: fit np_d ~ c_yoy trong TỪNG họ trên dữ liệu QUÁ KHỨ (expanding, chỉ quý < quý hiện tại) => PIT
D=D.sort_values('qend'); D['np_hat']=np.nan
for fam,g in D.groupby('family'):
    for q in g.quarter.unique():
        past=g[g.quarter<q]
        if past.quarter.nunique()<6: continue
        b=np.polyfit(past.c_yoy,past.np_d,1)
        D.loc[(D.family==fam)&(D.quarter==q),'np_hat']=np.polyval(b,D.loc[(D.family==fam)&(D.quarter==q),'c_yoy'])
D=D.dropna(subset=['np_hat']); D['np_res']=D.np_d-D.np_hat
print('n ticker-quy',len(D),'quy',D.quarter.nunique())
print('IC(np_hat,np_d) PIT expanding:',round(D[['np_hat','np_d']].corr('spearman').iloc[0,1],3))
def reg(df,y,xs,B=3000):
    Z=df.copy()
    for c in xs+[y]: Z[c]=Z.groupby('family')[c].transform(r)
    X=np.c_[np.ones(len(Z)),Z[xs].values]; beta=np.linalg.lstsq(X,Z[y].values,rcond=None)[0]
    qs=Z.quarter.unique(); byq={q:Z[Z.quarter==q] for q in qs}; bs=[]
    for _ in range(B):
        s=pd.concat([byq[q] for q in rng.choice(qs,len(qs))]); Xs=np.c_[np.ones(len(s)),s[xs].values]
        bs.append(np.linalg.lstsq(Xs,s[y].values,rcond=None)[0])
    bs=np.array(bs); se=bs.std(0)
    return {x:dict(b=round(beta[i+1],3),t=round(beta[i+1]/se[i+1],2)) for i,x in enumerate(xs)}|dict(n=len(Z),nq=len(qs))
out={}
for y in ['ann','post60','pre']:
    for lab,sub in [('ALL',D),('IS',D[D.IS]),('OOS',D[~D.IS])]:
        s=sub.dropna(subset=[y]); out[f'{y}|{lab}|np_d']=reg(s,y,['np_d']); out[f'{y}|{lab}|hat+res']=reg(s,y,['np_hat','np_res'])
for k,v in out.items(): print(k,v)
json.dump(out,open('b2_decomp.json','w'),indent=1)
