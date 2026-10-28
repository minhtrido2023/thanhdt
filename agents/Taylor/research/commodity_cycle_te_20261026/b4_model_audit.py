"""B4: V2.4 đối xử mã chu kỳ hàng hoá thế nào. CHỈ ĐỌC ledger pin (không đổi pin): R3-park0-pin0pct-SAN (md5 537e349b, đầu SÀN)
+ data/bq_cache/custom30v_8l.parquet (membership custom30V). Pha chu kỳ = phân vị expanding của TB63 phiên giá TE (PIT: obs <= ngày vào − 2 ngày)."""
import pandas as pd, numpy as np, json
from common import *
rng=np.random.default_rng(4)
L=pd.read_csv(f'{W}/data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz',low_memory=False)
tx=L[L.record_type=='TX'].copy(); tx['ymd']=pd.to_datetime(tx.ymd)
h=tx.groupby('holding_id').agg(ticker=('ticker','first'),book=('book','first'),play=('play_type','first'),entry=('ymd','min'),exit=('ymd','max'),
    buy=('buy_amount','sum'),sell=('sell_amount','sum'),fee=('fee','sum'),nsell=('action',lambda a:(a=='sell').sum())).reset_index()
h=h[h.nsell>0]; h['pnl']=h.sell-h.buy-h.fee; h['ret']=h.pnl/h.buy
m=pd.read_csv('commodity_map_te.csv'); m=m[(m.ticker!='-')]
prod=m[m.sign>0].drop_duplicates('ticker').set_index('ticker')   # producer: họ đầu tiên của mã
cons=set(m[m.sign<0].ticker)-set(prod.index)
h['grp']=np.where(h.ticker.isin(prod.index),'producer',np.where(h.ticker.isin(cons),'consumer','other'))
tot=h.pnl.sum()
share=h.groupby(['book','grp']).agg(n=('pnl','size'),pnl_bn=('pnl',lambda x:x.sum()/1e9),buy_bn=('buy',lambda x:x.sum()/1e9),ret_w=('pnl','sum')).reset_index()
share['ret_w']=share.ret_w/(share.buy_bn*1e9); share['pnl_share']=share.pnl_bn*1e9/tot
print('closed holdings',len(h),'pnl total bn',round(tot/1e9,2)); print(share.round(4).to_string())
print('producer by ticker:'); print(h[h.grp=='producer'].groupby(['book','ticker']).agg(n=('pnl','size'),pnl_bn=('pnl',lambda x:round(x.sum()/1e9,2))).reset_index().sort_values('pnl_bn').to_string())
# pha chu kỳ tại ngày vào
T=te(); A63={k:T[k].dropna().rolling(63).mean().dropna() for k in prod.te_metric_key.unique()}
def pct_at(key,d):
    a=A63[key]; a=a[a.index<=d-pd.Timedelta(days=2)]
    return (a<=a.iloc[-1]).mean() if len(a)>=252*2 else np.nan
hp=h[h.grp=='producer'].copy(); hp['key']=hp.ticker.map(prod.te_metric_key); hp['family']=hp.ticker.map(prod.family)
hp['pct']=[pct_at(k,d) for k,d in zip(hp.key,hp.entry)]
hp=hp.dropna(subset=['pct'])
# lợi suất vượt trội = ret − TB ret các holding 'other' cùng book vào trong ±30 ngày
oth=h[h.grp=='other']
def peer(r):
    o=oth[(oth.book==r.book)&(abs((oth.entry-r.entry).dt.days)<=30)]; return r.ret-o.ret.mean() if len(o)>=5 else np.nan
hp['xret']=hp.apply(peer,axis=1)
hp.to_csv('b4_producer_holdings.csv',index=False)
# phân phối pha lúc vào vs phân phối vô điều kiện của pha (cùng họ, mọi ngày giao dịch 2018+)
base={}
for k,a in A63.items():
    v=[(a[:i+1]<=a.iloc[i]).mean() for i in range(504,len(a),5)]; base[k]=np.array(v)
out={}
for book,g in hp.groupby('book'):
    hi=g[g.pct>=.67]; lo=g[g.pct<=.33]
    bfrac=np.mean(np.concatenate([base[k] for k in g.key]) >=.67) if len(g) else np.nan
    # bootstrap hiệu theo cụm = (họ × năm vào)
    g=g.assign(cl=g.family+'_'+g.entry.dt.year.astype(str))
    def diff(G): return G[G.pct>=.67].xret.mean()-G[G.pct<=.33].xret.mean()
    cls=g.cl.unique(); bs=[]
    for _ in range(3000):
        s=pd.concat([g[g.cl==c] for c in rng.choice(cls,len(cls))]); bs.append(diff(s))
    out[book]=dict(n=len(g),n_cl=len(cls),frac_entry_peak=round((g.pct>=.67).mean(),3),frac_entry_trough=round((g.pct<=.33).mean(),3),
        base_frac_peak_weighted=round(bfrac,3),xret_peak=round(hi.xret.mean(),4),n_peak=len(hi),xret_trough=round(lo.xret.mean(),4),n_trough=len(lo),
        diff=round(diff(g),4),ci90=[round(np.nanpercentile(bs,5),4),round(np.nanpercentile(bs,95),4)],
        pnl_peak_bn=round(hi.pnl.sum()/1e9,2),pnl_trough_bn=round(lo.pnl.sum()/1e9,2))
    print(book,out[book])
# custom30V membership
c=pd.read_parquet(f'{W}/data/bq_cache/custom30v_8l.parquet'); print(c.columns.tolist()[:12])
json.dump(dict(share=share.to_dict('records'),phase=out),open('b4_results.json','w'),indent=1,default=str)
