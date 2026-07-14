# -*- coding: utf-8 -*-
"""
dcf_rate_robustness.py — Study-B robustness probe: is the margin-of-safety IC sensitive to the
hindsight-biased deposit-rate series?

CONTEXT (Spyros / risk-auditor, 2026-07-14): all 26 anchors in deposit_rate_vn.py were calibrated
retrospectively on ONE date (2026-06-19) — they are NOT truly point-in-time for the past, so the
discount rate fed into every historical FV carries a hindsight bias (esp. the IS 2014-19 window).

WHAT THIS DOES: re-runs Study B's cross-sectional MoS IC with a CONSTANT discount rate (single
window-mean deposit + ERP) applied to EVERY as-of date, and compares to the pinned time-varying
result. Rationale: the IC is computed cross-sectionally WITHIN each month, and the discount rate is
identical across tickers on a given date (date-only, not ticker-specific). A constant rate therefore
removes any date-level hindsight from the discount rate entirely; if the IC barely moves, the Study-B
conclusion is not sensitive to the deposit-rate hindsight. If it moves a lot, we must down-weight the
historical IS number honestly.

Writes its FV cache to a SEPARATE experiment file (dcf_exp/fv_releases_fixedrate.parquet) — never
clobbers the pinned dcf_exp/fv_releases.parquet (coding_guidelines §8).

Author: Taylor. Job Taylor_20260714_055038. Research-only, not wired into production.
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import duckdb
import dcf_valuation as D
import deposit_rate_vn as _dep
from dcf_backtest import spearman_ic


def window_mean_deposit(start="2014-01-01", end="2026-06-01"):
    ev = _dep.deposit_events_df()
    idx = pd.date_range(start, end, freq="MS")
    s = pd.merge_asof(pd.DataFrame({"time": idx}), ev, on="time", direction="backward")
    return float(s.deposit_rate.mean())


def run(fixed_deposit=None, erp=D.ERP, cache_tag="fixedrate"):
    dep_mean = window_mean_deposit() if fixed_deposit is None else fixed_deposit
    r_fixed = (dep_mean + erp) / 100.0
    print("=" * 78)
    print(f"STUDY B ROBUSTNESS — CONSTANT discount rate r={r_fixed:.4f} "
          f"(deposit {dep_mean:.2f}% + ERP {erp:.1f}%), applied to ALL dates")
    print("=" * 78)

    # monkeypatch the discount rate to a constant (date-independent) — this is the whole probe
    D._RATE_CACHE.clear()
    D.discount_rate = lambda asof, erp=erp: r_fixed

    c = duckdb.connect(":memory:")
    cand = c.execute("""SELECT DISTINCT ticker FROM read_parquet('data/bq_cache/fa_ratings_8l.parquet')
        WHERE rating<=3 AND route NOT IN ('BANK','INSURANCE','SECURITIES')""").df().ticker.tolist()
    cand_sql = "(" + ",".join(f"'{t}'" for t in cand) + ")"

    # 1) FV once per release with the constant rate -> SEPARATE experiment cache
    cache_fp = f"{WORKDIR}/mike/agents/Taylor/dcf_exp/fv_releases_{cache_tag}.parquet"
    os.makedirs(os.path.dirname(cache_fp), exist_ok=True)
    if os.path.exists(cache_fp) and not os.environ.get("DCF_REFRESH"):
        fv = pd.read_parquet(cache_fp)
        print(f"FV loaded from cache: {fv.ticker.nunique()} tickers, {len(fv)} release-points")
    else:
        fin = D._load_financials(); D._load_routes(); D._load_icb_map()
        fin_by_tk = {tk: g for tk, g in fin.groupby("ticker")}
        fv_rows = []; skipped_degenerate = 0
        for tk in cand:
            g = fin_by_tk.get(tk)
            if g is None or len(g) < 5: continue
            for t in g.time.unique():
                if pd.Timestamp(t) < pd.Timestamp("2012-06-01"): continue
                # Under a CONSTANT low rate, the 2011 CPI-spike still in a short 5Y window can push
                # terminal g >= r (degenerate Gordon) for a handful of 2012 releases — all pre-2014,
                # outside the IC eval window. Skip them rather than fabricate a value.
                if D.terminal_growth(t) >= r_fixed - 0.02:
                    skipped_degenerate += 1; continue
                res = D.fair_value(tk, t, price=None, fin=g)
                if res["ok"]:
                    fv_rows.append({"ticker": tk, "rel_time": pd.Timestamp(t), "fv_ps": res["fair_value_ps"]})
        if skipped_degenerate:
            print(f"  (skipped {skipped_degenerate} pre-2014 releases where terminal g >= r under the constant-rate counterfactual)")
        fv = pd.DataFrame(fv_rows).sort_values(["ticker", "rel_time"]).reset_index(drop=True)
        fv.to_parquet(cache_fp)
        print(f"FV computed for {fv.ticker.nunique()} tickers, {len(fv)} release-points (cached {cache_fp})")

    # 2) monthly price panel (identical to Study B)
    px = c.execute(f"""
        SELECT ticker, tdate, Price, profit_1M, profit_2M, profit_3M FROM (
          SELECT ticker, CAST(time AS DATE) AS tdate, Price, profit_1M, profit_2M, profit_3M,
                 row_number() OVER (PARTITION BY ticker, date_trunc('month',CAST(time AS DATE)) ORDER BY CAST(time AS DATE)) rn
          FROM read_parquet('data/bq_cache/ticker/2*.parquet')
          WHERE ticker IN {cand_sql} AND CAST(time AS DATE) >= DATE '2014-01-01'
        ) WHERE rn=1 AND Price IS NOT NULL
    """).df().rename(columns={"tdate": "time"})
    px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"]).reset_index(drop=True)

    # 3) as-of merge FV
    merged = []
    for tk, gp in px.groupby("ticker"):
        gf = fv[fv.ticker == tk].drop(columns=["ticker"])
        if len(gf) == 0: continue
        merged.append(pd.merge_asof(gp.sort_values("time"), gf.sort_values("rel_time"),
                                    left_on="time", right_on="rel_time", direction="backward"))
    m = pd.concat(merged, ignore_index=True)
    m = m[m.fv_ps.notna() & (m.fv_ps > 0)]
    rat = c.execute("""SELECT ticker, time, rating FROM read_parquet('data/bq_cache/fa_ratings_8l.parquet')""").df()
    rat["time"] = pd.to_datetime(rat["time"]); rat = rat.sort_values(["ticker", "time"])
    mm = []
    for tk, gp in m.groupby("ticker"):
        rr = rat[rat.ticker == tk]
        if len(rr) == 0: continue
        mm.append(pd.merge_asof(gp.sort_values("time"), rr.sort_values("time"), on="time", by="ticker", direction="backward"))
    m = pd.concat(mm, ignore_index=True)
    m = m[m.rating <= 3]
    m["mos"] = (m.fv_ps - m.Price) / m.fv_ps
    m = m[(m.time - m.rel_time).dt.days <= 460]
    m["year"] = m.time.dt.year
    print(f"panel rows={len(m)}  months={m.time.dt.to_period('M').nunique()}  tickers={m.ticker.nunique()}")
    print(f"  MoS distribution: mean={m.mos.mean():+.2f} median={m.mos.median():+.2f} %cheap={100*(m.mos>0).mean():.0f}%")

    def ic_table(df, label):
        print(f"\n  {label}:")
        out = {}
        for tgt in ["profit_1M", "profit_2M", "profit_3M"]:
            ics = df.groupby("time").apply(lambda x: spearman_ic(x.mos.values, x[tgt].values)).dropna()
            if len(ics) == 0: print(f"    {tgt}: no data"); continue
            mic = ics.mean(); t = mic/(ics.std()/np.sqrt(len(ics))) if ics.std() > 0 else np.nan
            print(f"    {tgt}: meanIC={mic:+.4f}  t={t:+.2f}  hit%={100*(ics>0).mean():.0f}  (n_months={len(ics)})")
            out[tgt] = mic
        return out
    all_ic = ic_table(m, "ALL 2014-2026")
    ic_table(m[m.year <= 2019], "IS 2014-2019")
    ic_table(m[m.year >= 2020], "OOS 2020-2026")

    print("\n  --- delta vs PINNED time-varying result (framework §7) ---")
    pinned = {"profit_1M": 0.0444, "profit_2M": 0.0584, "profit_3M": 0.0690}   # ALL window
    for tgt in ["profit_1M", "profit_2M", "profit_3M"]:
        if tgt in all_ic:
            print(f"    {tgt} ALL: fixed={all_ic[tgt]:+.4f}  pinned={pinned[tgt]:+.4f}  Δ={all_ic[tgt]-pinned[tgt]:+.4f}")
    return m


if __name__ == "__main__":
    run()
