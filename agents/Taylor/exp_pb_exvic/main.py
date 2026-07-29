"""PB thi truong: do lai bang nhieu phuong phap, kiem tra meo mo do 1 ma sieu lon (VIC)."""
import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width',260)

p=pd.read_csv(EXP+'t100_panel2.csv',parse_dates=['time'])
p['pb_i']=p.mcap/p.book                      # PB thuc te tu BVPS (nhat quan voi tu/mau so)
p=p[np.isfinite(p.pb_i) & (p.pb_i>0)].copy()
p['w']=p.mcap/p.groupby('time').mcap.transform('sum')

def cap_weights(w, cap=0.10):
    w=w.astype(float).copy(); n=len(w)
    if n*cap<1: return w/w.sum()
    for _ in range(50):
        w=w/w.sum()
        over=w>cap+1e-12
        if not over.any(): break
        excess=(w[over]-cap).sum(); w[over]=cap
        free=~over
        if w[free].sum()<=0: break
        w[free]=w[free]+excess*w[free]/w[free].sum()
    return w/w.sum()

def harm(w,pb): return w.sum()/ (w/pb).sum()

rows=[]
for t,d in p.groupby('time'):
    pb=d.pb_i.values; w=d.w.values; mc=d.mcap.values; bk=d.book.values; tk=d.ticker.values
    i1=np.argmax(w)
    ex=tk!='VIC'
    # trimmed: bo 5% ten co PB cao nhat va 5% thap nhat
    o=np.argsort(pb); k=max(1,int(round(0.05*len(pb)))); keep=o[k:len(pb)-k]
    rows.append(dict(time=t,n=len(d),
        pb_cw=mc.sum()/bk.sum(),
        pb_cw_exvic=(mc[ex].sum()/bk[ex].sum()) if ex.sum()>0 else np.nan,
        pb_cw_extop1=(np.delete(mc,i1).sum()/np.delete(bk,i1).sum()),
        pb_cap10=harm(cap_weights(pd.Series(w)).values,pb),
        pb_ewmed=np.median(pb),
        pb_ewmean=pb.mean(),
        pb_trim=mc[keep].sum()/bk[keep].sum(),
        top1_tk=tk[i1], top1_w=w[i1], top1_pb=pb[i1],
        vic_w=w[tk=='VIC'][0] if (tk=='VIC').any() else 0.0,
        vic_pb=pb[tk=='VIC'][0] if (tk=='VIC').any() else np.nan,
        top1_rank_pb=float((pb>pb[i1]).sum()+1)))
S=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)

a=pd.read_csv(EXP+'agg_all2.csv',parse_dates=['time'])
a['pb_all']=a.mcap_all/a.book_all; a['pb_all_exvic']=a.mcap_ex/a.book_ex
S=S.merge(a[['time','pb_all','pb_all_exvic','n_pb']],on='time',how='left')
S.to_csv(EXP+'pb_variants.csv',index=False)

cur=S.iloc[-1]
print('=== HIEN TAI %s (n_top100=%d, n_all=%d) ==='%(cur.time.date(),cur.n,cur.n_pb))
for c in ['pb_all','pb_all_exvic','pb_cw','pb_cw_exvic','pb_cw_extop1','pb_cap10','pb_trim','pb_ewmed','pb_ewmean']:
    print('  %-14s = %.4f'%(c,cur[c]))
print('  VIC: w=%.2f%% PB=%.2f | top1=%s w=%.2f%% PB=%.2f (hang PB thu %d/100)'%(
    100*cur.vic_w,cur.vic_pb,cur.top1_tk,100*cur.top1_w,cur.top1_pb,int(cur.top1_rank_pb)))

end=cur.time
wins={'full_2008+':S.time>='2008-01-01','last_10Y':S.time>=end-pd.DateOffset(years=10),
      'last_5Y':S.time>=end-pd.DateOffset(years=5),'last_3Y':S.time>=end-pd.DateOffset(years=3)}
cols=['pb_all','pb_all_exvic','pb_cw','pb_cw_exvic','pb_cw_extop1','pb_cap10','pb_trim','pb_ewmed','pb_ewmean']
out=[]
for wn,m in wins.items():
    sub=S[m]
    for c in cols:
        s=sub[c].dropna(); q=s.quantile([.05,.25,.5,.75,.95])
        out.append(dict(window=wn,metric=c,cur=round(cur[c],4),pctile=round(100*(s<cur[c]).mean(),1),N=len(s),
            p05=round(q.iloc[0],3),p25=round(q.iloc[1],3),p50=round(q.iloc[2],3),p75=round(q.iloc[3],3),p95=round(q.iloc[4],3)))
R=pd.DataFrame(out); R.to_csv(EXP+'percentiles_pb.csv',index=False)
print('\n=== PHAN VI PB (100 = dat nhat) ===')
for wn in wins: print(R[R.window==wn].to_string(index=False)); print()
