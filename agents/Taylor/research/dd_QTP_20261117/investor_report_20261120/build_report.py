"""Tái lập biểu đồ + PDF cho báo cáo DD nhà đầu tư QTP (dữ liệu tới BCTC Q3/2026, giá đóng cửa 19/11/2026).

Chạy:  /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
Đầu vào (figs/):
  model_numbers.json    — extract_model_numbers.py (trích từ qtp_model_r3c.py, md5 6d80cb978eb340fec7c9c26eaf0ec2a5)
  price_raw.csv         — tav2_bq.ticker (QTP Close/Price/Volume, 03/11/2025–16/11/2026)
  fig_01..07 (+CSV), fig_03_map, fig_map_points.csv — giữ nguyên từ bộ hình nền (BCTC/BQ, không đổi).
Ảnh: src/web_banner1.jpg, src/logo.png (website công ty tpcquangninh.com.vn).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
SRC = os.path.join(HERE, "src")
STEM = "QTP_DD_investor_report_20261120"

NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 10_200                 # đóng cửa 19/11/2026
LIQ = 0.10
FV_POST, FV_PRE = 7_701, 8_557
SINGLE = (6_315, 8_894)     # biến thể đơn lẻ, sau CK
COMBO = (5_887, 9_240)      # kết hợp bất lợi / thuận lợi, sau CK
EPS_N = 1_257


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
    plt = setup_mpl()
    M = json.load(open(os.path.join(FIGS, "model_numbers.json")))
    assert round(M["center_post"]) == FV_POST and round(M["center_pre"]) == FV_PRE, "tâm lệch mô hình"
    PP = {k: v * (1 - LIQ) for k, v in M["P_pure_pre"].items()}
    px = pd.read_csv(os.path.join(FIGS, "price_raw.csv"), parse_dates=["time"])
    px = px[px["time"] >= "2025-11-17"].reset_index(drop=True)
    lo12, hi12 = float(px["Close"].min()), float(px["Close"].max())

    # 0. Hero: ảnh nhà máy + thanh định giá
    from PIL import Image
    im = Image.open(os.path.join(SRC, "web_banner1.jpg")).convert("RGB")
    w, h = im.size
    im = im.crop((int(w * 0.18), 0, int(w * 0.78), h))
    fig = plt.figure(figsize=(7.2, 3.9))
    a0 = fig.add_axes([0.0, 0.52, 1.0, 0.48]); a0.imshow(im, aspect="auto"); a0.axis("off")
    a0.text(0.012, 0.93, "Nhà máy Nhiệt điện Quảng Ninh · 4 tổ máy · 1.200 MW", transform=a0.transAxes, fontsize=10.5,
            color="white", fontweight="bold", va="top", bbox=dict(facecolor=NAVY, alpha=0.82, lw=0, pad=4))
    a0.text(0.988, 0.04, "Ảnh: website công ty", transform=a0.transAxes, fontsize=6.5, color="white", ha="right",
            bbox=dict(facecolor="black", alpha=0.35, lw=0, pad=1.5))
    a1 = fig.add_axes([0.05, 0.19, 0.90, 0.14]); a1.grid(False)
    for s in ("left", "top", "right"):
        a1.spines[s].set_visible(False)
    a1.set_yticks([]); a1.set_xlim(2_500, 14_500); a1.set_ylim(0, 1); a1.set_xticks([])
    a1.barh(0.5, COMBO[1] - COMBO[0], left=COMBO[0], height=0.42, color="#EEF1F4")
    a1.barh(0.5, SINGLE[1] - SINGLE[0], left=SINGLE[0], height=0.62, color=LIGHT)
    a1.plot([FV_POST] * 2, [0.15, 0.85], color=NAVY, lw=2.6)
    a1.plot([PX] * 2, [0.02, 0.98], color=ACCENT, lw=2.6)
    for k, lab in (("P0", "Không bù"), ("P100", "Bù đủ")):
        a1.plot(PP[k], 0.5, "D", color=GREY, ms=6)
        a1.text(PP[k], -0.62, f"{lab}\n{vn(PP[k] / 1e3, 1)}k", ha="center", fontsize=6.9, color="#555")
    a1.text(FV_POST, 1.06, f"Tâm giá trị {vn(FV_POST / 1e3, 1)}k", ha="center", fontsize=7.6, color=NAVY, fontweight="bold")
    a1.text(PX + 120, 1.06, f"Giá {vn(PX / 1e3, 1)}k (19/11)", ha="left", fontsize=7.6, color=ACCENT, fontweight="bold")
    a1.text((SINGLE[0] + SINGLE[1]) / 2, -0.62, f"Vùng giá trị hợp lý {vn(SINGLE[0] / 1e3, 1)}–{vn(SINGLE[1] / 1e3, 1)}k",
            ha="center", fontsize=6.9, color="#333")
    fig.text(0.05, 0.43, "Vay 0 · tiền ròng 1.541 tỷ (3.425 đ/cp) · dự án khí thải 3.485 tỷ + vận hành ~572 tỷ/năm từ ~2030 · giá trị sau chiết khấu thanh khoản 10%",
             fontsize=7.2, color="#222")
    save(fig, "fig_00_hero", "Nguồn: ảnh nhà máy từ website công ty (tpcquangninh.com.vn); giá đóng cửa 19/11/2026; giá trị: mô hình DCF vòng đời hữu hạn của nhóm nghiên cứu (ước lượng).",
         pd.DataFrame({"muc": ["gia", "tam_sau_CK", "vung_don_le_thap", "vung_don_le_cao", "ket_hop_thap", "ket_hop_cao", "P0_thuan", "P100_thuan"],
                       "dcp": [PX, FV_POST, SINGLE[0], SINGLE[1], COMBO[0], COMBO[1], round(PP["P0"]), round(PP["P100"])]}))
    plt.close(fig)

    # 10. Giá trị theo 3 kịch bản bù giá (sau CK)
    lab = {"P0": "Không bù\n(xác suất 0,40)", "P50": "Bù một phần\n(0,36)", "P100": "Bù đủ\n(0,24)"}
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xs = np.arange(3); vals = [PP[k] for k in ("P0", "P50", "P100")]
    ax.bar(xs, vals, color=[ACCENT, GREY, GREEN], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 250, vn(v), ha="center", fontsize=8.4, fontweight="bold")
    ax.axhline(PX, color=ACCENT, lw=1.4, ls="-"); ax.text(1.0, PX + 250, f"Giá {vn(PX)} (19/11)", fontsize=7.5, color=ACCENT, ha="center")
    ax.axhline(FV_POST, color=NAVY, lw=1.2, ls="--"); ax.text(-0.42, FV_POST + 200, f"Giá trị có trọng số {vn(FV_POST)}", fontsize=7.5, color=NAVY)
    ax.set_xticks(xs, [lab[k] for k in ("P0", "P50", "P100")], fontsize=8); ax.set_ylim(0, 15_000)
    ax.set_ylabel("đ/cp, sau chiết khấu thanh khoản")
    ax.set_title("Giá hiện tại chỉ được biện minh nếu chi phí khí thải được bù gần như chắc chắn")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_10_scenarios", "Nguồn: mô hình DCF của nhóm nghiên cứu (ước lượng); mỗi cột = trung bình có trọng số ba kịch bản vận hành nền (0,25/0,65/0,10). Xác suất bù giá là nhận định, chưa có tiền lệ đo được.",
         pd.DataFrame({"kich_ban": list(PP), "dcp_sau_CK": [round(v) for v in PP.values()], "xac_suat": [0.40, 0.36, 0.24]}))
    plt.close(fig)

    # 11. Dòng tiền toàn công ty + tiền ròng (kịch bản vận hành cơ sở)
    cf = {p: pd.DataFrame(M["cf"][p]) for p in M["cf"]}
    p0 = cf["P0"]; p0n = p0[p0.dps == 0].set_index("y"); p0d = p0[p0.dps == 900].set_index("y")
    p50d = cf["P50"][cf["P50"].dps == 900].set_index("y"); p100d = cf["P100"][cf["P100"].dps == 900].set_index("y")
    yrs = [y for y in p0n.index if y <= 2042]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    tot = p0n.loc[yrs, "total"]
    ax.bar(yrs, tot, color=np.where(tot < 0, ACCENT, GREY), width=0.7, label="Dòng tiền vốn chủ toàn công ty, không bù (tỷ/năm)")
    ax.plot(yrs, p0n.loc[yrs, "cash"], color=NAVY, lw=1.8, label="Tiền ròng: không bù, không chia cổ tức")
    ax.plot(yrs, p0d.loc[yrs, "cash"], color=ACCENT, lw=1.8, ls="--", label="Tiền ròng: không bù, cổ tức 900 đ/cp")
    ax.plot(yrs, p50d.loc[yrs, "cash"], color=GREY, lw=1.6, ls=":", label="Tiền ròng: bù một phần, cổ tức 900 đ/cp")
    ax.plot(yrs, p100d.loc[yrs, "cash"], color=GREEN, lw=1.6, ls="-.", label="Tiền ròng: bù đủ, cổ tức 900 đ/cp")
    ax.axhline(0, color="#333", lw=0.8)
    ax.axvspan(2026.5, 2029.5, color="#EEF1F4", lw=0, zorder=0); ax.text(2028, 4_300, "xây dựng", ha="center", fontsize=7.2, color="#555")
    ax.set_ylim(-4_000, 4_800); ax.set_xticks(yrs[::2]); ax.set_xlim(2026.4, 2042.6); ax.set_ylabel("tỷ đồng")
    ax.legend(fontsize=6.6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    ax.set_title("Không được bù: dòng tiền âm từ 2030, cổ tức 900 đ đẩy tiền ròng xuống dưới 0 từ 2032")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    df = p0n.loc[yrs, ["fcfe_base", "dfcfe", "total", "cash"]].rename(columns={"cash": "tien_rong_P0_khong_co_tuc"})
    df["tien_rong_P0_co_tuc_900"] = p0d.loc[yrs, "cash"]; df["tien_rong_P50_co_tuc_900"] = p50d.loc[yrs, "cash"]
    df["tien_rong_P100_co_tuc_900"] = p100d.loc[yrs, "cash"]
    save(fig, "fig_11_cashflow", "Nguồn: mô hình của nhóm nghiên cứu (ước lượng), kịch bản vận hành cơ sở; tiền ròng đầu kỳ 1.541 tỷ (30/9/2026, sau tạm ứng cổ tức). Lãi vay 9%, trả gốc 10 năm, giải ngân 30/45/25% 2027–29: ước lượng.",
         df.reset_index())
    plt.close(fig)

    # 8. Football field
    W = M["wgrid_post"]; R = M["rate"]
    ff = pd.DataFrame([
        ("Biến thể giả định đơn lẻ (tâm 7,7k)", SINGLE[0], SINGLE[1]),
        ("Biến thể kết hợp (bất lợi – thuận lợi)", COMBO[0], COMBO[1]),
        ("Xác suất không bù 0,6 – 0,2", W["0.6"], W["0.2"]),
        ("Lãi huy động ±100 điểm cơ bản", R["100"] * (1 - LIQ), R["-100"] * (1 - LIQ)),
        ("Từng kịch bản: không bù – bù đủ", PP["P0"], PP["P100"]),
        ("P/E 7–9 × EPS 1.257 (chưa tính dự án)", 7 * EPS_N, 9 * EPS_N),
        ("Vùng giá 12 tháng", lo12, hi12)], columns=["phuong_phap", "thap", "cao"])
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        col = NAVY if i < 4 else (GREY if i < 6 else LIGHT)
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=col, height=0.52)
        ax.text(r["thap"] - 150, yy, vn(r["thap"] / 1e3, 1), ha="right", va="center", fontsize=7.3)
        ax.text(r["cao"] + 150, yy, vn(r["cao"] / 1e3, 1), ha="left", va="center", fontsize=7.3)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.6)
    ax.axvline(FV_POST, color=NAVY, ls="--", lw=1.1, label="Tâm giá trị 7,7k (sau chiết khấu thanh khoản)")
    ax.axvline(PX, color=ACCENT, ls="-", lw=1.4, label="Giá 10,2k (19/11/2026)")
    ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.35, -0.2), ncol=2)
    ax.set_xlim(1_500, 15_000); ax.set_xlabel("đồng/cổ phiếu · DCF: sau chiết khấu thanh khoản 10%; bội số: chưa chiết khấu", fontsize=7.6)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v / 1e3:.0f}k")
    ax.set_title("Giá nằm trên mọi biến thể; chỉ kịch bản bù đủ và bội số vượt giá")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_08_football_field", "Nguồn: mô hình DCF vòng đời hữu hạn của nhóm nghiên cứu (ước lượng); P/E peer điện 7–9 (16/11/2026); giá 12 tháng 17/11/2025–16/11/2026.", ff.round(0))
    plt.close(fig)

    # 9. Ma trận rủi ro (nhận định)
    rk = pd.DataFrame([
        ("#1", "Chi phí khí thải không được bù vào giá điện", 3, 5), ("#2", "Bù giá chậm sau ngày vận hành", 3, 4),
        ("#3", "Dự án vượt dự toán / chậm tiến độ", 2, 3), ("#4", "Cổ tức giảm từ 2030 nếu không bù", 3, 3),
        ("#5", "Giá cố định PPA giảm sâu hơn khấu hao", 3, 3), ("#6", "EVN trả chậm, phải thu kéo dài", 3, 3),
        ("#7", "El Niño qua, sản lượng H2/27 giảm", 4, 2), ("#8", "Vòng đời ngắn hơn 2047", 1, 4)],
        columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.11, 0.27, 0.42, 0.64])
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 12 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"#4": (-0.25, 0.22), "#5": (0.0, -0.22), "#6": (0.25, 0.22)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 12 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    fig.text(0.57, 0.86, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.75)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất\nthấp", "Thấp", "TB", "Cao", "Rất\ncao"], fontsize=7.2)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–48 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("Cơ chế bù chi phí khí thải quyết định phần lớn giá trị")
    save(fig, "fig_09_risk_matrix", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan).", rk)
    plt.close(fig)
    print("12m lo/hi", lo12, hi12)
    print(ff.round(0).to_string())


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
BREAK_BEFORE = ("1.", "4.", "5.", "7.", "9.", "Phụ lục A")


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
        page.insert_text((42, 34), "QTP — CTCP Nhiệt điện Quảng Ninh · Báo cáo Due Diligence · 20/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
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
