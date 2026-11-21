"""Kiem doc lap P0/co so (9%) bang cong thuc annuity, KHONG import qtp_model_r3. + doi chieu FIRR 11% cua FS."""
r=0.135; i=0.09; T=3484.88; L=2787.9; E=T-L; SH=450
df=lambda t:(1+r)**-t
# xay dung: giai ngan 30/45/25 giua nam 2027/28/29 (t=0.5,1.5,2.5); lai vay tren du no binh quan
w=[.30,.45,.25]; bal=0; pv=0; idc=0
for k,wk in enumerate(w):
    d=L*wk; c=i*(bal+d/2); idc+=c; bal+=d; pv-= (E*wk+c)*df(k+0.5)
# van hanh 2030-2039: goc L/10, lai tren du no TB; KH (T+idc)/10; opex 572,3; thue: P0 lo -> mat toan bo thue nen 126 (2030-2047)
P=L/10; base_tax=503.8/0.8*0.2; opex=102.01+470.29
for n in range(10):
    t=3.5+n; ob=L-P*n; pv-= (P+i*(ob-P/2))*df(t)
ann=lambda a,b: sum(df(t) for t in [x+0.5 for x in range(a,b)])   # nam a..b-1 tinh tu 2027=0
pv-= opex*ann(3,21)            # 2030..2047
pv+= base_tax*ann(3,21)        # thue tiet kiem (cap tai thue nen)
print('IDC',round(idc,1),'| P0 co so PV delta (d/cp):',round(pv/SH*1000))
# Doi chieu FS: IRR khong don bay, sau thue, FC 529,4 x 18 nam, opex duoc bu (trung hoa), KH (T)/10
def npv(rate,cfs): return sum(c/(1+rate)**k for k,c in enumerate(cfs))
fc=81.42*6501.57/1000; dep=T/10
for life in (10,18):
    cfs=[-T*.30,-T*.45,-T*.25]+[fc-0.2*(fc-(dep if k<10 else 0)) for k in range(life)]
    lo,hi=0.0,0.5
    for _ in range(80):
        m=(lo+hi)/2; (lo,hi)=(m,hi) if npv(m,cfs)>0 else (lo,m)
    print(f'FC {fc:.1f} ty/nam x {life} nam -> IRR du an khong don bay sau thue {m:.2%} (FS FIRR 11,00%)')
