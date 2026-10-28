import pandas as pd, numpy as np
f=pd.read_csv('nt2_fin_le2026Q2.csv')
f=f[f.Revenue_P0.fillna(0)>0].copy()
f['qi']=f.quarter.str[:4].astype(int)*4+f.quarter.str[-1].astype(int)
f=f.set_index('qi').sort_index()
full=pd.DataFrame(index=range(f.index.min(),f.index.max()+1)).join(f)
full['quarter']=[f"{i//4 if i%4 else i//4-1}Q{i%4 or 4}" for i in full.index]
r=full.Revenue_P0/1e9; n=full.NP_P0/1e9
full['rev_ttm']=r.rolling(4,min_periods=4).sum(); full['np_ttm']=n.rolling(4,min_periods=4).sum()
full['npm_ttm']=full.np_ttm/full.rev_ttm
# gross: pre-2018 GPM_P0 is quarterly -> GP_q; 2018Q1+ GPM_P0 is TTM
full['gpm_ttm']=np.nan
pre=full.quarter<'2018Q1'
gpq=(full.GPM_P0*r).where(pre)
full.loc[pre,'gpm_ttm']=(gpq.rolling(4,min_periods=4).sum()/full.rev_ttm)[pre]
full.loc[~pre,'gpm_ttm']=full.GPM_P0[~pre]
s=full.dropna(subset=['npm_ttm'])
print(s[['quarter','rev_ttm','np_ttm','npm_ttm','gpm_ttm']].round(3).to_string())
def pct(series,v): x=series.dropna(); return 100*(x<v).mean()+50*(x==v).mean()
last=s.iloc[-1]
print('window',s.quarter.iloc[0],'-',s.quarter.iloc[-1],'N',len(s))
print('NPM last',last.npm_ttm,'pct',pct(s.npm_ttm,last.npm_ttm))
g=s.gpm_ttm.dropna(); print('GPM N',len(g),'last',last.gpm_ttm,'pct',pct(g,last.gpm_ttm))
# annual NP
a=full[full.quarter.str.endswith('Q4')][['quarter','rev_ttm','np_ttm']].dropna()
print(a.round(1).to_string()); print('median annual NP 2013-2025', a.np_ttm.median(), 'n',len(a))
a2=a[a.quarter>='2016Q4']; print('median 2016-2025',a2.np_ttm.median())
s.to_csv('nt2_ttm_series.csv',index=False)
