"""Dựng biểu đồ + PDF cho báo cáo DD nhà đầu tư VLB (dữ liệu tới BCTC Q3/2026; giá đóng cửa 20/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Nguồn số: ../REPORT.md + ../model/output_r2.txt (model/dcf_vlb.py md5 93e0ec77a0cc97bd8b48af98249e0939).
Đầu vào figs/: fin_quarterly_bq.csv (tav2_bq.ticker_financial VLB 2022Q1–2026Q3), price_raw.csv (= model/px_vlb.csv, tav2_bq.ticker),
fig_map_mines.png / fig_map_market.png (make_map.py, điểm ở fig_map_*_points.csv), title_banner.png (make_title_banner.py).
Ảnh: src/ (website bbcc.com.vn, tải 22/11/2026). Mỗi hình ghi kèm CSV (figs/fig_XX_*.csv).
Cổ tức tạm ứng 2026 2.500 đ/cp, GDKHQ 19/11/2026, trả 17/12/2026 (vietstock 11/2026; khớp hệ số điều chỉnh Close/Price BQ 0,953 trước 19/11).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")
STEM = "VLB_DD_investor_report_20261122"

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

# ---- số dùng chung: model/output_r2.txt (khớp REPORT.md) ----
PX = 48_100                     # đóng cửa 20/11/2026 (đã không hưởng cổ tức 2.500 đ từ 19/11)
DIV = 2_500                     # tạm ứng cổ tức 2026, GDKHQ 19/11/2026
LIQ = 0.0298                    # chiết khấu thanh khoản Q = 5 tỷ
SCEN = {"Xấu": (35_836, 0.25), "Cơ sở": (53_604, 0.50), "Tốt": (67_885, 0.25)}   # trước CK, cơ sở 30/9/2026
W_PRE, W_POST = 52_732, 51_163
RATE = {"−100bp": 55_019, "−50bp": 53_851, "0": 52_732, "+50bp": 51_659, "+100bp": 50_629}
ZONE_LO, ZONE_HI = 43_489, 58_838          # 0,85–1,15 × tâm sau CK (cơ sở 30/9)
FUND_LO_CENTER = 52_304
NONE_BASE, LIFE17_BASE = 48_933, 56_981
NET_CASH, OFFSET_PV = 488.8, 119.4
SH = 46.72056


def ex(v):          # cùng cơ sở với giá: trừ cổ tức 2.500 đ đã tách khỏi giá từ 19/11
    return v - DIV


W_POST_EX = round((W_PRE - DIV) * (1 - LIQ))
ZONE_LO_EX, ZONE_HI_EX = round(0.85 * W_POST_EX), round(1.15 * W_POST_EX)


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
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()
    ok = lambda a, b, t=5: abs(a - b) <= t
    assert ok(sum(v * p for v, p in SCEN.values()), W_PRE, 1)
    assert ok(W_PRE * (1 - LIQ), W_POST)
    assert ok(0.85 * W_POST, ZONE_LO) and ok(1.15 * W_POST, ZONE_HI)
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    assert float(px.loc[px.time == "2026-11-20", "Price"].iloc[0]) == PX
    r = px.loc[px.time == "2026-11-18"].iloc[0]
    print(f"Close/Price 18/11 = {r.Close / r.Price:.4f} (≈ (P−2.500)/P = {(r.Price - DIV) / r.Price:.4f})")
    print(f"tâm sau CK, cùng cơ sở không hưởng cổ tức: {W_POST_EX} ; vùng {ZONE_LO_EX}–{ZONE_HI_EX}; giá/tâm {PX / W_POST_EX:.3f} ; theo cơ sở 30/9 {PX / W_POST:.3f}")

    # 0. HERO: ảnh trụ sở + đá thành phẩm (website) + thanh định giá
    hq = Image.open(os.path.join(SRC, "632962312813871_1053.7121906508x400.jpg")).convert("RGB")
    st = Image.open(os.path.join(SRC, "4x6-3873.jpg")).convert("RGB")
    hq = hq.crop((int(hq.width * 0.18), 0, int(hq.width * 0.82), hq.height))
    fig = plt.figure(figsize=(7.2, 3.9))
    a0 = fig.add_axes([0.0, 0.50, 0.64, 0.50]); a0.imshow(hq, aspect="auto"); a0.axis("off")
    a2 = fig.add_axes([0.645, 0.50, 0.355, 0.50]); a2.imshow(st, aspect="auto"); a2.axis("off")
    a0.text(0.015, 0.93, "Đá xây dựng Đồng Nai · không vay · phải thu ≈ 0 · biên gộp 9T 33,0%", transform=a0.transAxes,
            fontsize=8.8, color="white", fontweight="bold", va="top", bbox=dict(facecolor=NAVY, alpha=0.88, lw=0, pad=4))
    a2.text(0.97, 0.04, "Ảnh: website công ty (trụ sở; đá 4×6)", transform=a2.transAxes, fontsize=6.3, color="white", ha="right",
            bbox=dict(facecolor="black", alpha=0.4, lw=0, pad=1.5))
    a1 = fig.add_axes([0.05, 0.17, 0.90, 0.15]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xlim(28_000, 72_000); a1.set_ylim(0, 1); a1.set_xticks([])
    xs, ts = ex(SCEN["Xấu"][0]), ex(SCEN["Tốt"][0])
    a1.barh(0.5, ts - xs, left=xs, height=0.42, color="#EEF1F4")
    a1.barh(0.5, ZONE_HI_EX - ZONE_LO_EX, left=ZONE_LO_EX, height=0.62, color=LIGHT)
    a1.plot([W_POST_EX] * 2, [0.15, 0.85], color=NAVY, lw=2.6)
    a1.plot([PX] * 2, [0.02, 0.98], color=ACCENT, lw=2.6)
    for k, v in (("Xấu", xs), ("Tốt", ts)):
        a1.plot(v, 0.5, "D", color=GREY, ms=6)
        a1.text(v, -0.62, f"{k}\n{vn(v / 1e3, 1)}k", ha="center", fontsize=6.9, color="#555")
    a1.text(W_POST_EX + 500, 1.06, f"Tâm {vn(W_POST_EX / 1e3, 1)}k", ha="left", fontsize=7.6, color=NAVY, fontweight="bold")
    a1.text(PX - 500, 1.06, f"Giá {vn(PX / 1e3, 1)}k (20/11)", ha="right", fontsize=7.4, color=ACCENT, fontweight="bold")
    a1.text(ZONE_LO_EX, -0.62, f"Vùng hợp lý\n{vn(ZONE_LO_EX / 1e3, 1)}–{vn(ZONE_HI_EX / 1e3, 1)}k", ha="center", fontsize=6.9, color="#333")
    fig.text(0.05, 0.41, "Giá trị/cp sau chiết khấu thanh khoản, cùng cơ sở với giá (đã trừ cổ tức tạm ứng 2.500 đ, giao dịch không hưởng quyền 19/11)",
             fontsize=7.0, color="#222")
    save(fig, "fig_00_hero", "Nguồn: ảnh website bbcc.com.vn; BCTC Q3/2026; giá đóng cửa UPCoM 20/11/2026; giá trị: mô hình của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia_20_11", "tam_sau_ck_khong_huong_co_tuc", "vung_thap", "vung_cao", "xau", "tot"],
                       "dong_cp": [PX, W_POST_EX, ZONE_LO_EX, ZONE_HI_EX, xs, ts]}))
    plt.close(fig)

    # 1. Doanh thu + LNST quý (tách khoản một lần Q2/26)
    q = pd.read_csv(os.path.join(FIGS, "fin_quarterly_bq.csv"))
    q["one_off"] = 0.0
    q.loc[q.quarter == "2026Q2", "one_off"] = round(343.93 * 0.8, 2)
    q["core"] = q.np_ty - q.one_off
    assert ok(q.loc[q.quarter == "2026Q3", "np_ty"].iloc[0], 117.41, 0.05)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1, 1]})
    x = range(len(q))
    ax.bar(x, q.rev_ty, color=[ACCENT if s.startswith("2026") else NAVY for s in q.quarter], width=0.7)
    ax.set_xticks(list(x)[::2], [s.replace("20", "", 1) for s in q.quarter][::2], fontsize=6.6, rotation=45)
    ax.set_title("Doanh thu quý: ≈440 tỷ, cao nhất lịch sử"); ax.set_ylabel("tỷ đồng")
    for i in (len(q) - 1, len(q) - 5):
        ax.text(i, q.rev_ty.iloc[i] + 6, vn(q.rev_ty.iloc[i]), ha="center", fontsize=6.8)
    bx.bar(x, q.core, color=NAVY, width=0.7, label="LNST lõi")
    bx.bar(x, q.one_off, bottom=q.core, color=LIGHT, width=0.7, label="Một lần: nộp thừa tiền cấp quyền (sau thuế)")
    bx.axhline(0, color="#555", lw=0.6)
    bx.set_xticks(list(x)[::2], [s.replace("20", "", 1) for s in q.quarter][::2], fontsize=6.6, rotation=45)
    bx.set_title("LNST quý: lõi Q3/26 117 tỷ (+86%)"); bx.set_ylim(-260, 420)
    for i in (len(q) - 1, len(q) - 5):
        bx.text(i, q.core.iloc[i] + 8, vn(q.core.iloc[i]), ha="center", fontsize=6.8)
    bx.text(q.index[q.quarter == "2022Q3"][0] + 0.3, -215, "Q3/22: nộp bổ sung\ntiền cấp quyền", fontsize=6.4, color="#555")
    bx.legend(fontsize=6.4, loc="upper left", frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_01_quarterly", "Nguồn: tav2_bq.ticker_financial (Revenue_P0, NP_P0) 2022Q1–2026Q3, khớp BCTC Q3/2026 [DT 442,08; LNST 117,41]. Khoản một lần = 343,93 tỷ × (1 − 20% thuế) ghi nhận Q2/2026 (BCTC Q3/2026 TM VI.6).", q)
    plt.close(fig)

    # 2. LNST năm: đỉnh lịch sử
    yr = pd.DataFrame({"nam": ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "TTM lõi\n9/2026"],
                       "lnst_ty": [149, 142, 131, 182, 161, -51, 143, 218, 301, 391.6]})
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.bar(yr.nam, yr.lnst_ty, color=[ACCENT if v < 0 else (GREEN if i == len(yr) - 1 else NAVY) for i, v in enumerate(yr.lnst_ty)], width=0.62)
    for i, v in enumerate(yr.lnst_ty):
        ax.text(i, v + (8 if v >= 0 else -28), vn(v), ha="center", fontsize=7.2)
    ax.axhline(143, color=GREY, ls="--", lw=1); ax.text(5.45, 160, "Trung vị 2017–2023: 143 tỷ", fontsize=6.8, color="#555")
    ax.set_ylim(-90, 440); ax.set_ylabel("tỷ đồng"); ax.tick_params(axis="x", labelsize=7)
    ax.set_title("Lợi nhuận lõi đang ở đỉnh lịch sử, gấp ≈2,7 lần trung vị 2017–2023")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_02_annual", "Nguồn: tav2_bq.ticker_financial (LNST năm); 2025 = 301,44 tỷ theo NQ ĐHĐCĐ (BCTC kiểm toán); TTM lõi = Q4/25 100,73 + 9T/26 lõi 290,83 (bỏ khoản một lần). 2022 lỗ do nộp bổ sung tiền cấp quyền.", yr)
    plt.close(fig)

    # 3. Cầu nối tiền gộp -> tiền ròng thật (waterfall)
    wf = pd.DataFrame([("Tiền + tiền gửi\ncó kỳ hạn", 812.59), ("Quỹ khen thưởng\nphúc lợi", -107.47), ("Thuế\nphải nộp", -61.75),
                       ("Giá vốn phần\nkhách ứng trước", -51.5), ("Vốn lưu\nđộng ròng", -67.1), ("Trích quỹ\ntạm 9T/26", -35.9)],
                      columns=["khoan", "ty"])
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    cum = 0
    for i, rr in wf.iterrows():
        b = cum if rr.ty < 0 else 0
        h = rr.ty if rr.ty > 0 else -rr.ty
        ax.bar(i, h, bottom=(cum + rr.ty) if rr.ty < 0 else 0, color=NAVY if rr.ty > 0 else ACCENT, width=0.6)
        ax.text(i, (cum if rr.ty < 0 else rr.ty) + 12, vn(rr.ty, 1), ha="center", fontsize=7.2)
        cum += rr.ty
    n = len(wf)
    ax.bar(n, cum, color=GREEN, width=0.6); ax.text(n, cum + 12, vn(cum, 1), ha="center", fontsize=7.6, fontweight="bold")
    assert ok(cum, NET_CASH, 0.2)
    ax.set_xticks(range(n + 1), list(wf.khoan) + ["Tiền ròng\nthật"], fontsize=6.8)
    ax.set_ylim(0, 900); ax.set_ylabel("tỷ đồng")
    ax.set_title("Tiền gộp 813 tỷ nhưng tiền ròng thuộc cổ đông ≈489 tỷ (≈10.460 đ/cp); vay = 0")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_03_net_cash", "Nguồn: BCTC Q3/2026 (bảng cân đối 30/9/2026, TM V.15, V.17, 23d). Trong đó 20,5 tỷ tiền gửi cầm cố bảo lãnh dự án. Tiền ròng chưa trừ cổ tức tạm ứng 2.500 đ/cp (≈117 tỷ) chốt sau ngày 30/9.", wf)
    plt.close(fig)

    # 4. Khoản bù trừ tiền cấp quyền: số dư giảm dần vs đời mỏ
    yrs = list(range(0, 18))
    bal = [max(329.36 - 19.42 * t, 0) for t in yrs]
    off = pd.DataFrame({"nam_thu": yrs, "so_du_ty": [round(b, 1) for b in bal]})
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.fill_between(yrs, bal, color=LIGHT); ax.plot(yrs, bal, color=NAVY, lw=1.6)
    for L, lab, c in ((11, "đời mỏ kịch bản xấu 11 năm", GREY), (14, "cơ sở 14 năm", NAVY), (16, "tốt 16 năm", GREEN)):
        ax.axvline(L, color=c, ls="--", lw=1); ax.text(L + 0.1, 300 - (L - 11) * 25, lab, fontsize=6.8, color=c)
    ax.text(1.0, 25, "còn ≈57 tỷ khi mỏ hết đời\n(hoàn lại hay không: chưa rõ)", fontsize=6.6, color="#555")
    ax.set_xlim(0, 17.5); ax.set_ylim(0, 350); ax.set_xlabel("năm kể từ 30/9/2026"); ax.set_ylabel("số dư, tỷ đồng")
    ax.set_title("344 tỷ là quyền bù trừ ≈19,4 tỷ/năm, không phải tiền mặt: giá trị hiện tại ≈119 tỷ (≈2.560 đ/cp)")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_04_offset", "Nguồn: BCTC Q3/2026 TM V.17, VI.6 (số dư 329,36 tỷ; cấn trừ 9T 14,57 tỷ, tức 19,4 tỷ/năm); BCTC bán niên 2026 TM 16. Giá trị hiện tại chiết khấu 13,5% trong đời mỏ cơ sở 14 năm (ước lượng).", off)
    plt.close(fig)

    # 5. Ảnh sản phẩm (website công ty)
    prods = [("1x2soklu-9791.jpg", "Đá 1×2", "cốt liệu bê tông, cầu, nhà"), ("4x6-3873.jpg", "Đá 4×6", "móng đường, nền công trình"),
             ("0x4-5772.jpg", "Đá 0×4 (cấp phối)", "lớp móng đường cao tốc"), ("datsanlap-4510.jpg", "Đất san lấp", "san nền dự án, KCN")]
    fig = plt.figure(figsize=(7.2, 2.3))
    for i, (f, t, d) in enumerate(prods):
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        w, h = im.size; tw = int(h * 1.35)
        if w > tw:
            im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
        a = fig.add_axes([0.01 + i * 0.2475, 0.27, 0.235, 0.62]); a.imshow(im); a.axis("off")
        a.set_title(t, fontsize=8.6, loc="left")
        a.text(0, -0.08, d, transform=a.transAxes, fontsize=6.9, color="#333", va="top")
    save(fig, "fig_05_products", "Ảnh: website công ty bbcc.com.vn (trang sản phẩm, tải 22/11/2026). Đá và đất chiếm 99,9% doanh thu 9T/2026 (BCTC Q3/2026, tr. 23).",
         pd.DataFrame({"san_pham": [p[1] for p in prods], "anh": [p[0] for p in prods], "cong_dung": [p[2] for p in prods]}))
    plt.close(fig)

    # 6. Ghép 2 bản đồ khu vực
    m1 = Image.open(os.path.join(FIGS, "fig_map_mines.png")).convert("RGB")
    m2 = Image.open(os.path.join(FIGS, "fig_map_market.png")).convert("RGB")
    hh = 1300
    m1 = m1.resize((int(m1.width * hh / m1.height), hh)); m2 = m2.resize((int(m2.width * hh / m2.height), hh))
    canvas = Image.new("RGB", (m1.width + m2.width + 30, hh), "white")
    canvas.paste(m1, (0, 0)); canvas.paste(m2, (m1.width + 30, 0))
    canvas.save(os.path.join(FIGS, "fig_06_map.png"))
    pd.concat([pd.read_csv(os.path.join(FIGS, f)) for f in ("fig_map_mines_points.csv", "fig_map_market_points.csv")]).to_csv(os.path.join(FIGS, "fig_06_map.csv"), index=False)

    # 7. Football field
    px12 = px[px.time >= "2025-11-20"]
    ff = pd.DataFrame([
        ("3 kịch bản xấu – tốt, trước CK (đời mỏ 11–16 năm)", ex(SCEN["Xấu"][0]), ex(SCEN["Tốt"][0]), ex(SCEN["Cơ sở"][0])),
        ("Vùng hợp lý: tâm ± 15% (sau CK thanh khoản)", ZONE_LO_EX, ZONE_HI_EX, W_POST_EX),
        ("Lãi huy động ± 100bp (sau CK)", round(ex(RATE["+100bp"]) * (1 - LIQ)), round(ex(RATE["−100bp"]) * (1 - LIQ)), W_POST_EX),
        ("Đời mỏ −3 … +3 năm (kịch bản cơ sở, trước CK)", ex(NONE_BASE), ex(LIFE17_BASE), ex(SCEN["Cơ sở"][0])),
        ("P/E 4,4–6,8x peer × EPS lõi 7.140 + tiền ròng", 4.4 * 7_137 + 10_463 - DIV, 6.8 * 7_137 + 10_463 - DIV, None),
        ("Giá 12 tháng (đóng cửa, điều chỉnh)", float(px12.Close.min()), float(px12.Close.max()), None)],
        columns=["phuong_phap", "thap", "cao", "giua"])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for i, rr in ff.iterrows():
        yy = len(ff) - 1 - i
        ax.barh(yy, rr.cao - rr.thap, left=rr.thap, color=NAVY if i < 4 else GREY, height=0.5, alpha=0.9)
        ax.text(rr.thap - 600, yy, vn(rr.thap / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(rr.cao + 600, yy, vn(rr.cao / 1e3, 1), ha="left", va="center", fontsize=7.3)
        if rr.giua == rr.giua and rr.giua is not None:
            ax.plot(rr.giua, yy, "|", color="white", ms=13, mew=2)
    ax.set_yticks(range(len(ff)), ff.phuong_phap[::-1], fontsize=7.4)
    ax.axvspan(ZONE_LO_EX, ZONE_HI_EX, color=LIGHT, alpha=0.35, lw=0)
    ax.axvline(PX, color=ACCENT, lw=1.4, label=f"Giá 20/11: {vn(PX)}")
    ax.axvline(W_POST_EX, color=GREEN, lw=1.1, ls="--", label=f"Tâm: {vn(W_POST_EX)}")
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(20_000, 80_000); ax.xaxis.set_major_formatter(lambda v, p: f"{v / 1e3:.0f}k")
    ax.set_xlabel("đ/cp, cùng cơ sở với giá (đã trừ cổ tức tạm ứng 2.500 đ)")
    ax.set_title("Giá 48.100 đ nằm sát tâm giá trị và trong mọi dải định giá")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_07_football_field", "Nguồn: mô hình của nhóm nghiên cứu (ước lượng); P/E peer tav2_bq 20/11/2026 (MVC 4,4x … KSB 6,8x), chỉ đối chiếu; giá tav2_bq.ticker 20/11/2025–20/11/2026. Vạch trắng = giữa dải.", ff)
    plt.close(fig)

    # 8. Độ nhạy lãi huy động + thanh khoản
    rs = pd.DataFrame({"lai_huy_dong": list(RATE.keys()), "truoc_ck": list(RATE.values())})
    rs["sau_ck_khong_huong_co_tuc"] = [round((v - DIV) * (1 - LIQ)) for v in rs.truoc_ck]
    lq = pd.DataFrame({"quy_mo": ["0,5 tỷ", "1 tỷ", "5 tỷ"], "chiet_khau_pct": [1.06, 1.43, 2.98], "phien_thoat": [2.2, 4.4, 21.8]})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw={"width_ratios": [1.3, 1]})
    ax.bar(rs.lai_huy_dong, rs.sau_ck_khong_huong_co_tuc, color=[GREEN, GREEN, NAVY, ACCENT, ACCENT], width=0.6)
    for i, v in enumerate(rs.sau_ck_khong_huong_co_tuc):
        ax.text(i, v + 400, vn(v), ha="center", fontsize=7)
    ax.axhline(PX, color=ACCENT, lw=1, ls=":"); ax.text(4.35, PX + 300, "giá", fontsize=6.8, color=ACCENT)
    ax.set_ylim(40_000, 56_000); ax.set_title("Lãi huy động ±100bp: tâm ±4%"); ax.set_xlabel("thay đổi lãi huy động 12T (r 13,5% điểm neo)")
    bx.bar(lq.quy_mo, lq.chiet_khau_pct, color=NAVY, width=0.55)
    for i, rr in lq.iterrows():
        bx.text(i, rr.chiet_khau_pct + 0.08, f"{vn(rr.chiet_khau_pct, 2)}%\n{vn(rr.phien_thoat, 1)} phiên", ha="center", fontsize=6.8)
    bx.set_ylim(0, 4); bx.set_title("Chiết khấu thanh khoản theo quy mô"); bx.set_xlabel("quy mô giao dịch")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_rate_liq", "Nguồn: mô hình của nhóm nghiên cứu; r 13,5% neo lãi huy động 12T hiệu dụng 7,4% (CCTG 12T, 18/11/2026), truyền dẫn 1:1. Thanh khoản: GTGD trung vị 250 phiên 1,14 tỷ/phiên; số phiên thoát ở 20% GTGD.", pd.concat([rs, lq], axis=1))
    plt.close(fig)

    # 9. Peer P/E, P/B
    pe = pd.DataFrame([("VLB*", round(PX / 7_137, 1), 1.90), ("NNC", 4.9, 1.6), ("DHA", 5.9, 1.57), ("MVC", 4.4, 0.88), ("KSB", 6.8, 0.48)],
                      columns=["ma", "pe", "pb"])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.4))
    for a, col, t in ((ax, "pe", "P/E (lần)"), (bx, "pb", "P/B (lần)")):
        a.bar(pe.ma, pe[col], color=[ACCENT if m.startswith("VLB") else NAVY for m in pe.ma], width=0.55)
        for i, v in enumerate(pe[col]):
            a.text(i, v + 0.08, vn(v, 2 if col == "pb" else 1), ha="center", fontsize=7.2)
        a.set_title(t); a.set_ylim(0, pe[col].max() * 1.18)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    save(fig, "fig_09_peers", "Nguồn: tav2_bq.ticker 20/11/2026 (P/E TTM, P/B). *VLB: P/E = giá 48.100 / EPS lõi TTM sau trích quỹ 7.137 đ (P/E BQ gồm khoản một lần 3,4x). KSB có mảng BĐS/KCN. Chỉ mô tả, không dùng làm mỏ neo định giá.", pe)
    plt.close(fig)

    # 10. Ma trận rủi ro
    rk = pd.DataFrame([
        ("#1", "Khoản bù trừ tiền cấp quyền bị xét lại", 2, 4), ("#2", "Giấy phép Tân Cang 1 / đời mỏ ngắn hơn", 3, 4),
        ("#3", "Sản lượng giảm khi Long Thành, VĐ3 xong", 3, 3), ("#4", "Khống chế giá bán đá tại mỏ", 1, 3),
        ("#5", "Rà soát giấy phép lan sang mỏ chủ lực", 2, 5), ("#6", "Thanh khoản cổ phiếu thấp", 4, 2)],
        columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.0)); ax = fig.add_axes([0.11, 0.2, 0.40, 0.70])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    for _, rr in rk.iterrows():
        ax.plot(rr.xac_suat_1_5, rr.tac_dong_1_5, "o", color=ACCENT if rr.xac_suat_1_5 * rr.tac_dong_1_5 >= 12 else NAVY, ms=9)
        ax.text(rr.xac_suat_1_5 + 0.12, rr.tac_dong_1_5 + 0.12, rr.ma, fontsize=7.6, fontweight="bold")
    fig.text(0.55, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk.ma, rk.rui_ro)), fontsize=7.6, va="top", ha="left", linespacing=1.8)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.4)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.4)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Giấy phép và tiền cấp quyền là hai biến lớn nhất")
    save(fig, "fig_10_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan), tham chiếu đọc ngành độc lập 22/11/2026.", rk)
    plt.close(fig)

    # 11. Chuỗi giá trị (sơ đồ minh hoạ)
    fig = plt.figure(figsize=(7.2, 1.9)); a1 = fig.add_axes([0, 0.12, 1, 0.80]); a1.axis("off"); a1.set_xlim(0, 12); a1.set_ylim(0, 3)
    box = lambda x, y, t, c: a1.text(x, y, t, ha="center", va="center", fontsize=7.2, color="white", bbox=dict(boxstyle="round,pad=0.45", fc=c, ec="none"))
    box(1.2, 1.5, "Mỏ đá Đồng Nai\n3 mỏ chủ lực\n≈5 tr m³/năm*", NAVY)
    box(4.0, 1.5, "Nổ mìn, nghiền,\nsàng phân loại\n(1×2, 4×6, 0×4…)", NAVY)
    box(7.0, 2.3, "Xe tải: TP.HCM,\nBiên Hòa, Long Thành", GREEN)
    box(7.0, 0.7, "Bến sà lan Thạnh Phú,\nThiện Tân: ĐBSCL", GREEN)
    box(10.4, 1.5, "Nhà thầu hạ tầng,\nKCN, bê tông\n(khách ứng tiền trước)", GREY)
    for a, b in (((2.3, 1.5), (2.8, 1.5)), ((5.2, 1.5), (5.8, 2.2)), ((5.2, 1.5), (5.6, 0.8)), ((8.3, 2.2), (9.1, 1.6)), ((8.5, 0.8), (9.1, 1.4))):
        a1.annotate("", b, a, arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9))
    save(fig, "fig_11_value_chain", "Sơ đồ minh hoạ do nhóm nghiên cứu vẽ. *Sản lượng khai thác suy từ phí bảo vệ môi trường 9T/2026 (ước lượng); bến thuỷ nội địa + băng tải Thạnh Phú theo BCTC Q3/2026 (tr. 17).",
         pd.DataFrame({"buoc": ["khai thác", "chế biến", "vận chuyển bộ", "sà lan", "khách hàng"]}))
    plt.close(fig)
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
BREAK_BEFORE = ("Phụ lục A",)


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
        page.insert_text((42, 34), "VLB — CTCP Xây dựng và Sản xuất VLXD Biên Hòa · Báo cáo Due Diligence · 22/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
