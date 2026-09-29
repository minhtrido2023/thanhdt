#!/usr/bin/env python3
"""Pull + cache every BQ input for the Top-5-post-earnings sleeve backtest.

Idempotent: skips a pull whose parquet already exists (delete the file to refresh).
Run with $DNA_PYEXE (/home/trido/thanhdt/wc_venv/bin/python).
"""
import os, sys, subprocess, tempfile
from io import StringIO
import pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PROJECT = "lithe-record-440915-m9"
BQ_BIN = os.environ.get("BQ_BIN", "bq")
START = "2014-01-01"
END = "2026-08-18"          # pinned vintage: max(tav2_bq.ticker.time) at run time


def bq(sql, max_rows=8_000_000):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'cat "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows={max_rows}',
                           capture_output=True, text=True, timeout=3600, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip():
        raise RuntimeError("bq no rows. stderr:\n" + r.stderr[-2000:])
    return pd.read_csv(StringIO(r.stdout.strip()))


def cached(name, sql, **kw):
    p = os.path.join(DATA, name + ".parquet")
    if os.path.exists(p):
        print(f"  [cache] {name}", flush=True); return pd.read_parquet(p)
    print(f"  [bq]    {name} ...", flush=True)
    df = bq(sql, **kw)
    df.to_parquet(p, index=False)
    print(f"          -> {len(df):,} rows", flush=True)
    return df


# fund is read ONLY at the 49 rebalance dates (engine.py does `fund[fund["time"] == D]` per
# season) — seasons.csv is a pre-existing local artifact, not itself a BQ pull.
_seasons_csv = os.path.join(DATA, "seasons.csv")
if os.path.exists(_seasons_csv):
    _REBAL_DATES = sorted(pd.read_csv(_seasons_csv)["rebal"].unique())
else:
    _REBAL_DATES = []
_REBAL_DATES_SQL = ", ".join(f"DATE '{d}'" for d in _REBAL_DATES)

QUERIES = {
    # trading calendar (VNINDEX is the market clock)
    "calendar": f"""
SELECT t.time FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}'
ORDER BY t.time""",

    # daily adjusted close for the whole market (returns) + raw Price (audit)
    "px": f"""
SELECT t.ticker, t.time, t.Close, t.Price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.Close IS NOT NULL""",

    # gate inputs, read ONLY at the 49 rebalance dates (engine.py never reads fund at any other
    # date). Column set/order + date scope pinned to match the cached fund.parquet exactly
    # (verified: t.time IN <49 rebal dates> gives 52,767 rows == cached row count; CTG @
    # 2026-08-10 byte-matches cached PE/PCF/PB/EVEB/ROE_Min3Y/CF_OA_5Y/Price/Close).
    "fund": f"""
SELECT t.ticker, t.time, t.ICB_Code, t.PE, t.PCF, t.PB, t.EVEB,
       t.ROE_Min3Y, t.CF_OA_5Y, t.Price, t.Close
FROM tav2_bq.ticker AS t
WHERE t.time IN ({_REBAL_DATES_SQL})
  AND t.ticker != 'VNINDEX'""",

    # release-date fundamentals, quarterly (source for engine.py's finp merge_asof: PS_rel carried
    # forward by price ratio, CF_OA_3Y for the golden floor). Renamed to avoid colliding with
    # fund's own daily PE/PCF/ROE_Min3Y after the merge. Lower bound 2012-01-01 (2 years before
    # module START) so merge_asof(direction='backward') has release history for early 2014Q2+
    # seasons. Verified: this exact range gives 59,907 rows == cached row count, min/max
    # release_date 2012-01-17/2026-08-14 match exactly; CTG @ 2026-07-30 byte-matches cached
    # PE_rel/PS_rel/PCF_rel/CF_OA_3Y/ROE_Min3Y_f.
    "fin": f"""
SELECT f.ticker, f.time AS release_date, f.quarter,
       f.PE AS PE_rel, f.PS AS PS_rel, f.PCF AS PCF_rel,
       f.CF_OA_3Y, f.ROE_Min3Y AS ROE_Min3Y_f, f.EPS_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.time BETWEEN DATE '2012-01-01' AND DATE '{END}'""",

    "universe_pit": f"""
SELECT u.time, u.ticker, u.in_universe FROM tav2_mike.universe_pit AS u
WHERE u.time BETWEEN DATE '{START}' AND DATE '{END}' AND u.in_universe""",

    "ratings8l": """
SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l AS r ORDER BY r.ticker, r.time""",

    "dt5g": """
SELECT s.time, s.state, s.state_raw FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time""",

    # release calendar: ticker_financial.time IS Release_Date (verified 2026-08-18)
    "fin_rel": f"""
SELECT f.ticker, f.quarter, f.time AS release_date, f.Release_Date AS rd_col
FROM tav2_bq.ticker_financial AS f
WHERE f.time BETWEEN DATE '2013-01-01' AND DATE '{END}'""",
}

if __name__ == "__main__":
    only = sys.argv[1:] or list(QUERIES)
    for k in only:
        cached(k, QUERIES[k])
    print("done")
