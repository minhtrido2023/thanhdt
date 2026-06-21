# Cyclical framework across commodity groups (contrarian test)
buckets by commodity regime (price vs trailing-36m median) x stock deep-dd<-25%

## RUBBER  stocks=['DRI', 'PHR', 'DPR', 'GVR', 'TRC', 'HRC']  | latest 2, good=True, pctile5y=0.95 (2026-03-01)
bucket                      N    1Ymed  1Ywin    2Ymed  2Ywin
commodity WEAK +deep dd   179      +37%     79%      +69%     87%
commodity WEAK +normal    329      +11%     57%      +23%     65%
commodity GOOD +deep dd    99       +3%     47%      +20%     52%
commodity GOOD +normal    415       -0%     46%       -1%     38%
WEAK (any dd)             508      +18%     65%      +37%     73%
GOOD (any dd)             514       +0%     46%       +2%     41%

## IRON_ORE  stocks=['HPG', 'HSG', 'NKG']  | latest 104, good=False, pctile5y=0.35 (2026-03-01)
bucket                      N    1Ymed  1Ywin    2Ymed  2Ywin
commodity WEAK +deep dd    96      +33%     75%      +60%     75%
commodity WEAK +normal    192      +21%     60%      +47%     60%
commodity GOOD +deep dd   130      -14%     43%      +42%     65%
commodity GOOD +normal    164      -12%     44%      -16%     38%
WEAK (any dd)             288      +26%     65%      +57%     65%
GOOD (any dd)             294      -12%     44%       +1%     49%

## UREA  stocks=['DCM', 'DPM']  | latest 726, good=True, pctile5y=0.90 (2026-03-01)
bucket                      N    1Ymed  1Ywin    2Ymed  2Ywin
commodity WEAK +deep dd    51      +17%     84%      +27%     86%
commodity WEAK +normal    127       +1%     52%       +2%     46%
commodity GOOD +deep dd    52       -1%     44%      +11%     63%
commodity GOOD +normal    104      +12%     46%      +21%     53%
WEAK (any dd)             178       +7%     61%       +9%     58%
GOOD (any dd)             156       +2%     45%      +20%     56%

## DAP  stocks=['DDV', 'DGC']  | latest 658, good=True, pctile5y=0.65 (2026-03-01)
bucket                      N    1Ymed  1Ywin    2Ymed  2Ywin
commodity WEAK +deep dd    68      +26%     71%      +79%     88%
commodity WEAK +normal     70      +22%     59%       +7%     41%
commodity GOOD +deep dd    32       +5%     42%      +28%     47%
commodity GOOD +normal     80      +14%     50%      +31%     50%
WEAK (any dd)             138      +23%     64%      +46%     64%
GOOD (any dd)             112      +13%     48%      +30%     49%

## CAUSTIC_SODA  stocks=['CSV']  | latest 700, good=True, pctile5y=0.70 (2026-03-01)
bucket                      N    1Ymed  1Ywin    2Ymed  2Ywin
commodity WEAK +deep dd    13      +56%     77%     +161%    100%
commodity WEAK +normal     57      +42%     81%      +82%     86%
commodity GOOD +deep dd    18      -14%     27%     +139%     54%
commodity GOOD +normal     35       -2%     38%       -5%     41%
WEAK (any dd)              70      +42%     80%      +84%     89%
GOOD (any dd)              53       -4%     33%      +16%     46%

Read: across groups, if 'commodity WEAK + deep-dd' > 'GOOD', the contrarian
buy-the-trough pattern generalizes beyond rubber.