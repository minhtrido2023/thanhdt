"""Biểu đồ + PDF cho báo cáo DD nhà đầu tư PNJ (14/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/):
  fin_quarterly_bq.csv — cơ sở dữ liệu tài chính quý (PNJ 2022Q1–2026Q3), kéo 14/11/2026
  price_raw.csv        — giá ngày PNJ (Close điều chỉnh / Price chưa điều chỉnh), 03/11/2025–13/11/2026
Số BCTC hard-code có trích nguồn: BCTC hợp nhất Q3/2026 [HN], BCTC bán niên soát xét 2026 [SX], báo cáo KQKD Q3/2026 [IR],
tài liệu "Tình hình hoạt động & tài chính Q3.2026" trình ĐHĐCĐ 21/10/2026 [ĐHĐCĐ], mô hình calc/model_r2_out.json.
Ảnh sản phẩm/logo: pnj.com.vn (src/web/). Mỗi hình kèm CSV dữ liệu vẽ.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
DD = os.path.dirname(HERE)
WEB = os.path.join(DD, "src", "web")

NAVY, ACCENT, GOLD, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#B8892B", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

M = json.load(open(os.path.join(DD, "calc", "model_r2_out.json")))
PX = 14_950                      # DNSE latest_trade: khớp cuối 14:45:04 13/11/2026 (HOSE); phiên 14/11 không giao dịch
SH_NOW = 511.72                  # triệu cp lưu hành
SH_NEW_MAX = 550.0               # tối đa, tờ trình 622/2026/TTr-HĐQT
BASE = (M["base_g5_ps550"], M["base_g0_ps550"])        # 6.366 / 7.635
BULL = (M["bull_g0_ps550"], M["bull_g5_ps550"])        # 11.929 / 14.368
BEAR = (M["bear_alt_g5_ps550"], M["bear_alt_g0_ps550"])  # 3.267 / 5.726
GRID = M["level_grid"]
PLAN = {  # [ĐHĐCĐ p9] nghìn tỷ đồng
    "nam": ["2024", "2025", "2026KH", "2027KH", "2028KH", "2029KH"],
    "dt": [38.2, 35.4, 39.1, 43.4, 50.6, 57.7], "lng": [6.7, 7.7, -2.4, 3.8, 5.5, 6.3],
    "lnst": [2.1, 2.8, -6.3, 0.1, 1.2, 1.6]}


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def implied_level():
    """Nội suy tuyến tính mức LNST 2029 mà giá 14.950 ngầm định (g=5%, n=550tr) từ lưới mô hình."""
    ks = sorted(GRID, key=float)
    for a, b in zip(ks, ks[1:]):
        va, vb = GRID[a]["g5_n550"], GRID[b]["g5_n550"]
        if va <= PX <= vb:
            return float(a) + (PX - va) / (vb - va) * (float(b) - float(a))
    return None


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
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 138)), fontsize=6.4, color="#666", ha="left", va="bottom")
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
    fin = fin[fin["quarter"] >= "2023Q1"].reset_index(drop=True)
    for c in ["Revenue_P0", "NP_P0", "CF_OA_P0", "Cash_P0", "StDebt_P0", "LtDebt_P0", "Inventory_P0"]:
        fin[c] = fin[c] / 1e9
    fin["lab"] = fin["quarter"].map(qlabel)
    x = np.arange(len(fin))
    is26 = fin["quarter"].str.startswith("2026")
    imp = implied_level()

    # 0. HERO
    fig = plt.figure(figsize=(7.4, 3.0))
    fig.patch.set_facecolor("#0d1b2a")
    def panel(rect):
        ax = fig.add_axes(rect); ax.set_facecolor("#0d1b2a"); ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(colors="#cfd6de", labelsize=7)
        return ax
    a1 = panel((0.03, 0.14, 0.27, 0.6))
    a1.barh([1, 0], [39, 27], color=[GOLD, "#8fa3b8"], height=0.42)
    for y, v, t in ((1, 39, "Trang sức VN Q3/26, tấn YoY"), (0, 27, "Giá vàng thế giới từ đỉnh T1/26")):
        a1.text(0, y + 0.33, t, color="#e6ebf0", fontsize=7, va="bottom")
        a1.text(v + 1.5, y, f"−{v}%", va="center", ha="left", color="white", fontsize=9, fontweight="bold")
    a1.set_xlim(0, 55); a1.set_ylim(-0.5, 1.75); a1.set_xticks([]); a1.set_yticks([])
    a1.set_title("NGÀNH · khối lượng gần đáy chu kỳ", color="#e0a526", fontsize=8.5, loc="left")
    a2 = panel((0.37, 0.14, 0.27, 0.6))
    cols = ["#8fa3b8" if v >= 0 else ACCENT for v in PLAN["lnst"]]
    a2.bar(range(6), PLAN["lnst"], color=cols, width=0.65)
    for i, v in enumerate(PLAN["lnst"]):
        a2.text(i, v + (0.25 if v >= 0 else -1.0), vn(v, 1), ha="center", color="white", fontsize=7)
    a2.set_xticks(range(6), ["2024", "25", "26KH", "27KH", "28KH", "29KH"], color="#cfd6de", fontsize=6.5)
    a2.set_yticks([]); a2.axhline(0, color="#cfd6de", lw=0.6); a2.set_ylim(-7.9, 3.9)
    a2.set_title("KẾ HOẠCH DN · LNST, nghìn tỷ", color="#e0a526", fontsize=8.5, loc="left")
    a3 = panel((0.70, 0.14, 0.28, 0.6))
    for y, (lo, hi), t, c in ((1, BASE, "Cơ sở (kế hoạch DN)", "#8fa3b8"), (0, BULL, "Tốt (về kinh tế 2023–25)", "#5f7d99")):
        a3.barh(y, hi - lo, left=lo, color=c, height=0.36)
        a3.text(hi if y == 0 else lo, y + 0.27, t, color="#e6ebf0", fontsize=6.8, va="bottom", ha="right" if y == 0 else "left")
    a3.axvline(PX, color=ACCENT, lw=2)
    a3.text(PX - 300, 1.75, f"Giá 13/11: {vn(PX)}", color="#ff9d85", ha="right", fontsize=7.2, fontweight="bold")
    a3.set_yticks([]); a3.set_xlim(0, 18000); a3.set_ylim(-0.5, 2.0)
    a3.set_xticks([0, 5000, 10000, 15000]); a3.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    a3.set_title("ĐỊNH GIÁ · đ/cp sau phát hành", color="#e0a526", fontsize=8.5, loc="left")
    fig.text(0.03, 0.9, "Chuỗi trang sức lớn tái cấu trúc sau cú sốc thu đổi: kế hoạch lỗ 2026, hồi phục 2027–29; giá ngang kịch bản tốt",
             color="white", fontsize=8.6, fontweight="bold")
    fig.text(0.03, 0.025, "Nguồn: WGC Gold Demand Trends Q3/2026 qua đọc ngành độc lập; kế hoạch DN trình ĐHĐCĐ 21/10/2026 (tr.9); mô hình của nhóm nghiên cứu (ước lượng, 550 triệu cp mới).",
             color="#9fb0c2", fontsize=6.0)
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200, facecolor=fig.get_facecolor())
    pd.DataFrame({"chi_so": ["trang_suc_vn_q3_yoy_pct", "gia_vang_tu_dinh_pct"] + [f"lnst_{n}" for n in PLAN["nam"]] + ["base_lo", "base_hi", "bull_lo", "bull_hi", "gia"],
                  "gia_tri": [-39, -27] + PLAN["lnst"] + [BASE[0], BASE[1], BULL[0], BULL[1], PX]}).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)
    plt.close(fig)

    # 1. DT quý + biên gộp
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.bar(x, fin["Revenue_P0"], color=np.where(is26, NAVY, LIGHT), width=0.7)
    ax.set_ylabel("Doanh thu gộp quý, tỷ đồng"); ax.set_xticks(x, fin["lab"], fontsize=7.2)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    i25, i26 = int(fin.index[fin["quarter"] == "2025Q3"][0]), int(fin.index[fin["quarter"] == "2026Q3"][0])
    ax2.plot(i25, 19.8, "o", color=NAVY, ms=7); ax2.annotate("19,8%", (i25, 19.8), xytext=(-6, 7), textcoords="offset points", ha="right", fontsize=8, color=NAVY, fontweight="bold")
    ax2.plot(i26, 8.7, "o", color=ACCENT, ms=7); ax2.annotate("8,7%\nbáo cáo", (i26, 8.7), xytext=(10, -2), textcoords="offset points", ha="left", va="center", fontsize=7.5, color=ACCENT, fontweight="bold")
    ax2.vlines(i26 + 0.25, 13.3, 20.3, color=GREEN, lw=4)
    ax2.annotate("13,3–20,3%\ntrước\ndự phòng", (i26 + 0.25, 16.8), xytext=(10, 0), textcoords="offset points", ha="left", va="center", fontsize=7.2, color=GREEN)
    ax2.set_ylim(0, 28); ax2.set_ylabel("Biên gộp quý, %"); ax.set_xlim(-0.6, len(x) + 0.9)
    ax.set_title("Biên gộp Q3/26 8,7% chứa dự phòng; trước dự phòng 13,3–20,3% vs 19,8% cùng kỳ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_01_revenue_margin",
         "Nguồn: doanh thu gộp quý (mã 01) theo cơ sở dữ liệu tài chính, khớp BCTC; biên gộp BCTC hợp nhất Q3/2025, Q3/2026. Biên trước dự phòng = cộng lại dự phòng quý theo 2 cách (LCTT mã 03: 320,7 tỷ; chênh dự phòng giảm giá tồn kho 30/6–30/9: 812,1 tỷ) — khoảng, không phải một số.",
         fin[["quarter", "Revenue_P0"]].assign(gpm_bctc=fin["quarter"].map({"2025Q3": 19.8, "2026Q3": 8.7})))
    plt.close(fig)

    # 2. LNST quý
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    np_ = fin["NP_P0"].tolist(); labs = fin["lab"].tolist()
    np_.append(-6741.7); labs.append("Q4/26 KH")
    xx = np.arange(len(np_))
    cols = [ACCENT if v < 0 else (NAVY if l.endswith("/26") else LIGHT) for v, l in zip(np_, labs)]
    bars = ax.bar(xx, np_, color=cols, width=0.7)
    bars[-1].set_hatch("///"); bars[-1].set_facecolor("white"); bars[-1].set_edgecolor(ACCENT)
    for i, v in enumerate(np_):
        if abs(v) > 600 or i >= len(np_) - 4:
            ax.text(i, v + (60 if v >= 0 else -380), vn(v), ha="center", fontsize=6.8, color="#333")
    iq2 = labs.index("Q2/26")
    ax.plot(iq2, -738.9, "_", color="black", ms=16, mew=2)
    ax.annotate("Q2 ngầm định\nsau soát xét H1: −739", (iq2, -738.9), xytext=(-70, -40), textcoords="offset points", fontsize=7, arrowprops=dict(arrowstyle="-", color="#555"))
    ax.set_xticks(xx, labs, fontsize=7); ax.set_ylabel("LNST cổ đông mẹ, tỷ đồng"); ax.set_ylim(-7600, 2000)
    ax.set_title("Lỗ từ Q2/26; kế hoạch điều chỉnh của DN ngầm định Q4/26 lỗ khoảng 6.742 tỷ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_npat_quarterly",
         "Nguồn: LNST quý theo cơ sở dữ liệu tài chính (Q3/26 −256,9 khớp BCTC). Q2/26 sau soát xét = LNST H1 soát xét 728,5 − Q1 1.467,4. Q4/26 = LNST 2026 kế hoạch điều chỉnh do DN công bố (−6.270) − 9T (+471,7): con số ngầm định, không phải ước tính của nhóm.",
         pd.DataFrame({"quy": labs, "lnst": np_}))
    plt.close(fig)

    # 3. Kế hoạch 2024–2029
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    xi = np.arange(6)
    ax.bar(xi, PLAN["dt"], color=[LIGHT, LIGHT, "#b9c3cf", NAVY, NAVY, NAVY], width=0.6)
    for i, v in enumerate(PLAN["dt"]):
        ax.text(i, v + 0.8, vn(v, 1), ha="center", fontsize=7.5)
    ax.set_xticks(xi, PLAN["nam"]); ax.set_ylabel("Doanh thu thuần, nghìn tỷ"); ax.set_ylim(0, 68)
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    gm = [g / d * 100 for g, d in zip(PLAN["lng"], PLAN["dt"])]
    ax2.plot(xi, gm, "o-", color=ACCENT, lw=1.6)
    for i, v in enumerate(gm):
        ax2.annotate(vn(v, 1) + "%", (i, v), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=7.5, color=ACCENT)
    ax2.set_ylim(-10, 30); ax2.set_ylabel("Biên gộp, %")
    ax.set_title("Kế hoạch DN: doanh thu vượt 2025 từ 2027, biên gộp 8,8–10,9% (2024–25: 17,5–21,8%)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_03_plan", "Nguồn: \"Tình hình hoạt động & tài chính Q3.2026\" trình ĐHĐCĐ bất thường 21/10/2026, tr.9 — kế hoạch nếu huy động vốn thành công. 2026: kế hoạch điều chỉnh.",
         pd.DataFrame({"nam": PLAN["nam"], "dt": PLAN["dt"], "lai_gop": PLAN["lng"], "lnst": PLAN["lnst"], "bien_gop_pct": [round(g, 1) for g in gm]}))
    plt.close(fig)

    # 4. Nghĩa vụ thu đổi
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    lab = ["Giá trị thu đổi\ncòn lại (30/9)", "Giả định 80%\nkhách thu đổi", "Dự phòng tổn thất\n(kế hoạch)", "Vốn chủ sở hữu\n30/9/2026", "Vốn chủ sau Q4\n(ước lượng)"]
    val = [21057.9, 16500, 7071, 13198.7, 6440]
    ax.bar(range(5), val, color=[ACCENT, "#e3a493", GOLD, NAVY, "#7f93ab"], width=0.6)
    ax.bar(0, 10137.2, color="#a8402c", width=0.6)
    ax.text(0, 5000, "trước 2020\n10.137", ha="center", color="white", fontsize=7)
    ax.text(0, 15500, "2020–26\n10.921", ha="center", color="white", fontsize=7)
    for i, v in enumerate(val):
        ax.text(i, v + 300, vn(v), ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks(range(5), lab, fontsize=7.5); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 24000)
    ax.set_title("Nghĩa vụ thu đổi 21.058 tỷ = 1,6× vốn chủ; dự phòng 7.071 tỷ giả định 80% khách thực hiện")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_tradein", "Nguồn: BCTC hợp nhất Q3/2026 TM17 (giá trị thu đổi còn lại), TM27; tài liệu trình ĐHĐCĐ 21/10/2026 tr.7 (80%, 16.500, 7.100). Vốn chủ sau Q4 = vốn chủ mẹ 30/9 − lỗ Q4 ngầm định trong kế hoạch DN (ước lượng).",
         pd.DataFrame({"muc": [l.replace("\n", " ") for l in lab], "ty_dong": val}))
    plt.close(fig)

    # 5. CFO vs LNST + nợ ròng
    fin["net_debt"] = fin["StDebt_P0"] + fin["LtDebt_P0"] - fin["Cash_P0"]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    w = 0.38
    ax.bar(x - w / 2, fin["NP_P0"], width=w, color=GREY, label="LNST")
    ax.bar(x + w / 2, fin["CF_OA_P0"], width=w, color=np.where(fin["CF_OA_P0"] < 0, ACCENT, NAVY), label="Dòng tiền kinh doanh (CFO)")
    ax.plot(x, fin["net_debt"], "o-", color=GOLD, lw=1.4, ms=3.5, label="Nợ vay − tiền (cuối quý)")
    ax.annotate(vn(fin["net_debt"].iloc[-1]), (x[-1], fin["net_debt"].iloc[-1]), xytext=(-4, 6), textcoords="offset points", ha="right", fontsize=7.5, color=GOLD, fontweight="bold")
    ax.annotate(vn(fin["CF_OA_P0"].iloc[-1]), (x[-1] + w / 2, fin["CF_OA_P0"].iloc[-1]), xytext=(0, -11), textcoords="offset points", ha="center", fontsize=7.5, color=ACCENT, fontweight="bold")
    ax.axhline(0, color="#555", lw=0.6)
    ax.set_xticks(x, fin["lab"], fontsize=7.2); ax.set_ylabel("tỷ đồng"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("CFO Q2–Q3/26 âm 4,4 nghìn tỷ: tiền đi vào hàng thu đổi; nợ ròng tăng lên khoảng 3,1 nghìn tỷ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_05_cfo_netdebt", "Nguồn: cơ sở dữ liệu tài chính quý (CF_OA = CFO quý; nợ vay ngắn + dài hạn − tiền & tương đương; chưa trừ đầu tư nắm giữ đến đáo hạn 82,6 tỷ : BCTC: nợ ròng khoảng 2.996 tỷ 30/9). CFO mùa vụ: Q4 thường âm (Q4/24 −1.573, Q4/25 −1.695).",
         fin[["quarter", "NP_P0", "CF_OA_P0", "net_debt"]])
    plt.close(fig)

    # 6. Vay ngân hàng theo bên cho vay
    bk = pd.DataFrame([("VCB", 1799.2, 997.7), ("BIDV", 1000.0, 1000.0), ("VietinBank", 571.3, 1278.2), ("ACB", 499.9, 0.0),
                       ("KEB Hana", 180.0, 180.0), ("Woori", 161.0, 161.0), ("HSBC", 12.1, 0.0)], columns=["ngan_hang", "dau_nam", "cuoi_q3"])
    bk["delta"] = bk["cuoi_q3"] - bk["dau_nam"]
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    yy = np.arange(len(bk))[::-1]
    ax.barh(yy + 0.18, bk["dau_nam"], height=0.36, color=LIGHT, label="01/01/2026")
    ax.barh(yy - 0.18, bk["cuoi_q3"], height=0.36, color=NAVY, label="30/09/2026")
    for y, d, e in zip(yy, bk["delta"], bk["cuoi_q3"]):
        if d:
            ax.text(max(e, 0) + 30, y - 0.18, ("+" if d > 0 else "−") + vn(abs(d), 1), va="center", fontsize=7.5, color=GREEN if d > 0 else ACCENT, fontweight="bold")
    ax.set_yticks(yy, bk["ngan_hang"]); ax.set_xlabel("dư nợ vay, tỷ đồng"); ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_title("Vay ngân hàng −606 tỷ (−14%): ACB, HSBC rút hẳn, VCB giảm; VietinBank tăng +707")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_banks", "Nguồn: BCTC hợp nhất Q3/2026 TM16. Không gồm khoản vay cá nhân Chủ tịch HĐQT 700 tỷ (lãi 10%/năm, tín chấp, đáo hạn 25/09/2027). Tài sản bảo đảm: hàng tồn kho.", bk)
    plt.close(fig)

    # 7. Số cổ phiếu
    sh = pd.DataFrame({"moc": ["Q3/2025", "Q1/2026", "30/9/2026", "Sau phát hành\n(tối đa)"], "trieu_cp": [341.15, 511.72, 511.72, SH_NOW + SH_NEW_MAX]})
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.bar(range(4), sh["trieu_cp"], color=[LIGHT, NAVY, NAVY, ACCENT], width=0.55)
    for i, v in enumerate(sh["trieu_cp"]):
        ax.text(i, v + 15, vn(v, 1), ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks(range(4), sh["moc"], fontsize=7.8); ax.set_ylabel("triệu cổ phiếu"); ax.set_ylim(0, 1200)
    ax.set_title("Phát hành riêng lẻ tối đa 550 triệu cp: số cổ phiếu có thể tăng khoảng 107%")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_07_shares", "Nguồn: cơ sở dữ liệu tài chính (cp lưu hành; Q1/2026 tăng do phát hành cổ phiếu thưởng/cổ tức); tờ trình 622/2026/TTr-HĐQT, nghị quyết ĐHĐCĐ 21/10/2026 (tối đa 550.000.000 cp, giá ≥ max(TB 30 phiên, BVPS kiểm toán/soát xét gần nhất)).",
         sh.assign(moc=sh["moc"].str.replace("\n", " ")))
    plt.close(fig)

    # 8. Giá 12 tháng + sự kiện
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    ev = [("2026-07-09", "Khởi tố cựu GĐ\ncông ty con P-Lab"), ("2026-07-22", "Chậm thanh toán\nthu đổi"), ("2026-08-25", "CA xác nhận\nhồ sơ nhập khẩu"),
          ("2026-09-28", "Công bố dự phòng\n7.071 tỷ"), ("2026-10-30", "BCTC Q3")]
    offs = [(-62, -6), (-14, -44), (0, 34), (34, 30), (26, 26)]
    for k, (d, t) in enumerate(ev):
        r = px[px["time"] == d]
        if len(r):
            v = float(r["Close"].iloc[0])
            ax.plot(r["time"], v, "o", color=ACCENT, ms=4)
            ax.annotate(t, (r["time"].iloc[0], v), xytext=offs[k], textcoords="offset points", ha="center", va="center", fontsize=6.4,
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ccc", lw=0.5), arrowprops=dict(arrowstyle="-", color="#999", lw=0.6))
    ax.set_ylabel("đ/cp (giá điều chỉnh)"); ax.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Giá giảm khoảng 77% từ cuối T6/2026 qua chuỗi sự kiện; đóng cửa 13/11: 14.950 đ")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_price", "Nguồn: giá đóng cửa điều chỉnh theo cơ sở dữ liệu thị trường (03/11/2025–13/11/2026); giá 13/11 xác nhận qua DNSE (khớp 14:45:04). Chỉ là quan sát trình tự thời gian — không khẳng định quan hệ nhân quả.",
         px)
    plt.close(fig)

    # 9. Football field
    lv = {k: GRID[k] for k in GRID}
    rows = [("Kịch bản cơ sở — đúng kế hoạch DN (g 5%–0%)", BASE[0], BASE[1]),
            ("Kịch bản tốt — về kinh tế 2023–25 (g 0%–5%)", BULL[0], BULL[1]),
            ("Kịch bản xấu — kế hoạch trễ 1 năm (g 5%–0%)", BEAR[0], BEAR[1]),
            ("Độ nhạy mức LNST 2029: 1,2–2,8 nghìn tỷ", lv["1200.0"]["g5_n550"], lv["2828.5"]["g5_n550"]),
            ("Cơ sở nếu chỉ phát hành 400 triệu cp", M["base_g5_ps400"], M["base_g0_ps400"]),
            ("Kiểm chéo: sổ sách sau Q4 + 8.000 tỷ", 13600, 13600)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao"])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for i, r in ff.iterrows():
        y = len(ff) - 1 - i
        if r["thap"] == r["cao"]:
            ax.plot(r["thap"], y, "D", color=GREY, ms=7)
            ax.text(r["thap"] + 350, y, "khoảng 13,6k: trần, vì ROE < chi phí vốn", va="center", fontsize=7)
            continue
        ax.barh(y, r["cao"] - r["thap"], left=r["thap"], color=ACCENT if i == 0 else NAVY, height=0.5, alpha=0.88)
        ax.text(r["thap"] - 300, y, f"{r['thap']/1e3:.1f}".replace(".", ","), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 300, y, f"{r['cao']/1e3:.1f}".replace(".", ","), ha="left", va="center", fontsize=7.5)
    ax.axvline(PX, color="#333", ls="--", lw=1.2, label=f"Giá đóng cửa 13/11: {vn(PX)}")
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.4)
    ax.set_xlim(0, 20000); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_xlabel("đồng/cổ phiếu (511,7 + 550 triệu cp, trừ khi ghi khác)"); ax.legend(fontsize=7, loc="upper right")
    ax.set_title("Giá 14.950 TRÊN vùng cơ sở 6,4–7,6k; ngang kịch bản tốt")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_09_football_field", "Nguồn: mô hình của nhóm nghiên cứu: LNST 2029 × (1+g)(1−g/ROE)/(r−g), chiết khấu 3 năm về cuối 2026, r = 13,5%. Đây là khoảng rộng, không phải điểm vào.", ff)
    plt.close(fig)

    # 10. Ma trận rủi ro
    rk = pd.DataFrame([
        ("R1", "Thu đổi > 80% / dự phòng thêm", 3, 5), ("R2", "Phát hành chậm / thiếu vốn", 4, 5),
        ("R3", "Biên gộp ở mức kế hoạch khoảng 9–11%", 4, 4), ("R4", "Giá trị kim cương tồn kho (LGD)", 3, 3),
        ("R5", "Ngân hàng thu hẹp hạn mức", 3, 4), ("R6", "Pháp lý lan tới pháp nhân", 1, 5),
        ("R7", "Kiểm toán 2026: TM17 / hoạt động liên tục", 2, 5)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R1": (0, 0.2), "R2": (-0.2, 0.2), "R3": (0, 0), "R5": (0, -0.22), "R4": (0, 0), "R7": (0, 0), "R6": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.13, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    fig.text(0.60, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.4, va="top", ha="left", linespacing=1.7)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["1", "2", "3", "4", "5"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["1", "2", "3", "4", "5"], fontsize=7.5)
    ax.set_xlabel("Xác suất 12–18 tháng (1 rất thấp – 5 rất cao)", fontsize=7.5); ax.set_ylabel("Tác động (1 rất nhỏ – 5 rất lớn)", fontsize=7.5)
    ax.set_title("Vốn và biên gộp: hai rủi ro vừa dễ xảy ra vừa tác động lớn")
    fig.subplots_adjust(left=0.09, right=0.56, bottom=0.2, top=0.9)
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu BCTC Q3/2026 và đọc ngành độc lập 14/11/2026.", rk)
    plt.close(fig)

    # 12. Khung ảnh sản phẩm
    from PIL import Image, ImageDraw, ImageFont
    items = [("trang_suc_vang.jpg", "Trang sức vàng", "Dòng chủ lực bán lẻ"),
             ("nhan_cuoi.png", "Nhẫn cưới", "Mùa cưới Q4–Q1"),
             ("ts-kim-cuong-t4-26-1200x1200.jpg", "Trang sức kim cương", "Nhóm chịu thu đổi"),
             ("trang_suc_bac.jpg", "Trang sức bạc (STYLE)", "Phân khúc giá thấp")]
    S, PAD, CAP = 340, 14, 64
    W = 4 * S + 5 * PAD
    sheet = Image.new("RGB", (W, S + CAP + 2 * PAD), "white")
    fb = ImageFont.truetype(FONT_B, 21); fr = ImageFont.truetype(FONT, 17)
    d = ImageDraw.Draw(sheet)
    for k, (f, t, s) in enumerate(items):
        im = Image.open(os.path.join(WEB, f)).convert("RGBA")
        bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im); im = bg.convert("RGB")
        m = min(im.size); im = im.crop(((im.width - m) // 2, (im.height - m) // 2, (im.width + m) // 2, (im.height + m) // 2)).resize((S, S))
        x0 = PAD + k * (S + PAD)
        sheet.paste(im, (x0, PAD)); d.rectangle([x0, PAD, x0 + S - 1, PAD + S - 1], outline="#D9DEE4", width=2)
        d.text((x0 + 4, PAD + S + 8), t, font=fb, fill=NAVY); d.text((x0 + 4, PAD + S + 36), s, font=fr, fill="#555")
    sheet.save(os.path.join(FIGS, "fig_12_products.png"))
    pd.DataFrame(items, columns=["file", "san_pham", "ghi_chu"]).assign(nguon="pnj.com.vn (trang chủ, tải 14/11/2026)").to_csv(os.path.join(FIGS, "fig_12_products.csv"), index=False)

    print("implied N2029 at price (g5,n550) =", round(imp, 0) if imp else None)
    print(ff.to_string())


# ------------------------------------------------------------------ PDF (khuôn SCL)
CSS = """
@font-face {font-family: dv; src: url(BeVietnamPro-Regular.ttf);}
@font-face {font-family: dv; src: url(BeVietnamPro-Bold.ttf); font-weight: bold;}
* {font-family: dv;}
body {margin: 0; padding: 0; font-size: 8.6pt; line-height: 1.38; color: #1d2731;}
h1 {font-size: 14pt; color: #1F3A5F; margin: 0 0 4pt 0;}
h2 {font-size: 11.5pt; color: #1F3A5F; margin: 10pt 0 4pt 0;}
h3 {font-size: 9.6pt; color: #1F3A5F; margin: 7pt 0 3pt 0;}
p {margin: 3pt 0;}
table {border-collapse: collapse; width: 100%; margin: 4pt 0 6pt 0;}
th {background-color: #1F3A5F; color: #ffffff; font-size: 7.5pt; padding: 2pt 3pt; text-align: left;}
td {font-size: 7.5pt; padding: 2pt 3pt; border-bottom: 1px solid #D9DEE4;}
li {margin: 1pt 0;}
img {width: 100%;}
"""
IMG_W = 470
BREAK_BEFORE = ("3.", "5.", "7.", "Phụ lục A")


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
    # banner đặt riêng ở đầu trang 1 (full width) — bỏ dòng h1 trùng trong PDF
    md = re.sub(r"^# .*\n", "", md, count=1)
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

    banner = os.path.join(FIGS, "title_banner.png")
    if os.path.exists(banner):
        from PIL import Image
        with Image.open(banner) as im:
            bh = int(IMG_W * im.height / im.width)
        place_html(f'<p><img src="figs/title_banner.png" width="{IMG_W}" height="{bh}"/></p>')

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
        page.insert_text((42, 34), "PNJ — CTCP Vàng bạc Đá quý Phú Nhuận · Báo cáo Due Diligence · 14/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "PNJ_DD_investor_report_20261114.md"), os.path.join(HERE, "PNJ_DD_investor_report_20261114.pdf"))
