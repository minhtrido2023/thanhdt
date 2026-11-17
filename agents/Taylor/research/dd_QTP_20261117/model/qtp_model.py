"""QTP DD r2 17/11/2026 - mo hinh dinh gia MU gia thi truong. So nguon: BCTC goc (src/), BQ ticker_financial.
r2: Q4/26 stub, WC thu hoi dung nam dung, bang vong doi, trong so kich ban, boi so 2 cach. v1 = qtp_model_v1.py"""
import statistics as st, math
SH=450.0
q={'23Q1':143.9,'23Q2':248.3,'23Q3':11.6,'23Q4':210.6,'24Q1':226.5,'24Q2':161.8,'24Q3':76.1,'24Q4':154.8,
   '25Q1':172.6,'25Q2':190.6,'25Q3':33.0,'25Q4':639.7,'26Q1':197.2,'26Q2':326.6,'26Q3':75.7}
FX_AT=(663.0-(69.04+2.23))*0.8
adj=dict(q); adj['25Q4']-=FX_AT
for k in adj:
    if k[:2] in('23','24'): adj[k]*=0.8/0.9
keys=list(q); ttm=[sum(adj[k] for k in keys[i-3:i+1]) for i in range(3,len(keys))]
NORM=st.median(ttm[-12:])
cash=82.18; htm=1774.11; interim=0.07*10000*SH/1000
netcash=cash+htm-interim
equity=5984.68; BVPS=equity/SH*1000
nwc=3091.52+729.32+16.66-1578.55
r=0.135
INT_AT=1541.3*0.05*0.8
NORM_OP=NORM-INT_AT
EPS_N=NORM/SH*1000; EPS_OP=NORM_OP/SH*1000
print('NORM',round(NORM,1),'NORM_OP',round(NORM_OP,1),'EPS',round(EPS_N),'EPS_OP',round(EPS_OP),'netcash',round(netcash,1),round(netcash/SH*1000),'d/cp | NWC',round(nwc))
DA_Q=104.53; DA_now=4*DA_Q
REM=1803.4   # TSCD huu hinh con lai 30/9/26 (r1 dung 1805,1 = tong TSCD)
# Q4/26 stub (UOC LUONG): LNST hoat dong Q4 = 160 - lai tien gui ~15 ; + KH 104,5 - capex 4. Q4/24 154,8 ; Q4/25 bo FX 166,3
Q4_NPAT=145.0; Q4_FLOW=Q4_NPAT+DA_Q-4.0
print('Q4/26 stub',round(Q4_FLOW,1),'ty =',round(Q4_FLOW/SH*1000),'d/cp (uoc luong; skeptic ~600)')
YEARS=list(range(2027,2055))
def da_sched():
    out={};left=REM-DA_Q
    for y in YEARS:
        d=max(0,min(left,DA_now*(0.85 if y>2028 else 1.0))); out[y]=d; left-=d
    return out
DA=da_sched()
def capfn(stop):
    if stop=='40y': return lambda y: 1.0 if y<=2051 else (0.5 if y<=2054 else 0.0)  # TM1-2 COD 2011->2051; TM3-4 COD 2014->2054; GIA DINH gia han thue dat
    return lambda y: 1.0 if y<=stop else 0.0
def val(kind,stop=2047,rr=r,close=0.0,gnom=0.0,q4=True):
    cap=capfn(stop)
    if kind=='bad':
        c0=capfn(min(2040,stop) if stop!='40y' else 2040); cap=c0
    pv=Q4_FLOW/(1+rr)**0.125 if q4 else 0.0
    for y in YEARS:
        c=cap(y); cp=cap(y-1) if y>2027 else 1.0
        n=NORM_OP*(1+gnom)**(y-2026)
        if kind=='base': npat=n
        elif kind=='good': npat=n+(DA_now-DA[y])*0.8
        else: npat=(n*0.85 if y<=2027 else n*0.5)
        pv+=c*(npat+DA[y]-15)/(1+rr)**(y-2027+0.5)
        pv+=(nwc-close)*(cp-c)/(1+rr)**(y-2027)   # thu hoi VLD (tru chi phi dong cua) cuoi nam y-1 = nam dung
    return (pv+netcash)/SH*1000
LIQ=0.10
WSETS={'chon 0,25/0,65/0,10':(0.25,0.65,0.10),'0,25/0,75/0':(0.25,0.75,0.0),'0,5/0,5/0':(0.5,0.5,0.0),'v1 0,25/0,5/0,25':(0.25,0.5,0.25)}
def w(ws,stop=2047,**k):
    b,m,g=ws; return b*val('bad',stop,**k)+m*val('base',stop,**k)+g*val('good',stop,**k)
vb,vm,vg=val('bad'),val('base'),val('good')
print('Kich ban (dung 2047; xau dung 2040): xau',round(vb),'co so',round(vm),'tot',round(vg))
print('v1 xau (WC cuoi 2047, sai) = 10614 ; r2 xau (WC dung 2040) =',round(vb))
CH=WSETS['chon 0,25/0,65/0,10']
for n,ws in WSETS.items():
    x=w(ws); print(f' trong so {n}: truoc CK {round(x)} | sau CK10% {round(x*(1-LIQ))} | gia/tam sau CK {10300/(x*(1-LIQ)):.3f}')
print('Khong co Q4/26 stub (chon):',round(w(CH,q4=False)),'-> voi Q4 stub',round(w(CH)),'delta',round(w(CH)-w(CH,q4=False)))
print('\nBANG DO NHAY VONG DOI (chon trong so; gia 10300):')
print('stop | co_so_truoc | co_so_sau | chon_truoc | chon_sau | gia/tam_chon_sau | gia/co_so_sau')
for s in (2030,2035,2040,2047,'40y'):
    m=val('base',s); x=w(CH,s)
    print(f' {s} | {round(m)} | {round(m*(1-LIQ))} | {round(x)} | {round(x*(1-LIQ))} | {10300/(x*(1-LIQ)):.3f} | {10300/(m*(1-LIQ)):.3f}')
print('\nChi phi dong cua/hoan nguyen bai tro (UOC LUONG, khong trong mo hinh): tru tai nam dung, do nhay chon, dung 2047')
for c in (200,500,1000): print(f' close {c} ty -> {round(w(CH,close=c))} (delta {round(w(CH,close=c)-w(CH))})')
print('LNST danh nghia +3%/nam (UOC LUONG, ranh gioi tren cua lam phang):',round(w(CH,gnom=0.03)),'delta',round(w(CH,gnom=0.03)-w(CH)))
print('\nr +-:')
c0=w(CH)
for bp in(-100,-50,50,100): x=w(CH,rr=r+bp/1e4); print(f' r{bp:+}bp -> {round(x)} ({(x/c0-1)*100:+.1f}%)')
print('\nBOI SO (NORM EPS %d; EPS_op %d; tien rong %d d/cp)'%(round(EPS_N),round(EPS_OP),round(netcash/SH*1000)))
print(' PE | A: PE*EPS_chuan(gom lai, KHONG cong tien rong) | B: PE*EPS_op + tien rong')
for pe in (5,6,6.6,7,7.95,8,8.5,9): print(f' {pe} | {round(pe*EPS_N)} | {round(pe*EPS_OP+netcash/SH*1000)}')
pe_all=dict(PGV=4.35,NT2=4.68,NBP=5.07,POW=5.63,SJD=6.03,BTP=7.57,TBC=7.60,SBH=8.01,QPH=8.34,HND=8.51,PPC=8.94,DRL=9.04,TMP=9.09,VPD=9.27,HNA=9.77,GEG=10.49,SHP=10.55,REE=10.99,VSH=11.36,NED=11.42,CHP=12.12,KHP=13.37)
print(' median PE 22 peer (BQ 16/11, TTM tho):',round(st.median(pe_all.values()),2))
core=[pe_all[k] for k in('PPC','HND','NBP','POW','NT2','BTP','QPH','VSH')]; print(' median 8 peer tr1:',round(st.median(core),2))
th=[pe_all[k] for k in('PGV','NT2','NBP','POW','SJD','BTP','HND','PPC')]; print(' median 8 nhiet dien/thuy (PGV,NT2,NBP,POW,SJD,BTP,HND,PPC):',round(st.median(th),2))
for pb in(0.6,0.7): print(f' PB {pb} x BVPS =',round(pb*BVPS))
