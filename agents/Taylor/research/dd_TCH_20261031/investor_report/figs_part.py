"""Dựng biểu đồ cho báo cáo DD nhà đầu tư TCH (31/10/2026). Import bởi build_report.py.
Số: ../REPORT.md v2 (đã áp đính chính của người phản biện) + ../tính toán của nhóm nghiên cứu. Mỗi hình kèm CSV.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 11_850                                   # đóng cửa 30/10/2026
FV_LO, FV_HI = 10_151, 15_055
FV_C, FV_C_TILT = 12_650, 12_278
SCEN = {"Tiêu cực": (10_151, 0.25), "Cơ sở": (12_697, 0.50), "Tích cực": (15_055, 0.25)}
SRC_BCTC = "Nguồn: BCTC hợp nhất & riêng 01/04–30/09/2026 (chưa soát xét), BCTC FY25 kiểm toán; tính toán của nhóm nghiên cứu."


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
    import numpy as np
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()

    # 00 HERO -------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.40, 0.92]); axp.axis("off")
    im = crop_to(Image.open(os.path.join(FIGS, "ph_nc2.png")).convert("RGB"), 0.40 * 7.2 / (0.92 * 3.3))
    axp.imshow(im, aspect="auto")
    axp.text(0.04, 0.05, "New City-II, Thủy Nguyên — phối cảnh,\nảnh: Hoàng Huy công bố (BCTN 2025)", transform=axp.transAxes,
             color="white", fontsize=6.2, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.43, 0.50, 0.56, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "11.850 đ"), ("Vùng hợp lý (ước lượng)", "10,2–15,1k"), ("LNST mẹ Q3/26 (×13 cùng kỳ)", "538 tỷ"),
            ("Nợ vay · trái phiếu", "0 · 0"), ("P/B (VCSH mẹ)", "0,98x"), ("ROE mẹ chuẩn hoá", "5,6–6,4%")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=12.5, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=6.3, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.45, 0.17, 0.52, 0.22])
    axv.barh(0, FV_HI - FV_LO, left=FV_LO, color=LIGHT, height=0.5)
    for lab, (v, p) in SCEN.items():
        axv.plot(v, 0, "o", color=GREY, ms=5)
        axv.text(v, -0.62, f"{lab} {vn(v/1000,1)}k", ha="left" if lab == "Cơ sở" else "center", fontsize=6.4, color="#444")
    axv.axvspan(FV_C_TILT, FV_C, ymin=0.42, ymax=0.66, color=NAVY, alpha=0.85)
    axv.text(FV_C + 120, 0.42, "tâm 12,3–12,7k", ha="left", fontsize=7, color=NAVY, weight="bold")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX - 120, 0.42, "giá 11,85k", ha="right", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(9_300, 15_800); axv.set_ylim(-0.9, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    axv.set_xticks([10_000, 11_000, 12_000, 13_000, 14_000, 15_000]); axv.set_xticklabels(["10k", "11k", "12k", "13k", "14k", "15k"], fontsize=7)
    axv.set_title("Giá nằm TRONG vùng giá trị hợp lý, ở nửa dưới (NAV dự án, đ/cp)", fontsize=8, pad=3)
    save(fig, "fig_00_hero", "Nguồn: dữ liệu giao dịch HOSE (giá), BCTC 30/09/2026, tính toán NAV của nhóm nghiên cứu (ước lượng). Ảnh: Hoàng Huy công bố (phối cảnh).",
         pd.DataFrame({"chi_so": [k for k, _ in kpis], "gia_tri": [v for _, v in kpis]}))
    plt.close(fig)

    # 01 DT & biên gộp theo quý ------------------------------------------
    q = ["Q2/24", "Q3/24", "Q4/24", "Q1/25", "Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]
    rev = [828.4, 1418.8, 1561.0, 858.8, 390.4, 345.9, 317.0, 394.1, 453.5, 1958.2]
    gm = [None, None, None, None, 28.9, 25.9, None, None, 31.1, 48.8]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.09, right=0.92)
    cols = [GREY] * 9 + [NAVY]
    ax.bar(q, rev, color=cols, width=0.62)
    for i, v in enumerate(rev):
        ax.text(i, v + 25, vn(v), ha="center", fontsize=7, color="#333")
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    xs = [i for i, g in enumerate(gm) if g is not None]
    ax2.plot(xs, [gm[i] for i in xs], "o", color=ACCENT, ms=6)
    for i in xs:
        ax2.text(i - 0.1 if i == 9 else i + 0.12, gm[i] + 3 if i == 9 else gm[i] + 1.5, f"{vn(gm[i],1)}%", color=ACCENT, fontsize=7.5, weight="bold")
    ax2.set_ylim(0, 60); ax2.set_ylabel("Biên gộp %", color=ACCENT, fontsize=8)
    ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.set_title("Doanh thu quý 7–9/2026 gấp 5,7 lần cùng kỳ nhờ đợt bàn giao đầu tiên của New City-II")
    save(fig, "fig_01_revenue_margin", "Quý dương lịch (niên độ TCH kết thúc 31/3: Q3/26 = Q2 năm tài chính 2026). DT: dữ liệu tài chính tổng hợp (DT gộp) tới Q2/26, Q3/26 = DT thuần BCTC. Biên gộp chỉ có ở quý có BCTC đọc được. " + SRC_BCTC,
         pd.DataFrame({"quy": q, "doanh_thu_ty": rev, "bien_gop_pct": gm}))
    plt.close(fig)

    # 02 LNST HN vs mẹ ----------------------------------------------------
    qq = ["Q2/25", "Q3/25", "Q2/26", "Q3/26"]
    hn = [56.2, 56.3, 163.8, 750.5]; me = [37.9, 40.2, 125.4, 537.7]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.09, right=0.98)
    x = np.arange(4)
    ax.bar(x - 0.18, hn, 0.36, color=GREY, label="LNST hợp nhất")
    ax.bar(x + 0.18, me, 0.36, color=NAVY, label="LNST thuộc cổ đông mẹ")
    for i in range(4):
        ax.text(i - 0.18, hn[i] + 12, vn(hn[i]), ha="center", fontsize=7.5, color="#444")
        ax.text(i + 0.18, me[i] + 12, vn(me[i]), ha="center", fontsize=7.5, color=NAVY, weight="bold")
    ax.text(2.45, 560, "Q3/26: 28% lợi nhuận\nthuộc cổ đông thiểu số CRV", ha="center", fontsize=7, color=ACCENT)
    ax.set_xticks(x); ax.set_xticklabels(qq); ax.set_ylabel("Tỷ đồng", fontsize=8); ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Lợi nhuận thuộc cổ đông mẹ là 538 tỷ, không phải 750 tỷ")
    save(fig, "fig_02_npat", "Q2/25 = 6T FY25 − Q2FY25; Q2/26 = 6T FY26 − Q2FY26 (BCTC hợp nhất). " + SRC_BCTC,
         pd.DataFrame({"quy": qq, "lnst_hop_nhat": hn, "lnst_me": me}))
    plt.close(fig)

    # 03 NMTT theo dự án + ΔNMTT -------------------------------------------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})
    fig.subplots_adjust(bottom=0.25, top=0.84, left=0.08, right=0.98, wspace=0.28)
    dates = ["31/03/26", "30/06/26", "30/09/26"]
    d = {"New City-II (CRV)": [3905.89, 4132.23, 3099.20], "Green River (mẹ)": [1693.27, 1779.69, 1837.75],
         "H2 (mẹ)": [458.70, 521.61, 617.83], "Khác": [6124.75 - 3905.89 - 1693.27 - 458.70, 6492.49 - 4132.23 - 1779.69 - 521.61, 5599.82 - 3099.20 - 1837.75 - 617.83]}
    bot = np.zeros(3); cs = [NAVY, GREEN, GOLD, GREY]
    for (k, v), c in zip(d.items(), cs):
        a1.bar(dates, v, bottom=bot, color=c, width=0.6, label=k); bot += np.array(v)
    for i, t in enumerate(bot):
        a1.text(i, t + 80, vn(t), ha="center", fontsize=7.5, weight="bold")
    a1.set_ylim(0, 9000); a1.legend(fontsize=6.3, frameon=False, ncol=2, loc="upper left")
    a1.set_title("Người mua trả tiền trước (tỷ)", fontsize=8.6)
    dq = ["Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]; dv = [2643, None, 775, 368, -893]
    for i, v in enumerate(dv):
        if v is None:
            a2.text(i, 120, "chưa có\nsố", ha="center", fontsize=6.5, color="#888"); continue
        a2.bar(i, v, color=GREEN if v > 0 else ACCENT, width=0.6)
        a2.text(i, v + 70 if v > 0 else v / 2, vn(v), ha="center", va="bottom" if v > 0 else "center", fontsize=7.5, weight="bold", color=GREEN if v > 0 else "white")
    a2.set_xticks(range(5)); a2.set_xticklabels(dq, fontsize=7.5); a2.axhline(0, color="#555", lw=0.8)
    a2.set_title("Thay đổi NMTT theo quý (tỷ)", fontsize=8.6)
    fig.suptitle("Backlog đang tiêu nhanh hơn bổ sung: NMTT âm lần đầu, New City-II −1.033 tỷ trong một quý", x=0.01, ha="left", fontsize=9.8, weight="bold", color="#1d2731")
    save(fig, "fig_03_nmtt", "NMTT = người mua trả tiền trước (TM16). Thay đổi Q3/25, Q1/26, Q2/26 theo báo cáo bên bán 08/2026 (SHS); Q3/26 tính từ BCTC Q1/Q2 FY26; Q4/25 chưa có số. Quý dương lịch. " + SRC_BCTC,
         pd.DataFrame({"ngay": dates, **{k: v for k, v in d.items()}}))
    pd.DataFrame({"quy": dq, "delta_nmtt": dv}).to_csv(os.path.join(FIGS, "fig_03_nmtt_delta.csv"), index=False)
    plt.close(fig)

    # 04 HTK theo dự án ----------------------------------------------------
    pj = ["New City-II (CRV)", "Green River (mẹ)", "150 Tô Hiệu (mẹ)", "Lô I.14 (CRV/Đại Lộc)", "H2 Commerce (mẹ)", "TP & khác"]
    a = [7230.42, 2995.59, 4.40, 0.0, 512.78, 14630.92 - 7390.37 - 3317.07 - 1677.51 - 1328.75 - 555.53]
    b = [7390.37, 3317.07, 1677.51, 1328.75, 555.53, 14630.92 - 7390.37 - 3317.07 - 1677.51 - 1328.75 - 555.53]
    a[5] = 11115.85 - 7230.42 - 2995.59 - 4.40 - 512.78
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.16, top=0.86, left=0.24, right=0.97)
    y = np.arange(len(pj))[::-1]
    ax.barh(y + 0.18, a, 0.36, color=LIGHT, label="31/03/2026")
    ax.barh(y - 0.18, b, 0.36, color=[NAVY, NAVY, ACCENT, ACCENT, NAVY, GREY], label="30/09/2026")
    for yi, v, v0 in zip(y, b, a):
        ax.text(v + 60, yi - 0.18, vn(v) + (f"  (+{vn(v - v0)})" if v - v0 > 1000 else ""), va="center", fontsize=7.2,
                weight="bold" if v - v0 > 1000 else None, color=ACCENT if v - v0 > 1000 else "#333")
    ax.set_yticks(y); ax.set_yticklabels(pj, fontsize=7.8); ax.set_xlim(0, 9300); ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_title("HTK BĐS +3.515 tỷ: gần trọn là 2.993 tỷ tiền đất 2 quỹ đất mới", loc="right")
    save(fig, "fig_04_inventory", "HTK BĐS gồm chi phí dở dang + thành phẩm (TM9(*) hợp nhất; pháp nhân theo TM9 BCTC riêng). Tiền SDĐ đã nộp 6T: TM17. " + SRC_BCTC,
         pd.DataFrame({"du_an": pj, "htk_31_03_2026": a, "htk_30_09_2026": b}))
    plt.close(fig)

    # 05 Bản đồ: vùng + Hải Phòng (tự vẽ, không vẽ sông) --------------------
    pts = pd.DataFrame([
        ("Trụ sở 116 Nguyễn Đức Cảnh", 20.85492, 106.67596, "hq", -0.0345, 0.0005),
        ("150 Tô Hiệu (mẹ) · HTK 1.678 tỷ", 20.85117, 106.68070, "proj", 0.004, -0.0045),
        ("H2 Commerce (mẹ) · 556 tỷ", 20.82977, 106.68587, "proj", 0.004, -0.002),
        ("New City-II + HH1–HH4 (CRV) · 7.390 tỷ", 20.89262, 106.68241, "proj", 0.004, 0.0035),
        ("Green River (mẹ) · 3.317 tỷ — vị trí xấp xỉ", 20.89273, 106.66566, "proj", -0.040, -0.0055),
        ("Lô I.14 Bắc Sông Cấm (Đại Lộc) · 1.329 tỷ", 20.87740, 106.67800, "proj", 0.004, -0.0005)],
        columns=["ten", "lat", "lon", "loai", "dx", "dy"])
    pts.to_csv(os.path.join(FIGS, "fig_05_maps.csv"), index=False)
    import math
    fig = plt.figure(figsize=(4.4, 4.6)); ax = fig.add_axes([0.02, 0.1, 0.96, 0.82])
    ax.set_xlim(106.625, 106.735); ax.set_ylim(20.818, 20.905); ax.set_aspect(1 / math.cos(math.radians(20.86)))
    ax.set_facecolor("#F3F6F9"); ax.grid(False); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color("#C9D2DC")
    ax.text(106.629, 20.901, "THỦY NGUYÊN — bờ bắc sông Cấm", fontsize=7, color=GREY, style="italic", va="top")
    ax.text(106.629, 20.821, "LÊ CHÂN — trung tâm cũ", fontsize=7, color=GREY, style="italic")
    for r in pts.itertuples():
        ax.scatter(r.lon, r.lat, marker="s" if r.loai == "hq" else "*", s=60 if r.loai == "hq" else 190,
                   c=NAVY if r.loai == "hq" else GOLD, edgecolors="white", linewidths=0.8, zorder=5)
        ax.annotate(r.ten, (r.lon, r.lat), (r.lon + r.dx, r.lat + r.dy), fontsize=6.3, color=NAVY, weight="bold", zorder=6,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5))
    ax.plot([106.629, 106.6386], [20.827, 20.827], color="#333", lw=2); ax.text(106.6338, 20.8282, "1 km", ha="center", fontsize=6.5)
    ax.set_title("Hải Phòng: 5 dự án trong bán kính ~8 km", fontsize=8.6, loc="left")
    fig.text(0.02, 0.02, "Toạ độ: OpenStreetMap Nominatim 31/10/2026, cấp phố/khu đô thị — không phải ranh dự án.\nKhông vẽ sông/đường (không có dữ liệu vector).", fontsize=5.6, color="#666")
    fig.savefig(os.path.join(FIGS, "map_hp.png"), dpi=200); plt.close(fig)
    r1 = Image.open(os.path.join(FIGS, "map_region.png")).convert("RGB"); r2 = Image.open(os.path.join(FIGS, "map_hp.png")).convert("RGB")
    H = 900
    r1 = r1.resize((int(r1.width * H / r1.height), H)); r2 = r2.resize((int(r2.width * H / r2.height), H))
    can = Image.new("RGB", (r1.width + r2.width + 20, H), "white"); can.paste(r1, (0, 0)); can.paste(r2, (r1.width + 20, 0))
    can.save(os.path.join(FIGS, "fig_05_maps.png"))

    # 06 Cấu trúc tập đoàn / dự án -----------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 60)
    def box(x, y, w, h, t, fc, tc="white", fs=7.4):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="none")); ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc, weight="bold")
    def line(x1, y1, x2, y2, t=""):
        ax.plot([x1, x2], [y1, y2], color=GREY, lw=1.1)
        if t:
            ax.text((x1 + x2) / 2 + 0.8, (y1 + y2) / 2, t, fontsize=7, color=ACCENT, weight="bold", va="center")
    box(36, 48, 28, 9, "TCH — công ty mẹ\nVCSH mẹ 12.159 tỷ · 0 vay", NAVY)
    box(2, 26, 30, 11, "Dự án 100% của mẹ\nGreen River · H2 Commerce · 150 Tô Hiệu\nHTK 5.552 tỷ · NMTT 2.457 tỷ", "#E8EEF5", NAVY, 6.8)
    box(36, 26, 28, 11, "CRV (HOSE)\nlợi ích 68,02%\nbiểu quyết 96,72%", NAVY, fs=7)
    box(68, 26, 30, 11, "HHS (HOSE) — ô tô\n58,31% · phân phối xe đầu kéo\nInternational", GREY, fs=6.8)
    box(30, 6, 22, 10, "New City-II + HH1–HH4\nHTK 7.390 · NMTT 3.099", "#E8EEF5", NAVY, 6.8)
    box(55, 6, 22, 10, "Lô I.14 (Đại Lộc)\nHTK 1.329 · đất giao 07/2026", "#E8EEF5", NAVY, 6.8)
    line(50, 48, 17, 37); line(50, 48, 50, 37); line(50, 48, 83, 37)
    line(50, 26, 41, 16); line(50, 26, 66, 16)
    line(68, 30, 64, 30)
    ax.text(83, 22.5, "HHS nắm 35,26% CRV", fontsize=6.3, color="#555", ha="center")
    ax.text(1, 1, "Lợi nhuận dự án của mẹ về thẳng cổ đông TCH; lợi nhuận NC-II/I.14 về TCH 68,02% qua cổ tức CRV.", fontsize=6.8, color="#333")
    ax.set_title("Cấu trúc: dự án Green River/H2/150 Tô Hiệu thuộc công ty mẹ; NC-II và I.14 nằm ở CRV", fontsize=9.4)
    save(fig, "fig_06_structure", "Nguồn: BCTC 30/09/2026 TM1.5 (tỷ lệ), TM9 hợp nhất & riêng (HTK), TM16 (NMTT); BCTN 2025 tr.16–18 (pháp nhân thực hiện dự án).")
    plt.close(fig)

    # 07 Khung ảnh dự án ---------------------------------------------------
    names = [("ph_nc2.png", "New City-II (CRV) — 50 ha, TMĐT 15.076 tỷ;\nđang bàn giao thấp tầng"),
             ("ph_green_river.png", "Green River (mẹ) — 32,5 ha, TMĐT 4.050 tỷ;\nliền kề/biệt thự ven sông"),
             ("ph_h2.png", "H2 Commerce (mẹ) — 36 tầng, TMĐT 2.199 tỷ;\nđang thi công thân, hạn Q4/2027"),
             ("ph_tohieu.png", "150 Tô Hiệu (mẹ) — 1,62 ha, TMĐT 3.179 tỷ;\nvừa nộp tiền đất, bắt đầu thi công"),
             ("ph_i14.png", "Lô I.14 (Đại Lộc) — 3,25 ha, TMĐT 6.223 tỷ;\nđất giao 23/07/2026")]
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
    dr.multiline_text((x0 + 10, y0 + 40), "Ảnh: Hoàng Huy công bố (phối cảnh),\nBáo cáo thường niên 2025 tr.16–18.\n\nQuy mô, tổng mức đầu tư (TMĐT):\nBCTN 2025. Không phải ảnh hiện trạng.",
                      font=ImageFont.truetype(FONT, 21), fill="#555", spacing=6)
    can.save(os.path.join(FIGS, "fig_07_projects.png"))
    pd.DataFrame({"anh": [n for n, _ in names], "chu_thich": [c.replace("\n", " ") for _, c in names],
                  "nguon": "BCTN 2025 TCH tr.16-18 (pymupdf extract_image)"}).to_csv(os.path.join(FIGS, "fig_07_projects.csv"), index=False)

    # 08 CFO vs LNST -------------------------------------------------------
    per = ["FY24", "FY25", "6T FY26"]; cfo = [1467.7, 2030.0, -3078.5]; np_ = [1121.5, 259.2, 914.3]
    land = [0, 0, -2992.9]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.2, top=0.86, left=0.08, right=0.98)
    x = np.arange(3)
    ax.bar(x - 0.2, np_, 0.38, color=GREY, label="LNST hợp nhất")
    ax.bar(x + 0.2, cfo, 0.38, color=[NAVY, NAVY, ACCENT], label="CFO")
    for i in range(3):
        ax.text(i - 0.2, np_[i] + 60, vn(np_[i]), ha="center", fontsize=7.5)
        ax.text(i + 0.2, cfo[i] + (60 if cfo[i] > 0 else -260), vn(cfo[i]), ha="center", fontsize=7.5, weight="bold", color=NAVY if cfo[i] > 0 else ACCENT)
    ax.text(1.95, -1500, "trong đó tiền đất\n2 quỹ đất mới −2.993", ha="right", fontsize=7, color=ACCENT, weight="bold")
    ax.axhline(0, color="#555", lw=0.8); ax.set_xticks(x); ax.set_xticklabels(per); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.legend(fontsize=7.5, frameon=False, loc="lower left"); ax.set_ylim(-3500, 2600)
    ax.set_title("CFO 6T âm 3.079 tỷ gần như toàn bộ vì nộp tiền đất; bỏ khoản này CFO lõi xấp xỉ 0 đến dương")
    save(fig, "fig_08_cashflow", "LNST HN FY24, FY25: BCTC FY25 kiểm toán (cột so sánh); 6T FY26 BCTC chưa soát xét. CFO: LCTT. " + SRC_BCTC,
         pd.DataFrame({"ky": per, "lnst_hn": np_, "cfo": cfo, "tien_sdd": land}))
    plt.close(fig)

    # 09 Tiền/HTM/NMTT/nợ --------------------------------------------------
    it = ["Tiền + HTM", "NMTT (nghĩa vụ giao nhà)", "Phải trả NB/khác (TM36)", "Vay + trái phiếu"]
    v0 = [6206.6, 6124.75, None, 0]; v1 = [3296.3, 5599.82, 1086.8, 0]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.27, right=0.97)
    y = np.arange(4)[::-1]
    ax.barh(y + 0.18, [v or 0 for v in v0], 0.36, color=LIGHT, label="31/03/2026")
    ax.barh(y - 0.18, v1, 0.36, color=[NAVY, GOLD, GREY, GREEN], label="30/09/2026")
    for yi, a_, b_ in zip(y, v0, v1):
        ax.text(b_ + 60, yi - 0.18, vn(b_) if b_ else "0", va="center", fontsize=7.5, weight="bold")
        if a_:
            ax.text(a_ + 60, yi + 0.18, vn(a_), va="center", fontsize=7, color="#777")
    ax.set_yticks(y); ax.set_yticklabels(it, fontsize=7.8); ax.set_xlim(0, 7300); ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_title("Không vay; còn 3.296 tỷ tiền + HTM sau khi chi ~3.000 tỷ mua đất", loc="right")
    save(fig, "fig_09_balance", "Tiền + HTM gồm HTM dài hạn 57,8. Phần mẹ = tiền mẹ 2.244 + 68% phần công ty con (ước lượng). " + SRC_BCTC,
         pd.DataFrame({"khoan": it, "31_03_2026": v0, "30_09_2026": v1}))
    plt.close(fig)

    # 10 Số cổ phiếu -------------------------------------------------------
    yrs = ["2021", "2022", "2023", "2024", "2025", "2026"]; sh = [399.2, 618.7, 668.2, 868.7, 912.1, 1003.3]
    fig, ax = plt.subplots(figsize=(7.2, 2.4)); fig.subplots_adjust(bottom=0.2, top=0.84, left=0.08, right=0.98)
    ax.bar(yrs, sh, color=[GREY] * 5 + [NAVY], width=0.6)
    for i, v in enumerate(sh):
        ax.text(i, v + 15, vn(v, 1), ha="center", fontsize=7.5)
    ax.text(3, 960, "phát hành 200 tr cp ở mệnh giá (2025)", ha="center", fontsize=7, color=ACCENT)
    ax.text(5, 1110, "thưởng 10:1", ha="center", fontsize=7, color=ACCENT)
    ax.set_ylim(0, 1250); ax.set_ylabel("Triệu cp", fontsize=8)
    ax.set_title("Số cổ phiếu ×2,5 trong 5 năm: EPS từ 1.219 đ (FY24) còn ~793 đ (TTM)")
    save(fig, "fig_10_shares", "Nguồn: dữ liệu tài chính tổng hợp (số cổ phiếu) (2021–2025), BCTC 30/09/2026 TM21 (1.003,31 tr cp, không có cp quỹ).",
         pd.DataFrame({"nam": yrs, "trieu_cp": sh}))
    plt.close(fig)

    # 11 Giá 12 tháng + sự kiện ---------------------------------------------
    px = pd.read_csv(os.path.join(CALC, "bq_tch_daily.csv"), parse_dates=["time"]).set_index("time").loc["2025-10-31":]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.18, top=0.86, left=0.08, right=0.97)
    ax.plot(px.index, px.Close, color=NAVY, lw=1.4, label="TCH (giá điều chỉnh)")
    vni = px.VNINDEX / px.VNINDEX.iloc[0] * px.Close.iloc[0]
    ax.plot(px.index, vni, color=GREY, lw=1.0, ls="--", label="VN-Index quy về cùng gốc")
    ev = [("2026-04-07", "CBTT QĐ thuế"), ("2026-04-29", "đỉnh 16.500"), ("2026-06-15", "Dragon <5%"),
          ("2026-07-29", "BCTC Q1 FY26"), ("2026-09-10", "cp thưởng xong"), ("2026-10-29", "BCTC Q2 FY26")]
    for k, (dt, t) in enumerate(ev):
        dts = pd.Timestamp(dt); yv = px.Close.asof(dts)
        ax.axvline(dts, color=LIGHT, lw=0.8, zorder=0)
        ax.annotate(t, (dts, yv), (dts, yv + (1700 if k % 2 == 0 else 3300)), fontsize=6.6, ha="center", color=ACCENT,
                    arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.5))
    ax.text(px.index[-1], px.Close.iloc[-1] - 1100, "11.850", fontsize=7.5, ha="center", color=NAVY, weight="bold")
    ax.legend(fontsize=7, frameon=False, loc="upper right"); ax.set_ylabel("đ/cp", fontsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    r1y = px.Close.iloc[-1] / px.Close.iloc[0] - 1; rv = px.VNINDEX.iloc[-1] / px.VNINDEX.iloc[0] - 1
    ax.set_title(f"12 tháng: TCH {vn(r1y*100,1)}% so VN-Index {'+' if rv > 0 else ''}{vn(rv*100,1)}%; phiên sau BCTC Q2 giảm 2,9%")
    save(fig, "fig_11_price", "Nguồn: dữ liệu giao dịch HOSE (giá đóng cửa điều chỉnh cổ phiếu thưởng), tới 30/10/2026; sự kiện: CBTT công ty/cổ đông lớn.",
         px.reset_index()[["time", "Close", "VNINDEX"]])
    plt.close(fig)

    # 12 Football field ----------------------------------------------------
    rows = [("NAV dự án — 3 kịch bản", 10_151, 15_055, NAVY), ("NAV — tâm (trọng số / nghiêng đọc ngành)", 12_278, 12_650, NAVY),
            ("SOTP hỗn hợp (sổ sách + HHS giá thị trường)", 11_196, 11_444, GREEN),
            ("P/B 0,72–0,86x cùng cơ sở dữ liệu thị trường", 9_479, 11_322, GOLD),
            ("P/E 10–16x × EPS chuẩn hoá 675–775", 6_750, 12_400, GREY)]
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.18, top=0.86, left=0.38, right=0.97)
    for i, (lab, lo, hi, c) in enumerate(rows[::-1]):
        ax.barh(i, hi - lo, left=lo, color=c, height=0.5, alpha=0.9)
        ax.text(lo - 120, i, vn(lo), ha="right", va="center", fontsize=7); ax.text(hi + 120, i, vn(hi), ha="left", va="center", fontsize=7)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.6)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.8); ax.text(PX + 100, -0.75, "giá 11.850", color=ACCENT, ha="left", fontsize=7.5, weight="bold"); ax.set_ylim(-1, len(rows) - 0.5)
    ax.set_xlim(5_500, 16_500); ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_title("Bội số/sổ sách thấp hơn NAV dự án: chưa cộng thặng dư quỹ đất", loc="right")
    save(fig, "fig_12_football_field", "Nguồn: tính toán của nhóm nghiên cứu (ước lượng). P/B peer: trung vị 15 DN BĐS niêm yết 0,72x, nhóm khá 0,86x, nhân giá trị sổ/cp 13.165 đ theo cùng cơ sở dữ liệu.",
         pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "mau"]).drop(columns="mau"))
    plt.close(fig)

    # 13 Ma trận thặng dư × chiết khấu -------------------------------------
    s = ["10% (~20%)", "25% (~31%)", "40% (~40%)", "55% (~47%)", "70% (~52%)"]
    ck = ["0%", "10%", "15%", "20%", "25%", "30%"]
    M = np.array([[13928, 12535, 11839, 11142, 10446, 9749], [14824, 13342, 12600, 11859, 11118, 10377],
                  [15720, 14148, 13362, 12576, 11790, 11004], [16616, 14955, 14124, 13293, 12462, 11631],
                  [17513, 15761, 14886, 14010, 13134, 12259]])
    imp = ["14,9%", "20,1%", "24,6%", "28,7%", "32,3%"]
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); fig.subplots_adjust(bottom=0.26, top=0.84, left=0.17, right=0.84)
    from matplotlib.colors import TwoSlopeNorm
    ax.imshow(M / PX - 1, cmap="RdBu", norm=TwoSlopeNorm(0, -0.25, 0.5), aspect="auto")
    for i in range(5):
        for j in range(6):
            ax.text(j, i, vn(M[i, j]), ha="center", va="center", fontsize=7.3, weight="bold" if (i, j) == (2, 3) else None,
                    color="white" if abs(M[i, j] / PX - 1) > 0.3 else "#1d2731")
        ax.text(6.0, i, imp[i], ha="left", va="center", fontsize=7.5, color=ACCENT, weight="bold")
    ax.text(6.0, 4.85, "CK ngầm\nđịnh\ntrong giá", fontsize=6.6, color=ACCENT, va="top")
    ax.set_xticks(range(6)); ax.set_xticklabels(ck); ax.set_yticks(range(5)); ax.set_yticklabels(s, fontsize=7.5); ax.grid(False)
    ax.set_xlabel("Chiết khấu tổng hiệu dụng so NAV dự án", fontsize=8); ax.set_ylabel("Thặng dư quỹ đất (≈ biên gộp)", fontsize=8)
    ax.set_title("Giá 11.850 đ ngầm định chiết khấu ~20–29% so NAV dự án (thặng dư 25–55%)")
    save(fig, "fig_13_matrix", "Đ/cp; biên ròng backlog 33,5%; thặng dư sau thuế s và biên gộp g liên hệ qua s(1−g)=0,8(g−0,1); biên gộp BĐS lịch sử 51,9% tương ứng s≈70%. Nguồn: tính toán của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame(M, index=s, columns=ck).reset_index().rename(columns={"index": "thang_du"}))
    plt.close(fig)

    # 14 Ma trận rủi ro -----------------------------------------------------
    risks = [("R1 Bán mới HH1–HH4 chậm, backlog cạn", 0.55, 0.85), ("R2 Biên quỹ đất mới mỏng", 0.45, 0.6),
             ("R3 Cung Hải Phòng lớn, siêu dự án cạnh tranh", 0.5, 0.5), ("R4 Vi phạm tuân thủ mới", 0.25, 0.55),
             ("R5 Soát xét điều chỉnh LN/EPS", 0.2, 0.4), ("R6 Lãi vay mua nhà tăng", 0.35, 0.45),
             ("R7 Vay nội bộ chuyển giá trị sang CRV/HHS", 0.2, 0.25), ("R8 Chi phí hoàn thành vượt dự toán", 0.3, 0.5)]
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.08, right=0.98)
    ax.axhspan(0.5, 1, xmin=0.5, color="#F6DCD6", zorder=0); ax.axhspan(0, 0.5, xmax=0.5, color="#E3EEE8", zorder=0)
    off = {"R3 Cung Hải Phòng lớn, siêu dự án cạnh tranh": (0.02, -0.06), "R6 Lãi vay mua nhà tăng": (0.02, -0.06), "R5 Soát xét điều chỉnh LN/EPS": (0.015, -0.06), "R8 Chi phí hoàn thành vượt dự toán": (0.015, 0.025)}
    for t, p, i in risks:
        ax.scatter(p, i, s=70, color=ACCENT if p * i > 0.2 else NAVY, zorder=3)
        dx, dy = off.get(t, (0.015, 0.02))
        ax.text(p + dx, i + dy, t, fontsize=6.8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xlabel("Xác suất (12 tháng, ước lượng)", fontsize=8); ax.set_ylabel("Tác động lên giá trị", fontsize=8)
    ax.set_title("Rủi ro lớn nhất là tốc độ bán mới, không phải bảng cân đối")
    save(fig, "fig_14_risk_matrix", "Đánh giá định tính của nhóm nghiên cứu (ước lượng), xem bảng rủi ro mục 8.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)
    print("figs done")
