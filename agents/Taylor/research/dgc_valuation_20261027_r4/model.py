"""DGC định giá VÒNG 4 2026-10-27 (job Taylor_20261026_181244; r3 = ../dgc_valuation_20261027_r3). READ-ONLY research.
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
CFG_R3 = dict(rf=0.074, uplift=1_000, pe_peer="now", pat=True, q4acc=True, mifin=True, mid=True, nsuni=True, tax_fin=0.13, mi_core=0.10,
              sched=False, term_tax=None, norm=None, eqm=False, x326=False, loan_h=None, prov=0.0)
CFG_R4 = dict(CFG_R3, tax_fin=0.20, sched=True, term_tax=0.20, norm="avg", eqm=True, x326=True, loan_h=0.50, prov=1.0)
CFG = dict(CFG_R4)

# ---------------------------------------------------------------- INPUTS
SH = 379.778413          # triệu cp [BQ ticker_financial.OShares 2026Q2]
PX = 32_100              # đ/cp, đóng cửa 2026-10-26 [BQ ticker.Close]
FX = 26_300              # VND/USD hàm ý Q2: 1.572 tỷ / 12,9 kt / 4.631 $ [DSC 10/08/2026]

NP_MI_Q1, NP_MI_Q2 = 408.8, 389.0   # LNST mẹ [BQ NP_P0 2026Q1; Vietcap flash 22/07 (BQ 380,1 lệch)]
NP_CONS_H1 = 871.0                  # LNST hợp nhất 6T [UL: Q1 ~430 ACBS + Q2 440 Vietcap]
Q3_MI = {"thuan": 420, "coso": 321, "nghich": 219}          # FORECAST.md khoá md5 d6ea39f4
Q3_CONS = {"thuan": 450, "coso": 350, "nghich": 246}
W = {"thuan": 0.20, "coso": 0.50, "nghich": 0.30}           # trọng số = FORECAST.md Q3 (giữ nhất quán)

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


def eq_mi_0930():
    base = EQ_MOTHER_0630 if CFG["eqm"] else EQ_MI_0630_R3
    return base - DIV_PAID_0925 + Q3_MI["coso"]


def extras_book():
    """Giá trị SỔ SÁCH các khoản ngoài tiền+tiền gửi (để loại khỏi VCSH lõi, khỏi tính đôi)."""
    return (INT_RECV_326 if CFG["x326"] else 0) + (LOAN_819 if CFG["loan_h"] is not None else 0) - PROV_100 * CFG["prov"]


def extras_value(k):
    """Giá trị quy về mẹ: lãi phải thu × (1−haircut pháp lý k) + cho vay 819 × (1−haircut riêng) − dự phòng. Tỷ đồng."""
    v = 0.0
    if CFG["x326"]:
        v += INT_RECV_326 * (1 - HC_LEGAL[k])
    if CFG["loan_h"] is not None:
        v += LOAN_819 * (1 - CFG["loan_h"])
    return v - PROV_100 * CFG["prov"]


NS_CAPEX_TOTAL, NS_CIP_0630 = 2_400, 1_221      # Nghi Sơn GĐ1 [Vietcap/Nhadautu/DSC]
NS_CAPEX_LEFT = NS_CAPEX_TOTAL - NS_CIP_0630 - 250   # trừ capex Q3 [UL]

TAX = 0.13               # thuế hiệu dụng Q2 = 1 − 440/507 [Vietcap]
MI_SHARE = 0.10          # CĐKKS/LNST hợp nhất: Q2 11,6% ; Q3 ước 8% [FORECAST.md]
PAT_MI_CASH = 274        # r3: 49% × (tiền + đầu tư nắm giữ đến đáo hạn PAT 30/09 = 559 tỷ; chuyendongthitruong 25/10/2026); r2 = 365 [UL]
HC_LEGAL = {"thuan": 0.03, "coso": 0.09, "nghich": 0.29}   # haircut pháp lý còn lại sau khi tách PAT (r1: 5/15/35% gồm ~6pp PAT)
NS_BOOK = NS_CIP_0630 + 250                                   # XDCB NS ghi sổ 30/09 [UL]
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
    for k, rev, gm in [("thuan", 2450, 0.195), ("coso", 2250, 0.165), ("nghich", 2050, 0.135)]:
        gp = rev * gm
        ebit = gp - 130
        fi = (CASH_DEP_0630 - DIV_PAID_0925 + CFO_Q3_UL - CAPEX_Q3_UL) * SCN[k]["dep"] / 4 + {"thuan": 10, "coso": 0, "nghich": -10}[k]
        core_c = ebit * (1 - tax_core(2026))
        np_c = core_c + (fi - 25) * (1 - CFG["tax_fin"])
        core_mi = core_c * (1 - CFG["mi_core"])
        np_mi = core_mi + fin_np(fi - 25, SCN[k]["dep"], 1.0 * 1) if CFG["mifin"] else (ebit + fi - 25) * (1 - tax_core(2026)) * (1 - CFG["mi_core"])
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
    gp = rev * s["gm"][i] + CFG["uplift"] * s["reopen"][i]
    ebit_core = gp - SGA
    fin = avg_gross_cash * s["dep"] - DEBT_0630 * 0.065
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
    gross0 = CASH_DEP_0630 - DIV_PAID_0925 + CFO_Q3_UL - CAPEX_Q3_UL
    q4t = q4_bridge().set_index("scn")
    for k in SCN:
        fy26_mi = NP_MI_Q1 + NP_MI_Q2 + Q3_MI[k] + q4t.np_mi[k]
        fy26_c = NP_CONS_H1 + Q3_CONS[k] + q4t.np_cons[k]
        rows.append(dict(scn=k, year=2026, np_mi=round(fy26_mi), np_cons=round(fy26_c)))
        # tiền gửi bình quân: trừ capex NS còn lại 2027, cổ tức 30%/năm (3.000 đ = 1.139 tỷ) từ 2027
        g27 = gross0 - NS_CAPEX_LEFT * 0.8 - 1139 * 0.5 + 600
        g28 = g27 - 1139 + 900
        for i, g in enumerate([g27, g28]):
            rows.append(year_pnl(k, i, g))
    return pd.DataFrame(rows)


def prob_1600(n=200_000):
    """P(cả năm ≥1.600) — Q3 ~ phân phối FORECAST (sd≈82, từ khoảng 80% [215;425]); Q4 sd 85 [UL]; tương quan 0,6 [UL]."""
    rg = np.random.default_rng(20261027)
    q4t = q4_bridge().set_index("scn")
    cov = np.array([[82**2, 0.6 * 82 * 85], [0.6 * 82 * 85, 85**2]])
    z = rg.multivariate_normal([0, 0], cov, n)
    h2_mi = 321 + q4t.np_mi["coso"] + z.sum(1)
    h2_c = 350 + q4t.np_cons["coso"] + z.sum(1) * 1.08
    p_mi = float((h2_mi >= 1600 - NP_MI_Q1 - NP_MI_Q2).mean())
    p_c = float((h2_c >= 1600 - NP_CONS_H1).mean())
    return dict(need_h2_mi=round(1600 - NP_MI_Q1 - NP_MI_Q2), need_q4_mi_if_q3_base=round(1600 - NP_MI_Q1 - NP_MI_Q2 - 321),
                p_mi=round(p_mi, 3), need_h2_cons=round(1600 - NP_CONS_H1),
                need_q4_cons_if_q3_base=round(1600 - NP_CONS_H1 - 350), p_cons=round(p_c, 3),
                p_combined_5050=round(0.5 * p_mi + 0.5 * p_c, 3), p_combined_6040=round(0.4 * p_mi + 0.6 * p_c, 3))


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
        c = (NET_CASH_0930 - PAT_MI_CASH) * (1 - HC_LEGAL[k])
    else:
        c = NET_CASH_0930 * (1 - HAIRCUT[k])
    return c + q4_core(k) + extras_value(k)


def norm_core(k, fc):
    """LNST mẹ LÕI chuẩn hoá (TB 2027-28). norm=None: theo lịch thuế từng năm (r3: 13%); norm≠None: quy về thuế t_norm()."""
    r = fc[(fc.scn == k) & (fc.year >= 2027)]
    if t_norm() is None:
        return float(r.core_np_mi.mean())
    return float((r.ebit_core * (1 - t_norm()) * (1 - CFG["mi_core"])).mean())


def ns_value(k):
    return SCN[k]["ns_steady"] * NS_MULT[k] / (1 + ke()) ** 2 - NS_CAPEX_LEFT


def sotp(fc):
    out = []
    for k in SCN:
        r = fc[(fc.scn == k) & (fc.year >= 2027)]
        core_norm = norm_core(k, fc)             # chuẩn hoá = TB 2027-28 (KHÔNG dùng đỉnh 2022-25)
        cash = cash_adj(k)
        core = core_norm * CORE_PE[k]
        ns = ns_value(k)
        tot = cash + core + ns
        out.append(dict(scn=k, net_cash_0930=round(NET_CASH_0930), pat_mi_cash=PAT_MI_CASH if CFG["pat"] else 0,
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
    wc = [300 if k != "nghich" else 0, 0, 0, 0, 0]
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
    cash = cash_adj(k) - NS_CAPEX_LEFT
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
        net_adj = NET_CASH_0930 - (PAT_MI_CASH if CFG["pat"] else 0)
        eq_core = eq_mi_0930() - net_adj - extras_book()     # VCSH phi-tiền (gồm tồn kho, TSCĐ, XDCB NS); r4: VCSH MẸ, loại 326/819/dự phòng
        adj = per_share(q4_core(k)) - (per_share(NS_CAPEX_LEFT) if CFG["nsuni"] else 0) + per_share(extras_value(k))
        e_norm_peer = e_norm - (core_sched - core_n)         # PE peer (thuế ~20%) áp trên LNST đã chuẩn hoá thuế lõi
        if CFG["nsuni"]:
            eq_core -= NS_BOOK
        roe = core_n / eq_core
        pb_j = max(roe - G_BASE, 0) / (ke() - G_BASE)
        if CFG["nsuni"]:   # lõi + tiền + NS (ns_value đã trừ capex còn lại)
            v_pb = per_share(pb_j * eq_core + cash_adj(k) + ns_value(k))
        else:
            v_pb = per_share(pb_j * eq_core + (cash_adj(k) if CFG["pat"] else NET_CASH_0930 * (1 - HAIRCUT[k])))
        peer_pe = pe_peer_now if CFG["pe_peer"] == "now" else pe_peer10
        out.append(dict(scn=k, np_mi_norm=round(e_norm), eps_norm=round(per_share(e_norm)),
                        v_pe_dgc10y=round(per_share(e_norm) * pe_dgc10 + adj), v_pe_peer_now=round(per_share(e_norm_peer) * pe_peer_now + adj),
                        v_pe_peer10y=round(per_share(e_norm_peer) * pe_peer10 + adj), v_pe_peer_used=round(per_share(e_norm_peer) * peer_pe + adj),
                        roe_core=round(roe, 3), pb_justified=round(pb_j, 2), v_pb=round(v_pb),
                        cash_value_in_pe=round(pe_dgc10 * float(fc[(fc.scn == k) & (fc.year >= 2027)].fin_np_mi.mean()) / max(NET_CASH_0930, 1), 2)))
    return pd.DataFrame(out), dict(pe_dgc10=pe_dgc10, pe_peer_now=pe_peer_now, pe_peer10=pe_peer10)


def evaluate(W_=None):
    W_ = W_ or W
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


def main():
    pd.set_option("display.width", 250)
    csv = lambda n: os.path.join(HERE, n)
    print(f"Net cash 30/09 dựng lại [UL] = {NET_CASH_0930:.0f} tỷ = {per_share(NET_CASH_0930):.0f} đ/cp ; "
          f"VCSH MẸ 30/09 ≈ {eq_mi_0930():.0f} tỷ, BVPS mẹ ≈ {per_share(eq_mi_0930()):.0f}, P/B ≈ {PX / per_share(eq_mi_0930()):.2f} "
          f"(30/06 sau cổ tức 8.000: BVPS {per_share(EQ_MOTHER_0630 - DIV_PAID_0925):.0f}, P/B {PX / per_share(EQ_MOTHER_0630 - DIV_PAID_0925):.2f}) ; "
          f"NS capex còn lại ≈ {NS_CAPEX_LEFT} ; Ke = {ke():.3f}")
    print("BVPS mẹ 30/06 trước cổ tức:", round(per_share(EQ_MOTHER_0630)), "| r3 (gồm CĐKKS):", round(per_share(EQ_MI_0630_R3)))
    sch = pd.DataFrame([dict(year=y, tax_core=round(TAX_SCHED[y], 4)) for y in range(2026, 2036)])
    sch.loc[len(sch)] = dict(year="terminal", tax_core=0.20); sch.loc[len(sch)] = dict(year="TB 2027-34 (chuẩn hoá PE/P-B)", tax_core=round(TAX_AVG_2734, 4))
    print("\nLịch thuế lõi [UL] (tỷ trọng:", TAX_SHARES, ")\n", sch.to_string(index=False)); sch.to_csv(csv("out_tax_schedule.csv"), index=False)
    for e, lab in [(2026, "6T/2026 phép thử"), ]:
        print(f"phép thử 6T: (131,3 − 20%×366,4)/(1.004,3 − 366,4) = {(131.3 - 0.2 * 366.4) / (1004.3 - 366.4):.4f} vs lịch 2026 {TAX_SCHED[2026]:.4f}")
    q4t = q4_bridge(); print("\nQ4/2026 bridge\n", q4t.to_string(index=False))
    R = evaluate(); fc, so, dc, mu, summ, refs = R["fc"], R["so"], R["dc"], R["mu"], R["summ"], R["refs"]
    print("\nDự phóng\n", fc.to_string(index=False))
    p = prob_1600(); print("\nP(1.600)", p)
    print("\n(a) SOTP\n", so.to_string(index=False)); print("\n(b) DCF\n", dc.to_string(index=False))
    sens_kg = pd.DataFrame({f"g={g:.0%}": [round(dcf_core("coso", k_, g, fc=fc)) for k_ in (0.12, 0.13, ke(), 0.16, 0.18)]
                            for g in (0.01, 0.02, 0.03, 0.04)}, index=["12%", "13%", f"{ke():.1%}", "16%", "18%"])
    print("\nDCF cơ sở: Ke × g\n", sens_kg)
    print("\n(c) Multiple", refs, "\n", mu.to_string(index=False))
    print("\nTổng hợp đ/cp\n", summ.to_string(index=False))
    ev = R["ev"]
    print(f"\nGiá trị kỳ vọng (thuận 0,2 / cơ sở 0,5 / nghịch 0,3) = {ev:.0f} đ/cp vs giá {PX} ⇒ {ev / PX - 1:+.1%} ; vs TB 5 phiên 33.500 ⇒ {ev / 33500 - 1:+.1%}")
    W_alt = {"thuan": 0.30, "coso": 0.50, "nghich": 0.20}
    ev_alt = float((summ.blend * summ.scn.map(W_alt)).sum())
    print(f"Trọng số thuận 0,3 / cơ sở 0,5 / nghịch 0,2 ⇒ {ev_alt:.0f}")
    so_b = so.set_index("scn").loc["coso"]
    implied_core = (PX * SH / 1000 - so_b.cash_after_hc - so_b.nghison_val) / CORE_PE["coso"]
    print(f"Hoà vốn: giá {PX} ngầm định LNST mẹ LÕI chuẩn hoá ≈ {implied_core:.0f} tỷ/năm")

    # ---- WATERFALL r3 → r4 (bật dần)
    steps = [("r3 (tái lập)", {}), ("1a thuế lãi tiền gửi 20%", dict(tax_fin=0.20)), ("1b lõi theo lịch ưu đãi (2026Q4-2031)", dict(sched=True)),
             ("1c terminal lõi 20%", dict(term_tax=0.20)), ("1d chuẩn hoá thuế PE lõi/P-B/PE peer (TB 2027-34)", dict(norm="avg")),
             ("2 VCSH MẸ (bỏ CĐKKS 417,6)", dict(eqm=True)), ("4a lãi tiền gửi phải thu 326,2", dict(x326=True)),
             ("4b cho vay 819 (haircut 50%)", dict(loan_h=0.50)), ("5 dự phòng 100 (trừ 100%)", dict(prov=1.0))]
    wf = []; cur = dict(CFG_R3)
    for lab, kw in steps:
        cur.update(kw); r, row = ev_cfg(**cur); wf.append(dict(step=lab, **row))
    wf = pd.DataFrame(wf); wf["delta"] = wf.ev.diff(); print("\nWaterfall r3→r4\n", wf.to_string(index=False)); wf.to_csv(csv("out_waterfall.csv"), index=False)
    assert abs(wf.ev.iloc[-1] - round(ev)) < 1, "waterfall cuối phải = CFG_R4"
    # tác động tách riêng lên DCF terminal và PE lõi (SOTP cơ sở): nhìn theo từng bước, cơ sở
    det = []; cur = dict(CFG_R3)
    for lab, kw in steps:
        cur.update(kw); r = with_cfg(**cur); c = r["dc"].set_index("scn").dcf["coso"]; sp = r["so"].set_index("scn").loc["coso"]
        det.append(dict(step=lab, dcf_coso=int(c), sotp_coso=int(sp.ps_total), ps_core_coso=int(sp.ps_core), pb_coso=int(r["mu"].set_index("scn").v_pb["coso"]),
                        pe_peer_coso=int(r["mu"].set_index("scn").v_pe_peer_used["coso"]), pe_dgc10_coso=int(r["mu"].set_index("scn").v_pe_dgc10y["coso"])))
    det = pd.DataFrame(det); print("\nTác động theo phương pháp (kịch bản cơ sở)\n", det.to_string(index=False)); det.to_csv(csv("out_waterfall_methods_coso.csv"), index=False)

    # ---- BẢNG NHẠY: haircut khoản 819 × thuế terminal lõi
    rows = []
    for tt in (0.13, 0.15, 0.17, 0.20):
        for h in (0.0, 0.25, 0.50, 1.0):
            r, row = ev_cfg(term_tax=tt, loan_h=h); rows.append(dict(term_tax=tt, loan_haircut=h, **row))
    sens819 = pd.DataFrame(rows); piv = sens819.pivot(index="loan_haircut", columns="term_tax", values="ev")
    print("\nKỳ vọng (đ/cp): haircut khoản 819 (hàng) × thuế terminal lõi (cột)\n", piv.to_string()); sens819.to_csv(csv("out_sens_819_x_terminal_tax.csv"), index=False)
    print("819 một mình = ", round(per_share(LOAN_819)), "đ/cp ; 326,2 = ", round(per_share(INT_RECV_326)), "đ/cp ; dự phòng 100 = ", round(per_share(PROV_100)), "đ/cp")

    # ---- độ nhạy bổ sung
    sens = []
    base_r, base_row = ev_cfg(); sens.append(dict(case="r4 chính", **base_row))
    for lab, kw in [("norm PE lõi/P-B ở 20% (thay vì TB 2027-34)", dict(norm=0.20)), ("không chuẩn hoá thuế PE lõi (norm=None)", dict(norm=None)),
                    ("terminal lõi 17%", dict(term_tax=0.17)), ("dự phòng 100 không trừ", dict(prov=0.0)), ("dự phòng 100 trừ 50%", dict(prov=0.5)),
                    ("bỏ lãi phải thu 326", dict(x326=False)), ("MI lõi 13%", dict(mi_core=0.13)), ("MI lõi 17,8% (Q2 thực)", dict(mi_core=0.178)),
                    ("PE peer 10y", dict(pe_peer="10y")), ("lãi suất tiền gửi hàng năm dùng thuế lãi 13% (r3)", dict(tax_fin=0.13))]:
        r, row = ev_cfg(**kw); sens.append(dict(case=lab, **row))
    # CFO Q3 (H1 thực ước ~0-50 vs giả định 300) — đổi hằng số tạm thời
    import sys
    mod = sys.modules[__name__]
    for lab, cfo in [("CFO Q3 = 100 (thay 300)", 100), ("CFO Q3 = 0", 0)]:
        old = (mod.CFO_Q3_UL, mod.NET_CASH_0930)
        try:
            mod.CFO_Q3_UL = cfo; mod.NET_CASH_0930 = CASH_DEP_0630 - DIV_PAID_0925 + cfo - CAPEX_Q3_UL - DEBT_0630
            r, row = ev_cfg()
        finally:
            mod.CFO_Q3_UL, mod.NET_CASH_0930 = old
        sens.append(dict(case=lab, **row))
    sens = pd.DataFrame(sens); print("\nĐộ nhạy bổ sung\n", sens.to_string(index=False)); sens.to_csv(csv("out_sensitivities.csv"), index=False)

    # ---- tồn kho: xoá sổ thêm X tỷ (sau dự phòng 292,9 đã có) × haircut pháp lý — SOTP cơ sở
    so_b0 = so.set_index("scn").loc["coso"]
    hc = pd.DataFrame({f"tồn kho −{inv}": [round(per_share((NET_CASH_0930 - PAT_MI_CASH) * (1 - h) + q4_core("coso") + extras_value("coso") + so_b0.core_val + so_b0.nghison_val
                                                           - inv * (1 - TAX_AVG_2734))) for h in (0, 0.09, 0.15, 0.30, 0.50)] for inv in (0, 300, 600, 951)},
                      index=["haircut pháp lý 0%", "9%", "15%", "30%", "50%"])
    print("\nSOTP cơ sở: haircut pháp lý × xoá sổ thêm tồn kho (nguyên liệu+thành phẩm = 2.235,4 gộp; dự phòng sẵn 292,9)\n", hc); hc.to_csv(csv("out_sotp_sens_haircut.csv"))

    for name, df in [("q4", q4t), ("forecast", fc), ("sotp", so), ("dcf", dc), ("multiples", mu), ("summary", summ)]:
        df.to_csv(csv(f"out_{name}.csv"), index=False)
    sens_kg.to_csv(csv("out_dcf_sens_ke_g.csv"))
    pd.DataFrame([p | dict(ev=round(ev), ev_w302050=round(ev_alt), implied_core=round(implied_core))]).to_csv(csv("out_headline.csv"), index=False)


if __name__ == "__main__":
    main()
