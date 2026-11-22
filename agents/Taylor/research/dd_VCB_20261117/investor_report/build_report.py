"""Dựng biểu đồ + PDF cho báo cáo DD nhà đầu tư VCB (dữ liệu tới BCTC Q3/2026; neo định giá 17/11/2026; giá đóng cửa 20/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Nguồn số: ../REPORT.md + ../calc_r4_output.txt (calc.py trên assumptions_VCB_20261117.json, md5 85d41e08f834127e57cd740ed88dd931).
Đầu vào figs/: fin_quarterly_bq.csv (tav2_bq.ticker_financial VCB 2019Q1–2026Q3), price_raw.csv (tav2_bq.ticker VCB 03/11/2025–20/11/2026),
fig_map_hn.png / fig_map_hcm.png (make_map.py, điểm ở fig_map_*_points.csv).
Ảnh: src/logo.png, src/web_khcn.jpg, src/web_visa.jpg (website vietcombank.com.vn, tải 22/11/2026).
Mỗi hình ghi kèm CSV (figs/fig_XX_*.csv).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")
STEM = "VCB_DD_investor_report_20261122"

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung: calc_r4_output.txt (đã khớp REPORT.md) ----
BVPS = 30_359
G = 0.07
KE = 0.135
PX17 = 52_100            # đóng cửa 17/11/2026 (neo định giá)
PX20 = 50_200            # đóng cửa 20/11/2026 = DNSE latest_trade 20/11 14:45:05 (bảng G1)
SCEN = {"Xấu": (28_958, 0.25, "ROE 13,2%"), "Cơ sở": (35_497, 0.50, "ROE 14,6%"), "Tốt": (55_198, 0.25, "ROE 18%, g 8%")}
WEIGHTED = 38_787
KE_SENS = {"-100bp": 41_950, "-50bp": 38_455, "0": 35_497, "+50bp": 32_961, "+100bp": 30_764}
BETA05 = {"-100bp": 38_455, "+100bp": 32_961}
ROE_ANCH = {13.2: 28_958, 14.6: 35_497, 16.0: 42_035}
KE_BETA_REAL = 46_145     # Ke 12%
TWO_STAGE = (36_135, 45_069)
DIV_CASH, DIV_HAIRCUT, VAL_POST, VAL_TOTAL = 2_433, 2_845, 32_652, 35_085
PEERS = [  # P/B 17/11/2026, P10, trung vị, P90 (5 năm) — tav2_bq.ticker cột PB
    ("VCB", 1.72, 2.16, 2.83, 3.33), ("BID", 1.19, 1.57, 1.97, 2.28), ("CTG", 1.16, 1.18, 1.36, 1.66),
    ("ACB", 1.14, 1.26, 1.40, 1.74), ("TCB", 1.14, 0.87, 1.21, 1.79), ("MBB", 1.16, 1.03, 1.26, 1.71),
    ("VPB", 1.08, 1.03, 1.20, 1.67), ("HDB", 1.55, 1.16, 1.46, 1.88), ("STB", 2.12, 1.14, 1.33, 2.06)]


def val(roe, ke=KE, g=G):
    return BVPS * (roe - g) / (ke - g)


def implied(px):
    pb = px / BVPS
    return G + pb * (KE - G), G + (0.146 - G) / pb


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


def vn(v, d=0):
    s = f"{v:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def figs():
    import numpy as np
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()
    # kiểm số khớp mô hình
    ok = lambda a, b: abs(a - b) <= 1
    assert ok(val(0.146), 35_497) and ok(val(0.132), 28_958) and ok(val(0.16), 42_035)
    assert ok(val(0.146, 0.125), 41_950) and ok(val(0.146, 0.145), 30_764)
    assert ok(sum(v * p for v, p, _ in SCEN.values()), WEIGHTED)
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    assert float(px.loc[px.time == "2026-11-17", "Close"].iloc[0]) == PX17
    assert float(px.loc[px.time == "2026-11-20", "Close"].iloc[0]) == PX20
    r17, k17 = implied(PX17)
    r20, k20 = implied(PX20)
    assert round(r17, 3) == 0.182 and round(k17, 3) == 0.114
    print(f"implied 17/11 ROE {r17:.4f} Ke {k17:.4f} | 20/11 ROE {r20:.4f} Ke {k20:.4f} PB {PX20 / BVPS:.3f}")

    # 0. HERO: ảnh website + thanh định giá
    im = Image.open(os.path.join(SRC, "web_khcn.jpg")).convert("RGB")
    w, h = im.size
    im = im.crop((int(w * 0.30), int(h * 0.05), int(w * 0.92), int(h * 0.80)))
    fig = plt.figure(figsize=(7.2, 3.9))
    a0 = fig.add_axes([0.0, 0.50, 1.0, 0.50]); a0.imshow(im, aspect="auto"); a0.axis("off")
    a0.text(0.012, 0.93, "Ngân hàng thương mại Nhà nước · NPL 0,71% · bao phủ nợ xấu 243% · CASA 31,8%", transform=a0.transAxes,
            fontsize=9.6, color="white", fontweight="bold", va="top", bbox=dict(facecolor=NAVY, alpha=0.85, lw=0, pad=4))
    a0.text(0.988, 0.04, "Ảnh: website Vietcombank", transform=a0.transAxes, fontsize=6.5, color="white", ha="right",
            bbox=dict(facecolor="black", alpha=0.35, lw=0, pad=1.5))
    a1 = fig.add_axes([0.05, 0.17, 0.90, 0.15]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xlim(24_000, 60_000); a1.set_ylim(0, 1); a1.set_xticks([])
    a1.barh(0.5, SCEN["Tốt"][0] - SCEN["Xấu"][0], left=SCEN["Xấu"][0], height=0.42, color="#EEF1F4")
    a1.barh(0.5, KE_SENS["-100bp"] - KE_SENS["+100bp"], left=KE_SENS["+100bp"], height=0.62, color=LIGHT)
    a1.plot([SCEN["Cơ sở"][0]] * 2, [0.15, 0.85], color=NAVY, lw=2.6)
    a1.plot([WEIGHTED] * 2, [0.25, 0.75], color=GREEN, lw=2.0)
    a1.plot([PX17] * 2, [0.02, 0.98], color=ACCENT, lw=2.6)
    a1.plot([PX20] * 2, [0.10, 0.90], color=ACCENT, lw=1.2, ls=":")
    for k in ("Xấu", "Tốt"):
        a1.plot(SCEN[k][0], 0.5, "D", color=GREY, ms=6)
        a1.text(SCEN[k][0], -0.62, f"{k}\n{vn(SCEN[k][0] / 1e3, 1)}k", ha="center", fontsize=6.9, color="#555")
    a1.text(SCEN["Cơ sở"][0], 1.06, f"Tâm {vn(SCEN['Cơ sở'][0] / 1e3, 1)}k", ha="right", fontsize=7.6, color=NAVY, fontweight="bold")
    a1.text(WEIGHTED, -0.62, f"Có trọng số\n{vn(WEIGHTED / 1e3, 1)}k", ha="center", fontsize=6.9, color=GREEN)
    a1.text(PX17 + 300, 1.06, f"Giá {vn(PX17 / 1e3, 1)}k (17/11) · {vn(PX20 / 1e3, 1)}k (20/11)", ha="left", fontsize=7.4, color=ACCENT, fontweight="bold")
    a1.text(36_300, -0.62, "", ha="center")
    a1.text(30_900, 1.06, f"Vùng hợp lý {vn(KE_SENS['+100bp'] / 1e3, 1)}–{vn(KE_SENS['-100bp'] / 1e3, 1)}k", ha="right", fontsize=6.9, color="#333")
    fig.text(0.05, 0.41, "Giá trị/cp theo P/B = (ROE bền − g)/(Ke − g), BVPS 30.359 đ, Ke 13,5%, g 7%; giá 17/11 hàm ý ROE bền 18,2% hoặc Ke 11,4%",
             fontsize=7.0, color="#222")
    save(fig, "fig_00_hero", "Nguồn: ảnh website vietcombank.com.vn; BCTC hợp nhất Q3/2026; giá đóng cửa HOSE 17/11 và 20/11/2026; giá trị: mô hình của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia_17_11", "gia_20_11", "tam", "co_trong_so", "vung_thap", "vung_cao", "xau", "tot"],
                       "dcp": [PX17, PX20, SCEN["Cơ sở"][0], WEIGHTED, KE_SENS["+100bp"], KE_SENS["-100bp"], SCEN["Xấu"][0], SCEN["Tốt"][0]]}))
    plt.close(fig)

    # 1. LNST quý (BQ)
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    q = fin[fin.quarter >= "2023Q1"].reset_index(drop=True)
    q["np"] = q.NP_P0 / 1e9
    x = np.arange(len(q))
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    col = [ACCENT if s == "2026Q2" else (NAVY if s.startswith("2026") else LIGHT) for s in q.quarter]
    ax.bar(x, q.np, color=col, width=0.7)
    for i, v in enumerate(q.np):
        ax.text(i, v + 150, vn(v / 1e3, 1), ha="center", fontsize=7)
    i2 = int(q.index[q.quarter == "2026Q2"][0])
    ax.annotate("gồm ≈3.171 tỷ lãi đánh giá lại\nkhi hợp nhất (một lần, không chịu thuế)", (i2, q.np[i2]), xytext=(i2 - 6.5, 13_200),
                fontsize=7.3, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
    ax.set_xticks(x, [s[4:] + "/" + s[2:4] for s in q.quarter], fontsize=7.5)
    ax.set_ylabel("LNST, nghìn tỷ đồng" if False else "LNST quý, tỷ đồng"); ax.set_ylim(0, 16_500)
    ax.yaxis.set_major_formatter(lambda v, p: vn(v))
    ax.set_title("LNST quý lõi quanh 9.000 tỷ; Q2/26 phồng nhờ khoản một lần, Q3/26 về lại nền")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_npat_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (VCB); khoản một lần: giải trình biến động LNST kèm BCTC hợp nhất Q3/2026 (mục 2). Nhãn = nghìn tỷ đồng.",
         q[["quarter", "np"]])
    plt.close(fig)

    # 2. Kết quả 9T: dòng thu nhập
    inc = pd.DataFrame({"dong": ["Thu nhập lãi thuần", "Dịch vụ thuần", "Ngoại hối", "HĐ khác thuần", "Chi phí HĐ", "LN trước dự phòng", "Dự phòng", "LNTT"],
                        "t9_26": [57_179, 2_707, 6_408, 5_919, 23_363, 49_620, 9_180, 40_440],
                        "t9_25": [42_505, 2_605, 4_939, 2_748, 17_715, 35_470, 2_338, 33_133]})
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    xi = np.arange(len(inc)); w = 0.38
    ax.bar(xi - w / 2, inc.t9_25, w, color=LIGHT, label="9T/2025")
    ax.bar(xi + w / 2, inc.t9_26, w, color=[NAVY] * 4 + [GREY, NAVY, ACCENT, NAVY], label="9T/2026")
    for i, r in inc.iterrows():
        d = r.t9_26 / r.t9_25 - 1
        ax.text(i + w / 2, r.t9_26 + 900, f"{'+' if d >= 0 else '−'}{vn(abs(d) * 100, 0)}%" if r.dong != "Dự phòng" else "×3,9",
                ha="center", fontsize=7.2, color=ACCENT if r.dong == "Dự phòng" else "#222", fontweight="bold")
    ax.set_xticks(xi, ["Lãi thuần", "Dịch vụ", "Ngoại hối", "HĐ khác*", "Chi phí", "LN trước\ndự phòng", "Dự phòng", "LNTT"], fontsize=7.5)
    ax.set_ylabel("tỷ đồng"); ax.yaxis.set_major_formatter(lambda v, p: vn(v)); ax.set_ylim(0, 66_000)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.set_title("LN trước dự phòng +40%, nhưng dự phòng gấp 3,9 lần nên LNTT chỉ +22%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_income_9m", "Nguồn: BCTC hợp nhất Q3/2026 (kết quả kinh doanh, TM6–7). *HĐ khác gồm ≈3.171 tỷ một lần. Dự phòng = cho vay 6.190 + trái phiếu DN chưa niêm yết 2.997 (tổng làm tròn).", inc)
    plt.close(fig)

    # 3. Chất lượng tài sản
    aq = pd.DataFrame({"moc": ["31/12/2025", "30/09/2026"], "nhom2": [2_702, 4_995], "nhom3": [761, 2_571], "nhom4": [302, 1_657],
                       "nhom5": [8_651, 8_589], "du_phong": [24_980, 31_168], "npl_pct": [0.58, 0.71], "bao_phu_pct": [257, 243]})
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    xi = np.arange(2); w = 0.34; bot = np.zeros(2)
    for c, lab, cl in (("nhom5", "Nhóm 5", "#7A2E22"), ("nhom4", "Nhóm 4", ACCENT), ("nhom3", "Nhóm 3", "#E39B88"), ("nhom2", "Nhóm 2 (cần chú ý)", "#F3D2C8")):
        ax.bar(xi - w / 2, aq[c], w, bottom=bot, color=cl, label=lab); bot += aq[c].values
    ax.bar(xi + w / 2, aq.du_phong, w, color=NAVY, label="Dự phòng cho vay")
    for i in range(2):
        ax.text(i - w / 2, bot[i] + 600, f"NPL {vn(aq.npl_pct[i], 2)}%\nnhóm 2–5: {vn(bot[i])}", ha="center", fontsize=7.4)
        ax.text(i + w / 2, aq.du_phong[i] + 600, f"{vn(aq.du_phong[i])}\nbao phủ {aq.bao_phu_pct[i]}%", ha="center", fontsize=7.4, color=NAVY)
    ax.set_xticks(xi, aq.moc); ax.set_ylabel("tỷ đồng"); ax.yaxis.set_major_formatter(lambda v, p: vn(v)); ax.set_ylim(0, 38_000)
    ax.legend(fontsize=7, frameon=False, loc="upper left", ncol=2)
    ax.set_title("Nhóm 2 +85% và nhóm 3–4 gấp 4 lần, nhưng dự phòng vẫn gấp 2,4 lần nợ xấu")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_03_asset_quality", "Nguồn: BCTC hợp nhất Q3/2026, TM5–6 (số 31/12/2025 trình bày lại). Cho vay +8,5% từ đầu năm. Chưa xoá nợ bằng dự phòng trong 9T/2026.", aq)
    plt.close(fig)

    # 4. Nguồn vốn
    fd = pd.DataFrame({"nguon": ["Tiền gửi khách hàng", "Tiền gửi Kho bạc NN", "Giấy tờ có giá", "Vay NHNN"],
                       "d31_12_25": [1_672_535, 136_001, 27_101, 24_127], "d30_09_26": [1_781_703, 171_617, 47_392, 282]})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1, 2.3]})
    a1.bar([0, 1], [fd.d31_12_25[0] / 1e3, fd.d30_09_26[0] / 1e3], color=[LIGHT, NAVY], width=0.6)
    for i, v in enumerate([fd.d31_12_25[0], fd.d30_09_26[0]]):
        a1.text(i, v / 1e3 + 25, vn(v / 1e3, 0), ha="center", fontsize=7.5)
    a1.text(0.5, 1_950, "CASA 33,7% đến 31,8%", ha="center", fontsize=7.4, color=ACCENT, fontweight="bold")
    a1.set_xticks([0, 1], ["31/12/25", "30/09/26"], fontsize=7.5); a1.set_ylim(0, 2_100); a1.set_ylabel("nghìn tỷ đồng")
    a1.set_title("Tiền gửi KH +6,5%", fontsize=8.8)
    xi = np.arange(3); w = 0.38
    a2.bar(xi - w / 2, fd.d31_12_25[1:] / 1e3, w, color=LIGHT, label="31/12/2025")
    a2.bar(xi + w / 2, fd.d30_09_26[1:] / 1e3, w, color=NAVY, label="30/09/2026")
    for i in range(3):
        a2.text(i + w / 2, fd.d30_09_26[i + 1] / 1e3 + 4, vn(fd.d30_09_26[i + 1] / 1e3, 1), ha="center", fontsize=7.4)
        a2.text(i - w / 2, fd.d31_12_25[i + 1] / 1e3 + 4, vn(fd.d31_12_25[i + 1] / 1e3, 1), ha="center", fontsize=7.0, color="#666")
    a2.set_xticks(xi, ["Kho bạc NN\n(8,8% tổng tiền gửi)", "Giấy tờ có giá\n(chủ yếu CCTG)", "Vay NHNN"], fontsize=7.5)
    a2.set_ylim(0, 200); a2.legend(fontsize=7, frameon=False); a2.set_title("Bù bằng Kho bạc và CCTG — nguồn ngắn, đắt hơn", fontsize=8.8)
    fig.suptitle("Nguồn vốn vẫn rẻ, nhưng CASA giảm và phần tăng đến từ nguồn kém bền hơn", x=0.01, ha="left", fontsize=9.8, fontweight="bold")
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    save(fig, "fig_04_funding", "Nguồn: BCTC hợp nhất Q3/2026, TM9, TM11; CASA = tiền gửi không kỳ hạn / tiền gửi KH. Tỷ trọng Kho bạc = KBNN / (TG KH + KBNN).", fd)
    plt.close(fig)

    # 5. ROE lịch sử + mốc ROE bền
    yr = fin[fin.quarter.str.endswith("Q4") & (fin.quarter >= "2019Q4")].copy()
    yr["lab"] = yr.quarter.str[:4]
    last = fin[fin.quarter == "2026Q3"].iloc[0]
    xs = list(yr.lab) + ["9T/26*"]; ys = list(yr.ROE_Trailing * 100) + [16.65]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(range(len(xs)), ys, color=[LIGHT] * (len(xs) - 1) + [NAVY], width=0.62)
    for i, v in enumerate(ys):
        ax.text(i, v + 0.3, vn(v, 1), ha="center", fontsize=7.5)
    for v, s, c in ((16.0, "Mốc ROE bền cao 16,0%", GREEN), (14.6, "Tâm ROE bền 14,6%", NAVY), (13.2, "Mốc ROE bền thấp 13,2%", ACCENT), (13.5, "Ke 13,5%", "#555")):
        ax.axhline(v, color=c, lw=1.0, ls="--" if s.startswith("Ke") else "-", label=s)
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="upper right", ncol=2)
    ax.set_xticks(range(len(xs)), xs); ax.set_ylim(0, 30); ax.set_ylabel("ROE, %")
    ax.set_title("ROE giảm từ ≈24% về ≈16% khi vốn tích luỹ nhanh hơn lợi nhuận; tâm định giá dùng 14,6%")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_05_roe", f"Nguồn: tav2_bq.ticker_financial ROE_Trailing (quý 4 mỗi năm); *9T/26 = ROE lõi năm hoá tự tính (bỏ khoản một lần), BQ ghi {vn(last.ROE_Trailing * 100, 1)}% gồm khoản một lần.",
         pd.DataFrame({"nam": xs, "roe_pct": ys}))
    plt.close(fig)

    # 6. Giá trị theo ROE bền × Ke
    roes = np.linspace(0.12, 0.20, 81)
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    rows = []
    for ke, c, ls in ((0.125, GREEN, "--"), (0.135, NAVY, "-"), (0.145, ACCENT, "--")):
        vv = [val(r, ke) for r in roes]
        ax.plot(roes * 100, vv, color=c, ls=ls, lw=1.6, label=f"Ke {vn(ke * 100, 1)}%")
        rows += [(round(r, 4), ke, round(v)) for r, v in zip(roes, vv)]
    for r, v in ROE_ANCH.items():
        ax.plot(r, v, "o", color=NAVY, ms=6); ax.text(r, v - 3_300, vn(v / 1e3, 1) + "k", ha="center", fontsize=7.4, color=NAVY)
    ax.axhline(PX17, color=ACCENT, lw=1.2); ax.text(12.05, PX17 + 700, f"Giá 17/11: {vn(PX17)} (hàm ý ROE 18,2% ở Ke 13,5%)", fontsize=7.3, color=ACCENT)
    ax.axhline(PX20, color=ACCENT, lw=0.8, ls=":"); ax.text(12.05, PX20 - 2_300, f"Giá 20/11: {vn(PX20)}", fontsize=7, color=ACCENT)
    ax.axvline(16.65, color=GREY, lw=0.8, ls=":"); ax.text(16.7, 22_500, "ROE lõi 9T/26\n16,65%", fontsize=7, color="#555")
    ax.set_xlabel("ROE bền dài hạn, %"); ax.set_ylabel("đ/cp"); ax.yaxis.set_major_formatter(lambda v, p: vn(v))
    ax.set_ylim(18_000, 75_000); ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Mỗi 1 điểm % ROE bền đổi giá trị ≈4.700 đ/cp; giá hiện tại cần ROE ≈18%")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_06_roe_value", "Nguồn: P/B = (ROE − g)/(Ke − g), BVPS 30.359 đ (VCSH công ty mẹ 30/9/2026 / 8.355,7 triệu cp), g 7%. Chấm = ba mốc ROE bền.",
         pd.DataFrame(rows, columns=["roe", "ke", "dcp"]))
    plt.close(fig)

    # 7. Football field
    lo_pb, hi_pb = PEERS[0][2] * BVPS, PEERS[0][4] * BVPS
    px12 = px[px.time >= "2025-11-20"]
    ff = pd.DataFrame([
        ("3 kịch bản (xấu – tốt)", SCEN["Xấu"][0], SCEN["Tốt"][0], SCEN["Cơ sở"][0]),
        ("Ke 13,5% ± 100bp (ROE 14,6%)", KE_SENS["+100bp"], KE_SENS["-100bp"], SCEN["Cơ sở"][0]),
        ("Ba mốc ROE bền 13,2–16,0%", ROE_ANCH[13.2], ROE_ANCH[16.0], ROE_ANCH[14.6]),
        ("Hai giai đoạn (Ke 13,5% – 12,5%)", TWO_STAGE[0], TWO_STAGE[1], None),
        ("Ke 12% theo beta thực tế 0,84", KE_BETA_REAL - 300, KE_BETA_REAL + 300, None),
        ("P/B lịch sử 5 năm của VCB (P10–P90)", lo_pb, hi_pb, PEERS[0][3] * BVPS),
        ("Giá 12 tháng (đóng cửa)", float(px12.Close.min()), float(px12.Close.max()), None)],
        columns=["phuong_phap", "thap", "cao", "giua"])
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        c = NAVY if i < 5 else GREY
        ax.barh(yy, r.cao - r.thap, left=r.thap, color=c, height=0.5, alpha=0.9)
        ax.text(r.thap - 700, yy, vn(r.thap / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(r.cao + 700, yy, vn(r.cao / 1e3, 1), ha="left", va="center", fontsize=7.3)
        if r.giua == r.giua and r.giua is not None:
            ax.plot(r.giua, yy, "|", color="white", ms=13, mew=2)
    ax.set_yticks(range(len(ff)), ff.phuong_phap[::-1], fontsize=7.6)
    ax.axvspan(KE_SENS["+100bp"], KE_SENS["-100bp"], color=LIGHT, alpha=0.35, lw=0)
    ax.axvline(PX17, color=ACCENT, lw=1.3, label=f"Giá 17/11: {vn(PX17)}")
    ax.axvline(PX20, color=ACCENT, lw=1.0, ls=":", label=f"Giá 20/11: {vn(PX20)}")
    ax.axvline(WEIGHTED, color=GREEN, lw=1.1, ls="--", label=f"Có trọng số: {vn(WEIGHTED)}")
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="upper right")
    ax.set_xlim(15_000, 112_000); ax.xaxis.set_major_formatter(lambda v, p: f"{v / 1e3:.0f}k")
    ax.set_xlabel("đ/cp (số cp hiện hành, trước ngày giao dịch không hưởng quyền cổ tức tiền)")
    ax.set_title("Mô hình nội tại dưới giá thị trường; P/B lịch sử cao hơn")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_football_field", "Nguồn: mô hình của nhóm nghiên cứu (ước lượng); P/B lịch sử tav2_bq.ticker 17/11/2021–17/11/2026 × BVPS 30.359 (chỉ đối chiếu, không dùng để định giá). Vạch trắng = tâm/trung vị.", ff)
    plt.close(fig)

    # 8. P/B so với lịch sử 5 năm — nhóm ngân hàng lớn
    pdf_ = pd.DataFrame(PEERS, columns=["ma", "pb_17_11", "p10", "trung_vi", "p90"])
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for i, r in pdf_.iterrows():
        ax.plot([i, i], [r.p10, r.p90], color=LIGHT, lw=7, solid_capstyle="butt")
        ax.plot(i, r.trung_vi, "_", color=GREY, ms=14, mew=2)
        ax.plot(i, r.pb_17_11, "o", color=ACCENT if r.ma == "VCB" else NAVY, ms=7)
        ax.text(i + 0.14, r.pb_17_11, vn(r.pb_17_11, 2), fontsize=7.2, va="center")
    ax.set_xticks(range(len(pdf_)), pdf_.ma); ax.set_ylabel("P/B (lần)")
    ax.plot([], [], "o", color=NAVY, label="P/B 17/11/2026"); ax.plot([], [], color=LIGHT, lw=7, label="P10–P90 5 năm"); ax.plot([], [], "_", color=GREY, ms=12, mew=2, label="Trung vị 5 năm")
    ax.legend(fontsize=7, frameon=False, loc="upper right", ncol=3)
    ax.set_ylim(0.5, 3.7)
    ax.set_title("VCB ở đáy P/B 5 năm của chính nó nhưng vẫn cao nhất nhóm, trừ STB; nén P/B là chung ngành")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_08_pb_peers", "Nguồn: tav2_bq.ticker cột PB, point-in-time theo ngày, 17/11/2021–17/11/2026 (1.246 phiên/mã). Chỉ mô tả, không dùng làm cơ sở định giá.", pdf_)
    plt.close(fig)

    # 9. Giá 12 tháng
    p = px[px.time >= "2025-11-20"].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.6), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(p.time, p.Close, color=NAVY, lw=1.3)
    for d, v in (("2026-11-17", PX17), ("2026-11-20", PX20)):
        a1.plot(pd.Timestamp(d), v, "o", color=ACCENT, ms=4)
    a1.axhspan(KE_SENS["+100bp"], KE_SENS["-100bp"], color=LIGHT, alpha=0.5, lw=0)
    a1.text(p.time.iloc[5], (KE_SENS["+100bp"] + KE_SENS["-100bp"]) / 2, "Vùng giá trị hợp lý 30,8–42,0k (Ke 13,5% ± 100bp)", fontsize=7, color="#333", va="center")
    for d, s in (("2026-04-24", "ĐHĐCĐ 2026"), ("2026-06-03", "Hợp nhất công ty con mới"), ("2026-10-30", "BCTC Q3")):
        a1.axvline(pd.Timestamp(d), color=GREY, lw=0.8, ls=":"); a1.text(pd.Timestamp(d), p.Close.max() * 1.01, " " + s, fontsize=6.6, color="#444", ha="left" if d.startswith("2026-06") else "right")
    a1.set_ylabel("đ/cp (điều chỉnh)"); a1.yaxis.set_major_formatter(lambda v, p_: vn(v)); a1.set_ylim(25_000, p.Close.max() * 1.06)
    a2.bar(p.time, p.Volume / 1e6, color=GREY, width=1.0); a2.set_ylabel("KL, triệu cp")
    a1.set_title(f"Giá 12 tháng trong khoảng {vn(p.Close.min() / 1e3, 1)}–{vn(p.Close.max() / 1e3, 1)}k, luôn trên vùng giá trị hợp lý")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_09_price_12m", "Nguồn: tav2_bq.ticker (Close điều chỉnh, Volume) 20/11/2025–20/11/2026; 20/11 khớp DNSE latest_trade. Mốc sự kiện: BCTC Q3/2026 (TM8), báo chí ĐHĐCĐ.",
         p[["time", "Close", "Volume"]])
    plt.close(fig)

    # 10. Cổ tức tiền và giá trị sau ngày GDKHQ
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(0, SCEN["Cơ sở"][0], color=NAVY, width=0.55)
    ax.bar(1, DIV_HAIRCUT, bottom=VAL_POST, color=GREY, width=0.55)
    ax.bar(2, VAL_POST, color=NAVY, width=0.55)
    ax.bar(3, VAL_POST, color=NAVY, width=0.55); ax.bar(3, DIV_CASH, bottom=VAL_POST, color=GREEN, width=0.55)
    for i, (y, s) in enumerate(((SCEN["Cơ sở"][0], vn(SCEN["Cơ sở"][0])), (SCEN["Cơ sở"][0], "−" + vn(DIV_HAIRCUT)), (VAL_POST, vn(VAL_POST)), (VAL_TOTAL, vn(VAL_TOTAL)))):
        ax.text(i, y + 500, s, ha="center", fontsize=8.4, fontweight="bold")
    ax.set_xticks(range(4), ["Tâm trước GDKHQ", "Giảm do chi cổ tức\n(1,169 × 2.433)", "Giá trị/cp sau GDKHQ", "Sau GDKHQ + tiền\ncổ tức 2.433 nhận về"], fontsize=7.6)
    ax.set_ylim(0, 41_000); ax.set_ylabel("đ/cp"); ax.yaxis.set_major_formatter(lambda v, p_: vn(v))
    ax.set_title("Cổ tức tiền 2.433 đ/cp: giá trị/cp giảm ≈2.850 đ sau GDKHQ; tổng cho cổ đông gần như giữ nguyên")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_10_dividend", "Nguồn: cổ tức từ LN 2025 = 20.331 tỷ / 8.355,7 triệu cp (báo chí ĐHĐCĐ 24/4/2026, chưa đối chiếu nghị quyết gốc; hình thức tiền/cổ phiếu chưa chốt). Giá trị/cp = P/B 1,169 × (BVPS − cổ tức).",
         pd.DataFrame({"buoc": ["tam", "giam", "sau_gdkhq", "tong_co_dong"], "dcp": [SCEN["Cơ sở"][0], -DIV_HAIRCUT, VAL_POST, VAL_TOTAL]}))
    plt.close(fig)

    # 11. Độ nhạy theo lãi huy động 12T
    rs = pd.DataFrame({"delta": ["−100bp", "−50bp", "0", "+50bp", "+100bp"], "beta1": list(KE_SENS.values()),
                       "beta05": [BETA05["-100bp"], None, SCEN["Cơ sở"][0], None, BETA05["+100bp"]]})
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    xi = np.arange(5)
    ax.bar(xi, rs.beta1, color=[GREEN, GREEN, NAVY, ACCENT, ACCENT], width=0.55)
    for i, v in enumerate(rs.beta1):
        ax.text(i, v + 500, vn(v), ha="center", fontsize=8, fontweight="bold")
    ax.axhline(PX17, color=ACCENT, lw=1.0); ax.text(-0.3, PX17 + 600, f"Giá 17/11: {vn(PX17)}", fontsize=7.2, color=ACCENT)
    ax.set_xticks(xi, [f"{d}\n(r {vn(13.5 + k * 0.5, 1)}%)" for d, k in zip(rs.delta, (-2, -1, 0, 1, 2))], fontsize=7.6)
    ax.set_ylim(0, 58_000); ax.set_ylabel("đ/cp"); ax.yaxis.set_major_formatter(lambda v, p_: vn(v))
    ax.set_title("Lãi huy động 12 tháng giảm 1 điểm % nâng tâm lên 42.000 — vẫn dưới giá")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_11_rate_sens", "Nguồn: mô hình của nhóm nghiên cứu; r 13,5% neo theo lãi huy động 12 tháng hiệu dụng 7,40% (CCTG 12T, 02/11/2026), truyền dẫn 1:1. Truyền dẫn 0,5: −100bp 38.455 / +100bp 32.961.", rs)
    plt.close(fig)

    # 12. Ma trận rủi ro
    rk = pd.DataFrame([
        ("#1", "Nợ nhóm 2 chuyển xuống nợ xấu", 3, 4), ("#2", "Chỉ đạo giảm lãi cho vay ép NIM", 4, 3),
        ("#3", "Kho bạc rút tiền / quy chế mới", 3, 2), ("#4", "Hỗ trợ ngân hàng chuyển giao", 2, 3),
        ("#5", "Basel III / D-SIB pha loãng ROE", 2, 3), ("#6", "Bảo lãnh ngoại bảng tăng nhanh", 2, 3),
        ("#7", "Cung cổ phiếu ngân hàng lớn", 3, 2)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.2)); ax = fig.add_axes([0.11, 0.2, 0.40, 0.70])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"#4": (-0.25, 0.2), "#5": (0.0, -0.2), "#6": (0.25, 0.2), "#3": (-0.2, 0.0), "#7": (0.2, 0.0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r.ma, (0, 0))
        ax.plot(r.xac_suat_1_5 + dx, r.tac_dong_1_5 + dy, "o", color=ACCENT if r.xac_suat_1_5 * r.tac_dong_1_5 >= 12 else NAVY, ms=9)
        ax.text(r.xac_suat_1_5 + dx + 0.1, r.tac_dong_1_5 + dy + 0.12, r.ma, fontsize=7.6, fontweight="bold")
    fig.text(0.55, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk.ma, rk.rui_ro)), fontsize=7.6, va="top", ha="left", linespacing=1.8)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.4)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.4)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Chi phí tín dụng và NIM là hai biến lớn nhất")
    save(fig, "fig_12_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 17/11/2026.", rk)
    plt.close(fig)

    # 13. Sản phẩm / mô hình kinh doanh: ảnh thẻ (website) + sơ đồ minh hoạ
    card = Image.open(os.path.join(SRC, "web_visa.jpg")).convert("RGB")
    cw, ch = card.size
    card = card.crop((int(cw * 0.55), int(ch * 0.22), int(cw * 0.87), int(ch * 0.74)))
    fig = plt.figure(figsize=(7.2, 2.9))
    a0 = fig.add_axes([0.0, 0.12, 0.38, 0.76]); a0.imshow(card); a0.axis("off")
    a0.set_title("Thẻ và thanh toán bán lẻ", fontsize=8.8, loc="left")
    a0.text(0.0, -0.06, "Ảnh: website Vietcombank (thẻ Visa ghi nợ)", transform=a0.transAxes, fontsize=6.5, color="#666")
    a1 = fig.add_axes([0.40, 0.08, 0.60, 0.80]); a1.axis("off"); a1.set_xlim(0, 10); a1.set_ylim(0, 6)
    a1.set_title("Mô hình kinh doanh (sơ đồ minh hoạ)", fontsize=8.8, loc="left")
    box = lambda x, y, t, c: a1.text(x, y, t, ha="center", va="center", fontsize=7.2, color="white", bbox=dict(boxstyle="round,pad=0.45", fc=c, ec="none"))
    box(1.6, 4.9, "Tiền gửi khách hàng\n1.782 nghìn tỷ\nCASA 31,8%", NAVY)
    box(1.6, 3.0, "Tiền gửi Kho bạc\n171,6 nghìn tỷ", GREY)
    box(1.6, 1.2, "Giấy tờ có giá\n47,4 nghìn tỷ", GREY)
    box(5.0, 3.0, "Vietcombank\nNPL 0,71%\nbao phủ 243%", GREEN)
    box(8.4, 4.6, "Cho vay\n(bán buôn + bán lẻ)", NAVY)
    box(8.4, 2.9, "Ngoại hối, thanh toán\nquốc tế", NAVY)
    box(8.4, 1.2, "Dịch vụ, thẻ", NAVY)
    for y in (4.9, 3.0, 1.2):
        a1.annotate("", (4.0, 3.0), (2.9, y), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9))
    for y in (4.6, 2.9, 1.2):
        a1.annotate("", (7.0, y), (6.0, 3.0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9))
    save(fig, "fig_13_products", "Nguồn: ảnh website vietcombank.com.vn (tải 22/11/2026); số liệu BCTC hợp nhất Q3/2026 (30/9/2026). Sơ đồ do nhóm nghiên cứu vẽ, chỉ minh hoạ.",
         pd.DataFrame({"khoi": ["TG KH", "KBNN", "GTCG"], "nghin_ty": [1_781.7, 171.6, 47.4]}))
    plt.close(fig)

    # 14. Ghép 2 bản đồ khu vực
    m1 = Image.open(os.path.join(FIGS, "fig_map_hn.png")).convert("RGB")
    m2 = Image.open(os.path.join(FIGS, "fig_map_hcm.png")).convert("RGB")
    hh = 1300
    m1 = m1.resize((int(m1.width * hh / m1.height), hh)); m2 = m2.resize((int(m2.width * hh / m2.height), hh))
    canvas = Image.new("RGB", (m1.width + m2.width + 30, hh), "white")
    canvas.paste(m1, (0, 0)); canvas.paste(m2, (m1.width + 30, 0))
    canvas.save(os.path.join(FIGS, "fig_14_map.png"))
    pd.concat([pd.read_csv(os.path.join(FIGS, f)) for f in ("fig_map_hn_points.csv", "fig_map_hcm_points.csv")]).to_csv(os.path.join(FIGS, "fig_14_map.csv"), index=False)
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
BREAK_BEFORE = ("1.", "3.", "7.", "Phụ lục A")


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
        if m and len(m.group(1)) == 1:   # h1 đã nằm trong ảnh banner -> bỏ trong PDF
            i += 1; continue
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
    md = "![](figs/title_banner.png)\n\n" + md   # banner đầu trang 1 PDF; email truyền --banner riêng
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
        page.insert_text((42, 34), "VCB — Ngân hàng TMCP Ngoại thương Việt Nam · Báo cáo Due Diligence · 22/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, STEM + ".md"), os.path.join(HERE, STEM + ".pdf"))
