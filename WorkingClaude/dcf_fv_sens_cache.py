# -*- coding: utf-8 -*-
"""dcf_fv_sens_cache.py — build the PIT DCF fair-value + sensitivity-box cache, one row per
(ticker, financial release), for the Pha-3 selector backtest (job Taylor_20260714_070221).

Why a cache: the Pha-3 harness needs `status`/`robust` EXACTLY as production computes them
(trading_bot/strategies.py::_dcf_check_for_order) for ~2.9k (rebal_date, pool-ticker) pairs.
fair_value() is deterministic in everything except `price`, and `price` only enters via
MoS = (fv - price)/fv. So the price-independent part (base fv_ps + the 4 sensitivity-box fv's)
is computed ONCE per release here; the harness then applies the rebal-date price to get
MoS/status/robust with zero look-ahead.

PIT: ticker_financial.time IS the release date (dcf_valuation._load_financials docstring), so a
rebal date d uses the last release with rel_time <= d. Nothing here reads price or forward data.

Output: mike/agents/Taylor/dcf_exp/fv_sens_releases.parquet
  ticker, rel_time, ok, reason, fv_ps, fv_r_dn, fv_r_up, fv_g_dn, fv_g_up

Research-only. Author: Taylor. Run: $DNA_PYEXE dcf_fv_sens_cache.py
"""
import os, sys, warnings
import pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import dcf_valuation as dcf

OUT = f"{WORKDIR}/mike/agents/Taylor/dcf_exp/fv_sens_releases.parquet"
SENS_MAP = {"r-1%": "fv_r_dn", "r+1%": "fv_r_up", "g-2%": "fv_g_dn", "g+2%": "fv_g_up"}


def main():
    fin = dcf._load_financials()
    # NOTE: pass the FULL `fin` to fair_value — filtering it (e.g. to >=2012) truncates the
    # trailing NP history that _annual_series() reads and silently perturbs the growth estimate,
    # so the cache would no longer reproduce production. Restrict the OUTPUT rows instead.
    pairs = fin[fin.time >= pd.Timestamp("2012-01-01")][["ticker", "time"]] \
        .drop_duplicates().sort_values(["ticker", "time"])
    print(f"[cache] {len(pairs)} (ticker, release) pairs from {pairs.time.min().date()} → {pairs.time.max().date()}")

    rows = []
    for i, (tk, t) in enumerate(zip(pairs.ticker, pairs.time)):
        # price=None -> fair_value returns fv_ps + sensitivity but no MoS (price applied later).
        res = dcf.fair_value(tk, t, price=None, fin=fin)
        r = {"ticker": tk, "rel_time": t, "ok": bool(res["ok"]),
             "reason": res.get("reason"), "fv_ps": res.get("fair_value_ps")}
        sens = res.get("sensitivity") or {}
        for k, col in SENS_MAP.items():
            r[col] = (sens.get(k) or {}).get("fv")
        rows.append(r)
        if (i + 1) % 5000 == 0:
            print(f"  ... {i+1}/{len(pairs)}")

    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.to_parquet(OUT, index=False)
    ok = out.ok.sum()
    print(f"[cache] wrote {OUT}: {len(out)} rows, ok={ok} ({ok/len(out):.1%}), "
          f"not_computed={len(out)-ok}")
    print("\ntop NOT_COMPUTED reasons:")
    print(out[~out.ok].reason.str.slice(0, 60).value_counts().head(8).to_string())


if __name__ == "__main__":
    main()
