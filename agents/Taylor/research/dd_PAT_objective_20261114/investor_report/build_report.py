"""Dựng biểu đồ + PDF + HTML cho báo cáo DD nhà đầu tư PAT (14/11/2026) — khuôn từ build_report_SCL_example.py.

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|html|all]
Đầu vào (src/): model_out_r2.json (cây 54 lá, độ nhạy), pat_quarterly_series.csv (BQ ticker_financial), pat_identified_periods.csv.
Số BCTC hard-code kèm trang ở Phụ lục A. Mỗi hình có CSV dữ liệu vẽ (figs/*.csv).
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")
MD = os.path.join(HERE, "PAT_DD_investor_report_20261114.md")

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
SK = "/home/trido/.claude/skills/dd-investor-report"
FONT = SK + "/fonts/BeVietnamPro-Regular.ttf"
FONT_B = SK + "/fonts/BeVietnamPro-Bold.ttf"

CENTER, P25, P75, P10, P90 = 64700, 49600, 79200, 36200, 100200
PRICE = 71000      # đóng cửa 13/11/2026 — CHỈ dùng ở hình mục 8
MOS15 = 0.85 * CENTER   # 54.995


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


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
    from matplotlib.patches import FancyBboxPatch
    plt = setup_mpl()
    mo = json.load(open(os.path.join(SRC, "model_out_r2.json")))
    sens = mo["sens"]
    leaves = mo["leaves"]

    # ---------------- 1. HERO: chuỗi giá trị + KPI + thanh giá trị (KHÔNG có thị giá) ----------------
    fig = plt.figure(figsize=(7.2, 3.9))
    ax = fig.add_axes([0, 0.07, 1, 0.93]); ax.set_xlim(0, 100); ax.set_ylim(0, 56); ax.axis("off")
    boxes = [
        (1, "Quặng apatit Lào Cai", "Mỏ nhóm DGC và quặng mua ngoài\nPAT mua từ DLC 627,9 tỷ (9T/2026)\n≈ 88,5% chi phí NVL cùng kỳ"),
        (26, "Lò điện luyện P4", "Công suất ~20.000 t/năm\n(báo, trích BCTN 2024)\nQuặng + than cốc + cát + điện"),
        (51, "Sản phẩm", "Thành phẩm, chủ yếu P4:\n96,5% doanh thu 2025\n(xỉ phốt pho, ferro-phốt pho)"),
        (76, "Đầu ra 9T/2026", "Bán cho công ty mẹ DLC: 63,7%\n(riêng Q3: 85,5%)\nKhách nước ngoài: 35,3%"),
    ]
    for x, t, s in boxes:
        ax.add_patch(FancyBboxPatch((x, 36), 22.5, 17.5, boxstyle="round,pad=0.2,rounding_size=1.2", fc="#F3F6FA", ec=NAVY, lw=1.0))
        ax.text(x + 11.25, 50.6, t, ha="center", va="center", fontsize=8.6, fontweight="bold", color=NAVY)
        ax.text(x + 11.25, 43.2, s, ha="center", va="center", fontsize=6.9, color="#333", linespacing=1.5)
    for x in (23.7, 48.7, 73.7):
        ax.annotate("", xy=(x + 2.1, 44.7), xytext=(x, 44.7), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6))
    tiles = [
        ("EBIT: đường cơ sở", "2025: 339 tỷ · 2027: 123 tỷ\ndài hạn: 172 tỷ (giá 2028)"),
        ("Tiền ròng", "357,4 tỷ = 14.300 đ/cp\n(tiền + tiền gửi − vay − khoản khoá)"),
        ("Thuế xuất khẩu P4", "10% lên 15% từ 01/01/2027\n(NĐ 199/2025/NĐ-CP)"),
    ]
    for i, (t, s) in enumerate(tiles):
        x = 1 + i * 33.4
        ax.add_patch(FancyBboxPatch((x, 22), 31.5, 11, boxstyle="round,pad=0.2,rounding_size=1.0", fc="white", ec=LIGHT, lw=1.2))
        ax.text(x + 1.6, 30.4, t, ha="left", va="center", fontsize=7.6, fontweight="bold", color=ACCENT)
        ax.text(x + 1.6, 25.6, s, ha="left", va="center", fontsize=7.0, color="#222", linespacing=1.5)
    # thanh giá trị
    lo, hi = 20000, 120000
    X = lambda v: 3 + (v - lo) / (hi - lo) * 94
    ax.plot([X(lo), X(hi)], [11, 11], color=LIGHT, lw=1.0)
    ax.add_patch(plt.Rectangle((X(P10), 8.6), X(P90) - X(P10), 4.8, fc="#DCE4EE", ec="none"))
    ax.add_patch(plt.Rectangle((X(P25), 8.6), X(P75) - X(P25), 4.8, fc=NAVY, ec="none", alpha=0.9))
    ax.plot([X(CENTER)] * 2, [7.6, 14.4], color=ACCENT, lw=2.4)
    ax.text(X(CENTER), 16.6, "Tâm 64.700 đ/cp", ha="center", va="center", fontsize=8.6, fontweight="bold", color=ACCENT)
    ax.text(X(P25), 5.4, "P25: 49.600", ha="center", va="center", fontsize=7, color=NAVY)
    ax.text(X(P75), 5.4, "P75: 79.200", ha="center", va="center", fontsize=7, color=NAVY)
    ax.text(X(P10), 5.4, "P10: 36.200", ha="center", va="center", fontsize=7, color="#555")
    ax.text(X(P90), 5.4, "P90: 100.200", ha="center", va="center", fontsize=7, color="#555")
    ax.text(1, 20.1, "Giá trị nội tại trên mỗi cổ phiếu (trước chiết khấu thanh khoản; mô hình dựng mù giá thị trường)", fontsize=7.4, color="#333", va="center")
    ax.text(1, 1.2, "Cây 54 kịch bản: thanh đậm = P25–P75, thanh nhạt = P10–P90.", fontsize=6.8, color="#666", va="center")
    save(fig, "fig_01_hero", "Nguồn: BCTC Q3/2026 (tr.1, tr.5, TM21, TM29, TM30), BCTC kiểm toán 2025 (TM19); mô hình định giá khoá 14/11/2026 (cây 54 kịch bản). Số mô tả ngành: báo chí (công suất).",
         pd.DataFrame({"chi_tieu": ["tam", "p25", "p75", "p10", "p90"], "dong_cp": [CENTER, P25, P75, P10, P90]}))
    plt.close(fig)

    # ---------------- 3. Tài chính: DT + LNST quý; biên gộp theo kỳ ----------------
    q = pd.read_csv(os.path.join(SRC, "pat_quarterly_series.csv"))
    q = q[q["quarter"] >= "2024Q1"].reset_index(drop=True)
    per = pd.read_csv(os.path.join(SRC, "pat_identified_periods.csv"))
    per = per.rename(columns={per.columns[0]: "ky"})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.05, 1]})
    x = np.arange(len(q))
    a1.bar(x, q["rev"], color=[NAVY if s >= "2026" else LIGHT for s in q["quarter"]], width=0.7)
    a1.set_ylabel("Doanh thu thuần, tỷ đồng")
    a1.set_xticks(x, [s[4:] + "/" + s[2:4] for s in q["quarter"]], fontsize=6.6, rotation=45)
    a1b = a1.twinx(); a1b.grid(False); a1b.spines["right"].set_visible(True)
    a1b.plot(x, q["np"], color=ACCENT, marker="o", ms=3.5, lw=1.4)
    a1b.set_ylabel("LNST, tỷ đồng", color=ACCENT); a1b.set_ylim(0, 130)
    for i in (len(q) - 1, len(q) - 2):
        a1b.annotate(vn(q["np"][i], 1), (i, q["np"][i]), xytext=(0, 7 if i == len(q) - 2 else -13), textcoords="offset points", fontsize=7, color=ACCENT, ha="center", fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    a1.set_title("Doanh thu đi ngang, LNST thấp hơn nền 2025", fontsize=8.6)
    sel = per[per["ky"].isin(["H1/2024", "Q3/2024", "Q4/2024", "H1/2025", "Q3/2025", "Q4/2025", "H1/2026", "Q3/2026"])].reset_index(drop=True)
    xs = np.arange(len(sel))
    a2.bar(xs, sel["gpm"] * 100, color=[ACCENT if k == "Q3/2026" else LIGHT for k in sel["ky"]], width=0.7)
    for i, v in enumerate(sel["gpm"] * 100):
        a2.text(i, v + 0.5, vn(v, 1), ha="center", fontsize=7, color="#333")
    a2.set_xticks(xs, sel["ky"], fontsize=6.4, rotation=45)
    a2.set_ylabel("Biên gộp, %"); a2.set_ylim(0, 32)
    a2.set_title("Biên gộp Q3/2026 14,5%: thấp nhất 15 kỳ", fontsize=8.6)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_03_financials", "Nguồn: tav2_bq.ticker_financial (PAT; DT/LNST quý, số công bố ban đầu); biên gộp kỳ dựng lại từ TTM + neo BCTC (H1, Q3, Q4 xác định được; Q1/Q2 riêng không tách). Kéo 14/11/2026.",
         q[["quarter", "rev", "np"]])
    sel[["ky", "gpm"]].to_csv(os.path.join(FIGS, "fig_03_financials_gpm_ky.csv"), index=False)
    plt.close(fig)

    # ---------------- 4. Nguyên liệu/DT theo chế độ + biên gộp thành phẩm ----------------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1, 1.05]})
    reg = pd.DataFrame({"che_do": ["2025\n(cốc ~1.491)", "H1/2026\n(cốc ~1.541)", "Q3/2026\n(cốc ~2.040)"], "nvl_dt": [46.6, 48.6, 55.2]})
    a1.bar(range(3), reg["nvl_dt"], color=[LIGHT, GREY, ACCENT], width=0.6)
    for i, v in enumerate(reg["nvl_dt"]):
        a1.text(i, v + 0.8, vn(v, 1) + "%", ha="center", fontsize=8, fontweight="bold")
    a1.set_xticks(range(3), reg["che_do"], fontsize=7); a1.set_ylim(30, 62); a1.set_ylabel("Nguyên vật liệu / doanh thu, %")
    a1.set_title("Chi phí nguyên liệu: +8,6 điểm % so 2025", fontsize=8.6)
    gp = pd.DataFrame({"ky": ["FY2024", "FY2025", "H1/2026", "Q3/2026"], "gpm_tp": [22.2, 23.4, 20.2, 14.5]})
    a2.bar(range(4), gp["gpm_tp"], color=[LIGHT, LIGHT, GREY, ACCENT], width=0.6)
    for i, v in enumerate(gp["gpm_tp"]):
        a2.text(i, v + 0.5, vn(v, 1) + "%", ha="center", fontsize=8, fontweight="bold")
    a2.set_xticks(range(4), gp["ky"], fontsize=7.4); a2.set_ylim(0, 30); a2.set_ylabel("Biên gộp thành phẩm, %")
    a2.set_title("Biên gộp thành phẩm: 23,4% xuống 14,5%", fontsize=8.6)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_04_cost_regimes", "Nguồn: BCTC kiểm toán 2025 (TM19–20), BCTC soát xét bán niên 2026 (TM23–24, TM28), BCTC Q3/2026 (TM21–22, TM28). NVL/DT quy theo đơn vị bán; cốc = than cốc sunsirs (CNY/t, BQ). Biên TP = (DT TP − GV TP)/DT TP.",
         reg.assign(gpm_ky=gp["ky"], gpm_tp=gp["gpm_tp"]))
    plt.close(fig)

    # ---------------- 5. Cấu phần giá trị + waterfall tiền ròng ----------------
    base = mo["base"]
    comp = {"Dòng tiền\ndự phóng": base["pv_flows"] / 0.025, "Giá trị cuối kỳ": base["pv_tv"] / 0.025, "Tiền ròng": base["net_cash"] / 0.025}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [0.8, 1.35]})
    bot = 0
    for (k, v), c in zip(comp.items(), [NAVY, GREY, GREEN]):
        a1.bar(0, v, bottom=bot, color=c, width=0.5)
        a1.text(0, bot + v / 2, f"{k}\n{vn(round(v, -2))}", ha="center", va="center", color="white", fontsize=7.4, fontweight="bold")
        bot += v
    a1.text(0, bot + 1200, "Giá trị cơ sở " + vn(round(bot, -2)), ha="center", fontsize=8, fontweight="bold", color=ACCENT)
    a1.set_xticks([]); a1.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); a1.set_ylim(0, 74000); a1.set_xlim(-0.6, 0.6); a1.set_ylabel("đồng/cổ phiếu")
    a1.set_title("Cấu phần của 64.700 (đường cơ sở)", fontsize=8.6)
    steps = [("Tiền", 1.246), ("Tiền gửi giữ\nđến đáo hạn", 558.069), ("Vay NH", -67.218), ("Quỹ KT-PL\nhiện có", -76.690), ("70 tỷ khoá\n(chỉ tính\nlãi)", -45.11), ("Quỹ KT-PL\ntừ LNST\n9T/26", -12.94)]
    cum = 0; xs_ = []
    for i, (k, v) in enumerate(steps):
        a2.bar(i, v, bottom=cum if v >= 0 else cum + v, color=GREEN if v >= 0 else ACCENT, width=0.6)
        a2.text(i, (cum + v if v >= 0 else cum) + 12, ("+" if v > 0 else "−") + vn(abs(v), 1), ha="center", fontsize=7)
        cum += v
    a2.bar(len(steps), cum, color=NAVY, width=0.6)
    a2.text(len(steps), cum + 12, vn(cum, 1), ha="center", fontsize=8, fontweight="bold")
    a2.set_xticks(range(len(steps) + 1), [s[0] for s in steps] + ["Tiền ròng\nđưa vào\ngiá trị"], fontsize=5.8)
    a2.set_ylim(0, 700); a2.set_ylabel("tỷ đồng")
    a2.set_title("Tiền ròng 357,4 tỷ = 14.300 đ/cp (30/09/2026)", fontsize=8.6)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_05_value_components", "Nguồn: BCTC Q3/2026 (BCĐKT tr.1; TM4, TM15); mô hình định giá (calc: PV dòng tiền 712,8 + PV giá trị cuối kỳ 547,9 + tiền ròng 357,4 = 1.618,1 tỷ; 25,0 triệu cổ phiếu).",
         pd.DataFrame({"buoc": [s[0].replace("\n", " ") for s in steps], "ty_dong": [s[1] for s in steps]}))
    plt.close(fig)

    # ---------------- 6. Football: nhánh có điều kiện của từng nút ----------------
    rows = [("Cây 54 kịch bản (P10–P90)", P10, P90, CENTER), ("Cây 54 kịch bản (P25–P75)", P25, P75, CENTER),
            ("Nút O: chi phí quặng từ 2028", 52500, 82100, None), ("Nút P: giá thực hiện từ 2027", 40000, 103500, 71700),
            ("Nút T: giá công ty mẹ trả sau 01/2027", 57900, 84500, None), ("Nút TX: thuế 15% hiệu lực", 62600, 84100, None)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for i, (lab, a, b, m) in enumerate(rows):
        yy = len(rows) - 1 - i
        ax.barh(yy, b - a, left=a, color=ACCENT if i < 2 else NAVY, height=0.5, alpha=0.9 if i != 0 else 0.45)
        ax.text(a - 700, yy, vn(a / 1e3, 1), ha="right", va="center", fontsize=7.5)
        ax.text(b + 700, yy, vn(b / 1e3, 1), ha="left", va="center", fontsize=7.5)
    ax.axvline(CENTER, color=ACCENT, ls="--", lw=1.1)
    ax.text(CENTER + 600, -0.62, "Tâm 64,7k", color=ACCENT, fontsize=7.6, fontweight="bold")
    ax.set_ylim(-0.8, 5.6)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1], fontsize=7.6)
    ax.set_xlim(25000, 112000); ax.set_xlabel("đồng/cổ phiếu (nút: giá trị bình quân có điều kiện của nhánh thấp nhất và cao nhất)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá thực hiện và chi phí quặng là hai nút làm giá trị dao động nhiều nhất")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_football_field", "Nguồn: mô hình định giá khoá 14/11/2026 (model_out_r2.json). Mỗi thanh nút = bình quân có điều kiện của nhánh thấp nhất và cao nhất của nút đó.",
         pd.DataFrame(rows, columns=["noi_dung", "thap", "cao", "ghi_chu"]))
    plt.close(fig)

    # ---------------- 7. Tornado độ nhạy ----------------
    b = 64700
    tor = [("Giá thực hiện ×0,95 / ×1,05", sens["price_x0.95"], sens["price_x1.05"]),
           ("Chi phí quặng cố định O3 / O1", sens["O_fixed_O3"], sens["O_fixed_O1"]),
           ("Tỷ trọng DT chịu thuế 15%: 100% / 13,5%", sens["s_eff1.0"], sens["s_eff0.135"]),
           ("NVL/DT dài hạn ±2,75 điểm %", sens["nvlLR+0.0275"], sens["nvlLR-0.0275"]),
           ("EBIT dài hạn ×0,8 / ×1,2", sens["ebitLR_x0.8"], sens["ebitLR_x1.2"]),
           ("Thuế xuất khẩu giữ 10%", b, sens["tax_stays_10"]),
           ("Giá công ty mẹ trả dưới netback 5%", sens["transfer_below_netback_-5pct"], b),
           ("Than cốc dài hạn 2.108 / 1.704", sens["cokeLR_2108"], sens["cokeLR_1704"]),
           ("r 14,5% / 12,5% (g = 2%)", 61080, 69047)]
    tor = sorted(tor, key=lambda t: abs(t[2] - t[1]))
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, (lab, lo_, hi_) in enumerate(tor):
        ax.barh(i, lo_ - b, left=b, color=ACCENT, height=0.55)
        ax.barh(i, hi_ - b, left=b, color=GREEN, height=0.55)
        ax.text(min(lo_, hi_, b) - 600, i, vn(lo_ / 1e3, 1) if lo_ != b else "", ha="right", va="center", fontsize=7)
        ax.text(max(lo_, hi_, b) + 600, i, vn(hi_ / 1e3, 1) if hi_ != b else "", ha="left", va="center", fontsize=7)
    ax.axvline(b, color="#333", lw=1)
    ax.set_yticks(range(len(tor)), [t[0] for t in tor], fontsize=7.4)
    ax.set_xlim(30000, 100000); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_xlabel("đồng/cổ phiếu, so với đường cơ sở 64.700 (đỏ = giảm, xanh = tăng)")
    ax.set_title("Giá bán thực hiện: ±5% giá làm giá trị ±38%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_tornado", "Nguồn: mô hình định giá khoá 14/11/2026 (model_out_r2.json, mục sens và grid); r 14,5%/12,5% đọc từ lưới r×g.",
         pd.DataFrame(tor, columns=["bien", "gia_tri_thap_hoac_a", "gia_tri_cao_hoac_b"]))
    plt.close(fig)

    # ---------------- 8. Đối chiếu thị giá (CHỈ hình này có giá thị trường) ----------------
    p_below = sum(l["p"] for l in leaves if l["v"] < PRICE)
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.barh(0, P90 - P10, left=P10, color="#DCE4EE", height=0.42)
    ax.barh(0, P75 - P25, left=P25, color=NAVY, height=0.42, alpha=0.9)
    ax.plot([CENTER] * 2, [-0.36, 0.36], color=ACCENT, lw=2.4)
    ax.plot([MOS15] * 2, [-0.36, 0.36], color=GREEN, lw=1.8, ls="--")
    ax.plot([PRICE] * 2, [-0.36, 0.36], color="#111", lw=2.4)
    ax.text(CENTER, 0.55, "Tâm 64.700", ha="center", fontsize=7.8, color=ACCENT, fontweight="bold")
    ax.text(MOS15 - 800, -0.62, "Ngưỡng biên an toàn 15%\n54.995", ha="right", fontsize=7.2, color=GREEN)
    ax.text(PRICE + 900, -0.62, "Thị giá đóng cửa 13/11/2026\n71.000 (+9,7% so với tâm)", ha="left", fontsize=7.2, color="#111", fontweight="bold")
    ax.text(P25, 0.30, "P25 49.600", ha="center", fontsize=6.6, color="white") if False else None
    ax.set_yticks([]); ax.set_ylim(-1.1, 0.95); ax.set_xlim(30000, 105000)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.grid(axis="y", visible=False)
    ax.set_xlabel("đồng/cổ phiếu (đậm: P25–P75; nhạt: P10–P90)")
    ax.set_title("Thị giá nằm trong vùng P25–P75, trên tâm 9,7%, cách ngưỡng biên an toàn +29,1%")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_08_price_check", "Nguồn: mô hình định giá mù giá (khoá 14/11/2026); giá đóng cửa 13/11/2026 = 71.000 đ/cp (giá thị trường duy nhất dùng trong báo cáo). Ngưỡng 15% = 0,85 × 64.700.",
         pd.DataFrame({"moc": ["tam", "nguong_15pct", "thi_gia_13_11", "p_gia_tri_duoi_thi_gia_theo_cay"], "gia_tri": [CENTER, MOS15, PRICE, p_below]}))
    plt.close(fig)
    print("p(V<71000) =", round(p_below, 4))


# ------------------------------------------------------------------ PDF / HTML
CSS = """
@font-face {font-family: dv; src: url(BeVietnamPro-Regular.ttf);}
@font-face {font-family: dv; src: url(BeVietnamPro-Bold.ttf); font-weight: bold;}
* {font-family: dv;}
body {margin: 0; padding: 0; font-size: 8.4pt; line-height: 1.36; color: #1d2731;}
h1 {font-size: 14pt; color: #1F3A5F; margin: 0 0 4pt 0;}
h2 {font-size: 11.2pt; color: #1F3A5F; margin: 10pt 0 3pt 0;}
h3 {font-size: 9.4pt; color: #1F3A5F; margin: 7pt 0 3pt 0;}
p {margin: 3pt 0;}
table {border-collapse: collapse; width: 100%; margin: 4pt 0 6pt 0;}
th {background-color: #1F3A5F; color: #ffffff; font-size: 7.4pt; padding: 2pt 3pt; text-align: left;}
td {font-size: 7.4pt; padding: 2pt 3pt; border-bottom: 1px solid #D9DEE4;}
li {margin: 1pt 0;}
img {width: 100%;}
"""

IMG_W = 470
BREAK_BEFORE = ("Phụ lục A",)


def md_to_html(md, pdf_mode=True):
    import html as H
    import re
    from PIL import Image

    def inl(s):
        s = H.escape(s, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        return re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
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
            with Image.open(os.path.join(HERE, m.group(2))) as im:
                hh = int(IMG_W * im.height / im.width)
            close()
            if pdf_mode:
                out.append(f'<IMG {m.group(2)} {hh}/>')
            else:
                with open(os.path.join(HERE, m.group(2)), "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode()
                out.append(f'<p><img alt="{H.escape(m.group(1), quote=True)}" src="data:image/png;base64,{b64}"/></p>')
            i += 1; continue
        if re.fullmatch(r"-{3,}", s):
            close(); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            close(); lv = len(m.group(1))
            if lv == 2 and m.group(2).startswith(BREAK_BEFORE) and pdf_mode:
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


def html_out(md_path, html_path):
    md = open(md_path, encoding="utf-8").read()
    import re as _re
    md = _re.sub(r"^# .*\n", "", md, count=1, flags=_re.M)
    body = md_to_html(md, pdf_mode=False)
    css = """body{font-family:'Be Vietnam Pro','Segoe UI','Helvetica Neue',Arial,Tahoma,sans-serif;max-width:820px;margin:24px auto;padding:0 16px;color:#1d2731;font-size:15px;line-height:1.55}
h1{color:#1F3A5F;font-size:24px;line-height:1.3}h2{color:#1F3A5F;font-size:19px;margin-top:28px;border-bottom:2px solid #D9DEE4;padding-bottom:4px}h3{color:#1F3A5F;font-size:16px}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}th{background:#1F3A5F;color:#fff;padding:5px 7px;text-align:left}td{padding:5px 7px;border-bottom:1px solid #D9DEE4;vertical-align:top}
tr:nth-child(even) td{background:#F3F5F7}img{max-width:100%;height:auto}"""
    banner = os.path.join(FIGS, "title_banner.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f'<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><title>PAT — Báo cáo Due Diligence 14/11/2026</title><style>{css}</style></head><body>{body}</body></html>')
    print("html", html_path, os.path.getsize(html_path) // 1024, "KB")


def pdf(md_path, pdf_path):
    sys.path.insert(0, "/tmp/pdflib")
    import pymupdf
    import shutil
    import re
    md = open(md_path, encoding="utf-8").read()
    # banner đã chứa tiêu đề: bỏ dòng h1 khi dựng PDF
    md = re.sub(r"^# .*\n", "", md, count=1, flags=re.M)
    body = md_to_html(md)
    chunks = body.split("<PAGEBREAK/>")
    for f in (FONT, FONT_B):
        shutil.copy(f, os.path.join(HERE, os.path.basename(f)))
    arch = pymupdf.Archive(HERE)
    A4 = pymupdf.paper_rect("a4")
    where = A4 + (42, 54, -42, -50)
    tmp = pdf_path + ".tmp"
    writer = pymupdf.DocumentWriter(tmp)
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
                if room < hh and room >= (0.40 if first_img[0] else 0.75) * hh:
                    ww, hh = int(IMG_W * room / hh), int(room)
                elif room < hh:
                    new_page()
                place_html(f'<p><img src="{m.group(1)}" width="{ww}" height="{hh}"/></p>')
                first_img[0] = False
            else:
                raw = [b for b in part.split("\n") if b.strip()]
                blocks, cur = [], None
                for b in raw:
                    if cur is not None:
                        cur += b
                        if b in ("</ul>", "</ol>"):
                            blocks.append(cur); cur = None
                    elif b in ("<ul>", "<ol>"):
                        cur = b
                    else:
                        blocks.append(b)
                k = 0
                while k < len(blocks):
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
        page.insert_text((42, 34), "PAT — CTCP Phốt pho Apatit Việt Nam · Báo cáo Due Diligence · 14/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(MD, os.path.join(HERE, "PAT_DD_investor_report_20261114.pdf"))
    if mode in ("html", "all"):
        html_out(MD, os.path.join(HERE, "PAT_DD_investor_report_20261114.html"))
