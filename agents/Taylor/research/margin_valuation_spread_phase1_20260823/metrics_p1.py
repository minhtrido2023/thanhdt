"""Phase 1 — bang chi tieu 9 bien the x 3 lai vay + DSR + PBO(CSCV) + LOO theo EPISODE + margin call.
Job Taylor_20260823_120317. RESEARCH-ONLY. Cong GO/NO-GO khoa truoc o PREREG.md §7."""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, math, json, os
import numpy as np, pandas as pd
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav, moments, expected_max_sr, dsr, cscv_pbo
DATA='/home/trido/thanhdt/WorkingClaude/data/'
W=os.path.dirname(os.path.abspath(__file__)); ANN=252.0
VAR=json.load(open(f"{W}/variants.json"))
RATES={'R10':'10%','R125':'12,5% (THAT, goi 1840)','R15':'15% (stress)'}
VS=['V0','V1','V2','V3','V4','V5','V6','V7','V8']

def paths(tag):
    return [p for p in sorted(glob.glob(DATA+f'*exp_{tag}_univpit*.csv'))
            if not p.endswith(('_borrowledger.csv','_leveraudit.csv'))]
def metr(s):
    lp=np.log(s.values); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; r=np.diff(lp)
    sh=r.mean()/r.std(ddof=1)*math.sqrt(ANN); dd=s/s.cummax()-1; mdd=dd.min()
    return dict(CAGR=100*cagr,Sharpe=sh,MaxDD=100*mdd,Calmar=cagr/abs(mdd),
                FinalNAV=s.iloc[-1]/1e9,MDD_date=str(dd.idxmin().date()))
def seg(s,a,b):
    x=s[(s.index>=a)&(s.index<=b)]
    if len(x)<20: return np.nan
    y=(x.index[-1]-x.index[0]).days/365.25
    return 100*((x.iloc[-1]/x.iloc[0])**(1/y)-1)

navs={}
for t in ['P1_BASE','P1_INERT']+[f'P1_{v}_{r}' for v in VS for r in RATES]:
    g=paths(t)
    if g: navs[t]=load_nav(g[0])
missing=[t for t in [f'P1_{v}_{r}' for v in VS for r in RATES] if t not in navs]
print(f"legs loaded: {len(navs)} | THIEU: {missing if missing else 'khong'}")

base=navs['P1_BASE']; b=metr(base)
bIS=seg(base,'2014-01-01','2019-12-31'); bOOS=seg(base,'2020-01-01','2026-12-31')
print('\n'+'='*150)
print('CONTROL f=1,0 vs pin R3 (28,8627 / -17,7851 / 1,6229 / 1.178,0099B / IS 27,0925 / OOS 30,4786):')
print(f'  CAGR {b["CAGR"]:.4f}%  MaxDD {b["MaxDD"]:.4f}%  Calmar {b["Calmar"]:.4f}  '
      f'FinalNAV {b["FinalNAV"]:.4f}B  IS {bIS:.4f}%  OOS {bOOS:.4f}%')
ok=(abs(b['CAGR']-28.8627)<0.02 and abs(b['MaxDD']+17.7851)<0.02 and abs(b['FinalNAV']-1178.0099)<0.5)
print(f'  -> {"TAI LAP DUNG PIN" if ok else "*** LECH PIN — DUNG LAI ***"}')
if 'P1_INERT' in navs:
    e=paths('E125_f13')
    if e:
        o=load_nav(e[0]); j=pd.concat([o.rename('o'),navs['P1_INERT'].rename('n')],axis=1).dropna()
        print(f'  INERT vs E125_f13 (2026-08-03): max |diff| = {(j.o-j.n).abs().max():.1f} VND tren {len(j)} phien '
              f'-> {"HUNK A/B BYTE-INERT" if (j.o-j.n).abs().max()==0 else "*** KHONG INERT ***"}')

rows=[]
for v in VS:
    for rk in RATES:
        t=f'P1_{v}_{rk}'
        if t not in navs: continue
        a=metr(navs[t]); aIS=seg(navs[t],'2014-01-01','2019-12-31'); aOOS=seg(navs[t],'2020-01-01','2026-12-31')
        rows.append(dict(V=v,rate=rk,f=VAR['f'][v],n_arm=len(VAR['arm'][v]),
            CAGR=a['CAGR'],dCAGR=a['CAGR']-b['CAGR'],Sharpe=a['Sharpe'],
            MaxDD=a['MaxDD'],dMaxDD=a['MaxDD']-b['MaxDD'],Calmar=a['Calmar'],
            IS=aIS,dIS=aIS-bIS,OOS=aOOS,dOOS=aOOS-bOOS,FinalNAV=a['FinalNAV']))
T=pd.DataFrame(rows); T.to_csv(f'{W}/metrics_p1.csv',index=False)
print('\n'+'='*150); print('BANG CHI TIEU — delta so voi BASE f=1,0 (dMaxDD AM = rui ro XAU hon)')
print('='*150)
for rk,lbl in RATES.items():
    sub=T[T.rate==rk]
    if not len(sub): continue
    print(f'\n--- lai vay {lbl} ---')
    print(sub[['V','f','n_arm','CAGR','dCAGR','Sharpe','MaxDD','dMaxDD','Calmar','IS','dIS','OOS','dOOS','FinalNAV']].round(4).to_string(index=False))

print('\n'+'='*150); print('V7 vs V0 — CAU HOI H1 (gia tri GIA TANG cua spread so voi dd52 dang chay)')
print('='*150)
for rk,lbl in RATES.items():
    a=T[(T.V=='V7')&(T.rate==rk)]; c=T[(T.V=='V0')&(T.rate==rk)]
    if not len(a) or not len(c): continue
    a=a.iloc[0]; c=c.iloc[0]
    print(f'  {lbl:<28} dCAGR(V7-V0) {a.CAGR-c.CAGR:+.4f}pp | dIS {a.IS-c.IS:+.4f}pp | dOOS {a.OOS-c.OOS:+.4f}pp | '
          f'dMaxDD {a.MaxDD-c.MaxDD:+.4f}pp  [G1 {"PASS" if (a.IS>c.IS and a.OOS>c.OOS and a.OOS-c.OOS>0) else "FAIL"}]')
print('\nV8 vs V0 (PREREG §4.1 du bao: TRUNG KHIT vi T2/T3 khong co su kien nao):')
for rk in RATES:
    a=navs.get(f'P1_V8_{rk}'); c=navs.get(f'P1_V0_{rk}')
    if a is None or c is None: continue
    j=pd.concat([a.rename('a'),c.rename('c')],axis=1).dropna()
    print(f'  {rk:<5} max |V8-V0| = {(j.a-j.c).abs().max():.1f} VND tren {len(j)} phien')

print('\n'+'='*150); print('DSR tren chuoi excess (log-return bien the tru control), N=8 trial (PREREG §7)')
print('='*150)
for v in VS:
    for rk in ['R125']:
        t=f'P1_{v}_{rk}'
        if t not in navs: continue
        idx=navs[t].index.intersection(base.index)
        r=np.diff(np.log(navs[t].reindex(idx).values))-np.diff(np.log(base.reindex(idx).values))
        if r.std()==0:
            print(f'  {v:<3} @12,5%  chuoi excess = 0 (leg trung control) -> DSR khong dinh nghia'); continue
        srh,g3,g4=moments(r)
        line=f'  {v:<3} @12,5%  SR/obs {srh:+.4f}'
        for N in (8,25,180):
            sr0=expected_max_sr(1.0/(len(r)-1),N); d,_=dsr(srh,sr0,g3,g4,len(r))
            line+=f'   N={N:<3d}: DSR {d:.4f}'+('' if d>=0.95 else ' <-RED')
        print(line)

print('\n'+'='*150); print('PBO / CSCV — ho 8 trial (V1..V8) + control, @12,5% (PREREG: N_trials=8 => chay PBO)')
print('='*150)
tags=['P1_BASE']+[f'P1_{v}_R125' for v in VS[1:] if f'P1_{v}_R125' in navs]
if len(tags)>=3:
    idx=navs[tags[0]].index
    for t in tags: idx=idx.intersection(navs[t].index)
    M=np.column_stack([np.diff(np.log(navs[t].reindex(idx).values)) for t in tags])
    for S in (8,12,16):
        pbo,lg,ncomb,ncfg,T2=cscv_pbo(M,S=S)
        print(f'  {len(tags)} cau hinh  S={S:2d}  combos={ncomb}  PBO={pbo:.3f}  median logit={np.median(lg):+.3f}'
              +('  <-- >=0,5 FAIL' if pbo>=0.5 else '  PASS'))
print('\nDONE')
