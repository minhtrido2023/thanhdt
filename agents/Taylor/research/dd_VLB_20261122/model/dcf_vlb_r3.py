"""DD VLB rev3 (23/11/2026) — mô hình MÙ GIÁ, đời mỏ THEO TỪNG MỎ = min(hạn giấy phép, trữ lượng ÷ sản lượng).
Chạy: python3 -I dcf_vlb_r3.py   (threads=1, thuần python). Đơn vị: tỷ VND.
Không ghi đè r2 (dcf_vlb.py). Thay đổi so với r2 + nguồn: REPORT_rev3.md mục "Đính chính so với rev trước".
Nguồn mới: src/BVSC_VLB_update_202602.pdf tr.7 (bảng 5 mỏ: công suất, hạn GP, trữ lượng; nguồn "VLB, Sở Xây dựng Đồng Nai"),
src/BVSC_VLB_initiation_202503.pdf tr.5, src/FPTS_VLB_update_20260406.pdf tr.2/4/6 (sản lượng 2025 từng mỏ, công suất 5,7 tr m³
nguyên khối ≈ 7,9 tr m³ thành phẩm), src/nhan_su_0617.pdf tr.2-4 (NQ ĐHĐCĐ 2026: LNTT 2025 kiểm toán 376,993; không có hạng mục đầu tư).
Giá thị trường CHỈ dùng cho thanh khoản (px_vlb.csv) sau khi khoá — không vào giá trị.
"""
import csv, math, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
SH = 46.720560  # triệu CP lưu hành [Q3 p22 23c]
R = 0.135        # V1: neo 13,5%; lãi huy động 12T hiệu dụng 7,4% (cctg_12m 02/11; Big-4 6,8% 16/11) = tại neo ⇒ Δ=0
DEP = 0.074      # lãi huy động 12T hiệu dụng (deposit_rate_vn.consumer_deposit_rate_detail(), last_update 2026-11-16)

# ---------- 1. Net cash THẬT 30/9/2026 (GIỮ r2 — skeptic r1 tính lại khớp 488,84) [Q3 p2-3] ----------
cash, htm = 27.576, 785.008
kt_pl, tax_pay, adv_cust = 107.466, 61.748, 76.938
gm_9t = 407.320 / 1233.930
adv_cost = adv_cust * (1 - gm_9t)
wc_liab = 37.560 + 54.215 + 0.377
wc_asset = 20.130 + 0.002762480 + 4.164 + 0.793
fund_accrued_9t = 565.970338 - 11.345 * 46.720560
net_cash = cash + htm - kt_pl - tax_pay - adv_cost - (wc_liab - wc_asset) - fund_accrued_9t
FUND_HI = (39.186778 + 5.538254) / 301.437   # 14,84% — NQ ĐHĐCĐ 2026 tr.2 (quỹ KTPL 39,187 + thưởng QL 5,538; LNST 301,437)
FUND_LO = (565.970338 - 11.345 * 46.720560) / (565.970338 - 343.929 * 0.8)
DIV_2026_INTERIM = 2500  # đ/cp tạm ứng 2026, GDKHQ 19/11/2026 — chỉ để quy tâm về cơ sở ex-div cho sổ (nằm trong net cash 30/9)

# ---------- 2. Mỏ: hạn GP + trữ lượng (BVSC 2/2026 tr.7) + sản lượng 2025 (FPTS 4/2026 tr.4,6) ----------
T0 = 2026.75                          # 30/9/2026
CONV = 7.9 / 5.7                      # m³ thành phẩm / m³ nguyên khối (FPTS tr.2)
YRS_SINCE_RES = 2.75                  # trữ lượng 3 mỏ chính "còn lại" = số cuối 2023 (BVSC 3/2025 tr.5 ghi "Hết năm 2023") → 30/9/2026
MINES = {  # cap: công suất GP (tr m³ nguyên khối/năm); exp: hết hạn GP (năm thập phân); res: trữ lượng (tr m³); sold25: tiêu thụ 2025 (tr m³ thành phẩm)
    'TC1': dict(cap=1.5, exp=2038.0, res=24.440115, sold25=2.43, res_age=2.75),
    'TP1': dict(cap=1.8, exp=2038.0, res=37.131154, sold25=2.30, res_age=2.75),
    'TT2': dict(cap=1.5, exp=2041.58, res=24.232408, sold25=2.20, res_age=2.75),
    # Soklu: trữ lượng bảng 2/2026 (giả định mốc 30/6/2025 — ước lượng); 0,66 tr m³ tiêu thụ 2025 chia theo công suất 4:5
    'SK2': dict(cap=0.4, exp=2031.83, res=2.303277, sold25=0.66 * 4 / 9, res_age=1.25),
    'SK5': dict(cap=0.5, exp=2029.58, res=1.723708, sold25=0.66 * 5 / 9, res_age=1.25),
}
TOT_SOLD = sum(m['sold25'] for m in MINES.values())
for k, m in MINES.items():
    m['rate'] = min(m['cap'], m['sold25'] / CONV)              # khai thác nguyên khối/năm (ước lượng)
    m['res_now'] = max(m['res'] - m['res_age'] * m['rate'], 0)
    m['life_lic'] = m['exp'] - T0
    m['life_res'] = m['res_now'] / m['rate']
    m['life'] = min(m['life_lic'], m['life_res'])
    m['share'] = m['sold25'] / TOT_SOLD                         # tỷ trọng LN ∝ sản lượng 2025 (ước lượng)

def lives(ext=None):
    """ext: dict mỏ -> năm hết hạn mới (gia hạn); đời vẫn bị chặn bởi trữ lượng."""
    out = {}
    for k, m in MINES.items():
        lic = (ext.get(k, m['exp']) if ext else m['exp']) - T0
        out[k] = min(lic, m['life_res'])
    return out

def share_active(t, L):  # t = năm thứ t (1..), phần năm còn hoạt động của từng mỏ
    return sum(m['share'] * max(0.0, min(1.0, L[k] - (t - 1))) for k, m in MINES.items())

# ---------- 3. Khoản bù trừ tiền cấp quyền 329,36 (non-cash, 163) ----------
offset_bal = 329.363
offset_use = 14.565383 / 0.75        # 19,42 tỷ/năm [H1 p30 / Q3 p19 V.17]
MAIN3 = ('TC1', 'TP1', 'TT2')        # khoản nộp thừa phát sinh ở 3 mỏ này [Q3 p19; báo chí 29/5/2026]
def offset_pv(r, L):
    """Dùng ∝ tỷ trọng sản lượng 3 mỏ chính còn hoạt động; hết đời mỏ ⇒ phần dư = 0 trong base (hoàn lại: KHÔNG KIỂM CHỨNG ĐƯỢC)."""
    w3 = sum(MINES[k]['share'] for k in MAIN3)
    bal, pv, t = offset_bal, 0.0, 1
    while bal > 1e-9 and t <= 40:
        act = sum(MINES[k]['share'] * max(0.0, min(1.0, L[k] - (t - 1))) for k in MAIN3) / w3
        use = min(bal, offset_use * act)
        if act <= 0: break
        pv += use / (1 + r) ** t; bal -= use; t += 1
    return pv, bal   # bal = dư chưa dùng khi 3 mỏ hết đời

# ---------- 4. Ký quỹ PHMT vượt dự phòng hoàn nguyên (skeptic r1: chưa đếm) ----------
DEPOSIT_EXCESS = 38.88 - 16.22       # ký quỹ 5 mỏ [Q3 p16] − dự phòng hoàn nguyên DH [Q3 p3/p21]; nhận lại khi đóng mỏ
def deposit_pv(r, L): return DEPOSIT_EXCESS / (1 + r) ** max(L['TC1'], L['TP1'])

# ---------- 5. LN vận hành sau thuế năm 1 (loại lãi tiền gửi, loại thu nhập khác, loại 343,93 một lần) ----------
# FY2025: LNTT kiểm toán 376,993 (NQ ĐHĐCĐ 2026 tr.1) − DTTC 31 − khác ròng 15 (BVSC 2/2026 tr.2; FPTS tr.5: lãi tiền gửi 30,1)
CORE_FY25 = (376.993 - 31.0 - 15.0) * 0.8
# TTM 9T/26 + Q4/25: LN HĐKD 9T/26 355,95 − DTTC 25,19 [Q3 p5]; Q4/25 op = op FY25 − op 9T/25 (op 9T/25 ước lượng: LNST 200,71/0,8 − DTTC ~21,7 − khác 14,05)
op_fy25 = 376.993 - 31.0 - 15.0
op_9t25 = 200.71 / 0.8 - 31.0 * 0.7 - 14.05      # ước lượng (DTTC 9T/25 ≈ 70% cả năm)
CORE_TTM = (355.95 - 25.19 + (op_fy25 - op_9t25)) * 0.8
NP_BASE = 310.0   # = trung điểm (CORE_FY25, CORE_TTM) làm tròn; r2 dùng 330
SCEN = {
    'xau':   dict(np1=250, g=0.00, w=0.25, offset=False, ext=None),
    'co_so': dict(np1=NP_BASE, g=0.02, w=0.50, offset=True, ext=None),
    'tot':   dict(np1=370, g=0.02, w=0.25, offset=True, ext={'TP1': 2042.58}),  # gia hạn TP1 tới hết thuê đất 31/7/2042 (QĐ 1537/QĐ-UBND)
}

def value(s, r=R, fund=FUND_HI, r_off=DEP, np1=None):
    L = lives(s['ext'])
    np1 = s['np1'] if np1 is None else np1
    op = sum(np1 * (1 - fund) * (1 + s['g']) ** (t - 1) * share_active(t, L) / (1 + r) ** t for t in range(1, 41))
    off, left = offset_pv(r_off, L) if s['offset'] else (0.0, offset_bal)
    dep = deposit_pv(r, L)
    return dict(op=op, off=off, left=left, dep=dep, L=L, v=(op + off + dep + net_cash) / SH * 1000)

def center(**kw):
    return sum(s['w'] * value(s, **kw)['v'] for s in SCEN.values())

# ---------- 6. Thanh khoản (SAU khoá; quy ước fleet như r2) ----------
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
    print(f"net_cash={net_cash:.2f} ty ({net_cash/SH*1000:,.0f} d/cp); CORE_FY25={CORE_FY25:.1f} CORE_TTM={CORE_TTM:.1f} -> NP_BASE {NP_BASE}")
    for k, m in MINES.items():
        print(f"  {k}: rate {m['rate']:.3f} res_now {m['res_now']:.2f} life_lic {m['life_lic']:.2f} life_res {m['life_res']:.2f} -> {m['life']:.2f} share {m['share']:.3f}")
    wl = sum(m['share'] * m['life'] for m in MINES.values()); print(f"  doi mo binh quan theo ty trong LN = {wl:.2f} nam (r2: 14)")
    tot = 0
    for k, s in SCEN.items():
        x = value(s); tot += s['w'] * x['v']
        print(f"{k:6s} op={x['op']:7.1f} off={x['off']:6.1f} (du {x['left']:.1f}) dep={x['dep']:.1f} -> {x['v']:9,.0f} d/cp w {s['w']}")
    print(f"TAM truoc CK = {tot:,.0f} | ex-div (-{DIV_2026_INTERIM}) = {tot-DIV_2026_INTERIM:,.0f}")
    d5 = d_liq(5); d1 = d_liq(1)
    print(f"thanh khoan: ADV250 {adv250:.2f} ADV68 {adv68:.2f} sigma {sig:.3%} CS {spread:.2%}; d(5ty)={d5:.2%} d(1ty)={d1:.2%}; phien thoat 5ty@20%ADV {5/(0.2*adv250):.1f}")
    sc = {k: value(s)['v'] for k, s in SCEN.items()}
    post = lambda v: v * (1 - d5)
    print("SAU CK 5ty (co so 30/9): tam {:,.0f} xau {:,.0f} co_so {:,.0f} tot {:,.0f}".format(post(tot), post(sc['xau']), post(sc['co_so']), post(sc['tot'])))
    print("SAU CK 5ty ex-div: tam {:,.0f} xau {:,.0f} co_so {:,.0f} tot {:,.0f}".format(*(post(v) - DIV_2026_INTERIM for v in (tot, sc['xau'], sc['co_so'], sc['tot']))))
    print("-- do nhay (truoc CK, % so tam) --")
    for dr in (-0.01, -0.005, 0.005, 0.01):
        print(f"  lai huy dong {dr*1e4:+.0f}bp b1: {center(r=R+dr):,.0f} ({center(r=R+dr)/tot-1:+.1%}); b0.5: {center(r=R+dr/2):,.0f}")
    for ke in (0.123, 0.134):
        print(f"  Ke dai noi dia {ke:.1%}: {center(r=ke):,.0f} ({center(r=ke)/tot-1:+.1%})")
    print(f"  offset chiet khau @Ke 13.5% (thay vi {DEP:.1%}): {center(r_off=R):,.0f} ({center(r_off=R)/tot-1:+.1%})")
    print(f"  quy LO 12.4%: {center(fund=FUND_LO):,.0f} ({center(fund=FUND_LO)/tot-1:+.1%})")
    b = SCEN['co_so']
    for npx in (265, 290, 357):
        v = value(b, np1=npx)['v']; print(f"  co_so np1={npx}: {v:,.0f} ({v/value(b)['v']-1:+.1%} vs co_so)")
    bg = dict(b, g=0.0); print(f"  co_so g=0: {value(bg)['v']:,.0f} ({value(bg)['v']/value(b)['v']-1:+.1%})")
    for tag, ext in (('gia han TP1 toi 2042', {'TP1': 2042.58}), ('gia han ca TC1/TP1/TT2 den het tru luong', {'TC1': 2060, 'TP1': 2060, 'TT2': 2060})):
        v = value(dict(b, ext=ext))['v']; print(f"  co_so + {tag}: {v:,.0f} ({v/value(b)['v']-1:+.1%})")
    xb = value(b); left_pv = xb['left'] / (1 + DEP) ** max(xb['L'][k] for k in MAIN3)
    print(f"  du bu tru chua dung {xb['left']:.1f} ty neu duoc HOAN tai dong mo: +{left_pv/SH*1000:,.0f} d/cp (khong kiem chung duoc, KHONG vao base)")
    # TC1 mất 20% trữ lượng (cote -80m sát đáy, FPTS tr.4): đời TC1 giới hạn trữ lượng
    save = MINES['TC1']['life_res']; MINES['TC1']['life_res'] = save * 0.8
    v = value(b)['v']; MINES['TC1']['life_res'] = save
    print(f"  co_so neu TC1 tru luong -20%: {v:,.0f} ({v/value(b)['v']-1:+.1%})")
    # V6 hai nen (hien thi)
    g = 0.02; roe = 0.40; reinv = min(max(g / roe, 0), 0.8)
    v_short = NP_BASE * (1 - FUND_HI) * (1 - reinv) / (R - g) / SH * 1000 + net_cash / SH * 1000
    v_long = value(b)['v']
    print(f"V6: V_ngan(Gordon vo han, +net cash)={v_short:,.0f} V_dai(huu han)={v_long:,.0f} D={abs(math.log(v_short/v_long)):.3f} (ln2={math.log(2):.3f})")
