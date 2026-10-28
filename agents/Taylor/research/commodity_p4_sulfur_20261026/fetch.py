"""B1: kéo P4 (sunsirs) + sulfur (TE daily) + phosphate_rock_cny/di_ammonium (TE daily) + WB phosphate_rock/dap — source/cadence TƯỜNG MINH, không dùng commodity_latest."""
import subprocess, io, pandas as pd, os
O=os.path.dirname(os.path.abspath(__file__))
q="""SELECT metric_key, source, cadence, observation_date, value, unit, change_pct, fetched_at FROM tav2_bq.commodity_prices
WHERE (metric_key='yellow_phosphorus' AND source='sunsirs' AND cadence='daily')
 OR (metric_key IN ('sulfur','phosphate_rock_cny','di_ammonium','urea','coal') AND source='trading_economics' AND cadence='daily')
 OR (metric_key IN ('phosphate_rock','dap','sulphur') AND source='worldbank_cmo')
ORDER BY metric_key, source, observation_date"""
env="source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null 2>&1; "
out=subprocess.run(["bash","-c",env+f"bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=1000000 \"{q}\""],capture_output=True,text=True,check=True).stdout
df=pd.read_csv(io.StringIO(out),parse_dates=['observation_date'])
assert not df.duplicated(['metric_key','source','cadence','observation_date']).any()
print(df.groupby(['metric_key','source','cadence']).observation_date.agg(['count','min','max']))
df.to_parquet(f"{O}/raw.parquet")
