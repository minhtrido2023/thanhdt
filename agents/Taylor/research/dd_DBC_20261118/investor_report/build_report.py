"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư DBC (18/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/):
  fin_quarterly_bq.csv  — tav2_bq.ticker_financial (DBC, 2022Q4–2026Q3), kéo 18/11/2026
  price_raw.csv         — tav2_bq.ticker (DBC Close/Price/Volume, 03/11/2025–17/11/2026)
  fig_map_points.csv    — toạ độ bản đồ (OSM Nominatim 18/11/2026), dùng bởi tools/make_map_dbc.py
Ảnh (src/): logo + ảnh sản phẩm/cơ sở tải từ website công ty dabaco.vn ngày 18/11/2026.
Số BCTC/định giá: ../REPORT.md (DD đã phản biện) + ../model/calc_output.txt. Mỗi hình kèm CSV (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"  # luật 13
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung (nguồn: REPORT.md §0–§9 + model/calc_output.txt) ----
PX = 16_950                     # đóng cửa 17/11/2026 (BQ) = DNSE latest_trade 18/11 11:29:40
CENTER, CENTER_PRE = 19_491, 19_888
ZONE = (11_314, 27_270)
BASE_POST = 19_689              # giá trị kịch bản cơ sở sau chiết khấu thanh khoản
V_SHORT = 15_291
SCEN_PRE = {"Xấu": (11_545, 0.25), "Cơ sở": (20_091, 0.50), "Tốt": (27_826, 0.25)}
NORM = [  # (cách chuẩn hoá, LNST, ROE, tâm sau CK, giá/tâm)
    ("ROE trung bình 15 quý, vốn cùng kỳ (chọn)", 996.3, 11.4, 19_491, 0.87),
    ("Trung vị 12 lần LNST 12 tháng", 1_083.3, 12.4, 21_818, 0.78),
    ("Trung bình 12 lần LNST 12 tháng", 950.0, 10.9, 18_253, 0.93),
    ("LNST 12 tháng sau Q4/26 (ước lượng)", 898.3, 10.3, 16_871, 1.00),
    ("Trung bình LNST 15 quý ÷ vốn hiện tại", 843.8, 9.7, 15_412, 1.10),
    ("Trung bình LNST năm 2023–25", 767.0, 8.8, 13_357, 1.27)]
MATRIX = (15_412, 20_453)
RATE = {-100: 21_721, -50: 20_536, 50: 18_561, 100: 17_730}
WIDE = (4_900, 33_684)          # kịch bản ±6,0 điểm % ROE


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


def load_img(name, box=None):
    from PIL import Image
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    if box:
        w, h = im.size
        im = im.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])))
    return im


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    fin["NP"] = fin["NP_P0"] / 1e9
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-11-18"].reset_index(drop=True)
    lo12, hi12 = float(px["Close"].min()), float(px["Close"].max())

    # 0. Hero: ảnh cơ sở (website công ty) + thanh định giá
    fig = plt.figure(figsize=(7.2, 3.9))
    ims = [load_img("trang-chu-Linh-vuc-san-xuat-1024x683.jpg", (0, 0.12, 1, 0.82)),
           load_img("Dau-GD1.png", (0, 0.1, 1, 0.9)),
           load_img("trang-chu-Linh-vuc-san-xuat-1-1024x683.jpg", (0, 0.1, 1, 0.9))]
    caps = ["Trại gà đẻ khép kín", "Nhà máy ép dầu thực vật", "Phòng thí nghiệm vaccine"]
    for k, (im, c) in enumerate(zip(ims, caps)):
        a = fig.add_axes([k / 3 + 0.003, 0.50, 1 / 3 - 0.006, 0.50]); a.imshow(im, aspect="auto"); a.axis("off")
        a.text(0.03, 0.06, c, transform=a.transAxes, fontsize=7.6, color="white", fontweight="bold",
               bbox=dict(facecolor=NAVY, alpha=0.82, lw=0, pad=2.5))
    fig.text(0.995, 0.985, "Ảnh: website công ty dabaco.vn", fontsize=6.0, color="white", ha="right", va="top", bbox=dict(facecolor="black", alpha=0.4, lw=0, pad=1.5))
    a1 = fig.add_axes([0.06, 0.205, 0.86, 0.12]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xticks([]); a1.set_xlim(9_000, 30_000); a1.set_ylim(0, 1)
    a1.barh(0.5, ZONE[1] - ZONE[0], left=ZONE[0], height=0.55, color=LIGHT)
    a1.plot([CENTER] * 2, [0.18, 0.82], color=NAVY, lw=2.4)
    a1.plot([PX] * 2, [0.05, 0.95], color=ACCENT, lw=2.4)
    a1.plot([V_SHORT] * 2, [0.25, 0.75], color=GREY, lw=1.6, ls=":")
    a1.text(CENTER + 150, 1.05, f"Tâm giá trị {vn(CENTER)}", ha="left", fontsize=7.6, color=NAVY, fontweight="bold")
    a1.text(PX - 150, 1.05, f"Giá {vn(PX)} (0,87× tâm)", ha="right", fontsize=7.6, color=ACCENT, fontweight="bold")
    a1.text(V_SHORT, -0.5, f"{vn(V_SHORT)}\n(toàn vốn)", ha="center", va="top", fontsize=6.4, color="#555")
    a1.text(ZONE[0], -0.5, vn(ZONE[0]) + "\n(xấu)", ha="center", va="top", fontsize=6.8, color="#444")
    a1.text(ZONE[1], -0.5, vn(ZONE[1]) + "\n(tốt)", ha="center", va="top", fontsize=6.8, color="#444")
    fig.text(0.06, 0.425, "Tích hợp thức ăn – giống – trại – thực phẩm · ND/E 0,38 · ROE chuẩn hoá chu kỳ 11,4% · Q3/26 LNST −41,6%",
             fontsize=7.6, color="#222")
    fig.text(0.06, 0.375, "Vùng giá trị hợp lý (đ/cp, sau chiết khấu thanh khoản 2%) và giá 17/11/2026", fontsize=7.2, color="#555")
    save(fig, "fig_00_hero", "Nguồn: ảnh từ website công ty (dabaco.vn, tải 18/11/2026); giá tav2_bq.ticker 17/11/2026 (= DNSE 18/11 11:29); giá trị: mô hình thu nhập thặng dư của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia", "tam_sau_CK", "v_toan_von", "vung_thap", "vung_cao"], "dcp": [PX, CENTER, V_SHORT, ZONE[0], ZONE[1]]}))
    plt.close(fig)

    # 1. LNST quý + ROE quý quy năm (chuỗi vốn chủ đã sửa 2 mẫu số, REPORT §1/§2b)
    import json
    asm = json.load(open(os.path.join(HERE, "..", "model", "assumptions_DBC_20261118.json"), encoding="utf-8"))
    eq = asm["equity_parent_q_bn"]; npq = asm["np_quarterly_bn"]
    qs = sorted(q for q in npq)
    roe = [4 * npq[q] / eq[q] * 100 for q in qs]
    mean_roe = float(np.mean(roe))
    # khớp chuỗi BQ
    bq = fin.set_index("quarter")["NP"]
    assert all(abs(bq[q] - npq[q]) < 0.01 for q in qs), "NP BQ lệch assumptions"
    x = np.arange(len(qs))
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    vals = [npq[q] for q in qs]
    ax.bar(x, vals, color=[ACCENT if v < 0 else (NAVY if q.startswith("2026") else LIGHT) for q, v in zip(qs, vals)], width=0.68)
    for i, v in enumerate(vals):
        ax.text(i, v + (12 if v >= 0 else -40), vn(v), ha="center", fontsize=6.8, color="#333")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(x, [qlabel(q) for q in qs], fontsize=7.2); ax.set_ylabel("LNST cổ đông mẹ, tỷ đồng"); ax.set_ylim(-380, 640)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(x, roe, color=GREEN, marker="o", ms=3.5, lw=1.3, label="ROE quý quy năm (trục phải)")
    ax2.axhline(mean_roe, color=GREEN, ls="--", lw=1.0)
    ax2.text(3.5, mean_roe + 3.0, f"ROE trung bình 15 quý {vn(mean_roe, 2)}%", color=GREEN, fontsize=7.4, ha="center", fontweight="bold", bbox=dict(facecolor="white", alpha=0.85, lw=0, pad=1))
    ax2.set_ylim(-35, 60); ax2.set_ylabel("ROE, %")
    ax2.legend(loc="upper left", fontsize=7.2, frameon=False)
    ax.set_title("Lợi nhuận dao động theo chu kỳ heo: lỗ Q1/23, đỉnh 2025, giảm từ Q1/26")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_npat_roe", "Nguồn: tav2_bq.ticker_financial NP_P0 (khớp BCTC: Q3/26 200,17; H1/26 663,16; 9T/25 1.358,19 tỷ); vốn chủ cuối quý = BVPS × số cổ phiếu (2 điểm điều chỉnh mẫu số sau cổ tức cổ phiếu). ROE quý quy năm = 4 × LNST quý ÷ vốn chủ cuối quý.",
         pd.DataFrame({"quarter": qs, "np_bn": vals, "equity_bn": [eq[q] for q in qs], "roe_annualised_pct": roe}))
    plt.close(fig)
    print("mean ROE 15q =", round(mean_roe, 3))

    # 2. Q3/26 so Q3/25 (REPORT §2a)
    q3 = pd.DataFrame({"chi_tieu": ["Doanh thu thuần", "Lợi nhuận gộp", "CP bán hàng + QLDN", "Chi phí lãi vay", "LNST"],
                       "q3_25": [3_739.2, 652.2, 244.6, 62.5, 343.0], "q3_26": [5_138.0, 587.7, 291.9, 100.4, 200.2]})
    q3["pct"] = (q3["q3_26"] / q3["q3_25"] - 1) * 100
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    yy = np.arange(len(q3))[::-1]
    fav = [True, True, False, False, True]  # tăng là thuận lợi?
    cols = [GREEN if (p > 0) == f else ACCENT for p, f in zip(q3["pct"], fav)]
    ax.barh(yy, q3["pct"], color=cols, height=0.55)
    for y_, p, a, b in zip(yy, q3["pct"], q3["q3_25"], q3["q3_26"]):
        ax.text(p + (2 if p >= 0 else -2), y_, f"{'+' if p >= 0 else '−'}{vn(abs(p), 1)}%  ({vn(a, 1)} ; {vn(b, 1)})",
                va="center", ha="left" if p >= 0 else "right", fontsize=7.4)
    ax.set_yticks(yy, q3["chi_tieu"]); ax.axvline(0, color="#555", lw=0.8); ax.set_xlim(-110, 120)
    ax.set_xlabel("thay đổi Q3/26 so với Q3/25, %   (trong ngoặc: Q3/25 ; Q3/26, tỷ đồng)")
    ax.set_title("Q3/26: doanh thu +37%, nhưng biên gộp 11,4% (từ 17,4%) và lãi vay kéo LNST −42%")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_02_q3_yoy", "Nguồn: BCTC hợp nhất Q3/2026 (KQKD tr.5), số hợp nhất. Màu xanh = thuận lợi, đỏ = bất lợi cho lợi nhuận.", q3)
    plt.close(fig)

    # 3. Chuỗi giá trị (sơ đồ minh hoạ)
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(7.2, 2.9))
    ax = fig.add_axes([0, 0.08, 1, 0.92]); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 44)
    boxes = [(1, "Nguyên liệu\nngô, đậu tương nhập\n(VN tự chủ ~37%)", "#6B4E3D"),
             (26, "Thức ăn chăn nuôi\n+ ép dầu đậu tương\n(khô đậu tự cung)", "#1565C0"),
             (51, "Giống & trại\nlợn, gà · nái, bố mẹ\n(heo thịt 1.878 tỷ)", GREEN),
             (76, "Thực phẩm\nthịt, trứng, dầu ăn\nqua đại lý, bán lẻ", ACCENT)]
    for x0, s, c in boxes:
        ax.add_patch(FancyBboxPatch((x0, 21), 21, 19, boxstyle="round,pad=0.6", fc=c, ec="none"))
        ax.text(x0 + 10.5, 30.5, s, ha="center", va="center", color="white", fontsize=7.6, fontweight="bold", linespacing=1.35)
    for xa in (22.6, 47.6, 72.6):
        ax.annotate("", xy=(xa + 3.2, 30.5), xytext=(xa, 30.5), arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.6))
    notes = [(11.5, "Giá nhập theo CBOT/WB;\nđỉnh Q3/2026"),
             (36.5, "H1/26 bán ngoài 3.731 tỷ,\nbán nội bộ 3.657 tỷ"),
             (61.5, "Hỗ trợ: vaccine (NM 234 tỷ,\nvào vận hành 2026)"),
             (86.5, "H1/26 giống + thực phẩm\nbán ngoài 4.558 tỷ")]
    for xc, s in notes:
        ax.text(xc, 12.5, s, ha="center", va="center", fontsize=6.9, color="#333", linespacing=1.3)
    ax.text(50, 3, "Mảng phụ: bất động sản – xây dựng (doanh thu 9T/26 98,6 tỷ, lợi nhuận gộp 7,6 tỷ)", ha="center", fontsize=6.9, color="#555")
    save(fig, "fig_03_value_chain", "Sơ đồ minh hoạ của nhóm nghiên cứu. Nguồn: BCTC bán niên 2026 soát xét (thuyết minh bộ phận), BCTC Q3/2026 (TM 8, TM 12), đọc ngành độc lập 18/11/2026 (tỷ lệ tự chủ nguyên liệu).",
         pd.DataFrame({"khau": [b[1].replace("\n", " ") for b in boxes], "ghi_chu": [n[1].replace("\n", " ") for n in notes]}))
    plt.close(fig)

    # 5. Khung ảnh sản phẩm (website công ty)
    from PIL import Image, ImageDraw, ImageFont
    items = [("Giong-vat-nuoi.jpg", (0, 0, 1, 0.76), "Giống lợn, gà", "Đầu chuỗi: giống cụ kỵ, bố mẹ"),
             ("trang-chu-Linh-vuc-san-xuat-1024x683.jpg", (0.17, 0, 0.83, 1), "Trứng gà – trại khép kín", "Gà đẻ, chế biến trứng"),
             ("Trung-ga.jpg", (0, 0, 1, 0.76), "Trứng gà tươi đóng hộp", "Thực phẩm bán lẻ"),
             ("mau-fb-2000-px-12.jpg", (0, 0, 1, 1), "Dầu ăn đậu nành", "Khô đậu dùng cho TACN")]
    H = 330; tiles = []
    for f, box, t1, t2 in items:
        im = load_img(f, box); im = im.resize((int(im.width * H / im.height), H))
        if im.width > 360:
            l = (im.width - 360) // 2; im = im.crop((l, 0, l + 360, H))
        tiles.append((im, t1, t2))
    W = 1440; gap = 12; tw = (W - gap * 5) // 4
    canvas = Image.new("RGB", (W, H + 150), "white"); d = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(FONT_B, 26); fr = ImageFont.truetype(FONT, 21); fs = ImageFont.truetype(FONT, 17)
    for k, (im, t1, t2) in enumerate(tiles):
        im = im.resize((tw, int(im.height * tw / im.width))) if im.width != tw else im
        im = im.crop((0, 0, tw, min(H, im.height)))
        x0 = gap + k * (tw + gap); canvas.paste(im, (x0, 8)); d.rectangle([x0, 8, x0 + tw - 1, 8 + im.height - 1], outline="#D9DEE4", width=2)
        d.text((x0 + 4, H + 22), t1, font=fb, fill=NAVY); d.text((x0 + 4, H + 58), t2, font=fr, fill="#333")
    d.text((gap, H + 112), "Ảnh: website công ty dabaco.vn (tải 18/11/2026). Thức ăn chăn nuôi: website không có ảnh sản phẩm, xem sơ đồ chuỗi giá trị.", font=fs, fill="#666")
    canvas.save(os.path.join(FIGS, "fig_05_products.png"))
    pd.DataFrame([(i[0], i[2], i[3]) for i in items], columns=["file", "san_pham", "vi_tri_chuoi"]).to_csv(os.path.join(FIGS, "fig_05_products.csv"), index=False)

    # 6. Bảng cân đối: vay gộp, tiền + HTM, nợ ròng
    bs = pd.DataFrame({"moc": ["31/12/2025", "30/9/2026"], "vay_gop": [5_876.6, 7_622.3], "tien_htm": [2_295.4, 4_337.6],
                       "no_rong": [3_581.2, 3_284.7], "nd_e": [0.44, 0.38]})
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    xi = np.arange(2); w = 0.26
    for off, col, c, lab in ((-w, "vay_gop", LIGHT, "Vay + thuê tài chính"), (0, "tien_htm", GREY, "Tiền + tiền gửi có kỳ hạn"), (w, "no_rong", NAVY, "Nợ ròng")):
        ax.bar(xi + off, bs[col], w, color=c, label=lab)
        for i in range(2):
            ax.text(i + off, bs[col][i] + 80, vn(bs[col][i]), ha="center", fontsize=7.4)
    for i in range(2):
        ax.text(i + w, bs["no_rong"][i] / 2, f"ND/E\n{vn(bs['nd_e'][i], 2)}", ha="center", va="center", color="white", fontsize=7.4, fontweight="bold")
    ax.set_xticks(xi, bs["moc"]); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 9_800); ax.legend(fontsize=7.4, frameon=False, ncol=3, loc="upper center")
    ax.set_title("Vay tăng 1.746 tỷ nhưng tiền gửi tăng 2.042 tỷ: nợ ròng giảm, ND/E 0,38")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_06_balance_sheet", "Nguồn: BCTC hợp nhất Q3/2026 (BCĐKT tr.2–4). Nợ ròng = vay + thuê tài chính − tiền − tiền gửi giữ đến đáo hạn; 798 tỷ tiền gửi đang cầm cố cho khoản vay (BCTC bán niên TM 5).", bs)
    plt.close(fig)

    # 7. Dòng tiền 9T/26
    cf = pd.DataFrame({"muc": ["LNST 9T", "CFO 9T", "CFO cốt lõi\n(dải)", "Đầu tư 9T\n(capex + thuê TC)"],
                       "thap": [863.3, 1_517.9, 1_019.3, 1_106.0], "cao": [863.3, 1_517.9, 1_307.4, 1_679.7]})
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    xi = np.arange(4)
    ax.bar(0, 863.3, color=LIGHT, width=0.55); ax.bar(1, 1_517.9, color=NAVY, width=0.55)
    ax.bar(2, 1_019.3, color=NAVY, alpha=0.55, width=0.55); ax.bar(2, 1_307.4 - 1_019.3, bottom=1_019.3, color=NAVY, alpha=0.25, width=0.55, hatch="//")
    ax.bar(3, 1_106.0, color=ACCENT, width=0.55, label="Capex tiền 1.106,0"); ax.bar(3, 573.7, bottom=1_106.0, color=ACCENT, alpha=0.45, width=0.55, label="Thuê tài chính 573,7")
    for i, s, yv in ((0, "863,3", 863.3), (1, "1.517,9", 1_517.9), (2, "1.019–1.307", 1_307.4), (3, "1.679,7", 1_679.7)):
        ax.text(i, yv + 35, s, ha="center", fontsize=7.8, fontweight="bold")
    ax.set_xticks(xi, cf["muc"], fontsize=7.6); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 2_000)
    ax.legend(fontsize=7.2, frameon=False, loc="upper left")
    ax.set_title("CFO 9T gấp 1,8 lần LNST nhờ giải phóng tồn kho; đầu tư vẫn vượt CFO")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_cashflow", "Nguồn: BCTC hợp nhất Q3/2026 (LCTT tr.6–7; TM 11 thuê tài chính). CFO cốt lõi: bỏ giải phóng tồn kho 498,6 (cận dưới) hoặc cộng lại trả trước người bán tăng 288,1 (cận trên); vẫn gồm ~87,5 tỷ lãi tiền gửi.",
         cf.assign(muc=cf["muc"].str.replace("\n", " ")))
    plt.close(fig)

    # 8. Độ nhạy theo cách chuẩn hoá lợi nhuận
    nm = pd.DataFrame(NORM, columns=["cach", "lnst", "roe", "tam", "gia_tam"])
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    yy = np.arange(len(nm))[::-1]
    ax.barh(yy, nm["tam"], color=[NAVY] + [LIGHT] * (len(nm) - 1), height=0.58)
    for y_, r in zip(yy, nm.itertuples()):
        ax.text(r.tam + 250, y_, f"{vn(r.tam)} · giá/tâm {vn(r.gia_tam, 2)} · ROE {vn(r.roe, 1)}%", va="center", fontsize=7.2)
    ax.axvline(PX, color=ACCENT, lw=1.4); ax.text(PX + 150, -0.75, f"Giá {vn(PX)}", color=ACCENT, fontsize=7.4, fontweight="bold")
    ax.set_yticks(yy, nm["cach"], fontsize=7.3); ax.set_xlim(0, 32_000); ax.set_ylim(-1.1, len(nm) - 0.4)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_xlabel("tâm giá trị sau chiết khấu thanh khoản, đ/cp")
    ax.set_title("Kết luận nhạy với cách đo lợi nhuận \"bình thường\": giá/tâm 0,78–1,27")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_08_normalisation", "Nguồn: mô hình của nhóm nghiên cứu (calc_output, 18/11/2026); kịch bản xấu/tốt đối xứng ±3,25 điểm % ROE quanh từng cách chuẩn hoá. LNST 12 tháng sau Q4/26 dùng ước lượng Q4 = +35 tỷ.", nm)
    plt.close(fig)

    # 9. Football field
    ff = pd.DataFrame([
        ("3 kịch bản xấu – tốt (±3,25 điểm % ROE)", ZONE[0], ZONE[1]),
        ("Kịch bản rộng hơn (±6,0 điểm % ROE)", WIDE[0], WIDE[1]),
        ("6 cách chuẩn hoá lợi nhuận", 13_357, 21_818),
        ("Chuẩn hoá × tập kịch bản (4 tổ hợp)", MATRIX[0], MATRIX[1]),
        ("Lãi huy động 12T ±100 điểm cơ bản", RATE[100], RATE[-100]),
        ("Vùng giá 12 tháng (điều chỉnh)", lo12, hi12)], columns=["phuong_phap", "thap", "cao"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, r in ff.iterrows():
        yy_ = len(ff) - 1 - i
        ax.barh(yy_, r["cao"] - r["thap"], left=r["thap"], color=NAVY if i != 1 and i < 5 else (LIGHT if i == 1 else GREY), height=0.52)
        ax.text(r["thap"] - 300, yy_, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(r["cao"] + 300, yy_, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.3)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.5)
    ax.axvline(CENTER, color=NAVY, ls="--", lw=1.1, label=f"Tâm giá trị {vn(CENTER/1e3, 1)}k")
    ax.axvline(V_SHORT, color=GREY, ls=":", lw=1.1, label=f"Toàn vốn sinh ROE 11,4%: {vn(V_SHORT/1e3, 1)}k")
    ax.axvline(PX, color=ACCENT, ls="-", lw=1.4, label=f"Giá {vn(PX/1e3, 2)}k (17–18/11/2026)")
    ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=3)
    ax.set_xlim(0, 38_000); ax.set_xlabel("đồng/cổ phiếu, sau chiết khấu thanh khoản 2%", fontsize=7.6)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá thấp hơn tâm nhưng nằm trong hầu hết các dải: quanh vùng giá trị hợp lý")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_09_football_field", "Nguồn: mô hình thu nhập thặng dư của nhóm nghiên cứu (ước lượng; calc_output 18/11/2026); giá 12 tháng tav2_bq.ticker 18/11/2025–17/11/2026.", ff)
    plt.close(fig)

    # 10. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("R1", "Đáy giá heo kéo dài sang 2027", 3, 4), ("R2", "Trích lập tài sản sinh học 94–188 tỷ", 3, 2),
        ("R3", "Dịch tả lợn châu Phi lọt trại nái", 2, 4), ("R4", "Trại mới (873 tỷ) vào đúng đáy chu kỳ", 3, 3),
        ("R5", "Phải thu người lao động 237 tỷ chậm hoàn ứng", 2, 2), ("R6", "Lãi huy động tăng 100 điểm cơ bản", 2, 3),
        ("R7", "Thịt nhập giá rẻ đặt trần giá", 4, 2)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.11, 0.27, 0.42, 0.64])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R2": (-0.2, 0.18), "R4": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 9 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    fig.text(0.57, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.75)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7.2)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Chu kỳ giá heo và dịch bệnh chi phối rủi ro")
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 18/11/2026.", rk)
    plt.close(fig)

    adv = float((px.tail(63)["Price"] * px.tail(63)["Volume"]).median() / 1e9)
    print(f"12m Close lo={lo12:.0f} hi={hi12:.0f}; ADV median 63 phien (ty)={adv:.2f}")
    print(ff.round(0).to_string())


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
BREAK_BEFORE = ("1.", "4.", "5.", "Phụ lục A")


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
        page.insert_text((42, 34), "DBC — CTCP Tập đoàn Dabaco Việt Nam · Báo cáo Due Diligence · 18/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "DBC_DD_investor_report_20261118.md"), os.path.join(HERE, "DBC_DD_investor_report_20261118.pdf"))
