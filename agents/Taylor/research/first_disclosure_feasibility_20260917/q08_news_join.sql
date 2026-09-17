WITH c AS (SELECT * FROM tav2_bq.corporate_action AS c WHERE c.source_news_id IS NOT NULL),
n AS (SELECT CAST(sn.news_id AS STRING) nid, ANY_VALUE(sn.public_datetime) pdt, ANY_VALUE(sn.public_date) pd, COUNT(*) nrows, COUNT(DISTINCT sn.ticker) ntk,
   ANY_VALUE(sn.first_ingested_at) fia, STRING_AGG(DISTINCT sn.ticker) tks FROM tav2_bq.stock_news AS sn GROUP BY 1)
SELECT c.event_code, COUNT(*) n_sid, COUNTIF(n.nid IS NOT NULL) n_join,
 COUNTIF(n.nid IS NOT NULL AND STRPOS(CONCAT(',',n.tks,','), CONCAT(',',c.ticker,','))>0) n_join_same_ticker,
 COUNTIF(n.nid IS NOT NULL AND c.first_disclosure_datetime IS NOT NULL) n_join_fd,
 COUNTIF(n.nid IS NOT NULL AND DATE(c.first_disclosure_datetime)=n.pd) fd_date_eq_news_date
FROM c LEFT JOIN n ON n.nid=c.source_news_id GROUP BY 1
