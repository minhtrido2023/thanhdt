SELECT ticker, quarter, ANY_VALUE(GPM_P0) GPM, ANY_VALUE(Revenue_P0) REV
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` f
WHERE ticker IN ('NNC','KSB','DHA','VLB','MVC') AND quarter >= '2011Q1'
GROUP BY ticker, quarter ORDER BY ticker, quarter
