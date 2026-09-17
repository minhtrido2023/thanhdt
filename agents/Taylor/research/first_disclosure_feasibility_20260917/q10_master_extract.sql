WITH n AS (SELECT CAST(sn.news_id AS STRING) nid, ANY_VALUE(sn.public_datetime) news_pdt, ANY_VALUE(sn.public_date) news_pd,
  ANY_VALUE(REPLACE(REPLACE(sn.title, '\n',' '), '\r',' ')) news_title, ANY_VALUE(sn.matched_event_codes) news_mec, ANY_VALUE(sn.action_type) news_act,
  STRING_AGG(DISTINCT sn.ticker) news_tickers, ANY_VALUE(sn.source) news_source
 FROM tav2_bq.stock_news AS sn GROUP BY 1)
SELECT c.id, c.ticker, c.event_code, c.event_status, c.issue_method_name_vi, c.value_per_share, c.dividend_year, c.dividend_stage_vi,
 c.public_date, c.exright_date, c.record_date, c.payout_date, c.effective_date,
 FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', c.first_disclosure_datetime) fd, c.source_news_id sid,
 FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', c.ingested_at) ingested_at,
 REPLACE(c.event_title_vi, '\n',' ') title_vi, c.source_url,
 n.news_pdt, n.news_pd, n.news_title, n.news_mec, n.news_act, n.news_tickers, n.news_source
FROM tav2_bq.corporate_action AS c LEFT JOIN n ON n.nid=c.source_news_id
