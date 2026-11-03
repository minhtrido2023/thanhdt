"""Dựng biểu đồ + PDF cho báo cáo DD nhà đầu tư MVC (03/11/2026; skill dd-investor-report luật 1–19).
Số định giá: ../calc/valuation_out.txt, sotp_detail.csv, valuation_v2_out.txt (đã khoá md5 ở ../calc/LOCK_md5*.txt). Số BCTC: BCTC HN Q3/2026, KT 2025, SX 6T/2026.
Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]   (bản đồ: make_map_inputs.py)
Đầu vào figs/: fin_quarterly_bq.csv (tav2_bq.ticker_financial MVC; dòng 2026Q3 của BQ lặp Q2 nên thay bằng BCTC Q3), price_raw.csv (tav2_bq.ticker MVC).
Ảnh sản phẩm: src_img/ (vlxdbd.com.vn, 03/11/2026). Mỗi hình kèm CSV dữ liệu vẽ (figs/*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
IMGS = os.path.join(HERE, "src_img")
CALC = os.path.join(HERE, "..", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#3C7A5A"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 13_700                                     # đóng cửa 02/11/2026 (tav2_bq.ticker)
FV_LO, FV_HI, FV_MID = 14_566, 24_514, 19_540  # valuation_out.txt: r13% holding15%, phẳng … thực, điểm giữa
GRID = dict(p10=13_488, p90=26_993)
SC3 = {"Tích cực": (0.25, 34_538, 51_441), "Cơ sở": (0.50, 9_406, 19_942), "Tiêu cực": (0.25, 4_914, 6_729)}
PEERS = {"VLB": 3.65, "NNC": 4.83, "DHA": 5.43, "KSB": 7.13}   # PE TTM BQ 30/10/2026 (báo cáo ngành đá)
EPS_LO, EPS_HI = 2_725, 3_068                    # TTM ex-hoàn nhập Q4/25 (ước lượng) … theo BCTC


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": ["Be Vietnam Pro", "DejaVu Sans"], "font.size": 9, "axes.titlesize": 9.8,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#555", "axes.labelcolor": "#333", "xtick.color": "#333",
        "ytick.color": "#333", "figure.facecolor": "white", "savefig.facecolor": "white",
        "axes.grid": True, "grid.color": "#ECEFF2", "grid.linewidth": 0.8, "axes.axisbelow": True})
    return plt


def save(fig, name, source, df=None):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 125)), fontsize=6.4, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def vn(v, d=1):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def k(v):
    return f"{v/1000:,.1f}k".replace(".", ",")


def figs():
    import numpy as np
    import pandas as pd
    import matplotlib.patches as mp
    from PIL import Image
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    fin = fin[fin["quarter"] != "2026Q3"]                       # BQ lặp Q2 → thay bằng BCTC Q3/2026
    fin = pd.concat([fin, pd.DataFrame([{"quarter": "2026Q3", "Revenue_P0": 221.5e9, "NP_P0": 81.325e9, "GPM_P0": float("nan")}])], ignore_index=True)
    fin["q"] = fin["quarter"].str[4:] + "/" + fin["quarter"].str[2:4]
    fin["rev"] = fin["Revenue_P0"] / 1e9
    fin["np"] = fin["NP_P0"] / 1e9
    ann = {}
    for y in ("2022", "2023", "2024", "2025"):
        ann[y] = float(fin[fin["quarter"].str.startswith(y)]["np"].sum())
    ann["TTM"] = float(fin[fin["quarter"].isin(["2025Q4", "2026Q1", "2026Q2", "2026Q3"])]["np"].sum())

    # 00 HERO ---------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.15))
    band = fig.add_axes([0, 0.86, 1, 0.14]); band.axis("off")
    band.add_patch(mp.Rectangle((0, 0), 1, 1, fc=NAVY, transform=band.transAxes))
    band.text(0.015, 0.5, "MVC · Đá xây dựng, gạch, BOT — Bình Dương / Đồng Phú", color="white", fontsize=10.2, fontweight="bold", va="center")
    band.text(0.985, 0.5, "Giá 13,7k: dưới tâm giá trị", color="white", fontsize=10, fontweight="bold", va="center", ha="right",
              bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT, ec="none"))
    a = fig.add_axes([0.0, 0.15, 0.28, 0.66]); a.axis("off"); a.set_xlim(0, 3); a.set_ylim(0, 3.2)
    a.add_patch(mp.Polygon([[0.2, 0.9], [1.0, 2.4], [1.5, 1.7], [2.1, 2.6], [2.85, 0.9]], fc="#8A98A8", ec=NAVY, lw=0.8))
    for x, y, s in ((0.5, 0.75, 0.16), (0.85, 0.72, 0.12), (1.1, 0.76, 0.14)):
        a.add_patch(mp.Circle((x, y), s, fc=ACCENT, alpha=0.75, ec="none"))
    a.plot([0.05, 2.95], [0.6, 0.6], color="#B9C3CE", lw=1.2)
    a.text(1.5, 0.4, "Mỏ Tân Lập · ≈1,4 tr m³/năm", ha="center", fontsize=8.2, fontweight="bold", color=NAVY)
    a.text(1.5, 0.2, "+ 2 mỏ mới 1,5 tr m³/năm từ 2028\n(đầu tư dự kiến 1.500 tỷ)", ha="center", va="top", fontsize=6.4, color="#333")
    a.text(0.05, 3.1, "1 · NGÀNH NGHỀ", fontsize=7.6, fontweight="bold", color=ACCENT)
    b = fig.add_axes([0.35, 0.2, 0.30, 0.5])
    xs = list(ann.keys()); ys = list(ann.values())
    b.bar(xs, ys, color=[NAVY] * 4 + [ACCENT], width=0.62)
    for x, y in zip(xs, ys):
        b.text(x, y + 6, vn(y, 0), ha="center", fontsize=6.4, color="#333")
    b.set_ylim(0, 350); b.tick_params(labelsize=6.4); b.set_ylabel("LNST hợp nhất, tỷ đồng", fontsize=6.6)
    fig.text(0.35, 0.83, "2 · TĂNG TRƯỞNG", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.35, 0.81, "LNST 4 quý gần nhất 307 tỷ, gấp ≈4 lần 2023;\nnhờ biên gộp đá, ≈30% từ liên kết", fontsize=6.3, color="#333", va="top")
    c = fig.add_axes([0.71, 0.13, 0.23, 0.56])
    c.set_xlim(0, 1); c.set_ylim(0, 55_000); c.grid(False)
    for sp in ("left", "bottom"):
        c.spines[sp].set_visible(False)
    c.set_xticks([]); c.yaxis.tick_right(); c.tick_params(labelsize=6.4)
    c.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    c.add_patch(mp.Rectangle((0.08, GRID["p10"]), 0.42, GRID["p90"] - GRID["p10"], fc=GREEN, alpha=0.18, ec="none"))
    c.add_patch(mp.Rectangle((0.08, FV_LO), 0.42, FV_HI - FV_LO, fc=GREEN, alpha=0.85, ec="none"))
    c.text(0.29, (FV_LO + FV_HI) / 2, "giá trị\nhợp lý\n14,6–24,5k", ha="center", va="center", fontsize=6.0, color="white", fontweight="bold")
    c.add_patch(mp.Rectangle((0.6, SC3["Tiêu cực"][1]), 0.28, SC3["Tiêu cực"][2] - SC3["Tiêu cực"][1], fc="white", ec=GREY, hatch="////", lw=0.8))
    c.text(0.74, SC3["Tiêu cực"][1] - 1500, "tiêu cực\n4,9–6,7k", ha="center", va="top", fontsize=5.8, color="#555")
    c.axhline(PX, xmin=0.02, xmax=0.98, color=NAVY, lw=1.6)
    c.text(0.53, PX - 2600, "Giá 13,7k\n(02/11)", fontsize=6.2, color=NAVY, fontweight="bold", va="top")
    fig.text(0.70, 0.83, "3 · ĐỊNH GIÁ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.70, 0.81, "tâm ≈19,5k; giá thấp hơn 30%;\nphụ thuộc giá đá sau 2028", fontsize=6.3, color="#333", va="top")
    fig.text(0.01, 0.005, "Nguồn: BCTC hợp nhất Q3/2026, tav2_bq NP_P0 (cộng 4 quý); mô hình SOTP hữu hạn của nhóm (ước lượng; vùng đậm = kỳ vọng từ giá đá danh nghĩa phẳng tới giữ giá trị thực, "
             "vùng nhạt = P10–P90 của 18 tổ hợp); giá đóng cửa 02/11/2026.", fontsize=5.8, color="#666", va="bottom", wrap=True)
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200); plt.close(fig)
    pd.DataFrame([*[(f"lnst_{x}", round(y, 1), "BQ NP_P0 + BCTC Q3/26") for x, y in ann.items()], ("fv_lo_phang", FV_LO, "valuation_out"), ("fv_hi_thuc", FV_HI, "valuation_out"),
                  ("grid_p10", GRID["p10"], "valuation_out"), ("grid_p90", GRID["p90"], "valuation_out"), ("tieu_cuc_lo", SC3["Tiêu cực"][1], "valuation_out"),
                  ("tieu_cuc_hi", SC3["Tiêu cực"][2], "valuation_out"), ("gia_0211", PX, "tav2_bq.ticker")], columns=["chi_tieu", "gia_tri", "nguon"]).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)

    # 01 KPI ----------------------------------------------------------------
    kpi = [("Doanh thu thuần 9T/26", "659,4 tỷ", "+26% YoY; Q3 221,5 tỷ", "DT"), ("LNST hợp nhất 9T/26", "231,8 tỷ", "+123% YoY; Q3 81,3 tỷ", "LN"),
           ("Biên gộp 9T/26", "38,1%", "9T/25: 24,4%", "%"), ("Nợ ròng 30/9/26", "116,6 tỷ", "cuối 2025: tiền ròng 217 tỷ", "₫"),
           ("P/E TTM · P/B", "4,5× · 0,89×", "tại giá 02/11/2026", "×"), ("Hai mỏ mới", "1.500 tỷ", "1,5 tr m³/năm, dự kiến 2028", "M")]
    fig = plt.figure(figsize=(7.2, 2.2))
    for i, (t, v, n, ic) in enumerate(kpi):
        ax = fig.add_axes([0.01 + (i % 3) * 0.33, 0.53 - (i // 3) * 0.47, 0.31, 0.42]); ax.axis("off")
        ax.add_patch(mp.FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.02", fc="#F3F5F7", ec=LIGHT, transform=ax.transAxes))
        ax.add_patch(mp.Circle((0.14, 0.5), 0.1, fc=ACCENT if i in (3, 5) else NAVY, transform=ax.transAxes))
        ax.text(0.14, 0.5, ic, ha="center", va="center", color="white", fontsize=7.2, fontweight="bold", transform=ax.transAxes)
        ax.text(0.3, 0.72, t, fontsize=6.9, color="#555", transform=ax.transAxes)
        ax.text(0.3, 0.42, v, fontsize=11, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(0.3, 0.17, n, fontsize=6.3, color="#555", transform=ax.transAxes)
    fig.savefig(os.path.join(FIGS, "fig_01_kpi.png"), dpi=200); plt.close(fig)
    pd.DataFrame(kpi, columns=["chi_tieu", "gia_tri", "ghi_chu", "icon"]).to_csv(os.path.join(FIGS, "fig_01_kpi.csv"), index=False)

    # 02 Doanh thu + LNST quý -------------------------------------------------
    f2 = fin[fin["quarter"] >= "2023Q1"].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); x = np.arange(len(f2)); w = 0.4
    ax.bar(x - w / 2, f2["rev"], w, color=NAVY, label="Doanh thu thuần quý (tỷ)")
    ax.bar(x + w / 2, f2["np"], w, color=[ACCENT if q >= "2026Q1" else "#D98B7B" for q in f2["quarter"]], label="LNST hợp nhất quý (tỷ)")
    for xi, v in zip(x, f2["np"]):
        if v > 60:
            ax.text(xi + w / 2, v + 4, vn(v, 0), ha="center", fontsize=6.2)
    ax.set_xticks(x, f2["q"], fontsize=6.6, rotation=45); ax.set_ylabel("tỷ đồng"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("LNST quý Q3/2026 gấp 4 lần Q3/2023; doanh thu quý tăng ≈58%")
    fig.subplots_adjust(bottom=0.27, top=0.9)
    save(fig, "fig_02_quarterly", "Nguồn: tav2_bq.ticker_financial (Revenue_P0, NP_P0; khớp BCTC các quý) và BCTC hợp nhất Q3/2026 cho Q3/26 (dòng Q3/26 của cơ sở dữ liệu lặp Q2). Màu cam = 2026.",
         f2[["quarter", "rev", "np"]]); plt.close(fig)

    # 09 Nợ ròng và cam kết ------------------------------------------------------
    steps = [("Tiền ròng thô\n31/12/2025", 217.4), ("Tiền ròng thô\n30/9/2026", -50.0), ("Sau nghĩa vụ\nngoài vận hành", -116.6)]
    commits = [("Mỏ mới\ncòn lại", -1062.0), ("Cụm công\nnghiệp (≤)", -500.0), ("Mua NNC\nlên 51%", -72.0)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    for i, (n, v) in enumerate(steps):
        ax.bar(i, v, color=GREEN if v > 0 else NAVY, width=0.6); ax.text(i, v + (25 if v > 0 else -90), vn(v, 1), ha="center", fontsize=6.8)
    cum = -116.6
    for j, (n, v) in enumerate(commits):
        i = len(steps) + j
        ax.bar(i, v, bottom=cum, color=ACCENT, width=0.6); ax.text(i, cum + v - 90, vn(v, 0), ha="center", fontsize=6.8); cum += v
    i = len(steps) + len(commits)
    ax.bar(i, cum, color="#7A2E20", width=0.6); ax.text(i, cum - 90, vn(cum, 0), ha="center", fontsize=7, fontweight="bold")
    ax.set_xticks(range(i + 1), [n for n, _ in steps + commits] + ["Cam kết cộng dồn\n(trước dòng tiền HĐ)"], fontsize=6.2)
    ax.axhline(0, color="#333", lw=0.8); ax.set_ylabel("tỷ đồng"); ax.set_ylim(-2050, 330)
    ax.set_title("Tiền ròng 217 tỷ (cuối 2025) → nợ ròng 117 tỷ; cam kết đưa lên ≈1,75 nghìn tỷ")
    fig.subplots_adjust(bottom=0.27, top=0.9)
    save(fig, "fig_09_commitments", "Nguồn: BCTC hợp nhất Q3/2026 (tr.1–3, V.1, V.2, V.19, V.20); NQ ĐHĐCĐ 2026 (mỏ mới 1.500 tỷ, cụm công nghiệp ≤500 tỷ, mua NNC lên 51% ≈1,52 tr cp). Các khoản cam kết là ước lượng; chưa trừ dòng tiền hoạt động 2027–28.",
         pd.DataFrame(steps + commits + [("cam_ket_cong_don", round(cum, 1))], columns=["khoan", "ty"])); plt.close(fig)

    # 10 Cấu thành giá trị kịch bản cơ sở (điểm giữa phẳng–thực) ------------------
    sd = pd.read_csv(os.path.join(CALC, "sotp_detail.csv"))
    def mid(kb, col):
        return float(sd[(sd["kb"] == kb) & (sd["mode"] == "flat")][col].iloc[0] + sd[(sd["kb"] == kb) & (sd["mode"] == "real")][col].iloc[0]) / 2
    comp = [("Mỏ Tân Lập", mid("co_so", "A_TanLap")), ("Hai mỏ mới", mid("co_so", "B_moMoi")), ("Cổ phần NNC\n(sau holding)", mid("co_so", "NNC_stake")),
            ("BOT + gạch +\nQ4/26", mid("co_so", "C_BOT") + mid("co_so", "D_gach_xang") + mid("co_so", "Q4")),
            ("Đất nhà ở +\nMCC/NHC/ICD", mid("co_so", "LAND") + mid("co_so", "MCC_NHC_ICD")), ("Nợ ròng\n30/9/26", mid("co_so", "NETFIN"))]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); cum = 0
    for i, (n, v) in enumerate(comp):
        pv_ = v * 10   # tỷ → đ/cp (100 tr cp)
        ax.bar(i, abs(pv_), bottom=cum if pv_ > 0 else cum + pv_, color=NAVY if pv_ > 0 else ACCENT, width=0.6)
        ax.text(i, max(cum, cum + pv_) + 300, f"{vn(pv_, 0)}", ha="center", fontsize=6.8); cum += pv_
    ax.bar(len(comp), cum, color=GREEN, width=0.6); ax.text(len(comp), cum + 350, vn(cum, 0), ha="center", fontsize=7, fontweight="bold")
    ax.set_xticks(range(len(comp) + 1), [n for n, _ in comp] + ["Kịch bản cơ sở\n(điểm giữa)"], fontsize=6.2)
    ax.set_ylabel("đ/cp"); ax.set_ylim(0, 17_500); ax.set_title("Kịch bản cơ sở: Tân Lập và NNC tạo giá trị; hai mỏ mới gần như trung hoà")
    fig.subplots_adjust(bottom=0.27, top=0.9)
    save(fig, "fig_10_bridge", "Nguồn: ../calc/sotp_detail.csv (r 13%, holding 15%; điểm giữa hai đường giá đá; 100 tr cổ phiếu). Giá trị từng phần gồm cả vòng sở hữu chéo MVC–NNC. Ước lượng của nhóm.",
         pd.DataFrame([(n.replace("\n", " "), round(v * 10)) for n, v in comp] + [("tong_kb_co_so", round(cum))], columns=["thanh_phan", "dong_cp"])); plt.close(fig)

    # 11 Ba kịch bản -----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.4))
    names = list(SC3.keys())
    for i, n in enumerate(names):
        pr, lo, hi = SC3[n]
        ax.barh(i, hi - lo, left=lo, color=[GREEN, NAVY, ACCENT][i], height=0.5)
        ax.text(hi + 900, i, f"{k(lo)}–{k(hi)}  (xác suất {int(pr*100)}%)", va="center", fontsize=7)
    ax.axvline(FV_MID, color="#222", lw=1.2, ls="--"); ax.text(FV_MID + 400, 2.45, "tâm 19,5k", fontsize=6.8)
    ax.set_yticks(range(3), names); ax.invert_yaxis(); ax.set_xlim(0, 75_000)
    ax.xaxis.set_major_formatter(lambda v, p_: f"{v/1e3:.0f}k")
    ax.set_title("Ba kịch bản (đầu trái = giá đá danh nghĩa phẳng, đầu phải = giữ giá trị thực)")
    fig.subplots_adjust(left=0.12, bottom=0.2, top=0.88)
    save(fig, "fig_11_scenarios", "Nguồn: ../calc/valuation_out.txt (r 13%, holding 15%). Tiêu cực = xấu (20%) + rất xấu (5%), bình quân theo trọng số. Xác suất là nhận định của nhóm.",
         pd.DataFrame([(n, *SC3[n]) for n in names], columns=["kich_ban", "xac_suat", "gia_phang", "gia_thuc"])); plt.close(fig)

    # 12 Độ nhạy (tornado) ----------------------------------------------------------
    w_alt = {"tot": .15, "co_so": .45, "xau": .32, "rat_xau": .08}
    v = {m: {kb: float(sd[(sd["kb"] == kb) & (sd["mode"] == m)]["per_share"].iloc[0]) for kb in w_alt} for m in ("flat", "real")}
    alt = (sum(w_alt[kb] * v["flat"][kb] for kb in w_alt) + sum(w_alt[kb] * v["real"][kb] for kb in w_alt)) / 2
    sens = [("Xác suất tiêu cực 40% (thay vì 25%)", alt - FV_MID, 0), ("Hệ số giá MVC/NNC 0,80 / 0,95", -3346, 3853), ("Mỏ mới chi phí 165k/m³", -2309, 0),
            ("Mỏ mới: capex +30%", -2184, 0), ("Cụm công nghiệp 500 tỷ, thu hồi 50%", -2125, 0), ("Hạn giấy phép Tân Lập 2035 / 2045", -1837, 457),
            ("Chi phí mỏ cũ +15% / −15%", -1514, 1555), ("Đất dự án nhà ở = 0", -1560, 0), ("Mỏ mới trễ 1 năm (kịch bản cơ sở)", -470, 0)]
    sens.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    for i, (n, lo, hi) in enumerate(sens):
        ax.barh(i, lo, color=ACCENT, height=0.55)
        if hi:
            ax.barh(i, hi, color=GREEN, height=0.55)
        ax.text(min(lo, 0) - 150, i, f"{lo:,.0f}".replace(",", "."), ha="right", va="center", fontsize=6.4)
        if hi:
            ax.text(hi + 150, i, f"+{hi:,.0f}".replace(",", "."), ha="left", va="center", fontsize=6.4)
    ax.set_yticks(range(len(sens)), [n for n, _, _ in sens], fontsize=6.6); ax.invert_yaxis(); ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlim(-7_500, 5_500); ax.set_xlabel("thay đổi so với tâm 19.540 đ/cp")
    ax.set_title("Xác suất kịch bản và hệ số giá bán nhạy nhất; giả định mỏ mới đứng sau")
    fig.subplots_adjust(left=0.36, bottom=0.24, top=0.9)
    save(fig, "fig_12_sensitivity", "Nguồn: ../calc/valuation_out.txt (độ nhạy), ../calc/valuation_v2_out.txt (trễ 1 năm, cụm công nghiệp; ước lượng), trọng số 15/45/32/8 tính từ sotp_detail.csv. Mỗi dòng đổi MỘT giả định.",
         pd.DataFrame(sens, columns=["gia_dinh", "giam", "tang"]).round(0)); plt.close(fig)

    # 13 Football field -----------------------------------------------------------
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    p12 = px[px["time"] >= "2025-11-03"]
    ff = [("Giá 12 tháng", p12["Close"].min(), p12["Close"].max()),
          ("P/E nhóm 3,7–7,1× nhân EPS TTM 2.725–3.068", PEERS["VLB"] * EPS_LO, PEERS["KSB"] * EPS_HI),
          ("SOTP: ba kịch bản (tiêu cực → tích cực)", SC3["Tiêu cực"][1], SC3["Tích cực"][2]),
          ("SOTP: lưới 18 tổ hợp P10–P90", GRID["p10"], GRID["p90"]),
          ("SOTP: vùng hợp lý (phẳng → thực)", FV_LO, FV_HI)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    for i, (n, lo, hi) in enumerate(ff):
        ax.barh(i, hi - lo, left=lo, color=GREEN if i == 4 else NAVY, alpha=1 if i == 4 else 0.7, height=0.5)
        ax.text(hi + 700, i, f"{k(lo)}–{k(hi)}", va="center", fontsize=6.8)
    ax.axvline(PX, color=ACCENT, lw=1.6); ax.text(PX - 400, -0.62, "giá 13,7k", color=ACCENT, ha="right", fontsize=6.8, fontweight="bold")
    ax.axvline(FV_MID, color=GREY, lw=1, ls="--"); ax.text(FV_MID + 300, -0.62, "tâm 19,5k", fontsize=6.4, color="#555")
    ax.set_ylim(-0.9, len(ff) - 0.5)
    ax.set_yticks(range(len(ff)), [n for n, _, _ in ff], fontsize=6.6); ax.set_xlim(0, 58_000)
    ax.xaxis.set_major_formatter(lambda v_, p_: f"{v_/1e3:.0f}k"); ax.set_title("Football field (đ/cp)")
    fig.subplots_adjust(left=0.36, bottom=0.24, top=0.9)
    save(fig, "fig_13_football_field", "Nguồn: tav2_bq.ticker (giá 03/11/2025–02/11/2026); PE TTM nhóm BQ 30/10/2026; EPS TTM theo BCTC (3.068) và ex-hoàn nhập Q4/25 (2.725, ước lượng); SOTP ../calc/valuation_out.txt. Giá chỉ để đối chiếu.",
         pd.DataFrame(ff, columns=["phuong_phap", "thap", "cao"]).round(0)); plt.close(fig)

    # 15 Giá 12T + công bố KQKD --------------------------------------------------
    p2 = px[px["time"] >= "2025-07-01"]
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.plot(p2["time"], p2["Close"], color=NAVY, lw=1.4)
    evs = [("2025-10-22", "KQ Q3/25"), ("2026-01-21", "KQ Q4/25"), ("2026-05-04", "KQ Q1/26"), ("2026-07-30", "KQ Q2/26"), ("2026-10-30", "KQ Q3/26")]
    for d, t in evs:
        d = pd.Timestamp(d); ax.axvline(d, color=GREY, lw=0.8, ls="--"); ax.text(d, p2["Close"].max() * 1.02, t, fontsize=6.2, ha="center")
    ax.yaxis.set_major_formatter(lambda v_, p_: f"{v_/1e3:.0f}k"); ax.set_ylim(p2["Close"].min() * 0.9, p2["Close"].max() * 1.1)
    ax.set_title(f"Giá cổ phiếu 12 tháng: biên độ {k(p12['Close'].min())}–{k(p12['Close'].max())}")
    fig.subplots_adjust(bottom=0.14, top=0.88)
    save(fig, "fig_15_price", "Nguồn: tav2_bq.ticker MVC Close 01/07/2025–02/11/2026; ngày công bố = Release_Date (tav2_bq.ticker_financial) và CBTT Q3/2026. Quan sát, không suy nhân quả; thanh khoản mỏng nên giá nhạy với lệnh lớn.",
         p2[["time", "Close", "Volume"]]); plt.close(fig)

    # 18 Lịch kiểm chứng --------------------------------------------------------------
    cats = [("2027-01-25", "BCTC Q4/2026\n(≈20–30/01/2027)"), ("2027-04-25", "BCTC Q1/2027\n(≈04/2027)"), ("2027-06-30", "Giấy phép mỏ mới?\n(mốc 30/06/2027)"),
            ("2027-08-31", "Giá đá Sở XD Đồng Nai\nQ2/27 vs Q3/26")]
    fig, ax = plt.subplots(figsize=(7.2, 1.9)); ax.axis("off")
    ds = [pd.Timestamp(d) for d, _ in cats]; t0, t1 = pd.Timestamp("2026-11-01"), pd.Timestamp("2027-09-30")
    ax.set_xlim(t0, t1); ax.set_ylim(-1.3, 1.3); ax.plot([t0, t1], [0, 0], color=NAVY, lw=2)
    for i, (d, (_, t)) in enumerate(zip(ds, cats)):
        up = 1 if i % 2 == 0 else -1
        ax.plot(d, 0, "o", color=ACCENT, ms=6); ax.plot([d, d], [0, 0.35 * up], color=GREY, lw=0.8)
        ax.text(d, 0.42 * up, t, ha="center", va="bottom" if up > 0 else "top", fontsize=6.3)
    save(fig, "fig_18_catalysts", "Nguồn: lịch công bố BCTC theo quy định (ngày là ước lượng); giá Sở Xây dựng, giấy phép mỏ theo dõi từ nguồn công khai.",
         pd.DataFrame(cats, columns=["ngay", "moc"])); plt.close(fig)

    # 21/22 Ảnh sản phẩm (website công ty) ------------------------------------------------
    def white(im):
        im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); return bg.convert("RGB")
    def panel(files, labels, name, source, ncols):
        fig, axs = plt.subplots(1, ncols, figsize=(7.2, 1.95))
        for ax_, f, lab in zip(axs, files, labels):
            ax_.imshow(white(Image.open(os.path.join(IMGS, f)))); ax_.axis("off"); ax_.grid(False)
            ax_.set_title(lab, fontsize=6.8, fontweight="bold", loc="center", color=NAVY)
        fig.subplots_adjust(left=0.01, right=0.99, bottom=0.07, top=0.84, wspace=0.04)
        save(fig, name, source, pd.DataFrame({"anh": files, "chu_thich": [l.replace("\n", " ") for l in labels]})); plt.close(fig)
    panel(["da-1-x-21676446862_215x185.png", "da-4x61676447460_215x185.png", "da-0-x-41676446334_215x185.png", "da-mi-san1676445048_215x185.png"],
          ["Đá 1x2\ncốt liệu bê tông, nhựa", "Đá 4x6\nbê tông lót, móng", "Đá 0x4\nmóng, nền đường", "Đá mi sàng\nvữa, gạch, san lấp"], "fig_21_products_stone",
          "Ảnh: trang sản phẩm website vlxdbd.com.vn (03/11/2026). Công dụng theo mô tả thông dụng của sản phẩm, công ty không công bố cơ cấu sản lượng.", 4)
    panel(["gach-dinh-dac1679651710_215x185.png", "gach-ong-4-lo1679651585_215x185.png", "gach-block-2-lo1679651343_215x185.png"],
          ["Gạch đinh đặc", "Gạch ống 4 lỗ", "Gạch block 2 lỗ"], "fig_22_products_brick",
          "Ảnh: trang sản phẩm website vlxdbd.com.vn (03/11/2026). Công suất gạch 200 tr viên/năm (BCTN 2025); mỏ sét Long Nguyên.", 3)
    print("figs ok")


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
BANNER_W = 511   # = bề rộng vùng nội dung A4 (595 − 2×42)
BREAK_BEFORE = ("4.", "7.")


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
        if s.startswith("<!--"):   # ghi chú nội bộ của file (gợi ý tiêu đề email) — không in
            close(); i += 1; continue
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
    body = md_to_html(md)
    # luật 13: banner tiêu đề (ảnh, font Be Vietnam Pro + logo) thay h1 ở đầu trang 1, full-width vùng nội dung
    import re as _re
    from PIL import Image
    with Image.open(os.path.join(HERE, "figs/title_banner.png")) as im:
        bh = int(BANNER_W * im.height / im.width)
    body = _re.sub(r"<h1>.*?</h1>", f"<IMG figs/title_banner.png {bh} {BANNER_W}/>", body, count=1)
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
            m = re.fullmatch(r"<IMG (\S+) (\d+)(?: (\d+))?/>", part)
            if m:
                hh, ww = int(m.group(2)), int(m.group(3) or IMG_W)
                room = where.y1 - state["y"] - 12 if state["dev"] is not None else 0
                if room < hh and room >= 0.85 * hh:   # co nhẹ (≤15%) cho vừa trang thay vì để trống nửa trang
                    ww, hh = int(ww * room / hh), int(room)
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
                    long_tbl = "<table" in grp and grp.count("<tr") > 12   # bảng dài (phụ lục) được tách trang
                    if long_tbl and state["dev"] is not None and where.y1 - state["y"] < 90:
                        new_page()   # tránh để mồ côi tiêu đề + hàng đầu bảng ở đáy trang
                    place_html(grp, keep=("<table" in grp and not long_tbl)); k += 1
    writer.end_page()
    writer.close()
    doc = pymupdf.open(tmp)
    n = doc.page_count
    for k, page in enumerate(doc):
        page.insert_font(fontname="dv", fontfile=FONT)
        page.draw_line((42, 40), (A4.width - 42, 40), color=(0.12, 0.23, 0.37), width=0.6)
        page.insert_text((42, 34), "MVC — CTCP Vật liệu và Xây dựng Bình Dương · Báo cáo Due Diligence · 03/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "MVC_DD_investor_report_20261103.md"), os.path.join(HERE, "MVC_DD_investor_report_20261103.pdf"))
