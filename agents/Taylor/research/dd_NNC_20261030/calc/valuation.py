"""DD NNC 30/10/2026 — dinh gia. Moi so BCTC doc tu anh trang (BCTC rieng Q3/2026 duyet 19/10/2026,
BCTC 2025 kiem toan AASCs 26/02/2026). Gia dinh tu dat = (uoc luong)."""
import numpy as np
SH=21.92e6; PX=47100; MCAP=SH*PX/1e9
# --- Bang can doi 30/09/2026 (ty dong) [BCTC Q3 tr.1-3, V1/V2/V11/V19a]
cash=25.474; htm=322.440; tradsec=0.130
debt_st=5.000; debt_lt=69.890
prov_truythu=22.373          # V19a: CQ Nui Nho 15.579 + thue dat 2019 5.952 + CQ Mui Tau 0.842
bonus_fund=16.776; div_pay=5.888; prov_lt_env=4.497
net_cash_raw=cash+htm+tradsec-debt_st-debt_lt
net_cash_adj=net_cash_raw-prov_truythu-bonus_fund-div_pay-prov_lt_env
# --- Dau tu: MVC 10.3tr cp, NHC 710.242 cp [V11]; gia BQ tav2_bq.ticker 30/10 (MVC 14.100; NHC 18.600 phien cuoi 16/09)
mvc_mkt=10.3e6*14100/1e9; nhc_mkt=710242*18600/1e9
# vong tron: MVC so huu 9.659.170 cp NNC (V22: 96,5917 ty / 10.000) ; MVC OShares 100tr (BQ, chua doi chieu dieu le)
mvc_nnc_val=9.659170e6*PX/1e9; mvc_cap=100e6*14100/1e9
mvc_excirc=mvc_mkt*(1-mvc_nnc_val/mvc_cap)
cip_tamlap=83.506            # V10a: 4.030 + 79.475
print(f'MCAP {MCAP:.1f} | net cash tho {net_cash_raw:.1f} ({net_cash_raw*1e9/SH:,.0f} d/cp) | net cash sau nghia vu {net_cash_adj:.1f} ({net_cash_adj*1e9/SH:,.0f} d/cp)')
print(f'MVC mkt {mvc_mkt:.1f}  MVC ex-vong-tron {mvc_excirc:.1f} (NNC chiem {mvc_nnc_val/mvc_cap:.0%} von hoa MVC) | NHC {nhc_mkt:.1f}')
inv=mvc_excirc+nhc_mkt
# --- LN: TTM = 9T26 + (FY25-9T25)
q4_25=dict(rev=390.948-261.885, gp=193.014-128.343, sga=(3.925+16.142)-(3.007+11.014), np=147.832-93.953)
t9=dict(rev=402.196, gp=218.515, sga=1.481+11.386, np=160.075, other=-19.287, fin=15.603-1.827)
ttm_np=t9['np']+q4_25['np']; ttm_ebit=(t9['gp']-t9['sga'])+(q4_25['gp']-q4_25['sga'])
da_ttm=4*(5.511+3.476)   # Q3 KH + phan bo tra truoc x4 (uoc luong)
ttm_ebitda=ttm_ebit+da_ttm
print(f'Q4/25 rev {q4_25["rev"]:.1f} np {q4_25["np"]:.1f} | TTM NP {ttm_np:.1f} EPS {ttm_np*1e9/SH:,.0f} | TTM core EBIT {ttm_ebit:.1f} EBITDA {ttm_ebitda:.1f} (uoc luong DA)')
ev_op=MCAP-net_cash_adj-inv
print(f'EV hoat dong (tru net cash sau nghia vu, MVC ex-vong-tron, NHC) {ev_op:.1f}')
print(f'PE TTM {MCAP/ttm_np:.2f} | ex-cash PE core (EBIT*0.8) {ev_op/(ttm_ebit*0.8):.2f} | EV/EBITDA TTM {ev_op/ttm_ebitda:.2f}')
BV=655.732; print(f'PB {MCAP/BV:.2f} (BVPS {BV*1e9/SH:,.0f})')
ann={2021:38.4,2022:39.3,2023:36.6,2024:62.6,2025:147.8}   # BQ NP_P0 cong 4 quy; 2024/2025 khop BCTC
for lab,v in [('trung vi 2021-25',np.median(list(ann.values()))),('TB 2021-TTM',np.mean(list(ann.values())+[ttm_np])),('2025',147.8)]:
    print(f'PE ex-cash tren LN {lab} {v:.1f}: {ev_op/v:.1f}x')
# --- DCF HUU HAN 2027-2043 (17 nam, het GP Mui Tau). Q4/26 cong rieng.
# chi phi: bien doi 110k/m3 + co dinh 70 ty/nam (hieu chinh Q3/26: 0,35tr m3 *110 + 17,5 = 56 ~ GV thanh pham 56,07) (uoc luong)
VAR=110; FIX=70; SGA=20; TAX=0.2; INFL=0.03
def path(v27,v28,p27,p28,ylate=None,plate=None):
    yrs=list(range(2027,2044)); out=[]
    for y in yrs:
        v=v27 if y==2027 else (v28 if (y<=2030 or ylate is None) else ylate)
        p=p27 if y==2027 else (p28 if (y<=2030 or plate is None) else plate)
        f=(1+INFL)**(y-2026)
        ebit=v*(p-VAR*f)-FIX*f-SGA*f       # v tr m3, p nghin d/m3 -> ty dong
        out.append((y,max(ebit,0)*(1-TAX)))   # capex duy tri ~ KH (uoc luong)
    return out
SC={ # xac suat chu quan (uoc luong)
 'tot':     (0.20, path(1.40,1.40,420,400,1.40,420)),
 'co_so':   (0.45, path(1.40,1.10,380,300,1.20,320)),
 'xau':     (0.25, path(1.30,0.80,330,250,0.80,250)),
 'rat_xau': (0.10, path(0.80,0.80,230,210,0.80,210)),
}
q4_26=60.0   # LN Q4/26 (uoc luong, ~ trung binh Q1-Q3/26 = 53)
def pv(cf,r): return sum(c/(1+r)**(y-2026.83+0.5) for y,c in cf)   # giua nam, tu 30/10/2026
for r in (0.11,0.13,0.15):
    vals={}
    for k,(w,cf) in SC.items():
        eq=pv(cf,r)+q4_26+net_cash_adj+inv+cip_tamlap*(0 if k in('xau','rat_xau') else 1)
        vals[k]=eq*1e9/SH
    ev=sum(SC[k][0]*vals[k] for k in SC)
    print(f'r={r:.0%}: '+' '.join(f'{k} {v:,.0f}' for k,v in vals.items())+f' | ky vong {ev:,.0f} ({ev/PX-1:+.0%})')
print('NOPAT 2027/2028 theo kich ban:',{k:(round(cf[0][1],1),round(cf[1][1],1)) for k,(w,cf) in SC.items()})
# do nhay gia x san luong (r=13%, ap tu 2028; 2027 = co so)
print('Do nhay (gia/m3 2028+ x san luong 2028+), d/cp, r=13%:')
for v in (0.8,1.0,1.2,1.4):
    row=[]
    for p in (220,260,300,340,380,420):
        cf=path(1.40,v,380,p,v,p); eq=pv(cf,0.13)+q4_26+net_cash_adj+inv+cip_tamlap
        row.append(f'{eq*1e9/SH:>7,.0f}')
    print(f' V={v:.1f}: '+' '.join(row))
