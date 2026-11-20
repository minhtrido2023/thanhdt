"""Kéo dữ liệu BQ MỘT lần vào data/*.csv (cache bất biến). Job Taylor_20261030_034654. Rổ = tav2_mike.universe_pit (KHÔNG ticker_prune)."""
import os, subprocess, io
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); P = "lithe-record-440915-m9"

def q(sql):
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={P}", "--format=csv", "--max_rows=1000000", sql],
                         capture_output=True, text=True, check=True).stdout
    return pd.read_csv(io.StringIO(out))

DATES = """WITH d AS (SELECT DISTINCT time FROM tav2_mike.universe_pit WHERE time >= '2014-01-01'),
qe AS (SELECT MAX(time) AS time FROM d GROUP BY DATE_TRUNC(time, QUARTER) UNION DISTINCT SELECT DATE '2026-10-29')"""
snap = q(DATES + """
SELECT t.time, t.ticker, t.Price, t.PE, t.PB, t.OShares, t.ROE5Y, t.ICB_Code
FROM tav2_bq.ticker AS t JOIN tav2_mike.universe_pit AS u ON u.ticker = t.ticker AND u.time = t.time
WHERE u.in_universe AND t.time IN (SELECT time FROM qe) ORDER BY t.time, t.ticker""")
snap.to_csv(os.path.join(HERE, "data", "snap_universe_pit_qe.csv"), index=False)
vni = q("""SELECT v.time, v.Close AS vnindex, v.VNINDEX_PE FROM tav2_bq.ticker AS v
WHERE v.ticker = 'VNINDEX' AND v.time >= '2007-12-01' ORDER BY v.time""")
vni.to_csv(os.path.join(HERE, "data", "vnindex_daily.csv"), index=False)
print(len(snap), snap.time.nunique(), snap.time.max(), len(vni), vni.time.min(), vni.time.max())
