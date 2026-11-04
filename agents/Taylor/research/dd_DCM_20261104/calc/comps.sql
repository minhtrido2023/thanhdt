SELECT k.ticker, k.time, k.Price, ROUND(k.PE,2) PE, ROUND(k.PB,2) PB, ROUND(k.EVEB,2) EVEB, ROUND(k.PE_MA5Y,2) PE_MA5Y, ROUND(k.PB_MA5Y,2) PB_MA5Y
FROM tav2_bq.ticker AS k WHERE k.ticker IN ('DPM','DDV','DCM') AND k.time='2026-11-04'
