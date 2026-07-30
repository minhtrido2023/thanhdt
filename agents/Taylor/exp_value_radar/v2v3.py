"""VIEC 2 (goc nhin khac: EY-spread, tach nganh, PEG) + VIEC 3 (breadth PB<1)."""
import warnings; warnings.filterwarnings('ignore')
import sys, pandas as pd, numpy as np
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
from deposit_rate_vn import deposit_events_df
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width',250)

S=pd.read_csv(EXP+'pe_variants.csv',parse_dates=['time'])
A=pd.read_csv(EXP+'agg_universe.csv',parse_dates=['time'])
p=pd.read_parquet(EXP+'panel300.parquet'); p['time']=pd.to_datetime(p.time)
p['pb_i']=p.mcap/p.book
end=S.time.max()

def pct(s,v): 
    s=pd.Series(s).dropna(); return 100*(s<v).mean() if len(s) else np.nan
def blocks_year(t):  # so nam duong lich doc lap = can duoi tho cua N doc lap
    return pd.Series(t).dt.year.nunique()
def boot_pct(series,times,v,B=2000,seed=11):
    """CI90 cho phan vi hien tai, block-bootstrap theo NAM (khoi ~250 phien)."""
    df=pd.DataFrame({'t':pd.to_datetime(times),'x':series}).dropna()
    if df.empty: return (np.nan,np.nan)
    df['blk']=df.t.dt.year
    bl=df.blk.unique(); rng=np.random.default_rng(seed); out=[]
    for _ in range(B):
        pick=rng.choice(bl,size=len(bl),replace=True)
        x=np.concatenate([df.x.values[df.blk.values==b] for b in pick])
        out.append(100*(x<v).mean())
    return tuple(np.percentile(out,[5,95]))

# =========================== VIEC 3: breadth PB<1 ===========================
print('='*100); print('VIEC 3 — TY LE MA CO PB < 1 (cross-sectional breadth, DEM DAU MA)'); print('='*100)
A['pct_lt1_all']=100*A.n_pb_lt1/A.n_pb_pos
# top-N theo von hoa
br=[]
for N in (100,250,500):
    q=p[np.isfinite(p.pb_i)&(p.pb_i>0)].copy()
    q['rk']=q.groupby('time').mcap.rank(ascending=False,method='first')
    q=q[q.rk<=N]
    g=q.groupby('time').pb_i.agg(n='size',lt1=lambda s:(s<1).sum())
    br.append((N,(100*g.lt1/g.n).rename('top%d'%N)))
B3=A[['time','pct_lt1_all','n_pb_pos','n_pb_lt1']].set_index('time')
for N,s in br: B3['top%d'%N]=s
B3=B3.dropna(subset=['pct_lt1_all'])
B3=B3[B3.n_pb_pos>=50]
cur3=B3.iloc[-1]
print('\nNgay du lieu: %s'%B3.index[-1].date())
print('  Toan universe (PB>0): %d/%d ma co PB<1  = %.1f%%'%(cur3.n_pb_lt1,cur3.n_pb_pos,cur3.pct_lt1_all))
for N in (100,250,500): print('  Top-%-3d von hoa        : %.1f%%'%(N,cur3['top%d'%N]))
print('\nPhan vi lich su cua CHINH ty le nay (100 = nhieu ma PB<1 nhat = so hai nhat):')
rows=[]
for c,lab in [('pct_lt1_all','toan universe'),('top100','top-100'),('top250','top-250'),('top500','top-500')]:
    for wn,msk in [('2008+',B3.index>='2008-01-01'),('10Y',B3.index>=end-pd.DateOffset(years=10)),
                   ('5Y',B3.index>=end-pd.DateOffset(years=5)),('3Y',B3.index>=end-pd.DateOffset(years=3))]:
        s=B3[c][msk]; v=cur3[c]
        lo,hi=boot_pct(s.values,s.index,v) if wn=='2008+' else (np.nan,np.nan)
        rows.append(dict(chi_bao=lab,window=wn,hien_tai=round(v,1),pctile=round(pct(s,v),1),N_ngay=len(s),
                         N_nam=blocks_year(s.index),p50=round(s.median(),1),p90=round(s.quantile(.9),1),
                         CI90_pctile='[%.0f, %.0f]'%(lo,hi) if np.isfinite(lo) else ''))
R3=pd.DataFrame(rows); print(R3.to_string(index=False))
print('\nKY LUC lich su (toan universe): max %.1f%% ngay %s | cac dot >50%%: %s'%(
    B3.pct_lt1_all.max(),B3.pct_lt1_all.idxmax().date(),
    sorted(B3[B3.pct_lt1_all>50].index.year.unique().tolist())))
print('Trung binh theo nam (toan universe / top-100):')
yr=B3.groupby(B3.index.year)[['pct_lt1_all','top100','top250']].mean().round(1)
print(yr.to_string())
B3.to_csv(EXP+'breadth_pb_lt1.csv')

# =========================== VIEC 2a: EY vs lai suat huy dong ===========================
print('\n'+'='*100); print('VIEC 2a — SPREAD lai suat: earnings yield (1/PE) TRU lai suat huy dong Big4-12M'); print('='*100)
ev=deposit_events_df()
S2=S.copy()
S2=pd.merge_asof(S2.sort_values('time'),ev.sort_values('time'),on='time',direction='backward')
for c in ['pe_agg_pos','pe_cap10','pe_ewmed']:
    S2['ey_'+c]=100.0/S2[c]
    S2['sp_'+c]=S2['ey_'+c]-S2.deposit_rate
S2=S2.dropna(subset=['deposit_rate'])
cur2=S2.iloc[-1]
print('\nNgay %s | lai suat huy dong Big4-12M = %.2f%%'%(cur2.time.date(),cur2.deposit_rate))
rows=[]
for c in ['pe_agg_pos','pe_cap10','pe_ewmed']:
    s_all=S2[S2.time>='2011-01-01']
    v=cur2['sp_'+c]
    lo,hi=boot_pct(s_all['sp_'+c].values,s_all.time,v)
    rows.append(dict(PE_dung=c,EY=round(cur2['ey_'+c],2),spread=round(v,2),
        pctile_2011=round(pct(s_all['sp_'+c],v),1),CI90='[%.0f, %.0f]'%(lo,hi),
        N_ngay=len(s_all),N_nam=blocks_year(s_all.time),
        p10=round(s_all['sp_'+c].quantile(.1),2),p50=round(s_all['sp_'+c].median(),2),p90=round(s_all['sp_'+c].quantile(.9),2)))
    for wn,msk in [('10Y',S2.time>=end-pd.DateOffset(years=10)),('5Y',S2.time>=end-pd.DateOffset(years=5)),('3Y',S2.time>=end-pd.DateOffset(years=3))]:
        rows[-1]['pctile_'+wn]=round(pct(S2[msk]['sp_'+c],v),1)
R2a=pd.DataFrame(rows); print(R2a.to_string(index=False))
print('\n(LUU Y phan vi o day: 100 = spread RONG nhat = RE nhat so voi gui tiet kiem — nguoc chieu voi bang PE)')
print('Trung binh spread theo nam (pe_cap10):')
print(S2[S2.time>='2011-01-01'].groupby(S2.time.dt.year).sp_pe_cap10.mean().round(2).to_string())
S2.to_csv(EXP+'ey_spread.csv',index=False)

# =========================== VIEC 2b: tach nganh ngan hang / phi ngan hang ===========================
print('\n'+'='*100); print('VIEC 2b — TACH NGANH: ngan hang (ICB 8355) vs phi ngan hang'); print('='*100)
A2=A[A.n_pb_pos>=50].copy()
A2['pb_bank']=A2.mcap_pb_bank/A2.book_pb_bank
A2['pb_nonbank']=(A2.mcap_pb-A2.mcap_pb_bank)/(A2.book_pb-A2.book_pb_bank)
A2['pe_bank']=A2.mcap_pe_bank/A2.earn_bank
A2['pe_nonbank']=(A2.mcap_pe-A2.mcap_pe_bank)/(A2.earn_all-A2.earn_bank)
A2['w_bank_mcap']=100*A2.mcap_pb_bank/A2.mcap_pb
A2=A2[A2.time>='2008-01-01']
c2=A2.iloc[-1]
print('\nNgay %s | ngan hang chiem %.1f%% von hoa ro PB>0 (toan universe)'%(c2.time.date(),c2.w_bank_mcap))
rows=[]
for c in ['pe_bank','pe_nonbank','pb_bank','pb_nonbank']:
    v=c2[c]; s=A2[c]
    lo,hi=boot_pct(s.values,A2.time,v)
    d=dict(chi_bao=c,hien_tai=round(v,3),pctile_2008=round(pct(s,v),1),CI90='[%.0f, %.0f]'%(lo,hi),
           N_nam=blocks_year(A2.time))
    for wn,msk in [('10Y',A2.time>=end-pd.DateOffset(years=10)),('5Y',A2.time>=end-pd.DateOffset(years=5)),('3Y',A2.time>=end-pd.DateOffset(years=3))]:
        d['pctile_'+wn]=round(pct(A2[msk][c],v),1)
    rows.append(d)
print(pd.DataFrame(rows).to_string(index=False))
A2.to_csv(EXP+'sector_split.csv',index=False)

# =========================== VIEC 2c: PEG ===========================
print('\n'+'='*100); print('VIEC 2c — PEG thi truong (PE / tang truong loi nhuan %)'); print('='*100)
q=p[np.isfinite(p.pb_i)&(p.pb_i>0)].copy()
q['rk']=q.groupby('time').mcap.rank(ascending=False,method='first'); q=q[q.rk<=100]
g=q.groupby('time').agg(mcap=('mcap','sum'),np0=('NP_P0','sum'),np4=('NP_P4','sum'),
                        earn=('earn','sum'),n=('ticker','size'))
g=g[g.n>=50]
g['growth_pct']=100*(g.np0/g.np4-1)
g['pe_agg']=g.mcap/g.earn
g['peg_agg']=g.pe_agg/g.growth_pct
# PEG cat ngang: trung vi cua PE_i/growth_i tren ma co PE>0 va growth>0
q['gr_i']=100*(q.NP_P0/q.NP_P4-1)
q['peg_i']=np.where((q.PE>0)&(q.gr_i>0),q.PE/q.gr_i,np.nan)
med=q.groupby('time').peg_i.median().rename('peg_ewmed')
g=g.join(med); g=g[g.index>='2008-01-01']
cg=g.dropna(subset=['peg_agg']).iloc[-1]
print('\nNgay %s | tang truong LN gop top-100 (NP_P0 vs NP_P4) = %+.1f%% | PE_agg=%.2f'%(g.index[-1].date(),cg.growth_pct,cg.pe_agg))
rows=[]
for c in ['peg_agg','peg_ewmed','growth_pct']:
    v=cg[c]; s=g[c].replace([np.inf,-np.inf],np.nan)
    lo,hi=boot_pct(s.values,g.index,v)
    d=dict(chi_bao=c,hien_tai=round(v,3),pctile_2008=round(pct(s,v),1),CI90='[%.0f, %.0f]'%(lo,hi),N_nam=blocks_year(g.index))
    for wn,msk in [('10Y',g.index>=end-pd.DateOffset(years=10)),('5Y',g.index>=end-pd.DateOffset(years=5)),('3Y',g.index>=end-pd.DateOffset(years=3))]:
        d['pctile_'+wn]=round(pct(s[msk],v),1)
    rows.append(d)
print(pd.DataFrame(rows).to_string(index=False))
print('\nCANH BAO PEG: mau so am (tang truong am) lam PEG vo nghia — so phien growth<=0 trong 2008+: %d/%d (%.1f%%)'%(
    (g.growth_pct<=0).sum(),len(g),100*(g.growth_pct<=0).mean()))
g.to_csv(EXP+'peg.csv')
