"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư PAT (14/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py figs   (hình)
       /home/trido/thanhdt/wc_venv/bin/python -I build_report.py pdf    (PDF; cần banner figs/title_banner.png)
Đầu vào (figs/): fin_quarterly_bq.csv (tav2_bq.ticker_financial PAT 2023Q1–2026Q3, kéo 14/11/2026),
price_raw.csv (tav2_bq.ticker PAT Close/Volume 13/11/2025–13/11/2026). Số BCTC hard-code có nguồn
(BCTC riêng Q3/2026, bán niên 2026 soát xét, BCTC 2025 kiểm toán); số định giá lấy từ ../calc/valuation_PAT.csv.
Mỗi hình ghi kèm CSV (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.join(HERE, "..", "calc", "valuation_PAT.csv")
MD = os.path.join(HERE, "PAT_DD_investor_report_20261114.md")
PDF = os.path.join(HERE, "PAT_DD_investor_report_20261114.pdf")

NAVY, ACCENT, GREY, LIGHT = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 71_000            # đóng cửa 13/11/2026 [BQ tav2_bq.ticker]
CENTRE, LO, HI = 66_600, 56_600, 76_600
SCEN = {"Xấu": (56_600, 0.30), "Cơ sở": (71_600, 0.50), "Tốt": (106_100, 0.20)}
SHARES = 25_000_000
NETCASH = 415.4


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


def vn(v, d=1):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def qlabel(q):
    return q[4:] + "/" + q[2:4]


def figs():
    import numpy as np
    import pandas as pd
    plt = setup_mpl()
    val = pd.read_csv(CALC)
    chk = {"centre": float(val[val["item"] == "centre_after_liq10"]["per_share_vnd"].iloc[0]),
           "base": float(val[val["item"] == "base"]["per_share_vnd"].iloc[0]),
           "bad": float(val[val["item"] == "bad"]["per_share_vnd"].iloc[0]),
           "good": float(val[val["item"] == "good"]["per_share_vnd"].iloc[0])}
    assert abs(chk["centre"] - CENTRE) < 60 and abs(chk["base"] - 71_600) < 60 and abs(chk["bad"] - 56_600) < 60 and abs(chk["good"] - 106_100) < 60, chk
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    fin["Revenue"] = fin["Revenue_P0"] / 1e9
    fin["NP"] = fin["NP_P0"] / 1e9
    fin.loc[fin["quarter"] == "2025Q4", "NP"] = 70.89      # số kiểm toán (năm 343,21 − 9T 272,33)
    fin["lab"] = fin["quarter"].map(qlabel)
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])

    # 0. Hero
    fig = plt.figure(figsize=(7.2, 3.0))
    tiles = [("Giá đóng cửa 13/11", f"{vn(PX,0)} đ", "trong vùng hợp lý"),
             ("Giá trị trung tâm", f"{vn(CENTRE,0)} đ", "sau chiết khấu thanh khoản 10%"),
             ("Vùng hợp lý", "56.600–76.600", "đ/cổ phiếu"),
             ("Tiền ròng", f"{vn(NETCASH,0)} tỷ", "≈ 16.600 đ/cp · 23% vốn hoá")]
    for i, (a, b, c) in enumerate(tiles):
        ax = fig.add_axes([0.01 + i * 0.248, 0.60, 0.235, 0.36]); ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#F3F5F7", transform=ax.transAxes))
        ax.text(0.06, 0.80, a, fontsize=7.4, color="#555", transform=ax.transAxes)
        ax.text(0.06, 0.42, b, fontsize=13, fontweight="bold", color=NAVY if i != 0 else ACCENT, transform=ax.transAxes)
        ax.text(0.06, 0.12, c, fontsize=6.8, color="#555", transform=ax.transAxes)
    ax = fig.add_axes([0.06, 0.13, 0.90, 0.36])
    ax.axvspan(LO, HI, color="#DCE6F1", lw=0)
    ax.axvline(CENTRE, color=NAVY, lw=1.4)
    ax.axvline(PX, color=ACCENT, lw=1.8)
    for k, (v, p) in SCEN.items():
        ax.plot(v, 0.5, "v", color=GREY, ms=9)
        ax.text(v + (2600 if k == "Cơ sở" else 0), 0.78, f"{k} {int(p*100)}%\n{vn(v,0)}", ha="center", fontsize=7, color="#333", va="bottom", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
    ax.text(CENTRE, 0.04, "tâm 66.600", ha="right", fontsize=7, color=NAVY, va="bottom")
    ax.text(PX + 600, 0.04, "giá 71.000", ha="left", fontsize=7, color=ACCENT, va="bottom", fontweight="bold")
    ax.set_xlim(45_000, 115_000); ax.set_ylim(0, 1.45); ax.set_yticks([]); ax.grid(False)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.spines["left"].set_visible(False)
    fig.text(0.06, 0.52, "Vùng xanh = vùng hợp lý; tam giác = ba kịch bản (xác suất 0,3 / 0,5 / 0,2); đ/cổ phiếu", fontsize=6.8, color="#555")
    save(fig, "fig_00_hero", "Nguồn: nhóm nghiên cứu; giá đóng cửa 13/11/2026 từ tav2_bq.ticker; BCTC Q3/2026; calc/valuation_PAT.csv.",
         pd.DataFrame({"item": ["gia_13_11", "tam", "vung_thap", "vung_cao", "xau", "co_so", "tot", "net_cash_ty"],
                       "value": [PX, CENTRE, LO, HI, 56_600, 71_600, 106_100, NETCASH]}))
    plt.close(fig)

    # 1. Chuỗi giá trị (sơ đồ minh hoạ, vector)
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); ax.axis("off"); ax.grid(False)
    ax.set_xlim(0, 100); ax.set_ylim(0, 42)

    def box(x, y, w, h, t, fc, tc="white", fs=7.4):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="white", lw=1.2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc, fontweight="bold", linespacing=1.3)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color="#666", lw=1.1))
    box(1, 24, 24, 13, "Quặng apatit\n(mua từ công ty mẹ)", GREY, fs=7)
    box(1, 6, 24, 13, "Than cốc\nĐiện", GREY, fs=7)
    box(33, 12, 24, 20, "PAT\nLò điện\nP4 thô\n20 kt/năm", NAVY, fs=8.2)
    box(66, 27, 33, 12, "Công ty mẹ (DLC)\n64% DT 9T/26 · 85% DT Q3/26", ACCENT, fs=6.8)
    box(66, 5, 33, 12, "Xuất khẩu\n35% DT 9T/26 (90% DT 2025)", "#6b7f95", fs=6.8)
    arrow(25, 30, 33, 25); arrow(25, 12, 33, 19); arrow(57, 26, 66, 31); arrow(57, 18, 66, 12)
    ax.text(82.5, 22, "Hạ nguồn (axit nhiệt, muối…)\nnằm ở DLC/DGC, không ở PAT", ha="center", fontsize=6.6, color="#555", va="center")
    ax.text(0.5, 1.0, "NVL 749,9 tỷ (2025) và 627,9 tỷ (9T/26) mua từ DLC", fontsize=6.8, color="#555")
    ax.set_title("PAT là mắt xích gia công P4 thô: quặng vào từ mẹ, sản phẩm đi ra chủ yếu cho mẹ", loc="left")
    save(fig, "fig_01_value_chain", "Sơ đồ MINH HOẠ (không phải ảnh sản phẩm). Nguồn: BCTC Q3/2026 (thuyết minh bên liên quan, bộ phận địa lý), BCTC 2025; tỷ trọng = đo từ BCTC.",
         pd.DataFrame({"khau": ["ban_DLC_9T26", "ban_DLC_Q3_26", "xuat_khau_9T26", "xuat_khau_2025", "mua_DLC_2025", "mua_DLC_9T26"],
                       "gia_tri": ["878,14 tỷ = 63,7% DT", "376,29 tỷ = 85,5% DT", "487,51 tỷ = 35,3% DT", "1.738,33 tỷ = 90,4% DT", "749,86 tỷ", "627,92 tỷ"]}))
    plt.close(fig)

    # 3. Doanh thu quý + biên gộp BCTC
    sub = fin[fin["quarter"] >= "2025Q1"].reset_index(drop=True)
    x = np.arange(len(sub))
    gpm = {"2025Q3": 25.7, "2026Q1": 13.6, "2026Q2": 25.0, "2026Q3": 14.5}
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.bar(x, sub["Revenue"], color=np.where(sub["quarter"].str.startswith("2026"), NAVY, LIGHT), width=0.65)
    for i, v in enumerate(sub["Revenue"]):
        ax.text(i, v + 6, vn(v, 0), ha="center", fontsize=7, color="#333")
    ax.set_ylabel("Doanh thu quý, tỷ đồng"); ax.set_xticks(x, sub["lab"]); ax.set_ylim(0, 640)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    for q, g in gpm.items():
        i = int(sub.index[sub["quarter"] == q][0])
        ax2.plot(i, g, "o", color=ACCENT, ms=7, zorder=5)
        ax2.annotate(vn(g) + "%", (i, g), xytext=(0, 9), textcoords="offset points", ha="center", color=ACCENT, fontsize=8.5, fontweight="bold")
    ax2.plot([], [], "o", color=ACCENT, label="Biên gộp theo BCTC (Q1: báo cáo quý; Q2: suy từ 9T trừ Q1, Q3)")
    ax2.set_ylim(0, 45); ax2.set_ylabel("Biên gộp, %"); ax2.legend(loc="upper left", fontsize=7, frameon=False)
    ax.set_title("Biên gộp Q3/26 14,5%, bằng một nửa Q3/25 (25,7%), dù giá P4 Trung Quốc cao hơn 22%")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_03_revenue_gpm", "Nguồn: DT quý tav2_bq.ticker_financial (khớp BCTC Q3/26: 440,03; Q3/25: 506,73); biên gộp từ BCTC Q3/2026 và 9T. Chưa có sản lượng tấn.",
         sub[["quarter", "Revenue"]].assign(gpm_bctc=sub["quarter"].map(gpm)))
    plt.close(fig)

    # 4. LNST quý
    sub = fin[fin["quarter"] >= "2024Q1"].reset_index(drop=True)
    x = np.arange(len(sub))
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.bar(x, sub["NP"], color=np.where(sub["quarter"].str.startswith("2026"), NAVY, LIGHT), width=0.65)
    for i, v in enumerate(sub["NP"]):
        ax.text(i, v + 1.5, vn(v), ha="center", fontsize=7, color="#333")
    ax.set_xticks(x, sub["lab"], fontsize=7.5); ax.set_ylabel("LNST, tỷ đồng"); ax.set_ylim(0, 125)
    ax.set_title("LNST Q3/26 59,3 tỷ: −46% so với Q3/25 và −46% so với Q2/26; 9T/26 đạt 77% kế hoạch 280 tỷ")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_04_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0; Q4/25 lấy số kiểm toán 70,89 (năm 343,21 − 9T 272,33). 9T/26 = 215,71 theo BCTC Q3/2026.",
         sub[["quarter", "NP"]])
    plt.close(fig)

    # 5. Bên liên quan
    rp = pd.DataFrame({"ky": ["2024", "2025", "9T/2026"], "ban_DLC": [313.00, 163.72, 878.14], "mua_DLC": [533.62, 749.86, 627.92],
                       "dt": [1721.44, 1923.39, 1379.30]})
    rp["ty_trong_ban"] = rp["ban_DLC"] / rp["dt"] * 100
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xi = np.arange(3); w = 0.34
    ax.bar(xi - w / 2, rp["ban_DLC"], w, color=ACCENT, label="Bán cho DLC (đầu ra)")
    ax.bar(xi + w / 2, rp["mua_DLC"], w, color=NAVY, label="Mua từ DLC (đầu vào)")
    for i in range(3):
        ax.text(i - w / 2, rp["ban_DLC"][i] + 15, vn(rp["ban_DLC"][i], 0), ha="center", fontsize=8)
        ax.text(i + w / 2, rp["mua_DLC"][i] + 15, vn(rp["mua_DLC"][i], 0), ha="center", fontsize=8)
        ax.text(i - w / 2, 40, vn(rp["ty_trong_ban"][i], 0) + "% DT", ha="center", fontsize=7.5, color="white", fontweight="bold")
    ax.set_xticks(xi, rp["ky"]); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 980); ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Bán cho công ty mẹ: 18% DT (2024), 9% (2025), rồi 64% (9T/26); riêng Q3/26 là 85%")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_05_related_party", "Nguồn: BCTC 2025 và BCTC Q3/2026, thuyết minh giao dịch bên liên quan (DLC = CTCP Hoá chất Đức Giang Lào Cai, sở hữu 51%). DT: 2024 1.721,44; 2025 1.923,39; 9T/26 1.379,30.", rp)
    plt.close(fig)

    # 6. Tiền ròng + cầu CFO
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1, 1.25]})
    steps = [("Tiền + tiền gửi\nkỳ hạn", 559.3, 0), ("Vay\nngắn hạn", -67.2, 559.3), ("Quỹ khen thưởng\nphúc lợi", -76.7, 492.1)]
    for i, (n, v, b) in enumerate(steps):
        a1.bar(i, v if i == 0 else abs(v), bottom=0 if i == 0 else b + v, color=NAVY if i == 0 else GREY, width=0.6)
        a1.text(i, (v if i == 0 else b) + 12, vn(v), ha="center", fontsize=8)
    a1.bar(3, NETCASH, color=ACCENT, width=0.6); a1.text(3, NETCASH + 12, vn(NETCASH), ha="center", fontsize=8.5, fontweight="bold", color=ACCENT)
    a1.set_xticks(range(4), [s[0] for s in steps] + ["Tiền ròng\n30/09/26"], fontsize=6.5); a1.set_ylim(0, 640); a1.set_ylabel("tỷ đồng")
    a1.set_title("Tiền ròng 415 tỷ ≈ 16.600 đ/cp", fontsize=8.8)
    bridge = [("LN trước\nvốn lưu động", 243.4), ("Thu phải thu\n(khách XK)", 249.4), ("Tăng\ntồn kho", -52.5), ("Trả nhà\ncung cấp", -292.7), ("Thuế, lãi,\nkhác", -19.4)]
    cum = 0
    for i, (n, v) in enumerate(bridge):
        a2.bar(i, abs(v), bottom=cum if v > 0 else cum + v, color=NAVY if v > 0 else ACCENT, width=0.6)
        a2.text(i, (cum + v if v > 0 else cum) + 8, ("+" if v > 0 else "−") + vn(abs(v)), ha="center", fontsize=7.5)
        cum += v
    a2.bar(len(bridge), cum, color="#2e7d5b", width=0.6); a2.text(len(bridge), cum + 8, vn(cum), ha="center", fontsize=8.5, fontweight="bold", color="#2e7d5b")
    a2.set_xticks(range(len(bridge) + 1), [b[0] for b in bridge] + ["CFO\n9T/26"], fontsize=6.3); a2.set_ylim(0, 560)
    a2.set_title("CFO 9T/26 +128 tỷ sau khi trả mẹ 297 tỷ", fontsize=8.8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_netcash_cfo", "Nguồn: BCTC Q3/2026 (BCĐKT 30/09, LCTT 9T; 439 tỷ tiền gửi đang cầm cố). Phải trả nhà cung cấp: chủ yếu công ty mẹ (313,3 giảm còn 16,5 tỷ). Mục 'thuế, lãi, khác' là phần còn lại để khớp CFO 128,2.",
         pd.DataFrame({"muc": ["tien+HTM", "vay", "quy_KTPL", "net_cash", "LN_truoc_VLD", "thu_phai_thu", "ton_kho", "tra_NCC", "thue_quy_lai_vay_khac", "CFO_9T"],
                       "ty_dong": [559.3, -67.2, -76.7, 415.4, 243.4, 249.4, -52.5, -292.7, -19.4, 128.2]}))
    plt.close(fig)

    # 7. Đồng hồ cắt hào
    fig, ax = plt.subplots(figsize=(7.2, 2.5)); ax.set_ylim(0, 10); ax.set_xlim(2025.5, 2036.5); ax.grid(False)
    ax.axhline(4, color="#555", lw=1.4)
    ev = [(2026.0, "Thuế XK P4 10%\n(đang áp)", 6.2, GREY), (2027.0, "01/01/2027:\nthuế XK P4 15%", 6.2, ACCENT),
          (2031.0, "TNDN 5% lên 10%\n(hết giảm 50%)", 6.2, ACCENT), (2033.0, "TNDN 20%\n(hết ưu đãi)", 6.2, ACCENT),
          (2034.6, "~2034–35: hết thuê đất\n(ước lượng từ phân bổ GPMB)", 3.0, GREY)]
    for xv, t, yv, c in ev:
        ax.plot(xv, 4, "o", color=c, ms=8, zorder=4)
        ax.text(xv + (-0.15 if xv == 2026.0 else (0.15 if xv == 2027.0 else 0)), yv, t, ha="right" if xv == 2026.0 else ("left" if xv == 2027.0 else "center"), fontsize=7, color="#333", va="bottom" if yv > 4 else "top")
    ax.text(2025.6, 8.9, "Quặng: nguồn cung do cơ quan quản lý và công ty mẹ chi phối, không có mốc ngày cố định", fontsize=7, color="#555")
    ax.set_xticks(range(2026, 2037)); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_title("Bốn đồng hồ làm hẹp lợi thế: thuế xuất khẩu, thuế TNDN, thuê đất, quặng")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_07_moat_clocks", "Nguồn: NĐ 199/2025/NĐ-CP (tóm tắt EY 07/2025); BCTC Q3/2026 thuyết minh 27 (thuế TNDN), thuyết minh 9 (GPMB đất thuê phân bổ 16 năm). Mốc thuê đất là ước lượng.",
         pd.DataFrame({"moc": [e[0] for e in ev], "su_kien": [e[1].replace("\n", " ") for e in ev]}))
    plt.close(fig)

    # 8. Football field
    lo12, hi12 = float(px["Close"].min()), float(px["Close"].max())
    rows = [("Ba kịch bản (xấu – tốt)", 56_600, 106_100, 71_600),
            ("Hai nền: DCF dài hạn – chuẩn hoá ngắn hạn", 71_600, 91_700, None),
            ("Có trọng số, lãi huy động ±100bp (trước CK)", 69_800, 78_900, 74_000),
            ("Sau chiết khấu thanh khoản 20% – 0%", 59_200, 74_000, 66_600),
            ("Giả định mất lợi thế cạnh tranh (trước – sau CK)", 60_800, 67_500, None),
            ("Giá 12 tháng (đóng cửa)", lo12, hi12, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "diem"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.axvspan(LO, HI, color="#EAF0F6", lw=0)
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=NAVY if i < 5 else GREY, height=0.5, alpha=0.9)
        ax.text(r["thap"] - 1000, yy, vn(r["thap"] / 1e3), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 1000, yy, vn(r["cao"] / 1e3), ha="left", va="center", fontsize=7.5)
        if r["diem"] == r["diem"] and r["diem"] is not None:
            ax.plot(r["diem"], yy, "|", color="white", ms=14, mew=2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.4)
    ax.axvline(CENTRE, color=NAVY, ls="--", lw=1.1, label="Tâm 66.600")
    ax.axvline(PX, color=ACCENT, ls="-", lw=1.4, label="Giá 13/11: 71.000")
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="center right", bbox_to_anchor=(1.0, 0.42))
    ax.set_xlim(40_000, 125_000); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_xlabel("đ/cổ phiếu · nền xanh = vùng hợp lý · vạch trắng = điểm giữa", fontsize=8)
    ax.set_title("Giá nằm trong vùng hợp lý, cao hơn tâm 6,6%, cách cận trên 7,3%")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_08_football_field", "Nguồn: calc/valuation_PAT.csv (mô hình FCFE, r 13,5%); giá 12 tháng tav2_bq.ticker 13/11/2025–13/11/2026.", ff)
    plt.close(fig)

    # 9. Giá 12 tháng
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.5), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.axhspan(LO, HI, color="#EAF0F6", lw=0); a1.axhline(CENTRE, color=NAVY, ls="--", lw=1)
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    ymax = px["Close"].max()
    for k, (d, s) in enumerate([("2026-03-17", "17/03 khởi tố vụ án"), ("2026-06-01", "01/06 hạn chế GD"), ("2026-06-20", "20/06 BCKT 2025"), ("2026-10-20", "20/10 BCTC Q3")]):
        dd = pd.Timestamp(d); a1.axvline(dd, color=GREY, lw=0.8, ls=":")
        a1.text(dd, (ymax * (1.0 - 0.07 * k) if k < 3 else 58_800), " " + s + " ", fontsize=6.8, color="#444", ha="left" if k < 3 else "right")
    a1.set_ylabel("đ/cp"); a1.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    a2.bar(px["time"], px["Volume"] / 1e3, color=GREY, width=1.0); a2.set_ylabel("KL, nghìn cp")
    a1.set_title(f"Giá 12 tháng (điều chỉnh) dao động {vn(lo12/1e3,1)}–{vn(hi12/1e3,1)}k; khối lượng mỏng: {int((px['Volume']<1000).sum())}/{len(px)} phiên khớp dưới 1.000 cp")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_09_price_12m", "Nguồn: tav2_bq.ticker (đóng cửa, khối lượng) 13/11/2025–13/11/2026; mốc sự kiện từ BCTC/báo chí, chỉ để tham chiếu thời điểm, không gán nhân quả. Nền xanh = vùng hợp lý; vạch đứt = tâm.",
         px[["time", "Close", "Volume"]])
    plt.close(fig)
    adv = px["Volume"].median()
    print(f"price 12m lo={lo12:.0f} hi={hi12:.0f} last={px['Close'].iloc[-1]:.0f} median vol={adv:.0f} n={len(px)} zero/low(<1000)={(px['Volume']<1000).sum()}")


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
BREAK_BEFORE = ("1.", "3.", "Phụ lục A")


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
    md = "![banner](figs/title_banner.png)\n" + "\n".join(l for k, l in enumerate(md.split("\n")) if not (l.startswith("# ") and k < 3))
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
        pdf(MD, PDF)
