SELECT quarter, Revenue_P0, GPM_P0, NP_P0 FROM tav2_bq.ticker_financial t WHERE t.ticker='SZL' AND t.quarter>='2017Q1' ORDER BY quarter  -- chay 2026-11-23
