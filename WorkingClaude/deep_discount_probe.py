"""Probe: do individually deep-discounted QUALITY names have forward edge the market-level gates miss?
pbz = (PB - PB_MA5Y)/PB_SD5Y per name (own-history cheapness). Quality floor = ROIC5Y>0.08 & ROE_Min5Y>0 &
FSCORE>=5. Forward = profit_2M (T+40, training col, research only). Split by DT5G market state to see if the
edge exists OUTSIDE CRISIS/BEAR (= missed by recovery/A&C gates which only fire market-wide)."""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from bq_local_cache import get_cache
lc = get_cache()

# 1) forward 2M return by individual-discount depth (quality names, 2014+)
q1 = lc.query("""
WITH q AS (
  SELECT (t.PB - t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0) AS pbz, t.profit_2M AS f
  FROM tav2_bq.ticker_prune t
  WHERE t.time >= DATE '2014-01-01' AND t.PB_SD5Y > 0 AND t.profit_2M IS NOT NULL
    AND t.ROIC5Y > 0.08 AND t.ROE_Min5Y > 0 AND t.FSCORE >= 5)
SELECT CASE WHEN pbz<=-2 THEN '1.pbz<=-2' WHEN pbz<=-1.5 THEN '2.[-2,-1.5]'
            WHEN pbz<=-1 THEN '3.[-1.5,-1]' WHEN pbz<=0 THEN '4.[-1,0]' ELSE '5.pbz>0' END AS bucket,
       COUNT(*) n, ROUND(AVG(f)*100,2) avg_fwd2M_pct, ROUND(AVG(CASE WHEN f>0 THEN 1.0 ELSE 0 END)*100,1) winrate
FROM q GROUP BY bucket ORDER BY bucket""")
print("=== Forward 2M return by OWN-discount depth (quality names) ==="); print(q1.to_string(index=False))

# 2) deep-discount quality events split by DT5G market state (is the edge OUTSIDE crisis/bear?)
q2 = lc.query("""
WITH q AS (
  SELECT t.time, (t.PB - t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0) AS pbz, t.profit_2M AS f
  FROM tav2_bq.ticker_prune t
  WHERE t.time >= DATE '2014-01-01' AND t.PB_SD5Y > 0 AND t.profit_2M IS NOT NULL
    AND t.ROIC5Y > 0.08 AND t.ROE_Min5Y > 0 AND t.FSCORE >= 5)
SELECT s.state, COUNT(*) n, ROUND(AVG(q.f)*100,2) avg_fwd2M_pct,
       ROUND(AVG(CASE WHEN q.f>0 THEN 1.0 ELSE 0 END)*100,1) winrate
FROM q JOIN tav2_bq.vnindex_5state_dt5g_live s ON q.time = s.time
WHERE q.pbz <= -1.5
GROUP BY s.state ORDER BY s.state""")
print("\n=== DEEP-discount (pbz<=-1.5) quality events by DT5G state (1=CRISIS..5=EXBULL) ==="); print(q2.to_string(index=False))
print("\n(If avg_fwd2M is high in states 3/4/5 = NEUTRAL/BULL, those are deep single-name discounts the MARKET-level gates MISS.)")
