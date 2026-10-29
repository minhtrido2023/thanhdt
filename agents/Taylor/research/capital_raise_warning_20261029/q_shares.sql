# Tăng số CP 12 tháng = OShares quý gần nhất / OShares 4 quý trước − 1, mã có trong ticker_1m (đang GD).
WITH f AS (SELECT t.ticker, t.time, t.quarter, t.OShares,
             LAG(t.OShares, 4) OVER (PARTITION BY t.ticker ORDER BY t.time) os4,
             ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
           FROM tav2_bq.ticker_financial AS t WHERE t.OShares > 0),
live AS (SELECT DISTINCT m.ticker FROM tav2_bq.ticker_1m AS m)
SELECT f.ticker, f.quarter, f.OShares, f.os4, SAFE_DIVIDE(f.OShares, f.os4) - 1 g12
FROM f JOIN live USING (ticker) WHERE f.rn = 1 AND f.os4 > 0
