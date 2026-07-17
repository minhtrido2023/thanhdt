# -*- coding: utf-8 -*-
"""
dcf_earning_power.py — EXPERIMENTAL DCF variants for two upgrade questions (job Taylor_20260717_063638):

  (Việc 1) BASIS: does an EARNING-POWER base (normalized multi-year net income to equity) value VN
    non-financials better than the raw FCFE base (CF_OA_3Y + CF_Invest_3Y)/3, which is lumpy because
    VN working capital + capex swing hard? Motivation: the 8L system has repeatedly shown 1/PE
    (earnings) is the single strongest, most regime-robust value factor (IC 0.125-0.181), indirect
    evidence that an earnings anchor may beat a cash-flow anchor — but that MUST be tested, not
    assumed (dcf_earning_power_test.py runs Study A/B + orthogonality on the variant).

  (Việc 3) TERMINAL GROWTH: the production DCF uses terminal g = 5y-avg CPI only → implicit REAL
    growth = 0 forever (very conservative). User asks to add long-run real GDP. Convergence theory
    (Damodaran): using CURRENT ~7-8% real growth as a PERPETUAL rate over-values grossly; average
    15-20y and FADE/CAP toward a mature sustainable rate. This module supplies 4 terminal-g modes
    so the fade/cap is explicit and testable (gdp_growth_vn.py supplies the raw long-run real GDP).

DESIGN NOTE — reuses dcf_valuation.py wholesale (helpers, gates, 2-stage formula, sensitivity). The
ONLY differences vs the canonical model are (a) the base cash-flow input and (b) the terminal-g rule,
both parametrized here. The canonical dcf_valuation.py is UNTOUCHED (coding_guidelines §3, §8): the
production Pha-2 helper trading_bot/strategies.py keeps calling D.fair_value with default behavior.

RESEARCH-ONLY. Nothing wired to production. Author: Taylor.
"""
import numpy as np, pandas as pd
import dcf_valuation as D
import gdp_growth_vn as G

# ---------------------------------------------------------------- terminal growth modes
TERM_MODES = ("cpi", "cpi_gdp_full", "cpi_gdp_half", "cap_rf")
GDP_FADE = 0.5                 # convergence haircut on long-run real GDP for cpi_gdp_half


def terminal_growth_mode(asof, mode="cpi", erp=D.ERP):
    """Terminal NOMINAL growth (decimal) under the chosen mode. Also returns diagnostics.

      cpi          : 5y-avg CPI only  (PRODUCTION baseline; real growth = 0)
      cpi_gdp_full : 5y-avg CPI + long-run(15y) real GDP  (user's naive proposal; ~9.6% — fragile)
      cpi_gdp_half : 5y-avg CPI + 0.5*long-run real GDP    (convergence-faded; ~6.5%)
      cap_rf       : min(cpi_gdp_full, nominal risk-free)  (Damodaran hard cap: g_term <= r_f)

    The nominal risk-free proxy = the Big-4 deposit rate = discount_rate - ERP."""
    cpi = D.terminal_growth(asof)                          # decimal, 5y-avg CPI
    if mode == "cpi":
        g = cpi
    else:
        gdp = G.longrun_real_gdp(asof)                     # decimal, 15y-avg real GDP
        if mode == "cpi_gdp_full":
            g = cpi + gdp
        elif mode == "cpi_gdp_half":
            g = cpi + GDP_FADE * gdp
        elif mode == "cap_rf":
            rf = D.discount_rate(asof, erp) - erp / 100.0  # deposit rate (nominal risk-free proxy)
            g = min(cpi + gdp, rf)
        else:
            raise ValueError(f"unknown term_mode {mode!r}")
    return g


# ---------------------------------------------------------------- experimental fair value
def fv_experimental(ticker, asof, price=None, oshares=None, erp=D.ERP,
                    basis="fcfe", term_mode="cpi", weights=D.DEFAULT_WEIGHTS, fin=None,
                    with_sens=False):
    """Point-in-time fair value under a chosen (basis, term_mode). Mirrors D.fair_value; the two
    axes are the ONLY changes. Returns the same dict schema + `basis`,`term_mode`,`gordon_clamped`.

      basis="fcfe"          : base = (CF_OA_3Y + CF_Invest_3Y)/3   (= canonical model)
      basis="earning_power" : base = normalized 3y-avg TTM NET INCOME to equity (cycle-smoothed
                              earning power; capex NOT deducted → EPV/Greenwald-style steady-state
                              assumption maintenance-capex ≈ D&A). Discounted at COST OF EQUITY, so
                              the earning-power measure is NET INCOME (equity earnings), NOT NOPAT/
                              EBIT (which is unlevered → would need WACC; inconsistent here)."""
    a = pd.to_datetime(asof)
    fin = D._load_financials() if fin is None else fin
    rows = fin[(fin.ticker == ticker) & (fin.time <= a)]
    res = {"ticker": ticker, "asof": str(a.date()), "ok": False, "reason": None,
           "basis": basis, "term_mode": term_mode, "gordon_clamped": False}
    if len(rows) < 4:
        res["reason"] = "insufficient financial history (<4 quarters)"; return res
    last = rows.iloc[-1]

    if D.is_financial(ticker, a):
        res["reason"] = "financial-sector — use Gordon-P/B"; return res

    # golden-floor cash gate (quality; kept for BOTH bases — positive earnings + negative operating
    # cash is an accrual red flag we still want to exclude)
    cfoa3 = float(last.CF_OA_3Y) if pd.notna(last.CF_OA_3Y) else np.nan
    if not (cfoa3 > 0):
        res["reason"] = "CF_OA_3Y <= 0 (operating cash gate fails)"; return res

    annual_np = D._annual_series(rows, ["NP_P0", "NP_P1", "NP_P2", "NP_P3"])

    # --- base cash-flow / earning-power input
    if basis == "fcfe":
        cfinv3 = float(last.CF_Invest_3Y) if pd.notna(last.CF_Invest_3Y) else 0.0
        base = (cfoa3 + cfinv3) / 3.0
        if base <= 0:
            res["reason"] = "normalized 3y FCFE <= 0 (capex > CFO)"; return res
    elif basis == "earning_power":
        # normalized earning power = mean of up to 3 trailing annual TTM net-income points
        ep_pts = [x for x in annual_np[:3] if x is not None and not (isinstance(x, float) and np.isnan(x))]
        if len(ep_pts) == 0:
            res["reason"] = "no TTM net-income points"; return res
        base = float(np.mean(ep_pts))
        if base <= 0:
            res["reason"] = "normalized 3y earning power <= 0 (loss-making)"; return res
    else:
        raise ValueError(f"unknown basis {basis!r}")
    res["base_input_vnd"] = base

    # --- growth (identical assembly to canonical: recency-weighted, shrink toward terminal)
    g_raw, gpts = D.recency_weighted_growth(annual_np, weights)
    g_T = terminal_growth_mode(a, term_mode, erp)
    if np.isnan(g_raw):
        g_raw = g_T
    g_clamp = float(np.clip(g_raw, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP))
    g_exp = g_T + D.GROWTH_SHRINK * (g_clamp - g_T)

    r = D.discount_rate(a, erp)
    if r <= g_T:                                # Gordon guard — CAN fire for cpi_gdp_full (fragile)
        g_T = r - 0.01
        res["gordon_clamped"] = True

    oshares = float(last.OShares) if oshares is None else float(oshares)
    if not (oshares and oshares > 0):
        res["reason"] = "OShares missing"; return res

    fv_ps = D._fv_per_share(base, g_exp, g_T, r, oshares)
    res.update({"ok": True, "fair_value_ps": fv_ps, "price": price, "discount_rate": r,
                "g_explicit": g_exp, "g_explicit_raw": g_raw, "g_terminal": g_T,
                "growth_points": gpts, "oshares": oshares, "quarter": last.quarter})
    if price is not None and fv_ps and fv_ps > 0:
        res["margin_of_safety"] = (fv_ps - price) / fv_ps
    if with_sens and (r - g_T) > 0.001 and (r - 0.01 - g_T) > 0.001:
        # skip sensitivity when a ±1% r perturbation would collide with g_T (Gordon-clamped
        # cpi_gdp_full) — the grid is informational only and not used by the IC harness
        res["sensitivity"] = D._sensitivity(base, g_exp, g_T, r, oshares)
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Experimental DCF (earning-power basis / GDP terminal g)")
    ap.add_argument("ticker")
    ap.add_argument("--asof", default="2026-06-15")
    ap.add_argument("--basis", default="earning_power", choices=["fcfe", "earning_power"])
    ap.add_argument("--term", default="cpi_gdp_half", choices=list(TERM_MODES))
    ap.add_argument("--price", type=float, default=None)
    args = ap.parse_args()
    px = args.price if args.price is not None else D.latest_price(args.ticker, args.asof)
    print(f"\n--- terminal-g modes as-of {args.asof} ---")
    for md in TERM_MODES:
        print(f"  {md:14s} = {terminal_growth_mode(args.asof, md):.2%}")
    for basis in ("fcfe", "earning_power"):
        r = fv_experimental(args.ticker, args.asof, price=px, basis=basis, term_mode=args.term)
        print(f"\n=== {args.ticker} basis={basis} term={args.term} ===")
        if not r["ok"]:
            print(f"  NOT COMPUTED: {r['reason']}"); continue
        print(f"  base input      : {r['base_input_vnd']/1e9:,.1f} bn VND/yr")
        print(f"  r={r['discount_rate']:.2%}  g_exp={r['g_explicit']:+.2%}  g_term={r['g_terminal']:.2%}"
              f"  {'[GORDON-CLAMPED]' if r['gordon_clamped'] else ''}")
        print(f"  FAIR VALUE/sh   : {r['fair_value_ps']:,.0f} VND   price={px:,.0f}")
        if "margin_of_safety" in r:
            print(f"  margin of safety: {r['margin_of_safety']:+.1%}")
