SELECT Release_Date, COUNT(*) AS n, ANY_VALUE(quarter) AS q_example FROM tav2_bq.ticker_financial
WHERE time BETWEEN '2010-01-01' AND '2014-12-31' AND Release_Date IS NOT NULL GROUP BY 1 ORDER BY n DESC LIMIT 12
