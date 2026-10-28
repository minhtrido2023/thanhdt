WITH qd AS (SELECT DATE_TRUNC(time, QUARTER) AS q, MAX(time) AS d FROM tav2_mike.universe_pit
            WHERE time BETWEEN '2008-01-01' AND '2019-12-31' GROUP BY q),
u AS (SELECT qd.q, p.ticker FROM tav2_mike.universe_pit AS p JOIN qd ON p.time = qd.d WHERE p.in_universe),
fin AS (SELECT DISTINCT ticker, DATE_TRUNC(time, QUARTER) AS q FROM tav2_bq.ticker_financial),
last_seen AS (SELECT ticker, MAX(time) AS last_t FROM tav2_pin.ticker_pin_202610 GROUP BY ticker)
SELECT u.q, COUNT(*) AS n_univ,
  COUNTIF(fin.ticker IS NOT NULL) AS n_univ_with_fin_row,
  COUNTIF(ls.last_t < '2020-01-01') AS n_univ_delisted_before_2020,
  COUNTIF(ls.ticker IS NULL) AS n_univ_absent_from_pin202610
FROM u LEFT JOIN fin ON fin.ticker = u.ticker AND fin.q = u.q
LEFT JOIN last_seen AS ls ON ls.ticker = u.ticker
GROUP BY u.q ORDER BY u.q
