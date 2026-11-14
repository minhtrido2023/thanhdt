SELECT t.ticker, t.time, t.quarter, t.ID_Release, t.Release_Date, t.OShares,
 t.Revenue_P0,t.Revenue_P1,t.Revenue_P2,t.Revenue_P3,t.Revenue_P4,t.Revenue_P5,t.Revenue_P6,t.Revenue_P7,
 t.NP_P0,t.NP_P1,t.NP_P2,t.NP_P3,t.NP_P4,t.NP_P5,t.NP_P6,t.NP_P7,
 t.GPM_P0,t.GPM_P1,t.GPM_P2,t.GPM_P3,t.GPM_P4,t.GPM_P5,t.GPM_P6,t.GPM_P7,
 t.Inventory_P0,t.Inventory_P1,t.Inventory_P2,t.Inventory_P3,t.Inventory_P4,t.Inventory_P5,t.Inventory_P6,t.Inventory_P7,
 t.CF_OA_P0,t.CF_OA_P1,t.CF_OA_P2,t.CF_OA_P3,t.CF_OA_P4,
 t.EBITM_P0,t.EBITM_P4,t.NPM_P0,t.NPM_P4,t.EBITDA_P0,t.StDebt_P0,t.LtDebt_P0,t.totalAsset_P0,t.StLiab_P0,t.LtLiab_P0,t.Cash_P0,t.AR_P0,t.LtInvest_P0,t.EPS_P0
FROM tav2_bq.ticker_financial AS t WHERE t.ticker='PAT' ORDER BY t.time
