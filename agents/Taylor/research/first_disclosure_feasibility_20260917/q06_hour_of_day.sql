SELECT c.event_code, EXTRACT(YEAR FROM c.first_disclosure_datetime) yr,
 EXTRACT(HOUR FROM c.first_disclosure_datetime) hr_utc, c.source_news_id IS NOT NULL has_sid,
 DATE(c.ingested_at) ing_date, COUNT(*) n,
 COUNTIF(EXTRACT(SECOND FROM c.first_disclosure_datetime)=0) n_sec0
FROM tav2_bq.corporate_action AS c WHERE c.first_disclosure_datetime IS NOT NULL
GROUP BY 1,2,3,4,5
