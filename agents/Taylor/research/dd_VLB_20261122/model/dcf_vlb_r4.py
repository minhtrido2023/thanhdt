"""DD VLB rev4 (23/11/2026, vòng skeptic cuối) — mô hình MÙ GIÁ, đời mỏ theo từng mỏ = min(hạn GP, trữ lượng ÷ sản lượng).
Chạy: python3 -I dcf_vlb_r4.py   (threads=1, thuần python). Đơn vị: tỷ VND. Không ghi đè r3 (dcf_vlb_r3.py).
Thay đổi so với r3 (chi tiết: REPORT_rev4.md §1):
 (1) Hạn GP + trữ lượng: lấy từ NGUỒN SƠ CẤP của công ty — src/BCTN_2025.pdf tr.8 (trang in 14-15) "Tổng hợp trữ lượng khai thác
     còn lại của mỏ (đến 31/12/2025)", có SỐ GP: TP1 GP 1048/GP-UBND 11/04/2016 hạn 31/7/2042; TT2 GP 1362/GP-UBND 28/05/2015 hạn
     30/6/2038; TC1 GP 661/QĐ-UBND 28/02/2018 hạn 01/01/2039; SK2 GP 31/GP-UBND 28/02/2025 hạn 28/11/2031; SK5 GP 30/GP-UBND
     28/02/2025 hạn 28/08/2029. Thay bảng tổng hợp BVSC 2/2026 tr.7 (TC1/TP1 1/2038, TT2 8/2041) của r3.
 (2) LN lõi FY25 từ BCTC KIỂM TOÁN 2025 (src/BCTC_KiemToan_2025.pdf tr.13 (PDF), A&C chấp nhận toàn phần tr.7):
     LNTT 376,993 − DTTC 30,655 − LN khác 15,031 = 331,307 trước thuế ⇒ 265,05 sau thuế. FY24 cùng định nghĩa: 276,244 − 19,889 + 8,729.
 (3) Đường LN cơ sở: năm 1 = TTM lõi; phần vượt mức chu kỳ giữa (lõi FY25 kiểm toán × 1,02^t) giảm tuyến tính về 0 ở năm 3
     (cơ sở độc lập: KQKD kiểm toán FY24/FY25; BVSC 2/2026 tr.3 cầu cụm Tân Cang giảm sau Long Thành GĐ1; BCTN 2025: Long Thành GĐ1
     "cơ bản hoàn thành" 2025). Thay mức phẳng 310 của r3 (skeptic r2 killer objection).
 (4) Vốn lưu động: tiền khách ứng trước (ĐỦ 76,938) + WC ròng 67,06 là số dư quay vòng ⇒ tất toán khi từng mỏ đóng (PV @r, theo
     tỷ trọng mỏ), thay vì trừ ngay tại 30/9 (skeptic r2: lệch quy ước ≈ −4%).
Giá thị trường CHỈ dùng cho thanh khoản (px_vlb.csv) sau khi khoá — không vào giá trị.
"""
import csv, math, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
SH = 46.720560  # triệu CP lưu hành [Q3 p22 23c]
R = 0.135        # V1: neo 13,5%; lãi huy động 12T hiệu dụng 7,4% (cctg_12m 02/11; Big-4 6,8%; last_update 2026-11-16, đọc lại 23/11) ⇒ Δ=0
DEP = 0.074

# ---------- 1. Net cash 30/9/2026 [Q3 p2-3] — phần tức thời (không gồm số dư VLĐ quay vòng) ----------
cash, htm = 27.576, 785.008
kt_pl, tax_pay, adv_cust = 107.466, 61.748, 76.938
wc_liab = 37.560 + 54.215 + 0.377
wc_asset = 20.130 + 0.002762480 + 4.164 + 0.793
WC_NET = wc_liab - wc_asset                       # 67,06
fund_accrued_9t = 565.970338 - 11.345 * 46.720560  # 35,93
net_cash_now = cash + htm - kt_pl - tax_pay - fund_accrued_9t
# r3 (để đối chiếu): trừ ngay phần giá vốn của ứng trước + WC ròng
gm_9t = 407.320 / 1233.930
net_cash_r3 = net_cash_now - adv_cust * (1 - gm_9t) - WC_NET
FUND_HI = (39.186778 + 5.538254) / 301.437   # 14,84% — NQ ĐHĐCĐ 2026 tr.2
FUND_LO = (565.970338 - 11.345 * 46.720560) / (565.970338 - 343.929 * 0.8)
DIV_2026_INTERIM = 2500  # đ/cp tạm ứng 2026, GDKHQ 19/11/2026 (nằm trong net cash 30/9)

# ---------- 2. Mỏ: BCTN 2025 tr.8 (sơ cấp, có số GP), trữ lượng nguyên khối còn lại 31/12/2025 ----------
T0 = 2026.75
CONV = 7.9 / 5.7      # m³ thành phẩm / m³ nguyên khối (FPTS tr.2)
RES_AGE = 0.75        # 31/12/2025 → 30/9/2026
MINES = {  # exp: năm thập phân hết hạn GP; res: trữ lượng nguyên khối 31/12/2025 (tr m³); sold25: tiêu thụ 2025 (tr m³ thành phẩm, FPTS tr.4,6)
    'TC1': dict(cap=1.5, exp=2039.0,  res=22.571743, sold25=2.43),        # GP 661/QĐ-UBND, hạn 01/01/2039
    'TP1': dict(cap=1.8, exp=2042.58, res=35.407949, sold25=2.30),        # GP 1048/GP-UBND, hạn 31/7/2042
    'TT2': dict(cap=1.5, exp=2038.5,  res=22.527367, sold25=2.20),        # GP 1362/GP-UBND, hạn 30/6/2038
    'SK2': dict(cap=0.4, exp=2031.91, res=2.303277,  sold25=0.66 * 4 / 9),  # GP 31/GP-UBND, hạn 28/11/2031
    'SK5': dict(cap=0.5, exp=2029.66, res=1.613878,  sold25=0.66 * 5 / 9),  # GP 30/GP-UBND, hạn 28/08/2029
}
TOT_SOLD = sum(m['sold25'] for m in MINES.values())
for k, m in MINES.items():
    m['rate'] = min(m['cap'], m['sold25'] / CONV)
    m['res_now'] = max(m['res'] - RES_AGE * m['rate'], 0)
    m['life_lic'] = m['exp'] - T0
    m['life_res'] = m['res_now'] / m['rate']
    m['life'] = min(m['life_lic'], m['life_res'])
    m['share'] = m['sold25'] / TOT_SOLD

def lives(ext=None):
    out = {}
    for k, m in MINES.items():
        lic = (ext.get(k, m['exp']) if ext else m['exp']) - T0
        out[k] = min(lic, m['life_res'])
    return out

def share_active(t, L):
    return sum(m['share'] * max(0.0, min(1.0, L[k] - (t - 1))) for k, m in MINES.items())

# ---------- 3. Khoản bù trừ tiền cấp quyền 329,36 (non-cash, 163) — giữ r3 ----------
offset_bal = 329.363
offset_use = 14.565383 / 0.75
MAIN3 = ('TC1', 'TP1', 'TT2')
def offset_pv(r, L):
    w3 = sum(MINES[k]['share'] for k in MAIN3)
    bal, pv, t = offset_bal, 0.0, 1
    while bal > 1e-9 and t <= 40:
        act = sum(MINES[k]['share'] * max(0.0, min(1.0, L[k] - (t - 1))) for k in MAIN3) / w3
        if act <= 0: break
        use = min(bal, offset_use * act)
        pv += use / (1 + r) ** t; bal -= use; t += 1
    return pv, bal

# ---------- 4. Ký quỹ PHMT vượt dự phòng — giữ r3 ----------
DEPOSIT_EXCESS = 38.88 - 16.22
def deposit_pv(r, L): return DEPOSIT_EXCESS / (1 + r) ** max(L['TC1'], L['TP1'])

# ---------- 5. VLĐ quay vòng tất toán khi đóng mỏ (MỚI r4) ----------
WC_SETTLE = adv_cust + WC_NET   # 76,938 ứng trước (đủ, không chỉ phần giá vốn) + 67,06 WC ròng
def wc_pv(r, L):
    return sum(WC_SETTLE * m['share'] / (1 + r) ** L[k] for k, m in MINES.items())

# ---------- 6. LN lõi (loại lãi tiền gửi, loại LN khác, loại 343,93 một lần) ----------
OP_FY25 = 376.992904 - 30.655067 - 15.031106          # BCTC KT 2025 tr.13 (PDF)
OP_FY24 = 276.244024 - 19.889159 + 8.729055           # cùng trang, cột năm trước
CORE_FY25 = OP_FY25 * 0.8
CORE_FY24 = OP_FY24 * 0.8
op_9t25 = 200.71 / 0.8 - 30.655 * 0.7 - 14.05         # ước lượng (DTTC 9T/25 ≈ 70% cả năm; LN khác 9T/25 14,05 [Q3 p5 cột năm trước])
CORE_TTM = (355.95 - 25.19 + (OP_FY25 - op_9t25)) * 0.8
G = 0.02
def mid(t):   # mức chu kỳ giữa: lõi FY25 kiểm toán, tăng g từ giữa 2025 tới giữa năm t (năm 1 = 10/2026–9/2027, giữa ≈ 4/2027)
    return CORE_FY25 * (1 + G) ** (t + 0.75)
PREM = CORE_TTM - mid(1)
def np_fade(t, fade_years=2):
    return mid(t) + PREM * max(0.0, 1 - (t - 1) / fade_years)

SCEN = {
    'xau':   dict(path=lambda t: 250.0, w=0.25, offset=False, ext=None),
    'co_so': dict(path=np_fade, w=0.50, offset=True, ext=None),
    # tốt: giữ mức TTM (g 2%) + gia hạn 3 mỏ chính tới hết trữ lượng (BCTN 2025: thủ tục huy động 44,3 ha TC1; tiền lệ gia hạn Soklu)
    'tot':   dict(path=lambda t: CORE_TTM * (1 + G) ** (t - 1), w=0.25, offset=True, ext={'TC1': 2070, 'TP1': 2070, 'TT2': 2070}),
}

def value(s, r=R, fund=FUND_HI, r_off=DEP, path=None, ext='__s', wc_mode='close'):
    L = lives(s['ext'] if ext == '__s' else ext)
    p = s['path'] if path is None else path
    op = sum(p(t) * (1 - fund) * share_active(t, L) / (1 + r) ** t for t in range(1, 46))
    off, left = offset_pv(r_off, L) if s['offset'] else (0.0, offset_bal)
    dep = deposit_pv(r, L)
    if wc_mode == 'close':
        nc = net_cash_now - wc_pv(r, L)
    else:  # quy ước r3
        nc = net_cash_r3
    return dict(op=op, off=off, left=left, dep=dep, nc=nc, L=L, v=(op + off + dep + nc) / SH * 1000)

def center(scen=None, **kw):
    sc = scen or SCEN
    return sum(s['w'] * value(s, **kw)['v'] for s in sc.values())

# ---------- 7. Thanh khoản (SAU khoá; giữ r3) ----------
rows = list(csv.DictReader(open(os.path.join(HERE, 'px_vlb.csv'))))[-250:]
tv = [float(r['Price']) * float(r['Volume']) / 1e9 for r in rows]
adv250 = st.median(tv); adv68 = st.median(tv[-68:])
cl = [float(r['Close']) for r in rows]
sig = st.pstdev([math.log(cl[i] / cl[i - 1]) for i in range(1, len(cl))])
def cs_spread(rs):
    out = []
    for a, b in zip(rs[:-1], rs[1:]):
        h1, l1, h2, l2 = map(float, (a['High'], a['Low'], b['High'], b['Low']))
        if min(l1, l2) <= 0: continue
        beta = math.log(h1 / l1) ** 2 + math.log(h2 / l2) ** 2
        gam = math.log(max(h1, h2) / min(l1, l2)) ** 2
        k = 3 - 2 * math.sqrt(2)
        al = (math.sqrt(2 * beta) - math.sqrt(beta)) / k - math.sqrt(gam / k)
        out.append(max(2 * (math.exp(al) - 1) / (1 + math.exp(al)), 0.0))
    return st.mean(out)
spread = cs_spread(rows[-120:])
def d_liq(q, adv=adv250): return spread / 2 + sig * math.sqrt(q / adv)

if __name__ == '__main__':
    print(f"net_cash_now={net_cash_now:.2f} (r3 quy uoc {net_cash_r3:.2f}); WC_SETTLE={WC_SETTLE:.2f}")
    print(f"CORE_FY24={CORE_FY24:.1f} CORE_FY25={CORE_FY25:.2f} CORE_TTM={CORE_TTM:.1f} mid(1)={mid(1):.1f} PREM={PREM:.1f}")
    print("  duong LN co so t1..6: " + ", ".join(f"{np_fade(t):.1f}" for t in range(1, 7)))
    for k, m in MINES.items():
        print(f"  {k}: rate {m['rate']:.3f} res_now {m['res_now']:.2f} life_lic {m['life_lic']:.2f} life_res {m['life_res']:.2f} -> {m['life']:.2f} share {m['share']:.3f} du_tru_luong_khi_het_GP {max(m['res_now']-m['rate']*m['life_lic'],0):.2f}")
    wl = sum(m['share'] * m['life'] for m in MINES.values()); print(f"  doi mo binh quan theo ty trong LN = {wl:.2f} nam (r3: 11,2)")
    tot = 0; sc = {}
    for k, s in SCEN.items():
        x = value(s); tot += s['w'] * x['v']; sc[k] = x['v']
        print(f"{k:6s} op={x['op']:7.1f} off={x['off']:6.1f} (du {x['left']:.1f}) dep={x['dep']:.1f} nc={x['nc']:.1f} -> {x['v']:9,.0f} d/cp w {s['w']}")
    print(f"TAM truoc CK = {tot:,.0f} | ex-div (-{DIV_2026_INTERIM}) = {tot-DIV_2026_INTERIM:,.0f}")
    d5 = d_liq(5); d1 = d_liq(1)
    print(f"thanh khoan: ADV250 {adv250:.2f} ADV68 {adv68:.2f} sigma {sig:.3%} CS {spread:.2%}; d(5ty)={d5:.2%} d(1ty)={d1:.2%}; phien thoat 5ty@20%ADV {5/(0.2*adv250):.1f}")
    post = lambda v: v * (1 - d5)
    print("SAU CK 5ty (co so 30/9): tam {:,.0f} xau {:,.0f} co_so {:,.0f} tot {:,.0f}".format(post(tot), post(sc['xau']), post(sc['co_so']), post(sc['tot'])))
    print("SAU CK 5ty ex-div: tam {:,.0f} xau {:,.0f} co_so {:,.0f} tot {:,.0f}".format(*(post(v) - DIV_2026_INTERIM for v in (tot, sc['xau'], sc['co_so'], sc['tot']))))
    print("-- cau noi r3 -> r4 (tam truoc CK, them tung thay doi) --")
    # bước cầu: GP/trữ lượng BCTN; đường LN; VLĐ
    print(f"  r4 voi quy uoc VLD r3 (tru ngay): {center(wc_mode='r3'):,.0f}")
    print("-- do nhay (truoc CK, % so tam) --")
    for dr in (-0.01, -0.005, 0.005, 0.01):
        print(f"  lai huy dong {dr*1e4:+.0f}bp b1: {center(r=R+dr):,.0f} ({center(r=R+dr)/tot-1:+.1%}); b0.5: {center(r=R+dr/2):,.0f} ({center(r=R+dr/2)/tot-1:+.1%})")
    for ke in (0.123, 0.134):
        print(f"  Ke dai noi dia {ke:.1%}: {center(r=ke):,.0f} ({center(r=ke)/tot-1:+.1%})")
    print(f"  offset chiet khau @Ke 13.5%: {center(r_off=R):,.0f} ({center(r_off=R)/tot-1:+.1%})")
    print(f"  quy LO 12.4%: {center(fund=FUND_LO):,.0f} ({center(fund=FUND_LO)/tot-1:+.1%})")
    b = SCEN['co_so']; vb = value(b)['v']
    for tag, pth in (('phang 265 (loi FY25 KT, g0)', lambda t: CORE_FY25), ('phang 310 g2% (r3)', lambda t: 310 * 1.02 ** (t - 1)),
                     ('TTM giu (g2%)', lambda t: CORE_TTM * 1.02 ** (t - 1)), ('fade 1 nam', lambda t: np_fade(t, 1)), ('fade 4 nam', lambda t: np_fade(t, 4)),
                     ('mid = loi FY24 KT', lambda t: CORE_FY24 * 1.02 ** (t + 1.75))):
        v = value(b, path=pth)['v']; print(f"  co_so LN {tag}: {v:,.0f} ({v/vb-1:+.1%} vs co_so)")
    for tag, ext in (('gia han 3 mo chinh den het tru luong', {'TC1': 2070, 'TP1': 2070, 'TT2': 2070}), ('GP theo bang BVSC 2/2026 (r3)', {'TC1': 2038.0, 'TP1': 2038.0, 'TT2': 2041.58})):
        v = value(b, ext=ext)['v']; print(f"  co_so + {tag}: {v:,.0f} ({v/vb-1:+.1%})")
    for wt in (0.25, 0.50):
        sc2 = {'xau': dict(SCEN['xau'], w=(1 - wt) / 2 if wt != 0.25 else 0.25), 'co_so': dict(SCEN['co_so'], w=0.5 if wt == 0.25 else (1 - wt) / 2), 'tot': dict(SCEN['tot'], w=wt)}
        print(f"  trong so kich ban tot (gia han) {wt:.0%}: tam {center(scen=sc2):,.0f} ({center(scen=sc2)/tot-1:+.1%}) [w xau/co_so/tot = {sc2['xau']['w']:.3f}/{sc2['co_so']['w']:.3f}/{sc2['tot']['w']:.3f}]")
    print(f"  quy uoc VLD r3 (tru ngay phan gia von ung truoc + WC): {center(wc_mode='r3'):,.0f} ({center(wc_mode='r3')/tot-1:+.1%})")
    xb = value(b); left_pv = xb['left'] / (1 + DEP) ** max(xb['L'][k] for k in MAIN3)
    print(f"  du bu tru chua dung {xb['left']:.1f} ty neu duoc HOAN: +{left_pv/SH*1000:,.0f} d/cp (KHONG vao base)")
    print(f"  ky quy vuot du phong = 0 (skeptic r2: ky quy co the = chi phi hoan nguyen): -{deposit_pv(R, xb['L'])/SH*1000:,.0f} d/cp")
    truy = 270 * 0.8 / SH * 1000
    print(f"  STRESS ngoai mo hinh: truy thu kieu 2022 (~270 ty truoc thue, x0,8) = -{truy:,.0f} d/cp tren kich ban xau -> {sc['xau']-truy:,.0f} (HARD ABANDON)")
    g = 0.02; roe = 0.40; reinv = min(max(g / roe, 0), 0.8)
    v_short = np_fade(1) * (1 - FUND_HI) * (1 - reinv) / (R - g) / SH * 1000 + net_cash_now / SH * 1000
    print(f"V6: V_ngan(Gordon, LN nam1, +net cash)={v_short:,.0f} V_dai(huu han, co so)={vb:,.0f} D={abs(math.log(v_short/vb)):.3f} (ln2={math.log(2):.3f})")
