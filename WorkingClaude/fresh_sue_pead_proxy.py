"""#23 PROXY (cheap, no harness): fresh high-SUE PEAD tilt for the LAG book.
Signal: SUE = NP_P0/NP_P4-1 (YoY earnings surprise, NP_P4>0) + freshness = ID_Current-ID_Release (sessions
since the earnings release). PEAD thesis: drift is concentrated in FRESH (recently-reported) HIGH-SUE names.

User flag: median is flat in-sample -> don't trust median; dig tercile winrate + IC, and walk-forward IS/OOS.
Event panel: ONE obs per (ticker, ID_Release) at the ENTRY window (freshness in [5,10], mirrors LAG T+5 entry),
liquid (Volume_3M_P50*Close >= 1bn/day). Forward = profit_1M (T+20) and profit_2M (T+40). Direct-parquet read.

Tests:
 (1) SUE tercile (within calendar quarter) forward return — top vs bottom, IS(<2020)/OOS(>=2020). PASS if
     top-tercile beats bottom in BOTH halves (the SUE edge is real & robust).
 (2) Spearman IC of SUE vs forward, IS/OOS.
 (3) Freshness validation: SUE edge among FRESH ([5,10]) vs STALE (>60 sessions) — PEAD should be stronger fresh.
"""
import os, sys
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd, duckdb
c = duckdb.connect()
TP = "data/bq_cache/ticker_prune/*.parquet"

# entry-window event panel: per (ticker, ID_Release) the first row with freshness in [5,10]; plus a stale set.
df = c.execute(f"""
WITH base AS (
  SELECT ticker, time, ID_Current - ID_Release AS fresh,
         CASE WHEN NP_P4>0 THEN NP_P0/NP_P4 - 1 ELSE NULL END AS sue,
         profit_1M, profit_2M, ID_Release,
         DATE_TRUNC('quarter', time) AS cq
  FROM read_parquet('{TP}')
  WHERE time>=DATE '2014-01-01' AND profit_1M IS NOT NULL AND NP_P4>0 AND NP_P0 IS NOT NULL
    AND Volume_3M_P50*Close >= 1e9 AND ID_Release IS NOT NULL AND ID_Current IS NOT NULL)
SELECT * FROM base WHERE sue IS NOT NULL
""").df()
df["time"] = pd.to_datetime(df["time"])
print(f"loaded {len(df)} liquid name-day rows with SUE+freshness, 2014+")

def panel(lo, hi):
    """one obs per (ticker, ID_Release): first row with freshness in [lo,hi]."""
    s = df[(df["fresh"]>=lo) & (df["fresh"]<=hi)].sort_values(["ticker","ID_Release","fresh"])
    return s.groupby(["ticker","ID_Release"]).first().reset_index()

def tercile_report(p, label):
    p = p.dropna(subset=["sue","profit_1M"]).copy()
    # SUE tercile within each calendar quarter (remove regime/level bias)
    p["terc"] = p.groupby("cq")["sue"].transform(lambda s: pd.qcut(s, 3, labels=["lo","mid","hi"], duplicates="drop") if s.nunique()>=3 else np.nan)
    p["era"] = np.where(p["time"]<"2020-01-01", "IS", "OOS")
    print(f"\n=== {label}: {len(p)} events ({(p.era=='IS').sum()} IS / {(p.era=='OOS').sum()} OOS) ===")
    print(f"{'era':>4} {'terc':>5} {'n':>5} {'win1M%':>7} {'mean1M%':>8} {'mean2M%':>8}")
    for era in ["IS","OOS"]:
        for t in ["lo","hi"]:
            g = p[(p.era==era)&(p.terc==t)]
            if len(g):
                print(f"{era:>4} {t:>5} {len(g):>5} {(g.profit_1M>0).mean()*100:>6.0f}% {g.profit_1M.mean():>7.2f}% {g.profit_2M.mean():>7.2f}%")
        # hi-minus-lo spread
        hi=p[(p.era==era)&(p.terc=='hi')]; lo=p[(p.era==era)&(p.terc=='lo')]
        if len(hi) and len(lo):
            print(f"     -> {era} hi-lo spread: 1M {hi.profit_1M.mean()-lo.profit_1M.mean():+.2f}pp | 2M {hi.profit_2M.mean()-lo.profit_2M.mean():+.2f}pp")
    # Spearman IC of SUE vs fwd, per era
    for era in ["IS","OOS"]:
        g=p[p.era==era]
        ic1=g[["sue","profit_1M"]].rank().corr().iloc[0,1]; ic2=g[["sue","profit_2M"]].rank().corr().iloc[0,1]
        print(f"     {era} Spearman IC(SUE,fwd): 1M {ic1:+.3f} | 2M {ic2:+.3f}")

tercile_report(panel(5,10),  "FRESH high-SUE (entry freshness 5-10 sessions)")
tercile_report(panel(61,120),"STALE control (freshness 61-120) — PEAD should be WEAKER here")
print("\nREAD: PASS if FRESH hi-tercile beats lo in BOTH IS & OOS (1M/2M) AND IC>0 both halves AND fresh edge")
print(">> stale edge. If flat/OOS-only/no-better-than-stale -> not robust -> do NOT wire to LAG harness.")
