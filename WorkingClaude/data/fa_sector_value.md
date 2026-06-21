# Directions #1 (bank gap) and #4 (conditional value)

## #1 — FA composite IC by ICB sector (does it fail for financials?)

sector              N  IC_total  IC_qual   IC_val  med_p3M
----------------------------------------------------------
?                 261   -0.0197  -0.1326  -0.0028   -1.10%
O&G             1,395   +0.0872  +0.0806  -0.0992   -1.31%
Materials       2,560   +0.1745  +0.1667  -0.0242   -2.43%
Industrials     1,675   +0.0701  +0.0712  -0.0132   -1.07%
ConsGoods         323   +0.1608  +0.1599  -0.1525   -2.82%
Health            486   +0.0741  +0.0946  -0.0476   -0.91%
Telecom           509   +0.0671  +0.0113  +0.0749    0.22%
Financials      3,753   +0.0605  +0.0188  -0.0059   -0.21%
Tech/Utl          201   +0.2464  +0.0882  -0.1504   -0.85%
----------------------------------------------------------
FINANCIALS      3,753   +0.0605
NON-FIN         7,453   +0.1236
  → gap = -0.0631 (negative = FA composite weaker for banks/financials)

## #4 — Does value work CONDITIONALLY? (valuation IC within quality terciles)

quality tercile   IC_valuation       N
--------------------------------------
LowQ                   -0.0350   3,736
MidQ                   -0.0246   3,735
HighQ                  -0.0139   3,735

(valuation axis: higher score = cheaper after the INV sign-flip in fundamental_rating.
 positive IC within a tercile = cheap predicts higher return there.)

### Quality × Cheapness 2×2 (median profit_3M)
                 Expensive       Cheap
HighQuality          0.00%      -0.08%
LowQuality          -1.64%      -2.79%

Greenblatt hypothesis: 'HighQuality+Cheap' should be best; 'LowQuality+Cheap'
(the value trap) should be worst or near-worst — explaining valuation's negative
standalone IC (dominated by cheap junk).
