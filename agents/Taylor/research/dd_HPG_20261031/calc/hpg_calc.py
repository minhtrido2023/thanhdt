# NB: LDLK 9T26 = 1.987.970.143 VND = 1,99 TY (khong phai 1.988 ty) — da sua 31/10
# Taylor DD HPG 31/10/2026 — moi so dau vao doc tu anh BCTC (notes_bs.md), don vi ty dong
import math
# ---- Quarterly P&L (DTT, LNG, DTTC, lai vay, LDLK, LNTT, LNST, LNST me)
FY25=dict(dtt=156116.1,lng=24497.8,dttc=2081.8,laivay=3114.9,ldlk=0,lntt=18040.6,lnst=15514.9,me=15453.2,kh=8470.7)
M9_25=dict(dtt=109939.6,lng=18101.1,dttc=1644.5,laivay=1878.3,ldlk=0,lntt=13440.5,lnst=11626.6,me=11589.1,kh=5588.0)
H1_25=dict(dtt=73532.2,lng=12013.9,dttc=936.2,laivay=1066.1,ldlk=0,lntt=8812.1,lnst=7614.3,me=7600.8)
Q1_25=dict(dtt=37621.7,lng=5424.2,dttc=438.1,laivay=627.0,ldlk=0,lntt=3839.8,lnst=3349.8,me=3344.3)
Q3_25=dict(dtt=36407.4,lng=6087.3,dttc=711.9,laivay=812.2,ldlk=0,lntt=4628.3,lnst=4012.3,me=3988.3)
Q1_26=dict(dtt=52900.8,lng=8365.1,dttc=5938.3,laivay=1333.4,ldlk=0.3,lntt=10762.2,lnst=9055.9,me=8994.0)
H1_26=dict(dtt=108059.7,lng=18852.9,dttc=6555.0,laivay=2853.0,ldlk=1.99,lntt=17946.9,lnst=15480.4,me=15365.0,kh=5705.5)
Q3_26=dict(dtt=62214.2,lng=11922.5,dttc=1188.0,laivay=1774.0,ldlk=0,lntt=9108.7,lnst=8265.4,me=8217.3)
M9_26=dict(dtt=170273.9,lng=30775.3,dttc=7742.4,laivay=4627.1,ldlk=1.99,lntt=27055.6,lnst=23745.9,me=23582.4,kh=8768.6)
sub=lambda a,b:{k:round(a[k]-b[k],1) for k in a if k in b}
Q2_25=sub(H1_25,Q1_25); Q4_25=sub(FY25,M9_25); Q2_26=sub(H1_26,Q1_26)
# check H1+Q3 = 9T
chk=sub(M9_26,{k:H1_26[k]+Q3_26[k] for k in Q3_26}); print('check 9T26 - (H1+Q3):',chk)
chk=sub(M9_25,{k:H1_25[k]+Q3_25[k] for k in Q3_25}); print('check 9T25 - (H1+Q3):',chk)
Q={'Q1/25':Q1_25,'Q2/25':Q2_25,'Q3/25':Q3_25,'Q4/25':Q4_25,'Q1/26':Q1_26,'Q2/26':Q2_26,'Q3/26':Q3_26}
print('\nQuy | DTT | LNG | GM% | DTTC | lai vay | LDLK | LNTT | LNST | me')
for q,d in Q.items(): print(q,d['dtt'],d['lng'],round(100*d['lng']/d['dtt'],2),d['dttc'],d['laivay'],d['ldlk'],d['lntt'],d['lnst'],d['me'])
# ---- TTM
ttm_me=Q4_25['me']+M9_26['me']; ttm_lnst=Q4_25['lnst']+M9_26['lnst']
sh=8442.96452  # trieu cp
print('\nTTM LNST',round(ttm_lnst,1),'me',round(ttm_me,1),'EPS TTM',round(ttm_me/sh*1000))
# ---- one-offs 9T26 (truoc thue)
gain_disp=4929.1+(112.7-108.4)   # H1 lai thanh ly + Q3 net
ldlk=1.99
fx_unreal_q3=105.3-0.9
tax_gain=1030.2   # thue phan BDS segment H1 (proxy thue tren lai thoai von) [BN p55]
bds_ops_after_tax = (4293.0-(4929.1-1030.2)) + 204.9   # BDS van hanh H1 (phan du sau lai thoai von) + Q3
core9_lnst=M9_26['lnst']-(4929.1-tax_gain)-(112.7-108.4)*0.8-ldlk-bds_ops_after_tax
core9_me=core9_lnst-163.5
print('core 9T26 LNST (bo lai thoai von sau thue, LDLK, BDS van hanh):',round(core9_lnst,1),' me ~',round(core9_me,1), ' bds_ops',round(bds_ops_after_tax,1))
core_q3=Q3_26['lnst']-204.9-0.8*(fx_unreal_q3+4.3); print('core Q3/26 LNST ~',round(core_q3,1))
core_ttm_me=Q4_25['me']+core9_me; print('core TTM me ~',round(core_ttm_me,1),'EPS core',round(core_ttm_me/sh*1000))
# ---- Tax rate
print('ETR 9T26',round(100*(3409.2-99.4)/27055.6,1),'Q3/26',round(100*(822.8+20.5)/9108.7,1),'Q3/25',round(100*(632.8-16.7)/4628.3,1),'FY25',round(100*(2574.2-48.6)/18040.6,1))
# ---- Balance sheet
vay=78615.0+27121.7; tien=6852.9; htm=39273.9+2.3
nd=vay-tien-htm; print('\nVay',round(vay,1),'Tien+HTM',round(tien+htm,1),'No rong',round(nd,1),' (dau nam:',round(64695.0+27479.2-8325.1-19878.1-2266.9,1),')')
ebitda_ttm=(Q4_25['lntt']+Q4_25['laivay']+(FY25['kh']-M9_25['kh']))+(M9_26['lntt']+M9_26['laivay']+M9_26['kh'])
one_off_pre=4929.1+4.3+ldlk
print('EBITDA TTM',round(ebitda_ttm,1),'core (bo one-off',round(one_off_pre,1),')',round(ebitda_ttm-one_off_pre,1),' ND/EBITDA core',round(nd/(ebitda_ttm-one_off_pre),2))
q3_kh=M9_26['kh']-H1_26['kh']; print('Q3 KH',round(q3_kh,1),'EBITDA Q3 tu tinh',round(Q3_26['lntt']+Q3_26['laivay']+q3_kh,1),'(slide 14.307)')
eq_me=149568.4-772.9; bvps=eq_me/sh*1000; print('VCSH me',eq_me,'BVPS',round(bvps))
print('Vay/VCSH',round(vay/149568.4,2),' TS - (No+VCSH) =',round(283449.8-(133881.4+149568.4),1))
print('Delta TS 9T',round(283449.8-257899.2,1),' dNo',round(133881.4-126679.2,1),' dVCSH',round(149568.4-131220.0,1),' dVay',round(vay-(64695.0+27479.2),1))
cfo=20936.3; capex=14607.2; print('CFO 9T',cfo,'FCF (CFO-capex)',round(cfo-capex,1),'CFO/LNST',round(cfo/23745.9,2),'CFO/core',round(cfo/core9_lnst,2))
# lai suat ngam
dep_avg=(46129.1+ (9782.0+27473.9))/2  # 30/6: TDT 9.782,0 + HTM 27.473,9 (doc tu BN p9 so tom tat) 
print('Lai tien gui Q3 nam hoa / so du binh quan ~',round(704.3*4/dep_avg*100,2),'%')
# ---- Market
px=21000; mcap=px*sh/1000; print('\nGia 30/10',px,'Von hoa',round(mcap,1),'PE TTM',round(px/(ttm_me/sh*1000),2),'PE core TTM',round(px/(core_ttm_me/sh*1000),2),'PB',round(px/bvps,2),'PE Q3 core x4',round(mcap/(core_q3*4),2))
ev=mcap+nd+772.9-12664.1; print('EV (tru dau tu LK 12.664)',round(ev,1),'EV/EBITDA core TTM',round(ev/(ebitda_ttm-one_off_pre),2))
