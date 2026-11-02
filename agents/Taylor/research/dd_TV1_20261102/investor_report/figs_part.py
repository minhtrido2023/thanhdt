"""Biểu đồ cho báo cáo DD nhà đầu tư TV1 (02/11/2026). Import bởi build_report.py.
Số: ../REPORT.md (vòng 2, đã áp 12 đính chính của người phản biện) + ../calc/valuation_out.txt. Mỗi hình kèm CSV.
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
PV = (19_200, 20_600)            # PV kỳ vọng 25/50/25, T=1–2 năm, Ke 12,3–13,4%
EVU = 21_600                     # kỳ vọng chưa chiết khấu (2027–28)
BASE = (13_500, 29_000, 20_100)
SCEN = {"Xấu": (10_800, 15_100, 12_900), "Cơ sở": BASE, "Tốt": (28_500, 38_700, 33_400)}
SOTP = (23_900, 44_200)
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
    kpis = [("Giá 30/10/2026", "19.800 đ"), ("Kỳ vọng hiện tại (ước lượng)", "19,2–20,6k"),
            ("Vùng cơ sở (ước lượng)", "13,5–29,0k"), ("P/E 4 quý · bỏ một lần", "2,8x · 3,2–3,8x"),
            ("P/B (Q3 · soát xét 30/6)", "0,92 · 1,04x"), ("Cổ tức 2025 · lợi suất", "1.500 đ · 7,6%")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=11, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=5.9, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.41, 0.17, 0.56, 0.22])
    axv.barh(0, BASE[1] - BASE[0], left=BASE[0], color=LIGHT, height=0.5)
    axv.barh(0, PV[1] - PV[0], left=PV[0], color=NAVY, height=0.5, alpha=0.85)
    for lab, (lo, hi, c) in SCEN.items():
        axv.plot(c, 0, "o", color=GREY, ms=4.5)
        axv.text(c, -0.62, f"{lab} {vn(c/1000,1)}k", ha="center", fontsize=6.2, color="#444")
    for s in SOTP:
        axv.plot(s, 0, "^", color=GOLD, ms=6)
    axv.text(SOTP[1], 0.40, "giá trị tài sản\n(trần tham chiếu)", ha="center", fontsize=5.8, color="#8a6d10")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--")
    axv.text(PX - 400, 0.42, "giá 19,8k", ha="right", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(8_000, 47_000); axv.set_ylim(-0.9, 0.9); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    axv.set_xticks(range(10_000, 46_000, 5_000)); axv.set_xticklabels([f"{t//1000}k" for t in range(10_000, 46_000, 5_000)], fontsize=7)
    axv.set_title("Giá nằm trong dải giá trị kỳ vọng hiện tại (khối đậm), đ/cp", fontsize=7.6, pad=3)
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

    # 02 LNST báo cáo vs lõi -------------------------------------------------------
    labs = ["Q3/25\nlõi", "Q3/26\nbáo cáo", "Q3/26 bỏ\nthu nhập khác", "Q3/26 lõi\nhai chiều"]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.09, right=0.98)
    ax.bar(0, 30.7, color=GREY, width=0.55); ax.bar(1, 66.9, color=ACCENT, width=0.55); ax.bar(2, 36.0, color=NAVY, width=0.55)
    ax.bar(3, 45 - 16, bottom=16, color=NAVY, alpha=0.35, width=0.55, hatch="//", edgecolor=NAVY)
    for i, v in ((0, 30.7), (1, 66.9), (2, 36.0)):
        ax.text(i, v + 2, vn(v, 1), ha="center", fontsize=8, weight="bold")
    ax.text(3, 47, "16–45", ha="center", fontsize=8, weight="bold", color=NAVY)
    ax.text(3.32, 16, "bỏ toàn bộ hoàn nhập\ndự phòng 24,9", fontsize=6.3, va="center")
    ax.text(3.32, 45, "QLDN gấp đôi\nlà một lần", fontsize=6.3, va="center")
    ax.set_xticks(range(4)); ax.set_xticklabels(labs, fontsize=7.4); ax.set_xlim(-0.5, 4.1); ax.set_ylim(0, 78); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.set_title("Lợi nhuận lõi quý 3 là một KHOẢNG 16–45 tỷ, không phải 66,9 tỷ (ước lượng)")
    save(fig, "fig_02_core_np", "LNST lõi (ước lượng, thuế 20%): cột 3 chỉ bỏ khoản khác ròng 31,9; cột 4 hai chiều theo cách đọc chi phí quản lý và hoàn nhập dự phòng. 9T lõi 74–103 tỷ so 88,9 cùng kỳ (−17%…+15%). " + SRC,
         pd.DataFrame({"chi_tieu": [l.replace("\n", " ") for l in labs], "thap": [30.7, 66.9, 36.0, 16], "cao": [30.7, 66.9, 36.0, 45]}))
    plt.close(fig)

    # 03 Dự phòng ------------------------------------------------------------------
    d = ["01/01/2026", "30/06/2026\n(soát xét)", "30/09/2026\n(chưa soát xét)"]
    ar = [113.10, 105.08, 85.91]; inv = [59.56, 59.29, 53.57]; kh = [63.2, 90.81, 68.36]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.09, right=0.98)
    x = np.arange(3)
    ax.bar(x, ar, width=0.5, color=NAVY, label="Dự phòng phải thu ngắn hạn (tổng)")
    ax.bar(x, inv, bottom=ar, width=0.5, color=GREY, label="Dự phòng giảm giá tồn kho")
    for i in range(3):
        ax.text(i, ar[i] / 2, vn(ar[i], 1), ha="center", va="center", color="white", fontsize=7.5, weight="bold")
        ax.text(i, ar[i] + inv[i] / 2, vn(inv[i], 1), ha="center", va="center", color="white", fontsize=7.5)
    ax.plot(x, kh, "o-", color=GOLD, lw=1.6, label="trong đó: dự phòng phải thu khách hàng")
    for i in range(3):
        ax.text(i - 0.08, kh[i] + 6, vn(kh[i], 1), fontsize=7, color="#8a6d10", weight="bold", ha="right", bbox=dict(fc="white", ec="none", pad=0.6))
    ax.annotate("−24,9 tỷ trong quý 3\n(khách hàng −22,4)", (2, 140), (1.45, 185), fontsize=7.2, color=ACCENT, weight="bold",
                arrowprops=dict(arrowstyle="->", color=ACCENT))
    ax.set_xticks(x); ax.set_xticklabels(d, fontsize=7.4); ax.set_ylim(0, 235); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.legend(fontsize=6.4, frameon=False, loc="upper left", ncol=3)
    ax.set_title("Cờ: dự phòng mà bên soát xét còn giữ ở 30/6 được hoàn nhập trong quý chưa soát xét")
    save(fig, "fig_03_provisions", "Phải thu khách hàng gộp không giảm tương ứng (378,7 lên 387,5), nên không phải xoá sổ nợ. Dự phòng tổng 85,9 lệch thuyết minh (70,5) ≈15 tỷ, chưa giải. " + SRC,
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
    ax.axhspan(PV[0], PV[1], color=NAVY, alpha=0.18)
    ax.text(px.date.iloc[2], 10_500, "dải ngang = giá trị kỳ vọng hiện tại 19,2–20,6k (ước lượng)", fontsize=6.6, color=NAVY)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_ylim(8_000, 40_000); ax.set_ylabel("đ/cp (điều chỉnh)", fontsize=8)
    c0, c1 = px.Close.iloc[0], px.Close.iloc[-1]
    hi = px.Close.max()
    ax.set_title(f"12 tháng {vn((c1/c0-1)*100,1)}%; −{vn((1-c1/hi)*100,0)}% từ đỉnh 25/03/2026, ≈3/4 mức giảm xảy ra TRƯỚC ngày khởi tố")
    save(fig, "fig_06_price", f"Giá đóng cửa đã điều chỉnh cổ tức, 30/10/2025–30/10/2026 (đóng cửa 30/10 khớp DNSE 19.800). Sự kiện: quan sát, không chứng minh nhân quả. Tính toán của nhóm nghiên cứu.",
             px[["date", "Close", "Price", "Volume"]])
    plt.close(fig)
    print("px 12m", c0, c1, hi, px.loc[px.Close.idxmax(), "date"].date())

    # 07 Football field ----------------------------------------------------------
    rows = [("Kịch bản xấu (25%): P/B 0,5–0,7x", 10_800, 15_100, ACCENT),
            ("Kịch bản cơ sở (50%): LN 103–172 tỷ × P/E 3,5–4,5x", 13_500, 29_000, NAVY),
            ("Kịch bản tốt (25%): LN 152–172 tỷ × P/E 5–6x", 28_500, 38_700, GREEN),
            ("Kỳ vọng hiện tại 25/50/25 (chiết khấu 1–2 năm)", 19_200, 20_600, NAVY),
            ("Kỳ vọng hiện tại, trọng số xấu hơn (20/50/30; 15/45/40)", 17_200, 19_700, GREY),
            ("Dòng cổ tức 1.500–2.800 đ/năm, Ke 12,3–13,4%", 11_200, 22_800, GREY),
            ("Giá trị tài sản (SOTP) — trần tham chiếu", 23_900, 44_200, GOLD)]
    fig, ax = plt.subplots(figsize=(7.2, 3.2)); fig.subplots_adjust(bottom=0.15, top=0.88, left=0.44, right=0.97)
    for i, (lab, lo, hi_, c) in enumerate(rows[::-1]):
        ax.barh(i, hi_ - lo, left=lo, color=c, height=0.55, alpha=0.9)
        ax.text(hi_ + 400, i, f"{vn(lo/1000,1)}–{vn(hi_/1000,1)}k", va="center", fontsize=6.6, bbox=dict(fc="white", ec="none", pad=0.5), zorder=5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=6.8)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.6); ax.text(PX, len(rows) - 0.35, "giá 19,8k", color=ACCENT, fontsize=7.2, ha="center", weight="bold")
    ax.set_xlim(8_000, 50_000); ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xticks(range(10_000, 50_001, 10_000)); ax.set_xticklabels([f"{t//1000}k" for t in range(10_000, 50_001, 10_000)], fontsize=7)
    ax.set_title("Giá nằm trong vùng giá trị hợp lý, sát giá trị kỳ vọng hiện tại", loc="right", fontsize=8.8)
    save(fig, "fig_07_football", "Kịch bản: giá trị tại 2027–28, chưa chiết khấu. SOTP = thuỷ điện DCF có thời hạn đến 2059 + tư vấn − nợ điều chỉnh; cổ đông thiểu số chỉ nhận qua cổ tức hoặc bán tài sản. Ước lượng của nhóm nghiên cứu.",
         pd.DataFrame(rows, columns=["phep_do", "thap", "cao", "mau"]).drop(columns="mau"))
    plt.close(fig)

    # 08 Ma trận rủi ro -------------------------------------------------------------
    risks = [("R1 Pháp nhân bị khởi tố / cấm thầu EVN", 0.35, 0.90), ("R2 Kiểm toán 2026 ngoại trừ", 0.35, 0.80),
             ("R3 Khoản thu nhập khác 33,8 tỷ bị đảo", 0.40, 0.45), ("R4 El Niño cắt sản lượng thuỷ điện", 0.50, 0.55),
             ("R5 Lợi nhuận được giữ lại, cổ tức không tăng", 0.60, 0.40), ("R6 Phán quyết vay cá nhân vượt sổ", 0.20, 0.35),
             ("R7 Thanh khoản mỏng (trung vị 0,41 tỷ/phiên)", 0.85, 0.25)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.22, top=0.88, left=0.10, right=0.98)
    ax.axhspan(0.6, 1.0, xmin=0.5, color=ACCENT, alpha=0.08); ax.axvline(0.5, color=LIGHT); ax.axhline(0.6, color=LIGHT)
    for lab, p, im in risks:
        c = ACCENT if im >= 0.6 else (GOLD if im >= 0.4 else GREY)
        ax.scatter(p, im, s=90, color=c, zorder=3)
        ha = "right" if p > 0.7 else "left"
        ax.text(p + (-0.02 if ha == "right" else 0.02), im + 0.035, lab, fontsize=6.6, ha=ha)
    ax.set_xlim(0, 1); ax.set_ylim(0.1, 1.0); ax.set_xlabel("Xác suất xảy ra (ước lượng, khớp mốc M1–M8)", fontsize=8); ax.set_ylabel("Tác động lên giá trị", fontsize=8)
    ax.set_yticks([0.25, 0.5, 0.8]); ax.set_yticklabels(["thấp", "trung bình", "cao"], fontsize=7)
    ax.set_title("Hai rủi ro lớn nhất là pháp lý và ý kiến kiểm toán; cả hai đều có mốc kiểm cụ thể")
    save(fig, "fig_08_risk", "Xác suất/tác động: phán đoán của nhóm nghiên cứu, nhất quán với mốc M1–M8 (không phải đo thống kê).",
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
    items = [("dam", "Thuỷ điện"), ("grid", "Lưới truyền tải"), ("wind", "Điện gió · mặt trời")]
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
