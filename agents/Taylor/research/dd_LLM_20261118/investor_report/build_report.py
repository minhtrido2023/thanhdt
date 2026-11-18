"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư LLM (Lilama, 18/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào:
  figs/price_raw.csv            — tav2_bq.ticker (LLM Close/Price/Volume, 18/11/2025–18/11/2026), kéo 18/11/2026
  figs/fig_map_points_{bac,nam}.csv — toạ độ OSM Nominatim 18/11/2026; bản đồ dựng bằng tools/make_map_llm.py
  src/                          — logo + ảnh công trình tải từ lilama.com.vn ngày 18/11/2026
Số BCTC/định giá: ../REPORT.md (bản cuối, assumptions md5 aaaeec2149986398055371ea535850ea) + ../model/calc_output.txt (khối REV2).
Không tạo số định giá mới; mỗi hình kèm CSV (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")

NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#D4A017"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"  # luật 13
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung (nguồn: REPORT.md §0, §5, §8 + calc_output.txt khối REV2) ----
PX = 33_300                       # đóng cửa 18/11/2026 (BQ) = DNSE khớp cuối 14:59:55
CENTER, CENTER_PRE = 24_599, 27_332
ZONE = (3_630, 39_728)
THR85 = 20_909
SCEN = {"Xấu": (4_033, 3_630, 0.25), "Cơ sở": (30_577, 27_519, 0.50), "Tốt": (44_142, 39_728, 0.25)}
GPM_SENS = [(4.0, 23_846), (4.5, 24_599), (5.0, 25_351), (6.0, 26_857), (7.0, 28_362)]
GPM_BE = 10.28                    # breakeven: biên cơ sở để tâm = giá (calc: 0.1028)
RATE = {-100: 25_024, -50: 24_803, 50: 24_409, 100: 24_233}
LIQ = {0: 27_332, 5: 25_965, 10: 24_599, 20: 21_866}
WEIGHTS = [("25/50/25 (chọn)", 24_599), ("40/45/15", 19_795), ("50/40/10", 16_795), ("10/50/40", 30_013), ("chỉ cơ sở", 27_519)]
AUDIT = (17_573, 21_278, 22_746)  # xoá khoản mục con bị ngoại trừ + liên kết về 0 / chỉ khoản mục con / chỉ liên kết 50%
TRAPPED = {1.0: 24_599, 0.75: 21_496, 0.5: 18_392}
NFP_DCP = 18_390


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
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    lo12, hi12 = float(px["Close"].min()), float(px["Close"].max())
    last90 = px.tail(90)
    adv_shares = float(last90["Volume"].median())
    adv_bn = float((last90["Price"] * last90["Volume"]).median() / 1e9)

    # 0. Hero: ảnh công trình (website công ty) + thanh định giá
    fig = plt.figure(figsize=(7.2, 3.9))
    ims = [load_img("song_hau_1.jpg", (0, 0.05, 1, 0.95)),
           load_img("nhon_trach_21.jpg", (0, 0.08, 1, 0.92)),
           load_img("hydro.jpg", (0, 0.08, 1, 0.92))]
    caps = ["Nhiệt điện Sông Hậu 1 (tổng thầu EPC)", "LNG Nhơn Trạch 3&4 (liên danh)", "Module hydrogen NEOM (chế tạo)"]
    for k, (im, c) in enumerate(zip(ims, caps)):
        a = fig.add_axes([k / 3 + 0.003, 0.50, 1 / 3 - 0.006, 0.50]); a.imshow(im, aspect="auto"); a.axis("off")
        a.text(0.03, 0.06, c, transform=a.transAxes, fontsize=7.0, color="white", fontweight="bold",
               bbox=dict(facecolor=NAVY, alpha=0.82, lw=0, pad=2.5))
    fig.text(0.995, 0.985, "Ảnh: website công ty lilama.com.vn", fontsize=6.0, color="white", ha="right", va="top", bbox=dict(facecolor="black", alpha=0.4, lw=0, pad=1.5))
    a1 = fig.add_axes([0.05, 0.205, 0.90, 0.12]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xticks([]); a1.set_xlim(0, 44_000); a1.set_ylim(0, 1)
    a1.barh(0.5, ZONE[1] - ZONE[0], left=ZONE[0], height=0.55, color=LIGHT)
    a1.plot([CENTER] * 2, [0.18, 0.82], color=NAVY, lw=2.4)
    a1.plot([PX] * 2, [0.05, 0.95], color=ACCENT, lw=2.4)
    a1.plot([NFP_DCP] * 2, [0.25, 0.75], color=GREEN, lw=1.6, ls=":")
    a1.text(CENTER - 300, 1.05, f"Tâm giá trị {vn(CENTER)}", ha="right", fontsize=7.6, color=NAVY, fontweight="bold")
    a1.text(PX + 300, 1.05, f"Giá {vn(PX)} (1,35× tâm)", ha="left", fontsize=7.6, color=ACCENT, fontweight="bold")
    a1.text(NFP_DCP, -0.5, f"{vn(NFP_DCP)}\n(tài chính ròng/cp)", ha="center", va="top", fontsize=6.4, color=GREEN)
    a1.text(ZONE[0], -0.5, vn(ZONE[0]) + "\n(xấu)", ha="center", va="top", fontsize=6.8, color="#444")
    a1.text(ZONE[1], -0.5, vn(ZONE[1]) + "\n(tốt)", ha="center", va="top", fontsize=6.8, color="#444")
    fig.text(0.05, 0.425, "Nhà thầu lắp máy – EPC năng lượng · tài chính ròng 1.466 tỷ · LNTT 9T/26 có 290,5 tỷ một lần · kiểm toán ngoại trừ 3 năm",
             fontsize=7.3, color="#222")
    fig.text(0.05, 0.375, "Vùng giá trị hợp lý (đ/cp, sau chiết khấu thanh khoản 10%) và giá 18/11/2026", fontsize=7.2, color="#555")
    save(fig, "fig_00_hero", "Nguồn: ảnh từ website công ty (lilama.com.vn, tải 18/11/2026); giá tav2_bq.ticker 18/11/2026 (= DNSE khớp cuối 14:59); giá trị: mô hình tổng các phần của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia", "tam_sau_CK", "tai_chinh_rong_dcp", "vung_thap", "vung_cao"], "dcp": [PX, CENTER, NFP_DCP, ZONE[0], ZONE[1]]}))
    plt.close(fig)

    # 1. LNST mẹ năm + biên gộp năm (REPORT §0, §3)
    yrs = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "9T/26"]
    npat = [-163.1, -78.0, 55.5, 15.4, 10.2, 1.1, 87.8, 492.0, 695.0]
    gpm = [5.0, 5.9, 4.5, 5.3, 3.1, 2.4, 1.7, 7.0, 31.3]
    x = np.arange(len(yrs))
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(x, npat, color=[ACCENT if v < 0 else (NAVY if i >= 7 else LIGHT) for i, v in enumerate(npat)], width=0.66)
    for i, v in enumerate(npat):
        ax.text(i, v + (14 if v >= 0 else -42), vn(v, 1), ha="center", fontsize=7.0, color="#333")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(x, yrs); ax.set_ylabel("LNST cổ đông mẹ, tỷ đồng"); ax.set_ylim(-260, 820)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(x, gpm, color=GREEN, marker="o", ms=3.5, lw=1.3, label="Biên lợi nhuận gộp năm, % (trục phải)")
    ax2.axhline(4.5, color=GREEN, ls="--", lw=1.0)
    ax2.text(1.2, 7.4, "Trung vị lịch sử 4,5%", color=GREEN, fontsize=7.2, fontweight="bold", bbox=dict(facecolor="white", alpha=0.85, lw=0, pad=1))
    ax2.text(8.42, 31.0, "31,3%", color=GREEN, fontsize=7.4, ha="center", fontweight="bold")
    ax2.set_ylim(-10, 36); ax2.set_ylabel("Biên gộp, %")
    ax2.legend(loc="upper left", fontsize=7.2, frameon=False)
    ax.set_title("2018–2024 cộng dồn −71 tỷ; 2025–2026 bật mạnh cùng biên gộp quyết toán")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_npat_gpm", "Nguồn: tav2_bq.ticker_financial (LNST mẹ năm, biên gộp năm 2018–2025); BCTC hợp nhất Q3/2026 (9T/26: LNST mẹ 695,0 tỷ, biên gộp 31,3%).",
         pd.DataFrame({"nam": yrs, "lnst_me_ty": npat, "bien_gop_pct": gpm}))
    plt.close(fig)

    # 2. LNTT 9T/26: tách khoản một lần (REPORT §3)
    steps = [("LNTT 9T/26", 904.5, "tot"), ("Hoàn nhập dự phòng\nbảo hành ròng", -227.1, "d"), ("Lãi thanh lý\ntài sản cố định", -61.0, "d"),
             ("Hoàn nhập\nbảo hành khác", -2.3, "d"), ("LNTT sau khi bỏ\nkhoản một lần", 614.0, "tot"), ("LNTT 9T/25\n(so sánh)", 179.2, "ref")]
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    run = 0.0
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "tot":
            ax.bar(i, v, color=NAVY, width=0.6); run = v; top = v
        elif kind == "ref":
            ax.bar(i, v, color=GREY, width=0.6); top = v
        else:
            ax.bar(i, -v, bottom=run + v, color=ACCENT, width=0.6); top = run; run = run + v
        ax.text(i, top + 18, vn(v, 1), ha="center", fontsize=7.6, fontweight="bold")
    ax.set_xticks(range(len(steps)), [s[0] for s in steps], fontsize=7.2); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 1_020)
    ax.text(4, 760, "vẫn gồm biên gộp\nquyết toán 31,3%\n(Q3: 51,2%)", ha="center", fontsize=6.9, color=NAVY)
    ax.set_title("290,5 tỷ trong LNTT 9T/26 là khoản một lần đã gọi tên được")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_02_one_offs", "Nguồn: BCTC hợp nhất Q3/2026 (KQKD tr.5–6; TM31 chi phí bán hàng, TM33–34 thu nhập khác). Phần còn lại vẫn mang biên quyết toán dự án; BCTC không tách doanh thu theo dự án.",
         pd.DataFrame([(s[0].replace("\n", " "), s[1]) for s in steps], columns=["buoc", "ty_dong"]))
    plt.close(fig)

    # 3. Vị trí trong chuỗi giá trị (sơ đồ minh hoạ)
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(7.2, 2.9))
    ax = fig.add_axes([0, 0.08, 1, 0.92]); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 44)
    boxes = [(1, "Chủ đầu tư\nEVN, PV Power,\nPVN, TKV", "#6B4E3D"),
             (26, "Tổng thầu EPC\nnhà máy lớn: thường do\nnhà thầu nước ngoài\nđứng đầu liên danh", "#1565C0"),
             (51, "Lilama\nlắp đặt cơ khí – điện,\nchế tạo thiết bị,\nchạy thử", GREEN),
             (76, "Công ty liên kết\nhọ Lilama (35–41%)\nvà thầu phụ", ACCENT)]
    for x0, s, c in boxes:
        ax.add_patch(FancyBboxPatch((x0, 21), 21, 19, boxstyle="round,pad=0.6", fc=c, ec="none"))
        ax.text(x0 + 10.5, 30.5, s, ha="center", va="center", color="white", fontsize=7.2, fontweight="bold", linespacing=1.3)
    for xa in (22.6, 47.6, 72.6):
        ax.annotate("", xy=(xa + 3.2, 30.5), xytext=(xa, 30.5), arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.6))
    notes = [(11.5, "Phải thu 3 chủ đầu tư lớn\n2.269 / 3.102 tỷ"),
             (36.5, "Quảng Trạch II: liên danh\nPowerChina – Lilama"),
             (61.5, "Đứng đầu gói vừa: Ô Môn I\n(~1.949 tỷ, ký 09/2025)"),
             (86.5, "Phải trả Lilama 10\n137,4 tỷ")]
    for xc, s in notes:
        ax.text(xc, 12.5, s, ha="center", va="center", fontsize=6.9, color="#333", linespacing=1.3)
    ax.text(50, 3, "Xuất khẩu chế tạo: module hydrogen NEOM (Ả-Rập Xê-Út), module H2GS (Thuỵ Điển)", ha="center", fontsize=6.9, color="#555")
    save(fig, "fig_03_value_chain", "Sơ đồ minh hoạ của nhóm nghiên cứu. Nguồn: BCTC hợp nhất Q3/2026 (TM phải thu, TM18 người mua trả trước, TM phải trả), báo chí về Ô Môn I và Quảng Trạch II, đọc ngành độc lập 18/11/2026.",
         pd.DataFrame({"khau": [b[1].replace("\n", " ") for b in boxes], "ghi_chu": [n[1].replace("\n", " ") for n in notes]}))
    plt.close(fig)

    # 4. Ghép 2 bản đồ khu vực (đã dựng bằng tools/make_map_llm.py)
    from PIL import Image, ImageDraw, ImageFont
    ma, mb = Image.open(os.path.join(FIGS, "fig_04a_map_bac.png")).convert("RGB"), Image.open(os.path.join(FIGS, "fig_04b_map_nam.png")).convert("RGB")
    H = 900
    ma = ma.resize((int(ma.width * H / ma.height), H)); mb = mb.resize((int(mb.width * H / mb.height), H))
    W = ma.width + mb.width + 30
    cv = Image.new("RGB", (W, H), "white"); cv.paste(ma, (0, 0)); cv.paste(mb, (ma.width + 30, 0))
    cv.save(os.path.join(FIGS, "fig_04_map.png"))

    # 5. Khung ảnh công trình (website công ty)
    items = [("dsc_0033.jpg", (0, 0, 1, 1), "Nhiệt điện Vũng Áng 1", "Tổng thầu EPC, 1.200 MW (Hà Tĩnh)"),
             ("toancanh12camaucopy.jpg", (0.1, 0, 0.9, 1), "Điện khí Cà Mau 1&2", "Tổng thầu EPC, 2×750 MW"),
             ("quang_trach_ii_final.jpg", (0, 0, 1, 1), "LNG Quảng Trạch II (phối cảnh)", "Liên danh PowerChina – Lilama"),
             ("img_2495_copy.jpg", (0, 0, 1, 1), "Lọc dầu Nghi Sơn", "Lắp đặt cơ khí công nghiệp")]
    Ht = 330; tiles = []
    for f, box, t1, t2 in items:
        im = load_img(f, box); im = im.resize((int(im.width * Ht / im.height), Ht))
        tiles.append((im, t1, t2))
    W = 1440; gap = 12; tw = (W - gap * 5) // 4
    canvas = Image.new("RGB", (W, Ht + 150), "white"); d = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(FONT_B, 24); fr = ImageFont.truetype(FONT, 20); fs = ImageFont.truetype(FONT, 17)
    for k, (im, t1, t2) in enumerate(tiles):
        if im.width > tw:
            l = (im.width - tw) // 2; im = im.crop((l, 0, l + tw, Ht))
        else:
            im = im.resize((tw, int(im.height * tw / im.width))).crop((0, 0, tw, Ht))
        x0 = gap + k * (tw + gap); canvas.paste(im, (x0, 8)); d.rectangle([x0, 8, x0 + tw - 1, 8 + im.height - 1], outline="#D9DEE4", width=2)
        d.text((x0 + 4, Ht + 22), t1, font=fb, fill=NAVY); d.text((x0 + 4, Ht + 58), t2, font=fr, fill="#333")
    d.text((gap, Ht + 112), "Ảnh: website công ty lilama.com.vn, mục Dự án (tải 18/11/2026). Quảng Trạch II là ảnh phối cảnh do công ty công bố.", font=fs, fill="#666")
    canvas.save(os.path.join(FIGS, "fig_05_projects.png"))
    pd.DataFrame([(i[0], i[2], i[3]) for i in items], columns=["file", "cong_trinh", "vai_tro"]).to_csv(os.path.join(FIGS, "fig_05_projects.csv"), index=False)

    # 6. Cầu từ tiền mặt đến vị thế tài chính ròng (REPORT §5)
    steps = [("Tiền + tiền gửi", 3_576.0, "tot"), ("Vay ngắn hạn", -620.7, "d"), ("Tiền ròng", 2_955.7, "tot"),
             ("Tài sản vận hành\n(phải thu, tồn kho…)", 3_679.7, "u"), ("Nợ vận hành\n(phải trả, ứng trước,\nchi phí phải trả…)", -5_169.2, "d"),
             ("Tài chính ròng\nsau nợ vận hành", 1_466.2, "tot")]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    run = 0.0
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "tot":
            ax.bar(i, v, color=NAVY if i < 5 else GREEN, width=0.6); run = v; top = v
        elif kind == "u":
            ax.bar(i, v, bottom=run, color=GREY, width=0.6); run += v; top = run
        else:
            ax.bar(i, -v, bottom=run + v, color=ACCENT, width=0.6); top = run; run += v
        ax.text(i, top + 90, vn(v, 1), ha="center", fontsize=7.6, fontweight="bold")
    ax.set_xticks(range(len(steps)), [s[0] for s in steps], fontsize=6.9); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 7_400)
    ax.text(5, 2_150, "= 18.390 đ/cp", ha="center", fontsize=7.6, color=GREEN, fontweight="bold")
    ax.set_title("3,6 nghìn tỷ tiền, nhưng phần lớn là tiền của dự án: còn 1.466 tỷ sau nợ vận hành")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_06_net_financial", "Nguồn: BCTC hợp nhất Q3/2026 (BCĐKT tr.3–4; thuyết minh tr.21–22, 34–37). Theo BCTC riêng của công ty mẹ: 1.605,8 tỷ (cao hơn vì hợp nhất gánh 100% vay quá hạn của công ty con).",
         pd.DataFrame([(s[0].replace("\n", " "), s[1]) for s in steps], columns=["buoc", "ty_dong"]))
    plt.close(fig)

    # 7. CFO 9T/26: phần lớn từ vốn lưu động một lần (REPORT §5)
    cf = [("LN trước thay đổi\nvốn lưu động", 761.3), ("Giảm\ntồn kho", 440.9), ("Tăng phải trả\n(tạm ứng QT II,\nÔ Môn I)", 515.1),
          ("Tăng\nphải thu", -216.1), ("Thuế TNDN\nđã nộp", -225.3), ("Lãi vay\nđã trả", -39.1)]
    other = 1_231.3 - sum(v for _, v in cf)
    cf.append(("Khác", round(other, 1)))
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    run = 0.0
    for i, (lab, v) in enumerate(cf):
        c = NAVY if i == 0 else (GREY if v >= 0 else ACCENT)
        if i in (1, 2):
            c = GOLD
        ax.bar(i, v, bottom=run if v >= 0 else run + v, color=c, width=0.6)
        top = run + max(v, 0); run += v
        ax.text(i, top + 25, vn(v, 1), ha="center", fontsize=7.4, fontweight="bold")
    ax.bar(len(cf), 1_231.3, color=NAVY, width=0.6); ax.text(len(cf), 1_231.3 + 25, "1.231,3", ha="center", fontsize=7.6, fontweight="bold")
    ax.set_xticks(range(len(cf) + 1), [c[0] for c in cf] + ["CFO 9T/26"], fontsize=6.8); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 1_900)
    ax.set_title("CFO 9T/26 dương 1.231 tỷ chủ yếu nhờ tạm ứng mới và giải phóng tồn kho (màu vàng)")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_cfo", "Nguồn: BCTC hợp nhất Q3/2026 (LCTT tr.7). \"Khác\" = phần còn lại để khớp CFO. Cùng kỳ 9T/25: CFO −271,5 tỷ.",
         pd.DataFrame(cf + [("CFO 9T/26", 1_231.3)], columns=["muc", "ty_dong"]).assign(muc=lambda d: d["muc"].str.replace("\n", " ")))
    plt.close(fig)
    print("CFO other residual:", round(other, 1))

    # 8. Độ nhạy theo biên gộp cơ sở (tham số mạnh nhất)
    g = pd.DataFrame(GPM_SENS, columns=["bien_co_so_pct", "tam_dcp"])
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(g["bien_co_so_pct"], g["tam_dcp"], color=NAVY, marker="o", lw=1.8)
    ax.plot([7.0, GPM_BE], [28_362, PX], color=NAVY, ls="--", lw=1.2)
    ax.axhline(PX, color=ACCENT, lw=1.3); ax.text(3.8, PX + 500, f"Giá {vn(PX)}", color=ACCENT, fontsize=7.6, fontweight="bold")
    for v, lab in ((4.5, "Trung vị lịch sử\n4,5%: 24.599"), (7.0, "Năm 2025\n7,0%: 28.362"), (GPM_BE, "Hoà với giá\n10,3%")):
        ax.axvline(v, color=GREY, ls=":", lw=1)
        ax.text(v + 0.1, 19_300, lab, fontsize=7.0, color="#333")
    ax.set_xlim(3.5, 11.5); ax.set_ylim(18_500, 36_000)
    ax.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_xlabel("biên lợi nhuận gộp bền vững giả định ở kịch bản cơ sở, % (kịch bản tốt giữ 7%)")
    ax.set_ylabel("tâm giá trị, đ/cp")
    ax.set_title("Giá chỉ ngang tâm nếu biên gộp bền ≥10,3%, gấp 2,3 lần trung vị lịch sử")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_08_margin_sensitivity", "Nguồn: mô hình của nhóm nghiên cứu (ước lượng; sau chiết khấu thanh khoản 10%). Đoạn nét đứt nối tới điểm hoà vốn tính trong mô hình. Biên gộp 9T/26 31,3% là biên quyết toán, không dùng làm biên bền vững.",
         pd.concat([g, pd.DataFrame({"bien_co_so_pct": [GPM_BE], "tam_dcp": [PX]})]))
    plt.close(fig)

    # 9. Football field
    ff = pd.DataFrame([
        ("3 kịch bản xấu – tốt", ZONE[0], ZONE[1]),
        ("Trọng số kịch bản (5 bộ)", min(w[1] for w in WEIGHTS), max(w[1] for w in WEIGHTS)),
        ("Biên gộp cơ sở 4–7%", GPM_SENS[0][1], GPM_SENS[-1][1]),
        ("Tiền dùng được 50–100%", TRAPPED[0.5], TRAPPED[1.0]),
        ("Ngoại trừ kiểm toán (thử sức chịu)", AUDIT[0], AUDIT[2]),
        ("Chiết khấu thanh khoản 0–20%", LIQ[20], LIQ[0]),
        ("Lãi huy động 12T ±100 điểm cơ bản", RATE[100], RATE[-100]),
        ("Vùng giá 12 tháng", lo12, hi12)], columns=["phuong_phap", "thap", "cao"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i, r in ff.iterrows():
        yy_ = len(ff) - 1 - i
        ax.barh(yy_, r["cao"] - r["thap"], left=r["thap"], color=GREY if i == len(ff) - 1 else (LIGHT if i == 0 else NAVY), height=0.52)
        ax.text(r["thap"] - 400, yy_, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.2)
        ax.text(r["cao"] + 400, yy_, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.4)
    ax.axvline(CENTER, color=NAVY, ls="--", lw=1.1, label=f"Tâm giá trị {vn(CENTER/1e3, 1)}k")
    ax.axvline(THR85, color=GREEN, ls=":", lw=1.1, label=f"0,85 × tâm {vn(THR85/1e3, 1)}k")
    ax.axvline(PX, color=ACCENT, ls="-", lw=1.4, label=f"Giá {vn(PX/1e3, 1)}k (18/11/2026)")
    ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.22), ncol=3)
    ax.set_xlim(0, 46_000); ax.set_xlabel("đồng/cổ phiếu, sau chiết khấu thanh khoản 10%", fontsize=7.6)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá nằm trên mọi dải độ nhạy, chỉ còn dưới kịch bản tốt")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_09_football_field", "Nguồn: mô hình tổng các phần của nhóm nghiên cứu (ước lượng; 18/11/2026); vùng giá 12 tháng tav2_bq.ticker 18/11/2025–18/11/2026.", ff)
    plt.close(fig)

    # 10. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("R1", "Biên gộp về mức lịch sử sau quyết toán", 4, 4), ("R2", "Tiền không được phân phối / dùng kém hiệu quả", 3, 4),
        ("R3", "Nợ đọng chủ đầu tư nhà nước (Vũng Áng 1, TKV)", 3, 3), ("R4", "Ngoại trừ kiểm toán mở rộng / quyết toán CPH", 2, 3),
        ("R5", "Vay quá hạn công ty con ảnh hưởng công ty mẹ", 2, 2), ("R6", "Thanh khoản thấp, free float 2,12%", 5, 2),
        ("R7", "Tăng vốn giá thấp, pha loãng", 3, 2)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.11, 0.27, 0.40, 0.64])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R3": (0, 0.15), "R7": (0, -0.15)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 9 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    fig.text(0.55, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.0, va="top", ha="left", linespacing=1.75)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7.2)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Độ bền của biên gộp và việc dùng tiền chi phối rủi ro")
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu BCTC soát xét bán niên 2026 và đọc ngành độc lập 18/11/2026.", rk)
    plt.close(fig)

    print(f"12m Close lo={lo12:.0f} hi={hi12:.0f}; ADV 90 phien median cp={adv_shares:.0f}, ty={adv_bn:.3f}")
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
BREAK_BEFORE = ("1.", "4.", "6.", "Phụ lục A")


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
        page.insert_text((42, 34), "LLM — Tổng Công ty Lắp máy Việt Nam – CTCP (Lilama) · Báo cáo Due Diligence · 18/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "LLM_DD_investor_report_20261118.md"), os.path.join(HERE, "LLM_DD_investor_report_20261118.pdf"))
