"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư POW (18/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/): fin_quarterly_bq.csv (tav2_bq.ticker_financial POW 2022Q1–2026Q3), price_raw.csv (tav2_bq.ticker POW đến 17/11/2026),
  map_south_points.csv / map_north_points.csv (toạ độ OSM; bản đồ dựng bằng make_map.py), src/photo_*.jpg (ảnh trích BCTN 2025),
  src/logo.png (pvpower.vn). Số BCTC/định giá: REPORT.md (DD đã phản biện) + model/calc_output_rev2.txt. Mỗi hình kèm CSV.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX_CLOSE, PX_LIVE = 13_250, 13_500      # đóng cửa 17/11 (BQ) ; DNSE latest_trade 18/11/2026 11:29:50
TAM, TAM_PRE = 9_792, 9_891
ZONE = (7_166, 12_419)
SCEN = {"Xấu (25%)": 7_166, "Cơ sở (50%)": 9_792, "Tốt (25%)": 12_419}
# Kết quả hoạt động (tỷ đồng) — BCTC hợp nhất Q3/2026
NP_PARENT_9T = {"9T/2025": 1_856.8, "9T/2026": 6_434.5}
CORE_LO, CORE_HI = 3_980, 4_063      # LNST mẹ cốt lõi 9T/26 (ước lượng)
ROE_PARENT = [("2019", 9.3), ("2020", 7.8), ("2021", 6.1), ("2022", 6.3), ("2023", 3.4), ("2024", 3.5), ("2025", 7.1)]
OUTPUT_9T = [("Vũng Áng 1 (than)", 5_709), ("Cà Mau 1&2 (khí)", 4_245), ("Nhơn Trạch 3&4 (LNG)", 3_757),
             ("Nhơn Trạch 2 (khí)", 3_184), ("Nhơn Trạch 1 (khí)", 1_014)]
OUTPUT_TOTAL = 18_954
BS = {"Tiền + tiền gửi HTM": (19_473.0, 30_157.7), "Vay (ngắn + dài hạn)": (28_887.1, 37_525.4),
      "Phải thu KH ngắn hạn": (14_197.0, 23_964.3), "Nợ ròng thật": (9_414.1, 7_367.7)}


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
    from PIL import Image, ImageDraw, ImageFont
    plt = setup_mpl()
    fin = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    lo12, hi12 = float(px["Close"].min()), float(px["Close"].max())

    # 0. Hero: ảnh nhà máy (BCTN 2025) + thanh định giá
    im = Image.open(os.path.join(SRC, "photo_NhonTrach.jpg")).convert("RGB")
    w, h = im.size
    im = im.crop((0, int(h * 0.22), w, int(h * 0.74)))
    fig = plt.figure(figsize=(7.2, 3.7))
    a0 = fig.add_axes([0.0, 0.50, 1.0, 0.50]); a0.imshow(im, aspect="auto"); a0.axis("off")
    a0.text(0.012, 0.93, "Cụm điện khí/LNG Nhơn Trạch (Đồng Nai)", transform=a0.transAxes, fontsize=9.6,
            color="white", fontweight="bold", va="top", bbox=dict(facecolor=NAVY, alpha=0.85, lw=0, pad=4))
    a0.text(0.988, 0.04, "Ảnh: BCTN 2025 của công ty", transform=a0.transAxes, fontsize=6.5, color="white", ha="right",
            bbox=dict(facecolor="black", alpha=0.35, lw=0, pad=1.5))
    a1 = fig.add_axes([0.06, 0.20, 0.90, 0.13]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xlim(5_500, 15_500); a1.set_ylim(0, 1)
    a1.barh(0.5, ZONE[1] - ZONE[0], left=ZONE[0], height=0.55, color=LIGHT)
    a1.plot([TAM] * 2, [0.18, 0.82], color=NAVY, lw=2.4)
    a1.plot([PX_LIVE] * 2, [0.05, 0.95], color=ACCENT, lw=2.4)
    a1.text(TAM, 1.05, f"Tâm giá trị {vn(TAM/1e3,2)}k", ha="center", fontsize=7.8, color=NAVY, fontweight="bold")
    a1.text(PX_LIVE, 1.05, f"Giá {vn(PX_LIVE/1e3,1)}k", ha="center", fontsize=7.8, color=ACCENT, fontweight="bold")
    a1.text(ZONE[0], -0.55, vn(ZONE[0]) + " (xấu)", ha="center", fontsize=7.2, color="#444")
    a1.text(ZONE[1], -0.55, vn(ZONE[1]) + " (tốt)", ha="center", fontsize=7.2, color="#444")
    a1.set_xticks([])
    fig.text(0.06, 0.43, "Giá nằm trên vùng giá trị hợp lý (1,38 × tâm) · LNST mẹ 9T/26: 6.434 tỷ (+247%) · ~40% LNTT là hồi tố một lần",
             fontsize=7.8, color="#222")
    save(fig, "fig_00_hero", "Nguồn: ảnh BCTN 2025 (công ty); giá DNSE 18/11/2026 11:29 = 13.500 (tham chiếu 13.250); giá trị: mô hình thu nhập thặng dư của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia_dnse_18_11", "dong_cua_17_11", "tam_sau_CK", "vung_thap", "vung_cao"],
                       "dcp": [PX_LIVE, PX_CLOSE, TAM, ZONE[0], ZONE[1]]}))
    plt.close(fig)

    # 1. Phân rã LNST mẹ 9T
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(0, NP_PARENT_9T["9T/2025"], color=GREY, width=0.5)
    ax.bar(1, CORE_LO, color=NAVY, width=0.5, label="Cốt lõi (ước lượng 3.980–4.063)")
    ax.bar(1, CORE_HI - CORE_LO, bottom=CORE_LO, color="#6F88AD", width=0.5)
    ax.bar(1, NP_PARENT_9T["9T/2026"] - CORE_HI, bottom=CORE_HI, color=ACCENT, width=0.5, label="Hồi tố / hoàn nhập một lần (ước lượng ≈2.371–2.454)")
    ax.text(0, NP_PARENT_9T["9T/2025"] + 90, vn(NP_PARENT_9T["9T/2025"]), ha="center", fontsize=8)
    ax.text(1, NP_PARENT_9T["9T/2026"] + 90, vn(NP_PARENT_9T["9T/2026"]), ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks([0, 1], ["9T/2025", "9T/2026"]); ax.set_ylabel("LNST công ty mẹ, tỷ đồng"); ax.set_ylim(0, 8600); ax.set_xlim(-0.6, 1.6)
    ax.legend(fontsize=7.4, frameon=False, loc="upper left")
    ax.set_title("LNST mẹ 9T/26 tăng 247%, nhưng gần 40% đến từ khoản hồi tố một lần")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_np_split", "Nguồn: BCTC hợp nhất Q3/2026 (LNST mẹ 6.434,5; 9T/25 1.856,8); CBTT 03/08/2026 (hồi tố H1) và giải trình Q3. Tách cốt lõi = LNST mẹ − một lần×(1−10,9%): ước lượng của nhóm nghiên cứu.",
         pd.DataFrame({"muc": ["9T25", "cot_loi_thap", "cot_loi_cao", "9T26"], "ty_dong": [1856.8, CORE_LO, CORE_HI, 6434.5]}))
    plt.close(fig)

    # 2. LNST mẹ theo quý (BQ)
    fin["lab"] = fin["quarter"].map(lambda q: q[4:] + "/" + q[2:4])
    sub = fin[fin["quarter"] >= "2023Q1"].reset_index(drop=True)
    npq = sub["NP_P0"] / 1e9
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    x = np.arange(len(sub))
    ax.bar(x, npq, color=np.where(sub["quarter"].isin(["2026Q2", "2026Q3"]), ACCENT, NAVY), width=0.68)
    for i, v in enumerate(npq):
        ax.text(i, v + 50, vn(v), ha="center", fontsize=6.9, color="#333")
    ax.set_xticks(x, sub["lab"], fontsize=7); ax.set_ylabel("LNST công ty mẹ, tỷ đồng")
    ax.set_title("Q2–Q3/26 (cam) vượt xa mọi quý trước, Q2 gồm phần lớn khoản hồi tố")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_02_np_quarterly", "Nguồn: tav2_bq.ticker_financial NP_P0 (khớp BCTC Q3/26 và Q3/25; Q2/26 trên BQ 3.518,6 vs 3.375,3 suy từ BCTC lũy kế — lệch 143,3). Cột cam: Q2, Q3/2026.",
         pd.DataFrame({"quarter": sub["quarter"], "np_parent_ty": npq}))
    plt.close(fig)

    # 3. Bốn ảnh nhà máy (BCTN) — khung sản phẩm
    items = [("photo_VA1.jpg", "Vũng Áng 1 · 1.200 MW · than (Hà Tĩnh)"), ("photo_CaMau.jpg", "Cà Mau 1&2 · 1.500 MW · khí (Cà Mau)"),
             ("photo_NhonTrach.jpg", "Nhơn Trạch 1/2/3/4 · khí & LNG (Đồng Nai)"), ("photo_HuaNa.jpg", "Thuỷ điện Hủa Na · 180 MW (Nghệ An)")]
    tw, gap, cw = 1440, 16, 712
    th = 420
    canvas = Image.new("RGB", (tw, 2 * (th + 44) + 40), "white")
    d = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(FONT_B, 20); fr = ImageFont.truetype(FONT, 14)
    for k, (fn, cap) in enumerate(items):
        a = Image.open(os.path.join(SRC, fn)).convert("RGB")
        sc = max(cw / a.width, th / a.height)
        a = a.resize((int(a.width * sc) + 1, int(a.height * sc) + 1))
        l, t = (a.width - cw) // 2, (a.height - th) // 2
        a = a.crop((l, t, l + cw, t + th))
        x0, y0 = (k % 2) * (cw + gap), (k // 2) * (th + 44)
        canvas.paste(a, (x0, y0)); d.rectangle([x0, y0, x0 + cw - 1, y0 + th - 1], outline="#9AA5B1")
        d.text((x0 + 4, y0 + th + 8), cap, font=fb, fill="#1F3A5F")
    d.text((2, 2 * (th + 44) + 8), "Ảnh: BCTN 2025 của PV Power (trích từ PDF công bố); ảnh cắt gọn. Công suất theo BCTN 2025.", font=fr, fill="#666")
    canvas.save(os.path.join(FIGS, "fig_04_photos.png"))
    pd.DataFrame({"anh": [c for _, c in items], "nguon": "BCTN 2025 PV Power"}).to_csv(os.path.join(FIGS, "fig_04_photos.csv"), index=False)

    # 5. Sản lượng 9T theo nhà máy
    out = pd.DataFrame(OUTPUT_9T, columns=["nha_may", "san_luong_trkWh"])
    rest = OUTPUT_TOTAL - out["san_luong_trkWh"].sum()
    out.loc[len(out)] = ["Khác (thuỷ điện, NLTT… = hiệu số)", rest]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    y = np.arange(len(out))[::-1]
    cols = [NAVY, NAVY, ACCENT, NAVY, NAVY, GREY]
    ax.barh(y, out["san_luong_trkWh"], color=cols, height=0.6)
    for yy, v in zip(y, out["san_luong_trkWh"]):
        ax.text(v + 80, yy, vn(v), va="center", fontsize=7.8)
    ax.set_yticks(y, out["nha_may"], fontsize=7.8); ax.set_xlim(0, 7000); ax.set_xlabel("triệu kWh, 9T/2026")
    ax.set_title("Sản lượng 9T/26: 18.954 triệu kWh (+41%), Nhơn Trạch 3&4 đóng góp 3.757")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_05_output", "Nguồn: CBTT 13/10/2026 (sản lượng 9T theo nhà máy; tổng 18.954). 'Khác' = hiệu số, nhóm nghiên cứu tính (ước lượng). CBTT 10/11 và hội thảo 12/11 dùng định nghĩa khác (14.955 / 19.329), không cộng được.", out)
    plt.close(fig)

    # 6. Bảng cân đối: 1/1/26 vs 30/9/26 + CFO vs LNST
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.5, 1]})
    k = list(BS); xi = np.arange(len(k)); w = 0.38
    ax.bar(xi - w / 2, [BS[i][0] for i in k], w, color=GREY, label="01/01/2026")
    ax.bar(xi + w / 2, [BS[i][1] for i in k], w, color=NAVY, label="30/09/2026")
    for i, kk in enumerate(k):
        ax.text(i - w / 2, BS[kk][0] + 500, vn(BS[kk][0]), ha="center", fontsize=6.6)
        ax.text(i + w / 2, BS[kk][1] + 500, vn(BS[kk][1]), ha="center", fontsize=6.6, color=NAVY, fontweight="bold")
    ax.set_xticks(xi, [s.replace(" (", "\n(").replace(" + ", "\n+ ").replace(" KH ", "\nKH ") for s in k], fontsize=6.8)
    ax.set_ylim(0, 44_000); ax.set_ylabel("tỷ đồng"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("Nợ ròng giảm, nhưng phải thu +9.767 tỷ")
    xs = np.arange(2); w2 = 0.38
    bx.bar(xs - w2 / 2, [2_182.0, 6_898.6], w2, color=LIGHT, label="LNST hợp nhất")
    bx.bar(xs + w2 / 2, [3_414.0, 2_739.0], w2, color=NAVY, label="Dòng tiền kinh doanh (CFO)")
    for i, (a, b) in enumerate([(2_182.0, 3_414.0), (6_898.6, 2_739.0)]):
        bx.text(i - w2 / 2, a + 150, vn(a), ha="center", fontsize=7); bx.text(i + w2 / 2, b + 150, vn(b), ha="center", fontsize=7, color=NAVY, fontweight="bold")
    bx.set_xticks(xs, ["9T/2025", "9T/2026"]); bx.set_ylim(0, 10_500); bx.legend(fontsize=6.8, frameon=False, loc="upper left")
    bx.set_title("Lãi chưa thành tiền")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_06_balance_cfo", "Nguồn: BCTC hợp nhất Q3/2026 (bảng cân đối 30/9/26 và 1/1/26; LCTT 9T). Nợ ròng thật = vay − tiền − tiền gửi giữ đến đáo hạn. Phải thu KH ngắn hạn gồm EPTC/EVN 23.879,9. CFO 9T/25 theo BCTC Q3/2025.",
         pd.DataFrame({"chi_tieu": k, "01_01_2026": [BS[i][0] for i in k], "30_09_2026": [BS[i][1] for i in k]}))
    plt.close(fig)

    # 7. ROE lịch sử vs Ke vs ngầm định
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    yrs = [a for a, _ in ROE_PARENT] + ["2026 (9T, cốt lõi, cuối kỳ)"]
    vals = [b for _, b in ROE_PARENT] + [12.5]
    ax.bar(range(len(yrs)), vals, color=[NAVY] * 7 + [ACCENT], width=0.62)
    for i, v in enumerate(vals):
        if i < 7:
            ax.text(i, v + 0.3, vn(v, 1) + "%", ha="center", fontsize=7.4)
        else:
            ax.text(i, v - 2.2, "12,3–\n12,6%", ha="center", fontsize=7.4, color="white", fontweight="bold")
    ax.axhline(13.5, color=GREEN, ls="--", lw=1.2); ax.text(-0.4, 15.3, "Chi phí vốn r = 13,5% (đường nét đứt)", fontsize=7.4, color=GREEN)
    ax.axhline(12.9, color=ACCENT, ls=":", lw=1.2); ax.text(-0.4, 14.2, "ROE di sản giá thị trường hàm ý: 12,9% (giá 13.500; đường chấm)", fontsize=7.2, color=ACCENT)
    ax.set_xticks(range(len(yrs)), [y.replace(" (", "\n(") for y in yrs], fontsize=7.2); ax.set_ylim(0, 17); ax.set_ylabel("ROE trên VCSH công ty mẹ, %")
    ax.set_title("ROE 2019–2025 trung bình 6,2%; giá hàm ý ROE di sản ~12,9% vĩnh viễn")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_roe", "Nguồn: tav2_bq.ticker_financial (LNST mẹ ÷ VCSH mẹ, nhóm nghiên cứu tính lại); 2026: LNST mẹ cốt lõi năm hoá 5.307–5.417 ÷ VCSH mẹ cuối kỳ (ước lượng). ROE hàm ý: mô hình, giải ngược từ giá (12,6% tại 13.250; 12,9% tại 13.500).",
         pd.DataFrame({"nam": yrs, "roe_pct": vals}))
    plt.close(fig)

    # 8. Football field
    ff = pd.DataFrame([
        ("Mô hình: 3 kịch bản ROE di sản (xấu–tốt)", ZONE[0], ZONE[1], TAM),
        ("ROE cả 3 kịch bản −2 đến +2 điểm %", 8_291, 11_293, None),
        ("Lãi huy động ±100 điểm cơ bản", 9_378, 10_272, None),
        ("g từ −2% đến +4% (chỉ độ nhạy)", 8_054, 10_325, None),
        ("Vốn chủ NT3&4 7.000–10.000 tỷ", 9_529, 9_924, None),
        ("r 11–12% (utility, độ nhạy) đến cận lạc quan chồng", 10_543, 11_443, None),
        ("P/E 7–9 × EPS chuẩn hoá 1.335 (ước lượng)", 7 * 1_335, 9 * 1_335, None),
        ("P/B 0,8–1,0 × BVPS mẹ 14.060 (trung vị peer 0,97)", 0.8 * 14_060, 1.0 * 14_060, None),
        ("Nền ngắn (LN trung vị 12 quý, chỉ hiển thị)", 3_487, 3_487, None),
        ("Giá 12 tháng (điều chỉnh)", lo12, hi12, None)], columns=["phuong_phap", "thap", "cao", "tam"])
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        col = NAVY if i < 6 else (GREY if i < 9 else LIGHT)
        wd = max(r["cao"] - r["thap"], 90)
        ax.barh(yy, wd, left=r["thap"] if r["cao"] > r["thap"] else r["thap"] - 45, color=col, height=0.52)
        if r["cao"] > r["thap"]:
            ax.text(r["thap"] - 120, yy, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.2)
        ax.text(r["cao"] + 120, yy, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.2)
    ax.axvline(TAM, color=NAVY, ls="--", lw=1.1, label="Tâm giá trị 9,79k (sau chiết khấu thanh khoản 1%)")
    ax.axvline(PX_LIVE, color=ACCENT, ls="-", lw=1.4, label="Giá 13,5k (DNSE 18/11/2026 11:29)")
    ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.35, -0.13), ncol=2)
    ax.set_xlim(2_000, 16_000); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_xlabel("đồng/cổ phiếu", fontsize=7.6)
    ax.set_title("Mô hình: giá trên vùng giá trị; bội số peer: giá gần hợp lý")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_08_football_field", "Nguồn: mô hình thu nhập thặng dư của nhóm nghiên cứu (ước lượng; model/calc_output_rev2.txt); trung vị P/B 10 peer điện/khí 0,97 (tav2_bq.ticker 17/11/2026); EPS chuẩn hoá 1.335 là ước lượng; giá 12T tav2_bq.ticker.", ff)
    plt.close(fig)

    # 9. Ma trận rủi ro
    rk = pd.DataFrame([
        ("A", "EVN chậm thu 23.880 tỷ / trích lập", 3, 4), ("B", "Hồi tố đảo chiều / không lặp lại", 3, 4),
        ("C", "Qc – take-or-pay LNG NT3&4 bất lợi", 3, 4), ("D", "Giá LNG giao ngay cao kéo dài", 3, 3),
        ("E", "Lợi nhuận về mức lịch sử khi hết El Niño", 4, 4), ("F", "Quyết toán NT3&4 ghi giảm tài sản", 2, 3),
        ("G", "Lãi huy động tăng 100 điểm cơ bản", 2, 2), ("H", "Giao dịch bên liên quan / quản trị", 2, 2)],
        columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.11, 0.27, 0.42, 0.64])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"A": (-0.3, 0.2), "B": (0.3, 0.2), "C": (0.0, -0.22), "G": (-0.25, 0), "H": (0.25, 0), "D": (0, 0), "E": (0, 0), "F": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs[r["ma"]]
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 10 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.13, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    fig.text(0.57, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.75)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7.2)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–36 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Phải thu EVN, hồi tố và điều khoản LNG quyết định chất lượng lợi nhuận")
    save(fig, "fig_09_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 18/11/2026.", rk)
    plt.close(fig)
    print("12m Close", lo12, hi12)


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
BREAK_BEFORE = ("7.",)


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
        page.insert_text((42, 34), "POW — PV Power · Báo cáo Due Diligence · 18/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
        pdf(os.path.join(HERE, "POW_DD_investor_report_20261118.md"), os.path.join(HERE, "POW_DD_investor_report_20261118.pdf"))
