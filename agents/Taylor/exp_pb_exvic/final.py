"""BAN CUOI: PB (va PE/ROE) thi truong theo nhieu phuong phap, loai ngay du lieu hong."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
pd.set_option('display.width',260)

p=pd.read_csv(EXP+'t100_panel2.csv',parse_dates=['time'])
p['pb_i']=p.mcap/p.book
p=p[np.isfinite(p.pb_i)&(p.pb_i>0)].copy()
nday=p.groupby('time').size()
good=nday[nday>=50].index                      # chi loai 2 ngay hong 2025-05-04/05-11 (n=1); cac ngay 95-99 ten van hop le
p=p[p.time.isin(good)].copy()
p['w']=p.mcap/p.groupby('time').mcap.transform('sum')

def cap_weights(w,cap=0.10):
    w=np.asarray(w,float).copy()
    for _ in range(60):
        w=w/w.sum(); over=w>cap+1e-12
        if not over.any(): break
        ex=(w[over]-cap).sum(); w[over]=cap; fr=~over
        if w[fr].sum()<=0: break
        w[fr]+=ex*w[fr]/w[fr].sum()
    return w/w.sum()
def harm(w,x): return w.sum()/(w/x).sum()

rows=[]
for t,d in p.groupby('time'):
    pb=d.pb_i.values; w=d.w.values; mc=d.mcap.values; bk=d.book.values
    er=d.earn.values; tk=d.ticker.values
    i1=int(np.argmax(w)); ex=tk!='VIC'
    o=np.argsort(pb); k=max(1,int(round(0.05*len(pb)))); keep=o[k:len(pb)-k]
    ok=np.isfinite(er)&(er>0)                       # ro PE: chi ma co PE>0
    okx=ok&ex
    rows.append(dict(time=t,n=len(d),
      pb_cw=mc.sum()/bk.sum(), pb_cw_exvic=mc[ex].sum()/bk[ex].sum(),
      pb_cw_extop1=np.delete(mc,i1).sum()/np.delete(bk,i1).sum(),
      pb_cap10=harm(cap_weights(w),pb), pb_trim=mc[keep].sum()/bk[keep].sum(),
      pb_ewmed=np.median(pb), pb_ewmean=pb.mean(),
      pe_cw=mc[ok].sum()/er[ok].sum() if ok.sum()>5 else np.nan,
      pe_cw_exvic=mc[okx].sum()/er[okx].sum() if okx.sum()>5 else np.nan,
      top1_tk=tk[i1], top1_w=w[i1], top1_pb=pb[i1],
      vic_w=w[tk=='VIC'][0] if (tk=='VIC').any() else 0.0))
S=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
S['roe_cw']=S.pb_cw/S.pe_cw; S['roe_cw_exvic']=S.pb_cw_exvic/S.pe_cw_exvic

a=pd.read_csv(EXP+'agg_all2.csv',parse_dates=['time'])
a['pb_all']=a.mcap_all/a.book_all; a['pb_all_exvic']=a.mcap_ex/a.book_ex
S=S.merge(a[['time','pb_all','pb_all_exvic','n_pb']],on='time',how='left')
S.to_csv(EXP+'pb_variants_final.csv',index=False)
cur=S.iloc[-1]; end=cur.time

wins={'full_2008+':S.time>='2008-01-01','last_10Y':S.time>=end-pd.DateOffset(years=10),
      'last_5Y':S.time>=end-pd.DateOffset(years=5),'last_3Y':S.time>=end-pd.DateOffset(years=3)}
cols=['pb_all','pb_all_exvic','pb_cw','pb_cw_exvic','pb_cw_extop1','pb_cap10','pb_trim','pb_ewmed','pb_ewmean',
      'pe_cw','pe_cw_exvic','roe_cw','roe_cw_exvic']
out=[]
for wn,m in wins.items():
    sub=S[m]
    for c in cols:
        s=sub[c].dropna(); q=s.quantile([.05,.25,.5,.75,.95])
        out.append(dict(window=wn,metric=c,cur=round(cur[c],4),pctile=round(100*(s<cur[c]).mean(),1),N=len(s),
          p05=round(q.iloc[0],3),p25=round(q.iloc[1],3),p50=round(q.iloc[2],3),p75=round(q.iloc[3],3),p95=round(q.iloc[4],3)))
R=pd.DataFrame(out); R.to_csv(EXP+'percentiles_final.csv',index=False)
print('=== HIEN TAI %s ==='%cur.time.date())
print(R[R.window=='last_3Y'][['metric','cur']].to_string(index=False))
print('\n=== BANG PHAN VI (pivot: hang=phuong phap, cot=cua so) ===')
pv=R.pivot(index='metric',columns='window',values='pctile').reindex(cols)[['full_2008+','last_10Y','last_5Y','last_3Y']]
pv['cur']=R.drop_duplicates('metric').set_index('metric').cur.reindex(cols)
print(pv.to_string())
print('\n=== chi tiet tung cua so ==='); 
for wn in wins: print(R[R.window==wn].to_string(index=False)); print()

# ---- chart ----
fig,ax=plt.subplots(2,1,figsize=(13,9),sharex=True,gridspec_kw={'height_ratios':[2,1]})
ax[0].plot(S.time,S.pb_cw,lw=1.1,label='PB cap-weighted top-100 (CÓ VIC) — bản đã báo cáo')
ax[0].plot(S.time,S.pb_cw_exvic,lw=1.1,label='PB cap-weighted top-100 EX-VIC')
ax[0].plot(S.time,S.pb_cw_extop1,lw=1.0,alpha=.8,label='PB cap-weighted, bỏ mã lớn nhất MỖI NGÀY (đối xứng)')
ax[0].plot(S.time,S.pb_cap10,lw=1.0,alpha=.8,label='PB capped-weight 10%/mã')
ax[0].plot(S.time,S.pb_ewmed,lw=1.2,color='k',alpha=.75,label='PB trung vị equal-weight (mã điển hình)')
ax[0].axhline(cur.pb_cw,ls=':',c='C0',lw=.8); ax[0].axhline(cur.pb_ewmed,ls=':',c='k',lw=.8)
ax[0].set_ylabel('P/B'); ax[0].legend(fontsize=8,ncol=2); ax[0].grid(alpha=.25)
ax[0].set_title('P/B thị trường VN (rổ top-100 vốn hoá) — 5 cách đo · dữ liệu đến %s'%cur.time.date())
ax[1].plot(S.time,100*S.top1_w,lw=1,color='C3',label='tỷ trọng mã LỚN NHẤT trong top-100')
ax[1].plot(S.time,100*S.vic_w,lw=1,color='C1',alpha=.8,label='tỷ trọng VIC')
ax[1].axhline(15,ls='--',c='grey',lw=.8); ax[1].set_ylabel('% vốn hoá top-100')
ax[1].legend(fontsize=8); ax[1].grid(alpha=.25); ax[1].set_ylim(0,25)
plt.tight_layout(); plt.savefig('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/pb_exvic_20260729.png',dpi=115)
print('chart saved')
