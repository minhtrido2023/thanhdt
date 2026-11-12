"""Tái lập hình + PDF cho báo cáo DD nhà đầu tư VCP (dữ liệu đến 12/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào: figs/fin_quarterly_bq.csv (dữ liệu tài chính thị trường, VCP 2023Q1–2026Q3), ../calc/px_vcp.csv,
         ../calc/model_out.json, ../calc/peer_multiples_20261111.csv, src/site/*.jpg (ảnh website công ty).
Số BCTC (hard-code có chú thích) khớp REPORT.md nội bộ; mỗi hình ghi kèm CSV (figs/fig_XX_*.csv).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc")
SKILL = "/home/trido/.claude/skills/dd-investor-report"
NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = SKILL + "/fonts/BeVietnamPro-Regular.ttf"
FONT_B = SKILL + "/fonts/BeVietnamPro-Bold.ttf"
MD_NAME = "VCP_DD_investor_report_20261112"

M = json.load(open(os.path.join(CALC, "model_out.json")))
PX = 37_900           # đóng cửa 11/11/2026 [tav2_bq.ticker]
CENTER_PRE, CENTER_POST = M["center"], M["liq"]["by_size"]["1.0"]["center_post"]
BEAR_PRE, BULL_PRE = M["bear"], M["bull"]
BEAR_POST, BULL_POST = M["liq"]["by_size"]["1.0"]["bear_post"], M["liq"]["by_size"]["1.0"]["bull_post"]
# DT / LN gộp theo mảng, tỷ đồng [BCTC hợp nhất: KT25 PL07; H1/26 PL07; Q3/26 thuyết minh VI.10–11]
SEG = {  # kỳ: (DT điện, LN gộp điện, DT ngoài điện, LN gộp ngoài điện)
    "2025": (898.3, 605.1, 1012.1 + 383.5 + 9.3, 15.3 + 173.9 + 0.5),
    "H1/26": (569.5, 432.8, 656.7 + 224.0 + 4.2, 29.8 + 100.6 + 0.2),
    "Q3/25": (226.2, 150.3, 402.8, 67.8),
    "Q3/26": (223.0, 174.4, 602.6, 174.0)}


def fvn(x, nd=0):
    s = f"{x:,.{nd}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "Be Vietnam Pro", "font.size": 9, "axes.titlesize": 9.8, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#555", "axes.labelcolor": "#333", "xtick.color": "#333", "ytick.color": "#333",
        "figure.facecolor": "white", "savefig.facecolor": "white", "axes.grid": True, "grid.color": "#ECEFF2",
        "grid.linewidth": 0.8, "axes.axisbelow": True})
    return plt


def save(fig, name, source, df=None):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.6, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def qlabel(q):
    return q[4:] + "/" + q[2:4]


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0", "CF_Invest_P0", "Cash_P0", "StDebt_P0", "LtDebt_P0"]:
        fin[c] = fin[c] / 1e9
    fin["lab"] = fin["quarter"].map(qlabel)
    x = np.arange(len(fin))
    is26 = fin["quarter"].str.startswith("2026").values

    # ---------- HERO: cơ cấu DT/LN gộp 2025 + thanh giá vs vùng giá trị
    seg25 = [("Thuỷ điện", 898.3, 605.1, NAVY), ("Dịch vụ (điện rác, xử lý chất thải)", 383.5, 173.9, GREEN),
             ("Hàng hoá (phế liệu)", 1012.1, 15.3, ACCENT), ("Khác", 9.3, 0.5, GREY)]
    dt_tot, gp_tot = sum(s[1] for s in seg25), sum(s[2] for s in seg25)
    fig = plt.figure(figsize=(7.2, 2.9))
    a1 = fig.add_axes([0.11, 0.40, 0.42, 0.44]); a1.grid(False)
    for k, (lab, dt, gp, col) in enumerate(seg25):
        pass
    left_dt = left_gp = 0
    for lab, dt, gp, col in seg25:
        a1.barh(1, dt / dt_tot * 100, left=left_dt, color=col, height=0.6)
        a1.barh(0, gp / gp_tot * 100, left=left_gp, color=col, height=0.6)
        if dt / dt_tot > 0.08:
            a1.text(left_dt + dt / dt_tot * 50, 1, f"{fvn(dt / dt_tot * 100, 0)}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        if gp / gp_tot > 0.08:
            a1.text(left_gp + gp / gp_tot * 50, 0, f"{fvn(gp / gp_tot * 100, 0)}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        left_dt += dt / dt_tot * 100; left_gp += gp / gp_tot * 100
    a1.set_yticks([1, 0], ["Doanh thu\n2025", "LN gộp\n2025"], fontsize=8); a1.set_xlim(0, 100); a1.set_xticks([])
    a1.spines["left"].set_visible(False); a1.spines["bottom"].set_visible(False); a1.tick_params(left=False)
    hs = [plt.Rectangle((0, 0), 1, 1, color=s[3]) for s in seg25]
    fig.legend(hs, [s[0] for s in seg25], loc="lower left", bbox_to_anchor=(0.02, 0.10), fontsize=7, frameon=False, ncol=2)
    fig.text(0.03, 0.92, "Thuỷ điện: 39% doanh thu nhưng 76% lợi nhuận gộp", fontsize=9.8, fontweight="bold", color="#222")
    a2 = fig.add_axes([0.60, 0.30, 0.37, 0.54]); a2.grid(False)
    lo, hi = BEAR_POST, BULL_POST
    a2.barh(0, hi - lo, left=lo, color=LIGHT, height=0.34)
    a2.plot([CENTER_POST], [0], "|", color=NAVY, ms=22, mew=3)
    a2.plot([PX], [0.0], "o", color=ACCENT, ms=9, zorder=5)
    a2.text(lo, -0.32, fvn(lo), ha="left", fontsize=7.5); a2.text(hi, -0.32, fvn(hi), ha="right", fontsize=7.5)
    a2.text(CENTER_POST, 0.30, f"Tâm\n{fvn(CENTER_POST)}", ha="center", fontsize=7.8, color=NAVY, fontweight="bold")
    a2.text(PX, -0.62, f"Giá 11/11\n{fvn(PX)}", ha="center", va="top", fontsize=7.8, color=ACCENT, fontweight="bold")
    a2.set_xlim(lo - 3000, hi + 3000); a2.set_ylim(-1.1, 0.9); a2.set_yticks([])
    a2.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); a2.tick_params(axis="x", labelsize=7)
    fig.text(0.60, 0.92, "Giá nằm trong vùng giá trị, sát tâm", fontsize=9.8, fontweight="bold", color="#222")
    save(fig, "fig_00_hero", "Nguồn: BCTC hợp nhất 2025 kiểm toán (phụ lục báo cáo bộ phận); mô hình định giá nhóm nghiên cứu (vùng và tâm sau chiết khấu thanh khoản, vị thế 1 tỷ đồng); giá đóng cửa 11/11/2026.",
         pd.DataFrame([(s[0], s[1], s[2]) for s in seg25], columns=["manh", "dt_2025", "ln_gop_2025"]).assign(
             vung_thap=lo, tam=CENTER_POST, vung_cao=hi, gia_11_11=PX))
    plt.close(fig)

    # ---------- 1. DT & biên gộp theo mảng
    per = list(SEG.keys())
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    xs = np.arange(len(per)); w = 0.36
    dd = [SEG[p][0] for p in per]; do = [SEG[p][2] for p in per]
    ax.bar(xs - w / 2, dd, w, color=NAVY, label="DT mảng điện")
    ax.bar(xs + w / 2, do, w, color=ACCENT, label="DT ngoài điện (dịch vụ, hàng hoá, khác)")
    rows = []
    for i, p in enumerate(per):
        gme = SEG[p][1] / SEG[p][0] * 100; gmo = SEG[p][3] / SEG[p][2] * 100
        ax.text(i - w / 2, dd[i] + 18, f"biên gộp\n{fvn(gme, 1)}%", ha="center", fontsize=7.4, color=NAVY, fontweight="bold")
        ax.text(i + w / 2, do[i] + 18, f"biên gộp\n{fvn(gmo, 1)}%", ha="center", fontsize=7.4, color=ACCENT, fontweight="bold")
        rows.append((p, SEG[p][0], SEG[p][1], gme, SEG[p][2], SEG[p][3], gmo))
    ax.set_xticks(xs, ["Cả năm 2025", "6T/2026", "Quý 3/2025", "Quý 3/2026"]); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 1750)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.set_title("Quý 3/26: DT điện đi ngang, biên gộp ngoài điện nhảy từ 16,8% lên 28,9%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_01_segments", "Nguồn: BCTC hợp nhất 2025 (kiểm toán) PL07; 6T/2026 (soát xét) PL07; Q3/2026 (chưa soát xét) thuyết minh VI.10–11. Biên gộp ngoài điện tính lại từ DT và LN gộp các mảng cộng gộp.",
         pd.DataFrame(rows, columns=["ky", "dt_dien", "lg_dien", "bien_dien_pct", "dt_ngoai_dien", "lg_ngoai_dien", "bien_ngoai_dien_pct"]))
    plt.close(fig)

    # ---------- 2. LNST quý
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(x, fin["NP_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    for i, v in enumerate(fin["NP_P0"]):
        ax.text(i, v + 4, fvn(v, 0), ha="center", fontsize=7, color="#333")
    ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.set_ylabel("LNST cổ đông công ty mẹ, tỷ đồng")
    ax.set_title("LNST Q3/26 gấp đôi cùng kỳ (245 so với 125 tỷ), sau ba quý tăng đều")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_npat_quarterly", "Nguồn: dữ liệu tài chính thị trường (NP_P0), khớp BCTC hợp nhất Q3/2026: 245,4 tỷ. Kéo 12/11/2026.", fin[["quarter", "NP_P0"]])
    plt.close(fig)

    # ---------- 3. CFO vs LNST vs đầu tư
    sub = fin[fin["quarter"] >= "2025Q1"].reset_index(drop=True)
    xs = np.arange(len(sub)); w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(xs - w / 2, sub["NP_P0"], w, color=LIGHT, label="LNST")
    ax.bar(xs + w / 2, sub["CF_OA_P0"], w, color=NAVY, label="Dòng tiền kinh doanh (CFO)")
    ax.plot(xs, -sub["CF_Invest_P0"], color=ACCENT, marker="o", lw=1.5, label="Dòng tiền đầu tư ròng (chi = dương)")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(xs, sub["lab"]); ax.set_ylabel("tỷ đồng / quý"); ax.legend(fontsize=7.5, frameon=False, ncol=3, loc="upper left")
    ax.set_ylim(-120, 920)
    ax.annotate("CFO Q3/26 764 tỷ gồm\n373 tỷ giảm phải thu\n(khoản một lần)", (len(sub) - 1 + 0.18, 764), xytext=(2.3, 470), fontsize=7.4, color=NAVY,
                arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.7))
    ax.set_title("CFO 9T/26 là 1.004 tỷ, nhưng 373 tỷ là thu hồi phải thu một lần")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_03_cfo_npat", "Nguồn: dữ liệu tài chính thị trường (CF_OA_P0, NP_P0, CF_Invest_P0). Tổng 9T/26 khớp BCTC Q3/2026 (CFO 1.004,4; LCTT tr.7). 373,3 tỷ giảm phải thu: LCTT 9T/26.",
         sub[["quarter", "NP_P0", "CF_OA_P0", "CF_Invest_P0"]])
    plt.close(fig)

    # ---------- 4. Nợ / tiền / nợ ròng
    fin["debt"] = fin["StDebt_P0"] + fin["LtDebt_P0"]
    fin["net_debt"] = fin["debt"] - fin["Cash_P0"]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(x, fin["debt"], color=LIGHT, width=0.7, label="Tổng vay và trái phiếu")
    ax.bar(x, -fin["Cash_P0"], color=GREY, width=0.7, label="Tiền (hiển thị âm)")
    ax.plot(x, fin["net_debt"], color=NAVY, marker="o", lw=1.6, label="Nợ ròng (chỉ trừ tiền)")
    ax.annotate(f"{fvn(fin['debt'].iloc[-1])}", (len(fin) - 1, fin["debt"].iloc[-1]), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8, color="#333")
    ax.annotate(f"{fvn(fin['net_debt'].iloc[-1])}", (len(fin) - 1, fin["net_debt"].iloc[-1]), xytext=(-8, -12), textcoords="offset points", ha="right", fontsize=8, color=NAVY, fontweight="bold")
    ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.axhline(0, color="#555", lw=0.8); ax.set_ylabel("tỷ đồng")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left"); ax.set_ylim(-600, 4700)
    ax.set_title("Vay tăng từ 3.487 lên 4.282 tỷ trong 9T/26; nợ vay/EBITDA khoảng 3,2 lần")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_debt", "Nguồn: dữ liệu tài chính thị trường (StDebt_P0 + LtDebt_P0, Cash_P0); 30/9/2026 khớp BCTC Q3/2026 (vay 679,4 + 3.602,6; tiền 487,9). EBITDA TTM ≈ 1.336 tỷ (ước lượng).",
         fin[["quarter", "debt", "Cash_P0", "net_debt"]])
    plt.close(fig)

    # ---------- 5. Cho vay: cơ cấu + lãi dồn tích vs thu tiền
    loans = [("Cho vay cá nhân, TSĐB là cổ phần\nbên thứ ba (HĐ 4 và 6)", 566.6 + 97.4, ACCENT),
             ("Tín chấp lãi 5%", 84.2 + 4.5, GREY), ("Cho vay, TSĐB là\ncổ phiếu VCP", 51.0, "#E39C8B"),
             ("CP Sông Đà (đã dự phòng 100%)", 19.7, LIGHT)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1.5, 1]})
    for i, (lab, v, col) in enumerate(loans[::-1]):
        a1.barh(i, v, color=col, height=0.6); a1.text(v + 10, i, fvn(v, 1), va="center", fontsize=8)
    a1.set_yticks(range(4), [l[0] for l in loans[::-1]], fontsize=7); a1.set_xlim(0, 820); a1.set_xlabel("dư nợ 30/6/2026, tỷ đồng (tổng 823,4)")
    a1.set_title("Dư nợ cho vay 823 tỷ")
    a2.bar([0, 1], [91.6, 21.25], color=[NAVY, ACCENT], width=0.55)
    for i, v in enumerate([91.6, 21.25]):
        a2.text(i, v + 2, fvn(v, 2 if i else 1), ha="center", fontsize=8.5, fontweight="bold")
    a2.set_xticks([0, 1], ["DT tài chính\n9T/26", "Tiền thu lãi, cổ\ntức, LN chia 9T"], fontsize=7.4); a2.set_ylim(0, 108); a2.set_title("Lãi thu bằng tiền ≈ 23%")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_05_loans", "Nguồn: BCTC hợp nhất 6T/2026 phụ lục 01 (cho vay); BCTC hợp nhất Q3/2026 KQKD và LCTT dòng 27 (tiền thu lãi cho vay, cổ tức, lợi nhuận được chia). 77% chưa thu là cận trên.",
         pd.DataFrame([(l[0].replace("\n", " "), l[1]) for l in loans], columns=["nhom", "du_no_ty"]).assign(dt_tc_9T=91.6, tien_thu_lai_9T=21.25))
    plt.close(fig)

    # ---------- 6. Giá 12 tháng
    px = pd.read_csv(os.path.join(CALC, "px_vcp.csv"), parse_dates=["time"])
    px = px[px["time"] >= px["time"].max() - pd.Timedelta(days=365)].reset_index(drop=True)
    last = px.iloc[-1]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.6), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.axhline(CENTER_POST, color=ACCENT, ls="--", lw=1)
    a1.text(px["time"].iloc[2], CENTER_POST + 700, f"Tâm sau chiết khấu {fvn(CENTER_POST)}", fontsize=7.5, color=ACCENT)
    a1.plot(last["time"], last["Close"], "o", color=ACCENT, ms=5)
    a1.annotate(f"{last['time']:%d/%m}: {fvn(last['Close'])}", (last["time"], last["Close"]), xytext=(-70, 8), textcoords="offset points", fontsize=7.5, color=ACCENT)
    a1.set_ylabel("đ/cp (điều chỉnh)")
    a2.bar(px["time"], px["Volume"] / 1e3, color=GREY, width=1.0); a2.set_ylabel("KL, nghìn cp")
    lo_p, hi_p = px["Close"].min(), px["Close"].max()
    a1.set_title(f"Giá 12 tháng: {fvn(lo_p)} – {fvn(hi_p)} đ/cp; tăng mạnh sau báo cáo Q3, thanh khoản mỏng trước đó")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_price_12m", "Nguồn: dữ liệu giá thị trường (Close điều chỉnh, Volume) đến 11/11/2026; tâm: mô hình nhóm nghiên cứu.", px[["time", "Close", "Volume"]])
    plt.close(fig)

    # ---------- 7. Football field
    rows = [("Ba kịch bản (trước chiết khấu); tâm 41.560", BEAR_PRE, BULL_PRE, CENTER_PRE),
            ("Ba kịch bản sau chiết khấu thanh khoản", BEAR_POST, BULL_POST, CENTER_POST),
            ("Vùng bất định của tâm sau chiết khấu", 36_900, 46_100, CENTER_POST),
            ("Nền dòng tiền / lợi nhuận (V dài – D2)", M["V_dai"], M["V_D2"], M["V_ngan"]),
            ("Lãi huy động ±100bp (tâm)", M["sens"]["dep+100bp_b1.0"], M["sens"]["dep-100bp_b1.0"], CENTER_PRE),
            ("Giá 12 tháng", lo_p, hi_p, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "diem"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=GREY if i == 5 else NAVY, height=0.5, alpha=0.88)
        ax.text(r["thap"] - 500, yy, fvn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 500, yy, fvn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.5)
        if r["diem"] == r["diem"] and r["diem"] is not None:
            ax.plot(r["diem"], yy, "|", color="white", ms=14, mew=2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.6)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.2, label=f"Giá đóng cửa 11/11: {fvn(PX)}")
    ax.axvline(CENTER_POST, color="#555", ls=":", lw=1.2, label=f"Tâm sau chiết khấu: {fvn(CENTER_POST)}")
    ax.legend(fontsize=7.2, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(12000, 75000); ax.set_xlabel("đồng/cổ phiếu"); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá 37.900 nằm trong mọi vùng, gần đáy vùng bất định của tâm")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_football_field", "Nguồn: mô hình nhóm nghiên cứu (ước lượng); vạch trắng = điểm giữa/tâm của mỗi vùng. Hai nền V dài – D2 chỉ để tham khảo, chưa qua thử nghiệm độc lập.", ff)
    plt.close(fig)

    # ---------- 8. Comp ngành
    pc = pd.read_csv(os.path.join(CALC, "peer_multiples_20261111.csv"))
    vcp = {"ticker": "VCP", "PE": 4.53, "EVEB": 5.6}
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, col, ttl, med in ((axs[0], "PE", "P/E (lần)", 9.3), (axs[1], "EVEB", "EV/EBITDA (lần)", 6.7)):
        d = pc.dropna(subset=[col]).sort_values(col)
        names = list(d["ticker"]); vals = list(d[col])
        order = np.argsort(vals); names = [names[i] for i in order]; vals = [vals[i] for i in order]
        ax.barh(range(len(vals)), vals, color=[ACCENT if n == "VCP" else LIGHT for n in names], height=0.7)
        ax.axvline(med, color=NAVY, ls="--", lw=1); ax.text(med + 0.15, len(vals) - 0.6, f"trung vị {fvn(med, 1)}", fontsize=7, color=NAVY)
        ax.set_yticks(range(len(vals)), names, fontsize=7); ax.set_title(ttl, fontsize=9)
        for i, v in enumerate(vals):
            ax.text(v + 0.1, i, fvn(v, 1), va="center", fontsize=6.6)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_comps", "Nguồn: dữ liệu giá thị trường ngày 11/11/2026, rổ 13 mã thuỷ điện có dữ liệu; VCP: P/E 4,5 lần, EV/EBITDA 5,6 lần (BQ).",
         pc[["ticker", "PE", "EVEB"]])
    plt.close(fig)

    # ---------- 9. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("A", "Tín dụng cho vay cá nhân", 3, 5), ("B", "Biên ngoài điện về mức thường", 4, 4),
        ("C", "Thuỷ văn / El Niño 2026–27", 4, 3), ("D", "Tái đàm phán giá điện sau trả nợ", 2, 4),
        ("E", "Giải chấp cổ phiếu VCP đang cầm cố", 2, 4), ("F", "Kiểm soát nội bộ / pháp lý", 2, 3),
        ("G", "Thanh khoản UPCoM", 4, 2), ("H", "Lãi suất huy động tăng", 3, 3)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i in range(1, 6):
        for j in range(1, 6):
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if i * j >= 12 else ("#F3F5F7" if i * j < 6 else "#FBF1EC"), lw=0))
    offs = {"B": (-0.18, 0.0), "E": (0.18, 0.0), "F": (-0.18, 0.0), "D": (0.18, 0.0), "C": (0, 0.2), "H": (0, -0.2)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.16, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.4, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["1", "2", "3", "4", "5"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["1", "2", "3", "4", "5"], fontsize=7.5)
    ax.set_xlabel("Xác suất 12–18 tháng (1–5)"); ax.set_ylabel("Tác động lên giá trị (1–5)")
    ax.set_title("Tín dụng cho vay và biên ngoài điện: nhóm rủi ro lớn nhất")
    fig.tight_layout(rect=(0, 0.08, 0.66, 1))
    save(fig, "fig_09_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5: 1 = rất thấp/rất nhỏ, 5 = rất cao/rất lớn; chủ quan), tham chiếu đọc ngành độc lập 12/11/2026.", rk)
    plt.close(fig)

    # ---------- khung ảnh hoạt động (ảnh website công ty)
    from PIL import Image, ImageDraw, ImageFont
    site = os.path.join(HERE, "src", "site")
    items = [("1-cua-dat_4642.jpg", "Cửa Đạt, 97 MW (Thanh Hoá)"), ("2-xuan-minh_7954.jpg", "Xuân Minh, 15 MW (Thanh Hoá)"),
             ("nha-may-td-nam-la_7931.jpg", "Nậm La, 27 MW (Sơn La)"), ("dak-glun2_3032.jpg", "Đăk Glun, 18 MW (Bình Phước cũ)")]
    W, Hh, cap = 360, 240, 26
    canvas = Image.new("RGB", (W * 4 + 5 * 6, Hh + cap + 12), "white")
    fb = ImageFont.truetype(FONT_B, 15)
    for k, (fn, lab) in enumerate(items):
        im = Image.open(os.path.join(site, fn)).convert("RGB")
        r = max(W / im.width, Hh / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
        l, t = (im.width - W) // 2, (im.height - Hh) // 2
        im = im.crop((l, t, l + W, t + Hh)); xx = 6 + k * (W + 6)
        canvas.paste(im, (xx, 6)); ImageDraw.Draw(canvas).rectangle([xx, 6, xx + W - 1, 6 + Hh - 1], outline="#9AA5B1")
        ImageDraw.Draw(canvas).text((xx, 6 + Hh + 4), lab, font=fb, fill="#1F3A5F")
    canvas = canvas.resize((canvas.width * 2, canvas.height * 2), Image.LANCZOS)
    canvas.save(os.path.join(FIGS, "fig_10_plant_photos.png"))
    pd.DataFrame(items, columns=["file_anh_website", "chu_thich"]).to_csv(os.path.join(FIGS, "fig_10_plant_photos.csv"), index=False)
    print("figs done; 12m close lo/hi", lo_p, hi_p, "| last", last["time"].date(), last["Close"])


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
BREAK_BEFORE = ("1.",)


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
        if not s or s.startswith("<!--"):
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
            if lv == 1:
                i += 1; continue   # tiêu đề nằm trong banner
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
    import re
    import shutil
    md = open(md_path, encoding="utf-8").read()
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

    def new_page():
        if state["dev"] is not None:
            writer.end_page()
        state["dev"] = writer.begin_page(A4); state["y"] = where.y0

    def place_html(h, keep=False):
        mk = lambda: pymupdf.Story(html=f"<body>{h}</body>", user_css=CSS, archive=arch)
        story = mk(); more = 1
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
                if room < hh and room >= 0.75 * hh:
                    ww, hh = int(IMG_W * room / hh), int(room)
                elif room < hh:
                    new_page()
                place_html(f'<p><img src="{m.group(1)}" width="{ww}" height="{hh}"/></p>')
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
    writer.end_page(); writer.close()
    doc = pymupdf.open(tmp)
    n = doc.page_count
    for k, page in enumerate(doc):
        page.insert_font(fontname="dv", fontfile=FONT)
        if k:
            page.draw_line((42, 40), (A4.width - 42, 40), color=(0.12, 0.23, 0.37), width=0.6)
            page.insert_text((42, 34), "VCP — CTCP Xây dựng và Năng lượng VCP · Báo cáo Due Diligence · 12/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
            page.insert_text((A4.width - 125, 34), "Nhóm nghiên cứu", fontname="dv", fontsize=7.5, color=(0.4, 0.4, 0.4))
        page.draw_line((42, A4.height - 36), (A4.width - 42, A4.height - 36), color=(0.75, 0.78, 0.82), width=0.5)
        page.insert_text((42, A4.height - 24), "Thông tin nghiên cứu, không phải lời khuyên đầu tư cá nhân hoá. Xem tuyên bố miễn trừ ở Phụ lục F.", fontname="dv", fontsize=6.8, color=(0.4, 0.4, 0.4))
        page.insert_text((A4.width - 90, A4.height - 24), f"Trang {k + 1}/{n}", fontname="dv", fontsize=7.5, color=(0.2, 0.2, 0.2))
    doc.save(pdf_path, garbage=3, deflate=True); doc.close(); os.remove(tmp)
    for f in (FONT, FONT_B):
        os.remove(os.path.join(HERE, os.path.basename(f)))
    print("pages", n)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("figs", "all"):
        figs()
    if mode in ("pdf", "all"):
        pdf(os.path.join(HERE, MD_NAME + ".md"), os.path.join(HERE, MD_NAME + ".pdf"))
