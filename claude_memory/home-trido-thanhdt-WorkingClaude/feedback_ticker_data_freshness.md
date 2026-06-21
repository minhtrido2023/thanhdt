---
name: Use ticker_1m for latest data when ticker is stale
description: tav2_bq.ticker can lag; fallback to tav2_bq.ticker_1m for rolling 1-month snapshot
type: feedback
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# Data freshness — auto-fallback rule

**Rule**: When pulling current/recent data and `tav2_bq.ticker` doesn't have the latest dates needed:
- Auto-fallback to `tav2_bq.ticker_1m` (rolling ~1-month snapshot, more up-to-date)
- Use UNION ALL pattern: prefer ticker (canonical), fallback to ticker_1m for dates missing from ticker
- For VNINDEX specifically: ticker uses 'VNINDEX' ticker, ticker_1m uses 'VNI'

## Reference pattern (from recommend_holistic.py SCORE_SQL)

```sql
WITH ticker_data AS (
  SELECT t.ticker, t.time, t.Close, ... FROM tav2_bq.ticker AS t
  WHERE t.time = DATE '{day}' AND t.D_RSI IS NOT NULL
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)

  UNION ALL

  SELECT t.ticker, t.time, t.Close, ... FROM tav2_bq.ticker_1m AS t
  WHERE t.time = DATE '{day}' AND t.D_RSI IS NOT NULL
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND NOT EXISTS (
      SELECT 1 FROM tav2_bq.ticker AS t2
      WHERE t2.time = DATE '{day}' AND t2.ticker = t.ticker AND t2.D_RSI IS NOT NULL
    )
)
```

## When to apply

- Live picks / live screening (recommend_holistic.py already implements)
- Latest-date queries for current price/indicators
- Any "get me the most recent X" query
- Backtest sims where END_DATE is close to today

## When NOT to apply

- Historical backtest with date range fully in the past (just use ticker)
- Aggregation across years (UNION fallback adds noise)

## User instruction

"nếu không thấy dữ liệu về giá mới nhất, bạn tra cứu bảng ticker_1M. cái này không nên nhắc lại mỗi lần chạy simulation nữa"

→ Apply this as default behavior. Don't ask user to confirm each time.
