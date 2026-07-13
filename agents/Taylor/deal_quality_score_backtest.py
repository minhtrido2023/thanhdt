#!/usr/bin/env python3
"""
deal_quality_score_backtest.py — job Taylor_20260713_092636.

QUESTION (user, via Mike): the sector-lens STRONG tier only measures "cheap vs OWN history"
(self-referential). Does combining it with a CROSS-SECTIONAL "cheap vs the whole market" axis
into one comparable Deal-Quality Score (DQS) predict forward returns BETTER than either axis
alone? Empirical, not conceptual.

PRE-DECLARED FAMILY (N=4 scores x 2 horizons; no other variant was tried before this run):
  A     = self-referential cheapness: 1 - rolling-3Y percentile of the lens's PRIMARY metric
          within the name's OWN history (weekly grid, window 156w, min 52w, causal).
          Higher = more extreme cheap vs itself — the axis today's STRONG tier uses.
  B     = cross-sectional cheapness: per-date percent-rank of value composite
          (mean of pct-rank(1/PE), pct-rank(1/PCF)) within the LIQUID whole-market universe
          (turnover Close*Volume_3M_P50 >= 1e9 VND, PE>0). Mirrors 8L composite-v3's ey+cfy
          (PS absent from the daily cache — noted, 2/3 of the 8L value axis).
          Higher = cheaper vs the whole market at the same date.
  MEAN  = (A+B)/2      (both axes contribute; one extreme + one average -> middling score)
  PROD  = A*B          (joint extremity required for a top score)

SUCCESS CRITERION (declared before running): the composite (MEAN or PROD) "wins clearly" only
if, at BOTH horizons (profit_1M / profit_3M — EVAL-ONLY columns, never live filters):
  (i) OOS (2020+) mean per-date Spearman IC >= both single axes, AND
 (ii) OOS Q5-Q1 forward-return spread >= both single axes, AND
(iii) per-year IC sign is not carried by 1-2 years (LOO discipline).
Anything less -> verdict "KHONG thang ro", keep the existing binary double-confirm display.

POPULATION: pooled quality-gated sector universes (same gates as sector_strong_threshold.py /
the live monitor): Banking(8355) Tech(9537) Textile(3763) Securities(8777) Pharma(4577)
Logistics(2777,2773) + CTR by name. Weekly global grid (every 5th trading day) to cut
forward-return overlap; IS 2014-19 / OOS 2020-26. RESEARCH ONLY — reads the read-only BQ
DuckDB cache; writes nothing outside mike/agents/Taylor/.
"""
import os
import duckdb
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
CACHE = os.path.join(ROOT, "data", "bq_cache")
TKG = f"read_parquet('{CACHE}/ticker/*.parquet')"
OUT = os.path.join(ROOT, "mike", "agents", "Taylor", "dqs_backtest_obs.csv")

SECTORS = {
    "Banking":    dict(icbs=[8355], metric="PB"),
    "Tech":       dict(icbs=[9537], metric="PE"),
    "Textile":    dict(icbs=[3763], metric="PE"),
    "Securities": dict(icbs=[8777], metric="PB"),
    "Pharma":     dict(icbs=[4577], metric="PE"),
    "Logistics":  dict(icbs=[2777, 2773], metric="EVEB"),
}
LIQ_FLOOR_VND = 1e9   # tradeable-name bar, same as sector_strong_threshold tech check


def con1():
    c = duckdb.connect(":memory:")
    c.execute("SET threads=1")
    return c


def load_pool():
    """Sector-pool rows (daily, 2013+ so the 3Y window is warm by 2014) + CTR."""
    c = con1()
    icb_all = sorted({i for s in SECTORS.values() for i in s["icbs"]})
    q = ",".join(str(i) for i in icb_all)
    df = c.execute(f"""
        SELECT ticker, CAST(time AS DATE) AS time, ICB_Code, PE, PB, EVEB, PE_MA5Y,
               ROE5Y, ROE_Min3Y, ROIC5Y, IntCov_P0, Debt_Eq_P0, Close, Volume_3M_P50,
               profit_1M, profit_3M
        FROM {TKG}
        WHERE (ICB_Code IN ({q}) OR ticker='CTR') AND CAST(time AS DATE) >= DATE '2013-01-02'
        ORDER BY ticker, time
    """).df()
    c.close()
    icb2sec = {}
    for s, cfg in SECTORS.items():
        for i in cfg["icbs"]:
            icb2sec[i] = s
    df["sector"] = df["ICB_Code"].map(icb2sec)
    df.loc[df["ticker"] == "CTR", "sector"] = "Viettel-infra"
    df = df.dropna(subset=["sector"])
    return df


def load_axis_b():
    """Per-date cross-sectional value percentile over the LIQUID whole-market universe."""
    c = con1()
    df = c.execute(f"""
        WITH liq AS (
            SELECT ticker, CAST(time AS DATE) AS time, PE, PCF
            FROM {TKG}
            WHERE CAST(time AS DATE) >= DATE '2013-01-02'
              AND PE > 0 AND Close * Volume_3M_P50 >= {LIQ_FLOOR_VND}
        ), r AS (
            SELECT ticker, time,
                   PERCENT_RANK() OVER (PARTITION BY time ORDER BY 1.0/PE) AS pr_ey,
                   CASE WHEN PCF > 0 THEN
                        PERCENT_RANK() OVER (PARTITION BY time ORDER BY CASE WHEN PCF>0 THEN 1.0/PCF END)
                   END AS pr_cfy,
                   COUNT(*) OVER (PARTITION BY time) AS n_univ
            FROM liq
        )
        SELECT ticker, time,
               CASE WHEN pr_cfy IS NOT NULL THEN (pr_ey + pr_cfy)/2.0 ELSE pr_ey END AS axis_b,
               n_univ
        FROM r
    """).df()
    c.close()
    return df


def quality_gate(df):
    """Same quality gates the live monitor / sector_strong_threshold use. Gate ONLY (no
    buy-window cut): DQS must rank the whole gated watchlist, RICH names included."""
    s = df["sector"]
    ok = pd.Series(False, index=df.index)
    m = s == "Banking"
    ok |= m & (df["ROE5Y"] >= 0.12) & (df["ROE_Min3Y"] >= 0.08) & (df["PB"] > 0)
    m = s == "Tech"
    ok |= m & (df["ROIC5Y"] > 0.12) & (df["ROE5Y"] > 0.15) & (df["PE"] > 0)
    m = s == "Textile"
    ok |= m & (df["ROE5Y"] > 0.15) & ((df["IntCov_P0"] > 1.5) | df["IntCov_P0"].isna()) & (df["PE"] > 0)
    m = s == "Securities"
    ok |= m & ((df["IntCov_P0"] > 1.5) | df["IntCov_P0"].isna()) & (df["PB"] > 0)
    m = s == "Pharma"
    ok |= m & (df["ROE5Y"] > 0.15) & (df["ROIC5Y"] > 0.15) & (df["PE"] > 0)
    m = s == "Logistics"
    ok |= m & (df["ROE5Y"] > 0.15) & (df["Debt_Eq_P0"] < 2.0) & (df["EVEB"] > 0)
    m = s == "Viettel-infra"
    ok |= m & (df["ROIC5Y"] > 0.20) & (df["EVEB"] > 0)
    return ok.fillna(False)


def rolling_pct(arr, window=156, minp=52):
    """Causal percentile of the LAST value within the trailing window (inclusive)."""
    out = np.full(len(arr), np.nan)
    for i in range(len(arr)):
        lo = max(0, i - window + 1)
        w = arr[lo:i + 1]
        w = w[np.isfinite(w)]
        if len(w) >= minp and np.isfinite(arr[i]):
            out[i] = (w <= arr[i]).mean()
    return out


def build_obs():
    pool = load_pool()
    axb = load_axis_b()

    # weekly global grid on the pooled calendar
    dates = np.sort(pool["time"].unique())
    grid = set(dates[::5])
    pool = pool[pool["time"].isin(grid)].copy()
    axb = axb[axb["time"].isin(grid)]

    # primary metric per sector
    met = {**{s: c["metric"] for s, c in SECTORS.items()}, "Viettel-infra": "EVEB"}
    pool["metric"] = np.nan
    for s, mcol in met.items():
        m = pool["sector"] == s
        v = pool.loc[m, mcol]
        pool.loc[m, "metric"] = v.where(v > 0)

    # axis A: 1 - trailing percentile of the metric in the name's own weekly history
    pool = pool.sort_values(["ticker", "time"])
    pool["axis_a"] = (pool.groupby("ticker")["metric"]
                      .transform(lambda g: 1.0 - rolling_pct(g.to_numpy(float))))

    obs = pool.merge(axb[["ticker", "time", "axis_b", "n_univ"]], on=["ticker", "time"], how="left")
    obs = obs[quality_gate(obs)]
    obs = obs.dropna(subset=["axis_a", "axis_b", "profit_1M"])
    obs["time"] = pd.to_datetime(obs["time"])
    obs = obs[obs["time"] >= pd.Timestamp("2014-01-01")]
    obs = obs[obs["n_univ"] >= 100]   # cross-sectional pct meaningless on a thin date
    obs["MEAN"] = (obs["axis_a"] + obs["axis_b"]) / 2
    obs["PROD"] = obs["axis_a"] * obs["axis_b"]
    obs = obs.rename(columns={"axis_a": "A", "axis_b": "B"})
    return obs


SCORES = ["A", "B", "MEAN", "PROD"]
HORIZONS = ["profit_1M", "profit_3M"]


def perdate_ic(d, score, hz):
    """Mean per-date Spearman IC (>=8 names on the date)."""
    ics = []
    for _, g in d.groupby("time"):
        g = g.dropna(subset=[score, hz])
        if len(g) >= 8 and g[score].nunique() > 2:
            ic = stats.spearmanr(g[score], g[hz]).statistic
            if np.isfinite(ic):
                ics.append(ic)
    return (np.mean(ics), len(ics)) if ics else (np.nan, 0)


def quintile_table(d, score, hz):
    q = pd.qcut(d[score], 5, labels=False, duplicates="drop") + 1
    g = d.groupby(q)[hz].agg(["mean", "size"])
    spread = g["mean"].iloc[-1] - g["mean"].iloc[0] if len(g) >= 2 else np.nan
    return g, spread


def main():
    print("=" * 100)
    print("DEAL QUALITY SCORE (2-axis) BACKTEST — job Taylor_20260713_092636")
    print("family N=4 pre-declared: A(self) / B(cross) / MEAN / PROD  ·  horizons 1M & 3M (EVAL-ONLY)")
    print("=" * 100)
    obs = build_obs()
    obs.to_csv(OUT, index=False)
    print(f"pooled quality-gated weekly obs: N={len(obs)}  "
          f"({obs['time'].min()} → {obs['time'].max()}, {obs['ticker'].nunique()} names, "
          f"{obs['sector'].nunique()} sectors)")
    print(obs.groupby("sector").size().to_string())
    print(f"corr(A,B) pooled: {obs['A'].corr(obs['B']):.3f} (spearman "
          f"{obs['A'].corr(obs['B'], method='spearman'):.3f})")

    segs = [("ALL 2014-26", obs),
            ("IS 2014-19", obs[obs["time"] < pd.Timestamp("2020-01-01")]),
            ("OOS 2020-26", obs[obs["time"] >= pd.Timestamp("2020-01-01")])]

    for hz in HORIZONS:
        print("\n" + "#" * 100)
        print(f"### HORIZON {hz}")
        rows = []
        for seg, d in segs:
            for sc in SCORES:
                dd = d.dropna(subset=[sc, hz])
                ic_pool = stats.spearmanr(dd[sc], dd[hz]).statistic
                ic_pd, nd = perdate_ic(d, sc, hz)
                _, spread = quintile_table(d, sc, hz)
                rows.append(dict(seg=seg, score=sc, pooled_IC=round(ic_pool, 4),
                                 perdate_IC=round(ic_pd, 4), n_dates=nd,
                                 Q5_Q1_spread=round(spread, 2)))
        t = pd.DataFrame(rows).pivot(index="score", columns="seg",
                                     values=["pooled_IC", "perdate_IC", "Q5_Q1_spread"])
        print(t.to_string())

        print(f"\n--- quintile detail (OOS 2020-26, {hz}) ---")
        d = segs[2][1]
        for sc in SCORES:
            g, spread = quintile_table(d, sc, hz)
            print(f"  {sc}: " + "  ".join(f"Q{int(i)}={r['mean']:+.2f}%(n={int(r['size'])})"
                                          for i, r in g.iterrows()) + f"   Q5-Q1={spread:+.2f}pp")

    # per-year IC (LOO discipline) for the 1M horizon
    print("\n" + "#" * 100)
    print("### PER-YEAR per-date Spearman IC (profit_1M) — is any winner carried by 1-2 years?")
    obs["year"] = pd.to_datetime(obs["time"]).dt.year
    rows = []
    for y, d in obs.groupby("year"):
        r = {"year": y, "n": len(d)}
        for sc in SCORES:
            r[sc] = round(perdate_ic(d, sc, "profit_1M")[0], 3)
        rows.append(r)
    print(pd.DataFrame(rows).set_index("year").to_string())

    # double-confirm binary check: both-extreme vs single-extreme (the ✓✓ question directly)
    print("\n" + "#" * 100)
    print("### BINARY DOUBLE-CONFIRM CHECK — fwd return when A>=0.8 / B>=0.8 / BOTH (per segment)")
    for hz in HORIZONS:
        print(f"\n--- {hz} ---")
        for seg, d in segs:
            both = d[(d["A"] >= 0.8) & (d["B"] >= 0.8)]
            onlya = d[(d["A"] >= 0.8) & (d["B"] < 0.8)]
            onlyb = d[(d["A"] < 0.8) & (d["B"] >= 0.8)]
            neither = d[(d["A"] < 0.8) & (d["B"] < 0.8)]
            def f(x):
                return f"{x[hz].mean():+.2f}%/n={len(x)}/hit={(x[hz]>0).mean():.2f}" if len(x) else "n=0"
            print(f"  {seg:12s} BOTH✓✓ {f(both)}   A-only {f(onlya)}   B-only {f(onlyb)}   neither {f(neither)}")

    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
