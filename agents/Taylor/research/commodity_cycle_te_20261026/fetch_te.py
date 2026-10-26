"""Kéo TE daily (source/cadence tường minh, KHÔNG dùng commodity_latest/unified) -> te_daily.parquet."""
import subprocess, io, pandas as pd, sys, os
O=os.path.dirname(os.path.abspath(__file__))
q="""SELECT metric_key, observation_date, value, unit FROM tav2_bq.commodity_prices
WHERE source='trading_economics' AND cadence='daily' ORDER BY metric_key, observation_date"""
env="source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null 2>&1; "
out=subprocess.run(["bash","-c",env+f"bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=1000000 \"{q}\""],capture_output=True,text=True,check=True).stdout
df=pd.read_csv(io.StringIO(out),parse_dates=['observation_date'])
print(df.shape, df.metric_key.nunique(), df.observation_date.min(), df.observation_date.max())
assert not df.duplicated(['metric_key','observation_date']).any()
df.to_parquet(f"{O}/te_daily.parquet")
