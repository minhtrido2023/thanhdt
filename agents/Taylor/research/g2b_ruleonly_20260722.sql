WITH D AS (SELECT d FROM UNNEST([DATE"2014-06-30",DATE"2018-06-29",DATE"2022-06-30",DATE"2026-06-15"]) d),
U AS (SELECT u.time, u.ticker FROM `lithe-record-440915-m9.tav2_mike.universe_pit` u JOIN D ON u.time=D.d WHERE u.in_universe),
P AS (SELECT p.time, p.ticker FROM tav2_bq.ticker_prune p JOIN D ON p.time=D.d),
RO AS (SELECT U.time, U.ticker FROM U LEFT JOIN P ON U.time=P.time AND U.ticker=P.ticker WHERE P.ticker IS NULL),
FIN AS (
  SELECT * FROM (
    SELECT D.d AS asof, f.ticker, f.CF_OA_3Y,
           ROW_NUMBER() OVER (PARTITION BY D.d, f.ticker ORDER BY f.time DESC) rn
    FROM tav2_bq.ticker_financial f CROSS JOIN D
    WHERE f.time <= D.d AND f.time >= DATE_SUB(D.d, INTERVAL 400 DAY))
  WHERE rn=1)
SELECT RO.time, RO.ticker, ROUND(t.ROE_Min3Y,4) roe_min3y, ROUND(FIN.CF_OA_3Y,4) cf_oa_3y,
  ROUND(t.ROE5Y,4) roe5y, t.FSCORE, ROUND(t.Volume_3M_P50*t.Price/1e9,2) adv_bn,
  (t.ROE_Min3Y IS NOT NULL AND t.ROE_Min3Y>=0 AND FIN.CF_OA_3Y IS NOT NULL AND FIN.CF_OA_3Y>0) pass_floor,
  (RO.ticker IN UNNEST(["PC1","VVS","KSF","NKG","HSG","HVN","VJC","NVL","GEG","SBA","DMC","IMP","TRA","TOS","VTP"])) banned
FROM RO JOIN tav2_bq.ticker t ON t.ticker=RO.ticker AND t.time=RO.time
LEFT JOIN FIN ON FIN.ticker=RO.ticker AND FIN.asof=RO.time
ORDER BY RO.time, RO.ticker
