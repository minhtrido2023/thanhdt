"""Dựng biểu đồ cho báo cáo DD nhà đầu tư HPG (31/10/2026). Import bởi build_report.py.
Số: REPORT.md v2 (đã áp đính chính của người phản biện) + calc/hpg_valuation_v2_out.txt. Mỗi hình kèm CSV.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "..", "src")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 21_000                       # đóng cửa 30/10/2026 [BQ]
FV_LO, FV_C, FV_HI = 18_000, 20_156, 22_500
SCEN = {"Xấu": (9_612, 0.25), "Trung lập": (19_563, 0.50), "Tốt": (28_147, 0.25)}
RI_W = 19_221
Q = ["Q1/25", "Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]
DTT = [37621.7, 35910.5, 36407.4, 46176.5, 52900.8, 55158.9, 62214.2]
GPM = [14.42, 18.35, 16.72, 13.85, 15.81, 19.01, 19.16]
LNST = [3349.8, 4264.5, 4012.3, 3888.3, 9055.9, 6424.5, 8265.4]
CORE = [None, None, 3570, None, 4900, 6300, 7714]           # lõi ước lượng (REPORT v2 §3b)


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
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.6, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def figs():
    import numpy as np
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()

    # 00 HERO -------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.40, 0.92]); axp.axis("off")
    im = Image.open(os.path.join(SRC, "web", "thep-xay-dung-1.jpg")).convert("RGB")
    w, h = im.size; im = im.crop((int(w * 0.10), 0, int(w * 0.10) + int(h * 0.95), h))
    axp.imshow(im, aspect="auto"); axp.text(0.04, 0.06, "Luyện thép — ảnh: hoaphat.com.vn", transform=axp.transAxes, color="white", fontsize=6.5, bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.43, 0.50, 0.56, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "21.000 đ"), ("Vùng hợp lý", "18,0–22,5k"), ("P/E lõi TTM", "≈8,0x"),
            ("LN lõi Q3 vs cùng kỳ", "+116–120%"), ("Nợ ròng/EBITDA lõi", "1,54x"), ("P/B", "1,19x")]
    for i, (k, v) in enumerate(kpis):
        x, y = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((x, y), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(x + 0.02, y + 0.27, v, fontsize=12.5, weight="bold", color=NAVY, transform=axk.transAxes)
        axk.text(x + 0.02, y + 0.07, k, fontsize=7, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.45, 0.17, 0.52, 0.22])
    axv.barh(0, FV_HI - FV_LO, left=FV_LO, color=LIGHT, height=0.5)
    for lab, (v, p) in SCEN.items():
        axv.plot(v, 0, "o", color=GREY, ms=5)
        axv.text(v, -0.55, f"{lab} {vn(v/1000,1)}k", ha="center", fontsize=6.5, color="#444")
    axv.axvline(FV_C, color=NAVY, lw=2); axv.text(FV_C - 250, 0.42, f"tâm {vn(FV_C/1000,1)}k", ha="right", fontsize=7, color=NAVY, weight="bold")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX + 250, 0.42, "giá 21,0k", ha="left", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(7000, 31000); axv.set_ylim(-1.1, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False); axv.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    axv.tick_params(labelsize=7)
    fig.text(0.45, 0.43, "Giá trong vùng hợp lý, cao hơn tâm ≈4%", fontsize=8.5, weight="bold", color=NAVY)
    save(fig, "fig_00_hero", "Nguồn: BCTC hợp nhất Q3/2026; tav2_bq (giá 30/10/2026); định giá của nhóm nghiên cứu (ước lượng). Ảnh: website hoaphat.com.vn.",
         pd.DataFrame(kpis, columns=["kpi", "gia_tri"]))
    plt.close(fig)

    # 01 DT + biên gộp ----------------------------------------------------
    x = np.arange(7)
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(x, np.array(DTT) / 1e3, color=[LIGHT] * 4 + [NAVY] * 3, width=0.65)
    for i, v in enumerate(DTT):
        ax.text(i, v / 1e3 - 6, vn(v / 1e3, 1), ha="center", fontsize=7.5, color="white" if i >= 4 else "#333")
    ax.set_xticks(x, Q); ax.set_ylabel("DT thuần, nghìn tỷ đồng"); ax.set_ylim(0, 115)
    a2 = ax.twinx(); a2.grid(False); a2.spines["right"].set_visible(True)
    a2.plot(x, GPM, color=ACCENT, marker="o", lw=1.6)
    for i, v in enumerate(GPM):
        a2.text(i, v + 0.7, vn(v, 1) + "%", ha="center", fontsize=7.5, color=ACCENT, weight="bold")
    a2.set_ylim(-12, 21); a2.set_yticks([10, 15, 20]); a2.set_ylabel("Biên gộp, %")
    ax.set_title("Doanh thu +71% cùng kỳ; biên gộp ≈19% hai quý liền dù spread HRC đi ngang")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_revenue_margin", "Nguồn: BCTC hợp nhất Q1–Q3/2026, soát xét 6T/2026, kiểm toán 2025 (Q2, Q4 = luỹ kế trừ nhau). Q4 và Q1 yếu theo mùa nên so cùng kỳ.",
         pd.DataFrame({"quy": Q, "dtt_ty": DTT, "bien_gop_pct": GPM}))
    plt.close(fig)

    # 02 LNST báo cáo vs lõi ---------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    one = [0, 0, 4012.3 - 3570, 0, 9055.9 - 4900, 6424.5 - 6300, 8265.4 - 7714]
    base = [l - o for l, o in zip(LNST, one)]
    ax.bar(x, np.array(base) / 1e3, color=[LIGHT] * 4 + [NAVY] * 3, width=0.65, label="LNST (lõi khi bóc được)")
    ax.bar(x, np.array(one) / 1e3, bottom=np.array(base) / 1e3, color=ACCENT, alpha=0.75, width=0.65, label="Một lần / phi cốt lõi (ước lượng)")
    for i, v in enumerate(LNST):
        ax.text(i, v / 1e3 + 0.15, vn(v / 1e3, 1), ha="center", fontsize=7.5)
    ax.annotate("Q1/26: lãi thoái vốn BĐS\n4.929 tỷ trước thuế", (4, 8.5), xytext=(1.8, 6.6), fontsize=7.5, color=ACCENT,
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
    ax.set_xticks(x, Q); ax.set_ylabel("nghìn tỷ đồng"); ax.set_ylim(0, 10.5)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Lõi đi lên đều Q1 ≈4,9k – Q2 ≈6,3k – Q3 ≈7,7k; 9T báo cáo bị thổi bởi Q1")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_02_npat_core", "Nguồn: BCTC hợp nhất (LNST); bóc một lần: lãi chuyển nhượng 4.929,1 (TM34 soát xét 6T), LNST BĐS, LN khác Q3 286,6 — ước lượng của nhóm nghiên cứu. Lõi 2025 chỉ bóc được Q3/25.",
         pd.DataFrame({"quy": Q, "lnst": LNST, "phan_mot_lan_uoc_luong": one}))
    plt.close(fig)

    # 03 Sản lượng --------------------------------------------------------
    vol = pd.DataFrame({"quy": ["Q1/25", "Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"],
                        "xd_clc": [1192, 1300, 1000, 1300, 1400, 1300, 1300], "hrc": [993, 1170, 1200, 1600, 1400, 1900, 2000],
                        "ong": [186, 216, 225, 221, 241, 212, 228], "ton": [89, 110, 120, 103, 106, 83, 118],
                        "tong_ban": [2380, 2600, 2500, 3000, 3000, 3500, 3800]})
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    b = np.zeros(7)
    for col, c, lab in (("xd_clc", NAVY, "Thép XD + cuộn CLC"), ("hrc", ACCENT, "HRC"), ("ong", GREY, "Ống thép"), ("ton", GOLD, "Tôn mạ")):
        ax.bar(x, vol[col] / 1e3, bottom=b, color=c, width=0.65, label=lab); b += vol[col] / 1e3
    for i, v in enumerate(vol["tong_ban"]):
        ax.text(i, max(v, b[i] * 1e3) / 1e3 + 0.08, vn(v / 1e3, 1), ha="center", fontsize=7.5, weight="bold")
    ax.set_xticks(x, vol["quy"]); ax.set_ylabel("triệu tấn"); ax.set_ylim(0, 4.6)
    ax.legend(fontsize=7.2, frameon=False, ncol=4, loc="upper left")
    ax.set_title("Tăng trưởng là khối lượng: HRC gấp đôi nhờ Dung Quất 2 (9T HRC +59%)")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_03_volume", "Nguồn: thông cáo sản lượng của công ty (hoaphat.com.vn); số có dấu '>' trong thông cáo được vẽ ở mức sàn; tổng bán có thể gồm phôi. Không có trong BCTC.", vol)
    plt.close(fig)

    # 04 Khung ảnh sản phẩm ----------------------------------------------
    items = [("hrc_san-pham.jpg", "Thép xây dựng", "Thép thanh/cuộn cho nhà ở, hạ tầng — thị phần ≈35–36%"),
             ("hrc_12.jpg", "HRC (cán nóng)", "Đầu vào ống, tôn, cơ khí — sản phẩm của Dung Quất"),
             ("ong-thep.jpg", "Ống thép", "Hạ nguồn từ HRC — ≈228 nghìn tấn/quý"),
             ("ton-ma-mau-2.jpg", "Tôn mạ", "Hạ nguồn từ HRC — ≈118 nghìn tấn Q3/26"),
             ("nong-nghiep.jpg", "Nông nghiệp", "Thức ăn chăn nuôi, trứng — ≈3% DT 9T/26")]
    H = 330; tiles = []
    for f, _, _ in items:
        imx = Image.open(os.path.join(SRC, "web", f)).convert("RGB")
        w0, h0 = imx.size; tw = int(h0 * 1.25)
        if tw < w0:
            l = (w0 - tw) // 2; imx = imx.crop((l, 0, l + tw, h0))
        tiles.append(imx.resize((int(H * 1.25), H)))
    fig = plt.figure(figsize=(7.2, 2.6))
    for i, (t, (_, nm, cap)) in enumerate(zip(tiles, items)):
        a = fig.add_axes([0.005 + i * 0.199, 0.33, 0.19, 0.62]); a.imshow(t); a.axis("off")
        fig.text(0.008 + i * 0.199, 0.25, nm, fontsize=7.6, weight="bold", color=NAVY)
        import textwrap
        fig.text(0.008 + i * 0.199, 0.21, "\n".join(textwrap.wrap(cap, 30)), fontsize=6.3, color="#444", va="top")
    save(fig, "fig_04_products", "Ảnh: website hoaphat.com.vn (trang chủ và bài 'Thép cuộn cán nóng…'), truy cập 31/10/2026; cắt khung. Tỷ trọng: BCTC phân khúc + thông cáo sản lượng.",
         pd.DataFrame([(a, b, c) for a, b, c in items], columns=["file", "san_pham", "chu_thich"]))
    plt.close(fig)

    # 05 Bản đồ ghép ------------------------------------------------------
    ims = [Image.open(os.path.join(FIGS, f + ".png")).convert("RGB") for f in ("map_north", "map_central", "map_south")]
    # Bố cục 2 hàng (bản 1 hàng 3 bản đồ quá dẹt, in ra PDF chữ không đọc được): Bắc trên cả hàng; Trung | Nam dưới
    W = 3000; gap = 20
    n = ims[0].resize((int(ims[0].width * 1700 / ims[0].height), 1700))
    if n.width > W:
        n = n.resize((W, int(n.height * W / n.width)))
    Hb = int((W - gap) / (ims[1].width / ims[1].height + ims[2].width / ims[2].height))
    c, so = [i.resize((int(i.width * Hb / i.height), Hb)) for i in ims[1:]]
    S = Image.new("RGB", (W, n.height + gap + Hb), "white")
    S.paste(n, ((W - n.width) // 2, 0)); S.paste(c, (0, n.height + gap)); S.paste(so, (c.width + gap, n.height + gap))
    S.save(os.path.join(FIGS, "fig_05_maps.png"))
    import shutil
    rows = []
    for f in ("pts_north", "pts_central", "pts_south"):
        rows.append(pd.read_csv(os.path.join(HERE, "scripts", f + ".csv")).assign(ban_do=f))
    pd.concat(rows).to_csv(os.path.join(FIGS, "fig_05_maps.csv"), index=False)

    # 06 Chuỗi giá trị ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3)
    boxes = [(0.1, 1.1, "Quặng sắt, than cốc\n(nhập khẩu + nội địa)", LIGHT, NAVY), (2.3, 1.1, "Lò cao – lò thổi (BOF)\nthép thô 16 tr t/năm", NAVY, "white"),
             (4.6, 2.0, "Thép XD, cuộn CLC\n(Hải Dương, Dung Quất)", "#E8EEF5", NAVY), (4.6, 0.2, "HRC 9 tr t/năm\n(Dung Quất)", ACCENT, "white"),
             (7.3, 0.2, "Ống thép, tôn mạ\n(hạ nguồn, nội địa + XK)", "#E8EEF5", NAVY), (7.3, 2.0, "Nhà ở, hạ tầng\n(nội địa ≈74–79% DT)", "#F3F5F7", NAVY)]
    for x0, y0, t, fc, tc in boxes:
        ax.add_patch(plt.Rectangle((x0, y0), 2.15, 0.8, fc=fc, ec=NAVY, lw=0.8))
        ax.text(x0 + 1.075, y0 + 0.4, t, ha="center", va="center", fontsize=6.6, color=tc, weight="bold")
    arr = dict(arrowstyle="->", color=GREY, lw=1.2)
    for (a0, a1) in (((2.25, 1.5), (2.3, 1.5)), ((4.45, 1.6), (4.6, 2.3)), ((4.45, 1.4), (4.6, 0.6)), ((6.75, 0.6), (7.3, 0.6)), ((6.75, 2.4), (7.3, 2.4))):
        ax.annotate("", a1, a0, arrowprops=arr)
    ax.text(0.1, 0.35, "Bảo hộ: AD 23,1–27,83% với HRC Trung Quốc\n(QĐ 1959/QĐ-BCT; rà soát QĐ 1902)", ha="left", fontsize=6.6, color=ACCENT)
    ax.set_title("Mô hình tích hợp: từ quặng tới HRC và hạ nguồn — biên phụ thuộc spread và bảo hộ")
    save(fig, "fig_06_value_chain", "Minh họa của nhóm nghiên cứu. Công suất: thông cáo công ty 06/2026; AD: QĐ 1959/QĐ-BCT (04/07/2025), QĐ 1902/QĐ-BCT (27/07/2026); tỷ trọng nội địa: BCTC soát xét 6T/2026.")
    plt.close(fig)

    # 07 Dòng tiền 9T -----------------------------------------------------
    cf = pd.DataFrame({"muc": ["LNST lõi 9T", "CFO báo cáo", "CFO bỏ hoàn VAT", "CFO bỏ VAT\n& phải trả NB", "Capex"],
                       "ty": [19243, 20936.3, 15800.6, 20211.0, 14607.2]})
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(range(5), cf["ty"] / 1e3, color=[LIGHT, NAVY, ACCENT, NAVY, GREY], width=0.6)
    for i, v in enumerate(cf["ty"]):
        ax.text(i, v / 1e3 + 0.3, vn(v / 1e3, 1), ha="center", fontsize=8, weight="bold")
    ax.set_xticks(range(5), cf["muc"], fontsize=7.8); ax.set_ylabel("nghìn tỷ đồng"); ax.set_ylim(0, 25)
    ax.set_title("CFO 9T 0,82–1,09x LN lõi: tốt, nhưng có hoàn VAT một lần 5,1 nghìn tỷ")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_cashflow", "Nguồn: BCTC hợp nhất Q3/2026 (LCTT 9T; VAT được khấu trừ 7.429,9 – 2.294,2; phải trả người bán NH −4.410,4). LN lõi 9T: ước lượng của nhóm nghiên cứu.", cf)
    plt.close(fig)

    # 08 Nợ ròng / EBITDA --------------------------------------------------
    nd = pd.DataFrame({"cach": ["Trừ toàn bộ tiền gửi\n(cận dưới)", "Không trừ tiền gửi\ncầm cố 8.294", "+ phải trả người bán\ndài hạn 3.829"],
                       "no_rong": [59607.6, 67901.6, 71730.5]})
    nd["x"] = nd["no_rong"] / 44235.3
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.barh(range(3), nd["x"], color=[LIGHT, NAVY, NAVY], height=0.55)
    for i, (v, n) in enumerate(zip(nd["x"], nd["no_rong"])):
        ax.text(v + 0.04, i, f"{vn(v,2)}x  ({vn(n/1e3,1)} nghìn tỷ)", va="center", fontsize=8)
    ax.axvline(3, color=ACCENT, ls="--", lw=1); ax.text(2.95, -0.1, "ngưỡng cờ đỏ ngành 3x", ha="right", fontsize=7, color=ACCENT)
    ax.set_yticks(range(3), nd["cach"], fontsize=7.6); ax.set_xlim(0, 3.3); ax.invert_yaxis(); ax.set_xlabel("Nợ ròng / EBITDA lõi TTM (44.235 tỷ)")
    ax.set_title("Đòn bẩy 1,5–1,6x khi không coi tiền gửi cầm cố là tiền tự do — vẫn thấp")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_leverage", "Nguồn: BCTC hợp nhất Q3/2026 (vay 105.736,7; tiền + HTM); tiền gửi cầm cố ≈8.294 tỷ tại 30/6/2026 (TM6a, soát xét 6T); EBITDA lõi: ước lượng.", nd)
    plt.close(fig)

    # 09 Football field ----------------------------------------------------
    ff = pd.DataFrame([
        ("RI 3 kịch bản (xấu–tốt), Ke 11,8%", 9612, 28147, 19221),
        ("RI trọng số theo dải Ke 11,0–12,4%", 17560, 22223, 19221),
        ("EV/EBITDA 2027 × 5x (xấu–tốt)", 16162, 26229, 22025),
        ("EV/EBITDA 2027 × 6–7x (trọng số; comp, lệch lên)", 27651, 33277, None),
        ("Vùng giá 12 tháng (điều chỉnh)", None, None, None)], columns=["phuong_phap", "thap", "cao", "trung_vi"])
    pxr = pd.read_csv(os.path.join(FIGS, "price_raw.csv"))
    ff.loc[4, ["thap", "cao"]] = [pxr["Close"].min(), pxr["Close"].max()]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=GREY if i == 3 else NAVY, height=0.5, alpha=0.85)
        ax.text(r["thap"] - 300, yy, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 300, yy, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.5)
        if r["trung_vi"] == r["trung_vi"] and r["trung_vi"] is not None:
            ax.plot(r["trung_vi"], yy, "|", color="white", ms=14, mew=2)
    ax.axvspan(FV_LO, FV_HI, color=GREEN, alpha=0.12, label="Vùng hợp lý 18,0–22,5k")
    ax.axvline(FV_C, color=GREEN, lw=1.4, label="Tâm ≈20,2k (ước lượng)")
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.4, label="Đóng cửa 30/10: 21,0k")
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.6)
    ax.set_xlim(4000, 37000); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(-0.35, -0.12), ncol=3)
    ax.set_title("Giá 21,0k nằm trong vùng hợp lý, ở nửa trên")
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    save(fig, "fig_09_football_field", "Nguồn: mô hình thu nhập thặng dư và EV/EBITDA của nhóm nghiên cứu (ước lượng); giá: tav2_bq.ticker 30/10/2025–30/10/2026. Vạch trắng = trọng số/trung tâm.", ff)
    plt.close(fig)

    # 10 Độ nhạy ROE × Ke ------------------------------------------------
    roes = [10, 11, 12, 13, 14, 15, 16]; kes = ["11,25%", "11,83%", "12,42%", "13,00%"]
    grid = np.array([[16199, 14722, 13451, 12390], [19115, 17347, 15825, 14555], [22031, 19971, 18200, 16721],
                     [24947, 22596, 20574, 18886], [27863, 25220, 22948, 21052], [30779, 27845, 25322, 23217],
                     [33695, 30469, 27696, 25383]])
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    cm = ax.imshow(grid - PX, cmap="RdBu", vmin=-12000, vmax=12000, aspect="auto")
    for i in range(7):
        for j in range(4):
            ax.text(j, i, vn(grid[i, j] / 1e3, 1), ha="center", va="center", fontsize=8, color="black")
    ax.set_xticks(range(4), [f"Ke {k}" for k in kes]); ax.set_yticks(range(7), [f"ROE {r}%" for r in roes]); ax.grid(False)
    ax.set_title("Giá 21k ≈ ROE dài hạn sau thuế đầy đủ ≈12,4% — biến nhạy nhất là ROE, không phải Ke")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_10_sensitivity", "Nguồn: calc/hpg_valuation_v2.py — kịch bản trung lập, ROE terminal sau thuế 20%, g 5%; nghìn đ/cp; xanh = trên giá 21.000, đỏ = dưới.",
         pd.DataFrame(grid, index=[f"roe_{r}" for r in roes], columns=kes).reset_index())
    plt.close(fig)

    # 11 Giá 12 tháng + P/B ----------------------------------------------
    pxr["time"] = pd.to_datetime(pxr["time"])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.6), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
    a1.plot(pxr["time"], pxr["Close"], color=NAVY, lw=1.3, label="HPG (điều chỉnh)")
    vni = pxr["VNINDEX"] / pxr["VNINDEX"].iloc[0] * pxr["Close"].iloc[0]
    a1.plot(pxr["time"], vni, color=GREY, lw=1.0, ls="--", label="VN-Index (quy về cùng gốc)")
    pk = pxr.loc[pxr["Close"].idxmax()]
    a1.annotate(f"Đỉnh {vn(pk['Close'])} ({pk['time']:%d/%m})", (pk["time"], pk["Close"]), xytext=(10, 2), textcoords="offset points", fontsize=7, color=NAVY)
    for d, s in (("2026-04-29", "BCTC Q1"), ("2026-07-29", "BCTC Q2"), ("2026-10-29", "BCTC Q3")):
        a1.axvline(pd.Timestamp(d), color=GREY, lw=0.7, ls=":"); a1.text(pd.Timestamp(d), pxr["Close"].min() * 0.98, s, fontsize=6.5, ha="right", color="#555")
    a1.legend(fontsize=7, frameon=False, loc="upper left"); a1.set_ylabel("đ/cp")
    a2.plot(pxr["time"], pxr["PB"], color=ACCENT, lw=1.2); a2.axhline(1.14, color=GREY, lw=0.8, ls=":")
    a2.text(pxr["time"].iloc[5], 1.16, "đáy 2023: 1,14x", fontsize=6.5, color="#555"); a2.set_ylabel("P/B")
    a1.set_title("Giá −20% từ đỉnh 26.240 (26/02) dù lợi nhuận lõi tăng; P/B 1,19x ngang đáy 2025")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_11_price", "Nguồn: tav2_bq.ticker (Close điều chỉnh, PB, VNINDEX) 30/10/2025–30/10/2026. Đường VN-Index quy về giá HPG ngày đầu để so tương đối.", pxr)
    plt.close(fig)

    # 12 Sơ đồ TLSH --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    def box(x0, y0, w, h, t, fc, tc=NAVY):
        ax.add_patch(plt.Rectangle((x0, y0), w, h, fc=fc, ec=NAVY, lw=0.8)); ax.text(x0 + w / 2, y0 + h / 2, t, ha="center", va="center", fontsize=6.6, color=tc, weight="bold")
    box(0.1, 1.5, 2.0, 1.0, "HPG\n(công ty mẹ)", NAVY, "white")
    box(3.8, 2.9, 3.1, 0.9, "TLSH — 25,13%\n9.915 tỷ (giá gốc)", "#FBF1EC")
    box(3.8, 1.5, 3.1, 0.9, "BĐS Hòa Phát — còn 26,55%\n2.814 tỷ (giá gốc)", "#F3F5F7")
    box(3.8, 0.1, 3.1, 0.9, "Liên danh Đại lộ sông Hồng (BT)\nphải thu 1.600 – 100 tỷ", "#F3F5F7")
    box(7.5, 2.9, 2.4, 0.9, "Dự án KĐT 696 ha\n(Thư Lâm–Đông Anh)", "#FBF1EC")
    box(7.5, 0.6, 2.4, 1.1, "Chưa rõ đích:\n≈2.973 tỷ góp vốn,\nký quỹ/BCC ≈500 tỷ", "#FFF6E0")
    arr = dict(arrowstyle="->", color=ACCENT, lw=1.1)
    ax.annotate("", (3.8, 3.35), (2.1, 2.3), arrowprops=arr); ax.text(0.1, 3.3, "1.920 tiền (H1)\n+ 7.995 bằng CP BĐS HP (Q3)", fontsize=6.6, color=ACCENT)
    ax.annotate("", (3.8, 1.95), (2.1, 1.95), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.annotate("", (3.8, 0.55), (2.1, 1.6), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.annotate("", (7.5, 3.35), (6.9, 3.35), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.set_title("≈9,5% vốn chủ gắn vào hệ sinh thái dự án đất lớn Hà Nội, không do HPG kiểm soát")
    save(fig, "fig_12_tlsh", "Nguồn: BCTC riêng công ty mẹ Q3/2026 (TM VI.3: liên kết 12.728,9; VI.4); BCTC soát xét 6T/2026 TM6b, TM9; BCTC hợp nhất Q3 VI.4; NQ HĐQT 10 & 13/NQHP-2026; báo chí (dự án).",
         pd.DataFrame({"khoan": ["TLSH", "BĐS HP 26,55%", "Phai thu lien danh 30/9", "Gop von chua ro dich", "Ky quy+BCC cty me"], "ty": [9915, 2813.9, 100, 2973, 495.8]}))
    plt.close(fig)

    # 13 Ma trận rủi ro ----------------------------------------------------
    rk = pd.DataFrame([("R1", "Rà soát AD HRC hạ mức", 2, 5), ("R2", "Nhà ở gãy – thép XD H2/27", 3, 3),
                       ("R3", "Spread HRC về 150–200 USD/t", 2, 4), ("R4", "Hết ưu đãi thuế / DQ2 'mở rộng'", 3, 3),
                       ("R5", "TLSH: suy giảm / góp thêm", 2, 2), ("R6", "VinMetal cạnh tranh HRC", 3, 2),
                       ("R7", "Cầm cố CP cá nhân / quản trị", 2, 2)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 10 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R2": (-0.22, 0.2), "R4": (0.15, -0.2), "R5": (-0.22, 0.2), "R7": (0.15, -0.2), "R6": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 9 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("AD và spread: tác động lớn nhất; nhà ở và thuế: dễ xảy ra hơn")
    fig.tight_layout(rect=(0, 0.07, 0.68, 1))
    save(fig, "fig_13_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan); tham chiếu đọc ngành độc lập 31/10/2026.", rk)
    plt.close(fig)
    print("figs ok")
