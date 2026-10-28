"""DGC định giá VÒNG 2 2026-10-27 (job Taylor_20261026_174426; vòng 1 = ../dgc_valuation_20261027, job ..._171735). READ-ONLY research.
CFG: mỗi sửa của vòng 2 là một công tắc; CFG_R1 tái lập đúng số vòng 1 (33.609), CFG_R2 là kết quả chính; waterfall bật dần.

Tái lập: python3 model.py  (chỉ cần pandas/numpy; đọc data/*.csv cùng thư mục, ghi out_*.csv).
Đơn vị: tỷ đồng, trừ khi ghi khác. Mọi input có nhãn nguồn [BQ]/[URL]/[UL]=ước lượng trong INPUTS.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261027)

CFG_R1 = dict(rf=0.068, uplift=1_100, pe_peer="10y", pat=False, q4acc=False, mifin=False, mid=False, nsuni=False, tax_fin=0.13, mi_core=0.10)
CFG_R2 = dict(rf=0.074, uplift=1_000, pe_peer="now", pat=True, q4acc=True, mifin=True, mid=True, nsuni=True, tax_fin=0.13, mi_core=0.10)
CFG = dict(CFG_R2)

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
BVPS_0630 = 42_744       # [BQ] — TRƯỚC khi trả 8.000 đ/cp
EQ_MI_0930 = BVPS_0630 * SH / 1000 - DIV_PAID_0925 + Q3_MI["coso"]

NS_CAPEX_TOTAL, NS_CIP_0630 = 2_400, 1_221      # Nghi Sơn GĐ1 [Vietcap/Nhadautu/DSC]
NS_CAPEX_LEFT = NS_CAPEX_TOTAL - NS_CIP_0630 - 250   # trừ capex Q3 [UL]

TAX = 0.13               # thuế hiệu dụng Q2 = 1 − 440/507 [Vietcap]
MI_SHARE = 0.10          # CĐKKS/LNST hợp nhất: Q2 11,6% ; Q3 ước 8% [FORECAST.md]
PAT_MI_CASH = 365        # [UL] phần tiền của PAT thuộc CĐKKS 49%: PAT BQ 2026Q2 totalAsset 1.011 tỷ, VCSH 742 (BVPS 29.694×25tr); tiền gửi ~650-700 (TNTC Q3 11,4 tỷ — số của skeptic, CHƯA tự kiểm) ⇒ 49% ≈ 330-400
HC_LEGAL = {"thuan": 0.03, "coso": 0.09, "nghich": 0.29}   # haircut pháp lý còn lại sau khi tách PAT (r1: 5/15/35% gồm ~6pp PAT)
NS_BOOK = NS_CIP_0630 + 250                                   # XDCB NS ghi sổ 30/09 [UL]
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
        core_c = ebit * (1 - TAX)
        np_c = core_c + (fi - 25) * (1 - CFG["tax_fin"])
        core_mi = core_c * (1 - CFG["mi_core"])
        np_mi = core_mi + fin_np(fi - 25, SCN[k]["dep"], 1.0 * 1) if CFG["mifin"] else (ebit + fi - 25) * (1 - TAX) * (1 - CFG["mi_core"])
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
    core_c = ebit_core * (1 - TAX)
    np_cons = core_c + fin * (1 - CFG["tax_fin"]) + s["ns_np"][i]    # Nghi Sơn 100% DGC, NPAT trực tiếp
    if CFG["mifin"]:
        np_mi = core_c * (1 - CFG["mi_core"]) + fin_np(fin, s["dep"]) + s["ns_np"][i]
    else:
        np_mi = (ebit_core + fin) * (1 - TAX) * (1 - CFG["mi_core"]) + s["ns_np"][i]
    core_np_mi = core_c * (1 - CFG["mi_core"])
    return dict(scn=k, year=2027 + i, rev_core=round(rev), rev_p4=round(rev_p4), rev_tpa=round(rev_tpa), other=s["other"],
                gm_eff=round(gp / rev, 3), gp=round(gp), ebit_core=round(ebit_core), fin_net=round(fin),
                ns_np=s["ns_np"][i], np_cons=round(np_cons), np_mi=round(np_mi), core_np_mi=round(core_np_mi),
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
    return c + q4_core(k)


def ns_value(k):
    return SCN[k]["ns_steady"] * NS_MULT[k] / (1 + ke()) ** 2 - NS_CAPEX_LEFT


def sotp(fc):
    out = []
    for k in SCN:
        r = fc[(fc.scn == k) & (fc.year >= 2027)]
        core_norm = r.core_np_mi.mean()          # chuẩn hoá = TB 2027-28 (KHÔNG dùng đỉnh 2022-25)
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
        f = (ebit[t] * (1 - TAX) * (1 - CFG["mi_core"]) + ns[t]) * (1 - (reinv if t >= 2 else 0)) + wc[t]
        fcff.append(f)
        pv += f / (1 + k_e) ** tt[t]
    tv = fcff[-1] * (1 + g) / (k_e - g) / (1 + k_e) ** (tt[-1] if CFG["mid"] else 5)
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
        core_n = float(fc[(fc.scn == k) & (fc.year >= 2027)].core_np_mi.mean())
        net_adj = NET_CASH_0930 - (PAT_MI_CASH if CFG["pat"] else 0)
        eq_core = EQ_MI_0930 - net_adj                       # VCSH phi-tiền (gồm tồn kho, TSCĐ, XDCB NS)
        adj = per_share(q4_core(k)) - (per_share(NS_CAPEX_LEFT) if CFG["nsuni"] else 0)
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
                        v_pe_dgc10y=round(per_share(e_norm) * pe_dgc10 + adj), v_pe_peer_now=round(per_share(e_norm) * pe_peer_now + adj),
                        v_pe_peer10y=round(per_share(e_norm) * pe_peer10 + adj), v_pe_peer_used=round(per_share(e_norm) * peer_pe + adj),
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


def main():
    pd.set_option("display.width", 250)
    csv = lambda n: os.path.join(HERE, n)
    print(f"Net cash 30/09 dựng lại [UL] = {NET_CASH_0930:.0f} tỷ = {per_share(NET_CASH_0930):.0f} đ/cp ; "
          f"VCSH mẹ 30/09 ≈ {EQ_MI_0930:.0f} tỷ, BVPS ≈ {per_share(EQ_MI_0930):.0f}, P/B thật ≈ {PX / per_share(EQ_MI_0930):.2f} ; "
          f"NS capex còn lại ≈ {NS_CAPEX_LEFT} ; Ke = {ke():.3f} ; PAT-CĐKKS cash {PAT_MI_CASH} = {per_share(PAT_MI_CASH):.0f} đ/cp")
    q4t = q4_bridge(); print("\nQ4/2026 bridge\n", q4t.to_string(index=False))
    R = evaluate(); fc, so, dc, mu, summ, refs = R["fc"], R["so"], R["dc"], R["mu"], R["summ"], R["refs"]
    print("\nDự phóng\n", fc.to_string(index=False))
    p = prob_1600(); print("\nP(1.600)", p)
    print("\n(a) SOTP\n", so.to_string(index=False)); print("\n(b) DCF\n", dc.to_string(index=False))
    sens_kg = pd.DataFrame({f"g={g:.0%}": [round(dcf_core("coso", k_, g, fc=fc)) for k_ in (0.12, 0.13, ke(), 0.16, 0.18)]
                            for g in (0.01, 0.02, 0.03, 0.04)}, index=["12%", "13%", f"{ke():.1%}", "16%", "18%"])
    sens_kgm = pd.DataFrame({f"GM={m:.0%}": [round(dcf_core("coso", k_, G_BASE, gm_override=m, fc=fc)) for k_ in (0.12, 0.13, ke(), 0.16, 0.18)]
                             for m in (0.14, 0.17, 0.20, 0.23, 0.26, 0.30)}, index=["12%", "13%", f"{ke():.1%}", "16%", "18%"])
    print("\nDCF cơ sở: Ke × g\n", sens_kg); print("\nDCF cơ sở: Ke × biên gộp dài hạn\n", sens_kgm)
    print("\n(c) Multiple", refs, "\n", mu.to_string(index=False))
    so_b0 = so.set_index("scn").loc["coso"]
    hc = pd.DataFrame({f"tồn kho −{inv}": [round(per_share((NET_CASH_0930 - PAT_MI_CASH) * (1 - h) + q4_core("coso") + so_b0.core_val + so_b0.nghison_val - inv * (1 - TAX)))
                                           for h in (0, 0.09, 0.15, 0.30, 0.50)] for inv in (0, 475, 951)},
                      index=["haircut pháp lý 0%", "9%", "15%", "30%", "50%"])
    print("\nSOTP cơ sở: haircut pháp lý (đã tách PAT) × xoá sổ tồn kho bị ngoại trừ (951 tỷ)\n", hc); hc.to_csv(csv("out_sotp_sens_haircut.csv"))
    print("\nTổng hợp đ/cp\n", summ.to_string(index=False))
    ev = R["ev"]
    print(f"\nGiá trị kỳ vọng (thuận 0,2 / cơ sở 0,5 / nghịch 0,3) = {ev:.0f} đ/cp vs giá {PX} ⇒ {ev / PX - 1:+.1%} ; vs TB 5 phiên 33.500 ⇒ {ev / 33500 - 1:+.1%}")
    W_alt = {"thuan": 0.30, "coso": 0.50, "nghich": 0.20}
    ev_alt = float((summ.blend * summ.scn.map(W_alt)).sum())
    print(f"Trọng số thuận 0,3 / cơ sở 0,5 / nghịch 0,2 ⇒ {ev_alt:.0f}")
    so_b = so.set_index("scn").loc["coso"]
    implied_core = (PX * SH / 1000 - so_b.cash_after_hc - so_b.nghison_val) / CORE_PE["coso"]
    print(f"Hoà vốn: giá {PX} ngầm định LNST mẹ LÕI chuẩn hoá ≈ {implied_core:.0f} tỷ/năm "
          f"(so: nghịch {so.set_index('scn').loc['nghich'].core_np_mi_norm}, cơ sở {so_b.core_np_mi_norm}, thuận {so.set_index('scn').loc['thuan'].core_np_mi_norm})")

    # ---- (7) HIỆN TRẠNG: không mở lại khai trường
    rows = []
    def ev_with_reopen(mode):
        saved = {k: list(SCN[k]["reopen"]) for k in SCN}
        try:
            for k in SCN:
                if mode == "coso_no" and k == "coso": SCN[k]["reopen"] = [0.0, 0.0]
                if mode == "coso_nghich_no" and k in ("coso", "nghich"): SCN[k]["reopen"] = [0.0, 0.0]
                if mode == "all_no": SCN[k]["reopen"] = [0.0, 0.0]
            r = evaluate()
        finally:
            for k in SCN: SCN[k]["reopen"] = saved[k]
        return r
    for mode, lab in [("base", "cơ sở-có-mở-lại ½ trong 2028 (kịch bản chính)"), ("coso_no", "HIỆN TRẠNG: cơ sở KHÔNG mở lại (thuận giữ nguyên)"),
                      ("coso_nghich_no", "cơ sở+nghịch không mở lại, thuận giữ"), ("all_no", "không mở lại Ở CẢ 3 kịch bản")]:
        r = ev_with_reopen(mode); sm = r["summ"].set_index("scn")
        rows.append(dict(mode=mode, label=lab, thuan=sm.blend["thuan"], coso=sm.blend["coso"], nghich=sm.blend["nghich"], ev=round(r["ev"])))
    reopen_tbl = pd.DataFrame(rows); print("\nPhụ thuộc khai trường\n", reopen_tbl.to_string(index=False)); reopen_tbl.to_csv(csv("out_reopen_conditional.csv"), index=False)

    # ---- waterfall r1 → r2 (bật dần)
    steps = [("r1 (tái lập)", {}), ("+4 uplift khai trường 1.000", dict(uplift=1_000)), ("+8 rf 7,4%", dict(rf=0.074)),
             ("+9 PE peer hiện tại 9,1", dict(pe_peer="now")), ("+12 tách PAT-CĐKKS khỏi haircut", dict(pat=True)),
             ("+13a lõi Q4/2026 cộng vào tiền", dict(q4acc=True)), ("+13b MI không ăn lãi tiền", dict(mifin=True)),
             ("+13c DCF chiết khấu giữa năm từ 27/10", dict(mid=True)), ("+13d NS capex thống nhất P/B+PE", dict(nsuni=True))]
    wf = []; cur = dict(CFG_R1)
    for lab, kw in steps:
        cur.update(kw); r = with_cfg(**cur); sm = r["summ"].set_index("scn")
        wf.append(dict(step=lab, ev=round(r["ev"]), thuan=sm.blend["thuan"], coso=sm.blend["coso"], nghich=sm.blend["nghich"]))
    wf = pd.DataFrame(wf); wf["delta"] = wf.ev.diff(); print("\nWaterfall r1→r2\n", wf.to_string(index=False)); wf.to_csv(csv("out_waterfall.csv"), index=False)
    r1 = with_cfg(**CFG_R1)["summ"]; print("\nr1 tái lập:\n", r1.to_string(index=False))

    # ---- độ nhạy bổ sung
    sens = []
    for lab, kw in [("r2 chính", {}), ("thuế lãi tiền 20% [cần legal-vn]", dict(tax_fin=0.20)), ("MI lõi 13% (Q3-forecast; Q2 thực 17,8%)", dict(mi_core=0.13)),
                    ("MI lõi 17,8% (Q2 thực tế)", dict(mi_core=0.178)), ("PE peer 10y 10,5", dict(pe_peer="10y")), ("rf 6,8% (r1)", dict(rf=0.068))]:
        r = with_cfg(**kw); sm = r["summ"].set_index("scn")
        sens.append(dict(case=lab, ev=round(r["ev"]), coso=sm.blend["coso"], nghich=sm.blend["nghich"], thuan=sm.blend["thuan"]))
    for lab, d in [("lợi suất tiền gửi 7,1% (Q2 thực) mọi kịch bản", 0.071)]:
        sv = {k: SCN[k]["dep"] for k in SCN}
        try:
            for k in SCN: SCN[k]["dep"] = d
            r = evaluate(); sm = r["summ"].set_index("scn")
        finally:
            for k in SCN: SCN[k]["dep"] = sv[k]
        sens.append(dict(case=lab, ev=round(r["ev"]), coso=sm.blend["coso"], nghich=sm.blend["nghich"], thuan=sm.blend["thuan"]))
    sens = pd.DataFrame(sens); print("\nĐộ nhạy bổ sung\n", sens.to_string(index=False)); sens.to_csv(csv("out_sensitivities.csv"), index=False)

    for name, df in [("q4", q4t), ("forecast", fc), ("sotp", so), ("dcf", dc), ("multiples", mu), ("summary", summ)]:
        df.to_csv(csv(f"out_{name}.csv"), index=False)
    sens_kg.to_csv(csv("out_dcf_sens_ke_g.csv")); sens_kgm.to_csv(csv("out_dcf_sens_ke_gm.csv"))
    pd.DataFrame([p | dict(ev=round(ev), ev_w302050=round(ev_alt), implied_core=round(implied_core))]).to_csv(csv("out_headline.csv"), index=False)


if __name__ == "__main__":
    main()
