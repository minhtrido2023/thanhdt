"""Biểu đồ báo cáo nhà đầu tư TV1 (02/11/2026). Import bởi build_report.py.
Số định giá: ../valuation_blind_v2_out.json (python3 -I ../valuation_blind_v2.py). Peer: scripts/src_fig_14/15 (peer study 02/11).
Giá: scripts/tv1_px_bq.csv (đến 30/10) + DNSE latest_trade 02/11/2026 14:34:40 (../phase2/dnse_20261102.json).
Hình tái dùng nguyên trạng (dữ liệu BCTC, không chứa định giá): fig_01, fig_04, fig_09, fig_10, fig_11 (+ map_*.png).
"""
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
J = json.load(open(os.path.join(HERE, "..", "valuation_blind_v2_out.json"), encoding="utf-8"))
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"
PX = 19_500                       # DNSE latest_trade 02/11/2026 14:34:40 (phiên đã đóng)
SH = 26_691_319
SRC = "Nguồn: BCTC hợp nhất Q3/2026 (chưa soát xét), BCTC bán niên 2026 (soát xét), BCTC 2025 kiểm toán; tính toán của nhóm nghiên cứu (ước lượng)."
PLAB = {"P1_949": "949 (giữ giá)", "P2_600": "600", "P3_520": "520", "P4_440": "440", "P5_340": "340 (văn bản 2018)"}
CLAB = {"C_bien5": "Biên 5%", "C_thap": "Thấp", "C_giua": "Giữa", "C_cao": "Cao"}


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def k(x):
    return vn(x / 1000, 1) + "k"


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "Be Vietnam Pro", "font.size": 9, "axes.titlesize": 9.6,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#555", "axes.labelcolor": "#333", "xtick.color": "#333",
        "ytick.color": "#333", "figure.facecolor": "white", "savefig.facecolor": "white",
        "axes.grid": True, "grid.color": "#ECEFF2", "grid.linewidth": 0.8, "axes.axisbelow": True})
    return plt


def save(fig, name, source, df):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 160)), fontsize=6.2, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def grid_df():
    rows = []
    for key, v in J["grid"].items():
        pk, ck = key.split("|")
        rows.append(dict(gia_ppa=J["PRICE"][pk], kb_gia=pk, p_gia=J["PROB"][pk], kb_tu_van=ck, p_tu_van=J["P_CON"][ck],
                         trong_so=J["PROB"][pk] * J["P_CON"][ck], gia_tri_dcp=round(v)))
    return pd.DataFrame(rows)


def peer_sotp():
    """Đối chiếu chéo SAU định giá nội tại: thuỷ điện = LNST 2028 theo kịch bản × P/E thuỷ điện UPCOM p25–trung vị (7,9–9,2x),
    tư vấn = LNST lõi 2026E ~45 tỷ (ước lượng) × P/E TV4–TV3 2026 (6,0–9,2x), + tiền ròng điều chỉnh."""
    ni = sum(J["hydro_ni28"][p] * J["PROB"][p] for p in J["PRICE"])
    lo = (ni * 7.9 + 45 * 6.0 + J["netcash_bn"]) * 1e9 / SH
    hi = (ni * 9.22 + 45 * 9.2 + J["netcash_bn"]) * 1e9 / SH
    return ni, lo, hi


def figs():
    plt = setup_mpl()
    import numpy as np
    g = grid_df()
    C, P20, P80, LO, HI = J["centre"], J["p20"], J["p80"], J["lo"], J["hi"]

    # ---------------- fig_00 hero: phân bố giá trị 20 kịch bản vs giá
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    rng = np.random.default_rng(7)
    ys = {pk: i for i, pk in enumerate(J["PRICE"])}
    ax.axvspan(P20, P80, color=NAVY, alpha=0.10)
    for _, r in g.iterrows():
        ax.scatter(r.gia_tri_dcp, ys[r.kb_gia] + rng.uniform(-0.18, 0.18), s=1400 * r.trong_so + 12,
                   color=NAVY, alpha=0.55, edgecolor="white", lw=0.6, zorder=3)
    ax.axvline(C, color=NAVY, lw=2); ax.text(C + 300, 4.45, f"tâm {k(C)}", color=NAVY, fontsize=8, weight="bold")
    ax.axvline(PX, color=ACCENT, lw=1.6, ls="--"); ax.text(PX - 300, -0.75, f"giá {k(PX)} (02/11)", color=ACCENT, fontsize=8, weight="bold", ha="right")
    ax.text(P80 + 300, -0.75, f"P20–P80: {k(P20)}–{k(P80)}", color=NAVY, fontsize=7.4)
    ax.set_yticks(range(5)); ax.set_yticklabels([f"giá điện {PLAB[p]}" for p in J["PRICE"]], fontsize=7.4)
    ax.set_ylim(-1.0, 4.8); ax.set_xlim(0, 47_000); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Giá trị nội tại (đ/cp); mỗi chấm = 1 ô giá điện × tư vấn, cỡ chấm = xác suất (ước lượng)", fontsize=7.4)
    ax.set_title("20 kịch bản: giá trị 4,6k–44,9k, tâm 18,1k sát giá 19,5k")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_00_hero", "Giá DNSE: khớp cuối 14:34:40 ngày 02/11/2026 (UPCOM). Giá trị: DCF thuỷ điện 2027–08/2059 + DCF tư vấn + tiền ròng điều chỉnh; Ke 12,85%. " + SRC, g)

    # ---------------- fig_07 football field
    ni, plo, phi = peer_sotp()
    S = J["sens"]
    rows = [("Toàn bộ 20 kịch bản", LO, HI), ("Dải chính P20–P80", P20, P80),
            ("Giá điện 340 – 949 đ/kWh (tư vấn kỳ vọng)", min(S["Gia_PPA_ky_vong_tu_van"].values()), max(S["Gia_PPA_ky_vong_tu_van"].values())),
            ("Tư vấn biên 5% – cao (thuỷ điện kỳ vọng)", min(S["Tu_van_kich_ban"].values()), max(S["Tu_van_kich_ban"].values())),
            ("Chi phí vốn Ke 14% – 10%", S["Ke"]["14.0%"], S["Ke"]["10.0%"]),
            ("Sản lượng 175 – 236,6 GWh", S["San_luong"]["Q175"], S["San_luong"]["Q236.6"]),
            ("Đối chiếu chéo: bội số peer (sau định giá)", plo, phi)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for i, (lab, lo, hi) in enumerate(rows[::-1]):
        col = GREY if "peer" in lab else (NAVY if i >= len(rows) - 2 else "#5B7BA3")
        ax.barh(i, hi - lo, left=lo, color=col, height=0.55)
        ax.text(hi + 400, i, f"{k(lo)}–{k(hi)}", va="center", fontsize=7)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.4)
    ax.axvline(C, color=NAVY, lw=1.6); ax.axvline(PX, color=ACCENT, lw=1.6, ls="--")
    ax.text(C - 300, len(rows) - 0.45, f"tâm {k(C)}", color=NAVY, fontsize=7.4, weight="bold", ha="right")
    ax.text(PX + 300, len(rows) - 0.45, f"giá {k(PX)}", color=ACCENT, fontsize=7.4, weight="bold")
    ax.set_xlim(0, 50_000); ax.grid(axis="y", visible=False); ax.set_xlabel("đ/cp")
    ax.set_title("Giá 19,5k nằm trong dải chính 11,4k–24,2k, sát tâm 18,1k")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_football", "Mỗi thanh đổi một biến, giữ các biến khác ở tâm. Đối chiếu chéo peer: LNST thuỷ điện 2028 kỳ vọng × P/E thuỷ điện UPCOM 7,9–9,2x + LNST tư vấn ~45 tỷ (ước lượng) × P/E TV4–TV3 6,0–9,2x + tiền ròng. " + SRC,
         pd.DataFrame(rows, columns=["thanh", "thap", "cao"]))

    # ---------------- fig_16 lịch giá điện SB5 + hành lang 2027+
    hist = pd.DataFrame({"nam": [2014, 2015, 2016, 2017, 2022, 2023, 2024, 2025],
                         "gia_rong": [938.78, 938.78, 938.78, 940.76, 949, 949, 949, 949],
                         "nguon": ["PA bán SB5 2018 tr.10-11"] * 4 + ["giá gồm thuế/phí 1.052–1.148 trừ pass-through; ước lượng ròng"] * 4})
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(hist.nam[:4], hist.gia_rong[:4], "o-", color=NAVY, lw=2, label="giá hợp đồng thực hiện")
    ax.plot(hist.nam[4:], hist.gia_rong[4:], "o-", color=NAVY, lw=2)
    ax.plot([2019, 2021], [569.36, 569.36], color=GOLD, lw=2.2, ls="--", label="dự thảo sửa đổi 2018 (chưa từng áp dụng)")
    ax.plot([2022, 2026.4], [243.66, 243.66], color=GOLD, lw=2.2, ls="--")
    ax.plot([2022, 2026.4], [338, 338], color=GOLD, lw=1, ls=":")
    ax.text(2022.1, 262, "bậc 243,66 (+ vận hành ≈95 : ≈340)", fontsize=6.8, color="#8a6d10")
    for pk, p in J["PRICE"].items():
        ax.plot([2027, 2030], [p, p], color=ACCENT, lw=1 + 10 * J["PROB"][pk], alpha=0.75)
        ax.text(2030.15, p, f"{vn(p)} · P {vn(J['PROB'][pk]*100)}%", va="center", fontsize=6.8, color=ACCENT)
    ax.axvspan(2026.6, 2030, color=ACCENT, alpha=0.05)
    ax.text(2027, 1010, "2027+: chưa xác định (ước lượng)", fontsize=7, color=ACCENT, weight="bold")
    ax.set_xlim(2013.5, 2032.3); ax.set_ylim(150, 1080); ax.set_ylabel("đ/kWh (giá ròng)"); ax.set_xticks(range(2014, 2031, 2))
    ax.legend(fontsize=6.8, loc="lower left", frameon=False)
    ax.set_title("Giá điện Sông Bung 5: thực hiện ≈940–949 đ/kWh; bậc thấp 2018 chưa từng áp")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_16_ppa_path", "2014–17: PECC1, Báo cáo phương án bán NMTĐ Sông Bung 5 (8/2018) tr.10–13; 2022–25: doanh thu bán điện trừ thuế tài nguyên và DVMTR (EVN trả thêm ngoài giá), ước lượng; 2018–21: thiếu số liệu. Độ dày đường 2027+ theo xác suất (ước lượng).",
         pd.concat([hist, pd.DataFrame({"nam": ["2027+"] * 5, "gia_rong": list(J["PRICE"].values()), "nguon": [f"kịch bản P={v}" for v in J["PROB"].values()]})]))

    # ---------------- fig_12 LNST thuỷ điện 2028 theo giá PPA
    pr = list(J["PRICE"].values()); ni28 = [J["hydro_ni28"][p] for p in J["PRICE"]]
    hv = [J["hydro_val"][p][str(J["Q"])] * 1e9 / SH for p in J["PRICE"]]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    cols = [NAVY if v > 0 else ACCENT for v in ni28]
    ax.bar(range(5), ni28, color=cols, width=0.6)
    for i, (v, h) in enumerate(zip(ni28, hv)):
        ax.text(i, max(v, 0) + 3, f"{vn(v,1)} tỷ\n(giá trị {k(h)}/cp)", ha="center", fontsize=7)
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(range(5)); ax.set_xticklabels([f"{PLAB[p]}\nP {vn(J['PROB'][p]*100)}%" for p in J["PRICE"]], fontsize=7.2)
    ax.set_ylim(-15, 112); ax.set_ylabel("LNST thuỷ điện 2028, tỷ đ")
    ax.set_title("Mỗi 100 đ/kWh ≈ 15 tỷ LNST; ở 340 đ/kWh lỗ kế toán, dòng tiền vẫn dương")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_12_np_by_ppa", f"Sản lượng {vn(J['Q'],1)} GWh/năm (ước lượng P50); vận hành 2025 trượt 2,5%/năm; khấu hao 38 tỷ đến 2039; chi phí chung 8 tỷ; thuế 20%. Giá trị = DCF dòng tiền chủ sở hữu 2027–08/2059 sau quỹ khen thưởng 20%, Ke 12,85%. 2025 thực tế: kết quả bộ phận thuỷ điện 165,1 tỷ (giá ≈949). " + SRC,
         pd.DataFrame({"gia_ppa": pr, "xac_suat": [J["PROB"][p] for p in J["PRICE"]], "lnst_2028_ty": ni28, "gia_tri_dcp": hv}))

    # ---------------- fig_17 tư vấn: doanh thu, biên lịch sử, hợp đồng ký mới
    yrs = ["2022", "2023", "2024", "2025", "9T/26"]
    dt = [358.4, 318.7, 346.2, 447.0, 324.5]
    mh = J["margin_hist"]
    mlo = [mh["2022"][0], mh["2023"][0], mh["2024"][0], mh["2025"][0], 0.11]
    mhi = [mh["2022"][1], mh["2023"][1], mh["2024"][1], mh["2025"][1], 0.17]
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.bar(range(5), dt, color=LIGHT, width=0.6, label="doanh thu tư vấn (tỷ đ)")
    for i, v in enumerate(dt):
        ax.text(i, 25, vn(v, 0), ha="center", fontsize=7.4, color="#333")
    ax.bar([2.3, 3.3], [280, 835.1], color=GOLD, width=0.22, label="hợp đồng ký mới (tỷ đ)")
    ax.text(3.3, 845, "835,1", ha="center", fontsize=7.2, color="#8a6d10", weight="bold"); ax.text(2.3, 290, "≈280", ha="center", fontsize=7.2, color="#8a6d10")
    ax.set_ylim(0, 960); ax.set_ylabel("tỷ đ"); ax.set_xticks(range(5)); ax.set_xticklabels(yrs)
    a2 = ax.twinx(); a2.grid(False)
    x = np.arange(5)
    a2.fill_between(x, [m * 100 for m in mlo], [m * 100 for m in mhi], color=NAVY, alpha=0.25)
    a2.plot(x, [(a + b) * 50 for a, b in zip(mlo, mhi)], "o-", color=NAVY, lw=2, label="biên EBIT tư vấn (%)")
    for xi, a, b in zip(x, mlo, mhi):
        a2.text(xi + 0.12, (a + b) * 50 + 1.5, f"{vn(a*100)}…{vn(b*100)}%", fontsize=6.8, color=NAVY)
    a2.axhline(0, color=ACCENT, lw=0.8, ls=":"); a2.set_ylim(-25, 30); a2.set_ylabel("biên EBIT, %"); a2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=6.8, loc="upper left", frameon=False)
    ax.set_title("Tư vấn: biên có chu kỳ (âm 2022–23, 11–17% 9T/26); hợp đồng ký mới 2025 kỷ lục")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_17_consulting", "Doanh thu tư vấn = doanh thu thuần − doanh thu thuỷ điện. EBIT tư vấn = tổng các quý (doanh thu × biên EBIT) theo dữ liệu tài chính tổng hợp − kết quả bộ phận thuỷ điện (2025 kiểm toán; 2022–24 mô hình); dải = trước/sau 8 tỷ chi phí chung phân bổ thuỷ điện. Đối chiếu kiểm toán: 2024 10,9 tỷ, 2025 36,8 tỷ. 9T/26: BCTC Q3 chưa soát xét. Hợp đồng ký mới: baodauthau.vn. Ước lượng.",
         pd.DataFrame({"nam": yrs, "dt_tu_van": dt, "bien_lo": mlo, "bien_hi": mhi, "hd_ky_moi": [None, None, 280, 835.1, None]}))

    # ---------------- fig_18 lưới kịch bản (heatmap)
    pks, cks = list(J["PRICE"]), list(J["P_CON"])
    M = np.array([[J["grid"][f"{p}|{c}"] for c in cks] for p in pks])
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    from matplotlib.colors import TwoSlopeNorm
    im = ax.imshow(M, cmap="RdBu", norm=TwoSlopeNorm(vcenter=PX, vmin=0, vmax=46_000), aspect="auto")
    for i in range(5):
        for j in range(4):
            ax.text(j, i, k(M[i, j]), ha="center", va="center", fontsize=8, weight="bold", color="#111")
    ax.set_xticks(range(4)); ax.set_xticklabels([f"Tư vấn {CLAB[c]}\nP {vn(J['P_CON'][c]*100)}%" for c in cks], fontsize=7.2)
    ax.set_yticks(range(5)); ax.set_yticklabels([f"Giá điện {PLAB[p]} · P {vn(J['PROB'][p]*100)}%" for p in pks], fontsize=7.2)
    ax.grid(False)
    ax.set_title("Giá trị/cp theo 20 kịch bản: xanh = cao hơn giá 19,5k, đỏ = thấp hơn")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_18_scenarios", "Ke 12,85%; sản lượng 187,5 GWh; tiền ròng điều chỉnh −64,4 tỷ (gồm quỹ khen thưởng phúc lợi). Xác suất là ước lượng của nhóm nghiên cứu. " + SRC, g)

    # ---------------- fig_19 độ nhạy (tornado)
    tor = [("Giá điện 340 – 949 đ/kWh", S["Gia_PPA_ky_vong_tu_van"]["340"], S["Gia_PPA_ky_vong_tu_van"]["949"]),
           ("Tư vấn biên 5% – cao", S["Tu_van_kich_ban"]["C_bien5"], S["Tu_van_kich_ban"]["C_cao"]),
           ("Ke 14% – 10%", S["Ke"]["14.0%"], S["Ke"]["10.0%"]),
           ("Sản lượng 175 – 236,6 GWh", S["San_luong"]["Q175"], S["San_luong"]["Q236.6"]),
           ("Quỹ khen thưởng 25% – 10% LNST", S["KTPL_ty_le"]["25%"], S["KTPL_ty_le"]["10%"]),
           ("Vốn lưu động 53% – 40% tăng doanh thu", S["VLD"]["53%"], S["VLD"]["40%"])]
    tor.sort(key=lambda t: t[2] - t[1])
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for i, (lab, lo, hi) in enumerate(tor):
        ax.barh(i, lo - C, left=C, color=ACCENT, height=0.55); ax.barh(i, hi - C, left=C, color=NAVY, height=0.55)
        ax.text(lo - 300, i, k(lo), ha="right", va="center", fontsize=7); ax.text(hi + 300, i, k(hi), va="center", fontsize=7)
    ax.axvline(C, color="#333", lw=1); ax.axvline(PX, color=ACCENT, lw=1.2, ls="--")
    ax.text(PX + 200, -0.75, f"giá {k(PX)}", color=ACCENT, fontsize=7); ax.set_ylim(-1, len(tor) - 0.4)
    ax.set_yticks(range(len(tor))); ax.set_yticklabels([t[0] for t in tor], fontsize=7.4); ax.grid(axis="y", visible=False)
    ax.set_xlim(5_000, 38_000); ax.set_xlabel("tâm giá trị, đ/cp")
    ax.set_title("Độ nhạy của tâm 18,1k: giá điện và mảng tư vấn là hai biến lớn nhất")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_19_sensitivity", "Mỗi thanh đổi một biến, các biến khác ở tâm (xác suất kịch bản giữ nguyên trừ biến đang thử). " + SRC,
         pd.DataFrame(tor, columns=["bien", "thap", "cao"]))

    # ---------------- fig_05 tiền ròng điều chỉnh (thác nước)
    steps = [("Tiền + tiền gửi", 198.55), ("Vay (chủ yếu cá nhân)", -129.88), ("Cổ tức phải trả", -43.15), ("Lãi vay cá nhân phải trả", -64.25),
             ("Quỹ khen thưởng phúc lợi", -40.71), ("Quỹ trích từ LNST 9T", -24.93), ("LNST Q4/26 sau quỹ (ước lượng)", 40.0)]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    cum = 0
    for i, (lab, v) in enumerate(steps):
        ax.bar(i, abs(v), bottom=cum if v >= 0 else cum + v, color=GREEN if v > 0 else ACCENT, width=0.6)
        ax.text(i, (cum + v + 6) if v > 0 else (cum + v - 18), vn(v, 1), ha="center", fontsize=7.2, weight="bold")
        cum += v
    ax.bar(len(steps), cum, color=NAVY, width=0.6); ax.text(len(steps), cum - 18, vn(cum, 1), ha="center", fontsize=7.6, weight="bold", color=NAVY)
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(range(len(steps) + 1)); ax.set_xticklabels([s[0] for s in steps] + ["Tiền ròng điều chỉnh"], fontsize=6.4, rotation=18, ha="right")
    ax.set_ylabel("tỷ đ"); ax.set_ylim(-135, 235)
    ax.set_title(f"Tiền dồi dào trên bề mặt; sau nghĩa vụ đã biết và quỹ khen thưởng, tiền ròng ≈ {vn(cum,0)} tỷ")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_05_netcash", "Số dư 30/09/2026 (BCTC Q3, mã 323 quỹ khen thưởng phúc lợi 40,71 tỷ). Gồm khoản vay + lãi cá nhân đang tranh chấp (127,63 tỷ) theo sổ. Quỹ trích từ LNST 9T = 20% × 124,6 (theo tỷ lệ 2025). " + SRC,
         pd.DataFrame(steps + [("Tiền ròng điều chỉnh", cum)], columns=["khoan", "ty_dong"]))

    # ---------------- fig_06 giá 12 tháng (không vẽ vùng giá trị)
    px = pd.read_csv(os.path.join(HERE, "scripts", "tv1_px_bq.csv"), parse_dates=["time"])
    px = pd.concat([px, pd.DataFrame({"time": [pd.Timestamp("2026-11-02")], "Price": [PX], "Close": [PX], "Volume": [62_900]})])
    px = px[px.time >= "2025-11-01"]
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.plot(px.time, px.Close, color=NAVY, lw=1.6)
    for d, lab, dx, dy in [("2026-05-07", "07/05: khởi tố\nlãnh đạo", 0, 6_500), ("2026-10-07", "07/10: GDKHQ\ncổ tức 1.500", -40, 9_000), ("2026-10-30", "30/10: BCTC Q3", 0, 4_500)]:
        r = px.iloc[(px.time - pd.Timestamp(d)).abs().argmin()]
        ax.annotate(lab, (r.time, r.Close), (r.time + pd.Timedelta(days=dx), r.Close + dy), fontsize=6.4, ha="center", color=ACCENT,
                    arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
    hi = px.Close.max(); dhi = px.time[px.Close.idxmax()] if False else px.loc[px.Close.idxmax(), "time"]
    ax.text(dhi, hi + 600, f"đỉnh {k(hi)}", fontsize=6.8, ha="center")
    ax.set_ylim(10_000, hi + 9_000); ax.set_ylabel("đ/cp (điều chỉnh cổ tức)")
    ax.set_title(f"Giá 12 tháng: {k(px.Close.iloc[0])} đến {k(PX)}; đi ngang 18k–20,5k từ giữa tháng 7")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_06_price", "Giá đóng cửa điều chỉnh cổ tức, cơ sở dữ liệu thị trường của nhóm (30/10/2026 khớp DNSE 19.800); 02/11/2026: DNSE khớp cuối 14:34:40. Sự kiện: quan sát, không chứng minh nhân quả.",
         px[["time", "Close", "Volume"]])

    # ---------------- fig_14 peer P/E (không có dải áp cho TV1)
    pe = pd.read_csv(os.path.join(HERE, "scripts", "src_fig_14_peer_pe.csv"))
    th, nh = pe[pe.nhom == "thuy_dien"], pe[pe.nhom == "nhiet_dien"]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.fill_between(th.y, th.pe_p25, th.pe_p75, color=LIGHT, label="Thuỷ điện: p25–p75 (32 mã)")
    ax.plot(th.y, th.pe_med, "o-", color=NAVY, lw=2.2, label="Thuỷ điện: trung vị")
    ax.plot(nh.y, nh.pe_med, "--", color=GREY, lw=1.4, label="Nhiệt điện: trung vị (9 mã)")
    tv = pd.DataFrame({"y": [2026], "pe": [2.8]})
    ax.scatter([2026], [2.8], marker="s", s=60, color=ACCENT, zorder=5, label="TV1: 2,8x (LNST 12T gồm khoản một lần Q3)")
    ax.scatter([2026], [3.3], marker="s", s=30, facecolor="white", edgecolor=ACCENT, zorder=5, label="TV1: 3,3x (bỏ thu nhập khác ròng Q3)")
    for y_, v_ in zip(th.y, th.pe_med):
        ax.text(y_, v_ + 0.9, vn(v_, 1), ha="center", fontsize=6.6, color=NAVY)
    ax.set_ylim(0, 24); ax.set_ylabel("P/E (lần)"); ax.legend(fontsize=6.4, ncol=2, loc="upper left", frameon=False)
    ax.set_title("P/E thuỷ điện niêm yết: trung vị 2026 9,2x; TV1 ≈3x trên lợi nhuận ở giá điện hiện hành")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_14_peer_pe", "P/E trailing, trung vị theo mã–năm của phiên cuối tháng (loại ≤0 hoặc ≥60); 2026 = đến 02/11/2026. Nhóm thuỷ điện = 32 mã ngành điện truyền thống có nhà máy thuỷ điện là chính (phân loại theo tên doanh nghiệp). TV1 tại 19.500 đ. Nguồn: cơ sở dữ liệu thị trường của nhóm nghiên cứu.",
         pd.concat([pe, tv.assign(nhom="TV1")]))

    # ---------------- fig_15 peer yield (không có đường lợi suất yêu cầu)
    yl = pd.read_csv(os.path.join(HERE, "scripts", "src_fig_15_peer_yield.csv"))
    y = yl.yld.dropna() * 100
    n10, n = int((y >= 10).sum()), len(y)
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.hist(y.clip(upper=20), bins=np.arange(0, 21, 1), color=NAVY, alpha=0.8, edgecolor="white")
    ax.axvspan(10, 20, color=GOLD, alpha=0.15); ax.text(10.3, 25, f"≥10%: {n10}/{n} mã–năm;\nchuỗi ≥10% dài nhất 3 năm", fontsize=7, color="#8a6d10")
    ax.axvline(y.median(), color=ACCENT, ls="--"); ax.text(y.median() + 0.2, 28, f"trung vị {vn(y.median(),1)}%", fontsize=7, color=ACCENT)
    ax.axvline(7.7, color=GREEN, lw=1.4); ax.text(7.8, 21, "TV1 FY2025: 7,7%", fontsize=7, color=GREEN)
    ax.set_xlabel("Tỷ suất cổ tức tiền trong năm (%), 2019–2025, mã có trả (cắt ở 20%)"); ax.set_ylabel("số mã–năm")
    ax.set_title("Cổ tức thuỷ điện: trung vị ≈7%/năm; tỷ suất ≥10% hiếm và không bền")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_15_peer_yield", "Tỷ suất = tổng cổ tức tiền có ngày GDKHQ trong năm / giá bình quân cuối tháng. 32 mã thuỷ điện, chỉ mã–năm có trả. TV1: 1.500 đ / 19.500 đ. Nguồn: dữ liệu sự kiện doanh nghiệp + giá của nhóm nghiên cứu.", yl)
    print("figs ok; peer cross-check", round(ni, 1), round(plo), round(phi))


if __name__ == "__main__":
    figs()
