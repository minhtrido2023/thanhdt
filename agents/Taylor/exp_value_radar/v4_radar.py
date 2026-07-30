"""VIEC 4 — VALUE RADAR: composite dinh gia PIT (khong nhin truoc), doc CHEAP/FAIR/EXPENSIVE."""
import warnings; warnings.filterwarnings('ignore')
import sys, pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width',260)

S=pd.read_csv(EXP+'pe_variants.csv',parse_dates=['time'])
E=pd.read_csv(EXP+'ey_spread.csv',parse_dates=['time'])[['time','deposit_rate','sp_pe_cap10','ey_pe_cap10']]
F=pd.read_csv(OLD+'panel_fwd.csv',parse_dates=['time'])
D=pd.read_csv(EXP+'dt5g.csv',parse_dates=['time'])

d=S[['time','pe_cap10','pb_cap10','pe_agg_pos','pb_cw','pe_ewmed','pb_ewmed']].merge(E,on='time',how='left')
d=d.merge(F[['time','vni_close','fwd_1M','fwd_3M','fwd_6M','fwd_12M','minfwd_12M']],on='time',how='left')
d=d.merge(D,on='time',how='left').sort_values('time').reset_index(drop=True)

MINP=500
def pit_pct(s,minp=MINP):
    """phan vi EXPANDING, chi dung du lieu DEN thoi diem do (nhan qua, khong nhin truoc)."""
    v=s.values.astype(float); out=np.full(len(v),np.nan)
    for i in range(len(v)):
        if not np.isfinite(v[i]): continue
        h=v[:i+1]; h=h[np.isfinite(h)]
        if len(h)<minp: continue
        out[i]=100*(h[:-1]<v[i]).mean()
    return out
def roll_pct(s,win=2500):
    v=s.values.astype(float); out=np.full(len(v),np.nan)
    for i in range(len(v)):
        if not np.isfinite(v[i]): continue
        h=v[max(0,i-win+1):i+1]; h=h[np.isfinite(h)]
        if len(h)<MINP: continue
        out[i]=100*(h[:-1]<v[i]).mean()
    return out

d['p_pe']=pit_pct(d.pe_cap10)
d['p_pb']=pit_pct(d.pb_cap10)
d['p_sp']=100-pit_pct(d.sp_pe_cap10)     # spread rong = re => dao chieu de "cao = dat"
d['p_pe_r']=roll_pct(d.pe_cap10); d['p_pb_r']=roll_pct(d.pb_cap10); d['p_sp_r']=100-roll_pct(d.sp_pe_cap10)

print('='*100); print('B1 — DA CONG TUYEN giua 3 thanh phan (tren chuoi phan vi PIT)'); print('='*100)
cc=d[['p_pe','p_pb','p_sp']].dropna()
print('N chung=%d (%s -> %s)'%(len(cc),d.loc[cc.index[0],'time'].date(),d.loc[cc.index[-1],'time'].date()))
print(cc.corr().round(3).to_string())
print('\ncorr tren GIA TRI THO (khong phan vi):')
print(d[['pe_cap10','pb_cap10','sp_pe_cap10']].dropna().corr().round(3).to_string())
# VIF tho
X=cc.values; 
for i,c in enumerate(cc.columns):
    y=X[:,i]; Z=np.column_stack([np.ones(len(X)),np.delete(X,i,1)])
    b=np.linalg.lstsq(Z,y,rcond=None)[0]; r2=1-((y-Z@b)**2).sum()/((y-y.mean())**2).sum()
    print('  VIF(%s) = %.2f  (R2=%.3f)'%(c,1/max(1e-9,1-r2),r2))

# ---- composite ----
d['radar3']=d[['p_pe','p_pb','p_sp']].mean(axis=1)          # chinh: 3 thanh phan
d['radar2']=d[['p_pe','p_pb']].mean(axis=1)                 # du phong: 2 thanh phan (co tu 2010)
d['radar3_med']=d[['p_pe','p_pb','p_sp']].median(axis=1)
d['radar3_roll']=d[['p_pe_r','p_pb_r','p_sp_r']].mean(axis=1)
def lab(x):
    if not np.isfinite(x): return ''
    return 'CHEAP' if x<33 else ('EXPENSIVE' if x>67 else 'FAIR')
for c in ['radar3','radar2','radar3_med','radar3_roll']: d['lab_'+c]=d[c].map(lab)
d.to_csv(EXP+'radar.csv',index=False)

cur=d.dropna(subset=['radar3']).iloc[-1]
print('\n'+'='*100); print('B2 — DOC HIEN TAI (%s)'%cur.time.date()); print('='*100)
print('  PE capped10 = %.2f -> phan vi PIT %.1f'%(cur.pe_cap10,cur.p_pe))
print('  PB capped10 = %.2f -> phan vi PIT %.1f'%(cur.pb_cap10,cur.p_pb))
print('  EY-spread   = %+.2fpp -> phan vi PIT (dao chieu) %.1f'%(cur.sp_pe_cap10,cur.p_sp))
print('  RADAR3 = %.1f -> %s   | radar2(PE+PB)=%.1f %s | trung vi=%.1f %s | rolling10Y=%.1f %s'%(
    cur.radar3,cur.lab_radar3,cur.radar2,cur.lab_radar2,cur.radar3_med,cur.lab_radar3_med,cur.radar3_roll,cur.lab_radar3_roll))
print('  DT5G state hom nay = %s'%cur.state)

# ---- phan bo nhan ----
print('\nPhan bo nhan radar3 tren toan chuoi co du lieu (%d phien):'%d.radar3.notna().sum())
print(d.lab_radar3.replace('',np.nan).dropna().value_counts().to_string())
print('\nRadar3 trung binh theo nam:')
print(d.dropna(subset=['radar3']).groupby(d.time.dt.year).radar3.mean().round(1).to_string())

# =============== B3: LIET KE MOI DOT BEAR/WASHOUT 2008+ va doc radar tai day ===============
print('\n'+'='*100); print('B3 — MOI DOT SUT GIAM LON 2008+ : radar doc gi TAI DAY?'); print('='*100)
v=d.dropna(subset=['vni_close']).copy().reset_index(drop=True)
v['peak52']=v.vni_close.rolling(250,min_periods=60).max()
v['dd']=v.vni_close/v.peak52-1
eps=[];  inep=False
for i,r in v.iterrows():
    if not inep and r.dd<=-0.20: inep=True; st=i
    elif inep and r.dd>-0.10: eps.append((st,i)); inep=False
if inep: eps.append((st,len(v)-1))
rows=[]
for a,b in eps:
    seg=v.iloc[a:b+1]; j=seg.dd.idxmin(); t=v.loc[j]
    rows.append(dict(dot='%s..%s'%(v.loc[a,'time'].date(),v.loc[b,'time'].date()),
        day=t.time.date(), n_phien=b-a+1, dd_day=round(100*t.dd,1), vni=round(t.vni_close,1),
        radar3=round(t.radar3,1) if np.isfinite(t.radar3) else np.nan, nhan=t.lab_radar3,
        radar2=round(t.radar2,1) if np.isfinite(t.radar2) else np.nan, nhan2=t.lab_radar2,
        PE=round(t.pe_cap10,1), PB=round(t.pb_cap10,2), spread=round(t.sp_pe_cap10,2) if np.isfinite(t.sp_pe_cap10) else np.nan,
        DT5G=t.state if pd.notna(t.state) else '',
        fwd6M=round(100*t.fwd_6M,1) if np.isfinite(t.fwd_6M) else np.nan,
        fwd12M=round(100*t.fwd_12M,1) if np.isfinite(t.fwd_12M) else np.nan))
EP=pd.DataFrame(rows); print(EP.to_string(index=False))
EP.to_csv(EXP+'episodes.csv',index=False)

# ---- cac moc user nhac cu the ----
print('\n'+'-'*100); print('CAC MOC USER NHAC CU THE (doc radar tai dung ngay)'); print('-'*100)
marks={'2018-Q4 day (thuong chien)':'2018-12-31','2018-07-11 (day giua nam)':'2018-07-11',
       '2022-Q2 day':'2022-06-16','2022-Q4 day (SCB/Terra)':'2022-11-15',
       '2020-03-30 (COVID day)':'2020-03-30','2012-01-06 (day 2012)':'2012-01-06',
       '2026-07-20 (CAPIT fire)':'2026-07-20','HOM NAY':str(cur.time.date())}
rows=[]
for k,ds in marks.items():
    s=d[d.time<=ds]
    if s.empty: continue
    t=s.iloc[-1]
    rows.append(dict(moc=k,ngay=t.time.date(),radar3=round(t.radar3,1) if np.isfinite(t.radar3) else np.nan,nhan=t.lab_radar3,
        radar2=round(t.radar2,1) if np.isfinite(t.radar2) else np.nan,nhan2=t.lab_radar2,
        p_pe=round(t.p_pe,1) if np.isfinite(t.p_pe) else np.nan,p_pb=round(t.p_pb,1) if np.isfinite(t.p_pb) else np.nan,
        p_sp=round(t.p_sp,1) if np.isfinite(t.p_sp) else np.nan,
        PE=round(t.pe_cap10,2),PB=round(t.pb_cap10,2),
        fwd12M=round(100*t.fwd_12M,1) if np.isfinite(t.fwd_12M) else np.nan,
        min12M=round(100*t.minfwd_12M,1) if np.isfinite(t.minfwd_12M) else np.nan))
print(pd.DataFrame(rows).to_string(index=False))

# =============== B4: radar co phan biet ket cuc khong? (base rate) ===============
print('\n'+'='*100); print('B4 — RADAR CO PHAN BIET KET CUC 12M KHONG? (base rate theo nhan)'); print('='*100)
g=d.dropna(subset=['radar3','fwd_12M'])
def epi_count(t):
    idx=np.array(t.index); 
    return 1+int((np.diff(idx)>21).sum()) if len(idx) else 0
rows=[]
for nh in ['CHEAP','FAIR','EXPENSIVE']:
    s=g[g.lab_radar3==nh]
    if not len(s): continue
    rows.append(dict(nhan=nh,n_ngay=len(s),n_episode=epi_count(s),
        fwd12M_trungvi=round(100*s.fwd_12M.median(),1),fwd12M_TB=round(100*s.fwd_12M.mean(),1),
        P_bear=round(100*(s.minfwd_12M<=-0.20).mean(),1),P_am=round(100*(s.fwd_12M<0).mean(),1)))
rows.append(dict(nhan='TAT CA',n_ngay=len(g),n_episode=epi_count(g),
    fwd12M_trungvi=round(100*g.fwd_12M.median(),1),fwd12M_TB=round(100*g.fwd_12M.mean(),1),
    P_bear=round(100*(g.minfwd_12M<=-0.20).mean(),1),P_am=round(100*(g.fwd_12M<0).mean(),1)))
print(pd.DataFrame(rows).to_string(index=False))
# tuong quan radar vs fwd
for h in ['fwd_3M','fwd_6M','fwd_12M']:
    s=d.dropna(subset=['radar3',h])
    print('  corr(radar3, %s) = %+.3f  (Spearman %+.3f, N=%d ngay, ~%d nam doc lap)'%(
        h,s.radar3.corr(s[h]),s.radar3.corr(s[h],method='spearman'),len(s),s.time.dt.year.nunique()))
