"""Vong 2 — do nhay bo sung (KHONG doi mo hinh valuation.py, KHONG doi tam). Chay: python3 valuation_v2.py > valuation_v2_out.txt
(1) tre 1 nam mo moi o kich ban co so; (2) CCN 500 ty thu hoi 70%/50%; (3) nguong no rong 2028 theo cam ket von; (4) P/E TTM ex hoan nhap Q4/25."""
import valuation as M
SCN=M.SCN
def mid(**kw): return (sum(M.W[k]*M.value(k,'flat',**kw) for k in SCN)+sum(M.W[k]*M.value(k,'real',**kw) for k in SCN))/2
base=mid(); print(f'TAM goc (khong doi): {base:,.0f}')
# (1) tre 1 nam cho co_so (xau da tre 1, rat_xau 2, tot 0)
old=dict(M.DELAY); M.DELAY['co_so']=1; x=mid(); print(f'(1) mo moi co_so tre 1 nam (van hanh 2029): tam {x:,.0f} ({x-base:+,.0f}); co_so phang {M.value("co_so","flat"):,.0f} / thuc {M.value("co_so","real"):,.0f}')
M.DELAY['tot']=1; y=mid(); print(f'(1b) CA tot cung tre 1 nam: tam {y:,.0f} ({y-base:+,.0f})')
M.DELAY.update(old)
# (2) CCN 500 ty: chi 2027-28 (50/50), thu hoi x% (ngay thu hoi = nua sau 2030, chiet khau r13%) -> NPV am; don gian: -500*(1-x) hien gia ~ -500*(1-x)*0.85
for rec in (0.7,0.5,0.0):
    npv=-500*(1-rec)*0.85; print(f'(2) CCN 500 ty thu hoi {rec:.0%}: {npv:,.0f} ty = {npv*1e9/M.SH_M:+,.0f} d/cp (uoc luong: he so 0,85 chiet khau thanh toan)')
# (3) no rong: cam ket von
nf=-M.NETFIN; print(f'(3) no rong 30/09 sau nghia vu: {nf:.1f} ty; +mo moi con lai {M.CAPEX_LEFT:.0f} + CCN 500 + mua NNC len 51% ~72 = {nf+M.CAPEX_LEFT+500+72:,.0f} ty (truoc dong tien HD 2027-28, tren VCSH 1.546)')
print(f'    D/E tho = {(nf+M.CAPEX_LEFT+500+72)/1546:.2f} neu KHONG co dong tien HD; skeptic uoc 1,4-1,5 nghin ty sau 2 nam dong tien (uoc luong)')
# (4) TTM ex hoan nhap Q4/25: FY25 HN hoan nhap du phong dau tu 31.297 (KT25 7.4) + 9T/25 chi phi tai chinh khac lai vay = 13.121-10.091=3.031
rev=31.297+3.031; ttm=306.8
for lab,aft in (('co thue 20%',rev*0.8),('khong thue',rev)):
    t=ttm-aft; print(f'(4) hoan nhap Q4/25 ~{rev:.1f} ty truoc thue; {lab}: sau thue {aft:.1f} -> TTM ex {t:.1f} ty, EPS {t*10:,.0f} d, P/E tai 13.700 = {13700/(t*10):.2f}x, tam/EPS {base/(t*10):.1f}x')
