"""VIEC 1 — PE robust hoa: aggregate ratio-of-sums + 4 cach do doi xung (parity Phu luc B)."""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
OLDB='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
pd.set_option('display.width',250)

p=pd.read_parquet(EXP+'panel300.parquet')
p['time']=pd.to_datetime(p.time)
p['pb_i']=p.mcap/p.book
p=p[np.isfinite(p.pb_i)&(p.pb_i>0)].copy()          # ro PB>0 == dinh nghia Phu luc B
p['rk']=p.groupby('time').mcap.rank(ascending=False,method='first')
t100=p[p.rk<=100].copy()
nday=t100.groupby('time').size(); good=nday[nday>=50].index   # loai 2 ngay hong 2025-05-04/11
t100=t100[t100.time.isin(good)].copy()
t100['w']=t100.mcap/t100.groupby('time').mcap.transform('sum')
print('panel top-100: %d dong, %d phien, %s -> %s'%(len(t100),t100.time.nunique(),t100.time.min().date(),t100.time.max().date()))
# canh bao neu top-300 khong du sau khi loc PB>0
short=p.groupby('time').rk.max()
print('so phien co <100 ma sau loc PB>0: %d'%(nday<100).sum())

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
for t,d in t100.groupby('time'):
    mc=d.mcap.values; bk=d.book.values; er=d.earn.values; tk=d.ticker.values; w=d.w.values
    pe_i=d.PE.values.astype(float); pb=d.pb_i.values
    i1=int(np.argmax(mc)); notop1=np.ones(len(d),bool); notop1[i1]=False
    ex=tk!='VIC'
    fin=np.isfinite(er)                      # co du lieu loi nhuan (ke ca am)
    pos=fin&(er>0)                           # chi ma co lai
    okp=np.isfinite(pe_i)&(pe_i>0)
    # trimmed 5% theo PE (chi tren ma PE>0)
    tr=np.zeros(len(d),bool)
    if okp.sum()>20:
        ii=np.where(okp)[0]; o=ii[np.argsort(pe_i[ii])]
        k=max(1,int(round(0.05*len(o)))); tr[o[k:len(o)-k]]=True
    r=dict(time=t,n=len(d),
      # --- PE ---
      pe_agg_all = mc[fin].sum()/er[fin].sum() if fin.sum()>5 and er[fin].sum()>0 else np.nan,   # ke ca ma lo (chuan S&P)
      pe_agg_pos = mc[pos].sum()/er[pos].sum() if pos.sum()>5 else np.nan,                        # parity Phu luc B pe_cw
      pe_agg_pos_exvic = mc[pos&ex].sum()/er[pos&ex].sum() if (pos&ex).sum()>5 else np.nan,
      pe_agg_pos_extop1 = mc[pos&notop1].sum()/er[pos&notop1].sum() if (pos&notop1).sum()>5 else np.nan,
      pe_cap10 = harm(cap_weights(w[okp]),pe_i[okp]) if okp.sum()>5 else np.nan,
      pe_trim  = mc[tr].sum()/er[tr].sum() if tr.sum()>5 and er[tr].sum()>0 else np.nan,
      pe_ewmed = np.median(pe_i[okp]) if okp.sum()>5 else np.nan,
      pe_ewmean= pe_i[okp].mean() if okp.sum()>5 else np.nan,
      pe_capw_ratios = float(np.sum(w[okp]/w[okp].sum()*pe_i[okp])) if okp.sum()>5 else np.nan,  # SIGMA w*PE_i
      # --- PB (tai lap parity) ---
      pb_cw=mc.sum()/bk.sum(), pb_cap10=harm(cap_weights(w),pb), pb_ewmed=np.median(pb),
      pb_cw_extop1=mc[notop1].sum()/bk[notop1].sum(),
      top1_tk=tk[i1], top1_w=w[i1], top1_pe=pe_i[i1],
      n_loss=int((fin&(er<=0)).sum()), n_pe_pos=int(okp.sum()))
    rows.append(r)
S=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
S.to_csv(EXP+'pe_variants.csv',index=False)

# ---------- SELF-CHECK PARITY voi Phu luc B ----------
B=pd.read_csv(OLDB+'pb_variants_final.csv',parse_dates=['time'])
m=S.merge(B[['time','pb_cw','pb_cap10','pb_ewmed','pe_cw']],on='time',suffixes=('','_B'))
print('\n=== SELF-CHECK PARITY voi Phu luc B (%d phien chung) ==='%len(m))
for a,b in [('pb_cw','pb_cw_B'),('pb_cap10','pb_cap10_B'),('pb_ewmed','pb_ewmed_B'),('pe_agg_pos','pe_cw')]:
    d=(m[a]-m[b]).abs()
    print('  %-14s corr=%.10f  maxdiff=%.3e  median_diff=%.3e'%(a,m[a].corr(m[b]),d.max(),d.median()))

cur=S.dropna(subset=['pe_agg_pos']).iloc[-1]; end=cur.time
print('\n=== GIA TRI HIEN TAI (%s) ==='%end.date())
for c in ['pe_agg_all','pe_agg_pos','pe_capw_ratios','pe_agg_pos_exvic','pe_agg_pos_extop1','pe_cap10','pe_trim','pe_ewmed','pe_ewmean']:
    print('  %-18s %.3f'%(c,cur[c]))
print('  top1 = %s (w=%.1f%%, PE=%.1f) | so ma lo trong top-100 = %d | so ma PE>0 = %d'%(
    cur.top1_tk,100*cur.top1_w,cur.top1_pe,cur.n_loss,cur.n_pe_pos))

wins={'full_2008+':S.time>='2008-01-01','last_10Y':S.time>=end-pd.DateOffset(years=10),
      'last_5Y':S.time>=end-pd.DateOffset(years=5),'last_3Y':S.time>=end-pd.DateOffset(years=3)}
cols=['pe_agg_all','pe_agg_pos','pe_capw_ratios','pe_agg_pos_exvic','pe_agg_pos_extop1','pe_cap10','pe_trim','pe_ewmed','pe_ewmean']
out=[]
for wn,msk in wins.items():
    sub=S[msk]
    for c in cols:
        s=sub[c].dropna()
        if not len(s) or not np.isfinite(cur[c]): continue
        out.append(dict(window=wn,metric=c,cur=round(cur[c],3),pctile=round(100*(s<cur[c]).mean(),1),N=len(s),
                        p05=round(s.quantile(.05),2),p50=round(s.quantile(.5),2),p95=round(s.quantile(.95),2)))
R=pd.DataFrame(out); R.to_csv(EXP+'pe_percentiles.csv',index=False)
pv=R.pivot(index='metric',columns='window',values='pctile').reindex(cols)[['full_2008+','last_10Y','last_5Y','last_3Y']]
pv.insert(0,'cur',[round(cur[c],3) for c in cols])
print('\n=== BANG PHAN VI PE (100 = dat nhat) ===')
print(pv.to_string())

# ---------- quet meo mo do 1 ma (giong B.3, nhung cho PE) ----------
print('\n=== MUC MEO MO PE = pe_agg_pos - pe_agg_pos_extop1 ===')
S['dist']=S.pe_agg_pos-S.pe_agg_pos_extop1
g=S.dropna(subset=['dist'])
print('hien tai %+.3f (phan vi %.1f) | trung vi lich su %+.3f | max truoc 2025 %+.3f (%s) | max toan lich su %+.3f (%s)'%(
  g.dist.iloc[-1],100*(g.dist<g.dist.iloc[-1]).mean(),g.dist.median(),
  g[g.time<'2025-01-01'].dist.max(),g.loc[g[g.time<'2025-01-01'].dist.idxmax(),'time'].date(),
  g.dist.max(),g.loc[g.dist.idxmax(),'time'].date()))
print('\nmuc meo mo PE theo ma lon nhat (chi phien co |dist|>1.0):')
h=g[g.dist.abs()>1.0]
print(h.groupby('top1_tk').agg(n=('dist','size'),dist_med=('dist','median'),dist_max=('dist','max'),
      tu=('time','min'),den=('time','max')).sort_values('n',ascending=False).to_string())
