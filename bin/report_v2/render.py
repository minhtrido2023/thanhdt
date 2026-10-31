"""report_v2.render — thành phần dựng báo cáo tài khoản chuẩn v2 (ngày/tuần/tháng/quý).

Module KHÔNG nạp số liệu và KHÔNG tính tỷ suất: nhận số đã có từ pipeline (xem data_sources.py)
và chỉ lo trình bày. Thành phần:
  • định dạng số kiểu Việt Nam ...................... vn(), pct(), pp(), mil()
  • biểu đồ (PNG 200dpi + CSV kèm, tiêu đề-kết luận) . chart_* ()
  • khối HTML (KPI tile, bảng, gạch đầu dòng) ....... kpi_tiles(), table(), bullets(), section()
  • PDF A4 Be Vietnam Pro (pymupdf.Story) ............ build_pdf()
  • HTML email ảnh nhúng cid ......................... build_email_html()
  • tự kiểm (markdown thô, repr tuple, font nhúng) ... lint_pdf(), render_pages()

Chạy bằng python3 hệ thống (matplotlib + PIL + pymupdf ở user site-packages).
"""
import csv
import html as H
import os
import re
import subprocess
import sys
import textwrap
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")          # Be Vietnam Pro (OFL), đi kèm repo
FONT_R = f"{FONT_DIR}/BeVietnamPro-Regular.ttf"
FONT_B = f"{FONT_DIR}/BeVietnamPro-Bold.ttf"
FONT_M = f"{FONT_DIR}/BeVietnamPro-Medium.ttf"
BANNER = os.path.join(HERE, "make_title_banner.py")

# Bảng màu — palette tham chiếu skill dataviz (đã chạy validate_palette.js: PASS, aqua cần nhãn trực tiếp)
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#ecebe7"
NAVY = "#1F3A5F"                       # chữ tiêu đề / header bảng (đồng bộ báo cáo DD)
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"   # danh mục / Trứng vàng / tiền mặt (thứ tự cố định)
BENCH = "#8a8984"                      # VN-Index: xám trung tính, luôn là đường tham chiếu
GOOD, BAD = "#0ca30c", "#d03b3b"       # chỉ dùng cho dấu +/− (luôn kèm dấu và số, không màu đơn độc)
BAND_RES, BAND_SUP = "#f6d5d5", "#d5ecd5"


# ───────────────────────── định dạng số ─────────────────────────
def nfc(s):
    return unicodedata.normalize("NFC", s)


def vn(x, nd=0, sign=False):
    """1234567.8 → '1.234.568'; dấu trừ '−'."""
    s = f"{abs(x):,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    if x < 0 and float(s.replace(".", "").replace(",", ".")) != 0:
        return "−" + s
    return ("+" + s) if sign and x > 0 else s


def pct(x, nd=2, sign=True):
    return vn(x, nd, sign) + "%"


def pp(x, nd=2):
    return vn(x, nd, True) + " điểm %"


def mil(x, nd=2):
    return vn(x / 1e6, nd) + " tr"


def tone(x):
    return GOOD if x > 0 else BAD if x < 0 else INK


# ───────────────────────── biểu đồ ─────────────────────────
def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT_R, FONT_B, FONT_M):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "Be Vietnam Pro", "font.size": 8.6, "axes.titlesize": 10,
        "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": "#bdbcb6", "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "ytick.left": False, "figure.facecolor": "white", "savefig.facecolor": "white",
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 8})
    return plt


def _save(fig, out_png, source, rows=None, header=None):
    """Lưu PNG + CSV dữ liệu vẽ; dòng nguồn ở chân hình."""
    fig.text(0.012, 0.012, "\n".join(textwrap.wrap(nfc(source), 165)), fontsize=6.4, color=MUTED,
             ha="left", va="bottom")
    fig.savefig(out_png, dpi=200)
    if rows is not None:
        with open(out_png[:-4] + ".csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if header:
                w.writerow(header)
            w.writerows(rows)
    import matplotlib.pyplot as plt
    plt.close(fig)
    return out_png


def _date_axis(ax, dates, max_ticks=8):
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=max_ticks))


def chart_index_vs_bench(dates, port, bench, title, out, source, *, unit="Chỉ số, cơ sở 100",
                         port_label="Danh mục (đã loại dòng tiền)", bench_label="VN-Index",
                         shade=None, size=(7.6, 3.0)):
    """Hai đường cùng cơ sở 100 (một trục). shade=(d0, d1) tô nền kỳ báo cáo."""
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=size)
    if shade:
        ax.axvspan(shade[0], shade[1], color="#f3f2ee", zorder=0, lw=0)
    ax.axhline(100, color="#bdbcb6", lw=0.8)
    ax.plot(dates, bench, color=BENCH, lw=1.6, label=bench_label)
    ax.plot(dates, port, color=S1, lw=2.0, label=port_label)
    for ys, c in ((port, S1), (bench, BENCH)):
        ax.annotate(vn(ys[-1], 1), (dates[-1], ys[-1]), xytext=(4, 0), textcoords="offset points",
                    color=INK, fontsize=8, fontweight="bold", va="center")
    ax.set_ylabel(unit)
    _date_axis(ax, dates)
    # Chú giải ĐẶT NGOÀI vùng vẽ (trên trục, dưới tiêu đề) — loc="best" từng đè lên đường NAV ở
    # chart tháng của bản ngày (lỗi hình thức mục G, 31/10).
    ax.set_title(nfc(title), pad=16)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 0.99), ncol=2, borderaxespad=0, frameon=False)
    ax.margins(x=0.06)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    rows = [(d.isoformat(), round(p, 4), round(b, 4)) for d, p, b in zip(dates, port, bench)]
    return _save(fig, out, source, rows, ["date", "portfolio_idx", "bench_idx"])


def chart_hbars(items, title, out, source, *, unit="VND", fmt=None, total=None, size=(7.6, 3.2),
                xlabel=None):
    """Cột ngang xanh/đỏ có nhãn số (đóng góp, P&L theo mã). items=[(nhãn, giá trị)] đã sắp.
    total=(nhãn, giá trị) vẽ thanh tổng màu đậm ở cuối."""
    plt = setup_mpl()
    fmt = fmt or (lambda v: vn(v, 0, True))
    labs = [nfc(k) for k, _ in items] + ([nfc(total[0])] if total else [])
    vals = [v for _, v in items] + ([total[1]] if total else [])
    cols = [tone(v) for _, v in items] + ([NAVY] if total else [])
    fig, ax = plt.subplots(figsize=size)
    y = list(range(len(vals)))[::-1]
    ax.barh(y, vals, color=cols, height=0.62, edgecolor="white", linewidth=1)
    span = max(abs(v) for v in vals) or 1
    for yi, v in zip(y, vals):
        ax.text(v + (0.012 * span if v >= 0 else -0.012 * span), yi, fmt(v), va="center",
                ha="left" if v >= 0 else "right", fontsize=7.6, color=INK)
    ax.set_yticks(y, labs)
    if total:
        ax.axhline(y[-1] + 0.5, color="#bdbcb6", lw=0.8)
    ax.axvline(0, color="#7d7c77", lw=0.8)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    ax.set_xlim(-span * 1.32, span * 1.32)
    ax.xaxis.set_major_formatter(lambda v, p: vn(v / 1e6, 0) + " tr" if unit == "VND" else vn(v, 0) + "%")
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    return _save(fig, out, source, [(k, v) for k, v in zip(labs, vals)], ["label", "value_" + unit])


def chart_alloc(rows, title, out, source, *, size=(7.6, 1.9)):
    """Thanh 100% xếp chồng theo mốc. rows=[(nhãn mốc, {thành phần: giá trị})] — thứ tự thành phần
    cố định S1,S2,S3; nhãn % trực tiếp trên đoạn (aqua dưới 3:1 ⇒ bắt buộc nhãn)."""
    plt = setup_mpl()
    comps = list(rows[0][1].keys())
    cols = [S1, S2, S3, "#e87ba4"][:len(comps)]
    fig, ax = plt.subplots(figsize=size)
    for i, (lab, d) in enumerate(rows[::-1]):
        tot = sum(d.values()); left = 0
        for c, col in zip(comps, cols):
            w = d[c] / tot * 100
            ax.barh(i, w, left=left, color=col, height=0.6, edgecolor="white", linewidth=2)
            if w >= 4:
                ax.text(left + w / 2, i, vn(w, 1) + "%", ha="center", va="center", fontsize=8,
                        color="white", fontweight="bold")
            left += w
    ax.set_yticks(range(len(rows)), [nfc(r[0]) for r in rows[::-1]])
    ax.set_xlim(0, 100); ax.grid(False); ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    from matplotlib.patches import Patch
    ax.legend([Patch(color=c) for c in cols], [nfc(c) for c in comps], loc="upper center",
              bbox_to_anchor=(0.5, -0.02), ncol=len(comps))
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    data = [(lab, *[d[c] for c in comps]) for lab, d in rows]
    return _save(fig, out, source, data, ["moc", *comps])


def chart_tape(bars, ind, title, out, source, *, zones=(), size=(7.6, 3.6)):
    """VN-Index + MA20/50/200 (panel trên) + khối lượng (panel dưới, trục riêng — 2 panel, không
    phải 2 trục chồng). zones=[(y0, y1, nhãn, 'res'|'sup')]."""
    plt = setup_mpl()
    ds = [b["time"] for b in bars]
    fig, (ax, av) = plt.subplots(2, 1, figsize=size, sharex=True, gridspec_kw={"height_ratios": [3.2, 1]})
    for y0, y1, lab, kind in zones:
        ax.axhspan(y0, y1, color=BAND_RES if kind == "res" else BAND_SUP, lw=0, zorder=0)
        ax.text(ds[-1], (y0 + y1) / 2, nfc(lab) + " ", fontsize=6.4, color=INK2, va="center", ha="right",
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.75))
    ax.plot(ds, [b["close"] for b in bars], color=INK, lw=1.4, label="VN-Index")
    for k, c, ls in (("MA20", S1, "-"), ("MA50", S2, "-"), ("MA200", "#6250d6", "--")):
        xs = [d for d in ds if d in ind]
        ax.plot(xs, [ind[d][k] for d in xs], color=c, lw=1.1, ls=ls, label=k)
    ax.set_ylabel("điểm")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 0.99), ncol=4, fontsize=7, handlelength=1.4, borderaxespad=0)
    ax.set_title(nfc(title), pad=16)
    av.bar(ds, [b["volume"] / 1e6 for b in bars],
           color=[GOOD if b["close"] >= (bars[i - 1]["close"] if i else b["close"]) else BAD for i, b in enumerate(bars)],
           width=0.8)
    av.set_ylabel("KL, tr cp")
    _date_axis(av, ds)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    rows = [(d.isoformat(), b["close"], b["volume"], *(round(ind[d][k], 2) if d in ind else "" for k in ("MA20", "MA50", "MA200")))
            for d, b in zip(ds, bars)]
    return _save(fig, out, source, rows, ["date", "close", "volume", "MA20", "MA50", "MA200"])


def chart_line_threshold(dates, vals, thr, title, out, source, *, unit="%", thr_label="", size=(7.6, 2.4)):
    """Một đường + vạch ngưỡng (độ rộng %>MA50 với vạch 40%)."""
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=size)
    ax.axhline(thr, color=BAD, lw=1, ls="--")
    ax.text(dates[0], thr + 1.2, nfc(thr_label), color=BAD, fontsize=7.4)
    ax.plot(dates, vals, color=S1, lw=1.8)
    ax.plot(dates[-1], vals[-1], "o", color=S1, ms=5)
    ax.annotate(vn(vals[-1], 1) + "%", (dates[-1], vals[-1]), xytext=(5, -2), textcoords="offset points",
                fontsize=8, fontweight="bold", color=INK)
    ax.set_ylabel(unit); ax.set_ylim(0, 100)
    _date_axis(ax, dates)
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return _save(fig, out, source, [(d.isoformat(), round(v, 3)) for d, v in zip(dates, vals)], ["date", "value"])


def chart_underwater(dates, dd, title, out, source, *, bench=None, size=(7.6, 2.3)):
    """Sụt giảm từ đỉnh (%, ≤0) — vùng tô đỏ nhạt; bench (tuỳ chọn) đường xám."""
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=size)
    ax.fill_between(dates, dd, 0, color="#f1c4c4", lw=0)
    ax.plot(dates, dd, color=BAD, lw=1.3, label="Danh mục (đã loại dòng tiền)")
    if bench is not None:
        ax.plot(dates, bench, color=BENCH, lw=1.2, label="VN-Index")
        ax.legend(loc="lower right", ncol=2)
    i = min(range(len(dd)), key=lambda k: dd[k])
    ax.annotate(f"{pct(dd[i], 2, False)} ({dates[i]:%d/%m})", (dates[i], dd[i]), xytext=(6, -2),
                textcoords="offset points", fontsize=7.8, fontweight="bold", color=INK)
    ax.set_ylabel("% so với đỉnh")
    _date_axis(ax, dates)
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    rows = [(d.isoformat(), round(v, 4), round(bench[k], 4) if bench else "") for k, (d, v) in enumerate(zip(dates, dd))]
    return _save(fig, out, source, rows, ["date", "dd_pct", "bench_dd_pct"])


def chart_month_grid(months, port, bench, title, out, source, *, size=(7.6, 1.7)):
    """Heatmap nhỏ tháng-theo-tháng: 3 hàng (Danh mục / VN-Index / Chênh). Màu phân kỳ xanh–đỏ quanh 0,
    số in trong ô (không phụ thuộc màu)."""
    plt = setup_mpl()
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    diff = [p - b for p, b in zip(port, bench)]
    M = np.array([port, bench, diff])
    lim = max(abs(M).max(), 1)
    cmap = LinearSegmentedColormap.from_list("dv", ["#e34948", "#f0efec", "#2a78d6"])
    fig, ax = plt.subplots(figsize=size)
    ax.imshow(M, cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect="auto")
    for r in range(3):
        for c in range(len(months)):
            v = M[r, c]
            ax.text(c, r, (pp(v).replace(" điểm %", " đ%") if r == 2 else pct(v)), ha="center", va="center",
                    fontsize=8.4, fontweight="bold" if r == 0 else "normal", color=INK)
    ax.set_xticks(range(len(months)), [nfc(m) for m in months])
    ax.set_yticks(range(3), ["Danh mục", "VN-Index", "Chênh lệch"])
    ax.grid(False); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    rows = [(m, p, b, round(d, 3)) for m, p, b, d in zip(months, port, bench, diff)]
    return _save(fig, out, source, rows, ["month", "portfolio_pct", "vnindex_pct", "diff_pp"])


def chart_line(dates, vals, title, out, source, *, unit, ref=None, ref_label="", size=(7.6, 2.3), fmt_last=None):
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=size)
    if ref is not None:
        ax.axhline(ref, color="#bdbcb6", lw=0.9, ls="--")
        ax.text(dates[0], ref, " " + nfc(ref_label), fontsize=7, color=INK2, va="bottom")
    ax.plot(dates, vals, color=S1, lw=1.8)
    for i in (0, len(vals) - 1):
        ax.annotate((fmt_last or (lambda v: vn(v, 1)))(vals[i]), (dates[i], vals[i]), xytext=(4, 4),
                    textcoords="offset points", fontsize=8, fontweight="bold", color=INK)
    ax.set_ylabel(unit)
    _date_axis(ax, dates)
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return _save(fig, out, source, [(d.isoformat(), round(v, 4)) for d, v in zip(dates, vals)], ["date", "value"])


def chart_waterfall(start, items, end, title, out, source, *, size=(7.6, 2.5)):
    """Cầu NAV: cột đầu kỳ (xanh đậm) → các bước +/− (xanh lá/đỏ, nổi từ mức trước) → cột cuối kỳ.
    Nhãn số trực tiếp (triệu VND, có dấu). Bước khớp đến 1 VND (assert ở người gọi)."""
    plt = setup_mpl()
    labs = ["NAV đầu kỳ"] + [nfc(k) for k, _ in items] + ["NAV cuối kỳ"]
    fig, ax = plt.subplots(figsize=size)
    lvl = start
    ax.bar(0, start / 1e6, color=NAVY, width=0.6)
    ax.text(0, start / 1e6, vn(start / 1e6, 1), ha="center", va="bottom", fontsize=7.6, color=INK)
    tops = [start]
    for i, (_, v) in enumerate(items, start=1):
        lo, hi = sorted((lvl, lvl + v))
        ax.bar(i, max((hi - lo) / 1e6, 1e-9), bottom=lo / 1e6, color=tone(v) if v else MUTED, width=0.6)
        ax.text(i, hi / 1e6, vn(v / 1e6, 2, True), ha="center", va="bottom", fontsize=7.6, color=INK)
        lvl += v; tops.append(hi)
    ax.bar(len(items) + 1, end / 1e6, color=NAVY, width=0.6)
    ax.text(len(items) + 1, end / 1e6, vn(end / 1e6, 1), ha="center", va="bottom", fontsize=7.6, color=INK)
    tops.append(end)
    lo_all = min(min(start, end, *(start + sum(v for _, v in items[:k]) for k in range(len(items) + 1))) / 1e6, 0)
    span = max(tops) / 1e6 - lo_all
    floor = min(start, end) / 1e6 - 0.35 * max(abs(v) for _, v in items) / 1e6 - 0.02 * span if items else 0
    ax.set_ylim(max(floor, 0), max(tops) / 1e6 + 0.12 * (max(tops) / 1e6 - max(floor, 0)))
    ax.set_xticks(range(len(labs)), ["\n".join(textwrap.wrap(l, 14)) for l in labs], fontsize=7)
    ax.set_ylabel("triệu VND")
    ax.grid(axis="x", visible=False)
    ax.set_title(nfc(title))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    rows = [("NAV đầu kỳ", round(start))] + [(k, round(v)) for k, v in items] + [("NAV cuối kỳ", round(end))]
    return _save(fig, out, source, rows, ["buoc", "vnd"])


def side_by_side(pngs, out, gap=30):
    """Ghép 2 hình cùng chiều cao thành 1 PNG (để đặt 2 chart một hàng trong PDF/email)."""
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in pngs]
    h = max(i.height for i in ims)
    ims = [i.resize((int(i.width * h / i.height), h)) for i in ims]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    canvas = Image.new("RGB", (W, h), "white"); x = 0
    for i in ims:
        canvas.paste(i, (x, 0)); x += i.width + gap
    canvas.save(out, dpi=(200, 200))
    return out


def banner(title, kicker, sub, out, mono="NAV", accent="#2a78d6"):
    """Banner tiêu đề Be Vietnam Pro (script của skill dd-investor-report; không logo ⇒ monogram)."""
    subprocess.run([sys.executable, BANNER, "--title", nfc(title), "--ticker", mono, "--kicker", nfc(kicker),
                    "--sub", nfc(sub), "--out", out, "--accent", accent], check=True, capture_output=True)
    return out


# ───────────────────────── khối HTML ─────────────────────────
CSS = """
@font-face {font-family: bvp; src: url(BeVietnamPro-Regular.ttf);}
@font-face {font-family: bvp; src: url(BeVietnamPro-Bold.ttf); font-weight: bold;}
* {font-family: bvp;}
body {margin: 0; padding: 0; font-size: 8.4pt; line-height: 1.36; color: #1d2731;}
h1 {font-size: 13pt; color: #1F3A5F; margin: 0 0 3pt 0;}
h2 {font-size: 11pt; color: #1F3A5F; margin: 8pt 0 1pt 0;}
p {margin: 2pt 0;}
p.k {font-size: 7.2pt; color: #6b6a66; margin: 0 0 3pt 0;}
p.fn {font-size: 6.8pt; color: #6b6a66; margin: 1pt 0 4pt 0;}
table {border-collapse: collapse; width: 100%; margin: 2pt 0 3pt 0;}
th {background-color: #1F3A5F; color: #ffffff; font-size: 7.4pt; padding: 2pt 4pt; text-align: left;}
td {font-size: 7.6pt; padding: 1.8pt 4pt; border-bottom: 1px solid #E3E6EA;}
td.r, th.r {text-align: right;}
tr.tot td {font-weight: bold; border-top: 1px solid #1F3A5F;}
ul {margin: 2pt 0 2pt 0; padding-left: 12pt;}
li {margin: 1.5pt 0;}
table.kpi td {border: none; padding: 4pt 5pt; background-color: #F3F5F8;}
table.kpi td.gap {background-color: #ffffff; padding: 0; width: 4pt;}
span.kl {font-size: 6.8pt; color: #5b6570;}
span.kv {font-size: 12.5pt; font-weight: bold;}
span.ks {font-size: 6.8pt; color: #5b6570;}
"""


# Ký tự Be Vietnam Pro KHÔNG có glyph ⇒ PDF lén nhúng font dự phòng (Noto Sans Math). Thay bằng chữ.
NO_GLYPH = {"→": "–", "√": "căn ", "≥": ">=", "≤": "<=", "Σ": "Tổng ", "≠": " khác "}


def glyph_safe(s):
    s = nfc(str(s))
    for k, v in NO_GLYPH.items():
        s = s.replace(k, v)
    return s


def esc(s):
    return H.escape(glyph_safe(s), quote=False)


def section(title, kicker=None):
    """Tiêu đề mục = câu kết luận."""
    return f"<h2>{esc(title)}</h2>" + (f'<p class="k">{esc(kicker)}</p>' if kicker else "")


def kpi_tiles(tiles, per_row=4):
    """tiles=[(nhãn, giá trị, phụ, màu|None)] → lưới tile (bảng HTML để email cũng là chữ thật)."""
    out = ['<table class="kpi">']
    for i in range(0, len(tiles), per_row):
        row = tiles[i:i + per_row] + [None] * (per_row - len(tiles[i:i + per_row]))
        cells = []
        for t in row:
            if t is None:
                cells.append('<td style="background-color:#ffffff"></td>')
                continue
            lab, val, sub, col = t
            c = f' style="color:{col}"' if col else ""
            cells.append(f'<td><span class="kl">{esc(lab)}</span><br/><span class="kv"{c}>{esc(val)}</span>'
                         f'<br/><span class="ks">{esc(sub)}</span></td>')
        out.append("<tr>" + '<td class="gap"></td>'.join(cells) + "</tr>")
        if i + per_row < len(tiles):
            out.append(f'<tr><td colspan="{2 * per_row - 1}" style="background-color:#ffffff;padding:2pt"></td></tr>')
    return "".join(out) + "</table>"


def table(header, rows, *, align=None, total_rows=0, color_cols=(), max_rows=10, widths=None, bold_rows=()):
    """Bảng gọn: số căn phải (align 'r'), cột màu có điều kiện (theo dấu của chuỗi), hàng tổng đậm.
    Trần max_rows hàng thân (luật v2: bảng dài → phụ lục, gọi với max_rows=None)."""
    if max_rows is not None and len(rows) > max_rows:
        raise ValueError(f"bảng {len(rows)} hàng > trần {max_rows} — đưa vào phụ lục")
    align = align or ["l"] + ["r"] * (len(header) - 1)
    wd = (lambda j: f' width="{widths[j]}%"' if widths else "")
    t = "<table><tr>" + "".join(f'<th class="{a}"{wd(j)}>{esc(h)}</th>' for j, (h, a) in enumerate(zip(header, align))) + "</tr>"
    for k, r in enumerate(rows):
        cls = ' class="tot"' if (k >= len(rows) - total_rows or k in bold_rows) else ""
        bg = ' style="background-color:#F6F7F9"' if (k % 2 and not cls) else ""
        cells = []
        for j, (c, a) in enumerate(zip(r, align)):
            s = esc(c)
            st = ""
            if j in color_cols and s.strip():
                st = f' style="color:{BAD if s.startswith("−") else GOOD if s.startswith("+") else INK}"'
            cells.append(f'<td class="{a}"{st}>{s}</td>')
        t += f"<tr{cls}{bg}>" + "".join(cells) + "</tr>"
    return t + "</table>"


def bullets(items, max_words=25, max_items=3):
    if max_items is not None and len(items) > max_items:
        raise ValueError(f"{len(items)} gạch > {max_items} (luật v2: tối đa 3 gạch mỗi mục)")
    for it in items:
        n = len(re.sub(r"<[^>]+>", "", it).split())
        if n > max_words:
            raise ValueError(f"gạch đầu dòng {n} từ > {max_words}: {it[:60]}…")
    return "<ul>" + "".join(f"<li>{glyph_safe(it)}</li>" for it in items) + "</ul>"


def b(s):
    return f"<b>{esc(s)}</b>"


def footnote(s):
    return f'<p class="fn">{esc(s)}</p>'


def img(path, width_pt=None):
    return ("img", path, width_pt)


# ───────────────────────── PDF A4 ─────────────────────────
def build_pdf(blocks, out_pdf, *, header_left, header_right="", footer="", archive_dirs=()):
    """blocks: chuỗi HTML | ('img', path, width_pt|None) | 'PAGEBREAK'. Mỗi khối giữ nguyên trên một
    trang (không tách bảng/khối); không đủ chỗ ⇒ sang trang. Hình co tối đa 18% để vừa trang."""
    import pymupdf
    from PIL import Image
    arch = pymupdf.Archive(FONT_DIR)
    for d in archive_dirs:
        arch.add(d)
    A4 = pymupdf.paper_rect("a4")
    where = A4 + (38, 46, -38, -40)
    full_w = where.width
    tmp = out_pdf + ".tmp"
    wr = pymupdf.DocumentWriter(tmp)
    st = {"dev": None, "y": where.y0}

    def new_page():
        if st["dev"] is not None:
            wr.end_page()
        st["dev"] = wr.begin_page(A4); st["y"] = where.y0

    def place(h):
        mk = lambda: pymupdf.Story(html=f"<body>{h}</body>", user_css=CSS, archive=arch)
        if st["dev"] is None:
            new_page()
        story = mk()
        more, filled = story.place(pymupdf.Rect(where.x0, st["y"], where.x1, where.y1))
        if more and st["y"] > where.y0 + 1:          # không vừa phần còn lại ⇒ trang mới
            new_page(); story = mk()
            more, filled = story.place(pymupdf.Rect(where.x0, st["y"], where.x1, where.y1))
        story.draw(st["dev"])
        while more:                                   # khối dài hơn 1 trang (chỉ phụ lục)
            new_page(); more, filled = story.place(where); story.draw(st["dev"])
        st["y"] = pymupdf.Rect(filled).y1 + 2

    def is_heading(blk):
        return isinstance(blk, str) and blk.startswith("<h2>") and "<table" not in blk and "<ul>" not in blk

    for k, blk in enumerate(blocks):
        if blk == "PAGEBREAK":
            new_page(); continue
        if is_heading(blk) and st["dev"] is not None and k + 1 < len(blocks):
            # giữ tiêu đề cùng trang với khối kế: ước chiều cao khối kế (ảnh: theo tỷ lệ; chữ/bảng: thử đặt)
            nxt = blocks[k + 1]
            if isinstance(nxt, tuple) and nxt[0] == "img":
                with Image.open(nxt[1]) as im:
                    need = (nxt[2] or full_w) * im.height / im.width * 0.82 + 40
            elif isinstance(nxt, str) and nxt != "PAGEBREAK":
                probe = pymupdf.Story(html=f"<body>{blk}{nxt}</body>", user_css=CSS, archive=arch)
                more, filled = probe.place(pymupdf.Rect(where.x0, 0, where.x1, where.height))
                need = pymupdf.Rect(filled).y1 if not more else where.height
            else:
                need = 0
            if st["y"] + need > where.y1 and st["y"] > where.y0 + 1:
                new_page()
        if isinstance(blk, tuple) and blk[0] == "img":
            _, path, wpt = blk
            wpt = wpt or full_w
            with Image.open(path) as im:
                hpt = wpt * im.height / im.width
            if st["dev"] is None:
                new_page()
            room = where.y1 - st["y"] - 4
            if hpt > room:
                if room >= 0.82 * hpt:
                    wpt, hpt = wpt * room / hpt, room
                else:
                    new_page()
            # DocumentWriter không vẽ ảnh trực tiếp ⇒ dùng Story với <img> kích thước tuyệt đối
            name = os.path.basename(path)
            arch.add(os.path.dirname(path))
            story = pymupdf.Story(html=f'<body><p style="margin:0;text-align:center"><img src="{name}" width="{wpt:.1f}" height="{hpt:.1f}"/></p></body>',
                                  user_css=CSS, archive=arch)
            more, filled = story.place(pymupdf.Rect(where.x0, st["y"], where.x1, where.y1 + 2))
            story.draw(st["dev"])
            st["y"] = pymupdf.Rect(filled).y1 + 3
            continue
        place(blk)
    wr.end_page(); wr.close()

    doc = pymupdf.open(tmp)
    n = doc.page_count
    for k, page in enumerate(doc):
        page.insert_font(fontname="bvp", fontfile=FONT_R)
        col = (0.12, 0.23, 0.37)
        page.draw_line((38, 36), (A4.width - 38, 36), color=col, width=0.6)
        page.insert_text((38, 30), nfc(header_left), fontname="bvp", fontsize=7.2, color=col)
        if header_right:
            w = pymupdf.Font(fontfile=FONT_R).text_length(nfc(header_right), fontsize=7.2)
            page.insert_text((A4.width - 38 - w, 30), nfc(header_right), fontname="bvp", fontsize=7.2, color=(0.4, 0.4, 0.4))
        page.draw_line((38, A4.height - 32), (A4.width - 38, A4.height - 32), color=(0.8, 0.82, 0.85), width=0.5)
        if footer:
            page.insert_text((38, A4.height - 21), nfc(footer), fontname="bvp", fontsize=6.6, color=(0.4, 0.4, 0.4))
        page.insert_text((A4.width - 80, A4.height - 21), f"Trang {k + 1}/{n}", fontname="bvp", fontsize=7.2, color=(0.2, 0.2, 0.2))
    doc.save(out_pdf, garbage=3, deflate=True)
    doc.close(); os.remove(tmp)
    return n


# ───────────────────────── HTML email (cid) ─────────────────────────
EMAIL_CSS = ("body{font-family:'Segoe UI','Helvetica Neue',Arial,Tahoma,sans-serif;color:#1d2731;font-size:14px;"
             "max-width:760px;margin:auto}h2{color:#1F3A5F;font-size:17px;margin:18px 0 4px}"
             "table{border-collapse:collapse;width:100%;font-size:13px}th{background:#1F3A5F;color:#fff;padding:4px 6px;text-align:left}"
             "td{padding:3px 6px;border-bottom:1px solid #E3E6EA}td.r,th.r{text-align:right}tr.tot td{font-weight:bold}"
             "table.kpi td{background:#F3F5F8;padding:8px}span.kv{font-size:20px;font-weight:bold}"
             "span.kl,span.ks,p.k,p.fn{font-size:12px;color:#5b6570}img{max-width:100%}")


def build_email_html(blocks, banner_png, title, out_html):
    """Thân email = cùng khối với PDF; ảnh nhúng bằng cid (manifest JSON cạnh file). Không gửi."""
    import json
    cids, parts = [], [f'<img src="cid:banner" alt="{H.escape(nfc(title), quote=True)}" style="width:100%"/>']
    cids.append(("banner", banner_png))
    for k, blk in enumerate(blocks):
        if blk == "PAGEBREAK":
            continue
        if isinstance(blk, tuple):
            cid = f"fig{k}"
            cids.append((cid, blk[1]))
            parts.append(f'<p><img src="cid:{cid}" alt="{H.escape(os.path.basename(blk[1]), quote=True)}"/></p>')
        else:
            parts.append(blk)
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{EMAIL_CSS}</style></head><body>"
           + "\n".join(parts) + "</body></html>")
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(doc)
    with open(out_html[:-5] + "_cid.json", "w", encoding="utf-8") as fh:
        json.dump(dict(cids), fh, ensure_ascii=False, indent=1)
    return out_html


# ───────────────────────── tự kiểm ─────────────────────────
def prose_words(blocks, stop_at=None):
    """Số từ VĂN XUÔI thân báo cáo (tiêu đề mục, gạch đầu dòng, chú thích) — bỏ bảng, KPI, hình.
    stop_at: chuỗi đánh dấu mục bắt đầu phụ lục (không tính)."""
    n = 0
    for blk in blocks:
        if not isinstance(blk, str) or blk == "PAGEBREAK":
            continue
        if stop_at and stop_at in blk:
            break
        txt = re.sub(r"<table.*?</table>", " ", blk, flags=re.S)
        n += len(H.unescape(re.sub(r"<[^>]+>", " ", txt)).split())
    return n


RAW_MD = [r"\['\|", r"\*\*", r"^\s*\|[-:| ]+\|\s*$", r"^#{1,4} ", r"\\n\|", r"!\[", r"\bNone\b", r"\bnan\b"]


def pdf_text(pdf):
    import pymupdf
    with pymupdf.open(pdf) as d:
        return [p.get_text() for p in d]


def lint_pdf(pdf):
    """→ dict: số trang, vi phạm markdown thô/repr, font (phải nhúng & là Be Vietnam Pro)."""
    import pymupdf
    hits = []
    with pymupdf.open(pdf) as d:
        fonts = set()
        for i, p in enumerate(d):
            t = p.get_text()
            for pat in RAW_MD:
                for m in re.finditer(pat, t, flags=re.M):
                    hits.append((i + 1, pat, t[max(0, m.start() - 20):m.end() + 20].replace("\n", " ")))
            for f in p.get_fonts(full=True):
                fonts.add((f[3], f[1] != "n/a" and f[0] > 0))
        words = sum(len(p.get_text().split()) for p in d)
        n = d.page_count
    names = sorted({f[0] for f in fonts})
    bad_fonts = [f for f in names if "BeVietnamPro" not in f.replace(" ", "") and "bvp" not in f.lower()]
    return {"pages": n, "words_total": words, "raw_markdown_hits": hits, "fonts": names, "non_bvp_fonts": bad_fonts}


def render_pages(pdf, outdir, dpi=110, prefix=None):
    import pymupdf
    os.makedirs(outdir, exist_ok=True)
    prefix = prefix or os.path.basename(pdf)[:-4]
    out = []
    with pymupdf.open(pdf) as d:
        for i, p in enumerate(d):
            f = os.path.join(outdir, f"{prefix}_p{i + 1}.png")
            p.get_pixmap(dpi=dpi).save(f); out.append(f)
    return out
