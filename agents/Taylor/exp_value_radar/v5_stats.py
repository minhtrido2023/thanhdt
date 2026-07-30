"""VIEC 5 + ky luat da kiem dinh: CI90 block-bootstrap, BH/Bonferroni, sector robust, chart."""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
pd.set_option('display.width',260)
d=pd.read_csv(EXP+'radar.csv',parse_dates=['time'])
p=pd.read_parquet(EXP+'panel300.parquet'); p['time']=pd.to_datetime(p.time)

# ---------- 1) SECTOR ROBUST: phi ngan hang co bi VIC lam meo khong? ----------
print('='*100); print('1 — TACH NGANH BAN VUNG (phi ngan hang: co/khong VIC, capped-10%)'); print('='*100)
q=p.copy(); q['pb_i']=q.mcap/q.book
q=q[np.isfinite(q.pb_i)&(q.pb_i>0)]
q['rk']=q.groupby('time').mcap.rank(ascending=False,method='first'); q=q[q.rk<=100]
q['bank']=q.ICB_Code==8355
def cap_w(w,cap=.10):
    w=np.asarray(w,float).copy()
    for _ in range(60):
        w=w/w.sum(); o=w>cap+1e-12
        if not o.any(): break
        ex=(w[o]-cap).sum(); w[o]=cap; f=~o
        if w[f].sum()<=0: break
        w[f]+=ex*w[f]/w[f].sum()
    return w/w.sum()
rows=[]
for t,g in q.groupby('time'):
    nb=g[~g.bank]; bk=g[g.bank]
    nbx=nb[nb.ticker!='VIC']
    e=lambda s:(s.earn.values,s.mcap.values)
    def agg(s):
        m,er=s.mcap.values,s.earn.values; ok=np.isfinite(er)&(er>0)
        return (m.sum()/s.book.values.sum(), m[ok].sum()/er[ok].sum() if ok.sum()>3 else np.nan)
    pbn,pen=agg(nb); pbx,pex=agg(nbx); pbb,peb=agg(bk) if len(bk)>2 else (np.nan,np.nan)
    w=cap_w(nb.mcap.values); pb_nb_cap=w.sum()/(w/nb.pb_i.values).sum()
    rows.append(dict(time=t,pb_nb=pbn,pe_nb=pen,pb_nb_exvic=pbx,pe_nb_exvic=pex,
                     pb_bank=pbb,pe_bank=peb,pb_nb_cap10=pb_nb_cap,n_bank=len(bk)))
SEC=pd.DataFrame(rows).sort_values('time'); SEC=SEC[SEC.time>='2008-01-01']
c=SEC.iloc[-1]; end=SEC.time.max()
out=[]
for col in ['pb_bank','pe_bank','pb_nb','pe_nb','pb_nb_exvic','pe_nb_exvic','pb_nb_cap10']:
    r=dict(chi_bao=col,hien_tai=round(c[col],3))
    for wn,m in [('2008+',SEC.time>='2008-01-01'),('10Y',SEC.time>=end-pd.DateOffset(years=10)),
                 ('5Y',SEC.time>=end-pd.DateOffset(years=5)),('3Y',SEC.time>=end-pd.DateOffset(years=3))]:
        s=SEC[m][col].dropna(); r['pct_'+wn]=round(100*(s<c[col]).mean(),1)
    out.append(r)
print(pd.DataFrame(out).to_string(index=False))
SEC.to_csv(EXP+'sector_robust.csv',index=False)

# ---------- 2) BH / Bonferroni tren HO cac lang kinh da thu ----------
print('\n'+'='*100); print('2 — DA KIEM DINH: BH (FDR 10%) + Bonferroni tren ho lang kinh dinh gia'); print('='*100)
# p-value 1 phia "re hon lich su" = phan vi/100 (2008+, cua so day du). N doc lap ~ so nam.
tests=[('PE aggregate (top-100)',44.3),('PE capped-10%',27.4),('PE trimmed-5%',19.6),('PE median EW',49.8),
       ('PE bo ma lon nhat',19.9),('PB capped-10% (PhuLucB)',35.0),('PB median EW (PhuLucB)',35.2),
       ('PB bo ma lon nhat (PhuLucB)',22.9),('EY-spread vs huy dong (2011+)',100-52.1),
       ('PE ngan hang',17.8),('PB ngan hang',16.9),('PE phi-ngan-hang',48.4),('PB phi-ngan-hang',70.1),
       ('PEG aggregate',37.7),('PEG median EW',62.1),('%ma PB<1 (toan universe, dao chieu)',100-64.3),
       ('%ma PB<1 (top-100, dao chieu)',100-38.3)]
T=pd.DataFrame(tests,columns=['lang_kinh','pctile']); T['p_1phia']=T.pctile/100
T=T.sort_values('p_1phia').reset_index(drop=True); m=len(T)
T['rank']=T.index+1; T['BH_nguong_10%']=0.10*T['rank']/m; T['Bonferroni_5%']=0.05/m
T['qua_BH']=T.p_1phia<=T['BH_nguong_10%']; T['qua_Bonf']=T.p_1phia<=T['Bonferroni_5%']
print(T[['lang_kinh','pctile','p_1phia','BH_nguong_10%','qua_BH','qua_Bonf']].to_string(index=False))
print('\nSo lang kinh thu = %d | qua BH(FDR10%%): %d | qua Bonferroni(5%%): %d'%(m,T.qua_BH.sum(),T.qua_Bonf.sum()))
print('LUU Y: p_1phia = phan vi/100 KHONG phai p-value that (chuoi tu tuong quan manh, N doc lap ~19 nam,')
print('       khong phai ~4600 ngay). Bang nay chi de XEP HANG do manh tuong doi, khong phai kiem dinh chinh thuc.')

# ---------- 3) BASE RATE theo nhan radar, CI90 block-bootstrap theo episode ----------
print('\n'+'='*100); print('3 — RADAR PHAN BIET KET CUC 12M: CI90 block-bootstrap theo episode'); print('='*100)
g=d.dropna(subset=['radar3','fwd_12M','minfwd_12M']).reset_index(drop=True)
def blocks(idx): return np.concatenate([[0],np.cumsum(np.diff(idx)>21)])
def boot(sub,fn,B=4000,seed=3):
    idx=np.array(sub.index); br=blocks(idx); eps=np.unique(br)
    rng=np.random.default_rng(seed); o=[]
    for _ in range(B):
        pick=rng.choice(eps,size=len(eps),replace=True)
        o.append(fn(pd.concat([sub[br==e] for e in pick])))
    return np.percentile(o,[5,95]),len(eps)
rows=[]
for nh in ['CHEAP','FAIR','EXPENSIVE']:
    s=g[g.lab_radar3==nh]
    if not len(s): continue
    ci_m,ne=boot(s,lambda x:100*x.fwd_12M.median())
    ci_b,_ =boot(s,lambda x:100*(x.minfwd_12M<=-0.20).mean())
    rows.append(dict(nhan=nh,n_ngay=len(s),n_ep=ne,fwd12M_trvi=round(100*s.fwd_12M.median(),1),
        CI90_fwd='[%.1f, %.1f]'%tuple(ci_m),P_bear=round(100*(s.minfwd_12M<=-0.20).mean(),1),
        CI90_bear='[%.0f, %.0f]'%tuple(ci_b)))
print(pd.DataFrame(rows).to_string(index=False))
# hieu CHEAP - EXPENSIVE
A=g[g.lab_radar3=='CHEAP']; Bx=g[g.lab_radar3=='EXPENSIVE']
def diffboot(B=4000,seed=5):
    ia,ib=np.array(A.index),np.array(Bx.index); ba,bb=blocks(ia),blocks(ib)
    ea,eb=np.unique(ba),np.unique(bb); rng=np.random.default_rng(seed); o=[]
    for _ in range(B):
        pa=rng.choice(ea,size=len(ea),replace=True); pb=rng.choice(eb,size=len(eb),replace=True)
        xa=pd.concat([A[ba==e] for e in pa]); xb=pd.concat([Bx[bb==e] for e in pb])
        o.append(100*(xa.fwd_12M.median()-xb.fwd_12M.median()))
    return np.percentile(o,[5,50,95]),(np.array(o)<=0).mean()
ci,pneg=diffboot()
print('\nHieu fwd12M trung vi (CHEAP - EXPENSIVE) = %+.1fpp | CI90 [%+.1f, %+.1f] | P(hieu<=0)=%.3f'%(
    100*(A.fwd_12M.median()-Bx.fwd_12M.median()),ci[0],ci[2],pneg))
print('N_episode: CHEAP=%d, EXPENSIVE=%d  <= DAY LA CO MAU THAT'%(len(np.unique(blocks(np.array(A.index)))),
                                                                  len(np.unique(blocks(np.array(Bx.index))))))

# ---------- 4) Chi tai DAY cac dot washout (N cuc nho — bao trung thuc) ----------
print('\n'+'='*100); print('4 — CHI TAI DAY CAC DOT WASHOUT (N cuc nho)'); print('='*100)
EPI=pd.read_csv(EXP+'episodes.csv')
e=EPI.dropna(subset=['radar3','fwd12M'])
print(e[['day','dd_day','radar3','nhan','fwd6M','fwd12M']].to_string(index=False))
ch=e[e.nhan=='CHEAP']; nc=e[e.nhan!='CHEAP']
print('\nday CHEAP  : N=%d, fwd12M trung vi %+.1f%%  (%s)'%(len(ch),ch.fwd12M.median(),', '.join('%+.0f'%x for x in ch.fwd12M)))
print('day KHONG-CHEAP: N=%d, fwd12M trung vi %+.1f%%  (%s)'%(len(nc),nc.fwd12M.median(),', '.join('%+.0f'%x for x in nc.fwd12M)))
print('=> N=%d+%d. Bat ky kiem dinh nao tren co mau nay deu VO NGHIA THONG KE.'%(len(ch),len(nc)))

# ---------- 5) chart ----------
v=d.dropna(subset=['radar3']).copy()
fig,ax=plt.subplots(3,1,figsize=(14,11),sharex=True,gridspec_kw={'height_ratios':[2,1.4,1]})
ax[0].fill_between(v.time,0,33,color='#2e7d32',alpha=.10); ax[0].fill_between(v.time,33,67,color='#f9a825',alpha=.08)
ax[0].fill_between(v.time,67,100,color='#c62828',alpha=.10)
ax[0].plot(v.time,v.radar3,lw=1.3,color='k',label='VALUE RADAR (trung binh 3 phân vị PIT)')
ax[0].plot(v.time,v.radar3.rolling(60).mean(),lw=1.0,color='C0',alpha=.7,label='trung bình trượt 60 phiên')
for lab_,dt in [('2018-Q4','2018-12-28'),('2022-Q2','2022-06-16'),('2022-Q4','2022-11-15'),
                ('2020-03','2020-03-30'),('nay','2026-07-30')]:
    x=pd.Timestamp(dt); y=v[v.time<=x].radar3.iloc[-1] if len(v[v.time<=x]) else np.nan
    ax[0].scatter([x],[y],s=45,zorder=5,color='C3'); ax[0].annotate('%s\n%.0f'%(lab_,y),(x,y),fontsize=8,
        textcoords='offset points',xytext=(4,8),ha='left')
ax[0].axhline(33,ls='--',c='grey',lw=.8); ax[0].axhline(67,ls='--',c='grey',lw=.8)
ax[0].set_ylim(0,100); ax[0].set_ylabel('Value Radar (0=RẺ nhất, 100=ĐẮT nhất)')
ax[0].set_title('VALUE RADAR — lăng kính ĐỊNH GIÁ độc lập, phân vị point-in-time (không nhìn trước) · đến %s'%v.time.max().date())
ax[0].legend(fontsize=8,loc='upper left'); ax[0].grid(alpha=.2)
ax[1].plot(v.time,v.p_pe,lw=1,label='P/E capped-10% (phân vị PIT)')
ax[1].plot(v.time,v.p_pb,lw=1,label='P/B capped-10% (phân vị PIT)')
ax[1].plot(v.time,v.p_sp,lw=1,label='spread EY − lãi suất huy động (đảo chiều)')
ax[1].set_ylabel('phân vị PIT'); ax[1].legend(fontsize=8,ncol=3); ax[1].grid(alpha=.2); ax[1].set_ylim(0,100)
w=d.dropna(subset=['vni_close'])
ax[2].semilogy(w.time,w.vni_close,lw=1,color='C4'); ax[2].set_ylabel('VNINDEX (log)'); ax[2].grid(alpha=.2)
plt.tight_layout(); plt.savefig('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/value_radar_20260730.png',dpi=115)
print('\nchart saved -> research/value_radar_20260730.png')
