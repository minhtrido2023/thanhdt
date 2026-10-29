"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư PVP (29/10/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (cùng thư mục figs/):
  fin_quarterly_bq.csv  — tav2_bq.ticker_financial (PVP, 2023Q1–2026Q3), kéo 29/10/2026
  price_raw.csv         — tav2_bq.ticker (PVP Close/Price/Volume/VNINDEX, 01/10/2025–28/10/2026)
Số BCTC (hard-code) lấy từ ../calc.py → ../out.txt (v2.1, 0 FAIL / 29 self-check), đã qua phản biện độc lập.
Mỗi hình ghi kèm CSV dữ liệu vẽ (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")

NAVY, ACCENT, GREY, LIGHT = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- số dùng chung (nguồn: ../REPORT.md v2.1 + ../out.txt) ----
SHARES = 103.702452          # triệu CP [BCTC Q3 tr.13]
PX_2910 = 18_750             # DNSE latest_trade 29/10/2026 14:29:47 ICT (giá sàn)
CLOSE_2810 = 20_150          # đóng cửa 28/10/2026 [BQ] = tham chiếu 29/10 [DNSE secdef]
BVPS = 20_246
PB_MED = 15_545              # PB trung vị lịch sử 0,77 × BVPS
PP_A = {"xau": 1_229, "co_so": 10_255, "tot": 20_057, "ky_vong": 8_115}
PP_B = {"xau": 15_701, "co_so": 24_428, "tot": 34_095, "ky_vong": 22_387}
PP_B_BOTH = {"xau": 12_821, "co_so": 23_468, "tot": 34_095, "ky_vong": 20_803}
FLOOR_PRE = (13_568, 14_887)
FLOOR_POST = (4_731, 6_050)


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


def vn(v, d=1):
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


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

    # 1. Vận tải: DT & LN gộp theo quý (BCTC, bộ phận)
    vt = pd.DataFrame({"ky": ["Q3/25", "Q1/26 (suy ra)", "Q2/26", "Q3/26"],
                       "dt_van_tai": [172.9, 232.6, 365.5, 224.4], "lng_van_tai": [62.5, 76.0, 146.5, 70.4]})
    vt["bien_pct"] = vt["lng_van_tai"] / vt["dt_van_tai"] * 100
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    xi = np.arange(len(vt)); w = 0.36
    ax.bar(xi - w / 2, vt["dt_van_tai"], w, color=LIGHT, label="Doanh thu vận tải")
    ax.bar(xi + w / 2, vt["lng_van_tai"], w, color=[NAVY, NAVY, ACCENT, NAVY], label="LN gộp vận tải")
    for i, r in vt.iterrows():
        ax.text(i - w / 2, r["dt_van_tai"] + 5, vn(r["dt_van_tai"]), ha="center", fontsize=7.5)
        ax.text(i + w / 2, r["lng_van_tai"] + 5, f"{vn(r['lng_van_tai'])}\n({vn(r['bien_pct'])}%)", ha="center", fontsize=7.2)
    ax.set_xticks(xi, vt["ky"]); ax.set_ylabel("tỷ đồng / quý"); ax.set_ylim(0, 430)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Q2/26 là quý đỉnh: LN gộp vận tải 146,5 tỷ; Q3/26 giảm 52% về 70,4 tỷ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_01_transport_quarterly", "Nguồn: BCTC Q3/2026 tr.13–14, Q2/2026 tr.13–14, bán niên 2026 soát xét tr.29–30 (báo cáo bộ phận). Q1/26 = H1 − Q2. Q3/25 còn trích dự phòng sửa chữa.", vt)
    plt.close(fig)

    # 2. LN gộp 9T theo mảng
    seg = pd.DataFrame({"mang": ["Vận tải", "FSO", "LPG + ủy thác + khác"],
                        "lng_9t_25": [140.7, 68.5, 225.9 - 140.7 - 68.5], "lng_9t_26": [292.9, 66.3, 362.4 - 292.9 - 66.3]})
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    left = {"lng_9t_25": 0, "lng_9t_26": 0}
    cols = [NAVY, GREY, LIGHT]
    for k, r in seg.iterrows():
        for yy, c in ((1, "lng_9t_25"), (0, "lng_9t_26")):
            ax.barh(yy, r[c], left=left[c], color=cols[k], height=0.5, label=r["mang"] if yy == 0 else None)
            if r[c] > 20:
                ax.text(left[c] + r[c] / 2, yy, vn(r[c]), ha="center", va="center", fontsize=8, color="white" if k == 0 else "#222")
            left[c] += r[c]
    ax.text(left["lng_9t_25"] + 4, 1, vn(left["lng_9t_25"]), va="center", fontsize=8.5, fontweight="bold")
    ax.text(left["lng_9t_26"] + 4, 0, vn(left["lng_9t_26"]), va="center", fontsize=8.5, fontweight="bold")
    ax.set_yticks([0, 1], ["9T/2026", "9T/2025"]); ax.set_xlim(0, 420); ax.set_xlabel("LN gộp, tỷ đồng")
    ax.legend(fontsize=7.5, frameon=False, ncol=3, loc="lower right", bbox_to_anchor=(1, 1.0))
    ax.set_title("Vận tải gánh 111% mức tăng LN gộp 9T; FSO đi ngang", pad=18)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_gross_profit_by_segment", "Nguồn: BCTC Q3/2026 và bán niên 2026 soát xét, báo cáo bộ phận; tổng LN gộp 9T 362,4 / 225,9 tỷ khớp KQKD.", seg)
    plt.close(fig)

    # 3. LNST quý
    x = np.arange(len(fin)); is26 = fin["quarter"].str.startswith("2026")
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(x, fin["NP_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    for i, v in enumerate(fin["NP_P0"]):
        ax.text(i, v + 1.5, vn(v), ha="center", fontsize=7, color="#333")
    ax.set_xticks(x, fin["lab"], fontsize=7.5); ax.set_ylabel("LNST, tỷ đồng")
    ax.set_ylim(0, 155)
    ax.set_title("LNST Q3/26 67,5 tỷ: −50% so với Q2, −2,5% so với cùng kỳ; 9T vẫn +80%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_03_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (tổng 3 quý 2026 = 278,03 tỷ, khớp BCTC 9T; Q2/26 = H1 soát xét − Q1 = 134,97, BCTC Q2 riêng 134,19). Kéo 29/10/2026.",
         fin[["quarter", "NP_P0"]])
    plt.close(fig)

    # 4. Bridge LNTT 9T báo cáo → cùng cơ sở
    br = pd.DataFrame({"buoc": ["LNTT 9T/25", "Không còn trích\ndự phòng (TT99)\n(suy luận)", "Apollo hết\nkhấu hao", "Tăng trưởng\nhoạt động", "LNTT 9T/26"],
                       "gia_tri": [194.3, 53.1, 35.7, 65.8, 348.9]})
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    base = 194.3
    ax.bar(0, base, color=GREY, width=0.6)
    run = base
    for i, (v, c) in enumerate(((53.1, LIGHT), (35.7, LIGHT), (65.8, NAVY)), start=1):
        ax.bar(i, v, bottom=run, color=c, width=0.6, edgecolor="#888" if c == LIGHT else c, hatch="//" if c == LIGHT else None)
        ax.text(i, run + v + 5, "+" + vn(v), ha="center", fontsize=8.5, fontweight="bold")
        run += v
    ax.bar(4, 348.9, color=ACCENT, width=0.6)
    ax.text(0, base + 5, vn(base), ha="center", fontsize=8.5, fontweight="bold")
    ax.text(4, 348.9 + 5, vn(348.9) + "\n(+79,5%)", ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(range(5), br["buoc"], fontsize=7.6); ax.set_ylim(0, 420); ax.set_ylabel("tỷ đồng")
    ax.set_title("+79,5% báo cáo; bỏ hai khác biệt kế toán chỉ còn +23% … +34%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_pbt_bridge", "Nguồn: BCTC Q3/2026 KQKD + LCTT (mã 02, 03); phép tính ../calc.py §3. Phần gạch chéo là khác biệt kế toán (ước lượng/suy luận). Cơ sở B: 348,9/283,1 = +23,2%; cơ sở A: 260,2/194,3 = +33,9%.", br)
    plt.close(fig)

    # 5. CFO vs LNST vs capex
    sub = fin[fin["quarter"] >= "2024Q1"].reset_index(drop=True)
    xs = np.arange(len(sub)); w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(xs - w / 2, sub["NP_P0"], w, color=LIGHT, label="LNST")
    ax.bar(xs + w / 2, sub["CF_OA_P0"], w, color=NAVY, label="CFO")
    ax.plot(xs, -sub["CF_Invest_P0"], color=ACCENT, marker="o", lw=1.4, label="Dòng tiền đầu tư ròng (chi = dương)")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(xs, sub["lab"], fontsize=7.5); ax.set_ylabel("tỷ đồng / quý"); ax.legend(fontsize=7.5, frameon=False, ncol=3, loc="upper left")
    ax.set_ylim(0, 700)
    ax.set_title("9T/26: CFO 473 tỷ = 1,70× LNST, capex gần 0 — lợi nhuận là thật về tiền")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_05_cfo_npat_capex", "Nguồn: tav2_bq.ticker_financial CF_OA_P0/NP_P0/CF_Invest_P0 (tổng 9T/26 khớp BCTC LCTT: CFO 473,0; capex 0,18). Chi đầu tư Q4/24 616,7 tỷ.",
         sub[["quarter", "NP_P0", "CF_OA_P0", "CF_Invest_P0"]])
    plt.close(fig)

    # 6. Tiền ròng: hiện tại → sau cổ tức → kịch bản capex
    sc = pd.DataFrame({"moc": ["30/9/2026\n(BCTC)", "Sau trừ phải trả\ncổ tức 109,5", "Chỉ mua\nAframax #2", "Mua cả hai\ndự án (116 tr USD)"],
                       "tien_ron_ty": [1125.6, 1016.0, 1016.0 - 17.08 * 26.04 - 39.42 * 26.04, 1016.0 - 116.0 * 26.04]})
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    cl = [NAVY, NAVY, GREY, ACCENT]
    ax.bar(range(4), sc["tien_ron_ty"], color=cl, width=0.6)
    for i, v in enumerate(sc["tien_ron_ty"]):
        ax.text(i, v + (40 if v > 0 else -190), vn(v, 0), ha="center", fontsize=9, fontweight="bold")
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(range(4), sc["moc"], fontsize=7.8); ax.set_ylabel("tiền ròng (+) / nợ ròng (−), tỷ đồng"); ax.set_ylim(-2300, 1400)
    ax.set_title("Mua cả hai dự án tàu đảo 1.016 tỷ tiền ròng thành ~2.005 tỷ nợ ròng")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_net_cash_capex", "Nguồn: BCTC Q3/2026 tr.3–5, 11 (tiền + tiền gửi HTM 1.734,0; vay 608,5); NQ ĐHĐCĐ 23/06/2026 + BCTC bán niên tr.34 (cơ cấu vốn dự án); tỷ giá VCB 26.040. Kịch bản = phép tính, không phải dự báo.", sc)
    plt.close(fig)

    # 7. FSO: dòng doanh thu theo lịch cam kết
    yrs = ["Hiện tại\n(Q3×4)", "7/26–6/27", "7/27–6/28", "7/28–6/29", "7/29–6/30", "7/30–6/31", "7/31–12/36\n(bình quân/năm)"]
    vals = [59.7 * 4, 415.8, 135.7, 135.7, 135.7, 135.7, 37.3]
    fso = pd.DataFrame({"ky": [y.replace("\n", " ") for y in yrs], "doanh_thu_ty": vals})
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(range(7), vals, color=[GREY, ACCENT, NAVY, NAVY, NAVY, NAVY, NAVY], width=0.62)
    ax.bar(1, 415.8 - 239.0, bottom=239.0, color="white", edgecolor=ACCENT, hatch="///", width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v + 8, vn(v), ha="center", fontsize=8)
    ax.text(1.42, 330, "177 tỷ vượt mức hiện tại:\nchưa hoà giải được", fontsize=7.2, color=ACCENT, va="center")
    ax.set_xticks(range(7), yrs, fontsize=7.4); ax.set_ylabel("tỷ đồng / năm"); ax.set_ylim(0, 470)
    ax.set_title("Lịch cam kết FSO: ~239 → ~136 tỷ/năm từ 7/2027 → ~37 tỷ/năm từ 7/2031")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_fso_schedule", "Nguồn: BCTC bán niên 2026 soát xét tr.34 (cam kết cho thuê không huỷ ngang 1.163,7 tỷ tại 30/6/2026, riêng FSO Đại Hùng Queen, theo đơn giá mới tới 31/12/2036). Chia đều theo năm = ước lượng.", fso)
    plt.close(fig)

    # 8. Giá 12 tháng + sự kiện
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-10-29"].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.plot(pd.Timestamp("2026-10-29"), PX_2910, "o", color=ACCENT, ms=5)
    a1.annotate("29/10 14:29: 18.750\n(sàn, DNSE)", (pd.Timestamp("2026-10-29"), PX_2910), xytext=(pd.Timestamp("2026-08-10"), 14300),
                textcoords="data", fontsize=7, color=ACCENT, ha="left", arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    ev = [("2026-06-23", "ĐHĐCĐ: duyệt 116 tr USD tàu; đổi GĐ"), ("2026-09-25", "25/09 tăng trần"),
          ("2026-10-08", "08/10 đỉnh 25.000"), ("2026-10-21", "21/10 sàn (VNINDEX +2,8%)")]
    ymax = px["Close"].max()
    for k, (d, s) in enumerate(ev):
        dd = pd.Timestamp(d)
        a1.axvline(dd, color=GREY, lw=0.8, ls=":")
        a1.text(dd, ymax * (0.99 - 0.07 * k), " " + s + " ", fontsize=6.8, color="#444", ha="right")
    a1.set_ylabel("đ/cp (điều chỉnh)")
    a2.bar(px["time"], px["Volume"] / 1e6, color=GREY, width=1.0)
    a2.set_ylabel("KL, triệu cp")
    a1.set_title("Giá 12 tháng: 13,1k (30/12/2025) → đỉnh 25,0k (08/10) → 18,75k (29/10, −25%)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_price_12m", "Nguồn: tav2_bq.ticker (Close điều chỉnh, Volume) 29/10/2025–28/10/2026; điểm 29/10 từ DNSE latest_trade 14:29:47 ICT. Mốc sự kiện là quan sát, không gán nhân quả.",
         px[["time", "Close", "Volume", "VNINDEX"]])
    plt.close(fig)
    lo, hi = px["Close"].min(), px["Close"].max()

    # 9. Football field
    rows = [
        ("SOTP (xấu–tốt), kỳ vọng theo xác suất mua", PP_B["xau"], PP_B["tot"], PP_B["ky_vong"]),
        ("SOTP nếu chắc chắn mua cả hai dự án", PP_B_BOTH["xau"], PP_B_BOTH["tot"], PP_B_BOTH["ky_vong"]),
        ("P/B lịch sử p25–p75 (0,53–0,91) × BVPS", 0.53 * BVPS, 0.91 * BVPS, PB_MED),
        ("P/E lịch sử × LNST 2027 (giá thị trường quen trả)", PP_A["xau"], PP_A["tot"], PP_A["ky_vong"]),
        ("Sàn tài sản trước capex (đội tàu = 0)", FLOOR_PRE[0], FLOOR_PRE[1], None),
        ("Sàn tài sản sau capex mua cả hai", FLOOR_POST[0], FLOOR_POST[1], None),
        ("Vùng giá 12 tháng (điều chỉnh)", lo, hi, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "trung_tam"])
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        col = ACCENT if i == 0 else (GREY if i >= 4 else NAVY)
        ax.barh(yy, max(r["cao"] - r["thap"], 250), left=r["thap"], color=col, height=0.5, alpha=0.88)
        ax.text(r["thap"] - 400, yy, vn(r["thap"] / 1e3), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 400, yy, vn(r["cao"] / 1e3), ha="left", va="center", fontsize=7.5)
        if r["trung_tam"] is not None and r["trung_tam"] == r["trung_tam"]:
            ax.plot(r["trung_tam"], yy, "|", color="white", ms=14, mew=2.2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.6)
    ax.axvspan(PB_MED, PP_B["ky_vong"], color=ACCENT, alpha=0.08, lw=0, label="Dải tham khảo 15,5–22,4k")
    ax.axvline(PX_2910, color="#555", ls=":", lw=1.1, label="Giá 29/10 14:29: 18,75k (sàn)")
    ax.axvline(CLOSE_2810, color=NAVY, ls="--", lw=1.0, label="Đóng cửa 28/10: 20,15k")
    ax.legend(fontsize=6.8, frameon=False, loc="upper center", bbox_to_anchor=(0.25, -0.2), ncol=3)
    ax.set_xlim(-2000, 40000); ax.set_xlabel("đồng/cổ phiếu (103,7 triệu CP)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá nằm trong dải tham khảo; không có biên an toàn")
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    save(fig, "fig_09_football_field", "Nguồn: ../calc.py §6 (ước lượng của nhóm nghiên cứu); P/E, P/B lịch sử PVP từ 2018 (tav2_bq). Vạch trắng = kỳ vọng/trung vị. Đây là quan điểm định giá ngoài khung §2.5, không phải căn cứ mua.", ff)
    plt.close(fig)

    # 10. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("R1", "Mua tàu ở đỉnh giá tàu cũ", 4, 5), ("R2", "Cước tàu dầu về mức thường 2027", 4, 4),
        ("R3", "FSO: dòng tiền giảm; 177 tỷ chưa hoà giải", 3, 3), ("R4", "Pha loãng (nếu ĐHĐCĐ có phát hành)", 2, 3),
        ("R5", "Bên liên quan 63% DT; quản trị", 3, 2), ("R6", "Chi phí sửa chữa định kỳ lên đà", 4, 2),
        ("R7", "Tàu già (Apollo ~21 tuổi), vetting", 3, 3), ("R8", "Lãi tiền gửi giảm khi chi VCSH", 4, 2)],
        columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R3": (0, 0.22), "R7": (0, -0.22), "R6": (0, 0.22), "R8": (0, -0.22)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.2, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất 12–18 tháng (nhận định)", fontsize=8); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Mua tàu ở đỉnh và cước quay đầu: hai rủi ro chi phối")
    fig.tight_layout(rect=(0, 0.08, 0.66, 1))
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu bản đọc ngành độc lập 29/10/2026.", rk)
    plt.close(fig)

    print(f"12m Close lo={lo:.0f} hi={hi:.0f}")
    print(ff.round(0).to_string())
    print(sc.round(1).to_string())


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
BREAK_BEFORE = ("7.", "Phụ lục A")


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
        page.insert_text((42, 34), "PVP — CTCP Vận tải Dầu khí Thái Bình Dương · Báo cáo Due Diligence · 29/10/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "PVP_DD_investor_report_20261029.md"), os.path.join(HERE, "PVP_DD_investor_report_20261029.pdf"))
