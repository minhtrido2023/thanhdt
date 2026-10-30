"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư DRI — bản v3 (30/10/2026; luật 9–14 skill dd-investor-report: trung dung, font Be Vietnam Pro, banner logo).
Khuôn: build_report.py v1 (../investor_report/) + hình mới figs_v2() (hero, KPI, lịch sử, chuỗi giá trị, địa bàn, cơ cấu DT,
vòng đời vườn, cổ đông, xúc tác) — số trích BCTN 2024/2025 hoặc số đã có ở v1; không có số định giá mới.

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (cùng thư mục figs/):
  fin_quarterly_bq.csv  — tav2_bq.ticker_financial (DRI, 2022Q1–2026Q2; Q3/26 chưa có trong BQ), kéo 29/10/2026
  price_raw.csv         — tav2_bq.ticker (DRI Close/Price/Volume, 01/10/2025–29/10/2026)
Số BCTC (hard-code, có trích nguồn) lấy từ BCTC hợp nhất Q3/2026 (ký 22/10), bán niên 2026 soát xét (AFC, ký 14/08),
báo cáo SXKD 9T/2026 (29/BC-CT, 20/10) — đã trích kèm số trang ở ../extract_q3_bctc.md và ../REPORT_Q3_UPDATE.md.
Số định giá lấy từ ../../dri_val_supply_adj_r4_20261027/REPORT.md + out.txt (bản đã qua phản biện).
Mỗi hình ghi kèm CSV dữ liệu vẽ (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")

NAVY, ACCENT, GREY, LIGHT = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"  # luật 13
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung ----
SH = 73_200_000              # CP lưu hành [BCTC3 vốn góp 732 tỷ]
CLOSE_2810 = 14_500          # đóng cửa 28/10/2026 [BQ tav2_bq.ticker] (chỉ để tham chiếu lịch sử)
CLOSE_2910 = 14_700          # đóng cửa 29/10/2026 = MỐC ĐỊNH GIÁ v3 [DNSE ohlc 1D + tav2_bq.ticker]
PX_3010 = 14_500             # DNSE latest_trade 30/10/2026 10:08:44 ICT (G1, phiên sáng, CHƯA đóng cửa)
EQ_PARENT = 729.862          # VCSH cổ đông mẹ 30/09/2026, tỷ [BCTC3: 400 − 429]
NP_TTM = 40.598 + 167.755    # LNST mẹ Q4/25 [BQ NP_P0] + 9T/26 [BCTC3], tỷ
NET_CASH_AFTER_DIV = 162.8   # tiền 72,57 + TG NH 271,81 − vay 107,64 − cổ tức phải trả 73,92 [BCTC3]
# FV r4 POST-HOC, đường TRUNG BÌNH (L27, capex m7), đ/cp @ mid RSS3 1,865/1,97/2,075/2,18 $/kg [r4 REPORT §0]
MIDS = [1.865, 1.97, 2.075, 2.18]
FV_TB = [8_058, 9_078, 10_097, 11_116]
FV_NHANH = [6_920, 7_903, 8_886, 9_869]
FV_CHAM = [8_906, 9_961, 11_015, 12_070]
GRID_MIN, GRID_MAX = 3_853, 14_319          # lưới 27 ô, min @1,865 / max @2,18 [r4 §0]
CI_LO, CI_HI, CI_MID = 8_000, 12_500, 10_200  # khoảng tin sau phản biện; tâm ~10,2k @2,075 [dri-triggers 27/10 20:0x]
NOREPLANT = (13_225, 15_115)                # đuôi "hoãn/cắt tái canh", số của người phản biện @1,97/@2,18
PEERS = {"TRC": (9.7, 1.18), "DPR": (7.9, 0.89), "PHR": (8.4, 1.61), "GVR": (18.0, 1.89)}  # P/E, P/B [BQ 28/10/2026]


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": ["Be Vietnam Pro", "DejaVu Sans"], "font.size": 9, "axes.titlesize": 9.8,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#555", "axes.labelcolor": "#333", "xtick.color": "#333",
        "ytick.color": "#333", "figure.facecolor": "white", "savefig.facecolor": "white",
        "axes.grid": True, "grid.color": "#ECEFF2", "grid.linewidth": 0.8, "axes.axisbelow": True})
    return plt


def save(fig, name, source, df=None):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.6, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def qlabel(q):
    return q[4:] + "/" + q[2:4]


def vn(v, d=1):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0", "CF_Invest_P0", "Cash_P0", "StDebt_P0", "LtDebt_P0"]:
        fin[c] = fin[c] / 1e9
    q3 = pd.DataFrame([{"quarter": "2026Q3", "Revenue_P0": 135.998, "NP_P0": 25.983}])
    fq = pd.concat([fin[["quarter", "Revenue_P0", "NP_P0"]], q3], ignore_index=True)
    fq["lab"] = fq["quarter"].map(qlabel)
    fq["nguon"] = np.where(fq["quarter"] == "2026Q3", "BCTC HN Q3/26", "BQ ticker_financial")
    x = np.arange(len(fq))
    is26 = fq["quarter"].str.startswith("2026")

    # 1. Doanh thu & biên gộp
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(x, fq["Revenue_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    ax.set_ylabel("Doanh thu thuần quý, tỷ đồng")
    ax.set_xticks(x, fq["lab"], fontsize=6.8, rotation=45)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    gm = {"2025Q3": 35.5, "2026Q3": 34.2}
    for q, v in gm.items():
        i = int(fq.index[fq["quarter"] == q][0])
        ax2.plot(i, v, "o", color=ACCENT, ms=7, zorder=5)
        ax2.annotate(f"{vn(v)}%", (i, v), xytext=(-6, 8), textcoords="offset points", color=ACCENT, fontsize=8.5,
                     fontweight="bold", ha="right")
    i1, i2 = int(fq.index[fq["quarter"] == "2026Q1"][0]), int(fq.index[fq["quarter"] == "2026Q2"][0])
    ax2.plot([i1, i2], [40.6, 40.6], color=ACCENT, lw=2.2)
    ax2.annotate("H1/26 40,6%\n(soát xét)", (i1, 40.6), xytext=(-4, 6), textcoords="offset points", color=ACCENT,
                 fontsize=8, ha="right")
    ax2.plot([], [], "o", color=ACCENT, label="Biên gộp theo BCTC hợp nhất")
    ax2.set_ylim(20, 50); ax2.set_ylabel("Biên gộp, %")
    ax2.legend(loc="upper left", fontsize=7.5, frameon=False)
    ax.set_title("Q3/26: doanh thu −26% YoY, biên gộp 34,2% (H1 40,6%) — giá không giảm, lượng bán giảm")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    gm_col = fq["quarter"].map(gm)
    gm_col[fq["quarter"].isin(["2026Q1", "2026Q2"])] = 40.6
    save(fig, "fig_01_revenue_margin",
         "Nguồn: tav2_bq.ticker_financial Revenue_P0 (= DT thuần, khớp BCTC Q3/25 184,12 tỷ); Q3/26 BCTC HN Q3/2026 (135,998 tỷ). "
         "Biên gộp: BCTC Q3/25, Q3/26; H1/26 theo bản soát xét. Kéo 29/10/2026.",
         fq.assign(bien_gop_bctc_pct=gm_col)[["quarter", "Revenue_P0", "bien_gop_bctc_pct", "nguon"]])
    plt.close(fig)

    # 2. LNST quý + dự báo trước BCTC
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(x, fq["NP_P0"], color=[ACCENT if q == "2026Q3" else (NAVY if q.startswith("2026") else LIGHT) for q in fq["quarter"]], width=0.7)
    for i, v in enumerate(fq["NP_P0"]):
        ax.text(i, v + (1.2 if v >= 0 else -4.5), vn(v), ha="center", fontsize=6.4, color="#333")
    n = len(fq) - 1
    ax.add_patch(plt.Rectangle((n - 0.42, 55), 0.84, 10, fill=False, ls="--", ec=GREY, lw=1.2))
    ax.annotate("Dự báo trước BCTC: 55–65 tỷ\n(trượt; thực 25,98)", (n - 0.42, 60), xytext=(n - 13, 72),
                fontsize=7.5, color="#444", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.set_xticks(x, fq["lab"], fontsize=6.8, rotation=45); ax.set_ylabel("LNST cổ đông mẹ, tỷ đồng")
    ax.set_ylim(-10, 90)
    ax.set_title("LNST mẹ Q3/26 25,98 tỷ (−33% YoY), thấp hơn xa dự báo của nhóm")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_npat_quarterly",
         "Nguồn: tav2_bq.ticker_financial NP_P0 (Q2/26 63,79 = H1 soát xét 142,21 − Q1 78,42); Q3/26 BCTC HN Q3/2026. "
         "Dự báo 55–65 tỷ: DD 27/10/2026 (lập trước khi đọc BCTC Q3).", fq[["quarter", "NP_P0", "nguon"]])
    plt.close(fig)

    # 3. Q3: luồng tấn + thành phẩm tồn kho
    tons = pd.DataFrame({"buoc": ["Tự khai thác", "Mua ngoài", "Chế biến", "Bán"], "tan": [3381, 666, 4086, 2369]})
    inv = pd.DataFrame({"moc": ["01/01/2026", "30/06/2026", "30/09/2026"], "thanh_pham_ty": [153.18, 64.99, 138.81]})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.25, 1]})
    a1.bar(range(4), tons["tan"], color=[NAVY, GREY, NAVY, ACCENT], width=0.62)
    for i, v in enumerate(tons["tan"]):
        a1.text(i, v + 60, vn(v, 0), ha="center", fontsize=8)
    a1.set_xticks(range(4), tons["buoc"], fontsize=7.8); a1.set_ylabel("tấn, Q3/2026"); a1.set_ylim(0, 4800)
    a1.set_title("Q3: chế biến 4.086 t, chỉ bán 2.369 t", fontsize=8.8)
    a2.bar(range(3), inv["thanh_pham_ty"], color=[LIGHT, LIGHT, ACCENT], width=0.6)
    for i, v in enumerate(inv["thanh_pham_ty"]):
        a2.text(i, v + 3, vn(v, 2), ha="center", fontsize=8)
    a2.set_xticks(range(3), inv["moc"], fontsize=7.5); a2.set_ylabel("thành phẩm tồn kho, tỷ đồng"); a2.set_ylim(0, 175)
    a2.set_title("Thành phẩm gấp 2,1 lần trong Q3", fontsize=8.8)
    fig.suptitle("Q3/26 lợi nhuận thấp chủ yếu vì DRI giữ hàng (~1.717 t, ước lượng), không vì giá", x=0.01, ha="left",
                 fontsize=9.8, fontweight="bold")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    save(fig, "fig_03_q3_tons_inventory",
         "Nguồn: báo cáo SXKD 9T/2026 của DRI (29/BC-CT, 20/10/2026; khai thác Q3 = 9T 8.617 − H1 5.236); thành phẩm: BCTC HN Q3/2026 TM 5.6, "
         "bán niên soát xét. Chênh 1.717 t = chế biến − bán (ước lượng).",
         pd.concat([tons.assign(loai="tan_Q3"), inv.assign(loai="thanh_pham")], ignore_index=True))
    plt.close(fig)

    # 4. LNST vs CFO vs capex theo kỳ
    cf = pd.DataFrame({"ky": ["9T/2025", "H1/2026", "Q3/2026 (tính)", "9T/2026"],
                       "lnst_me": [116.80, 142.21, 25.98, 167.75],
                       "cfo": [70.13, 154.45, -29.17, 125.28],
                       "capex": [39.73, 28.34, 4.55, 32.89]})
    xs = np.arange(4); w = 0.26
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(xs - w, cf["lnst_me"], w, color=LIGHT, label="LNST cổ đông mẹ")
    ax.bar(xs, cf["cfo"], w, color=NAVY, label="CFO")
    ax.bar(xs + w, cf["capex"], w, color=ACCENT, label="Chi mua sắm TSCĐ")
    for i in range(4):
        for off, col in ((-w, "lnst_me"), (0, "cfo"), (w, "capex")):
            v = cf[col][i]
            ax.text(i + off, v + (3 if v >= 0 else -12), vn(v), ha="center", fontsize=7)
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(xs, cf["ky"]); ax.set_ylabel("tỷ đồng"); ax.set_ylim(-45, 195)
    ax.legend(fontsize=7.5, frameon=False, ncol=3, loc="upper left")
    ax.set_title("CFO 9T/26 = 0,75× LNST; riêng Q3 CFO âm ~29 tỷ (trả phải trả + tích hàng)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_cfo_npat_capex",
         "Nguồn: BCTC HN Q3/2026 LCTT (CFO 9T 125,28; capex 32,89; 9T/25 70,13 / 39,73); bán niên 2026 soát xét (CFO H1 154,45; capex 28,34; "
         "LNST mẹ 142,21). Q3 = 9T − H1 (tính). CFO/LNST 0,75× dùng LNST hợp nhất 167,44.", cf)
    plt.close(fig)

    # 5. Tiền + tiền gửi vs vay, 3 mốc
    bs = pd.DataFrame({"moc": ["01/01/2026", "30/06/2026", "30/09/2026"],
                       "tien": [93.07, 61.09, 72.57], "tg_co_ky_han_nh": [104.22, 303.50, 271.81],
                       "vay": [104.71, 99.88, 107.64]})
    bs["tien_rong"] = bs["tien"] + bs["tg_co_ky_han_nh"] - bs["vay"]
    xi = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(xi, bs["tien"], 0.55, color=NAVY, label="Tiền")
    ax.bar(xi, bs["tg_co_ky_han_nh"], 0.55, bottom=bs["tien"], color=GREY, label="Tiền gửi có kỳ hạn ngắn hạn")
    ax.bar(xi, -bs["vay"], 0.55, color=LIGHT, label="Vay (âm)")
    ax.plot(xi, bs["tien_rong"], "o-", color=ACCENT, lw=1.5, label="Tiền ròng")
    for i, v in enumerate(bs["tien_rong"]):
        ax.annotate(vn(v), (i, v), xytext=(10, 4), textcoords="offset points", color=ACCENT, fontsize=8, fontweight="bold")
    ax.plot(2.35, NET_CASH_AFTER_DIV, "D", color=ACCENT, ms=6)
    ax.annotate("sau cổ tức phải trả\n73,92 tỷ: 162,8", (2.35, NET_CASH_AFTER_DIV), xytext=(2.45, 30), fontsize=7.3,
                color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
    ax.axhline(0, color="#555", lw=0.8); ax.set_xticks(xi, bs["moc"]); ax.set_xlim(-0.5, 3.1)
    ax.set_ylabel("tỷ đồng"); ax.set_ylim(-140, 420); ax.legend(fontsize=7.3, frameon=False, loc="upper left", ncol=2)
    ax.set_title("Tiền ròng 236,7 tỷ (30/9/26); trừ cổ tức đã chốt chưa chi còn ~163 tỷ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_05_net_cash",
         "Nguồn: BCTC HN Q3/2026 CĐKT (mã 110, 123, 321, 339, 313) và bán niên 2026 soát xét. Không gồm khoản cho cổ đông lớn vay 40 tỷ (mã 265).",
         bs.assign(tien_rong_sau_co_tuc=[None, None, NET_CASH_AFTER_DIV]))
    plt.close(fig)

    # 6. Tiền theo nơi gửi 30/09
    dep = pd.DataFrame([
        ("NH tại Lào — có kỳ hạn", 154.65), ("NH tại Lào — không kỳ hạn", 42.07),
        ("Quỹ TDND Cao su Đắk Lắk — có kỳ hạn", 70.00), ("NH tại Việt Nam — có kỳ hạn", 45.00),
        ("NH tại Việt Nam — không kỳ hạn + tiền mặt", 30.51), ("Lãi dự thu", 2.16),
        ("Cho cổ đông lớn Dakruco vay (dài hạn)", 40.00)], columns=["noi_gui", "ty_dong"])
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    cols = [ACCENT, ACCENT, NAVY, LIGHT, LIGHT, LIGHT, NAVY]
    ax.barh(range(len(dep))[::-1], dep["ty_dong"], color=cols, height=0.6)
    for k, v in enumerate(dep["ty_dong"]):
        ax.text(v + 2, len(dep) - 1 - k, vn(v, 2), va="center", fontsize=7.8)
    ax.set_yticks(range(len(dep))[::-1], dep["noi_gui"], fontsize=7.6); ax.set_xlim(0, 185); ax.set_xlabel("tỷ đồng, 30/09/2026")
    ax.set_title("~197 tỷ ở ngân hàng tại Lào; 70 tỷ ở Quỹ TDND; 40 tỷ cho Dakruco vay")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_cash_location",
         "Nguồn: BCTC HN Q3/2026 TM 5.1 (tiền), 5.2.1 (đầu tư nắm giữ đến đáo hạn); tổng tiền + TG ngắn hạn = 344,38 tỷ. Nguyên tệ, lãi suất, kỳ hạn tiền gửi ở Lào: không thuyết minh.",
         dep)
    plt.close(fig)

    # 7. Đường sản lượng r4
    yrs = [2026, 2027, 2028, 2030, 2032, 2034, 2036, 2038, 2040, 2042, 2045, 2048, 2051, 2054]
    paths = {
        "Giả định cũ (sản lượng gần phẳng, −2%/năm từ 2030)": [14000, 14000, 14000, 13720, 13177, 12655, 12154, 11672, 11210, 10766, 10133, 9537, 8976, 8449],
        "Thanh lý/tái canh NHANH (2027–34)": [13800, 12966, 12131, 10254, 8362, 7072, 8187, 8660, 8305, 7658, 6898, 6898, 6898, 6898],
        "TRUNG BÌNH (2029–36) — đường trung tâm": [13800, 13800, 13800, 11889, 9933, 8136, 6854, 6991, 6636, 6434, 6804, 6898, 6898, 6898],
        "CHẬM (2031–38)": [13800, 13800, 13800, 13524, 11503, 9645, 7858, 5658, 4968, 4765, 6172, 6898, 6898, 6898]}
    lo = [13800, 13800, 13800, 11889, 9933, 5593, 2895, 2793, 3669, 5338, 6804, 6898, 6898, 6898]
    hi = [13800, 13800, 13800, 11889, 9933, 8136, 6854, 7942, 9375, 10818, 9486, 7545, 6898, 6898]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.fill_between(yrs, lo, hi, color=LIGHT, alpha=0.7, label="TRUNG BÌNH, đời cạo 22–32 năm")
    sty = [(GREY, "--", 1.3), ("#7A8A9A", ":", 1.4), (ACCENT, "-", 2.0), (NAVY, "-.", 1.3)]
    for (k, v), (c, ls, lw) in zip(paths.items(), sty):
        ax.plot(yrs, v, color=c, ls=ls, lw=lw, label=k)
    ax.set_ylim(0, 15500); ax.set_ylabel("tấn mủ tự khai thác/năm"); ax.yaxis.set_major_formatter(lambda v, p: vn(v, 0))
    ax.legend(fontsize=6.9, frameon=False, loc="lower left")
    ax.set_title("Chỉ 48% diện tích có dự án tái canh: sản lượng ~2036 còn khoảng một nửa mức 2026")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    df7 = pd.DataFrame({"nam": yrs, **{k: v for k, v in paths.items()}, "TB_Ltap22": lo, "TB_Ltap32": hi})
    save(fig, "fig_07_production_paths",
         "Nguồn: mô hình định giá vòng 4 của nhóm (ước lượng), dựng từ 8.166 ha đang cạo (KH 2026 13.800 t / 1,69 t/ha, BCTN 2025) và dự án tái canh 4.081,64 ha "
         "(NQ 01/2025); đời cạo 27 năm, năng suất cây mới là giả định. Σ2027–54: cũ 314 nghìn t; ba đường mới ~227–228 nghìn t.", df7)
    plt.close(fig)

    # 8. Giá 12 tháng + KL
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[(px["time"] >= "2025-10-30") & (px["time"] <= "2026-10-29")].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.plot(pd.Timestamp("2026-10-30"), PX_3010, "o", color=ACCENT, ms=5)
    a1.annotate("30/10 10:08: 14.500 (DNSE, chưa đóng cửa)", (pd.Timestamp("2026-10-30"), PX_3010), xytext=(pd.Timestamp("2026-05-01"), 15900),
                fontsize=7, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    ev = [("2026-09-22", "~22/09 GDKHQ cổ tức 1.000 đ"), ("2026-10-09", "09/10 đỉnh 16.900"),
          ("2026-10-20", "20/10 SXKD 9T"), ("2026-10-26", "26/10 BCTC Q3 lên web")]
    ymin = px["Close"].min()
    for k, (d, s) in enumerate(ev):
        dd = pd.Timestamp(d)
        a1.axvline(dd, color=GREY, lw=0.8, ls=":")
        a1.text(dd, ymin + 300 + 650 * k, s + " ", fontsize=6.6, color="#444", ha="right")
    a1.set_ylabel("đ/cp (điều chỉnh)"); a1.yaxis.set_major_formatter(lambda v, p: vn(v, 0))
    a2.bar(px["time"], px["Volume"] / 1e6, color=GREY, width=1.0)
    a2.set_ylabel("KL, triệu cp")
    a1.set_title("Giá +55% từ đáy 11/2025 tới đỉnh 09/10/26; −13% từ đỉnh tới 29/10")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_price_12m",
         "Nguồn: tav2_bq.ticker (Close điều chỉnh cổ tức, Volume) 30/10/2025–29/10/2026; điểm 30/10 DNSE latest_trade 10:08:44 ICT (phiên sáng, chưa đóng cửa). "
         "GDKHQ ~22/09 suy từ chênh Close/Price; công ty công bố chi trả từ 20/10/2026 (TB 94/TB-CT). Mốc sự kiện là quan sát, không gán nhân quả.",
         px[["time", "Close", "Price", "Volume"]])
    plt.close(fig)
    lo12, hi12 = px["Close"].min(), px["Close"].max()

    # 9. Football field
    bvps = EQ_PARENT * 1e9 / SH
    pbs = [v[1] for v in PEERS.values()]
    rows = [
        ("Đường TRUNG BÌNH, mid RSS3 1,865–2,18 $/kg", FV_TB[0], FV_TB[-1], FV_TB[1]),
        ("Khoảng tin sau phản biện", CI_LO, CI_HI, CI_MID),
        ("3 đường thanh lý × 4 mid", FV_NHANH[0], FV_CHAM[-1], None),
        ("Lưới 27 ô (đời cạo × capex × đường)", GRID_MIN, GRID_MAX, None),
        ("Đuôi trên: DRI hoãn/cắt tái canh", NOREPLANT[0], NOREPLANT[1], None),
        (f"P/B nhóm cao su × BVPS {vn(bvps, 0)}", min(pbs) * bvps, max(pbs) * bvps, float(np.median(pbs)) * bvps),
        ("Vùng giá 12 tháng (điều chỉnh)", lo12, hi12, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "diem_giua"])
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        c = ACCENT if i < 2 else (GREY if i == 4 else NAVY)
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=c, height=0.5, alpha=0.85)
        ax.text(r["thap"] - 250, yy, vn(r["thap"] / 1e3), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 250, yy, vn(r["cao"] / 1e3), ha="left", va="center", fontsize=7.5)
        if r["diem_giua"] == r["diem_giua"] and r["diem_giua"] is not None:
            ax.plot(r["diem_giua"], yy, "|", color="white", ms=14, mew=2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.6)
    for v, s, c, ls in ((CLOSE_2910, "Đóng cửa 29/10: 14,7k (mốc)", NAVY, "--"), (PX_3010, "30/10 10:08 (DNSE): 14,5k", "#555", ":")):
        ax.axvline(v, color=c, ls=ls, lw=1.1, label=s)
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="lower left")
    ax.set_xlim(0, 22000); ax.set_xlabel("đồng/cổ phiếu (73,2 triệu CP)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá 14,7k nằm trên dải cơ sở, trong dải \"hoãn tái canh\" và dải P/B nhóm")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_09_football_field",
         "Nguồn: mô hình định giá vòng 4 (POST-HOC, ước lượng; vạch trắng: mid 1,97 / tâm phản biện ~10,2k / trung vị P/B); đuôi trên: số của người phản biện @1,97–2,18; "
         "P/B nhóm TRC, DPR, PHR, GVR tav2_bq 28/10/2026 (không đồng nhất: PHR/DPR/GVR có thu nhập đất KCN).", ff)
    plt.close(fig)

    # 10. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("R1", "Giá cao su quay đầu từ đỉnh", 4, 4), ("R2", "Sản lượng giảm khi vườn hết chu kỳ", 4, 4),
        ("R3", "Chính sách đất/thuế/ngoại hối Lào", 2, 5), ("R4", "Thưởng/chi phí dồn Q4", 4, 2),
        ("R5", "Hàng giữ lại gặp giá giảm", 3, 3), ("R6", "Bên liên quan: Dakruco, Quỹ TDND", 2, 4),
        ("R7", "LAK mất giá, LN khó chuyển về mẹ", 3, 3), ("R8", "Chuyển HOSE chậm", 3, 2)],
        columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R1": (-0.25, 0.2), "R2": (-0.25, -0.2), "R5": (-0.25, 0.2), "R7": (-0.25, -0.2)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Giá cao su và tuổi vườn: rủi ro lớn nhất; Lào: xác suất thấp, tác động rất lớn")
    fig.tight_layout(rect=(0, 0.08, 0.68, 1))
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu bản đọc ngành độc lập 27/10/2026.", rk)
    plt.close(fig)

    print(f"BVPS={bvps:.0f} PB28={CLOSE_2810/bvps:.2f} PB29={CLOSE_2910/bvps:.2f} PB30={PX_3010/bvps:.2f}; EPS_TTM={NP_TTM*1e9/SH:.0f} PE28={CLOSE_2810/(NP_TTM*1e9/SH):.2f} PE29={CLOSE_2910/(NP_TTM*1e9/SH):.2f}")
    print(f"12m Close lo={lo12:.0f} hi={hi12:.0f}")
    print(ff.round(0).to_string())


# ------------------------------------------------------------------ HÌNH MỚI v2 (luật 10: hero + hình kiểu BCTN)
# Mọi số dưới đây là số đã có trong bản v1 / nguồn đã phản biện, hoặc trích nguyên văn BCTN 2024/2025
# (../../dri_val_supply_adj_r4_20261027/src/BCTN2025.pdf, BCTN2024.pdf). Không có số định giá mới.
TB_YRS = [2026, 2027, 2028, 2030, 2032, 2034, 2036, 2038, 2040, 2042, 2045, 2048, 2051, 2054]
TB_PATH = [13800, 13800, 13800, 11889, 9933, 8136, 6854, 6991, 6636, 6434, 6804, 6898, 6898, 6898]  # r4 đường TB


def _tree(ax, x0, y0, s=1.0, col=None):
    """Cây cao su cách điệu: thân + vết cạo xoắn + chén hứng mủ + tán lá (chỉ là hình vẽ)."""
    import matplotlib.patches as mp
    col = col or NAVY
    ax.add_patch(mp.FancyBboxPatch((x0 - 0.06 * s, y0), 0.12 * s, 0.95 * s, boxstyle="round,pad=0.01", fc="#6B4F3A", ec="none"))
    for k, (dx, dy, r) in enumerate([(0, 1.25, .42), (-.33, 1.05, .32), (.33, 1.05, .32), (-.18, 1.5, .3), (.2, 1.52, .3)]):
        ax.add_patch(mp.Circle((x0 + dx * s, y0 + dy * s), r * s, fc=[col, "#2E5C8A", "#3E6E9E", "#2E5C8A", "#3E6E9E"][k], ec="white", lw=0.8, alpha=0.95))
    for k in range(3):   # vết cạo xoắn
        yy = y0 + (0.28 + 0.13 * k) * s
        ax.plot([x0 - 0.06 * s, x0 + 0.06 * s], [yy + 0.05 * s, yy], color="#F1E6D8", lw=1.4)
    ax.add_patch(mp.Wedge((x0 + 0.1 * s, y0 + 0.2 * s), 0.07 * s, 180, 360, fc=ACCENT, ec="none"))   # chén mủ
    ax.plot([x0 + 0.06 * s, x0 + 0.1 * s], [y0 + 0.28 * s, y0 + 0.22 * s], color="white", lw=1.6)   # giọt mủ


def foot(fig, text):
    import textwrap
    fig.text(0.01, 0.005, "\n".join(textwrap.wrap(text, 150)), fontsize=5.8, color="#666", va="bottom")


def figs_v2():
    import numpy as np
    import pandas as pd
    import matplotlib.patches as mp
    plt = setup_mpl()

    # 0. HERO trang 1 -------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.15))
    fig.patch.set_facecolor("white")
    band = fig.add_axes([0, 0.86, 1, 0.14]); band.axis("off")
    band.add_patch(mp.Rectangle((0, 0), 1, 1, fc=NAVY, transform=band.transAxes))
    band.text(0.015, 0.5, "DRI · Cao su thiên nhiên tại Nam Lào", color="white", fontsize=10.5, fontweight="bold", va="center")
    band.text(0.985, 0.5, "Giá 14,7k: trên dải cơ sở", color="white", fontsize=10, fontweight="bold", va="center", ha="right",
              bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT, ec="none"))
    # (a) ngành nghề
    a = fig.add_axes([0.0, 0.17, 0.27, 0.68]); a.axis("off"); a.set_xlim(0, 3); a.set_ylim(0, 3.2)
    for (x, sc) in ((0.55, 0.85), (1.45, 1.05), (2.4, 0.85)):
        _tree(a, x, 0.75, sc)
    a.plot([0.05, 2.95], [0.75, 0.75], color="#B9C3CE", lw=1.2)
    a.text(1.5, 0.42, "8.592 ha cao su", ha="center", fontsize=9.2, fontweight="bold", color=NAVY)
    a.text(1.5, 0.2, "Champasak & Salavan (Lào)\nnhà máy 18.000 t/năm", ha="center", va="top", fontsize=6.8, color="#333")
    a.text(0.05, 3.1, "1 · NGÀNH NGHỀ", fontsize=7.6, fontweight="bold", color=ACCENT)
    # (b) tăng trưởng & sản lượng
    b = fig.add_axes([0.335, 0.2, 0.31, 0.50])
    b.bar([2025], [15152.83], color=NAVY, width=1.6)
    b.plot(TB_YRS, TB_PATH, color=ACCENT, lw=2.0)
    b.fill_between(TB_YRS, 0, TB_PATH, color=ACCENT, alpha=0.10)
    b.annotate("2025: 15.153 t\n(kỷ lục, 1,81 t/ha)", (2025, 15152.83), xytext=(2030.5, 14200), fontsize=6.6, color=NAVY,
               arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.6))
    b.annotate("~2036: còn khoảng\nmột nửa mức 2026", (2036, 6854), xytext=(2040, 11300), fontsize=6.6, color=ACCENT,
               arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    b.set_ylim(0, 17500); b.set_xlim(2023.5, 2055); b.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    b.tick_params(labelsize=6.5); b.set_ylabel("tấn mủ/năm", fontsize=6.8)
    fig.text(0.335, 0.83, "2 · TĂNG TRƯỞNG", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.335, 0.81, "LNST 9T/26 +43,6%, tiền ròng 237 tỷ;\nsản lượng giảm dần theo tuổi vườn", fontsize=6.4, color="#333", va="top")
    # (c) định giá
    c = fig.add_axes([0.70, 0.14, 0.24, 0.55])
    c.set_xlim(0, 1); c.set_ylim(6000, 17000); c.grid(False)
    for sp in ("left", "bottom"):
        c.spines[sp].set_visible(False)
    c.set_xticks([]); c.yaxis.tick_right(); c.tick_params(labelsize=6.5)
    c.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    c.add_patch(mp.Rectangle((0.08, CI_LO), 0.4, CI_HI - CI_LO, fc=ACCENT, alpha=0.18, ec="none"))
    c.add_patch(mp.Rectangle((0.08, FV_TB[1]), 0.4, FV_TB[3] - FV_TB[1], fc=ACCENT, alpha=0.85, ec="none"))
    c.add_patch(mp.Rectangle((0.55, NOREPLANT[0]), 0.3, NOREPLANT[1] - NOREPLANT[0], fc="white", ec=GREY, hatch="////", lw=0.8))
    c.text(0.28, (FV_TB[1] + FV_TB[3]) / 2, "giá trị\nhợp lý\n9,1–11,1k", ha="center", va="center", fontsize=6.4, color="white", fontweight="bold")
    c.text(0.28, CI_LO + 250, "khoảng tin 8,0–12,5k", ha="center", fontsize=5.6, color=ACCENT)
    c.text(0.70, NOREPLANT[0] - 250, "nếu hoãn\ntái canh", ha="center", va="top", fontsize=5.8, color="#555")
    c.axhline(CLOSE_2910, xmin=0.02, xmax=0.98, color=NAVY, lw=1.6)
    c.text(0.02, CLOSE_2910 + 280, "Giá 14,7k (29/10)", fontsize=6.6, color=NAVY, fontweight="bold")
    c.plot(0.95, PX_3010, "o", color=NAVY, ms=3.5)
    fig.text(0.69, 0.83, "3 · ĐỊNH GIÁ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.69, 0.81, "trên dải cơ sở; trong dải\nnếu DRI hoãn tái canh", fontsize=6.4, color="#333", va="top")
    foot(fig, "Nguồn: BCTN 2025 (diện tích, nhà máy, sản lượng 2025); BCTC HN Q3/2026; mô hình định giá vòng 4 của nhóm (POST-HOC, ước lượng; "
             "đường TRUNG BÌNH, mid RSS3 1,97–2,18 $/kg); giá: đóng cửa 29/10/2026 (DNSE/tav2_bq), chấm tròn = DNSE 30/10 10:08:44 ICT (14.500, chưa đóng cửa).")
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200)
    pd.DataFrame([("dien_tich_cao_su_ha", 8592.3, "BCTN 2025 tr.37"), ("cong_suat_nha_may_t_nam", 18000, "BCTN 2025 tr.37"),
                  ("san_luong_2025_t", 15152.83, "BCTN 2025"), ("lnst_me_9T26_yoy_pct", 43.6, "BCTC HN Q3/26"),
                  *[(f"duong_TB_{y}_t", v, "mô hình vòng 4 (ước lượng)") for y, v in zip(TB_YRS, TB_PATH)],
                  ("fv_tb_mid197", FV_TB[1], "vòng 4"), ("fv_tb_mid218", FV_TB[3], "vòng 4"), ("ci_lo", CI_LO, "phản biện"),
                  ("ci_hi", CI_HI, "phản biện"), ("duoi_tren_lo", NOREPLANT[0], "phản biện"), ("duoi_tren_hi", NOREPLANT[1], "phản biện"),
                  ("dong_cua_2910_moc", CLOSE_2910, "DNSE ohlc + tav2_bq"), ("gia_3010_1008_dnse", PX_3010, "DNSE latest_trade, chưa đóng cửa")],
                 columns=["chi_tieu", "gia_tri", "nguon"]).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)
    plt.close(fig)

    # 11. Khung KPI ---------------------------------------------------------
    kpi = pd.DataFrame([
        ("Doanh thu thuần 9T/26", "622,0 tỷ", "+27,6% YoY", "DT"),
        ("LNST cổ đông mẹ 9T/26", "167,75 tỷ", "+43,6% YoY", "LN"),
        ("Biên gộp 9T/26", "39,3%", "Q3/26 chỉ 34,2%", "%"),
        ("Tiền ròng 30/9/26", "236,7 tỷ", "sau cổ tức chốt: 162,8 tỷ", "₫"),
        ("Cổ tức tiền 2025", "1.000 đ/cp", "tỷ suất 6,8% @14.700; chi từ 20/10", "CT"),
        ("P/E TTM · P/B", "5,2× · 1,47×", "P/E thấp nhất nhóm cao su", "×")], columns=["chi_tieu", "gia_tri", "ghi_chu", "icon"])
    fig = plt.figure(figsize=(7.2, 2.25))
    for i, r in kpi.iterrows():
        ax = fig.add_axes([0.01 + (i % 3) * 0.33, 0.53 - (i // 3) * 0.47, 0.31, 0.42]); ax.axis("off")
        ax.add_patch(mp.FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.02", fc="#F3F5F7", ec=LIGHT, transform=ax.transAxes))
        ax.add_patch(mp.Circle((0.14, 0.5), 0.1, fc=ACCENT if i in (2, 5) else NAVY, transform=ax.transAxes))
        ax.text(0.14, 0.5, r["icon"], ha="center", va="center", color="white", fontsize=7.5, fontweight="bold", transform=ax.transAxes)
        ax.text(0.3, 0.74, r["chi_tieu"], fontsize=7, color="#555", transform=ax.transAxes)
        ax.text(0.3, 0.44, r["gia_tri"], fontsize=11.5, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(0.3, 0.18, r["ghi_chu"], fontsize=6.6, color=ACCENT if i in (2, 5) else "#444", transform=ax.transAxes)
    foot(fig, "Nguồn: BCTC hợp nhất Q3/2026; giá đóng cửa 29/10/2026 (14.700); P/E trên LNST mẹ TTM 208,4 tỷ, P/B trên VCSH mẹ 729,9 tỷ.")
    fig.savefig(os.path.join(FIGS, "fig_11_kpi.png"), dpi=200)
    kpi.to_csv(os.path.join(FIGS, "fig_11_kpi.csv"), index=False)
    plt.close(fig)

    # 12. Lịch sử hình thành -----------------------------------------------
    ms = pd.DataFrame([
        (2004.9, "19/11/2004", "Thoả thuận tô nhượng đất\ntrồng cao su tại Lào"),
        (2012.1, "02/2012", "Thành lập DRI (cổ phần hoá\ntừ Cao su Đắk Lắk), vốn 500 tỷ"),
        (2012.5, "04–07/2012", "Nhà máy 10.000 t/năm;\ntiếp quản Daklaoruco"),
        (2014.5, "2014", "Tăng vốn lên 732 tỷ"),
        (2015.5, "2015", "80% vườn cây đã\nđưa vào khai thác"),
        (2017.4, "23/5/2017", "Giao dịch trên UPCoM"),
        (2018.5, "2018", "Nâng công suất chế biến\nlên 18.000 t/năm"),
        (2022.5, "2022", "Nhãn hiệu\nCao su Việt Nam"),
        (2024.5, "2024", "FSC cho 6.148,03 ha;\nsầu riêng cho thu hoạch"),
        (2025.5, "2025", "Dự án tái canh 4.081,64 ha;\nsầu riêng 238,12 ha tới 2030"),
        (2026.8, "Q4/2026 (kế hoạch)", "Phấn đấu chuyển sàn HOSE")],
        columns=["x", "moc", "su_kien"])
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); ax.axis("off")
    ax.set_xlim(2003.5, 2028.3); ax.set_ylim(-1.35, 1.35)
    ax.plot([2004, 2027.6], [0, 0], color=NAVY, lw=2.2)
    for k, r in ms.iterrows():
        up = 1 if k % 2 == 0 else -1
        lvl = up * (0.42 if k % 4 in (0, 1) else 0.95)
        c = ACCENT if r["moc"].startswith(("19/11", "Q4")) else NAVY
        ax.plot([r["x"], r["x"]], [0, lvl * 0.88], color=c, lw=0.8)
        ax.plot(r["x"], 0, "o", color=c, ms=6, zorder=3, mfc="white" if "kế hoạch" in r["moc"] else c)
        ax.text(r["x"], lvl, r["moc"], ha="center", va="bottom" if up > 0 else "top", fontsize=6.8, fontweight="bold", color=c)
        ax.text(r["x"], lvl - 0.06 if up > 0 else lvl - 0.17, r["su_kien"], ha="center", va="top", fontsize=5.8, color="#333",
                linespacing=1.15, bbox=dict(fc="white", ec="none", pad=0.5) if up > 0 else None)
    foot(fig, "Nguồn: BCTN 2025 \"Quá trình hình thành và phát triển\" (tr.9–11); thoả thuận dự án 19/11/2004: thuyết minh BCTC (trích ở hồ sơ DD);\n"
             "HOSE: báo cáo SXKD 9T/2026 (20/10/2026) — kế hoạch, chưa phải sự kiện. Mốc rỗng = kế hoạch.")
    fig.savefig(os.path.join(FIGS, "fig_12_history.png"), dpi=200)
    ms.drop(columns="x").to_csv(os.path.join(FIGS, "fig_12_history.csv"), index=False)
    plt.close(fig)

    # 13. Chuỗi giá trị -----------------------------------------------------
    steps = pd.DataFrame([
        ("1. Vườn cây", "8.592,3 ha cao su\n~8.166 ha đang cạo\n1,81 t/ha (2025)"),
        ("2. Cạo mủ", "15.152,83 t tự khai thác\n(2025, +4.036,83 t)\n+ mủ mua ngoài"),
        ("3. Chế biến", "1 nhà máy tại Champasak\n18.000 t/năm\nSVR 3L·10·20·CV50·CV60"),
        ("4. Bán hàng", "14.007,76 t (2025)\n47,24 triệu đ/t · XK 49,13%\nĐài Loan, Hàn, Ấn, EU, Mỹ")],
        columns=["buoc", "so_lieu_2025"])
    fig, ax = plt.subplots(figsize=(7.2, 2.15)); ax.axis("off"); ax.set_xlim(0, 4); ax.set_ylim(0, 1)
    for i, r in steps.iterrows():
        x0 = i * 1.0 + 0.02
        pts = [(x0, 0.62), (x0 + 0.86, 0.62), (x0 + 0.96, 0.78), (x0 + 0.86, 0.94), (x0, 0.94), (x0 + 0.1, 0.78)] if i else \
              [(x0, 0.62), (x0 + 0.86, 0.62), (x0 + 0.96, 0.78), (x0 + 0.86, 0.94), (x0, 0.94)]
        ax.add_patch(mp.Polygon(pts, fc=ACCENT if i == 3 else NAVY, ec="white"))
        ax.text(x0 + 0.47, 0.78, r["buoc"], ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        ax.text(x0 + 0.47, 0.52, r["so_lieu_2025"], ha="center", va="top", fontsize=6.6, color="#222", linespacing=1.35)
    foot(fig, "Nguồn: BCTN 2025 (Daklaoruco tr.37; kết quả SXKD 2025 tr.30–31). Thị trường xuất khẩu chính 2025 theo BCTN; "
             "784,32 t bán chuẩn EUDR/FSC, cao hơn bình quân 130 USD/t. BCTC không công bố cơ cấu khách hàng.")
    fig.savefig(os.path.join(FIGS, "fig_13_value_chain.png"), dpi=200)
    steps.to_csv(os.path.join(FIGS, "fig_13_value_chain.csv"), index=False)
    plt.close(fig)

    # 14. Sơ đồ địa bàn (cách điệu) + sử dụng đất --------------------------
    land = pd.DataFrame([("Cao su", 8592.3), ("Điều", 465.67), ("Đất trống, hành lang ven suối…", 191.23), ("Sầu riêng (2025)", 30.48)],
                        columns=["loai", "ha"])
    fig = plt.figure(figsize=(7.2, 3.0))
    m = fig.add_axes([0.0, 0.08, 0.56, 0.9]); m.axis("off"); m.set_xlim(0, 10); m.set_ylim(0, 7)
    m.add_patch(mp.Polygon([(0.3, 6.8), (5.6, 6.8), (6.0, 4.6), (5.2, 2.6), (4.6, 0.6), (0.3, 0.6)], fc="#EEF1F5", ec="#B9C3CE", lw=0.8))   # Lào (cách điệu)
    m.add_patch(mp.Polygon([(6.4, 6.8), (9.8, 6.8), (9.8, 0.3), (6.9, 0.3), (6.3, 2.4), (6.9, 4.6)], fc="#F7F3EE", ec="#D8CBB8", lw=0.8))  # VN (cách điệu)
    xs = np.linspace(0.6, 6.6, 50); m.plot(1.8 + 0.35 * np.sin(xs * 1.3), xs, color="#7FA7C9", lw=2.2, alpha=0.9)   # Mê Kông
    m.text(1.05, 4.6, "Sông Mê Kông", fontsize=6, color="#4F7FA8", rotation=90)
    m.text(0.6, 0.75, "LÀO", fontsize=8.5, color="#8795A5", fontweight="bold")
    m.text(9.6, 0.5, "VIỆT NAM", fontsize=8.5, color="#B0A089", fontweight="bold", ha="right")
    m.add_patch(mp.FancyBboxPatch((2.6, 4.3), 2.7, 1.6, boxstyle="round,pad=0.08", fc=NAVY, ec="none", alpha=0.85))
    m.text(3.95, 5.1, "SALAVAN\nvườn cao su", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    m.add_patch(mp.FancyBboxPatch((2.15, 1.35), 3.9, 2.45, boxstyle="round,pad=0.08", fc=NAVY, ec="none"))
    m.text(4.1, 3.3, "CHAMPASAK", ha="center", fontsize=7.5, color="white", fontweight="bold")
    m.text(4.1, 2.95, "Daklaoruco (100%), Bản Tha Luông\nnhà máy chế biến 18.000 t/năm\nvườn cao su, điều, sầu riêng", ha="center", va="top", fontsize=5.7, color="white")
    m.add_patch(mp.FancyBboxPatch((7.1, 3.6), 2.4, 2.4, boxstyle="round,pad=0.08", fc=ACCENT, ec="none"))
    m.text(8.3, 5.6, "ĐẮK LẮK", ha="center", fontsize=7.5, color="white", fontweight="bold")
    m.text(8.3, 5.25, "Trụ sở DRI (công ty mẹ,\nbán hàng & xuất khẩu)\nCNC DRI 83,87%\n(Krông Búk)", ha="center", va="top", fontsize=6, color="white")
    m.annotate("", xy=(6.15, 2.6), xytext=(7.05, 3.55), arrowprops=dict(arrowstyle="<->", color="#555", lw=1, ls="--"))
    m.text(6.95, 2.55, "mủ, cổ tức,\nvốn", fontsize=5.8, color="#555", ha="center")
    m.text(0.4, 0.15, "Sơ đồ cách điệu, không theo tỷ lệ địa lý.", fontsize=5.8, color="#888", style="italic")
    b = fig.add_axes([0.66, 0.24, 0.32, 0.62])
    b.barh(range(len(land))[::-1], land["ha"], color=[NAVY, GREY, LIGHT, ACCENT])
    for i, v in enumerate(land["ha"]):
        b.text(v + 120, len(land) - 1 - i, vn(v, 2), va="center", fontsize=7)
    b.set_yticks(range(len(land))[::-1], land["loai"], fontsize=6.8); b.set_xlim(0, 11000)
    b.xaxis.set_major_formatter(lambda v, p: vn(v, 0)); b.tick_params(axis="x", labelsize=6.3)
    b.set_title("Daklaoruco quản lý 9.276,07 ha", fontsize=8.2)
    foot(fig, "Nguồn: BCTN 2025 tr.12–13, 37 (vùng dự án Champasak, Salavan; Daklaoruco; CNC DRI). Các cấu phần đất BCTN liệt kê cộng lại "
             "9.279,68 ha, lệch 3,61 ha so với tổng công bố 9.276,07 ha (BCTN ghi \"…\" sau các cấu phần).")
    fig.savefig(os.path.join(FIGS, "fig_14_map_land.png"), dpi=200)
    land.to_csv(os.path.join(FIGS, "fig_14_map_land.csv"), index=False)
    plt.close(fig)

    # 15. Doanh thu năm + cơ cấu --------------------------------------------
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    fin["y"] = fin["quarter"].str[:4]
    ann = fin[fin["y"] <= "2025"].groupby("y")[["Revenue_P0", "NP_P0"]].sum().div(1e9).reset_index()
    ann = pd.concat([ann, pd.DataFrame([{"y": "9T/2026", "Revenue_P0": 622.0, "NP_P0": 167.75}])], ignore_index=True)
    mix = pd.DataFrame({"khoan_muc": ["Cao su", "Sầu riêng", "Điều", "Chuối", "Khác"],
                        "2024_pct": [89.93, 4.21, 0.75, 0.41, 4.70], "2025_pct": [93.58, 2.84, 0.36, 0.0, 3.22],
                        "2024_trieu": [444566, 20790, 3699, 2016, 23256], "2025_trieu": [661700, 20091, 2544, 0, 22790]})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.5, 1]})
    xx = np.arange(len(ann))
    a1.bar(xx - 0.2, ann["Revenue_P0"], 0.4, color=[LIGHT] * 4 + [NAVY], label="Doanh thu thuần")
    a1.bar(xx + 0.2, ann["NP_P0"], 0.4, color=[GREY] * 4 + [ACCENT], label="LNST cổ đông mẹ")
    for i, r in ann.iterrows():
        a1.text(i - 0.2, r["Revenue_P0"] + 8, vn(r["Revenue_P0"], 0), ha="center", fontsize=6.4)
        a1.text(i + 0.2, r["NP_P0"] + 8, vn(r["NP_P0"], 0), ha="center", fontsize=6.4, color=ACCENT if i == 4 else "#333")
    a1.set_xticks(xx, ann["y"], fontsize=7); a1.set_ylabel("tỷ đồng"); a1.legend(fontsize=6.6, frameon=False, loc="upper left")
    a1.set_title("Lợi nhuận tăng gần 3 lần từ 2022 nhờ giá và sản lượng", fontsize=8.4)
    bottom = np.zeros(2); cols = [NAVY, ACCENT, GREY, LIGHT, "#C9D3DD"]
    for (k, r), c in zip(mix.iterrows(), cols):
        vals = np.array([r["2024_pct"], r["2025_pct"]])
        a2.bar([0, 1], vals, bottom=bottom, color=c, width=0.55, label=r["khoan_muc"])
        if vals[1] > 2.5:
            for j in (0, 1):
                a2.text(j, bottom[j] + vals[j] / 2, f"{vn(vals[j], 1)}%", ha="center", va="center", fontsize=6.5, color="white" if c in (NAVY, ACCENT) else "#333")
        bottom += vals
    a2.set_xticks([0, 1], ["2024", "2025"]); a2.set_ylim(0, 100); a2.set_ylabel("% doanh thu (BCTN)")
    a2.legend(fontsize=6, frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    a2.set_title("Cao su = 93,6% doanh thu", fontsize=8.4)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_15_revenue_mix",
         "Nguồn: trái — tav2_bq.ticker_financial (tổng 4 quý Revenue_P0, NP_P0; 2025 = 684,3 tỷ DT thuần), 9T/2026 BCTC HN Q3/2026. "
         "Phải — BCTN 2025 \"Cơ cấu doanh thu\" (gồm thu nhập tài chính; tổng 707,12 tỷ, khác DT thuần).",
         pd.concat([ann.rename(columns={"y": "ky"}), mix], axis=1))
    plt.close(fig)

    # 16. Vòng đời vườn cây + diện tích tái canh + năng suất -----------------
    fig = plt.figure(figsize=(7.2, 3.2))
    a = fig.add_axes([0.04, 0.55, 0.92, 0.33]); a.axis("off"); a.set_xlim(0, 36); a.set_ylim(0, 1)
    ph = [(0, 7, NAVY, "KTCB ~7 năm", "chăm sóc 24,655 tr đ/ha/năm\n⇒ capex ~172,6 tr đ/ha"),
          (7, 34, ACCENT, "Cạo mủ ~27 năm (giả định của mô hình)", "nguồn lợi nhuận duy nhất của vườn"),
          (34, 36, GREY, "Thanh lý", "gỗ ~20,9 tr đ/ha\n(ước lượng)")]
    for x0, x1, c, t, s in ph:
        a.add_patch(mp.FancyBboxPatch((x0 + 0.1, 0.45), x1 - x0 - 0.2, 0.42, boxstyle="round,pad=0.02", fc=c, ec="none"))
        a.text((x0 + x1) / 2, 0.66, t if x1 - x0 > 3 else "", ha="center", va="center", color="white", fontsize=7.2, fontweight="bold")
        a.text((x0 + x1) / 2, 0.38, s, ha="center", va="top", fontsize=6.2, color="#333")
    a.text(35, 0.66, "TL", ha="center", va="center", color="white", fontsize=7, fontweight="bold")
    a.text(35, 0.95, "→ tái canh = vòng đời mới", fontsize=6.4, color="#555", ha="right")
    fig.text(0.04, 0.92, "Vòng đời một ha cao su (năm)", fontsize=8.4, fontweight="bold", color="#222")
    b1 = fig.add_axes([0.2, 0.14, 0.3, 0.26])
    ar = pd.DataFrame([("Có dự án tái canh", 4081.64), ("Chưa có kế hoạch\ntrồng lại", 4216.0)], columns=["nhom", "ha"])
    b1.barh([1, 0], ar["ha"], color=[NAVY, ACCENT], height=0.6)
    for i, v in enumerate(ar["ha"]):
        b1.text(v + 60, 1 - i, (vn(v, 2) if i == 0 else "~" + vn(v, 0)) + " ha", va="center", fontsize=6.8)
    b1.set_yticks([1, 0], ar["nhom"], fontsize=6.6); b1.set_xlim(0, 6000); b1.tick_params(axis="x", labelsize=6)
    b1.set_title("Chỉ ~48% diện tích đang cạo có kế hoạch tái canh", fontsize=7.6)
    b2 = fig.add_axes([0.64, 0.14, 0.32, 0.26])
    yl = pd.DataFrame([("2023", 1.63), ("2024", 1.34), ("2025", 1.81), ("KH 2026", 1.69)], columns=["nam", "t_ha"])
    b2.bar(range(4), yl["t_ha"], color=[LIGHT, LIGHT, NAVY, GREY], width=0.6)
    for i, v in enumerate(yl["t_ha"]):
        b2.text(i, v + 0.04, vn(v, 2), ha="center", fontsize=6.6)
    b2.set_xticks(range(4), yl["nam"], fontsize=6.6); b2.set_ylim(0, 2.2); b2.tick_params(axis="y", labelsize=6)
    b2.set_title("Năng suất, tấn/ha", fontsize=7.6)
    foot(fig, "Nguồn: BCTN 2024/2025 (năng suất, chi phí KTCB/ha, dự án tái canh 4.081,64 ha; 2015: 80% diện tích đã khai thác); "
             "đời cạo 27 năm, capex/ha, giá gỗ, ~4.216 ha: giả định/ước lượng của mô hình định giá vòng 4.")
    fig.savefig(os.path.join(FIGS, "fig_16_lifecycle.png"), dpi=200)
    pd.concat([pd.DataFrame([(a_, b_, c_, s_) for a_, b_, _, c_, s_ in ph], columns=["tu_nam", "den_nam", "giai_doan", "ghi_chu"]), ar, yl], axis=1) \
        .to_csv(os.path.join(FIGS, "fig_16_lifecycle.csv"), index=False)
    plt.close(fig)

    # 17. Cổ đông & quan hệ hệ sinh thái -----------------------------------
    rel = pd.DataFrame([
        ("Dakruco → DRI", "sở hữu 45% (32,94 triệu CP)", "BCTN 2025, 01/08/2025"),
        ("Cổ đông khác → DRI", "54,25% trong nước + 0,75% nước ngoài; 6.716 cổ đông", "BCTN 2025"),
        ("DRI → Daklaoruco (Lào)", "100%, vốn điều lệ 25 triệu USD", "BCTN 2025"),
        ("DRI → CNC DRI (Đắk Lắk)", "83,87%, vốn điều lệ 31 tỷ", "BCTN 2025"),
        ("DRI cho Dakruco vay", "còn 40 tỷ (30/9/26); TSĐB 6 triệu CP DRI", "BCTC HN Q3/26"),
        ("DRI ↔ Quỹ TDND Cao su Đắk Lắk", "tiền gửi 70 tỷ + góp vốn 3 tỷ", "BCTC HN Q3/26"),
        ("Cổ tức 2025 phải trả Dakruco", "32,94 tỷ (chưa chi tại 30/9)", "BCTC HN Q3/26")], columns=["quan_he", "noi_dung", "nguon"])
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 6)

    def node(x, y, w, h, t, fc, fs=7.2):
        ax.add_patch(mp.FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.06", fc=fc, ec="none"))
        ax.text(x, y, t, ha="center", va="center", fontsize=fs, color="white" if fc in (NAVY, ACCENT, "#2E5C8A") else "#222", fontweight="bold")
    node(5, 3.2, 2.2, 0.9, "DRI\n73,2 triệu CP", NAVY, 8)
    node(1.6, 5.2, 2.6, 0.8, "Dakruco\n(CTCP Cao su Đắk Lắk)", ACCENT)
    node(8.4, 5.2, 2.6, 0.8, "6.716 cổ đông khác\n55%", LIGHT)
    node(2.6, 0.8, 2.8, 0.8, "Daklaoruco (Lào)\n100% · 25 tr USD", "#2E5C8A")
    node(7.4, 0.8, 2.8, 0.8, "CNC DRI (Đắk Lắk)\n83,87% · 31 tỷ", "#2E5C8A")
    node(8.6, 3.2, 2.2, 0.8, "Quỹ TDND\nCao su Đắk Lắk", "#E9ECF0", 6.8)
    arr = dict(arrowstyle="-|>", color="#555", lw=1.0)
    ax.annotate("", xy=(4.2, 3.6), xytext=(2.2, 4.8), arrowprops=arr); ax.text(2.55, 4.15, "45%", fontsize=7.5, fontweight="bold", color=ACCENT)
    ax.annotate("", xy=(5.8, 3.6), xytext=(7.8, 4.8), arrowprops=arr); ax.text(7.05, 4.15, "55%", fontsize=7.5, color="#444")
    ax.annotate("", xy=(3.2, 1.2), xytext=(4.5, 2.75), arrowprops=arr)
    ax.annotate("", xy=(6.8, 1.2), xytext=(5.5, 2.75), arrowprops=arr)
    ax.annotate("", xy=(2.9, 4.85), xytext=(4.4, 3.65), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.1, ls="--"))
    ax.text(3.55, 4.95, "cho vay còn 40 tỷ\n(TSĐB: 6 tr CP DRI)\ncổ tức chờ chi 32,94 tỷ", fontsize=6.2, color=ACCENT, va="bottom")
    ax.annotate("", xy=(7.45, 3.2), xytext=(6.15, 3.2), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.1, ls="--"))
    ax.text(6.8, 2.7, "tiền gửi 70 tỷ\n+ góp vốn 3 tỷ", fontsize=6.2, color=ACCENT, ha="center", va="top")
    ax.text(0.05, 2.6, "Đường liền: sở hữu\nĐường đứt: dòng tiền /\nrủi ro bên liên quan", fontsize=6.2, color="#555", va="top")
    foot(fig, "Nguồn: BCTN 2025 (cơ cấu cổ đông tại 01/08/2025; công ty con); BCTC HN Q3/2026 (khoản cho vay, tiền gửi, cổ tức phải trả). "
             "Quan hệ giữa Quỹ TDND và hệ sinh thái Dakruco chưa xác minh.")
    fig.savefig(os.path.join(FIGS, "fig_17_ownership.png"), dpi=200)
    rel.to_csv(os.path.join(FIGS, "fig_17_ownership.csv"), index=False)
    plt.close(fig)

    # 18. Timeline xúc tác ----------------------------------------------------
    cat = pd.DataFrame([
        ("2026-11-10", "~10/11", "SXKD tháng 10", "nowcast Q4: tấn bán, LNTT 10T", 1),
        ("2026-11-26", "26/11", "Chấm dự báo giá #1", "TSR20 vs 254,3¢", 0),
        ("2026-12-10", "~10/12", "SXKD tháng 11", "", 0),
        ("2026-12-31", "30–31/12", "EUDR áp dụng; HOSE (kế hoạch Q4)", "quyết định niêm yết", 0),
        ("2027-01-20", "~20/01", "BCTC Q4/2026", "tồn kho, CFO, thưởng", 1),
        ("2027-01-25", "25/01", "Chấm dự báo giá #2", "", 0),
        ("2027-03-15", "~03/2027", "BCTC kiểm toán 2026", "ý kiến kiểm toán", 1),
        ("2027-04-25", "ĐHĐCĐ 2027", "Kế hoạch 2027", "hoãn/cắt tái canh?", 1)],
        columns=["ngay", "nhan", "su_kien", "kiem", "quan_trong"])
    cat["d"] = pd.to_datetime(cat["ngay"])
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); ax.axis("off")
    t0, t1 = pd.Timestamp("2026-10-20"), pd.Timestamp("2027-05-25")
    ax.set_xlim(t0, t1); ax.set_ylim(-1.75, 1.6)
    ax.plot([t0, t1], [0, 0], color=NAVY, lw=2)
    for mth in pd.date_range("2026-11-01", "2027-05-01", freq="MS"):
        ax.plot([mth, mth], [-0.06, 0.06], color=NAVY, lw=1)
        ax.text(mth, -0.16, f"{mth.month:02d}/{str(mth.year)[2:]}", ha="center", va="top")
    lv = [0.45, 1.2, -0.45, -1.2, 0.45, 1.2, -0.45, 0.45]
    for (k, r), y in zip(cat.iterrows(), lv):
        c = ACCENT if r["quan_trong"] else NAVY
        ax.plot([r["d"], r["d"]], [0, y], color=c, lw=0.7, alpha=0.6)
        ax.plot(r["d"], 0, "o", color=c, ms=5.5, zorder=3)
        txt = f"{r['nhan']} · {r['su_kien']}" + (f"\n{r['kiem']}" if r["kiem"] else "")
        ax.text(r["d"], y, txt, ha="center", va="bottom" if y > 0 else "top", fontsize=5.9, color=c if r["quan_trong"] else "#333",
                fontweight="bold" if r["quan_trong"] else "normal", linespacing=1.15, zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.6))
    foot(fig, "Nguồn: mục 10 của báo cáo (lịch công bố thông lệ của DRI; mốc chấm dự báo giá của bản đọc ngành độc lập 27/10/2026). "
             "Ngày có \"~\" là ước theo thông lệ; HOSE là kế hoạch công bố. Màu nhấn = mốc có thể làm đổi nhận định (cả hai chiều).")
    fig.savefig(os.path.join(FIGS, "fig_18_catalysts.png"), dpi=200)
    cat.drop(columns="d").to_csv(os.path.join(FIGS, "fig_18_catalysts.csv"), index=False)
    plt.close(fig)

    # 19. Giá RSS3 10 năm + mức giá thị trường đang ngầm định ------------------
    rs = pd.read_csv(os.path.join(FIGS, "rss3_monthly_src.csv"))
    rs = rs[rs["month"] >= "2016-10"].reset_index(drop=True)
    rs["d"] = pd.to_datetime(rs["month"] + "-01")
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(rs["d"], rs["price"], color=NAVY, lw=1.5)
    ax.fill_between(rs["d"], 0, rs["price"], color=NAVY, alpha=0.06)
    refs = [(1.865, "trung vị danh nghĩa 10 năm 1,865", GREY, ":"), (2.075, "trung vị 5 năm 2,075", GREY, "--"),
            (2.18, "≈ trung vị thực 10 năm 2,18", NAVY, "--"), (2.55, "ngầm định ~2,55 nếu tái canh đúng kế hoạch (giá 14.700)", ACCENT, "-")]
    for v, t, c, ls in refs:
        ax.axhline(v, color=c, ls=ls, lw=1.1)
        ax.text(rs["d"].iloc[3], v + 0.025, t, fontsize=6.5, color=c, va="bottom")
    last = rs.iloc[-1]
    ax.plot(last["d"], last["price"], "o", color=ACCENT, ms=5)
    ax.annotate("T9/2026: 2,75", (last["d"], last["price"]), xytext=(-60, 10), textcoords="offset points", fontsize=7, color=ACCENT, fontweight="bold")
    ax.set_ylim(1.0, 3.1); ax.set_ylabel("RSS3, USD/kg (tháng)")
    ax.set_title("Giá cao su ở vùng cao nhất 10 năm; giá cổ phiếu ngầm định ~2,55 $/kg (có tái canh) hoặc ~2,1 (hoãn)")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_19_rss3_10y",
         "Nguồn: World Bank CMO, RSS3 bình quân tháng 10/2016–09/2026 (data/rubber_monthly.csv). Trung vị 10 năm/5 năm tính trên chuỗi này; "
         "trung vị thực và mức ngầm định ~2,55 $/kg tại 14.700 (ngoại suy tuyến tính đường TRUNG BÌNH, ước lượng) theo mô hình định giá vòng 4.",
         rs[["month", "price"]])
    plt.close(fig)

    # 20. Vị thế trong nhóm cao su niêm yết (P/E, P/B) -------------------------
    bv = EQ_PARENT * 1e9 / SH
    pe_dri, pb_dri = CLOSE_2910 / (NP_TTM * 1e9 / SH), CLOSE_2910 / bv
    pr = pd.DataFrame([(k, v[0], v[1], d) for (k, v), d in zip(PEERS.items(), ["gần thuần mủ, vườn Campuchia", "có khu công nghiệp",
                       "thu nhập đất KCN", "tập đoàn, quỹ đất lớn"])] + [("DRI", round(pe_dri, 1), round(pb_dri, 2), "thuần mủ, toàn bộ vườn ở Lào")],
                      columns=["ma", "pe", "pb", "dac_diem"])
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    for _, r in pr.iterrows():
        dri = r["ma"] == "DRI"
        ax.scatter(r["pe"], r["pb"], s=160 if dri else 90, color=ACCENT if dri else NAVY, zorder=3)
        ax.annotate(f"{r['ma']}  ({r['dac_diem']})", (r["pe"], r["pb"]), xytext=(8, -3), textcoords="offset points",
                    fontsize=7, color=ACCENT if dri else "#333", fontweight="bold" if dri else "normal")
    ax.set_xlim(3, 24); ax.set_ylim(0.6, 2.2); ax.set_xlabel("P/E (lần)"); ax.set_ylabel("P/B (lần)")
    ax.set_title("DRI rẻ nhất nhóm theo P/E vì lợi nhuận đỉnh và rủi ro Lào; P/B nằm giữa nhóm")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_20_peers",
         "Nguồn: tav2_bq 28/10/2026 (P/E, P/B nhóm); DRI tính lại trên LNST mẹ TTM tới Q3/26 và VCSH mẹ 30/9/26 tại đóng cửa 29/10 (14.700). "
         "Nhóm không đồng nhất (PHR, DPR, GVR định giá một phần theo đất khu công nghiệp) — chỉ là khung tham chiếu.", pr)
    plt.close(fig)


# 21. Ba kịch bản (v3, luật 12) — chỉ dùng số đã phản biện; xác suất là NHẬN ĐỊNH chủ quan -----------
SCEN = [  # (tên, xác suất chủ quan, thấp, cao, mô tả)
    ("Tích cực", 0.25, NOREPLANT[0], NOREPLANT[1], "hoãn/thu hẹp tái canh; mid RSS3 1,97–2,18 $/kg"),
    ("Cơ sở", 0.50, FV_TB[1], FV_TB[3], "tái canh đúng kế hoạch (đường TB); mid 1,97–2,18"),
    ("Tiêu cực", 0.25, FV_NHANH[0], FV_TB[0], "giá về trung vị danh nghĩa 10 năm 1,865; tái canh nhanh–TB")]


def fig_scenarios():
    import pandas as pd
    plt = setup_mpl()
    df = pd.DataFrame(SCEN, columns=["kich_ban", "xac_suat_chu_quan", "thap", "cao", "gia_dinh"])
    df["giua"] = (df["thap"] + df["cao"]) / 2
    w = float((df["xac_suat_chu_quan"] * df["giua"]).sum())
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    cols = ["#2E7D5B", NAVY, ACCENT]
    for i, r in df.iterrows():
        yy = len(df) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=cols[i], height=0.5, alpha=0.85)
        ax.text(r["thap"] - 200, yy, vn(r["thap"] / 1e3), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 200, yy, vn(r["cao"] / 1e3), ha="left", va="center", fontsize=7.5)
    ax.set_yticks(range(len(df)), [f"{k} · {int(p*100)}%" for k, p in zip(df["kich_ban"][::-1], df["xac_suat_chu_quan"][::-1])], fontsize=8)
    ax.axvline(CLOSE_2910, color=NAVY, ls="--", lw=1.1, label="Đóng cửa 29/10: 14,7k (mốc)")
    ax.axvline(PX_3010, color="#555", ls=":", lw=1.1, label="30/10 10:08 (DNSE, chưa đóng cửa): 14,5k")
    ax.axvline(w, color="#999", ls="-", lw=1.0, label=f"Bình quân theo xác suất ~{vn(w/1e3)}k (ước lượng)")
    ax.legend(fontsize=6.8, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(4000, 18500); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_xlabel("đồng/cổ phiếu")
    ax.set_title("Giá hiện tại nằm trong kịch bản tích cực, trên kịch bản cơ sở")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    df["binh_quan_xac_suat"] = w
    save(fig, "fig_21_scenarios",
         "Nguồn: mô hình định giá vòng 4 (POST-HOC, ước lượng) và số của người phản biện (dải hoãn tái canh). Xác suất là nhận định chủ quan "
         "của nhóm, không phải đầu ra mô hình. Giá: DNSE (đóng cửa 29/10; khớp 10:08:44 ngày 30/10).", df)
    plt.close(fig)
    print(f"scenario weighted mid = {w:.0f}")


# ------------------------------------------------------------------ PDF
CSS = """
@font-face {font-family: dv; src: url(BeVietnamPro-Regular.ttf);}
@font-face {font-family: dv; src: url(BeVietnamPro-Bold.ttf); font-weight: bold;}
* {font-family: dv;}
body {margin: 0; padding: 0; font-size: 8.6pt; line-height: 1.38; color: #1d2731;}
h1 {font-size: 15pt; color: #1F3A5F; margin: 0 0 4pt 0;}
h2 {font-size: 11.5pt; color: #1F3A5F; margin: 12pt 0 4pt 0;}
h3 {font-size: 9.6pt; color: #1F3A5F; margin: 8pt 0 3pt 0;}
p {margin: 3pt 0;}
table {border-collapse: collapse; width: 100%; margin: 4pt 0 6pt 0;}
th {background-color: #1F3A5F; color: #ffffff; font-size: 7.6pt; padding: 2pt 3pt; text-align: left;}
td {font-size: 7.6pt; padding: 2pt 3pt; border-bottom: 1px solid #D9DEE4;}
li {margin: 1pt 0;}
img {width: 100%;}
"""


IMG_W = 470
BANNER_W = 511   # = bề rộng vùng nội dung A4 (595 − 2×42)
BREAK_BEFORE = ("3.",)


def md_to_html(md):
    import html as H
    import re
    def inl(s):
        s = H.escape(s, quote=False)
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    out, lines, i, lst = [], md.split("\n"), 0, None
    def close():
        nonlocal lst
        if lst:
            out.append(f"</{lst}>"); lst = None
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            close(); i += 1; continue
        m = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", s)
        if m:
            from PIL import Image
            with Image.open(os.path.join(HERE, m.group(2))) as im:
                hh = int(IMG_W * im.height / im.width)
            close(); out.append(f'<IMG {m.group(2)} {hh}/>'); i += 1; continue
        if s.startswith("<!--"):   # ghi chú nội bộ của file (gợi ý tiêu đề email) — không in
            close(); i += 1; continue
        if re.fullmatch(r"-{3,}", s):
            close(); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            close(); lv = len(m.group(1))
            if lv == 2 and m.group(2).startswith(BREAK_BEFORE):
                out.append("<PAGEBREAK/>")
            out.append(f"<h{lv}>{inl(m.group(2))}</h{lv}>"); i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and re.fullmatch(r"\|[\s:|-]+\|", lines[i + 1].strip()):
            close()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            hdr, body = rows[0], rows[2:]
            t = "<table><tr>" + "".join(f"<th>{inl(c)}</th>" for c in hdr) + "</tr>"
            for k, r in enumerate(body):
                bg = ' style="background-color:#F3F5F7"' if k % 2 else ""
                t += f"<tr{bg}>" + "".join(f"<td>{inl(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</table>"); continue
        m = re.match(r"^[-*]\s+(.*)$", s) or re.match(r"^\d+\.\s+(.*)$", s)
        if m:
            tag = "ol" if re.match(r"^\d+\.", s) else "ul"
            if lst != tag:
                close(); out.append(f"<{tag}>"); lst = tag
            item = [m.group(1)]; i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^([-*]\s|\d+\.\s|#|\||!\[)", lines[i].strip()):
                item.append(lines[i].strip()); i += 1
            out.append(f"<li>{inl(' '.join(item))}</li>"); continue
        close()
        para = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^([-*]\s|\d+\.\s|#|\||!\[|<!--)", lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        out.append(f"<p>{inl(' '.join(para))}</p>")
    close()
    return "\n".join(out)


def pdf(md_path, pdf_path):
    sys.path.insert(0, "/tmp/pdflib")
    import pymupdf
    import shutil
    md = open(md_path, encoding="utf-8").read()
    body = md_to_html(md)
    # luật 13: banner tiêu đề (ảnh, font Be Vietnam Pro + logo) thay h1 ở đầu trang 1, full-width vùng nội dung
    import re as _re
    from PIL import Image
    with Image.open(os.path.join(HERE, "figs/title_banner.png")) as im:
        bh = int(BANNER_W * im.height / im.width)
    body = _re.sub(r"<h1>.*?</h1>", f"<IMG figs/title_banner.png {bh} {BANNER_W}/>", body, count=1)
    chunks = body.split("<PAGEBREAK/>")
    for f in (FONT, FONT_B):
        shutil.copy(f, os.path.join(HERE, os.path.basename(f)))
    arch = pymupdf.Archive(HERE)
    A4 = pymupdf.paper_rect("a4")
    where = A4 + (42, 54, -42, -50)
    tmp = pdf_path + ".tmp"
    writer = pymupdf.DocumentWriter(tmp)
    import re
    state = {"dev": None, "y": where.y0}
    first_img = [True]

    def new_page():
        if state["dev"] is not None:
            writer.end_page()
        state["dev"] = writer.begin_page(A4); state["y"] = where.y0

    def place_html(h, keep=False):
        mk = lambda: pymupdf.Story(html=f"<body>{h}</body>", user_css=CSS, archive=arch)
        story = mk()
        more = 1
        while more:
            if state["dev"] is None or where.y1 - state["y"] < 30:
                new_page()
            r = pymupdf.Rect(where.x0, state["y"], where.x1, where.y1)
            more, filled = story.place(r)
            if more and keep and state["y"] > where.y0 + 1:
                # bảng không được tách trang (Story vẽ lặp nền hàng bảng sang trang sau) -> sang trang mới
                new_page(); story = mk(); more = 1; continue
            story.draw(state["dev"])
            if more:
                new_page()
            else:
                state["y"] = pymupdf.Rect(filled).y1 + 1

    for ci, ch in enumerate(chunks):
        if ci:
            new_page()
        for part in re.split(r"(<IMG [^>]+/>)", ch):
            m = re.fullmatch(r"<IMG (\S+) (\d+)(?: (\d+))?/>", part)
            if m:
                hh, ww = int(m.group(2)), int(m.group(3) or IMG_W)
                room = where.y1 - state["y"] - 12 if state["dev"] is not None else 0
                if room < hh and room >= 0.85 * hh:   # co nhẹ (≤15%) cho vừa trang thay vì để trống nửa trang
                    ww, hh = int(ww * room / hh), int(room)
                elif room < hh:
                    new_page()
                place_html(f'<p><img src="{m.group(1)}" width="{ww}" height="{hh}"/></p>')
                first_img[0] = False
            else:
                raw = [b for b in part.split("\n") if b.strip()]
                blocks, cur = [], None
                for b in raw:   # gộp <ul>/<ol> ... </ul> thành 1 khối
                    if cur is not None:
                        cur += b
                        if b in ("</ul>", "</ol>"):
                            blocks.append(cur); cur = None
                    elif b in ("<ul>", "<ol>"):
                        cur = b
                    else:
                        blocks.append(b)
                k = 0
                while k < len(blocks):   # mỗi khối 1 Story riêng; heading dính khối kế
                    grp = blocks[k]
                    while re.match(r"<h[1-4]>", blocks[k]) and k + 1 < len(blocks):
                        k += 1; grp += blocks[k]
                    long_tbl = "<table" in grp and grp.count("<tr") > 12   # bảng dài (phụ lục) được tách trang
                    if long_tbl and state["dev"] is not None and where.y1 - state["y"] < 90:
                        new_page()   # tránh để mồ côi tiêu đề + hàng đầu bảng ở đáy trang
                    place_html(grp, keep=("<table" in grp and not long_tbl)); k += 1
    writer.end_page()
    writer.close()
    doc = pymupdf.open(tmp)
    n = doc.page_count
    for k, page in enumerate(doc):
        page.insert_font(fontname="dv", fontfile=FONT)
        page.draw_line((42, 40), (A4.width - 42, 40), color=(0.12, 0.23, 0.37), width=0.6)
        page.insert_text((42, 34), "DRI — CTCP Đầu tư Cao su Đắk Lắk · Báo cáo Due Diligence · 30/10/2026 (v3)", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
        page.insert_text((A4.width - 160, 34), "Nhóm nghiên cứu — lưu hành hạn chế", fontname="dv", fontsize=7.5, color=(0.4, 0.4, 0.4))
        page.draw_line((42, A4.height - 36), (A4.width - 42, A4.height - 36), color=(0.75, 0.78, 0.82), width=0.5)
        page.insert_text((42, A4.height - 24), "Thông tin nghiên cứu, không phải lời khuyên đầu tư cá nhân hoá. Xem tuyên bố miễn trừ ở Phụ lục F.", fontname="dv", fontsize=6.8, color=(0.4, 0.4, 0.4))
        page.insert_text((A4.width - 90, A4.height - 24), f"Trang {k + 1}/{n}", fontname="dv", fontsize=7.5, color=(0.2, 0.2, 0.2))
    doc.save(pdf_path, garbage=3, deflate=True)
    doc.close(); os.remove(tmp)
    for f in (FONT, FONT_B):
        os.remove(os.path.join(HERE, os.path.basename(f)))
    print("pages", n)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("figs", "all"):
        figs()
        figs_v2()
        fig_scenarios()
    if mode in ("pdf", "all"):
        pdf(os.path.join(HERE, "DRI_DD_investor_report_20261030_v3.md"), os.path.join(HERE, "DRI_DD_investor_report_20261030_v3.pdf"))
