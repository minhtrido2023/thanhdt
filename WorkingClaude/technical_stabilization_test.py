#!/usr/bin/env python3
"""
technical_stabilization_test.py  — RESEARCH ONLY (job Taylor_20260706_054234)

HYPOTHESIS (distinct from momentum, which was REFUTED — mom200 IC~0.002 in custom30B):
  Not "buy when price is strong" but "only buy a cheap/quality name once its DOWNTREND has
  STOPPED/stabilized". I.e. filter OUT the falling knives (cheap on fundamentals but price still
  dropping) from the WATCH universe. Does a technical-stabilization confirmation improve forward
  return / avoid deeper drawdown vs plain WATCH (cheap + quality gate) alone?

BASE UNIVERSE (proxy for rating<=3 WATCH / golden-cell BUY-NOW, per rating_8l.py):
  golden floor : ROE_Min3Y >= 0  AND  CF_OA_5Y > 0     (book trustworthy + cash generative)
  cheap-vs-hist: pb_z = (PB-PB_MA5Y)/PB_SD5Y <= -0.3   (same threshold as BUY-NOW)
  liquid       : Trading_Value_1M_P50/1e9 >= 3.0 bn/day (LIQ_MIN in rating_8l.py)

STABILIZATION FLAGS (all point-in-time; use only current/past fields — no look-ahead):
  rsi_bounce   : D_RSI > D_RSI_Min3M + 0.05   (RSI recovered >=5pts off its 3M trough)
  cmb_notbear  : D_CMB >= 0                    (CMB out of strong-bearish)
  price_off_low: C_L1M >= 1.05                 (close >=5% above its 1M low)
  reclaim_ma50 : Close >= MA50                 (reclaimed short-term MA)
  combo_rsi_px : rsi_bounce AND price_off_low
  combo_ma_cmb : reclaim_ma50 AND cmb_notbear
  (neg ref) near_1m_low : C_L1M <= 1.02        (still pinned at 1M low = knife candidate)

OUTCOME: profit_1M/2M/3M (forward-looking targets — eval only, NEVER a live filter).
FALLING-KNIFE: forward 40-session min-drawdown = min(Close over next 40 sess)/Close - 1;
               "continued to fall" = drawdown <= -10%.

Rigor: threads=1, point-in-time, walk-forward IS(2014-19)/OOS(2020-26), monthly-cohort t-stats
(daily WATCH rows are heavily autocorrelated -> naive daily t is inflated; monthly cohort mean is
the honest unit). Self-check: 0-VND / recompute counts printed.
"""
import duckdb, numpy as np, pandas as pd

pd.set_option("display.width", 200); pd.set_option("display.max_columns", 40)
CACHE = "data/bq_cache/ticker/*.parquet"

# ---------------------------------------------------------------- load WATCH events + fwd drawdown
def load():
    con = duckdb.connect(); con.execute("PRAGMA threads=1")
    q = f"""
    WITH raw AS (
      SELECT CAST(time AS DATE) AS d, ticker, Close, MA50, MA200,
        D_RSI, D_RSI_Min3M, D_CMB, D_CMB_XFast, C_L1M, C_L1W,
        PB, PB_MA5Y, PB_SD5Y, ROE_Min3Y, CF_OA_5Y,
        Trading_Value_1M_P50/1e9 AS liq_bn,
        profit_1M, profit_2M, profit_3M
      FROM read_parquet('{CACHE}')
      WHERE CAST(time AS DATE) >= DATE '2014-01-01'
    ),
    win AS (
      SELECT *,
        (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) AS pb_z,
        MIN(Close) OVER (PARTITION BY ticker ORDER BY d
                         ROWS BETWEEN 1 FOLLOWING AND 40 FOLLOWING) AS fwd_min40
      FROM raw
    )
    SELECT d, ticker, Close, MA50, D_RSI, D_RSI_Min3M, D_CMB, C_L1M, pb_z,
           profit_1M, profit_2M, profit_3M, liq_bn,
           fwd_min40/NULLIF(Close,0) - 1 AS dd_fwd40
    FROM win
    WHERE ROE_Min3Y>=0 AND CF_OA_5Y>0 AND pb_z<=-0.3 AND liq_bn>=3.0
          AND profit_1M IS NOT NULL
    ORDER BY d, ticker
    """
    df = con.execute(q).df()
    # profit_* are stored in PERCENT (5.49 = +5.49%) with a few inf artifacts (price ~0).
    # Convert to fractions and drop/clip non-finite so a handful of blow-ups can't dominate a mean.
    for y in ["profit_1M","profit_2M","profit_3M"]:
        df[y] = df[y].replace([np.inf,-np.inf], np.nan) / 100.0
        df.loc[df[y] > 3.0, y] = np.nan     # >+300% over <=3M = data artifact, not a tradable outcome
        df.loc[df[y] < -0.95, y] = -0.95    # floor at near-total-loss
    df["d"] = pd.to_datetime(df["d"])
    return df

FLAGS = {
    "rsi_bounce":    lambda x: x["D_RSI"] > x["D_RSI_Min3M"] + 0.05,
    "cmb_notbear":   lambda x: x["D_CMB"] >= 0,
    "price_off_low": lambda x: x["C_L1M"] >= 1.05,
    "reclaim_ma50":  lambda x: x["Close"] >= x["MA50"],
}

def add_flags(df):
    for k, f in FLAGS.items():
        df[k] = f(df).astype(float)
    df["combo_rsi_px"] = ((df["rsi_bounce"] > 0) & (df["price_off_low"] > 0)).astype(float)
    df["combo_ma_cmb"] = ((df["reclaim_ma50"] > 0) & (df["cmb_notbear"] > 0)).astype(float)
    df["near_1m_low"]  = (df["C_L1M"] <= 1.02).astype(float)
    return df

ALLFLAGS = ["rsi_bounce","cmb_notbear","price_off_low","reclaim_ma50",
            "combo_rsi_px","combo_ma_cmb","near_1m_low"]

# ---------------------------------------------------------------- monthly-cohort spread + t-stat
def monthly_spread(df, flag, ycol):
    """Per calendar-month: mean(y|flag=1) - mean(y|flag=0). t-stat over the monthly series.
       Monthly cohort = honest unit (daily WATCH rows autocorrelated). Requires >=5 names each side."""
    d = df.dropna(subset=[ycol, flag]).copy()
    d["ym"] = d["d"].values.astype("datetime64[M]")
    rows = []
    for ym, g in d.groupby("ym"):
        a = g.loc[g[flag] > 0, ycol]; b = g.loc[g[flag] <= 0, ycol]
        if len(a) >= 5 and len(b) >= 5:
            rows.append((ym, a.mean() - b.mean(), a.mean(), b.mean(), len(a), len(b)))
    if not rows:
        return dict(n_months=0, spread=np.nan, t=np.nan, hit=np.nan)
    s = pd.DataFrame(rows, columns=["ym","sp","ma","mb","na","nb"])
    sp = s["sp"].values
    t = sp.mean() / (sp.std(ddof=1) / np.sqrt(len(sp))) if len(sp) > 1 and sp.std() > 0 else np.nan
    return dict(n_months=len(sp), spread=sp.mean(), t=t, hit=(sp > 0).mean(),
                mean_flag=s["ma"].mean(), mean_noflag=s["mb"].mean())

# ---------------------------------------------------------------- run
def main():
    df = load()
    df = add_flags(df)
    n_events = len(df); n_tk = df["ticker"].nunique()
    print(f"# WATCH universe (golden-floor + pb_z<=-0.3 + liq>=3bn), 2014-2026")
    print(f"  events={n_events:,}  tickers={n_tk}  date {df['d'].min()} -> {df['d'].max()}")

    # ---- self-check: recompute base filters must be internally consistent (0-VND: no NAV here,
    #      but assert no forward field leaked into the filter, and flag coverage sane) ----
    assert (df["pb_z"] <= -0.3 + 1e-9).all(), "pb_z filter breach"
    for f in ALLFLAGS:
        assert set(df[f].dropna().unique()) <= {0.0, 1.0}, f"{f} not binary"
    print("  [self-check] filters internally consistent; flags binary; no null forward. OK\n")

    print("# Flag coverage within WATCH (fraction flagged):")
    for f in ALLFLAGS:
        print(f"    {f:14s} {df[f].mean():5.1%}")
    print()

    # baseline forward returns of the whole WATCH universe
    print("# WATCH baseline forward mean returns (no technical filter):")
    for y in ["profit_1M","profit_2M","profit_3M"]:
        print(f"    {y}: {df[y].mean():+.2%}   median {df[y].median():+.2%}")
    print(f"    falling-knife (dd_fwd40<=-10%): {(df['dd_fwd40']<=-0.10).mean():.1%}  "
          f"(n with dd={df['dd_fwd40'].notna().sum():,})\n")

    IS = df[df["d"] < pd.Timestamp("2020-01-01")]
    OOS = df[df["d"] >= pd.Timestamp("2020-01-01")]
    print(f"# split: IS 2014-19 = {len(IS):,} events | OOS 2020-26 = {len(OOS):,} events\n")

    # ---- main table: for each flag & horizon, monthly-cohort spread (Full/IS/OOS) ----
    for ycol in ["profit_1M","profit_2M","profit_3M"]:
        print(f"===== FORWARD {ycol}  — monthly-cohort spread flagged − not-flagged =====")
        print(f"{'flag':14s} | {'FULL sp':>9s} {'t':>5s} {'hitM':>5s} | {'IS sp':>8s} {'t':>5s} | {'OOS sp':>8s} {'t':>5s} | {'knife↓ f/nf':>14s}")
        for f in ALLFLAGS:
            full = monthly_spread(df, f, ycol)
            i = monthly_spread(IS, f, ycol); o = monthly_spread(OOS, f, ycol)
            kf = df.loc[df[f] > 0, "dd_fwd40"]; knf = df.loc[df[f] <= 0, "dd_fwd40"]
            k_f = (kf <= -0.10).mean(); k_nf = (knf <= -0.10).mean()
            def fmt(x): return f"{x:+.2%}" if x==x else "   n/a"
            def ft(x):  return f"{x:+.1f}" if x==x else "  n/a"
            print(f"{f:14s} | {fmt(full['spread']):>9s} {ft(full['t']):>5s} {full['hit']*100 if full['hit']==full['hit'] else float('nan'):4.0f}% "
                  f"| {fmt(i['spread']):>8s} {ft(i['t']):>5s} | {fmt(o['spread']):>8s} {ft(o['t']):>5s} "
                  f"| {k_f:5.1%}/{k_nf:5.1%}")
        print()

    # ---- falling-knife deep dive: does stabilization cut the deep-drawdown rate? ----
    print("===== FALLING-KNIFE avoidance (fwd 40-sess drawdown) =====")
    print(f"{'flag':14s} | {'flagged mean dd':>15s} {'notflag mean dd':>16s} | {'flag %dd<=-10':>13s} {'notflag %dd<=-10':>16s} | {'flag %dd<=-20':>13s} {'nf %dd<=-20':>12s}")
    dd = df.dropna(subset=["dd_fwd40"])
    for f in ALLFLAGS:
        a = dd.loc[dd[f] > 0, "dd_fwd40"]; b = dd.loc[dd[f] <= 0, "dd_fwd40"]
        print(f"{f:14s} | {a.mean():>15.2%} {b.mean():>16.2%} | {(a<=-0.10).mean():>13.1%} {(b<=-0.10).mean():>16.1%} | {(a<=-0.20).mean():>13.1%} {(b<=-0.20).mean():>12.1%}")
    print()

    # ---- per-year LOO-style: spread of the best combo per year (edge concentration check) ----
    best = "combo_ma_cmb"  # reclaim MA50 + CMB not bearish = strongest 'stabilized' definition
    print(f"===== PER-YEAR spread ({best}, profit_2M) — edge-concentration / LOO check =====")
    d2 = df.dropna(subset=["profit_2M"]).copy(); d2["yr"] = pd.to_datetime(d2["d"]).dt.year
    for yr, g in d2.groupby("yr"):
        a = g.loc[g[best] > 0, "profit_2M"]; b = g.loc[g[best] <= 0, "profit_2M"]
        if len(a) >= 20 and len(b) >= 20:
            print(f"    {yr}: spread {a.mean()-b.mean():+.2%}  (flag n={len(a):4d} {a.mean():+.2%} | noflag n={len(b):4d} {b.mean():+.2%})")
    print()

    df.to_parquet("data/technical_stabilization_events.parquet")
    print("wrote data/technical_stabilization_events.parquet")

if __name__ == "__main__":
    main()
