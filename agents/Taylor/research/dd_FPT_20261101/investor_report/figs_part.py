"""Dựng biểu đồ cho báo cáo DD nhà đầu tư FPT (01/11/2026). Import bởi build_report.py.
Số: ../REPORT.md v2 (đã áp đính chính của người phản biện) + ../calc/valuation_out.txt / valuation_out.json. Mỗi hình kèm CSV.
Khuôn: ../../dd_HHS_20261101/investor_report/figs_part.py.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 52_700                                   # DNSE latest_trade khớp 30/10/2026 14:45:03 (còn quyền cổ tức 1.000đ)
SH = 1885.727648
# --- cùng công thức ../calc/valuation.py (v2, cùng gốc có quyền cổ tức)
CORE = 6705.133333                            # LN lõi vận hành TTM (ước lượng)
FOX = 55.4e3 * 738.763463 / 1e3 * 0.4566
FRT = 148.7e3 * 178.815054 / 1e3 * 0.4654
OTHER = 1500.0 + 494.4 + 451.1                # liên kết khác theo sổ (ước lượng) + TPBank, FPTS giá gốc
NC = 12233.0                                  # tiền ròng 30/9, chưa trừ cổ tức


def dcf(g1, conv, gT, ke, n=5, base=CORE):
    pv, e = 0.0, base
    for t in range(1, n + 1):
        e *= 1 + g1; pv += e * conv / (1 + ke) ** t
    return pv + e * (1 + gT) * conv / (ke - gT) / (1 + ke) ** n


def fv(g1, conv, gT, ke, fd):
    return (dcf(g1, conv, gT, ke) + FOX * (1 - fd) + FRT * 0.8 + OTHER + NC) / SH * 1e3


SCEN = {"Tiêu cực": (fv(0.03, 0.40, 0.03, 0.134, 0.30), 0.35),
        "Cơ sở": (fv(0.09, 0.75, 0.04, 0.1285, 0.15), 0.45),
        "Tích cực": (fv(0.14, 0.85, 0.04, 0.123, 0.00), 0.20)}
EV = sum(v * p for v, p in SCEN.values())
Z_LO, Z_HI = fv(0.09, 0.75, 0.03, 0.134, 0.15), fv(0.09, 0.75, 0.05, 0.123, 0.15)
SRC_BCTC = "Nguồn: BCTC hợp nhất Q3/2026 (chưa soát xét), Q2/2026, BCTN 2025, thông cáo KQKD 9T/2026 của FPT; tính toán của nhóm nghiên cứu."


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
    print("Kịch bản:", {k: round(v) for k, (v, p) in SCEN.items()}, "kỳ vọng", round(EV), "vùng", round(Z_LO), round(Z_HI))

    # 00 HERO -------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.40, 0.92]); axp.axis("off")
    im = crop_to(Image.open(os.path.join(FIGS, "ph_building.jpg")).convert("RGB"), 0.40 * 7.2 / (0.92 * 3.3))
    axp.imshow(im, aspect="auto")
    axp.text(0.04, 0.05, "Ảnh: BCTN 2025 FPT", transform=axp.transAxes,
             color="white", fontsize=6.2, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.43, 0.50, 0.56, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "52.700 đ"), ("Vùng cơ sở (ước lượng)", "55,0–66,7k"), ("LNST mẹ 9T/26 · +13,3%", "7.778 tỷ"),
            ("Tiền ròng 30/9/26", "12.233 tỷ"), ("P/E 4 quý gần nhất", "9,7x"), ("Ký mới NN riêng Q3", "+3,6%")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=12.0 if len(v) < 9 else 10.5, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=6.3, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.45, 0.17, 0.52, 0.22])
    lo, hi = SCEN["Tiêu cực"][0], SCEN["Tích cực"][0]
    axv.barh(0, hi - lo, left=lo, color=LIGHT, height=0.5)
    axv.barh(0, Z_HI - Z_LO, left=Z_LO, color=NAVY, height=0.5, alpha=0.85)
    for lab, (v, p) in SCEN.items():
        axv.plot(v, 0, "o", color=GREY, ms=5)
        axv.text(v, -0.62, f"{lab} {vn(v/1000,1)}k", ha="center", fontsize=6.4, color="#444")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX - 500, 0.42, "giá 52,7k", ha="right", fontsize=7, color=ACCENT, weight="bold")
    axv.text(Z_HI + 500, 0.42, "vùng cơ sở", ha="left", fontsize=7, color=NAVY, weight="bold")
    axv.set_xlim(30_000, 84_000); axv.set_ylim(-0.9, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    axv.set_xticks(range(30_000, 84_001, 10_000)); axv.set_xticklabels([f"{x//1000}k" for x in range(30_000, 84_001, 10_000)], fontsize=7)
    axv.set_title("Giá DƯỚI vùng cơ sở ≈4%; kỳ vọng 3 kịch bản 54,8k (đ/cp)", fontsize=8, pad=3)
    save(fig, "fig_00_hero", "Nguồn: dữ liệu giao dịch HOSE (giá), BCTC Q3/2026; vùng cơ sở = DCF dòng tiền cho cổ đông, g dài hạn 3–5% × Ke 12,3–13,4% (ước lượng, nhóm nghiên cứu). Ảnh: BCTN 2025 FPT.",
         pd.DataFrame({"chi_so": [k for k, _ in kpis], "gia_tri": [v for _, v in kpis]}))
    plt.close(fig)

    # 01 Giảm tốc 6T -> Q3 -------------------------------------------------
    it = ["DT CNTT nước ngoài", "Ký mới nước ngoài", "DT chuyển đổi số NN", "DT CNTT trong nước", "LNST cổ đông mẹ"]
    g6 = [13.4, 32.3, 23.8, 22.5, 14.1]; gq = [8.2, 3.6, 3.8, 42.9, 11.8]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.28, top=0.88, left=0.24, right=0.97)
    y = np.arange(len(it))[::-1]
    ax.barh(y + 0.18, g6, 0.36, color=LIGHT, label="6T/2026")
    ax.barh(y - 0.18, gq, 0.36, color=[ACCENT, ACCENT, ACCENT, GREEN, NAVY], label="riêng Q3/2026")
    for yi, a_, b_ in zip(y, g6, gq):
        ax.text(a_ + 0.6, yi + 0.18, f"+{vn(a_,1)}%", va="center", fontsize=6.8, color="#777")
        ax.text(b_ + 0.6, yi - 0.18, f"+{vn(b_,1)}%", va="center", fontsize=7.4, weight="bold")
    ax.set_yticks(y); ax.set_yticklabels(it, fontsize=7.8); ax.set_xlim(0, 50); ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_xlabel("Tăng trưởng so với cùng kỳ (%)", fontsize=8)
    ax.set_title("Q3 giảm tốc ở xuất khẩu (ký mới +3,6%); trong nước tăng tốc; lãi giữ +12%")
    save(fig, "fig_01_growth", "Q3 = 9T − 6T; cùng kỳ suy từ % tăng trưởng FPT công bố (số 2025 đã điều chỉnh bỏ FPT Telecom). " + SRC_BCTC,
         pd.DataFrame({"chi_tieu": it, "yoy_6T": g6, "yoy_Q3": gq}))
    plt.close(fig)

    # 02 Thị trường xuất khẩu (sơ đồ, không nền bản đồ) ----------------------
    mk = [("Nhật Bản", 13197, 17.2, "+25,2% theo JPY; Q3 ≈+15% (ước lượng)", 0.80, 0.55, 0.84),
          ("Mỹ", 6485, 6.5, "USD Q3 +5,8%", 0.16, 0.55, 0.74),
          ("Châu Âu", 3422, 35.3, "", 0.42, 0.78, 0.88),
          ("Châu Á–TBD", 5434, -4.6, "", 0.68, 0.24, 0.02)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.12)
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    vx, vy = 0.42, 0.42
    ax.scatter(vx, vy, s=900, color=NAVY, zorder=4); ax.text(vx, vy, "Việt Nam\n(kỹ sư)", ha="center", va="center", color="white", fontsize=6.6, weight="bold", zorder=5)
    tot = sum(m[1] for m in mk)
    for n, v, g, note, x, yv, ly in mk:
        ax.annotate("", (x, yv), (vx, vy), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.6 + 4 * v / tot, alpha=0.7))
        ax.scatter(x, yv, s=v / 4.5, color=GREEN if g >= 10 else (GOLD if g >= 0 else ACCENT), alpha=0.85, zorder=3, edgecolors="white")
        ax.text(x, ly, f"{n}: {vn(v)} tỷ ({vn(100*v/tot,0)}%)\n{'+' if g >= 0 else ''}{vn(g,1)}% theo VND" + (f"\n{note}" if note else ""),
                ha="center", fontsize=6.8, color=NAVY, weight="bold")
    ax.set_title("DT CNTT nước ngoài 9T/2026 = 28.538 tỷ: Nhật chiếm 46%; châu Âu tăng nhanh nhất, châu Á–TBD giảm")
    save(fig, "fig_02_export", "Sơ đồ minh họa (không phải bản đồ): cỡ chấm tỷ lệ với doanh thu 9T/2026; màu: xanh ≥ +10%, vàng 0–10%, đỏ < 0. Nguồn: slide KQKD 9T/2026 của FPT; JPY/USD Q3 suy từ số lũy kế (ước lượng).",
         pd.DataFrame([m[:4] for m in mk], columns=["thi_truong", "dt_9T_ty", "yoy_vnd_pct", "ghi_chu"]))
    plt.close(fig)

    # 03 Cầu nối tăng LNTT 9T ------------------------------------------------
    steps = [("LNTT 9T/2025\n(điều chỉnh)", 7495.5, "base"), ("Lãi công ty\nliên kết", 663.4, "up"), ("Khối Công nghệ", 718.6, "up"),
             ("GD + lãi ròng\n+ khác", -107.3, "dn"), ("LNTT 9T/2026", 8770.2, "base")]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.24, top=0.86, left=0.11, right=0.98)
    cum = 0
    for i, (lab, v, k) in enumerate(steps):
        if k == "base":
            ax.bar(i, v, color=NAVY, width=0.6); cum = v; ax.text(i, v + 80, vn(v), ha="center", fontsize=7.5, weight="bold")
        else:
            b = cum if v > 0 else cum + v
            ax.bar(i, abs(v), bottom=b, color=GREEN if v > 0 else ACCENT, width=0.6); cum += v
            ax.text(i, cum + 80 if v > 0 else b - 260, f"{'+' if v > 0 else ''}{vn(v)}", ha="center", fontsize=7.5, weight="bold")
    ax.set_xticks(range(len(steps))); ax.set_xticklabels([s[0] for s in steps], fontsize=7.2); ax.set_ylim(6500, 9300)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v))); ax.set_ylabel("Tỷ đồng", fontsize=8)
    ax.set_title("52% mức tăng LNTT 9T đến từ lãi liên kết (chủ yếu FPT Telecom); bỏ phần này LNST chỉ +5,2%")
    save(fig, "fig_03_profit_bridge", "Số 2025 là số FPT điều chỉnh bỏ hợp nhất FPT Telecom (BCTC Q3/2026 tr.8). Thuế trên LNTT trừ liên kết tăng từ 11,1% lên 15,2%. " + SRC_BCTC,
         pd.DataFrame([(s[0].replace("\n", " "), s[1]) for s in steps], columns=["buoc", "ty_dong"]))
    plt.close(fig)

    # 04 Tỷ lệ chuyển lãi thành tiền --------------------------------------------
    per = ["Năm 2024\n(gồm FTEL)", "Năm 2025\n(gồm FTEL)", "9T/2025\n(gồm FTEL)", "9T/2026\n(FTEL là liên kết)"]
    cv = [1.07, 0.60, 0.34, -0.12]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(bottom=0.27, top=0.82, left=0.07, right=0.98, wspace=0.28)
    a1.bar(range(4), cv, color=[GREY, GREY, LIGHT, ACCENT], width=0.6)
    for i, v in enumerate(cv):
        a1.text(i, v + (0.04 if v >= 0 else -0.12), vn(v, 2), ha="center", fontsize=8, weight="bold")
    a1.axhline(0.75, color=NAVY, ls="--", lw=1); a1.text(3.35, 0.79, "giả định cơ sở 0,75", fontsize=6.6, color=NAVY, ha="right")
    a1.axhline(0.40, color=ACCENT, ls=":", lw=1); a1.text(3.35, 0.44, "tiêu cực 0,40", fontsize=6.6, color=ACCENT, ha="right")
    a1.axhline(0, color="#555", lw=0.8); a1.set_xticks(range(4)); a1.set_xticklabels(per, fontsize=6.6); a1.set_ylim(-0.3, 1.25)
    a1.set_title("Tỷ lệ chuyển lãi lõi thành tiền", fontsize=8.6)
    q = ["H1/26", "Q3/26", "9T/26"]; cfo = [-1145, 2097, 952]; cap = [1337, 692, 2029]
    x = np.arange(3)
    a2.bar(x - 0.19, cfo, 0.38, color=NAVY, label="CFO"); a2.bar(x + 0.19, [-c for c in cap], 0.38, color=GOLD, label="Capex (âm)")
    for i in range(3):
        a2.text(i - 0.19, cfo[i] + (60 if cfo[i] > 0 else -230), vn(cfo[i]), ha="center", fontsize=6.8, weight="bold")
        a2.text(i + 0.19, -cap[i] - 230, vn(-cap[i]), ha="center", fontsize=6.8)
    a2.axhline(0, color="#555", lw=0.8); a2.set_xticks(x); a2.set_xticklabels(q, fontsize=7.5); a2.set_ylim(-2600, 2600)
    a2.legend(fontsize=6.6, frameon=False, loc="upper left"); a2.set_title("CFO và capex 2026 (tỷ)", fontsize=8.6)
    fig.suptitle("Tiền chưa về: 9T/2026 âm; Q4 là quý thu tiền chính (Q4/2025 đóng góp ≈3.300 tỷ tử số)", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_04_cash", "Tỷ lệ = (CFO + lãi vay đã trả × (1 − thuế) − capex) / [(LNTT − lãi hoạt động đầu tư + chi phí lãi vay) × (1 − thuế)]. 2021–2023 chưa đo trên định nghĩa này. Năm 2024–2025 gồm FPT Telecom nên không cùng phạm vi với 2026. " + SRC_BCTC,
         pd.DataFrame({"ky": [p.replace("\n", " ") for p in per], "ty_le": cv}))
    plt.close(fig)

    # 05 Bản đồ vùng ghép -------------------------------------------------------
    n_, c_, s_ = [Image.open(os.path.join(FIGS, f)).convert("RGB") for f in ("map_north.png", "map_central.png", "map_south.png")]
    W = 2400; gap = 20
    # hàng 1: Bắc + Trung cùng chiều cao, tổng rộng W; hàng 2: Nam rộng W
    h1 = int((W - gap) / (n_.width / n_.height + c_.width / c_.height))
    n_ = n_.resize((int(n_.width * h1 / n_.height), h1)); c_ = c_.resize((W - gap - n_.width, h1))
    s_ = s_.resize((int(s_.width * (W * 0.75) / s_.width), int(s_.height * (W * 0.75) / s_.width)))
    can = Image.new("RGB", (W, h1 + gap + s_.height), "white")
    can.paste(n_, (0, 0)); can.paste(c_, (n_.width + gap, 0)); can.paste(s_, ((W - s_.width) // 2, h1 + gap))
    can.save(os.path.join(FIGS, "fig_05_maps.png"))
    pts = pd.concat([pd.read_csv(os.path.join(HERE, "scripts", f"pts_{r}.csv")).assign(vung=r) for r in ("north", "central", "south")])
    pts.to_csv(os.path.join(FIGS, "fig_05_maps.csv"), index=False)

    # 06 Khung ảnh hoạt động ----------------------------------------------------
    names = [("ph_engineers.jpg", "Kỹ sư phần mềm — CNTT nước ngoài\n= 71% doanh thu 9T/2026"),
             ("ph_dc.jpg", "Hạ tầng máy chủ / trung tâm dữ liệu\n(nay thuộc liên kết FPT Telecom)"),
             ("ph_ai_gialai.jpg", "Khởi công trung tâm nghiên cứu AI\ntại Gia Lai (Quy Nhơn)"),
             ("ph_school.jpg", "Khởi công trường phổ thông FPT —\nkhối giáo dục hút 56% capex 9T"),
             ("ph_campus.jpg", "Khuôn viên làm việc của FPT")]
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
    dr.multiline_text((x0 + 10, y0 + 30), "Ảnh: Báo cáo thường niên 2025\ncủa FPT (trang PDF 26, 50, 54,\n74, 99; ảnh công ty tự công bố).\n\nẢnh hạ tầng máy chủ minh họa\nmảng viễn thông/TTDL; từ 2026\nFPT Telecom không còn hợp nhất.",
                      font=ImageFont.truetype(FONT, 21), fill="#555", spacing=6)
    can.save(os.path.join(FIGS, "fig_06_photos.png"))
    pd.DataFrame({"anh": [n for n, _ in names], "chu_thich": [c.replace("\n", " ") for _, c in names],
                  "nguon": ["BCTN 2025 FPT trang PDF 54", "BCTN 2025 FPT trang PDF 26", "BCTN 2025 FPT trang PDF 50",
                            "BCTN 2025 FPT trang PDF 74", "BCTN 2025 FPT trang PDF 99"]}).to_csv(os.path.join(FIGS, "fig_06_photos.csv"), index=False)

    # 07 Bảng cân đối + vốn lưu động ---------------------------------------------
    d = ["31/12/25\n(còn FTEL)", "30/6/26", "30/9/26"]
    cash = [40547, 28972, 28830]; debt = [21073, 18448, 16596]; net = [19474, 10523, 12233]
    wip = [686, 1021, 1811]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(bottom=0.25, top=0.82, left=0.08, right=0.98, wspace=0.28)
    x = np.arange(3)
    a1.bar(x - 0.27, cash, 0.27, color=LIGHT, label="Tiền + tiền gửi"); a1.bar(x, debt, 0.27, color=GREY, label="Vay")
    a1.bar(x + 0.27, net, 0.27, color=NAVY, label="Tiền ròng")
    for i in range(3):
        a1.text(i + 0.27, net[i] + 600, vn(net[i]), ha="center", fontsize=6.8, weight="bold", color=NAVY)
    a1.set_xticks(x); a1.set_xticklabels(d, fontsize=7); a1.legend(fontsize=6.5, frameon=False, loc="upper right"); a1.set_ylim(0, 46000)
    a1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v))); a1.set_title("Tiền ròng 12.233 tỷ (tỷ đồng)", fontsize=8.6)
    a2.bar(range(3), wip, color=[GREY, GOLD, ACCENT], width=0.6)
    for i, v in enumerate(wip):
        a2.text(i, v + 40, vn(v), ha="center", fontsize=7.5, weight="bold")
    a2.set_xticks(range(3)); a2.set_xticklabels(["31/12/25", "30/6/26", "30/9/26"], fontsize=7); a2.set_ylim(0, 2100)
    a2.set_title("Chi phí dở dang chờ nghiệm thu (tỷ)", fontsize=8.6)
    fig.suptitle("Bảng cân đối vững, nhưng chi phí dự án chờ nghiệm thu tăng 2,6 lần trong 9 tháng", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_07_balance", "Tiền + tiền gửi = tiền + đầu tư nắm giữ đến ngày đáo hạn. Chi phí dở dang là chi phí đã bỏ ra, hoãn ghi nhận đến khi nghiệm thu: không làm phồng lợi nhuận nhưng giữ tiền. " + SRC_BCTC,
         pd.DataFrame({"ngay": [s.replace("\n", " ") for s in d], "tien_htm": cash, "vay": debt, "tien_rong": net, "do_dang": wip}))
    plt.close(fig)

    # 08 Giá và P/E 8 năm -------------------------------------------------------
    w = pd.read_csv(os.path.join(CALC, "bq_fpt_weekly.csv"), parse_dates=["time"]).sort_values("time")
    w = w[w.time >= "2018-10-01"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.2, top=0.82, left=0.08, right=0.98, wspace=0.25)
    a1.plot(w.time, w.Close / 1000, color=NAVY, lw=1.2); a1.set_title("Giá điều chỉnh (nghìn đ/cp)", fontsize=8.6)
    a1.text(w.time.iloc[-1], 52.7 - 12, "52,7", ha="center", fontsize=7.5, color=ACCENT, weight="bold")
    a2.plot(w.time, w.PE, color=GREY, lw=1.0)
    a2.axhline(10.5, color=ACCENT, ls=":", lw=1); a2.text(w.time.iloc[5], 6.2, "p10 10 năm = 10,5 (đường chấm)", fontsize=6.6, color=ACCENT)
    a2.axhline(15.4, color=NAVY, ls="--", lw=0.8); a2.text(w.time.iloc[5], 16.0, "trung vị 15,4", fontsize=6.6, color=NAVY)
    a2.scatter(w.time.iloc[-1], 9.66, color=ACCENT, zorder=5); a2.text(w.time.iloc[-1], 7.4, "9,7", ha="center", fontsize=7.5, color=ACCENT, weight="bold")
    a2.set_ylim(5, 32); a2.set_title("P/E 4 quý gần nhất (lần)", fontsize=8.6)
    import matplotlib.dates as mdates
    for a in (a1, a2):
        a.xaxis.set_major_locator(mdates.YearLocator(2)); a.xaxis.set_major_formatter(mdates.DateFormatter("%Y")); a.tick_params(axis="x", labelsize=7)
    fig.suptitle("Giá −45% từ đỉnh 1 năm; P/E 9,7 thấp nhất ≈8 năm (cả nhóm CNTT cùng giảm)", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_08_price_pe", "Nguồn: cơ sở dữ liệu thị trường (giá điều chỉnh theo tuần, P/E TTM), tới 30/10/2026. Quan sát, không phải quan hệ nhân quả.",
         w[["time", "Close", "PE"]])
    plt.close(fig)

    # 09 Football field ---------------------------------------------------------
    sotp = lambda pe, fd: (CORE * pe + FOX * (1 - fd) + FRT * 0.8 + OTHER + NC) / SH * 1e3
    eps26 = (7778.1 + 2509.5 * 1.12) / SH * 1e3
    rows = [("Ba kịch bản (tiêu cực – tích cực)", SCEN["Tiêu cực"][0], SCEN["Tích cực"][0], LIGHT),
            ("DCF cơ sở: g 3–5% × Ke 12,3–13,4%", Z_LO, Z_HI, NAVY),
            ("DCF: tỷ lệ chuyển tiền 0,60–0,90", fv(0.09, 0.60, 0.04, 0.1285, 0.15), fv(0.09, 0.90, 0.04, 0.1285, 0.15), GOLD),
            ("SOTP: P/E lõi 8–12x", sotp(8, 0.15), sotp(12, 0.15), GREEN),
            ("P/E 9–13x × EPS 2026E (ước lượng)", 9 * eps26, 13 * eps26, GREY),
            ("Mốc Ke nước ngoài 15,8% (USD)", fv(0.09, 0.75, 0.03, 0.158, 0.15), fv(0.09, 0.75, 0.05, 0.158, 0.15), "#B9C3CE")]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.18, top=0.86, left=0.37, right=0.97)
    for i, (lab, lo_, hi_, c) in enumerate(rows[::-1]):
        ax.barh(i, hi_ - lo_, left=lo_, color=c, height=0.5)
        ax.text(lo_ - 600, i, vn(lo_ / 1000, 1), ha="right", va="center", fontsize=7); ax.text(hi_ + 600, i, vn(hi_ / 1000, 1), ha="left", va="center", fontsize=7)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.4)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.8); ax.text(PX + 400, -0.85, "giá 52,7k", color=ACCENT, fontsize=7.5, weight="bold")
    ax.axvline(EV, color=NAVY, ls=":", lw=1.2); ax.text(EV + 400, len(rows) - 0.55, f"kỳ vọng {vn(EV/1000,1)}k", color=NAVY, fontsize=7)
    ax.set_ylim(-1, len(rows) - 0.4); ax.set_xlim(25_000, 88_000)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v/1000)}k"))
    ax.set_title("Giá dưới vùng DCF cơ sở, trong dải SOTP và P/E; thấp hơn kỳ vọng ≈4% (đ/cp)", loc="right")
    df = pd.DataFrame([(r[0], round(r[1]), round(r[2])) for r in rows], columns=["phuong_phap", "thap", "cao"])
    save(fig, "fig_09_football_field", "Mọi giá trị cùng gốc giá có quyền cổ tức 1.000 đ (chốt 30/11). FPT Telecom và FRT theo thị giá 30/10 có chiết khấu; tiền ròng 12.233 tỷ. Tính toán của nhóm nghiên cứu (ước lượng).", df)
    plt.close(fig)

    # 10 Ma trận tỷ lệ chuyển tiền × Ke -------------------------------------------
    cvs = [0.40, 0.50, 0.60, 0.75, 0.90]; kes = [0.123, 0.1285, 0.134, 0.14, 0.158]
    M = np.array([[fv(0.09, c, 0.04, k, 0.15) for k in kes] for c in cvs])
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); fig.subplots_adjust(bottom=0.30, top=0.88, left=0.17, right=0.97)
    from matplotlib.colors import TwoSlopeNorm
    ax.imshow(M / PX - 1, cmap="RdBu", norm=TwoSlopeNorm(0, -0.3, 0.4), aspect="auto")
    for i in range(5):
        for j in range(5):
            ax.text(j, i, vn(M[i, j] / 1000, 1), ha="center", va="center", fontsize=7.6, weight="bold" if (i, j) == (3, 1) else None,
                    color="white" if abs(M[i, j] / PX - 1) > 0.25 else "#1d2731")
    ax.set_xticks(range(5)); ax.set_xticklabels(["12,3%", "12,85%", "13,4%", "14,0%", "15,8%\n(nước ngoài)"], fontsize=7.4)
    ax.set_yticks(range(5)); ax.set_yticklabels([vn(c, 2) for c in cvs], fontsize=7.6); ax.grid(False)
    ax.set_xlabel("Chi phí vốn chủ Ke", fontsize=8); ax.set_ylabel("Tỷ lệ chuyển lãi thành tiền", fontsize=8)
    ax.set_title("Biến quyết định là dòng tiền: giá 52,7k ngầm định tỷ lệ chuyển tiền ≈0,6 ở Ke nội địa")
    save(fig, "fig_10_matrix", "Nghìn đ/cp; tăng trưởng lợi nhuận lõi 5 năm 9%/năm, g dài hạn 4%, chiết khấu FPT Telecom 15%. Tỷ trọng giá trị cuối kỳ 62–72%. Tính toán của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame(M.round(0), index=[f"conv_{c}" for c in cvs], columns=[f"ke_{k}" for k in kes]).reset_index().rename(columns={"index": "conv"}))
    plt.close(fig)

    # 11 Ma trận rủi ro ---------------------------------------------------------
    risks = [("R1 Dòng tiền 2026 không phục hồi ở Q4", 0.45, 0.75), ("R2 AI làm giảm phát giá xuất khẩu", 0.45, 0.65),
             ("R3 JPY yếu kéo dài", 0.40, 0.35), ("R4 Dự án công chậm nghiệm thu", 0.35, 0.40),
             ("R5 Chính sách FPT Telecom bất lợi", 0.20, 0.40), ("R6 Siết tuyển sinh / trần học phí", 0.35, 0.25),
             ("R7 Khoản 618,8 tỷ phải phân bổ lớn", 0.15, 0.15)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.08, right=0.98)
    ax.axhspan(0.5, 1, xmin=0.5, color="#F6DCD6", zorder=0); ax.axhspan(0, 0.5, xmax=0.5, color="#E3EEE8", zorder=0)
    off = {"R2 AI làm giảm phát giá xuất khẩu": (0.015, -0.06, "left"), "R6 Siết tuyển sinh / trần học phí": (0.015, -0.03, "left"),
           "R4 Dự án công chậm nghiệm thu": (0.0, 0.045, "center"), "R5 Chính sách FPT Telecom bất lợi": (0.0, -0.075, "center"),
           "R3 JPY yếu kéo dài": (0.015, -0.035, "left"), "R7 Khoản 618,8 tỷ phải phân bổ lớn": (0.0, -0.075, "center")}
    for t, p, i in risks:
        ax.scatter(p, i, s=70, color=ACCENT if p * i > 0.2 else NAVY, zorder=3)
        dx, dy, ha = off.get(t, (0.015, 0.02, "left"))
        ax.text(p + dx, i + dy, t, fontsize=6.8, ha=ha)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xlabel("Xác suất (12 tháng, ước lượng)", fontsize=8); ax.set_ylabel("Tác động lên giá trị", fontsize=8)
    ax.set_title("Rủi ro lớn nhất: dòng tiền và giảm phát giá do AI, không phải nợ vay")
    save(fig, "fig_11_risk_matrix", "Đánh giá định tính của nhóm nghiên cứu (ước lượng), xem bảng rủi ro mục 8.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)
    print("figs done")
