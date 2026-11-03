"""Dựng biểu đồ + PDF cho báo cáo DD nhà đầu tư SCL (03/11/2026; skill dd-investor-report luật 1–21).
Số định giá: ../r2/calc/model_r2_out.json (khoá md5 ../r2/calc/LOCK_md5_r2.txt 22:34:41 TRƯỚC khi đọc giá) + compare_r2_out.json + reverse_r2_out.json.
Số BCTC: BCTC HN Q3/2026 (ký 15/10/2026), soát xét bán niên 2026, kiểm toán 2025. Lịch sử quý: ../r2/calc/fin_bq_scl.csv (tav2_bq.ticker_financial). Giá: ../r2/calc/px_scl.csv.
Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]   (bản đồ: make_map_inputs.py)
Ảnh: src_img/ (songdacaocuong.vn, tải 03/11/2026). Mỗi hình kèm CSV (figs/*.csv).
"""
import os
import sys
import json as _json

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
IMGS = os.path.join(HERE, "src_img")
CALC = os.path.join(HERE, "..", "r2", "calc")
NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#3C7A5A"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

M = _json.load(open(os.path.join(CALC, "model_r2_out.json")))
C = _json.load(open(os.path.join(CALC, "compare_r2_out.json")))
RV = _json.load(open(os.path.join(CALC, "reverse_r2_out.json")))
D = C["ref_discount"]
PX, TERP = C["px_cum"], C["terp"]
ZP = {q: round(v) for q, v in C["pct_post_liq"].items()}     # sau quyền, sau CK thanh khoản 1 tỷ
ZC = {q: round(v) for q, v in C["pct_cum_liq"].items()}      # trước quyền (cum), sau CK
TP, TC = round(C["tam_post_liq"]), round(C["tam_cum_liq"])
TP0, TC0 = round(M["tam_post"]), round(M["tam_cum"])
BR = {b: round(v * (1 - D)) for b, v in M["branch_post"].items()}
PEERS = {"VGC": 10.8, "VCS": 8.7, "PLC": 11.8, "DHA": 5.5, "NNC": 5.1, "HT1": 13.1, "KSB": 7.8, "BMP": 9.0}   # P/E TTM, tav2_bq 28/10/2026


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
    import pandas as pd
    import matplotlib.patches as mp
    from PIL import Image
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(CALC, "fin_bq_scl.csv"))
    fin = fin[fin["quarter"] >= "2023Q1"].copy()
    fin["q"] = fin["quarter"].str[4:] + "/" + fin["quarter"].str[2:4]
    hist = M["hist_npm"]
    npm_years = [(str(y), hist[str(y)] * 100) for y in range(2020, 2026)] + [("4Q gần nhất", M["npm_ttm"] * 100)]
    ann_np = {"2023": 45.3, "2024": 26.6, "2025": 64.3, "4Q gần nhất": 117.7}

    # 00 HERO ---------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.15))
    band = fig.add_axes([0, 0.86, 1, 0.14]); band.axis("off")
    band.add_patch(mp.Rectangle((0, 0), 1, 1, fc=NAVY, transform=band.transAxes))
    band.text(0.015, 0.5, "SCL · Tro bay, gạch nhẹ AAC, vữa — Chí Linh (Hải Phòng) / Vĩnh Tân (Lâm Đồng)", color="white", fontsize=9.4, fontweight="bold", va="center")
    band.text(0.985, 0.5, "Giá trên vùng hợp lý", color="white", fontsize=9.6, fontweight="bold", va="center", ha="right",
              bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT, ec="none"))
    a = fig.add_axes([0.0, 0.15, 0.28, 0.66]); a.axis("off"); a.set_xlim(0, 3); a.set_ylim(0, 3.2)
    a.add_patch(mp.Rectangle((0.25, 0.9), 0.5, 1.3, fc="#8A98A8", ec=NAVY, lw=0.8)); a.add_patch(mp.Rectangle((0.35, 2.2), 0.3, 0.5, fc="#8A98A8", ec=NAVY, lw=0.8))
    for i in range(3):
        for j in range(4):
            a.add_patch(mp.Rectangle((1.2 + i * 0.5, 0.9 + j * 0.36), 0.46, 0.32, fc=LIGHT, ec=NAVY, lw=0.6))
    a.annotate("", xy=(1.15, 1.5), xytext=(0.8, 1.5), arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.4))
    a.text(1.5, 0.55, "Tro xỉ nhiệt điện → tro bay, gạch nhẹ", ha="center", fontsize=7.4, fontweight="bold", color=NAVY)
    a.text(1.5, 0.35, "+ dự án Phả Lại 262,9 tỷ (đã chi 190,7)", ha="center", va="top", fontsize=6.3, color="#333")
    a.text(0.05, 3.1, "1 · NGÀNH NGHỀ", fontsize=7.6, fontweight="bold", color=ACCENT)
    b = fig.add_axes([0.35, 0.2, 0.30, 0.5])
    xs = list(ann_np.keys()); ys = list(ann_np.values())
    b.bar(xs, ys, color=[NAVY] * 3 + [ACCENT], width=0.62)
    for x, y in zip(xs, ys):
        b.text(x, y + 3, vn(y, 0), ha="center", fontsize=6.4, color="#333")
    b.set_ylim(0, 140); b.tick_params(labelsize=6.2); b.set_ylabel("LNST cổ đông mẹ, tỷ đồng", fontsize=6.6)
    fig.text(0.35, 0.83, "2 · TĂNG TRƯỞNG", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.35, 0.81, "LNST 4 quý gần nhất 118 tỷ, gấp 2,6 lần 2023;\nbiên ròng 12,7% là mức cao nhất 7 năm", fontsize=6.3, color="#333", va="top")
    c = fig.add_axes([0.71, 0.13, 0.23, 0.56])
    c.set_xlim(0, 1); c.set_ylim(10_000, 34_000); c.grid(False)
    for sp in ("left", "bottom"):
        c.spines[sp].set_visible(False)
    c.set_xticks([]); c.yaxis.tick_right(); c.tick_params(labelsize=6.4)
    c.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    c.add_patch(mp.Rectangle((0.08, ZC["10"]), 0.42, ZC["90"] - ZC["10"], fc=GREEN, alpha=0.25, ec="none"))
    c.add_patch(mp.Rectangle((0.08, ZC["25"]), 0.42, ZC["75"] - ZC["25"], fc=GREEN, alpha=0.85, ec="none"))
    c.text(0.53, (ZC["25"] + ZC["75"]) / 2, f"hợp lý\n{k(ZC['25'])}–{k(ZC['75'])}", ha="left", va="center", fontsize=5.8, color=GREEN, fontweight="bold")
    c.axhline(PX, xmin=0.02, xmax=0.98, color=NAVY, lw=1.6)
    c.text(0.53, PX + 500, "Giá 30,0k (03/11)", fontsize=6.2, color=NAVY, fontweight="bold", va="bottom")
    fig.text(0.70, 0.83, "3 · ĐỊNH GIÁ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.70, 0.81, f"tâm ≈{k(TC)} trước quyền (≈{k(TP)} sau);\ngiá cao hơn tâm {round((PX/TC-1)*100)}%", fontsize=6.3, color="#333", va="top")
    fig.text(0.01, 0.005, "Nguồn: BCTC hợp nhất Q3/2026; tav2_bq NP_P0 (cộng 4 quý); mô hình chuẩn hoá chu kỳ của nhóm (ước lượng; vùng đậm P25–P75, nhạt P10–P90, "
             "sau chiết khấu thanh khoản ở quy mô 1 tỷ đ; cơ sở trước quyền mua); giá đóng cửa 03/11/2026.", fontsize=5.8, color="#666", va="bottom", wrap=True)
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200); plt.close(fig)
    pd.DataFrame([*[(f"lnst_{x}", y, "BQ NP_P0 / BCTC") for x, y in ann_np.items()], ("tam_cum_liq", TC, "compare_r2_out.json"),
                  *[(f"cum_liq_p{q}", v, "compare_r2_out.json") for q, v in ZC.items()], ("gia_0311", PX, "tav2_bq.ticker 03/11/2026")],
                 columns=["chi_tieu", "gia_tri", "nguon"]).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)

    # 01 KPI ----------------------------------------------------------------
    kpi = [("Doanh thu thuần 9T/26", "665,5 tỷ", "+81% YoY; Q3 263,4 tỷ", "DT"), ("LNST cổ đông mẹ 9T/26", "94,4 tỷ", "+130% YoY; Q3 38,1 tỷ", "LN"),
           ("Biên gộp 9T/26", "40,1%", "9T/25: 36,1%", "%"), ("Nợ ròng 30/9/26", "321,4 tỷ", "1,4× EBITDA năm hoá 9T", "₫"),
           ("Dự án dở dang", "205,5 tỷ", "Phả Lại 190,7 + tách tro 14,8", "DA"), ("Quyền mua 100:15,4", "6,0 tr cp", "giá 12.500 đ; ĐKCC 10/11/2026", "Q")]
    fig = plt.figure(figsize=(7.2, 2.2))
    for i, (t, v, n, ic) in enumerate(kpi):
        ax = fig.add_axes([0.01 + (i % 3) * 0.33, 0.53 - (i // 3) * 0.47, 0.31, 0.42]); ax.axis("off")
        ax.add_patch(mp.FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.02", fc="#F3F5F7", ec=LIGHT, transform=ax.transAxes))
        ax.add_patch(mp.Circle((0.14, 0.5), 0.1, fc=ACCENT if i in (3, 5) else NAVY, transform=ax.transAxes))
        ax.text(0.14, 0.5, ic, ha="center", va="center", color="white", fontsize=7.0, fontweight="bold", transform=ax.transAxes)
        ax.text(0.3, 0.72, t, fontsize=6.9, color="#555", transform=ax.transAxes)
        ax.text(0.3, 0.42, v, fontsize=11, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(0.3, 0.17, n, fontsize=6.3, color="#555", transform=ax.transAxes)
    fig.savefig(os.path.join(FIGS, "fig_01_kpi.png"), dpi=200); plt.close(fig)
    pd.DataFrame(kpi, columns=["chi_tieu", "gia_tri", "ghi_chu", "icon"]).to_csv(os.path.join(FIGS, "fig_01_kpi.csv"), index=False)

    # 02 Doanh thu + LNST theo quý ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.bar(fin["q"], fin["rev"], color=LIGHT, label="Doanh thu gộp (tỷ đ)")
    ax2 = ax.twinx(); ax2.plot(fin["q"], fin["np"], color=ACCENT, marker="o", lw=1.6, label="LNST cổ đông mẹ (tỷ đ)"); ax2.grid(False)
    for x, y in zip(fin["q"], fin["np"]):
        ax2.text(x, y + 1.5, vn(y, 1), ha="center", fontsize=5.8, color=ACCENT)
    ax.tick_params(axis="x", labelsize=6.2, rotation=0); ax.set_ylabel("Doanh thu, tỷ đ", fontsize=7); ax2.set_ylabel("LNST, tỷ đ", fontsize=7, color=ACCENT)
    ax2.set_ylim(0, 48); ax.set_title("Doanh thu gấp đôi trong 4 quý; LNST quý đi ngang ≈38 tỷ ở Q2–Q3/2026")
    fig.subplots_adjust(bottom=0.17, top=0.88, right=0.92)
    save(fig, "fig_02_quarterly", "Nguồn: tav2_bq.ticker_financial (Revenue_P0 = doanh thu gộp; NP_P0 = LNST cổ đông mẹ), đối chiếu BCTC HN Q3/2026 (DT thuần Q3 263,4 tỷ; LNST 38,1 tỷ).",
         fin[["quarter", "rev", "np"]]); plt.close(fig)

    # 03 Biên ròng theo năm + chuẩn hoá chu kỳ -----------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xs = [x for x, _ in npm_years]; ys = [y for _, y in npm_years]
    ax.bar(xs, ys, color=[NAVY] * 6 + [ACCENT], width=0.6)
    for x, y in zip(xs, ys):
        ax.text(x, y + 0.25, vn(y, 1) + "%", ha="center", fontsize=6.6)
    for lab, key, col in (("TB 2020–nay", "2020-TTM", GREY), ("TB 2023–nay", "2023-TTM", GREEN)):
        v = M["npm_mean"][key] * 100
        ax.axhline(v, color=col, ls="--", lw=1); ax.text(6.45, v + 0.15, f"{lab} {vn(v, 1)}%", fontsize=6.4, color=col, ha="right")
    ax.set_ylim(0, 15); ax.set_ylabel("LNST / doanh thu gộp, %", fontsize=7)
    ax.set_title("Biên ròng 12,7% là đỉnh 7 năm; mô hình cho biên quay về trung bình chu kỳ theo xác suất")
    fig.subplots_adjust(bottom=0.24, top=0.88)
    save(fig, "fig_03_margin_cycle", "Nguồn: tav2_bq.ticker_financial (NP_P0 / Revenue_P0, cộng 4 quý mỗi năm). Chuẩn hoá: chu kỳ (xác suất 50%) quay về trung bình, hành chính (30%) quay nửa đường, cấu trúc (20%) giữ mức hiện tại — xác suất theo đọc ngành độc lập 29/10/2026.",
         pd.DataFrame(npm_years, columns=["nam", "bien_rong_pct"])); plt.close(fig)

    # 04 Cầu giá trị (đ/cp sau quyền) -----------------------------------------------------
    sp = 1e9 / (M["eq_parent"] * 0 + 44_836_815)
    v_ops = (M["v_total_pre"]) * sp
    steps = [("Hoạt động hiện hữu\n(chuẩn hoá chu kỳ)", v_ops), ("Dự án dở dang\ntheo giá vốn", M["cip_total"] * sp), ("Nợ vay tài\ntrợ dự án", -M["cip_total"] * sp),
             ("Tiền thu từ\nquyền mua", 75 * sp), ("Chiết khấu thanh\nkhoản (1 tỷ đ)", -TP0 * D)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7)); cum = 0
    for i, (lab, v) in enumerate(steps):
        ax.bar(i, v, bottom=cum if v >= 0 else cum + v, color=NAVY if i == 0 else (GREEN if v >= 0 else ACCENT), width=0.6)
        ax.text(i, (cum + v if v >= 0 else cum) + 300, ("+" if v >= 0 and i else "") + vn(v, 0), ha="center", fontsize=6.6)
        cum += v
    ax.bar(len(steps), cum, color=NAVY, width=0.6); ax.text(len(steps), cum + 300, vn(cum, 0), ha="center", fontsize=6.8, fontweight="bold")
    ax.set_xticks(range(len(steps) + 1)); ax.set_xticklabels([s[0] for s in steps] + ["Giá trị/cp\nsau quyền"], fontsize=6.2)
    ax.yaxis.set_major_formatter(lambda v_, p_: f"{v_/1e3:.0f}k"); ax.set_ylim(0, 30_000)
    ax.set_title("Dự án Phả Lại tính theo giá vốn: tài sản và khoản vay tài trợ nó bù trừ nhau")
    fig.subplots_adjust(bottom=0.22, top=0.88)
    save(fig, "fig_04_bridge", "Nguồn: mô hình của nhóm (ước lượng); đ/cp trên 44,84 tr cp sau phát hành. Hoạt động hiện hữu đã cộng lại lãi vay của khoản nợ tài trợ dự án dở dang (không trừ hai lần).",
         pd.DataFrame([(s[0].replace("\n", " "), round(s[1])) for s in steps] + [("gia_tri_sau_quyen", round(cum))], columns=["buoc", "dcp"])); plt.close(fig)

    # 05 Football field (sau quyền) ------------------------------------------------------
    rows = [("Kịch bản chu kỳ (50%)", BR["CYCLICAL"]), ("Kịch bản hành chính (30%)", BR["ADMIN_GATED"]), ("Kịch bản biên bền (20%)", BR["STRUCTURAL"])]
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.barh(3, ZP["90"] - ZP["10"], left=ZP["10"], color=GREEN, alpha=0.25, height=0.5)
    ax.barh(3, ZP["75"] - ZP["25"], left=ZP["25"], color=GREEN, alpha=0.85, height=0.5)
    ax.text(ZP["10"], 3.35, f"P10 {k(ZP['10'])}", fontsize=6.2); ax.text(ZP["90"], 3.35, f"P90 {k(ZP['90'])}", fontsize=6.2, ha="right")
    for i, (lab, v) in enumerate(rows):
        ax.plot(v, 2 - i, "o", color=NAVY, ms=7); ax.text(v + 250, 2 - i, k(v), va="center", fontsize=6.6)
    pe_lo, pe_hi = min(PEERS.values()), sorted(PEERS.values())[-2]
    ax.axvline(TERP, color=ACCENT, lw=1.5); ax.text(TERP + 150, -0.55, f"TERP {k(TERP)}", color=ACCENT, fontsize=6.6, fontweight="bold")
    ax.axvline(TP, color=NAVY, lw=1, ls="--"); ax.text(TP - 150, -0.55, f"tâm {k(TP)}", color=NAVY, fontsize=6.6, ha="right")
    ax.set_yticks([3, 2, 1, 0]); ax.set_yticklabels(["Vùng giá trị (lưới)"] + [r[0] for r in rows], fontsize=6.8)
    ax.set_xlim(14_000, 31_000); ax.xaxis.set_major_formatter(lambda v_, p_: f"{v_/1e3:.0f}k"); ax.set_ylim(-0.8, 3.7)
    ax.set_title("Giá ex-quyền lý thuyết cao hơn cả kịch bản biên bền (đ/cp sau quyền)")
    fig.subplots_adjust(left=0.2, bottom=0.25, top=0.88)
    save(fig, "fig_05_football", f"Nguồn: mô hình của nhóm, lưới {M['n_grid']} bộ tham số (ước lượng); TERP tính từ giá đóng cửa 03/11/2026 (30.000 đ, còn quyền). Chiết khấu thanh khoản {vn(D*100,1)}% ở quy mô 1 tỷ đ.",
         pd.DataFrame(rows + [(f"grid_p{q}", v) for q, v in ZP.items()] + [("TERP", round(TERP)), ("tam", TP)], columns=["muc", "dcp"])); plt.close(fig)

    # 06 Độ nhạy lãi huy động --------------------------------------------------------------
    sens = M["sens_rate"]
    bps = [-100, -50, 0, 50, 100]
    v1 = [sens[f"b1.0_{b:+d}"]["v_post"] * (1 - D) for b in bps]; v05 = [sens[f"b0.5_{b:+d}"]["v_post"] * (1 - D) for b in bps]
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    xx = range(len(bps)); w = 0.38
    ax.bar([x - w / 2 for x in xx], v1, w, color=NAVY, label="β = 1 (truyền dẫn đủ)"); ax.bar([x + w / 2 for x in xx], v05, w, color=GREY, label="β = 0,5")
    for x, v in zip(xx, v1):
        ax.text(x - w / 2, v + 250, k(v), ha="center", fontsize=6.2)
    ax.axhline(TERP, color=ACCENT, lw=1.2); ax.text(4.6, TERP + 250, f"TERP {k(TERP)}", color=ACCENT, fontsize=6.4, ha="right")
    ax.set_xticks(list(xx)); ax.set_xticklabels([f"{b/100:+.1f}%".replace(".", ",") + f"\n(lãi {vn(7.40 + b/100, 2)}%)" for b in bps], fontsize=6.4)
    ax.set_ylim(15_000, 31_500); ax.yaxis.set_major_formatter(lambda v_, p_: f"{v_/1e3:.0f}k"); ax.legend(fontsize=6.4, loc="upper center", frameon=False, ncol=2)
    ax.set_title("Lãi huy động giảm 1 điểm % nâng giá trị ≈11%; vẫn chưa tới mức giá hiện tại")
    fig.subplots_adjust(bottom=0.3, top=0.88)
    save(fig, "fig_06_rate_sens", "Nguồn: mô hình của nhóm. r = 13,5% + β × (lãi huy động 12 tháng − 7,40%); điểm neo 7,40% = chứng chỉ tiền gửi 12 tháng 02/11/2026. Đ/cp sau quyền, sau chiết khấu thanh khoản 1 tỷ đ.",
         pd.DataFrame({"bp": bps, "v_beta1": [round(v) for v in v1], "v_beta05": [round(v) for v in v05]})); plt.close(fig)

    # 07 Giá 12T + sự kiện ----------------------------------------------------------------------
    px = pd.read_csv(os.path.join(CALC, "px_scl.csv"), parse_dates=["time"])
    p2 = px[px["time"] >= "2025-11-01"]
    fig, ax = plt.subplots(figsize=(7.2, 2.4))
    ax.plot(p2["time"], p2["Close"], color=NAVY, lw=1.3)
    for d_, t_ in (("2026-01-20", "KQ Q4/25"), ("2026-04-20", "KQ Q1/26"), ("2026-07-20", "KQ Q2/26"), ("2026-10-15", "KQ Q3/26"), ("2026-10-27", "TB chào bán")):
        d_ = pd.Timestamp(d_); ax.axvline(d_, color=GREY, lw=0.7, ls="--"); ax.text(d_, p2["Close"].max() * 1.03, t_, fontsize=5.8, ha="center")
    ax.axhline(TP, color=GREEN, lw=1, ls=":"); ax.text(p2["time"].iloc[5], TP + 300, f"tâm giá trị sau quyền {k(TP)}", fontsize=6.2, color=GREEN)
    ax.yaxis.set_major_formatter(lambda v_, p_: f"{v_/1e3:.0f}k"); ax.set_ylim(p2["Close"].min() * 0.85, p2["Close"].max() * 1.12)
    ax.set_title(f"Giá 12 tháng (điều chỉnh): {k(p2['Close'].min())}–{k(p2['Close'].max())}; giá đã vượt tâm giá trị từ giữa 2026")
    fig.subplots_adjust(bottom=0.12, top=0.86)
    save(fig, "fig_07_price", "Nguồn: tav2_bq.ticker SCL Close (giá điều chỉnh) 01/11/2025–03/11/2026; ngày KQKD là ước lượng theo hạn công bố. Quan sát, không suy nhân quả.",
         p2[["time", "Close", "Volume"]]); plt.close(fig)

    # 08 Ảnh sản phẩm/hoạt động (website công ty) ----------------------------------------------
    def white(im):
        im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); return bg.convert("RGB")
    files = ["763tro-bay-3.png", "DSC00205-scaled.jpg", "dai-hoc-nguyen-trai-1024x576.jpg", "5.-silo-2.png"]
    labs = ["Tro bay\nphụ gia bê tông, xi măng", "Bãi xử lý tro + silo\nnhà máy tro bay", "Gạch nhẹ trong công trình\n(ĐH Nguyễn Trãi, Hà Nội)", "Lắp đặt dây chuyền tách tro\nVĩnh Tân (Bình Thuận cũ)"]
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.15))
    for ax_, f, lab in zip(axs, files, labs):
        im = white(Image.open(os.path.join(IMGS, f)))
        w_, h_ = im.size; t_ = 1.45; cw = min(w_, int(h_ * t_)); ch = int(cw / t_); l_ = (w_ - cw) // 2; tp = (h_ - ch) // 2
        ax_.imshow(im.crop((l_, tp, l_ + cw, tp + ch))); ax_.axis("off"); ax_.grid(False)
        ax_.set_title(lab, fontsize=6.5, fontweight="bold", loc="center", color=NAVY)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.16, top=0.8, wspace=0.04)
    save(fig, "fig_08_products", "Ảnh: website songdacaocuong.vn (trang Tro bay, Dây chuyền phân tách tro xỉ, Dự án; tải 03/11/2026). Công ty không công bố cơ cấu doanh thu theo sản phẩm.",
         pd.DataFrame({"anh": files, "chu_thich": [l.replace("\n", " ") for l in labs]})); plt.close(fig)
    print("figs ok")


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
BREAK_BEFORE = ("3.", "6.", "Phụ lục A")


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
        page.insert_text((42, 34), "SCL — CTCP Sông Đà Cao Cường · Báo cáo Due Diligence · 03/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "SCL_DD_investor_report_20261103.md"), os.path.join(HERE, "SCL_DD_investor_report_20261103.pdf"))
