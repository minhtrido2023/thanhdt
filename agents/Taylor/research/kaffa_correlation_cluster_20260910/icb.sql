WITH uni AS (
  SELECT ticker FROM tav2_mike.universe_pit
  WHERE time = (SELECT MAX(time) FROM tav2_mike.universe_pit) AND in_universe
),
counted AS (
  SELECT ca.ticker, ca.icb_code_lv1, COUNT(*) n
  FROM tav2_bq.corporate_action AS ca
  JOIN uni ON uni.ticker = ca.ticker
  WHERE ca.icb_code_lv1 IS NOT NULL
  GROUP BY 1,2
),
ranked AS (
  SELECT ticker, icb_code_lv1, n,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY n DESC) rn
  FROM counted
)
SELECT ticker, icb_code_lv1 FROM ranked WHERE rn=1
