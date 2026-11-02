-- Peer study TV1 r7: panel tháng (phiên cuối tháng) 2019-01 → 2026-11, nhóm ICB 7535 (Conventional Electricity) + TV1.
-- PE/PB lấy nguyên từ tav2_bq.ticker (cột join từ ticker_financial theo ngày công bố — PIT theo ID_Release).
-- ADV = trung vị Price*Volume trong tháng (tỷ đ). Price = giá chưa điều chỉnh (đi cùng DPS danh nghĩa).
WITH base AS (
  SELECT t.ticker AS tk, t.time, t.Price, t.Close, t.PE, t.PB, t.BVPS, t.DY, t.ROE5Y, t.Volume, t.ICB_Code,
         DATE_TRUNC(t.time, MONTH) AS m
  FROM tav2_bq.ticker AS t
  WHERE (t.ICB_Code = 7535 OR t.ticker = 'TV1') AND t.time >= '2019-01-01'
), adv AS (
  SELECT tk, m, APPROX_QUANTILES(Price*Volume, 100)[OFFSET(50)]/1e9 AS adv_med, COUNT(*) AS nd,
         MAX(ABS(SAFE_DIVIDE(Close, LAG_C) - 1)) AS max_absret
  FROM (SELECT b.*, LAG(b.Close) OVER (PARTITION BY b.tk ORDER BY b.time) AS LAG_C FROM base AS b)
  GROUP BY tk, m
)
SELECT b.tk AS ticker, b.m, b.time, b.Price, b.Close, b.PE, b.PB, b.BVPS, b.DY, b.ROE5Y, b.ICB_Code,
       a.adv_med, a.nd, a.max_absret
FROM base AS b JOIN adv AS a ON a.tk = b.tk AND a.m = b.m
QUALIFY ROW_NUMBER() OVER (PARTITION BY b.tk, b.m ORDER BY b.time DESC) = 1
ORDER BY ticker, m
