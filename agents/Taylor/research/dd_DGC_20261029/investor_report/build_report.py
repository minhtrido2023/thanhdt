"""Tái lập biểu đồ + PDF + HTML cho báo cáo DD nhà đầu tư DGC (29/10/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/):
  fin_quarterly_bq.csv     — tav2_bq.ticker_financial (DGC, 2022Q1–2026Q2), kéo 29/10/2026
  price_raw.csv            — tav2_bq.ticker (DGC Close/Price/Volume, 01/10/2025–28/10/2026) + điểm 29/10 (DNSE)
  commodity_weekly_bq.csv  — tav2_bq.commodity_prices (TE daily sulfur, di_ammonium; TB tuần), kéo 29/10/2026
Số định giá lấy nguyên từ ../../dgc_valuation_20261029_r10/ (REPORT.md + out_r10_*.csv, out_r9_margin_pp.csv)
và ERRATA_r10_skeptic_round4.md (ô r4 + lặp vĩnh viễn 26.117 / 26.340 / 26.558).
Số BCTC Q3/2026 (chưa soát xét) lấy từ r6/MIKE_EXTRACT_BCTC_Q3_2026.md. Mỗi hình kèm CSV.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#3E7C59"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- số dùng chung (nguồn: r10 REPORT.md + errata vòng 4; BCTC Q3/2026) ----
SH = 379_779_286
PX_ANCHOR = 32_900       # đóng cửa 28/10/2026 (BQ; = basicPrice DNSE 29/10)
PX_2910 = 33_300         # DNSE latest_trade 29/10/2026 14:45:02 (khớp cuối phiên)
A7, B7 = 32_182, 37_060
R1 = 30_598              # nền R2 + lặp vĩnh viễn 100 tỷ/quý (qua mô hình)
R2_N0, R4_N0 = 36_880, 32_399
R4_PERP = (26_117, 26_340, 26_558)   # errata: ô r4 + lặp vĩnh viễn, 3 cách đo
NETCASH_PRE, NETCASH_POST = 22_040, 19_400
BVPS = 34_425
GRID = {  # (r4 trước thuế, r4 sau lá chắn, R2 trước thuế, R2 sau lá chắn) — out_r10_final_grid.csv
    "0 quý (không trích thêm)": (32399, 32399, 36880, 36880),
    "100 tỷ × 1 quý": (32146, 32197, 36627, 36678),
    "100 tỷ × 4 quý": (31439, 31631, 35920, 36112),
    "200 tỷ × 4 quý": (30478, 30862, 34959, 35343),
    "100 tỷ × 8 quý": (30603, 30962, 35084, 35443),
    "200 tỷ × 8 quý": (28807, 29525, 33288, 34006),
    "100 tỷ/quý vĩnh viễn": (26117, None, 30598, None),
}


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


def vn(v, d=0):
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def qlabel(q):
    return q[4:] + "/" + q[2:4]


def fin_table():
    import pandas as pd
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0"]:
        fin[c] = fin[c] / 1e9
    q3 = {"quarter": "2026Q3", "Revenue_P0": 2469.45, "NP_P0": 478.16, "CF_OA_P0": 996.07, "GPM_P0": None}
    fin = pd.concat([fin, pd.DataFrame([q3])], ignore_index=True)
    fin["src"] = ["BQ"] * (len(fin) - 1) + ["BCTC Q3/26"]
    fin["lab"] = fin["quarter"].map(qlabel)
    return fin


def figs():
    import numpy as np
    import pandas as pd
    from matplotlib.patches import FancyBboxPatch
    plt = setup_mpl()
    fin = fin_table()

    # 0. HERO — ngành + tiềm năng + mức định giá
    fig = plt.figure(figsize=(7.4, 3.5))
    fig.patch.set_facecolor("white")
    axL = fig.add_axes([0.01, 0.12, 0.36, 0.76]); axL.axis("off")
    axM = fig.add_axes([0.43, 0.20, 0.25, 0.62])
    axR = fig.add_axes([0.76, 0.20, 0.22, 0.62])
    fig.text(0.01, 0.95, "Chuỗi phốt pho tích hợp từ quặng apatit tới sản phẩm xuất khẩu", fontsize=9.5, fontweight="bold", color=NAVY)
    chain = [("Quặng apatit", "Lào Cai (khai trường 25\ntạm dừng, giải trình Q3)"),
             ("Phốt pho vàng P4", "40.000 t/năm"),
             ("Axit photphoric", "160.000 t/năm\n+ 30.000 t thực phẩm"),
             ("Phân bón · DCP/MCP", "100.000 · 60.000 t/năm\n+ tẩy rửa 10.000 t")]
    for k, (a, b) in enumerate(chain):
        y = 0.86 - k * 0.245
        axL.add_patch(FancyBboxPatch((0.02, y - 0.17), 0.96, 0.17, boxstyle="round,pad=0.01,rounding_size=0.03",
                                     fc=NAVY if k else GREY, ec="none", transform=axL.transAxes))
        axL.text(0.06, y - 0.06, a, color="white", fontsize=8.2, fontweight="bold", transform=axL.transAxes, va="center")
        axL.text(0.94, y - 0.06, b, color="white", fontsize=6.6, transform=axL.transAxes, va="center", ha="right")
        if k < 3:
            axL.annotate("", (0.5, y - 0.245 + 0.005), (0.5, y - 0.17), xycoords="axes fraction",
                         arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.4))
    axL.text(0.02, -0.06, "~80% doanh thu từ xuất khẩu (website DGC); 6T/26: 84% (BCTC)", fontsize=6.8, color=ACCENT,
             transform=axL.transAxes, fontweight="bold")
    yrs = ["2021", "2022", "2023", "2024", "2025", "9T/26"]
    np_y = [2388, 5568, 3109, 2987, 3025, 1267]
    axM.bar(range(6), np_y, color=[LIGHT, LIGHT, LIGHT, LIGHT, LIGHT, NAVY], width=0.7)
    for i, v in enumerate(np_y):
        axM.text(i, v + 80, vn(v), ha="center", fontsize=6.5)
    axM.set_xticks(range(6), yrs, fontsize=6.6); axM.set_yticks([]); axM.spines["left"].set_visible(False)
    axM.set_title("LNST cổ đông mẹ, tỷ đ:\nqua đỉnh 2022, 2026 chịu sốc chi phí", fontsize=7.8)
    axM.set_ylim(0, 6300)
    # thước định giá
    axR.set_xlim(0, 1); axR.set_ylim(17_000, 40_000); axR.grid(False)
    axR.set_xticks([]); axR.spines["bottom"].set_visible(False)
    axR.bar(0.5, NETCASH_PRE - NETCASH_POST, bottom=NETCASH_POST, width=0.5, color=GREEN, alpha=0.55)
    axR.bar(0.5, R2_N0 - R4_PERP[0], bottom=R4_PERP[0], width=0.5, color=LIGHT)
    axR.bar(0.5, B7 - A7, bottom=A7, width=0.5, color=NAVY, alpha=0.85)
    axR.axhline(PX_ANCHOR, color=ACCENT, lw=1.6)
    axR.text(0.02, PX_ANCHOR + 350, "Giá 32,9k", fontsize=6.8, color=ACCENT, fontweight="bold")
    axR.text(0.78, (A7 + B7) / 2, "A7–B7\n32,2–37,1k", fontsize=6.2, color=NAVY, va="center")
    axR.text(0.78, 27_500, "Mọi tổ hợp\ngiả định\n26,1–36,9k", fontsize=6.2, color="#555", va="center")
    axR.text(0.78, 20_700, "Tiền ròng/cp\n19,4–22,0k", fontsize=6.2, color=GREEN, va="center")
    axR.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); axR.tick_params(labelsize=6.6)
    axR.set_title("Giá nằm TRONG mọi dải:\nkhông có biên an toàn", fontsize=7.8)
    fig.text(0.01, 0.005, "Nguồn: công suất & tỷ trọng XK theo website ducgiangchem.vn (truy cập 29/10/2026); LNST: tav2_bq.ticker_financial + BCTC HN Q3/2026 (chưa soát xét);\n"
             "dải định giá: ước lượng của nhóm nghiên cứu sau 4 vòng phản biện; giá đóng cửa 28/10/2026.", fontsize=5.6, color="#666")
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200)
    pd.DataFrame({"muc": ["LNST " + y for y in yrs] + ["A7", "B7", "thap_nhat", "cao_nhat", "tien_rong_sau", "tien_rong_truoc", "gia_2810"],
                  "gia_tri": np_y + [A7, B7, R4_PERP[0], R2_N0, NETCASH_POST, NETCASH_PRE, PX_ANCHOR]}).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)
    plt.close(fig)

    # 1. Cơ sở theo địa bàn (sơ đồ vĩ độ)
    sites = pd.DataFrame([
        ("Lào Cai (Tằng Loỏng)", 22.33, 104.05, "DGC Lào Cai 100%, PAT 51%:\nP4, H3PO4, phân bón; mỏ apatit", NAVY),
        ("Hà Nội", 21.03, 105.85, "Trụ sở; BĐS, thể thao (con 100%)", GREY),
        ("Hải Phòng (Đình Vũ, An Hải)", 20.85, 106.75, "Kho bãi Đình Vũ 100%;\nẮc quy Tia Sáng 51%", NAVY),
        ("Hưng Yên", 20.65, 106.05, "Chi nhánh", GREY),
        ("Thanh Hoá (Nghi Sơn)", 19.35, 105.75, "Tổ hợp Nghi Sơn GĐ1 ~2.400 tỷ;\nchạy thử Q4/2026 (CBTT 15/10)", ACCENT),
        ("Lâm Đồng (Cư Jút)", 12.45, 107.85, "DGC Đắk Nông 100%", NAVY),
        ("Bình Dương", 11.0, 106.65, "Chi nhánh", GREY)],
        columns=["dia_diem", "lat", "lon", "vai_tro", "c"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    n = len(sites)
    yy = np.arange(n)[::-1]
    ax.plot([0, 0], [yy.min(), yy.max()], color=LIGHT, lw=6, zorder=1, solid_capstyle="round")
    ax.scatter(np.zeros(n), yy, s=110, c=sites["c"], zorder=3)
    for k, r in sites.iterrows():
        ax.text(0.06, yy[k], r["dia_diem"], fontsize=8.2, fontweight="bold", va="center", color=r["c"] if r["c"] != GREY else "#555")
        ax.text(0.62, yy[k], r["vai_tro"].replace("\n", " "), fontsize=7.4, va="center", color="#222")
    ax.text(-0.04, yy.max() + 0.55, "Bắc", fontsize=7, color="#777", ha="center"); ax.text(-0.04, yy.min() - 0.6, "Nam", fontsize=7, color="#777", ha="center")
    ax.set_xlim(-0.1, 2.2); ax.set_ylim(-0.9, n - 0.2); ax.axis("off")
    ax.set_title("Lõi sản xuất ở Lào Cai; tăng trưởng mới đặt ở Nghi Sơn (sắp theo Bắc → Nam)")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_sites", "Nguồn: BCTC HN Q3/2026 thuyết minh 1 (8 công ty con, 3 chi nhánh, tỷ lệ sở hữu); CBTT NQ HĐQT 34 ngày 15/10/2026 (Nghi Sơn). Toạ độ gần đúng, chỉ minh hoạ.",
         sites.drop(columns="c"))
    plt.close(fig)

    # 2. Ngành: lưu huỳnh & DAP
    cm = pd.read_csv(os.path.join(FIGS, "commodity_weekly_bq.csv"), parse_dates=["wk"])
    s = cm[cm.metric_key == "sulfur"]; d = cm[cm.metric_key == "di_ammonium"]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(s["wk"], s["px"], color=ACCENT, lw=1.5, label="Lưu huỳnh nội địa TQ (CNY/t, trục trái)")
    ax.set_ylabel("CNY/t")
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(d["wk"], d["px"], color=NAVY, lw=1.5, label="DAP (USD/t, trục phải)")
    ax2.set_ylabel("USD/t"); ax2.set_ylim(400, 1000)
    ax.axvline(pd.Timestamp("2026-02-28"), color=GREY, ls=":", lw=1)
    ax.text(pd.Timestamp("2026-03-05"), s["px"].max() * 0.97, "28/02/2026: xung đột\nIran, Hormuz gián đoạn", fontsize=6.8, color="#444")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.2, frameon=False, loc="upper left")
    ax.set_title("Giá đầu ra DAP ở vùng cao 10 năm, nhưng chi phí lưu huỳnh tăng nhanh hơn")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_sulfur_dap", "Nguồn: tav2_bq.commodity_prices, Trading Economics daily (sulfur, di_ammonium), trung bình tuần 01/2024–10/2026; kéo 29/10/2026. "
         "Lưu huỳnh TE là giá nội địa TQ, không phải giá nhập của DN Việt Nam (bản đọc ngành độc lập 28/10/2026).", cm)
    plt.close(fig)

    # 3. Doanh thu & LNST quý
    x = np.arange(len(fin))
    is26 = fin["quarter"].str.startswith("2026")
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    w = 0.4
    ax.bar(x - w / 2, fin["Revenue_P0"], w, color=np.where(is26, NAVY, LIGHT), label="Doanh thu thuần")
    ax.bar(x + w / 2, fin["NP_P0"], w, color=np.where(is26, ACCENT, GREY), label="LNST cổ đông mẹ")
    for i in np.where(is26)[0]:
        ax.text(i + w / 2, fin["NP_P0"][i] + 60, vn(fin["NP_P0"][i]), ha="center", fontsize=6.8, color=ACCENT)
    ax.set_xticks(x, fin["lab"], fontsize=6.6, rotation=45); ax.set_ylabel("tỷ đồng / quý")
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.set_title("LNST 2026 thấp nhất nhiều năm: 409 → 380 → 478 tỷ/quý")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_03_rev_np_quarterly", "Nguồn: tav2_bq.ticker_financial (Revenue_P0, NP_P0; 2026Q1 khớp DT thuần BCTC 2.124,6 tỷ) tới Q2/26; Q3/26 từ BCTC HN Q3/2026 (chưa soát xét). Kéo 29/10/2026.",
         fin[["quarter", "Revenue_P0", "NP_P0", "src"]])
    plt.close(fig)

    # 4. Biên gộp 2026 có/không dự phòng
    gm = pd.DataFrame({"quy": ["Q1/26", "Q2/26", "Q3/26"], "bien_bctc": [23.0, 18.9, 20.5], "bien_ex_du_phong": [23.0, 23.0, 24.6],
                       "du_phong_ty": [0, 100, 100]})
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    xi = np.arange(3)
    ax.bar(xi - 0.18, gm["bien_bctc"], 0.36, color=NAVY, label="Biên gộp theo BCTC")
    ax.bar(xi + 0.18, gm["bien_ex_du_phong"], 0.36, color=LIGHT, label="Nếu bỏ dự phòng môi trường 100 tỷ (suy luận: nằm trong giá vốn)")
    for i in range(3):
        ax.text(i - 0.18, gm["bien_bctc"][i] + 0.4, vn(gm["bien_bctc"][i], 1) + "%", ha="center", fontsize=8, color=NAVY, fontweight="bold")
        ax.text(i + 0.18, gm["bien_ex_du_phong"][i] + 0.4, vn(gm["bien_ex_du_phong"][i], 1) + "%", ha="center", fontsize=8)
    ax.set_xticks(xi, gm["quy"]); ax.set_ylim(0, 30); ax.set_ylabel("%")
    ax.legend(fontsize=7.3, frameon=False, loc="upper left", ncol=1)
    ax.set_title("Dự phòng môi trường 2×100 tỷ kéo biên gộp xuống ~4pp ở Q2 và Q3")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_gross_margin", "Nguồn: BCTC HN Q3/2026 (LN gộp 506,35 / DT 2.469,45); BCTC Q2/2026; dự phòng phải trả ngắn hạn mã 322: 0 → 100 (30/6) → 200 (30/9). "
         "Vị trí khoản dự phòng trong giá vốn là suy luận loại trừ, chưa xác nhận.", gm)
    plt.close(fig)

    # 5. CFO vs LNST
    sub = fin[fin["quarter"] >= "2025Q1"].reset_index(drop=True)
    xs = np.arange(len(sub))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1.35, 1]})
    a1.bar(xs - 0.2, sub["NP_P0"], 0.4, color=LIGHT, label="LNST mẹ")
    a1.bar(xs + 0.2, sub["CF_OA_P0"], 0.4, color=NAVY, label="CFO")
    a1.axhline(0, color="#555", lw=0.8)
    for i, v in enumerate(sub["CF_OA_P0"]):
        a1.text(i + 0.2, v + (40 if v > 0 else -130), vn(v), ha="center", fontsize=6.4)
    a1.set_xticks(xs, sub["lab"], fontsize=7); a1.set_ylabel("tỷ đồng / quý")
    a1.legend(fontsize=7, frameon=False, loc="upper left"); a1.set_title("CFO theo quý dao động rất mạnh", fontsize=8.6)
    br = pd.read_csv(os.path.join(HERE, "..", "..", "dgc_valuation_20261029_r10", "out_r8_cfo_base_rate.csv"))
    a2.bar(br["y"].astype(str), br["r"], color=[ACCENT if v < 0.8 else NAVY for v in br["r"]], width=0.7)
    a2.axhline(1, color="#555", lw=0.8, ls="--")
    a2.set_xticks(range(len(br)), [str(y)[2:] for y in br["y"]], fontsize=6.8)
    a2.set_title("CFO/LNST theo năm (2015–2025)", fontsize=8.6)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_05_cfo", "Nguồn: tav2_bq.ticker_financial CF_OA_P0/NP_P0 (tới Q2/26), BCTC HN Q3/2026 (CFO 9T 755,6 ⇒ Q3 ≈ 996,1); tỷ lệ năm: out_r8_cfo_base_rate.csv (cùng nguồn BQ).",
         sub[["quarter", "NP_P0", "CF_OA_P0"]].merge(br.rename(columns={"y": "quarter"}).astype({"quarter": str}), how="outer"))
    plt.close(fig)

    # 6. Bảng cân đối: tiền + tiền gửi vs vay; tiền ròng/cp
    bs = pd.DataFrame({"moc": ["31/12/2025", "30/06/2026", "30/09/2026"], "tien_va_tien_gui": [13436.7, 10921.5, 9761.2],
                       "vay": [1546.2, 1869.7, 1391.0]})
    bs["tien_rong"] = bs["tien_va_tien_gui"] - bs["vay"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1.1, 1]})
    xi = np.arange(3)
    a1.bar(xi - 0.2, bs["tien_va_tien_gui"], 0.4, color=NAVY, label="Tiền + tiền gửi có kỳ hạn")
    a1.bar(xi + 0.2, bs["vay"], 0.4, color=ACCENT, label="Vay ngắn hạn")
    for i in range(3):
        a1.text(i - 0.2, bs["tien_va_tien_gui"][i] + 150, vn(bs["tien_va_tien_gui"][i]), ha="center", fontsize=6.6)
        a1.text(i + 0.2, bs["vay"][i] + 150, vn(bs["vay"][i]), ha="center", fontsize=6.6)
    a1.set_xticks(xi, bs["moc"], fontsize=7); a1.set_ylabel("tỷ đồng"); a1.set_ylim(0, 15500)
    a1.legend(fontsize=6.8, frameon=False, loc="upper right"); a1.set_title("Tiền ròng 8.370 tỷ sau chi cổ tức 4.213 tỷ", fontsize=8.4)
    lv = [("Tiền ròng/cp\n(trước haircut)", NETCASH_PRE, GREEN), ("Sau PAT + haircut 9%\n(ước lượng)", NETCASH_POST, GREEN),
          ("Giá 28/10", PX_ANCHOR, ACCENT), ("BVPS mẹ 30/9", BVPS, NAVY)]
    a2.barh(range(4), [v for _, v, _ in lv], color=[c for _, _, c in lv], height=0.6)
    for i, (_, v, _) in enumerate(lv):
        a2.text(v + 400, i, vn(v), va="center", fontsize=7.2)
    a2.set_yticks(range(4), [s for s, _, _ in lv], fontsize=6.8); a2.invert_yaxis(); a2.set_xlim(0, 42000)
    a2.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); a2.set_title("P/B ≈ 0,96; tiền ròng ≈ 59–67% giá", fontsize=8.4)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_06_balance_sheet", "Nguồn: BCTC HN Q3/2026 (tiền 230,2 + HTM 9.531,0; vay 1.391,0; VCSH mẹ 13.073,9; 379,78 tr CP), BCTC soát xét H1/2026, BCTC 2025. "
         "Haircut 9% và trừ phần CĐKKS PAT 274 tỷ là ước lượng của nhóm.", bs)
    plt.close(fig)

    # 7. Giá 12 tháng + sự kiện
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-10-29"].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    ev = [("2026-03-17", "17/03 khởi tố vụ án"), ("2026-05-26", "26/05 hạn chế GD"), ("2026-07-23", "23/07 khởi tố thêm"),
          ("2026-08-26", "26/08 soát xét H1\nngoại trừ"), ("2026-10-06", "06/10 cắt margin"), ("2026-10-28", "28/10 BCTC Q3")]
    ymax = px["Close"].max()
    for k, (dd, s_) in enumerate(ev):
        t = pd.Timestamp(dd)
        a1.axvline(t, color=GREY, lw=0.8, ls=":")
        a1.text(t, ymax * (1.0 - 0.09 * k), " " + s_ + " ", fontsize=6.4, color="#444", ha="left" if k < 3 else "right", va="top")
    a1.set_ylabel("đ/cp (điều chỉnh)")
    a2.bar(px["time"], px["Volume"] / 1e3, color=GREY, width=1.0)
    a2.set_ylabel("KL, nghìn cp")
    a1.set_title(f"Giá điều chỉnh giảm từ ~{vn(px['Close'].iloc[0]/1e3,1)}k xuống {vn(PX_ANCHOR/1e3,1)}k (28/10); 29/10 đóng cửa {vn(PX_2910/1e3,1)}k")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_price_12m", "Nguồn: tav2_bq.ticker (Close điều chỉnh cổ tức, Volume) 29/10/2025–28/10/2026; 29/10 từ DNSE latest_trade 14:45:02 ICT. Ngày sự kiện: báo chí/CBTT (Phụ lục C). "
         "Đường dọc chỉ đánh dấu thời điểm, không hàm ý nhân quả.", px[["time", "Close", "Price", "Volume"]])
    plt.close(fig)
    lo, hi = px["Close"].min(), px["Close"].max()

    # 8. Football field (đối xứng)
    rows = [
        ("Nền biên thấp: lặp vĩnh viễn → không trích thêm", R4_PERP[0], R4_N0),
        ("Nền biên cao: lặp vĩnh viễn → không trích thêm", R1, R2_N0),
        ("Mô hình A7 → B7 (B7: khai trường mở lại)", A7, B7),
        ("Biên gộp 2027-28 ±2pp quanh A7", 29_345, 35_017),
        ("Nền biên thấp + nghĩa vụ vụ án 200–1.000 tỷ", 29_766, 31_872),
        ("Tiền ròng/cp (tài sản, không phải giá trị)", NETCASH_POST, NETCASH_PRE)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao"])
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        col = GREEN if i == 5 else NAVY
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=col, height=0.5, alpha=0.85)
        ax.text(r["thap"] - 400, yy, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.2)
        ax.text(r["cao"] + 400, yy, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.2)
    ax.axvline(PX_ANCHOR, color=ACCENT, ls="--", lw=1.2, label="Đóng cửa 28/10: 32.900")
    ax.axvline(PX_2910, color="#555", ls=":", lw=1.1, label="Đóng cửa 29/10: 33.300 (DNSE)")
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(14_000, 46_000); ax.set_xlabel("đồng/cổ phiếu (379,78 triệu CP)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá nằm trong mọi dải; không chọn tổ hợp nào làm cơ sở")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_football_field", "Nguồn: ước lượng của nhóm nghiên cứu (bảng độ nhạy vòng định giá cuối, đã qua 4 vòng phản biện); BCTC HN Q3/2026. Biên thấp = 16,5/17,5%; biên cao = 19,5/20,7% (2027/28). "
         "Thanh = khoảng giữa hai tổ hợp giả định, không phải khoảng tin cậy.", ff)
    plt.close(fig)

    # 9. Lưới độ nhạy (heatmap)
    gl = pd.DataFrame([(k, *v) for k, v in GRID.items()], columns=["so_quy_con_trich", "r4_truoc_thue", "r4_sau_la_chan", "R2_truoc_thue", "R2_sau_la_chan"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    cols = ["r4_truoc_thue", "r4_sau_la_chan", "R2_truoc_thue", "R2_sau_la_chan"]
    M = gl[cols].to_numpy(dtype=float)
    im = ax.imshow(np.nan_to_num(M, nan=np.nan), cmap="RdBu", vmin=24_000, vmax=42_000, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if v == v:
                c = "white" if abs(v - 33_000) > 6000 else "#111"
                ax.text(j, i, vn(v), ha="center", va="center", fontsize=8, color=c,
                        fontweight="bold" if v < PX_ANCHOR else "normal")
            else:
                ax.text(j, i, "26.340–26.558\n(cách đo khác)" if j == 1 else "—", ha="center", va="center", fontsize=6.4, color="#333")
    ax.set_xticks(range(4), ["Biên thấp\ntrước thuế", "Biên thấp\nsau lá chắn 20%", "Biên cao\ntrước thuế", "Biên cao\nsau lá chắn 20%"], fontsize=7.4)
    ax.set_yticks(range(len(gl)), gl["so_quy_con_trich"], fontsize=7.4); ax.grid(False)
    ax.set_title("Giá trị/cp theo số quý còn trích × nền biên (đậm: dưới giá 32.900)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_09_sensitivity_grid", "Nguồn: bảng độ nhạy của nhóm nghiên cứu (Q4/2026 tách khỏi dự phòng). Biên thấp 16,5/17,5%, biên cao 19,5/20,7% (2027/28). Hàng vĩnh viễn: biên cao 30.598 (qua mô hình); biên thấp 26.117 (= 32.399 − 6.282; người phản biện đo 3 cách 26.117–26.558). "
         "Lá chắn thuế 20% là giả định; thuế suất ưu đãi trong mô hình 13%.", gl)
    plt.close(fig)

    # 10. Quy mô tác động của 100 tỷ theo cách đọc
    sc = pd.DataFrame({"cach_doc": ["Trừ một lần", "1 quý", "4 quý", "8 quý", "Lặp vĩnh viễn\n(qua mô hình)", "Lặp vĩnh viễn\n(thô, trước thuế)"],
                       "dong_cp": [263, 253, 960, 1796, 6065, 7406]})
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(range(6), sc["dong_cp"], color=[NAVY] * 4 + [ACCENT, ACCENT], width=0.6)
    for i, v in enumerate(sc["dong_cp"]):
        ax.text(i, v + 120, vn(v), ha="center", fontsize=8)
    ax.set_xticks(range(6), sc["cach_doc"], fontsize=7.3); ax.set_ylabel("đ/cp (giá trị hiện tại)")
    ax.set_title("Cùng 100 tỷ/quý, câu hỏi 'một lần hay lặp' đổi giá trị từ ~0,3k đến ~6–7k/cp")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_10_provision_scale", "Nguồn: bảng độ nhạy của nhóm nghiên cứu; chi phí vốn chủ 14,9%. Hàng 'qua mô hình' và 'thô' khác cơ sở thuế — không so tỷ lệ trực tiếp.", sc)
    plt.close(fig)

    # 11. Ma trận rủi ro
    rk = pd.DataFrame([
        ("R1", "Dự phòng môi trường lặp/tăng", 3, 5), ("R2", "Pháp lý: pháp nhân/đình chỉ", 2, 5),
        ("R3", "Biên gộp 2027-28 thấp", 3, 4), ("R4", "Khai trường chưa mở lại", 3, 3),
        ("R5", "Kiểm toán 2026 ngoại trừ", 4, 2), ("R6", "Nghi Sơn chậm/kém hiệu quả", 3, 2),
        ("R7", "Giá DAP/P4 điều chỉnh", 3, 3)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i in range(1, 6):
        for j in range(1, 6):
            s_ = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s_ >= 12 else ("#F3F5F7" if s_ < 6 else "#FBF1EC"), lw=0))
    offs = {"R4": (-0.25, 0.2), "R7": (-0.25, -0.2), "R6": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Dự phòng lặp và pháp lý: tác động lớn nhất")
    fig.tight_layout(rect=(0, 0.08, 0.70, 1))
    save(fig, "fig_11_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan); tác động tham chiếu bảng độ nhạy mục 7.", rk)
    plt.close(fig)

    # 12. Dòng thời gian pháp lý + mốc kiểm chứng
    tl = pd.DataFrame([
        ("2026-03-17", "Khởi tố vụ án (Đ.221, 227, 235), 14 bị can", "qua"),
        ("2026-05-26", "HOSE hạn chế giao dịch (1 nguồn: chậm nộp BCTC KT 2025)", "qua"),
        ("2026-07-23", "Khởi tố thêm TGĐ, PTGĐ (cá nhân)", "qua"),
        ("2026-08-13", "ĐHĐCĐ: nêu trích dự phòng 100 tỷ (diễn ý báo)", "qua"),
        ("2026-08-26", "Soát xét H1: ngoại trừ do vụ việc đang điều tra", "qua"),
        ("2026-10-28", "BCTC Q3 (chưa soát xét): dự phòng lên 200 tỷ", "qua"),
        ("2026-12-15", "Q4/2026|Nghi Sơn GĐ1 chạy thử (theo CBTT)", "toi"),
        ("2027-01-30", "~01/2027|BCTC Q4/2026: có trích thêm dự phòng?", "toi"),
        ("2027-03-31", "31/03/27|Hạn BCTC kiểm toán 2026: ý kiến kiểm toán", "toi")], columns=["ngay", "su_kien", "loai"])
    tl["d"] = pd.to_datetime(tl["ngay"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.axhline(0, color="#555", lw=1)
    for k, r in tl.iterrows():
        up = 1 if k % 2 == 0 else -1
        h = up * (0.55 + 0.35 * ((k // 2) % 2))
        c = NAVY if r["loai"] == "qua" else ACCENT
        ax.plot([r["d"], r["d"]], [0, h], color=c, lw=0.8); ax.plot(r["d"], 0, "o", color=c, ms=5)
        import textwrap
        ax.text(r["d"].to_pydatetime(), h + 0.05 * up, (r["su_kien"].split("|")[0] if "|" in r["su_kien"] else r["d"].strftime("%d/%m/%y")) + "\n" + "\n".join(textwrap.wrap(r["su_kien"].split("|")[-1], 26)), fontsize=5.9, ha="center",
                va="bottom" if up > 0 else "top", color=c)
    ax.axvline(pd.Timestamp("2026-10-29"), color=GREY, ls=":", lw=1); ax.text(pd.Timestamp("2026-10-31"), 1.25, "hôm nay", fontsize=6.5, color="#555")
    ax.set_ylim(-1.6, 1.6); ax.set_yticks([]); ax.grid(False); ax.spines["left"].set_visible(False)
    ax.set_xlim(pd.Timestamp("2026-02-01"), pd.Timestamp("2027-05-15"))
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y")); ax.tick_params(axis="x", labelsize=7.5)
    ax.set_title("Pháp lý và mốc kiểm chứng: xanh đậm = đã xảy ra, cam = sắp tới (dự kiến)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_12_timeline", "Nguồn: bocongan.gov.vn/nhandan.vn 17/03; tuoitre.vn 23/07; doanhnhan.baophapluat.vn 15/08; VietnamFinance 06/10; BCTC soát xét H1 (UHY 26/08); BCTC Q3; CBTT 15/10. Mốc tương lai là dự kiến.",
         tl.drop(columns="d"))
    plt.close(fig)
    print("12m Close lo/hi", lo, hi)


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
BREAK_BEFORE = ("1.", "3.", "4.", "5.", "9.", "Phụ lục A", "Phụ lục C", "Phụ lục E")


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
        page.insert_text((42, 34), "DGC — CTCP Tập đoàn Hóa chất Đức Giang · Báo cáo Due Diligence · 29/10/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
        page.insert_text((A4.width - 175, 34), "Nhóm nghiên cứu — lưu hành hạn chế", fontname="dv", fontsize=7.5, color=(0.4, 0.4, 0.4))
        page.draw_line((42, A4.height - 36), (A4.width - 42, A4.height - 36), color=(0.75, 0.78, 0.82), width=0.5)
        page.insert_text((42, A4.height - 24), "Thông tin nghiên cứu, không phải lời khuyên đầu tư cá nhân hoá. Xem tuyên bố miễn trừ ở Phụ lục F.", fontname="dv", fontsize=6.8, color=(0.4, 0.4, 0.4))
        page.insert_text((A4.width - 90, A4.height - 24), f"Trang {k + 1}/{n}", fontname="dv", fontsize=7.5, color=(0.2, 0.2, 0.2))
    doc.save(pdf_path, garbage=3, deflate=True)
    doc.close(); os.remove(tmp)
    for f in (FONT, FONT_B):
        os.remove(os.path.join(HERE, os.path.basename(f)))
    print("pages", n)


def html(md_path, html_path):
    body = md_to_html(open(md_path, encoding="utf-8").read()).replace("<PAGEBREAK/>", "")
    import re
    body = re.sub(r"<IMG (\S+) (\d+)/>", r'<p><img src="\1" style="max-width:100%"/></p>', body)
    css = "body{font-family:DejaVu Sans,Arial,sans-serif;max-width:860px;margin:24px auto;font-size:14px;line-height:1.5;color:#1d2731}" \
          "h1{color:#1F3A5F}h2,h3{color:#1F3A5F}table{border-collapse:collapse;width:100%;margin:6px 0}" \
          "th{background:#1F3A5F;color:#fff;padding:3px 5px;text-align:left;font-size:12px}td{border-bottom:1px solid #D9DEE4;padding:3px 5px;font-size:12px}"
    open(html_path, "w", encoding="utf-8").write(f"<!doctype html><html lang=vi><head><meta charset=utf-8><title>DGC DD 29/10/2026</title><style>{css}</style></head><body>{body}</body></html>")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    base = os.path.join(HERE, "DGC_DD_investor_report_20261029")
    if mode in ("figs", "all"):
        figs()
    if mode in ("pdf", "all"):
        pdf(base + ".md", base + ".pdf")
        html(base + ".md", base + ".html")
