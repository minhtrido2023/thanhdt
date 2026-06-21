# Bank lens v3 — asset-quality GATE + NPL trend (real vnstock data)
GATE: AVOID(NPL>3%|cov<50%|CAR<9%|ROE<8%) WATCH(NPL>2%|cov<80%|NPL rising>+0.5pp/4q) else CLEAN

tkr    NPL%  4qChg  cov%  CAR%  NIM% CASA%  ROE%   PB   gate
----------------------------------------------------------------
SSB    2.24  +0.40    68  13.4  2.60    11   7.7 1.16  AVOID
VIB    2.94  -0.85    43  11.9  3.03    14  16.4 1.12  AVOID
EIB    3.07  +0.48    38  12.4  2.40    15   2.8 1.50  AVOID
OCB    3.52  -0.39    56  12.5  3.04    11  12.7 0.88  AVOID
VPB    3.58  -1.16    53  14.3  5.26    14  15.5 1.23  AVOID
STB    6.62  +4.11    53   9.2  3.05    16   7.6 2.09  AVOID
VCB    0.62  -0.41   253  12.2  2.66    34  16.1 2.21  CLEAN
ACB    0.97  -0.51   114  12.4  2.87    22  17.5 1.30  CLEAN
CTG    1.02  -0.54   167   9.5  2.59    25  21.7 1.44  CLEAN
TCB    1.09  -0.08   129  14.6  3.67    33  14.7 1.31  CLEAN
MBB    1.42  -0.42    92  11.8  3.87    33  20.1 1.40  CLEAN
BID    1.76  -0.14    87   9.2  2.09    20  17.8 1.65  CLEAN
NAB    1.82  -0.67    56  11.2  2.34     7  19.7 0.98  WATCH
LPB    1.84  +0.11    70  11.9  3.03     7  24.7 3.14  WATCH
TPB    2.17  -0.11    58  18.9  2.94    20  17.1 0.99  WATCH
SHB    2.60  -0.27    71  11.8  2.50     7  18.1 0.90  WATCH
HDB    2.60  +0.23    50  16.7  4.42    10  23.2 1.61  WATCH
MSB    2.66  +0.09    52  12.5  3.23    26  14.1 1.09  WATCH

## CLEAN banks ranked (passed quality gate) — quality 0.6 + value 0.4
rank tkr   SCORE  QUAL VALUE  NPL%  cov%  ROE%   PB
 1 TCB     0.70  0.72  0.67  1.09   129  14.7 1.31
 2 ACB     0.64  0.62  0.67  0.97   114  17.5 1.30
 3 MBB     0.59  0.55  0.67  1.42    92  20.1 1.40
 4 CTG     0.57  0.50  0.67  1.02   167  21.7 1.44
 5 VCB     0.45  0.69  0.08  0.62   253  16.1 2.21
 6 BID     0.18  0.14  0.25  1.76    87  17.8 1.65

CLEAN: VCB, BID, CTG, TCB, MBB, ACB
WATCH: HDB, SHB, TPB, MSB, LPB, NAB
AVOID: VPB, VIB, STB, OCB, EIB, SSB

NPL rising >+0.5pp over 4q (deteriorating): STB
Note: real vnstock/VCI. CAR=annual. NPL trend = change vs ~4 quarters ago. Snapshot — recheck quarterly.