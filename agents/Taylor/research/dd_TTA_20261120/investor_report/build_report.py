"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư TTA (20/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|maps|pdf|all]
Đầu vào: figs/fin_quarterly_bq.csv (tav2_bq.ticker_financial TTA 2022Q1–2026Q3), ../model/data/px_tta.csv (tav2_bq.ticker TTA đến 19/11/2026),
  ../model/out_r3.json (mô hình định giá), figs/map_*_points.csv (toạ độ OSM Nominatim 20/11/2026), src/*.jpg + src/2020_08_logo.png
  (website truongthanhgroup.com.vn). Mỗi hình kèm CSV.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")
MODEL = os.path.join(HERE, "..", "model")
SKILL = "/home/trido/.claude/skills/dd-investor-report"
PY = "/home/trido/thanhdt/wc_venv/bin/python"

NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = SKILL + "/fonts/BeVietnamPro-Regular.ttf"
FONT_B = SKILL + "/fonts/BeVietnamPro-Bold.ttf"

R = json.load(open(os.path.join(MODEL, "out_r3.json"), encoding="utf-8"))
D = R["d_ref"]
PX = R["price"]["px"]
TAM_PRE, TAM = R["center"]["pre_liq"], R["center"]["post_liq"]
ZLO, ZHI = R["zones_post_liq"]["fair_low"], R["zones_post_liq"]["fair_high"]
KS = ["A", "B", "B'", "C"]
P = {"A": 0.15, "B": 0.25, "B'": 0.35, "C": 0.25}
SHORT = {"A": "A", "B": "B", "B'": "C", "C": "D"}   # nhãn bản nhà đầu tư (B' nội bộ = C; C nội bộ = D)
LAB = {"A": "A · Giữ giá FIT", "B": "B · Bầu Ngứ về FIT2", "B'": "C · Cả hai NM điều chỉnh", "C": "D · Cả hai về giá trần"}
VPRE = R["V"]["V1"]
VPOST = {k: round(v * (1 - D)) for k, v in VPRE.items()}
# phải thu Công ty Mua bán điện (EPTC) — BCTC kiểm toán 2025 tr.24; BCTC Q3/2025 tr.19; BCTC Q3/2026 tr.18
EPTC_AR = [("31/12/2024", 77.11), ("30/09/2025", 211.94), ("31/12/2025", 237.66), ("30/09/2026", 399.63)]


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


def maps():
    common = ["--source", "Ranh giới: geoBoundaries VNM-ADM1 (2008). Vị trí gần đúng theo xã/huyện (OSM Nominatim 20/11/2026), không phải ranh giấy phép."]
    subprocess.run([PY, "-I", os.path.join(HERE, "make_map_power.py"), "--points", os.path.join(FIGS, "map_north_points.csv"),
                    "--bbox", "103.6,20.8,106.2,22.3", "--highlight", "Yên Bái,Hà Nội",
                    "--title", "Yên Bái (nay thuộc Lào Cai): 3 nhà máy thuỷ điện", "--out", os.path.join(FIGS, "fig_03a_map_north.png")] + common, check=True)
    subprocess.run([PY, "-I", os.path.join(HERE, "make_map_power.py"), "--points", os.path.join(FIGS, "map_south_points.csv"),
                    "--bbox", "108.5,11.2,109.3,11.9", "--highlight", "Ninh Thuận",
                    "--title", "Ninh Thuận (nay thuộc Khánh Hoà): 2 trang trại điện mặt trời", "--out", os.path.join(FIGS, "fig_03b_map_south.png")] + common, check=True)
    from PIL import Image
    a, b = Image.open(os.path.join(FIGS, "fig_03a_map_north.png")).convert("RGB"), Image.open(os.path.join(FIGS, "fig_03b_map_south.png")).convert("RGB")
    h = 900
    a = a.resize((int(a.width * h / a.height), h)); b = b.resize((int(b.width * h / b.height), h))
    c = Image.new("RGB", (a.width + b.width + 20, h), "white"); c.paste(a, (0, 0)); c.paste(b, (a.width + 20, 0))
    c.save(os.path.join(FIGS, "fig_03_maps.png"))


def figs():
    import numpy as np
    import pandas as pd
    from PIL import Image, ImageDraw, ImageFont
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))

    # 0. HERO — ảnh Bầu Ngứ (website công ty) + thanh định giá sau thanh khoản
    im = Image.open(os.path.join(SRC, "2020_08_Ho-Bau-Ngu-cover.jpg")).convert("RGB")
    w, h = im.size
    im = im.crop((0, int(h * 0.12), w, int(h * 0.80)))
    fig = plt.figure(figsize=(7.2, 3.9))
    a0 = fig.add_axes([0.0, 0.47, 1.0, 0.53]); a0.imshow(im, aspect="auto"); a0.axis("off")
    a0.text(0.012, 0.93, "Trang trại điện mặt trời Hồ Bầu Ngứ (Ninh Thuận) · 61,77 MWp", transform=a0.transAxes, fontsize=9.4,
            color="white", fontweight="bold", va="top", bbox=dict(facecolor=NAVY, alpha=0.85, lw=0, pad=4))
    a0.text(0.988, 0.04, "Ảnh: website công ty", transform=a0.transAxes, fontsize=6.5, color="white", ha="right",
            bbox=dict(facecolor="black", alpha=0.35, lw=0, pad=1.5))
    a1 = fig.add_axes([0.06, 0.17, 0.90, 0.14]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xlim(0, 13_500); a1.set_ylim(0, 1)
    a1.barh(0.5, ZHI - ZLO, left=ZLO, height=0.55, color=LIGHT)
    for k in KS:
        a1.plot([VPOST[k]] * 2, [0.30, 0.70], color=GREY, lw=1.2)
        a1.text(VPOST[k], -0.42, SHORT[k], ha="center", fontsize=7.2, color="#555")
    a1.plot([TAM] * 2, [0.15, 0.85], color=NAVY, lw=2.4)
    a1.plot([PX] * 2, [0.05, 0.95], color=ACCENT, lw=2.4)
    a1.text(TAM, 1.05, f"Tâm giá trị {vn(TAM)}", ha="center", fontsize=7.8, color=NAVY, fontweight="bold")
    a1.text(PX, 1.05, f"Giá {vn(PX)}", ha="center", fontsize=7.8, color=ACCENT, fontweight="bold")
    a1.set_xticks([])
    fig.text(0.06, 0.40, f"Giá 19/11 nằm TRÊN vùng giá trị hợp lý {vn(ZLO)}–{vn(ZHI)} đ ({vn(PX / TAM, 2)} × tâm) · kết quả xoay quanh quyết định giá FIT",
             fontsize=7.8, color="#222")
    save(fig, "fig_00_hero", "Nguồn: ảnh website truongthanhgroup.com.vn; giá đóng cửa 19/11/2026 (HOSE); giá trị: DCF dòng tiền vốn chủ 4 kịch bản của nhóm nghiên cứu, sau chiết khấu thanh khoản (ước lượng).",
         pd.DataFrame({"muc": ["gia_19_11", "tam_sau_TK", "vung_thap", "vung_cao"] + [f"kb_{k}" for k in KS],
                       "dcp": [PX, TAM, ZLO, ZHI] + [VPOST[k] for k in KS]}))
    plt.close(fig)

    # 1. DT + LNST theo quý
    fin["lab"] = fin["quarter"].map(lambda q: q[4:] + "/" + q[2:4])
    sub = fin[fin["quarter"] >= "2023Q1"].reset_index(drop=True)
    x = np.arange(len(sub))
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.bar(x, sub["rev"] / 1e9, color=LIGHT, label="Doanh thu thuần")
    ax.bar(x, sub["np"] / 1e9, color=NAVY, width=0.5, label="LNST")
    for i, r in sub.iterrows():
        ax.text(i, r["np"] / 1e9 + 3, vn(r["np"] / 1e9), ha="center", fontsize=6.6, color=NAVY)
    ax.set_xticks(x, sub["lab"], fontsize=7); ax.set_ylabel("tỷ đồng")
    ax.legend(fontsize=7.4, frameon=False, loc="upper left", ncol=2)
    ax.set_title("Lợi nhuận kế toán ổn định và tăng: 9T/2026 LNST 206,7 tỷ (+9,7%)")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_01_rev_np", "Nguồn: tav2_bq.ticker_financial (đối chiếu BCTC tổng hợp Q3/2026: DT 9T 575,3 tỷ, LNST 206,7 tỷ). LNST trước chia lợi nhuận hợp tác kinh doanh và quỹ.",
         sub[["quarter", "rev", "np"]])
    plt.close(fig)

    # 2. Phải thu EPTC + tỷ lệ tiền thu
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw={"width_ratios": [1.5, 1]})
    ax.bar(range(4), [v for _, v in EPTC_AR], color=[GREY, GREY, GREY, ACCENT], width=0.55)
    for i, (_, v) in enumerate(EPTC_AR):
        ax.text(i, v + 8, vn(v, 1), ha="center", fontsize=7.6)
    ax.set_xticks(range(4), [d for d, _ in EPTC_AR], fontsize=7); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 460)
    ax.set_title("Phải thu bên mua điện tăng 5,2 lần trong 21 tháng")
    pay = R["eptc_pay"]
    ax2.bar([0, 1], [pay["9T/2025"]["ratio"] * 100, pay["9T/2026"]["ratio"] * 100], color=[GREY, ACCENT], width=0.5)
    for i, k in enumerate(["9T/2025", "9T/2026"]):
        ax2.text(i, pay[k]["ratio"] * 100 + 2, vn(pay[k]["ratio"] * 100, 1) + "%", ha="center", fontsize=8, fontweight="bold")
    ax2.axhline(100, color=GREEN, lw=1, ls="--"); ax2.text(1.35, 96, "trả đủ", fontsize=6.8, color=GREEN, ha="right")
    ax2.set_xticks([0, 1], ["9T/2025", "9T/2026"]); ax2.set_ylim(0, 110); ax2.set_ylabel("% hoá đơn mặt trời được trả")
    ax2.set_title("Tỷ lệ tiền thu (ước lượng)")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_02_eptc", "Nguồn: phải thu Công ty Mua bán điện — BCTC kiểm toán 2025 tr.24, BCTC Q3/2025 tr.19, Q3/2026 tr.18. Tỷ lệ = 1 − tăng phải thu/(DT khu vực Ninh Thuận × 1,08 VAT); giả định toàn bộ phần tăng phải thu là điện mặt trời (ước lượng).",
         pd.DataFrame({"ngay": [d for d, _ in EPTC_AR], "phai_thu_eptc_ty": [v for _, v in EPTC_AR]}))
    plt.close(fig)

    # 4. Ảnh 4 nhà máy (website công ty)
    items = [("2015_03_3.jpg", "Ngòi Hút 2 · 48 MW · thuỷ điện"), ("2020_10_unnamed-1.jpg", "Pá Hu · 26 MW · thuỷ điện"),
             ("2020_08_Ho-Bau-Ngu.jpg", "Hồ Bầu Ngứ · 61,77 MWp · mặt trời"), ("2021_10_Can-canh-tram-dien-HNM-1-adjusted.jpg", "Hồ Núi Một 1 · 50 MWp · mặt trời")]
    W, H, pad, cap = 700, 440, 14, 52
    canvas = Image.new("RGB", (2 * W + 3 * pad, 2 * (H + cap) + 3 * pad + 40), "white")
    dr = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(FONT_B, 26); fr = ImageFont.truetype(FONT, 20)
    for k, (f, c) in enumerate(items):
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        r_ = max(W / im.width, H / im.height); im = im.resize((int(im.width * r_) + 1, int(im.height * r_) + 1))
        l, t = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((l, t, l + W, t + H))
        x0, y0 = pad + (k % 2) * (W + pad), pad + (k // 2) * (H + cap + pad)
        canvas.paste(im, (x0, y0)); dr.rectangle([x0, y0, x0 + W - 1, y0 + H - 1], outline="#9AA5B1", width=2)
        dr.text((x0 + 4, y0 + H + 10), c, font=fb, fill=NAVY)
    dr.text((pad, canvas.height - 34), "Ảnh: website truongthanhgroup.com.vn (công ty tự công bố). Thuỷ điện tại Yên Bái; mặt trời tại Ninh Thuận.", font=fr, fill="#555")
    canvas.save(os.path.join(FIGS, "fig_04_photos.png"))
    pd.DataFrame({"anh": [c for _, c in items], "file": [f for f, _ in items], "nguon": "truongthanhgroup.com.vn/wp-content/uploads"}).to_csv(os.path.join(FIGS, "fig_04_photos.csv"), index=False)

    # 5. Thang giá bán điện (đ/kWh)
    ladder = [("Bầu Ngứ — FIT1 (9,35 US¢)", 2408, ACCENT), ("Núi Một 1 — FIT2 (7,09 US¢)", 1826, ACCENT),
              ("Trần chuyển tiếp mặt trời", 1185, GREY), ("Khung 2026 miền Nam/Trung (thấp)", 1104, GREY),
              ("Thuỷ điện nhỏ miền Bắc (biểu giá 2026)", 714, NAVY)]
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    for i, (n, v, c) in enumerate(ladder):
        ax.barh(i, v, color=c, height=0.55); ax.text(v + 25, i, vn(v), va="center", fontsize=7.8)
    ax.set_yticks(range(len(ladder)), [n for n, _, _ in ladder], fontsize=7.4); ax.invert_yaxis(); ax.set_xlim(0, 2800)
    ax.set_xlabel("đ/kWh (tỷ giá 25.755 cho giá USD)")
    ax.set_title("Giá FIT đang hưởng cao gấp 1,5–2 lần các mức giá thay thế")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_05_price_ladder", "Nguồn: QĐ 11/2017, QĐ 13/2020 (FIT1/FIT2); trần chuyển tiếp 1.184,90 đ/kWh (QĐ 21/QĐ-BCT 2023); khung 2026 và biểu giá thuỷ điện nhỏ (trung điểm 702–726): đọc ngành độc lập 20/11/2026.",
         pd.DataFrame({"muc": [n for n, _, _ in ladder], "dong_kwh": [v for _, v, _ in ladder]}))
    plt.close(fig)

    # 6. DSCR 2027 theo kịch bản
    ds = R["dscr_2027"]
    fig, ax = plt.subplots(figsize=(7.2, 2.4))
    vals = [ds[k][1] for k in KS]
    ax.bar(range(4), vals, color=[GREEN if v > 1.05 else (GOLD if v >= 0.95 else ACCENT) for v in vals], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, vn(v, 2), ha="center", fontsize=8, fontweight="bold")
    ax.axhline(1.0, color="#333", lw=1, ls="--"); ax.text(3.45, 1.02, "DSCR = 1", fontsize=6.8, ha="right")
    ax.set_xticks(range(4), [LAB[k] for k in KS], fontsize=7.2); ax.set_ylim(0, 1.5); ax.set_ylabel("lần")
    ax.set_title("Khả năng trả nợ 2027: dư ở kịch bản giữ giá, vừa đủ ở kịch bản trung tâm")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_06_dscr", "DSCR = (EBITDA − capex − thuế − chia lợi nhuận hợp tác kinh doanh) / (lãi + gốc 280 tỷ), năm 2027, chưa gồm tiền trả hồi tố. Nguồn: mô hình nhóm nghiên cứu trên BCTC Q3/2026 (ước lượng).",
         pd.DataFrame({"kich_ban": KS, "dscr": vals}))
    plt.close(fig)

    # 7. Football field — 4 kịch bản trước/sau thanh khoản + giá
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    rows = [(LAB[k] + f" ({int(P[k] * 100)}%)", VPOST[k], VPRE[k]) for k in KS]
    rows.append(("Kỳ vọng trọng số", TAM, TAM_PRE))
    for i, (n, a, b) in enumerate(rows):
        ax.barh(i, b, color=LIGHT, height=0.55); ax.barh(i, a, color=NAVY if i == 4 else GREY, height=0.32)
        ax.text(max(a, b) + 150, i, f"{vn(a)} (trước TK {vn(b)})", va="center", fontsize=7.2)
    ax.axvline(PX, color=ACCENT, lw=1.8); ax.text(PX + 120, -0.72, f"Giá 19/11: {vn(PX)}", color=ACCENT, ha="left", fontsize=7.6, fontweight="bold")
    ax.axvspan(ZLO, ZHI, color=GREEN, alpha=0.10); ax.text((ZLO + ZHI) / 2, 4.62, "vùng hợp lý", ha="center", fontsize=6.8, color=GREEN)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=7.4); ax.set_ylim(4.95, -1.05); ax.set_xlim(0, 16_500); ax.set_xlabel("đ/cổ phiếu")
    ax.set_title("Chỉ kịch bản giữ nguyên giá FIT cho giá trị trên giá hiện tại")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_football", f"DCF dòng tiền vốn chủ vòng đời hữu hạn từng nhà máy, r = 13,5%; thanh xám đậm = sau chiết khấu thanh khoản {vn(D * 100, 2)}% (lệnh 5 tỷ), nền nhạt = trước. Xác suất kịch bản là phán đoán (ước lượng).",
         pd.DataFrame({"kich_ban": [r[0] for r in rows], "sau_TK": [r[1] for r in rows], "truoc_TK": [r[2] for r in rows]}))
    plt.close(fig)

    # 8. Lưới độ nhạy xác suất
    g = R["grid_post_liq_V1"]; ra = list(g.keys()); cc = ["10%", "20%", "25%", "30%", "40%"]
    M = np.array([g[a] for a in ra])
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); ax.grid(False)
    ax.imshow(M, cmap="Blues", vmin=3000, vmax=11000, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, vn(M[i, j]), ha="center", va="center", fontsize=7.4, color="white" if M[i, j] > 7500 else "#222")
    ax.set_xticks(range(5), cc); ax.set_yticks(range(len(ra)), [f"{int(float(a) * 100)}%" for a in ra])
    ax.set_xlabel("Xác suất kịch bản D (cả hai về giá trần)"); ax.set_ylabel("Xác suất A (giữ FIT)")
    ax.set_title(f"Mọi tổ hợp xác suất hợp lý đều cho giá trị dưới giá 19/11 ({vn(PX)}); cao nhất {vn(R['grid_max'])}")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_grid", "Giá trị kỳ vọng sau chiết khấu thanh khoản (đ/cp); phần xác suất còn lại chia B:C = 1:1,4. Nguồn: mô hình nhóm nghiên cứu.",
         pd.DataFrame(M, index=ra, columns=cc).reset_index().rename(columns={"index": "P_A"}))
    plt.close(fig)

    # 9. Ma trận rủi ro
    risks = [("Văn bản hồi tố giá FIT", 0.45, 5), ("EVN tiếp tục giữ tiền", 0.6, 3.5), ("Tái cấp vốn/giãn nợ", 0.3, 4),
             ("Thuỷ văn xấu 2027", 0.35, 2.5), ("Tranh chấp kiểm soát", 0.25, 3), ("Giao dịch bên liên quan", 0.3, 2)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    for n, p, imp in risks:
        ax.scatter(p, imp, s=140, color=ACCENT if p * imp >= 1.2 else GOLD, alpha=0.85, edgecolor="white")
        ax.text(p + 0.015, imp + 0.12, n, fontsize=7.4)
    ax.set_xlim(0.1, 0.8); ax.set_ylim(1, 5.8); ax.set_xlabel("Xác suất 12 tháng (ước lượng)"); ax.set_ylabel("Tác động (1–5)")
    ax.set_title("Rủi ro tập trung ở quyết định giá FIT và dòng tiền từ bên mua")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_09_risk", "Xác suất và tác động là phán đoán định tính của nhóm nghiên cứu (ước lượng), không phải đo thống kê.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)
    print("figs ok; VPOST", VPOST)


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
BREAK_BEFORE = ("5.",)


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
        page.insert_text((42, 34), "TTA — Trường Thành · Báo cáo Due Diligence · 20/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
    if mode in ("maps", "all"):
        maps()
    if mode in ("figs", "all"):
        figs()
    if mode in ("pdf", "all"):
        pdf(os.path.join(HERE, "TTA_DD_investor_report_20261120.md"), os.path.join(HERE, "TTA_DD_investor_report_20261120.pdf"))
