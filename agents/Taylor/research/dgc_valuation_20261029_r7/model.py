"""DGC định giá VÒNG 7 2026-10-29 (job Taylor_20261029_104456; nền = r6 ../dgc_valuation_20261027_r6, tái lập A 29.817 / B 34.695).
r7: Nghi Sơn XDCB 1.408,8 theo note 11 (CFG ns_cip) ; PE (DGC 10y + peer) áp lên LNST LÕI bỏ lãi tiền gửi rồi cộng cash_adj như SOTP (CFG pe_core).
(Docstring r5/r4 bên dưới giữ làm lịch sử.)
r5 2026-10-29 (job Taylor_20261029_042820; nền = r4 ../dgc_valuation_20261027_r4). READ-ONLY research.
r5 = r4 + BCTC hợp nhất Q3/2026 GỐC (MIKE_EXTRACT_BCTC_Q3_2026.md; ảnh p05,p06,r07,p08,p24,p26 Taylor đã mở lại và khớp). CFG_R4 tái lập đúng 33.766;
CFG_R5 là kết quả chính; waterfall r4→r5 bật dần từng công tắc (xem steps trong main()).
(Phần docstring r4 bên dưới giữ nguyên làm lịch sử.)
r4: 
r4 = r3 + số liệu GỐC BCTC hợp nhất Q2/2026 (MIKE_EXTRACT_BCTC_Q2_2026.md). CFG_R3 tái lập đúng 32.650; CFG_R4 là kết quả chính;
waterfall r3→r4 bật dần từng công tắc (thuế lãi 20%, lịch thuế lõi, terminal 20%, chuẩn hoá thuế PE/P-B, VCSH mẹ, lãi phải thu 326, cho vay 819, dự phòng 100).

Tái lập: python3 model.py  (chỉ cần pandas/numpy; đọc data/*.csv cùng thư mục, ghi out_*.csv).
Đơn vị: tỷ đồng, trừ khi ghi khác. Mọi input có nhãn nguồn [BQ]/[URL]/[UL]=ước lượng trong INPUTS.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261027)

# công tắc r4: sched = lõi theo lịch ưu đãi theo năm ; term_tax = thuế lõi terminal DCF ; norm = chuẩn hoá thuế lõi cho PE lõi/P-B/PE peer
# (None | "avg" = TB lịch 2027-34 | số) ; eqm = VCSH CÔNG TY MẸ (không gồm CĐKKS 417,6) ; x326 = lãi tiền gửi phải thu ;
# loan_h = haircut khoản cho vay 819 (None = không tính) ; prov = tỷ lệ trừ dự phòng ngắn hạn 100
# r5 công tắc: bs_cash/bs_eq/bs_ns = bảng cân đối 30/09 THẬT (tiền+gửi 9.761,2; vay 1.391,0; VCSH mẹ 13.073,9; XDCB NS) thay dựng lại ; prov200 = dự phòng 200 (r4: 100) ;
# q3act = Q1/Q2/Q3 THỰC (Q2 sau soát xét 380,1) ; q4new = cầu Q4 mới (doanh thu/biên/opex) ; gmnew = biên gộp 2027-28 hiệu chỉnh theo 9T thực ;
# w = trọng số kịch bản (thuận, cơ sở, nghịch)
CFG_R3 = dict(rf=0.074, uplift=1_000, pe_peer="now", pat=True, q4acc=True, mifin=True, mid=True, nsuni=True, tax_fin=0.13, mi_core=0.10,
              sched=False, term_tax=None, norm=None, eqm=False, x326=False, loan_h=None, prov=0.0,
              bs_cash=False, bs_eq=False, bs_ns=False, prov200=False, q3act=False, q4new=False, gmnew=False, w=(0.20, 0.50, 0.30))
CFG_R4 = dict(CFG_R3, tax_fin=0.20, sched=True, term_tax=0.20, norm="avg", eqm=True, x326=True, loan_h=0.50, prov=1.0)
# r5: tiền thật ⇒ bỏ HẲN 326/819 (đã thu hồi, thành tiền); dự phòng 200 trừ 100% như nợ; MI lõi 9% (9T thực 9,4%, Q3 7,2%); trọng số 0,25/0,5/0,25
CFG_R5 = dict(CFG_R4, bs_cash=True, bs_eq=True, bs_ns=True, x326=False, loan_h=None, prov200=True, q3act=True, q4new=True, gmnew=True, mi_core=0.09, w=(0.25, 0.50, 0.25))
# r6 (job Taylor_20261029_053128): áp phản biện fundamental-skeptic vòng 5.
# nền A = số gốc thuần: BCTC thật, biên 2027-28 như r4 (gmnew=False), w r4, KHÔNG uplift khai trường, trừ dự phòng 200 VÀ quỹ KTPL 592,8 (100%), bỏ thu hồi WC 300.
CFG_R5X = dict(CFG_R5, fund=0.0, wc27=300)
CFG_A = dict(CFG_R5X, gmnew=False, w=(0.20, 0.50, 0.30), uplift=0, fund=1.0, wc27=0)
CFG_B = dict(CFG_A, uplift=1_000)       # + uplift khai trường 25/19B (reopen 0,5 năm 2028 cơ sở ⇒ +500 LN gộp; thuận 0,5/1,0)
CFG_C = dict(CFG_B, gmnew=True)         # + biên cao r5 (18,0/18,5%) — CHỈ ĐỘ NHẠY, không có cầu nối
# r7 (job Taylor_20261029_104456): Nghi Sơn 1.408,8 [note 11 p30] ; PE lõi + cash_adj (pe_core_peer / pe_core_dgc)
CFG_A7 = dict(CFG_A, ns_cip=1408.8, pe_core_peer=True, pe_core_dgc=True)
CFG_B7 = dict(CFG_A7, uplift=1_000)
CFG_C7 = dict(CFG_B7, gmnew=True)
CFG = dict(CFG_A)

# ---------------------------------------------------------------- INPUTS
SH = 379.778413          # triệu cp [BQ ticker_financial.OShares 2026Q2]
PX = 32_900              # đ/cp, đóng cửa 2026-10-28 [BQ ticker.Close] ; TB 5 phiên 22-28/10 = 33.080 [BQ]
PX_AVG5 = 33_080
FX = 26_300              # VND/USD hàm ý Q2: 1.572 tỷ / 12,9 kt / 4.631 $ [DSC 10/08/2026]

NP_MI_Q1, NP_MI_Q2 = 408.8, 389.0   # LNST mẹ [BQ NP_P0 2026Q1; Vietcap flash 22/07 (BQ 380,1 lệch)]
NP_CONS_H1 = 871.0                  # LNST hợp nhất 6T [UL: Q1 ~430 ACBS + Q2 440 Vietcap]
Q3_MI = {"thuan": 420, "coso": 321, "nghich": 219}          # FORECAST.md khoá md5 d6ea39f4
Q3_CONS = {"thuan": 450, "coso": 350, "nghich": 246}
W = {"thuan": 0.20, "coso": 0.50, "nghich": 0.30}           # trọng số r4 = FORECAST.md Q3 ; r5 dùng CFG["w"]
# r5 [GỐC BCTC Q3 p05/p06/r07/p08]: số THẬT
Q3_ACT_MI, Q3_ACT_CONS, NP_MI_Q2_REV, NP_CONS_H1_REV = 478.2, 506.7, 380.1, 862.7   # Q2 mẹ sau soát xét: 1.267,1 − 478,2 − 408,8 = 380,1 ; hợp nhất H1 = 1.369,4 − 506,7
NP_MI_9T, NP_CONS_9T = 1267.1, 1369.4
CASH_ACT, DEBT_ACT, EQM_ACT, PROV_ACT = 9761.2, 1391.0, 13073.9, 200.0   # tiền 230,2 + gửi 9.531,0 ; vay NH ; VCSH 13.474,6 − CĐKKS 400,7 ; mã 322
NS_CIP_R6 = 1221 + 131.9      # [UL] r5/r6 ; r7 dùng note 11 = 1.408,8 qua CFG["ns_cip"] XDCB tổng 1.452,8 (+131,9 trong Q3) — giả định phần tăng Q3 là Nghi Sơn
Q4_NEW = {"thuan": (2500, 0.205, 5), "coso": (2350, 0.190, 0), "nghich": (2100, 0.165, -5)}   # (doanh thu, biên gộp, LN khác) [UL] — xem REPORT §2
Q4_OLD = {"thuan": (2450, 0.195, 0), "coso": (2250, 0.165, 0), "nghich": (2050, 0.135, 0)}
GM_NEW = {"nghich": [0.155, 0.160], "coso": [0.180, 0.185], "thuan": [0.205, 0.210]}       # [UL] biên gộp 2027-28 (9T thực 20,7%; Q2-Q3 TB 19,7%)

# Bảng cân đối — 30/06/2026 [Vietcap/Elibook/DSC, thứ cấp] → 30/09 dựng lại [UL]
CASH_DEP_0630 = 10_921   # tiền + tiền gửi
DEBT_0630 = 1_870        # vay ngắn hạn, không vay dài hạn [DSC]
DIV_PAID_0925 = 8_000 * SH / 1000   # 5.000 (còn lại 2025) + 3.000 (tạm ứng 2026), TT 25/09/2026 [doanhnhan.baophapluat 13/09]
CFO_Q3_UL, CAPEX_Q3_UL = 300, 250   # [UL] CFO Q3 (EBITDA lõi ~300 + lãi 185 − thuế − WC) ; capex chủ yếu Nghi Sơn
NET_CASH_0930 = CASH_DEP_0630 - DIV_PAID_0925 + CFO_Q3_UL - CAPEX_Q3_UL - DEBT_0630
BVPS_0630 = 42_744       # [BQ] — TRƯỚC khi trả 8.000 đ/cp ; TÍNH TRÊN VCSH GỒM CĐKKS (r3) — r4 dùng VCSH mẹ
EQ_MI_0630_R3 = BVPS_0630 * SH / 1000            # = 16.233 (gồm CĐKKS)
EQ_MOTHER_0630 = 15_823.9                         # [GỐC BCTC p06] VCSH 16.241,4 − CĐKKS 417,6
LOAN_819, INT_RECV_326, PROV_100 = 819.0, 326.2, 100.0   # [GỐC BCTC p05/p06/p25]


def gross0():
    return CASH_ACT if CFG["bs_cash"] else CASH_DEP_0630 - DIV_PAID_0925 + CFO_Q3_UL - CAPEX_Q3_UL


def debt():
    return DEBT_ACT if CFG["bs_cash"] else DEBT_0630


def net_cash():
    return gross0() - debt()


FUND_KTPL = 592.8         # quỹ khen thưởng phúc lợi (mã 323) [BCTC p06]


def prov_amt():
    return PROV_ACT if CFG["prov200"] else PROV_100


def liab_ded():
    """r6: nghĩa vụ trừ khỏi tiền ròng = dự phòng 200 × prov + quỹ KTPL 592,8 × fund (đồng nhất cùng một tỷ lệ khi đặt prov=fund)."""
    return prov_amt() * CFG["prov"] + FUND_KTPL * CFG.get("fund", 0.0)


def ns_cip():
    return CFG.get("ns_cip", NS_CIP_R6)


def ns_left():
    return NS_CAPEX_TOTAL - (ns_cip() if CFG["bs_ns"] else NS_CIP_0630 + 250)


def ns_book():
    return ns_cip() if CFG["bs_ns"] else NS_CIP_0630 + 250


def q3_pair(k):
    return (Q3_ACT_MI, Q3_ACT_CONS) if CFG["q3act"] else (Q3_MI[k], Q3_CONS[k])


def h1_pair():
    return (NP_MI_Q1 + (NP_MI_Q2_REV if CFG["q3act"] else NP_MI_Q2), NP_CONS_H1_REV if CFG["q3act"] else NP_CONS_H1)


def eq_mi_0930():
    if CFG["bs_eq"]:
        return EQM_ACT
    base = EQ_MOTHER_0630 if CFG["eqm"] else EQ_MI_0630_R3
    return base - DIV_PAID_0925 + Q3_MI["coso"]


def extras_book():
    """Giá trị SỔ SÁCH các khoản ngoài tiền+tiền gửi (để loại khỏi VCSH lõi, khỏi tính đôi)."""
    return (INT_RECV_326 if CFG["x326"] else 0) + (LOAN_819 if CFG["loan_h"] is not None else 0) - liab_ded()


def extras_value(k):
    """Giá trị quy về mẹ: lãi phải thu × (1−haircut pháp lý k) + cho vay 819 × (1−haircut riêng) − dự phòng. Tỷ đồng."""
    v = 0.0
    if CFG["x326"]:
        v += INT_RECV_326 * (1 - HC_LEGAL[k])
    if CFG["loan_h"] is not None:
        v += LOAN_819 * (1 - CFG["loan_h"])
    return v - liab_ded()


NS_CAPEX_TOTAL, NS_CIP_0630 = 2_400, 1_221      # Nghi Sơn GĐ1 [Vietcap/Nhadautu/DSC]
NS_CAPEX_LEFT_R4 = NS_CAPEX_TOTAL - NS_CIP_0630 - 250   # r4: trừ capex Q3 [UL] ; r5 dùng ns_left()

TAX = 0.13               # thuế hiệu dụng Q2 = 1 − 440/507 [Vietcap]
MI_SHARE = 0.10          # CĐKKS/LNST hợp nhất: Q2 11,6% ; Q3 ước 8% [FORECAST.md]
PAT_MI_CASH = 274        # r3: 49% × (tiền + đầu tư nắm giữ đến đáo hạn PAT 30/09 = 559 tỷ; chuyendongthitruong 25/10/2026); r2 = 365 [UL]
HC_LEGAL = {"thuan": 0.03, "coso": 0.09, "nghich": 0.29}   # haircut pháp lý còn lại sau khi tách PAT (r1: 5/15/35% gồm ~6pp PAT)

# Lịch thuế TNDN LÕI (không gồm lãi tiền gửi, không gồm Nghi Sơn) theo ưu đãi dự án (note 29 BCTC gốc) — tỷ trọng LNTT lõi theo dự án là [UL],
# hiệu chỉnh để năm 2026 ≈ 9,1% (phép thử 6T/2026: (131,3 − 20%×366,4)/(1.004,3 − 366,4) = 9,1%).
#  A  = lò P4 1-2 + silicate + hoạt động khác: 20% (hết ưu đãi từ 2024)                          25%
#  B  = rich phosphate+DCP, MAP, axit trích ly+TSP: 5% → (TSP 10% 2027-28; DCP/MAP 10% 2028) → 20% từ 2029  27%
#  L6 = lò P4 số 6: 5% đến 2031, 20% từ 2032                                                      18%
#  F1 = axit TP GĐ1: 5% đến 2028, 10% 2029-30, 20% từ 2031                                        10%
#  F2 = axit TP GĐ2: "giảm 50%" 2026-34, mức cơ sở không ghi ⇒ giả định 10% (cơ sở 20% × 50%)       8%
#  PT = PAT: 5% đến 2030, 10% 2031-32, 20% từ 2033                                                 12%
TAX_SHARES = dict(A=0.25, B=0.27, L6=0.18, F1=0.10, F2=0.08, PT=0.12)


def _rate(y):
    r = dict(A=0.20,
             B=0.05 if y == 2026 else (0.065 if y == 2027 else (0.10 if y == 2028 else 0.20)),
             L6=0.05 if y <= 2031 else 0.20,
             F1=0.05 if y <= 2028 else (0.10 if y <= 2030 else 0.20),
             F2=0.10 if y <= 2034 else 0.20,
             PT=0.05 if y <= 2030 else (0.10 if y <= 2032 else 0.20))
    return sum(TAX_SHARES[p] * r[p] for p in TAX_SHARES)


TAX_SCHED = {y: _rate(y) for y in range(2026, 2036)}
TAX_AVG_2734 = float(np.mean([TAX_SCHED[y] for y in range(2027, 2035)]))


def tax_core(y):
    return TAX_SCHED[min(max(y, 2026), 2035)] if CFG["sched"] else TAX


def t_norm():
    n = CFG["norm"]
    return None if n is None else (TAX_AVG_2734 if n == "avg" else float(n))


DEP_RATE = 0.068         # Big4 12T online [deposit_rate_vn_events.csv 2026-10-26]
SGA = 520                # BH+QLDN/năm: Q2 125,6×4 + lạm phát [DSC]

# ---------------------------------------------------------------- KỊCH BẢN (lõi, hợp nhất, KHÔNG gồm Nghi Sơn & TNTC)
# P4: sản lượng kt/năm, giá xuất $/t ; TPA kt, $/t ; khác (DAP/MAP, phụ gia, axit ướt, xút-clo, tẩy rửa…) tỷ/năm
# GM_base = biên gộp blended khi quặng NHẬP 100% ; ORE_UPLIFT = cộng LN gộp khi khai trường 25/19B chạy lại (tỷ/năm, tỷ lệ năm)
SCN = {
    "nghich": dict(p4_vol=50, p4_px=[3950, 3950], tpa_vol=66, tpa_px=1050, other=1200, gm=[0.145, 0.15],
                   reopen=[0.0, 0.0], ns_np=[-30, 50], ns_steady=70, sulfur="ME FOB ≥850 $/t kéo dài", dep=0.060),
    "coso":   dict(p4_vol=54, p4_px=[4150, 4250], tpa_vol=68, tpa_px=1100, other=1400, gm=[0.165, 0.175],
                   reopen=[0.0, 0.5], ns_np=[30, 110], ns_steady=165, sulfur="~700 $/t 2027 → 550 2028", dep=0.065),
    "thuan":  dict(p4_vol=58, p4_px=[4400, 4600], tpa_vol=70, tpa_px=1150, other=1700, gm=[0.18, 0.19],
                   reopen=[0.5, 1.0], ns_np=[100, 200], ns_steady=280, sulfur="về 450-500 $/t", dep=0.068),
}
# [UL] 500 kt/năm × (155−60=95 $/t) × 26.300 = 1.249 tỷ ở mức 100%; × 80% tự cung [DSC] = 999 ≈ 1.000 (r1 ghi 1.100 nhầm: 1.250 là mức 100%)
# uplift đọc từ CFG['uplift']


def ke():
    return CFG["rf"] + 1.0 * 0.075     # rf = max(Big-4 12M, CCTG 12M) = 7,4% (r2, quy ước fleet DCF) | r1: 6,8% ; β 1,0 ; ERP 7,5% [UL]


def fin_np(fin_gross, dep_rate, quarters=4.0):
    """LNST sau thuế của thu nhập tài chính ròng, thuộc mẹ. r2: CĐKKS KHÔNG ăn vào lãi tiền của DGC mẹ (chỉ phần tiền PAT)."""
    if CFG["mifin"]:
        return fin_gross * (1 - CFG["tax_fin"]) - PAT_MI_CASH * dep_rate * (quarters / 4) * (1 - CFG["tax_fin"])
    return fin_gross * (1 - CFG["tax_fin"]) * (1 - CFG["mi_core"])


def q4_bridge():
    """Cầu Q4/2026: LN gộp lõi + TNTC trên tiền ĐÃ trừ cổ tức 25/09."""
    rows = []
    q4p = Q4_NEW if CFG["q4new"] else Q4_OLD
    for k in ("thuan", "coso", "nghich"):
        rev, gm, oth = q4p[k]
        gp = rev * gm
        ebit = gp - (135 if CFG["q4new"] else 130)
        fi = gross0() * SCN[k]["dep"] / 4 + {"thuan": 10, "coso": 0, "nghich": -10}[k]
        core_c = ebit * (1 - tax_core(2026))
        np_c = core_c + (fi - 25) * (1 - CFG["tax_fin"]) + oth * (1 - tax_core(2026))
        core_mi = core_c * (1 - CFG["mi_core"])
        np_mi = core_mi + fin_np(fi - 25, SCN[k]["dep"], 1.0 * 1) + oth * (1 - tax_core(2026)) * (1 - CFG["mi_core"]) if CFG["mifin"] else (ebit + fi - 25) * (1 - tax_core(2026)) * (1 - CFG["mi_core"])
        rows.append(dict(scn=k, rev=rev, gm=gm, gp=round(gp), ebit=round(ebit), fin_inc=round(fi), pbt=round(ebit + fi - 25),
                         np_cons=round(np_c), np_mi=round(np_mi), core_mi=round(core_mi)))
    return pd.DataFrame(rows)


def q4(kind):
    return q4_bridge().set_index("scn")[kind]


def year_pnl(k, i, avg_gross_cash):
    s = SCN[k]
    rev_p4 = s["p4_vol"] * s["p4_px"][i] * FX / 1e6          # kt×$/t×VND → tỷ
    rev_tpa = s["tpa_vol"] * s["tpa_px"] * FX / 1e6
    rev = rev_p4 + rev_tpa + s["other"]
    gm_i = GM_NEW[k][i] if CFG["gmnew"] else s["gm"][i]
    gp = rev * gm_i + CFG["uplift"] * s["reopen"][i]
    ebit_core = gp - SGA
    fin = avg_gross_cash * s["dep"] - debt() * 0.065
    core_c = ebit_core * (1 - tax_core(2027 + i))
    np_cons = core_c + fin * (1 - CFG["tax_fin"]) + s["ns_np"][i]    # Nghi Sơn 100% DGC, NPAT trực tiếp
    if CFG["mifin"]:
        np_mi = core_c * (1 - CFG["mi_core"]) + fin_np(fin, s["dep"]) + s["ns_np"][i]
    else:
        np_mi = (ebit_core + fin) * (1 - tax_core(2027 + i)) * (1 - CFG["mi_core"]) + s["ns_np"][i]
    core_np_mi = core_c * (1 - CFG["mi_core"])
    return dict(scn=k, year=2027 + i, rev_core=round(rev), rev_p4=round(rev_p4), rev_tpa=round(rev_tpa), other=s["other"],
                gm_eff=round(gp / rev, 3), gp=round(gp), ebit_core=round(ebit_core), fin_net=round(fin),
                ns_np=s["ns_np"][i], np_cons=round(np_cons), np_mi=round(np_mi), core_np_mi=round(core_np_mi), ebit_core_raw=round(ebit_core),
                fin_np_mi=round(fin_np(fin, s["dep"])))


def forecasts():
    rows = []
    gross0_ = gross0()
    q4t = q4_bridge().set_index("scn")
    for k in SCN:
        h1_mi, h1_c = h1_pair(); q3m, q3c = q3_pair(k)
        fy26_mi = h1_mi + q3m + q4t.np_mi[k]
        fy26_c = h1_c + q3c + q4t.np_cons[k]
        rows.append(dict(scn=k, year=2026, np_mi=round(fy26_mi), np_cons=round(fy26_c)))
        # tiền gửi bình quân: trừ capex NS còn lại 2027, cổ tức 30%/năm (3.000 đ = 1.139 tỷ) từ 2027
        g27 = gross0_ - ns_left() * 0.8 - 1139 * 0.5 + 600
        g28 = g27 - 1139 + 900
        for i, g in enumerate([g27, g28]):
            rows.append(year_pnl(k, i, g))
    return pd.DataFrame(rows)


def prob_1600(sd_within=100, rho_cons=1.08, n=400_000, w=None, target=1600):
    """P(LNST cả năm 2026 ≥ target) cho 2 cách hiểu. Q1-Q3 ĐÃ BIẾT (9T mẹ 1.267,1 ; hợp nhất 1.369,4). Q4 = trộn 3 kịch bản (trọng số w) + sai số trong-kịch-bản
    N(0, sd_within) ; hợp nhất = mẹ-shock × rho_cons. sd tổng Q4 trả về trong 'sd_total'."""
    w = w or CFG["w"]
    rg = np.random.default_rng(20261029)
    q4t = q4_bridge().set_index("scn")
    ks = ["thuan", "coso", "nghich"]
    pick = rg.choice(3, size=n, p=list(w))
    e = rg.normal(0, sd_within, n)
    mi = np.array([q4t.np_mi[k] for k in ks])[pick] + e
    c = np.array([q4t.np_cons[k] for k in ks])[pick] + e * rho_cons
    need_mi, need_c = target - NP_MI_9T, target - NP_CONS_9T
    p_mi, p_c = float((mi >= need_mi).mean()), float((c >= need_c).mean())
    return dict(sd_within=sd_within, sd_total=round(float(mi.std()), 1), q4_mi_mean=round(float(mi.mean()), 1), q4_cons_mean=round(float(c.mean()), 1),
                need_q4_mi=round(need_mi, 1), p_mi=round(p_mi, 3), need_q4_cons=round(need_c, 1), p_cons=round(p_c, 3),
                p_5050=round(0.5 * p_mi + 0.5 * p_c, 3), p_7030=round(0.7 * p_mi + 0.3 * p_c, 3))


# ---------------------------------------------------------------- ĐỊNH GIÁ
G_BASE = 0.03
RONIC = 0.12            # [UL] lợi suất vốn đầu tư mới (Nghi Sơn GĐ1 cơ sở 165/2.400 ≈ 7% ; lõi P4 lịch sử cao hơn)
HAIRCUT = {"thuan": 0.05, "coso": 0.15, "nghich": 0.35}   # r1: haircut tiền ròng gộp (pháp lý + phần PAT/CĐKKS)
NS_MULT = {"thuan": 8, "coso": 7, "nghich": 6}
CORE_PE = {"thuan": 8, "coso": 7, "nghich": 6}            # PE LÕI (đã bỏ tiền) — DGC PE trung vị 10y 8,3 gồm cả lãi tiền gửi


def per_share(x):
    return x * 1000 / SH   # tỷ → đ/cp


def q4_core(k):
    return float(q4_bridge().set_index("scn").core_mi[k]) if CFG["q4acc"] else 0.0


def cash_adj(k):
    """Tiền ròng quy về cổ đông mẹ: (net − phần PAT-CĐKKS) × (1 − haircut pháp lý) + lõi Q4/2026 (kiếm được sau 30/09)."""
    if CFG["pat"]:
        c = (net_cash() - PAT_MI_CASH) * (1 - HC_LEGAL[k])
    else:
        c = net_cash() * (1 - HAIRCUT[k])
    return c + q4_core(k) + extras_value(k)


def norm_core(k, fc):
    """LNST mẹ LÕI chuẩn hoá (TB 2027-28). norm=None: theo lịch thuế từng năm (r3: 13%); norm≠None: quy về thuế t_norm()."""
    r = fc[(fc.scn == k) & (fc.year >= 2027)]
    if t_norm() is None:
        return float(r.core_np_mi.mean())
    return float((r.ebit_core * (1 - t_norm()) * (1 - CFG["mi_core"])).mean())


def ns_value(k):
    return SCN[k]["ns_steady"] * NS_MULT[k] / (1 + ke()) ** 2 - ns_left()


def sotp(fc):
    out = []
    for k in SCN:
        r = fc[(fc.scn == k) & (fc.year >= 2027)]
        core_norm = norm_core(k, fc)             # chuẩn hoá = TB 2027-28 (KHÔNG dùng đỉnh 2022-25)
        cash = cash_adj(k)
        core = core_norm * CORE_PE[k]
        ns = ns_value(k)
        tot = cash + core + ns
        out.append(dict(scn=k, net_cash_0930=round(net_cash()), pat_mi_cash=PAT_MI_CASH if CFG["pat"] else 0,
                        haircut=HC_LEGAL[k] if CFG["pat"] else HAIRCUT[k], q4_core_accr=round(q4_core(k)), cash_after_hc=round(cash),
                        core_np_mi_norm=round(core_norm), core_pe=CORE_PE[k], core_val=round(core),
                        nghison_val=round(ns), equity=round(tot),
                        ps_cash=round(per_share(cash)), ps_core=round(per_share(core)), ps_ns=round(per_share(ns)),
                        ps_total=round(per_share(tot))))
    return pd.DataFrame(out)


def dcf_core(k, k_e, g, gm_override=None, fc=None):
    """FCFF lõi (gồm Nghi Sơn hoạt động), không nợ dài hạn ⇒ WACC≈Ke. 2027-2031 rồi terminal Gordon.
    D&A ≈ capex duy tu [UL]. ΔWC: 2027 thu hồi 300 tồn kho dư (cơ sở/thuận), sau đó 0.
    r2 mid=True: định giá tại ~27/10/2026, dòng tiền giữa-năm ⇒ t = 0,68 + j (r1: 1..5 từ cuối kỳ)."""
    s = SCN[k]
    r = fc[(fc.scn == k) & (fc.year >= 2027)].set_index("year")
    ebit = [r.loc[2027, "ebit_core"], r.loc[2028, "ebit_core"]]
    if gm_override is not None:   # biên gộp dài hạn cố định (đã gồm hiệu ứng quặng)
        rev = r.loc[2028, "rev_core"]
        ebit = [rev * gm_override - SGA] * 2
    ebit += [ebit[-1] * (1 + g) ** j for j in (1, 2, 3)]
    ns = [s["ns_np"][0], s["ns_np"][1]] + [s["ns_steady"] * (1 + g) ** j for j in (0, 1, 2)]
    wc = [CFG.get("wc27", 300) if k != "nghich" else 0, 0, 0, 0, 0]
    pv = 0.0
    fcff = []
    reinv = g / RONIC   # tái đầu tư ròng để có tăng trưởng g (Damodaran: g = RR × RONIC)
    tt = [0.68 + j for j in range(5)] if CFG["mid"] else [j + 1.0 for j in range(5)]
    for t in range(5):
        f = (ebit[t] * (1 - tax_core(2027 + t)) * (1 - CFG["mi_core"]) + ns[t]) * (1 - (reinv if t >= 2 else 0)) + wc[t]
        fcff.append(f)
        pv += f / (1 + k_e) ** tt[t]
    f_T = fcff[-1]
    if CFG["term_tax"] is not None:   # terminal: lõi chịu thuế dài hạn (20%), Nghi Sơn giữ NPAT trực tiếp [UL: dự án mới có thể có ưu đãi riêng]
        f_T = (ebit[-1] * (1 - CFG["term_tax"]) * (1 - CFG["mi_core"]) + ns[-1]) * (1 - reinv) + wc[-1]
    tv = f_T * (1 + g) / (k_e - g) / (1 + k_e) ** (tt[-1] if CFG["mid"] else 5)
    cash = cash_adj(k) - ns_left()
    return per_share(pv + tv + cash)


def multiples(fc):
    """(c) PE lịch sử DGC & peer trên LNST mẹ 2027-28 (gồm lãi tiền gửi) + P/B chính đáng = (ROE−g)/(Ke−g).
    r2 nsuni: PE và P/B đều trừ NS capex còn lại 929; P/B tách NS (book 1.471) ra khỏi VCSH lõi và cộng giá trị NS như SOTP."""
    pm = pd.read_csv(os.path.join(HERE, "data", "peer_multiples.csv"))
    peers = pm[~pm.t.isin(["DGC", "PAT"])]
    pe_dgc10 = float(pm.loc[pm.t == "DGC", "PE_med10y"].iloc[0])
    pe_peer_now = float(peers.PE_now.median())
    pe_peer10 = float(peers.PE_med10y.median())
    out = []
    for k in SCN:
        e27 = float(fc[(fc.scn == k) & (fc.year == 2027)].np_mi.iloc[0])
        e28 = float(fc[(fc.scn == k) & (fc.year == 2028)].np_mi.iloc[0])
        e_norm = (e27 + e28) / 2
        core_sched = float(fc[(fc.scn == k) & (fc.year >= 2027)].core_np_mi.mean())
        core_n = norm_core(k, fc)
        net_adj = net_cash() - (PAT_MI_CASH if CFG["pat"] else 0)
        eq_core = eq_mi_0930() - net_adj - extras_book()     # VCSH phi-tiền (gồm tồn kho, TSCĐ, XDCB NS); r4: VCSH MẸ, loại 326/819/dự phòng
        adj = per_share(q4_core(k)) - (per_share(ns_left()) if CFG["nsuni"] else 0) + per_share(extras_value(k))
        e_norm_peer = e_norm - (core_sched - core_n)         # PE peer (thuế ~20%) áp trên LNST đã chuẩn hoá thuế lõi
        if CFG["nsuni"]:
            eq_core -= ns_book()
        roe = core_n / eq_core
        pb_j = max(roe - G_BASE, 0) / (ke() - G_BASE)
        if CFG["nsuni"]:   # lõi + tiền + NS (ns_value đã trừ capex còn lại)
            v_pb = per_share(pb_j * eq_core + cash_adj(k) + ns_value(k))
        else:
            v_pb = per_share(pb_j * eq_core + (cash_adj(k) if CFG["pat"] else net_cash() * (1 - HAIRCUT[k])))
        peer_pe = pe_peer_now if CFG["pe_peer"] == "now" else pe_peer10
        fin_mi = float(fc[(fc.scn == k) & (fc.year >= 2027)].fin_np_mi.mean())   # LNST lãi tiền gửi thuộc mẹ (TB 2027-28)
        adj_core = per_share(cash_adj(k) - ns_left())                            # như SOTP/DCF: tiền sau haircut + lõi Q4 − dự phòng/quỹ − capex NS còn lại
        v_dgc = per_share(e_norm - fin_mi) * pe_dgc10 + adj_core if CFG.get("pe_core_dgc") else per_share(e_norm) * pe_dgc10 + adj
        v_peer = (lambda pe: per_share(e_norm_peer - fin_mi) * pe + adj_core) if CFG.get("pe_core_peer") else (lambda pe: per_share(e_norm_peer) * pe + adj)
        out.append(dict(scn=k, np_mi_norm=round(e_norm), eps_norm=round(per_share(e_norm)), fin_np_mi=round(fin_mi), np_core_mi=round(e_norm - fin_mi),
                        v_pe_dgc10y=round(v_dgc), v_pe_peer_now=round(v_peer(pe_peer_now)),
                        v_pe_peer10y=round(v_peer(pe_peer10)), v_pe_peer_used=round(v_peer(peer_pe)),
                        roe_core=round(roe, 3), pb_justified=round(pb_j, 2), v_pb=round(v_pb),
                        cash_value_in_pe=round(pe_dgc10 * float(fc[(fc.scn == k) & (fc.year >= 2027)].fin_np_mi.mean()) / max(net_cash(), 1), 2)))
    return pd.DataFrame(out), dict(pe_dgc10=pe_dgc10, pe_peer_now=pe_peer_now, pe_peer10=pe_peer10)


def evaluate(W_=None):
    W_ = W_ or dict(zip(("thuan", "coso", "nghich"), CFG["w"]))
    fc = forecasts()
    so = sotp(fc)
    dc = pd.DataFrame([dict(scn=k, dcf=round(dcf_core(k, ke(), G_BASE, fc=fc))) for k in SCN])
    mu, refs = multiples(fc)
    summ = so[["scn", "ps_total"]].rename(columns={"ps_total": "sotp"}).merge(dc, on="scn").merge(
        mu[["scn", "v_pe_dgc10y", "v_pe_peer_used", "v_pb"]], on="scn")
    summ["multiple_avg"] = summ[["v_pe_dgc10y", "v_pe_peer_used", "v_pb"]].mean(1).round()
    summ["blend"] = summ[["sotp", "dcf", "multiple_avg"]].mean(1).round()
    summ["w"] = summ.scn.map(W_)
    ev = float((summ.blend * summ.w).sum())
    return dict(fc=fc, so=so, dc=dc, mu=mu, refs=refs, summ=summ, ev=ev)


def with_cfg(**kw):
    global CFG
    old = dict(CFG)
    CFG.update(kw)
    try:
        return evaluate()
    finally:
        CFG.clear(); CFG.update(old)


def ev_cfg(**kw):
    r = with_cfg(**kw); sm = r["summ"].set_index("scn")
    return r, dict(ev=round(r["ev"]), thuan=sm.blend["thuan"], coso=sm.blend["coso"], nghich=sm.blend["nghich"])


def row_of(**kw):
    r, row = ev_cfg(**kw); return row


def per_scn(cfg):
    r = with_cfg(**dict(dict(fund=0.0, wc27=300), **cfg)); sm = r["summ"].set_index("scn")
    return round(r["ev"]), int(sm.blend["thuan"]), int(sm.blend["coso"]), int(sm.blend["nghich"]), r


def main():
    pd.set_option("display.width", 250)
    csv = lambda n: os.path.join(HERE, n)
    out = []
    P = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
    # ---- tái lập
    e4 = per_scn(CFG_R4)[0]; e5 = per_scn(CFG_R5)[0]
    P(f"tái lập: CFG_R4 = {e4} (r4: 33.766) ; CFG_R5 = {e5} (r5: 40.302)")
    assert e4 == 33766 and e5 == 40302, "phải tái lập đúng r4/r5"
    # ---- tái lập số của skeptic (r5 bỏ/giữ từng thứ)
    P("\n== TÁI LẬP SỐ SKEPTIC ==")
    sk = [("r5 bỏ riêng uplift", dict(CFG_R5X, uplift=0)),
          ("gốc thuần (r5 + biên r4 + w r4), CÓ uplift 500; chưa quỹ KTPL, còn WC300", dict(CFG_R5X, gmnew=False, w=(0.2, 0.5, 0.3))),
          ("  — KHÔNG uplift", dict(CFG_R5X, gmnew=False, w=(0.2, 0.5, 0.3), uplift=0)),
          ("  + trừ quỹ KTPL 592,8: CÓ uplift", dict(CFG_R5X, gmnew=False, w=(0.2, 0.5, 0.3), fund=1.0)),
          ("  + trừ quỹ KTPL 592,8: KHÔNG uplift", dict(CFG_R5X, gmnew=False, w=(0.2, 0.5, 0.3), fund=1.0, uplift=0)),
          ("r5 bỏ WC 300", dict(CFG_R5X, wc27=0)),
          ("r5 + quỹ KTPL", dict(CFG_R5X, fund=1.0))]
    rows = []
    for lab, c in sk:
        v = per_scn(c)[:4]; rows.append(dict(case=lab, ev=v[0], thuan=v[1], coso=v[2], nghich=v[3])); P(f"{lab}: {v[0]}")
    pd.DataFrame(rows).to_csv(csv("out_skeptic_replication.csv"), index=False)
    # ---- dải phân tầng
    P("\n== DẢI PHÂN TẦNG ==")
    tiers = [("A gốc thuần: biên r4, w r4, không uplift, trừ dự phòng+quỹ KTPL 100%, bỏ WC300", CFG_A),
             ("B = A + uplift khai trường 500 (độ nhạy tách riêng)", CFG_B),
             ("C = B + biên cao r5 18,0/18,5% (KHÔNG có cầu nối ⇒ chỉ độ nhạy)", CFG_C),
             ("D r5 cũ (để so)", CFG_R5)]
    rows = []
    for lab, c in tiers:
        v = per_scn(c)[:4]; rows.append(dict(tier=lab, ev=v[0], thuan=v[1], coso=v[2], nghich=v[3], vs_px=round(v[0] / PX - 1, 3), vs_px5=round(v[0] / PX_AVG5 - 1, 3)))
    T = pd.DataFrame(rows); P(T.to_string(index=False)); T.to_csv(csv("out_tiers.csv"), index=False)
    # tầng A' = A + uplift đo bằng w r5? (không) ; tầng phụ: A với w r5 để thấy đóng góp trọng số
    # ---- waterfall r5 → r6
    P("\n== WATERFALL r5 → r6 ==")
    steps = [("r5 (tái lập)", {}),
             ("1 biên 2027-28 về r4 (cơ sở 16,5/17,5%; gỡ phán đoán +18,0/18,5)", dict(gmnew=False)),
             ("2 trọng số về r4 0,2/0,5/0,3 (gỡ phán đoán đếm đôi Q3)", dict(w=(0.2, 0.5, 0.3))),
             ("3 trừ quỹ khen thưởng phúc lợi 592,8 (100%, đồng nhất với dự phòng 200)", dict(fund=1.0)),
             ("4 bỏ 'thu hồi vốn lưu động 300' 2027 (tồn kho đã giảm 374 vào tiền)", dict(wc27=0)),
             ("5 bỏ uplift khai trường 500 khỏi nền = TẦNG A", dict(uplift=0))]
    cur = dict(CFG_R5X); wf = []
    for lab, kw in steps:
        cur.update(kw); v = per_scn(cur)[:4]; wf.append(dict(step=lab, ev=v[0], thuan=v[1], coso=v[2], nghich=v[3]))
    wf = pd.DataFrame(wf); wf["delta"] = wf.ev.diff(); P(wf.to_string(index=False)); wf.to_csv(csv("out_waterfall.csv"), index=False)
    assert wf.ev.iloc[-1] == T.ev.iloc[0], "waterfall cuối phải = tầng A"
    # thứ tự khác (kiểm độ phụ thuộc thứ tự): bỏ từng thứ riêng khỏi r5
    P("\n== bỏ RIÊNG từng thứ khỏi r5 (không phụ thuộc thứ tự) ==")
    ind = [("bỏ nâng biên", dict(gmnew=False)), ("bỏ đổi trọng số", dict(w=(0.2, 0.5, 0.3))), ("trừ quỹ KTPL", dict(fund=1.0)), ("bỏ WC300", dict(wc27=0)), ("bỏ uplift", dict(uplift=0))]
    ind = pd.DataFrame([dict(case=l, ev=per_scn(dict(CFG_R5X, **kw))[0], d=per_scn(dict(CFG_R5X, **kw))[0] - e5) for l, kw in ind]); P(ind.to_string(index=False)); ind.to_csv(csv("out_waterfall_individual.csv"), index=False)
    # ---- độ nhạy 0/50/100% dự phòng × quỹ KTPL (trên tầng A và B)
    P("\n== ĐỘ NHẠY dự phòng 200 (hàng) × quỹ KTPL 592,8 (cột), trừ 0/50/100% ==")
    g = []
    for nm, base in (("A", CFG_A), ("B", CFG_B)):
        for pv in (0.0, 0.5, 1.0):
            for fd in (0.0, 0.5, 1.0):
                g.append(dict(tier=nm, prov=pv, fund=fd, ev=per_scn(dict(base, prov=pv, fund=fd))[0]))
    g = pd.DataFrame(g); P(g.pivot_table(index=["tier", "prov"], columns="fund", values="ev").to_string()); g.to_csv(csv("out_sens_prov_x_fund.csv"), index=False)
    # ---- uplift 0/250/500/750/1000 trên nền A
    P("\n== ĐỘ NHẠY uplift khai trường (nền A) ==")
    u = pd.DataFrame([dict(uplift=x, ev=per_scn(dict(CFG_A, uplift=x))[0]) for x in (0, 250, 500, 750, 1000)]); P(u.to_string(index=False)); u.to_csv(csv("out_sens_uplift.csv"), index=False)
    # ---- độ nhạy biên (nền A: gmnew=False ⇒ GM_NEW không dùng; dùng SCN gm) — dịch pp
    P("\n== ĐỘ NHẠY biên gộp 2027-28 (nền A; r4 cơ sở 16,5/17,5) ==")
    old = {k: list(v["gm"]) for k, v in SCN.items()}; mrows = []
    try:
        for dpp in (-0.03, -0.02, -0.01, 0, 0.01, 0.015, 0.02, 0.03):
            for k in SCN: SCN[k]["gm"] = [x + dpp for x in old[k]]
            mrows.append(dict(dpp=dpp * 100, ev_A=per_scn(CFG_A)[0], ev_B=per_scn(CFG_B)[0]))
    finally:
        for k in SCN: SCN[k]["gm"] = old[k]
    m = pd.DataFrame(mrows); P(m.to_string(index=False)); m.to_csv(csv("out_sens_margin.csv"), index=False)
    # ---- cầu nối giá → giá vốn → biên (ràng buộc cơ học, KHÔNG hiệu chỉnh được)
    P("\n== CẦU NỐI (ràng buộc cơ học) ==")
    cogs_q = {"Q1": 2124.6 - 488.7, "Q2": 2415.4 - 455.8, "Q3": 2469.45 - 506.35}
    cogs_q3_ann = cogs_q["Q3"] * 4
    brows = []
    for k in SCN:
        s = SCN[k]
        for i, y in enumerate((2027, 2028)):
            rev = s["p4_vol"] * s["p4_px"][i] * FX / 1e6 + s["tpa_vol"] * s["tpa_px"] * FX / 1e6 + s["other"]
            for cs in (0.95, 1.0, 1.05, 1.10):
                brows.append(dict(scn=k, year=y, rev_model=round(rev), p4_share=round(s["p4_vol"] * s["p4_px"][i] * FX / 1e6 / rev, 3), cogs_scale_vs_Q3ann=cs,
                                  gm_implied=round(1 - cogs_q3_ann * cs / rev, 3), gm_r4=s["gm"][i], gm_r5=GM_NEW[k][i]))
    b = pd.DataFrame(brows); P(b[b.scn == "coso"].to_string(index=False)); b.to_csv(csv("out_bridge.csv"), index=False)
    # P4 giá Q2→Q3→Q4 (SunSirs) và độ nhạy biên theo giá cứng
    pw = pd.read_csv(os.path.join(HERE, "data", "phosphorus_weekly.csv"), parse_dates=["date"]); pw["q"] = pw.date.dt.to_period("Q")
    pq = pw.groupby("q").price_rmb.agg(["mean", "count"]).round(0); P("\nP4 SunSirs theo quý (Q1 chỉ 3 điểm, từ 03/2026):\n", pq.to_string()); pq.to_csv(csv("out_p4_quarters.csv"))
    # ĐỊNH LƯỢNG hai cách đọc Q4: giá bán chốt trễ 1 quý ⇒ Q4 hưởng giá Q3 (−16% vs Q2) ; share P4 65% doanh thu Q2
    sh = 0.65; shocks = []
    for dp in (0.0, -0.05, -0.10, -0.16):
        rev_scale = 1 + sh * dp; shocks.append(dict(dp_p4=dp, gm_if_cogs_flat=round(1 - cogs_q["Q3"] / (cogs_q["Q3"] / (1 - 0.205) * rev_scale), 3)))
    shocks = pd.DataFrame(shocks); P("\nGiá P4 xuất khẩu đổi dp (tỷ trọng 65% DT), giá vốn phẳng như Q3, từ biên Q3 20,5%:\n", shocks.to_string(index=False)); shocks.to_csv(csv("out_price_shock_margin.csv"), index=False)
    # ---- sản lượng P4 (thanh lý TSCĐ): cơ sở 54 kt ⇒ 49 kt (−9%)
    P("\n== ĐỘ NHẠY sản lượng P4 (tầng A) ==")
    vo = {k: SCN[k]["p4_vol"] for k in SCN}; vr = []
    try:
        for f in (1.0, 0.95, 0.90, 0.80):
            for k in SCN: SCN[k]["p4_vol"] = vo[k] * f
            vr.append(dict(p4_vol_factor=f, ev_A=per_scn(CFG_A)[0], ev_B=per_scn(CFG_B)[0]))
    finally:
        for k in SCN: SCN[k]["p4_vol"] = vo[k]
    vr = pd.DataFrame(vr); P(vr.to_string(index=False)); vr.to_csv(csv("out_sens_p4vol.csv"), index=False)
    # ---- biên Q4 cơ sở 19% vs r4 16,5%
    P("\n== ĐỘ NHẠY biên Q4/2026 cơ sở (nền A) ==")
    q4o = dict(Q4_NEW); qr = []
    try:
        for gm in (0.15, 0.165, 0.19, 0.205):
            Q4_NEW["coso"] = (2350, gm, 0); qr.append(dict(q4_gm_coso=gm, ev_A=per_scn(CFG_A)[0]))
    finally:
        Q4_NEW.update(q4o)
    qr = pd.DataFrame(qr); P(qr.to_string(index=False)); qr.to_csv(csv("out_sens_q4gm.csv"), index=False)
    # ---- WC 300 chỉ phần tồn kho vượt YE25 (404) ⇒ độ nhạy
    P("\n== ĐỘ NHẠY WC 2027 (nền A) ==")
    wr = pd.DataFrame([dict(wc27=x, ev_A=per_scn(dict(CFG_A, wc27=x))[0]) for x in (0, 100, 200, 300)]); P(wr.to_string(index=False)); wr.to_csv(csv("out_sens_wc.csv"), index=False)
    # ---- hai cách đọc 'dự phòng 200' (mã 322: +100 trong Q2, +100 trong Q3; mọi dòng chi phí bán hàng/QLDN/tài chính ở note 26-28 đều < 100 và không có dòng dự phòng ⇒ nếu qua KQKD thì ở GIÁ VỐN hoặc chi khác)
    P("\n== HAI CÁCH ĐỌC dự phòng 200 (nếu nằm trong GIÁ VỐN) ==")
    q = pd.DataFrame([dict(q=q_, rev=r_, cogs=c_, gm=round(1 - c_ / r_, 4), gm_ex_prov=round(1 - (c_ - p_) / r_, 4), prov_q=p_) for q_, r_, c_, p_ in
                      [("Q1", 2124.6, 2124.6 - 488.7, 0), ("Q2", 2415.4, 2415.4 - 455.8, 100), ("Q3", 2469.45, 2469.45 - 506.35, 100)]]); P(q.to_string(index=False)); q.to_csv(csv("out_prov_in_cogs.csv"), index=False)
    ann_ex = (cogs_q["Q3"] - 100) * 4
    rr = []
    for k in ("coso",):
        for i in (0, 1):
            s_ = SCN[k]; rev = s_["p4_vol"] * s_["p4_px"][i] * FX / 1e6 + s_["tpa_vol"] * s_["tpa_px"] * FX / 1e6 + s_["other"]
            rr.append(dict(scn=k, year=2027 + i, gm_R1_recurring=round(1 - cogs_q3_ann / rev, 3), gm_R2_oneoff=round(1 - ann_ex / rev, 3), gm_r4=s_["gm"][i]))
    rr = pd.DataFrame(rr); P(rr.to_string(index=False)); rr.to_csv(csv("out_prov_readings_margin.csv"), index=False)
    gmo = {k: list(v["gm"]) for k, v in SCN.items()}; res = []
    try:
        for lab, key in (("R1 lặp lại (giá vốn Q3 giữ nguyên)", "gm_R1_recurring"), ("R2 một lần (giá vốn Q3 trừ 100/quý)", "gm_R2_oneoff")):
            shift = [float(rr[(rr.scn == "coso") & (rr.year == 2027 + i)][key].iloc[0]) - gmo["coso"][i] for i in (0, 1)]   # dịch pp suy từ cơ sở, áp đồng loạt (đồng nhất giá vốn cố định chỉ có nghĩa ở cơ sở)
            for k in SCN: SCN[k]["gm"] = [gmo[k][i] + shift[i] for i in (0, 1)]
            res.append(dict(reading=lab, shift_pp_27_28=[round(x * 100, 1) for x in shift], ev_A=per_scn(CFG_A)[0], ev_B=per_scn(CFG_B)[0]))
    finally:
        for k in SCN: SCN[k]["gm"] = gmo[k]
    res = pd.DataFrame(res); P(res.to_string(index=False)); res.to_csv(csv("out_prov_readings_ev.csv"), index=False)
    # ---- Nghi Sơn XDCB thật theo note 11: 1.408,8 (r5 dùng 1.352,9 = 1.221+131,9)
    ns_ev = (per_scn(dict(CFG_A, ns_cip=1408.8))[0], per_scn(dict(CFG_B, ns_cip=1408.8))[0])
    P(f"\nNghi Sơn XDCB theo note 11 = 1.408,8 (còn lại {NS_CAPEX_TOTAL - 1408.8:.0f}) thay 1.352,9: A {ns_ev[0]} (vs 29.817) ; B {ns_ev[1]} (vs 34.695)")
    pd.DataFrame([dict(ns_cip=1408.8, ev_A=ns_ev[0], ev_B=ns_ev[1])]).to_csv(csv("out_sens_ns_cip.csv"), index=False)
    # ---- đối chiếu phi-tiền (số học, từ BCTC)
    P("\n== ĐỐI CHIẾU LCTT / BẢNG CÂN ĐỐI (số học) ==")
    P(f"CFI: tổng các dòng 21-27 = {-511.577651602 + 332.292128775 - 11822.654805164 + 14309.522071726 + 542.920910695:.2f} vs dòng 30 in 2.802,27 (lệch {-511.577651602 + 332.292128775 - 11822.654805164 + 14309.522071726 + 542.920910695 - 2802.274776360:.2f}); dòng 20+30+40 = 50 và tiền cuối kỳ 230,18 KHỚP bảng cân đối ⇒ dòng TỔNG khớp tiền")
    nbv = 350.312275922 - 66.248025217
    P(f"TSCĐ hữu hình note 10(a): nguyên giá thanh lý 350,31 − khấu hao lũy kế thanh lý 66,25 = giá trị còn lại {nbv:.2f} ; thu thanh lý in 332,29 ⇒ chênh {332.292128775 - nbv:.2f} (≈ 48,23 lệch LCTT: {332.292128775 - nbv - 48.227878:.3f})")
    gap_prin = (12065 - 9437.8) - (14309.5 - 11822.7); gap_int = (527.5 + 331 - 93.2) - 542.9
    P(f"tiền gửi kỳ hạn: gốc giảm {12065 - 9437.8:.1f} vs net LCTT (thu hồi − cho vay) {14309.5 - 11822.7:.1f} ⇒ {gap_prin:.1f} không qua tiền [gốc 12.065 = số Mike chép]; lãi: kỳ vọng thu = 527,5 + dự thu đầu 331 − dự thu cuối 93,2 = {527.5 + 331 - 93.2:.1f} vs LCTT 542,9 ⇒ {gap_int:.1f}; tổng ≈ {gap_prin + gap_int:.0f}")
    P(f"XDCB Q3 +131,9 + trả trước người bán +110,8 = {131.9 + 110.8:.1f} vs chi XDCB tiền Q3 ≈ 18,6 (511,6 − H1 493,0 theo Mike) ⇒ ≈ {131.9 + 110.8 - 18.6:.1f} không qua tiền; phải trả người bán chỉ +1,8")
    # ---- chi tiết tầng A
    cfg_save = dict(CFG); CFG.clear(); CFG.update(CFG_A)
    R = evaluate(); fc, so, dc, mu, summ = R["fc"], R["so"], R["dc"], R["mu"], R["summ"]
    P("\nTầng A — tổng hợp\n", summ.to_string(index=False)); P(so.to_string(index=False)); P(fc.to_string(index=False))
    for nm, df in [("forecast", fc), ("sotp", so), ("dcf", dc), ("multiples", mu), ("summary", summ)]: df.to_csv(csv(f"out_A_{nm}.csv"), index=False)
    pr = pd.DataFrame([prob_1600(sd) for sd in (70, 100, 140)]); P("P(>=1.600), nền A (w r4):\n", pr.to_string(index=False)); pr.to_csv(csv("out_prob_1600.csv"), index=False)
    P("giá", PX, "TB5", PX_AVG5, "; tiền ròng/cổ phiếu", round(per_share(net_cash())), "; sau PAT 274 và haircut 9%:", round(per_share((net_cash() - PAT_MI_CASH) * (1 - 0.09))))
    CFG.clear(); CFG.update(cfg_save)
    open(csv("run_stdout.txt"), "w").write("\n".join(out))


def main_r7():
    """r7: tái lập r6 (A 29.817 / B 34.695) rồi áp sửa của fundamental-skeptic trên r6."""
    csv = lambda n: os.path.join(HERE, n)
    out = []
    P = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
    eA, eB = per_scn(CFG_A)[0], per_scn(CFG_B)[0]
    P(f"tái lập r6: A = {eA} (29.817) ; B = {eB} (34.695)")
    assert eA == 29817 and eB == 34695, "phải tái lập đúng r6"
    # ---- waterfall r6 → r7 (A và B)
    P("\n== WATERFALL r6 → r7 ==")
    steps = [("r6 (tái lập)", {}),
             ("1 Nghi Sơn XDCB 1.408,8 (note 11) thay 1.352,9", dict(ns_cip=1408.8)),
             ("2 PE peer áp LNST LÕI (bỏ lãi tiền gửi) + cash_adj", dict(pe_core_peer=True)),
             ("3 PE DGC 10y áp LNST LÕI (bỏ lãi tiền gửi) + cash_adj", dict(pe_core_dgc=True))]
    wf = []
    for nm, base in (("A", CFG_A), ("B", CFG_B)):
        cur = dict(base)
        for lab, kw in steps:
            cur.update(kw); v = per_scn(cur)[:4]; wf.append(dict(tier=nm, step=lab, ev=v[0], thuan=v[1], coso=v[2], nghich=v[3]))
    wf = pd.DataFrame(wf); wf["delta"] = wf.groupby("tier").ev.diff(); P(wf.to_string(index=False)); wf.to_csv(csv("out_r7_waterfall.csv"), index=False)
    eA7, eB7 = per_scn(CFG_A7)[0], per_scn(CFG_B7)[0]
    assert wf[wf.tier == "A"].ev.iloc[-1] == eA7 and wf[wf.tier == "B"].ev.iloc[-1] == eB7
    # ---- dải biên ĐỐI XỨNG quanh nền r4 (−2/−1/0/+1/+2pp 2027-28, mọi kịch bản)
    P("\n== DẢI BIÊN ĐỐI XỨNG (A7/B7) ==")
    old = {k: list(v["gm"]) for k, v in SCN.items()}; mrows = []
    try:
        for dpp in (-0.02, -0.01, 0, 0.01, 0.02):
            for k in SCN: SCN[k]["gm"] = [x + dpp for x in old[k]]
            mrows.append(dict(dpp=round(dpp * 100), ev_A7=per_scn(CFG_A7)[0], ev_B7=per_scn(CFG_B7)[0]))
    finally:
        for k in SCN: SCN[k]["gm"] = old[k]
    m = pd.DataFrame(mrows); P(m.to_string(index=False)); m.to_csv(csv("out_r7_margin_band.csv"), index=False)
    # ---- lưu huỳnh: ràng buộc cơ học (KHÔNG hiệu chỉnh) — giá vốn Q3×4 điều chỉnh theo tỷ trọng S [UL] × ΔS
    P("\n== LƯU HUỲNH → biên 2027 cơ sở (ràng buộc cơ học, tỷ trọng S trong giá vốn là [UL]) ==")
    cogs_q3_ann = (2469.45 - 506.35) * 4
    s_ = SCN["coso"]; rev27 = s_["p4_vol"] * s_["p4_px"][0] * FX / 1e6 + s_["tpa_vol"] * s_["tpa_px"] * FX / 1e6 + s_["other"]
    S_Q3 = 900   # [UL] ME FOB Q3/2026 ≈ 880-960 (T9 suy ngược 880/865/960; đỉnh index 947 T7) — Bobby §1
    srows = []
    for s27, lab in ((835, "giữ T10 Qatar 835"), (700, "r6 cơ sở 700"), (615, "Bobby trung vị ~650 T1 / ~580 T4"), (500, "K2 xả hàng 400-600")):
        for share in (0.06, 0.12):
            cs = 1 + share * (s27 / S_Q3 - 1)
            srows.append(dict(s_2027=s27, case=lab, s_share_cogs=share, cogs_scale=round(cs, 4), gm_2027=round(1 - cogs_q3_ann * cs / rev27, 3)))
    sr = pd.DataFrame(srows); P(sr.to_string(index=False)); sr.to_csv(csv("out_r7_sulfur_bridge.csv"), index=False)
    # ---- tầng r7
    P("\n== DẢI PHÂN TẦNG r7 ==")
    rows = []
    for lab, c in (("A7 = A r6 + Nghi Sơn 1.408,8 + PE lõi + cash_adj", CFG_A7), ("B7 = A7 + uplift khai trường", CFG_B7),
                   ("C7 = B7 + biên cao r5 (chỉ độ nhạy)", CFG_C7), ("A r6 (để so)", CFG_A), ("B r6 (để so)", CFG_B)):
        v = per_scn(c)[:4]; rows.append(dict(tier=lab, ev=v[0], thuan=v[1], coso=v[2], nghich=v[3], vs_px=round(v[0] / PX - 1, 3)))
    T = pd.DataFrame(rows); P(T.to_string(index=False)); T.to_csv(csv("out_r7_tiers.csv"), index=False)
    # ---- hai cách đọc dự phòng (R1/R2) trên A7/B7 — dịch biên cơ sở như r6
    gmo = {k: list(v["gm"]) for k, v in SCN.items()}; res = []
    s_ = SCN["coso"]; revs = [s_["p4_vol"] * s_["p4_px"][i] * FX / 1e6 + s_["tpa_vol"] * s_["tpa_px"] * FX / 1e6 + s_["other"] for i in (0, 1)]
    try:
        for lab, cogs in (("R1 lặp lại ~100/quý", cogs_q3_ann), ("R2 một lần", cogs_q3_ann - 400)):
            shift = [(1 - cogs / revs[i]) - gmo["coso"][i] for i in (0, 1)]
            for k in SCN: SCN[k]["gm"] = [gmo[k][i] + shift[i] for i in (0, 1)]
            res.append(dict(reading=lab, gm27=round(1 - cogs / revs[0], 3), gm28=round(1 - cogs / revs[1], 3), ev_A7=per_scn(CFG_A7)[0], ev_B7=per_scn(CFG_B7)[0]))
    finally:
        for k in SCN: SCN[k]["gm"] = gmo[k]
    res = pd.DataFrame(res); P("\n", res.to_string(index=False)); res.to_csv(csv("out_r7_prov_readings.csv"), index=False)
    # ---- dự phòng × quỹ KTPL trên A7
    g = pd.DataFrame([dict(prov=pv, fund=fd, ev_A7=per_scn(dict(CFG_A7, prov=pv, fund=fd))[0]) for pv in (0.0, 0.5, 1.0) for fd in (0.0, 0.5, 1.0)])
    P("\n", g.pivot_table(index="prov", columns="fund", values="ev_A7").to_string()); g.to_csv(csv("out_r7_prov_x_fund.csv"), index=False)
    # ---- dự phòng 200 đọc là PHẠT/NGHĨA VỤ vụ án lớn hơn (trigger HARD ABANDON): trừ thêm X tỷ khỏi tiền
    P("\n== Nghĩa vụ vụ án thêm (ngoài 200 đã trừ), trừ thẳng tiền ==")
    xr = []
    for x in (0, 200, 500, 1000):
        xr.append(dict(extra_liab=x, ev_A7=per_scn(CFG_A7)[0] - round(x * 1000 / SH), ev_B7=per_scn(CFG_B7)[0] - round(x * 1000 / SH)))
    xr = pd.DataFrame(xr); P(xr.to_string(index=False)); xr.to_csv(csv("out_r7_extra_liab.csv"), index=False)
    # ---- chi tiết tầng A7
    cfg_save = dict(CFG); CFG.clear(); CFG.update(CFG_A7)
    R = evaluate()
    P("\nTầng A7 — tổng hợp\n", R["summ"].to_string(index=False)); P(R["mu"].to_string(index=False))
    for nm in ("so", "dc", "mu", "summ"): R[nm].to_csv(csv(f"out_r7_A_{nm}.csv"), index=False)
    P("cash_value_in_pe cũ (PE DGC10y × lãi/tiền ròng) = ", R["mu"].cash_value_in_pe.tolist(), "; r7: tiền vào PE qua cash_adj 100% (sau haircut/PAT)")
    CFG.clear(); CFG.update(cfg_save)
    P(f"Đắk Nông note 11: 60,089 → 0 ; 'Giảm khác' 63,378 ; thu thanh lý 332,29 − NBV 284,06 = 48,23 ; 284,06 + 63,38 = {284.064 + 63.378:.2f} ≠ 332,29 ; 63,38 − 48,23 = {63.378 - 48.228:.2f}")
    P(f"ZaloPay DGC 10.000 cp × 32.900 = 329,0 tr / NAV 28/10 919,93 tr = {329.0 / 919.931:.1%} ; lỗ so giá vốn 39.775 = {32900 / 39775 - 1:.1%}")
    P(f"CFO/LNST hợp nhất 9T = 755,6 / 1.369,4 = {755.6 / 1369.4:.2f}x")
    open(csv("run_stdout_r7.txt"), "w").write("\n".join(out))


if __name__ == "__main__":
    main()
    main_r7()
