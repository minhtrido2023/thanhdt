"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư QTP (17/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/):
  fin_quarterly_bq.csv  — tav2_bq.ticker_financial (QTP, 2022Q1–2026Q3), kéo 17/11/2026
  price_raw.csv         — tav2_bq.ticker (QTP Close/Price/Volume, 03/11/2025–16/11/2026)
  fig_map_points.csv    — toạ độ bản đồ (OSM/Wikipedia), dùng bởi make_map.py
Ảnh: src/web_banner1.jpg (website công ty tpcquangninh.com.vn), src/logo.png (website công ty).
Số BCTC/định giá: REPORT.md (DD đã phản biện) + model/qtp_model_out.txt. Mỗi hình ghi kèm CSV (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"  # luật 13
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung (nguồn: REPORT.md §0–§9 + model/qtp_model_out.txt) ----
PX = 10_300                      # đóng cửa 16/11/2026 = DNSE latest_trade 17/11 11:24:15 (giá tham chiếu 10.300)
SCEN = {"Xấu": (11_546, 0.25), "Cơ sở": (15_200, 0.65), "Tốt": (18_324, 0.10)}
FV_PRE, FV_POST = 14_599, 13_139
LIQ = 0.10
ZONE = (10_390, 16_490)
LIFE = {"2030": 11_507, "2035": 12_437, "2040": 12_847, "2047": 13_139}     # trọng số chọn, sau CK
WEIGHTS_POST = (12_035, 13_561)  # bộ 0,5/0,5/0 … 0,25/0,5/0,25
RATE_PRE = {-100: 15_151, -50: 14_868, 50: 14_343, 100: 14_101}
EPS_N, EPS_OP, NETCASH_PS, BVPS = 1_257, 1_120, 3_425, 13_299
# Lợi nhuận gộp quý theo BCTC gốc (tỷ đồng). Q2 = 6T/9T trừ các quý (suy ra); Q4/25 gồm DT chênh lệch tỷ giá 663 tỷ.
GP_BCTC = {"2024Q4": 214.2, "2025Q1": 239.7, "2025Q2": 267.1, "2025Q3": 64.2, "2025Q4": 954.8,
           "2026Q1": 252.4, "2026Q2": 418.9, "2026Q3": 93.1}
FX_ONEOFF_GP, FX_ONEOFF_NP = 663.0, 473.4
# Tiền gửi giữ đến đáo hạn ngắn hạn (mã 123, BCĐKT các kỳ, tỷ đồng)
HTM = {"2024Q4": 520.0, "2025Q3": 1_030.0, "2025Q4": 1_460.0, "2026Q1": 1_025.0, "2026Q2": 1_220.0, "2026Q3": 1_774.1}
EBITDA_DEBT = [  # REPORT §6 (BQ ticker_financial, Q4 mỗi năm; nghìn tỷ)
    ("2017", 3.36, 9.56), ("2018", 3.09, 7.53), ("2019", 3.11, 5.58), ("2020", 2.88, 3.75), ("2021", 1.94, 2.15),
    ("2022", 1.93, 1.09), ("2023", 1.59, 0.32), ("2024", 1.28, 0.19), ("2025*", 1.27, 0.0), ("TTM Q3/26*", 1.39, 0.0)]


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "Be Vietnam Pro", "font.size": 9, "axes.titlesize": 9.8,
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


def vn(v, d=0):
    s = f"{v:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0", "CF_Invest_P0", "Cash_P0", "AR_P0", "EBITDA_P0"]:
        fin[c] = fin[c] / 1e9
    fin["lab"] = fin["quarter"].map(qlabel)
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-11-17"].reset_index(drop=True)
    lo12, hi12 = float(px["Close"].min()), float(px["Close"].max())

    # 0. Hero: ảnh nhà máy (website công ty) + thanh định giá
    from PIL import Image
    im = Image.open(os.path.join(SRC, "web_banner1.jpg")).convert("RGB")
    w, h = im.size
    im = im.crop((int(w * 0.18), 0, int(w * 0.78), h))
    fig = plt.figure(figsize=(7.2, 3.7))
    a0 = fig.add_axes([0.0, 0.50, 1.0, 0.50]); a0.imshow(im, aspect="auto"); a0.axis("off")
    a0.text(0.012, 0.93, "Nhà máy Nhiệt điện Quảng Ninh · 4 tổ máy · 1.200 MW", transform=a0.transAxes, fontsize=10.5,
            color="white", fontweight="bold", va="top", bbox=dict(facecolor=NAVY, alpha=0.82, lw=0, pad=4))
    a0.text(0.988, 0.04, "Ảnh: website công ty", transform=a0.transAxes, fontsize=6.5, color="white", ha="right",
            bbox=dict(facecolor="black", alpha=0.35, lw=0, pad=1.5))
    a1 = fig.add_axes([0.06, 0.20, 0.90, 0.13]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xlim(7_000, 19_500); a1.set_ylim(0, 1)
    a1.barh(0.5, ZONE[1] - ZONE[0], left=ZONE[0], height=0.55, color=LIGHT)
    a1.plot([FV_POST] * 2, [0.18, 0.82], color=NAVY, lw=2.4)
    a1.plot([PX] * 2, [0.05, 0.95], color=ACCENT, lw=2.4)
    a1.text(FV_POST, 1.05, f"Tâm giá trị {vn(FV_POST/1e3,2)}k (sau chiết khấu thanh khoản)", ha="center", fontsize=7.6, color=NAVY, fontweight="bold")
    a1.text(PX - 120, 1.05, f"Giá {vn(PX/1e3,1)}k", ha="right", fontsize=7.6, color=ACCENT, fontweight="bold")
    a1.text(ZONE[0], -0.55, vn(ZONE[0]) + " (xấu)", ha="center", fontsize=7.2, color="#444")
    a1.text(ZONE[1], -0.55, vn(ZONE[1]) + " (tốt)", ha="center", fontsize=7.2, color="#444")
    a1.text(ZONE[1] + 250, 0.5, "vùng giá trị\nhợp lý", ha="left", va="center", fontsize=7.0, color="#666")
    a1.set_xticks([])
    fig.text(0.06, 0.43, "Vay 0 · tiền ròng 3.425 đ/cp · LNST chuẩn hoá 565 tỷ (EPS 1.257) · giá ≈ P/E 8,2 lần lợi nhuận chuẩn hoá",
             fontsize=7.8, color="#222")
    save(fig, "fig_00_hero", "Nguồn: ảnh nhà máy từ website công ty (tpcquangninh.com.vn); giá DNSE 17/11/2026 11:24 (= đóng cửa 16/11); giá trị: mô hình DCF của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia", "tam_sau_CK", "vung_thap", "vung_cao"], "dcp": [PX, FV_POST, ZONE[0], ZONE[1]]}))
    plt.close(fig)

    # 1. Doanh thu quý & biên gộp quý (BCTC)
    sub = fin[fin["quarter"] >= "2023Q1"].reset_index(drop=True)
    x = np.arange(len(sub))
    isq3 = sub["quarter"].str.endswith("Q3")
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.bar(x, sub["Revenue_P0"], color=np.where(isq3, GREY, NAVY), width=0.68)
    ax.set_ylabel("Doanh thu thuần quý, tỷ đồng"); ax.set_ylim(0, 5200)
    ax.set_xticks(x, sub["lab"], fontsize=7.4)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    gq = [q for q in sub["quarter"] if q in GP_BCTC]
    gx = [int(np.where(sub["quarter"] == q)[0][0]) for q in gq]
    rev = sub.set_index("quarter")["Revenue_P0"]
    gpm = [GP_BCTC[q] / rev[q] * 100 for q in gq]
    gpm_x = [(GP_BCTC[q] - (FX_ONEOFF_GP if q == "2025Q4" else 0)) / rev[q] * 100 for q in gq]
    ax2.plot(gx, gpm_x, color=ACCENT, marker="o", lw=1.6, label="Biên gộp quý (Q4/25 đã loại DT tỷ giá 663 tỷ)")
    i4 = gq.index("2025Q4")
    ax2.plot(gx[i4], gpm[i4], marker="o", mfc="white", color=ACCENT, ms=7, ls="none", label="Q4/25 báo cáo (gồm khoản tỷ giá)")
    for xx, v in zip(gx, gpm_x):
        ax2.annotate(vn(v, 1) + "%", (xx, v), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=7, color=ACCENT,
                     bbox=dict(facecolor="white", alpha=0.8, lw=0, pad=0.6))
    ax2.annotate(vn(gpm[i4], 1) + "%", (gx[i4], gpm[i4]), xytext=(-4, 0), textcoords="offset points", ha="right", va="center", fontsize=7, color=ACCENT)
    ax2.set_ylim(0, 36); ax2.set_ylabel("Biên gộp quý, %")
    ax2.legend(loc="upper left", fontsize=7.2, frameon=False)
    ax.set_title("Doanh thu 2026 lên nền mới; quý 3 (xám) luôn là đáy biên vì mùa mưa")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_revenue_margin",
         "Nguồn: doanh thu thuần tav2_bq.ticker_financial (khớp BCTC Q3/25, Q3/26); lợi nhuận gộp quý: BCTC gốc Q4/25, Q1/26, Q3/25, Q3/26; Q2 = lũy kế 6T/9T trừ các quý. Biên Q4/25 loại 663 tỷ là ước lượng (giả định toàn bộ khoản tỷ giá nằm trong lợi nhuận gộp).",
         pd.DataFrame({"quarter": gq, "revenue": [rev[q] for q in gq], "gross_profit": [GP_BCTC[q] for q in gq],
                       "gpm_reported": gpm, "gpm_ex_fx": gpm_x}))
    plt.close(fig)

    # 2. LNST quý: mùa vụ Q3 + khoản một lần Q4/25
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    npq = sub["NP_P0"].copy()
    core = npq.copy(); one = np.zeros(len(sub))
    j = int(np.where(sub["quarter"] == "2025Q4")[0][0])
    core[j] = npq[j] - FX_ONEOFF_NP; one[j] = FX_ONEOFF_NP
    ax.bar(x, core, color=np.where(isq3, GREY, NAVY), width=0.68)
    ax.bar(x, one, bottom=core, color=ACCENT, width=0.68, label="Khoản tỷ giá một lần sau thuế (ước lượng 473 tỷ)")
    for i, v in enumerate(npq):
        ax.text(i, v + 8, vn(v, 0), ha="center", fontsize=7, color="#333")
    ax.set_xticks(x, sub["lab"], fontsize=7.4); ax.set_ylabel("LNST, tỷ đồng"); ax.set_ylim(0, 720)
    ax.legend(fontsize=7.4, frameon=False, loc="upper left")
    ax.set_title("Q3/26 lãi 75,7 tỷ: đáy mùa vụ như mọi năm, nhưng tăng 129% so với Q3/25")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_02_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (khớp BCTC gốc: Q3/26 75,68; 9T26 599,5; FY25 1.035,9 tỷ). Xám = quý 3. Tách khoản tỷ giá Q4/25 là ước lượng của nhóm nghiên cứu.",
         sub[["quarter", "NP_P0"]].assign(fx_oneoff=one))
    plt.close(fig)

    # 4. Chuỗi giá trị (sơ đồ minh hoạ + ảnh)
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(7.2, 2.6))
    ax = fig.add_axes([0, 0.1, 1, 0.9]); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 40)
    boxes = [(1, "Than antraxit TKV\nvùng Hòn Gai – Cẩm Phả\n(+ than nhập pha trộn)", "#6B4E3D"),
             (27, "Nhà máy QTP\n4 tổ máy · 1.200 MW\nHà Khánh, Quảng Ninh", NAVY),
             (53, "EVN / EPTC\nngười mua duy nhất\n(hợp đồng PPA)", GREEN),
             (79, "Phụ tải miền Bắc\nthiếu nguồn 2027\n(Hà Nội, Hải Phòng…)", "#555")]
    for x0, s, c in boxes:
        ax.add_patch(FancyBboxPatch((x0, 17), 20, 19, boxstyle="round,pad=0.6", fc=c, ec="none"))
        ax.text(x0 + 10, 26.5, s, ha="center", va="center", color="white", fontsize=7.8, fontweight="bold", linespacing=1.35)
    for xa in (21.6, 47.6, 73.6):
        ax.annotate("", xy=(xa + 4.6, 26.5), xytext=(xa, 26.5), arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.6))
    notes = [(11, "Giá than: chuyển vào\ngiá biến đổi (pass-through)"),
             (37, "Giá cố định = khấu hao + lãi vay\n+ O&M + lợi nhuận thoả thuận"),
             (63, "Trả tiền ~100 ngày;\nphải thu 3.090 tỷ (30/9/26)"),
             (89, "Huy động than 10T/26\n≈ 49,7% sản lượng hệ thống")]
    for xc, s in notes:
        ax.text(xc, 9.5, s, ha="center", va="center", fontsize=7.0, color="#333", linespacing=1.3)
    save(fig, "fig_04_value_chain", "Sơ đồ minh hoạ của nhóm nghiên cứu. Nguồn: BCTC Q3/26 (1.200 MW, phải thu EPTC); đọc ngành độc lập 17/11/2026 (cơ chế PPA hai thành phần, tỷ trọng than 10T/26 theo BCT/NSMO).",
         pd.DataFrame({"khau": [b[1].replace("\n", " ") for b in boxes], "ghi_chu": [n[1].replace("\n", " ") for n in notes]}))
    plt.close(fig)

    # 5. CFO vs LNST theo năm
    fin["year"] = fin["quarter"].str[:4]
    yr = fin[fin["year"] >= "2023"].groupby("year")[["NP_P0", "CF_OA_P0", "CF_Invest_P0"]].sum().reset_index()
    yr["lab"] = yr["year"].where(yr["year"] != "2026", "9T/2026")
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xi = np.arange(len(yr)); w = 0.36
    ax.bar(xi - w / 2, yr["NP_P0"], w, color=LIGHT, label="LNST")
    ax.bar(xi + w / 2, yr["CF_OA_P0"], w, color=NAVY, label="Dòng tiền kinh doanh (CFO)")
    for i in range(len(yr)):
        ax.text(i - w / 2, yr["NP_P0"][i] + 25, vn(yr["NP_P0"][i]), ha="center", fontsize=7.4)
        ax.text(i + w / 2, yr["CF_OA_P0"][i] + 25, vn(yr["CF_OA_P0"][i]), ha="center", fontsize=7.4, color=NAVY, fontweight="bold")
    ax.set_xticks(xi, yr["lab"]); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 2000)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("CFO vượt LNST mọi năm; capex duy trì chỉ vài tỷ đồng/năm")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_05_cfo_npat", "Nguồn: tav2_bq.ticker_financial (tổng quý; CFO 9T26 707,7 tỷ khớp BCTC LCTT). Capex 9T26 = 5,0 tỷ (BCTC Q3/26). 9T26 CFO thấp do nộp thuế TNDN 291 tỷ của năm 2025.",
         yr[["year", "NP_P0", "CF_OA_P0", "CF_Invest_P0"]])
    plt.close(fig)

    # 6. Tiền + tiền gửi vs phải thu
    fq = fin.set_index("quarter")
    rows = [(qlabel(q).replace("Q4/", "31/12/").replace("Q3/", "30/9/").replace("Q2/", "30/6/").replace("Q1/", "31/3/"),
             fq.loc[q, "Cash_P0"], HTM[q], fq.loc[q, "AR_P0"]) for q in HTM]
    cr = pd.DataFrame(rows, columns=["moc", "tien", "tien_gui_dao_han", "phai_thu_ngan_han"])
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    xi = np.arange(len(cr)); w = 0.38
    ax.bar(xi - w / 2, cr["tien"], w, color=GREY, label="Tiền")
    ax.bar(xi - w / 2, cr["tien_gui_dao_han"], w, bottom=cr["tien"], color=NAVY, label="Tiền gửi giữ đến đáo hạn")
    ax.bar(xi + w / 2, cr["phai_thu_ngan_han"], w, color=ACCENT, alpha=0.85, label="Phải thu ngắn hạn (chủ yếu EVN/EPTC)")
    for i, r in cr.iterrows():
        ax.text(i - w / 2, r["tien"] + r["tien_gui_dao_han"] + 40, vn(r["tien"] + r["tien_gui_dao_han"]), ha="center", fontsize=7.2, color=NAVY, fontweight="bold")
        ax.text(i + w / 2, r["phai_thu_ngan_han"] + 40, vn(r["phai_thu_ngan_han"]), ha="center", fontsize=7.2, color=ACCENT)
    ax.set_xticks(xi, cr["moc"], fontsize=7.6); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 4200)
    ax.legend(fontsize=7.2, frameon=False, loc="upper left", ncol=3)
    ax.set_title("Tiền + tiền gửi 1.856 tỷ (30/9/26), vay bằng 0; phải thu EVN gấp ~1,7 lần")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_06_cash_receivables", "Nguồn: BCĐKT các kỳ (mã 123 tiền gửi giữ đến đáo hạn); tiền và phải thu ngắn hạn: tav2_bq.ticker_financial (khớp BCTC 30/9/26). Tạm ứng cổ tức 315 tỷ trả từ 27/11/2026 chưa trừ trên hình.",
         cr)
    plt.close(fig)

    # 7. EBITDA vs nợ vay (cơ sở trọng số kịch bản)
    ed = pd.DataFrame(EBITDA_DEBT, columns=["nam", "ebitda_nghin_ty", "vay_nghin_ty"])
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xi = np.arange(len(ed))
    ax.bar(xi, ed["vay_nghin_ty"], color=LIGHT, width=0.62, label="Vay cuối năm")
    ax.plot(xi, ed["ebitda_nghin_ty"], color=NAVY, marker="o", lw=1.8, label="EBITDA (2025, TTM: đã loại khoản tỷ giá)")
    for i, v in enumerate(ed["ebitda_nghin_ty"]):
        ax.annotate(vn(v, 2), (i, v), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=7.2, color=NAVY)
    ax.set_xticks(xi, ed["nam"], fontsize=7.4); ax.set_ylabel("nghìn tỷ đồng"); ax.set_ylim(0, 10.5)
    ax.legend(fontsize=7.4, frameon=False, loc="upper right")
    ax.set_title("Khi trả hết nợ, EBITDA giảm 62% (2017–2024): giá cố định đi theo khấu hao + lãi vay")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_ebitda_debt", "Nguồn: tav2_bq.ticker_financial (EBITDA_P0, vay; quý 4 mỗi năm), đo 17/11/2026. (*) EBITDA trừ 663 tỷ doanh thu tỷ giá là ước lượng.", ed)
    plt.close(fig)

    # 8. Football field
    ff = pd.DataFrame([
        ("DCF 3 kịch bản (xấu – tốt)", ZONE[0], ZONE[1], FV_POST),
        ("DCF: vòng đời 2030 – 2047 (trần dưới hiếm)", LIFE["2030"], LIFE["2047"], None),
        ("DCF: các bộ trọng số kịch bản", WEIGHTS_POST[0], WEIGHTS_POST[1], None),
        ("DCF: lãi huy động ±100 điểm cơ bản", RATE_PRE[100] * (1 - LIQ), RATE_PRE[-100] * (1 - LIQ), None),
        ("P/E 7–9 × EPS chuẩn hoá 1.257", 7 * EPS_N, 9 * EPS_N, None),
        ("P/E 7–9 × EPS hoạt động + tiền ròng", 7 * EPS_OP + NETCASH_PS, 9 * EPS_OP + NETCASH_PS, None),
        ("P/B 0,6–0,7 × BVPS 13.299", 0.6 * BVPS, 0.7 * BVPS, None),
        ("Vùng giá 12 tháng (điều chỉnh)", lo12, hi12, None)], columns=["phuong_phap", "thap", "cao", "tam"])
    fig, ax = plt.subplots(figsize=(7.2, 3.7))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        col = NAVY if i < 4 else (GREY if i < 7 else LIGHT)
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=col, height=0.52)
        ax.text(r["thap"] - 150, yy, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(r["cao"] + 150, yy, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.3)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.6)
    ax.axvline(FV_POST, color=NAVY, ls="--", lw=1.1, label="Tâm giá trị 13,14k (sau chiết khấu thanh khoản)")
    ax.axvline(PX, color=ACCENT, ls="-", lw=1.4, label="Giá 10,3k (16–17/11/2026)")
    ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.35, -0.2), ncol=2)
    ax.set_xlim(5_000, 19_000); ax.set_xlabel("đồng/cổ phiếu · DCF: sau chiết khấu thanh khoản 10%; bội số: chưa chiết khấu", fontsize=7.6)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("DCF đặt giá dưới vùng giá trị; bội số cho thấy giá xấp xỉ hợp lý")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_08_football_field", "Nguồn: mô hình DCF vòng đời hữu hạn của nhóm nghiên cứu (ước lượng); P/E peer điện 7–9 (tav2_bq.ticker 16/11/2026); giá 12 tháng tav2_bq.ticker 17/11/2025–16/11/2026.", ff)
    plt.close(fig)

    # 9. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("R1", "Vòng đời ngắn hơn 2047 (đất, môi trường)", 1, 4), ("R2", "Giá cố định PPA giảm sâu hơn khấu hao", 3, 4),
        ("R3", "EVN trả chậm, phải thu kéo dài", 3, 3), ("R4", "ETS 2028 không chuyển vào giá", 3, 3),
        ("R5", "Chi phí khí thải không vào giá", 2, 4), ("R6", "El Niño qua, sản lượng H2/27 giảm", 4, 2),
        ("R7", "Cổ tức giảm 2027–29 (góp vốn dự án)", 3, 2), ("R8", "Than pha trộn lệch thiết kế lò", 2, 3)],
        columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.11, 0.27, 0.42, 0.64])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R3": (-0.22, 0.2), "R4": (-0.22, -0.2), "R7": (0, 0), "R8": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 10 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    fig.text(0.57, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.75)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7.2)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–36 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Giá cố định PPA và hạn thuê đất 2047 quyết định phần lớn giá trị")
    save(fig, "fig_09_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 17/11/2026.", rk)
    plt.close(fig)

    print(f"12m Close lo={lo12:.0f} hi={hi12:.0f}; ADV median 63 phien (ty)=",
          round(float((px.tail(63)["Price"] * px.tail(63)["Volume"]).median() / 1e9), 2))
    print(ff.round(0).to_string())
    print(yr.round(1).to_string())
    print(cr.round(1).to_string())


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
BREAK_BEFORE = ("1.", "4.", "5.", "7.", "8.", "Phụ lục C")


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
        if m and len(m.group(1)) == 1:   # h1 đã nằm trong ảnh banner -> bỏ trong PDF
            i += 1; continue
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
    md = "![](figs/title_banner.png)\n\n" + md   # banner đầu trang 1 PDF; email truyền --banner riêng
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
        page.insert_text((42, 34), "QTP — CTCP Nhiệt điện Quảng Ninh · Báo cáo Due Diligence · 17/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "QTP_DD_investor_report_20261117.md"), os.path.join(HERE, "QTP_DD_investor_report_20261117.pdf"))
