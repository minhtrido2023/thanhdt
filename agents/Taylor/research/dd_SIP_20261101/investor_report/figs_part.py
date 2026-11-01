"""Dựng biểu đồ cho báo cáo DD nhà đầu tư SIP (01/11/2026). Import bởi build_report.py.
Số: ../REPORT.md v2 (đã áp đính chính của người phản biện, §11) + ../calc/valuation.py (chạy lại tại chỗ, không chép tay).
Khuôn: ../../dd_HHS_20261101/investor_report/figs_part.py. Mỗi hình kèm CSV.
"""
import contextlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# --- định giá: chạy chính ../calc/valuation.py (v2) để lấy hàm scen/base_with; stdout bỏ đi
V = {"__name__": "valuation"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(os.path.join(CALC, "valuation.py"), encoding="utf-8").read(), V)
PX = V["PX"]                                   # 48.350, DNSE latest_trade khớp cuối 30/10/2026 14:45:06
SCEN = {"Tích cực": (V["res"][0][1], 0.20), "Cơ sở": (V["res"][1][1], 0.50), "Tiêu cực": (V["res"][2][1], 0.30)}
FV_LO, FV_BASE, FV_HI = SCEN["Tiêu cực"][0], SCEN["Cơ sở"][0], SCEN["Tích cực"][0]
FV_C = V["w"]; FV_C_SYM = V["sym"]
BOX_LO, BOX_HI = V["lo"], V["hi"]
EPS = V["eps_bctc"]
SRC_BCTC = "Nguồn: BCTC hợp nhất 9T/2026 (chưa soát xét), BCTC 2025 kiểm toán (EY), BCTN 2025; tính toán của nhóm nghiên cứu."


def ke_rows():
    """Độ nhạy theo chi phí vốn chủ: Ke dùng cả cho PE lõi (≈1/(Ke−g), g=2%) và chiết khấu khối đất."""
    pv = V["pv_even"]; old = pv.__defaults__
    out = []
    for ke in (0.105, 0.123, 0.13, 0.134, 0.14):
        pv.__defaults__ = (ke,)
        pe = 1 / (ke - 0.02)
        out.append((ke, pe, V["base_with"](pe_core=pe)))
    pv.__defaults__ = old
    return out


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
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    plt = setup_mpl()
    print("Kịch bản:", {k: round(v) for k, (v, p) in SCEN.items()}, "tâm", round(FV_C), round(FV_C_SYM), "hộp", round(BOX_LO), round(BOX_HI))
    kfmt = lambda v: f"{vn(v / 1000, 1)}k"

    # 00 HERO -------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.40, 0.92]); axp.axis("off")
    im = crop_to(Image.open(os.path.join(FIGS, "ph_p004_x36.jpg")).convert("RGB"), 0.40 * 7.2 / (0.92 * 3.3))
    axp.imshow(im, aspect="auto")
    axp.text(0.04, 0.05, "KCN của SIP — ảnh: BCTN 2025", transform=axp.transAxes,
             color="white", fontsize=6.2, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.43, 0.50, 0.56, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "48.350 đ"), ("Vùng hợp lý hẹp (ước lượng)", "42–55k"), ("LNST mẹ 9T/26 · YoY", "1.078 tỷ · +7,6%"),
            ("P/E theo EPS BCTC", "9,3x"), ("Quỹ đất KCN chưa cho thuê", "937 ha"), ("Tín dụng phi ngân hàng", "6.016 tỷ")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.25, v, fontsize=12.5 if len(v) < 9 else 9.6, weight="bold", color=ACCENT if i == 5 else NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=6.3, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.45, 0.17, 0.52, 0.22])
    axv.barh(0, FV_HI - FV_LO, left=FV_LO, color=LIGHT, height=0.5)
    axv.barh(0, 55_000 - 42_000, left=42_000, color="#B9C6D6", height=0.5)
    for lab, (v, p) in SCEN.items():
        axv.plot(v, 0, "o", color=GREY, ms=5)
        axv.text(v, -0.62, f"{lab} {kfmt(v)}", ha="center", fontsize=6.4, color="#444")
    axv.axvspan(FV_C, FV_C_SYM, ymin=0.42, ymax=0.66, color=NAVY, alpha=0.85)
    axv.text(FV_C_SYM + 900, 0.42, "tâm ≈47,7–50,3k", ha="left", fontsize=7, color=NAVY, weight="bold")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX - 900, 0.42, "giá 48,35k", ha="right", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(20_000, 82_000); axv.set_ylim(-0.9, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False)
    ticks = list(range(20_000, 82_001, 10_000))
    axv.set_xticks(ticks); axv.set_xticklabels([f"{t // 1000}k" for t in ticks], fontsize=7)
    axv.set_title("Giá TRONG vùng giá trị hợp lý, ngay tại tâm (đ/cp)", fontsize=8, pad=3)
    save(fig, "fig_00_hero", "Nguồn: DNSE (giá khớp cuối 30/10/2026), BCTC 30/09/2026, SOTP ba kịch bản của nhóm nghiên cứu (ước lượng). Ảnh: BCTN 2025 SIP.",
         pd.DataFrame({"chi_so": [k for k, _ in kpis], "gia_tri": [v for _, v in kpis]}))
    plt.close(fig)

    # 01 Mô hình kinh doanh (sơ đồ) ------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 60)

    def box(x, y, w, h, t, fc, tc="white", fs=7.0):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="none"))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc, weight="bold")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))
    box(1, 40, 22, 14, "Doanh nghiệp FDI\nthuê đất KCN\n(cả thời hạn)", "#E8EEF5", NAVY)
    box(31, 40, 30, 14, "Tiền thuê trả trước\nDT chưa thực hiện 15.077 tỷ\n(+1.702 trong 9T/26)", NAVY)
    box(69, 40, 30, 14, "Phân bổ dần vào DT\n9T/26: 342 tỷ, biên gộp 69%\n(phi tiền mặt)", "#E8EEF5", NAVY)
    box(31, 21, 30, 13, "Tiền gửi, cho vay CTCK, trái phiếu\n13.808 tỷ tài sản tài chính", GOLD, "#1d2731", 6.6)
    box(69, 21, 30, 13, "Lãi tài chính ròng 9T/26\n379 tỷ ≈ 26% LNTT", "#FBEFD6", "#1d2731", 6.8)
    box(1, 2, 22, 13, "EVN / nhà máy nước\n(mua đầu vào)", "#E8EEF5", NAVY)
    box(31, 2, 30, 13, "Bán lại điện, nước + dịch vụ KCN\nDT 9T/26: 6.245 tỷ", GREEN)
    box(69, 2, 30, 13, "LN gộp 735 tỷ\n(điện nước biên 8,7%; dịch vụ 46%)", "#E3EEE8", "#1d2731", 6.8)
    arrow(23, 47, 31, 47); arrow(61, 47, 69, 47); arrow(46, 40, 46, 34); arrow(61, 27.5, 69, 27.5)
    arrow(23, 8.5, 31, 8.5); arrow(61, 8.5, 69, 8.5)
    ax.set_title("Ba dòng lãi: phân bổ tiền thuê đất, chênh lãi trên tiền trả trước, và bán lại điện nước trong KCN", fontsize=9)
    save(fig, "fig_01_model", "Số 9T/2026 (DT tiện ích = điện nước 5.730,3 + dịch vụ KCN 514,8; LN gộp 497,0 + 238,4; lãi TC ròng = DT tài chính 646,1 − CP tài chính 267,6). " + SRC_BCTC,
         pd.DataFrame({"khoi": ["dt_chua_th_3009", "tang_9T", "phan_bo_9T", "tai_san_tc", "lai_tc_rong_9T", "dt_tien_ich_9T", "lng_tien_ich_9T"],
                       "ty_dong": [15077.2, 1701.8, 341.8, 13808.1, 378.5, 6245.1, 735.4]}))
    plt.close(fig)

    # 02 LN gộp theo mảng + LNTT waterfall --------------------------------------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1, 1.25]})
    fig.subplots_adjust(bottom=0.27, top=0.82, left=0.17, right=0.98, wspace=0.32)
    seg = ["Điện, nước KCN", "Dịch vụ KCN khác", "Phân bổ thuê đất", "BĐS + khác"]
    g25 = [439.9, 212.9, 211.8, 977.5 - 439.9 - 212.9 - 211.8]; g26 = [497.0, 238.4, 235.8, 1072.2 - 497.0 - 238.4 - 235.8]
    y = np.arange(4)[::-1]
    a1.barh(y + 0.19, g25, 0.38, color=LIGHT, label="9T/2025"); a1.barh(y - 0.19, g26, 0.38, color=NAVY, label="9T/2026")
    for yi, a_, b_ in zip(y, g25, g26):
        a1.text(b_ + 8, yi - 0.19, f"{vn(b_)} ({vn((b_ / a_ - 1) * 100, 0)}%)", va="center", fontsize=6.8, weight="bold")
    a1.set_yticks(y); a1.set_yticklabels(seg, fontsize=7.2); a1.set_xlim(0, 700); a1.legend(fontsize=6.6, frameon=False, loc="lower right")
    a1.set_title("LN gộp theo mảng (tỷ)", fontsize=8.6)
    wf = [("Tiện ích\n+dịch vụ", 735.4), ("Phân bổ\nđất", 235.8), ("BĐS\n+khác", 101.0), ("BH\n+QL", -108.4),
          ("Tài chính\nròng", 378.5), ("Liên\nkết", 47.8), ("Một\nlần", 75.6)]
    cum = 0
    for i, (lab, v) in enumerate(wf):
        c = ACCENT if v < 0 else (GOLD if "Tài chính" in lab else (GREY if "Một" in lab else NAVY))
        a2.bar(i, v, bottom=cum if v >= 0 else cum + v, color=c, width=0.62)
        a2.text(i, cum + max(v, 0) + 20, vn(v), ha="center", fontsize=6.6)
        cum += v
    a2.bar(len(wf), cum, color="#1d2731", width=0.62); a2.text(len(wf), cum + 20, vn(cum), ha="center", fontsize=7, weight="bold")
    a2.set_xticks(range(len(wf) + 1)); a2.set_xticklabels([w[0] for w in wf] + ["LNTT\n9T/26"], fontsize=6.4)
    a2.set_ylim(0, 1650); a2.set_title("Từ LN gộp tới LNTT 9T/2026 (tỷ)", fontsize=8.6)
    fig.suptitle("LN gộp tiện ích và dịch vụ KCN tăng 12–13%; lãi tài chính ròng chiếm ≈26% LNTT", x=0.01, ha="left", fontsize=9.6, weight="bold", color="#1d2731")
    save(fig, "fig_02_profit", "BĐS + khác = hàng hoá, xây dựng, bán BĐS, dịch vụ khác. Một lần 9T/26: lãi thanh lý BCC 67,8 tỷ (thu nhập khác). Q3/2026 riêng: LNST mẹ 344,4 tỷ (−5,9% YoY). " + SRC_BCTC,
         pd.DataFrame({"mang": seg, "lng_9T25": g25, "lng_9T26": g26}))
    pd.DataFrame(wf + [("LNTT", cum)], columns=["khoan", "ty_dong"]).to_csv(os.path.join(FIGS, "fig_02_waterfall.csv"), index=False)
    plt.close(fig)

    # 03 Quỹ đất theo KCN -------------------------------------------------------
    kcn = ["Phước Đông A", "Phước Đông B", "Lộc An–Bình Sơn", "Lê Minh Xuân 3", "Đông Nam"]
    leased = [789.9, 225.58, 245.12, 58.1, 184.76]; left = [24.13, 678.2, 115.5, 97.7, 21.47]; fill = [97.04, 24.96, 67.98, 37, 89]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.30, top=0.86, left=0.17, right=0.97)
    y = np.arange(5)[::-1]
    ax.barh(y, leased, color=NAVY, height=0.55, label="Đã cho thuê")
    ax.barh(y, left, left=leased, color=GOLD, height=0.55, label="Còn lại (thương phẩm)")
    for yi, a_, b_, f in zip(y, leased, left, fill):
        ax.text(a_ + b_ + 10, yi, f"còn {vn(b_)} ha · lấp đầy {vn(f, 0)}%", va="center", fontsize=7)
    ax.set_yticks(y); ax.set_yticklabels(kcn, fontsize=7.8); ax.set_xlim(0, 1200); ax.set_xlabel("ha", fontsize=8)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_title("937 ha còn lại: 678 ha ở Phước Đông B (Tây Ninh), nơi giá thuê vùng đang giảm")
    save(fig, "fig_03_landbank", "Nguồn: BCTN 2025 SIP, bảng tình hình cho thuê đất tại 31/12/2025 (tổng thương phẩm 2.440,6 ha; đã thuê 1.503,5; lấp đầy 61,6%). Cho thuê 2025: 28,6 ha (kế hoạch 45); kế hoạch 2026: 60 ha.",
         pd.DataFrame({"kcn": kcn, "da_thue_ha": leased, "con_lai_ha": left, "lap_day_pct": fill}))
    plt.close(fig)

    # 04 Bản đồ (đã vẽ bằng scripts/make_maps.sh) — cắt lề trắng --------------------
    mp = Image.open(os.path.join(FIGS, "map_region.png")).convert("RGB")
    mp.crop(ImageChops.difference(mp, Image.new("RGB", mp.size, "white")).getbbox()).save(os.path.join(FIGS, "fig_04_map.png"))
    pd.read_csv(os.path.join(HERE, "scripts", "pts_region.csv")).to_csv(os.path.join(FIGS, "fig_04_map.csv"), index=False)

    # 05 Khung ảnh hạ tầng ------------------------------------------------------
    names = [("ph_p020_x492.jpg", "Cổng KCN Phước Đông (Tây Ninh) — KCN\nlớn nhất, 2.189 ha"),
             ("ph_p031_x614.jpg", "Khu liên hợp Phước Đông – Bời Lời:\nnhà máy thuê đất dài hạn"),
             ("ph_p030_x605.jpg", "KCN Đông Nam (Củ Chi cũ, TP.HCM):\nlấp đầy ≈89%"),
             ("ph_p022_x531.jpg", "Nhà xưởng xây sẵn cho thuê —\nmảng nhỏ, lấp đầy >95%")]
    fb = ImageFont.truetype(FONT, 22)
    tw, th = 700, 400; cap = 70; pad = 14
    can = Image.new("RGB", (2 * tw + 3 * pad, 2 * (th + cap) + 3 * pad), "white"); dr = ImageDraw.Draw(can)
    for k, (fn, c) in enumerate(names):
        gx, gy = k % 2, k // 2
        im = crop_to(Image.open(os.path.join(FIGS, fn)).convert("RGB"), tw / th).resize((tw, th))
        x0 = pad + gx * (tw + pad); y0 = pad + gy * (th + cap + pad)
        can.paste(im, (x0, y0)); dr.rectangle([x0, y0, x0 + tw - 1, y0 + th - 1], outline="#C9D2DC")
        dr.multiline_text((x0 + 4, y0 + th + 6), c, font=fb, fill="#1F3A5F", spacing=4)
    can.save(os.path.join(FIGS, "fig_05_photos.png"))
    pd.DataFrame({"anh": [n for n, _ in names], "chu_thich": [c.replace("\n", " ") for _, c in names],
                  "nguon": ["BCTN 2025 SIP, trang PDF 20", "BCTN 2025 SIP, trang PDF 31 (mục dự án Phước Đông – Bời Lời)",
                            "BCTN 2025 SIP, trang PDF 30 (mục dự án KCN Đông Nam)", "BCTN 2025 SIP, trang PDF 22 (mục cơ cấu doanh thu)"]}).to_csv(os.path.join(FIGS, "fig_05_photos.csv"), index=False)

    # 06 Bảng cân đối: tài sản tài chính vs nghĩa vụ ------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.22, top=0.86, left=0.22, right=0.97)
    A = [("Tiền + tiền gửi", 400.8 + 7187.6, NAVY), ("Cho vay CTCK", 4223.4, ACCENT), ("Trái phiếu DN", 1792.4, "#E08A6F"), ("Cổ phiếu", 203.9, GREY)]
    L = [("Vay ngân hàng", 5494.2, "#555"), ("CP hạ tầng phải trả", 3262.8, GREY), ("Quỹ KTPL", 638.8, LIGHT)]
    for row, parts in ((1, A), (0, L)):
        left_ = 0
        for lab, v, c in parts:
            ax.barh(row, v, left=left_, color=c, height=0.55)
            if v > 900:
                ax.text(left_ + v / 2, row, f"{lab}\n{vn(v)}", ha="center", va="center", fontsize=6.6, color="white", weight="bold")
            left_ += v
        ax.text(left_ + 120, row, vn(left_), va="center", fontsize=7.6, weight="bold")
    ax.set_yticks([1, 0]); ax.set_yticklabels(["Tài sản tài chính", "Nghĩa vụ"], fontsize=8); ax.set_xlim(0, 16_500)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_title("Ròng ≈4.410 tỷ; nhưng 6.016 tỷ là tín dụng phi ngân hàng (116% VCSH mẹ)")
    save(fig, "fig_06_balance", "Tỷ đồng, 30/09/2026. Phần nhỏ cuối mỗi thanh: cổ phiếu 203,9 (GTHL); quỹ khen thưởng phúc lợi 638,8. Cho vay CTCK: 31,07% có tài sản bảo đảm của bên vay. Trái phiếu mua mới trong 9T: Thời Đại Mới T&T 1.000,7; Vinhomes 363,6; Phước Sơn 200,0; khác 228,1. Vay ngân hàng ngắn hạn 4.374 đều tín chấp. Công ty mẹ chỉ còn ròng ≈781 tỷ; phần lớn ở công ty con. " + SRC_BCTC,
         pd.DataFrame([("tai_san", l, v) for l, v, _ in A] + [("nghia_vu", l, v) for l, v, _ in L], columns=["nhom", "khoan", "ty_dong"]))
    plt.close(fig)

    # 07 Giá 12 tháng + thanh khoản ------------------------------------------------
    o = json.load(open(os.path.join(CALC, "dnse_ohlc_SIP.json")))
    idx = [dt.datetime.fromtimestamp(x, dt.timezone(dt.timedelta(hours=7))).date() for x in o["t"]]
    px = pd.Series([c * 1000 for c in o["c"]], index=pd.to_datetime(idx)).loc["2025-10-31":]
    val = pd.Series([c * v / 1e6 for c, v in zip(o["c"], o["v"])], index=pd.to_datetime(idx)).loc["2025-10-31":]
    adv = val.resample("ME").mean()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.3), sharex=True, gridspec_kw={"height_ratios": [2.3, 1]})
    fig.subplots_adjust(bottom=0.16, top=0.88, left=0.10, right=0.97, hspace=0.12)
    a1.plot(px.index, px.values, color=NAVY, lw=1.4)
    for d_, t_, ty, ha in [("2026-04-21", "ĐHĐCĐ: cổ tức 2025 = 50%", 64_000, "right"), ("2026-05-14", "GDKHQ cổ tức 40%", 62_000, "left"), ("2026-06-10", "Chủ tịch bán 3,7 tr cp", 59_000, "left"), ("2026-10-30", "BCTC Q3", 56_000, "right")]:
        ts = pd.Timestamp(d_); yv = px.asof(ts)
        a1.axvline(ts, color=LIGHT, lw=0.8, zorder=0)
        a1.annotate(t_, (ts, yv), (ts, ty), fontsize=6.3, ha=ha, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.5))
    a1.text(px.index[-1], px.iloc[-1] - 2_600, "48.350", fontsize=7.5, ha="center", color=NAVY, weight="bold")
    a1.set_ylim(42_000, 66_000); a1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v))); a1.set_ylabel("đ/cp", fontsize=8)
    r = px.iloc[-1] / px.iloc[0] - 1
    a1.set_title(f"12 tháng: {vn(r * 100, 1)}% (giá điều chỉnh cổ tức); thanh khoản giảm từ ≈13–40 tỷ xuống ≈4 tỷ/phiên")
    a2.bar(adv.index - pd.Timedelta(days=14), adv.values, width=20, color=GREY)
    a2.set_ylabel("tỷ/phiên", fontsize=7.5); a2.tick_params(labelsize=7)
    save(fig, "fig_07_price", "Nguồn: DNSE (đóng cửa điều chỉnh cổ tức, tới 30/10/2026; giá trị giao dịch = đóng cửa × khối lượng, bình quân tháng, ước lượng). Sự kiện: CBTT công ty. Quan sát, không phải quan hệ nhân quả.",
         pd.DataFrame({"ngay": px.index.date, "dong_cua": px.values, "gt_ty": val.values}))
    plt.close(fig)

    # 08 Football field ----------------------------------------------------------
    rows = [("SOTP — 3 kịch bản (tiêu cực–tích cực)", FV_LO, FV_HI, NAVY), ("SOTP — tâm (20/50/30 · 25/50/25)", FV_C, FV_C_SYM, NAVY),
            ("Hộp sai số mô hình quanh kịch bản cơ sở", BOX_LO, BOX_HI, LIGHT), ("Vùng giá trị hợp lý hẹp", 42_000, 55_000, "#7F95AE"),
            (f"P/E 8–10x × EPS BCTC {vn(EPS)}", 8 * EPS, 10 * EPS, GOLD),
            ("Giá 52 tuần (điều chỉnh, tham chiếu)", float(px.min()), float(px.max()), GREEN)]
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); fig.subplots_adjust(bottom=0.18, top=0.86, left=0.38, right=0.97)
    for i, (lab, lo, hi, c) in enumerate(rows[::-1]):
        ax.barh(i, hi - lo, left=lo, color=c, height=0.5, alpha=0.9)
        ax.text(lo - 600, i, vn(lo, 0), ha="right", va="center", fontsize=6.8); ax.text(hi + 600, i, vn(hi, 0), ha="left", va="center", fontsize=6.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.2)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.8); ax.text(PX + 500, -0.8, "giá 48.350", color=ACCENT, ha="left", fontsize=7.5, weight="bold"); ax.set_ylim(-1.05, len(rows) - 0.5)
    ax.set_xlim(14_000, 88_000); ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: vn(v)))
    ax.set_title("Mọi phép đo đều bao quanh giá: không rẻ, không đắt", loc="right")
    save(fig, "fig_08_football_field", "Đ/cp. Nguồn: tính toán của nhóm nghiên cứu (ước lượng); EPS TTM 5.184 = EPS kiểm toán 2025 − 9T/25 + 9T/26 (đã trừ quỹ khen thưởng phúc lợi). Giá 52 tuần: DNSE, điều chỉnh cổ tức.",
         pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "mau"]).drop(columns="mau").round(0))
    plt.close(fig)

    # 09 Ma trận: lỗ tín dụng × giá trị đất -------------------------------------------
    losses = [0.0, 0.10, 0.30, 0.50]; perha = [4.0, 8.0, 12.0, 16.0, 20.0]
    M = np.array([[V["base_with"](credit_loss=c, perha=h) for h in perha] for c in losses])
    from matplotlib.colors import TwoSlopeNorm
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); fig.subplots_adjust(bottom=0.26, top=0.86, left=0.20, right=0.97)
    ax.imshow(M / PX - 1, cmap="RdBu", norm=TwoSlopeNorm(0, -0.3, 0.3), aspect="auto")
    for i in range(len(losses)):
        for j in range(len(perha)):
            ax.text(j, i, vn(M[i, j]), ha="center", va="center", fontsize=7.6, weight="bold" if (i, j) == (0, 2) else None,
                    color="white" if abs(M[i, j] / PX - 1) > 0.2 else "#1d2731")
    ax.set_xticks(range(len(perha))); ax.set_xticklabels([f"{vn(h, 0)} tỷ/ha" for h in perha], fontsize=7.5)
    ax.set_yticks(range(len(losses))); ax.set_yticklabels([f"lỗ {int(c * 100)}%" for c in losses], fontsize=7.5); ax.grid(False)
    ax.set_xlabel("Giá trị ròng toàn phần mỗi ha đất còn lại", fontsize=8); ax.set_ylabel("Lỗ trên 4.340 tỷ\ntín dụng không bảo đảm", fontsize=7.6)
    ax.set_title("Hai biến chi phối: chất lượng tín dụng và giá trị 937 ha đất (đ/cp, kịch bản cơ sở)")
    save(fig, "fig_09_matrix", "Các tham số khác giữ ở kịch bản cơ sở (lỗ tín dụng cơ sở 5%; 12 tỷ/ha; 22 năm; Ke 13%; NCI con 20%; chiết khấu quản trị 10%). Xanh: giá trị > giá; đỏ: < giá. Nguồn: tính toán của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame(M.round(0), index=[f"lo_{int(c * 100)}" for c in losses], columns=[f"ha_{int(h)}" for h in perha]).reset_index().rename(columns={"index": "lo_tin_dung"}))
    plt.close(fig)

    # 10 Ma trận rủi ro --------------------------------------------------------------
    risks = [("R1 Tổn thất cho vay CTCK / trái phiếu", 0.25, 0.80), ("R2 Cho thuê Phước Đông B chậm, giá giảm", 0.45, 0.65),
             ("R3 Cổ tức về mức sàn 10%", 0.45, 0.30), ("R4 Q3 bị điều chỉnh khi kiểm toán", 0.20, 0.25),
             ("R5 Tạm ứng 635,6 tỷ cho người quản lý không thu hồi", 0.25, 0.40), ("R6 Đền bù GPMB tăng theo bảng giá đất", 0.50, 0.35),
             ("R7 Thanh khoản thấp khi cần thoát", 0.60, 0.20)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.20, top=0.88, left=0.08, right=0.98)
    ax.axhspan(0.5, 1, xmin=0.5, color="#F6DCD6", zorder=0); ax.axhspan(0, 0.5, xmax=0.5, color="#E3EEE8", zorder=0)
    off = {"R3 Cổ tức về mức sàn 10%": (-0.015, -0.05, "right"), "R4 Q3 bị điều chỉnh khi kiểm toán": (0.015, -0.06, "left"), "R6 Đền bù GPMB tăng theo bảng giá đất": (0.015, 0.02, "left"),
           "R5 Tạm ứng 635,6 tỷ cho người quản lý không thu hồi": (0.015, 0.02, "left"), "R7 Thanh khoản thấp khi cần thoát": (0.015, -0.01, "left")}
    for t, p, i in risks:
        ax.scatter(p, i, s=70, color=ACCENT if p * i > 0.18 else NAVY, zorder=3)
        dx, dy, ha = off.get(t, (0.015, 0.02, "left"))
        ax.text(p + dx, i + dy, t, fontsize=6.6, ha=ha)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xlabel("Xác suất (12 tháng, ước lượng)", fontsize=8); ax.set_ylabel("Tác động lên giá trị", fontsize=8)
    ax.set_title("Rủi ro lớn nhất: chất lượng 6.016 tỷ tín dụng và tốc độ cho thuê Phước Đông B")
    save(fig, "fig_10_risk_matrix", "Đánh giá định tính của nhóm nghiên cứu (ước lượng), xem bảng rủi ro mục 8.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)

    kr = ke_rows()
    pd.DataFrame(kr, columns=["ke", "pe_loi", "gia_tri_co_so"]).round(4).to_csv(os.path.join(FIGS, "tab_ke_sensitivity.csv"), index=False)
    print("Ke:", [(k, round(p, 2), round(v)) for k, p, v in kr])
    print("figs done")
