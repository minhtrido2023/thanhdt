"""Pull hourly time-travel vintages (last ~7d) of ticker_financial (quarter 2026Q3) and fa_ratings_8l
(time>=2026-10-01) -> first-seen timestamp per key. Read-only. Output raw/tt_*.csv."""
import subprocess, io, sys, datetime as dt
import pandas as pd
from zoneinfo import ZoneInfo
ICT = ZoneInfo("Asia/Ho_Chi_Minh"); OUT = sys.argv[1]
P = "lithe-record-440915-m9"
def bq(sql):
    r = subprocess.run(["bq","query","--use_legacy_sql=false",f"--project_id={P}","--format=csv","--quiet","--max_rows=100000",sql],
                       capture_output=True, text=True)
    if r.returncode: return None
    return pd.read_csv(io.StringIO(r.stdout)) if r.stdout.strip() else pd.DataFrame()
now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
t = now - dt.timedelta(hours=167)
tf, fa = [], []
while t <= now:
    ts = t.strftime("%Y-%m-%d %H:%M:%S")
    a = bq(f"SELECT ticker, quarter, CAST(time AS STRING) time, CAST(Release_Date AS STRING) rd FROM tav2_bq.ticker_financial FOR SYSTEM_TIME AS OF TIMESTAMP('{ts}+00') WHERE quarter='2026Q3'")
    b = bq(f"SELECT ticker, CAST(time AS STRING) time, rating FROM tav2_bq.fa_ratings_8l FOR SYSTEM_TIME AS OF TIMESTAMP('{ts}+00') WHERE time>='2026-10-01'")
    ict = t.astimezone(ICT).strftime("%Y-%m-%d %H:%M")
    for d, L in ((a, tf), (b, fa)):
        if d is not None: d["snap_ict"] = ict; L.append(d)
    print(ict, None if a is None else len(a), None if b is None else len(b), flush=True)
    t += dt.timedelta(hours=1)
pd.concat(tf).to_csv(f"{OUT}/tt_ticker_financial_2026Q3.csv", index=False)
pd.concat(fa).to_csv(f"{OUT}/tt_fa_ratings_8l_202610.csv", index=False)
