"""Phase 1 — LOO THEO EPISODE cho bien the manh nhat @12,5% (V3). Cong G4 (PREREG §7-4).
Doi chieu voi THUOC DO NHIEU 0,3854pp: LOO chi co nghia neu bien thien LOO > nhieu."""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, math, os
import numpy as np, pandas as pd
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav
DATA='/home/trido/thanhdt/WorkingClaude/data/'; W=os.path.dirname(os.path.abspath(__file__)); NOISE=0.3854
def nav(tag):
    g=[p for p in sorted(glob.glob(DATA+f'*exp_{tag}_univpit*.csv')) if not p.endswith(('_borrowledger.csv','_leveraudit.csv'))]
    return load_nav(g[0]) if g else None
def cagr(s):
    y=(s.index[-1]-s.index[0]).days/365.25
    return 100*((s.iloc[-1]/s.iloc[0])**(1/y)-1)
base=nav('P1_BASE'); full=nav('P1_V3_R125')
b=cagr(base); dfull=cagr(full)-b
LAB={0:'2014-05-08 (E0, vay 25,9%NAV — dot lon nhat)',2:'2015-08-24 (E2)',3:'2016-01-18 (E3)',
     7:'2020-03-11 (E7)',8:'2020-07-27 (E8)'}
print("="*118); print(f"LOO THEO EPISODE — V3 @12,5% (dCAGR FULL {dfull:+.4f}pp so control)"); print("="*118)
print(f"{'bo episode':<44}{'dCAGR con lai':>16}{'dong gop episode':>20}{'% edge':>10}   G4")
rows=[]
for e,lab in LAB.items():
    s=nav(f'P1_V3LOO_e{e}')
    if s is None: print(f"  (thieu leg e{e})"); continue
    d=cagr(s)-b; contrib=dfull-d
    rows.append(dict(drop=e,dCAGR_rest=d,contrib=contrib,share=100*contrib/dfull if dfull else np.nan))
    print(f"{lab:<44}{d:>15.4f}pp{contrib:>19.4f}pp{100*contrib/dfull:>9.1f}%   {'PASS' if d>0 else 'FAIL'}")
R=pd.DataFrame(rows); R.to_csv(f'{W}/loo_episode_p1.csv',index=False)
if len(R):
    big=R.loc[R['contrib'].idxmax()]
    print("-"*118)
    print(f"Episode dong gop LON NHAT: E{int(big['drop'])} = {big['contrib']:+.4f}pp ({big['share']:.1f}% edge). "
          f"Bo no => dCAGR con {big['dCAGR_rest']:+.4f}pp -> G4 {'PASS' if big['dCAGR_rest']>0 else 'FAIL'}")
    print(f"Bien thien dong gop giua cac episode = {R['contrib'].max()-R['contrib'].min():.4f}pp "
          f"vs THUOC DO NHIEU {NOISE:.4f}pp -> "
          f"{'LON hon nhieu, LOO co nghia' if (R['contrib'].max()-R['contrib'].min())>NOISE else 'NHO hon/ngang nhieu => LOO KHONG PHAN GIAI duoc'}")
