"""Phần dùng chung DD redo VÒNG 2 (05/11/2026) nhóm SIP/SCL/TV1/TV2 — job Taylor_20261105_020018.
Theo STANDARD_r2.md (12 điều). Khác vòng 1 (_common_g2/ddg2.py):
  - Phân vị: _shared/wpct.py (mid-block CDF) trên TỪNG KẾT CỤC của lưới (điều 1); báo n, % trọng số dưới giá, min.
  - Lưới = tích Descartes các TRỤC độc lập, mỗi trục có giá trị + xác suất + cơ sở (điều 2, 3) — build_grid().
  - Thanh khoản: giữ phương pháp ĐĂNG KÝ TRƯỚC của vòng 1 (nửa spread CS 120 phiên + Y·σ·√(Q/ADV120 trung vị), Y=1)
    cho cỡ tham chiếu 5 tỷ; THÊM cỡ sleeve thật 10/20/40 triệu đ và ADV trung vị 250 & 60 phiên (điều 6);
    cờ khi Q/ADV ngoài vùng hiệu chỉnh luật căn bậc hai (giả định vùng ≈ 0,1%–30% ADV một phiên — ước lượng).
  - Dữ liệu giá: px_g2r2_20261104.csv (tav2_bq.ticker 2025-08-01→2026-11-04, SQL px_g2r2.sql).
r: dùng lại ddg2.r_info() (13,5% + β(lãi huy động hiệu dụng − neo 03/11), β=1).
"""
import csv, hashlib, itertools, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "_shared"))
sys.path.insert(0, os.path.join(ROOT, "_common_g2"))
from wpct import wpct as _wpct, weight_below   # noqa: E402
import ddg2 as g1                               # noqa: E402

PX_CSV = os.path.join(HERE, "px_g2r2_20261104.csv")
REF_SIZE = 5e9
SLEEVE = (10e6, 20e6, 40e6)
NAV_SPACEX_NOTE = "NAV SpaceX ≈ 0,94 tỷ (STANDARD_r2 điều 6)"
SQRT_ZONE = (0.001, 0.30)   # vùng Q/ADV một phiên mà luật căn bậc hai thường được hiệu chỉnh (ước lượng)
QS = (0.10, 0.25, 0.50, 0.75, 0.90)

r_info = g1.r_info
r_grid = g1.r_grid
fmt = g1.fmt


def px_rows(tk):
    rows = [r for r in csv.DictReader(open(PX_CSV)) if r["ticker"] == tk]
    for r in rows:
        for k in ("Open", "High", "Low", "Close", "Price", "Volume"):
            r[k] = float(r[k])
    return rows


def liquidity(tk):
    rows = px_rows(tk)
    win = rows[-120:]
    val = lambda rs: [r["Price"] * r["Volume"] for r in rs]
    adv = {n: st.median(val(rows[-n:])) for n in (250, 120, 60)}
    rets = [math.log(win[i]["Close"] / win[i - 1]["Close"]) for i in range(1, len(win))]
    sigma = st.pstdev(rets)
    k = 3 - 2 * math.sqrt(2)
    cs = []
    for a, b in zip(win[:-1], win[1:]):
        be = math.log(a["High"] / a["Low"]) ** 2 + math.log(b["High"] / b["Low"]) ** 2
        ga = math.log(max(a["High"], b["High"]) / min(a["Low"], b["Low"])) ** 2
        al = (math.sqrt(2 * be) - math.sqrt(be)) / k - math.sqrt(ga / k)
        cs.append(max(2 * (math.exp(al) - 1) / (1 + math.exp(al)), 0.0))
    spread = st.mean(cs)

    def cost(q, adv_n):
        a = adv[adv_n]
        d = dict(size_vnd=q, adv_window=adv_n, pct_adv=q / a, days_p10=q / (0.10 * a), days_p20=q / (0.20 * a),
                 half_spread=spread / 2, impact=sigma * math.sqrt(q / a), impact_y05=0.5 * sigma * math.sqrt(q / a))
        d["discount"] = d["half_spread"] + d["impact"]
        d["discount_low"] = d["half_spread"] + d["impact_y05"]
        d["in_sqrt_zone"] = SQRT_ZONE[0] <= q / a <= SQRT_ZONE[1]
        return d

    table = {f"{q/1e6:.0f}tr_adv{n}": cost(q, n) for q in (*SLEEVE, 1e9, REF_SIZE, 10e9) for n in (250, 120, 60)}
    ref = table[f"{REF_SIZE/1e6:.0f}tr_adv120"]
    sl = {f"{q/1e6:.0f}tr": table[f"{q/1e6:.0f}tr_adv120"]["discount"] for q in SLEEVE}
    last = rows[-1]
    return dict(price=last["Price"], close=last["Close"], price_date=last["time"],
                adv250_med_ty=adv[250] / 1e9, adv120_med_ty=adv[120] / 1e9, adv60_med_ty=adv[60] / 1e9,
                n_rows=len(rows), sigma_d=sigma, cs_spread=spread, table=table,
                ref_size_ty=REF_SIZE / 1e9, ref_discount=ref["discount"], ref_in_sqrt_zone=ref["in_sqrt_zone"],
                ref_pct_adv120=ref["pct_adv"], ref_discount_adv250=table[f"{REF_SIZE/1e6:.0f}tr_adv250"]["discount"],
                ref_discount_adv60=table[f"{REF_SIZE/1e6:.0f}tr_adv60"]["discount"],
                sleeve_discount=sl, sleeve_max_discount=max(sl.values()))


def build_grid(axes, fn):
    """axes: dict tên → list[(nhãn, giá trị, xác suất)] (xác suất mỗi trục cộng 1). fn(**{tên: giá trị}) → đ/cp.
    Trả list kết cục: dict(labels, w, v). Trọng số kết cục = tích xác suất các trục (độc lập)."""
    for name, lv in axes.items():
        s = sum(p for _, _, p in lv)
        assert abs(s - 1) < 1e-9, (name, s)
    out = []
    names = list(axes)
    for combo in itertools.product(*[axes[n] for n in names]):
        w = 1.0
        for _, _, p in combo:
            w *= p
        if w == 0:
            continue
        kw = {n: c[1] for n, c in zip(names, combo)}
        out.append(dict(labels={n: c[0] for n, c in zip(names, combo)}, w=w, v=fn(**kw)))
    return out


def dist(outs, px, disc):
    """Phân phối MỨC KẾT CỤC (điều 1). disc = CK thanh khoản ở cỡ tham chiếu (nhân (1−disc))."""
    v = [o["v"] for o in outs]; w = [o["w"] for o in outs]
    tw = sum(w)
    E = sum(a * b for a, b in zip(v, w)) / tw
    pre = _wpct(v, w, QS)
    post = {f"p{int(round(q*100))}": x * (1 - disc) for q, x in pre.items()}
    vpost = [x * (1 - disc) for x in v]
    return dict(n=len(v), center_pre=E, center_post=E * (1 - disc),
                P_pre={f"p{int(round(q*100))}": x for q, x in pre.items()}, P_post=post,
                pct_w_below_px=weight_below(vpost, w, px), min_post=min(vpost), max_post=max(vpost))


def branch_share(outs, axis, q_value):
    """Trọng số từng nhãn của 1 trục nằm quanh phân vị q_value (±2% trọng số) — để nêu P10/P90 do nhánh nào quyết định (điều 4)."""
    s = sorted(outs, key=lambda o: o["v"]); tw = sum(o["w"] for o in s); acc = 0; band = {}
    for o in s:
        mid = (acc + o["w"] / 2) / tw
        acc += o["w"]
        if abs(mid - q_value) <= 0.02:
            lab = o["labels"][axis]
            band[lab] = band.get(lab, 0) + o["w"]
    t = sum(band.values()) or 1
    return {k: round(x / t, 3) for k, x in sorted(band.items())}


def label(px, p10, p90):
    if px < p10:
        return "DƯỚI vùng (<P10)"
    if px > p90:
        return "TRÊN vùng (>P90)"
    return "TRONG vùng"


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def write_lock(path, files, note=""):
    """Điều 9: khoá md5 ĐỦ mọi file upstream script thực thi hoặc đọc."""
    lines = [f"# LOCK upstream md5 — {note}".rstrip()]
    for f in files:
        lines.append(f"{md5(f)}  {os.path.relpath(f, ROOT)}")
    open(path, "w").write("\n".join(lines) + "\n")
    return lines


COMMON_FILES = [os.path.abspath(__file__), PX_CSV, os.path.join(HERE, "px_g2r2.sql"),
                os.path.join(ROOT, "_shared", "wpct.py"), os.path.join(ROOT, "_common_g2", "ddg2.py"),
                "/home/trido/thanhdt/WorkingClaude/deposit_rate_vn.py",
                "/home/trido/thanhdt/WorkingClaude/cctg_rate_vn.py",
                "/home/trido/thanhdt/WorkingClaude/data/deposit_rate_vn_events.csv",
                "/home/trido/thanhdt/WorkingClaude/data/cctg_rate_vn_events.csv"]
