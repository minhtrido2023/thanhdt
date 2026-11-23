SELECT MAX(t.time) last_t, ARRAY_AGG(t.Price ORDER BY t.time DESC LIMIT 1)[OFFSET(0)] px,
 AVG(IF(t.time>=DATE_SUB(DATE "2026-11-06", INTERVAL 90 DAY), t.Price*t.Volume,NULL)) adv3m,
 APPROX_QUANTILES(IF(t.time>=DATE_SUB(DATE "2026-11-06", INTERVAL 365 DAY), t.Price*t.Volume,NULL),2)[OFFSET(1)] adv250_med,
 APPROX_QUANTILES(IF(t.time>=DATE_SUB(DATE "2026-11-06", INTERVAL 90 DAY), t.Price*t.Volume,NULL),2)[OFFSET(1)] adv60_med,
 MIN(IF(t.time>=DATE_SUB(DATE "2026-11-06", INTERVAL 365 DAY), t.Price,NULL)) lo1y,
 MAX(IF(t.time>=DATE_SUB(DATE "2026-11-06", INTERVAL 365 DAY), t.Price,NULL)) hi1y
FROM tav2_bq.ticker AS t WHERE t.ticker="GAS" AND t.time>="2025-11-01"
