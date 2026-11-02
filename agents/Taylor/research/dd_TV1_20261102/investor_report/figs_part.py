"""Biểu đồ cho báo cáo DD nhà đầu tư TV1 (02/11/2026). Import bởi build_report.py.
Số: ../REPORT.md §0/§8g + ../calc/valuation_out.txt khối "r7" + ../calc/peer_study/ (peer thuỷ điện). Mỗi hình kèm CSV.
Ảnh: ../src/web/ (banner trang chủ pecc1.com.vn, tải 02/11/2026). Giá 12T: scripts/tv1_px_bq.csv (giá điều chỉnh, khớp DNSE 30/10).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
WEB = os.path.join(HERE, "..", "src", "web")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 19_800                      # đóng cửa 30/10/2026 (DNSE)
# số từ ../calc/valuation_out.txt khối "r7" (hiệu chuẩn peer: P/E 6,8/7,42/8,0; Ke 11,1/10,4/9,5%)
FAIR = (18_200, 22_000)          # vùng = [min(P/E 6,8; DDM27); max(P/E 8,0; DDM40)] (đầu vào giữa)
CENTER = 20_700
PE_EXP = (12_400, 19_600, 24_400)   # (i) P/E kỳ vọng lo/mid/hi
DDM_EXP = (14_800, 22_000, 27_300)  # (ii) DDM lo (payout 27%) / mid 40% / hi 40%
# theo kịch bản giá (pháp lý ổn, mid, đúng mốc): P/E 7,42, DDM27, DDM40; LNST hoạt động ổn/cấm thầu mid
SCN = [("(a) giữ ~975 đ/kWh · P 10%", 39_200, 38_300, 39_300, 143.1, 118.1),
       ("(b) 600 đ/kWh · P 45%", 22_500, 24_000, 24_500, 81.6, 56.6),
       ("(c) 500 đ/kWh · P 35%", 18_000, 20_100, 20_600, 65.2, 40.2),
       ("(d) ~340 đ/kWh · P 10%", 10_900, 14_000, 14_300, 39.0, 14.0)]
SOTP = (15_500, 51_100)            # SOTP: (d) thấp … (a) cao; kỳ vọng ~28.000, trộn pháp lý ~25.900
SOTP_DISC = (15_600, 20_800)       # SOTP trộn × (0,6–0,8): chiết khấu thiểu số/holding thông lệ 20–40%
SRC = "Nguồn: BCTC hợp nhất Q3/2026 (chưa soát xét), BCTC bán niên 2026 (soát xét); tính toán của nhóm nghiên cứu."


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


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
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.3, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def crop_to(im, ratio):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


# phần ảnh banner không chứa khung chữ của website (x0, x1)
CROPS = {"dam": ("dl_Untitled-2.png", 1020, 1583), "grid": ("dl_Untitled-3.png", 0, 740),
         "wind": ("dl_Untitled-1.png", 1000, 1583)}


def banner_crop(key):
    from PIL import Image
    f, x0, x1 = CROPS[key]
    im = Image.open(os.path.join(WEB, f)).convert("RGB")
    return im.crop((x0, 0, x1, im.height))


def figs():
    import numpy as np
    import pandas as pd
    from PIL import Image, ImageDraw, ImageFont
    plt = setup_mpl()

    # 00 HERO ----------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.36, 0.92]); axp.axis("off")
    axp.imshow(crop_to(banner_crop("grid"), 0.36 * 7.2 / (0.92 * 3.3)), aspect="auto")
    axp.text(0.04, 0.05, "Minh hoạ lĩnh vực tư vấn lưới điện — ảnh:\nwebsite pecc1.com.vn", transform=axp.transAxes,
             color="white", fontsize=5.8, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.39, 0.50, 0.60, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "19.800 đ"), ("Vùng giá trị hợp lý (ước lượng)", "18,2–22,0k"),
            ("LNST bền 2027+ ở 500–600 đ/kWh", "65–82 tỷ"), ("Giá điện hoà vốn với giá 19,8k (đ/kWh)", "≈515–540"),
            ("P/E thuỷ điện UPCOM 2026 · TV1 áp", "8,6 · 7,4x"), ("Cổ tức FY2025 · lợi suất", "1.500 đ · 7,6%")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=11, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=5.2, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.41, 0.17, 0.56, 0.22])
    axv.barh(0, PE_EXP[2] - DDM_EXP[0], left=DDM_EXP[0], color=LIGHT, height=0.5)
    axv.barh(0, FAIR[1] - FAIR[0], left=FAIR[0], color=NAVY, height=0.5, alpha=0.85)
    for lab, pe, d27, d40, _, _ in SCN:
        c = (pe + d40) / 2
        axv.plot(c, 0, "o", color=GREY, ms=4.5)
        axv.text(c, -0.62, f"{lab[:3]} {vn(c/1000,1)}k", ha="center", fontsize=6.2, color="#444")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--")
    axv.text(PX + 300, 0.42, "giá 19,8k", ha="left", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(6_000, 42_000); axv.set_ylim(-0.9, 0.9); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    axv.set_xticks(range(10_000, 40_001, 5_000)); axv.set_xticklabels([f"{t//1000}k" for t in range(10_000, 40_001, 5_000)], fontsize=7)
    axv.set_title("Giá 19,8k nằm trong vùng giá trị hợp lý (khối đậm); chấm = kịch bản giá điện", fontsize=7.6, pad=3)
    save(fig, "fig_00_hero", "Nguồn: giá DNSE (đóng cửa 30/10/2026, UPCOM); BCTC Q3/2026; tính toán của nhóm nghiên cứu (ước lượng). Ảnh: banner website pecc1.com.vn.",
         pd.DataFrame({"chi_so": [k for k, _ in kpis], "gia_tri": [v for _, v in kpis]}))
    plt.close(fig)

    # 01 DT & LNST theo quý ----------------------------------------------------
    q = ["Q1/24", "Q2/24", "Q3/24", "Q4/24", "Q1/25", "Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]
    rev = [78.1, 107.9, 148.1, 228.1, 112.6, 128.7, 149.3, 318.0, 144.8, 134.0, 168.1]
    np_ = [14.5, 16.3, 27.5, 33.7, 30.6, 29.0, 26.8, 63.8, 32.2, 25.5, 66.9]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.2, top=0.86, left=0.08, right=0.98)
    x = np.arange(len(q))
    ax.bar(x - 0.2, rev, width=0.4, color=[LIGHT] * 10 + [GREY], label="Doanh thu thuần")
    ax.bar(x + 0.2, np_, width=0.4, color=[NAVY] * 10 + [ACCENT], label="LNST")
    for i in range(len(q)):
        ax.text(i + 0.2, np_[i] + 4, vn(np_[i], 1), ha="center", fontsize=6.4, color=NAVY if i < 10 else ACCENT, weight="bold" if i == 10 else None)
    ax.annotate("Q3/26: 66,9 tỷ, gần một nửa\nlà thu nhập khác 33,8 tỷ\nchưa thuyết minh", (10.2, 66.9), (7.4, 215), fontsize=6.8, color=ACCENT,
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
    ax.annotate("Q4 là mùa nước thuỷ điện\n(Q4/25 ≈47% DT thuỷ điện năm)", (7, 318), (4.2, 228), fontsize=6.6, color="#444",
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.set_xticks(x); ax.set_xticklabels(q, fontsize=7.4); ax.set_ylim(0, 345); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("Doanh thu đi theo mùa nước; LNST quý 3 cao nhất 11 quý, nhưng phần đột biến là một lần")
    save(fig, "fig_01_quarterly", "Q1/24–Q2/26: dữ liệu tài chính tổng hợp theo quý (Q1+Q2/26 = 57,76 tỷ khớp LNST H1 soát xét 57,759). Q3/26: BCTC chưa soát xét. " + SRC,
         pd.DataFrame({"quy": q, "dt_thuan": rev, "lnst": np_}))
    plt.close(fig)

    # 02 LNST báo cáo vs lõi (r3: tách hai trường hợp hạch toán) -------------------------
    labs = ["Q3/25\nlõi", "Q3/26\nbáo cáo", "Q3/26 bỏ\nthu nhập khác", "lõi (A) hoàn nhập\nvào chi phí QL", "lõi (B) hoàn nhập\nvào thu nhập khác"]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.26, top=0.86, left=0.09, right=0.98)
    ax.bar(0, 30.7, color=GREY, width=0.55); ax.bar(1, 66.9, color=ACCENT, width=0.55); ax.bar(2, 36.0, color=NAVY, width=0.55)
    ax.bar(3, 45 - 16, bottom=16, color=NAVY, alpha=0.35, width=0.55, hatch="//", edgecolor=NAVY)
    ax.bar(4, 45 - 31, bottom=31, color=NAVY, alpha=0.35, width=0.55, hatch="//", edgecolor=NAVY)
    for i, v in ((0, 30.7), (1, 66.9), (2, 36.0)):
        ax.text(i, v + 2, vn(v, 1), ha="center", fontsize=8, weight="bold")
    ax.text(3, 47, "16–45", ha="center", fontsize=8, weight="bold", color=NAVY)
    ax.text(4, 47, "31–45", ha="center", fontsize=8, weight="bold", color=NAVY)
    ax.text(3, 6, "khác 31,9 không\ngiải thích được", ha="center", fontsize=6.0, color="#444")
    ax.text(4, 20, "còn ≈16 chưa\ngiải thích", ha="center", fontsize=6.0, color="#444")
    ax.set_xticks(range(5)); ax.set_xticklabels(labs, fontsize=7.0); ax.set_xlim(-0.5, 4.5); ax.set_ylim(0, 78); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.set_title("Lãi lõi quý 3: 16–45 hoặc 31–45 tỷ tuỳ cách hạch toán hoàn nhập — không phải 66,9 (ước lượng)")
    save(fig, "fig_02_core_np", "LNST lõi (ước lượng, thuế 20%). Hoàn nhập dự phòng phải thu 19,2 tỷ trong quý 3 chưa rõ ghi vào chi phí quản lý (A) hay thu nhập khác (B); hai trường hợp loại trừ nhau. 9T lõi: (A) −17%…+15%, (B) 0%…+15% so cùng kỳ. " + SRC,
         pd.DataFrame({"chi_tieu": [l.replace("\n", " ") for l in labs], "thap": [30.7, 66.9, 36.0, 16, 31], "cao": [30.7, 66.9, 36.0, 45, 45]}))
    plt.close(fig)

    # 03 Dự phòng ------------------------------------------------------------------
    d = ["01/01/2026\n(kiểm toán 2025)", "30/06/2026\n(soát xét)", "30/09/2026\n(chưa soát xét)"]
    ar = [113.10, 105.08, 85.91]; inv = [59.56, 59.29, 53.57]; kh = [89.93, 90.81, 68.36]   # r3: 01/01 = BCTC 2025 kiểm toán (16,75 + 73,18), không phải 63,2
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.31, top=0.86, left=0.09, right=0.98)
    x = np.arange(3)
    ax.bar(x, ar, width=0.5, color=NAVY, label="Dự phòng phải thu ngắn hạn (tổng)")
    ax.bar(x, inv, bottom=ar, width=0.5, color=GREY, label="Dự phòng giảm giá tồn kho")
    for i in range(3):
        ax.text(i, ar[i] / 2, vn(ar[i], 1), ha="center", va="center", color="white", fontsize=7.5, weight="bold")
        ax.text(i, ar[i] + inv[i] / 2, vn(inv[i], 1), ha="center", va="center", color="white", fontsize=7.5)
    ax.plot(x, kh, "o-", color=GOLD, lw=1.6, label="trong đó: dự phòng phải thu khách hàng")
    for i in range(3):
        ax.text(i - 0.08, kh[i] + 6, vn(kh[i], 1), fontsize=7, color="#8a6d10", weight="bold", ha="right", bbox=dict(fc="white", ec="none", pad=0.6))
    ax.annotate("−24,9 tỷ trong quý 3\n(khách hàng −22,4)", (2, 142), (1.45, 178), fontsize=7.2, color=ACCENT, weight="bold",
                arrowprops=dict(arrowstyle="->", color=ACCENT))
    ax.set_xticks(x); ax.set_xticklabels(d, fontsize=7.4); ax.set_ylim(0, 270); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.legend(fontsize=6.4, frameon=False, loc="upper left", ncol=3)
    ax.set_title("Cờ: dự phòng khách hàng đi ngang ở H1 (89,9 và 90,8) rồi giảm ≈22 tỷ trong quý chưa soát xét")
    save(fig, "fig_03_provisions", "Phải thu khách hàng gộp không giảm tương ứng (378,7 lên 387,5), nên không phải xoá sổ nợ. Dự phòng tổng 85,9 lệch thuyết minh (70,5) ≈15 tỷ, chưa giải. Thuyết minh quý 3 ghi dự phòng khách hàng đầu năm 63,2 — lệch 26,7 tỷ so BCTC 2025 đã kiểm toán (89,9). " + SRC,
         pd.DataFrame({"ngay": [s.replace("\n", " ") for s in d], "du_phong_phai_thu": ar, "du_phong_htk": inv, "du_phong_kh": kh}))
    plt.close(fig)

    # 04 CFO vs LNST -----------------------------------------------------------------
    per = ["9T/2025", "9T/2026", "Q3/2026"]
    cfo = [137.6, 116.8, 69.8]; npv = [86.4, 124.6, 66.9]; npx = [None, 92.7, None]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); fig.subplots_adjust(bottom=0.2, top=0.86, left=0.09, right=0.98)
    x = np.arange(3)
    ax.bar(x - 0.2, cfo, width=0.4, color=GREEN, label="Dòng tiền kinh doanh (CFO)")
    ax.bar(x + 0.2, npv, width=0.4, color=GREY, label="LNST báo cáo")
    ax.plot(1 + 0.2, 92.7, "D", color=NAVY, ms=6, label="LNST bỏ khoản khác ròng (92,7)")
    for i in range(3):
        ax.text(i - 0.2, cfo[i] + 3, vn(cfo[i], 1), ha="center", fontsize=7.5, weight="bold", color=GREEN)
        ax.text(i + 0.2, npv[i] + 3, vn(npv[i], 1), ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(per); ax.set_ylim(0, 165); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.legend(fontsize=6.8, frameon=False, loc="upper right")
    ax.set_title("Dòng tiền khớp lợi nhuận lõi: CFO 9T = 1,26× LNST đã bỏ khoản một lần")
    save(fig, "fig_04_cfo", "CFO Q3 = 9T − H1 soát xét (47,03). " + SRC,
         pd.DataFrame({"ky": per, "cfo": cfo, "lnst": npv, "lnst_bo_khac": npx}))
    plt.close(fig)

    # 05 Tiền ròng điều chỉnh ----------------------------------------------------------
    labs = ["Tiền + tiền gửi\nđến hạn", "Vay\n(118,8 cá nhân)", "Tiền ròng thô", "Cổ tức đã trả\n29/10", "Lãi vay cá nhân\nphải trả", "Tiền ròng\nđiều chỉnh"]
    vals = [198.5, -129.9, 68.7, -43.2, -64.3, -38.7]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); fig.subplots_adjust(bottom=0.26, top=0.86, left=0.09, right=0.98)
    ax.bar(labs, vals, color=[GREEN, ACCENT, NAVY, ACCENT, ACCENT, NAVY], width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 6 if v > 0 else v - 17, ("+" if v > 0 and i in (2,) else "") + vn(v, 1), ha="center", fontsize=7.6, weight="bold")
    ax.axhline(0, color="#555", lw=0.8); ax.set_ylim(-170, 230); ax.set_ylabel("Tỷ đồng", fontsize=8); ax.tick_params(axis="x", labelsize=7.2)
    ax.set_title("Tiền dồi dào trên bề mặt; trừ nghĩa vụ đã biết thì tiền ròng ≈ −39 tỷ")
    save(fig, "fig_05_netcash", "Số 30/09/2026; lãi vay cá nhân phải trả lấy mốc 30/06 (Q3 không tách) — ước lượng. Gồm khoản đang tranh chấp (tổng nợ vay + lãi 127,63 tỷ theo đoạn nhấn mạnh soát xét H1). " + SRC,
         pd.DataFrame({"chi_tieu": [l.replace("\n", " ") for l in labs], "ty_dong": vals}))
    plt.close(fig)

    # 06 Giá 12 tháng -------------------------------------------------------------------
    px = pd.read_csv(os.path.join(HERE, "scripts", "tv1_px_bq.csv"), parse_dates=["time"]).rename(columns={"time": "date"})
    px = px[px.date >= "2025-10-30"]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.2, top=0.86, left=0.11, right=0.98)
    ax.plot(px.date, px.Close, color=NAVY, lw=1.4)
    ev = [("2026-05-07", "Khởi tố Chủ tịch\n+ phó phòng TCKT", 7000), ("2026-07-02", "Bộ Công an nêu\n13 đơn vị (có TV1)", 7000),
          ("2026-08-28", "Soát xét H1\n(An Việt)", -6000), ("2026-10-07", "GDKHQ cổ tức\n1.500 đ", -6500), ("2026-10-29", "BCTC Q3", 5500)]
    for dt, lab, off in ev:
        t = pd.Timestamp(dt); r = px[px.date >= t].iloc[0]
        ax.plot(r.date, r.Close, "o", color=ACCENT, ms=4.5)
        ax.annotate(lab, (r.date, r.Close), (r.date, r.Close + off), fontsize=6.2, ha="center", color=ACCENT,
                    arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    ax.axhspan(FAIR[0], FAIR[1], color=NAVY, alpha=0.18)
    ax.text(px.date.iloc[2], 10_500, f"dải ngang = vùng giá trị cân bằng {vn(FAIR[0]/1000,1)}–{vn(FAIR[1]/1000,1)}k (ước lượng)", fontsize=6.6, color=NAVY)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_ylim(8_000, 40_000); ax.set_ylabel("đ/cp (điều chỉnh)", fontsize=8)
    c0, c1 = px.Close.iloc[0], px.Close.iloc[-1]
    hi = px.Close.max()
    ax.set_title(f"12 tháng {vn((c1/c0-1)*100,1)}%; −{vn((1-c1/hi)*100,0)}% từ đỉnh 25/03/2026, ≈3/4 mức giảm xảy ra TRƯỚC ngày khởi tố")
    save(fig, "fig_06_price", f"Giá đóng cửa đã điều chỉnh cổ tức, 30/10/2025–30/10/2026 (đóng cửa 30/10 khớp DNSE 19.800). Sự kiện: quan sát, không chứng minh nhân quả. Tính toán của nhóm nghiên cứu.",
             px[["date", "Close", "Price", "Volume"]])
    plt.close(fig)
    print("px 12m", c0, c1, hi, px.loc[px.Close.idxmax(), "date"].date())

    # 07 Football field -------------------------------------------------------
    rows = [("(d) giá ~340 đ/kWh: P/E · DDM", 10_900, 14_300, ACCENT),
            ("(c) giá 500 đ/kWh: P/E · DDM", 18_000, 20_600, NAVY),
            ("(b) giá 600 đ/kWh: P/E · DDM", 22_500, 24_500, NAVY),
            ("(a) giữ giá ~975 đ/kWh: P/E · DDM", 38_300, 39_300, GREEN),
            ("(i) P/E 6,8–8,0x kỳ vọng (LNST bền 2027+)", PE_EXP[0], PE_EXP[2], GREY),
            ("(ii) DDM kỳ vọng (payout 27–40%, Ke 9,5–11,1%)", DDM_EXP[0], DDM_EXP[2], GREY),
            ("Vùng giá trị hợp lý (hợp hai phương pháp)", FAIR[0], FAIR[1], NAVY),
            ("SOTP trộn × 0,6–0,8 (chiết khấu thiểu số thông lệ)", SOTP_DISC[0], SOTP_DISC[1], GOLD),
            ("Giá trị tài sản (SOTP), từ (d) đến (a)", SOTP[0], SOTP[1], GOLD)]
    fig, ax = plt.subplots(figsize=(7.2, 3.6)); fig.subplots_adjust(bottom=0.22, top=0.89, left=0.42, right=0.97)
    for i, (lab, lo, hi_, c) in enumerate(rows[::-1]):
        ax.barh(i, hi_ - lo, left=lo, color=c, height=0.55, alpha=0.9)
        ax.text(hi_ + 400, i, f"{vn(lo/1000,1)}–{vn(hi_/1000,1)}k", va="center", fontsize=6.6, bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=6.8)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.6); ax.text(PX + 400, len(rows) - 0.35, "giá 19,8k", color=ACCENT, fontsize=7.2, ha="left", weight="bold")
    ax.set_xlim(0, 58_000); ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xticks(range(0, 50_001, 10_000)); ax.set_xticklabels([f"{t//1000}k" for t in range(0, 50_001, 10_000)], fontsize=7)
    ax.set_title("Giá 19,8k trong vùng giá trị 18,2–22,0k (tâm ≈20,7k); hoà vốn ở giá điện ≈515–540 đ/kWh", loc="right", fontsize=8.8)
    save(fig, "fig_07_football", "Mỗi kịch bản giá điện (pháp lý ổn, giữa): khoảng giữa P/E 7,42x (trên LNST bền 2027+ cộng tiền ròng) và DDM payout 27–40%. Kỳ vọng: trọng số giá 10/45/35/10 × pháp lý ổn/cấm thầu 70/30 × mốc hạ đúng 2027/lùi 2 năm 85/15; PV về 11/2026, lợi suất yêu cầu 9,5–11,1% (đo từ cổ tức thuỷ điện niêm yết), cộng cổ tức 2026. P/E = thuỷ điện UPCOM 2026 × hệ số payout thấp 0,87. SOTP = thuỷ điện DCF 2027–2059 + tư vấn − nợ điều chỉnh; cổ đông thiểu số nhận qua cổ tức hoặc bán tài sản. Ước lượng của nhóm nghiên cứu.",
         pd.DataFrame(rows, columns=["phep_do", "thap", "cao", "mau"]).drop(columns="mau"))
    plt.close(fig)

    # 12 LNST bền theo kịch bản giá PPA ------------------------------------------
    labs = ["2025 (giá ≈949)", "(a) ~975", "(b) 600", "(c) 500", "(d) ~340"]
    hydro = [122.7, 103.1, 41.6, 25.2, -1.0]         # LNST thuỷ điện, Q 205 (2025: Q 236,6, giá 949)
    cons = [35.8, 40, 40, 40, 40]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.24, top=0.87, left=0.09, right=0.98)
    x = np.arange(len(labs))
    ax.bar(x, hydro, width=0.55, color=NAVY, label="Thuỷ điện Sông Bung 5 (LNST)")
    ax.bar(x, cons, bottom=[max(h, 0) for h in hydro], width=0.55, color=GOLD, label="Tư vấn (LNST, pháp lý ổn)")
    for i in range(len(labs)):
        tot = hydro[i] + cons[i]
        ax.text(i, max(hydro[i], 0) + cons[i] + 4, vn(tot, 0), ha="center", fontsize=7.6, weight="bold", color="#222")
    ax.axhline(71.8, color=ACCENT, ls="--", lw=1.2, label="LNST hoà vốn với giá 19,8k ≈72 (P/E 7,42x; giá điện ≈540)")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=7.6); ax.set_ylabel("tỷ đồng/năm", fontsize=8); ax.set_ylim(-15, 185)
    ax.legend(fontsize=6.8, frameon=False, loc="upper right")
    ax.set_title("LNST bền 2027+ theo giá điện Sông Bung 5: ở 500–600 đ/kWh còn ≈65–82 tỷ")
    save(fig, "fig_12_np_by_ppa", "Giá ròng chưa thuế tài nguyên/phí DVMTR (EVN trả thêm ngoài giá). Sản lượng 205 tr kWh (bình quân các năm có số 2015–2025); O&M 25, khấu hao 38, chi phí chung 8 tỷ; thuế 20%. 2025: báo cáo bộ phận BCTC kiểm toán (giá ròng ≈949, Q 236,6). Tư vấn 40 tỷ nếu không bị cấm thầu (2025 ≈35,8; 2024 ≈15,1). Ước lượng của nhóm nghiên cứu.",
         pd.DataFrame({"kich_ban": labs, "lnst_thuy_dien": hydro, "lnst_tu_van": cons, "tong": [h + c for h, c in zip(hydro, cons)]}))
    plt.close(fig)

    # 13 Cổ tức cần có vs thực trả / bền vững --------------------------------------
    labs = ["Cần có để\nbiện minh 19,8k", "Thực trả\nFY2025", "Kế hoạch\nFY2026", "(a) ~975", "(b) 600", "(c) 500", "(d) ~340"]
    lo = [1_879, 1_500, 1_000, 1_458, 826, 657, 388]; hi = [2_198, 1_500, 1_000, 2_160, 1_224, 974, 574]
    cols = [ACCENT, NAVY, NAVY, GREEN, GREY, GREY, GREY]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.26, top=0.87, left=0.09, right=0.98)
    x = np.arange(len(labs))
    ax.bar(x, lo, width=0.55, color=cols, alpha=0.9)
    ax.bar(x, [h - l for h, l in zip(hi, lo)], bottom=lo, width=0.55, color=cols, alpha=0.45)
    for i in range(len(labs)):
        t = vn(lo[i]) if lo[i] == hi[i] else f"{vn(lo[i])}–{vn(hi[i])}"
        ax.text(i, hi[i] + 60, t, ha="center", fontsize=6.8, weight="bold")
    ax.axhspan(1_879, 2_198, color=ACCENT, alpha=0.08)
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=7); ax.set_ylabel("đ/cổ phiếu/năm", fontsize=8); ax.set_ylim(0, 3_000)
    ax.set_title("Chỉ trả cổ tức 27–40%: cổ tức bền ≈650–1.200 đ < 1.900–2.200 đ cần có — phần còn lại là tiền giữ lại")
    save(fig, "fig_13_dividend_gap", "Cần có = 19.800 × lợi suất yêu cầu 9,5–11,1% (thuỷ điện niêm yết, không tăng trưởng). Phần chênh không mất đi: lợi nhuận giữ lại tích luỹ thành tiền ròng, đã tính trong DDM theo giá trị sổ ở năm 10. Bền vững 2028+: tỷ lệ chi trả 27% (thực tế FY2025) đến 40% × LNST bền giữa (gồm lãi tiền), pháp lý ổn. Kế hoạch FY2026 = 10% mệnh giá (ĐHĐCĐ 30/04/2026, báo Đấu thầu). Ước lượng của nhóm nghiên cứu.",
         pd.DataFrame({"muc": [l.replace("\n", " ") for l in labs], "thap": lo, "cao": hi}))
    plt.close(fig)

    # 14 Peer P/E -----------------------------------------------------------------------
    PS = os.path.join(HERE, "..", "calc", "peer_study")
    T = pd.read_csv(os.path.join(PS, "out_pe_pb_by_group_year.csv"))
    th = T[T.nhom == "thuy_dien"].set_index("y"); tn = T[T.nhom == "nhiet_dien"].set_index("y")
    tv = {2023: 11.16, 2024: 7.82, 2025: 5.71, 2026: 4.04}   # peer_study_out.txt "TV1 P/E theo năm" (trên LNST giá điện cũ)
    up = {2019: 8.39, 2020: 9.92, 2021: 10.58, 2022: 10.24, 2023: 8.74, 2024: 14.65, 2025: 11.00, 2026: 8.55}
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.24, top=0.87, left=0.08, right=0.98)
    ax.fill_between(th.index, th.pe_p25, th.pe_p75, color=LIGHT, alpha=0.9, label="Thuỷ điện niêm yết: p25–p75 (32 mã)")
    ax.plot(th.index, th.pe_med, color=NAVY, lw=2, marker="o", ms=4, label="Thuỷ điện: trung vị")
    ax.plot(list(up), list(up.values()), color=NAVY, lw=1.2, ls=":", marker=".", label="Thuỷ điện UPCOM: trung vị (14 mã)")
    ax.plot(tn.index, tn.pe_med, color=GREY, lw=1.1, ls="--", label="Nhiệt điện: trung vị (9 mã)")
    ax.plot(list(tv), list(tv.values()), color=ACCENT, lw=1.6, marker="s", ms=4, label="TV1 (lợi nhuận ở giá điện cũ)")
    ax.axhspan(6.8, 8.0, color=GOLD, alpha=0.18); ax.text(2019.05, 7.1, "dải áp cho TV1 6,8–8,0x", fontsize=6.8, color="#8a6d10")
    for y_, v_ in ((2026, th.pe_med[2026]), (2026, up[2026])):
        ax.text(y_ + 0.08, v_, vn(v_, 1), fontsize=6.8, va="center", color=NAVY)
    ax.set_ylim(0, 24); ax.set_ylabel("P/E (lần)", fontsize=8); ax.legend(fontsize=6.4, frameon=False, ncol=2, loc="upper left")
    ax.set_title("P/E thuỷ điện 2026: trung vị 9,2x (UPCOM 8,6x); TV1 ≈4x trên lợi nhuận ở giá điện cũ", fontsize=8.8)
    save(fig, "fig_14_peer_pe", "P/E trailing, trung vị theo mã–năm của các phiên cuối tháng (loại P/E ≤0 hoặc ≥60); 2026 = đến 02/11/2026. Nhóm thuỷ điện = 32 mã ngành điện truyền thống có nhà máy thuỷ điện là chính (phân loại theo tên doanh nghiệp). Nguồn: cơ sở dữ liệu thị trường của nhóm nghiên cứu; truy vấn và tính toán lưu cùng báo cáo.",
         T[T.nhom.isin(["thuy_dien", "nhiet_dien"])])
    plt.close(fig)

    # 15 Peer yield -------------------------------------------------------------------
    Y = pd.read_csv(os.path.join(PS, "out_yield_ticker_year.csv"))
    yh = Y[(Y.grp == "thuy_dien") & (Y.dps > 0)]
    v = (yh.yld * 100).clip(upper=20)
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.24, top=0.87, left=0.08, right=0.98)
    ax.hist(v, bins=np.arange(0, 21, 1), color=NAVY, alpha=0.75, edgecolor="white")
    lines = [(6.8, GREEN, "Tiết kiệm 12T Big-4 6,8%"), (v.median(), NAVY, f"Trung vị {vn(v.median(),1)}%"),
             (9.5, GOLD, "Lợi suất yêu cầu áp cho TV1 9,5–11,1%"), (12.85, ACCENT, "Ke khung DCF nội địa 12,3–13,4%")]
    for x_, c_, l_ in lines:
        ax.axvline(x_, color=c_, ls="--", lw=1.3, label=l_)
    ax.axvspan(9.5, 11.1, color=GOLD, alpha=0.15); ax.axvspan(12.3, 13.4, color=ACCENT, alpha=0.08)
    n10 = int((yh.yld >= .10).sum()); n12 = int((yh.yld >= .12).sum())
    ax.set_xlabel("Tỷ suất cổ tức tiền thực hiện trong năm (%), 2019–2025, mã có trả (cắt ở 20%)", fontsize=7.6); ax.set_ylabel("số mã–năm", fontsize=8)
    ax.legend(fontsize=6.4, frameon=False, loc="upper right")
    ax.set_title(f"Cổ tức thuỷ điện: trung vị ≈7%; ≥12% chỉ {n12}/{len(yh)} mã–năm; không mã nào ≥10% quá 3 năm liền", fontsize=8.6)
    save(fig, "fig_15_peer_yield", "Tỷ suất = tổng cổ tức tiền có ngày GDKHQ trong năm / giá bình quân cuối tháng trong năm. 32 mã thuỷ điện, chỉ mã–năm có trả. Lãi tiết kiệm 12 tháng Big-4 (kênh online) 02/11/2026. Nguồn: dữ liệu sự kiện doanh nghiệp + giá của nhóm nghiên cứu.",
         yh[["ticker", "y", "dps", "px", "yld"]])
    plt.close(fig)
    print("peer ge10", n10, "ge12", n12, "n", len(yh))

    # 08 Ma trận rủi ro -------------------------------------------------------------
    risks = [("Giá điện Sông Bung 5 hạ về ≤600 đ/kWh từ 2027", 0.75, 0.95),
             ("Cấm thầu EVN 3–5 năm / buộc nộp lợi bất chính", 0.30, 0.80), ("Kiểm toán 2026 ngoại trừ", 0.35, 0.80),
             ("Khoản thu nhập khác 33,8 tỷ bị đảo", 0.40, 0.45), ("El Niño cắt sản lượng thuỷ điện", 0.50, 0.55),
             ("Lợi nhuận được giữ lại, cổ tức không tăng", 0.50, 0.55), ("Phán quyết vay cá nhân vượt sổ", 0.20, 0.35),
             ("Truy thu phần giá điện trả vượt 2022–26", 0.10, 0.85),
             ("Thanh khoản mỏng (trung vị 0,41 tỷ/phiên)", 0.85, 0.25)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.22, top=0.88, left=0.10, right=0.98)
    ax.axhspan(0.6, 1.0, xmin=0.5, color=ACCENT, alpha=0.08); ax.axvline(0.5, color=LIGHT); ax.axhline(0.6, color=LIGHT)
    for lab, p, im in risks:
        c = ACCENT if im >= 0.6 else (GOLD if im >= 0.4 else GREY)
        ax.scatter(p, im, s=90, color=c, zorder=3)
        ha = "right" if p > 0.7 else "left"
        ax.text(p + (-0.02 if ha == "right" else 0.02), im + 0.035, lab, fontsize=6.6, ha=ha)
    ax.set_xlim(0, 1); ax.set_ylim(0.1, 1.0); ax.set_xlabel("Xác suất xảy ra (ước lượng, khớp mốc M0–M9)", fontsize=8); ax.set_ylabel("Tác động lên giá trị", fontsize=8)
    ax.set_yticks([0.25, 0.5, 0.8]); ax.set_yticklabels(["thấp", "trung bình", "cao"], fontsize=7)
    ax.set_title("Rủi ro lớn nhất là giá điện Sông Bung 5 sau 2027; tiếp theo là pháp lý và kiểm toán")
    save(fig, "fig_08_risk", "Xác suất/tác động: phán đoán của nhóm nghiên cứu, nhất quán với mốc M0–M9 (không phải đo thống kê).",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)

    # 09 Hai mảng --------------------------------------------------------------------
    per = ["Q3/25", "Q3/26", "9T/25", "9T/26"]
    hyd = [41.6, 41.2, 138.3, 122.4]; con = [107.7, 126.9, 252.3, 324.5]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.27, top=0.88, left=0.09, right=0.98)
    x = np.arange(4)
    ax.bar(x, hyd, width=0.55, color=NAVY, label="Thuỷ điện Sông Bung 5")
    ax.bar(x, con, bottom=hyd, width=0.55, color=GOLD, label="Tư vấn khảo sát–thiết kế")
    for i in range(4):
        ax.text(i, hyd[i] / 2, vn(hyd[i], 1), ha="center", va="center", color="white", fontsize=7.4, weight="bold")
        ax.text(i, hyd[i] + con[i] / 2, vn(con[i], 1), ha="center", va="center", color="#222", fontsize=7.4, weight="bold")
    ax.text(1, hyd[1] + con[1] + 10, "tư vấn +18%", ha="center", fontsize=7, color="#8a6d10", weight="bold")
    ax.text(3, hyd[3] + con[3] + 10, "tư vấn +29% · thuỷ điện −11,5%", ha="center", fontsize=7, color="#8a6d10", weight="bold")
    ax.set_xticks(x); ax.set_xticklabels(per); ax.set_ylim(0, 530); ax.set_ylabel("Doanh thu, tỷ đồng", fontsize=8)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("[Ước lượng proxy] Tư vấn đang tăng khối lượng; thuỷ điện đi ngang–giảm theo thời tiết")
    save(fig, "fig_09_segments", "Ước lượng proxy: BCTC Q3 không có báo cáo bộ phận; doanh thu thuỷ điện suy từ thuế tài nguyên phải nộp (tỷ lệ ổn định ≈10,8–11,0% DT trên 2025–H1/26), tư vấn = phần còn lại. 2025: thuỷ điện 67% lợi nhuận gộp. " + SRC,
         pd.DataFrame({"ky": per, "thuy_dien": hyd, "tu_van": con}))
    plt.close(fig)

    # 10 Khung ảnh website ---------------------------------------------------------------
    items = [("dam", "Thuỷ điện — minh hoạ, không phải tài sản công ty"), ("grid", "Lưới truyền tải"), ("wind", "Điện gió · mặt trời")]
    W, H, pad = 1440, 330, 8
    w = (W - pad * 4) // 3
    canvas = Image.new("RGB", (W, H + 56), "white"); dr = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(FONT_B, 18)
    for i, (k, cap) in enumerate(items):
        im = crop_to(banner_crop(k), w / H).resize((w, H))
        x = pad + i * (w + pad); canvas.paste(im, (x, pad)); dr.rectangle((x, pad, x + w - 1, pad + H - 1), outline="#C9D2DC")
        dr.text((x + 2, H + pad + 8), cap, font=fb, fill=NAVY)
    canvas.save(os.path.join(FIGS, "fig_10_photos.png"))
    pd.DataFrame([(CROPS[k][0], c) for k, c in items], columns=["file", "chu_thich"]).assign(
        nguon="banner trang chủ pecc1.com.vn (tải 02/11/2026); minh hoạ lĩnh vực, không xác định công trình").to_csv(os.path.join(FIGS, "fig_10_photos.csv"), index=False)

    # 11 Ghép bản đồ ---------------------------------------------------------------------
    a = Image.open(os.path.join(FIGS, "map_central.png")).convert("RGB"); b = Image.open(os.path.join(FIGS, "map_hn.png")).convert("RGB")
    hh = min(a.height, b.height)
    a = a.resize((int(a.width * hh / a.height), hh)); b = b.resize((int(b.width * hh / b.height), hh))
    canvas = Image.new("RGB", (a.width + b.width + 20, hh), "white"); canvas.paste(a, (0, 0)); canvas.paste(b, (a.width + 20, 0))
    canvas.save(os.path.join(FIGS, "fig_11_maps.png"))
    pd.read_csv(os.path.join(HERE, "scripts", "pts_central.csv")).pipe(
        lambda df: pd.concat([df, pd.read_csv(os.path.join(HERE, "scripts", "pts_hn.csv"))])).to_csv(os.path.join(FIGS, "fig_11_maps.csv"), index=False)
    print("figs ok")
