"""DD NNC — DINH CHINH 31/10/2026 (ap ban phan bien E1-E12). Ke thua valuation.py (30/10), KHONG sua ban cu.
Thay doi: (1) gia danh nghia/gia thuc = gia dinh so 1, 4 bien the; (2) cong LN gop cho thue Nui Nho;
(3) chi phi hieu chinh tren GV thanh pham kiem toan 2024-25 (KT25 7.2), dai +-10%; (4) MVC co/khong chiet khau thanh khoan 30%;
(5) trong so kich ban theo bang chung (nguoi doc nganh F2 P(gia Q2/27 < -7%)=0,15); (6) bang comp PE TTM BQ 30/10.
Gia dinh tu dat = (uoc luong)."""
import csv, itertools, numpy as np
SH=21.92e6; PX=47100; MCAP=SH*PX/1e9
cash=25.474; htm=322.440; tradsec=0.130; debt=5.000+69.890
net_cash_adj=cash+htm+tradsec-debt-22.373-16.776-5.888-4.497
mvc_mkt=10.3e6*14100/1e9; nhc_mkt=710242*18600/1e9
mvc_excirc=mvc_mkt*(1-9.659170e6*PX/1e9/(100e6*14100/1e9))
cip_tamlap=83.506; q4_26=60.0
VAR=110; FIX=70; SGA=20; TAX=0.2; INFL=0.03
# --- (3) hieu chinh chi phi tren GV thanh pham kiem toan [KT25 7.2]: 2024 178,29 ; 2025 178,59
# san luong 2024 = 1,05 tr m3 (FPTS tr.?); 2025 = 1,2 (FPTS 2025F) -> ca hai la uoc luong thu cap
gv_aud={2024:(1.05,178.287),2025:(1.20,178.589)}
k_list=[]
for y,(v,g) in gv_aud.items():
    model=(v*VAR+FIX)/(1+INFL)**(2026-y); k_list.append(g/model)
    print(f'GV kiem toan {y} {g:.1f} vs mo hinh {model:.1f} @ {v} tr m3 -> he so {g/model:.3f}')
K_MID=round(np.mean(k_list),2)   # tam = TB 2 nam kiem toan
print(f'He so chi phi tam {K_MID} (Q3/26 dinh diesel = 1,00 nam trong dai +-10%: {K_MID-0.10:.2f}-{K_MID+0.10:.2f})')
# (2) LN gop cho thue Nui Nho 2025 = 18,920 - 7,790 = 11,13 [KT25 7.1-7.2]; giu toi 2043 (dat sau dong mo chua co quy hoach)
RENT=18.920-7.790
def path(v27,v28,p27,p28,ylate,plate,mode='flat',k=1.0,rent=True,late_from=2031,rec=None):
    out=[]
    for y in range(2027,2044):
        v=v27 if y==2027 else (v28 if y<late_from else ylate)
        p=p27 if y==2027 else (p28 if y<late_from else plate)
        if rec and y>=rec[0]: v,p=rec[1],rec[2]
        f=(1+INFL)**(y-2026)
        if mode=='flat': g=1.0
        elif mode=='g2031': g=(1+INFL)**max(0,y-2030)
        elif mode=='g2028': g=(1+INFL)**max(0,y-2027)
        elif mode=='real': g=f            # gia nhap theo tien 2026, giu gia tri thuc
        ebit=v*(p*g-VAR*k*f)-FIX*k*f-SGA*f+(RENT*f if rent else 0)
        out.append((y,max(ebit,0)*(1-TAX)))
    return out
def pv(cf,r): return sum(c/(1+r)**(y-2026.83+0.5) for y,c in cf)
SCN={'tot':(1.40,1.40,420,400,1.40,420),'co_so':(1.40,1.10,380,300,1.20,320),
     'xau':(1.30,0.80,330,250,0.80,250),'rat_xau':(0.80,0.80,230,210,0.80,210)}
W_OLD={'tot':.20,'co_so':.45,'xau':.25,'rat_xau':.10}
W_NEW={'tot':.25,'co_so':.50,'xau':.20,'rat_xau':.05}
def value(k_s,mode='flat',k=1.0,rent=True,mvc_disc=0.0,r=0.13,rec=None,ovr=None):
    a=ovr or SCN[k_s]
    cf=path(*a,mode=mode,k=k,rent=rent,rec=rec if k_s=='xau' else None)
    eq=pv(cf,r)+q4_26+net_cash_adj+mvc_excirc*(1-mvc_disc)+nhc_mkt+cip_tamlap*(0 if k_s in('xau','rat_xau') else 1)
    return eq*1e9/SH
def ev(W,**kw):
    vals={s:value(s,**kw) for s in SCN}; return sum(W[s]*vals[s] for s in SCN),vals
rows=[]
def rep(lab,W,**kw):
    e,v=ev(W,**kw); rows.append([lab]+[round(v[s]) for s in SCN]+[round(e)])
    print(f'{lab:58s} '+' '.join(f'{v[s]:>7,.0f}' for s in SCN)+f' | KV {e:>7,.0f} ({e/PX-1:+.0%})')
print('\n=== Cau truc (tot / co_so / xau / rat_xau | ky vong), r=13% ===')
rep('[0] ban 30/10: phang, k=1, khong thue, W cu',W_OLD,mode='flat',k=1.0,rent=False)
rep('[1] + LN gop cho thue',W_OLD,mode='flat',k=1.0)
rep(f'[2] + chi phi k={K_MID}',W_OLD,mode='flat',k=K_MID)
rep('[3] + trong so moi 25/50/20/5 (gia phang)',W_NEW,mode='flat',k=K_MID)
print('\n=== Gia dinh so 1: duong gia danh nghia (W moi, k tam, co thue) ===')
for m,lab in [('flat','phang danh nghia (gia thuc -3%/nam)'),('g2031','+3%/nam tu 2031'),('g2028','+3%/nam tu 2028'),('real','giu gia tri thuc (+3%/nam tu 2027)')]:
    rep(f'gia {lab}',W_NEW,mode=m,k=K_MID)
print('\n=== Do nhay chi phi +-10% quanh tam (W moi) ===')
for m in ('flat','real'):
    for kk in (K_MID-0.10,K_MID,K_MID+0.10): rep(f'{m} k={kk:.2f}',W_NEW,mode=m,k=kk)
print('\n=== MVC chiet khau thanh khoan 0 / 30% ===')
for m in ('flat','real'):
    for d in (0.0,0.30): rep(f'{m} MVC disc {d:.0%}',W_NEW,mode=m,k=K_MID,mvc_disc=d)
print('\n=== Lai suat chiet khau ===')
for m in ('flat','real'):
    for r in (0.11,0.13,0.15): rep(f'{m} r={r:.0%}',W_NEW,mode=m,k=K_MID,r=r)
print('\n=== Xau co hoi phuc 1,2 x 320 tu 2035 (Tam Lap 2/3 het GP som hon 8-10 nam, FPTS tr.9) ===')
for m in ('flat','real'): rep(f'{m} xau hoi phuc 2035',W_NEW,mode=m,k=K_MID,rec=(2035,1.2,320))
print('\n=== Gia "tot" thap hon 400/380/400 ===')
for m in ('flat','real'):
    e,v=ev(W_NEW,mode=m,k=K_MID); vt=value('tot',mode=m,k=K_MID,ovr=(1.40,1.40,400,380,1.40,400))
    print(f'{m}: tot {vt:,.0f} | KV {e-W_NEW["tot"]*(v["tot"]-vt):,.0f}')
# --- dai tong hop (luat 12: ca hai chieu vao dai)
grid=[]
for m,kk,d,r in itertools.product(('flat','g2031','g2028','real'),(K_MID-0.10,K_MID,K_MID+0.10),(0.0,0.30),(0.11,0.13,0.15)):
    grid.append(ev(W_NEW,mode=m,k=kk,mvc_disc=d,r=r)[0])
g=np.array(grid)
lo_c=ev(W_NEW,mode='flat',k=K_MID,mvc_disc=0.15)[0]; hi_c=ev(W_NEW,mode='real',k=K_MID,mvc_disc=0.15)[0]
mid=(lo_c+hi_c)/2
print(f'\nLUOI 4 duong gia x 3 chi phi x 2 MVC x 3 r = {len(g)} o: min {g.min():,.0f} P10 {np.percentile(g,10):,.0f} trung vi {np.median(g):,.0f} P90 {np.percentile(g,90):,.0f} max {g.max():,.0f}')
print(f'Tam (r13%, k tam, MVC disc 15% = giua 0/30): phang {lo_c:,.0f} ({lo_c/PX-1:+.0%}) .. thuc {hi_c:,.0f} ({hi_c/PX-1:+.0%}); diem giua {mid:,.0f} ({mid/PX-1:+.0%})')
# 3 kich ban cho bao cao nha dau tu: gop tot / co so / xau+rat xau (trong so 25/50/25), diem giua phang..thuc
print('\n3 kich ban (bao cao NDT): gop xau+rat_xau theo trong so 20:5')
sc3={}
for m in ('flat','real'):
    v={s:value(s,mode=m,k=K_MID,mvc_disc=0.15) for s in SCN}
    sc3[m]={'tich_cuc':v['tot'],'co_so':v['co_so'],'tieu_cuc':(0.20*v['xau']+0.05*v['rat_xau'])/0.25}
    print(m,{a:round(b) for a,b in sc3[m].items()})
with open('valuation_v2_scenarios.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['bien_the','tot','co_so','xau','rat_xau','ky_vong']); w.writerows(rows)
with open('valuation_v2_3scen.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['kich_ban','xac_suat','gia_phang','gia_thuc'])
    for a,p in (('tich_cuc',.25),('co_so',.50),('tieu_cuc',.25)): w.writerow([a,p,round(sc3['flat'][a]),round(sc3['real'][a])])
# do nhay gia x san luong, gia giu gia tri thuc (r13, k tam) -> bo sung cho bang cu (phang)
print('\nDo nhay gia(2026 tien) x san luong 2028+, r=13%, k tam, 2 che do:')
for m in ('flat','real'):
    print(' che do',m)
    for v in (0.8,1.0,1.2,1.4):
        row=[]
        for p in (220,260,300,340,380,420):
            cf=path(1.40,v,380,p,v,p,mode=m,k=K_MID); eq=pv(cf,0.13)+q4_26+net_cash_adj+mvc_excirc*0.85+nhc_mkt+cip_tamlap
            row.append(f'{eq*1e9/SH:>7,.0f}')
        print(f'  V={v:.1f}: '+' '.join(row))
# --- comp ngang nganh, BQ tav2_bq.ticker Close 30/10 x OShares ticker_financial / tong NP_P0 4 quy Q4/25-Q3/26
comp={'NNC':(47100,21.92e6,[53.879,39.607,51.178,69.290]),'DHA':(56000,14.721073e6,[19.032,26.193,26.933,79.578]),
      'KSB':(12750,114.443703e6,[41.337,31.823,96.766,34.702]),'VLB':(52100,46.72056e6,[100.729,74.114,374.449,117.407])}
print('\nComp PE TTM (BQ 30/10):')
for t,(p,s,npq) in comp.items():
    mc=p*s/1e9; print(f' {t}: von hoa {mc:,.0f} ty | LNST TTM {sum(npq):.1f} | PE {mc/sum(npq):.2f}x')
vl=comp['VLB']; adj=sum(vl[2])-vl[2][2]+np.mean([vl[2][0],vl[2][1],vl[2][3]])
print(f' VLB neu thay Q2/26 bang TB 3 quy con lai: LNST {adj:.1f} PE {vl[0]*vl[1]/1e9/adj:.2f}x (uoc luong)')
# --- tai lap so phan bien (doi TUNG gia dinh tren ban 30/10)
print('\nTai lap phan bien (1 thay doi/lan, ban 30/10):')
b=dict(k=1.0,rent=False)
for lab,W,kw in [('W 25/50/20/5',W_NEW,dict(mode='flat',**b)),('+3% tu 2031',W_OLD,dict(mode='g2031',**b)),('+3% tu 2028',W_OLD,dict(mode='g2028',**b)),
                 ('gia thuc',W_OLD,dict(mode='real',**b)),('thue',W_OLD,dict(mode='flat',k=1.0)),('chi phi -10%',W_OLD,dict(mode='flat',k=0.9,rent=False)),
                 ('chi phi +10%',W_OLD,dict(mode='flat',k=1.1,rent=False)),('MVC -30%',W_OLD,dict(mode='flat',mvc_disc=0.3,**b))]:
    print(f' {lab}: {ev(W,**kw)[0]:,.0f}')
# --- dinh gia nguoc: xac suat kich ban tieu cuc ma gia 47.100 ham y (giu ti le tich cuc:co so = 1:2)
print('\nDinh gia nguoc @47.100 va gia lan can:')
for m in ('flat','real'):
    s=sc3[m]; up=(s['tich_cuc']+2*s['co_so'])/3
    for px in (45000,47100,49350,52000):
        print(f' {m} gia {px:,}: P(tieu cuc) ham y = {(up-px)/(up-s["tieu_cuc"]):.0%}')
