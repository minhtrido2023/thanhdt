# DD HPG v2 — định giá TRUNG LẬP, nhất quán (β đo + thuế terminal 20% đi cùng nhau). Tất cả giả định = (ước lượng) trừ khi ghi nguồn.
sh=8442.96452; BV0=148795.5; px=21000            # cp lưu hành, VCSH mẹ 30/09/2026 [HN-Q3]; giá đóng cửa 30/10/2026 [BQ]
rf=0.0675; ERP=(0.050,0.0555,0.061)              # khung chi phí vốn nội địa (rf chuẩn hoá, ERP nội địa)
BETAS={'beta_do_2y_0.84':0.844,'blume_0.90':0.896,'blume_0.93':0.929}   # calc/gaps_beta_out.txt
payout=0.20; g=0.05
# LNST mẹ (tỷ) Q4/26, 2027, 2028, 2029 ở ETR hiện hành ~12%; roe_T = ROE terminal SAU thuế 20% (đã gồm hết ưu đãi)
# roe_T KHÔNG tự chọn: suy ra nhất quán = LN 2029 x (1+g) x (0,80/0,88) / BV cuối 2029 (thuế 12% -> 20% từ 2030, xử lý N2/GAPS §2+§7)
# Neo LN/tấn (ước lượng): 2023 ~1,05 · 2024 ~1,46 · 2025 ~1,48 · 9T/26 lõi ~1,87 tr đ/t; sản lượng 2026E ~14,1 tr t, công suất thép thô 16 tr t.
SC={
 'xau':      dict(w=0.25, e=[5500,16000,15000,16000], g=0.03, note='AD HRC cắt/giảm sau rà soát, spread 150-200; ~1,1 tr đ/t x 14-15 tr t (mức 2022-23)'),
 'trung_lap':dict(w=0.50, e=[7000,26000,26000,27000], g=0.05, note='KL 15 tr t (hiệu suất 81%->~90%), LN/tấn 1,87->~1,73 (nhà ở gãy -> thép XD H2/27, VinMetal 2027+)'),
 'tot':      dict(w=0.25, e=[8000,31000,33000,35000], g=0.05, note='LN/tấn giữ ~2,0 với 15,5-16 tr t; AD mở rộng sang ASEAN'),
}
TAXF=0.80/0.88
def ri(e,ke,g=g,roe_T=None,taxf=TAXF):
    bv=BV0; pv=0.0; t=0.0
    for i,ni in enumerate(e):
        dt=0.25 if i==0 else 1.0; t+=dt
        pv+=(ni-ke*dt*bv)/((1+ke)**t); bv+=ni*(1-payout)
    if roe_T is None: roe_T=e[-1]*(1+g)*taxf/bv
    tv=(roe_T-ke)*bv/(ke-g)/((1+ke)**t)
    return (BV0+pv+tv)/sh*1000, bv, roe_T
def wavg(ke,sc=SC):
    return sum(s['w']*ri(s['e'],ke,s['g'])[0] for s in sc.values())
print('== RI theo (beta, ERP), thue terminal 20%, g 5% (xau 3%) ==')
kes=[]
for nb,b in BETAS.items():
    row=[]
    for erp in ERP:
        ke=rf+b*erp; kes.append(ke)
        vals={k:ri(s['e'],ke,s['g'])[0] for k,s in SC.items()}
        row.append(f"Ke {ke*100:.2f}%: xau {vals['xau']:,.0f} / TL {vals['trung_lap']:,.0f} / tot {vals['tot']:,.0f} -> W {wavg(ke):,.0f}")
    print(nb); [print('   ',r) for r in row]
ke_c=rf+0.915*0.0555
print(f'\nKe trung tam (beta 0,915 x ERP 5,55%) = {ke_c*100:.2f}%  -> RI trong so {wavg(ke_c):,.0f}')
print(f'Dai Ke {min(kes)*100:.2f}-{max(kes)*100:.2f}% -> RI trong so {wavg(max(kes)):,.0f} - {wavg(min(kes)):,.0f}')
for k,s in SC.items():
    v_,bv_,r_=ri(s['e'],ke_c,s['g']); print(f'  {k}: {v_:,.0f} d/cp  BV2029 {bv_:,.0f}  ROE terminal sau thue 20% (suy ra) {r_*100:.1f}%  g {s["g"]}  P/B ngam {v_/(BV0/sh*1000):.2f}x')
print('\n-- Doi chieu: neu KHONG dua thue 20% vao terminal (roe_T/0,909) --')
nt=sum(s['w']*ri(s['e'],ke_c,s['g'],taxf=1.0)[0] for s in SC.values())
print(f'  Ke {ke_c*100:.2f}%: {nt:,.0f}  (lech +{nt-wavg(ke_c):,.0f} d/cp)')
print('-- Doi chieu: beta 1,1 cu (Ke 12,85%) + thue 20% --', f'{wavg(rf+1.1*0.0555):,.0f}')
print('\n== Do nhay trung lap: ROE terminal x Ke ==')
print('roe\\Ke', ' '.join(f'{k*100:6.2f}' for k in (0.1125,ke_c,0.1242,0.13)))
for r in (0.10,0.11,0.12,0.13,0.14,0.15,0.16):
    print(f'{r:.3f} ', ' '.join(f"{ri(SC['trung_lap']['e'],k,0.05,roe_T=r)[0]:6,.0f}" for k in (0.1125,ke_c,0.1242,0.13)))
print('\n== Trong so kich ban (Ke trung tam) ==')
for ws in ((0.25,0.5,0.25),(0.3,0.5,0.2),(0.2,0.5,0.3),(0.15,0.5,0.35),(0.35,0.5,0.15)):
    v=sum(w*ri(s['e'],ke_c,s['g'])[0] for w,s in zip(ws,SC.values())); print(ws, f'{v:,.0f}')
# ROE terminal ngam dinh o gia 21.000, duong LN trung lap
lo,hi=0.05,0.30
for _ in range(60):
    m=(lo+hi)/2
    if ri(SC['trung_lap']['e'],ke_c,0.05,roe_T=m)[0]<px: lo=m
    else: hi=m
print(f'\nGia 21.000 ngam ROE terminal (sau thue 20%) = {m*100:.1f}% tren duong LN trung lap, Ke {ke_c*100:.2f}%')
# EV/EBITDA
nd=59607.6; pt_dh=3828.9; pledged=8294.0; inv_lk=12664.1; mi=772.9
nd_adj=nd+pt_dh
EB={k:round(s['e'][1]/0.88+7100+12300,-2) for k,s in SC.items()}   # EBITDA 2027 = LN/0,88 + lai vay ~7,1k + KH ~12,3k (Q3/26 x4) (uoc luong); TTM loi 44.235
print('EBITDA 2027 theo kich ban:',EB)
print('\n== EV/EBITDA (no rong + phai tra nguoi ban DH 3.829 = no co tinh chat vay; tien gui cam co VAN la tai san) ==')
for m in (5,6,7):
    vals={k:(m*e-nd_adj-mi+inv_lk)/sh*1000 for k,e in EB.items()}
    w=sum(SC[k]['w']*v for k,v in vals.items())
    print(f'x{m}: xau {vals["xau"]:,.0f} / TL {vals["trung_lap"]:,.0f} / tot {vals["tot"]:,.0f} -> W {w:,.0f}')
mcap=px*sh/1000; ev=mcap+nd_adj+mi-inv_lk
print(f'EV hien tai (no dieu chinh) {ev:,.0f} ; EV/EBITDA loi TTM {ev/44235.3:.2f}x ; tren EBITDA 2027 trung lap {ev/EB["trung_lap"]:.2f}x ; P/E 2027 trung lap {mcap/SC["trung_lap"]["e"][1]:.2f}x')
print('\n== No rong / EBITDA loi TTM 44.235 ==')
for lab,x in (('tru toan bo tien gui (can duoi)',nd),('khong tru tien gui cam co 8.294',nd+pledged),('+ phai tra nguoi ban DH 3.829',nd+pledged+pt_dh)):
    print(f'  {lab}: {x:,.1f} -> {x/44235.3:.2f}x')
# Ghep nhat quan
ri_c=wavg(ke_c); ev6=sum(SC[k]['w']*(6*e-nd_adj-mi+inv_lk)/sh*1000 for k,e in EB.items())
ev5=sum(SC[k]['w']*(5*e-nd_adj-mi+inv_lk)/sh*1000 for k,e in EB.items())
ev7=sum(SC[k]['w']*(7*e-nd_adj-mi+inv_lk)/sh*1000 for k,e in EB.items())
print(f'\n== Ghep: RI trung tam {ri_c:,.0f}; EV/EBITDA 5x {ev5:,.0f} / 6x {ev6:,.0f} / 7x {ev7:,.0f}')
print(f'   Tam ghep 50/50 RI + 6x = {(ri_c+ev6)/2:,.0f}; RI + 5x = {(ri_c+ev5)/2:,.0f}; RI + 7x = {(ri_c+ev7)/2:,.0f}')
print(f'   Bien RI theo dai Ke: {wavg(max(kes)):,.0f}-{wavg(min(kes)):,.0f}')
# EPS loi
ttm_core=22943.2; lnk_q3=286.6*(1-0.093); q4_bds='Q4/25 bao cao co the con LN BDS van hanh nho (khong tach duoc)'
ttm2=ttm_core-lnk_q3; eps2=ttm2*(1-0.0216)/sh*1000
print(f'\nTTM loi me v2 = {ttm_core:,.0f} - LN khac Q3 sau thue {lnk_q3:,.0f} = {ttm2:,.0f}; EPS sau trich quy 2,16% = {eps2:,.0f} d; P/E loi {px/eps2:.2f}x ; ({q4_bds})')
print(f'Q3/26 loi: 7.973,5 - {lnk_q3:,.0f} = {7973.5-lnk_q3:,.0f}; Q3/25 loi = 4.012,3 - 392,7 - 57,3x0,86 = {4012.3-392.7-57.3*0.86:,.0f}; tang {((7973.5-lnk_q3)/(4012.3-392.7-57.3*0.86)-1)*100:.0f}% (khong bo LN khac: {(7973.5/(4012.3-392.7)-1)*100:.0f}%)')
cfo=20936.3; vat=7429.9-2294.2; ap=4410.4
print(f'CFO 9T {cfo:,.1f}; bo hoan VAT {vat:,.1f} -> {cfo-vat:,.1f} ({(cfo-vat)/19242.6:.2f}x loi); bo ca VAT va giam phai tra NB {ap} -> {cfo-vat+ap:,.1f} ({(cfo-vat+ap)/19242.6:.2f}x)')
# Tam ghep: RI la neo chinh (2/3) — da gom ROE fade + thue terminal; EV/EBITDA 5x (1/3) — boi so thi truong dang tra (5,2x TTM),
# KHONG dung 6-7x vi comp (VN 11,1x / khu vuc 7,8x) tinh tren EBITDA DAY chu ky => keo len neu ap len EBITDA gan dinh cua HPG.
center=(2*ri_c+ev5)/3
lo_=(2*wavg(max(kes))+sum(SC[k]['w']*(5*e-nd_adj-mi+inv_lk)/sh*1000 for k,e in {k:e*0.9 for k,e in EB.items()}.items()))/3
print(f'\n== TAM v2 = (2 x RI {ri_c:,.0f} + EV5x {ev5:,.0f})/3 = {center:,.0f} d/cp ; gia {px} = {(px/center-1)*100:+.1f}% so voi tam')
print(f'   can duoi (Ke 12,42% + EBITDA -10%): {lo_:,.0f}; can tren (Ke 10,97% + EV 5x): {(2*wavg(min(kes))+ev5)/3:,.0f}')
# Doi nhan dinh 2 chieu
up=dict(SC); up={k:dict(s) for k,s in SC.items()}; up['trung_lap']['e']=[8000,28000,28000,29000]
dn={k:dict(s) for k,s in SC.items()}; dn['trung_lap']['e']=[5500,23000,23000,24000]
def W(sc,ws): return sum(w*ri(s['e'],ke_c,s['g'])[0] for w,s in zip(ws,sc.values()))
print(f'LEN: trong so 0,15/0,50/0,35 + TL [8,0k;28k;28k;29k] -> {W(up,(0.15,0.5,0.35)):,.0f} ; chi doi trong so -> {W(SC,(0.15,0.5,0.35)):,.0f}')
print(f'XUONG: trong so 0,35/0,50/0,15 + TL [5,5k;23k;23k;24k] -> {W(dn,(0.35,0.5,0.15)):,.0f} ; chi doi trong so -> {W(SC,(0.35,0.5,0.15)):,.0f}')
print(f'Duoi trai TLSH: mat 50% khoan 9.915 = {-0.5*9915/sh*1000:,.0f} d/cp')
