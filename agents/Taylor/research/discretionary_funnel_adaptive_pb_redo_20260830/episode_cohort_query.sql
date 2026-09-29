-- discretionary_funnel_adaptive_pb_redo_20260830 — episode cohort + PB percentile pull
-- Params substituted by run_episode_sensitivity.py: {TROUGH}, {WINDOW_START}
-- Định nghĩa cohort GIỐNG HỆT bin/discretionary_candidate_funnel.py (không tự chế lại):
--   washout>=30% từ đỉnh cục bộ 400 ngày LỊCH, dd52<=-20% từ đỉnh rolling 252 PHIÊN.
-- Cơ sở percentile ĐÃ KHOÁ TRƯỚC KHI CHẠY QUERY NÀY (xem §1 report): universe_pit ∩ Volume>0
-- cùng ngày — không phải toàn bộ mã niêm yết.
WITH px AS (
  SELECT
    t.ticker,
    t.time,
    t.Close,
    t.Volume,
    t.PB,
    MAX(t.Close) OVER (
      PARTITION BY t.ticker ORDER BY UNIX_DATE(t.time)
      RANGE BETWEEN 400 PRECEDING AND CURRENT ROW
    ) AS peak_400d,
    MAX(t.Close) OVER (
      PARTITION BY t.ticker ORDER BY t.time
      ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
    ) AS high_252s
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time BETWEEN DATE('{WINDOW_START}') AND DATE('{TROUGH}')
),
trough_px AS (
  SELECT ticker, Close, Volume, PB, peak_400d, high_252s
  FROM px
  WHERE time = DATE('{TROUGH}')
),
univ AS (
  SELECT ticker
  FROM `lithe-record-440915-m9.tav2_mike.universe_pit`
  WHERE time = DATE('{TROUGH}') AND in_universe = TRUE
),
cross_section AS (
  -- percentile basis = universe_pit ∩ Volume>0 cùng ngày (khoá TRƯỚC, xem §1)
  SELECT tp.ticker, tp.PB
  FROM trough_px AS tp
  JOIN univ AS u ON tp.ticker = u.ticker
  WHERE tp.Volume > 0 AND tp.PB IS NOT NULL
),
ranked AS (
  SELECT ticker, PB, PERCENT_RANK() OVER (ORDER BY PB) AS pb_pct_rank
  FROM cross_section
)
SELECT
  tp.ticker,
  tp.Close,
  tp.Volume,
  tp.PB,
  tp.peak_400d,
  tp.high_252s,
  SAFE_DIVIDE(tp.Close, tp.peak_400d) - 1 AS washout_pct,
  SAFE_DIVIDE(tp.Close, tp.high_252s) - 1 AS dd52_pct,
  r.pb_pct_rank
FROM trough_px AS tp
JOIN univ AS u ON tp.ticker = u.ticker
LEFT JOIN ranked AS r ON tp.ticker = r.ticker
WHERE tp.Volume > 0
