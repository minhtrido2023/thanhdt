# Growth RUNWAY / TAM detector — revenue-trajectory (2nd-derivative) + export tag
DURABLE/CAPTURING=runway open | SATURATING=S-curve topping (domestic captured) | MATURE=saturated

## Validation (examples)
  VNM   [DOMESTIC  ] recent3y CAGR +4% vs prior +2% (accel +2pp) → MATURE/FLAT
  MWG   [DOMESTIC  ] recent3y CAGR +10% vs prior +5% (accel +5pp) → MODERATE
  FRT   [DOMESTIC  ] recent3y CAGR +22% vs prior +21% (accel +1pp) → CAPTURING
  DGC   [EXPORT    ] recent3y CAGR -7% vs prior +35% (accel -42pp) → SATURATING
  VCS   [EXPORT    ] recent3y CAGR -9% vs prior -4% (accel -5pp) → MATURE/FLAT
  HPG   [STRUCTURAL] recent3y CAGR +12% vs prior +22% (accel -10pp) → SATURATING
  MSN   [DOMESTIC  ] recent3y CAGR +4% vs prior +17% (accel -12pp) → SATURATING
  PNJ   [DOMESTIC  ] recent3y CAGR +8% vs prior +25% (accel -17pp) → SATURATING

tkr   tag         recent3y  prior3y  accel  runway
----------------------------------------------------
GAS   DOMESTIC        +16%      +9%    +7  DURABLE
MBB   DOMESTIC        +19%     +22%    -3  DURABLE
SCS   DOMESTIC        +16%      +0%   +16  DURABLE
D2D   DOMESTIC        +68%     -42%  +110  CAPTURING
FRT   DOMESTIC        +22%     +21%    +1  CAPTURING
NCT   DOMESTIC        +22%      -0%   +22  CAPTURING
NNC   DOMESTIC        +69%     -44%  +113  CAPTURING
NTC   DOMESTIC        +34%     +12%   +23  CAPTURING
PVT   DOMESTIC        +24%      +7%   +17  CAPTURING
BIC   DOMESTIC        +14%     +18%    -5  MODERATE
BMP   DOMESTIC         -1%     +10%   -12  MODERATE
BWE   DOMESTIC        +11%      +7%    +4  MODERATE
CSV   DOMESTIC         +5%      +9%    -5  MODERATE
CTR   DOMESTIC        +15%     +23%    -8  MODERATE
CVT   DOMESTIC         +5%     +11%    -7  MODERATE
DMC   DOMESTIC         +9%      +3%    +6  MODERATE
MCH   DOMESTIC         +6%     +11%    -5  MODERATE
MWG   DOMESTIC        +10%      +5%    +5  MODERATE
NTP   DOMESTIC         +6%      +8%    -2  MODERATE
QNS   DOMESTIC         +9%      +6%    +2  MODERATE
TCL   DOMESTIC        +12%     +12%    -1  MODERATE
VGC   DOMESTIC         +1%     +10%    -9  MODERATE
FMC   EXPORT          +13%     +14%    -0  MODERATE
FPT   EXPORT          +13%     +17%    -4  MODERATE
DPM   DOMESTIC         +4%     +27%   -23  SATURATING
DTD   DOMESTIC        -11%     +65%   -77  SATURATING
HAH   DOMESTIC        +17%     +40%   -23  SATURATING
IDC   DOMESTIC         +2%     +16%   -14  SATURATING
MSN   DOMESTIC         +4%     +17%   -12  SATURATING
PNJ   DOMESTIC         +8%     +25%   -17  SATURATING
REE   DOMESTIC         +2%     +25%   -22  SATURATING
DGC   EXPORT           -7%     +35%   -42  SATURATING
HPG   STRUCTURAL      +12%     +22%   -10  SATURATING
DHA   DOMESTIC         +4%      +5%    -1  MATURE/FLAT
DHG   DOMESTIC         +4%      +6%    -2  MATURE/FLAT
DVP   DOMESTIC         +1%      +2%    -2  MATURE/FLAT
HDG   DOMESTIC        -10%      -4%    -6  MATURE/FLAT
LHG   DOMESTIC         +0%      -0%    +0  MATURE/FLAT
LIX   DOMESTIC         +5%      -0%    +5  MATURE/FLAT
PGS   DOMESTIC         -2%      +0%    -2  MATURE/FLAT
PHP   DOMESTIC         +8%      +4%    +4  MATURE/FLAT
QTP   DOMESTIC         -1%      +2%    -2  MATURE/FLAT
SAB   DOMESTIC         -8%      +0%    -8  MATURE/FLAT
TIP   DOMESTIC        -12%      +3%   -15  MATURE/FLAT
TLG   DOMESTIC         +6%      +5%    +1  MATURE/FLAT
VNM   DOMESTIC         +4%      +2%    +2  MATURE/FLAT
VTO   DOMESTIC         -2%      -7%    +5  MATURE/FLAT
PTB   EXPORT           +6%      +6%    -0  MATURE/FLAT
VCS   EXPORT           -9%      -4%    -5  MATURE/FLAT

RUNWAY OPEN (DURABLE/CAPTURING): GAS, MBB, SCS, D2D, FRT, NCT, NNC, NTC, PVT
  └ of which EXPORT (best TAM): none
SATURATING (S-curve topping): DPM, DTD, HAH, IDC, MSN, PNJ, REE, DGC, HPG
MATURE/FLAT: DHA, DHG, DVP, HDG, LHG, LIX, PGS, PHP, QTP, SAB, TIP, TLG, VNM, VTO, PTB, VCS

Caveat: revenue-trajectory only (cyclical/event dips muddy recent CAGR, e.g. DGC/VCS event); EXPORT tag manual (BQ no export%); STRUCTURAL=domestic+country-growth (HPG).