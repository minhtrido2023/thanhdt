"""Dựng biểu đồ cho báo cáo DD nhà đầu tư HHS (01/11/2026). Import bởi build_report.py.
Số: ../REPORT.md v2 (đã áp đính chính của người phản biện) + ../calc/valuation_v2_out.txt. Mỗi hình kèm CSV.
Khuôn: ../../dd_TCH_20261031/investor_report/figs_part.py.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 9_450                                    # đóng cửa 30/10/2026 (DNSE latest_trade 14:45:04)
SH = 431.985968
# --- định giá cơ sở chính (cùng tham số giá trị tài sản ròng theo dự án của báo cáo TCH 31/10/2026); khớp ../calc/valuation_v2.py
HHS = 0.5115; KE = 0.1285
CRV_FV = 7726.98 / (1 - HHS); STEP_AT = 2020.76 / 0.20 * 0.8; CRV_COST = CRV_FV - STEP_AT
OTHER = 9152.94 - HHS * CRV_FV - (694.84 - 310.74)
NMTT, VAT, REST = 3099.20, 1.08, 7338.8
pv = lambda y: 1 / (1 + KE) ** y


def crv(m, s):
    return CRV_COST + NMTT / VAT * m * pv(1) + REST * s * pv(4)


def val(c, hd, g, auto):
    return ((HHS * c) * (1 - hd) + OTHER + auto) * (1 - g) / SH * 1000


SCEN = {"Tiêu cực": (val(crv(0.30, 0.15), 0.35, 0.15, 125), 0.30),
        "Cơ sở": (val(crv(0.335, 0.40), 0.25, 0.10, 210), 0.50),
        "Tích cực": (val(crv(0.36, 0.55), 0.15, 0.05, 400), 0.20)}
FV_LO, FV_HI = SCEN["Tiêu cực"][0], SCEN["Tích cực"][0]
FV_C = sum(v * p for v, p in SCEN.values())                                  # 30/50/20
FV_C_SYM = 0.25 * FV_LO + 0.5 * SCEN["Cơ sở"][0] + 0.25 * FV_HI               # 25/50/25
SRC_BCTC = "Nguồn: BCTC hợp nhất 9T/2026 (chưa soát xét), 6T/2026 (soát xét), BCTC 2025 kiểm toán; tính toán của nhóm nghiên cứu."


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
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 135)), fontsize=6.4, color="#666", ha="left", va="bottom")
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
    import json
    import datetime as dt
    import numpy as np
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()
    print("Kịch bản:", {k: round(v) for k, (v, p) in SCEN.items()}, "tâm", round(FV_C), round(FV_C_SYM))

    # 00 HERO -------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.40, 0.92]); axp.axis("off")
    im = crop_to(Image.open(os.path.join(FIGS, "ph_tractor.jpg")).convert("RGB"), 0.40 * 7.2 / (0.92 * 3.3))
    axp.imshow(im, aspect="auto")
    axp.text(0.04, 0.05, "Đầu kéo Dongfeng — ảnh: BCTN 2025 HHS", transform=axp.transAxes,
             color="white", fontsize=6.2, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.43, 0.50, 0.56, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "9.450 đ"), ("Vùng hợp lý (ước lượng)", "7,6–13,0k"), ("LN mẹ Q3/26 · chưa soát xét", "116 tỷ"),
            ("Nợ vay", "0"), ("P/B sổ sách · giá gốc", "0,45x · 0,81x"), ("Sở hữu CRV (lợi ích)", "51,15%")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=12.5 if len(v) < 9 else 10.5, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=6.3, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.45, 0.17, 0.52, 0.22])
    axv.barh(0, FV_HI - FV_LO, left=FV_LO, color=LIGHT, height=0.5)
    for lab, (v, p) in SCEN.items():
        axv.plot(v, 0, "o", color=GREY, ms=5)
        axv.text(v, -0.62, f"{lab} {vn(v/1000,1)}k", ha="center", fontsize=6.4, color="#444")
    axv.axvspan(FV_C, FV_C_SYM, ymin=0.42, ymax=0.66, color=NAVY, alpha=0.85)
    axv.text(FV_C_SYM + 120, 0.42, "tâm ≈10,0–10,2k", ha="left", fontsize=7, color=NAVY, weight="bold")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX - 120, 0.42, "giá 9,45k", ha="right", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(6_800, 14_000); axv.set_ylim(-0.9, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    axv.set_xticks([7_000, 8_000, 9_000, 10_000, 11_000, 12_000, 13_000, 14_000]); axv.set_xticklabels(["7k", "8k", "9k", "10k", "11k", "12k", "13k", "14k"], fontsize=7)
    axv.set_title("Giá TRONG vùng giá trị hợp lý, nửa dưới, thấp hơn tâm ≈5–8% (đ/cp)", fontsize=8, pad=3)
    save(fig, "fig_00_hero", "Nguồn: dữ liệu giao dịch HOSE (giá), BCTC 30/09/2026, giá trị tài sản ròng theo dự án của nhóm nghiên cứu (ước lượng, cùng tham số báo cáo TCH 31/10/2026). Ảnh: BCTN 2025 HHS.",
         pd.DataFrame({"chi_so": [k for k, _ in kpis], "gia_tri": [v for _, v in kpis]}))
    plt.close(fig)

    # 01 DT theo quý theo mảng ---------------------------------------------
    q = ["Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]
    tot = [323.38, 282.72, 244.44, 233.81, 1901.13]
    auto = [246.51, 203.30, 143.78, 203.07, 156.40]
    bds = [t - a for t, a in zip(tot, auto)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(bottom=0.24, top=0.84, left=0.08, right=0.98, wspace=0.25)
    a1.bar(q, auto, color=GREY, width=0.62, label="Ô tô & phụ tùng")
    a1.bar(q, bds, bottom=auto, color=NAVY, width=0.62, label="BĐS & khác")
    for i, t in enumerate(tot):
        a1.text(i, t + 30, vn(t), ha="center", fontsize=7.2, weight="bold" if i == 4 else None)
    a1.set_ylim(0, 2150); a1.legend(fontsize=7, frameon=False, loc="upper left"); a1.set_ylabel("Tỷ đồng", fontsize=8)
    a1.set_title("Doanh thu thuần theo quý (tỷ)", fontsize=8.6)
    seg = ["DT BĐS", "Biên báo cáo", "Biên bỏ PPA"]
    a2.bar([0], [15.6], color=GREY, width=0.55); a2.bar([1], [52.2], color=NAVY, width=0.55); a2.bar([2], [51.9], color=GREEN, width=0.55)
    for i, v in enumerate([15.6, 52.2, 51.9]):
        a2.text(i, v + 1.5, f"{vn(v,1)}%", ha="center", fontsize=8, weight="bold")
    a2.set_xticks([0, 1, 2]); a2.set_xticklabels(["HHS báo cáo", "HHS bỏ phần\nPPA (ước lượng)", "NC-II tại\nTCH (6T)"], fontsize=7)
    a2.set_ylim(0, 62); a2.set_title("Biên gộp BĐS Q3/2026", fontsize=8.6)
    fig.suptitle("Q3/2026: CRV bàn giao đợt đầu New City-II; biên kinh tế ≈52%, biên báo cáo chỉ 15,6% vì PPA", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_01_revenue", "Ô tô Q2/26 suy từ số 6 tháng tới 30/09 của công ty mẹ TCH, Q1/26 = 6T − Q2 (ước suy); BĐS & khác = DT thuần − ô tô. Biên bỏ PPA = (LN gộp 272,4 + thu nhập thuế hoãn lại 127,7/20%)/DT 1.746,2. " + SRC_BCTC,
         pd.DataFrame({"quy": q, "dt_thuan": tot, "o_to": auto, "bds_khac": bds}))
    plt.close(fig)

    # 02 LNST mẹ theo quý + tự lập vs soát xét ---------------------------------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.2, 1]})
    fig.subplots_adjust(bottom=0.24, top=0.82, left=0.08, right=0.98, wspace=0.28)
    qq = ["Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]; me = [17.25, -38.50, 40.17, 3.15, 115.76]
    cols = [GREY, ACCENT, GREY, GOLD, NAVY]
    a1.bar(qq, me, color=cols, width=0.6)
    for i, v in enumerate(me):
        a1.text(i, v + (4 if v >= 0 else -12), vn(v, 1), ha="center", fontsize=7.4, weight="bold" if i == 4 else None)
    a1.axhline(0, color="#555", lw=0.8); a1.set_ylim(-60, 140)
    a1.text(3, 30, "≈3,2 sau\nsoát xét", ha="center", fontsize=6.4, color=GOLD)
    a1.text(4, 130, "chưa soát xét", ha="center", fontsize=6.4, color=NAVY)
    a1.set_title("LNST thuộc cổ đông mẹ theo quý (tỷ)", fontsize=8.6)
    it = ["LNTT", "LNST", "LNST mẹ"]; tl = [101.67, 81.96, 65.51]; sx = [72.04, 62.95, 43.32]
    x = np.arange(3)
    a2.bar(x - 0.19, tl, 0.38, color=LIGHT, label="Tự lập 29/07")
    a2.bar(x + 0.19, sx, 0.38, color=ACCENT, label="Soát xét 27/08")
    for i in range(3):
        a2.text(i - 0.19, tl[i] + 2, vn(tl[i], 1), ha="center", fontsize=6.8)
        a2.text(i + 0.19, sx[i] + 2, vn(sx[i], 1), ha="center", fontsize=6.8, weight="bold", color=ACCENT)
    a2.text(2.2, 78, "−34%", fontsize=9, weight="bold", color=ACCENT, ha="center")
    a2.set_xticks(x); a2.set_xticklabels(it, fontsize=7.5); a2.set_ylim(0, 120); a2.legend(fontsize=6.6, frameon=False, loc="upper right")
    a2.set_title("6T/2026: tự lập vs soát xét (tỷ)", fontsize=8.6)
    fig.suptitle("Lãi Q3 tăng mạnh, nhưng soát xét 6T đã hạ LNST mẹ 34% — Q3 vẫn chưa được soát xét", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_02_npat", "Q2/25 có lãi đánh giá lại 3.488,7 tỷ khi hợp nhất CRV (không vẽ). Q4/25 = năm 2025 − 9T; Q1/26 theo bản tự lập; Q2/26 = 6T soát xét − Q1 tự lập (ước suy); Q3/26 = 9T − 6T soát xét. " + SRC_BCTC,
         pd.DataFrame({"quy": qq, "lnst_me": me}))
    pd.DataFrame({"chi_tieu": it, "tu_lap": tl, "soat_xet": sx}).to_csv(os.path.join(FIGS, "fig_02_review.csv"), index=False)
    plt.close(fig)

    # 03 Sổ sách bóc tách ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.5)); fig.subplots_adjust(bottom=0.26, top=0.84, left=0.24, right=0.97)
    rows = [("Giá 30/10/2026", [(PX, ACCENT, "9.450")]),
            ("Tâm giá trị (ước lượng)", [(FV_C, NAVY, vn(FV_C))]),
            ("Sổ sách VCSH mẹ", [(11_617, GREY, "giá gốc 11.617"), (21_188 - 11_617, GOLD, "thặng dư PPA chưa thực hiện ≈9.570")])]
    for i, (lab, parts) in enumerate(rows):
        left = 0
        for v, c, t in parts:
            ax.barh(i, v, left=left, color=c, height=0.55)
            ax.text(left + v / 2, i, t, ha="center", va="center", fontsize=7.2, color="white", weight="bold")
            left += v
        if i == 2:
            ax.text(left + 150, i, "21.188", va="center", fontsize=7.5, weight="bold")
    ax.set_yticks(range(3)); ax.set_yticklabels([r[0] for r in rows], fontsize=7.8); ax.set_xlim(0, 23_000)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_title("Sổ sách 21.188 đ/cp gồm ≈9.570 đ thặng dư định giá CRV chưa thực hiện")
    save(fig, "fig_03_book", "Thặng dư PPA = thuế hoãn lại phải trả 2.020,8 tỷ / 20% × (1 − 20%) × 51,15% = 4.134 tỷ (ước lượng; gồm HTK và BĐS đầu tư). " + SRC_BCTC,
         pd.DataFrame({"hang": ["gia", "tam", "so_sach_gia_goc", "thang_du_ppa"], "dcp": [PX, round(FV_C), 11617, 21188 - 11617]}))
    plt.close(fig)

    # 04 Mảng xe ----------------------------------------------------------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(bottom=0.24, top=0.82, left=0.08, right=0.98, wspace=0.28)
    qa = ["Q1–Q2/25\n(TB/quý)", "Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]; va = [249.77 / 2, 246.51, 203.30, 143.78, 203.07, 156.40]
    a1.bar(qa, va, color=[GREY, ACCENT, GREY, GREY, GREY, NAVY], width=0.6)
    for i, v in enumerate(va):
        a1.text(i, v + 4, vn(v), ha="center", fontsize=7.2)
    a1.text(1, 268, "nền đột biến", ha="center", fontsize=6.6, color=ACCENT)
    a1.set_ylim(0, 300); a1.tick_params(axis="x", labelsize=6.8); a1.set_title("DT ô tô theo quý (tỷ) · 9T/26 +1,4%", fontsize=8.6)
    lab = ["Tồn kho ô tô", "trong đó xe sát xi", "Phải trả Dongfeng"]; v0 = [317.6, 38.65, 364.01]; v1 = [608.2, 255.42, 305.26]
    y = np.arange(3)[::-1]
    a2.barh(y + 0.18, v0, 0.36, color=LIGHT, label="31/12/2025"); a2.barh(y - 0.18, v1, 0.36, color=[ACCENT, ACCENT, GREY], label="30/09/2026")
    for yi, a_, b_ in zip(y, v0, v1):
        a2.text(b_ + 8, yi - 0.18, vn(b_), va="center", fontsize=7, weight="bold"); a2.text(a_ + 8, yi + 0.18, vn(a_), va="center", fontsize=6.6, color="#777")
    a2.set_yticks(y); a2.set_yticklabels(lab, fontsize=7); a2.set_xlim(0, 760); a2.legend(fontsize=6.5, frameon=False, loc="lower right")
    a2.set_title("Tồn kho ×1,9 (tỷ)", fontsize=8.6)
    fig.suptitle("Mảng xe: doanh số 9T đi ngang, nhưng tồn kho gấp đôi và biên gộp giảm 3–5 điểm %", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_04_trucks", "Q1, Q2/2026 ước suy (xem hình 1). Biên gộp ô tô (BCTC riêng) 9T/25 16,0%, 9T/26 12,5%; chiết khấu thương mại 9T/26 3,9 tỷ. " + SRC_BCTC,
         pd.DataFrame({"quy": [s.replace("\n", " ") for s in qa], "dt_o_to": va}))
    plt.close(fig)

    # 05 Bản đồ: vùng + Hải Phòng ------------------------------------------
    import math
    pts = pd.DataFrame([
        ("Trụ sở HHS · 116 Nguyễn Đức Cảnh", 20.85492, 106.67596, "hq", 0.004, -0.0035),
        ("New City-II + HH1–HH4 (CRV) · 15.011 tỷ", 20.89262, 106.68241, "proj", -0.062, 0.0045),
        ("Lô I.14 Bắc Sông Cấm (CRV/Đại Lộc) · 1.329 tỷ", 20.87740, 106.67800, "proj", -0.058, 0.0045),
        ("Hoàng Huy Commerce H1 (CRV) · thành phẩm 824 tỷ", 20.82977, 106.68587, "done", -0.052, -0.0060),
        ("Pruksa Town, An Đồng (Pruksa VN 90,17%) — xấp xỉ", 20.85313, 106.64054, "done", -0.012, 0.0085)],
        columns=["ten", "lat", "lon", "loai", "dx", "dy"])
    pts.to_csv(os.path.join(FIGS, "fig_05_maps.csv"), index=False)
    fig = plt.figure(figsize=(4.4, 4.6)); ax = fig.add_axes([0.02, 0.1, 0.96, 0.82])
    ax.set_xlim(106.618, 106.735); ax.set_ylim(20.818, 20.905); ax.set_aspect(1 / math.cos(math.radians(20.86)))
    ax.set_facecolor("#F3F6F9"); ax.grid(False); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color("#C9D2DC")
    ax.text(106.690, 20.903, "THỦY NGUYÊN — bờ bắc sông Cấm", fontsize=7, color=GREY, style="italic", va="top")
    ax.text(106.690, 20.821, "LÊ CHÂN", fontsize=7, color=GREY, style="italic")
    for r in pts.itertuples():
        mk = {"hq": ("s", 60, NAVY), "proj": ("*", 190, GOLD), "done": ("o", 70, GREEN)}[r.loai]
        ax.scatter(r.lon, r.lat, marker=mk[0], s=mk[1], c=mk[2], edgecolors="white", linewidths=0.8, zorder=5)
        ax.annotate(r.ten, (r.lon, r.lat), (r.lon + r.dx, r.lat + r.dy), fontsize=6.0, color=NAVY, weight="bold", zorder=6,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5))
    ax.plot([106.622, 106.6316], [20.827, 20.827], color="#333", lw=2); ax.text(106.6268, 20.8282, "1 km", ha="center", fontsize=6.5)
    ax.set_title("Hải Phòng: dự án của nhóm CRV/Pruksa trong bán kính ≈8 km", fontsize=8.4, loc="left")
    fig.text(0.02, 0.02, "Toạ độ: OpenStreetMap Nominatim 31/10–01/11/2026, cấp phố/khu đô thị — không phải ranh dự án.\nSao vàng: đang triển khai; chấm xanh: đã bàn giao/đang bán. Không vẽ sông/đường.", fontsize=5.6, color="#666")
    fig.savefig(os.path.join(FIGS, "map_hp.png"), dpi=200); plt.close(fig)
    r1 = Image.open(os.path.join(FIGS, "map_region.png")).convert("RGB"); r2 = Image.open(os.path.join(FIGS, "map_hp.png")).convert("RGB")
    H = 900
    r1 = r1.resize((int(r1.width * H / r1.height), H)); r2 = r2.resize((int(r2.width * H / r2.height), H))
    can = Image.new("RGB", (r1.width + r2.width + 20, H), "white"); can.paste(r1, (0, 0)); can.paste(r2, (r1.width + 20, 0))
    can.save(os.path.join(FIGS, "fig_05_maps.png"))

    # 06 Cấu trúc ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 62)
    def box(x, y, w, h, t, fc, tc="white", fs=7.2):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="none")); ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc, weight="bold")
    def line(x1, y1, x2, y2, t="", dx=0.8):
        ax.plot([x1, x2], [y1, y2], color=GREY, lw=1.1)
        if t:
            ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2, t, fontsize=6.8, color=ACCENT, weight="bold", va="center")
    box(36, 51, 28, 8, "TCH (HOSE) — công ty mẹ", GREY)
    box(36, 31, 28, 10, "HHS (HOSE)\nVCSH mẹ 9.153 tỷ · 0 vay", NAVY)
    box(2, 31, 28, 10, "Mảng xe tải Dongfeng\nDT 9T 503 tỷ · TS ≈695 tỷ", "#E8EEF5", NAVY, 6.8)
    box(70, 31, 28, 10, "Pruksa VN 90,17%\n(Pruksa Town — NƠXH)", "#E8EEF5", NAVY, 6.8)
    box(36, 9, 28, 11, "CRV (HOSE)\nlợi ích HHS 51,15%\nbiểu quyết 58,53%", NAVY, fs=6.9)
    box(2, 9, 28, 11, "New City-II + HH1–HH4\nH1 Commerce\nLô I.14 (Đại Lộc)", "#E8EEF5", NAVY, 6.6)
    box(70, 9, 28, 11, "Hoàng Giang 99,79%\nHHS Capital 99,996%\n(nắm cổ phần CRV)", "#E8EEF5", NAVY, 6.6)
    line(50, 51, 50, 41, "58,31%"); line(36, 36, 30, 36); line(64, 36, 70, 36); line(50, 31, 50, 20, "51,15%")
    line(36, 14.5, 30, 14.5); line(70, 14.5, 64, 14.5)
    ax.plot([64, 80], [55, 55], color=GREY, lw=1.1, ls="--"); ax.plot([80, 80], [55, 22], color=GREY, lw=1.1, ls="--")
    ax.text(81, 47, "TCH nắm trực tiếp\n38,19% CRV", fontsize=6.3, color="#555")
    ax.text(1, 1.5, "Tiền dự án chỉ lên HHS qua cổ tức CRV; cổ đông thiểu số CRV hưởng 48,85%. Cả nhóm TCH kiểm soát CRV 89,35% kể cả không tính uỷ quyền.", fontsize=6.6, color="#333")
    ax.set_title("Cấu trúc: HHS là tầng giữa — nắm 51,15% CRV (chủ đầu tư New City-II) và mảng xe tải", fontsize=9.2)
    save(fig, "fig_06_structure", "Nguồn: BCTC 30/09/2026 TM1.5 (tỷ lệ), TM22b (TCH 58,31%), TM39 (tài sản bộ phận); BCTN 2025.")
    plt.close(fig)

    # 07 Khung ảnh sản phẩm ------------------------------------------------
    names = [("ph_tractor.jpg", "Đầu kéo Dongfeng — dòng chủ lực,\nnhập khẩu từ Trung Quốc"),
             ("ph_cargo.jpg", "Xe tải thùng Dongfeng\nhạng trung/nặng"),
             ("ph_white.jpg", "Xe tải thùng dài — phân phối\ntoàn quốc qua đại lý"),
             ("ph_intl.jpg", "Đầu kéo International: chủ yếu ở TCH;\nHHS dự kiến mua lại để phân phối"),
             ("ph_nc2.png", "New City-II (CRV), Thủy Nguyên — 50 ha;\nđang bàn giao thấp tầng (phối cảnh)")]
    from PIL import ImageDraw, ImageFont
    fb = ImageFont.truetype(FONT, 22)
    tw, th = 560, 360; cap = 70; pad = 14
    grid = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
    can = Image.new("RGB", (3 * tw + 4 * pad, 2 * (th + cap) + 3 * pad), "white"); dr = ImageDraw.Draw(can)
    for (fn, c), (gx, gy) in zip(names, grid):
        im = crop_to(Image.open(os.path.join(FIGS, fn)).convert("RGB"), tw / th).resize((tw, th))
        x0 = pad + gx * (tw + pad); y0 = pad + gy * (th + cap + pad)
        can.paste(im, (x0, y0)); dr.rectangle([x0, y0, x0 + tw - 1, y0 + th - 1], outline="#C9D2DC")
        dr.multiline_text((x0 + 4, y0 + th + 6), c, font=fb, fill="#1F3A5F", spacing=4)
    x0 = pad + 2 * (tw + pad); y0 = pad + (th + cap + pad)
    dr.multiline_text((x0 + 10, y0 + 30), "Ảnh xe: Báo cáo thường niên 2025 HHS\n(tr.4, 18, 20, 24; ảnh quảng bá).\nẢnh New City-II: BCTN 2025 TCH\n(phối cảnh, không phải hiện trạng).\n\nBCTN tr.12: HHS là đại lý xe tải\nDongfeng; tr.21: kế hoạch mua và\nphân phối xe Navistar của TCH.",
                      font=ImageFont.truetype(FONT, 21), fill="#555", spacing=6)
    can.save(os.path.join(FIGS, "fig_07_products.png"))
    pd.DataFrame({"anh": [n for n, _ in names], "chu_thich": [c.replace("\n", " ") for _, c in names],
                  "nguon": ["BCTN 2025 HHS tr.4", "BCTN 2025 HHS tr.18", "BCTN 2025 HHS tr.24", "BCTN 2025 HHS tr.20", "BCTN 2025 TCH tr.16-18"]}).to_csv(os.path.join(FIGS, "fig_07_products.csv"), index=False)

    # 08 Bảng cân đối --------------------------------------------------------
    it = ["Tiền + tiền gửi (hợp nhất)", "trong đó công ty mẹ", "Người mua trả trước (BĐS)", "Vay"]
    v0 = [3444.7, None, 3530.0, 390.0]; v1 = [1030.6, 171.4, 3142.8, 0]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.27, right=0.97)
    y = np.arange(4)[::-1]
    ax.barh(y + 0.18, [v or 0 for v in v0], 0.36, color=LIGHT, label="01/01/2026")
    ax.barh(y - 0.18, v1, 0.36, color=[NAVY, ACCENT, GOLD, GREEN], label="30/09/2026")
    for yi, a_, b_ in zip(y, v0, v1):
        ax.text(b_ + 40, yi - 0.18, vn(b_, 1) if b_ else "0", va="center", fontsize=7.5, weight="bold")
        if a_:
            ax.text(a_ + 40, yi + 0.18, vn(a_, 1), va="center", fontsize=7, color="#777")
    ax.set_yticks(y); ax.set_yticklabels(it, fontsize=7.8); ax.set_xlim(0, 4300); ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_title("Không còn vay; tiền giảm 2.414 tỷ vì nộp tiền đất I.14 và xây NC-II", loc="right")
    save(fig, "fig_08_balance", "9T/2026: nộp tiền đất ≈1.066 tỷ; tồn kho +1.909 tỷ; trả vay 390 tỷ; CFO −2.110 tỷ. Tiền công ty mẹ 171 tỷ; phần còn lại ở CRV/Đại Lộc. " + SRC_BCTC,
         pd.DataFrame({"khoan": it, "01_01_2026": v0, "30_09_2026": v1}))
    plt.close(fig)

    # 09 Giá 12 tháng ---------------------------------------------------------
    def load(t):
        o = json.load(open(os.path.join(CALC, f"dnse_ohlc_{t}.json")))
        idx = [dt.datetime.fromtimestamp(x, dt.timezone(dt.timedelta(hours=7))).date() for x in o["t"]]
        return pd.Series([c * 1000 for c in o["c"]], index=pd.to_datetime(idx))
    h = load("HHS").loc["2025-10-31":]; tc = load("TCH").loc["2025-10-31":]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.18, top=0.86, left=0.09, right=0.97)
    ax.plot(h.index, h.values, color=NAVY, lw=1.4, label="HHS")
    ax.plot(tc.index, tc / tc.iloc[0] * h.iloc[0], color=GREY, lw=1.0, ls="--", label="TCH quy về cùng gốc")
    ev = [("2026-06-04", "cổ đông lớn mới 5,06%"), ("2026-07-29", "BCTC Q2 tự lập"), ("2026-08-28", "6T soát xét: LN mẹ −34%"), ("2026-10-29", "BCTC Q3")]
    for k, (d, t) in enumerate(ev):
        ts = pd.Timestamp(d); yv = h.asof(ts)
        ax.axvline(ts, color=LIGHT, lw=0.8, zorder=0)
        ax.annotate(t, (ts, yv), (ts, 16600 if k % 2 == 0 else 17900), fontsize=6.5, ha="center", color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.5))
    ax.text(h.index[-1], h.iloc[-1] - 1000, "9.450", fontsize=7.5, ha="center", color=NAVY, weight="bold")
    ax.legend(fontsize=7, frameon=False, loc="lower left"); ax.set_ylabel("đ/cp", fontsize=8); ax.set_ylim(7000, 18800)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    r = h.iloc[-1] / h.iloc[0] - 1
    ax.set_title(f"12 tháng: HHS {vn(r*100,1)}%; đỉnh/đáy 52 tuần 15.600 / 8.580; thanh khoản ≈10,8 tỷ/phiên")
    save(fig, "fig_09_price", "Nguồn: dữ liệu giao dịch HOSE qua DNSE (đóng cửa, chưa điều chỉnh), tới 30/10/2026; sự kiện: CBTT công ty/cổ đông lớn. Quan sát, không phải quan hệ nhân quả.",
         pd.DataFrame({"ngay": h.index.date, "HHS": h.values}))
    plt.close(fig)

    # 10 Football field ----------------------------------------------------
    rows = [("Giá trị tài sản ròng (cơ sở chính) — 3 kịch bản", FV_LO, FV_HI, NAVY), ("Giá trị ròng — tâm (30/50/20 · 25/50/25)", FV_C, FV_C_SYM, NAVY),
            ("Giá trị ròng theo PPA của HHS (tham chiếu)", 8_755, 15_563, GREY),
            ("P/B 0,72–0,98x × sổ sách giá gốc 11.617", 8_364, 11_385, GOLD),
            ("51,15% × VCSH CRV sổ riêng (31/03/2026)", 8_930, 9_020, GREEN)]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.18, top=0.86, left=0.38, right=0.97)
    for i, (lab, lo, hi, c) in enumerate(rows[::-1]):
        ax.barh(i, hi - lo, left=lo, color=c, height=0.5, alpha=0.9)
        if hi - lo > 400:
            ax.text(lo - 100, i, vn(lo), ha="right", va="center", fontsize=7); ax.text(hi + 100, i, vn(hi), ha="left", va="center", fontsize=7)
        elif lo > 9_500:
            ax.text(hi + 100, i, f"{vn(lo)}–{vn(hi)}", ha="left", va="center", fontsize=7)
        else:
            ax.text(lo - 100, i, "≈8.974", ha="right", va="center", fontsize=7)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.4)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.8); ax.text(PX + 80, -0.75, "giá 9.450", color=ACCENT, ha="left", fontsize=7.5, weight="bold"); ax.set_ylim(-1, len(rows) - 0.5)
    ax.set_xlim(6_500, 16_800); ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_title("Mọi phép thử đều ≥ giá; khoảng cách lớn chỉ xuất hiện ở cơ sở PPA", loc="right")
    save(fig, "fig_10_football_field", "Nguồn: tính toán của nhóm nghiên cứu (ước lượng). P/B 0,98x = TCH tự giao dịch (VCSH mẹ); 0,72x = trung vị 15 DN BĐS niêm yết (cơ sở dữ liệu thị trường, chưa truy nguyên cách tính).",
         pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "mau"]).drop(columns="mau"))
    plt.close(fig)

    # 11 Ma trận thặng dư × CK holding ---------------------------------------
    ss = [0.10, 0.25, 0.40, 0.55, 0.70]; hds = [0.15, 0.20, 0.25, 0.30, 0.35]
    M = np.array([[val(crv(0.335, s), hd, 0.10, 210) for hd in hds] for s in ss])
    lab_s = [f"{int(s*100)}% (≈{vn((s+0.08)/(s+0.8)*100,0)}%)" for s in ss]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.18, right=0.97)
    from matplotlib.colors import TwoSlopeNorm
    ax.imshow(M / PX - 1, cmap="RdBu", norm=TwoSlopeNorm(0, -0.25, 0.5), aspect="auto")
    for i in range(5):
        for j in range(5):
            ax.text(j, i, vn(M[i, j]), ha="center", va="center", fontsize=7.5, weight="bold" if (i, j) == (2, 2) else None,
                    color="white" if abs(M[i, j] / PX - 1) > 0.3 else "#1d2731")
    ax.set_xticks(range(5)); ax.set_xticklabels([f"{int(h*100)}%" for h in hds]); ax.set_yticks(range(5)); ax.set_yticklabels(lab_s, fontsize=7.5); ax.grid(False)
    ax.set_xlabel("Chiết khấu holding phần CRV (chiết khấu quản trị giữ 10%)", fontsize=8); ax.set_ylabel("Thặng dư quỹ đất (≈ biên gộp)", fontsize=8)
    ax.set_title("Giá 9.450 đ ngầm định thặng dư quỹ đất ≈20% (biên gộp ≈28%) ở chiết khấu cơ sở")
    save(fig, "fig_11_matrix", "Đ/cp; biên ròng backlog 33,5%; mảng xe 210 tỷ; thặng dư sau thuế s và biên gộp g: s(1−g)=0,8(g−0,1). Biên gộp NC-II lịch sử ≈52% tương ứng s≈70%. Nguồn: tính toán của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame(M.round(0), index=lab_s, columns=[f"ck_{int(h*100)}" for h in hds]).reset_index().rename(columns={"index": "thang_du"}))
    plt.close(fig)

    # 12 Ma trận rủi ro -----------------------------------------------------
    risks = [("R1 Q3 bị điều chỉnh khi kiểm toán", 0.40, 0.40), ("R2 NC-II/I.14 bán chậm, thặng dư thấp", 0.45, 0.75),
             ("R3 CRV không trả cổ tức tiền", 0.50, 0.50), ("R4 Mảng xe giảm giá tồn kho", 0.45, 0.20),
             ("R5 Thanh tra phát sinh nghĩa vụ", 0.30, 0.20), ("R6 Giao dịch nội bộ nhóm bất lợi", 0.25, 0.45),
             ("R7 Xử phạt mới trong nhóm", 0.25, 0.55)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.08, right=0.98)
    ax.axhspan(0.5, 1, xmin=0.5, color="#F6DCD6", zorder=0); ax.axhspan(0, 0.5, xmax=0.5, color="#E3EEE8", zorder=0)
    off = {"R1 Q3 bị điều chỉnh khi kiểm toán": (0.015, -0.055, "left"), "R4 Mảng xe giảm giá tồn kho": (0.015, 0.02, "left"),
           "R5 Thanh tra phát sinh nghĩa vụ": (0.015, -0.055, "left"), "R6 Giao dịch nội bộ nhóm bất lợi": (-0.015, -0.01, "right"),
           "R7 Xử phạt mới trong nhóm": (-0.015, -0.01, "right")}
    for t, p, i in risks:
        ax.scatter(p, i, s=70, color=ACCENT if p * i > 0.2 else NAVY, zorder=3)
        dx, dy, ha = off.get(t, (0.015, 0.02, "left"))
        ax.text(p + dx, i + dy, t, fontsize=6.8, ha=ha)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xlabel("Xác suất (12 tháng, ước lượng)", fontsize=8); ax.set_ylabel("Tác động lên giá trị", fontsize=8)
    ax.set_title("Rủi ro lớn nhất: tốc độ bán quỹ đất CRV và cổ tức từ CRV, không phải nợ vay")
    save(fig, "fig_12_risk_matrix", "Đánh giá định tính của nhóm nghiên cứu (ước lượng), xem bảng rủi ro mục 8.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)
    print("figs done")
