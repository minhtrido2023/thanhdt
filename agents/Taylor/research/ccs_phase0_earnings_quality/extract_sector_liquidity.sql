-- Phase 0b V1/V2: sector (ICB_Code, full universe via `ticker`) + self-built ADV_30d
-- (AVG(Volume*Close) over the 30 calendar days ending at Release_Date, also via `ticker` since
-- Trading_Value_1M_P50 only lives in ticker_1m/ticker_prune, both of which are ALREADY
-- quality-filtered and would drop most of the 19.8% floor-excluded names before we even look).
-- Same PIT window convention as extract.sql (<=Release_Date, within 7d) for ICB_Code.
WITH funda AS (
  SELECT ticker, quarter, Release_Date
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial`
  WHERE Release_Date IS NOT NULL AND quarter IS NOT NULL
    AND EXTRACT(YEAR FROM Release_Date) >= 2014
),
icb AS (
  SELECT
    f.ticker, f.quarter, f.Release_Date,
    t.ICB_Code
  FROM funda f
  LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker` t
    ON t.ticker = f.ticker
   AND t.time <= f.Release_Date
   AND t.time >= DATE_SUB(f.Release_Date, INTERVAL 7 DAY)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) = 1
),
adv AS (
  SELECT
    f.ticker, f.quarter, f.Release_Date,
    AVG(t.Volume * t.Close) AS adv_30d,
    COUNT(*) AS n_days_30d
  FROM funda f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` t
    ON t.ticker = f.ticker
   AND t.time <= f.Release_Date
   AND t.time >= DATE_SUB(f.Release_Date, INTERVAL 30 DAY)
  GROUP BY f.ticker, f.quarter, f.Release_Date
)
SELECT icb.ticker, icb.quarter, icb.Release_Date, icb.ICB_Code, adv.adv_30d, adv.n_days_30d
FROM icb
LEFT JOIN adv USING (ticker, quarter, Release_Date)
ORDER BY ticker, quarter
