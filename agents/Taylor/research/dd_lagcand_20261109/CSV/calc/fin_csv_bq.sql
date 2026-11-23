SELECT f.quarter, f.Revenue_P0, f.NP_P0 FROM tav2_bq.ticker_financial AS f WHERE f.ticker="CSV" AND f.quarter >= "2017Q1" ORDER BY f.quarter
