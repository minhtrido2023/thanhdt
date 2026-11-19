"""Chụp 1 lần (19/11/2026) dữ liệu cần cho A4 vào parquet cục bộ, source tường minh (KHÔNG dùng commodity_latest/unified).
macro_indicator KHÔNG có vintage ⇒ giá trị là bản hiện hành (có thể đã revise); độ trễ công bố là GIẢ ĐỊNH (map_v2.csv)."""
import subprocess,io,pandas as pd
def bq(sql):
    out=subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9','--format=csv','--max_rows=1000000',sql],capture_output=True,text=True,check=True).stdout
    return pd.read_csv(io.StringIO(out))
C=bq("""SELECT metric_key,source,observation_date,value FROM tav2_bq.commodity_prices WHERE cadence='daily' AND (
 (source='trading_economics' AND metric_key IN ('steel','iron_ore_cny','corn','polyvinyl')) OR
 (source='sunsirs' AND metric_key IN ('coke','soybean_meal_cny','yellow_phosphorus','caustic_soda','polyester_staple_fiber','pta','ethylene_glycol')))""")
C.to_parquet('commodity_snapshot_20261119.parquet',index=False)
M=bq("""SELECT series_key,observation_date,value FROM tav2_bq.macro_indicator WHERE series_key IN
 ('vn_usdvnd','cn_usdcny','vn_retail_sales_yoy','vn_tourist_arrivals','vn_exports','vn_imports','vn_car_registrations','vn_interbank_3m','vn_policy_rate','vn_bond_10y')""")
M.to_parquet('macro_snapshot_20261119.parquet',index=False)
print(C.groupby(['metric_key','source']).observation_date.agg(['min','max','count']).to_string())
print(M.groupby('series_key').observation_date.agg(['min','max','count']).to_string())
