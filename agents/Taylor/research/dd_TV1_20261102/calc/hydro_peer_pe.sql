-- r6 B1(a): P/E trung vị theo mã x năm (và tháng 10/2026) cho nhóm thuỷ điện niêm yết. PE>0.
-- Loại khỏi nhóm: PPC, QTP (nhiệt điện than), KHP (phân phối điện). TV1 giữ lại để so, KHÔNG vào trung vị ngang hàng.
SELECT EXTRACT(YEAR FROM t.time) AS y, 'Y' AS per, t.ticker,
       APPROX_QUANTILES(t.PE, 100)[OFFSET(50)] AS pe_med
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ('AVC','BSA','CHP','DNH','DRL','GHC','HJS','HNA','ISH','NED','S4A','SBA','SBH','SEB','SHP','SJD','TBC','TMP','TV1','VPD','VSH','PPC','QTP','KHP')
  AND t.PE > 0 AND t.time >= '2024-01-01'
GROUP BY y, per, t.ticker
UNION ALL
SELECT 2026, 'M10', t.ticker, APPROX_QUANTILES(t.PE, 100)[OFFSET(50)]
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ('AVC','BSA','CHP','DNH','DRL','GHC','HJS','HNA','ISH','NED','S4A','SBA','SBH','SEB','SHP','SJD','TBC','TMP','TV1','VPD','VSH','PPC','QTP','KHP')
  AND t.PE > 0 AND t.time >= '2026-10-01'
GROUP BY t.ticker
ORDER BY per, y, ticker
