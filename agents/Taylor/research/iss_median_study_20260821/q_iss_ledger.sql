-- So ISS/Rights executed co exright_date — dung cho H3 (ghep voi deal ledger)
SELECT ticker, exright_date, event_status, issue_method_code,
       SAFE_DIVIDE(total_value, issue_volumn) AS issue_price
FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
WHERE event_code = 'ISS' AND issue_method_code = 'Rights'
  AND event_status = 'executed' AND exright_date IS NOT NULL
ORDER BY ticker, exright_date
