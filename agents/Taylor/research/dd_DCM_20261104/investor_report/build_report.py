"""Dựng biểu đồ + PDF báo cáo DD nhà đầu tư DCM (as-of 05/11/2026).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Số liệu hard-code lấy từ ../calc/quarterly_out.txt, ../calc/model_r5_out.txt, ../calc/compare_px_r5_out.txt (mỗi hình kèm CSV)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 33000
EV = 24326
Q = ["Q1/25", "Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]
DTT = [3407, 6037, 2988, 4528, 5286, 6712, 5742]
GP = [885, 1241, 657, 1252, 1346, 2001, 1099]
GPM = [26.0, 20.6, 22.0, 27.6, 25.5, 29.8, 19.1]
LNST = [412, 788, 328, 389, 789, 1067, 432]
UREGP = [876, 881, 537, 1155, 1212, 1792, 908]
UREM = [35.9, 36.3, 39.0, 48.1, 41.5, 46.0, 35.3]


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
        "figure.facecolor": "white", "savefig.facecolor": "white", "axes.grid": True,
        "grid.color": "#ECEFF2", "grid.linewidth": 0.8, "axes.axisbelow": True})
    return plt


def save(fig, name, source, df=None):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.6, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def vn(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def figs():
    import numpy as np
    import pandas as pd
    from matplotlib.patches import FancyBboxPatch
    plt = setup_mpl()
    x = np.arange(7)
    SRC = "Nguồn: BCTC hợp nhất DCM các quý 2025–Q3/2026 (Q3/26 công bố 29/10/2026); Q2/25 theo số trình bày lại."

    # 0 HERO
    fig, ax = plt.subplots(figsize=(7.2, 1.9)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(6, 36)
    steps = [("Khí tự nhiên\ngắn giá dầu", "PM3–CAA, Nam Du"), ("Nhà máy đạm\nCà Mau", "urê · NPK"), ("Phân phối\nnội địa", "ĐBSCL, ĐNB"), ("Nông dân &\nxuất khẩu", "XK 5.289 tỷ 9T/26")]
    for i, (a, b) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((1 + i * 15.5, 18), 13.5, 14, boxstyle="round,pad=0.3", fc=NAVY if i != 1 else ACCENT, ec="none"))
        ax.text(7.75 + i * 15.5, 27, a, ha="center", va="center", color="white", fontsize=6.6, fontweight="bold")
        ax.text(7.75 + i * 15.5, 20.4, b, ha="center", va="center", color="#DDE6F0", fontsize=5.2)
        if i < 3:
            ax.annotate("", (16.3 + i * 15.5, 25), (14.7 + i * 15.5, 25), arrowprops=dict(arrowstyle="->", color=GREY))
    ax.text(1, 13, "Biên urê–khí (USD/t) quyết định lợi nhuận", fontsize=8, fontweight="bold", color=NAVY)
    ax.text(1, 9, "Lợi nhuận 9T/26 +49,6% so cùng kỳ; Q3/26 giảm 59,5% so Q2/26 khi biên urê về 35,3%.", fontsize=6.8, color="#333")
    # value bar at right
    x0, x1 = 68, 97
    sc = lambda v: x0 + (v - 19000) / (35000 - 19000) * (x1 - x0)
    ax.add_patch(plt.Rectangle((sc(20522), 20), sc(27708) - sc(20522), 6, fc=LIGHT, ec="none"))
    ax.add_patch(plt.Rectangle((sc(21643), 20), sc(26243) - sc(21643), 6, fc=GREY, ec="none"))
    ax.plot([sc(EV)] * 2, [19, 27], color=NAVY, lw=2); ax.plot([sc(PX)] * 2, [19, 27], color=ACCENT, lw=2)
    ax.text(sc(EV) - 1.5, 28.2, "Giá trị kỳ vọng\n24.326", ha="center", fontsize=6.3, color=NAVY, fontweight="bold")
    ax.text(sc(PX) + 1, 28.2, "Đóng cửa 04/11\n33.000", ha="center", fontsize=6.3, color=ACCENT, fontweight="bold")
    ax.text(x0, 15.5, "Xám đậm: P25–P75; xám nhạt: P10–P90 (đ/cp)", fontsize=5.6, color="#555")
    ax.set_title("Chuỗi khí – đạm và vị trí của giá so với vùng giá trị", x=0.0, fontsize=9)
    save(fig, "fig_00_hero", "Minh họa dựng từ số của báo cáo (không phải ảnh công ty). Giá trị: mô hình DCF 05/11/2026, lưới đối xứng 270 ô.", pd.DataFrame({"chi_tieu": ["P10", "P25", "EV", "P75", "P90", "gia"], "dong_cp": [20522, 21643, EV, 26243, 27708, PX]}))
    plt.close(fig)

    # 1 football
    rows = [("Lưới đối xứng 270 ô (P10–P90)", 20522, 27708, 24095),
            ("Lưới đối xứng 450 ô, biên 98–260 (P10–P90)", 18062, 29991, 24095),
            ("Theo biên dài hạn 98–260 USD/t (tâm)", 18356, 30272, 24314),
            ("Hai cách đọc cơ cấu khí (A–B)", 24192, 24459, 24326),
            ("Độ nhạy khí: sau 2035 giá phẳng … Nam Du 30% + PM3 rẻ", 16719, 28288, None),
            ("Giá 250 phiên (thấp–cao)", 28900, 50200, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "giua"])
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    for i, r in ff.iterrows():
        y = len(ff) - 1 - i
        ax.barh(y, r.cao - r.thap, left=r.thap, color=GREY if i >= 4 else NAVY, height=0.5, alpha=0.9)
        ax.text(r.thap - 300, y, vn(r.thap / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(r.cao + 300, y, vn(r.cao / 1e3, 1), ha="left", va="center", fontsize=7.3)
        if r.giua == r.giua and r.giua is not None:
            ax.plot(r.giua, y, "|", color="white", ms=14, mew=2)
    ax.set_yticks(range(len(ff)), ff.phuong_phap[::-1], fontsize=7.0)
    ax.axvline(EV, color=NAVY, ls="--", lw=1.1, label="Giá trị kỳ vọng 24.326")
    ax.axvline(PX, color=ACCENT, ls="-", lw=1.4, label="Đóng cửa 04/11/2026: 33.000")
    ax.set_xlim(12000, 54000); ax.legend(fontsize=7, frameon=False, loc="upper right")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_xlabel("đồng/cổ phiếu")
    ax.set_title("Giá 33.000 nằm trên các vùng giá trị; chỉ chạm khi biên ≈ 297 USD/t", loc="right", fontsize=8.8)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_football", "Nguồn: mô hình DCF của nhóm nghiên cứu (05/11/2026), giá DNSE 04/11/2026; giá 250 phiên: BigQuery. Vạch trắng = giữa (P50 hoặc kỳ vọng). Hai dòng xám: độ nhạy, không vào giá trị kỳ vọng.", ff)
    plt.close(fig)

    # 2 DT & biên
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(x, DTT, color=[LIGHT] * 4 + [NAVY] * 3, width=0.7)
    ax.set_xticks(x, Q); ax.set_ylabel("DT thuần, tỷ đồng")
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(x, GPM, color=ACCENT, marker="o", lw=1.6)
    for i, v in enumerate(GPM):
        ax2.annotate(vn(v, 1) + "%", (i, v), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=7.5, color=ACCENT, fontweight="bold")
    ax2.set_ylim(10, 36); ax2.set_ylabel("Biên gộp, %")
    ax.set_title("Biên gộp lên 29,8% ở Q2/26 rồi về 19,1% ở Q3/26")
    fig.tight_layout(rect=(0, 0.07, 1, 1)); save(fig, "fig_02_revenue_margin", SRC, pd.DataFrame({"quy": Q, "dt_thuan": DTT, "bien_gop_pct": GPM})); plt.close(fig)

    # 3 LNST + LN gộp urê
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); w = 0.38
    ax.bar(x - w / 2, LNST, w, color=NAVY, label="LNST")
    ax.bar(x + w / 2, UREGP, w, color=ACCENT, label="LN gộp urê")
    for i in range(7):
        ax.text(i - w / 2, LNST[i] + 25, vn(LNST[i]), ha="center", fontsize=6.8); ax.text(i + w / 2, UREGP[i] + 25, vn(UREGP[i]), ha="center", fontsize=6.8)
    ax.set_xticks(x, Q); ax.set_ylabel("tỷ đồng"); ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_title("LNST Q3/26 432 tỷ: LN gộp urê giảm 884 tỷ so với Q2/26")
    fig.tight_layout(rect=(0, 0.07, 1, 1)); save(fig, "fig_03_npat_ure", SRC + " LN gộp urê theo thuyết minh doanh thu/giá vốn theo sản phẩm.", pd.DataFrame({"quy": Q, "lnst": LNST, "ln_gop_ure": UREGP, "bien_ure_pct": UREM})); plt.close(fig)

    # 4 waterfall
    steps = [("LNTT\nQ3/25", 378.6, "t"), ("LN gộp\nthuần", 442.0, "d"), ("CP bán\nhàng", -87.3, "d"), ("QLDN", -46.7, "d"), ("DT tài\nchính", -72.5, "d"), ("CP tài\nchính", -116.3, "d"), ("LN\nkhác", 3.7, "d"), ("LNTT\nQ3/26", 501.4, "t")]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); cum = 0
    for i, (l, v, k) in enumerate(steps):
        if k == "t":
            ax.bar(i, v, color=NAVY); cum = v; ax.text(i, v + 10, vn(v, 1), ha="center", fontsize=7.5, fontweight="bold")
        else:
            b = cum if v >= 0 else cum + v
            ax.bar(i, abs(v), bottom=b, color=GREEN if v >= 0 else ACCENT); cum += v
            ax.text(i, max(cum, cum - v) + 10, ("+" if v > 0 else "−") + vn(abs(v), 1), ha="center", fontsize=7.5)
    ax.set_xticks(range(8), [s[0] for s in steps], fontsize=7.4); ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 950)
    ax.set_title("LN gộp tăng 442 tỷ nhưng chi phí và tài chính ăn 319 tỷ: LNTT chỉ +123 tỷ")
    fig.tight_layout(rect=(0, 0.07, 1, 1)); save(fig, "fig_04_bridge", "Nguồn: BCTC hợp nhất Q3/2026 và Q3/2025 (cột quý). Tài chính ròng −189 tỷ gồm chi phí tài chính khác 71,2 tỷ chưa có thuyết minh.", pd.DataFrame(steps, columns=["buoc", "tyd", "loai"])); plt.close(fig)

    # 5 cash
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1, 1]})
    a.bar(["31/12/2025", "30/9/2026"], [5409, 7539], color=[LIGHT, NAVY], width=0.55)
    for i, v in enumerate([5409, 7539]): a.text(i, v + 120, vn(v), ha="center", fontsize=8, fontweight="bold")
    a.set_title("Net cash gộp, tỷ đồng"); a.set_ylim(0, 9000)
    b.bar(["CFO 9T/25", "CFO 9T/26", "Capex 9T/26"], [-2017, 2331, -546], color=[GREY, NAVY, ACCENT], width=0.55)
    for i, v in enumerate([-2017, 2331, -546]): b.text(i, v + (120 if v > 0 else -300), vn(v), ha="center", fontsize=8, fontweight="bold")
    b.axhline(0, color="#555", lw=0.8); b.set_title("Dòng tiền 9 tháng, tỷ đồng"); b.set_ylim(-2600, 2900)
    fig.tight_layout(rect=(0, 0.1, 1, 1)); save(fig, "fig_05_cash", "Nguồn: BCTC hợp nhất Q3/2026. Net cash = tiền + đầu tư nắm giữ đến hạn + tiền gửi phong tỏa − vay (chưa trừ quỹ khen thưởng phúc lợi 265 tỷ). CFO 9T/25 âm do tích tồn kho 1.609 tỷ.", pd.DataFrame({"chi_tieu": ["net_cash_1/1/26", "net_cash_30/9/26", "CFO_9T25", "CFO_9T26", "capex_9T26"], "ty_dong": [5409, 7539, -2017, 2331, -546]})); plt.close(fig)

    # 6 sensitivity to margin
    mg = [98, 138, 179, 220, 260]; val = [18356, 21298, 24314, 27330, 30272]
    lo = [18222, 21164, 24180, 27196, 30138]; hi = [18490, 21432, 24448, 27463, 30405]
    slope = (val[-1] - val[-2]) / 40; ext = [260, 300]; extv = [val[-1], val[-1] + slope * 40]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(mg, val, color=NAVY, marker="o", lw=1.8, label="Giá trị kỳ vọng (tâm)")
    ax.plot(ext, extv, color=NAVY, lw=1.4, ls="--")
    ax.fill_between(mg, lo, hi, color=NAVY, alpha=0.18, label="Dải hai cách đọc khí A–B")
    for m, v in zip(mg, val): ax.annotate(vn(v), (m, v), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=7.5)
    ax.axhline(PX, color=ACCENT, lw=1.4); ax.text(100, PX + 350, "Đóng cửa 04/11: 33.000", color=ACCENT, fontsize=8, fontweight="bold")
    ax.axvspan(180, 260, color=LIGHT, alpha=0.5); ax.text(220, 15600, "dải bền 180–260 (người đọc ngành độc lập)", ha="center", fontsize=7, color="#444")
    ax.plot([297], [PX], "o", color=ACCENT, ms=6); ax.annotate("giá = giá trị ở biên ≈ 297", (297, PX), xytext=(0, -34), textcoords="offset points", ha="center", fontsize=7.3, color=ACCENT)
    for m, s_, ha in ((152, "trung vị 10 năm 152", "right"), (179, "TB 10 năm 179", "left"), (257, "2025: 257", "left")):
        ax.axvline(m, color=GREY, ls=":", lw=0.9); ax.text(m + (-1 if ha == "right" else 1), 34600, s_, ha=ha, fontsize=6.8, color="#444")
    ax.set_xlim(90, 305); ax.set_ylim(15000, 35600); ax.set_xlabel("Biên urê–khí dài hạn, USD/t"); ax.set_ylabel("giá trị kỳ vọng, đ/cp")
    ax.legend(frameon=False, fontsize=7.2, loc="upper left", bbox_to_anchor=(0.0, 0.88))
    ax.set_title("Giá trị phụ thuộc biên dài hạn: 33.000 ứng với biên ≈ 297 USD/t, trên dải bền")
    fig.tight_layout(rect=(0, 0.07, 1, 1)); save(fig, "fig_06_margin_sensitivity", "Nguồn: mô hình DCF của nhóm nghiên cứu (kỳ vọng = 0,8 × biên + 0,2 × kịch bản cấu trúc 125; Brent 67,8). Đoạn nét đứt = kéo dài tuyến tính của mô hình ngoài biên 260. Biên = giá urê − 25 × (2,5 + 0,06 × Brent), thước đo hướng.", pd.DataFrame({"bien": mg, "gia_tri": val, "A": lo, "B": hi})); plt.close(fig)

    # 9 gas path
    g = pd.read_csv(os.path.join(FIGS, "fig_09_gas_path.csv"))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, bt, tt in ((axs[0], 67.8, "Brent 67,8 (TB 2016–25)"), (axs[1], 103, "Brent 103 (hiện tại)")):
        d = g[g.brent == bt]
        ax.plot(d.nam, d.cach_doc_A, color=NAVY, lw=1.8, label="Cơ cấu khí A")
        ax.plot(d.nam, d.cach_doc_B, color=GREEN, lw=1.8, label="Cơ cấu khí B")
        n2 = d.dropna(subset=["gia_nam_du_gom_cuoc"])
        ax.plot(n2.nam, n2.gia_nam_du_gom_cuoc, color=ACCENT, lw=1.4, ls="--", label="Giá Nam Du–U Minh (gồm cước)")
        d3 = d[d.nam >= 2034]
        ax.plot(d3.nam, d3.do_nhay_2035_phang, color=GREY, lw=1.6, ls=":", label="Độ nhạy: sau 2035 giá phẳng 10,39")
        ax.axvspan(2028.75, 2032.3, color=LIGHT, alpha=0.5)
        ax.set_title(tt, fontsize=8.5); ax.set_xticks([2026, 2028, 2030, 2032, 2034, 2036])
    axs[0].set_ylabel("USD/MMBtu, trước VAT"); axs[0].text(2029.0, 14.5, "bao tiêu 90% đến 24/4/2032", fontsize=6.3, color="#444")
    h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, frameon=False, fontsize=6.8, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.075))
    axs[0].set_ylim(6.5, 15.5)
    fig.suptitle("Giá khí bình quân của DCM: Nam Du cố định từ cuối 2028 làm giá khí cao hơn khi Brent thấp", x=0.01, ha="left", fontsize=9.3, fontweight="bold")
    fig.tight_layout(rect=(0, 0.16, 1, 0.94)); save(fig, "fig_09_gas_path", "Nguồn: mô hình DCF của nhóm nghiên cứu; Nam Du: dự thảo Sửa đổi bổ sung số 12, Điều 9.1 (10,39 USD/MMBtu tại mỏ, +2,25%/năm, chưa VAT); cước 1,14 USD/MMBtu và công thức PM3 theo ước tính của CTCK. Giá PM3 sau 2027: kịch bản, không phải văn bản hợp đồng.", None); plt.close(fig)

    # 7 mix (minh họa)
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    mix = [("Urê", 2573, NAVY), ("NPK", 1624, GREEN), ("Phân bón\nthương mại", 1536, ACCENT), ("Khác", 260, GREY)]
    left = 0; tot = sum(m[1] for m in mix)
    for n, v, c in mix:
        ax.barh(0, v, left=left, color=c, height=0.5)
        ax.text(left + v / 2, 0, f"{n}\n{vn(v)} ({vn(v/tot*100)}%)", ha="center", va="center", color="white", fontsize=7.3, fontweight="bold")
        left += v
    ax.set_ylim(-0.6, 0.9); ax.axis("off")
    ax.text(0, 0.62, "Sản phẩm: urê (hạt đục) · NPK · phân bón kinh doanh thương mại · khí công nghiệp và CO₂ (dự án đang xây)", fontsize=7.3, color="#333")
    ax.set_title("Cơ cấu doanh thu gộp Q3/26 (tỷ đồng): urê 43%, NPK 27%, thương mại 26%")
    fig.tight_layout(rect=(0, 0.1, 1, 1)); save(fig, "fig_07_mix", "Sơ đồ minh họa tự vẽ (không dùng ảnh công ty). Nguồn số: BCTC hợp nhất Q3/2026, thuyết minh doanh thu theo sản phẩm, Q3 = 9T − 6T.", pd.DataFrame(mix, columns=["san_pham", "dt_ty", "mau"]).drop(columns="mau")); plt.close(fig)
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
BREAK_BEFORE = ("3.", "5.", "Phụ lục A")


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
            if lv > 1:
                out.append(f"<h{lv}>{inl(m.group(2))}</h{lv}>")
            i += 1; continue
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
    md = "![Banner](figs/title_banner.png)\n\n" + open(md_path, encoding="utf-8").read()
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
        page.insert_text((42, 34), "DCM — CTCP – Tổng Công ty Phân bón Dầu khí Cà Mau · Báo cáo Due Diligence · 05/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "DCM_DD_investor_report_20261105.md"), os.path.join(HERE, "DCM_DD_investor_report_20261105.pdf"))
