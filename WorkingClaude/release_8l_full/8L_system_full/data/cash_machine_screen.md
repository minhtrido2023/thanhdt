# Cash-machine screen — CFO>NP (TTM) sustained + cash-accumulating + non-dilutive

## Validation: VCS / DGC as-of pre-multibagger date
  VCS @ 2015-12-31: TTM_CFO/NP med=0.53, %periods≥1=50%, cash 121→216bn(grow=True), dilut3y=-20% → CASH_MACHINE=False
  DGC @ 2016-09-30: TTM_CFO/NP med=1.21, %periods≥1=67%, cash 6→79bn(grow=True), dilut3y=+49% → CASH_MACHINE=True

## Current CASH MACHINES (7 of 50 quality names)
tkr    TTM_CFO/NP   %≥1 cashGrow  dilut3y cash_now(bn)
--------------------------------------------------------
NAB          8.26  100%     True     +30%         1336
CVT          5.59   88%     True      +0%          409
HDG          2.38  100%     True     +10%         1191
HAH          2.13  100%     True     +55%          817
FMC          2.00   88%     True      +0%          564
QTP          1.83  100%     True      +0%           81
PTB          1.18   75%     True     +20%          487

CASH MACHINES: NAB, CVT, HDG, HAH, FMC, QTP, PTB

NOT cash-machine but close (med TTM≥0.9): VGC, PGS, PVT, D2D, CTR, NTC, VTO, IDC, VCS, PHP, REE, DTD, DPM, DHG, NNC

Logic: gate not ranker (rare/precious quality). TTM (4Q) smooths working-capital noise.
Caveat: dilut3y can't fully separate bonus-shares vs cash-raise — cross-checked w/ cash growing.

## ENGINE classification (multibagger = cash-machine + runway + high ROIC)
  COMPOUNDER      : NCT, SCS, BMP, DGC, LIX, DTD, HAH, TCL, CTR, IDC, CSV, TLG, DHA, FPT, DPM, QNS, NTP, SIP, NTC, VGC, NNC, DMC, PTB, LHG
  YIELD           : QTP, HDG, CVT
  LOWROIC_GROWTH  : HPG, PHP, FMC, PVT, BWE, MWG, REE, TIP, NAB, MBB, BIC

tkr   engine           CFO/NP assetCAGR  ROIC5Y cashMach
PAT   -                  1.14       -8%     53%    False
VNM   -                  0.94       +1%     24%    False
MCH   -                  0.81       +2%     24%    False
DHG   -                  1.36       +3%     22%    False
VCS   -                  1.76       -3%     20%    False
GAS   -                  1.07       +2%     20%    False
SAB   -                  0.93       +1%     17%    False
DVP   -                  0.56       +2%     17%    False
D2D   -                  2.45       -6%     16%    False
MCM   -                  0.86       +0%     10%    False
PGS   -                  2.62       -2%      9%    False
VTO   -                  2.23       -3%      8%    False
NCT   COMPOUNDER         1.01      +13%     59%    False
SCS   COMPOUNDER         0.97       +8%     46%    False
BMP   COMPOUNDER         1.05       +7%     41%    False
DGC   COMPOUNDER         0.73      +18%     29%    False
LIX   COMPOUNDER         1.06       +7%     25%    False
DTD   COMPOUNDER         1.40       +8%     23%    False
HAH   COMPOUNDER         2.13      +23%     21%     True
TCL   COMPOUNDER         0.94       +7%     21%    False
CTR   COMPOUNDER         2.30      +22%     21%    False
IDC   COMPOUNDER         2.07      +10%     20%    False
CSV   COMPOUNDER         0.91       +8%     20%    False
TLG   COMPOUNDER         0.77       +9%     18%    False
DHA   COMPOUNDER        -0.70       +3%     18%    False
FPT   COMPOUNDER         1.24       +5%     18%    False
DPM   COMPOUNDER         1.39       +3%     17%    False
QNS   COMPOUNDER         0.88      +10%     16%    False
NTP   COMPOUNDER         1.25       +6%     16%    False
SIP   COMPOUNDER         1.14      +12%     15%    False
NTC   COMPOUNDER         2.29      +10%     14%    False
VGC   COMPOUNDER         3.38       +4%     14%    False
NNC   COMPOUNDER         1.31      +18%     14%    False
DMC   COMPOUNDER         0.53       +5%     14%    False
PTB   COMPOUNDER         1.18       +5%     13%     True
LHG   COMPOUNDER         0.45       +4%     13%    False
HPG   LOWROIC_GROWTH     0.78       +9%     11%    False
PHP   LOWROIC_GROWTH     1.47      +13%     11%    False
FMC   LOWROIC_GROWTH     2.00      +12%     10%     True
PVT   LOWROIC_GROWTH     2.56      +15%     10%    False
BWE   LOWROIC_GROWTH     1.25      +14%     10%    False
MWG   LOWROIC_GROWTH     1.29       +8%     10%    False
REE   LOWROIC_GROWTH     1.46       +6%      9%    False
TIP   LOWROIC_GROWTH     0.37      +21%      7%    False
NAB   LOWROIC_GROWTH     8.26      +26%      0%     True
MBB   LOWROIC_GROWTH     0.95      +26%      0%    False
BIC   LOWROIC_GROWTH     0.87      +13%    -23%    False
QTP   YIELD              1.83       -5%     14%     True
HDG   YIELD              2.38       -2%     13%     True
CVT   YIELD              5.59       +2%      6%     True