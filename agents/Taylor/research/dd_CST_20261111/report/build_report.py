"""Dựng hình + PDF cho báo cáo DD nhà đầu tư CST (11/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào: figs/fin_quarterly_bq.csv (tav2_bq.ticker_financial, CST 2023Q4–2026Q3), ../calc/px_cst.csv (tav2_bq.ticker),
../calc/model_out.json; số BCTC hard-code lấy từ ../REPORT.md (đã đối chiếu BCTC gốc).
Mỗi hình có CSV kèm theo trong figs/.
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")
CALC = os.path.join(HERE, "..", "calc")

NAVY, ACCENT, GREY, LIGHT = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4"
SK = "/home/trido/.claude/skills/dd-investor-report/fonts/"
FONT = SK + "BeVietnamPro-Regular.ttf"
FONT_B = SK + "BeVietnamPro-Bold.ttf"
FONT_SB = SK + "BeVietnamPro-SemiBold.ttf"

M = json.load(open(os.path.join(CALC, "model_out.json")))
PRICE, CENTER_POST, CENTER_PRE = 14_900, M["liq"]["by_size"]["0.3"]["center_post"], M["center"]
BEAR_POST, BULL_POST = M["liq"]["by_size"]["0.3"]["bear_post"], M["liq"]["by_size"]["0.3"]["bull_post"]
SHARES, B0 = 42_846_773, 961.322e9
BVPS = B0 / SHARES


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


def vn(x, nd=0):
    s = f"{x:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def qlabel(q):
    return q[4:] + "/" + q[2:4]


def photos():
    """Hero, khung ảnh (mỏ / trụ sở / than minh họa), từ ảnh website công ty + Wikimedia Commons."""
    import pandas as pd
    from PIL import Image, ImageDraw, ImageFont
    f_b, f_r = ImageFont.truetype(FONT_B, 34), ImageFont.truetype(FONT, 24)
    mine = Image.open(os.path.join(SRC, "banner-mo-than.jpg")).convert("RGB")
    W = 1440
    hero = mine.resize((W, int(mine.height * W / mine.width))).crop((0, 190, W, 190 + 400))
    ov = Image.new("RGBA", hero.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(160):
        d.line([(0, 400 - 160 + y), (W, 400 - 160 + y)], fill=(13, 27, 42, int(215 * y / 160)))
    hero = Image.alpha_composite(hero.convert("RGBA"), ov); d = ImageDraw.Draw(hero)
    d.text((36, 400 - 100), "Mỏ lộ thiên Cao Sơn · Cẩm Phả, Quảng Ninh", font=f_b, fill="white")
    d.text((36, 400 - 52), "Giấy phép tới 08/2045 · công suất thiết kế 4,5 triệu t/năm · P/B 0,66 · giá trên tâm giá trị 17,5%", font=f_r, fill=(226, 232, 240))
    hero.convert("RGB").save(os.path.join(FIGS, "fig_hero.png"))
    # khung 3 ảnh
    hq = Image.open(os.path.join(SRC, "header-cao-son.jpg")).convert("RGB")
    coal = Image.open(os.path.join(SRC, "coal.jpg")).convert("RGB")
    trucks = mine.crop((0, 330, 760, 747))
    H = 430
    ims = [("Xe tải khai thác tại mỏ (website công ty)", trucks), ("Trụ sở công ty (website công ty)", hq),
           ("Than antraxit — ảnh minh họa chung", coal.crop((0, 250, 960, 1250)))]
    ims = [(t, im.resize((int(im.width * H / im.height), H))) for t, im in ims]
    tot = sum(im.width for _, im in ims); gap = 14
    sc = (W - gap * 2) / tot
    ims = [(t, im.resize((int(im.width * sc), int(H * sc)))) for t, im in ims]
    h2 = ims[0][1].height
    panel = Image.new("RGB", (W, h2 + 44), "white"); pd_ = ImageDraw.Draw(panel); x = 0
    f_s = ImageFont.truetype(FONT, 20)
    for t, im in ims:
        panel.paste(im, (x, 0)); pd_.rectangle([x, 0, x + im.width - 1, im.height - 1], outline="#9AA5B1")
        pd_.text((x + 4, h2 + 10), t, font=f_s, fill="#333"); x += im.width + gap
    panel.save(os.path.join(FIGS, "fig_products.png"))
    pd.DataFrame([("fig_hero", "thancaoson.vn/assets/home/banner-mo-than.jpg"),
                  ("fig_products", "thancaoson.vn banner-mo-than.jpg; header-cao-son.webp; Wikimedia Commons File:Anthracite_chunk.JPG (Jakec, CC BY-SA 4.0)")],
                 columns=["hinh", "nguon"]).to_csv(os.path.join(FIGS, "fig_photos_sources.csv"), index=False)


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    photos()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0", "CF_Invest_P0", "Cash_P0", "StDebt_P0", "LtDebt_P0"]:
        fin[c] = fin[c] / 1e9
    fin = fin[fin["quarter"] >= "2024Q1"].reset_index(drop=True)
    fin["lab"] = fin["quarter"].map(qlabel)
    x = np.arange(len(fin)); is26 = fin["quarter"].str.startswith("2026").values

    # 1 doanh thu + biên gộp
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.bar(x, fin["Revenue_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    for i, v in enumerate(fin["Revenue_P0"]):
        ax.text(i, v + 40, vn(v), ha="center", fontsize=6.6)
    ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.set_ylabel("Doanh thu thuần quý, tỷ đồng"); ax.set_ylim(0, 3500)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(x, fin["GPM_P0"] * 100, color=GREY, ls="--", lw=1.2, label="Biên gộp 4 quý (cơ sở dữ liệu thị trường)")
    for q, v in {"2025Q3": 1.91, "2026Q3": 2.70}.items():
        i = int(fin.index[fin["quarter"] == q][0]); ax2.plot(i, v, "o", color=ACCENT, ms=7, zorder=5)
        ax2.annotate(vn(v, 2) + "%", (i, v), xytext=(-6, 8), textcoords="offset points", color=ACCENT, fontsize=8, fontweight="bold", ha="right")
    ax2.plot([], [], "o", color=ACCENT, label="Biên gộp quý theo BCTC")
    ax2.set_ylim(0, 10); ax2.set_ylabel("Biên gộp, %"); ax2.legend(loc="upper right", fontsize=7.2, frameon=False)
    ax.set_title("Doanh thu Q3/26 giảm 47,7% so cùng kỳ; biên gộp chỉ 2–3%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_01_revenue_margin", "Nguồn: tav2_bq.ticker_financial (Revenue_P0 theo quý, khớp BCTC Q3/2026 tr.5); biên gộp quý: BCTC Q3/2026 tr.5; đường nét đứt: chỉ số 4 quý của cơ sở dữ liệu (định nghĩa khác BCTC). Kéo 11/11/2026.",
         fin[["quarter", "Revenue_P0", "GPM_P0"]])
    plt.close(fig)

    # 2 LNST quý
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(x, fin["NP_P0"], color=np.where(fin["NP_P0"] < 0, ACCENT, np.where(is26, NAVY, LIGHT)), width=0.7)
    for i, v in enumerate(fin["NP_P0"]):
        ax.text(i, v + (3 if v >= 0 else -9), vn(v, 1), ha="center", fontsize=7, color="#333")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.set_ylabel("LNST, tỷ đồng"); ax.set_ylim(-60, 110)
    ax.set_title("LNST quý dao động từ −42,8 đến +94,0 tỷ; Q4 thường quyết định cả năm")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (3 quý 2026 cộng 15,88 tỷ, khớp BCTC 9T). Tổng 4 quý 2024 là 139,7 tỷ, số kiểm toán 2024 là 130,0 tỷ. Kéo 11/11/2026.",
         fin[["quarter", "NP_P0"]])
    plt.close(fig)

    # 3 CFO vs LNST theo quý + CFO vs capex theo năm
    sub = fin[fin["quarter"] >= "2025Q1"].reset_index(drop=True).copy()
    sub.loc[sub["quarter"] == "2026Q2", "CF_OA_P0"] = 284.9   # BCTC 6T 385,9 − Q1 101,0 (BQ thiếu quý này)
    xs = np.arange(len(sub)); w = 0.38
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1.55, 1]})
    a.bar(xs - w / 2, sub["NP_P0"], w, color=LIGHT, label="LNST"); a.bar(xs + w / 2, sub["CF_OA_P0"], w, color=NAVY, label="CFO")
    a.axhline(0, color="#555", lw=0.8); a.set_xticks(xs, sub["lab"], fontsize=7.2); a.set_ylabel("tỷ đồng / quý")
    a.legend(fontsize=7.2, frameon=False, loc="upper left"); a.set_title("CFO vs LNST theo quý", fontsize=9)
    yrs = ["2024", "2025", "9T/26"]; cfo = [289.6, 169.9, 583.3]; cap = [276.1, 359.2, 13.9]; xx = np.arange(3)
    b.bar(xx - w / 2, cfo, w, color=NAVY, label="CFO"); b.bar(xx + w / 2, cap, w, color=ACCENT, label="Capex")
    for i in range(3):
        b.text(i - w / 2, cfo[i] + 10, vn(cfo[i], 0), ha="center", fontsize=7); b.text(i + w / 2, cap[i] + 10, vn(cap[i], 0), ha="center", fontsize=7)
    b.set_xticks(xx, yrs, fontsize=7.5); b.legend(fontsize=7.2, frameon=False, loc="upper left"); b.set_title("CFO vs capex theo năm", fontsize=9); b.set_ylim(0, 700)
    fig.suptitle("CFO 9T/26 583 tỷ, nâng bởi xả tồn kho và dự phòng; capex gần như dừng", x=0.01, ha="left", fontsize=9.8, fontweight="bold")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    save(fig, "fig_03_cfo_npat_capex", "Nguồn: tav2_bq.ticker_financial (CFO, LNST theo quý; CFO Q2/26 = BCTC 6T 385,9 − Q1 101,0); năm: BCTC 2025 kiểm toán tr.9 và BCTC Q3/2026 tr.6 (capex 9T/26 13,9).",
         sub[["quarter", "NP_P0", "CF_OA_P0"]])
    pd.DataFrame({"nam": yrs, "cfo": cfo, "capex": cap}).to_csv(os.path.join(FIGS, "fig_03_cfo_capex_annual.csv"), index=False)
    plt.close(fig)

    # 4 tiền, vay, tiền ròng
    fin["debt"] = fin["StDebt_P0"] + fin["LtDebt_P0"]; fin["net_cash"] = fin["Cash_P0"] - fin["debt"]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(x - 0.2, fin["debt"], 0.4, color=LIGHT, label="Tổng vay"); ax.bar(x + 0.2, fin["Cash_P0"], 0.4, color=GREY, label="Tiền")
    ax.plot(x, fin["net_cash"], color=NAVY, marker="o", lw=1.6, label="Tiền ròng (âm = nợ ròng)")
    for i in (7, 10):
        ax.annotate(vn(fin["net_cash"].iloc[i]), (i, fin["net_cash"].iloc[i]), xytext=(0, -13 if fin["net_cash"].iloc[i] < 0 else 8), textcoords="offset points", ha="center", fontsize=7.8, color=NAVY, fontweight="bold")
    ax.axhline(0, color="#555", lw=0.8); ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.set_ylabel("tỷ đồng")
    ax.legend(fontsize=7.2, frameon=False, loc="upper left", ncol=3); ax.set_ylim(-620, 640)
    ax.set_title("Tiền ròng đảo từ −483 tỷ (cuối 2025) sang +66 tỷ (30/9/26), chủ yếu do mùa vụ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_debt", "Nguồn: tav2_bq.ticker_financial (vay ngắn + dài hạn, tiền); 31/12/25 và 30/9/26 khớp BCTC (vay 485,1 / 129,5; tiền 1,9 / 195,9).",
         fin[["quarter", "debt", "Cash_P0", "net_cash"]])
    plt.close(fig)

    # 5 giá 12 tháng + khối lượng
    px = pd.read_csv(os.path.join(CALC, "px_cst.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-11-11"].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.8), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.plot(pd.Timestamp("2026-11-11"), PRICE, "o", color=ACCENT, ms=5)
    ymax = px["Close"].max()
    for k, (d, s, dx) in enumerate([("2026-11-03", "03/11: KL tăng ~5 lần", "r"), ("2026-11-04", "04/11: công văn TKV", "r"), ("2026-11-06", "06/11: NQ HĐQT triệu tập ĐHĐCĐ bất thường", "r")]):
        dd = pd.Timestamp(d); a1.axvline(dd, color=GREY, lw=0.8, ls=":")
        a1.text(pd.Timestamp("2026-10-31"), 16300 - 450 * k, s + " ", fontsize=6.8, color="#444", ha="right")
    a1.annotate("11/11: 14.900 (+18,3% so 06/11)", (pd.Timestamp("2026-11-11"), PRICE), xytext=(pd.Timestamp("2026-05-10"), 14500), fontsize=7, color=ACCENT,
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    a1.set_ylabel("đ/cp (điều chỉnh)"); a1.set_ylim(9300, 16700)
    a2.bar(px["time"], px["Volume"] / 1e3, color=GREY, width=1.0); a2.bar(pd.Timestamp("2026-11-11"), px["Volume"].iloc[-1] / 1e3, color=ACCENT, width=2)
    a2.set_ylabel("KL, nghìn cp")
    lo, hi = px["Close"].min(), px["Close"].max()
    a1.set_title(f"Giá 12 tháng: {vn(lo)}–{vn(hi)}; tăng mạnh từ 06/11 cùng khối lượng đột biến")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_05_price_12m", "Nguồn: tav2_bq.ticker (Close điều chỉnh, Volume) 11/11/2025–11/11/2026; sự kiện theo công bố thông tin của công ty (NQ HĐQT 40/NQ-TCS-HĐQT, 06/11/2026). Quan sát, không khẳng định quan hệ nhân quả.",
         px[["time", "Close", "Volume"]])
    plt.close(fig)

    # 6 football field (toàn bộ số lấy từ REPORT/model_out; hàng P/B nhân BVPS)
    S = M["sens"]; pbl, pbh = 0.53, 0.69
    rows = [
        ("3 kịch bản (bi quan – lạc quan), sau chiết khấu", BEAR_POST, BULL_POST, CENTER_POST),
        ("Lãi huy động ±100bp (beta = 1), trước chiết khấu", S["dep+100bp_b1"], S["dep-100bp_b1"], CENTER_PRE),
        ("Thu hồi sổ sách khi đóng mỏ 0% – 100%", S["rho_0"], S["rho_1.0"], CENTER_PRE),
        ("N chuẩn hoá: lõi (11.263) – theo chu kỳ (15.300–17.700)", 11263, 17700, None),
        ("Hai nền: V dài – V ngắn", M["V_dai"], M["V_ngan"], None),
        (f"Nhóm than TKV: P/B 0,53–0,69 × BVPS {vn(BVPS)}", pbl * BVPS, pbh * BVPS, 0.66 * BVPS),
        ("Vùng giá 12 tháng (điều chỉnh)", px["Close"].min(), px["Close"].max(), None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "diem_giua"])
    fig, ax = plt.subplots(figsize=(7.2, 3.25))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=ACCENT if i == 0 else NAVY, height=0.5, alpha=0.88)
        ax.text(r["thap"] - 300, yy, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(r["cao"] + 300, yy, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.3)
        if r["diem_giua"] == r["diem_giua"] and r["diem_giua"] is not None:
            ax.plot(r["diem_giua"], yy, "|", color="white", ms=13, mew=2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.2)
    for v, s, c, ls in ((PRICE, "Giá 11/11: 14.900", "#222", "-"), (CENTER_POST, f"Tâm sau chiết khấu: {vn(CENTER_POST)}", ACCENT, "--"), (0.85 * CENTER_POST, f"0,85 × tâm: {vn(0.85 * CENTER_POST)}", GREY, ":")):
        ax.axvline(v, color=c, ls=ls, lw=1.2, label=s)
    ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=3)
    ax.set_xlim(0, 24500); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá 14.900: trong vùng giá trị, trên tâm", fontsize=9.8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_football", "Nguồn: mô hình thu nhập thặng dư của nhóm nghiên cứu (model_out.json); P/B nhóm than TKV từ cơ sở dữ liệu thị trường 11/11/2026 (THT, NBC, MDC, TVD, HLC, MVB); BVPS = VCSH 961,3 tỷ / 42,85 triệu cp. Vạch trắng = tâm hoặc trung vị.", ff)
    plt.close(fig)

    # 7 ma trận rủi ro
    rk = pd.DataFrame([("K1", "Lãi định mức bị nén", 4, 5), ("K2", "Tái cơ cấu TKV", 2, 4), ("K3", "Quyết toán Q4 lệch", 3, 3), ("K4", "Sản lượng thấp kéo dài", 3, 3),
                       ("K5", "Nhiên liệu / Hormuz", 3, 3), ("K6", "Cổ tức không như kỳ vọng", 3, 2), ("K7", "Đóng mỏ sớm (2030)", 2, 2)],
                      columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j; ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"K3": (-0.3, 0.0), "K4": (0.3, 0.2), "K5": (0.3, -0.25), "K6": (0.0, 0.0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.13, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.5, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.5); ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Lãi định mức bị nén: rủi ro vừa dễ xảy ra vừa tác động lớn nhất")
    fig.tight_layout(rect=(0, 0.08, 0.72, 1))
    save(fig, "fig_06_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 11/11/2026.", rk)
    plt.close(fig)

    # 8 chuỗi giá trị
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(7.2, 2.5)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.grid(False)
    boxes = [(1, "CST\nkhai thác than lộ thiên\n(giá vốn cộng lãi định mức)", NAVY, "white"), (28, "Tuyển than Cửa Ông\nKho vận & Cảng Cẩm Phả\n(đơn vị TKV, 97,2% DT)", "#E6EBF1", "#1d2731"),
             (55, "TKV\nkinh doanh than\n+ than nhập pha trộn", "#E6EBF1", "#1d2731"), (80, "Người dùng cuối\nnhiệt điện (phần lớn)\nxi măng · phân bón · xuất khẩu", "#F6E3DE", "#1d2731")]
    for xx, t, fc, tc in boxes:
        ax.add_patch(FancyBboxPatch((xx, 8), 19, 24, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=GREY, lw=0.8))
        ax.text(xx + 9.5, 20, t, ha="center", va="center", fontsize=7, color=tc, fontweight="bold" if fc == NAVY else "normal")
    for xx in (20.6, 47.6, 74.6):
        ax.annotate("", xy=(xx + 6.2, 20), xytext=(xx, 20), arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.4))
    ax.text(50, 3, "Doanh thu và chi phí quyết toán với TKV vào cuối năm (Q3/2026 tr.8); công thức đơn giá không công bố", ha="center", fontsize=7, color="#444")
    ax.set_title("Biên của CST là biên do TKV phân bổ, không phải biên thị trường", loc="left")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save(fig, "fig_chain", "Nguồn: BCTC Q3/2026 tr.8, tr.21–22; đọc ngành độc lập 11/11/2026 (cơ cấu người dùng cuối: phần lớn nhiệt điện).",
         pd.DataFrame({"khau": ["CST", "Tuyển than Cửa Ông / Kho vận & Cảng Cẩm Phả", "TKV", "Người dùng cuối"]}))
    plt.close(fig)

    # 9 khung KPI
    kp = [("Giá 11/11", "14.900"), ("Tâm giá trị", vn(CENTER_POST)), ("Vùng giá trị", f"{vn(BEAR_POST)}–{vn(BULL_POST)}"), ("Giá / tâm", "+17,5%"),
          ("P/B · P/E TTM", "0,66 · 8,5"), ("ROE 2025", "7,9%"), ("Vay · tiền ròng 30/9", "129,5 · +66,4 tỷ"), ("Biên gộp 9T/26", "2,2%")]
    fig, ax = plt.subplots(figsize=(7.2, 1.15)); ax.axis("off"); ax.set_xlim(0, 8); ax.set_ylim(0, 1); ax.grid(False)
    for i, (k, v) in enumerate(kp):
        ax.add_patch(plt.Rectangle((i + 0.03, 0.04), 0.94, 0.92, fc="#F3F5F7" if i != 3 else "#F6E3DE", ec=LIGHT, lw=0.8))
        ax.text(i + 0.5, 0.67, v, ha="center", va="center", fontsize=8.8 if len(v) < 12 else 7.4, fontweight="bold", color=NAVY if i != 3 else ACCENT)
        ax.text(i + 0.5, 0.25, k, ha="center", va="center", fontsize=6.4, color="#555")
    fig.tight_layout(pad=0.1)
    save(fig, "fig_kpi", "", pd.DataFrame(kp, columns=["chi_tieu", "gia_tri"]))
    plt.close(fig)
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
BREAK_BEFORE = ("1.", "6.", "Phụ lục A")


def md_to_html(md):
    import html as H
    import re
    def inl(s):
        s = H.escape(s, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        return re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"\1", s)
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
    md = "\n".join(l for l in md.split("\n") if not l.startswith("# "))
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
        page.insert_text((42, 34), "CST — CTCP Than Cao Sơn – TKV · Báo cáo Due Diligence · 11/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
        page.insert_text((A4.width - 160, 34), "Nhóm nghiên cứu", fontname="dv", fontsize=7.5, color=(0.4, 0.4, 0.4))
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
        pdf(os.path.join(HERE, "CST_DD_investor_report_20261111.md"), os.path.join(HERE, "CST_DD_investor_report_20261111.pdf"))
