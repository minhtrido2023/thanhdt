# P0 ai_momentum: ngay du dieu kien momentum (chua cooldown) + rating/route as-of + fwd return (CHI de cham diem, KHONG filter)
WITH px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume_1M, t.Volume_3M_P50, t.HI_3M_T1, t.VNINDEX,
    LAG(t.Close,20) OVER w c20, LAG(t.VNINDEX,20) OVER w v20,
    LEAD(t.Close,1) OVER w c1, LEAD(t.Close,21) OVER w c21, LEAD(t.Close,61) OVER w c61,
    u.in_universe
  FROM tav2_bq.ticker t
  JOIN tav2_mike.universe_pit u ON u.ticker=t.ticker AND u.time=t.time AND u.ruleset_version=1
  WHERE t.time>="2024-08-01" AND t.ticker!="VNINDEX"
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)),
rt AS (SELECT r.ticker, r.time rt_time, r.route, r.rating,
         LEAD(r.time) OVER (PARTITION BY r.ticker ORDER BY r.time) rt_next FROM tav2_bq.fa_ratings_8l AS r),
j AS (SELECT p.*, rt.route, rt.rating, rt.rt_time FROM px p
      LEFT JOIN rt ON rt.ticker=p.ticker AND rt.rt_time<=p.time AND (rt.rt_next IS NULL OR rt.rt_next>p.time)
      WHERE p.in_universe),
x AS (SELECT *, c21/c1-1 r20, c61/c1-1 r60,
        Close/c20-1 mom20, (Close/c20-1)-(VNINDEX/v20-1) idio20,
        Volume_1M/NULLIF(Volume_3M_P50,0) volr, Close>=HI_3M_T1 newhi, Price*Volume_1M/1e9 liq_bn FROM j),
med AS (SELECT time, route, APPROX_QUANTILES(r20,2)[OFFSET(1)] med20, APPROX_QUANTILES(r60,2)[OFFSET(1)] med60, COUNT(*) n_route
        FROM x WHERE route IS NOT NULL GROUP BY 1,2)
SELECT x.ticker, x.time, x.route, x.rating, x.rt_time, ROUND(x.mom20,4) mom20, ROUND(x.idio20,4) idio20, ROUND(x.volr,3) volr,
  ROUND(x.liq_bn,2) liq_bn, x.Close, ROUND(x.r20,4) r20, ROUND(x.r60,4) r60,
  ROUND(x.r20-m.med20,4) ex20, ROUND(x.r60-m.med60,4) ex60, m.n_route
FROM x LEFT JOIN med m ON m.time=x.time AND m.route=x.route
WHERE x.time>="2024-10-01" AND x.mom20>=0.15 AND x.idio20>=0.10 AND x.volr>=1.2 AND x.newhi AND x.liq_bn>=1
ORDER BY x.ticker, x.time
