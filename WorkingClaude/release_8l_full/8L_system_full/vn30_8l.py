#!/usr/bin/env python3
"""vn30_8l.py — build the deployable "8L-VN30" basket and cache it for the Telegram bot.

The 8L composite ranking (data/rank_8l.csv) tilts to quality but its top names are mostly
illiquid; this carves out an INVESTABLE 30-stock basket = the highest-8L-score names that
clear a real liquidity floor (>=10B VND/day), equal-weighted, quarterly-rebalanced.

Backtest (backtest_8l_vn30.py, 2014-2026): vs VN30 the edge is DEFENSIVE (MaxDD ~10pp shallower,
higher Calmar) not return alpha; the real lever is the DT5G market gate, applied at display time.
30 names is the size sweet-spot (20 is worse — quality is a broad defensive tilt, not top-N alpha).

Run EOD in pt_8l_daily.bat (after rank_8l.py). Output: data/vn30_8l.csv.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess
from io import StringIO
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
RANK_CSV = os.path.join(WORKDIR, "data", "rank_8l.csv")
OUT_CSV = os.path.join(WORKDIR, "data", "vn30_8l.csv")
PROJECT = "lithe-record-440915-m9"
LIQ_FLOOR = 10.0     # billion VND/day
N = 30

def _bq(sql):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); p = f.name
    try:
        cmd = f'bq query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=5000 < "{p}"'
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(p)
    return pd.read_csv(StringIO(out.stdout))

def _liquidity(tickers):
    """Latest real daily liquidity (B VND/day) per ticker = Volume_3M_P50 * unadjusted Price."""
    inlist = ",".join(f'"{t}"' for t in tickers)
    sql = f"""
    WITH latest AS (
      SELECT t.ticker, t.Volume_3M_P50 * COALESCE(t.Price, t.Close)/1e9 AS liq,
             ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
      FROM tav2_bq.ticker_1m t
      WHERE t.ticker IN ({inlist}) AND t.time >= DATE "2024-01-01"
    )
    SELECT ticker, ROUND(liq,2) AS liq FROM latest WHERE rn=1"""
    return _bq(sql)

def build():
    rank = pd.read_csv(RANK_CSV)
    liq = _liquidity(rank["ticker"].tolist())
    m = rank.merge(liq, on="ticker", how="left")
    m["liq"] = m["liq"].fillna(m.get("liqB"))      # BQ liquidity primary; rank's liqB as fallback
    elig = m[m["liq"] >= LIQ_FLOOR].sort_values("rank").head(N).copy()
    elig["weight"] = 1.0 / len(elig)
    elig["basket_rank"] = range(1, len(elig) + 1)
    cols = ["basket_rank", "ticker", "route", "score", "verdict", "liq", "weight"]
    elig[cols].to_csv(OUT_CSV, index=False)
    return elig[cols]

def main():
    df = build()
    print(f"8L-VN30 basket — {len(df)} names, EW {100/len(df):.2f}%/name, liq>={LIQ_FLOOR:.0f}B/day")
    print(df.to_string(index=False))
    print(f"\nSaved {OUT_CSV}")

if __name__ == "__main__":
    main()
