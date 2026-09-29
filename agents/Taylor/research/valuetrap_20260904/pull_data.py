#!/usr/bin/env python3
"""Pull PIT data for baseline-vs-golden-floor test on the ACTUAL custom30V admission funnel
(rating<=3 gate + yieldcombo, top-60 liquid pool -> top-30 by rank(1/PE)+rank(1/PCF)).
Mirrors custom_basket.py's build_pit() conventions (raw Price for selection/weight,
adjusted Close for return leg) but is a STANDALONE read-only script -- does not touch the
production module. Quarterly avg PE/PCF/liquidity per (ticker,quarter), same as custom_basket's
_yield_piv/liq_piv. ROE_Min3Y / CF_OA_P0..P3 read directly off tav2_bq.ticker (same cadence as
PE -- already-verified PIT-correct per CLAUDE.md), NOT Release_Date-staggered like custom_basket's
QFLOOR knob -- documented simplification for a screening-level test.
"""
import subprocess, tempfile, os
import pandas as pd

WORKDIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = "lithe-record-440915-m9"

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=csv",
                               "--max_rows=10000000", f"--project_id={PROJECT}"],
                              stdin=open(tmp), capture_output=True, text=True, timeout=600)
        if out.returncode != 0:
            raise RuntimeError(out.stderr)
        from io import StringIO
        return pd.read_csv(StringIO(out.stdout))
    finally:
        os.unlink(tmp)

START, END = "2014-01-01", "2026-09-03"

print("[1/5] fa_ratings_8l (PIT rating history)...")
rat = bq(f"""SELECT ticker, time AS eff_date, rating FROM tav2_bq.fa_ratings_8l
WHERE time <= DATE '{END}' ORDER BY ticker, eff_date""")
rat.to_csv(f"{WORKDIR}/fa_ratings_8l.csv", index=False)
print(f"  rows={len(rat)} tickers={rat.ticker.nunique()} range={rat.eff_date.min()}..{rat.eff_date.max()}")

print("[2/5] quarterly PE/PCF/liquidity + ROE_Min3Y/CF_OA_TTM (avg per ticker-quarter)...")
q = bq(f"""
SELECT t.ticker AS ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(SAFE_DIVIDE(1, t.PE)) AS ey,
  AVG(SAFE_DIVIDE(1, t.PCF)) AS cfy,
  AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) AS liq,
  AVG(t.ROE_Min3Y) AS roe_min3y,
  AVG(t.CF_OA_P0 + t.CF_OA_P1 + t.CF_OA_P2 + t.CF_OA_P3) AS cfo_ttm
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.ticker != 'VNINDEX'
  AND (t.PE > 0 OR t.PCF > 0 OR t.Volume_3M_P50 IS NOT NULL)
GROUP BY t.ticker, q""")
q.to_csv(f"{WORKDIR}/quarterly_panel.csv", index=False)
print(f"  rows={len(q)} tickers={q.ticker.nunique()}")

print("[3/5] daily adjusted Close (return leg) for all tickers ever in panel...")
tks = sorted(q.ticker.unique().tolist())
tk_list = ",".join(f"'{t}'" for t in tks)
px = bq(f"""SELECT t.ticker AS ticker, t.time AS time, t.Close AS Close FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tk_list}) AND t.time BETWEEN DATE '{START}' AND DATE '{END}'""")
px.to_csv(f"{WORKDIR}/daily_close.csv", index=False)
print(f"  rows={len(px)} tickers={px.ticker.nunique()}")

print("[4/5] VNINDEX daily close (benchmark)...")
vni = bq(f"""SELECT t.time AS time, t.Close AS Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX'
AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time""")
vni.to_csv(f"{WORKDIR}/vnindex.csv", index=False)
print(f"  rows={len(vni)}")

print("[5/5] done.")
