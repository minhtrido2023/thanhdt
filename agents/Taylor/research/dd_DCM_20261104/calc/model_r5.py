"""DCM r5 — sửa r4 theo phản biện độc lập: (S2) HAI cách đọc nhất quán A/B thay vì giao hai cách đọc bất lợi; (S3) năm 2028 dùng mức V2;
(S4) độ nhạy 2035+ (KHÔNG vào base); (M5) độ nhạy thang hồi quy. MÙ GIÁ (không nhận giá/vốn hoá/PE của DCM).
GHI TRUNG THỰC: người viết ĐÃ BIẾT giá đóng cửa 33.000 và nhãn ĐẮT từ r1–r4 trước khi sửa; model KHÔNG nhận giá.
Chạy từ thư mục dd_DCM_20261104/. Dựng TRÊN calc/model_r2.py (đã khoá md5, không sửa): giá trị r4 = giá trị r2 + PV(Δ chi phí khí theo năm).
Đơn vị tỷ đồng; USD/t urê; USD/MMBtu. Giả định tự đặt gắn (ước lượng).

NGUỒN (trang = trang pdf):
 [PL12] src/gas/egm2026_tailieu.pdf — Tài liệu ĐHĐCĐ bất thường 2026 (Vietstock static2), Phần 4 + Phụ lục "DỰ THẢO SỬA ĐỔI BỔ SUNG SỐ 12":
        p26 Đ4.1(a): LKN 495 tr Sm3/năm, LKNTT (bao tiêu) 445,5 tr Sm3 tới 24/4/2032; p27 Đ4.1.2(ii): LKNTT ND-UM giai đoạn bình ổn 269,74 tr Sm3;
        p28 Đ4.2: LKNTĐ 1,5 tr Sm3/ngày @37,3 MJ/Sm3, ND-UM 0,81; p29 Đ4.17(b): khí ND-UM đầu tiên ≤ Q4/2028; p30 Đ4.17(i): bình ổn tối thiểu
        = sớm hơn của 55 tháng / 120,45 bscf; p31 Đ9.1: Pn3 = 10,39 × (1+2,25%)^t USD/MMBTU tại mỏ, chưa VAT, t tính từ 01/01 năm có khí đầu
        nếu khí đầu ≤31/12/2028; Đ9.2: giá khí giao thiếu DP3 = 0,80×Pn3 + Tp; p26 Đ3.3: hết hạn = muộn nhất của (HĐ PM3 PVN–PVGAS, HĐ ND-UM,
        24/4/2032).
 [PL11] src/gas/egm2025_update_en.txt pdf p17–18: chỉ chuyển Bên bán PVN → PV GAS; KHÔNG có điều khoản giá/khối lượng mới.
 [BB25] src/gas/dl_1844450.txt (Biên bản ĐHĐCĐ bất thường 05/11/2025, PL I câu 1, pdf p8): khí PM3 chia 50% Petronas/50% PVN; PVN mua lại
        phần Petronas; "kết thúc hợp đồng mua khí với Petronas vào cuối năm 2027"; PVN đã gia hạn với chủ mỏ 20 năm (đến 2047). Không nêu giá.
 [VDSC] txt/VDSC_Q3_2026.txt p5–7 Bảng 3–4 (nguồn "DCM, CTCK Rồng Việt"): PVN quyền nhận = 46% MFO; Petronas 12,7% Brent (2026), 13,7% (2027+);
        MFO = 5,72×Brent USD/t; MFO USD/MMBtu = MFO/40,6; cước 1,14 (2026–27) / 1,06 (2028+). → THỨ CẤP, không phải văn bản hợp đồng.
"""
import sys, json, itertools
sys.path.insert(0, 'calc')
import model as m
import model_r2 as r2
ps, R0, DEP0, rdep = m.ps, m.R0, m.DEP0, m.rdep
TAX_LR, KTPL_RATE, KTPL_BAL, RESTRICTED = r2.TAX_LR, r2.KTPL_RATE, r2.KTPL_BAL, r2.RESTRICTED
USDVND, PROD_KT = r2.USDVND, r2.PROD_KT          # 26.400 (ước lượng) · 966,7 kt (NQ 2025)
BRENT_TC = r2.BRENT_TC                             # 67,8 = TB Brent 2016–25 (WB, BQ)

# ---------- công thức giá theo nguồn ----------
P0_ND, ESC_ND = 10.39, 0.0225                      # [PL12 p31] tại mỏ, chưa VAT
FREIGHT = 1.14                                     # [VDSC] cước Tp — chung mọi nguồn ⇒ triệt tiêu trong Δ; chỉ dùng cho mức tuyệt đối (mục c)
MFO_PER_BRENT, MMBTU_PER_T_MFO = 5.72, 40.6        # [VDSC] (ước lượng của CTCK)
K_PVN = 0.46*MFO_PER_BRENT/MMBTU_PER_T_MFO         # = 0,0648 USD/MMBtu mỗi USD Brent
K_PET = {2026: 0.127, 2027: 0.137}                 # [VDSC]; từ 2028 HĐ mua bổ sung Petronas HẾT HẠN [BB25] ⇒ giá phần này KHÔNG CÔNG BỐ
K_PET_POST = 0.137                                 # (ước lượng) giữ 13,7% cho phần PM3 ngoài quyền nhận PVN sau 2028 — biến thể V2
I_C = 22.0                                         # (ước lượng) MMBtu khí/t urê, hiệu chỉnh từ TM38 9T/25 & 9T/26 (mục c); độ nhạy 25
ND_CAP = 0.81/1.5                                  # [PL12 p28] LKNTĐ Nam Du / tổng = 54% — TRẦN theo công suất ngày, chỉ nhất quán nếu I_C≈18
SM3_TO_MMBTU = 37.3/1055.056                       # 37,3 MJ/Sm3 → MMBtu/Sm3 [PL12 p28]
def nd_share_bao_tieu(I=None):
    """Tỷ trọng Nam Du khi PHÂN BỔ THEO TIÊU THỤ + sàn bao tiêu 269,74 tr Sm3 [PL12 p27] trên mức tiêu thụ của DCM = PROD_KT × I_C."""
    I = I_C if I is None else I
    sm3 = PROD_KT*1e3*I/SM3_TO_MMBTU/1e6           # triệu Sm3/năm
    return 269.74/sm3
# cách đọc (reading): nd_plateau, biến thể PM3 từ 2029, 2028 luôn V2 (S3)
READ = {'A': dict(nd=None, var='AVG'),             # A: tiêu thụ + bao tiêu (≈44,8%), PM3 TB V1/V2
        'B': dict(nd=ND_CAP, var='V1')}            # B: Nam Du THAY phần Petronas (BB25 p8), ND 54%, PM3 còn lại V1
LAST_Y = 2034                                      # từ 2035: mặc định 50% PVN + 50% @13,7% Brent (ước lượng); xem LATE
LATE = dict(mode='base', p=None)                   # S4: 'flat' = 10,39 phẳng + cước; 'esc' = 10,39×1,0225^(2035-2028) + cước; KHÔNG vào base

def nd_shares(plateau):
    return {2028: 0.25*plateau, **{y: plateau for y in range(2029, 2034)}, 2034: 0.5*plateau}

def gas_usd_mmbtu(y, B, variant='V1', freight=True, plateau=None):
    """Giá khí bình quân trước VAT (USD/MMBtu) năm y ở Brent B. Cấu trúc PM3 = 50% quyền nhận PVN (46% MFO) + 50% phần Malaysia (BB25: chia 50/50).
    Pn1/Pn2 do Đ9.1 HĐ gốc quyết định, SĐBS 12 giữ nguyên Đ9.3 ⇒ ẩn số là KHỐI LƯỢNG khí bổ sung sau 2027 & nguồn thượng nguồn:
    V1 = phần bổ sung rẻ ngang quyền nhận PVN; V2 = phần bổ sung giữ 13,7% Brent. 2028: LUÔN V2 (S3: mua Petronas hết cuối 2027, Nam Du ≤ Q4/2028)."""
    plateau = ND_CAP if plateau is None else plateau
    nd = nd_shares(plateau).get(y, 0.0) if y <= LAST_Y else 0.0
    p_nd = P0_ND*(1+ESC_ND)**max(0, y-2028)       # t=0 ở năm 2028 [PL12 p31]
    if y <= 2027:
        pm3 = 0.5*K_PVN*B + 0.5*K_PET[y]*B
    elif y > LAST_Y:
        if LATE['mode'] == 'flat': return P0_ND + (FREIGHT if freight else 0.0)
        if LATE['mode'] == 'esc': return P0_ND*(1+ESC_ND)**(LAST_Y+1-2028) + (FREIGHT if freight else 0.0)
        pm3 = 0.5*K_PVN*B + 0.5*K_PET_POST*B
    elif y == 2028 or variant == 'V2':
        pm3 = 0.5*K_PVN*B + 0.5*K_PET_POST*B
    elif variant == 'V1':
        pm3 = K_PVN*B
    else:                                          # 'AVG' = trung bình V1/V2 (trọng số 0,5/0,5, ước lượng)
        pm3 = 0.5*K_PVN*B + 0.5*(0.5*K_PVN*B + 0.5*K_PET_POST*B)
    return (1-nd)*pm3 + nd*p_nd + (FREIGHT if freight else 0.0)

def proxy_cost(B): return 25*(2.5+0.06*B)          # proxy Bobby, USD/t urê
def hist_cost(B, I=I_C): return I*gas_usd_mmbtu(2026, B)   # chế độ 2021–26 (ước lượng: 50/50 @12,7%)
HIST_B = {y: m.cm[y][1] for y in range(2021, 2026)}
def bias_hist(I=I_C): return sum(proxy_cost(b)-hist_cost(b, I) for b in HIST_B.values())/len(HIST_B)

def delta_spread(y, B, variant='V1', I=I_C, plateau=None):
    """Δ biên (USD/t) so với chế độ mà hồi quy r2 đã hấp thụ: [proxy(B) − chi phí HĐ(y,B)] − độ lệch TB 2021–25. Dương = lợi cho DCM."""
    return (proxy_cost(B) - I*gas_usd_mmbtu(y, B, variant, plateau=plateau)) - bias_hist(I)

def pv_gas(B, variant='V1', I=I_C, r=R0, mode='path', plateau=None, kscale=1.0):
    """PV (đ/cp) của Δ chi phí khí sau thuế 20% và KTPL. t = y−2026. mode: 'slope' = chỉ hiệu chỉnh độ dốc; 'path' = đường hợp đồng đủ;
    'perm2030' = cơ cấu 2030 vĩnh viễn (GỒM cả phần độ dốc). kscale = hệ số thang (M5: 9,9/25,5 = thang hồi quy)."""
    k = kscale*(1-TAX_LR)*(1-KTPL_RATE)*PROD_KT*1e3*USDVND/1e9
    sl = lambda: proxy_cost(B)-hist_cost(B, I)-bias_hist(I)
    pv = 0.0
    for y in range(2027, LAST_Y+1):
        d = sl() if mode == 'slope' else delta_spread(y, B, variant, I, plateau)
        pv += d*k/(1+r)**(y-2026)
    yy = 2030 if mode == 'perm2030' else LAST_Y+1
    d_lr = sl() if mode == 'slope' else delta_spread(yy, B, variant, I, plateau)
    pv += d_lr*k/r/(1+r)**(LAST_Y-2026)
    return ps(pv)

def reading_gas(tag, B=BRENT_TC, I=I_C, r=R0, **kw):
    """PV phần khí theo cách đọc nhất quán. A: Nam Du = bao tiêu/tiêu thụ (tính từ I), PM3 = TB V1/V2. B: Nam Du 54% thay Petronas, PM3 còn lại V1."""
    c = READ[tag]; pl = nd_share_bao_tieu(I) if c['nd'] is None else c['nd']
    if c['var'] == 'AVG':
        return 0.5*pv_gas(B, 'V1', I, r, plateau=pl, **kw) + 0.5*pv_gas(B, 'V2', I, r, plateau=pl, **kw)
    return pv_gas(B, c['var'], I, r, plateau=pl, **kw)

def ev_reading(tag, B=BRENT_TC, I=I_C, r=R0, kscale=1.0, **kw):
    e = r2.ev_r2(r=r, **kw); g = reading_gas(tag, B, I, r, kscale=kscale)
    return {k: v+g for k, v in e.items()} | dict(gas=g)

def ev_r5(B=BRENT_TC, I=I_C, r=R0, kscale=1.0, **kw):
    """TÂM = trung bình A và B (công bố rõ); dải = [min, max]."""
    a, b = ev_reading('A', B, I, r, kscale, **kw), ev_reading('B', B, I, r, kscale, **kw)
    c = {k: 0.5*(a[k]+b[k]) for k in a}
    return c | dict(A=a['EV'], B=b['EV'], lo=min(a['EV'], b['EV']), hi=max(a['EV'], b['EV']))

if __name__ == '__main__':
    L = []; base = ev_r5(); b2 = r2.ev_r2()
    ndA = nd_share_bao_tieu(); sm3 = PROD_KT*1e3*I_C/SM3_TO_MMBTU/1e6
    L.append(f'0. Hằng số: K_PVN {K_PVN:.4f}/USD Brent · ND P0 {P0_ND} +{ESC_ND:.2%}/năm · I_C {I_C} MMBtu/t · Brent TC {BRENT_TC:.1f} · độ lệch proxy−HĐ TB 2021–25 {bias_hist():+.1f} USD/t')
    L.append(f'   Nhất quán khối lượng: {PROD_KT} kt × {I_C} MMBtu/t = {PROD_KT*I_C/1e3:.2f} tr MMBtu = {sm3:.0f} tr Sm3/năm = {sm3/495:.3f}×LKN(495). Nam Du: A (bao tiêu 269,74/tiêu thụ) = {ndA:.1%}; trần LKNTĐ 0,81×365/tiêu thụ = {0.81*365/sm3:.1%}; B (0,81/1,5) = {ND_CAP:.1%}; I_C để 54% đúng = {269.74/ND_CAP*SM3_TO_MMBTU*1e6/(PROD_KT*1e3):.1f}')
    cal = {}
    for tag, ty, b, yr in (('9T/25', 3109.5+3.4, HIST_B[2025], 2026), ('9T/26', 4258.1+22.4, 94.0, 2026)):
        usd = ty*1e9/(25400 if tag == '9T/25' else USDVND)
        for prod in (700, 725, 750):
            cal[f'{tag}_prod{prod}'] = round(usd/(prod*1e3)/gas_usd_mmbtu(yr, b), 1)
    L.append('1. Hiệu chỉnh I (MMBtu/t) = tiền khí TM38 / sản lượng 9T (ước lượng 700/725/750 kt) / giá công thức trước VAT (Brent 2025 69,0; 9T/26 94,0): '+json.dumps(cal))
    cmp = {B: dict(proxy=round(proxy_cost(B), 1), hd_I22=round(22*gas_usd_mmbtu(2026, B), 1), hd_I25=round(25*gas_usd_mmbtu(2026, B), 1),
                   proxy_mmbtu=round(2.5+0.06*B, 2), hd_mmbtu=round(gas_usd_mmbtu(2026, B), 2)) for B in (BRENT_TC, 82, 90, 103)}
    L.append('   Proxy 25×(2,5+0,06B) vs công thức HĐ 2026 (USD/t; USD/MMBtu): '+json.dumps(cmp))
    sched = {}
    for B in (BRENT_TC, 82, 90, 103):
        sched[round(B, 1)] = {y: dict(A_usd=round(0.5*gas_usd_mmbtu(y, B, 'V1', plateau=ndA)+0.5*gas_usd_mmbtu(y, B, 'V2', plateau=ndA), 2),
                                       B_usd=round(gas_usd_mmbtu(y, B, 'V1', plateau=ND_CAP), 2),
                                       V1_A=round(gas_usd_mmbtu(y, B, 'V1', plateau=ndA), 2), V2_A=round(gas_usd_mmbtu(y, B, 'V2', plateau=ndA), 2),
                                       dA=round(0.5*delta_spread(y, B, 'V1', plateau=ndA)+0.5*delta_spread(y, B, 'V2', plateau=ndA), 1),
                                       dB=round(delta_spread(y, B, 'V1', plateau=ND_CAP), 1))
                              for y in (2026, 2027, 2028, 2029, 2030, 2032, 2034, 2035)}
    L.append('2. Lịch giá khí trước VAT gồm cước (USD/MMBtu) theo cách đọc A/B và Δ biên (USD/t, dương = lợi), Brent phẳng: '+json.dumps(sched))
    L.append(f'3. Giá trị r5 (đ/cp, Brent {BRENT_TC:.1f}): TÂM {base["EV"]:,.0f} = TB(A {base["A"]:,.0f}; B {base["B"]:,.0f}) · CYC {base["CYC"]:,.0f} · ADMIN {base["ADMIN"]:,.0f} · STRUCT {base["STRUCT"]:,.0f} (r2/r3 {b2["EV"]:,.0f}; r4 23.644)')
    sA = pv_gas(BRENT_TC, 'V1', mode='slope', plateau=ndA)
    gA, gB = reading_gas('A'), reading_gas('B')
    br = dict(r3=round(b2['EV']), slope=round(sA), path_A=round(gA-sA), path_B=round(gB-sA), path_center=round(0.5*(gA+gB)-sA), r5=round(base['EV']),
              gas_A=round(gA), gas_B=round(gB))
    L.append('4. Cầu nối r3 -> r5 (đ/cp): '+json.dumps(br))
    # cầu nối r4 -> r5 từng bước (để báo trung thực chiều)
    byB = {}
    for B in (BRENT_TC, 82, 90, 103):
        e = ev_r5(B)
        byB[round(B, 1)] = dict(EV=round(e['EV']), A=round(e['A']), B=round(e['B']), gasA=round(reading_gas('A', B)), gasB=round(reading_gas('B', B)),
                                slope=round(pv_gas(B, 'V1', mode='slope', plateau=ndA)),
                                perm2030_B=round(pv_gas(B, 'V1', mode='perm2030', plateau=ND_CAP)), perm2030_A=round(0.5*pv_gas(B, 'V1', mode='perm2030', plateau=ndA)+0.5*pv_gas(B, 'V2', mode='perm2030', plateau=ndA)))
    L.append('5. Theo Brent phẳng (đ/cp): '+json.dumps(byB))
    mt = {}
    for s in (98, 138, 150, 179, 220, 242, 260):
        mt[s] = {round(B, 1): dict(c=round(ev_r5(B, s_tc=s)['EV']), A=round(ev_r5(B, s_tc=s)['A']), B=round(ev_r5(B, s_tc=s)['B'])) for B in (BRENT_TC, 82, 90, 103)}
    L.append('6. Biên dài hạn × Brent -> tâm/A/B (đ/cp): '+json.dumps(mt))
    sens = {}
    for tag in 'AB':
        for I in (20, 25): sens[f'{tag}_I{I}'] = round(ev_reading(tag, I=I)['EV'])
    sens['center_I20'] = round(ev_r5(I=20)['EV']); sens['center_I25'] = round(ev_r5(I=25)['EV'])
    for d in (-1.0, -0.5, 0.5, 1.0): sens[f'center_dep{d:+.1f}_b1'] = round(ev_r5(r=rdep(DEP0+d))['EV'])
    # Nam Du thấp: 30% (cụm Cà Mau), và 'V1 + ND30' / 'V1 + ND44,8' (ngưỡng đảo nhãn)
    for tag, pl in (('nd30', 0.30), ('nd448', ndA), ('nd491', 0.81*365/sm3), ('nd54', ND_CAP), ('nd605', 269.74/445.5)):
        for v in ('V1', 'V2'):
            sens[f'{tag}_{v}'] = round(r2.ev_r2()['EV']+pv_gas(BRENT_TC, v, plateau=pl))
            sens[f'{tag}_{v}_b103'] = round(r2.ev_r2(r=R0)['EV']+pv_gas(103, v, plateau=pl))
        sens[f'{tag}_AVG'] = round(r2.ev_r2()['EV']+0.5*pv_gas(BRENT_TC, 'V1', plateau=pl)+0.5*pv_gas(BRENT_TC, 'V2', plateau=pl))
    # trễ khí đầu sang 2029 (cách đọc A)
    _f = nd_shares
    def _late(pl): d = _f(pl); d[2028] = 0.0; d[2029] = 0.75*pl; return d
    nd_shares_bak = nd_shares
    nd_shares = _late
    sens['A_nd_late_2029'] = round(ev_reading('A')['EV']); sens['B_nd_late_2029'] = round(ev_reading('B')['EV'])
    nd_shares = nd_shares_bak
    # M5: thang hồi quy 9,9/25,5 (chiều sai không rõ)
    k_full = (1-TAX_LR)*(1-KTPL_RATE)*PROD_KT*1e3*USDVND/1e9
    reg_scale = (8.84/(1-m.TAX_HIST))/ (k_full/(1-TAX_LR)/(1-KTPL_RATE))
    sens['kscale_reg'] = round(reg_scale, 3)
    sens['center_kscale_reg'] = round(ev_r5(kscale=reg_scale)['EV']); sens['A_kscale_reg'] = round(ev_reading('A', kscale=reg_scale)['EV']); sens['B_kscale_reg'] = round(ev_reading('B', kscale=reg_scale)['EV'])
    # S4: 2035+ phẳng 10,39 / leo thang; KHÔNG vào base
    for mode in ('flat', 'esc'):
        LATE['mode'] = mode
        sens[f'late_{mode}_center'] = round(ev_r5()['EV']); sens[f'late_{mode}_A'] = round(ev_reading('A')['EV']); sens[f'late_{mode}_B'] = round(ev_reading('B')['EV'])
        sens[f'late_{mode}_center_b103'] = round(ev_r5(B=103)['EV'])
    LATE['mode'] = 'base'
    L.append('7. Độ nhạy (đ/cp): '+json.dumps(sens))
    def grid(stcs, Bs=(BRENT_TC,)):
        g = []
        for r_, stc, near_, st_, rc, B in itertools.product([rdep(DEP0+d) for d in (-1, -.5, 0, .5, 1)], stcs, [170, 222, 285], [100, 125, 150], [0, -RESTRICTED], Bs):
            g.append(ev_r5(B=B, r=r_, s_tc=stc, near=near_, struct=st_, nc_adj=-KTPL_BAL+rc)['EV'])
        g.sort(); n = len(g); q = lambda f: round(g[int(f*(n-1))])
        return dict(n=n, P10=q(.1), P25=q(.25), P50=q(.5), P75=q(.75), P90=q(.9))
    grids = dict(sym3=grid([138, m.spread_tc, 220]), sym5=grid([98, 138, m.spread_tc, 220, 260]), sym3_brent4=grid([138, m.spread_tc, 220], (BRENT_TC, 82, 90, 103)))
    L.append('8. Lưới trên TÂM (r±100bp × biên TC × năm1 170/222/285 × STRUCT 100/125/150 × phong toả 0/−332; Brent 67,8 trừ khi ghi): '+json.dumps(grids))
    # 9. cầu nối từng bước r4 -> r5 (mỗi bước sửa 1 thứ)
    import model_r4 as M4
    r4v = M4.ev_r4()['EV']; s3 = sens['nd54_AVG']
    L.append('9. Cầu nối r4 -> r5 (đ/cp): '+json.dumps(dict(r4=round(r4v), sau_S3_2028_theo_V2=s3, d_S3=s3-round(r4v), sau_S2_tam_AB=round(base['EV']), d_S2=round(base['EV'])-s3)))
    print('\n'.join(L)); open('calc/model_r5_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(dict(base=base, base_r2=b2, bridge=br, calib=cal, proxy_vs_contract=cmp, schedule=sched, by_brent=byB, margin_brent=mt, sens=sens, grids=grids, nd_A=ndA, nd_B=ND_CAP),
              open('calc/model_r5_out.json', 'w'), ensure_ascii=False, indent=1)
