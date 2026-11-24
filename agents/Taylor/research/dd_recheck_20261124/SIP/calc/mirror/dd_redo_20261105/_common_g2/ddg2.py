"""Phần dùng chung DD redo 05/11/2026 nhóm SIP/SCL/TV1/TV2 (job Taylor_20261105_014130).

- r (Ke nội địa) neo 13,5% @ lãi huy động 12T hiệu dụng của điểm neo 03/11/2026 (luật skill 03/11),
  r = 13,5% + β × (lãi hiệu dụng 04/11 − lãi điểm neo), β=1 (giả định; độ nhạy β 0,5).
  Lãi hiệu dụng = deposit_rate_vn.effective_deposit_rate() = max(Big-4 12M, CCTG 12M).
- Thanh khoản: px_g2_20261104.csv (tav2_bq.ticker, KHÔNG ticker_prune; universe_pit 04/11 = in_universe cả 4 mã).
  Phương pháp ĐĂNG KÝ TRƯỚC (giống SCL r3): chiết khấu = nửa spread Corwin-Schultz (120 phiên)
  + tác động giá căn bậc hai Y·σ_ngày·√(Q/ADV_trung vị), Y=1 (Y=0,5 = cận dưới); quy mô tham chiếu 5 tỷ đ.
  Số phiên thoát = Q/(p·ADV_trung vị), p ∈ {10%, 20%}. Amihud chỉ đối chiếu.
- Phân vị có trọng số + nhãn chuẩn hoá (DƯỚI <P10 / TRONG / TRÊN >P90).
"""
import csv, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
ASOF = "2026-11-04"
ANCHOR_DATE = "2026-11-03"
R_ANCHOR = 0.135
REF_SIZE = 5e9
SIZES = (1e9, 5e9, 10e9)


def r_info():
    sys.path.insert(0, WC)
    import deposit_rate_vn as d
    a = d.effective_deposit_rate(ANCHOR_DATE)
    c = d.effective_deposit_rate(ASOF)
    dep_a, dep_c = a["rate_pct"], c["rate_pct"]
    r = R_ANCHOR + 1.0 * (dep_c - dep_a) / 100
    return dict(r=round(r, 6), r_anchor=R_ANCHOR, beta=1.0,
                anchor=dict(rate=dep_a, date=ANCHOR_DATE, source=a["rate_source"]),
                current=dict(rate=dep_c, date=ASOF, source=c["rate_source"], big4=c["big4_rate_pct"],
                             cctg=c["cctg_rate_pct"]))


def r_grid(r0):
    """r theo ±50/±100bp lãi huy động, β 1,0 và 0,5."""
    out = {}
    for b in (1.0, 0.5):
        for bp in (-100, -50, 0, 50, 100):
            out[f"b{b}_{bp:+d}"] = r0 + b * bp / 1e4
    return out


def px_rows(tk):
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "px_g2_20261104.csv"))) if r["ticker"] == tk]
    for r in rows:
        for k in ("Open", "High", "Low", "Close", "Price", "Volume"):
            r[k] = float(r[k])
    return rows


def liquidity(tk, n=120):
    rows = px_rows(tk)
    win = rows[-n:]
    val = [r["Price"] * r["Volume"] for r in win]
    adv_med = st.median(val)
    rets = [math.log(win[i]["Close"] / win[i - 1]["Close"]) for i in range(1, len(win))]
    sigma = st.pstdev(rets)
    cs = []
    k = 3 - 2 * math.sqrt(2)
    for a, b in zip(win[:-1], win[1:]):
        beta = math.log(a["High"] / a["Low"]) ** 2 + math.log(b["High"] / b["Low"]) ** 2
        gam = math.log(max(a["High"], b["High"]) / min(a["Low"], b["Low"])) ** 2
        alpha = (math.sqrt(2 * beta) - math.sqrt(beta)) / k - math.sqrt(gam / k)
        cs.append(max(2 * (math.exp(alpha) - 1) / (1 + math.exp(alpha)), 0.0))
    spread = st.mean(cs)
    amihud = st.mean([abs(x) / v for x, v in zip(rets, val[1:]) if v > 0])
    sizes = []
    for q in SIZES:
        d = dict(size_ty=q / 1e9, pct_adv=q / adv_med, days_p10=q / (0.10 * adv_med), days_p20=q / (0.20 * adv_med),
                 half_spread=spread / 2, impact_y10=sigma * math.sqrt(q / adv_med),
                 impact_y05=0.5 * sigma * math.sqrt(q / adv_med), amihud_linear=min(amihud * q, 1.0))
        d["discount"] = d["half_spread"] + d["impact_y10"]
        d["discount_low"] = d["half_spread"] + d["impact_y05"]
        sizes.append(d)
    ref = [d for d in sizes if d["size_ty"] == REF_SIZE / 1e9][0]
    last = rows[-1]
    return dict(price=last["Price"], close=last["Close"], price_date=last["time"], n_sessions=len(win),
                window=[win[0]["time"], win[-1]["time"]], adv120_med_ty=adv_med / 1e9,
                adv60_med_ty=st.median([r["Price"] * r["Volume"] for r in rows[-60:]]) / 1e9,
                adv120_mean_ty=st.mean(val) / 1e9, sigma_d=sigma, cs_spread=spread,
                amihud_per_ty=amihud * 1e9, zero_vol_days=sum(1 for r in win if r["Volume"] == 0),
                sizes=sizes, ref_size_ty=REF_SIZE / 1e9, ref_discount=ref["discount"])


def wpct(vals, wts, qs=(0.10, 0.25, 0.50, 0.75, 0.90)):
    """Phân vị có trọng số (CDF bậc thang, lấy giá trị đầu tiên có CDF ≥ q)."""
    pairs = sorted(zip(vals, wts))
    tot = sum(w for _, w in pairs)
    out = {}
    for q in qs:
        c = 0.0
        for v, w in pairs:
            c += w / tot
            if c >= q - 1e-12:
                out[f"p{int(round(q * 100))}"] = v
                break
    return out


def label(px, p10, p90):
    if px < p10:
        return "DƯỚI vùng (<P10)"
    if px > p90:
        return "TRÊN vùng (>P90)"
    return "TRONG vùng"


def fmt(x):
    return f"{x:,.0f}".replace(",", ".")
