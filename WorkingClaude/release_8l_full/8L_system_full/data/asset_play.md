# ASSET-PLAY / SOTP detector — value on NAV, not earnings-multiple
proxies: NP↔Rev corr LOW (non-operating NP) + NP CV HIGH (lumpy) + asset-turn LOW (asset-heavy)

tkr    NP-Rev corr  NP CV assetTurn flags  verdict
----------------------------------------------------
NTC          +0.84   0.68      0.06     2  ASSET_PLAY
MBB          +0.96   0.74      0.07     2  ASSET_PLAY
KBC          +0.50   1.59      0.11     2  ASSET_PLAY
BCM          +0.70   0.84      0.15     2  ASSET_PLAY
KDH          +0.51   0.61      0.21     2  ASSET_PLAY
D2D          +0.89   1.32      0.24     2  ASSET_PLAY
NLG          +0.54   1.05      0.24     2  ASSET_PLAY
TIP          +0.30   0.82      0.25     3  ASSET_PLAY
HDG          +0.81   0.93      0.26     2  ASSET_PLAY
LHG          +0.82   0.80      0.26     2  ASSET_PLAY
DPR          +0.56   0.76      0.28     2  ASSET_PLAY
DXG          +0.49   1.52      0.28     2  ASSET_PLAY
PHR          +0.46   0.81      0.30     2  ASSET_PLAY
DTD          +0.75   1.11      0.31     2  ASSET_PLAY
IDC          +0.93   1.01      0.37     2  ASSET_PLAY
DVP          +0.27   0.29      0.42     2  ASSET_PLAY
BIC          +0.81   0.61      0.44     2  ASSET_PLAY
VTO          -0.06   0.65      0.68     2  ASSET_PLAY
CVT          -0.01   0.68      0.84     2  partial
QTP          +0.26   1.24      0.99     2  partial
PGS          -0.12   0.96      2.57     2  partial

ASSET_PLAY (value on NAV/SOTP): NTC, MBB, KBC, BCM, KDH, D2D, NLG, TIP, HDG, LHG, DPR, DXG, PHR, DTD, IDC, DVP, BIC, VTO

## Validation PHR vs DRI
  PHR: NP-Rev corr +0.46, NP CV 0.81, assetTurn 0.30 → ASSET_PLAY
  DRI: NP-Rev corr +0.80, NP CV 0.87, assetTurn 0.60 → operating (PE ok)
  DPR: NP-Rev corr +0.56, NP CV 0.76, assetTurn 0.28 → ASSET_PLAY
  → PHR = ASSET_PLAY (land-comp NP decoupled from rubber rev) → NAV; DRI = operating rubber (NP tracks rev) → PE/PB ok

Caveat: proxy only; true NAV (land at market) needs external estimate; flags land-banks/IP/holdcos/RE.