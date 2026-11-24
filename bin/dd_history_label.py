#!/usr/bin/env python3
"""dd_history_label.py — nhãn CƠ HỌC "so với lịch sử CỦA CHÍNH MÃ" trên thước RI-ROE5Y (CHỈ HIỂN THỊ).

v2 (24/11/2026, theo quant-skeptic CONFIRMED/medium; user duyệt): thêm (a) hạ nhãn khi k_mã ngoài [0,5; 2]
("proxy lệch DD"), (b) cờ đối xứng lợi nhuận SỤT (ROE TTM/ROE5Y ≤ 1/1,3), (c) hạ nhãn khi N hiệu dụng (hold)
< 2,5, (d) dòng hiển thị KHÔNG còn mệnh đề "trung vị 10 năm ≈ …× tâm" — nhãn KHÔNG dùng tâm DD.
Nhãn v1 giữ ở cột `label_v1` để so trước/sau.

User duyệt 24/11/2026, thiết kế theo quant-skeptic R2/D2 (b):
  - Với mỗi mã DD: x(t) = Price_t / (k_mã × proxy_mã(t)), k_mã = tâm DD hôm nay / proxy_mã hôm nay
    (cố định theo mã; GIẢ ĐỊNH k BẤT BIẾN THEO THỜI GIAN — KHÔNG KIỂM ĐƯỢC khi chưa có sổ DD lịch sử).
  - proxy = Residual Income / đồng sổ sách của D1/D2 (vbv_dd = giữ ROE 5 năm rồi RI phẳng; vbv_fade =
    ROE fade tuyến tính về r trong 10 năm), cơ sở ROE = ROE5Y (TB 5 năm của chính mã), r = 13,5% gắn
    lãi huy động 12T Big-4 thuần (β=1, neo tại mức Big-4 mới nhất) — y hệt `pv_avg5_b4_{hold,fade}` của D2.
  - Hôm nay = Price_asof / tâm. Phân vị nhân quả trên cửa sổ (asof−10 năm, asof) — CHỈ quá khứ.
    ≥36 tháng hợp lệ, ít hơn ⇒ 'KHÔNG ĐỦ LỊCH SỬ'.
  - Tercile: RẺ (<33) · TRUNG TÍNH (33–67) · ĐẮT (>67). Chỉ gán khi CẢ HAI đầu dải [fade, hold] cùng
    tercile; vắt ngưỡng ⇒ 'KHÔNG CHẮC (a…b)'.
  - Hệ quả toán học (ghi rõ): vì k cố định theo mã và hôm nay = Price/(k·proxy_hôm nay), phân vị KHÔNG
    phụ thuộc k ⇒ nhãn = vị trí giá/proxy hôm nay của mã trên lịch sử giá/proxy của CHÍNH mã. Tâm DD chỉ
    đổi THANG hiển thị ở CSV (cột hist_med_*, pc_asof), KHÔNG đổi nhãn và KHÔNG nằm trong dòng hiển thị v2.

KHÔNG: vào luật 4 (cổng giá ≤0,85×tâm giữ nguyên, riêng) · đổi tâm/sổ/schema · dùng giá làm đầu vào giá
trị nội tại (tâm đọc từ sổ ĐÃ KHOÁ, giá chỉ dùng SAU) · wire sizing. Không đọc đồng hồ: asof = ngày cuối panel
(hoặc --asof) ⇒ không phụ thuộc TZ.

Dùng:  dd_history_label.py --ticker FPT [--ticker VCB]   |   dd_history_label.py --all-ledger
       [--asof YYYY-MM-DD] [--panel <parquet>] [--out-dir <dir>]
Đầu vào (mặc định): panel tháng PIT D1 `panel_all.parquet` (tav2_bq.ticker cuối tháng, Price thô/PB/PE/ROE5Y;
kb/data_registry: valuation_pe_pb_pcf_ps.md + roe_roic_fscore_quality.md CANONICAL), lãi Big-4
`rerun/R2/out/deposit_big4_snapshot.csv` (caveat: 26 mốc neo hồi tố 2026-06-19), sổ `kb/dd_price_zones.json`.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CANON_ROOT = "/home/trido/thanhdt/WorkingClaude/mike"
RES = os.path.join("agents", "Taylor", "research", "dd_vs_radar_20261124")
PANEL_REL = os.path.join(RES, "D1", "calc", "panel_all.parquet")      # không trong git (ignored) ⇒ fallback CANON
DEP_REL = os.path.join(RES, "rerun", "R2", "out", "deposit_big4_snapshot.csv")
LEDGER_REL = os.path.join("kb", "dd_price_zones.json")
OUT_REL = os.path.join("agents", "Taylor", "research", "dd_label_20261124", "out")

# hằng số = D1/calc/proxy.py (selfcheck kiểm parity hàm)
B, H, FADE = 0.5, 5, 10
R0 = 0.135
ROE_CLIP = (-0.20, 0.45)
VBV_MIN = 0.05
WIN_YEARS = 10
MIN_MONTHS = 36
LO, HI = 33.0, 67.0
PEAK_RATIO = 1.3          # ROE TTM / ROE5Y ≥ 1,3 ⇒ cảnh báo đỉnh lợi nhuận (ngưỡng hiển thị, chọn trước)
DECLINE_RATIO = 1.0 / PEAK_RATIO   # ROE TTM / ROE5Y ≤ 0,77 ⇒ cờ lợi nhuận SỤT (đối xứng cờ đỉnh) — do skeptic đề xuất
K_BAND = (0.5, 2.0)       # k_mã ngoài dải ⇒ "proxy lệch DD" ⇒ hạ nhãn — NGƯỠNG DO QUANT-SKEPTIC ĐỀ XUẤT 24/11/2026
NEFF_MIN = 2.5            # N hiệu dụng (hold) < 2,5 ⇒ hạ nhãn — NGƯỠNG DO QUANT-SKEPTIC ĐỀ XUẤT 24/11/2026
ORDER = ["RẺ", "TRUNG TÍNH", "ĐẮT"]
DEFINITE = set(ORDER)


def vbv_dd(roe, r, g):
    """V/BV — giữ ROE H năm, BV tăng g, sau đó RI phẳng vĩnh viễn (= D1 proxy.vbv_dd)."""
    v = np.ones_like(roe)
    for t in range(1, H + 1):
        v += (roe - r) * (1 + g) ** (t - 1) / (1 + r) ** t
    v += (roe - r) * (1 + g) ** H / r / (1 + r) ** H
    return v


def vbv_fade(roe, r):
    """V/BV — ROE fade tuyến tính về r trong FADE năm, sau đó RI=0 (= D1 proxy.vbv_fade)."""
    v = np.ones_like(roe)
    bv = np.ones_like(roe)
    for t in range(1, FADE + 1):
        roe_t = roe + (r - roe) * t / FADE
        v += (roe_t - r) * bv / (1 + r) ** t
        bv = bv * (1 + B * np.clip(roe_t, 0, None))
    return v


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def resolve(rel):
    for base in (ROOT, CANON_ROOT):
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return p
    sys.exit(f"thiếu file đầu vào: {rel} (đã tìm trong {ROOT} và {CANON_ROOT})")


def add_proxy(panel, dep):
    """Thêm r_b4, pv_hold, pv_fade (= Price/proxy) cho mọi dòng. dep: cột time, deposit_rate (%)."""
    p = panel.sort_values(["time", "ticker"]).reset_index(drop=True)
    dep = dep.sort_values("time")
    dep_now = float(dep["deposit_rate"].iloc[-1])
    p = pd.merge_asof(p, dep.rename(columns={"deposit_rate": "dep_big4"}), on="time", direction="backward")
    p["r_b4"] = R0 + (p["dep_big4"] - dep_now) / 100.0
    x = p["ROE5Y"].clip(*ROE_CLIP)
    g = B * x.clip(lower=0)
    pb = p["PB"].where(p["PB"] > 0)
    vh = vbv_dd(x.values, p["r_b4"].values, g.values)
    vf = vbv_fade(x.values, p["r_b4"].values)
    p["pv_hold"] = np.where(vh > VBV_MIN, pb / vh, np.nan)
    p["pv_fade"] = np.where(vf > VBV_MIN, pb / vf, np.nan)
    ok = p["PB"].gt(0) & p["PE"].notna() & p["PE"].ne(0)
    p["roe_ttm"] = np.where(ok, p["PB"] / p["PE"], np.nan)
    return p, dep_now


def pct_rank(hist, x):
    """Phân vị nhân quả: % tháng lịch sử có giá trị NHỎ HƠN hôm nay (= quy ước D2 pct_rank)."""
    hist = np.asarray(hist, float)
    return float(100.0 * (hist < x).mean())


def tercile(p, lo=None, hi=None):
    lo = LO if lo is None else lo
    hi = HI if hi is None else hi
    return "RẺ" if p < lo else ("ĐẮT" if p > hi else "TRUNG TÍNH")


def combine(t_fade, t_hold):
    if t_fade == t_hold:
        return t_fade
    a, b = sorted([t_fade, t_hold], key=ORDER.index)
    return f"KHÔNG CHẮC ({a.lower()}…{b.lower()})"


def n_eff(series):
    """N hiệu dụng xấp xỉ AR(1): n(1−ρ1)/(1+ρ1) trên log chuỗi tháng (ước lượng, chỉ mô tả)."""
    s = np.log(np.asarray(series, float))
    n = len(s)
    if n < 3:
        return float(n)
    rho = float(np.corrcoef(s[:-1], s[1:])[0, 1])
    rho = min(max(rho, 0.0), 0.999)
    return float(max(1.0, n * (1 - rho) / (1 + rho)))


def ledger_centers(ledger_path):
    """Bản cuối (dd_date, rev) có tâm của mỗi mã — cùng quy tắc D2."""
    zones = json.load(open(ledger_path))["entries"]
    best = {}
    for e in zones:
        if not e.get("center"):
            continue
        k = (e["dd_date"], e.get("rev", 1))
        if e["ticker"] not in best or k > best[e["ticker"]][0]:
            best[e["ticker"]] = (k, e)
    return {tk: e for tk, (_, e) in best.items()}


def label_ticker(rows, center, asof, win_years=None, lo=None, hi=None):
    """rows: các dòng panel (đã add_proxy) của MỘT mã, time ≤ asof. Trả dict một dòng kết quả."""
    rows = rows[rows.time <= asof].sort_values("time")
    rec = {"asof": str(asof.date()), "center": float(center)}
    today = rows[rows.time == asof]
    if today.empty:
        rec["label"] = "KHÔNG CÓ GIÁ ASOF"
        return rec
    t0 = today.iloc[0]
    price = float(t0.Price)
    rec.update({"price_asof": price, "pc_asof": price / center, "ROE5Y": float(t0.ROE5Y),
                "roe_ttm": float(t0.roe_ttm) if pd.notna(t0.roe_ttm) else np.nan})
    win = rows[(rows.time > asof - pd.DateOffset(years=win_years or WIN_YEARS)) & (rows.time < asof)]
    res = {}
    for v in ("fade", "hold"):
        pv0 = t0[f"pv_{v}"]
        hist = win[f"pv_{v}"].dropna()
        hist = hist[hist > 0]
        if not (pd.notna(pv0) and pv0 > 0):
            res[v] = None
            rec[f"n_{v}"] = int(len(hist))
            continue
        k = center / (price / pv0)                 # k_mã = tâm / proxy hôm nay
        h = hist.values / k                        # giá/(k·proxy) lịch sử
        x0 = price / center                        # = pv0/k
        res[v] = {"k": k, "n": int(len(h)), "pct": pct_rank(h, x0), "med": float(np.median(h)),
                  "p25": float(np.quantile(h, .25)), "p75": float(np.quantile(h, .75)), "h": h}
        rec.update({f"k_{v}": k, f"n_{v}": int(len(h)), f"pct_{v}": res[v]["pct"],
                    f"hist_med_{v}": res[v]["med"], f"hist_p25_{v}": res[v]["p25"], f"hist_p75_{v}": res[v]["p75"]})
    if res["fade"] is None or res["hold"] is None:
        rec["label"] = "KHÔNG ĐỊNH NGHĨA (V/BV≤0,05)"
    elif min(res["fade"]["n"], res["hold"]["n"]) < MIN_MONTHS:
        rec["label"] = "KHÔNG ĐỦ LỊCH SỬ"
    else:
        tf, th = tercile(res["fade"]["pct"], lo, hi), tercile(res["hold"]["pct"], lo, hi)
        rec.update({"terc_fade": tf, "terc_hold": th, "label": combine(tf, th),
                    "pct_lo": min(res["fade"]["pct"], res["hold"]["pct"]),
                    "pct_hi": max(res["fade"]["pct"], res["hold"]["pct"]),
                    "n_eff_hold": n_eff(res["hold"]["h"]), "n_eff_fade": n_eff(res["fade"]["h"])})
    warn = []
    r5, rt = rec["ROE5Y"], rec["roe_ttm"]
    if not (pd.notna(r5) and r5 > 0):
        warn.append("ROE5Y≤0/thiếu")
    else:
        rec["roe_ttm_over_5y"] = rt / r5 if pd.notna(rt) else np.nan
        if pd.notna(rt) and rt / r5 >= PEAK_RATIO:
            warn.append(f"ĐỈNH LỢI NHUẬN? (ROE TTM/5Y={rt / r5:.2f})")
        if pd.notna(rt) and rt / r5 <= DECLINE_RATIO:
            warn.append(f"LỢI NHUẬN SỤT? (ROE TTM/5Y={rt / r5:.2f})")
        if r5 > ROE_CLIP[1]:
            warn.append("ROE5Y bị kẹp 45%")
    rec["warn"] = "; ".join(warn)
    # v2: hạ nhãn. label_v1 = nhãn trước khi hạ; reasons = lý do (có thể nhiều), chỉ hạ khi nhãn v1 là RẺ/TRUNG TÍNH/ĐẮT.
    rec["label_v1"] = rec["label"]
    reasons = []
    ks = [rec.get("k_fade"), rec.get("k_hold")]
    ks = [k for k in ks if k is not None and pd.notna(k)]
    if ks and any(not (K_BAND[0] <= k <= K_BAND[1]) for k in ks):
        reasons.append(f"proxy lệch DD, k={min(ks):.2f}–{max(ks):.2f}")
    ne = rec.get("n_eff_hold", np.nan)
    if pd.notna(ne) and ne < NEFF_MIN:
        reasons.append(f"N hiệu dụng thấp, {ne:.2f}")
    rec["reasons"] = "; ".join(reasons)
    rec["demote_k"] = int(any(x.startswith("proxy") for x in reasons))
    rec["demote_neff"] = int(any(x.startswith("N hiệu") for x in reasons))
    if reasons and rec["label"] in DEFINITE:
        rec["label"] = f"KHÔNG CHẮC ({'; '.join(reasons)})"
    return rec


def run(tickers, asof=None, panel_path=None, dep_path=None, ledger_path=None, panel_df=None,
        win_years=None, lo=None, hi=None):
    panel_path = panel_path or resolve(PANEL_REL)
    dep_path = dep_path or resolve(DEP_REL)
    ledger_path = ledger_path or resolve(LEDGER_REL)
    panel = panel_df if panel_df is not None else pd.read_parquet(panel_path)
    panel = panel.copy()
    panel["time"] = pd.to_datetime(panel["time"])
    asof = pd.Timestamp(asof) if asof else panel.time.max()
    panel = panel[panel.time <= asof]                         # nhân quả: không thấy dữ liệu sau asof
    dep = pd.read_csv(dep_path, parse_dates=["time"])
    dep = dep[dep.time <= asof]
    p, dep_now = add_proxy(panel, dep)
    centers = ledger_centers(ledger_path)
    if tickers is None:
        tickers = sorted(centers)
    rows = []
    for tk in tickers:
        if tk not in centers:
            rows.append({"ticker": tk, "label": "KHÔNG CÓ TÂM TRONG SỔ"})
            continue
        e = centers[tk]
        rec = {"ticker": tk, "dd_date": e["dd_date"], "rev": e.get("rev", 1),
               "skeptic_final": e.get("skeptic_final")}
        rec.update(label_ticker(p[p.ticker == tk], float(e["center"]), asof, win_years, lo, hi))
        rows.append(rec)
    meta = {"asof": str(asof.date()), "big4_anchor_pct": dep_now, "r_anchor": R0,
            "inputs_md5": {"panel": md5(panel_path) if panel_df is None else "in-memory",
                           "deposit_big4": md5(dep_path), "ledger": md5(ledger_path)},
            "inputs_path": {"panel": panel_path, "deposit_big4": dep_path, "ledger": ledger_path},
            "window_years": win_years or WIN_YEARS, "k_band": list(K_BAND), "neff_min": NEFF_MIN, "decline_ratio": DECLINE_RATIO, "version": "v2", "min_months": MIN_MONTHS, "tercile": [LO if lo is None else lo, HI if hi is None else hi], "peak_ratio": PEAK_RATIO}
    return pd.DataFrame(rows), meta


COLS = ["ticker", "dd_date", "rev", "skeptic_final", "asof", "center", "price_asof", "pc_asof", "label", "label_v1", "reasons", "demote_k", "demote_neff",
        "pct_fade", "pct_hold", "terc_fade", "terc_hold", "n_fade", "n_hold", "n_eff_hold", "n_eff_fade",
        "k_fade", "k_hold", "hist_med_fade", "hist_med_hold", "hist_p25_fade", "hist_p75_fade",
        "hist_p25_hold", "hist_p75_hold", "ROE5Y", "roe_ttm", "roe_ttm_over_5y", "warn"]


def fmt_table(df):
    lines = [f"{'Mã':<5}{'nhãn':<62}{'dải p[fade,hold]':>17}{'N th':>6}{'Neff':>6}  cảnh báo"]
    for _, r in df.iterrows():
        band = (f"[{r.pct_fade:.0f}, {r.pct_hold:.0f}]" if pd.notna(r.get("pct_fade", np.nan))
                and pd.notna(r.get("pct_hold", np.nan)) else "-")
        n = int(min(r.get("n_fade", 0) or 0, r.get("n_hold", 0) or 0)) if pd.notna(r.get("n_hold", np.nan)) else 0
        ne = f"{r.n_eff_hold:.1f}" if pd.notna(r.get("n_eff_hold", np.nan)) else "-"
        lines.append(f"{r.ticker:<5}{str(r.label):<62}{band:>17}{n:>6}{ne:>6}  {r.get('warn', '') or ''}")
    return "\n".join(lines)


def display_line(r):
    """Dòng hiển thị v2 (đề xuất cho DD). KHÔNG chứa giá/tâm hay trung vị theo tâm: nhãn không dùng tâm DD."""
    if pd.isna(r.get("pct_hold", np.nan)):
        return f"{r.ticker}: {r.label} (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD)"
    n = int(min(r.n_fade, r.n_hold))
    w = f" ⚠ {r.warn}" if r.get("warn") else ""
    return (f"{r.ticker}: so với lịch sử 10 năm của chính mã — **{r.label}** — phân vị [fade {r.pct_fade:.0f}, "
            f"hold {r.pct_hold:.0f}], {n} tháng, N hiệu dụng ≈ {r.n_eff_hold:.1f} (thước cơ học RI-ROE5Y của chính mã, "
            f"KHÔNG dùng tâm DD; chỉ hiển thị){w}")


def write_out(df, meta, out_dir, tag):
    os.makedirs(out_dir, exist_ok=True)
    df = df.reindex(columns=COLS)
    csv = os.path.join(out_dir, f"dd_history_label_{tag}_{meta['asof']}.csv")
    df.to_csv(csv, index=False, float_format="%.6g")
    js = csv[:-4] + ".meta.json"
    json.dump(meta, open(js, "w"), ensure_ascii=False, indent=1, sort_keys=True)
    return csv, js


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ticker", action="append", help="mã DD (lặp được)")
    g.add_argument("--all-ledger", action="store_true", help="mọi mã có tâm trong kb/dd_price_zones.json")
    ap.add_argument("--asof", help="YYYY-MM-DD (mặc định: ngày cuối panel)")
    ap.add_argument("--panel")
    ap.add_argument("--out-dir", default=os.path.join(ROOT, OUT_REL))
    a = ap.parse_args(argv)
    tickers = None if a.all_ledger else [t.upper() for t in a.ticker]
    df, meta = run(tickers, asof=a.asof, panel_path=a.panel)
    print(f"asof {meta['asof']} · cửa sổ {WIN_YEARS}Y nhân quả · ≥{MIN_MONTHS} tháng · cơ sở ROE5Y · r Big-4 thuần "
          f"(neo {meta['big4_anchor_pct']}% → 13,5%) · CHỈ HIỂN THỊ, không vào luật 4")
    print(fmt_table(df))
    print("\n".join(display_line(r) for _, r in df.iterrows()))
    tag = "all" if a.all_ledger else "-".join(tickers)
    csv, js = write_out(df, meta, a.out_dir, tag)
    print(f"→ {csv}\n→ {js}")
    print("caveat: k bất biến theo thời gian = giả định KHÔNG kiểm được; N hiệu dụng ~3–5 chu kỳ/10 năm "
          "(chuỗi tự tương quan) ⇒ phân vị là MÔ TẢ, không kiểm định.")
    return df


if __name__ == "__main__":
    main()
