SELECT c.ticker, c.exright_date, c.dividend_year, MAX(c.value_per_share) AS dps
FROM tav2_bq.corporate_action AS c
WHERE c.event_code='DIV' AND c.ticker IN ('TV2','TV3','TV4') AND c.exright_date>='2019-01-01' AND IFNULL(c.event_status,'')!='not_executed'
GROUP BY 1,2,3 ORDER BY 1,2
