# -*- coding: utf-8 -*-
"""
dcf_orthogonality_test.py — Is DCF margin-of-safety (MoS) an independent information axis, or
just 1/PE measured with a fancier tool?

Pha 1 of the DCF plan (Taylor_20260714_061144). The composite-as-selector approach failed before
because the 1/PE dominant factor absorbed everything (KNOWLEDGE.md). Before ANY wire is considered,
we must know whether the DCF MoS carries forward-return signal that SURVIVES neutralizing 1/PE
(and, ideally, 1/PB and 1/EV-EBITDA).

Reuses the Study B panel (FV computed once per financial release, cached in dcf_exp/fv_releases.parquet
— NOT recomputed here) and merges point-in-time PE / PB / EVEB from the ticker cache onto the same
monthly panel rows.

Tests:
  1) Cross-sectional rank-correlation rank(MoS) vs rank(1/PE) per month, averaged over all months.
     High = they measure the same thing; low = complementary.
  2) Residual IC: neutralize MoS by 1/PE each month (rank-space OLS residual), measure IC of the
     residual vs forward return (profit_1M/2M/3M). Core question: after knowing 1/PE, does MoS
     still predict?
  3) Same for PB and EVEB, and for the joint [1/PE,1/PB,1/EVEB] neutralization.
  4) Walk-forward IS(2014-19) / OOS(2020-26) for every residual IC.
  5) t-stat is computed on the MONTHLY IC series (n≈144 months), a time-series t — NOT on the
     51k pooled rows (which would inflate significance: same-month obs are not independent).
     This is stated explicitly in the output (Spyros' question).

Research-only. Touches nothing in production. Author: Taylor. Job Taylor_20260714_061144.
Run: $DNA_PY dcf_orthogonality_test.py
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import duckdb

FV_CACHE = f"{WORKDIR}/mike/agents/Taylor/dcf_exp/fv_releases.parquet"
RATINGS  = "data/bq_cache/fa_ratings_8l.parquet"
TICKER   = "data/bq_cache/ticker/2*.parquet"
TARGETS  = ["profit_1M", "profit_2M", "profit_3M"]
VALCOLS  = {"inv_pe": "1/PE", "inv_pb": "1/PB", "inv_eveb": "1/EVEB"}


def spearman_ic(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = (~np.isnan(a)) & (~np.isnan(b))
    if m.sum() < 8:
        return np.nan
    return pd.Series(a[m]).rank().corr(pd.Series(b[m]).rank())


def resid_rank(y, x):
    """Rank-space residual of y after neutralizing by columns x (2D). Intercept included.
    Returns residuals aligned to y (NaN where inputs missing)."""
    y = np.asarray(y, float)
    X = np.asarray(x, float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    mask = ~np.isnan(y)
    for j in range(X.shape[1]):
        mask &= ~np.isnan(X[:, j])
    out = np.full(len(y), np.nan)
    if mask.sum() < 10:
        return out
    yr = pd.Series(y[mask]).rank().values
    Xr = np.column_stack([pd.Series(X[mask, j]).rank().values for j in range(X.shape[1])])
    Xr = np.column_stack([np.ones(len(yr)), Xr])
    beta, *_ = np.linalg.lstsq(Xr, yr, rcond=None)
    out[mask] = yr - Xr @ beta
    return out


def build_panel():
    """Study B panel + point-in-time PE/PB/EVEB on the same monthly rows."""
    if not os.path.exists(FV_CACHE):
        sys.exit(f"FV cache missing: {FV_CACHE} — run dcf_backtest.py --ic first")
    c = duckdb.connect(":memory:")
    cand = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{RATINGS}')
        WHERE rating<=3 AND route NOT IN ('BANK','INSURANCE','SECURITIES')""").df().ticker.tolist()
    cand_sql = "(" + ",".join(f"'{t}'" for t in cand) + ")"

    fv = pd.read_parquet(FV_CACHE)
    fv["rel_time"] = pd.to_datetime(fv["rel_time"])

    # monthly price panel + forward returns + point-in-time valuation ratios (first row each month)
    px = c.execute(f"""
        SELECT ticker, tdate, Price, profit_1M, profit_2M, profit_3M, PE, PB, EVEB FROM (
          SELECT ticker, CAST(time AS DATE) AS tdate, Price, profit_1M, profit_2M, profit_3M,
                 PE, PB, EVEB,
                 row_number() OVER (PARTITION BY ticker, date_trunc('month',CAST(time AS DATE))
                                    ORDER BY CAST(time AS DATE)) rn
          FROM read_parquet('{TICKER}')
          WHERE ticker IN {cand_sql} AND CAST(time AS DATE) >= DATE '2014-01-01'
        ) WHERE rn=1 AND Price IS NOT NULL
    """).df().rename(columns={"tdate": "time"})
    px["time"] = pd.to_datetime(px["time"])
    px = px.sort_values(["ticker", "time"]).reset_index(drop=True)

    # as-of merge FV (latest release <= eval date)
    merged = []
    for tk, gp in px.groupby("ticker"):
        gf = fv[fv.ticker == tk].drop(columns=["ticker"])
        if len(gf) == 0:
            continue
        merged.append(pd.merge_asof(gp.sort_values("time"), gf.sort_values("rel_time"),
                                    left_on="time", right_on="rel_time", direction="backward"))
    m = pd.concat(merged, ignore_index=True)
    m = m[m.fv_ps.notna() & (m.fv_ps > 0)]

    # as-of rating<=3 filter
    rat = c.execute(f"SELECT ticker, time, rating FROM read_parquet('{RATINGS}')").df()
    rat["time"] = pd.to_datetime(rat["time"]); rat = rat.sort_values(["ticker", "time"])
    mm = []
    for tk, gp in m.groupby("ticker"):
        rr = rat[rat.ticker == tk]
        if len(rr) == 0:
            continue
        mm.append(pd.merge_asof(gp.sort_values("time"), rr.sort_values("time"),
                                on="time", by="ticker", direction="backward"))
    m = pd.concat(mm, ignore_index=True)
    m = m[m.rating <= 3]

    m["mos"] = (m.fv_ps - m.Price) / m.fv_ps
    m = m[(m.time - m.rel_time).dt.days <= 460]          # freshness (identical to Study B)
    # aligned value proxies: higher = cheaper (like MoS)
    m["inv_pe"]   = np.where(m.PE > 0, 1.0 / m.PE, np.nan)
    m["inv_pb"]   = np.where(m.PB > 0, 1.0 / m.PB, np.nan)
    m["inv_eveb"] = np.where(m.EVEB > 0, 1.0 / m.EVEB, np.nan)
    m["year"] = m.time.dt.year
    return m


def windows(m):
    return [("ALL 2014-2026", m), ("IS 2014-2019", m[m.year <= 2019]), ("OOS 2020-2026", m[m.year >= 2020])]


def rank_corr_table(m):
    print("\n" + "=" * 82)
    print("1) CROSS-SECTIONAL RANK-CORRELATION  rank(MoS) vs rank(value proxy)")
    print("   (per month, then averaged; t on the monthly series, n=months)")
    print("=" * 82)
    for col, lbl in VALCOLS.items():
        print(f"\n  MoS vs {lbl}:")
        for wl, w in windows(m):
            cs = w.groupby("time").apply(lambda x: spearman_ic(x.mos.values, x[col].values)).dropna()
            if len(cs) == 0:
                print(f"    {wl:16s} no data"); continue
            t = cs.mean() / (cs.std() / np.sqrt(len(cs))) if cs.std() > 0 else np.nan
            print(f"    {wl:16s} mean_rankcorr={cs.mean():+.3f}  median={cs.median():+.3f}  "
                  f"t={t:+.1f}  (n_months={len(cs)})")


def ic_series(df, val_cols, tgt):
    """Monthly residual-IC series: neutralize MoS by val_cols each month, IC of residual vs tgt.
    val_cols=None → raw MoS IC (baseline)."""
    ics = []
    for _, x in df.groupby("time"):
        if val_cols is None:
            r = x.mos.values
        else:
            r = resid_rank(x.mos.values, x[val_cols].values)
        ics.append(spearman_ic(r, x[tgt].values))
    return pd.Series(ics, index=sorted(df.time.unique())).dropna()


def ic_row(s):
    if len(s) == 0:
        return "   no data"
    t = s.mean() / (s.std() / np.sqrt(len(s))) if s.std() > 0 else np.nan
    return f"meanIC={s.mean():+.4f}  t={t:+.2f}  hit%={100*(s>0).mean():3.0f}  (n={len(s)})"


def residual_ic_table(m):
    print("\n" + "=" * 82)
    print("2-4) RESIDUAL IC — does MoS predict AFTER neutralizing value proxies?")
    print("     t-stat on the MONTHLY IC series (n≈144), NOT pooled rows (Spyros).")
    print("=" * 82)
    neutralizers = [
        ("RAW MoS (baseline, no neutralize)", None),
        ("MoS ⟂ 1/PE",              ["inv_pe"]),
        ("MoS ⟂ 1/PB",              ["inv_pb"]),
        ("MoS ⟂ 1/EVEB",            ["inv_eveb"]),
        ("MoS ⟂ [1/PE,1/PB,1/EVEB]", ["inv_pe", "inv_pb", "inv_eveb"]),
    ]
    for name, cols in neutralizers:
        print(f"\n  {name}")
        for wl, w in windows(m):
            parts = []
            for tgt in TARGETS:
                s = ic_series(w, cols, tgt)
                parts.append(f"{tgt.split('_')[1]}: {ic_row(s)}")
            print(f"    {wl}")
            for p in parts:
                print(f"        {p}")


def coverage(m):
    print("\n" + "=" * 82)
    print("PANEL COVERAGE")
    print("=" * 82)
    print(f"  rows={len(m)}  months={m.time.dt.to_period('M').nunique()}  tickers={m.ticker.nunique()}")
    for col, lbl in VALCOLS.items():
        both = (m.mos.notna() & m[col].notna()).sum()
        print(f"  {lbl:8s} non-null & MoS non-null: {both} ({100*both/len(m):.0f}% of panel)")


if __name__ == "__main__":
    m = build_panel()
    coverage(m)
    rank_corr_table(m)
    residual_ic_table(m)
