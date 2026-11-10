"""Dựng hình + PDF + HTML báo cáo DD VGS (10/11/2026).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I build_report.py figs ; python3 -I build_report.py pdf|html (pymupdf ở /tmp/pdflib)
Số: research/dd_VGS_20261110/{REPORT.md, SUMMARY.json, calc/model_out_r2.json}. Không số mới ngoài các số đó."""
import os, sys, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..")
FIGS = os.path.join(HERE, "figs")
NAVY, ACCENT, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2e7d5b"
SK = "/home/trido/.claude/skills/dd-investor-report"
FONT, FONT_B = SK + "/fonts/BeVietnamPro-Regular.ttf", SK + "/fonts/BeVietnamPro-Bold.ttf"
MD = "VGS_DD_investor_report_20261110"

def vn(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def setup():
    import matplotlib; matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B): fm.fontManager.addfont(f)
    plt.rcParams.update({"font.family": "Be Vietnam Pro", "font.size": 9, "axes.titlesize": 9.8, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#555",
        "figure.facecolor": "white", "savefig.facecolor": "white", "axes.grid": True, "grid.color": "#ECEFF2",
        "grid.linewidth": .8, "axes.axisbelow": True})
    return plt

def save(fig, name, source, rows=None, header=None):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.6, color="#666", ha="left", va="bottom")
    fig.savefig(f"{FIGS}/{name}.png", dpi=200)
    if rows is not None:
        with open(f"{FIGS}/{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)

def figs():
    import numpy as np
    plt = setup()
    S = json.load(open(f"{SRC}/SUMMARY.json")); M = json.load(open(f"{SRC}/calc/model_out_r2.json"))
    PX = S["price"]
    # 1 football field
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.barh([0], [34722 - 19393], left=[19393], color=LIGHT, height=.5)
    ax.plot([26526], [0], "D", color=NAVY, ms=8, zorder=5)
    ax.text(26526, .36, "Tâm 26.526", ha="center", fontsize=8, color=NAVY, fontweight="bold")
    ax.text(19393, -.42, "P10 19.393", ha="center", fontsize=7.5); ax.text(34722, -.42, "P90 34.722", ha="center", fontsize=7.5)
    ax.axvline(PX, color=ACCENT, lw=2); ax.text(PX + 250, 1.7, f"Giá 10/11: {vn(PX)}", color=ACCENT, fontsize=8.5, fontweight="bold", va="center")
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Vùng giá trị hợp lý\n(phân phối kịch bản)", "Các mốc độ nhạy"], fontsize=8)
    for v in (15033, 22765, 23379):
        ax.plot([v], [1], "o", color=GREY, ms=7)
    ax.annotate("Lõi + tiền ròng: 15.033", (15033, 1), (15033, 1.3), ha="center", fontsize=7.2)
    ax.annotate("Holding −30%: 22.765", (22765, 1), (21600, 1.3), ha="center", fontsize=7.2)
    ax.annotate("Liên kết 0,75×sổ (cả 3 KB): 23.379", (23379, 1), (28300, 1.0), ha="center", fontsize=7.2, va="center")
    ax.set_xlim(12000, 38000); ax.set_ylim(-.7, 1.9); ax.set_xlabel("đồng/cổ phiếu")
    ax.set_title("Giá 19.300 đ nằm sát cận dưới vùng giá trị hợp lý (nhãn mong manh)")
    fig.tight_layout(rect=(0, .1, 1, 1))
    save(fig, "fig_01_football_field", "Nguồn: nhóm nghiên cứu, mô hình SOTP khoá trước khi xem giá. Dải P10–P90 sau chiết khấu thanh khoản (cỡ minh hoạ 1 tỷ đ); các mốc độ nhạy là trước chiết khấu. Giá: 10/11/2026.",
         [("P10_sau_CK", 19393), ("tam_sau_CK", 26526), ("P90_sau_CK", 34722), ("gia_10/11", PX), ("lien_ket_0.75xso_3KB_truocCK", 23379),
          ("holding_-30%_truocCK", 22765), ("loi_cong_tien_rong", 15033)], ["muc", "dong_cp"])
    plt.close(fig)
    # 2 SOTP
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    parts = [("Lõi ống + tôn\ncán nguội", 15575, NAVY), ("Liên kết 28,6%\n(Tập đoàn SX Thép VĐ)", 6853, "#6b8fb5"),
             ("Dự án Legend City\n(vốn ròng, giá gốc)", 6524, "#6b8fb5"), ("Nợ ròng", -542, ACCENT)]
    cum = 0; lows = []
    for i, (l, v, c) in enumerate(parts):
        ax.bar(i, v, bottom=cum if v > 0 else cum + v, color=c, width=.6)
        ax.text(i, (cum + max(v, 0)) + 500, vn(v), ha="center", fontsize=8.5, fontweight="bold")
        lows.append((l.replace("\n", " "), v)); cum += v
    ax.bar(4, cum, color=GREEN, width=.6); ax.text(4, cum + 500, vn(cum), ha="center", fontsize=8.5, fontweight="bold")
    ax.axhline(PX, color=ACCENT, ls="--", lw=1.4); ax.text(-.45, PX + 450, f"Giá {vn(PX)}", color=ACCENT, ha="left", fontsize=8)
    ax.set_xticks(range(5), [p[0] for p in parts] + ["Tâm kịch bản cơ sở\n(trước CK)"], fontsize=7.4)
    ax.set_ylabel("đ/cổ phiếu"); ax.set_ylim(0, 31000)
    ax.set_title("Lõi ống thép + tiền ròng đáng 15.033 đ < giá; phần còn lại nằm ở liên kết và dự án đô thị")
    fig.tight_layout(rect=(0, .07, 1, 1))
    save(fig, "fig_02_sotp", "Nguồn: SOTP kịch bản cơ sở, r = 13,5% (mô hình SOTP khoá trước khi xem giá). Tâm kịch bản cơ sở 28.410; tâm có trọng số 26.778 (xem bảng kịch bản).",
         lows + [("tam_co_so_truoc_CK", cum)], ["khoi", "dong_cp"])
    plt.close(fig)
    # 3 PBT bridge Q3
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    items = [("Lãi liên kết", 26.2, ACCENT), ("EBIT lõi", 5.5, NAVY), ("Tài chính ròng", 2.8, NAVY), ("Khác (tính bù)", -0.6, GREY)]
    for i, (l, v, c) in enumerate(items):
        ax.bar(i, v, color=c, width=.55); ax.text(i, v + (1 if v > 0 else -2.6), f"{v:+.1f}".replace(".", ","), ha="center", fontsize=8.5, fontweight="bold")
    ax.bar(4, 33.9, color=GREEN, width=.55); ax.text(4, 34.9, "+33,9", ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(range(5), [i[0] for i in items] + ["Tăng LNTT\nQ3/26 so Q3/25"], fontsize=8); ax.set_ylabel("tỷ đồng"); ax.set_ylim(-5, 40)
    ax.set_title("77% phần tăng lợi nhuận trước thuế Q3/26 đến từ liên kết, không phải hoạt động ống thép")
    fig.tight_layout(rect=(0, .08, 1, 1))
    save(fig, "fig_03_pbt_bridge", "Nguồn: BCTC hợp nhất Q3/2026 (KQKD, TM). 'Khác' = 33,9 − (26,2 + 5,5 + 2,8), tính bù. Đơn vị: tỷ đồng.",
         [(l, v) for l, v, _ in items] + [("tong_tang_LNTT", 33.9)], ["khoan", "ty_dong"])
    plt.close(fig)
    # 4 gross margin 10Y + 5 CFO side by side
    h = list(csv.DictReader(open(f"{SRC}/calc/bq_vgs_hist.csv")))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.5, 1]})
    q = [r["quarter"] for r in h if r["gpm_ttm"]]; g = [float(r["gpm_ttm"]) * 100 for r in h if r["gpm_ttm"]]
    a1.plot(range(len(g)), g, color=NAVY, lw=1.8); a1.axhspan(2.3, 4.9, color=LIGHT, alpha=.5, lw=0)
    a1.set_xticks(range(0, len(q), 4), [x[2:4] + "Q" + x[-1] for x in q[::4]], fontsize=7)
    a1.plot(len(g) - 1, g[-1], "o", color=ACCENT); a1.text(len(g) - 1, g[-1] + .25, f"{g[-1]:.2f}%".replace(".", ","), color=ACCENT, ha="right", fontsize=8, fontweight="bold")
    a1.set_ylabel("Biên gộp 12T cuốn chiếu, %"); a1.set_title("Biên gộp mỏng 2–6% suốt 10 năm", fontsize=9)
    labs = ["2024", "2025", "9T/2026"]; cfo = [93.6, 440.7, 40.3]; npat = [109.9, 217.0, 199.3]
    x = np.arange(3); a2.bar(x - .18, npat, .36, color=LIGHT, label="LNST"); a2.bar(x + .18, cfo, .36, color=NAVY, label="Dòng tiền HĐKD")
    for i in range(3):
        a2.text(x[i] - .18, npat[i] + 8, vn(npat[i], 1), ha="center", fontsize=6.5); a2.text(x[i] + .18, cfo[i] + 8, vn(cfo[i], 1), ha="center", fontsize=6.5)
    a2.set_xticks(x, labs, fontsize=7.5); a2.legend(fontsize=6.8, frameon=False, loc="upper left"); a2.set_ylabel("tỷ đồng")
    a2.set_title("Dòng tiền lệch mạnh theo năm", fontsize=9)
    fig.tight_layout(rect=(0, .09, 1, 1))
    save(fig, "fig_04_margin_cfo", "Nguồn: tav2_bq.ticker_financial (biên gộp TTM, 2015Q1–2026Q3); BCTC hợp nhất 2025 kiểm toán và Q3/2026 (dòng tiền). Dải xám = 2,3–4,9% (cuối năm 2016–2025).",
         [(a, b, c) for a, b, c in zip(labs, npat, cfo)], ["ky", "LNST_ty", "CFO_ty"])
    plt.close(fig)
    # 6 sensitivity
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    sens = [("Lưới kịch bản (cơ sở)", 26778), ("Liên kết cơ sở = EPV + trọng số 0,45/0,45/0,10", 25600), ("Liên kết cơ sở = sổ sách", 25430),
            ("Liên kết cơ sở = 0,75 × sổ", 24911), ("Cả 3 kịch bản liên kết = 0,75 × sổ", 23379), ("Holding −30% (liên kết + dự án)", 22765)][::-1]
    ax.barh(range(len(sens)), [s[1] for s in sens], color=[ACCENT if "Holding" in s[0] else NAVY for s in sens], height=.6)
    for i, s in enumerate(sens): ax.text(s[1] + 150, i, vn(s[1]), va="center", fontsize=8)
    ax.axvline(PX, color=ACCENT, ls="--", lw=1.3); ax.text(PX + 100, len(sens) - .45, f"Giá {vn(PX)}", color=ACCENT, fontsize=8)
    ax.set_yticks(range(len(sens)), [s[0] for s in sens], fontsize=7.6); ax.set_xlim(15000, 30000); ax.set_xlabel("đ/cổ phiếu, trước chiết khấu thanh khoản")
    ax.set_title("Mọi cách định giá liên kết đều cho giá trị cao hơn giá 18–39%")
    fig.tight_layout(rect=(0, .07, 1, 1))
    save(fig, "fig_05_sensitivity", "Nguồn: mô hình SOTP của nhóm nghiên cứu. Trước chiết khấu thanh khoản.", sens, ["cach", "dong_cp"])
    plt.close(fig)
    # 7 price
    px = sorted(csv.DictReader(open(f"{SRC}/calc/px_vgs.csv")), key=lambda r: r["time"])
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    d = [r["time"][5:] for r in px]; p = [float(r["Close"]) for r in px]
    ax.plot(range(len(p)), p, color=NAVY, marker="o", ms=3.5); ax.set_xticks(range(len(d)), [x[3:] + "/" + x[:2] for x in d], fontsize=6.8, rotation=0)
    i = d.index("10-27"); ax.axvline(i, color=ACCENT, ls=":"); ax.text(i + .1, max(p), "27/10: công bố BCTC Q3", color=ACCENT, fontsize=7.5, va="top")
    ax.set_ylim(18000, 19700); ax.set_ylabel("đ/cổ phiếu")
    ax.set_title("Lợi nhuận Q3 +51% nhưng giá gần như không đổi sau công bố (18.800 sang 19.300)")
    fig.tight_layout(rect=(0, .07, 1, 1))
    save(fig, "fig_06_price", "Nguồn: tav2_bq.ticker (đóng cửa 21/10–10/11/2026; 15 phiên). Quan sát, không quy nhân quả.", [(r["time"], r["Close"]) for r in px], ["ngay", "dong_cua"])
    plt.close(fig)
    # 8 product panel
    from PIL import Image, ImageDraw, ImageFont
    names = [("Ong-thep-han-den", "Ống thép hàn đen"), ("Ong-thep-Ma-Kem-nhung-nong", "Ống mạ kẽm nhúng nóng"), ("Ong-ton-Ma-Kem", "Ống tôn mạ kẽm"), ("Ong-thep-co-lon", "Ống thép cỡ lớn")]
    th = 330; ims = []
    for f, _ in names:
        im = Image.open(f"{HERE}/src/{f}.png").convert("RGBA"); bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
        im = bg.convert("RGB"); ims.append(im.resize((int(im.width * th / im.height), th)))
    W = 1440; gap = 12; tot = sum(i.width for i in ims) + gap * 3; sc = (W - 3 * gap) / sum(i.width for i in ims)
    ims = [i.resize((int(i.width * sc), int(i.height * sc))) for i in ims]; hh = ims[0].height
    cv = Image.new("RGB", (W, hh + 70), "white"); dr = ImageDraw.Draw(cv); fb = ImageFont.truetype(FONT_B, 26); fr = ImageFont.truetype(FONT, 19)
    x = 0
    for im, (_, lab) in zip(ims, names):
        cv.paste(im, (x, 0)); dr.rectangle([x, 0, x + im.width - 1, hh - 1], outline="#C9D0D8"); dr.text((x + 6, hh + 6), lab, font=fb, fill=NAVY); x += im.width + gap
    dr.text((6, hh + 42), "Ảnh: website công ty (vgpipe.com.vn, mục Ống thép), truy cập 10/11/2026.", font=fr, fill="#666")
    cv.save(f"{FIGS}/fig_07_products.png")
    with open(f"{FIGS}/fig_07_products.csv", "w", encoding="utf-8") as f:
        f.write("anh,nguon\n" + "".join(f"{n},https://vgpipe.com.vn/wp-content/uploads/2024/07/{n}.png\n" for n, _ in names))
    # factory photo
    im = Image.open(f"{HERE}/src/IMG_4651-1-1-1-1-1726x607.jpg").convert("RGB"); im = im.resize((1440, int(im.height * 1440 / im.width)))
    dr = ImageDraw.Draw(im); dr.rectangle([0, im.height - 34, 1440, im.height], fill=(255, 255, 255)); dr.text((8, im.height - 28), "Ảnh: Nhà máy VG PIPE, KCN Bình Xuyên (website thepvietduc.com.vn, truy cập 10/11/2026).", font=fr, fill="#444")
    im.save(f"{FIGS}/fig_08_factory.png")
    open(f"{FIGS}/fig_08_factory.csv", "w").write("anh,nguon\nIMG_4651,https://thepvietduc.com.vn/wp-content/uploads/2024/08/IMG_4651-1-1-1-1-1726x607.jpg\n")

IMG_W_PLACEHOLDER = 0
# ---- PDF
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
    md = md.split("\n", 1)[1]
    md = "![banner](figs/title_banner.png)\n" + md
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
        page.insert_text((42, 34), "VGS — CTCP Ống thép Việt-Đức VG PIPE · Báo cáo Due Diligence · 10/11/2026", fontname="dv", fontsize=7.5, color=(0.12, 0.23, 0.37))
        page.insert_text((A4.width - 160, 34), "Nhóm nghiên cứu", fontname="dv", fontsize=7.5, color=(0.4, 0.4, 0.4))
        page.draw_line((42, A4.height - 36), (A4.width - 42, A4.height - 36), color=(0.75, 0.78, 0.82), width=0.5)
        page.insert_text((42, A4.height - 24), "Thông tin nghiên cứu, không phải lời khuyên đầu tư cá nhân hoá. Xem Phụ lục F.", fontname="dv", fontsize=6.8, color=(0.4, 0.4, 0.4))
        page.insert_text((A4.width - 90, A4.height - 24), f"Trang {k + 1}/{n}", fontname="dv", fontsize=7.5, color=(0.2, 0.2, 0.2))
    doc.save(pdf_path, garbage=3, deflate=True)
    doc.close(); os.remove(tmp)
    for f in (FONT, FONT_B):
        os.remove(os.path.join(HERE, os.path.basename(f)))
    print("pages", n)



if __name__ == "__main__":
    if sys.argv[1] == "figs": figs()
    if sys.argv[1] == "pdf": pdf(f"{HERE}/{MD}.md", f"{HERE}/{MD}.pdf")
