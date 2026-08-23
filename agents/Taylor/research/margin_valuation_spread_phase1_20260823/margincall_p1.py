"""Phase 1 — mo hinh GOI KY QUY cap TAI KHOAN. Job Taylor_20260823_120317.
So THAT goi 1840 RocketX (DNSE API, Mafee_20260823_083327): maintenance 40%, liquidation 30%.
equity_ratio_t = NAV_t / (NAV_t + debt_t); debt gop theo NGAY tren CA HAI book roi moi max()
(bai hoc dinh chinh 2026-08-03: max(BAL)+max(LAG) dem 2 dinh o 2 ngay khac nhau = sai)."""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, os, json
import numpy as np, pandas as pd
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav
DATA='/home/trido/thanhdt/WorkingClaude/data/'; W=os.path.dirname(os.path.abspath(__file__))
VAR=json.load(open(f"{W}/variants.json")); VS=['V0','V1','V2','V3','V4','V5','V6','V7','V8']
MAINT, LIQ = 0.40, 0.30
print(f"Goi 1840 RocketX: maintenance {MAINT:.0%} · liquidation {LIQ:.0%} (DNSE API verified 2026-08-23)")
print("="*135)
print(f"{'leg':<14}{'f':>5}{'debt dinh cao':>18}{'ngay co no':>12}{'equity_ratio MIN':>19}{'ngay MIN':>13}"
      f"{'call@40%':>10}{'liq@30%':>9}{'bien an toan':>15}")
print("="*135)
rows=[]
for v in VS:
    for rk in ['R10','R125','R15']:
        tag=f'P1_{v}_{rk}'
        g=[p for p in sorted(glob.glob(DATA+f'*exp_{tag}_univpit*.csv')) if not p.endswith(('_borrowledger.csv','_leveraudit.csv'))]
        bl=sorted(glob.glob(DATA+f'*exp_{tag}_univpit*_borrowledger.csv'))
        if not g or not bl: continue
        nav=load_nav(g[0]); L=pd.read_csv(bl[0],parse_dates=['ymd'])
        # no thuc te moi book moi ngay = max(notional forced-borrow, tien mat am tu nhien)
        L['debt']=np.maximum(L['notional'],L['native_neg_cash'])
        d=L.groupby('ymd')['debt'].sum().sort_index()          # gop 2 book TRONG CUNG NGAY
        j=pd.concat([nav.rename('nav'),d.rename('debt')],axis=1)
        j['debt']=j['debt'].fillna(0.0); j=j.dropna(subset=['nav'])
        j['eq_ratio']=j['nav']/(j['nav']+j['debt'])
        act=j[j['debt']>0]
        mn=act['eq_ratio'].min() if len(act) else 1.0
        mnd=str(act['eq_ratio'].idxmin().date()) if len(act) else '-'
        ncall=int((act['eq_ratio']<MAINT).sum()) if len(act) else 0
        nliq=int((act['eq_ratio']<LIQ).sum()) if len(act) else 0
        rows.append(dict(leg=tag,V=v,rate=rk,f=VAR['f'][v],peak_debt_b=j['debt'].max()/1e9,
                         days=int((j['debt']>0).sum()),eq_min=mn,eq_min_date=mnd,call=ncall,liq=nliq))
        print(f"{tag:<14}{VAR['f'][v]:>5.2f}{j['debt'].max()/1e9:>15.3f}B{int((j['debt']>0).sum()):>12}"
              f"{mn:>18.4f}{mnd:>13}{ncall:>10}{nliq:>9}{(mn-MAINT)*100:>13.2f}pp")
R=pd.DataFrame(rows); R.to_csv(f'{W}/margincall_p1.csv',index=False)
print("="*135)
tot_call=int(R['call'].sum()); tot_liq=int(R['liq'].sum())
print(f"CONG G5 (PREREG §7-5: 0 margin call o maintenance 40% + lai vay 15%): "
      f"tong call = {tot_call}, tong liquidation = {tot_liq} -> {'PASS' if tot_call==0 else 'FAIL'}")
w=R.loc[R['eq_min'].idxmin()]
print(f"Chan mong nhat: {w.leg} equity_ratio min {w.eq_min:.4f} ngay {w.eq_min_date} "
      f"(cach nguong call {(w.eq_min-MAINT)*100:.2f}pp)")
