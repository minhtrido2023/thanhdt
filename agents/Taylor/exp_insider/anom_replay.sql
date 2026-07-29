-- Tai tao cac quy tac gia/khoi luong cua anomaly_scan.py::compute_signals tren LICH SU,
-- roi ap dung cua so TTL cua anomaly_gate.py::anomaly_excluded (lo <= last_alert <= asof, ttl=30d).
-- Nguong copy nguyen van tu anomaly_scan.py (LIQ_1M_BN=3.0; real_trade val_bn>=0.3).
-- Hai bien the:
--   a_w = nhanh tier W (~ung vien MUA, chua nam giu) — dung nguong CHAT (co gate thanh khoan)
--   a_h = nhanh tier H (dang nam giu)               — nguong LONG hon => bien tren do phu cua anomaly
WITH cal AS (
  SELECT t.time FROM tav2_bq.ticker AS t
  WHERE t.ticker = "VNINDEX" AND t.time BETWEEN "2015-06-01" AND "2026-07-24"
  QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC(t.time, MONTH) ORDER BY t.time DESC) = 1
),
px AS (
  SELECT t.time, t.ticker, t.Close, t.Volume, t.Volume_1M, t.VNINDEX
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN "2015-04-01" AND "2026-07-24" AND t.ticker <> "VNINDEX" AND t.Close > 0
),
r AS (
  SELECT p.time, p.ticker, p.Close, p.Volume, p.Volume_1M,
    SAFE_DIVIDE(p.Close,   LAG(p.Close)   OVER (PARTITION BY p.ticker ORDER BY p.time)) - 1 AS ret,
    SAFE_DIVIDE(p.VNINDEX, LAG(p.VNINDEX) OVER (PARTITION BY p.ticker ORDER BY p.time)) - 1 AS vni_ret
  FROM px p
),
f AS (
  SELECT r.time, r.ticker,
    r.ret * 100 AS ret_pc,
    (r.ret - r.vni_ret) * 100 AS idio,
    SAFE_DIVIDE(r.Volume, NULLIF(r.Volume_1M, 0)) AS vol_x,
    r.Volume * r.Close / 1e9 AS val_bn,
    r.Volume_1M * r.Close / 1e9 AS val1m_bn,
    (r.ret * 100 <= -6.5 AND (r.ret - r.vni_ret) * 100 <= -4) AS fl,
    (r.ret * 100 >=  6.5 AND (r.ret - r.vni_ret) * 100 >=  4) AS ce
  FROM r
),
f2 AS (
  SELECT f.*,
    f.fl AND IFNULL(LAG(f.fl) OVER (PARTITION BY f.ticker ORDER BY f.time), FALSE) AS floor2,
    f.ce AND IFNULL(LAG(f.ce) OVER (PARTITION BY f.ticker ORDER BY f.time), FALSE) AS ceil2
  FROM f
),
alert AS (
  SELECT f2.time AS adate, f2.ticker,
    ((f2.floor2 AND f2.val_bn >= 0.3)
      OR (f2.ceil2 AND f2.val_bn >= 0.3)
      OR (f2.vol_x >= 8 AND f2.val_bn >= 8 AND f2.val1m_bn >= 3)
      OR (f2.ret_pc <= -6 AND f2.idio <= -5 AND f2.val1m_bn >= 3 AND f2.val_bn >= 3)) AS a_w,
    (f2.floor2 OR f2.ceil2
      OR (f2.vol_x >= 5 AND f2.val_bn >= 5)
      OR (f2.ret_pc <= -6 AND f2.idio <= -5)) AS a_h,
    ((f2.floor2 AND f2.val_bn >= 0.3)
      OR (f2.vol_x >= 8 AND f2.val_bn >= 8 AND f2.val1m_bn >= 3)
      OR (f2.ret_pc <= -6 AND f2.idio <= -5 AND f2.val1m_bn >= 3 AND f2.val_bn >= 3)) AS a_w_down
  FROM f2
),
alert2 AS (SELECT * FROM alert WHERE a_h OR a_w)
SELECT c.time, a.ticker,
  LOGICAL_OR(a.a_w)      AS anom_w,
  LOGICAL_OR(a.a_h)      AS anom_h,
  LOGICAL_OR(a.a_w_down) AS anom_w_down
FROM cal c
JOIN alert2 a ON a.adate BETWEEN DATE_SUB(c.time, INTERVAL 30 DAY) AND c.time
GROUP BY 1, 2
ORDER BY 1, 2
