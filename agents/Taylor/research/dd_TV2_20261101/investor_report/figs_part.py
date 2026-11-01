"""Biểu đồ cho báo cáo DD nhà đầu tư TV2 (01/11/2026). Import bởi build_report.py.
Số: ../REPORT_v3.md (đã áp đính chính của người phản biện) + ../calc/valuation_out.txt, ../calc/pe_by_phase_out.txt. Mỗi hình kèm CSV.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 27_000                     # đóng cửa 30/10/2026 (DNSE)
EV = 20_677                     # kỳ vọng 25/50/25 (valuation_out)
BASE = (17_104, 25_324, 21_029)
SCEN = {"Tiêu cực": (9_182, 13_032, 11_033), "Cơ sở": BASE, "Tích cực": (23_843, 35_986, 29_618)}
SRC = "Nguồn: BCTC hợp nhất Q3/2026 (chưa soát xét), BCTC bán niên 2026 (soát xét), dữ liệu tài chính tổng hợp theo quý; tính toán của nhóm nghiên cứu."


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
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 140)), fontsize=6.3, color="#666", ha="left", va="bottom")
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


def figs():
    import numpy as np
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()

    # 00 HERO ----------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.38, 0.92]); axp.axis("off")
    im = crop_to(Image.open(os.path.join(FIGS, "ph_p035_4166.png")).convert("RGB"), 0.38 * 7.2 / (0.92 * 3.3))
    axp.imshow(im, aspect="auto")
    axp.text(0.04, 0.05, "Nhà máy điện sinh khối — ảnh: PECC2 công bố\n(BCTN 2025, mục dự án đầu tư)", transform=axp.transAxes,
             color="white", fontsize=6.0, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.41, 0.50, 0.58, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "27.000 đ"), ("Giá trị kỳ vọng (ước lượng)", "≈20.700 đ"), ("Vùng cơ sở (ước lượng)", "17,1–25,3k"),
            ("LNST mẹ 9T/2026", "162 tỷ"), ("Backlog EPC đã ký", "4 hợp đồng"), ("Tiền + HTM · vay", "2.104 · 153 tỷ")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=12, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=6.3, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.43, 0.17, 0.54, 0.22])
    axv.barh(0, BASE[1] - BASE[0], left=BASE[0], color=LIGHT, height=0.5)
    for lab, (lo, hi, c) in SCEN.items():
        axv.plot(c, 0, "o", color=GREY, ms=5)
        axv.text(c, -0.62, f"{lab} {vn(c/1000,1)}k", ha="center", fontsize=6.4, color="#444")
    axv.plot(EV, 0, "D", color=NAVY, ms=7)
    axv.text(EV, 0.42, "kỳ vọng 20,7k", ha="center", fontsize=7, color=NAVY, weight="bold")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX + 250, 0.42, "giá 27,0k", ha="left", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(8_000, 33_000); axv.set_ylim(-0.9, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    axv.set_xticks(range(10_000, 33_000, 5_000)); axv.set_xticklabels([f"{t//1000}k" for t in range(10_000, 33_000, 5_000)], fontsize=7)
    axv.set_title("Giá cao hơn giá trị kỳ vọng ≈31%, trên đỉnh vùng cơ sở (đ/cp)", fontsize=8, pad=3)
    save(fig, "fig_00_hero", "Nguồn: giá DNSE (đóng cửa 30/10/2026, HOSE); BCTC Q3/2026; tính toán của nhóm nghiên cứu (ước lượng). Ảnh: BCTN 2025 của PECC2.",
         pd.DataFrame({"chi_so": [k for k, _ in kpis], "gia_tri": [v for _, v in kpis]}))
    plt.close(fig)

    # 01 Chu kỳ LNST năm + P/E theo pha --------------------------------------
    yrs = list(range(2014, 2027))
    np_ = [36.3, 57.1, 99.6, 214.5, 224.1, 256.3, 262.2, 271.8, 76.6, 53.0, 64.7, 94.6, 162.2]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.08, right=0.98)
    cols = [GREY] * 3 + [NAVY] * 5 + [ACCENT] * 4 + [GOLD]
    ax.bar([str(y) for y in yrs[:-1]] + ["9T/26"], np_, color=cols, width=0.65)
    for i, v in enumerate(np_):
        ax.text(i, v + 5, vn(v), ha="center", fontsize=7, color="#333")
    ax.add_patch(plt.Rectangle((2.6, 285), 4.8, 32, color=NAVY, alpha=0.10))
    ax.text(5.0, 300, "Đỉnh 2017–21: P/E trung vị 7,45x", ha="center", va="center", fontsize=7, color=NAVY, weight="bold")
    ax.add_patch(plt.Rectangle((7.6, 285), 3.8, 32, color=ACCENT, alpha=0.10))
    ax.text(9.5, 300, "Đáy 2022–25: P/E ≈33x", ha="center", va="center", fontsize=7, color=ACCENT, weight="bold")
    ax.set_ylim(0, 330); ax.set_ylabel("LNST, tỷ đồng", fontsize=8)
    ax.set_title("Lợi nhuận đi theo chu kỳ EPC: 214–272 tỷ khi có hợp đồng, sập ≈70% khi hết")
    save(fig, "fig_01_cycle", "LNST năm = tổng 4 quý (dữ liệu tài chính tổng hợp, khớp BCTC 2026Q3). P/E: trung vị tháng theo pha (n=60 và 48 tháng). 2026: 9 tháng. " + SRC,
         pd.DataFrame({"nam": yrs, "lnst_ty": np_}))
    plt.close(fig)

    # 02 Cơ cấu LNTT -----------------------------------------------------------
    per = ["Q3/25", "Q3/26", "9T/25", "9T/26"]
    core = [5.9, 47.5, 23.2, 76.3]; fin = [3.4, 27.3, 5.7, 85.6]; lk = [4.5, 0.7, 23.9, 31.3]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.08, right=0.98)
    x = np.arange(4); b = np.zeros(4)
    for v, c, lab in ((core, NAVY, "EBIT lõi"), (fin, GOLD, "Tài chính ròng (chủ yếu lãi tiền gửi)"), (lk, GREY, "Lãi liên kết")):
        ax.bar(x, v, bottom=b, color=c, width=0.55, label=lab)
        for i in range(4):
            if v[i] > 8:
                ax.text(i, b[i] + v[i] / 2, vn(v[i], 1), ha="center", va="center", fontsize=7, color="white", weight="bold")
        b += np.array(v)
    ax.set_xticks(x); ax.set_xticklabels(per); ax.set_ylabel("Tỷ đồng", fontsize=8); ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("Lõi đã chiếm 62% LNTT quý 3, nhưng 9 tháng vẫn 44% đến từ lãi trên tiền khách ứng")
    save(fig, "fig_02_pbt_mix", SRC, pd.DataFrame({"ky": per, "ebit_loi": core, "tc_rong": fin, "lien_ket": lk}))
    plt.close(fig)

    # 03 Tiền và float ---------------------------------------------------------
    labs = ["Tiền + HTM", "Vay", "Tiền khách ứng", "Float ròng*", "Tiền ròng thô", "Tiền ròng sau float"]
    vals = [2104.2, -152.8, 2418.6, 2006.2, 1951.4, -55.0]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.11, right=0.98)
    cs = [GREEN, ACCENT, GOLD, GOLD, NAVY, ACCENT]
    ax.bar(labs, vals, color=cs, width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 50 if v > 0 else v - 170, vn(v, 0), ha="center", fontsize=7.5, weight="bold")
    ax.axhline(0, color="#555", lw=0.8); ax.set_ylim(-400, 2750); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.tick_params(axis="x", labelsize=7.4)
    ax.set_title("2.104 tỷ tiền là có thật, nhưng gần như toàn bộ là tiền khách ứng cho hợp đồng EPC")
    save(fig, "fig_03_cash", "*Float ròng = tiền khách ứng − trả trước nhà cung cấp (293,0) − chi phí dở dang (119,5). Số 30/09/2026 (ước lượng cho 2 cột cuối). " + SRC,
         pd.DataFrame({"chi_tieu": labs, "ty_dong": vals}))
    plt.close(fig)

    # 04 Phải thu CMC ----------------------------------------------------------
    d = ["31/12/25", "30/06/26", "30/09/26"]; ar = [208.1, 367.1, 666.4]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.27, top=0.87, left=0.10, right=0.98)
    ax.bar(d, ar, color=[GREY, GREY, ACCENT], width=0.5, label="Phải thu CMC")
    ax.bar(d, [188.6] * 3, bottom=ar, color=LIGHT, width=0.5, label="Đầu tư vào CMC (25%)")
    for i, v in enumerate(ar):
        ax.text(i, v / 2, vn(v, 1), ha="center", va="center", color="white", fontsize=8, weight="bold")
        ax.text(i, v + 188.6 + 15, vn(v + 188.6, 0), ha="center", fontsize=7.5)
    ax.axhline(1331, color=NAVY, ls="--", lw=1); ax.text(2.3, 1345, "VCSH mẹ 1.331", ha="right", fontsize=7, color=NAVY)
    ax.set_ylim(0, 1500); ax.set_ylabel("Tỷ đồng", fontsize=8); ax.legend(fontsize=7, frameon=False, loc="center left", bbox_to_anchor=(0, 0.62))
    ax.set_title("Phơi nhiễm với bên liên quan CMC ≈64% vốn chủ, tăng 299 tỷ chỉ trong quý 3")
    save(fig, "fig_04_cmc", "Phải thu theo thuyết minh giao dịch bên liên quan (TM32); thuyết minh phải thu (TM3) ghi 657,3 tại 30/09 — hai thuyết minh lệch nhau. Chưa trích lập dự phòng. " + SRC,
         pd.DataFrame({"ngay": d, "phai_thu_cmc": ar, "dau_tu_cmc": [188.6] * 3}))
    plt.close(fig)

    # 05 CFO cầu nối --------------------------------------------------------------
    labs = ["CFO 9T báo cáo", "Trừ toàn bộ\ntiền ứng tăng", "Trừ float ròng\ntăng (nhất quán)", "Nếu loại tăng\nphải thu CMC"]
    vals = [858.6, -573.8, -224.8, 233.0]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); fig.subplots_adjust(bottom=0.27, top=0.86, left=0.11, right=0.98)
    ax.bar(labs, vals, color=[GREY, ACCENT, ACCENT, GREEN], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 25 if v > 0 else v - 70, ("+" if v > 0 else "") + vn(v, 0), ha="center", fontsize=8, weight="bold")
    ax.axhline(0, color="#555", lw=0.8); ax.set_ylim(-750, 1000); ax.set_ylabel("Tỷ đồng", fontsize=8); ax.tick_params(axis="x", labelsize=7.4)
    ax.set_title("CFO 9 tháng âm 225–574 tỷ khi bỏ tiền khách ứng; CMC là nguyên nhân chính")
    save(fig, "fig_05_cfo", "Ước lượng: trừ tăng tiền ứng 1.432,4; trừ tăng float ròng 1.083,4; cột cuối = −224,8 + tăng phải thu CMC ≈458 (TM32, làm tròn). " + SRC,
         pd.DataFrame({"buoc": [l.replace("\n", " ") for l in labs], "ty_dong": vals}))
    plt.close(fig)

    # 06 Giá 12 tháng ------------------------------------------------------------
    px = pd.read_csv(os.path.join(CALC, "tv2_px_12m.csv"), parse_dates=["date"])
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.2, top=0.86, left=0.08, right=0.98)
    ax.plot(px.date, px.close * 1000, color=NAVY, lw=1.4)
    ev = [("2026-05-21", "CBTT khởi tố\ncựu lãnh đạo"), ("2026-06-30", "ĐHĐCĐ"), ("2026-09-14", "room ngoại 0%"), ("2026-10-28", "BCTC Q3")]
    for dt, lab in ev:
        t = pd.Timestamp(dt); r = px[px.date >= t].iloc[0]
        ax.plot(t, r.close * 1000, "o", color=ACCENT, ms=5)
        ax.annotate(lab, (t, r.close * 1000), (t, r.close * 1000 + 5200), fontsize=6.6, ha="center", color=ACCENT,
                    arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    ax.axhspan(BASE[0], BASE[1], color=LIGHT, alpha=0.6); ax.axhline(EV, color=NAVY, ls=":", lw=1)
    ax.text(px.date.iloc[3], BASE[0] - 2300, "dải nền = vùng cơ sở 17,1–25,3k · chấm = giá trị kỳ vọng 20,7k", fontsize=6.8, color=NAVY)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_ylim(12_000, 50_000); ax.set_ylabel("đ/cp", fontsize=8)
    ax.set_title("Giá −21,6% từ đầu năm (34.450 xuống 27.000), vẫn trên vùng cơ sở")
    save(fig, "fig_06_price", "Giá đóng cửa (DNSE), 29/09/2025–30/10/2026. Sự kiện: quan sát, không phải quan hệ nhân quả. Tính toán của nhóm nghiên cứu.",
         px[["date", "close"]])
    plt.close(fig)

    # 07 Football field ----------------------------------------------------------
    rows = [("P/E nhóm PECC hiện tại 3,6–7,2x (thanh khoản mỏng)", 9_490, 18_979, GREY),
            ("Ke–P/E 6,2–8,8x (Ke 12,5–13,5%)", 16_300, 23_200, GREY),
            ("P/B hợp lý 0,93–1,12x (ROE 12,7%)", 18_300, 22_100, GREY),
            ("P/E TV2 pha LN đỉnh 7–9x × LN 178 tỷ", 18_500, 23_700, NAVY),
            ("P/E lẫn pha 9–11x (chỉ tham khảo)", 23_700, 29_000, LIGHT),
            ("Kịch bản tiêu cực (25%)", 9_182, 13_032, ACCENT),
            ("Kịch bản cơ sở (50%)", 17_104, 25_324, NAVY),
            ("Kịch bản tích cực (25%)", 23_843, 35_986, GREEN)]
    fig, ax = plt.subplots(figsize=(7.2, 3.3)); fig.subplots_adjust(bottom=0.16, top=0.88, left=0.40, right=0.97)
    for i, (lab, lo, hi, c) in enumerate(rows[::-1]):
        ax.barh(i, hi - lo, left=lo, color=c, height=0.55)
        ax.text(hi + 300, i, f"{vn(lo/1000,1)}–{vn(hi/1000,1)}k", va="center", fontsize=6.8, bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.2)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.6); ax.text(PX, len(rows) - 0.35, "giá 27,0k", color=ACCENT, fontsize=7.2, ha="center", weight="bold")
    ax.axvline(EV, color=NAVY, ls=":", lw=1.4); ax.text(EV, len(rows) - 0.35, "kỳ vọng 20,7k", color=NAVY, fontsize=7.2, ha="center", weight="bold")
    ax.set_xlim(7_000, 40_000); ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xticks(range(10_000, 40_001, 5_000)); ax.set_xticklabels([f"{t//1000}k" for t in range(10_000, 40_001, 5_000)], fontsize=7)
    ax.set_title("Mọi phép đo neo đúng pha đều cho giá trị dưới 27.000; chỉ P/E lẫn pha hoặc kịch bản tích cực vượt", loc="right", fontsize=8.8)
    save(fig, "fig_07_football", "LN 178 tỷ = tâm LNST bình quân 2027–28 kịch bản cơ sở (ước lượng). P/E và P/B lịch sử: dữ liệu giá tháng 2014–10/2026. Tính toán của nhóm nghiên cứu.",
         pd.DataFrame(rows, columns=["phep_do", "thap", "cao", "mau"]).drop(columns="mau"))
    plt.close(fig)

    # 08 Độ nhạy LN × P/E --------------------------------------------------------
    N = 67.526165
    nps = [100, 130, 160, 178, 190, 220, 250]; pes = [6, 7, 7.45, 8, 9, 10]
    m = np.array([[n * p / N for p in pes] for n in nps])
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.12, right=0.98)
    ax.imshow(m < PX / 1000, cmap="RdYlGn_r", alpha=0.0, aspect="auto"); ax.grid(False)
    for i in range(len(nps)):
        for j in range(len(pes)):
            v = m[i, j]; c = "#F4D6CF" if v >= 27 else ("#DCEBE2" if v >= EV / 1000 else "#FFFFFF")
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=c))
            ax.text(j, i, vn(v, 1), ha="center", va="center", fontsize=7.6, weight="bold" if v >= 27 else None)
    ax.set_xticks(range(len(pes))); ax.set_xticklabels([vn(p, 2 if p == 7.45 else 0) + "x" for p in pes])
    ax.set_yticks(range(len(nps))); ax.set_yticklabels([f"{n} tỷ" for n in nps]); ax.set_xlim(-0.5, len(pes) - 0.5); ax.set_ylim(len(nps) - 0.5, -0.5)
    ax.set_xlabel("P/E", fontsize=8); ax.set_ylabel("LNST bền vững 2027–28", fontsize=8)
    ax.set_title("Để biện minh 27.000 cần LN ≈245 tỷ ở 7,45x hoặc ≈203 tỷ ở 9x (nghìn đ/cp; đỏ = ≥ giá)")
    save(fig, "fig_08_sensitivity", "Giá trị/cp = LNST × P/E / 67,53 triệu cp. Xanh nhạt: ≥ giá trị kỳ vọng 20,7k; đỏ nhạt: ≥ giá 27,0k. Tính toán của nhóm nghiên cứu.",
         pd.DataFrame(m, index=nps, columns=pes).reset_index().rename(columns={"index": "lnst"}))
    plt.close(fig)

    # 09 Chuỗi giá trị (sơ đồ minh họa) ----------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.2)); fig.subplots_adjust(0.01, 0.12, 0.99, 0.88); ax.axis("off")
    boxes = [("Tư vấn khảo sát–thiết kế", "nguồn + lưới, gốc EVN\noligopoly 4 công ty PECC", "#5E6B7A"),
             ("Tổng thầu EPC", "Ô Môn IV, 2 eREX, Tân Thuận GĐ3\nđộng lực 2026–28", NAVY),
             ("Vận hành & bảo trì", "48 nhà máy (công ty con)\nLào, Philippines", GREEN),
             ("Đầu tư điện tái tạo", "58,7 MW thuần; liên kết CMC 25%,\nThác Bà 2 45%", GOLD)]
    for i, (t, s, c) in enumerate(boxes):
        x = 0.01 + i * 0.25
        ax.add_patch(plt.Rectangle((x, 0.18), 0.225, 0.68, color=c, alpha=0.95, transform=ax.transAxes))
        ax.text(x + 0.112, 0.70, t, ha="center", va="center", color="white", fontsize=8.6, weight="bold", transform=ax.transAxes)
        ax.text(x + 0.112, 0.40, s, ha="center", va="center", color="white", fontsize=6.9, transform=ax.transAxes)
        if i < 3:
            ax.annotate("", (x + 0.25, 0.52), (x + 0.226, 0.52), xycoords="axes fraction", arrowprops=dict(arrowstyle="-|>", color="#555"))
    ax.set_title("Bốn mảng nối tiếp trong vòng đời một nhà máy điện (sơ đồ minh họa)")
    save(fig, "fig_09_chain", "Minh họa. Nguồn: BCTN 2025, BCQT 6T/2026, biên bản ĐHĐCĐ 2026, EVN 31/01/2026; tính toán của nhóm nghiên cứu.")
    plt.close(fig)

    # 10 Khung ảnh do công ty công bố ---------------------------------------------------
    from PIL import ImageDraw, ImageFont
    items = [("ph_p009_6682.png", "Ký EPC Ô Môn IV, 06/06/2025"), ("ph_p009_1837.png", "Động thổ sinh khối Yên Bái 1"),
             ("ph_p009_1848.png", "Ký EPC điện gió Tân Thuận GĐ3"), ("ph_p029_3498.png", "Trung tâm vận hành & bảo trì")]
    W, H, pad = 1440, 300, 8
    w = (W - pad * 5) // 4
    canvas = Image.new("RGB", (W, H + 60), "white"); dr = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(FONT_B, 16)
    for i, (f, cap) in enumerate(items):
        im = crop_to(Image.open(os.path.join(FIGS, f)).convert("RGB"), w / H).resize((w, H))
        x = pad + i * (w + pad); canvas.paste(im, (x, pad)); dr.rectangle((x, pad, x + w - 1, pad + H - 1), outline="#C9D2DC")
        dr.text((x + 2, H + pad + 8), cap, font=fb, fill=NAVY)
    canvas.save(os.path.join(FIGS, "fig_10_photos.png"))
    pd.DataFrame(items, columns=["file", "chu_thich"]).assign(nguon="BCTN 2025 PECC2 tr.17 (PDF tr.9) và tr.57 (PDF tr.29)").to_csv(os.path.join(FIGS, "fig_10_photos.csv"), index=False)
    print("figs ok")
