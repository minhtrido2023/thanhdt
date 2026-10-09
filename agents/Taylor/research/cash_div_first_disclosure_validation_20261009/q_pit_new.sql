WITH s AS (SELECT * FROM `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` WHERE event_code='DIV'),
fs AS (SELECT id, MIN(snapshot_date) first_seen FROM s GROUP BY id),
fsfd AS (SELECT id, MIN(IF(first_disclosure_datetime IS NOT NULL, snapshot_date, NULL)) first_fd_snap FROM s GROUP BY id),
firstrow AS (SELECT s.id, s.public_date pd0, s.first_disclosure_datetime fd0, s.event_status st0 FROM s JOIN fs USING(id) WHERE s.snapshot_date=fs.first_seen),
last AS (SELECT id, ticker, first_disclosure_datetime fdL, public_date pdL, exright_date ex, record_date rd, event_status stL, value_per_share v FROM s WHERE snapshot_date='2026-10-09')
SELECT l.id, l.ticker, fs.first_seen, fsfd.first_fd_snap, f.pd0, f.fd0, f.st0, l.fdL, l.pdL, l.ex, l.rd, l.stL, l.v,
 DATE_DIFF(fs.first_seen, DATE(l.fdL), DAY) lag_seen_minus_fdL,
 DATE_DIFF(fs.first_seen, f.pd0, DAY) lag_seen_minus_pd0,
 DATE_DIFF(DATE(l.fdL), f.pd0, DAY) fdL_minus_pd0,
 DATE_DIFF(l.ex, DATE(l.fdL), DAY) lead_ex
FROM last l JOIN fs USING(id) JOIN fsfd USING(id) JOIN firstrow f USING(id)
WHERE fs.first_seen > '2026-08-17'
ORDER BY fs.first_seen
