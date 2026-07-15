# -*- coding: utf-8 -*-
"""
dcf_valuation.py — Two-stage FCFE Discounted-Cash-Flow intrinsic-value model for
Vietnamese NON-FINANCIAL equities. An ABSOLUTE-valuation layer that complements the
RELATIVE lenses already used across the 8L system (P/E-vs-history, P/B-vs-Gordon, EV/EBITDA).

WHAT IT DOES (point-in-time, no look-ahead):
  For a ticker + as-of date, computes an intrinsic fair-value-per-share and a
  margin-of-safety = (fair_value - market_price)/fair_value  (>0 = trading below intrinsic).

MODEL (2-stage FCFE):
  Stage 1 (explicit, 5y): base FCFE grows at g_explicit = recency-weighted average of the
    last 3 annual growth rates (weights calibrated in dcf_backtest.py, default 60/25/15).
  Stage 2 (terminal, Gordon): growth fades to g_terminal = 5y-average CPI (cpi_vn.py).
  Discount rate (cost of equity) r = Big-4 12M deposit rate (deposit_rate_vn.py) + ERP,
    ERP = 6.5% (empirical: VNINDEX total-return premium over Big-4 deposit, 2013-2026).
  FCFE (free cash flow to equity) proxy = CFO - capex = CF_OA + CF_Invest (both absolute
    VND in tav2_bq.ticker_financial; CF_Invest is negative for capex outflow; net-borrowing
    assumed ~0 = stable capital structure). Base level = normalized 3-year average FCFE
    (CF_OA_3Y + CF_Invest_3Y)/3 — smoother than a single lumpy TTM.

GATES (a DCF is only meaningful for cash-generative, non-financial firms):
  - EXCLUDE financials (BANK/INSURANCE/SECURITIES) — FCFE-DCF is meaningless when leverage
    IS the product; those have their own Gordon-P/B frameworks.
  - Require CF_OA_3Y > 0 (reuse of the 8L golden-floor cash gate) — no DCF on firms burning
    operating cash during an expansion (the renewables/utility-buildout lesson).
  - If normalized FCFE <= 0 (capex persistently > CFO, e.g. heavy-buildout infra), report
    "no positive FCFE" rather than a spurious negative fair value.

LIMITATIONS: DCF is notoriously sensitive to the discount rate and terminal value — see the
  sensitivity block. This is an INTERPRETIVE / reference tool; whether margin-of-safety has a
  measurable forward-return edge is tested honestly in dcf_backtest.py (walk-forward IC).

  CONGLOMERATE / HOLDING CAVEAT (user directive 2026-07-15): unlike financials, multi-segment
  groups are NOT excluded — they still get a number — but that number models the group as ONE
  cash-flow stream with ONE growth rate and ONE discount rate. A holding whose segments have
  different economics/risk (e.g. VGC: building materials + industrial-park leasing) is properly
  valued sum-of-the-parts; a single-stream FCFE-DCF on it can be meaningless even when it looks
  precise. is_conglomerate() flags the known names so every report echoes the warning inline
  (see format_dcf_check in trading_bot/strategies.py), and DCF_DISCLAIMER carries the general
  version for readers — the list is hand-maintained and can never be exhaustive.

Author: Taylor (quant). Job Taylor_20260714_042622. NOT wired into production trading.
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import deposit_rate_vn as _dep
import cpi_vn as _cpi

# ---------------------------------------------------------------- calibrated params
ERP = 6.5                       # equity risk premium (%), EMPIRICAL: VNINDEX total-return
                                # (price CAGR 11.5% 2013-2026 + ~1.7% div) minus Big-4 deposit
                                # avg ~6.8% => ERP ~6.3-6.6% across windows; use 6.5% central.
                                # (Damodaran VN mature+country ~7-8% = upper bound; see framework)
EXPLICIT_YEARS = 5              # stage-1 horizon
# CALIBRATION RESULT (dcf_backtest.py Study A): trailing earnings growth NEGATIVELY predicts
# next-year growth (mean reversion, rank-IC ~ -0.10 IS / -0.20 OOS) and recency-weighting makes
# the prediction WORSE, not better. So (a) use EQUAL weights (the least-bad of the tested schemes),
# and (b) SHRINK the extrapolated growth toward terminal to reflect that mean reversion — full
# extrapolation of recent growth is empirically unjustified for VN non-financials.
DEFAULT_WEIGHTS = (1/3, 1/3, 1/3)      # equal — recency weighting did not help (Study A)
GROWTH_SHRINK = 0.50           # g_used = g_terminal + SHRINK*(g_trailing - g_terminal)
G_EXPLICIT_FLOOR = -0.02       # clamp stage-1 growth (avoid explosive / runaway DCF)
G_EXPLICIT_CAP = 0.20          # high-growth caveat: DCF caps the extrapolated growth
CPI_TERMINAL_YEARS = 5

# financial-sector ICB codes (excluded — own Gordon-P/B frameworks)
def is_financial_icb(icb):
    if pd.isna(icb):
        return False
    icb = int(icb)
    return icb == 8355 or (8530 <= icb <= 8579) or (8770 <= icb <= 8779)

FIN_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}

# Đa ngành / holding — VẪN tính DCF (khác nhóm tài chính bị exclude hẳn), nhưng kết quả có thể
# vô nghĩa: mô hình gộp cả tập đoàn thành 1 dòng tiền / 1 g / 1 r, trong khi các mảng có kinh tế
# và rủi ro khác nhau (định giá đúng phải là sum-of-the-parts).
# Danh sách DUY TRÌ TAY: ICB/route không nhận diện được cấu trúc đa ngành — ICB chỉ gán 1 ngành
# chính (VGC=2353 vật liệu XD, MSN=3577 thực phẩm, VIC=8633 BĐS — đúng cái bẫy này), 8L route
# cũng không có nhóm HOLDING. Vì vậy danh sách KHÔNG BAO GIỜ đầy đủ → DCF_DISCLAIMER (cảnh báo
# chung) luôn hiện trong report, không chỉ dựa vào cờ theo tên.
CONGLOMERATE_TICKERS = {
    "VIC": "Vingroup: BĐS + ô tô (VinFast) + bán lẻ/y tế/giáo dục",
    "MSN": "Masan Group: hàng tiêu dùng + bán lẻ + khoáng sản + cổ phần ngân hàng",
    "GEX": "Gelex: thiết bị điện + năng lượng/nước + vật liệu XD + KCN",
    "VGC": "Viglacera: vật liệu xây dựng + cho thuê KCN",
    "REE": "REE: cơ điện lạnh (M&E) + điện + nước + BĐS văn phòng",
    "GVR": "GVR: cao su thiên nhiên + KCN + gỗ",
    "HAG": "HAGL: nông nghiệp (chuối/heo) + các mảng còn lại",
    "CII": "CII: hạ tầng BOT + BĐS + nước",
    "TCH": "TC Hoàng Huy: xe tải/ô tô + BĐS",
}

DCF_DISCLAIMER = (
    "DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp "
    "thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số "
    "này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần "
    "định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã "
    "biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài "
    "chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED."
)


def is_conglomerate(ticker):
    """True nếu ticker nằm trong danh sách đa ngành/holding đã biết (chỉ để CẢNH BÁO hiển thị —
    không loại khỏi DCF, không tham gia logic nào)."""
    return str(ticker).upper() in CONGLOMERATE_TICKERS


def conglomerate_reason(ticker):
    """Mô tả ngắn vì sao ticker được đánh dấu đa ngành; "" nếu không có trong danh sách."""
    return CONGLOMERATE_TICKERS.get(str(ticker).upper(), "")

_FIN_CACHE = None
_RATE_CACHE = {}
_ICB_CACHE = None
_ROUTE_CACHE = None


def _load_financials():
    """All ticker_financial rows (point-in-time via `time` = release date)."""
    global _FIN_CACHE
    if _FIN_CACHE is None:
        import duckdb
        cols = ("ticker,time,quarter,OShares,"
                "NP_P0,NP_P1,NP_P2,NP_P3,NP_P4,NP_P5,NP_P6,NP_P7,"
                "CF_OA_P0,CF_OA_P1,CF_OA_P2,CF_OA_P3,CF_OA_3Y,CF_OA_5Y,"
                "CF_Invest_P0,CF_Invest_P1,CF_Invest_P2,CF_Invest_P3,CF_Invest_3Y,CF_Invest_5Y")
        c = duckdb.connect(":memory:")
        df = c.execute(
            f"SELECT {cols} FROM read_parquet('{WORKDIR}/data/bq_cache/ticker_financial.parquet')"
        ).df()
        df["time"] = pd.to_datetime(df["time"])
        _FIN_CACHE = df.sort_values(["ticker", "time"]).reset_index(drop=True)
    return _FIN_CACHE


def _load_icb_map():
    """ticker -> latest ICB_Code, from ticker_1m snapshot (ICB rarely changes; used only for
    financial-sector exclusion, so latest value is adequate point-in-time)."""
    global _ICB_CACHE
    if _ICB_CACHE is None:
        import duckdb
        c = duckdb.connect(":memory:")
        try:
            df = c.execute(
                f"SELECT ticker, MAX(ICB_Code) icb FROM read_parquet('{WORKDIR}/data/bq_cache/ticker_1m.parquet') "
                "GROUP BY ticker").df()
            _ICB_CACHE = dict(zip(df.ticker, df.icb))
        except Exception:
            _ICB_CACHE = {}
    return _ICB_CACHE


def _load_routes():
    """(ticker,time,route) from fa_ratings_8l for point-in-time financial-sector exclusion."""
    global _ROUTE_CACHE
    if _ROUTE_CACHE is None:
        import duckdb
        c = duckdb.connect(":memory:")
        try:
            df = c.execute(
                f"SELECT ticker, time, route FROM read_parquet('{WORKDIR}/data/bq_cache/fa_ratings_8l.parquet')").df()
            df["time"] = pd.to_datetime(df["time"])
            _ROUTE_CACHE = df.sort_values(["ticker", "time"]).reset_index(drop=True)
        except Exception:
            _ROUTE_CACHE = pd.DataFrame(columns=["ticker", "time", "route"])
    return _ROUTE_CACHE


def is_financial(ticker, asof):
    """True if ticker is a financial (BANK/INSURANCE/SECURITIES) — excluded from FCFE-DCF.
    Prefer the point-in-time 8L route; fall back to ICB code."""
    routes = _load_routes()
    a = pd.to_datetime(asof)
    rr = routes[(routes.ticker == ticker) & (routes.time <= a)]
    if len(rr):
        return rr.route.iloc[-1] in FIN_ROUTES
    return is_financial_icb(_load_icb_map().get(ticker, np.nan))


def discount_rate(asof, erp=ERP):
    """Cost of equity = Big-4 12M deposit rate (as-of) + ERP, in decimal."""
    a = pd.to_datetime(asof)
    key = (str(a.date()), erp)
    if key not in _RATE_CACHE:
        ev = _dep.deposit_events_df()
        a_eff = max(a, ev.time.iloc[0])          # clamp to earliest available deposit event
        _RATE_CACHE[key] = (_dep.current_deposit_rate(a_eff) + erp) / 100.0
    return _RATE_CACHE[key]


_CPI_DF = None
_TG_CACHE = {}


def terminal_growth(asof, years=CPI_TERMINAL_YEARS, with_frac=False):
    """5y-average CPI YoY as-of date (decimal). Uses cpi_vn real-NSO where available, proxy before.
    Memoized: the full monthly CPI series is built once, then sliced per as-of month.

    `frac_real` = fraction of months in the 5y window flagged `is_real_nso` (real GSO/NSO print vs
    interpolated proxy). The NSO chart only reaches back ~13 months, so for as-of dates before mid-2025
    this is 0% (all proxy). Return (val, frac_real) when with_frac=True; a plain float otherwise so the
    fair_value() Gordon math is unchanged."""
    global _CPI_DF
    a = pd.to_datetime(asof)
    key = (a.year, a.month)
    if key not in _TG_CACHE:
        if _CPI_DF is None:
            _CPI_DF = _cpi.cpi_monthly_df(end="2026-12-01")
        cpi = _CPI_DF
        w = cpi[(cpi.time <= a) & (cpi.time > a - pd.Timedelta(days=365 * years))]
        val = 0.035 if len(w) == 0 else float(w.cpi_yoy.mean()) / 100.0
        frac = float(w.is_real_nso.mean()) if len(w) else 0.0
        _TG_CACHE[key] = (val, frac)
    val, frac = _TG_CACHE[key]
    return (val, frac) if with_frac else val


# ---------------------------------------------------------------- growth assembly
def _annual_series(rows, value_cols):
    """From point-in-time quarterly rows (asc), build an annual TTM series by sampling the
    latest row and rows ~365*k days earlier. Returns list newest->oldest of TTM sums."""
    if len(rows) == 0:
        return []
    t0 = rows.time.iloc[-1]
    out = []
    used_idx = []
    for k in range(0, 5):
        target = t0 - pd.Timedelta(days=365 * k)
        # closest row at or before target (within +/- 75 days so we don't reuse the same quarter)
        cand = rows[rows.time <= target + pd.Timedelta(days=20)]
        if len(cand) == 0:
            break
        idx = (cand.time - target).abs().idxmin()
        if abs((rows.loc[idx, "time"] - target).days) > 200:
            break
        if idx in used_idx:
            break
        used_idx.append(idx)
        ttm = sum(float(rows.loc[idx, c]) for c in value_cols if pd.notna(rows.loc[idx, c]))
        out.append(ttm)
    return out


def recency_weighted_growth(annual_np, weights=DEFAULT_WEIGHTS):
    """annual_np: newest->oldest TTM net-profit list. Returns (g_explicit, growth_points)."""
    growths = []
    for k in range(len(annual_np) - 1):
        num, den = annual_np[k], annual_np[k + 1]
        if den is None or den <= 0 or num is None:
            growths.append(np.nan)
        else:
            growths.append(num / den - 1.0)
    growths = growths[:3]                      # g1(recent), g2, g3
    w = np.array(weights[:len(growths)], dtype=float)
    g = np.array(growths, dtype=float)
    mask = ~np.isnan(g)
    if mask.sum() == 0:
        return np.nan, growths
    g_w = float((g[mask] * w[mask]).sum() / w[mask].sum())
    return g_w, growths


# ---------------------------------------------------------------- core valuation
def fair_value(ticker, asof, price=None, oshares=None, erp=ERP,
               weights=DEFAULT_WEIGHTS, fin=None, verbose=False):
    """Compute intrinsic fair-value-per-share + margin-of-safety, point-in-time as-of `asof`.

    Returns a dict (always) with `ok` flag and `reason` when not computable.
    `price`/`oshares` may be supplied (e.g. from a preloaded ticker frame in the backtest);
    otherwise oshares is taken from the financial row and price must be passed by the caller.
    """
    a = pd.to_datetime(asof)
    fin = _load_financials() if fin is None else fin
    rows = fin[(fin.ticker == ticker) & (fin.time <= a)]
    res = {"ticker": ticker, "asof": str(a.date()), "ok": False, "reason": None}
    if len(rows) < 4:
        res["reason"] = "insufficient financial history (<4 quarters)"
        return res
    last = rows.iloc[-1]

    # financial-sector exclusion (own Gordon-P/B frameworks)
    if is_financial(ticker, a):
        res["reason"] = "financial-sector (BANK/INSURANCE/SECURITIES) — use Gordon-P/B, not FCFE-DCF"
        return res

    # golden-floor cash gate (reuse 8L semantics): CF_OA_3Y > 0
    cfoa3 = float(last.CF_OA_3Y) if pd.notna(last.CF_OA_3Y) else np.nan
    if not (cfoa3 > 0):
        res["reason"] = "CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful"
        return res

    # base FCFE = normalized 3y-average (CF_OA_3Y + CF_Invest_3Y)/3
    cfinv3 = float(last.CF_Invest_3Y) if pd.notna(last.CF_Invest_3Y) else 0.0
    base_fcfe = (cfoa3 + cfinv3) / 3.0
    res["base_fcfe_vnd"] = base_fcfe
    if base_fcfe <= 0:
        res["reason"] = "normalized 3y FCFE <= 0 (capex > CFO, heavy reinvestment) — no positive FCFE"
        return res

    # growth from recency-weighted annual TTM net-profit
    annual_np = _annual_series(rows, ["NP_P0", "NP_P1", "NP_P2", "NP_P3"])
    g_raw, gpts = recency_weighted_growth(annual_np, weights)
    g_T, g_T_frac_real = terminal_growth(a, with_frac=True)
    if np.isnan(g_raw):
        g_raw = g_T                             # no usable growth -> assume terminal
    g_clamp = float(np.clip(g_raw, G_EXPLICIT_FLOOR, G_EXPLICIT_CAP))
    # shrink toward terminal (mean-reversion correction, Study A)
    g_exp = g_T + GROWTH_SHRINK * (g_clamp - g_T)

    r = discount_rate(a, erp)
    if r <= g_T:                                # Gordon guard (never triggers at VN rates)
        g_T = r - 0.01

    oshares = float(last.OShares) if oshares is None else float(oshares)
    if not (oshares and oshares > 0):
        res["reason"] = "OShares missing"
        return res

    fv_ps = _fv_per_share(base_fcfe, g_exp, g_T, r, oshares)
    res.update({
        "ok": True, "fair_value_ps": fv_ps, "price": price,
        "discount_rate": r, "g_explicit": g_exp, "g_explicit_raw": g_raw,
        "g_terminal": g_T, "g_terminal_frac_real": g_T_frac_real,
        "growth_points": gpts, "oshares": oshares,
        "annual_np": annual_np, "quarter": last.quarter,
    })
    if price is not None and fv_ps and fv_ps > 0:
        res["margin_of_safety"] = (fv_ps - price) / fv_ps
    # sensitivity
    res["sensitivity"] = _sensitivity(base_fcfe, g_exp, g_T, r, oshares)
    if verbose:
        _print_report(res)
    return res


def _fv_per_share(base_fcfe, g_exp, g_T, r, oshares):
    fcfe = base_fcfe
    pv = 0.0
    for y in range(1, EXPLICIT_YEARS + 1):
        fcfe *= (1 + g_exp)
        pv += fcfe / (1 + r) ** y
    tv = fcfe * (1 + g_T) / (r - g_T)
    pv_tv = tv / (1 + r) ** EXPLICIT_YEARS
    return (pv + pv_tv) / oshares


def _sensitivity(base_fcfe, g_exp, g_T, r, oshares):
    base = _fv_per_share(base_fcfe, g_exp, g_T, r, oshares)
    out = {"base_fv_ps": base}
    for dr in (-0.01, 0.01):
        fv = _fv_per_share(base_fcfe, g_exp, g_T, r + dr, oshares)
        out[f"r{dr:+.0%}"] = {"fv": fv, "pct": (fv / base - 1) if base else np.nan}
    for dg in (-0.02, 0.02):
        fv = _fv_per_share(base_fcfe, g_exp + dg, g_T, r, oshares)
        out[f"g{dg:+.0%}"] = {"fv": fv, "pct": (fv / base - 1) if base else np.nan}
    return out


def _print_report(res):
    print(f"\n=== DCF fair value: {res['ticker']} as-of {res['asof']} ({res.get('quarter')}) ===")
    if not res["ok"]:
        print(f"  NOT COMPUTED: {res['reason']}")
        return
    print(f"  base FCFE (norm 3y avg) : {res['base_fcfe_vnd']/1e9:,.1f} bn VND/yr")
    gp = ["n/a" if (g is None or (isinstance(g, float) and np.isnan(g))) else f"{g:+.1%}" for g in res["growth_points"]]
    print(f"  annual growth pts g1,g2,g3: {gp}   -> g_trailing {res['g_explicit_raw']:+.1%}, g_explicit(shrunk→terminal) = {res['g_explicit']:+.1%}")
    fr = res.get("g_terminal_frac_real", 0.0)
    print(f"  discount rate r          : {res['discount_rate']:.2%}   "
          f"terminal g = {res['g_terminal']:.2%} ({fr:.0%} REAL NSO / {1-fr:.0%} PROXY)")
    if fr < 0.15:
        print("  ⚠️ CPI window mostly proxy — refetch NSO if this becomes a recurring valuation")
    print(f"  OShares                  : {res['oshares']/1e6:,.1f} M")
    print(f"  FAIR VALUE / share       : {res['fair_value_ps']:,.0f} VND")
    if res.get("price") is not None:
        print(f"  market price             : {res['price']:,.0f} VND")
        if "margin_of_safety" in res:
            mos = res["margin_of_safety"]
            tag = "CHEAP (below intrinsic)" if mos > 0 else "RICH (above intrinsic)"
            print(f"  MARGIN OF SAFETY         : {mos:+.1%}   -> {tag}")
    s = res["sensitivity"]
    print(f"  sensitivity (fv %chg): r-1%={s['r-1%']['pct']:+.0%} r+1%={s['r+1%']['pct']:+.0%} | "
          f"g-2%={s['g-2%']['pct']:+.0%} g+2%={s['g+2%']['pct']:+.0%}")


# ---------------------------------------------------------------- report annotation (shared)
_SENS_KEYS = ["r-1%", "r+1%", "g-2%", "g+2%"]


def dcf_check(ticker, asof, price=None):
    """dcf_check dict for ANY report (informational only) — same schema as the Pha 2 production
    helper `trading_bot/strategies.py::_dcf_check_for_order` (status/margin_of_safety/robust),
    so a research report and the plan-generation echo never disagree on what "robust" means.
    Fail-safe: any error -> status=NOT_COMPUTED, never raises (job Taylor_20260714_095943)."""
    try:
        px = price if price is not None else latest_price(ticker, asof)
        if px is None:
            return {"status": "NOT_COMPUTED", "margin_of_safety": None, "robust": False,
                    "reason": "no_price", "as_of": str(asof)[:10]}
        res = fair_value(ticker, asof, price=px)
        if not res["ok"]:
            reason = res.get("reason", "unknown")
            if "financial-sector" in reason:
                nc_reason = "financial_sector_excluded"
            elif "positive FCFE" in reason or "FCFE <= 0" in reason:
                nc_reason = "fcfe_negative_buildout"
            elif "insufficient financial" in reason:
                nc_reason = "insufficient_history"
            else:
                nc_reason = reason[:80]
            return {"status": "NOT_COMPUTED", "margin_of_safety": None, "robust": False,
                    "reason": nc_reason, "as_of": str(asof)[:10]}

        mos = res.get("margin_of_safety")
        status = "CHEAP" if (mos is not None and mos > 0) else "RICH"
        sens = res.get("sensitivity", {})
        robust = False
        if mos is not None and px > 0:
            mos_positive = mos > 0
            sens_signs = []
            for k in _SENS_KEYS:
                s = sens.get(k, {})
                fv_s = s.get("fv")
                if fv_s and fv_s > 0:
                    sens_signs.append(((fv_s - px) / fv_s) > 0)
            robust = bool(sens_signs) and all(sg == mos_positive for sg in sens_signs)

        return {"status": status,
                "margin_of_safety": round(float(mos), 4) if mos is not None else None,
                "robust": robust, "conglomerate": is_conglomerate(ticker),
                "as_of": str(asof)[:10]}
    except Exception as exc:
        return {"status": "NOT_COMPUTED", "margin_of_safety": None, "robust": False,
                "reason": f"dcf_error: {str(exc)[:80]}", "as_of": str(asof)[:10]}


_NC_LABEL = {
    "financial_sector_excluded": "loại tài chính",
    "fcfe_negative_buildout": "FCFE âm",
    "insufficient_history": "thiếu dữ liệu",
    "no_price": "thiếu giá",
}


def dcf_line(ticker, asof, price=None):
    """One-line DCF annotation for a report, e.g. 'DCF: CHEAP (MoS +18.4%, robust)' or
    'DCF: N/A (loại tài chính)'. Wraps dcf_check() — never raises."""
    d = dcf_check(ticker, asof, price=price)
    if d["status"] == "NOT_COMPUTED":
        label = _NC_LABEL.get(d.get("reason", ""), (d.get("reason") or "unknown")[:40])
        return f"DCF: N/A ({label})"
    mos = d["margin_of_safety"]
    tag = ", robust" if d["robust"] else ""
    cong = " ⚠ đa ngành" if d.get("conglomerate") else ""
    return f"DCF: {d['status']} (MoS {mos*100:+.1f}%{tag}){cong}"


# ---------------------------------------------------------------- price lookup (research)
def latest_price(ticker, asof=None):
    """Unadjusted market price (`Price`) as-of date from the BQ cache ticker table.
    NOTE: for LIVE pre-trade sizing use DNSE, not BQ (coding_guidelines §6). Research use only here."""
    import duckdb
    c = duckdb.connect(":memory:")
    a = "" if asof is None else f"AND time <= DATE '{pd.to_datetime(asof).date()}'"
    yr = "2*" if asof is None else str(pd.to_datetime(asof).year)
    try:
        df = c.execute(
            f"SELECT time, Price, Close FROM read_parquet('{WORKDIR}/data/bq_cache/ticker/{yr}.parquet') "
            f"WHERE ticker = '{ticker}' {a} ORDER BY time DESC LIMIT 1").df()
    except Exception:
        df = c.execute(
            f"SELECT time, Price, Close FROM read_parquet('{WORKDIR}/data/bq_cache/ticker/2*.parquet') "
            f"WHERE ticker = '{ticker}' {a} ORDER BY time DESC LIMIT 1").df()
    if len(df) == 0:
        return None
    p = df.Price.iloc[0]
    return float(p) if pd.notna(p) else (float(df.Close.iloc[0]) if pd.notna(df.Close.iloc[0]) else None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Two-stage FCFE DCF fair value (VN non-financial).")
    ap.add_argument("ticker")
    ap.add_argument("--asof", default=None, help="YYYY-MM-DD (default: latest)")
    ap.add_argument("--price", type=float, default=None, help="market price VND (default: BQ cache)")
    ap.add_argument("--erp", type=float, default=ERP)
    args = ap.parse_args()
    px = args.price if args.price is not None else latest_price(args.ticker, args.asof)
    res = fair_value(args.ticker, args.asof or pd.Timestamp.today().normalize(),
                     price=px, erp=args.erp)
    _print_report(res)
