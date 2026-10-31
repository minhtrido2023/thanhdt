"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư NNC (31/10/2026; skill dd-investor-report luật 1–14).
Số định giá lấy từ ../calc/valuation_v2.py → ../calc/valuation_v2_out.txt (bản ĐÃ ĐÍNH CHÍNH, REPORT.md §13).
Số BCTC: BCTC riêng Q3/2026 (ký 19/10/2026), BCTC 2025 kiểm toán AASCs, BCTN 2025 — trích kèm trang ở ../REPORT.md.
Khuôn PDF/CSS/md_to_html: ../../dd_DRI_20261027/investor_report_v3/build_report.py.

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/): fin_quarterly_bq.csv (tav2_bq.ticker_financial NNC 2020Q4–2026Q3, kéo 31/10/2026);
                 price_raw.csv (tav2_bq.ticker NNC Close/Price/Volume 02/01/2024–30/10/2026 = ../calc/nnc_px.csv).
Mỗi hình ghi kèm CSV dữ liệu vẽ (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#3C7A5A"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"  # luật 13
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung (nguồn: ../calc/valuation_v2_out.txt trừ khi ghi khác) ----
SH = 21_920_000                 # VĐL 219,2 tỷ / 10.000 [BCTC Q3 V22]
PX = 47_100                     # đóng cửa 30/10/2026 [tav2_bq.ticker]; thứ Bảy 31/10 thị trường đóng cửa
FV_LO, FV_HI, FV_MID = 59_307, 79_498, 69_402      # kỳ vọng r13%: giá danh nghĩa phẳng … giữ giá trị thực (MVC −15%)
GRID = dict(mn=50_685, p10=57_617, med=70_318, p90=84_812, mx=94_442)   # lưới 72 tổ hợp
SC3 = {"Tích cực": (0.25, 99_099, 131_053), "Cơ sở": (0.50, 56_657, 77_418), "Tiêu cực": (0.25, 24_815, 32_102)}  # (p, phẳng, thực)
PATHS = {"phẳng danh nghĩa": 59_980, "+3%/năm từ 2031": 69_106, "+3%/năm từ 2028": 76_633, "giữ giá trị thực": 80_171}  # MVC 0%
FPTS_TP = 51_400
NP_ANN = {"2021": 38.4, "2022": 39.3, "2023": 36.6, "2024": 62.6, "2025": 147.8, "TTM": 214.0}   # tỷ, BQ NP_P0 cộng 4 quý; 2024/25 khớp BCTC
EPS_TTM = 9_761
PEERS = {"VLB*": 3.65, "NNC": 4.83, "DHA": 5.43, "KSB": 7.13}   # PE TTM, BQ 30/10/2026; *VLB gồm Q2/26 374 tỷ một lần (~6,3x nếu bỏ)


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
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.4, color="#666", ha="left", va="bottom")
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
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    fin = fin[fin["quarter"] >= "2022Q1"].reset_index(drop=True)
    fin["q"] = fin["quarter"].str[4:] + "/" + fin["quarter"].str[2:4]
    fin["rev"] = fin["Revenue_P0"] / 1e9
    fin["np"] = fin["NP_P0"] / 1e9
    fin["gpm_ttm"] = fin["GPM_P0"] * 100

    # 00 HERO ------------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.15))
    band = fig.add_axes([0, 0.86, 1, 0.14]); band.axis("off")
    band.add_patch(mp.Rectangle((0, 0), 1, 1, fc=NAVY, transform=band.transAxes))
    band.text(0.015, 0.5, "NNC · Đá xây dựng cụm Đồng Phú (Đông Nam Bộ)", color="white", fontsize=10.5, fontweight="bold", va="center")
    band.text(0.985, 0.5, "Giá 47,1k: dưới vùng hợp lý", color="white", fontsize=10, fontweight="bold", va="center", ha="right",
              bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT, ec="none"))
    a = fig.add_axes([0.0, 0.15, 0.28, 0.66]); a.axis("off"); a.set_xlim(0, 3); a.set_ylim(0, 3.2)
    a.add_patch(mp.Polygon([[0.2, 0.9], [1.0, 2.4], [1.5, 1.7], [2.1, 2.6], [2.85, 0.9]], fc="#8A98A8", ec=NAVY, lw=0.8))
    a.add_patch(mp.Polygon([[1.0, 2.4], [1.25, 2.05], [0.8, 2.05]], fc="white", ec="none"))
    a.add_patch(mp.Polygon([[2.1, 2.6], [2.35, 2.2], [1.85, 2.2]], fc="white", ec="none"))
    for x, y, s in ((0.5, 0.75, 0.16), (0.85, 0.72, 0.12), (1.1, 0.76, 0.14)):
        a.add_patch(mp.Circle((x, y), s, fc=ACCENT, alpha=0.75, ec="none"))
    a.plot([0.05, 2.95], [0.6, 0.6], color="#B9C3CE", lw=1.2)
    a.text(1.5, 0.4, "Mỏ Mũi Tàu · 1,0 tr m³/năm", ha="center", fontsize=8.6, fontweight="bold", color=NAVY)
    a.text(1.5, 0.2, "nguyên khối, giấy phép tới 2043\n≈1,42 tr m³ đá thành phẩm/năm", ha="center", va="top", fontsize=6.6, color="#333")
    a.text(0.05, 3.1, "1 · NGÀNH NGHỀ", fontsize=7.6, fontweight="bold", color=ACCENT)
    b = fig.add_axes([0.35, 0.2, 0.30, 0.5])
    xs = list(NP_ANN.keys()); ys = list(NP_ANN.values())
    b.bar(xs, ys, color=[NAVY] * 5 + [ACCENT], width=0.62)
    for x, y in zip(xs, ys):
        b.text(x, y + 4, vn(y, 0), ha="center", fontsize=6.4, color="#333")
    b.set_ylim(0, 245); b.tick_params(labelsize=6.4); b.set_ylabel("LNST, tỷ đồng", fontsize=6.6)
    fig.text(0.35, 0.83, "2 · TĂNG TRƯỞNG", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.35, 0.81, "LNST 4 quý gần nhất 214 tỷ, gần 6 lần 2023;\nnhờ giá đá, sản lượng đã chạm trần giấy phép", fontsize=6.3, color="#333", va="top")
    c = fig.add_axes([0.71, 0.13, 0.23, 0.56])
    c.set_xlim(0, 1); c.set_ylim(15_000, 100_000); c.grid(False)
    for sp in ("left", "bottom"):
        c.spines[sp].set_visible(False)
    c.set_xticks([]); c.yaxis.tick_right(); c.tick_params(labelsize=6.4)
    c.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    c.add_patch(mp.Rectangle((0.08, GRID["p10"]), 0.42, GRID["p90"] - GRID["p10"], fc=GREEN, alpha=0.18, ec="none"))
    c.add_patch(mp.Rectangle((0.08, FV_LO), 0.42, FV_HI - FV_LO, fc=GREEN, alpha=0.85, ec="none"))
    c.text(0.29, (FV_LO + FV_HI) / 2, "giá trị\nhợp lý\n59–79k", ha="center", va="center", fontsize=6.3, color="white", fontweight="bold")
    c.add_patch(mp.Rectangle((0.6, SC3["Tiêu cực"][1]), 0.28, SC3["Tiêu cực"][2] - SC3["Tiêu cực"][1], fc="white", ec=GREY, hatch="////", lw=0.8))
    c.text(0.74, SC3["Tiêu cực"][1] - 1500, "tiêu cực\n25–32k", ha="center", va="top", fontsize=5.8, color="#555")
    c.axhline(PX, xmin=0.02, xmax=0.98, color=NAVY, lw=1.6)
    c.text(0.02, PX + 1800, "Giá 47,1k (30/10)", fontsize=6.6, color=NAVY, fontweight="bold")
    fig.text(0.70, 0.83, "3 · ĐỊNH GIÁ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.70, 0.81, "dưới vùng hợp lý; thị trường\nđang định giá 'vách' 2028", fontsize=6.3, color="#333", va="top")
    fig.text(0.01, 0.005, "Nguồn: BCTN 2025 (giấy phép, công suất); tav2_bq NP_P0 cộng 4 quý (2024–25 khớp BCTC kiểm toán); mô hình DCF hữu hạn 2027–2043 của nhóm "
             "(ước lượng; vùng đậm = kỳ vọng từ giá đá danh nghĩa phẳng tới giữ giá trị thực, vùng nhạt = P10–P90 của 72 tổ hợp giả định); giá đóng cửa 30/10/2026.",
             fontsize=5.8, color="#666", va="bottom", wrap=True)
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200); plt.close(fig)
    pd.DataFrame([("cong_suat_nguyen_khoi_tr_m3", 1.0, "BCTN25 tr.3,6"), ("han_gp", 2043, "BCTN25 tr.3"),
                  *[(f"lnst_{x}", y, "BQ NP_P0 / BCTC") for x, y in NP_ANN.items()],
                  ("fv_lo_phang", FV_LO, "valuation_v2"), ("fv_hi_thuc", FV_HI, "valuation_v2"), ("grid_p10", GRID["p10"], "valuation_v2"),
                  ("grid_p90", GRID["p90"], "valuation_v2"), ("tieu_cuc_lo", SC3["Tiêu cực"][1], "valuation_v2"), ("tieu_cuc_hi", SC3["Tiêu cực"][2], "valuation_v2"),
                  ("gia_3010", PX, "tav2_bq.ticker")], columns=["chi_tieu", "gia_tri", "nguon"]).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)

    # 01 KPI -------------------------------------------------------------------
    kpi = [("Doanh thu thuần 9T/26", "402,2 tỷ", "+53,6% YoY", "DT"), ("LNST 9T/26", "160,1 tỷ", "+70,4% YoY; Q3 69,3 tỷ", "LN"),
           ("Biên gộp 9T/26", "54,3%", "2024: 31,6% · 2025: 49,4%", "%"), ("Tiền ròng sau nghĩa vụ", "223,6 tỷ", "≈22% vốn hoá (30/9/26)", "₫"),
           ("P/E TTM · EV/EBITDA", "4,8× · ~2,3×", "trên lợi nhuận đỉnh", "×"), ("Giấy phép Mũi Tàu", "tới 2043", "~17 năm; 1,0 tr m³/năm", "GP")]
    fig = plt.figure(figsize=(7.2, 2.2))
    for i, (t, v, n, ic) in enumerate(kpi):
        ax = fig.add_axes([0.01 + (i % 3) * 0.33, 0.53 - (i // 3) * 0.47, 0.31, 0.42]); ax.axis("off")
        ax.add_patch(mp.FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.02", fc="#F3F5F7", ec=LIGHT, transform=ax.transAxes))
        ax.add_patch(mp.Circle((0.14, 0.5), 0.1, fc=ACCENT if i in (4, 5) else NAVY, transform=ax.transAxes))
        ax.text(0.14, 0.5, ic, ha="center", va="center", color="white", fontsize=7.2, fontweight="bold", transform=ax.transAxes)
        ax.text(0.3, 0.72, t, fontsize=6.9, color="#555", transform=ax.transAxes)
        ax.text(0.3, 0.42, v, fontsize=11, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(0.3, 0.17, n, fontsize=6.3, color="#555", transform=ax.transAxes)
    fig.savefig(os.path.join(FIGS, "fig_01_kpi.png"), dpi=200); plt.close(fig)
    pd.DataFrame(kpi, columns=["chi_tieu", "gia_tri", "ghi_chu", "icon"]).to_csv(os.path.join(FIGS, "fig_01_kpi.csv"), index=False)

    # 02 Doanh thu + biên gộp TTM --------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(fin["q"], fin["rev"], color=NAVY, width=0.65, label="Doanh thu thuần quý (tỷ)")
    ax.set_ylabel("tỷ đồng"); ax.tick_params(axis="x", labelsize=6.6, rotation=45)
    ax2 = ax.twinx(); ax2.plot(fin["q"], fin["gpm_ttm"], color=ACCENT, lw=2, marker="o", ms=3, label="Biên gộp 4 quý gần nhất (%)")
    ax2.set_ylim(0, 70); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax.set_title("Doanh thu quý tăng gấp ~8 lần từ đáy 2022; biên gộp 4 quý từ ~17% lên 53%")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="upper left", frameon=False)
    fig.subplots_adjust(bottom=0.27, top=0.9)
    save(fig, "fig_02_revenue_margin", "Nguồn: tav2_bq.ticker_financial (Revenue_P0 khớp BCTC Q3/26 149,49 tỷ; GPM_P0 là biên gộp 4 quý gần nhất — riêng Q3/26 theo BCTC là 57,9%).",
         fin[["quarter", "rev", "gpm_ttm"]]); plt.close(fig)

    # 03 LNST quý ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    col = [ACCENT if q >= "2026Q1" else NAVY for q in fin["quarter"]]
    ax.bar(fin["q"], fin["np"], color=col, width=0.65)
    for x, y in zip(fin["q"], fin["np"]):
        if y > 30:
            ax.text(x, y + 1.5, vn(y, 1), ha="center", fontsize=6.2)
    ax.set_ylabel("tỷ đồng"); ax.tick_params(axis="x", labelsize=6.6, rotation=45)
    ax.set_title("LNST quý: 9 tháng 2026 = 160,1 tỷ, đã gồm 22 tỷ chi phí truy thu một lần ở Núi Nhỏ")
    fig.subplots_adjust(bottom=0.27, top=0.9)
    save(fig, "fig_03_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (khớp BCTC riêng Q3/2026: 69,29 tỷ; 9T 160,08 tỷ). Màu cam = 2026.",
         fin[["quarter", "np"]]); plt.close(fig)

    # 04 Lịch sử ---------------------------------------------------------------
    ev = [(1975, "Đội khai thác\nđá Châu Thới"), (1997, "Xí nghiệp đá số 3\n(Cty VL&XD Bình Dương)"), (2006, "Cổ phần hoá:\nCTCP Đá Núi Nhỏ"),
          (2007, "Chi nhánh Bình Phước:\nmỏ Mũi Tàu"), (2010, "Niêm yết HOSE\n23/06/2010"), (2017, "VĐL 219,2 tỷ"),
          (2019, "GP Mũi Tàu 1,0 tr m³/năm\ntới 2043; Núi Nhỏ hết GP"), (2021, "Đề án đóng cửa\nmỏ Núi Nhỏ"), (2025, "Lần đầu khai thác\n100% công suất")]
    fig, ax = plt.subplots(figsize=(7.2, 2.3)); ax.axis("off"); ax.set_xlim(-0.6, len(ev) - 0.4); ax.set_ylim(-1.6, 1.6)
    ax.plot([-0.5, len(ev) - 0.5], [0, 0], color=NAVY, lw=2)   # trục theo THỨ TỰ mốc, không theo tỉ lệ năm
    for i, (y, t) in enumerate(ev):
        up = 1 if i % 2 == 0 else -1
        ax.plot([i, i], [0, 0.45 * up], color=GREY, lw=0.8); ax.plot(i, 0, "o", color=ACCENT if y >= 2019 else NAVY, ms=6)
        ax.text(i, 0.55 * up, f"{y}\n{t}" if up > 0 else f"{t}\n{y}", ha="center", va="bottom" if up > 0 else "top", fontsize=6.1, color="#222")
    save(fig, "fig_04_history", "Nguồn: Báo cáo thường niên 2025, mục 'Quá trình hình thành và phát triển' (tr.2–3). Trục theo thứ tự mốc, không theo tỉ lệ thời gian.",
         pd.DataFrame(ev, columns=["nam", "moc"])); plt.close(fig)

    # 05 Chuỗi giá trị / sản phẩm ---------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.5)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    steps = [("Nổ mìn, khai thác", "đá nguyên khối\n≤1,0 tr m³/năm (GP)"), ("Nghiền – sàng", "≈1,42 tr m³ thành phẩm/năm;\ndây chuyền mới 350 t/h"),
             ("Sản phẩm", "1x2 · 4x6 · hộc · 0x4\nmi sàng · mi bụi"), ("Khách hàng", "TP.HCM · Đồng Nai\nít Tây Ninh")]
    for i, (t, d) in enumerate(steps):
        x = 0.15 + i * 2.5
        ax.add_patch(mp.FancyBboxPatch((x, 1.7), 2.05, 1.6, boxstyle="round,pad=0.05", fc=NAVY if i != 2 else ACCENT, ec="none"))
        ax.text(x + 1.02, 2.95, t, ha="center", color="white", fontsize=8.2, fontweight="bold")
        ax.text(x + 1.02, 2.2, d, ha="center", color="white", fontsize=6.5)
        if i < 3:
            ax.annotate("", (x + 2.42, 2.5), (x + 2.12, 2.5), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.4))
    uses = [("1x2", "cốt liệu bê tông xi măng,\nbê tông nhựa nóng"), ("4x6 · hộc", "bê tông lót, móng,\nkè, tường chắn"),
            ("0x4 · mi", "móng đường giao thông,\nnền nhà xưởng, gạch không nung")]
    for i, (p, u) in enumerate(uses):
        ax.text(0.4 + i * 3.3, 1.2, p, fontsize=7.6, fontweight="bold", color=ACCENT)
        ax.text(0.4 + i * 3.3, 1.0, u, fontsize=6.4, color="#333", va="top")
    save(fig, "fig_05_value_chain", "Nguồn: BCTN 2025 tr.6–9 (sản phẩm, công suất), tr.13 (thị trường); BCTC Q3/2026 V10a (máy nghiền 350 t/h). Cơ cấu sản lượng theo sản phẩm: công ty không công bố.",
         pd.DataFrame(steps + uses, columns=["muc", "mo_ta"])); plt.close(fig)

    # 06 Sơ đồ tài sản (không theo tỉ lệ) --------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0.6, 4.7)
    assets = [(7.6, 3.9, "Mỏ Mũi Tàu (Tân Lập, Đồng Phú)", "51,5 ha · đang khai thác · GP tới 2043\nchi nhánh Bình Phước cũ", NAVY),
              (7.9, 1.6, "Tam Lập 1 khu II", "đã chi 83,5 tỷ đền bù + đặt trước;\nchưa có giấy phép khai thác", GREY),
              (2.2, 1.6, "Mỏ Núi Nhỏ (Dĩ An)", "27,34 ha · hết GP 2019 · đóng cửa\nnay cho thuê kho bãi (~18,9 tỷ DT/năm)", ACCENT),
              (2.0, 4.0, "Thị trường chính", "TP.HCM · Đồng Nai · ít Tây Ninh\n(cự ly vận chuyển quyết định thị trường)", GREEN)]
    for x, y, t, d, cc in assets:
        ax.add_patch(mp.Circle((x - 1.75, y), 0.16, fc=cc, ec="none"))
        ax.text(x - 1.5, y + 0.12, t, fontsize=7.8, fontweight="bold", color=cc)
        ax.text(x - 1.5, y - 0.12, d, fontsize=6.4, color="#333", va="top")
    ax.annotate("", (2.2, 3.9), (5.6, 3.9), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2, ls="--"))
    ax.text(3.9, 4.25, "đá thành phẩm, xe tải", fontsize=6.2, color=NAVY, ha="center")
    save(fig, "fig_06_asset_map", "Sơ đồ minh hoạ, KHÔNG theo tỉ lệ/địa lý. Nguồn: BCTN 2025 tr.2–6, 13; BCTC Q3/2026 V10a, tr.26; BCTC 2025 kiểm toán TM 7.1.",
         pd.DataFrame([(t, d) for _, _, t, d, _ in assets], columns=["tai_san", "mo_ta"])); plt.close(fig)

    # 07 Cổ đông ----------------------------------------------------------------
    own = [("CTCP VL&XD Bình Dương (MVC)", 44.07), ("CTCP Đầu tư Thái Bình", 15.93), ("Bà Nguyễn Thị Mai Phương", 7.01), ("Cổ đông khác (free float)", 32.99)]
    fig, ax = plt.subplots(figsize=(7.2, 2.3))
    left = 0
    for i, (n, v) in enumerate(own):
        ax.barh([0], [v], left=left, color=[NAVY, "#4A6A8F", GREY, LIGHT][i], height=0.5)
        ax.text(left + v / 2, 0, f"{vn(v, 1)}%", ha="center", va="center", fontsize=8, color="white" if i < 2 else "#222", fontweight="bold")
        ax.text(left + v / 2, -0.45 if i % 2 == 0 else 0.45, n, ha="center", va="center", fontsize=6.6)
        left += v
    ax.set_xlim(0, 100); ax.set_ylim(-0.8, 0.8); ax.axis("off")
    ax.set_title("Cổ đông: MVC 44,07% (tăng nhẹ trong 2026); NNC ngược lại sở hữu ~10,3% MVC — sở hữu chéo")
    save(fig, "fig_07_ownership", "Nguồn: BCTC Q3/2026 V22 (MVC 9.659.170 cp); BCTN 2025 tr.18–19 (danh sách ngày 11/03/2026). Nước ngoài 3,19%. Free float = phần còn lại (tính).",
         pd.DataFrame(own, columns=["co_dong", "ty_le_pct"])); plt.close(fig)

    # 08 Dòng tiền -------------------------------------------------------------
    cf = pd.DataFrame({"ky": ["9T/2025", "9T/2026"], "lnst": [93.95, 160.08], "cfo": [132.9, 109.3], "capex": [53.9, 131.1]})
    fig, ax = plt.subplots(figsize=(7.2, 2.5)); x = np.arange(2); w = 0.26
    for j, (c_, lab, cc) in enumerate((("lnst", "LNST", NAVY), ("cfo", "Dòng tiền kinh doanh", GREEN), ("capex", "Đầu tư TSCĐ + Tam Lập", ACCENT))):
        ax.bar(x + (j - 1) * w, cf[c_], w, color=cc, label=lab)
        for xi, v in zip(x, cf[c_]):
            ax.text(xi + (j - 1) * w, v + 2, vn(v, 1), ha="center", fontsize=6.6)
    ax.set_xticks(x, cf["ky"]); ax.set_ylabel("tỷ đồng"); ax.legend(fontsize=7, frameon=False, ncol=3, loc="upper left")
    ax.set_ylim(0, 190); ax.set_title("Dòng tiền 9T/2026 = 0,68× LNST do nộp thuế năm trước + truy thu; capex tăng vì mỏ Tam Lập")
    fig.subplots_adjust(bottom=0.17, top=0.88)
    save(fig, "fig_08_cashflow", "Nguồn: BCTC riêng Q3/2026 tr.4–5 (LCTT), V10a. Hai năm cộng lại CFO/LNST ~0,96×.", cf); plt.close(fig)

    # 09 Tiền ròng waterfall ----------------------------------------------------
    wf = [("Tiền + tiền gửi + CK", 348.04), ("Vay", -74.89), ("Truy thu (dự phòng)", -22.37), ("Quỹ khen thưởng", -16.78),
          ("Cổ tức phải trả", -5.89), ("DP môi trường", -4.50)]
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); cum = 0
    for i, (n, v) in enumerate(wf):
        ax.bar(i, v, bottom=cum if v < 0 else 0, color=NAVY if v > 0 else ACCENT, width=0.6)
        ax.text(i, (cum + v if v < 0 else v) + 6, vn(v, 1), ha="center", fontsize=6.8); cum += v
    ax.bar(len(wf), cum, color=GREEN, width=0.6); ax.text(len(wf), cum + 6, vn(cum, 1), ha="center", fontsize=7, fontweight="bold")
    ax.set_xticks(range(len(wf) + 1), [n for n, _ in wf] + ["Tiền ròng sau\nnghĩa vụ"], fontsize=6.4)
    ax.set_ylabel("tỷ đồng"); ax.set_ylim(0, 390)
    ax.set_title("Tiền ròng sau các nghĩa vụ ngoài vận hành: 223,6 tỷ (10.200 đ/cp, ~22% vốn hoá)")
    fig.subplots_adjust(bottom=0.2, top=0.9)
    save(fig, "fig_09_net_cash", "Nguồn: BCTC riêng Q3/2026 tr.1–3, V1, V2, V19a, V21 (30/09/2026). 82,1 tỷ tiền gửi đang cầm cố bảo lãnh chính các khoản vay (tr.26) — đã cấn trừ với vay.",
         pd.DataFrame(wf + [("tien_rong_sau_nghia_vu", round(cum, 2))], columns=["khoan", "ty"])); plt.close(fig)

    # 10 Cụm mỏ: trữ lượng & thời hạn ---------------------------------------
    mines = pd.DataFrame({"mo": ["Rạch Rạt", "Mũi Tàu (NNC)", "Suối Rạc", "Tam Lập 3", "Tam Lập 2 - khu B"],
                          "tru_luong_tr_m3": [20.3, 20.2, 11.1, 7.5, 5.5], "nam_con_lai": [25, 17, 36, 9, 7]})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.6))
    cc = [ACCENT if "NNC" in m else NAVY for m in mines["mo"]]
    a1.barh(mines["mo"], mines["tru_luong_tr_m3"], color=cc); a1.invert_yaxis(); a1.set_title("Trữ lượng còn lại (tr m³ nguyên khối)")
    a2.barh(mines["mo"], mines["nam_con_lai"], color=cc); a2.invert_yaxis(); a2.set_title("Thời hạn khai thác còn lại (năm)"); a2.set_yticklabels([])
    for ax_, col_ in ((a1, "tru_luong_tr_m3"), (a2, "nam_con_lai")):
        for i, v in enumerate(mines[col_]):
            ax_.text(v + 0.3, i, vn(v, 1) if col_ == "tru_luong_tr_m3" else str(v), va="center", fontsize=6.6)
        ax_.tick_params(labelsize=6.6)
    fig.subplots_adjust(left=0.17, bottom=0.17, wspace=0.08)
    save(fig, "fig_10_cluster_mines", "Nguồn: FPTS báo cáo định giá lần đầu NNC 07/01/2026, tr.9 (Sở TN&MT các tỉnh, FPTS tổng hợp) — nguồn thứ cấp. Hai mỏ Tam Lập mới cấp 2025 là nguồn cung mới chính của cụm.",
         mines); plt.close(fig)

    # 11 Giả định số 1: đường giá danh nghĩa (kịch bản cơ sở) ----------------
    yrs = np.arange(2027, 2044)
    def p(mode):
        out = []
        for y in yrs:
            base = 380 if y == 2027 else (300 if y < 2031 else 320)
            g = {"flat": 1.0, "g2031": 1.03 ** max(0, y - 2030), "g2028": 1.03 ** max(0, y - 2027), "real": 1.03 ** (y - 2026)}[mode]
            out.append(base * g)
        return out
    pdat = pd.DataFrame({"nam": yrs, "phang": p("flat"), "tang3_tu2031": p("g2031"), "tang3_tu2028": p("g2028"), "giu_gia_tri_thuc": p("real"),
                         "chi_phi_bien_doi_k097": [110 * 0.97 * 1.03 ** (y - 2026) for y in yrs]})
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    for c_, lab, cc, ls in (("phang", "Giá phẳng danh nghĩa → KV 60,0k", ACCENT, "-"), ("tang3_tu2031", "+3%/năm từ 2031 → 69,1k", "#B08A3E", "--"),
                             ("tang3_tu2028", "+3%/năm từ 2028 → 76,6k", "#4A6A8F", "--"), ("giu_gia_tri_thuc", "Giữ giá trị thực → 80,2k", GREEN, "-")):
        ax.plot(pdat["nam"], pdat[c_], color=cc, lw=2, ls=ls, label=lab)
    ax.plot(pdat["nam"], pdat["chi_phi_bien_doi_k097"], color=GREY, lw=1.4, ls=":", label="Chi phí biến đổi/m³ (+3%/năm)")
    ax.set_ylabel("nghìn đ/m³ (danh nghĩa)"); ax.legend(fontsize=6.6, frameon=False, loc="upper left")
    ax.set_title("Giả định số 1: giá đá danh nghĩa sau 'vách' 2028 (kịch bản cơ sở)")
    fig.subplots_adjust(bottom=0.16, top=0.89)
    save(fig, "fig_11_price_paths", "Nguồn: mô hình của nhóm (ước lượng), ../calc/valuation_v2.py. KV = giá trị kỳ vọng 4 kịch bản (25/50/20/5), r 13%, chi phí ×0,97, MVC không chiết khấu. "
         "Lịch sử tham chiếu: giá đá 1x2 tại mỏ ~140–150k/tấn (≤2020) → 177–240k/tấn (đầu 2026).", pdat.round(1)); plt.close(fig)

    # 12 Ba kịch bản -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    names = list(SC3.keys())
    for i, n in enumerate(names):
        pr, lo, hi = SC3[n]
        ax.barh(i, hi - lo, left=lo, color=[GREEN, NAVY, ACCENT][i], height=0.5)
        ax.text(hi + 1500, i, f"{k(lo)}–{k(hi)}  (xác suất {int(pr*100)}%)", va="center", fontsize=7)
    ax.axvline(PX, color="#222", lw=1.3); ax.text(PX + 1000, 2.4, "giá 47,1k", ha="left", fontsize=6.8)
    ax.set_yticks(range(3), names); ax.invert_yaxis(); ax.set_xlim(15_000, 160_000)
    ax.xaxis.set_major_formatter(lambda v, p_: f"{v/1e3:.0f}k")
    ax.set_title("Ba kịch bản (đầu trái = giá đá danh nghĩa phẳng, đầu phải = giữ giá trị thực)")
    fig.subplots_adjust(left=0.12, bottom=0.18, top=0.88)
    save(fig, "fig_12_scenarios", "Nguồn: ../calc/valuation_v2_3scen.csv; r 13%, chi phí ×0,97, MVC chiết khấu 15%. Tiêu cực = xấu (20%) + rất xấu (5%). Xác suất là nhận định của nhóm.",
         pd.DataFrame([(n, *SC3[n]) for n in names], columns=["kich_ban", "xac_suat", "gia_phang", "gia_thuc"])); plt.close(fig)

    # 13 Football field -----------------------------------------------------------
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    p12 = px[px["time"] >= "2025-10-30"]
    ff = [("Giá 12 tháng (điều chỉnh)", p12["Close"].min(), p12["Close"].max()),
          ("PE nhóm 3,7–7,1× nhân EPS TTM 9.761", 3.65 * EPS_TTM, 7.13 * EPS_TTM),
          ("DCF: 3 kịch bản (tiêu cực → tích cực)", SC3["Tiêu cực"][1], SC3["Tích cực"][2]),
          ("DCF: lưới 72 tổ hợp P10–P90", GRID["p10"], GRID["p90"]),
          ("DCF: vùng hợp lý (phẳng → thực)", FV_LO, FV_HI)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    for i, (n, lo, hi) in enumerate(ff):
        ax.barh(i, hi - lo, left=lo, color=GREEN if i == 4 else NAVY, alpha=1 if i == 4 else 0.7, height=0.5)
        ax.text(hi + 1200, i, f"{k(lo)}–{k(hi)}", va="center", fontsize=6.8)
    ax.axvline(PX, color=ACCENT, lw=1.6); ax.text(PX - 800, -0.62, "giá 47,1k", color=ACCENT, ha="right", fontsize=6.8, fontweight="bold")
    ax.axvline(FPTS_TP, color=GREY, lw=1, ls="--"); ax.text(FPTS_TP + 600, -0.62, "FPTS 01/2026: 51,4k", fontsize=6.2, color="#555")
    ax.set_ylim(-0.9, len(ff) - 0.5)
    ax.set_yticks(range(len(ff)), [n for n, _, _ in ff], fontsize=6.8); ax.set_xlim(15_000, 150_000)
    ax.xaxis.set_major_formatter(lambda v, p_: f"{v/1e3:.0f}k"); ax.set_title("Football field (đ/cp)")
    fig.subplots_adjust(left=0.33, bottom=0.17, top=0.88)
    save(fig, "fig_13_football_field", "Nguồn: tav2_bq.ticker (giá 30/10/2025–30/10/2026, giá điều chỉnh); PE TTM nhóm BQ 30/10/2026; DCF ../calc/valuation_v2_out.txt; FPTS 07/01/2026 (FCFF, WACC 12,6%, g 2%).",
         pd.DataFrame(ff, columns=["phuong_phap", "thap", "cao"]).round(0)); plt.close(fig)

    # 14 Độ nhạy giá × sản lượng (2 chế độ) ------------------------------------
    flat = [[31341, 34553, 40166, 46918, 54024, 61131], [32973, 39124, 47267, 56135, 65017, 73900],
            [35615, 44291, 54691, 65351, 76010, 86669], [38735, 49742, 62131, 74567, 87003, 99439]]
    real = [[35584, 44407, 53231, 62055, 70879, 79703], [41832, 52862, 63892, 74921, 85951, 96981],
            [48080, 61316, 74552, 87788, 101023, 114259], [54329, 69770, 85212, 100654, 116096, 131537]]
    prices, vols = [220, 260, 300, 340, 380, 420], [0.8, 1.0, 1.2, 1.4]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for ax, M, t in ((axs[0], flat, "Giá đá danh nghĩa phẳng"), (axs[1], real, "Giá giữ giá trị thực")):
        M = np.array(M); ax.imshow(M >= PX, cmap="RdYlGn", vmin=-0.6, vmax=1.6, aspect="auto"); ax.grid(False)
        for r_ in range(4):
            for c_ in range(6):
                ax.text(c_, r_, f"{M[r_, c_]/1e3:.0f}", ha="center", va="center", fontsize=6.6)
        ax.set_xticks(range(6), prices, fontsize=6.4); ax.set_yticks(range(4), [vn(v_, 1) for v_ in vols], fontsize=6.4)
        ax.set_xlabel("giá 2028+ (nghìn đ/m³, tiền 2026)", fontsize=6.6); ax.set_title(t, fontsize=8)
    axs[0].set_ylabel("sản lượng 2028+ (tr m³)", fontsize=6.6)
    fig.subplots_adjust(bottom=0.22, top=0.88, wspace=0.18)
    save(fig, "fig_14_sensitivity", "Nguồn: ../calc/valuation_v2_out.txt (nghìn đ/cp; r 13%, chi phí ×0,97, MVC −15%, 2027 = 1,4 tr m³ × 380k). Xanh = ≥ giá 47.100.",
         pd.DataFrame([(m, v, p_, M_[i][j]) for m, M_ in (("phang", flat), ("thuc", real)) for i, v in enumerate(vols) for j, p_ in enumerate(prices)],
                      columns=["che_do", "san_luong", "gia", "dong_cp"])); plt.close(fig)

    # 15 Giá 12T + công bố KQKD --------------------------------------------------
    p2 = px[px["time"] >= "2025-07-01"]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.plot(p2["time"], p2["Close"], color=NAVY, lw=1.4)
    evs = [("2025-10-17", "KQ Q3/25"), ("2026-01-21", "KQ Q4/25"), ("2026-04-20", "KQ Q1/26"), ("2026-07-20", "KQ Q2/26"), ("2026-10-20", "KQ Q3/26")]
    import pandas as _pd
    for d, t in evs:
        d = _pd.Timestamp(d); ax.axvline(d, color=GREY, lw=0.8, ls="--"); ax.text(d, p2["Close"].max() * 1.02, t, fontsize=6.2, ha="center")
    ax.yaxis.set_major_formatter(lambda v, p_: f"{v/1e3:.0f}k"); ax.set_ylim(p2["Close"].min() * 0.9, p2["Close"].max() * 1.1)
    ax.set_title("Giá cổ phiếu: đỉnh 74,7k (29/12/2025) → đáy 37,0k (14/09/2026) trong khi LNST 4 quý gần nhất tăng 87%")
    fig.subplots_adjust(bottom=0.14, top=0.88)
    save(fig, "fig_15_price", "Nguồn: tav2_bq.ticker NNC Close (giá điều chỉnh) 01/07/2025–30/10/2026; ngày công bố = Release_Date trong tav2_bq.ticker_financial. Quan sát, không suy nhân quả.",
         p2[["time", "Close", "Volume"]]); plt.close(fig)

    # 16 So sánh ngang ngành ------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.2))
    names_ = list(PEERS.keys()); vals = list(PEERS.values())
    ax.bar(names_, vals, color=[ACCENT if n == "NNC" else NAVY for n in names_], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.15, vn(v, 2) + "×", ha="center", fontsize=7)
    ax.set_ylim(0, 8.5); ax.set_ylabel("PE TTM (×)"); ax.set_title("PE TTM nhóm đá xây dựng niêm yết: cả nhóm giao dịch 3,7–7,1× lợi nhuận hiện tại")
    fig.subplots_adjust(bottom=0.3, top=0.86)
    save(fig, "fig_16_peers", "Nguồn: tav2_bq.ticker Close 30/10/2026 × ticker_financial.OShares / Σ NP_P0 Q4/25–Q3/26. *VLB gồm Q2/26 374 tỷ nhiều khả năng một lần (~6,3× nếu bỏ, ước lượng).",
         pd.DataFrame({"ma": names_, "pe_ttm": vals})); plt.close(fig)

    # 17 Ma trận rủi ro -----------------------------------------------------------
    risks = [("Vách 2028 sâu: 0,8 tr m³ × 250k\n(mỏ Tam Lập đủ công suất)", 0.25, 0.9), ("Giá đá giảm vừa 2028–30 (kịch bản cơ sở)", 0.5, 0.6), ("Giá đá quay đầu sớm 2027", 0.15, 0.7), ("Chi phí/diesel tăng", 0.55, 0.38),
             ("Truy thu/phạt (công suất, tiền cấp quyền)", 0.2, 0.3), ("Bên liên quan NHC/MVC", 0.5, 0.2), ("MVC ≥51%, buộc thoái MVC", 0.1, 0.12),
             ("LN giữ lại, đầu tư ngoài ngành", 0.35, 0.48), ("Thanh khoản cổ phiếu thấp", 0.85, 0.2)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.axvspan(0.5, 1, ymin=0.5, ymax=1, color=ACCENT, alpha=0.08)
    for t, x_, y_ in risks:
        ax.plot(x_, y_, "o", color=ACCENT if x_ * y_ > 0.15 else NAVY, ms=7)
        ax.text(x_ + 0.02, y_, t, fontsize=6.3, va="center")
    ax.set_xlim(0, 1.25); ax.set_ylim(0, 1.05); ax.set_xlabel("xác suất (nhận định)"); ax.set_ylabel("tác động lên giá trị")
    ax.set_title("Ma trận rủi ro (nhận định của nhóm, không phải đầu ra mô hình)")
    fig.subplots_adjust(bottom=0.24, top=0.9)
    save(fig, "fig_17_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu dựa trên mục 8–9; xác suất/tác động là định tính đã quy ra thang 0–1.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"])); plt.close(fig)

    # 18 Lịch xúc tác -------------------------------------------------------------
    cats = [("2027-01-20", "BCTC Q4/2026\n(~20/01/2027)"), ("2027-04-20", "BCTC Q1/2027\n(~20/04/2027)"), ("2027-06-30", "VĐ4 ≥20% khối lượng?\nmỏ đấu giá được cấp GP?"),
            ("2027-08-31", "Giá đá Sở XD Đồng Nai\nQ2/27 vs Q3/26")]   # GP Tam Lập 1 khu II, MVC/NHC: chưa có ngày -> chỉ ở bảng mục 10
    import pandas as pd2
    fig, ax = plt.subplots(figsize=(7.2, 2.0)); ax.axis("off")
    ds = [pd2.Timestamp(d) for d, _ in cats]; t0, t1 = pd2.Timestamp("2026-11-01"), pd2.Timestamp("2027-09-30")
    ax.set_xlim(t0, t1); ax.set_ylim(-1.3, 1.3); ax.plot([t0, t1], [0, 0], color=NAVY, lw=2)
    for i, (d, (_, t)) in enumerate(zip(ds, cats)):
        up = 1 if i % 2 == 0 else -1
        ax.plot(d, 0, "o", color=ACCENT, ms=6); ax.plot([d, d], [0, 0.35 * up], color=GREY, lw=0.8)
        ax.text(d, 0.42 * up, t, ha="center", va="bottom" if up > 0 else "top", fontsize=6.3)
    save(fig, "fig_18_catalysts", "Nguồn: lịch công bố BCTC theo quy định (ước lượng ngày); chỉ báo theo dõi của người đọc ngành độc lập (giá Sở XD, VĐ4, giấy phép mỏ mới).",
         pd.DataFrame(cats, columns=["ngay", "moc"])); plt.close(fig)
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
BREAK_BEFORE = ("3.",)


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
        page.insert_text((42, 34), "NNC — CTCP Đá Núi Nhỏ · Báo cáo Due Diligence · 31/10/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "NNC_DD_investor_report_20261031.md"), os.path.join(HERE, "NNC_DD_investor_report_20261031.pdf"))
