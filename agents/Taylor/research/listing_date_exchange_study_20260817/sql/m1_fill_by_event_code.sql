
SELECT event_code, COUNT(*) AS n,
       COUNTIF(listing_date IS NOT NULL) AS n_listing,
       ROUND(100 * COUNTIF(listing_date IS NOT NULL) / COUNT(*), 1) AS pct_listing
FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
GROUP BY event_code ORDER BY n DESC
