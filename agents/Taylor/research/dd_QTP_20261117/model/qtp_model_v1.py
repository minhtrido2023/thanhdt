"""QTP DD 17/11/2026 - mo hinh dinh gia MU gia thi truong. So nguon: BCTC goc (src/), BQ ticker_financial."""
import statistics as st
SH=450.0  # trieu cp
# NPAT quy (ty) - BQ NP_P0, khop BCTC goc: FY25 = 1035,9; H1/26 523,8; Q3/26 75,68
q={'23Q1':143.9,'23Q2':248.3,'23Q3':11.6,'23Q4':210.6,'24Q1':226.5,'24Q2':161.8,'24Q3':76.1,'24Q4':154.8,
   '25Q1':172.6,'25Q2':190.6,'25Q3':33.0,'25Q4':639.7,'26Q1':197.2,'26Q2':326.6,'26Q3':75.7}
FX_ONEOFF_AT=(663.0-(69.04+2.23))*0.8   # DT chenh lech ty gia 663 (giai trinh FY25) - lo CLTG 71,3 (TM24) sau thue 20%
adj=dict(q); adj['25Q4']-=FX_ONEOFF_AT     # gan vao Q4/25 (uoc luong: Q4/25 639,7 vs Q4/24 154,8)
TAX_ADJ=0.8/0.9   # 2023-24 thue suat hieu dung ~10% (2024: 69,2/688,5=10,1%) -> quy ve 20% (uoc luong cho 2023)
for k in adj:
    if k[:2] in('23','24'): adj[k]*=TAX_ADJ
keys=list(q); ttm=[sum(adj[k] for k in keys[i-3:i+1]) for i in range(3,len(keys))]
ttm12=ttm[-12:]; NORM=st.median(ttm12)
print('FX one-off sau thue',round(FX_ONEOFF_AT,1)); print('TTM adj (12 diem):',[round(x) for x in ttm12])
print('Trung vi TTM 3 nam (adj)',round(NORM,1),'| TTM Q3/26 adj',round(ttm[-1],1),'| TTM tho',round(sum(q[k] for k in keys[-4:]),1))
# Bang can doi 30/09/2026 (BCTC goc)
cash=82.18; htm=1774.11; debt=0.0; interim_div=0.07*10000*SH/1000  # 700d x 450tr = 315 ty, GDKHQ truoc 06/11 -> tru
netcash=cash+htm-debt-interim_div
equity=5984.68; BVPS=equity/SH*1000
AR=3091.52; inv=729.32; liab=1578.55
nwc=AR+inv+16.66-(liab-0)   # NWC xap xi (tai san ngan han ngoai tien - toan bo no, khong co vay)
print('Net cash sau tam ung',round(netcash,1),'ty =',round(netcash/SH*1000),'d/cp | BVPS',round(BVPS),'| NWC',round(nwc))
r=0.135
INT_AT=1541.3*0.05*0.8  # lai tien gui sau thue tren net cash (uoc luong lai 5%/nam) - tru khoi LN khi da cong net cash
NORM_OP=NORM-INT_AT
print('NORM_OP (bo lai tien gui)',round(NORM_OP,1))
def pv(flows,r): return sum(f/(1+r)**(i+0.5) for i,f in enumerate(flows))
YEARS=list(range(2027,2048))  # dat thue toi 15/3/2047 (TM20 FY25); 40 nam QN2 ~2053 (uoc luong)
DA_now=4*104.53  # Q3/26 run-rate
def scen(name,npat_path,da_path,capex=15,end_wc=True,rr=r):
    fl=[npat_path(y)+da_path(y)-capex for y in YEARS]
    v=pv(fl,rr)+(nwc/(1+rr)**len(YEARS) if end_wc else 0)+netcash
    return v/SH*1000
# D&A: net PPE 1.805 ty, chay het ~2031 (uoc luong: 418/nam giam dan)
rem=1805.1
def da_sched():
    out={};left=rem
    for y in YEARS:
        d=min(left,DA_now*(0.85 if y>2028 else 1.0)); out[y]=d; left-=d
    return out
DA=da_sched()
base=lambda rr=r: scen('base',lambda y:NORM_OP,lambda y:DA[y],rr=rr)        # PPA co dinh giam dung bang KH het -> NPAT phang, cash = NPAT + KH con lai
good=lambda rr=r: scen('good',lambda y:NORM_OP+(DA_now-DA[y])*0.8,lambda y:DA[y],rr=rr)  # PPA KHONG giam sau het KH -> giu EBITDA
bad =lambda rr=r: scen('bad',lambda y:(NORM_OP*0.85 if y<=2027 else NORM_OP*0.5) if y<=2040 else 0,lambda y:DA[y] if y<=2040 else 0,rr=rr) # dung 2040, PPA ep + carbon 2028
W={'bad':0.25,'base':0.5,'good':0.25}
vb,vg,vx=base(),good(),bad(); wv=W['bad']*vx+W['base']*vb+W['good']*vg
print('Kich ban d/cp: xau',round(vx),'co so',round(vb),'tot',round(vg),'| trong so',round(wv))
for bp in(-100,-50,50,100):
    rr=r+bp/1e4; w=W['bad']*bad(rr)+W['base']*base(rr)+W['good']*good(rr); print(f' r{bp:+}bp -> {round(w)} ({(w/wv-1)*100:+.1f}%)')
for liq in(0.05,0.10,0.15): print(f' sau CK thanh khoan {int(liq*100)}%:',round(wv*(1-liq)))
# V_ngan / V_dai
ROE=NORM/equity; g=0.0; reinv=min(max(g/ROE,0),0.8)
V_ngan=NORM*(1-reinv)/(r-g)/SH*1000 + 0  # framework: khong cong net cash rieng (LN da gom lai tien gui)
V_dai=vb
import math; D=abs(math.log(V_ngan/V_dai))
print('ROE norm',round(ROE,3),'V_ngan',round(V_ngan),'V_dai(base DCF)',round(V_dai),'D',round(D,3),'ln2',round(math.log(2),3))
CFO3=(301+358+83+528+231+46+377+746+537+9+182+516)/3  # BQ CF_OA quy Q4/23..Q3/26
C4=(CFO3-min(15,DA_now)); print('CFO3',round(CFO3),'C4/nam',round(C4),'V_C4 (vinh vien, chi theo doi)',round(C4/r/SH*1000),'| V_C4 huu han 2047',round((pv([C4]*len(YEARS),r))/SH*1000))
# Boi so (mu gia: chi tinh gia tri ham y tu boi so peer)
for pe in(6,7,8.5): print(f' PE {pe} x EPS norm {round(NORM/SH*1000)} =',round(pe*NORM/SH*1000),'| PE x EPS_op + net cash =',round(pe*NORM_OP/SH*1000+netcash/SH*1000))
for pb in(0.6,0.7): print(f' PB {pb} x BVPS =',round(pb*BVPS))
