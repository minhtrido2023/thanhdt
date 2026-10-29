"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư DRI (29/10/2026).

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
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- số dùng chung ----
SH = 73_200_000              # CP lưu hành [BCTC3 vốn góp 732 tỷ]
CLOSE_2810 = 14_500          # đóng cửa 28/10/2026 [BQ tav2_bq.ticker]
PX_2910 = 14_700             # DNSE latest_trade 29/10/2026 14:59:46 ICT (lệnh khớp cuối phiên, G1)
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
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 9.8,
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
    px = px[(px["time"] >= "2025-10-29") & (px["time"] <= "2026-10-28")].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.plot(pd.Timestamp("2026-10-29"), PX_2910, "o", color=ACCENT, ms=5)
    a1.annotate("29/10: 14.700 (DNSE)", (pd.Timestamp("2026-10-29"), PX_2910), xytext=(pd.Timestamp("2026-05-01"), 15900),
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
    a1.set_title("Giá +55% từ đáy 11/2025 tới đỉnh 09/10/26; −14% từ đỉnh tới 28/10")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_price_12m",
         "Nguồn: tav2_bq.ticker (Close điều chỉnh cổ tức, Volume) 29/10/2025–28/10/2026; điểm 29/10 DNSE latest_trade 14:59:46 ICT. "
         "Ngày GDKHQ suy từ chênh Close/Price (chưa đối chiếu thông báo VSDC). Mốc sự kiện là quan sát, không gán nhân quả.",
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
    for v, s, c, ls in ((CLOSE_2810, "Đóng cửa 28/10: 14,5k", NAVY, "--"), (PX_2910, "29/10 (DNSE): 14,7k", "#555", ":")):
        ax.axvline(v, color=c, ls=ls, lw=1.1, label=s)
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="lower left")
    ax.set_xlim(0, 22000); ax.set_xlabel("đồng/cổ phiếu (73,2 triệu CP)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá 14,5k chỉ nằm trong dải khi DRI không tái canh")
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
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Giá cao su và tuổi vườn: rủi ro lớn nhất; Lào: xác suất thấp, tác động rất lớn")
    fig.tight_layout(rect=(0, 0.08, 0.68, 1))
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu bản đọc ngành độc lập 27/10/2026.", rk)
    plt.close(fig)

    print(f"BVPS={bvps:.0f} PB28={CLOSE_2810/bvps:.2f} PB29={PX_2910/bvps:.2f}; EPS_TTM={NP_TTM*1e9/SH:.0f} PE28={CLOSE_2810/(NP_TTM*1e9/SH):.2f} PE29={PX_2910/(NP_TTM*1e9/SH):.2f}")
    print(f"12m Close lo={lo12:.0f} hi={hi12:.0f}")
    print(ff.round(0).to_string())


# ------------------------------------------------------------------ PDF
CSS = """
@font-face {font-family: dv; src: url(DejaVuSans.ttf);}
@font-face {font-family: dv; src: url(DejaVuSans-Bold.ttf); font-weight: bold;}
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
BREAK_BEFORE = ("1.", "5.", "7.", "8.", "Phụ lục A")


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
            m = re.fullmatch(r"<IMG (\S+) (\d+)/>", part)
            if m:
                hh, ww = int(m.group(2)), IMG_W
                room = where.y1 - state["y"] - 12 if state["dev"] is not None else 0
                if room < hh and room >= (0.40 if first_img[0] else 0.75) * hh:   # co nhẹ cho vừa trang thay vì để trống nửa trang
                    ww, hh = int(IMG_W * room / hh), int(room)
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
                    place_html(grp, keep="<table" in grp); k += 1
    writer.end_page()
    writer.close()
    doc = pymupdf.open(tmp)
    n = doc.page_count
    for k, page in enumerate(doc):
        page.insert_font(fontname="dv", fontfile=FONT)
        page.draw_line((42, 40), (A4.width - 42, 40), color=(0.12, 0.23, 0.37), width=0.6)
        page.insert_text((42, 34), "DRI — CTCP Đầu tư Cao su Đắk Lắk · Báo cáo Due Diligence · 29/10/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
    if mode in ("pdf", "all"):
        pdf(os.path.join(HERE, "DRI_DD_investor_report_20261029.md"), os.path.join(HERE, "DRI_DD_investor_report_20261029.pdf"))
