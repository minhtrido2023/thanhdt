"""PAT: dựng chuỗi theo quý từ tav2_bq.ticker_financial (đã trích sang pat_ticker_financial_raw.csv).
GPM/EBITM trong BQ là TTM (dictionary 2026-11-08) => GP/EBIT quý dựng bằng sai phân TTM + neo từ BCTC gốc."""
import pandas as pd, numpy as np, sys
D='/home/trido/thanhdt/wt-1571194491489091644/agents/Taylor/research/dd_PAT_objective_20261114/factpack/data/'
raw=pd.read_csv(D+'pat_ticker_financial_raw.csv')
def qi(s): return int(s[:4])*4+int(s[5])-1
def qs(i): return f"{i//4}Q{i%4+1}"
raw['idx']=raw['quarter'].map(qi)
R={};NP={};G={};E={};INV={}
for _,r in raw.iterrows():
    for k in range(8):
        for var,store in (('Revenue',R),('NP',NP),('GPM',G),('Inventory',INV)):
            v=r.get(f'{var}_P{k}')
            if pd.notna(v): store[r.idx-k]=v
    for k,store in ((0,E),(4,E)):
        v=r.get(f'EBITM_P{k}')
        if pd.notna(v): store[r.idx-k]=v
Rq=pd.Series(R).sort_index(); NPq=pd.Series(NP).sort_index(); Gq=pd.Series(G).sort_index(); Eq=pd.Series(E).sort_index()
def ttm_rev(i):
    ks=[i-j for j in range(4)]
    return sum(Rq[k] for k in ks) if all(k in Rq.index for k in ks) else np.nan
TR=pd.Series({i:ttm_rev(i) for i in range(Rq.index.min(),Rq.index.max()+1)})
TGP=(Gq*TR).dropna(); TEB=(Eq*TR).dropna()
# --- Q-level df
idxs=range(qi('2021Q1'),qi('2026Q3')+1)
df=pd.DataFrame(index=idxs)
df['quarter']=[qs(i) for i in idxs]
df['rev']=Rq.reindex(idxs)/1e9
df['np']=NPq.reindex(idxs)/1e9
df['ttm_rev']=TR.reindex(idxs)/1e9
df['gpm_ttm']=Gq.reindex(idxs); df['ebitm_ttm']=Eq.reindex(idxs)
df['gp_ttm']=TGP.reindex(idxs)/1e9; df['ebit_ttm']=TEB.reindex(idxs)/1e9
if __name__=='__main__':
    pd.set_option('display.width',250,'display.max_rows',100)
    print(df)
