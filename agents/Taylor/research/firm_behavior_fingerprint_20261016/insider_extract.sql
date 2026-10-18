-- insider events (DDIND+DDRP, Done) for F6 insider net buy 90d pre-release. public_date of Done = result-report date (safe "known" date per data_registry insider_transaction.md)
SELECT i.ticker, i.public_date, i.event_code, i.action_code, i.share_acquire, i.trader_person_id
FROM `lithe-record-440915-m9.tav2_bq.insider_transaction` AS i
WHERE i.trade_status = 'Đã thực hiện xong' AND i.event_code IN ('DDIND','DDRP') AND i.action_code IN ('B','S')
