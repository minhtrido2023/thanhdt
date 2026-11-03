"""r3 — Duong gia da DOC LAP (khong dung nhan FPTS). Mu gia co phieu: chi doc GPM_P0/Revenue_P0 (ticker_financial, gpm_bq.csv) + CPI (cpi_vn.py).
Gia thuc hien ngam: GPM_t = 1 - C_t/P_t. Neu chi phi don vi THUC khong doi (C_t = C_0 x CPI_t) => P_t/P_0 (thuc) = (1-GPM_0)/(1-GPM_t).
Gia dinh chi phi thuc khong doi la (uoc luong) — mo sau hon lam chi phi thuc TANG => uoc luong gia thuc ngam bi THAP (than trong)."""
import sys, pandas as pd, numpy as np
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude'); import cpi_vn
q=pd.read_csv('gpm_bq.csv'); q['y']=q.quarter.str[:4].astype(int); q=q[q.REV>0]
q['GP']=q.GPM*q.REV
a=q.groupby(['ticker','y']).agg(GP=('GP','sum'),REV=('REV','sum'),nq=('quarter','count')).reset_index(); a['GPM']=a.GP/a.REV
c=cpi_vn.cpi_monthly_df(end='2026-08-01'); c['y']=c.time.dt.year
cy=c.groupby('y').cpi_yoy.mean()/100; idx={2012:1.0}
for y in range(2013,2027): idx[y]=idx[y-1]*(1+cy[y])
print('CPI binh quan nam (%):',' '.join(f'{y}:{cy[y]*100:.1f}' for y in range(2012,2027)))
print(f'CPI index 2012->2025 = {idx[2025]:.3f} (CAGR {idx[2025]**(1/13)-1:.2%}); 2019->2025 CAGR {(idx[2025]/idx[2019])**(1/6)-1:.2%}')
out=[]
for t in ['NNC','KSB','DHA','VLB','MVC']:
    s=a[(a.ticker==t)&(a.y>=2012)&(a.nq>=3)].set_index('y')
    if 2012 not in s.index: base=s.index.min()
    else: base=2012
    g0=s.GPM[base]
    print(f'\n{t} (goc {base}, GPM {g0:.1%})  nam: GPM | gia thuc ngam (goc=1) | gia danh nghia ngam | GPM neu gia DANH NGHIA PHANG & chi phi +CPI')
    for y,r in s.iterrows():
        real=(1-g0)/(1-r.GPM); nom=real*idx[y]/idx[base]; flatg=1-(1-g0)*idx[y]/idx[base]
        out.append(dict(ticker=t,y=y,GPM=r.GPM,real=real,nom=nom,gpm_if_flat=flatg,nq=r.nq))
        print(f'  {y}{"*" if r.nq<4 else " "} {r.GPM:6.1%} | {real:5.2f} | {nom:5.2f} | {flatg:6.1%}')
o=pd.DataFrame(out); o.to_csv('price_path_implied.csv',index=False)
# kiem dinh: tan suat cua so 4 nam ma gia thuc ngam GIAM (= "khong chuyen lam phat" kieu g2031) va giam >=15% ("vach")
print('\n=== Tan suat cua so (nam y -> y+4), 4 ma da (NNC/KSB/DHA/VLB), 2012-2025 ===')
rows=[]
for t in ['NNC','KSB','DHA','VLB']:
    s=o[o.ticker==t].set_index('y').real
    for y in s.index:
        if y+4 in s.index and y+4<=2025: rows.append((t,y,s[y+4]/s[y]-1))
    s1=s[s.index<=2025]
r=pd.DataFrame(rows,columns=['t','y','d4']); n=len(r)
print(f'N cua so = {n} (chong lap, 4 ma tuong quan => N doc lap thuc ~3 chu ky/ma, it)')
for th,lab in [(0,'gia thuc giam (bat ky)'),(-0.10,'gia thuc giam >=10%'),(-0.15,'giam >=15%'),(-0.25,'giam >=25%')]:
    k=(r.d4<th).sum() if th<0 else (r.d4<0).sum(); print(f'  {lab:28s}: {k}/{n} = {k/n:.0%}')
nom_flat=[]
for t in ['NNC','KSB','DHA','VLB']:
    s=o[o.ticker==t].set_index('y')
    for y in s.index:
        if y+8 in s.index and y+8<=2025: nom_flat.append((t,y,s.nom[y+8]/s.nom[y]-1))
nf=pd.DataFrame(nom_flat,columns=['t','y','d8']); print(f'Cua so 8 nam: gia DANH NGHIA ngam tang <=5% (~"phang"): {(nf.d8<=0.05).sum()}/{len(nf)}; trung vi tang {nf.d8.median():.0%}')
print(r.pivot(index='y',columns='t',values='d4').round(2).to_string())
