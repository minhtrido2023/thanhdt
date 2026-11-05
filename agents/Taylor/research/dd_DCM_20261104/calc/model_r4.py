"""DCM r4 — thay ĐƯỜNG GIÁ KHÍ bằng lịch theo hợp đồng/CTCK. MÙ GIÁ (không nhận giá/vốn hoá/PE của DCM).
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
ND_PLATEAU = 0.81/1.5                              # [PL12 p28] tỷ trọng ND-UM theo LKNTĐ = 54%
ND_SHARE = {2028: 0.25*ND_PLATEAU,                 # (ước lượng) khí đầu 01/10/2028 (hạn chót hợp đồng Q4/2028)
            2029: ND_PLATEAU, 2030: ND_PLATEAU, 2031: ND_PLATEAU, 2032: ND_PLATEAU, 2033: ND_PLATEAU,   # bình ổn ≥55 tháng [PL12 p30]
            2034: 0.5*ND_PLATEAU}                  # (ước lượng) suy giảm; trữ lượng 4,44 tỷ Sm3 / ~0,7 tỷ Sm3/năm ≈ 6,3 năm (Tuổi Trẻ/PVN 20/04/2026)
LAST_Y = 2034                                      # từ 2035: trạng thái dài hạn = PM3/khí thay thế 50% quyền nhận PVN + 50% @13,7% Brent (ước lượng)

def gas_usd_mmbtu(y, B, variant='V1', freight=True):
    """Giá khí bình quân trước VAT (USD/MMBtu) năm y ở Brent B.
    Cấu trúc PM3 = 50% quyền nhận PVN + 50% phần Malaysia (BB25: chia 50/50; Đ10.1(b) PL12 phân bổ nguồn theo tỷ trọng tiêu thụ).
    Giá phần Malaysia sau 2027 KHÔNG CÔNG BỐ (HĐ mua bổ sung Petronas hết cuối 2027; UGSA mới 2028–2047 không công bố giá) ⇒ 2 cận:
    V1 = phần này rẻ ngang quyền nhận PVN (46% MFO) — tương đương giả định VDSC Bảng 4 (PVN 50%, Petronas 0% từ 2029);
    V2 = phần này giữ 13,7% Brent như 2027."""
    nd = ND_SHARE.get(y, 0.0) if y <= LAST_Y else 0.0
    p_nd = P0_ND*(1+ESC_ND)**max(0, y-2028)       # t=0 ở năm 2028 [PL12 p31]
    if y <= 2027:
        pm3 = 0.5*K_PVN*B + 0.5*K_PET[y]*B
    elif y > LAST_Y or variant == 'V2':
        pm3 = 0.5*K_PVN*B + 0.5*K_PET_POST*B
    else:
        pm3 = K_PVN*B
    return (1-nd)*pm3 + nd*p_nd + (FREIGHT if freight else 0.0)

def proxy_cost(B): return 25*(2.5+0.06*B)          # proxy Bobby, USD/t urê
def hist_cost(B, I=I_C): return I*gas_usd_mmbtu(2026, B)   # chế độ 2021–26 (ước lượng: 50/50 @12,7%)
HIST_B = {y: m.cm[y][1] for y in range(2021, 2026)}
def bias_hist(I=I_C): return sum(proxy_cost(b)-hist_cost(b, I) for b in HIST_B.values())/len(HIST_B)

def delta_spread(y, B, variant='V1', I=I_C):
    """Δ biên (USD/t) so với chế độ mà hồi quy r2 đã hấp thụ: [proxy(B) − chi phí HĐ(y,B)] − độ lệch TB 2021–25.
    Dương = lợi cho DCM. Gồm 2 phần: hiệu chỉnh độ dốc proxy (mọi năm) + thay đổi cơ cấu/giá theo năm."""
    return (proxy_cost(B) - I*gas_usd_mmbtu(y, B, variant)) - bias_hist(I)

def pv_gas(B, variant='V1', I=I_C, r=R0, mode='path'):
    """PV (đ/cp) của Δ chi phí khí sau thuế 20% và KTPL. t = y−2026 (năm 2027 ≈ năm 1 của r2). mode:
    'slope' = chỉ hiệu chỉnh độ dốc (cơ cấu chế độ cũ, mọi năm); 'path' = đường hợp đồng đủ; 'perm2030' = cơ cấu 2030 vĩnh viễn."""
    k = (1-TAX_LR)*(1-KTPL_RATE)*PROD_KT*1e3*USDVND/1e9
    pv = 0.0
    for y in range(2027, LAST_Y+1):
        d = (proxy_cost(B)-hist_cost(B, I)-bias_hist(I)) if mode == 'slope' else delta_spread(y, B, variant, I)
        pv += d*k/(1+r)**(y-2026)
    yy = 2030 if mode == 'perm2030' else LAST_Y+1
    d_lr = (proxy_cost(B)-hist_cost(B, I)-bias_hist(I)) if mode == 'slope' else delta_spread(yy, B, variant, I)
    if mode == 'perm2030':   # cơ cấu 2030 (ND 54%, giá ND đóng băng ở 2030) giữ mãi
        pv += d_lr*k/r/(1+r)**(LAST_Y-2026)
    else:
        pv += d_lr*k/r/(1+r)**(LAST_Y-2026)
    return ps(pv)

W_V = {'V1': 0.5, 'V2': 0.5}                       # (ước lượng) văn bản không nói giá phần PM3 sau 2028 ⇒ trọng số đều
def gas_center(B=BRENT_TC, I=I_C, r=R0):
    return sum(w*pv_gas(B, v, I, r) for v, w in W_V.items())

def ev_r4(B=BRENT_TC, I=I_C, r=R0, **kw):
    e = r2.ev_r2(r=r, **kw); g = gas_center(B, I, r)
    return {k: v+g for k, v in e.items()} | dict(gas=g)

if __name__ == '__main__':
    L = []; base = ev_r4(); b2 = r2.ev_r2()
    L.append(f'0. Hằng số: K_PVN {K_PVN:.4f}/USD Brent · ND P0 {P0_ND} +{ESC_ND:.2%}/năm · ND tỷ trọng bình ổn {ND_PLATEAU:.1%} · I_C {I_C} MMBtu/t · Brent TC {BRENT_TC:.1f} · độ lệch proxy−HĐ TB 2021–25 {bias_hist():+.1f} USD/t')
    # (c) đối chiếu proxy vs công thức HĐ & hiệu chỉnh từ TM38
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
        sched[round(B, 1)] = {y: dict(V1=round(gas_usd_mmbtu(y, B, 'V1'), 2), V2=round(gas_usd_mmbtu(y, B, 'V2'), 2),
                                       dV1=round(delta_spread(y, B, 'V1'), 1), dV2=round(delta_spread(y, B, 'V2'), 1))
                              for y in (2027, 2028, 2029, 2030, 2032, 2034, 2035)}
    L.append('2. Lịch giá khí trước VAT gồm cước (USD/MMBtu) và Δ biên (USD/t, dương = lợi) theo Brent phẳng: '+json.dumps(sched))
    L.append(f'3. Giá trị r4 (đ/cp, Brent {BRENT_TC:.1f}): CYC {base["CYC"]:,.0f} · ADMIN {base["ADMIN"]:,.0f} · STRUCT {base["STRUCT"]:,.0f} · KỲ VỌNG {base["EV"]:,.0f} (r2/r3 {b2["EV"]:,.0f}; Δ khí {base["gas"]:+,.0f})')
    # cầu nối r3 -> r4
    s_slope = sum(w*pv_gas(BRENT_TC, v, mode='slope') for v, w in W_V.items())
    br = dict(r3=round(b2['EV']), slope=round(s_slope), path_V1=round(pv_gas(BRENT_TC, 'V1')-s_slope), path_V2=round(pv_gas(BRENT_TC, 'V2')-s_slope),
              path_center=round(base['gas']-s_slope), r4=round(base['EV']))
    L.append('4. Cầu nối r3 -> r4 (đ/cp): '+json.dumps(br))
    byB = {}
    for B in (BRENT_TC, 82, 90, 103):
        byB[round(B, 1)] = dict(EV=round(ev_r4(B)['EV']), V1=round(pv_gas(B, 'V1')), V2=round(pv_gas(B, 'V2')), slope_only=round(sum(w*pv_gas(B, v, mode='slope') for v, w in W_V.items())),
                                perm2030_V1=round(pv_gas(B, 'V1', mode='perm2030')))
    L.append('5. Theo Brent phẳng (đ/cp; EV = kỳ vọng; V1/V2/slope = PV phần khí): '+json.dumps(byB))
    mt = {}
    for s in (150, 179, 220, 242, 260):
        mt[s] = {round(B, 1): round(ev_r4(B, s_tc=s)['EV']) for B in (BRENT_TC, 82, 90, 103)}
    L.append('6. Biên dài hạn × Brent -> kỳ vọng (đ/cp): '+json.dumps(mt))
    sens = dict(I25=round(ev_r4(I=25)['EV']), I20=round(ev_r4(I=20)['EV']),
                V1_only=round(r2.ev_r2()['EV']+pv_gas(BRENT_TC, 'V1')), V2_only=round(r2.ev_r2()['EV']+pv_gas(BRENT_TC, 'V2')))
    for d in (-1.0, -0.5, 0.5, 1.0): sens[f'dep{d:+.1f}_b1'] = round(ev_r4(r=rdep(DEP0+d))['EV'])
    _bak = dict(ND_SHARE)
    for tag, sh in (('nd30', 0.30), ('nd60', 269.74/445.5)):   # 30% = ND ~30% nhu cầu cụm Cà Mau (PVN/Tuổi Trẻ 20/04/2026) nếu phân bổ theo tỷ trọng tiêu thụ (Đ10.1(b) p32); 60,5% = LKNTT ND/LKNTT tổng [PL12 p26-27]
        ND_SHARE.update({y: (0.25*sh if y == 2028 else (0.5*sh if y == 2034 else sh)) for y in _bak})
        sens[tag] = round(ev_r4()['EV']); sens[tag+'_brent103'] = round(ev_r4(B=103)['EV'])
    ND_SHARE.clear(); ND_SHARE.update(_bak)
    _y0 = dict(ND_SHARE); ND_SHARE.update({2028: 0.0, 2029: 0.75*ND_PLATEAU})   # khí đầu trễ sang Q2/2029 (phạt giao thiếu áp từ 01/01/2029, p29)
    sens['nd_late_2029'] = round(ev_r4()['EV']); ND_SHARE.clear(); ND_SHARE.update(_y0)
    L.append('7. Độ nhạy (đ/cp): '+json.dumps(sens))
    def grid(stcs, Bs=(BRENT_TC,)):
        g = []
        for r_, stc, near_, st_, rc, B in itertools.product([rdep(DEP0+d) for d in (-1, -.5, 0, .5, 1)], stcs, [170, 222, 285], [100, 125, 150], [0, -RESTRICTED], Bs):
            g.append(ev_r4(B=B, r=r_, s_tc=stc, near=near_, struct=st_, nc_adj=-KTPL_BAL+rc)['EV'])
        g.sort(); n = len(g); q = lambda f: round(g[int(f*(n-1))])
        return dict(n=n, P10=q(.1), P25=q(.25), P50=q(.5), P75=q(.75), P90=q(.9))
    grids = dict(sym3=grid([138, m.spread_tc, 220]), sym5=grid([98, 138, m.spread_tc, 220, 260]), old270=grid([150, m.spread_tc, 210]),
                 sym3_brent4=grid([138, m.spread_tc, 220], (BRENT_TC, 82, 90, 103)))
    L.append('8. Lưới (r±100bp × biên TC × năm1 170/222/285 × STRUCT 100/125/150 × phong toả 0/−332; Brent 67,8 trừ khi ghi): '+json.dumps(grids))
    print('\n'.join(L)); open('calc/model_r4_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(dict(base=base, base_r2=b2, bridge=br, calib=cal, proxy_vs_contract=cmp, schedule=sched, by_brent=byB, margin_brent=mt, sens=sens, grids=grids),
              open('calc/model_r4_out.json', 'w'), ensure_ascii=False, indent=1)
