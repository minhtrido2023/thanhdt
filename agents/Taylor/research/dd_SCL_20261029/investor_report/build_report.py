"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư SCL (29/10/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (cùng thư mục figs/):
  fin_quarterly_bq.csv  — tav2_bq.ticker_financial (SCL, 2023Q1–2026Q3), kéo 29/10/2026
  price_raw.csv         — tav2_bq.ticker (SCL Close/Price/Volume, 01/10/2025–28/10/2026)
Số BCTC (hard-code có trích trang) lấy từ BCTC hợp nhất Q3/2026 và bán niên 2026 soát xét.
Mỗi hình ghi kèm CSV dữ liệu vẽ (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")

NAVY, ACCENT, GREY, LIGHT = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- số dùng chung (nguồn: REPORT.md §2–§8, đã qua fundamental-skeptic) ----
SH_NOW = 38_836_815          # CP lưu hành 30/9/2026 [BCTC HN Q3, vốn góp 388,37 tỷ]
SH_NEW = 6_000_000           # CP chào bán [NQ1363, TB1368]
SH_POST = SH_NOW + SH_NEW    # 44.836.815
RATIO = 0.154453             # 100:15,4453
SUB_PX = 12_500
CLOSE_2810 = 31_100          # đóng cửa 28/10/2026 [BQ]
PX_2910 = 29_500             # DNSE latest_trade 29/10/2026 11:29:49 ICT
FV = 25_495                  # 0,3×13.050 + 0,5×27.100 + 0,2×40.150
SCEN = {"Bear": (13_050, 0.30), "Base": (27_100, 0.50), "Bull": (40_150, 0.20)}
EPS_PF, BVPS_PF = 2_746, 13_529
EBITDA_9T_ANN, ND_PF = 227.6, 246.4   # tỷ
COMPS = {  # PE, PB, EV/EBITDA [BQ 28/10/2026]
    "VGC": (10.8, 1.61, 5.6), "VCS": (8.7, 0.98, 6.2), "PLC": (11.8, 1.23, 7.9),
    "DHA": (5.5, 1.47, None), "NNC": (5.1, 1.65, 4.1), "HT1": (13.1, 1.02, 4.1),
    "KSB": (7.8, 0.56, None), "BMP": (9.0, 3.56, 6.0)}


def terp(p):
    return (p + RATIO * SUB_PX) / (1 + RATIO)


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 9.8,
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


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0", "CF_Invest_P0", "Cash_P0", "StDebt_P0", "LtDebt_P0"]:
        fin[c] = fin[c] / 1e9
    fin["lab"] = fin["quarter"].map(qlabel)
    x = np.arange(len(fin))
    is26 = fin["quarter"].str.startswith("2026")

    # 1. Doanh thu & biên gộp
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(x, fin["Revenue_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    ax.set_ylabel("Doanh thu gộp quý, tỷ đồng")
    ax.set_xticks(x, fin["lab"], rotation=0, fontsize=7.5)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(x, fin["GPM_P0"] * 100, color=GREY, ls="--", lw=1.2, label="Chỉ số biên gộp BQ (GPM_P0, định nghĩa khác BCTC)")
    bctc = {"2025Q3": 35.6, "2026Q3": 41.2}
    for q, v in bctc.items():
        i = int(fin.index[fin["quarter"] == q][0])
        ax2.plot(i, v, "o", color=ACCENT, ms=7, zorder=5)
        ax2.annotate(f"{v:.1f}%".replace(".", ","), (i, v), xytext=(-8, 8), textcoords="offset points",
                     color=ACCENT, fontsize=8.5, fontweight="bold", ha="right")
    ax2.plot([], [], "o", color=ACCENT, label="Biên gộp quý theo BCTC hợp nhất")
    ax2.set_ylim(25, 50); ax2.set_ylabel("Biên gộp, %")
    ax2.legend(loc="upper left", fontsize=7.5, frameon=False)
    ax.set_title("Doanh thu 2026 lên nền mới; biên gộp Q3/26 41,2% là đỉnh 3 năm")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_01_revenue_margin",
         "Nguồn: tav2_bq.ticker_financial (Revenue_P0 = DT gộp, khớp dòng 01 BCTC Q3/26 và Q3/25); BCTC hợp nhất Q3/2026 tr.3. Kéo 29/10/2026.",
         fin[["quarter", "Revenue_P0", "GPM_P0"]].assign(gpm_bctc=fin["quarter"].map(bctc)))
    plt.close(fig)

    # 2. LNST quý
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(x, fin["NP_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    for i, v in enumerate(fin["NP_P0"]):
        ax.text(i, v + 0.6, f"{v:.1f}".replace(".", ","), ha="center", fontsize=7, color="#333")
    ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.set_ylabel("LNST cổ đông mẹ, tỷ đồng")
    ax.set_title("LNST Q3/26 ≈ Q2/26: +136% YoY đến từ nền 2025 thấp, QoQ đã đi ngang")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (tổng 3 quý 2026 = 94,37 tỷ, khớp BCTC 9T). Kéo 29/10/2026.",
         fin[["quarter", "NP_P0"]])
    plt.close(fig)

    # 3. Phải thu KH & VinCons vs DT quý
    ar = pd.DataFrame({"moc": ["01/01/2026", "30/06/2026", "30/09/2026"],
                       "phai_thu_kh": [88.5, 82.3, 116.0], "vincons": [48.2, 23.4, 67.9],
                       "dt_gop_quy_truoc_moc": [219.7, 242.6, 277.9]})
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    xi = np.arange(3); w = 0.26
    ax.bar(xi - w, ar["dt_gop_quy_truoc_moc"], w, color=LIGHT, label="DT gộp của quý kết thúc tại mốc (BQ)")
    ax.bar(xi, ar["phai_thu_kh"], w, color=NAVY, label="Phải thu khách hàng")
    ax.bar(xi + w, ar["vincons"], w, color=ACCENT, label="— trong đó VinCons")
    for i in range(3):
        for off, col in ((-w, "dt_gop_quy_truoc_moc"), (0, "phai_thu_kh"), (w, "vincons")):
            v = ar[col][i]
            ax.text(i + off, v + 3, f"{v:.1f}".replace(".", ","), ha="center", fontsize=7.5)
    ax.set_xticks(xi, ar["moc"]); ax.set_ylabel("tỷ đồng"); ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_ylim(0, 320)
    ax.set_title("VinCons: giảm 48→23 tỷ trong H1, tăng lại 68 tỷ ở Q3 (chưa có tuổi nợ)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_03_receivables", "Nguồn: BCTC hợp nhất bán niên 2026 (soát xét) và Q3/2026, thuyết minh V.3; DT gộp quý: tav2_bq Revenue_P0 (Q4/25, Q2/26, Q3/26).", ar)
    plt.close(fig)

    # 4. CFO vs LNST + capex
    sub = fin[fin["quarter"] >= "2025Q1"].reset_index(drop=True)
    xs = np.arange(len(sub)); w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.bar(xs - w / 2, sub["NP_P0"], w, color=LIGHT, label="LNST")
    ax.bar(xs + w / 2, sub["CF_OA_P0"], w, color=NAVY, label="CFO")
    ax.plot(xs, -sub["CF_Invest_P0"], color=ACCENT, marker="o", lw=1.5, label="Dòng tiền đầu tư ròng (chi = dương)")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(xs, sub["lab"]); ax.set_ylabel("tỷ đồng / quý"); ax.legend(fontsize=7.5, frameon=False, ncol=3, loc="upper left")
    ax.set_ylim(-110, 260)
    ax.set_title("9T/26: CFO 9,9 tỷ so với LNST 94,4 tỷ; capex 198 tỷ cho Phả Lại")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_cfo_npat_capex", "Nguồn: tav2_bq.ticker_financial CF_OA_P0/NP_P0/CF_Invest_P0 (tổng 9T/26 khớp BCTC LCTT tr.5: CFO 9,86; capex 198,13). Kéo 29/10/2026.",
         sub[["quarter", "NP_P0", "CF_OA_P0", "CF_Invest_P0"]])
    plt.close(fig)

    # 5. Nợ vay, tiền, nợ ròng
    fin["debt"] = fin["StDebt_P0"] + fin["LtDebt_P0"]
    fin["net_debt"] = fin["debt"] - fin["Cash_P0"]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.bar(x, fin["debt"], color=LIGHT, width=0.7, label="Tổng vay")
    ax.bar(x, -fin["Cash_P0"], color=GREY, width=0.7, label="Tiền (âm = bù trừ)")
    ax.plot(x, fin["net_debt"], color=NAVY, marker="o", lw=1.6, label="Nợ ròng")
    n = len(fin) - 1
    ax.plot(n + 1, ND_PF, "D", color=ACCENT, ms=7)
    ax.annotate("Pro-forma sau trả nợ 75 tỷ: 246\n(nợ ròng/EBITDA 1,41× → 1,08×)", (n + 1, ND_PF), xytext=(n - 2.6, -175),
                textcoords="data", fontsize=7.5, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    ax.annotate(f"{fin['net_debt'].iloc[-1]:.0f}", (n, fin["net_debt"].iloc[-1]), xytext=(-6, 6), textcoords="offset points",
                fontsize=8, color=NAVY, ha="right", fontweight="bold")
    ax.set_xticks(list(x) + [n + 1], list(fin["lab"]) + ["PF"], fontsize=7.5)
    ax.axhline(0, color="#555", lw=0.8); ax.set_ylabel("tỷ đồng"); ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Nợ ròng 321 tỷ (30/9/26), gấp 2,3 lần cuối 2025; chào bán chỉ kéo về ~246 tỷ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_05_debt", "Nguồn: tav2_bq.ticker_financial (StDebt_P0+LtDebt_P0, Cash_P0; 30/9/26 khớp BCTC tr.1–2: vay 416,5; tiền 95,1). PF = ước lượng nếu 75 tỷ trả nợ hết.",
         fin[["quarter", "debt", "Cash_P0", "net_debt"]])
    plt.close(fig)

    # 6. Bậc thang số cổ phiếu
    sh = pd.DataFrame({
        "moc": ["2023", "12/2023\nCT 8%", "03/2025\nCT 20%", "11/2025\nCT 9%", "01/2026\nquyền 8tr", "06/2026\nCT 17%", "07/2026\nESOP", "12/2026 (dự kiến)\nquyền 6tr"],
        "so_cp_trieu": [17.279, 18.661, 22.393, 24.408, 32.408, 37.917, 38.837, 44.837]})
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    cols = [LIGHT] * 7 + [ACCENT]
    ax.bar(np.arange(8), sh["so_cp_trieu"], color=[NAVY] * 7 + [ACCENT], width=0.65)
    for i, v in enumerate(sh["so_cp_trieu"]):
        ax.text(i, v + 0.8, f"{v:.2f}".replace(".", ","), ha="center", fontsize=8)
    ax.set_xticks(np.arange(8), sh["moc"], fontsize=7)
    ax.set_ylabel("triệu cổ phiếu"); ax.set_ylim(0, 52)
    ax.set_title("Số cổ phiếu tăng 2,6 lần trong ~3 năm (17,3 → 44,8 triệu)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_share_count", "Nguồn: tav2_bq.corporate_action (AIS shares_total_after), BCTC Q3/26 (vốn góp 388,37 tỷ), NQ 1363/TB 1368 (6,0 triệu CP).", sh.assign(moc=sh["moc"].str.replace("\n", " ")))
    plt.close(fig)

    # 7. TERP waterfall
    t = terp(CLOSE_2810); rv = CLOSE_2810 - t
    t2 = terp(PX_2910)
    wf = pd.DataFrame({"buoc": ["Giá cum-quyền 28/10", "Giá trị lý thuyết quyền", "TERP", "Giá trị hợp lý có trọng số"],
                       "gia_tri": [CLOSE_2810, -rv, t, FV]})
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(0, CLOSE_2810, color=NAVY, width=0.6)
    ax.bar(1, rv, bottom=t, color=GREY, width=0.6)
    ax.bar(2, t, color=NAVY, width=0.6)
    ax.bar(3, FV, color=ACCENT, width=0.6)
    lbl = [f"{CLOSE_2810:,.0f}", f"−{rv:,.0f}", f"{t:,.0f}", "~25,500\n(ước lượng)"]
    ys = [CLOSE_2810, CLOSE_2810, t, FV]
    for i, (s, yv) in enumerate(zip(lbl, ys)):
        ax.text(i, yv + 500, s.replace(",", "."), ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(range(4), wf["buoc"], fontsize=8); ax.set_ylim(0, 36000); ax.set_ylabel("đồng/cổ phiếu")
    ax.set_title(f"TERP {t:,.0f} cao hơn giá trị hợp lý ~11%; tại giá 29/10 ({PX_2910:,}) TERP {t2:,.0f}".replace(",", "."))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_terp_waterfall", "Nguồn: NQ 1363 + TB 1368 (100:15,4453 @12.500); giá 28/10 tav2_bq.ticker; giá 29/10 DNSE latest_trade 11:29:49 ICT. TERP = (P + 0,154453×12.500)/1,154453.",
         wf.assign(terp_2910=t2))
    plt.close(fig)

    # 8. Giá 12 tháng + khối lượng
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-10-29"].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.plot(pd.Timestamp("2026-10-29"), PX_2910, "o", color=ACCENT, ms=5)
    a1.annotate("29/10 11:29: 29.500\n(DNSE, trong phiên)", (pd.Timestamp("2026-10-29"), PX_2910), xytext=(pd.Timestamp("2026-03-20"), 27500),
                textcoords="data", fontsize=7, color=ACCENT, ha="left", arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    ev = [("2025-11-06", "GDKHQ CT 9%"), ("2026-06-09", "GDKHQ CT 17%"), ("2026-07-30", "ESOP 0,92tr"),
          ("2026-09-08", "Công bố quyền 15,4%"), ("2026-10-28", "28/10: −6,6%")]
    ymax = px["Close"].max()
    for k, (d, s) in enumerate(ev):
        dd = pd.Timestamp(d)
        a1.axvline(dd, color=GREY, lw=0.8, ls=":")
        a1.text(dd, ymax * (1.03 - 0.075 * k), " " + s + " ", fontsize=6.8, color="#444", ha="left" if k < 2 else "right")
    a1.set_ylabel("đ/cp (điều chỉnh)")
    a2.bar(px["time"], px["Volume"] / 1e3, color=GREY, width=1.0)
    a2.bar(pd.Timestamp("2026-10-28"), px["Volume"].iloc[-1] / 1e3, color=ACCENT, width=1.5)
    a2.set_ylabel("KL, nghìn cp")
    a1.set_title("Giá tăng ~45% từ đáy T8 (23,0k) lên 33,3k (27/10), rồi giảm 6,6% phiên 28/10")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_price_12m", "Nguồn: tav2_bq.ticker (Close điều chỉnh, Volume) 29/10/2025–28/10/2026; điểm 29/10 từ DNSE latest_trade; ngày sự kiện: tav2_bq.corporate_action, NQ 1363.",
         px[["time", "Close", "Volume"]])
    plt.close(fig)
    hi, lo = px["Close"].max(), px["Close"].min()

    # 9. Football field
    pe = [v[0] for v in COMPS.values()]; pb = [v[1] for v in COMPS.values()]
    ev_ = [v[2] for v in COMPS.values() if v[2] is not None]
    eqv = lambda m: (m * EBITDA_9T_ANN - ND_PF) * 1e9 / SH_POST
    rows = [
        ("Kịch bản bear–bull (LN 2027)", SCEN["Bear"][0], SCEN["Bull"][0], SCEN["Base"][0]),
        ("Comp P/E × EPS TTM pro-forma 2.746", min(pe) * EPS_PF, max(pe) * EPS_PF, np.median(pe) * EPS_PF),
        ("Comp EV/EBITDA × EBITDA 9T năm hoá", eqv(min(ev_)), eqv(max(ev_)), eqv(np.median(ev_))),
        ("Comp P/B × BVPS pro-forma 13.529", min(pb) * BVPS_PF, max(pb) * BVPS_PF, np.median(pb) * BVPS_PF),
        ("Vùng giá 12 tháng (điều chỉnh)", lo, hi, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "trung_vi"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=NAVY if i else ACCENT, height=0.5, alpha=0.85)
        ax.text(r["thap"] - 400, yy, f"{r['thap']/1e3:.1f}".replace(".", ","), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 400, yy, f"{r['cao']/1e3:.1f}".replace(".", ","), ha="left", va="center", fontsize=7.5)
        if r["trung_vi"] == r["trung_vi"] and r["trung_vi"] is not None:
            ax.plot(r["trung_vi"], yy, "|", color="white", ms=14, mew=2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.8)
    for v, s, c, ls in ((FV, "Giá trị hợp lý có trọng số ~25,5k (ước lượng)", ACCENT, "--"), (terp(CLOSE_2810), "TERP 28,6k (giá 28/10)", NAVY, "--"), (PX_2910, "Giá 29/10 11:29: 29,5k (cum-quyền)", "#555", ":")):
        ax.axvline(v, color=c, ls=ls, lw=1.1, label=s)
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(0, 56000); ax.set_xlabel("đồng/cổ phiếu (trên 44,84 triệu CP sau phát hành)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá hiện tại cao hơn trung vị của mọi phương pháp định giá")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_09_football_field", "Nguồn: kịch bản của nhóm nghiên cứu (ước lượng); bội số comp tav2_bq 28/10/2026 (8 mã; EV/EBITDA 6 mã). Vạch trắng = trung vị. Phép tính trong build_report.py.", ff)
    plt.close(fig)

    # 10. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("R1", "VinCons/BĐS chậm trả", 2, 5), ("R2", "Pha loãng tiếp", 4, 3),
        ("R3", "Phả Lại trễ/hiệu suất thấp", 4, 3), ("R4", "Tro bay: hợp đồng/đấu giá", 3, 3),
        ("R5", "Thừa cung AAC theo vùng", 3, 3), ("R6", "Biên gộp về 36%", 3, 4),
        ("R7", "Quản trị / công bố", 3, 2)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R2": (-0.3, 0.22), "R3": (-0.3, -0.22), "R4": (-0.3, 0.22), "R5": (-0.3, -0.22)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.5, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Biên gộp và VinCons: tác động lớn nhất; pha loãng: dễ xảy ra nhất")
    fig.tight_layout(rect=(0, 0.08, 0.72, 1))
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 29/10/2026.", rk)
    plt.close(fig)

    print(f"TERP 28/10={terp(CLOSE_2810):.0f} rights={CLOSE_2810-terp(CLOSE_2810):.0f}; TERP 29/10={terp(PX_2910):.0f}")
    print(f"12m Close lo={lo:.0f} hi={hi:.0f}")
    print(ff.round(0).to_string())


# ------------------------------------------------------------------ PDF
CSS = """
@font-face {font-family: dv; src: url(DejaVuSans.ttf);}
@font-face {font-family: dv; src: url(DejaVuSans-Bold.ttf); font-weight: bold;}
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
BREAK_BEFORE = ("1.", "3.", "5.", "6.", "7.", "8.", "9.", "Phụ lục A", "Phụ lục B")


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
        page.insert_text((42, 34), "SCL — CTCP Sông Đà Cao Cường · Báo cáo Due Diligence · 29/10/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "SCL_DD_investor_report_20261029.md"), os.path.join(HERE, "SCL_DD_investor_report_20261029.pdf"))
