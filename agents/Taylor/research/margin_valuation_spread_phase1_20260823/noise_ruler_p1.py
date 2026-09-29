"""Phase 1 — THUOC DO NHIEU: lai vay la tham so chi lam GIAM CAGR (don dieu, theo dinh nghia).
Moi vi pham don dieu do duoc = bien do NHIEU PATH cua chinh harness, do bang chinh don vi (pp CAGR)
voi dai luong dang muon do. Job Taylor_20260823_120317."""
import warnings; warnings.filterwarnings('ignore')
import sys, os, glob, math, json
import numpy as np, pandas as pd
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav, moments, expected_max_sr, dsr
W=os.path.dirname(os.path.abspath(__file__))
T=pd.read_csv(f"{W}/metrics_p1.csv")
P=T.pivot_table(index='V',columns='rate',values='dCAGR')
P=P[['R10','R125','R15']]
print("="*118)
print("THUOC DO NHIEU — dCAGR (pp) theo lai vay. Chinh sach CO DINH => tang lai vay chi duoc lam GIAM.")
print("="*118)
print(f"{'V':<4}{'@10%':>10}{'@12,5%':>11}{'@15%':>10}{'hieu ung CHI PHI (10->15)':>28}{'vi pham don dieu':>20}")
viol={}
for v in P.index:
    a,b,c=P.loc[v,'R10'],P.loc[v,'R125'],P.loc[v,'R15']
    vio=max(0.0, b-a)+max(0.0, c-b)
    viol[v]=vio
    print(f"{v:<4}{a:>10.4f}{b:>11.4f}{c:>10.4f}{a-c:>26.4f}pp{vio:>18.4f}pp"+("   <-- KHONG THE VE KINH TE" if vio>0.01 else ""))
NOISE=max(viol.values())
print("-"*118)
print(f"Bien do nhieu path do duoc (vi pham don dieu lon nhat) = {NOISE:.4f}pp CAGR")
# do doc lap thu 2: dong gop BIEN cua CUNG MOT su kien (E6) o 2 muc lai vay
d=lambda v,r: float(T[(T.V==v)&(T.rate==r)]['dCAGR'].iloc[0])
m10=d('V4','R10')-d('V3','R10'); m125=d('V4','R125')-d('V3','R125'); m15=d('V4','R15')-d('V3','R15')
print(f"Kiem chung doc lap — dong gop BIEN cua DUNG 1 su kien E6 (2020-02-03), = V4 - V3:")
print(f"   @10% {m10:+.4f}pp | @12,5% {m125:+.4f}pp | @15% {m15:+.4f}pp  => bien do {max(m10,m125,m15)-min(m10,m125,m15):.4f}pp, DOI DAU")
h1=abs(d('V7','R125')-d('V0','R125'))
print(f"\nDai luong H1 muon do (|V7 - V0| @12,5%) = {h1:.4f}pp")
print(f"=> ty le TIN HIEU/NHIEU = {h1/NOISE:.3f}  ({NOISE/h1:.0f}x nho hon nhieu)")
print("   ==> tang engine KHONG PHAN GIAI duoc hieu ung co do lon nay. Day la gioi han CONG CU,")
print("       khong phai bang chung 'hieu ung bang 0'.")

print("\n"+"="*118)
print("DSR tren CHUOI CUA CHINH LEG (cach D-step 2026-08-03 bao DSR 1,0000) — de doi chieu dinh nghia")
print("="*118)
DATA='/home/trido/thanhdt/WorkingClaude/data/'
for v in ['V0','V3','V4','V7']:
    g=[p for p in sorted(glob.glob(DATA+f'*exp_P1_{v}_R125_univpit*.csv')) if not p.endswith(('_borrowledger.csv','_leveraudit.csv'))]
    if not g: continue
    s=load_nav(g[0]); r=np.diff(np.log(s.values)); srh,g3,g4=moments(r)
    line=f"  {v:<3} SR/obs {srh:.4f}"
    for N in (8,25,180):
        sr0=expected_max_sr(1.0/(len(r)-1),N); dd,_=dsr(srh,sr0,g3,g4,len(r)); line+=f"  N={N:<3d}: DSR {dd:.4f}"
    print(line)
print("  -> DSR tren chuoi leg gan 1,0 cho MOI leg (ke ca control) vi no do 'danh muc V2.4 co tot khong',")
print("     KHONG do 'lop don bay co them gi khong'. Chuoi EXCESS moi la thu do dung cau hoi — va tren do")
print("     MOI leg deu RED, KE CA V0 dang LIVE. Cong G3 vi vay KHONG phan biet duoc bien the.")
