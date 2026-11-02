-- Cổ tức TIỀN MẶT (event_code DIV; value_per_share = VND/cp gộp) — loại not_executed; dedup theo (ticker, exright_date, value).
SELECT c.ticker, c.exright_date, c.payout_date, c.dividend_year, c.dividend_stage_vi, c.event_status, c.issue_status_vi,
       MAX(c.value_per_share) AS dps, COUNT(*) AS n_dup, ANY_VALUE(SUBSTR(c.event_title_vi,1,100)) AS ttl
FROM tav2_bq.corporate_action AS c
WHERE c.event_code = 'DIV'
  AND c.ticker IN (SELECT DISTINCT t.ticker FROM tav2_bq.ticker AS t WHERE t.ICB_Code = 7535 AND t.time >= '2019-01-01' UNION DISTINCT SELECT 'TV1')
  AND c.exright_date >= '2015-01-01'
  AND IFNULL(c.event_status,'') != 'not_executed'
GROUP BY 1,2,3,4,5,6,7, c.value_per_share
ORDER BY c.ticker, c.exright_date
