"""DGC định giá chính thức 2026-10-27 (job Taylor_20261026_171735). READ-ONLY research.

Tái lập: python3 model.py  (chỉ cần pandas/numpy; đọc data/*.csv cùng thư mục, ghi out_*.csv).
Đơn vị: tỷ đồng, trừ khi ghi khác. Mọi input có nhãn nguồn [BQ]/[URL]/[UL]=ước lượng trong INPUTS.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261027)

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
ORE_UPLIFT_FULL = 1_100  # [UL] ~500 kt quặng/năm × (155 − ~60 $/t) ≈ 1.240 tỷ, × 80% tự cung [DSC "tự cung 80%"] ⇒ ~1.000-1.250


def q4_bridge():
    """Cầu Q4/2026 cơ sở: LN gộp lõi + TNTC trên tiền ĐÃ trừ cổ tức 25/09."""
    rows = []
    for k, rev, gm in [("thuan", 2450, 0.195), ("coso", 2250, 0.165), ("nghich", 2050, 0.135)]:
        gp = rev * gm
        ebit = gp - 130
        fi = (CASH_DEP_0630 - DIV_PAID_0925 + CFO_Q3_UL - CAPEX_Q3_UL) * SCN[k]["dep"] / 4 + {"thuan": 10, "coso": 0, "nghich": -10}[k]
        pbt = ebit + fi - 25
        np_c = pbt * (1 - TAX)
        rows.append(dict(scn=k, rev=rev, gm=gm, gp=round(gp), ebit=round(ebit), fin_inc=round(fi), pbt=round(pbt),
                         np_cons=round(np_c), np_mi=round(np_c * (1 - MI_SHARE))))
    return pd.DataFrame(rows)


_Q4 = None


def q4(kind):
    global _Q4
    if _Q4 is None:
        _Q4 = q4_bridge().set_index("scn")
    return _Q4[kind]


def year_pnl(k, i, avg_gross_cash):
    s = SCN[k]
    rev_p4 = s["p4_vol"] * s["p4_px"][i] * FX / 1e6          # kt×$/t×VND → tỷ
    rev_tpa = s["tpa_vol"] * s["tpa_px"] * FX / 1e6
    rev = rev_p4 + rev_tpa + s["other"]
    gp = rev * s["gm"][i] + ORE_UPLIFT_FULL * s["reopen"][i]
    ebit_core = gp - SGA
    fin = avg_gross_cash * s["dep"] - DEBT_0630 * 0.065
    pbt = ebit_core + fin
    np_cons = pbt * (1 - TAX) + s["ns_np"][i] / (1 - 0)     # Nghi Sơn 100% DGC, NPAT trực tiếp
    np_mi = (pbt * (1 - TAX)) * (1 - MI_SHARE) + s["ns_np"][i]
    core_np_mi = ebit_core * (1 - TAX) * (1 - MI_SHARE)
    return dict(scn=k, year=2027 + i, rev_core=round(rev), rev_p4=round(rev_p4), rev_tpa=round(rev_tpa), other=s["other"],
                gm_eff=round(gp / rev, 3), gp=round(gp), ebit_core=round(ebit_core), fin_net=round(fin),
                ns_np=s["ns_np"][i], np_cons=round(np_cons), np_mi=round(np_mi), core_np_mi=round(core_np_mi),
                fin_np_mi=round(fin * (1 - TAX) * (1 - MI_SHARE)))


def forecasts():
    rows = []
    gross0 = CASH_DEP_0630 - DIV_PAID_0925 + CFO_Q3_UL - CAPEX_Q3_UL
    for k in SCN:
        fy26_mi = NP_MI_Q1 + NP_MI_Q2 + Q3_MI[k] + q4("np_mi")[k]
        fy26_c = NP_CONS_H1 + Q3_CONS[k] + q4("np_cons")[k]
        rows.append(dict(scn=k, year=2026, np_mi=round(fy26_mi), np_cons=round(fy26_c)))
        # tiền gửi bình quân: trừ capex NS còn lại 2027, cổ tức 30%/năm (3.000 đ = 1.139 tỷ) từ 2027
        g27 = gross0 - NS_CAPEX_LEFT * 0.8 - 1139 * 0.5 + 600
        g28 = g27 - 1139 + 900
        for i, g in enumerate([g27, g28]):
            rows.append(year_pnl(k, i, g))
    return pd.DataFrame(rows)


def prob_1600(n=200_000):
    """P(cả năm ≥1.600) — Q3 ~ phân phối FORECAST (sd≈82, từ khoảng 80% [215;425]); Q4 sd 85 [UL]; tương quan 0,6 [UL]."""
    cov = np.array([[82**2, 0.6 * 82 * 85], [0.6 * 82 * 85, 85**2]])
    z = rng.multivariate_normal([0, 0], cov, n)
    h2_mi = 321 + q4("np_mi")["coso"] + z.sum(1)
    h2_c = 350 + q4("np_cons")["coso"] + z.sum(1) * 1.08
    return dict(need_h2_mi=round(1600 - NP_MI_Q1 - NP_MI_Q2), need_q4_mi_if_q3_base=round(1600 - NP_MI_Q1 - NP_MI_Q2 - 321),
                p_mi=round(float((h2_mi >= 1600 - NP_MI_Q1 - NP_MI_Q2).mean()), 3),
                need_h2_cons=round(1600 - NP_CONS_H1), need_q4_cons_if_q3_base=round(1600 - NP_CONS_H1 - 350),
                p_cons=round(float((h2_c >= 1600 - NP_CONS_H1).mean()), 3))


# ---------------------------------------------------------------- ĐỊNH GIÁ
KE_BASE = DEP_RATE + 1.0 * 0.075     # rf = Big4 12T 6,8% ; β 1,0 (đo 2y 0,79 / 5y 1,20 weekly vs VNINDEX) ; ERP 7,5% [UL]
G_BASE = 0.03
RONIC = 0.12            # [UL] lợi suất vốn đầu tư mới (Nghi Sơn GĐ1 cơ sở 165/2.400 ≈ 7% ; lõi P4 lịch sử cao hơn)
HAIRCUT = {"thuan": 0.05, "coso": 0.15, "nghich": 0.35}   # haircut tiền ròng: pháp lý/thuế tài nguyên/ngoại trừ kiểm toán
NS_MULT = {"thuan": 8, "coso": 7, "nghich": 6}
CORE_PE = {"thuan": 8, "coso": 7, "nghich": 6}            # PE LÕI (đã bỏ tiền) — DGC PE trung vị 10y 8,3 gồm cả lãi tiền gửi


def per_share(x):
    return x * 1000 / SH   # tỷ → đ/cp


def sotp(fc):
    out = []
    for k in SCN:
        r = fc[(fc.scn == k) & (fc.year >= 2027)]
        core_norm = r.core_np_mi.mean()          # chuẩn hoá = TB 2027-28 (KHÔNG dùng đỉnh 2022-25)
        cash = NET_CASH_0930 * (1 - HAIRCUT[k])
        core = core_norm * CORE_PE[k]
        ns = SCN[k]["ns_steady"] * NS_MULT[k] / (1 + KE_BASE) ** 2 - NS_CAPEX_LEFT
        tot = cash + core + ns
        out.append(dict(scn=k, net_cash_0930=round(NET_CASH_0930), haircut=HAIRCUT[k], cash_after_hc=round(cash),
                        core_np_mi_norm=round(core_norm), core_pe=CORE_PE[k], core_val=round(core),
                        nghison_val=round(ns), equity=round(tot),
                        ps_cash=round(per_share(cash)), ps_core=round(per_share(core)), ps_ns=round(per_share(ns)),
                        ps_total=round(per_share(tot))))
    return pd.DataFrame(out)


def dcf_core(k, ke, g, gm_override=None, fc=None):
    """FCFF lõi (gồm Nghi Sơn hoạt động), không nợ dài hạn ⇒ WACC≈Ke. 2027-2031 rồi terminal Gordon.
    D&A ≈ capex duy tu [UL]. ΔWC: 2027 thu hồi 300 tồn kho dư (cơ sở/thuận), sau đó 0."""
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
    for t in range(5):
        f = (ebit[t] * (1 - TAX) * (1 - MI_SHARE) + ns[t]) * (1 - (reinv if t >= 2 else 0)) + wc[t]
        fcff.append(f)
        pv += f / (1 + ke) ** (t + 1)
    tv = fcff[-1] * (1 + g) / (ke - g) / (1 + ke) ** 5
    cash = NET_CASH_0930 * (1 - HAIRCUT[k]) - NS_CAPEX_LEFT
    return per_share(pv + tv + cash)


def multiples(fc):
    """(c) PE lịch sử DGC & peer trên LNST mẹ 2027F (gồm lãi tiền gửi) + P/B chính đáng = (ROE−g)/(Ke−g)."""
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
        eq_core = EQ_MI_0930 - NET_CASH_0930          # VCSH phi-tiền (gồm tồn kho, TSCĐ, XDCB NS)
        roe = core_n / eq_core
        pb_j = max(roe - G_BASE, 0) / (KE_BASE - G_BASE)
        out.append(dict(scn=k, np_mi_norm=round(e_norm), eps_norm=round(per_share(e_norm)),
                        v_pe_dgc10y=round(per_share(e_norm) * pe_dgc10), v_pe_peer_now=round(per_share(e_norm) * pe_peer_now),
                        v_pe_peer10y=round(per_share(e_norm) * pe_peer10), roe_core=round(roe, 3), pb_justified=round(pb_j, 2),
                        v_pb=round(per_share(pb_j * eq_core + NET_CASH_0930 * (1 - HAIRCUT[k])))))
    return pd.DataFrame(out), dict(pe_dgc10=pe_dgc10, pe_peer_now=pe_peer_now, pe_peer10=pe_peer10)


def main():
    pd.set_option("display.width", 250)
    print(f"Net cash 30/09 dựng lại [UL] = {NET_CASH_0930:.0f} tỷ = {per_share(NET_CASH_0930):.0f} đ/cp ; "
          f"VCSH mẹ 30/09 ≈ {EQ_MI_0930:.0f} tỷ, BVPS ≈ {per_share(EQ_MI_0930):.0f}, P/B thật ≈ {PX / per_share(EQ_MI_0930):.2f} ; "
          f"NS capex còn lại ≈ {NS_CAPEX_LEFT} ; Ke = {KE_BASE:.3f}")
    q4 = q4_bridge(); print("\nQ4/2026 bridge\n", q4.to_string(index=False))
    fc = forecasts(); print("\nDự phóng\n", fc.to_string(index=False))
    p = prob_1600(); print("\nP(1.600)", p)
    so = sotp(fc); print("\n(a) SOTP\n", so.to_string(index=False))
    dc = pd.DataFrame([dict(scn=k, dcf=round(dcf_core(k, KE_BASE, G_BASE, fc=fc))) for k in SCN])
    print("\n(b) DCF\n", dc.to_string(index=False))
    sens_kg = pd.DataFrame({f"g={g:.0%}": [round(dcf_core("coso", ke, g, fc=fc)) for ke in (0.12, 0.13, KE_BASE, 0.16, 0.18)]
                            for g in (0.01, 0.02, 0.03, 0.04)}, index=["12%", "13%", f"{KE_BASE:.1%}", "16%", "18%"])
    sens_kgm = pd.DataFrame({f"GM={m:.0%}": [round(dcf_core("coso", ke, G_BASE, gm_override=m, fc=fc)) for ke in (0.12, 0.13, KE_BASE, 0.16, 0.18)]
                             for m in (0.14, 0.17, 0.20, 0.23, 0.26, 0.30)}, index=["12%", "13%", f"{KE_BASE:.1%}", "16%", "18%"])
    print("\nDCF cơ sở: Ke × g\n", sens_kg); print("\nDCF cơ sở: Ke × biên gộp dài hạn\n", sens_kgm)
    mu, refs = multiples(fc); print("\n(c) Multiple", refs, "\n", mu.to_string(index=False))
    so_b0 = so.set_index("scn").loc["coso"]
    hc = pd.DataFrame({f"tồn kho −{inv}": [round(per_share(NET_CASH_0930 * (1 - h) + so_b0.core_val + so_b0.nghison_val - inv * (1 - TAX)))
                                           for h in (0, 0.15, 0.30, 0.50)] for inv in (0, 475, 951)},
                      index=["haircut 0%", "15%", "30%", "50%"])
    print("\nSOTP cơ sở: haircut tiền × xoá sổ tồn kho bị ngoại trừ (951 tỷ)\n", hc); hc.to_csv(os.path.join(HERE, "out_sotp_sens_haircut.csv"))
    # tổng hợp
    summ = so[["scn", "ps_total"]].rename(columns={"ps_total": "sotp"}).merge(dc, on="scn").merge(
        mu[["scn", "v_pe_dgc10y", "v_pe_peer10y", "v_pb"]], on="scn")
    summ["multiple_avg"] = summ[["v_pe_dgc10y", "v_pe_peer10y", "v_pb"]].mean(1).round()
    summ["blend"] = summ[["sotp", "dcf", "multiple_avg"]].mean(1).round()
    summ["w"] = summ.scn.map(W)
    ev = float((summ.blend * summ.w).sum())
    print("\nTổng hợp đ/cp\n", summ.to_string(index=False))
    print(f"\nGiá trị kỳ vọng có trọng số = {ev:.0f} đ/cp vs giá {PX} ⇒ {ev / PX - 1:+.1%}")
    # hoà vốn: lõi chuẩn hoá ngầm định ở giá hiện tại (cơ sở: haircut 15%, PE lõi 7, NS cơ sở)
    so_b = so.set_index("scn").loc["coso"]
    implied_core = (PX * SH / 1000 - so_b.cash_after_hc - so_b.nghison_val) / CORE_PE["coso"]
    print(f"Hoà vốn: giá {PX} ngầm định LNST mẹ LÕI chuẩn hoá ≈ {implied_core:.0f} tỷ/năm "
          f"(so: nghịch {so.set_index('scn').loc['nghich'].core_np_mi_norm}, cơ sở {so_b.core_np_mi_norm}, thuận {so.set_index('scn').loc['thuan'].core_np_mi_norm})")
    for name, df in [("q4", q4), ("forecast", fc), ("sotp", so), ("dcf", dc), ("multiples", mu), ("summary", summ)]:
        df.to_csv(os.path.join(HERE, f"out_{name}.csv"), index=False)
    sens_kg.to_csv(os.path.join(HERE, "out_dcf_sens_ke_g.csv")); sens_kgm.to_csv(os.path.join(HERE, "out_dcf_sens_ke_gm.csv"))
    pd.DataFrame([p | dict(ev=round(ev), implied_core=round(implied_core))]).to_csv(os.path.join(HERE, "out_headline.csv"), index=False)


if __name__ == "__main__":
    main()
