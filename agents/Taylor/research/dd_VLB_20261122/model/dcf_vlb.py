"""DD VLB 2026-11-22 — mô hình định giá MÙ GIÁ (assumptions_file). Chạy: python3 -I dcf_vlb.py
Mọi số tỷ VND. Nguồn: BCTC Q3/2026 [Q3 p.x], BCTC bán niên [H1 p.x], NQ ĐHĐCĐ 2026, BQ ticker/ticker_financial.
Giá thị trường CHỈ dùng cho thanh khoản (px_vlb.csv) và so sánh cuối — không vào giá trị.
"""
import csv, math, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
SH = 46.720560  # triệu CP lưu hành [Q3 p22 23c]

# ---------- 1. Net cash THẬT 30/9/2026 [Q3 p2-3] ----------
cash, htm = 27.576, 785.008
kt_pl = 107.466          # quỹ KTPL (tiền của NLĐ)
tax_pay = 61.748         # thuế phải nộp
adv_cust = 76.938        # người mua trả trước
gm_9t = 407.320 / 1233.930
adv_cost = adv_cust * (1 - gm_9t)  # phần ứng trước phải tiêu để giao hàng (giá vốn)
wc_liab = 37.560 + 54.215 + 0.377  # phải trả NB + NLĐ + phải trả khác
wc_asset = 20.130 + 0.002762480 + 4.164 + 0.793  # tồn kho + phải thu KH (2.762.480 ĐỒNG, không phải 2,76 tỷ — r2) + trả trước NB + phải thu khác
# r2: quỹ KT-PL + thưởng BĐH trích 2025 = (39,187+5,538)/301,44 = 14,84% LNST [Q3 p22 23d]; EPS 9T/26 công bố 11.345 ngầm trừ
# 565,970 − 11,345×46,72056 ≈ 35,96 tỷ (≈12,4% LNST lõi 290,83) — khoản trích tạm 9T chưa chi, KHÔNG nằm trong 107,466 (BS) vì
# thuyết minh VCSH chưa ghi trích kỳ này. Trừ khỏi net cash.
FUND_HI = (39.186778 + 5.538254) / 301.44      # 14,84% — thực tế 2025 đã kiểm toán (BASE)
FUND_LO = (565.970338 - 11.345 * 46.720560) / (565.970338 - 343.929 * 0.8)  # ≈12,4% — ngầm theo EPS 9T/26
FUND = FUND_HI
fund_accrued_9t = 565.970338 - 11.345 * 46.720560
net_cash = cash + htm - kt_pl - tax_pay - adv_cost - (wc_liab - wc_asset) - fund_accrued_9t

# ---------- 2. Khoản bù trừ tiền cấp quyền (non-cash, 163) ----------
offset_bal = 329.363          # [Q3 p2 mã 163; p19 V.17]
# r2: dòng 163 là NET (gồm 7,04 tỷ phải thu tiền thuê đất ở 30/6, sang 30/9 thành phải trả 3,35) — KHÔNG dùng hiệu 341,256−329,363.
# Dòng con tiền cấp quyền chính: 9,710 (H1) → 14,565 (9T) [H1 p30 / Q3 p19 V.17] ⇒ 4,855/quý; 14,565/0,75 = 19,42 tỷ/năm.
offset_use = 14.565383 / 0.75
def pv_offset(r, life=None):
    n = offset_bal / offset_use                     # ~16,96 năm
    m = n if life is None else min(n, life)         # chỉ cấn trừ trong đời mỏ
    return offset_use * (1 - (1 + r) ** -m) / r, n
def offset_left(life):                              # số dư chưa dùng hết khi mỏ hết đời (hoàn lại hay không: CHƯA BIẾT)
    return max(offset_bal - offset_use * life, 0.0)

# ---------- 3. Kịch bản LN vận hành sau thuế (loại lãi tiền gửi + loại 343,93 một lần) ----------
# TTM core: Q4/25 100,73 (NQ 2026: 301,44 − 9T/25 200,71) + 9T/26 565,97 − 343,93×0,8
ttm_core = 100.73 + 565.97 - 343.929 * 0.8
SCEN = {  # LN vận hành năm 1 (ước lượng), đời mỏ còn lại (năm, ước lượng), g danh nghĩa, xác suất, giữ khoản bù trừ?
    # r2: đời mỏ 11/14/16 (r1: 12/15/18). Cơ sở 14 = ước lượng chính REPORT §4 (71 tr m³ ÷ 5,1 tr m³/năm), đã đếm đủ Tân Cang 1.
    # Tốt KHÔNG còn dựa 'Tân Cang 1 cấp lại' (đếm đôi với base) — chỉ dựa trữ lượng dưới cote/GĐ nói >24 tr m³ + sản lượng bền.
    'xau':   dict(np1=250, life=11, g=0.00, w=0.25, offset=False),
    'co_so': dict(np1=330, life=14, g=0.02, w=0.50, offset=True),
    'tot':   dict(np1=400, life=16, g=0.03, w=0.25, offset=True),
}

def pv_finite(x, r, g, n):
    q = (1 + g) / (1 + r)
    return x * (1 - q ** n) / (r - g)

def value(s, r, fund=None):
    fund = FUND if fund is None else fund
    op = pv_finite(s['np1'] * (1 - fund), r, s['g'], s['life'])
    off = pv_offset(r, s['life'])[0] if s['offset'] else 0.0
    return op, off, (op + off + net_cash) / SH * 1000  # đ/cp

# ---------- 4. Thanh khoản — quy ước fleet (SCL r3/TTA r3) ----------
rows = list(csv.DictReader(open(os.path.join(HERE, 'px_vlb.csv'))))
rows = rows[-250:]
tv = [float(r['Price']) * float(r['Volume']) / 1e9 for r in rows]
adv250 = st.median(tv); adv68 = st.median(tv[-68:])
cl = [float(r['Close']) for r in rows]
lr = [math.log(cl[i] / cl[i - 1]) for i in range(1, len(cl))]
sig = st.pstdev(lr)
def cs_spread(rs):  # Corwin-Schultz, 120 phiên
    out = []
    for a, b in zip(rs[:-1], rs[1:]):
        h1, l1, h2, l2 = map(float, (a['High'], a['Low'], b['High'], b['Low']))
        if min(l1, l2) <= 0: continue
        beta = math.log(h1 / l1) ** 2 + math.log(h2 / l2) ** 2
        gam = math.log(max(h1, h2) / min(l1, l2)) ** 2
        k = 3 - 2 * math.sqrt(2)
        al = (math.sqrt(2 * beta) - math.sqrt(beta)) / k - math.sqrt(gam / k)
        s = 2 * (math.exp(al) - 1) / (1 + math.exp(al))
        out.append(max(s, 0.0))
    return st.mean(out)
spread = cs_spread(rows[-120:])
def d_liq(q, adv): return spread / 2 + 1.0 * sig * math.sqrt(q / adv)

if __name__ == '__main__':
    R = 0.135
    print(f"net_cash_that={net_cash:.1f} ty = {net_cash/SH*1000:,.0f} d/cp (adv_cost {adv_cost:.1f}; WC rong {wc_liab-wc_asset:.1f})")
    pv, n = pv_offset(R); print(f"offset: su dung {offset_use:.2f} ty/nam, het sau {n:.1f} nam; PV(14 nam)@13.5% {pv_offset(R,14)[0]:.1f} ty ({pv_offset(R,14)[0]/SH*1000:,.0f} d/cp); PV@7% {pv_offset(0.07,14)[0]:.1f}; du chua dung khi mo het doi: life14 {offset_left(14):.1f} / life16 {offset_left(16):.1f} ty")
    print(f"fund: HI {FUND_HI:.2%} LO {FUND_LO:.2%}; trich tam 9T tru khoi net cash {fund_accrued_9t:.2f} ty")
    print(f"EPS loi TTM truoc trich {ttm_core/SH*1000:,.0f}; sau trich (HI) {ttm_core*(1-FUND_HI)/SH*1000:,.0f}; (LO) {ttm_core*(1-FUND_LO)/SH*1000:,.0f}")
    print(f"ttm_core_LNST={ttm_core:.1f}")
    tot = 0
    for k, s in SCEN.items():
        op, off, v = value(s, R); tot += s['w'] * v
        print(f"       fund-LO 12.4%: {value(s, R, FUND_LO)[2]:,.0f}")
        print(f"{k:6s} op_PV={op:7.1f} off={off:6.1f} -> {v:9,.0f} d/cp (w {s['w']})")
    print(f"TAM co trong so (truoc CK thanh khoan) = {tot:,.0f}")
    for dr in (-0.01, -0.005, 0.005, 0.01):
        t2 = sum(s['w'] * value(s, R + dr)[2] for s in SCEN.values())
        print(f"  lai huy dong {dr*1e4:+.0f}bp (beta1): {t2:,.0f} ({t2/tot-1:+.1%}); beta0.5: {sum(s['w']*value(s,R+dr/2)[2] for s in SCEN.values()):,.0f}")
    print(f"thanh khoan: ADV250 {adv250:.2f} ty, ADV68 {adv68:.2f}, sigma {sig:.3%}, CS spread {spread:.2%}")
    for q in (0.5, 1, 5):
        print(f"  Q={q} ty: d={d_liq(q,adv250):.2%} (ADV68 {d_liq(q,adv68):.2%}); phien thoat @20%ADV {q/(0.2*adv250):.1f}/{q/(0.2*adv68):.1f}")
    totlo = sum(s['w'] * value(s, R, FUND_LO)[2] for s in SCEN.values())
    print(f"TAM fund-LO truoc CK {totlo:,.0f} sau CK(5ty) {totlo*(1-d_liq(5,adv250)):,.0f}")
    print(f"PE loi ham y: tam sau CK / EPS loi sau trich = {tot*(1-d_liq(5,adv250))/(ttm_core*(1-FUND_HI)/SH*1000):.1f}x ; truoc trich {tot*(1-d_liq(5,adv250))/(ttm_core/SH*1000):.1f}x")
    d5 = d_liq(5, adv250); print(f"TAM sau CK (Q=5 ty) = {tot*(1-d5):,.0f}; Q=1 ty: {tot*(1-d_liq(1,adv250)):,.0f}")
    # Hai nen + C4 + D2 (hien thi)
    g = 0.02; roe = 0.40; reinv = min(max(g / roe, 0), 0.8)
    np_norm = st.median([218.0, 301.44, ttm_core])
    v_short = np_norm * (1 - FUND) * (1 - reinv) / (R - g) / SH * 1000
    v_long = value(SCEN['co_so'], R)[2]
    cfo3 = st.mean([300.4, 253.6, 345.6 + 343.929 * 0.2])  # 2024, 2025, TTM + thue da nop tren khoan mot lan
    cfo3 *= (1 - FUND)
    c4 = (cfo3 - 2.0) / (R - g) / SH * 1000
    d2 = (cfo3 - 0.1126 * 1614.4) / (R - g) / SH * 1000
    print(f"V_ngan={v_short:,.0f} (NP_norm {np_norm:.1f}) V_dai={v_long:,.0f} D={abs(math.log(v_short/v_long)):.3f} | C4={c4:,.0f} D2={d2:,.0f} (CFO3 {cfo3:.1f})")
    for tag, f in (('NONE: doi mo -3 nam', 3),):
        s = dict(SCEN['co_so']); s['life'] -= f
        print(f"  do nhay {tag}: co_so {value(s,R)[2]:,.0f}")
