WITH cal AS (
  SELECT t.time FROM tav2_bq.ticker AS t
  WHERE t.ticker = "VNINDEX" AND t.time BETWEEN "2015-06-01" AND "2026-07-24"
  QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC(t.time, MONTH) ORDER BY t.time DESC) = 1
),
px AS (
  SELECT t.time, t.ticker, t.Close, t.PE, t.PB, t.Volume_1M
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN "2015-06-01" AND "2026-07-24" AND t.ticker <> "VNINDEX"
),
fw AS (
  SELECT p.time, p.ticker, p.Close, p.PE, p.PB, p.Volume_1M,
    LEAD(p.Close, 20) OVER (PARTITION BY p.ticker ORDER BY p.time) AS c20,
    LEAD(p.Close, 60) OVER (PARTITION BY p.ticker ORDER BY p.time) AS c60
  FROM px p
),
base AS (
  SELECT f.* FROM fw f JOIN cal c ON f.time = c.time
),
univ AS (
  SELECT u.time, u.ticker FROM tav2_mike.universe_pit AS u
  WHERE u.in_universe AND u.time BETWEEN "2015-06-01" AND "2026-07-24"
),
ins AS (
  SELECT i.ticker, i.public_date,
    i.trader_person_id AS pid,
    IF(i.action_code = "S", -ABS(i.share_acquire), ABS(i.share_acquire)) AS qty
  FROM tav2_bq.insider_transaction AS i
  WHERE i.event_code IN ("DDIND","DDRP")
    AND i.action_code IN ("B","S")
    AND i.trade_status = "Đã thực hiện xong"
    AND i.share_acquire IS NOT NULL AND ABS(i.share_acquire) > 0
),
agg AS (
  SELECT c.time, x.ticker,
    SUM(IF(x.public_date > DATE_SUB(c.time, INTERVAL 180 DAY), x.qty, 0)) AS net_sh_180,
    SUM(IF(x.public_date > DATE_SUB(c.time, INTERVAL 90 DAY), x.qty, 0)) AS net_sh_90,
    COUNT(DISTINCT IF(x.public_date > DATE_SUB(c.time, INTERVAL 180 DAY) AND x.qty > 0, x.pid, NULL)) AS nbuy_180,
    COUNT(DISTINCT IF(x.public_date > DATE_SUB(c.time, INTERVAL 180 DAY) AND x.qty < 0, x.pid, NULL)) AS nsell_180,
    COUNT(DISTINCT IF(x.public_date > DATE_SUB(c.time, INTERVAL 90 DAY) AND x.qty > 0, x.pid, NULL)) AS nbuy_90,
    COUNT(DISTINCT IF(x.public_date > DATE_SUB(c.time, INTERVAL 90 DAY) AND x.qty < 0, x.pid, NULL)) AS nsell_90,
    COUNTIF(x.public_date > DATE_SUB(c.time, INTERVAL 180 DAY)) AS nevt_180
  FROM cal c JOIN ins x
    ON x.public_date <= c.time AND x.public_date > DATE_SUB(c.time, INTERVAL 180 DAY)
  GROUP BY 1,2
),
osh AS (
  SELECT q.ticker, q.time, q.OShares
  FROM tav2_bq.ticker_financial AS q WHERE q.OShares > 0
),
rat AS (
  SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l AS r
),
osh_asof AS (
  SELECT c.time AS d, o.ticker, o.OShares
  FROM cal c JOIN osh o ON o.time <= c.time
  QUALIFY ROW_NUMBER() OVER (PARTITION BY c.time, o.ticker ORDER BY o.time DESC) = 1
),
rat_asof AS (
  SELECT c.time AS d, r.ticker, r.rating
  FROM cal c JOIN rat r ON r.time <= c.time
  QUALIFY ROW_NUMBER() OVER (PARTITION BY c.time, r.ticker ORDER BY r.time DESC) = 1
)
SELECT
  b.time, b.ticker, b.Close, b.PE, b.PB, b.Volume_1M,
  SAFE_DIVIDE(b.c20, b.Close) - 1 AS fwd20,
  SAFE_DIVIDE(b.c60, b.Close) - 1 AS fwd60,
  IFNULL(a.net_sh_180, 0) AS net_sh_180,
  IFNULL(a.net_sh_90, 0) AS net_sh_90,
  IFNULL(a.nbuy_180, 0) AS nbuy_180,
  IFNULL(a.nsell_180, 0) AS nsell_180,
  IFNULL(a.nbuy_90, 0) AS nbuy_90,
  IFNULL(a.nsell_90, 0) AS nsell_90,
  IFNULL(a.nevt_180, 0) AS nevt_180,
  oa.OShares AS oshares,
  ra.rating AS rating8l
FROM base b
JOIN univ u ON u.time = b.time AND u.ticker = b.ticker
LEFT JOIN agg a ON a.time = b.time AND a.ticker = b.ticker
LEFT JOIN osh_asof oa ON oa.d = b.time AND oa.ticker = b.ticker
LEFT JOIN rat_asof ra ON ra.d = b.time AND ra.ticker = b.ticker
WHERE b.Close > 0
ORDER BY b.time, b.ticker
