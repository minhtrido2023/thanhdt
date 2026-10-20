SELECT EXTRACT(YEAR FROM DATE(public_date)) AS yr, COUNT(*) AS n_news, COUNT(DISTINCT ticker) AS n_tk,
  COUNTIF(REGEXP_CONTAINS(LOWER(title), r'bctc|báo cáo tài chính|kqkd|kết quả kinh doanh')) AS n_bctc
FROM tav2_bq.stock_news GROUP BY yr ORDER BY yr
