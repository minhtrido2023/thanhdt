"""Pull panels for FTSE-upgrade re-validation (READ-ONLY, measurement only). Job Taylor_20261013_114456."""
import json, urllib.request
import pandas as pd
from google.cloud import bigquery
PRJ = "lithe-record-440915-m9"; END = "2026-10-12"   # universe_pit max date at run time
c = bigquery.Client(project=PRJ)
q = lambda s: c.query(s).result().to_dataframe()
# A. PIT universe panel (tav2_bq.ticker JOIN universe_pit per day) — same join as macro_state_live._breadth_sql
q(f"""SELECT t.time, t.ticker, COALESCE(t.Price,t.Close)*t.Volume AS turn, t.Close, t.Close_T1, t.MA200,
  t.Volume_3M_P50*COALESCE(t.Price,t.Close) AS liq3m, t.ICB_Code IS NOT NULL AS has_icb
FROM tav2_bq.ticker AS t
JOIN `{PRJ}.tav2_mike.universe_pit` u ON u.ticker=t.ticker AND u.time=t.time AND u.in_universe
WHERE t.time BETWEEN DATE '2013-06-01' AND DATE '{END}'""").to_parquet("panel_pit.parquet")
# B. market-wide turnover (all rows of ticker with ICB) — denominator for foreign share
q(f"""SELECT t.time, SUM(COALESCE(t.Price,t.Close)*t.Volume) AS mkt_turn, COUNT(*) n
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL AND t.time BETWEEN DATE '2013-06-01' AND DATE '{END}'
GROUP BY t.time""").to_parquet("mkt_turn.parquet")
# C. CAPIT panel — production pool/ADV source is STILL ticker_prune (CAPIT_POOL_SOURCE="prune"); measured as-is
q(f"""SELECT p.time, p.ticker, COALESCE(p.Price,p.Close)*p.Volume AS turn, p.ROE_Min5Y, p.ROIC5Y, p.FSCORE
FROM tav2_bq.ticker_prune AS p WHERE p.time BETWEEN DATE '2013-06-01' AND DATE '{END}'""").to_parquet("panel_capit_prune.parquet")
# D. custom30V current members
q("""SELECT c.ticker, c.weight, c.liq_rank, c.rebal_date FROM tav2_bq.custom30v_8l AS c
WHERE c.rebal_date=(SELECT MAX(c2.rebal_date) FROM tav2_bq.custom30v_8l AS c2)""").to_csv("custom30v_members.csv", index=False)
# E. DT5G live state
q("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s WHERE s.time>='2014-01-01' ORDER BY s.time""").to_csv("dt5g_live.csv", index=False)
# F. foreign flow VNINDEX (VNDirect finfo, depth 2018-08-30; includes put-through blocks)
rows, page = [], 1
while True:
    url = ("https://api-finfo.vndirect.com.vn/v4/foreigns?q=code:VNINDEX~tradingDate:gte:2018-01-01"
           f"&sort=tradingDate:asc&size=1000&page={page}")
    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Referer": "https://dstock.vndirect.com.vn/"}), timeout=40))
    rows += r["data"]
    if page >= r["totalPages"]: break
    page += 1
pd.DataFrame(rows).to_csv("foreign_vnindex_vndirect.csv", index=False)
print("ok", len(rows))
