-- Sàn hiện hành: sự kiện NLIS/MOVE gần nhất (tiêu đề) — bổ sung bằng biên độ giá nếu thiếu.
SELECT c.ticker, c.event_code, c.effective_date, c.event_title_vi
FROM tav2_bq.corporate_action AS c
WHERE c.event_code IN ('NLIS','MOVE')
  AND c.ticker IN (SELECT DISTINCT t.ticker FROM tav2_bq.ticker AS t WHERE t.ICB_Code = 7535 AND t.time >= '2019-01-01' UNION DISTINCT SELECT 'TV1')
QUALIFY ROW_NUMBER() OVER (PARTITION BY c.ticker ORDER BY c.effective_date DESC NULLS LAST, c.public_date DESC) = 1
